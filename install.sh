#!/usr/bin/env bash
# Claude Code Multi-Agent System — Installer
#
# Clones (or updates) the repo, verifies prerequisites, builds the Rust
# workspace from source, installs agents + slash commands + Python tools,
# and verifies the result.
#
# Usage:
#   # From the web (recommended)
#   curl -fsSL https://raw.githubusercontent.com/BcKmini/claude-code-use/main/install.sh | bash
#
#   # From a cloned repo
#   ./install.sh
#   ./install.sh --release          # optimized build (slower compile, faster binary)
#   ./install.sh --no-binary        # skip Rust build; agents + Python tools only
#   ./install.sh --no-verify        # skip post-install verification
#   ./install.sh --update           # pull latest and reinstall
#   ./install.sh --help
#
# Environment overrides:
#   CLAUDE_HOME          default: ~/.claude
#   BIN_DIR              default: ~/.local/bin
#   BUILD_PROFILE        debug | release
#   SKIP_VERIFY          1 to skip
#   SKIP_BINARY          1 to skip Rust build

set -euo pipefail

# ── colour support ──────────────────────────────────────────────────────────
if [ -t 1 ] && command -v tput >/dev/null 2>&1 && [ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]; then
  R="$(tput sgr0)"; BOLD="$(tput bold)"; DIM="$(tput dim)"
  RED="$(tput setaf 1)"; GREEN="$(tput setaf 2)"; YELLOW="$(tput setaf 3)"
  BLUE="$(tput setaf 4)"; CYAN="$(tput setaf 6)"; PURPLE="$(tput setaf 5)"
else
  R=""; BOLD=""; DIM=""; RED=""; GREEN=""; YELLOW=""; BLUE=""; CYAN=""; PURPLE=""
fi

STEP_N=0
STEP_TOTAL=7

step()  {
  STEP_N=$((STEP_N + 1))
  printf '\n%s[%d/%d]%s %s%s%s\n' \
    "${BLUE}" "${STEP_N}" "${STEP_TOTAL}" "${R}" "${BOLD}" "$1" "${R}"
}
info()    { printf '%s  →%s %s\n'    "${CYAN}"   "${R}" "$*"; }
ok()      { printf '%s  ✓%s %s\n'    "${GREEN}"  "${R}" "$*"; }
warn()    { printf '%s  ⚠%s  %s\n'   "${YELLOW}" "${R}" "$*" >&2; }
error()   { printf '%s  ✗%s  %s\n'   "${RED}"    "${R}" "$*" >&2; }
section() { printf '\n%s%s%s\n%s%s%s\n' "${BOLD}${PURPLE}" "$*" "${R}" "${DIM}" "$(printf '%.0s─' $(seq 1 ${#1}))" "${R}"; }

REPO_URL="https://github.com/BcKmini/claude-code-use.git"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"
BUILD_PROFILE="${BUILD_PROFILE:-release}"
SKIP_VERIFY="${SKIP_VERIFY:-0}"
SKIP_BINARY="${SKIP_BINARY:-0}"
DO_UPDATE=0

# ── banner ──────────────────────────────────────────────────────────────────
print_banner() {
  printf '%s' "${BOLD}${PURPLE}"
  cat <<'EOF'

   ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗
  ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝
  ██║     ██║     ███████║██║   ██║██║  ██║█████╗
  ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝
  ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗
   ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝

  Claude Code Multi-Agent System  ·  Installer
EOF
  printf '%s\n\n' "${R}"
}

# ── help ────────────────────────────────────────────────────────────────────
print_help() {
  cat <<EOF
${BOLD}Usage:${R}
  ./install.sh [options]

${BOLD}Options:${R}
  --release       Build optimised release binary (default; slower compile, faster at runtime)
  --debug         Build debug binary (faster compile, slower at runtime)
  --no-binary     Skip the Rust build; install agents + Python tools only
  --no-verify     Skip post-install verification
  --update        Pull latest commits and reinstall everything
  -h, --help      Show this help text

${BOLD}Environment overrides:${R}
  CLAUDE_HOME     Where agents are installed (default: ~/.claude)
  BIN_DIR         Where binaries go (default: ~/.local/bin)
  BUILD_PROFILE   debug | release
  SKIP_VERIFY     1 = skip verification
  SKIP_BINARY     1 = skip Rust build
EOF
}

