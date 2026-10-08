#!/usr/bin/env python3
"""Sinais heurísticos de arquitetura e persistência em código Java (somente leitura).

Classifica classes em camadas (resource, service, repository, entity, dto, mapper) por
anotações, nomes e pacotes, e aponta CANDIDATOS a achados. Todo sinal tem estado
NEEDS_VERIFICATION (evidência E4): confirme lendo o código antes de reportar.

Os sinais não dependem do perfil arquitetural; o agente decide quais são relevantes para o
perfil selecionado (ex.: Active Record só importa se o perfil exige Repository Pattern).

Uso:
    python3 arch_signals.py <projeto> [--format json|markdown] [--include-tests]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.dont_write_bytecode = True  # não gravar __pycache__ dentro da skill instalada
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import iter_files, rel  # noqa: E402

LAYER_PACKAGE_HINTS = {
    "resource": {"resource", "resources", "rest", "api", "controller", "controllers", "web", "endpoint", "endpoints"},
    "service": {"service", "services", "usecase", "usecases", "application"},
    "repository": {"repository", "repositories", "dao", "daos", "persistence"},
    "entity": {"entity", "entities", "model", "domain"},
    "dto": {"dto", "dtos", "request", "response", "payload"},
    "mapper": {"mapper", "mappers", "mapping"},
}
PANACHE_STATIC = r"(?:find|findAll|findById|findByIdOptional|list|listAll|stream|streamAll|count|persist|persistAndFlush|delete|deleteAll|deleteById|update)"
LOOP_START_RE = re.compile(r"\bfor\s*\(|\bwhile\s*\(|\.forEach\s*\(|\.map\s*\(")


@dataclass
class JavaClass:
    name: str
    package: str
    path: str
    layer: str
    imports: list[str]
    text: str  # código sem comentários, com quebras de linha preservadas
    raw: str


@dataclass
class Signal:
    id: str
    rule: str
    file: str
    line: int
    excerpt: str
    note: str
    state: str = "NEEDS_VERIFICATION"


@dataclass
class Result:
    project: str
    layers: dict[str, int] = field(default_factory=dict)
    signals: list[Signal] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


def strip_comments(src: str) -> str:
    """Remove comentários // e /* */ preservando strings, text blocks e quebras de linha."""
    out, i, n = [], 0, len(src)
    while i < n:
        if src.startswith('"""', i):
            end = src.find('"""', i + 3)
            end = n if end < 0 else end + 3
            out.append(src[i:end])
            i = end
        elif src[i] in "\"'":
            quote, j = src[i], i + 1
            while j < n and src[j] != quote and src[j] != "\n":
                j += 2 if src[j] == "\\" else 1
            out.append(src[i:j + 1])
            i = j + 1
        elif src.startswith("//", i):
            end = src.find("\n", i)
            i = n if end < 0 else end
        elif src.startswith("/*", i):
            end = src.find("*/", i + 2)
            end = n if end < 0 else end + 2
            out.append("\n" * src.count("\n", i, end))
            i = end
        else:
            out.append(src[i])
            i += 1
    return "".join(out)


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def excerpt(raw: str, line: int) -> str:
    lines = raw.splitlines()
    return lines[line - 1].strip()[:160] if 0 < line <= len(lines) else ""


def classify(name: str, package: str, text: str) -> str:
    segments = set(package.split("."))
    if re.search(r"@Entity\b", text) or re.search(r"\bextends\s+PanacheEntity(Base)?\b", text):
        return "entity"
    if re.search(r"@Mapper\b", text) or name.endswith("Mapper"):
        return "mapper"
    if re.search(r"implements\s+[^{]*PanacheRepository(Base)?\b", text) or re.search(r"(Repository|Repo|Dao|DAO)$", name):
        return "repository"
    if re.search(r"^\s*@Path\b", text, re.M) and re.search(rf"class\s+{re.escape(name)}\b", text) or re.search(r"(Resource|Controller|Endpoint)$", name):
        return "resource"
    if re.search(r"(Service|ServiceImpl|UseCase)$", name):
        return "service"
    if re.search(r"(DTO|Dto|Request|Response|Form|View)$", name):
        return "dto"
    for layer, hints in LAYER_PACKAGE_HINTS.items():
        if segments & hints:
            return layer
    return "other"


