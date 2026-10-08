# Adaptador — Claude Code

Formato conferido em Claude Code 2.1.295 (documentação oficial de skills, subagentes e plugins, e
`claude plugin validate --strict`).

## O que este adaptador contém

| Arquivo | Função |
|---|---|
| `../../.claude-plugin/plugin.json` | Manifesto do plugin `quality-architecture-base` (raiz do repositório = raiz do plugin). Skill e subagentes são carregados das pastas padrão `skills/` e `agents/`. |
| `../../.claude-plugin/marketplace.json` | Marketplace de um plugin só, para instalar direto do GitHub. |
| `../../agents/quality-auditor.md` | Subagente Architecture Auditor — ferramentas `Read, Grep, Glob, Bash` (sem edição). |
| `../../agents/quality-refactorer.md` | Subagente Controlled Refactorer — inclui `Edit, Write`; exige `fix_gate.py` = 0. |
| `../../agents/quality-validator.md` | Subagente Regression/Performance Validator — sem edição. |

Os subagentes **não** duplicam regras: eles apontam para `roles/`, `workflows/` e `references/` da
skill. Em instalação via plugin, o caminho é resolvido por `${CLAUDE_PLUGIN_ROOT}`; nas instalações
por diretório, pelos caminhos `.claude/skills/quality-review` ou `~/.claude/skills/quality-review`.

## Opções de instalação

| Opção | Comando | Invocação |
|---|---|---|
| Plugin via marketplace (GitHub) | `claude plugin marketplace add ORDNALE/quality-architecture-base` e `claude plugin install quality-architecture-base@quality-architecture-base` | `/quality-architecture-base:quality-review AUDIT` |
| Plugin local (desenvolvimento) | `claude --plugin-dir /caminho/quality-architecture-base` | `/quality-architecture-base:quality-review AUDIT` |
| Skill no projeto | `scripts/install.sh --tool claude --scope project --project <dir> [--with-agents]` | `/quality-review AUDIT` |
| Skill do usuário | `scripts/install.sh --tool claude --scope user [--with-agents]` | `/quality-review AUDIT` |

Subagentes: o Claude delega automaticamente pela descrição, ou explicitamente:
`@agent-quality-auditor` (instalação por diretório) / `@agent-quality-architecture-base:quality-auditor`
(plugin), ou "Use o subagente quality-auditor para ...".

Veja `docs/INSTALLATION.md` para o passo a passo e o estado de verificação de cada opção.

## Por que os subagentes ficam em `agents/` na raiz

Verificado em Claude Code 2.1.295: com os subagentes listados pela chave `agents` do `plugin.json`
(apontando para outra pasta), `claude plugin validate --strict` passou, mas a instalação via
marketplace carregou **0** agentes (`claude plugin details`). Com a pasta padrão `agents/`, os 3
agentes carregaram. Por isso a pasta padrão é usada e o validador da base proíbe a chave `agents`.

## Limites honestos

- `tools` sem `Edit/Write` impede edição pelas ferramentas de arquivo, mas o `Bash` continua
  disponível; o somente leitura do auditor é reforçado por instrução e verificado por
  `tree_snapshot.py`, não por sandbox.
- O nome do plugin prefixa a skill (`/quality-architecture-base:quality-review`). Para o nome curto
  `/quality-review`, instale a skill por diretório.
