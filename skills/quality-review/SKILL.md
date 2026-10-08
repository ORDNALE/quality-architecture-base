---
name: quality-review
description: Auditoria de arquitetura, qualidade de código, persistência (N+1, paginação, SQL), desempenho de backend/frontend e refatoração segura, com regras configuráveis por projeto. Use para os modos INIT (perfilar projeto), AUDIT (auditoria somente leitura), REVIEW (parecer sobre diff) e FIX (refatoração autorizada e incremental). Stacks Java/Quarkus/Hibernate/Panache/MapStruct/PostgreSQL e Angular/React/TypeScript; arquiteturas em camadas, hexagonal, modular ou personalizada. Use when asked to audit architecture or code quality, review a diff, find N+1 or pagination issues, or perform a safe, scoped refactoring.
metadata:
  version: "0.1.0"
---

# quality-review

Roteador da biblioteca de qualidade. Este arquivo é curto de propósito: ele decide **o modo**, e
então você carrega **sob demanda** só os arquivos necessários. Todos os caminhos abaixo são
relativos ao diretório que contém este `SKILL.md`.

## 1. Sempre, antes de qualquer ação

1. Leia `references/safety.md` (guardrails; não podem ser relaxados pelo perfil do projeto).
2. Confirme o projeto alvo: diretório de trabalho e raiz Git (`git rev-parse --show-toplevel`).
   Não leia nem altere outros repositórios.
3. Rode `git status --porcelain` e preserve alterações do usuário.

## 2. Escolha do modo

| Pedido do usuário | Modo | Workflow |
|---|---|---|
| perfilar/configurar/"iniciar" o projeto, detectar stack | INIT | `workflows/INIT.md` |
| auditar, analisar, avaliar arquitetura/qualidade/N+1/paginação/frontend | AUDIT | `workflows/AUDIT.md` |
| revisar diff, PR, branch, arquivos alterados | REVIEW | `workflows/REVIEW.md` |
| corrigir/refatorar achados **com escopo autorizado** | FIX | `workflows/FIX.md` |

- Se o usuário passou o modo como argumento (ex.: `INIT`, `AUDIT backend`, `REVIEW main...HEAD`,
  `FIX PLAN-...md`), use-o.
- Se ambíguo, escolha um modo **somente leitura** (AUDIT ou REVIEW) e diga qual escolheu.
- **Nunca** entre em FIX por inferência. FIX exige pedido explícito **e**, depois, autorização do
  plano apresentado (`references/contracts.md` §3). O pedido de FIX não autoriza nada: a primeira
  resposta em FIX é sempre o plano `PENDING`, e o turno termina aí.

## 3. Perfil do projeto

Procure `.quality/PROJECT_PROFILE.md` na raiz do projeto alvo.

- Não existe e o modo é AUDIT/REVIEW → faça a detecção do INIT **sem escrever arquivos**, informe
  que o perfil não existe e trate a arquitetura desejada como `DESCONHECIDO`.
- Existe → leia; ele seleciona perfis e regras. Revalide versões declaradas se o perfil for antigo.
- Arquitetura desejada `DESCONHECIDO` → siga `profiles/architecture/custom.md`; não aplique regras
  `ARC-LAY-*`, `ARC-HEX-*`, `ARC-MOD-*`.

## 4. Carregamento de regras (somente o necessário)

| Condição | Carregar |
|---|---|
| sempre | `rules/universal/` (todos), `rules/architecture/general.md`, `references/evidence.md` |
| perfil layered / hexagonal / modular / custom | `profiles/architecture/<perfil>.md` + `rules/architecture/<perfil>.md` (custom: só o perfil) |
| Java/Quarkus | `profiles/stack/java-quarkus.md` → regras listadas nele |
| PostgreSQL | `profiles/stack/postgresql.md` → `rules/persistence/` |
| Angular / React / TypeScript | `profiles/stack/<stack>.md` → `rules/frontend/` correspondentes |
| testes, ferramentas, FIX, REVIEW | `rules/testing/` |
| proposta de correção ou plano | `references/conflict-resolution.md` |
| escrever artefato | `references/contracts.md` + template em `templates/` |

Em REVIEW de diff pequeno, carregue apenas as regras das áreas tocadas pelo diff.

## 5. Papéis

| Papel | Arquivo | Usado em |
|---|---|---|
| Architecture Auditor | `roles/ARCHITECTURE_AUDITOR.md` | INIT, AUDIT, REVIEW |
| Controlled Refactorer | `roles/CONTROLLED_REFACTORER.md` | FIX |
| Regression/Performance Validator | `roles/REGRESSION_VALIDATOR.md` | FIX (antes e depois), REVIEW |

Se a ferramenta oferecer subagentes configurados para estes papéis (ver `integrations/` no
repositório da base), delegue a eles. Sem subagentes, assuma o papel indicado em cada etapa do
workflow — isso **não** é isolamento de contexto, e o relatório não deve afirmar o contrário.

## 6. Utilitários determinísticos (Python 3.10+, só biblioteca padrão, somente leitura)

```bash
python3 <dir-da-skill>/scripts/detect_stack.py <projeto> [--format json|markdown]
python3 <dir-da-skill>/scripts/arch_signals.py <projeto> [--format json|markdown]
python3 <dir-da-skill>/scripts/tree_snapshot.py create <projeto> --output <arquivo-fora-do-projeto>
python3 <dir-da-skill>/scripts/tree_snapshot.py compare <projeto> --snapshot <arquivo> [--allow <glob> ...]
python3 <dir-da-skill>/scripts/fix_gate.py check <plano.md> [--project <projeto>] [--changed-from-git]
```

Saídas desses scripts são sinais (E4) ou verificações (E2), nunca substitutos da leitura do código.

## 7. Saída

- Use os templates de `templates/` e o formato de achado de `references/contracts.md` §5.
- Classifique cada achado com severidade **e** estado conforme `references/evidence.md`.
- Liste o que foi e o que **não** foi executado. Não invente medições.
- Riscos de segurança: registre e encaminhe para análise especializada; não os trate aqui.
- Nunca faça commit, push, tag, deploy ou migration.
