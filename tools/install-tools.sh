#!/usr/bin/env bash
# install-tools.sh
# Installs all three Claude Code productivity tools:
#   snippet       -- personal prompt manager
#   claude-handoff -- session continuity
#   claude-cost   -- cost predictor & tracker
#
# Usage:
#   bash tools/install-tools.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMMANDS_DIR="$HOME/.claude/commands"

echo ""
echo "========================================"
echo " Claude Code Tools Installer"
echo "========================================"
echo ""

# ── 1. Python 3 check ─────────────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null && "$cmd" --version 2>&1 | grep -q "Python 3"; then
        PYTHON="$cmd"; break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "[ERROR] Python 3 is required."
    echo "  macOS:  brew install python"
    echo "  Ubuntu: sudo apt install python3"
    exit 1
fi
echo "[OK] Python: $PYTHON ($($PYTHON --version))"

# ── 2. ~/.claude/commands/ ────────────────────────────────────────────────────
mkdir -p "$COMMANDS_DIR"
for cmd in snippet.md handoff.md cost.md; do
    cp -f "$REPO_ROOT/.claude/commands/$cmd" "$COMMANDS_DIR/$cmd"
done
echo "[OK] Slash commands installed: /snippet  /handoff  /cost"

# ── 3. Import default snippets ────────────────────────────────────────────────
"$PYTHON" "$REPO_ROOT/tools/snippet.py" import "$REPO_ROOT/snippets/defaults.json" 2>/dev/null || true
echo "[OK] Default snippets imported (20)"

# ── 4. Register shell functions ───────────────────────────────────────────────
FUNC_DEF="
# ── Claude Code Tools ──────────────────────────────────────────────────────
snippet()        { \"$PYTHON\" \"$REPO_ROOT/tools/snippet.py\" \"\$@\"; }
claude-handoff() { \"$PYTHON\" \"$REPO_ROOT/tools/claude-handoff.py\" \"\$@\"; }
claude-cost()    { \"$PYTHON\" \"$REPO_ROOT/tools/claude-cost.py\" \"\$@\"; }
# ──────────────────────────────────────────────────────────────────────────"

for PROFILE in "$HOME/.zshrc" "$HOME/.bashrc"; do
    if [ -f "$PROFILE" ] && ! grep -q "Claude Code Tools" "$PROFILE"; then
        echo "$FUNC_DEF" >> "$PROFILE"
        echo "[OK] Shell functions registered: $PROFILE"
    elif [ -f "$PROFILE" ]; then
        echo "[OK] Already registered: $PROFILE"
    fi
done

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo " Installation complete!"
echo "========================================"
echo ""
echo "Terminal commands:"
echo "  snippet list"
echo "  claude-handoff save"
echo "  claude-handoff load | claude"
echo "  claude-cost estimate --snippet full-pipeline"
echo ""
echo "Inside Claude Code:"
echo "  /snippet list"
echo "  /handoff save"
echo "  /cost estimate full-pipeline"
echo ""
echo "Activate: source ~/.zshrc  (or ~/.bashrc)"
echo ""
