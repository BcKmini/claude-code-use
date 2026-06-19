[← Back to README](../README.md)

**[한국어](INTEGRATION.ko.md)** · **English**

# Integration Guide — claw-code & claude-tools

`Claudecode-Agent` and `claw-code` operate at different layers and are more powerful together.

| System | Role | Link |
|--------|------|------|
| claude-code-use | Agent definitions + CLI tools (Python + Rust) | This repo |
| claw-code | CLI harness runtime (open-source Rust CLI) | [ultraworkers/claw-code](https://github.com/ultraworkers/claw-code) |

---

## claw-code Overview

**Key features:**
- Multi-AI-provider support (Anthropic, OpenAI-compatible)
- REPL-style session management
- RAG service (Qdrant + vector DB)
- Container support (Docker/Podman)
- Machine-readable JSON state output
- clawhip event routing

---

## Quick Start

```powershell
# Windows
git clone https://github.com/ultraworkers/claw-code
cd claw-code\rust
cargo build --workspace
$env:ANTHROPIC_API_KEY = "sk-ant-..."
.\target\debug\claw.exe doctor
```

```bash
# macOS/Linux
git clone https://github.com/ultraworkers/claw-code
cd claw-code/rust
cargo build --workspace
export ANTHROPIC_API_KEY="sk-ant-..."
./target/debug/claw doctor
```

```bash
claw init   # creates .claw, .claw.json, CLAUDE.md
cp /path/to/claude-code-use/docs/CLAUDE.md ./CLAUDE.md
```

---

## Architecture

```
claude-code-use                  claw-code
       |                               |
  11 agent definitions          CLI harness runtime
  (roles, tools, prompts)      (session, RAG, events)
       |                               |
  Claude Code CLI               claw CLI
  (claude command)              (claw command)
       \_____________________________/
                    |
         shared agents/*.md definitions
```

**Agent definitions (`agents/*.md`) work in both runtimes.**

---

## Integration Points

### 1. Shared CLAUDE.md

```bash
claw init
cp /path/to/claude-code-use/docs/CLAUDE.md ./CLAUDE.md
```

### 2. Orchestrator Pattern in claw REPL

```
Use the orchestrator to implement [feature].
Run the full pipeline: planner -> implementer -> reviewer -> tester
```

### 3. RAG Service (Qdrant)

```bash
cd claw-code
docker compose up qdrant -d
docker compose up rag-serve -d
docker run -d --restart always \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token \
  ghcr.io/github/github-mcp-server stdio
docker compose run rag-ingest   # index your codebase
```

### 4. Event Routing Comparison

| Feature | Claude Code | claw-code |
|---------|-------------|-----------|
| Block behaviors | hookify plugin | clawhip events |
| Notifications | none | clawhip channels (Discord, etc.) |
| Session monitoring | session-report plugin | claw status / JSON |
| Multi-agent | orchestrator agent | oh-my-openagent (OmO) |

---

## claude-tools Rust Binary

All Python tools + live monitor + environment check compiled into a single zero-dependency binary.

```
rust/
├── Cargo.toml
└── claude-tools/
    └── src/
        ├── main.rs       ← clap derive CLI entry point
        ├── snippet.rs    ← ~/.claude/snippets.json manager
        ├── handoff.rs    ← ~/.claude/handoffs/ session docs
        ├── cost.rs       ← ~/.claude/projects/ JSONL parser + estimates
        ├── watch.rs      ← real-time live cost monitor
        ├── env.rs        ← environment health check (NEW)
        └── colors.rs     ← ANSI color helpers
```

### Build & Install

```bash
cd rust
cargo build --release
# binary: rust/target/release/claude-tools

# or via Makefile
make install-rust

# or install globally
cargo install --path rust/claude-tools
```

### All Subcommands

```bash
claude-tools snippet list
claude-tools snippet run full-pipeline

claude-tools handoff save --note "auth done, next: tests"
claude-tools handoff load | claude

claude-tools cost estimate --snippet full-pipeline
claude-tools cost month
claude-tools cost set-budget 20

claude-tools watch              # live cost monitor (2s refresh)
claude-tools watch --interval 5

claude-tools env                # environment health check
```

### claude-tools env — Environment Health Check

```bash
claude-tools env
```

```
Claude Code Environment

  ✓ ANTHROPIC_API_KEY   sk-ant-…abcd
  ✓ ~/.claude/           exists
  ✓ ~/.claude/agents/    11 agents installed
  ✓ ~/.claude/commands/  5 commands: snippet, handoff, cost, review-diff, remind
  ✓ handoffs             3 saved, latest: 20250608-143022.md
  ✓ sessions             4 projects, 12 session files
```

Useful after a fresh install or when something stops working.

### claude-tools watch — Live Cost Monitor

```bash
claude-tools watch              # monitor latest session (refresh every 2s)
claude-tools watch --interval 5 # refresh every 5 seconds
```

```
Claude Code — Live Cost Monitor  (Ctrl+C to exit)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TIME     MODEL    INPUT    OUTPUT   COST
 12:01:05 sonnet   1,240    3,100    $0.0501
 12:01:18 sonnet     892    2,230    $0.0361
 12:01:44 opus       456    1,596    $0.1263
─────────────────────────────────────────────
 TOTAL              2,588    6,926   $0.2125
```

### Full Workflow (No Python)

```bash
# Add to PATH
export PATH="$PATH:$(pwd)/rust/target/release"

# Start session
claw

# Watch live costs in a second terminal
claude-tools watch

# Check environment
claude-tools env

# Save handoff before closing
claude-tools handoff save --note "auth done, next: tests"

# Resume next session
claude-tools handoff load | claude
```

### Dependency Comparison

| | Python tools | claude-tools (Rust) |
|--|-------------|---------------------|
| Runtime | Python 3.8+ required | Single binary, no deps |
| Speed | Normal | Fast |
| Deployment | Copy files | Copy 1 binary |
| claw-code integration | Separate install | Same Cargo workspace |

---

## Related Links

- [claw-code (ultraworkers)](https://github.com/ultraworkers/claw-code)
- [clawhip event router](https://github.com/Yeachan-Heo/clawhip)
- [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)
- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)
- [UltraWorkers Discord](https://discord.gg/5TUQKqFWd)
