#!/usr/bin/env bash
# dogfood-build.sh — Build claude-tools from current checkout with provenance check.
#
# Injects GIT_SHA at build time so the binary can report the exact commit.
# Suppresses Cargo noise on stderr; re-runs with full output on failure.
# Prints the verified binary path on success. Usage:
#
#   BIN=$(bash scripts/dogfood-build.sh)
#   $BIN --version
#
# Dogfood with config isolation (avoids user config leaking into test):
#
#   CLAUDE_HOME=$(mktemp -d) $BIN env
#   trap 'rm -rf "$CLAUDE_HOME"' EXIT

set -euo pipefail

usage() { sed -n '2,13p' "$0" | sed 's/^# //; s/^#//'; }

if [[ $# -gt 0 ]]; then
  case "$1" in
    --help|-h) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUST_DIR="$REPO_ROOT/rust"
PROFILE="${BUILD_PROFILE:-debug}"
BINARY="$RUST_DIR/target/${PROFILE}/claude-tools"
EXPECTED_SHA="$(git -C "$REPO_ROOT" rev-parse --short HEAD)"

echo "  Building claude-tools from ${REPO_ROOT}" >&2
echo "  Commit: $(git -C "$REPO_ROOT" log --oneline -1)" >&2
echo "  Profile: ${PROFILE}" >&2

CARGO_FLAGS=(build --workspace)
[ "$PROFILE" = "release" ] && CARGO_FLAGS+=(--release)

if ! GIT_SHA="$EXPECTED_SHA" CARGO_TERM_COLOR=always \
    cargo "${CARGO_FLAGS[@]}" \
    --manifest-path "$RUST_DIR/Cargo.toml" -q 2>/dev/null; then
  echo " Build failed — rerunning with output:" >&2
  GIT_SHA="$EXPECTED_SHA" cargo "${CARGO_FLAGS[@]}" \
    --manifest-path "$RUST_DIR/Cargo.toml" 2>&1 | sed 's/^/  /' >&2
  exit 1
fi

[[ -x "$BINARY" ]] || { echo " Binary not found: $BINARY" >&2; exit 1; }

BINARY_SHA=$("$BINARY" version 2>/dev/null | grep -o 'sha:[a-f0-9]*' | cut -d: -f2 || echo "null")

if [[ "$BINARY_SHA" == "null" || -z "$BINARY_SHA" ]]; then
  echo "  ⚠  Provenance check skipped (binary has no SHA output)" >&2
else
  if [[ "$BINARY_SHA" != "$EXPECTED_SHA" ]]; then
    echo "  Provenance mismatch: binary=${BINARY_SHA}, HEAD=${EXPECTED_SHA}" >&2
    exit 1
  fi
  echo "  Binary verified: ${BINARY_SHA} == HEAD" >&2
fi

echo "" >&2
echo "  Binary: ${BINARY}" >&2
echo "  Run time overhead vs pre-built: ~1s for cargo run vs ~5ms for binary." >&2
echo "" >&2
echo "$BINARY"
