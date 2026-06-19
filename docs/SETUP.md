[← Back to README](../README.md)

**[한국어](SETUP.ko.md)** · **English**

# Environment Setup Guide

Follow these steps in order when setting up a fresh machine or account.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Install Claude Code CLI](#2-install-claude-code-cli)
3. [Install Multi-Agent System](#3-install-multi-agent-system)
4. [Environment Variables](#4-environment-variables)
5. [MCP Servers](#5-mcp-servers)
6. [Plugins](#6-plugins)
7. [Config Files](#7-config-files)
8. [Install Tools](#8-install-tools)
9. [Rust Binary (optional)](#9-rust-binary-optional)
10. [Full Reinstall Checklist](#10-full-reinstall-checklist)

---

## 1. Prerequisites

| Item | Min Version | Check |
|------|------------|-------|
| Node.js | 18+ | `node -v` |
| npm | 9+ | `npm -v` |
| Git | 2.x | `git --version` |
| Docker | — | `docker --version` *(required for GitHub MCP)* |
| GNU make | — | `make --version` *(required for Makefile)* |

```bash
# macOS
brew install node make
# Windows
winget install OpenJS.NodeJS.LTS
winget install GnuWin32.Make
# Linux
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs make
```

---

## 2. Install Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
claude   # browser auth on first run
claude --version
```

> Already have an API key?
> ```bash
> export ANTHROPIC_API_KEY="sk-ant-..."   # macOS/Linux
> $env:ANTHROPIC_API_KEY = "sk-ant-..."  # Windows
> ```

---

## 3. Install Multi-Agent System

```bash
git clone https://github.com/BcKmini/claude-code-use.git
cd claude-code-use
```

```bash
# macOS / Linux (recommended)
bash install.sh

# or step by step
make install        # agents + slash commands + Python tools
make install-rust   # optional: Rust binary
```

Copies 11 agent files to `~/.claude/agents/` and sets `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

Verify inside Claude Code:
```
/agents   # → 11 agents listed
```

---

## 4. Environment Variables

```powershell
# Windows
[System.Environment]::SetEnvironmentVariable("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS","1","User")
```

```bash
# macOS/Linux (~/.zshrc or ~/.bashrc)
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

---

## 5. MCP Servers

### GitHub MCP (Docker)

**Token:** GitHub → Settings → Developer settings → Personal access tokens → scopes: `repo`, `read:org`

```bash
docker run -d --restart always \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token \
  ghcr.io/github/github-mcp-server stdio
```

Connect: Claude Code Settings → MCP Servers → Add → Docker stdio. Verify with `/mcp`.

### Google Drive MCP

Claude Code Settings → MCP Servers → claude.ai integrations → Google Drive → OAuth approve.

### context7

Auto-activates when you ask about libraries, APIs, or version migrations. No install needed.

---

## 6. Plugins

Register in `~/.claude/settings.json` → `enabledPlugins`.

| Plugin | Command | Role |
|--------|---------|------|
| hookify | `/hookify` | Block unwanted Claude behaviors |
| serena | — | LSP-based code symbol navigation |
| session-report | `/session-report` | Token usage HTML report |
| claude-md-management | `/claude-md-improver` | Audit CLAUDE.md files |

---

## 7. Config Files

`~/.claude/settings.json`

```json
{
  "effortLevel": "medium",
  "autoUpdatesChannel": "latest",
  "theme": "dark"
}
```

---

## 8. Install Tools

### Option A — Makefile (recommended)

```bash
make install        # agents + slash commands + Python tools
make install-rust   # optional: Rust binary (requires cargo)
make status         # verify everything installed correctly
```

### Option B — Script

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File tools\install-tools.ps1
```

```bash
# macOS / Linux
bash tools/install-tools.sh
```

Both install `/snippet`, `/handoff`, `/cost`, `/review-diff`, `/remind` slash commands into `~/.claude/commands/`, plus shell functions and 20 default snippets.

### Option C — Rust binary only

```bash
cd rust
cargo build --release
cp target/release/claude-tools ~/.local/bin/
# or: make install-rust
```

See [INTEGRATION.md](INTEGRATION.md) for full Rust workflow.

### Verify

```bash
make env
# or: claude-tools env
```

Expected output:
```
Claude Code Environment

  ✓ ANTHROPIC_API_KEY   sk-ant-…
  ✓ ~/.claude/           exists
  ✓ ~/.claude/agents/    11 agents installed
  ✓ ~/.claude/commands/  5 commands: snippet, handoff, cost, review-diff, remind
```

---

## 9. Rust Binary (optional)

> Full guide → [INTEGRATION.md](INTEGRATION.md)

```bash
# Install Rust toolchain if needed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build from source
cd claude-code-use
make install-rust        # builds and installs claude-tools binary

# Or use the installer
bash install.sh --release
```

---

## 10. Full Reinstall Checklist

```
[ ] 1.  Node.js 18+ / npm installed
[ ] 2.  npm install -g @anthropic-ai/claude-code
[ ] 3.  claude → Anthropic auth
[ ] 4.  Docker → GitHub MCP container running
[ ] 5.  GitHub MCP connected in Claude Code
[ ] 6.  Google Drive MCP connected in claude.ai
[ ] 7.  git clone https://github.com/BcKmini/claude-code-use.git
[ ] 8.  bash install.sh  (or: make install)
[ ] 9.  CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 set
[ ] 10. Plugins & config in ~/.claude/settings.json
[ ] 11. /agents → 11 agents listed
[ ] 12. /mcp → MCP connected
[ ] 13. make env  → all green
[ ] 14. (Optional) make install-rust → claude-tools env
```