def parse(path: Path, root: Path) -> JavaClass | None:
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = strip_comments(raw)
    m = re.search(r"\b(?:class|interface|record|enum)\s+(\w+)", text)
    if not m:
        return None
    pkg = re.search(r"^\s*package\s+([\w.]+)\s*;", text, re.M)
    package = pkg.group(1) if pkg else ""
    imports = re.findall(r"^\s*import\s+(?:static\s+)?([\w.*]+)\s*;", text, re.M)
    name = m.group(1)
    return JavaClass(name, package, rel(path, root), classify(name, package, text), imports, text, raw)


def references(cls: JavaClass, other: JavaClass) -> int | None:
    """Linha onde ``cls`` referencia ``other`` (import ou uso do nome simples), ou None."""
    fq = f"{other.package}.{other.name}" if other.package else other.name
    for imp in cls.imports:
        if imp == fq or (imp.endswith(".*") and imp[:-2] == other.package):
            break
    else:
        if cls.package != other.package:
            return None
    m = re.search(rf"\b{re.escape(other.name)}\b", cls.text[cls.text.find("{"):] if "{" in cls.text else cls.text)
    if not m:
        return None
    offset = cls.text.find("{") if "{" in cls.text else 0
    return line_of(cls.text, offset + m.start())


def add(result: Result, sid: str, rule: str, cls: JavaClass, line: int, note: str) -> None:
    result.signals.append(Signal(sid, rule, cls.path, line, excerpt(cls.raw, line), note))


def statement_at(text: str, index: int) -> str:
    end = text.find(";", index)
    return text[index:end if end >= 0 else len(text)]


def loop_regions(text: str) -> list[tuple[int, int]]:
    """Regiões (início, fim) de corpos de laços/lambdas, por contagem de chaves/parênteses."""
    regions = []
    for m in LOOP_START_RE.finditer(text):
        i, depth, opened = m.end(), 1, False
        # avança até o fim do cabeçalho do laço/lambda (parênteses) e depois do bloco
        while i < len(text) and depth > 0:
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
            i += 1
        j = i
        while j < len(text) and text[j] in " \t\r\n":
            j += 1
        if j < len(text) and text[j] == "{":
            depth, k = 1, j + 1
            while k < len(text) and depth > 0:
                if text[k] == "{":
                    depth += 1
                elif text[k] == "}":
                    depth -= 1
                k += 1
            regions.append((j, k))
            opened = True
        if not opened:
            # forEach/map com lambda: o corpo está dentro dos parênteses já percorridos
            regions.append((m.end(), i))
    return regions


