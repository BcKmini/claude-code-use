#!/usr/bin/env bash
# fmt.sh — Format all code in the repo.
#
# Usage:
#   bash scripts/fmt.sh           # format in place
#   bash scripts/fmt.sh --check   # exit 1 if any file needs reformatting (CI mode)

set -euo pipefail

CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUST_DIR="$REPO_ROOT/rust"

ok()   { printf '\033[32m  ✓\033[0m %s\n' "$*"; }
fail() { printf '\033[31m  ✗\033[0m  %s\n' "$*"; }

FAILURES=0

# ── Rust ──────────────────────────────────────────────────────────────────
if command -v cargo &>/dev/null && [ -d "$RUST_DIR" ]; then
  if [ "$CHECK" -eq 1 ]; then
    if cargo fmt --manifest-path "$RUST_DIR/Cargo.toml" --all --check; then
      ok "Rust: cargo fmt check passed"
    else
      fail "Rust: cargo fmt check failed — run: bash scripts/fmt.sh"
      FAILURES=$((FAILURES+1))
    fi
  else
    cargo fmt --manifest-path "$RUST_DIR/Cargo.toml" --all
    ok "Rust: cargo fmt applied"
  fi
else
  printf '  skipping Rust (cargo not found)\n'
fi

# ── Python ─────────────────────────────────────────────────────────────────
if command -v ruff &>/dev/null; then
  if [ "$CHECK" -eq 1 ]; then
    if ruff format --check "$REPO_ROOT/tools/" 2>/dev/null; then
      ok "Python: ruff format check passed"
    else
      fail "Python: ruff format check failed — run: bash scripts/fmt.sh"
      FAILURES=$((FAILURES+1))
    fi
  else
    ruff format "$REPO_ROOT/tools/" 2>/dev/null && ok "Python: ruff format applied"
  fi
else
  printf '  skipping Python (ruff not found)\n'
fi

echo ""
[ "$FAILURES" -eq 0 ] || exit 1
