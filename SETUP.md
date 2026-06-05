[← Back to README](./README.md)

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

The following must be installed first.

| Item | Min Version | Check |
|------|------------|-------|
| Node.js | 18+ | `node -v` |
| npm | 9+ | `npm -v` |
| Git | 2.x | `git --version` |
| Docker | — | `docker --version` *(required for GitHub MCP)* |

**Install Node.js**

```bash
# macOS — Homebrew
brew install node

# Windows — winget
winget install OpenJS.NodeJS.LTS

# Linux (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

---

## 2. Install Claude Code CLI

### Install

```bash
npm install -g @anthropic-ai/claude-code
```

### Authenticate

```bash
claude
```

On first run, a browser auth screen appears. Log in with your Anthropic account — the API key is set automatically.

> If you already have an API key, set it directly:
> ```bash
> export ANTHROPIC_API_KEY="sk-ant-..."   # macOS/Linux
> $env:ANTHROPIC_API_KEY = "sk-ant-..."  # Windows PowerShell
> ```

### Verify

```bash
claude --version
```

---

## 3. Install Multi-Agent System

Clone the repo, then run the installer for your platform.

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

The script automatically:
- Copies 9 agent files to `~/.claude/agents/`
- Permanently sets `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Creates `.claudeignore`

**Agent install locations**

| Path | Scope |
|------|-------|
| `~/.claude/agents/` | Global — all projects |
| `.claude/agents/` (project root) | Local — current project only |

**Verify** — launch Claude Code, then:

```
/agents
```

9 agents listed = done.

---

## 4. Environment Variables

```powershell
# Windows — permanent user environment variable
[System.Environment]::SetEnvironmentVariable(
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS",
    "1",
    "User"
)
```

```bash
# macOS/Linux — add to ~/.zshrc or ~/.bashrc
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

**Verify**

```powershell
# Windows
[System.Environment]::GetEnvironmentVariable("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", "User")
# Output: 1
```

```bash
# macOS/Linux
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
# Output: 1
```

---

## 5. MCP Servers

### GitHub MCP (Docker)

Official GitHub MCP server. Create/review PRs, manage issues — all from Claude.

**Create a token first**
- GitHub → Settings → Developer settings → Personal access tokens
- Required scopes: `repo`, `read:org`

**Run the container**

```bash
docker run -d \
  --restart always \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here \
  ghcr.io/github/github-mcp-server \
  stdio
```

**Connect to Claude Code**

Claude Code Settings → MCP Servers → Add new server → Docker container stdio

```bash
/mcp          # check connection status
docker ps --filter ancestor=ghcr.io/github/github-mcp-server
```

> If you see error -32000: verify the container is running, then `/mcp` to reconnect.

---

### Google Drive MCP

Provided by claude.ai. Read Google Docs, Sheets, Drive files.

- Claude Code Settings → MCP Servers → claude.ai integrations → Google Drive
- First connection requires OAuth (approve in browser)

---

### context7

Fetches real-time library/framework docs. No separate install — activates automatically in Claude Code when you ask about libraries, APIs, or version migrations.

---

## 6. Plugins

Register in `~/.claude/settings.json` under `enabledPlugins`.

| Plugin | Slash command | Role |
|--------|--------------|------|
| hookify | `/hookify` | Block unwanted Claude behaviors with hooks |
| serena | — | Code symbol analysis & navigation (LSP-based) |
| session-report | `/session-report` | Session token usage HTML report |
| claude-md-management | `/claude-md-improver` | Audit and improve CLAUDE.md files |

**Key commands**

```bash
/hookify            # auto-detect behaviors to block in current conversation
/hookify list       # list configured hooks
/session-report     # generate session-report-YYYYMMDD-HHMM.html
```

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

| Key | Value | Description |
|-----|-------|-------------|
| effortLevel | medium | Quality/speed balance (low / medium / high) |
| theme | dark | UI theme |
| autoUpdatesChannel | latest | Auto-update channel |

---

## 8. Install Tools

Install all three productivity tools at once:

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File tools\install-tools.ps1
```

```bash
# macOS / Linux
bash tools/install-tools.sh
```

Installs: `/snippet`, `/handoff`, `/cost` slash commands + shell functions + 20 default snippets.

Or use the Rust binary — see [INTEGRATION.md](./INTEGRATION.md).

---

## 9. claw-code Integration (optional)

claw-code is an open-source Rust CLI harness for Claude Code with RAG (Qdrant), clawhip event routing, and multi-provider support.

> Full guide → [INTEGRATION.md](./INTEGRATION.md)

**Prerequisites**

- Rust toolchain: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Docker (for RAG service)

**Build**

```powershell
# Windows PowerShell
git clone https://github.com/ultraworkers/claw-code
cd claw-code\rust
cargo build --workspace

$env:ANTHROPIC_API_KEY = "sk-ant-..."
.\target\debug\claw.exe doctor
```

```bash
# macOS / Linux
git clone https://github.com/ultraworkers/claw-code
cd claw-code/rust
cargo build --workspace

export ANTHROPIC_API_KEY="sk-ant-..."
./target/debug/claw doctor
```

**Apply to project**

```bash
claw init
cp /path/to/Claudecode-Agent/CLAUDE.md ./CLAUDE.md
```

---

## 10. Full Reinstall Checklist

Follow top to bottom on a fresh machine.

```
[ ] 1.  Verify Node.js 18+ / npm installed
[ ] 2.  Install Claude Code CLI  →  npm install -g @anthropic-ai/claude-code
[ ] 3.  Run claude → authenticate with Anthropic account
[ ] 4.  Install Docker → run GitHub MCP server container
[ ] 5.  Connect GitHub MCP in Claude Code
[ ] 6.  Connect Google Drive MCP in claude.ai
[ ] 7.  Clone this repo → run setup-agents script
[ ] 8.  Set CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
[ ] 9.  Apply plugins & config in ~/.claude/settings.json
[ ] 10. Run /agents to verify 9 agents listed
[ ] 11. Run /mcp to verify MCP connection
[ ] 12. Install tools: bash tools/install-tools.sh
[ ] 13. (Optional) Build claw-code → run claw doctor health check
```
