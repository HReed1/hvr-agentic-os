#!/usr/bin/env bash
# Install the AI Engineering scaffold plugin into one or more agent harnesses.
#
# Installs by symlinking (so `git pull` in hvr-agentic-os updates every harness):
#   antigravity  ~/.gemini/config/plugins/ai-engineering-scaffold  -> this plugin
#   claude       ~/.claude/skills/bootstrap-ai-engineering          -> skill dir
#                (or use the marketplace: /plugin marketplace add HReed1/hvr-agentic-os)
#   codex        ~/.agents/skills/bootstrap-ai-engineering          -> skill dir
#   copilot      ~/.copilot/extensions/ai-engineering-scaffold      -> copilot/ extension
#                ~/.copilot/skills/bootstrap-ai-engineering         -> skill dir
#
# Usage: ./install.sh --harness antigravity|claude|codex|copilot|all [--uninstall]
set -e

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$PLUGIN_DIR/skills/bootstrap-ai-engineering"
HARNESS_ARGS=""
UNINSTALL=0

usage() { sed -n '2,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
    case "$1" in
        --harness) [ $# -ge 2 ] || { usage; exit 1; }; HARNESS_ARGS="$HARNESS_ARGS,$2"; shift 2 ;;
        --harness=*) HARNESS_ARGS="$HARNESS_ARGS,${1#*=}"; shift ;;
        --uninstall) UNINSTALL=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
    esac
done
[ -n "$HARNESS_ARGS" ] || { usage; exit 1; }
HARNESS_ARGS="$(echo "$HARNESS_ARGS" | tr ',' ' ' | tr '[:upper:]' '[:lower:]')"
case " $HARNESS_ARGS " in *" all "*) HARNESS_ARGS="antigravity claude codex copilot" ;; esac

# link <source> <destination>
link() {
    local src="$1" dst="$2"
    if [ "$UNINSTALL" = 1 ]; then
        if [ -L "$dst" ]; then rm "$dst"; echo "  removed $dst"; else echo "  (not installed) $dst"; fi
        return
    fi
    mkdir -p "$(dirname "$dst")"
    if [ -e "$dst" ] && [ ! -L "$dst" ]; then
        echo "  [SKIP] $dst exists and is not a symlink; remove it manually to install." >&2
        return
    fi
    ln -sfn "$src" "$dst"
    echo "  linked $dst -> $src"
}

# Remove a legacy symlink only if it is dangling (its target no longer exists).
remove_dangling() {
    if [ -L "$1" ] && [ ! -e "$1" ]; then rm "$1"; echo "  removed dangling legacy link $1"; fi
}

for h in $HARNESS_ARGS; do
    case "$h" in
        antigravity)
            echo "[antigravity]"
            link "$PLUGIN_DIR" "$HOME/.gemini/config/plugins/ai-engineering-scaffold"
            ;;
        claude)
            echo "[claude]"
            link "$SKILL_DIR" "$HOME/.claude/skills/bootstrap-ai-engineering"
            echo "  Alternatively, install as a Claude Code plugin:"
            echo "    /plugin marketplace add HReed1/hvr-agentic-os"
            echo "    /plugin install ai-engineering-scaffold@hvr-agentic-os"
            ;;
        codex)
            echo "[codex]"
            link "$SKILL_DIR" "$HOME/.agents/skills/bootstrap-ai-engineering"
            ;;
        copilot)
            echo "[copilot]"
            remove_dangling "$HOME/.copilot/extensions/project-bootstrap"
            link "$PLUGIN_DIR/copilot" "$HOME/.copilot/extensions/ai-engineering-scaffold"
            link "$SKILL_DIR" "$HOME/.copilot/skills/bootstrap-ai-engineering"
            ;;
        *) echo "Unknown harness '$h' (expected: antigravity, claude, codex, copilot, all)" >&2; exit 1 ;;
    esac
done

[ "$UNINSTALL" = 1 ] && exit 0
echo ""
echo "Done. In your agent, ask: \"Bootstrap the AI engineering scaffold in this repo\"."
echo "Or run the script directly: bash \"$SKILL_DIR/assets/bin/bootstrap_ai_engineering.sh\" --help"
