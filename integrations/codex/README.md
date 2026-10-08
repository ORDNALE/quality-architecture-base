# Adaptador — Codex CLI

Formato conferido em codex-cli 0.161.0 (documentação oficial de skills e subagentes, strings do
binário e `codex debug prompt-input`).

## O que este adaptador contém

| Arquivo | Função |
|---|---|
| `../../skills/quality-review/agents/openai.yaml` | Metadados opcionais da skill para o Codex (`interface`, `policy`). Outras ferramentas ignoram. |
| `agents/quality_auditor.toml` | Agente customizado Architecture Auditor, `sandbox_mode = "read-only"`. |
| `agents/quality_refactorer.toml` | Agente customizado Controlled Refactorer (sandbox herdado da sessão). |
| `agents/quality_validator.toml` | Agente customizado Regression/Performance Validator (sandbox herdado; precisa gravar em `target/`). |

Os agentes apontam para os arquivos da skill; nenhuma regra é copiada para os `.toml`.

## Locais reconhecidos pelo Codex

| Escopo | Skill | Agentes customizados |
|---|---|---|
| Projeto | `<repo>/.agents/skills/quality-review/` (do diretório atual até a raiz do repositório) | `<repo>/.codex/agents/*.toml` |
| Usuário | `~/.agents/skills/quality-review/` | `~/.codex/agents/*.toml` |

## Instalação

```bash
# no projeto consumidor (cópia: nome da skill = quality-review)
scripts/install.sh --tool codex --scope project --project /caminho/do/projeto --with-agents

# para o usuário
scripts/install.sh --tool codex --scope user --with-agents
```

Invocação: `$quality-review AUDIT` (ou `/skills` para escolher). Agentes: peça pelo nome, por
exemplo "Use o quality_auditor para auditar o pacote vendas".

## Por que cópia e não symlink no Codex

Verificado com `codex debug prompt-input`: quando `.agents/skills/quality-review` é um symlink para
este repositório, o Codex segue o link, encontra `.claude-plugin/plugin.json` e lista a skill como
`quality-architecture-base:quality-review`. Com cópia, o nome é `quality-review`. Por isso o
instalador usa cópia para o Codex por padrão (`--mode auto`). Para atualizar a cópia:
`git pull` neste repositório e o mesmo comando de instalação com `--update`.

## Estado de verificação

- Descoberta da skill (cópia e symlink): **verificada** com `codex debug prompt-input` (sem chamada
  ao modelo).
- Agentes customizados: arquivos seguem o formato documentado (`name`, `description`,
  `developer_instructions`); a descoberta **não** aparece em `prompt-input` (ferramentas não são
  renderizadas) e **não foi verificada** em execução real nesta versão.
