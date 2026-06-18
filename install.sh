#!/usr/bin/env bash
# Claude Code Multi-Agent System — Installer
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/BcKmini/claude-code-use/main/install.sh | bash
#   curl -fsSL ... | bash -s -- --version v1.2.0   # specific version
#   curl -fsSL ... | bash -s -- --no-binary         # agents + tools only, skip Rust binary
set -euo pipefail

REPO="BcKmini/claude-code-use"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"
VERSION=""
INSTALL_BINARY=true

# ── parse args ───────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="$2"; shift 2 ;;
    --no-binary) INSTALL_BINARY=false; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# ── helpers ──────────────────────────────────────────────────────────────────
info()    { printf '\033[1;36m[claude-install]\033[0m %s\n' "$*"; }
success() { printf '\033[1;32m[claude-install]\033[0m %s\n' "$*"; }
warn()    { printf '\033[1;33m[claude-install]\033[0m %s\n' "$*" >&2; }
error()   { printf '\033[1;31m[claude-install]\033[0m %s\n' "$*" >&2; exit 1; }

need_cmd() { command -v "$1" &>/dev/null || error "Required command not found: $1"; }

# ── detect OS / arch ─────────────────────────────────────────────────────────
detect_target() {
  local os arch
  os="$(uname -s)"
  arch="$(uname -m)"

  case "$os" in
    Linux)
      case "$arch" in
        x86_64) echo "x86_64-unknown-linux-musl" ;;
        *) error "Unsupported Linux arch: $arch. Build from source with: cargo build --release" ;;
      esac
      ;;
    Darwin)
      case "$arch" in
        x86_64)  echo "x86_64-apple-darwin" ;;
        arm64)   echo "aarch64-apple-darwin" ;;
        *) error "Unsupported macOS arch: $arch" ;;
      esac
      ;;
    *) error "Unsupported OS: $os. Use install.ps1 on Windows." ;;
  esac
}

# ── resolve version ───────────────────────────────────────────────────────────
resolve_version() {
  if [ -n "$VERSION" ]; then
    # strip leading 'v' if user passed it
    echo "${VERSION#v}"
  else
    need_cmd curl
    curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
      | grep '"tag_name"' \
      | sed -E 's/.*"v([^"]+)".*/\1/'
  fi
}

# ── install agents + slash commands ──────────────────────────────────────────
install_agents() {
  local version="$1"
  info "Installing agents v${version}..."

  need_cmd curl unzip

  local tmp
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT

  curl -fsSL \
    "https://github.com/${REPO}/releases/download/v${version}/claude-agents-${version}.zip" \
    -o "$tmp/agents.zip"

  unzip -q "$tmp/agents.zip" -d "$tmp/extracted"

  mkdir -p "${CLAUDE_HOME}/agents" "${CLAUDE_HOME}/commands"

  # copy agents
  local count=0
  for f in "$tmp/extracted/agents/"*.md; do
    cp "$f" "${CLAUDE_HOME}/agents/"
    count=$((count + 1))
  done
  success "  ✓ $count agents → ${CLAUDE_HOME}/agents/"

  # copy slash commands
  count=0
  for f in "$tmp/extracted/.claude/commands/"*.md; do
    [ -f "$f" ] || continue
    cp "$f" "${CLAUDE_HOME}/commands/"
    count=$((count + 1))
  done
  success "  ✓ $count slash commands → ${CLAUDE_HOME}/commands/"
}

# ── install Python tools ─────────────────────────────────────────────────────
install_python_tools() {
  local version="$1"
  info "Installing Python tools v${version}..."

  local tmp
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT

  curl -fsSL \
    "https://github.com/${REPO}/releases/download/v${version}/claude-tools-python-${version}.zip" \
    -o "$tmp/pytools.zip"

  unzip -q "$tmp/pytools.zip" -d "$tmp/extracted"

  mkdir -p "$BIN_DIR"

  local tools=(snippet claude-handoff claude-cost claude-review-diff claude-remind claude-harness claude-pipeline)
  for tool in "${tools[@]}"; do
    local src="$tmp/extracted/tools/${tool}.py"
    if [ -f "$src" ]; then
      cp "$src" "${BIN_DIR}/${tool}"
      chmod +x "${BIN_DIR}/${tool}"
      success "  ✓ $tool → ${BIN_DIR}/${tool}"
    fi
  done
}

# ── install Rust binary ───────────────────────────────────────────────────────
install_binary() {
  local version="$1" target="$2"
  info "Installing claude-tools binary (${target}) v${version}..."

  local tmp
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT

  local archive="claude-tools-${version}-${target}.tar.gz"
  curl -fsSL \
    "https://github.com/${REPO}/releases/download/v${version}/${archive}" \
    -o "$tmp/${archive}"

  tar -xzf "$tmp/${archive}" -C "$tmp"

  mkdir -p "$BIN_DIR"
  cp "$tmp/claude-tools-${version}-${target}/claude-tools" "${BIN_DIR}/claude-tools"
  chmod +x "${BIN_DIR}/claude-tools"
  success "  ✓ claude-tools → ${BIN_DIR}/claude-tools"
}

# ── PATH hint ────────────────────────────────────────────────────────────────
check_path() {
  if ! echo "$PATH" | tr ':' '\n' | grep -q "$BIN_DIR"; then
    warn ""
    warn "Add this to your shell profile (~/.bashrc or ~/.zshrc):"
    warn '  export PATH="'"$BIN_DIR"':$PATH"'
    warn ""
  fi
}

# ── main ─────────────────────────────────────────────────────────────────────
main() {
  info "Claude Code Multi-Agent System — Installer"
  echo ""

  local version
  version="$(resolve_version)"
  info "Installing version: v${version}"
  echo ""

  install_agents "$version"
  install_python_tools "$version"

  if [ "$INSTALL_BINARY" = true ]; then
    local target
    target="$(detect_target)"
    install_binary "$version" "$target"
  fi

  check_path

  echo ""
  success "Installation complete!"
  echo ""
  printf '  Restart Claude Code, then run: \033[1m/agents\033[0m to verify.\n'
  echo ""
}

main "$@"