# ── troubleshooting ─────────────────────────────────────────────────────────
print_troubleshooting() {
  cat <<EOF

${BOLD}Troubleshooting${R}
${DIM}───────────────${R}

  ${BOLD}1. Rust toolchain not found${R}
     Install via rustup:
       curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
     Then reload:
       source "\$HOME/.cargo/env"

  ${BOLD}2. Linux — missing system packages${R}
     Debian / Ubuntu:
       sudo apt-get install -y git pkg-config libssl-dev ca-certificates build-essential
     Fedora / RHEL:
       sudo dnf install -y git pkgconf-pkg-config openssl-devel gcc
     Arch:
       sudo pacman -S --needed git pkgconf openssl base-devel

  ${BOLD}3. macOS — Xcode command line tools${R}
     xcode-select --install

  ${BOLD}4. Windows${R}
     Use WSL (Ubuntu recommended) and re-run this script inside WSL.

  ${BOLD}5. Build fails mid-way${R}
     cd rust && cargo clean && cargo build --workspace --release

  ${BOLD}6. 'claude-tools' not found after install${R}
     Add BIN_DIR to PATH in your shell profile:
       echo 'export PATH="\$HOME/.local/bin:\$PATH"' >> ~/.bashrc
       source ~/.bashrc

  ${BOLD}7. Agents not showing in /agents${R}
     Restart Claude Code after install.
     Verify: ls ~/.claude/agents/

EOF
}

# ── arg parse ────────────────────────────────────────────────────────────────
while [ "$#" -gt 0 ]; do
  case "$1" in
    --release)    BUILD_PROFILE="release" ;;
    --debug)      BUILD_PROFILE="debug" ;;
    --no-binary)  SKIP_BINARY="1" ;;
    --no-verify)  SKIP_VERIFY="1" ;;
    --update)     DO_UPDATE=1 ;;
    -h|--help)    print_help; exit 0 ;;
    *) error "Unknown argument: $1"; print_help; exit 2 ;;
  esac
  shift
done

trap 'rc=$?; [ "$rc" -ne 0 ] && { error "Installation failed (exit $rc)."; print_troubleshooting; }' EXIT

# ── helpers ──────────────────────────────────────────────────────────────────
need_cmd() { command -v "$1" &>/dev/null; }
require()  { need_cmd "$1" || { error "Required command not found: $1"; exit 1; }; }

# ── main ─────────────────────────────────────────────────────────────────────
print_banner

# ── Step 1: Detect environment ───────────────────────────────────────────────
step "Detecting host environment"

UNAME_S="$(uname -s 2>/dev/null || echo unknown)"
UNAME_M="$(uname -m 2>/dev/null || echo unknown)"
OS="unknown"
IS_WSL=0

case "${UNAME_S}" in
  Linux*)
    OS="linux"
    grep -qiE 'microsoft|wsl' /proc/version 2>/dev/null && IS_WSL=1
    ;;
  Darwin*) OS="macos" ;;
  MINGW*|MSYS*|CYGWIN*)
    error "Detected native Windows shell. Please run this inside WSL."
    exit 1
    ;;
esac

info "OS:   ${UNAME_S} ${UNAME_M}"
info "Home: ${CLAUDE_HOME}"
info "Bin:  ${BIN_DIR}"
[ "$IS_WSL" -eq 1 ] && info "WSL:  yes"
ok "Platform supported"

# ── Step 2: Check prerequisites ──────────────────────────────────────────────
step "Checking prerequisites"

MISSING=0

need_cmd git   && ok "git       $(git --version 2>/dev/null)" || { warn "git not found (some features may degrade)"; }
need_cmd python3 && ok "python3  $(python3 --version 2>/dev/null)" || warn "python3 not found — Python tools won't install"

