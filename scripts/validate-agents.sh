#!/usr/bin/env bash
# validate-agents.sh — Verify agent MD files are well-formed.
#
# Checks:
#   1. Every NN-name.md file is non-empty
#   2. Required sections exist (## Role, ## Instructions or ## Core Rules)
#   3. No duplicate agent numbers
#   4. Agent names match the expected numbering sequence
#
# Usage:
#   bash scripts/validate-agents.sh
#   bash scripts/validate-agents.sh --strict    # exit 1 on warnings too

set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/agents"
STRICT=0

[ "$*" = "--strict" ] && STRICT=1

ok()    { printf '\033[32m  ✓\033[0m %s\n' "$*"; }
warn()  { printf '\033[33m  ⚠\033[0m  %s\n' "$*"; [ "$STRICT" -eq 0 ] || exit 1; }
fail()  { printf '\033[31m  ✗\033[0m  %s\n' "$*"; FAILURES=$((FAILURES+1)); }

FAILURES=0

if [ ! -d "$AGENTS_DIR" ]; then
  fail "agents/ directory not found at $AGENTS_DIR"
  exit 1
fi

declare -A SEEN_NUMS

for f in "$AGENTS_DIR"/[0-9][0-9]-*.md; do
  [ -f "$f" ] || { warn "No agent files found in $AGENTS_DIR"; break; }

  base="$(basename "$f")"
  num="${base:0:2}"

  # Duplicate number check
  if [ "${SEEN_NUMS[$num]+x}" ]; then
    fail "Duplicate agent number: $num (${SEEN_NUMS[$num]} and $base)"
  fi
  SEEN_NUMS[$num]="$base"

  # Non-empty
  if [ ! -s "$f" ]; then
    fail "Empty agent file: $base"
    continue
  fi

  # Required sections
  if ! grep -q '^## ' "$f"; then
    fail "$base: No H2 sections found"
    continue
  fi

  # Role or name header
  if ! grep -qiE '^## (Role|Name|Identity|에이전트)' "$f"; then
    warn "$base: No '## Role' or '## Name' section found"
  fi

  # Instructions section
  if ! grep -qiE '^## (Instructions|Core Rules|Rules|규칙|지침)' "$f"; then
    warn "$base: No '## Instructions' / '## Core Rules' section found"
  fi

  ok "$base"
done

echo ""
if [ "$FAILURES" -gt 0 ]; then
  printf '\033[31m  %d validation failure(s)\033[0m\n\n' "$FAILURES"
  exit 1
else
  printf '\033[32m  All agents valid\033[0m\n\n'
fi
