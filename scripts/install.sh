#!/usr/bin/env bash
# Instala a skill quality-review (e opcionalmente os subagentes) para Claude Code e/ou Codex CLI.
#
# O instalador só cria symlinks ou cópias nos diretórios de descoberta das ferramentas. Ele não
# edita código, .gitignore, AGENTS.md/CLAUDE.md nem configurações do projeto consumidor, e não
# impõe perfil arquitetural: o perfil é criado depois, pelo modo INIT.
#
# Uso:
#   scripts/install.sh --tool claude|codex|both --scope project --project <dir> [opções]
#   scripts/install.sh --tool claude|codex|both --scope user [opções]
#
# Opções:
#   --mode auto|symlink|copy  auto (padrão): symlink para Claude, cópia para Codex (ver nota)
#   --with-agents             também instala os subagentes (Claude: .md; Codex: .toml)
#   --update                  substitui instalações anteriores feitas por este instalador
#   --uninstall               remove somente o que este instalador criou
#   --dry-run                 mostra o que faria, sem alterar nada
#   -h, --help                esta ajuda
#
# Destinos:
#   Claude, projeto:  <dir>/.claude/skills/quality-review    agentes: <dir>/.claude/agents/
#   Claude, usuário:  ~/.claude/skills/quality-review        agentes: ~/.claude/agents/
#   Codex,  projeto:  <dir>/.agents/skills/quality-review    agentes: <dir>/.codex/agents/
#   Codex,  usuário:  ~/.agents/skills/quality-review        agentes: ~/.codex/agents/
#
# Nota: o Codex segue o symlink até este repositório, encontra .claude-plugin/plugin.json e expõe a
# skill como "quality-architecture-base:quality-review". Com cópia, o nome é "quality-review".
#
# "Criado por este instalador" = symlink que aponta para este repositório, diretório de skill com o
# marcador .qab-install, ou arquivo de agente idêntico (uninstall) / com o mesmo name (update).
# Nada além disso é substituído ou removido.
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
SKILL_SRC="$BASE_DIR/skills/quality-review"
CLAUDE_AGENTS_SRC="$BASE_DIR/agents"
CODEX_AGENTS_SRC="$BASE_DIR/integrations/codex/agents"
MARKER=".qab-install"

TOOL="" SCOPE="" PROJECT="" MODE_OPT="auto"
WITH_AGENTS=0 DRY_RUN=0 UNINSTALL=0 UPDATE=0

usage() { sed -n '2,31p' "$0" | sed 's/^# \{0,1\}//'; }
die() { echo "erro: $*" >&2; exit 1; }
run() { if [[ $DRY_RUN -eq 1 ]]; then echo "[dry-run] $*"; else "$@"; fi; }
say() { if [[ $DRY_RUN -eq 1 ]]; then echo "[dry-run] $*"; else echo "$*"; fi; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool) TOOL="${2:-}"; shift 2 ;;
    --scope) SCOPE="${2:-}"; shift 2 ;;
    --project) PROJECT="${2:-}"; shift 2 ;;
    --mode) MODE_OPT="${2:-}"; shift 2 ;;
    --with-agents) WITH_AGENTS=1; shift ;;
    --update) UPDATE=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "opção desconhecida: $1 (use --help)" ;;
  esac
done

[[ "$TOOL" =~ ^(claude|codex|both)$ ]] || die "--tool deve ser claude, codex ou both"
[[ "$SCOPE" =~ ^(project|user)$ ]] || die "--scope deve ser project ou user"
[[ "$MODE_OPT" =~ ^(auto|symlink|copy)$ ]] || die "--mode deve ser auto, symlink ou copy"
[[ $UPDATE -eq 0 || $UNINSTALL -eq 0 ]] || die "--update e --uninstall são exclusivos"
[[ -f "$SKILL_SRC/SKILL.md" ]] || die "skill não encontrada em $SKILL_SRC"

if [[ "$SCOPE" == "project" ]]; then
  [[ -n "$PROJECT" ]] || die "--scope project exige --project <dir>"
  [[ -d "$PROJECT" ]] || die "diretório do projeto não existe: $PROJECT"
  ROOT="$(cd "$PROJECT" && pwd -P)"
  [[ "$ROOT" != "$BASE_DIR" ]] || die "não instale a skill dentro do próprio repositório da base"
else
  [[ -n "${HOME:-}" ]] || die "HOME não definido"
  ROOT="$HOME"
fi

mode_for() {  # $1 = claude|codex
  if [[ "$MODE_OPT" != "auto" ]]; then echo "$MODE_OPT"
  elif [[ "$1" == "codex" ]]; then echo "copy"
  else echo "symlink"; fi
}

agent_name() { sed -n 's/^name[[:space:]]*[:=][[:space:]]*"\{0,1\}\([A-Za-z0-9_-]*\)"\{0,1\}.*/\1/p' "$1" | head -n 1; }