if [ "$SKIP_BINARY" = "0" ]; then
  if need_cmd rustc; then
    ok "rustc    $(rustc --version 2>/dev/null)"
  else
    warn "rustc not found — skipping Rust build (use --no-binary to suppress this)"
    warn "Install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    SKIP_BINARY=1
  fi

  if need_cmd cargo; then
    ok "cargo    $(cargo --version 2>/dev/null)"
  else
    SKIP_BINARY=1
  fi

  if [ "$OS" = "linux" ]; then
    need_cmd pkg-config && ok "pkg-config found" || warn "pkg-config missing — may be needed for OpenSSL"
  fi

  if [ "$OS" = "macos" ] && ! need_cmd cc; then
    warn "Xcode CLT not detected — run: xcode-select --install"
  fi
fi

[ "$MISSING" -eq 0 ] && ok "Prerequisites satisfied"

# ── Step 3: Locate / clone repo ──────────────────────────────────────────────
step "Locating repository"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || pwd)"
REPO_DIR="$SCRIPT_DIR"

# If run via curl (no local repo), clone it
if [ ! -f "${REPO_DIR}/agents/00-orchestrator.md" ]; then
  info "No local repo detected — cloning ${REPO_URL}"
  need_cmd git || { error "git is required to clone the repository"; exit 1; }
  CLONE_TARGET="$HOME/.claude-code-agents-src"
  if [ -d "$CLONE_TARGET/.git" ]; then
    info "Existing clone found at ${CLONE_TARGET} — pulling latest"
    git -C "$CLONE_TARGET" pull --ff-only
  else
    git clone --depth=1 "$REPO_URL" "$CLONE_TARGET"
  fi
  REPO_DIR="$CLONE_TARGET"
  ok "Repository at ${REPO_DIR}"
elif [ "$DO_UPDATE" -eq 1 ]; then
  info "Pulling latest changes..."
  git -C "$REPO_DIR" pull --ff-only
  ok "Repository up-to-date"
else
  ok "Using local repo at ${REPO_DIR}"
fi

RUST_DIR="${REPO_DIR}/rust"

# ── Step 4: Build Rust workspace ─────────────────────────────────────────────
if [ "$SKIP_BINARY" = "0" ]; then
  step "Building Rust workspace (profile: ${BUILD_PROFILE})"

  [ -d "$RUST_DIR" ]           || { error "rust/ directory not found in ${REPO_DIR}"; exit 1; }
  [ -f "${RUST_DIR}/Cargo.toml" ] || { error "Cargo.toml not found in ${RUST_DIR}"; exit 1; }

  CARGO_FLAGS=(build --workspace)
  [ "$BUILD_PROFILE" = "release" ] && CARGO_FLAGS+=(--release)

  info "Running: cargo ${CARGO_FLAGS[*]}"
  info "First build may take a few minutes…"
  echo ""

  (
    cd "${RUST_DIR}"
    CARGO_TERM_COLOR=always cargo "${CARGO_FLAGS[@]}"
  )

  CLAUDE_TOOLS_BIN="${RUST_DIR}/target/${BUILD_PROFILE}/claude-tools"
  [ -x "$CLAUDE_TOOLS_BIN" ] || { error "Binary not found at ${CLAUDE_TOOLS_BIN}"; exit 1; }
  ok "Built → ${CLAUDE_TOOLS_BIN}"

  mkdir -p "$BIN_DIR"
  cp "$CLAUDE_TOOLS_BIN" "${BIN_DIR}/claude-tools"
  chmod +x "${BIN_DIR}/claude-tools"
  ok "Installed claude-tools → ${BIN_DIR}/claude-tools"
else
  step "Skipping Rust build (--no-binary)"
  info "claude-tools binary will not be installed"
  STEP_TOTAL=$((STEP_TOTAL - 1))
fi

