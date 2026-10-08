#!/usr/bin/env python3
"""Detecta versões DECLARADAS de stack em um projeto, sem alterá-lo.

Lê: pom.xml (Maven), wrapper Maven, package.json (+ package-lock.json), angular.json,
arquivos de versão (.nvmrc, .sdkmanrc, .java-version, .tool-versions), docker compose,
application.properties/yaml e diretórios de migração.

Limitações declaradas na saída:
- Versões gerenciadas por BOM/parent aparecem como "gerenciada"; não há resolução de
  dependências (isso exigiria Maven e possivelmente rede).
- Faixas do package.json ("^17.3.0") não são a versão instalada; o package-lock.json, quando
  existe, fornece a versão travada.
- Gradle, pnpm-lock e yarn.lock são apenas detectados, não interpretados.

Uso:
    python3 detect_stack.py <projeto> [--format json|markdown]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.dont_write_bytecode = True  # não gravar __pycache__ dentro da skill instalada
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import find_line, iter_files, rel  # noqa: E402

MAVEN_NOTABLE = {
    "io.quarkus:quarkus-hibernate-orm-panache": "Hibernate ORM com Panache",
    "io.quarkus:quarkus-hibernate-orm": "Hibernate ORM",
    "io.quarkus:quarkus-hibernate-reactive-panache": "Hibernate Reactive com Panache",
    "io.quarkus:quarkus-hibernate-reactive": "Hibernate Reactive",
    "io.quarkus:quarkus-rest": "Quarkus REST (reativo)",
    "io.quarkus:quarkus-rest-jackson": "Quarkus REST + Jackson",
    "io.quarkus:quarkus-rest-jsonb": "Quarkus REST + JSON-B",
    "io.quarkus:quarkus-resteasy-reactive": "RESTEasy Reactive (nome antigo de Quarkus REST)",
    "io.quarkus:quarkus-resteasy-reactive-jackson": "RESTEasy Reactive + Jackson (nome antigo)",
    "io.quarkus:quarkus-resteasy": "RESTEasy Classic",
    "io.quarkus:quarkus-resteasy-jackson": "RESTEasy Classic + Jackson",
    "io.quarkus:quarkus-jdbc-postgresql": "Driver JDBC PostgreSQL",
    "io.quarkus:quarkus-reactive-pg-client": "Cliente reativo PostgreSQL",
    "io.quarkus:quarkus-flyway": "Flyway",
    "io.quarkus:quarkus-liquibase": "Liquibase",
    "io.quarkus:quarkus-hibernate-validator": "Bean Validation (Hibernate Validator)",
    "io.quarkus:quarkus-cache": "Quarkus Cache",
    "io.quarkus:quarkus-junit5": "Testes @QuarkusTest",
    "io.rest-assured:rest-assured": "REST Assured",
    "org.mapstruct:mapstruct": "MapStruct",
    "org.mapstruct:mapstruct-processor": "MapStruct (processador)",
    "org.projectlombok:lombok": "Lombok",
    "org.projectlombok:lombok-mapstruct-binding": "Binding Lombok-MapStruct",
    "com.tngtech.archunit:archunit": "ArchUnit",
    "com.tngtech.archunit:archunit-junit5": "ArchUnit (JUnit 5)",
    "org.hibernate.orm:hibernate-core": "Hibernate ORM (explícito)",
    "org.hibernate:hibernate-core": "Hibernate ORM (explícito, groupId antigo)",
    "org.postgresql:postgresql": "Driver JDBC PostgreSQL",
    "org.springframework.boot:spring-boot-starter-web": "Spring Boot Web",
    "org.springframework.boot:spring-boot-starter-data-jpa": "Spring Data JPA",
}
MAVEN_TESTCONTAINERS_GROUP = "org.testcontainers"
MAVEN_PLUGINS = {
    "maven-compiler-plugin": "Compilador Maven",
    "quarkus-maven-plugin": "Plugin Quarkus",
    "maven-checkstyle-plugin": "Checkstyle",
    "maven-pmd-plugin": "PMD",
    "spotbugs-maven-plugin": "SpotBugs",
    "jacoco-maven-plugin": "JaCoCo",
    "sonar-maven-plugin": "Sonar",
    "maven-surefire-plugin": "Surefire (testes unitários)",
    "maven-failsafe-plugin": "Failsafe (testes de integração)",
}
NPM_NOTABLE = [
    "@angular/core",
    "@angular/cli",
    "@angular/cdk",
    "react",
    "react-dom",
    "next",
    "react-router",
    "react-router-dom",
    "react-scripts",
    "vite",
    "typescript",
    "rxjs",
    "@tanstack/react-query",
    "swr",
    "@reduxjs/toolkit",
    "zustand",
    "babel-plugin-react-compiler",
    "jest",
    "vitest",
    "karma",
    "jasmine-core",
    "@playwright/test",
    "cypress",
    "eslint",
    "@angular-eslint/builder",
    "eslint-plugin-react-hooks",
    "@typescript-eslint/eslint-plugin",
]
POSTGRES_IMAGE_RE = re.compile(
    r"image:\s*[\"']?(?P<image>(?:[\w.-]+/)?(?:postgres|postgis/postgis|postgresql))(?::(?P<tag>[\w.\-]+))?",
    re.IGNORECASE,
)
PROPERTY_KEYS = (
    "quarkus.datasource.db-kind",
    "quarkus.datasource.db-version",
    "quarkus.hibernate-orm.database.generation",
    "quarkus.hibernate-orm.schema-management.strategy",
    "quarkus.hibernate-orm.log.sql",
    "quarkus.hibernate-orm.fetch.batch-size",
    "quarkus.hibernate-orm.statistics",
)


@dataclass
class Fact:
    key: str
    value: str
    source: str
    note: str = ""


@dataclass
class Component:
    kind: str
    path: str
    facts: list[Fact] = field(default_factory=list)


@dataclass
class Report:
    project: str
    components: list[Component] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


def _src(path: Path, root: Path, text: str | None, needle: str | None) -> str:
    location = rel(path, root)
    if text is not None and needle:
        line = find_line(text, needle)
        if line:
            return f"{location}:{line}"
    return location


# --------------------------------------------------------------------------- Maven

def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[1] if "}" in tag else tag


def _child(elem: ET.Element | None, name: str) -> ET.Element | None:
    if elem is None:
        return None
    for c in elem:
        if _strip_ns(c.tag) == name:
            return c
    return None


def _elements(elem: ET.Element | None) -> list[ET.Element]:
    """Filhos diretos sem depender do valor-verdade de Element (depreciado no Python 3.12)."""
    return list(elem) if elem is not None else []


def _children(elem: ET.Element | None, name: str) -> list[ET.Element]:
    if elem is None:
        return []
    return [c for c in elem if _strip_ns(c.tag) == name]


def _text(elem: ET.Element | None, name: str) -> str | None:
    c = _child(elem, name)
    return c.text.strip() if c is not None and c.text else None


def _resolve(value: str | None, props: dict[str, str], depth: int = 0) -> str | None:
    if value is None or depth > 5:
        return value

    def repl(m: re.Match[str]) -> str:
        return props.get(m.group(1), m.group(0))

    new = re.sub(r"\$\{([^}]+)\}", repl, value)
    return new if new == value else _resolve(new, props, depth + 1)


def _parent_properties(pom: Path, root: Path) -> dict[str, str]:
    """Propriedades de poms ancestrais dentro do projeto (herança simples por diretório)."""
    props: dict[str, str] = {}
    chain = []
    current = pom.parent.parent
    while True:
        candidate = current / "pom.xml"
        if candidate.is_file():
            chain.append(candidate)
        if current.resolve() == root.resolve() or current.parent == current:
            break
        current = current.parent
    for parent in reversed(chain):
        try:
            tree = ET.parse(parent)
        except ET.ParseError:
            continue
        for p in _elements(_child(tree.getroot(), "properties")):
            if p.text:
                props[_strip_ns(p.tag)] = p.text.strip()
    return props


def scan_maven(pom: Path, root: Path) -> Component:
    comp = Component(kind="maven", path=rel(pom, root))
    text = pom.read_text(encoding="utf-8", errors="replace")
    try:
        project = ET.fromstring(text)
    except ET.ParseError as exc:
        comp.facts.append(Fact("erro", f"pom.xml inválido: {exc}", rel(pom, root)))
        return comp

    props = _parent_properties(pom, root)
    for p in _elements(_child(project, "properties")):
        if p.text:
            props[_strip_ns(p.tag)] = p.text.strip()
    for key in ("groupId", "artifactId", "version"):
        val = _text(project, key)
        if val:
            props[f"project.{key}"] = val

    parent = _child(project, "parent")
    if parent is not None:
        gid, aid, ver = _text(parent, "groupId"), _text(parent, "artifactId"), _text(parent, "version")
        comp.facts.append(Fact("maven.parent", f"{gid}:{aid}:{ver}", _src(pom, root, text, f"<artifactId>{aid}</artifactId>")))
        if gid == "org.springframework.boot":
            comp.facts.append(Fact("spring-boot", ver or "?", _src(pom, root, text, "spring-boot"), "Spring Boot detectado: o perfil java-quarkus se aplica só parcialmente"))

    modules = [m.text.strip() for m in _children(_child(project, "modules"), "module") if m.text]
    if modules:
        comp.facts.append(Fact("maven.modules", ", ".join(modules), _src(pom, root, text, "<modules>"), "projeto multi-módulo"))

    # JDK alvo
    for key in ("maven.compiler.release", "maven.compiler.source", "maven.compiler.target", "java.version"):
        if key in props:
            comp.facts.append(Fact(f"java ({key})", _resolve(props[key], props) or "", _src(pom, root, text, f"<{key}>")))

    # Quarkus via propriedades
    for key in ("quarkus.platform.version", "quarkus.version", "quarkus-plugin.version"):
        if key in props:
            comp.facts.append(Fact(f"quarkus ({key})", _resolve(props[key], props) or "", _src(pom, root, text, f"<{key}>")))

    # BOMs importados
    dm = _child(_child(project, "dependencyManagement"), "dependencies")
    for dep in _children(dm, "dependency"):
        gid, aid = _text(dep, "groupId"), _text(dep, "artifactId")
        ver = _resolve(_text(dep, "version"), props)
        if _text(dep, "scope") == "import":
            comp.facts.append(Fact("bom", f"{_resolve(gid, props)}:{_resolve(aid, props)}:{ver}", _src(pom, root, text, f"<artifactId>{aid}</artifactId>")))

    # Dependências
    deps = _child(project, "dependencies")
    for dep in _children(deps, "dependency"):
        gid = _resolve(_text(dep, "groupId"), props) or ""
        aid = _resolve(_text(dep, "artifactId"), props) or ""
        ver = _resolve(_text(dep, "version"), props)
        scope = _text(dep, "scope") or "compile"
        coord = f"{gid}:{aid}"
        label = MAVEN_NOTABLE.get(coord)
        if label is None and gid == MAVEN_TESTCONTAINERS_GROUP:
            label = f"Testcontainers ({aid})"
        if label is None:
            continue
        version = ver if ver else "gerenciada (BOM/parent) — NÃO RESOLVIDA"
        note = label + ("" if scope == "compile" else f"; escopo {scope}")
        comp.facts.append(Fact(f"dep {coord}", version, _src(pom, root, text, f"<artifactId>{aid}</artifactId>"), note))

    # Plugins (inclui annotationProcessorPaths do compilador)
    plugins = _child(_child(project, "build"), "plugins")
    for plugin in _children(plugins, "plugin"):
        aid = _text(plugin, "artifactId") or ""
        if aid not in MAVEN_PLUGINS:
            continue
        ver = _resolve(_text(plugin, "version"), props)
        comp.facts.append(Fact(f"plugin {aid}", ver or "gerenciada", _src(pom, root, text, f"<artifactId>{aid}</artifactId>"), MAVEN_PLUGINS[aid]))
        cfg = _child(plugin, "configuration")
        if aid == "maven-compiler-plugin" and cfg is not None:
            release = _resolve(_text(cfg, "release") or _text(cfg, "source"), props)
            if release:
                comp.facts.append(Fact("java (maven-compiler-plugin)", release, _src(pom, root, text, "<release>") if _text(cfg, "release") else _src(pom, root, text, "<source>")))
            for path in _children(_child(cfg, "annotationProcessorPaths"), "path"):
                pa = _resolve(_text(path, "artifactId"), props) or ""
                pv = _resolve(_text(path, "version"), props) or "gerenciada"
                comp.facts.append(Fact(f"annotationProcessor {_resolve(_text(path, 'groupId'), props)}:{pa}", pv, _src(pom, root, text, f"<artifactId>{pa}</artifactId>")))
        if aid == "quarkus-maven-plugin" and ver:
            comp.facts.append(Fact("quarkus (plugin)", ver, _src(pom, root, text, "quarkus-maven-plugin")))

    return comp


def scan_maven_wrapper(path: Path, root: Path) -> Component:
    comp = Component(kind="maven-wrapper", path=rel(path, root))
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"apache-maven-(\d+(?:\.\d+)+)", text)
    comp.facts.append(Fact("maven (wrapper)", m.group(1) if m else "não identificado", _src(path, root, text, "distributionUrl")))
    return comp


# --------------------------------------------------------------------------- npm

def scan_package_json(path: Path, root: Path) -> Component:
    comp = Component(kind="npm", path=rel(path, root))
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        comp.facts.append(Fact("erro", f"package.json inválido: {exc}", rel(path, root)))
        return comp

    locked: dict[str, str] = {}
    lock = path.parent / "package-lock.json"
    if lock.is_file():
        try:
            lock_data = json.loads(lock.read_text(encoding="utf-8", errors="replace"))
            for key, info in (lock_data.get("packages") or {}).items():
                if key.startswith("node_modules/") and isinstance(info, dict) and "version" in info:
                    name = key[len("node_modules/"):]
                    if "/node_modules/" not in name:
                        locked[name] = info["version"]
            for name, info in (lock_data.get("dependencies") or {}).items():  # lockfile v1
                if isinstance(info, dict) and "version" in info:
                    locked.setdefault(name, info["version"])
        except (json.JSONDecodeError, OSError):
            comp.facts.append(Fact("aviso", "package-lock.json ilegível", rel(lock, root)))
    for other in ("pnpm-lock.yaml", "yarn.lock"):
        if (path.parent / other).is_file():
            comp.facts.append(Fact("lockfile", other, rel(path.parent / other, root), "detectado, não interpretado; use-o para confirmar versões instaladas"))

    sections = {**(data.get("devDependencies") or {}), **(data.get("dependencies") or {})}
    for name in NPM_NOTABLE:
        if name in sections:
            declared = sections[name]
            lockv = locked.get(name)
            value = f"{declared} (declarada)" + (f"; {lockv} (package-lock)" if lockv else "")
            comp.facts.append(Fact(f"npm {name}", value, _src(path, root, text, f'"{name}"')))
    engines = data.get("engines") or {}
    for k, v in engines.items():
        comp.facts.append(Fact(f"engines.{k}", str(v), _src(path, root, text, '"engines"')))
    scripts = data.get("scripts") or {}
    for k in ("build", "test", "lint", "e2e"):
        if k in scripts:
            comp.facts.append(Fact(f"script {k}", scripts[k], _src(path, root, text, f'"{k}"')))
    return comp


def scan_angular_json(path: Path, root: Path) -> Component:
    comp = Component(kind="angular", path=rel(path, root))
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        comp.facts.append(Fact("erro", "angular.json inválido", rel(path, root)))
        return comp
    for name, proj in (data.get("projects") or {}).items():
        build = ((proj.get("architect") or proj.get("targets") or {}).get("build") or {})
        builder = build.get("builder")
        if builder:
            comp.facts.append(Fact(f"builder ({name})", builder, _src(path, root, text, builder)))
        budgets = (((build.get("configurations") or {}).get("production") or {}).get("budgets"))
        comp.facts.append(Fact(f"budgets ({name})", "configurados" if budgets else "não configurados", rel(path, root)))
    return comp


# --------------------------------------------------------------------------- outros

def scan_version_file(path: Path, root: Path) -> Component:
    comp = Component(kind="version-file", path=rel(path, root))
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            comp.facts.append(Fact(path.name, line, f"{rel(path, root)}:{find_line(text, line) or 1}"))
    return comp


def scan_compose(path: Path, root: Path) -> Component | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    matches = list(POSTGRES_IMAGE_RE.finditer(text))
    if not matches:
        return None
    comp = Component(kind="docker-compose", path=rel(path, root))
    for m in matches:
        tag = m.group("tag") or "latest (implícito)"
        comp.facts.append(Fact("postgresql (imagem)", f"{m.group('image')}:{tag}", f"{rel(path, root)}:{find_line(text, m.group(0))}"))
    return comp


def scan_app_config(path: Path, root: Path) -> Component | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    comp = Component(kind="app-config", path=rel(path, root))
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for key in PROPERTY_KEYS:
            # application.properties: [%perfil.]chave=valor
            m = re.match(rf"^(%[\w-]+\.)?{re.escape(key)}\s*[=:]\s*(.*)$", stripped)
            if m:
                profile = (m.group(1) or "").rstrip(".") or "todos os perfis"
                comp.facts.append(Fact(key, m.group(2).strip(), f"{rel(path, root)}:{i}", f"perfil: {profile}"))
    return comp if comp.facts else None


def scan_migrations(root: Path, files: list[Path]) -> Component | None:
    flyway = [f for f in files if "/db/migration/" in f.as_posix() and f.suffix == ".sql"]
    liquibase = [f for f in files if "changelog" in f.name.lower() and f.suffix in {".xml", ".yaml", ".yml", ".sql"}]
    if not flyway and not liquibase:
        return None
    comp = Component(kind="migrations", path=".")
    if flyway:
        comp.facts.append(Fact("flyway (scripts)", str(len(flyway)), rel(flyway[0].parent, root)))
    if liquibase:
        comp.facts.append(Fact("liquibase (changelogs)", str(len(liquibase)), rel(liquibase[0], root)))
    return comp


def detect(root: Path) -> Report:
    report = Report(project=str(root))
    files = list(iter_files(root))
    for path in files:
        name = path.name
        if name == "pom.xml":
            report.components.append(scan_maven(path, root))
        elif name == "maven-wrapper.properties":
            report.components.append(scan_maven_wrapper(path, root))
        elif name == "package.json":
            report.components.append(scan_package_json(path, root))
        elif name == "angular.json":
            report.components.append(scan_angular_json(path, root))
        elif name in {".nvmrc", ".node-version", ".sdkmanrc", ".java-version", ".tool-versions", ".python-version"}:
            report.components.append(scan_version_file(path, root))
        elif re.fullmatch(r"(docker-)?compose[\w.-]*\.ya?ml", name):
            comp = scan_compose(path, root)
            if comp:
                report.components.append(comp)
        elif re.fullmatch(r"application(-[\w]+)?\.(properties|ya?ml)", name) and "/src/test/" not in path.as_posix():
            comp = scan_app_config(path, root)
            if comp:
                report.components.append(comp)
        elif name in {"build.gradle", "build.gradle.kts"}:
            report.components.append(Component("gradle", rel(path, root), [Fact("gradle", "detectado", rel(path, root), "build Gradle não é interpretado por este script")]))
    mig = scan_migrations(root, files)
    if mig:
        report.components.append(mig)

    report.limitations = [
        "Versões gerenciadas por BOM/parent não são resolvidas (use mvn help:effective-pom ou dependency:tree, se disponível).",
        "Faixas do package.json não são versões instaladas; o package-lock.json é usado quando existe.",
        "Gradle, pnpm-lock.yaml e yarn.lock são apenas detectados.",
        "Valores vindos de variáveis de ambiente ou arquivos externos não são vistos.",
    ]
    if not report.components:
        report.limitations.insert(0, "Nenhum arquivo de build/configuração reconhecido foi encontrado.")
    return report


def to_markdown(report: Report) -> str:
    out = [f"# Stack detectada — {report.project}", "", "> Versões DECLARADAS (evidência E3). Confirme as marcadas como gerenciadas/não resolvidas.", ""]
    for comp in report.components:
        out.append(f"## {comp.kind} — `{comp.path}`")
        out.append("")
        out.append("| Item | Valor | Fonte | Observação |")
        out.append("|---|---|---|---|")
        for f in comp.facts:
            out.append(f"| {f.key} | {f.value} | `{f.source}` | {f.note} |")
        out.append("")
    out.append("## Limitações")
    out.append("")
    out.extend(f"- {item}" for item in report.limitations)
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args(argv)
    root = args.project.resolve()
    if not root.is_dir():
        print(f"erro: diretório não encontrado: {root}", file=sys.stderr)
        return 1
    report = detect(root)
    if args.format == "json":
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(to_markdown(report), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