# O destino existente foi criado por este instalador? $1 = origem, $2 = destino, $3 = uninstall|update
is_ours() {
  local src="$1" dst="$2" purpose="$3"
  if [[ -L "$dst" ]]; then [[ "$(readlink "$dst")" == "$BASE_DIR"/* ]]; return; fi
  if [[ -d "$dst" ]]; then [[ -f "$dst/$MARKER" ]]; return; fi
  if [[ -f "$dst" ]]; then
    if [[ "$purpose" == "uninstall" ]]; then cmp -s "$src" "$dst"; return; fi
    [[ -n "$(agent_name "$dst")" && "$(agent_name "$dst")" == "$(agent_name "$src")" ]]; return
  fi
  return 1
}

remove_path() {
  if [[ -d "$1" && ! -L "$1" ]]; then run rm -r "$1"; else run rm "$1"; fi
}

# Instala, atualiza ou remove um item: $1 = origem, $2 = destino, $3 = modo
place() {
  local src="$1" dst="$2" mode="$3"
  if [[ $UNINSTALL -eq 1 ]]; then
    if [[ -e "$dst" || -L "$dst" ]]; then
      if is_ours "$src" "$dst" uninstall; then remove_path "$dst"; say "removido: $dst"
      else echo "ignorado (não foi criado por este instalador): $dst"; fi
    fi
    return
  fi

  if [[ -e "$dst" || -L "$dst" ]]; then
    if [[ -L "$dst" && "$mode" == "symlink" && "$(readlink "$dst")" == "$src" ]]; then
      echo "já instalado: $dst -> $src"; return
    fi
    [[ $UPDATE -eq 1 ]] || die "$dst já existe (use --update para substituir uma instalação anterior deste instalador)"
    is_ours "$src" "$dst" update || die "$dst existe e não foi criado por este instalador; não será substituído"
    remove_path "$dst"
  fi

  run mkdir -p "$(dirname "$dst")"
  if [[ "$mode" == "symlink" ]]; then
    run ln -s "$src" "$dst"
  else
    run cp -R "$src" "$dst"
    if [[ -d "$src" ]]; then
      local version
      version="$(sed -n 's/^[[:space:]]*version:[[:space:]]*"\{0,1\}\([^"]*\)"\{0,1\}/\1/p' "$SKILL_SRC/SKILL.md" | head -n 1)"
      if [[ $DRY_RUN -eq 0 ]]; then
        printf 'source=%s\nversion=%s\n' "$BASE_DIR" "$version" > "$dst/$MARKER"
      fi
    fi
  fi
  say "instalado ($mode): $dst"
}

install_claude() {
  local mode; mode="$(mode_for claude)"
  place "$SKILL_SRC" "$ROOT/.claude/skills/quality-review" "$mode"
  if [[ $WITH_AGENTS -eq 1 ]]; then
    for f in "$CLAUDE_AGENTS_SRC"/*.md; do place "$f" "$ROOT/.claude/agents/$(basename "$f")" "$mode"; done
  fi
}

install_codex() {
  local mode; mode="$(mode_for codex)"
  place "$SKILL_SRC" "$ROOT/.agents/skills/quality-review" "$mode"
  if [[ $WITH_AGENTS -eq 1 ]]; then
    for f in "$CODEX_AGENTS_SRC"/*.toml; do place "$f" "$ROOT/.codex/agents/$(basename "$f")" "$mode"; done
  fi
}

case "$TOOL" in
  claude) install_claude ;;
  codex) install_codex ;;
  both) install_claude; install_codex ;;
esac

if [[ $UNINSTALL -eq 0 && $DRY_RUN -eq 0 ]]; then
  echo
  echo "Próximos passos (reinicie a sessão da ferramenta):"
  if [[ "$TOOL" != "codex" ]]; then echo "  Claude Code: /quality-review INIT"; fi
  if [[ "$TOOL" != "claude" ]]; then
    if [[ "$(mode_for codex)" == "copy" ]]; then echo "  Codex CLI:   \$quality-review INIT"
    else echo "  Codex CLI:   \$quality-architecture-base:quality-review INIT (nome com namespace via symlink)"; fi
  fi
  if [[ "$SCOPE" == "project" ]] && { [[ "$TOOL" != "codex" && "$(mode_for claude)" == "symlink" ]] || [[ "$TOOL" != "claude" && "$(mode_for codex)" == "symlink" ]]; }; then
    echo "  Observação: symlinks apontam para $BASE_DIR e não funcionam em outras máquinas;"
    echo "  para versionar a skill no projeto consumidor, use --mode copy."
  fi
  if [[ "$TOOL" != "claude" && "$(mode_for codex)" == "copy" ]]; then
    echo "  Atualização da cópia do Codex: git pull neste repositório e rode o mesmo comando com --update."
  fi
fi
