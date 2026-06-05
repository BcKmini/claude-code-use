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
8. [Install Tools (snippet / handoff / cost)](#8-install-tools)
9. [claw-code Integration (optional)](#9-claw-code-integration-optional)
10. [Full Reinstall Checklist](#10-full-reinstall-checklist)

---

## 1. Prerequisites

| Item | Min Version | Check |
|------|------------|-------|
| Node.js | 18+ | `node -v` |
| npm | 9+ | `npm -v` |
| Git | 2.x | `git --version` |
| Docker | — | `docker --version` *(required for GitHub MCP)* |

```bash
# macOS
brew install node
# Windows
winget install OpenJS.NodeJS.LTS
# Linux
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs
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
git clone https://github.com/BcKmini/Claudecode-Agent.git
cd Claudecode-Agent
```

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

```bash
# macOS / Linux
bash setup-agents.sh
```

Copies 9 agent files to `~/.claude/agents/`, sets `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

Verify inside Claude Code:
```
/agents   # → 9 agents listed
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

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File tools\install-tools.ps1
```

```bash
# macOS / Linux
bash tools/install-tools.sh
```

Installs `/snippet`, `/handoff`, `/cost` slash commands + shell functions + 20 default snippets.

Or build the Rust binary — see [INTEGRATION.md](INTEGRATION.md).

---

## 9. claw-code Integration (optional)

> Full guide → [INTEGRATION.md](INTEGRATION.md)

```bash
# Install Rust toolchain first
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

git clone https://github.com/ultraworkers/claw-code
cd claw-code/rust
cargo build --workspace
export ANTHROPIC_API_KEY="sk-ant-..."
./target/debug/claw doctor
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
[ ] 7.  Clone repo → run setup-agents script
[ ] 8.  CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 set
[ ] 9.  Plugins & config in ~/.claude/settings.json
[ ] 10. /agents → 9 agents listed
[ ] 11. /mcp → MCP connected
[ ] 12. bash tools/install-tools.sh
[ ] 13. (Optional) claw doctor health check
```
