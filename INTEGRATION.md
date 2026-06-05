[← Back to README](./README.md)

**[한국어](INTEGRATION.ko.md)** · **English**

# Integration Guide — claw-code & claude-tools

`Claudecode-Agent` and `claw-code` operate at different layers and are more powerful together.

| System | Role | Link |
|--------|------|------|
| Claudecode-Agent | Agent definitions (9 agent roles + behavior rules) + CLI tools | This repo |
| claw-code | CLI harness runtime (open-source Rust CLI) | [ultraworkers/claw-code](https://github.com/ultraworkers/claw-code) |

---

## claw-code Overview

claw-code is an open-source Rust CLI harness that works alongside Claude Code CLI.

**Key features:**
- Multi-AI-provider support (Anthropic, OpenAI-compatible)
- REPL-style session management
- RAG service (Qdrant + vector DB)
- Container support (Docker/Podman)
- Machine-readable JSON state output
- clawhip event routing

---

## Quick Start

### Build claw-code (Windows PowerShell)

```powershell
git clone https://github.com/ultraworkers/claw-code
cd claw-code\rust
cargo build --workspace

$env:ANTHROPIC_API_KEY = "sk-ant-..."
.\target\debug\claw.exe doctor
```

### Build claw-code (macOS/Linux)

```bash
git clone https://github.com/ultraworkers/claw-code
cd claw-code/rust
cargo build --workspace

export ANTHROPIC_API_KEY="sk-ant-..."
./target/debug/claw doctor
```

### Initialize a project

```bash
claw init
```

Creates `.claw`, `.claw.json`, `CLAUDE.md`. **Copy this repo's `CLAUDE.md` over it to apply the agent guidelines inside claw-code sessions.**

---

## Separation of Concerns

```
Claudecode-Agent                 claw-code
       |↓                               |↓
  9 agent definitions          CLI harness runtime
  (roles, tools, prompts)      (session, RAG, events)
       |↓                               |↓
  Claude Code CLI               claw CLI
  (claude command)              (claw command)
       \___________________________/
                 |↓
         shared agents/*.md definitions
```

**Agent definitions (`agents/*.md`) work in both runtimes.**
Whether you use Claude Code's `/agents` or the claw-code REPL, the same agent role definitions apply.

---

## Integration Points

### 1. Shared CLAUDE.md

After running `claw init`, replace the generated `CLAUDE.md` with this repo's version:

```bash
claw init
cp /path/to/Claudecode-Agent/CLAUDE.md ./CLAUDE.md
```

The agent system guidelines then apply inside claw-code sessions too.

### 2. Shared Agent Definitions

claw-code uses its own agent system rather than `~/.claude/agents/`. However, the **orchestrator pattern** works in claw-code directly:

```
# Inside claw REPL
Use the orchestrator to implement [feature].
Run the full pipeline: planner -> implementer -> reviewer -> tester
```

### 3. RAG Service (Qdrant)

claw-code supports RAG via Qdrant vector DB — use it as an alternative or complement to context7 MCP.

```bash
# Start RAG service (docker-compose)
cd claw-code
docker compose up qdrant rag-serve -d

# Also start GitHub MCP container
docker run -d \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token \
  ghcr.io/github/github-mcp-server stdio
```

**Recommended Docker startup order:**

```bash
# 1. Qdrant (RAG vector DB)
docker compose up qdrant -d

# 2. RAG service (depends on Qdrant)
docker compose up rag-serve -d

# 3. GitHub MCP server
docker run -d --restart always \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token \
  ghcr.io/github/github-mcp-server stdio
```

### 4. Codebase Indexing (RAG input)

```bash
docker compose run rag-ingest
```

After indexing, claw sessions automatically reference relevant code when answering codebase questions.

### 5. Event Routing Comparison

| Feature | Claude Code | claw-code |
|---------|-------------|-----------|
| Block unwanted behaviors | hookify plugin | clawhip events |
| Notifications | none | clawhip channels (Discord, etc.) |
| Session monitoring | session-report plugin | claw status / JSON output |
| Multi-agent | orchestrator agent | oh-my-openagent (OmO) |

---

## Recommended Workflows

### Coding (Claude Code + multi-agent)

```
Run claude
  -> Delegate task to orchestrator
  -> planner -> implementer -> reviewer -> tester pipeline
  -> Create PR via GitHub MCP
```

### Codebase Exploration (claw-code + RAG)

```
docker compose up qdrant rag-serve -d
Run claw
  -> /doctor
  -> RAG answers codebase queries from indexed code
```

### Automated Pipeline (claw-code + clawhip)

```
clawhip detects GitHub PR/Issue event
  -> auto-starts claw session
  -> executes task with orchestrator pattern
  -> sends result to Discord or other channel
```

---

## claude-tools Rust Binary

This repo includes `claude-tools` — all three Python tools compiled into a single Rust binary.

```
rust/
├── Cargo.toml                ← workspace
└── claude-tools/
    ├── Cargo.toml            ← clap 4, serde, chrono, dirs, anyhow, regex
    └── src/
        ├── main.rs           ← clap derive CLI (snippet / handoff / cost)
        ├── snippet.rs        ← manages ~/.claude/snippets.json
        ├── handoff.rs        ← manages ~/.claude/handoffs/ session docs
        ├── cost.rs           ← parses ~/.claude/projects/ JSONL + cost estimates
        └── colors.rs         ← ANSI color helpers
```

### Build

```bash
cd rust
cargo build --release
# binary: rust/target/release/claude-tools
```

### Use with claw-code

`claude-tools` uses the same Rust ecosystem as claw-code. Add both binaries to PATH for a fully Python-free workflow:

```bash
# ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/claude-tools/target/release"
export PATH="$PATH:/path/to/claw-code/target/release"
```

#### Session workflow (no Python)

```bash
# 1. Start coding session with claw
claw

# 2. Save handoff before ending session
claude-tools handoff save --note "auth done, next: write tests"

# 3. Check costs
claude-tools cost month

# 4. Resume context in next session
claude-tools handoff load | claude
# or
claude-tools handoff load | claw
```

### Dependency Comparison

| | Python tools | claude-tools (Rust) |
|--|-------------|---------------------|
| Runtime | Python 3.8+ required | Single binary, no dependencies |
| Speed | Normal | Fast |
| Deployment | Copy files | Copy one binary |
| claw-code integration | Separate install | Same Cargo workspace possible |

---

## Related Links

- [claw-code (ultraworkers)](https://github.com/ultraworkers/claw-code)
- [clawhip event router](https://github.com/Yeachan-Heo/clawhip)
- [oh-my-openagent multi-agent orchestration](https://github.com/code-yeongyu/oh-my-openagent)
- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)
- [UltraWorkers Discord](https://discord.gg/5TUQKqFWd)