# ── Step 5: Install agents ────────────────────────────────────────────────────
step "Installing agents → ${CLAUDE_HOME}/agents/"

mkdir -p "${CLAUDE_HOME}/agents"
count=0
for f in "${REPO_DIR}/agents/"*.md; do
  [ -f "$f" ] || continue
  cp "$f" "${CLAUDE_HOME}/agents/"
  count=$((count + 1))
done
ok "${count} agents installed"

# ── Step 6: Install slash commands + Python tools ─────────────────────────────
step "Installing slash commands + Python tools"

mkdir -p "${CLAUDE_HOME}/commands"
count=0
for f in "${REPO_DIR}/.claude/commands/"*.md; do
  [ -f "$f" ] || continue
  cp "$f" "${CLAUDE_HOME}/commands/"
  count=$((count + 1))
done
ok "${count} slash commands → ${CLAUDE_HOME}/commands/"

if need_cmd python3; then
  mkdir -p "$BIN_DIR"
  TOOLS=(snippet claude-handoff claude-cost claude-review-diff claude-remind claude-harness claude-pipeline)
  for tool in "${TOOLS[@]}"; do
    src="${REPO_DIR}/tools/${tool}.py"
    [ -f "$src" ] || continue
    cp "$src" "${BIN_DIR}/${tool}"
    chmod +x "${BIN_DIR}/${tool}"
    ok "${tool} → ${BIN_DIR}/${tool}"
  done
else
  warn "python3 not found — skipping Python tool installation"
fi

# ── Step 7: Verify ────────────────────────────────────────────────────────────
step "Verifying installation"

FAIL=0
INSTALLED_AGENTS=$(ls "${CLAUDE_HOME}/agents/"*.md 2>/dev/null | wc -l | tr -d ' ')

if [ "$INSTALLED_AGENTS" -gt 0 ]; then
  ok "${INSTALLED_AGENTS} agents confirmed in ${CLAUDE_HOME}/agents/"
else
  error "No agents found in ${CLAUDE_HOME}/agents/ — something went wrong"
  FAIL=1
fi

if [ "$SKIP_VERIFY" = "0" ] && [ "$SKIP_BINARY" = "0" ] && [ -x "${BIN_DIR}/claude-tools" ]; then
  info "Running: claude-tools --version"
  if VER="$("${BIN_DIR}/claude-tools" --version 2>&1)"; then
    ok "claude-tools → ${VER}"
  else
    error "claude-tools --version failed"
    FAIL=1
  fi
fi

[ "$FAIL" -eq 0 ] || exit 1

# ── Done ─────────────────────────────────────────────────────────────────────
VERSION="$(cat "${REPO_DIR}/VERSION" 2>/dev/null || echo '?')"

cat <<EOF

${GREEN}${BOLD}Installation complete!${R}  (v${VERSION})
${DIM}─────────────────────────────────────────────────────${R}

  Agents:    ${CLAUDE_HOME}/agents/   (${INSTALLED_AGENTS} installed)
  Commands:  ${CLAUDE_HOME}/commands/
  Tools:     ${BIN_DIR}/

${BOLD}Next steps:${R}

  1. Restart Claude Code
  2. Run ${CYAN}/agents${R} to verify agents are loaded
  3. Try a task:

     ${DIM}# Full pipeline${R}
     Use the orchestrator to add a login feature.

     ${DIM}# Check API cost first${R}
     /cost estimate full-pipeline

     ${DIM}# Surgical code fix${R}
     Have implementer fix ONLY the validateToken function in src/auth.ts.

${BOLD}PATH check:${R}
EOF

if echo "$PATH" | tr ':' '\n' | grep -q "$BIN_DIR"; then
  ok "${BIN_DIR} is already in PATH"
else
  printf '%s  ⚠%s  Add to your shell profile:\n' "${YELLOW}" "${R}"
  printf '     %sexport PATH="%s:\$PATH"%s\n' "${CYAN}" "${BIN_DIR}" "${R}"
fi

echo ""
trap - EXIT
