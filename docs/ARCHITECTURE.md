# Arquitetura interna da Quality Architecture Base

## Objetivo de projeto

Uma única fonte de regras, neutra em relação ao fornecedor, consumida por adaptadores finos para
Claude Code e Codex CLI. Nada nesta base conhece um projeto consumidor específico.

## Visão em camadas

```text
┌──────────────────────────── Adaptadores (específicos de ferramenta) ───────────────────────────┐
│ .claude-plugin/ (plugin + marketplace)   agents/*.md (subagentes Claude, pasta padrão do plugin)│
│ skills/quality-review/agents/openai.yaml (metadados Codex)  integrations/codex/agents/*.toml   │
└───────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                │ apontam para (nunca copiam regras)
┌───────────────────────────── Núcleo neutro: skills/quality-review/ ───────────────────────────┐
│ SKILL.md  → roteador enxuto (modo → workflow → regras/perfis sob demanda)                    │
│ workflows/  INIT, AUDIT, FIX, REVIEW                                                          │
│ roles/      Architecture Auditor, Controlled Refactorer, Regression/Performance Validator     │
│ rules/      universal, architecture, backend, persistence, performance, frontend, testing    │
│ profiles/   architecture/ (layered, hexagonal, modular, custom) · stack/ (java-quarkus, ...)  │
│ references/ contratos, evidência, resolução de conflitos, guardrails                         │
│ templates/  perfil, contrato, relatórios, plano, regressão, estado, ArchUnit                 │
│ scripts/    utilitários determinísticos somente leitura (detecção, sinais, snapshot, gate)    │
└───────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                │ lê (nunca grava regras)
┌────────────────────────── Projeto consumidor (fora deste repositório) ────────────────────────┐
│ .quality/PROJECT_PROFILE.md · ARCHITECTURE_CONTRACT.md · reports/ · plans/ · QUALITY_STATE.md │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Por que as regras ficam dentro de `skills/quality-review/`

A estrutura sugerida originalmente colocava `rules/`, `profiles/`, `workflows/`, `agents/` e
`templates/` na raiz do repositório. Isso foi alterado por motivo técnico verificado:

1. **Claude Code e Codex instalam uma skill como uma pasta** (`.claude/skills/<nome>/`,
   `.agents/skills/<nome>/`, cópia em cache de plugin). Arquivos fora da pasta da skill não estão
   garantidos após a instalação. Uma skill que referencia `../../rules` quebra quando copiada.
2. Mantendo tudo dentro da pasta da skill, **a mesma pasta** é instalada nas duas ferramentas
   (por symlink ou cópia) e continua sendo a única fonte de regras.
3. **`agents/` dentro de uma skill é reservado pelo Codex** para `agents/openai.yaml`. Por isso os
   papéis especializados ficam em `roles/`, e os subagentes nativos ficam em `integrations/`.

Mapeamento da estrutura sugerida para a implementada:

| Sugerido | Implementado | Motivo |
|---|---|---|
| `rules/` | `skills/quality-review/rules/` | portabilidade da skill |
| `profiles/` | `skills/quality-review/profiles/` | idem |
| `workflows/` | `skills/quality-review/workflows/` | idem |
| `agents/` | papéis neutros em `skills/quality-review/roles/`; `agents/` na raiz contém os subagentes do Claude Code (pasta padrão do plugin); agentes do Codex em `integrations/codex/agents/` | dentro da skill, `agents/` é reservado ao Codex; na raiz, é a pasta que o plugin do Claude carrega |
| `templates/` | `skills/quality-review/templates/` | o agente copia templates para o projeto consumidor |
| `skills/quality-review/references/` | mantido | contratos e critérios transversais |
| — | `scripts/` (raiz) | instalação e validação **da própria base** (não vão para o consumidor) |
| — | `skills/quality-review/scripts/` | utilitários usados **durante** INIT/AUDIT/FIX/REVIEW |

## Carregamento sob demanda

`SKILL.md` é deliberadamente curto. Ele identifica o modo pedido, carrega um workflow e, a partir do
perfil do projeto, apenas os arquivos de regra e perfis pertinentes. Um AUDIT de backend Quarkus não
carrega regras de React; um REVIEW de um diff pequeno carrega só as regras tocadas pelo diff.

## Papéis e subagentes

Os três papéis (`roles/*.md`) são instruções neutras. Eles podem ser usados de duas formas:

- **Sem subagentes:** o agente principal executa o workflow e assume o papel indicado em cada etapa.
  O workflow deixa explícito que isso **não** é isolamento real de contexto.
- **Com subagentes nativos:** Claude Code (`.claude/agents/*.md`) e Codex (`.codex/agents/*.toml`)
  suportam agentes customizados. Os adaptadores (`agents/` na raiz para o Claude Code,
  `integrations/codex/agents/` para o Codex) apenas configuram ferramentas e permissões (ex.:
  auditor sem ferramentas de edição) e mandam o subagente ler o papel na skill.

## Scripts determinísticos

Scripts em `skills/quality-review/scripts/` usam somente a biblioteca padrão do Python 3.10+, não
acessam a rede e não modificam o projeto analisado:

| Script | Uso | Escrita |
|---|---|---|
| `detect_stack.py` | INIT/AUDIT: versões declaradas (Maven, npm, Docker, arquivos de versão) | nenhuma (stdout) |
| `arch_signals.py` | INIT/AUDIT: sinais heurísticos de camadas e riscos de persistência em Java | nenhuma (stdout) |
| `tree_snapshot.py` | AUDIT/REVIEW/FIX: prova de que fontes não mudaram (ou só mudaram no escopo) | só o arquivo de snapshot indicado, fora do projeto |
| `fix_gate.py` | FIX: valida autorização e escopo de arquivos alterados | nenhuma (stdout) |

Saídas desses scripts são **sinais**, não achados confirmados. Ver `references/evidence.md`.
