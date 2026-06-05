#!/usr/bin/env bash
# install-snippet.sh
# snippet 도구를 Mac/Linux 환경에 설치한다.
#
# 실행 방법:
#   bash tools/install-snippet.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMMANDS_DIR="$HOME/.claude/commands"

echo ""
echo "=== snippet 설치 ==="
echo ""

# ── 1. Python 3 확인 ──────────────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null && "$cmd" --version 2>&1 | grep -q "Python 3"; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "[ERROR] Python 3가 필요합니다."
    echo "  macOS:  brew install python"
    echo "  Ubuntu: sudo apt install python3"
    exit 1
fi
echo "[OK] Python 확인됨: $PYTHON ($($PYTHON --version))"

# ── 2. .claude/commands/ 디렉터리 생성 ────────────────────────────────────────
mkdir -p "$COMMANDS_DIR"
echo "[OK] $COMMANDS_DIR"

# ── 3. /snippet 슬래시 커맨드 설치 ───────────────────────────────────────────
cp -f "$REPO_ROOT/.claude/commands/snippet.md" "$COMMANDS_DIR/snippet.md"
echo "[OK] 슬래시 커맨드 설치됨: $COMMANDS_DIR/snippet.md"

# ── 4. 기본 스니펫 임포트 ────────────────────────────────────────────────────
echo ""
printf "기본 스니펫(13개)을 가져오겠습니까? [Y/n] "
read -r answer
if [ -z "$answer" ] || echo "$answer" | grep -iq "^y"; then
    "$PYTHON" "$REPO_ROOT/tools/snippet.py" import "$REPO_ROOT/snippets/defaults.json"
    echo "[OK] 기본 스니펫 임포트 완료"
fi

# ── 5. snippet 단축 명령 등록 (shell profile) ─────────────────────────────────
SNIPPET_FUNC="
# snippet — Claude Code 프롬프트 매니저
snippet() { \"$PYTHON\" \"$REPO_ROOT/tools/snippet.py\" \"\$@\"; }"

# zsh / bash 둘 다 지원
for PROFILE in "$HOME/.zshrc" "$HOME/.bashrc"; do
    if [ -f "$PROFILE" ]; then
        if ! grep -q "Claude Code 프롬프트 매니저" "$PROFILE"; then
            echo "$SNIPPET_FUNC" >> "$PROFILE"
            echo "[OK] snippet 함수 등록됨: $PROFILE"
        else
            echo "[OK] snippet 함수 이미 등록되어 있음: $PROFILE"
        fi
    fi
done

# ── 완료 ──────────────────────────────────────────────────────────────────────
echo ""
echo "설치 완료!"
echo ""
echo "사용 방법:"
echo "  터미널  : snippet list"
echo "  터미널  : snippet run full-pipeline"
echo "  Claude  : /snippet list"
echo "  Claude  : /snippet run full-pipeline"
echo ""
echo "새 터미널을 열거나 'source ~/.zshrc' (또는 ~/.bashrc)를 실행하면 활성화됩니다."
echo ""
