# Instalação

A skill é uma pasta (`skills/quality-review/`). Instalar significa disponibilizar essa pasta onde
cada ferramenta procura skills — por **symlink** (atualiza com `git pull`) ou **cópia** (estável,
versionável no projeto consumidor). Nada no projeto consumidor é editado.

## 1. Obter a base

```bash
git clone https://github.com/ORDNALE/quality-architecture-base.git
cd quality-architecture-base
python3 scripts/validate_repo.py          # opcional: integridade da base
python3 -m unittest discover -s tests     # opcional: testes da base
```

## 2. Instalador

```text
scripts/install.sh --tool claude|codex|both --scope project|user [--project <dir>]
                   [--mode auto|symlink|copy] [--with-agents] [--update] [--uninstall] [--dry-run]
```

| Ferramenta | Escopo | Skill | Subagentes (`--with-agents`) | Modo padrão |
|---|---|---|---|---|
| Claude Code | projeto | `<dir>/.claude/skills/quality-review` | `<dir>/.claude/agents/quality-*.md` | symlink |
| Claude Code | usuário | `~/.claude/skills/quality-review` | `~/.claude/agents/quality-*.md` | symlink |
| Codex CLI | projeto | `<dir>/.agents/skills/quality-review` | `<dir>/.codex/agents/quality_*.toml` | cópia |
| Codex CLI | usuário | `~/.agents/skills/quality-review` | `~/.codex/agents/quality_*.toml` | cópia |

Garantias do instalador:

- nunca sobrescreve arquivo/diretório que ele não criou;
- `--update` substitui apenas instalações anteriores dele (symlink para esta base, diretório com
  marcador `.qab-install`, agente com o mesmo `name`);
- `--uninstall` remove apenas symlinks para esta base, cópias com marcador e agentes idênticos aos
  originais;
- recusa instalar dentro da própria base;
- não altera `.gitignore`, `AGENTS.md`, `CLAUDE.md` nem código.

### Symlink ou cópia?

A skill instalada é **gerenciada pelo framework**, nos dois modos: não a edite durante o trabalho em
projetos consumidores. Com symlink, editar a skill instalada altera a base original; com cópia, a
edição se perde no próximo `--update`. Personalizações locais pertencem ao `.quality/` do projeto
(`PROJECT_PROFILE.md`, `ARCHITECTURE_CONTRACT.md`); mudanças na skill são feitas no repositório
da base.

| | Symlink | Cópia |
|---|---|---|
| Atualização | automática com `git pull` | `--update` após `git pull` |
| Versionar no projeto consumidor | não (aponta para um caminho local) | sim |
| Nome no Codex | `quality-architecture-base:quality-review` (o Codex segue o link e detecta o manifesto de plugin) | `quality-review` |
| Nome no Claude Code | `quality-review` | `quality-review` |

## 3. Claude Code

### Por diretório (recomendado para uso diário)

```bash
scripts/install.sh --tool claude --scope project --project /caminho/do/projeto --with-agents
# ou
scripts/install.sh --tool claude --scope user --with-agents
```

Reinicie a sessão do Claude Code no projeto e use `/quality-review INIT`.

### Como plugin

O repositório é também um plugin e um marketplace de um plugin:

```bash
claude plugin marketplace add ORDNALE/quality-architecture-base
claude plugin install quality-architecture-base@quality-architecture-base
```

Ou, dentro de uma sessão: `/plugin marketplace add ORDNALE/quality-architecture-base` e
`/plugin install quality-architecture-base@quality-architecture-base`.

Para desenvolvimento local sem instalar: `claude --plugin-dir /caminho/quality-architecture-base`.

Com plugin, a skill é `/quality-architecture-base:quality-review` e os subagentes são
`quality-architecture-base:quality-auditor`, `...:quality-refactorer`, `...:quality-validator`.

## 4. Codex CLI

```bash
scripts/install.sh --tool codex --scope project --project /caminho/do/projeto --with-agents
# ou
scripts/install.sh --tool codex --scope user --with-agents
```

Reinicie a sessão do Codex e use `$quality-review INIT` (ou `/skills`). O Codex procura skills em
`.agents/skills` do diretório atual até a raiz do repositório, e em `~/.agents/skills`.

Agentes customizados: `.codex/agents/*.toml` (projeto) ou `~/.codex/agents/*.toml` (usuário). Peça
pelo nome: "Use o quality_auditor para auditar o pacote vendas".

## 5. Remover

```bash
scripts/install.sh --tool both --scope project --project /caminho/do/projeto --with-agents --uninstall
claude plugin uninstall quality-architecture-base@quality-architecture-base   # se instalou como plugin
```

## 6. Estado de verificação (2026-10-08)

| Item | Situação | Como foi verificado |
|---|---|---|
| Manifesto de plugin, marketplace, skill e subagentes Claude | **verificado** | `claude plugin validate --strict` (Claude Code 2.1.295) |
| Instalação do plugin a partir de marketplace local | **verificado** | `claude plugin marketplace add <dir>` + `install` em configuração isolada; `details`: Skills (1), Agents (3) |
| Instalação do plugin a partir do GitHub | **não verificado** | o repositório remoto ainda não contém estes arquivos (nenhum push foi feito) |
| Descoberta da skill no Codex (cópia e symlink) | **verificado** | `codex debug prompt-input` (codex-cli 0.161.0) |
| Modos AUDIT/REVIEW/INIT/FIX com modelos reais | **verificado por amostragem** | ver `docs/VALIDATION.md` §5 |
| Agentes customizados do Codex | **não verificado em execução** | formato conforme documentação oficial |
| Instalador (`install.sh`) | **verificado** | testes automatizados em `tests/test_install.py` |
