<div align="center">

<img src="assets/claude.png" alt="Claude Code Multi-Agent" width="420">

# Claude Code Multi-Agent System

**9 specialized AI agents + a personal prompt manager, all for Claude Code**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](https://github.com/BcKmini/claude-code-multi-agent)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet?style=flat-square&logo=anthropic)](https://claude.ai/code)
[![Agents](https://img.shields.io/badge/Agents-9-green?style=flat-square)](#agent-roster)

**[한국어 README](README.ko.md)** · **[Setup Guide](SETUP.md)** · **[Cheatsheet](AGENT-CHEATSHEET.md)** · **[claw-code Integration](INTEGRATION.md)**

</div>

---

## What is this?

A drop-in enhancement for **Claude Code** that gives you:

1. **9 specialized sub-agents** — each laser-focused on one job (design, code, review, test, security…)
2. **`snippet`** — a personal prompt manager so your best prompts are never more than one command away

Instead of one Claude instance doing everything, each task is routed to the agent best suited for it.

```
You                     Orchestrator
 │                           │
 └──► "Add OAuth login" ──► ├──► planner       (architecture)
                             ├──► database-expert (schema)
                             ├──► implementer   (code)
                             ├──► reviewer      (code review)
                             └──► tester        (tests)
```

---

## Agent Roster

| # | Agent | Model | Job |
|---|-------|-------|-----|
| 00 | **orchestrator** | Opus | Breaks down requests and delegates to sub-agents |
| 01 | **planner** | Opus | Architecture & design decisions — read-only |
| 02 | **implementer** | Sonnet | Writes and edits code |
| 03 | **reviewer** | Sonnet | Bug, security, quality, performance review — read-only |
| 04 | **tester** | Sonnet | Unit, integration, E2E test authoring |
| 05 | **security-auditor** | Opus | OWASP Top 10 audit — read-only |
| 06 | **performance-optimizer** | Sonnet | Bottleneck analysis and optimization |
| 07 | **database-expert** | Sonnet | Schema design, queries, migrations |
| 08 | **documenter** | Haiku | README, API docs, inline comments |

> **Why separate agents?**  
> Each agent carries only the context relevant to its role. No contamination between "design mode" and "implementation mode." Parallel execution (planner + security-auditor simultaneously) cuts wall-clock time.

---

## Quick Start

### 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude   # authenticate on first run
```

### 2. Install the agents

```powershell
# Windows
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

```bash
# macOS / Linux
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent
bash setup-agents.sh
```

### 3. Verify

```
claude
/agents          # → 9 agents listed
```

---

## Using the Agents

### Full feature pipeline

```
Use the orchestrator to implement OAuth 2.0 login with Google.
Requirements:
- JWT token issuance
- Integrate with existing email login

Run the full pipeline: planner -> implementer -> reviewer -> tester
```

### Quick review

```
Have the reviewer subagent review src/api/auth.ts
Focus on security vulnerabilities and error handling.
```

### Parallel tasks (saves time)

```
Run these in parallel:
1. Have planner design the notification module
2. Have database-expert design the schema
3. Have security-auditor review the requirements
Then have implementer execute the combined plan.
```

> See [AGENT-CHEATSHEET.md](AGENT-CHEATSHEET.md) for 20+ ready-to-use prompts.

---

## snippet — Personal Prompt Manager

`snippet` saves your best Claude prompts by name — and brings them back in one command from the terminal or inside a Claude Code session.

### Install snippet

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File tools\install-snippet.ps1
```

```bash
# macOS / Linux
bash tools/install-snippet.sh
```

Installs:
- `~/.claude/commands/snippet.md` → activates `/snippet` slash command inside Claude Code
- Imports 20 built-in snippets from `snippets/defaults.json`
- Registers the `snippet` shell function in your profile

### Terminal usage

```bash
snippet list                        # all snippets
snippet list --tag pipeline         # filter by tag
snippet list --sort-by uses         # sort by most-used

snippet save myfix "Fix {{BUG}} in {{FILE}}" --tags bug
snippet run myfix --var BUG="null ref" --var FILE="auth.ts"
snippet run full-pipeline | claude  # pipe directly to Claude

snippet search security
snippet show code-review
snippet edit code-review            # open in $EDITOR
snippet cp code-review my-review    # copy a snippet
snippet delete my-review            # delete (prompts confirmation)
snippet stats                       # usage statistics

snippet import snippets/defaults.json          # import from file
snippet export my-backup.json                  # export all
snippet export my-backup.json --tag pipeline   # export by tag
```

### Inside Claude Code

```
/snippet list
/snippet run full-pipeline
/snippet search security
/snippet show db-schema
```

### Template variables

Any `{{VARIABLE}}` in a prompt becomes a fill-in-the-blank at run time:

```bash
# Prompt stored as:
# "Use orchestrator to implement {{FEATURE}} in {{LANG}}. Requirements: {{REQUIREMENTS}}"

snippet run new-feature \
  --var FEATURE="user notifications" \
  --var LANG="TypeScript" \
  --var REQUIREMENTS="real-time push, email digest"
```

> Preview without running: add `--dry-run`

### Built-in snippets (20)

| Name | Tags | Purpose |
|------|------|---------|
| `full-pipeline` | pipeline | Full orchestrator pipeline with template vars |
| `new-feature` | pipeline, feature | Design + implement from scratch |
| `fix-bug` | bug | Fix + regression test |
| `hotfix` | bug, urgent | Emergency production fix |
| `code-review` | review | File-level code review |
| `pr-review` | review, pr | Diff review before merge |
| `security-audit` | security | OWASP Top 10 audit |
| `parallel-design` | parallel | Design, schema, security in parallel |
| `db-schema` | database | Schema + index strategy + migration |
| `db-migrate` | database, migration | Migration with rollback plan |
| `performance` | performance | Bottleneck analysis |
| `write-tests` | test | Comprehensive test suite |
| `write-docs` | docs | README + JSDoc update |
| `refactor` | refactor | Safe refactor with test verification |
| `explain` | explain | Explain unfamiliar code |
| `api-review` | review, api | REST API design review |
| `nextjs-feature` | nextjs, frontend | Next.js 15 App Router feature |
| `fastapi-endpoint` | fastapi, backend | FastAPI endpoint with tests |
| `context-reset` | meta | Compact context + list next steps |
| `cost-check` | meta | Session cost estimate |

---

## Repository Layout

```
claude-code-multi-agent/
├── agents/                   ← agent definitions (copied to ~/.claude/agents/)
│   ├── 00-orchestrator.md
│   ├── 01-planner.md
│   ├── 02-implementer.md
│   ├── 03-reviewer.md
│   ├── 04-tester.md
│   ├── 05-security-auditor.md
│   ├── 06-performance-optimizer.md
│   ├── 07-database-expert.md
│   └── 08-documenter.md
├── .claude/
│   └── commands/
│       └── snippet.md        ← /snippet slash command definition
├── snippets/
│   └── defaults.json         ← 20 built-in prompt templates
├── tools/
│   ├── snippet.py            ← prompt manager CLI (Python 3.8+, stdlib only)
│   ├── install-snippet.ps1   ← Windows installer
│   └── install-snippet.sh    ← macOS / Linux installer
├── AGENT-CHEATSHEET.md       ← ready-to-use prompt examples
├── CLAUDE.md                 ← personal coding guidelines
├── INTEGRATION.md            ← claw-code integration guide
├── SETUP.md                  ← full environment setup
├── setup-agents.ps1          ← Windows agent installer
└── setup-agents.sh           ← macOS / Linux agent installer
```

---

## Full Documentation

| Document | Contents |
|----------|----------|
| [SETUP.md](SETUP.md) | Complete env setup: MCP servers, Docker, plugins, env vars |
| [AGENT-CHEATSHEET.md](AGENT-CHEATSHEET.md) | 20+ copy-paste-ready prompts |
| [INTEGRATION.md](INTEGRATION.md) | claw-code (Rust CLI harness) integration |
| [CLAUDE.md](CLAUDE.md) | Coding principles and response style guidelines |

---

## Context Cost Tips

| Situation | Command |
|-----------|---------|
| After finishing a step | `/compact` |
| Switching to a completely different task | `/clear` |
| Reference a specific file | `@src/auth.ts review this` |
| Check spend | `/cost` |

---

## Troubleshooting

**Agents not showing in `/agents`**
```bash
ls ~/.claude/agents/*.md   # files must be present
# Restart Claude Code
```

**Agent Teams not working**
```powershell
# Windows
[System.Environment]::GetEnvironmentVariable("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS","User")
# Should print: 1
```
```bash
# macOS / Linux
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS   # should print 1
```

**MCP connection error (-32000)**
```bash
docker ps   # verify GitHub MCP container is running
# Then inside Claude Code:
/mcp        # reconnect
```

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

- **New agent idea?** → open a [Feature Request](https://github.com/BcKmini/claude-code-multi-agent/issues/new?template=feature_request.md)
- **Bug?** → open a [Bug Report](https://github.com/BcKmini/claude-code-multi-agent/issues/new?template=bug_report.md)
- **New snippet idea?** → add it to `snippets/defaults.json` and send a PR

---

## License

[MIT](LICENSE)

---

<div align="center">

Made for developers who want Claude Code at its best.  
If this saved you time, a ⭐ star helps others find it.

</div>