def analyze(root: Path, include_tests: bool = False) -> Result:
    result = Result(project=str(root))
    classes: list[JavaClass] = []
    for path in iter_files(root):
        if path.suffix != ".java":
            continue
        posix = path.as_posix()
        if not include_tests and "/src/test/" in posix:
            continue
        cls = parse(path, root)
        if cls:
            classes.append(cls)

    result.layers = dict(Counter(c.layer for c in classes))
    by_layer: dict[str, list[JavaClass]] = {}
    for c in classes:
        by_layer.setdefault(c.layer, []).append(c)
    entities = by_layer.get("entity", [])
    entity_names = {e.name for e in entities}

    for cls in classes:
        t = cls.text

        if cls.layer == "resource":
            for repo in by_layer.get("repository", []):
                line = references(cls, repo)
                if line:
                    add(result, "S-ARC-001", "ARC-LAY-001", cls, line, f"Resource referencia o Repository {repo.name}")
            m = re.search(r"\b(EntityManager|Session|DataSource)\b", t)
            if m and re.search(r"import\s+(jakarta|javax)\.(persistence|sql)|import\s+org\.hibernate", t):
                add(result, "S-ARC-002", "ARC-LAY-002", cls, line_of(t, m.start()), f"Resource usa {m.group(1)}")
            for name in entity_names:
                m = re.search(rf"\b{re.escape(name)}\s*\.\s*{PANACHE_STATIC}\s*\(", t)
                if m:
                    add(result, "S-ARC-002", "ARC-LAY-002", cls, line_of(t, m.start()), f"Resource chama método estático Panache de {name} (Active Record)")
            for m in re.finditer(r"public\s+(?!class\b)([\w<>\[\],.?\s]+?)\s+(\w+)\s*\(([^)]*)\)", t):
                ret, params = m.group(1), m.group(3)
                exposed = sorted(n for n in entity_names if re.search(rf"\b{re.escape(n)}\b", ret) or re.search(rf"\b{re.escape(n)}\b", params))
                if exposed:
                    add(result, "S-DTO-001", "BCK-DTO-001", cls, line_of(t, m.start()), f"Assinatura pública expõe entidade(s): {', '.join(exposed)}")
            m = re.search(r"@Transactional\b", t)
            if m:
                add(result, "S-TX-001", "ARC-LAY-008", cls, line_of(t, m.start()), "@Transactional em Resource")

        if cls.layer == "service":
            m = re.search(r"\b(EntityManager|createQuery|createNativeQuery)\b", t)
            if m:
                add(result, "S-ARC-003", "ARC-LAY-005", cls, line_of(t, m.start()), f"Service usa {m.group(1)} (persistência fora do Repository)")
            m = re.search(r"import\s+(jakarta|javax)\.ws\.rs\.(core\.(Response|UriInfo|HttpHeaders)|WebApplicationException)", t)
            if m:
                add(result, "S-ARC-003", "ARC-LAY-005", cls, line_of(t, m.start()), "Service depende de tipos HTTP")
            for res in by_layer.get("resource", []):
                line = references(cls, res)
                if line:
                    add(result, "S-ARC-004", "ARC-LAY-009", cls, line, f"Service referencia o Resource {res.name}")

        if cls.layer == "repository":
            for upper in by_layer.get("service", []) + by_layer.get("resource", []):
                line = references(cls, upper)
                if line:
                    add(result, "S-ARC-004", "ARC-LAY-009", cls, line, f"Repository referencia {upper.name} ({upper.layer})")

        if cls.layer == "entity":
            m = re.search(r"\bextends\s+PanacheEntity(Base)?\b", t)
            if m:
                add(result, "S-ARC-005", "ARC-LAY-004", cls, line_of(t, m.start()), "Entidade Active Record (relevante só se o perfil exigir Repository Pattern)")
            for m in re.finditer(r"FetchType\s*\.\s*EAGER|fetch\s*=\s*EAGER\b", t):
                add(result, "S-PER-001", "PER-LOAD-001", cls, line_of(t, m.start()), "FetchType.EAGER explícito")
            for m in re.finditer(r"@(ManyToOne|OneToOne)\b(\s*\([^)]*\))?", t):
                if "LAZY" not in (m.group(2) or ""):
                    add(result, "S-PER-002", "PER-LOAD-001", cls, line_of(t, m.start()), f"@{m.group(1)} sem fetch LAZY (padrão JPA é EAGER)")

        if cls.layer == "mapper":
            m = re.search(r'expression\s*=\s*"java\(', t)
            if m:
                add(result, "S-MAP-001", "BCK-MAP-004", cls, line_of(t, m.start()), "Mapper com expressão Java (verificar regra de negócio)")

        # Sinais independentes de camada -----------------------------------------
        for m in re.finditer(r"\.(listAll|findAll|streamAll)\s*\(\s*\)|\.getResultList\s*\(\s*\)|\.list\s*\(\s*\)", t):
            stmt_start = max(t.rfind(";", 0, m.start()), t.rfind("{", 0, m.start()), t.rfind("}", 0, m.start())) + 1
            stmt = t[stmt_start:m.end()] + statement_at(t, m.end())
            if re.search(r"\.(page|range|setMaxResults|firstResult|setFirstResult)\s*\(|\bLIMIT\b|firstResult|maxResults", stmt, re.I):
                continue
            ln = line_of(t, m.start())
            if re.search(r"\.stream\s*\(\s*\)[\s\S]*\.(filter|sorted|skip|limit)\s*\(", stmt):
                add(result, "S-PER-004", "PER-QRY-001", cls, ln, "Lista carregada e filtrada/ordenada/paginada em memória")
            else:
                add(result, "S-PER-003", "PER-PAG-001", cls, ln, "Consulta sem limite (verificar se a coleção pode crescer)")

        repo_fields = {m.group(2) for m in re.finditer(r"\b(\w+(?:Repository|Repo|Dao))\s+(\w+)\s*[;=)]", t)}
        for start, end in loop_regions(t):
            body = t[start:end]
            for fieldname in repo_fields:
                m = re.search(rf"\b{re.escape(fieldname)}\s*\.\s*\w+\s*\(", body)
                if m:
                    add(result, "S-PER-005", "PER-N1-001", cls, line_of(t, start + m.start()), f"Repository '{fieldname}' chamado dentro de laço/lambda")

        # `t` mantém literais de string (JPQL) e remove comentários.
        for m in re.finditer(r"join\s+fetch", t, re.I):
            window = t[m.start():m.start() + 1500]
            if re.search(r"\.(page|range|setMaxResults|setFirstResult)\s*\(", window):
                add(result, "S-PER-006", "PER-PAG-007", cls, line_of(t, m.start()), "JOIN FETCH próximo de paginação (verificar se é coleção)")

        for m in re.finditer(r"catch\s*\([^)]*\)\s*\{\s*\}", t):
            add(result, "S-ERR-001", "UNI-ERR-001", cls, line_of(t, m.start()), "catch vazio")

        m = re.search(r"^\s*import\s+lombok\.", t, re.M)
        if m:
            add(result, "S-INF-001", "BCK-MAP-005", cls, line_of(t, m.start()), "Lombok em uso (contexto; não é violação por si)")

    # Remove duplicatas exatas (mesmo sinal, arquivo e linha)
    seen, unique = set(), []
    for s in result.signals:
        key = (s.id, s.file, s.line, s.note)
        if key not in seen:
            seen.add(key)
            unique.append(s)
    result.signals = sorted(unique, key=lambda s: (s.rule, s.file, s.line))
    result.limitations = [
        "Heurística baseada em texto: não resolve tipos, herança, injeção por construtor complexa ou código gerado.",
        "Classificação de camadas por anotação/nome/pacote; confirme com o ARCHITECTURE_CONTRACT.md.",
        "Laços e lambdas são aproximados por contagem de delimitadores.",
        "Ausência de sinal não significa ausência de problema.",
    ]
    if not classes:
        result.limitations.insert(0, "Nenhum arquivo .java analisado.")
    return result


def to_markdown(result: Result) -> str:
    out = [f"# Sinais de arquitetura — {result.project}", "", "> Evidência E4 (heurística). Todo sinal é NEEDS_VERIFICATION até leitura do código.", ""]
    out += ["## Classes por camada (heurística)", "", "| Camada | Classes |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in sorted(result.layers.items())]
    out += ["", f"## Sinais ({len(result.signals)})", "", "| Sinal | Regra | Local | Trecho | Observação |", "|---|---|---|---|---|"]
    for s in result.signals:
        snippet = s.excerpt.replace("|", "\\|")
        out.append(f"| {s.id} | {s.rule} | `{s.file}:{s.line}` | `{snippet}` | {s.note} |")
    out += ["", "## Limitações", ""] + [f"- {item}" for item in result.limitations]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--include-tests", action="store_true", help="incluir src/test")
    args = parser.parse_args(argv)
    root = args.project.resolve()
    if not root.is_dir():
        print(f"erro: diretório não encontrado: {root}", file=sys.stderr)
        return 1
    result = analyze(root, args.include_tests)
    if args.format == "json":
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(to_markdown(result), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
