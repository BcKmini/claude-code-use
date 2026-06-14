#!/usr/bin/env python3
"""
claude-harness — AI harness design helper for Claude Code
Validates agent harness definitions and generates harness templates.

Usage:
  claude-harness validate <agent.md>
  claude-harness template tight|loose|adaptive
  claude-harness check-all
"""

import sys
import os
import re
import json
from pathlib import Path

VERSION = "1.0.0"
NO_COLOR = os.environ.get("NO_COLOR", "")


def green(s):
    return s if NO_COLOR else f"\033[32m{s}\033[0m"


def red(s):
    return s if NO_COLOR else f"\033[31m{s}\033[0m"


def yellow(s):
    return s if NO_COLOR else f"\033[33m{s}\033[0m"


def bold(s):
    return s if NO_COLOR else f"\033[1m{s}\033[0m"


def dim(s):
    return s if NO_COLOR else f"\033[2m{s}\033[0m"


HARNESS_CHECKS = [
    ("role_scoped", "Role is clearly scoped (not too broad)", r"(specialist|expert|only|exclusively|focus)", True),
    ("output_constrained", "Output format is constrained", r"(format|output|unified diff|json|markdown|schema)", True),
    ("forbidden_listed", "Forbidden actions are listed", r"(never|do not|must not|forbidden|절대)", True),
    ("tools_minimal", "Tools list is minimal", r"^tools:", True),
    ("language_support", "Bilingual language support", r"(Language:|language:|Korean|한국어)", True),
]


def parse_frontmatter(content):
    """Extract YAML frontmatter from a markdown file."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    fm_text = content[3:end].strip()
    body = content[end + 3:].strip()
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"')
    return fm, body


def validate_agent(path):
    """Validate a single agent file for harness quality."""
    path = Path(path)
    if not path.exists():
        print(red(f"  File not found: {path}"))
        return False

    content = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)
    full_text = content.lower()

    print(bold(f"\n{path.name}"))

    passed = 0
    failed = 0
    for check_id, label, pattern, required in HARNESS_CHECKS:
        found = bool(re.search(pattern, full_text, re.MULTILINE | re.IGNORECASE))
        if found:
            print(f"  {green('✓')} {label}")
            passed += 1
        else:
            marker = red("✗") if required else yellow("~")
            print(f"  {marker} {label}")
            if required:
                failed += 1

    # Check description bilingual
    desc = fm.get("description", "")
    if "|" in desc or ("(" in desc and ")" in desc):
        print(f"  {green('✓')} Description is bilingual")
        passed += 1
    else:
        print(f"  {yellow('~')} Description may not be bilingual (add EN | KO)")

    print(f"  {dim(f'Score: {passed}/{passed+failed} required checks passed')}")
    return failed == 0


def check_all_agents():
    """Check all agents in the agents/ directory."""
    agents_dir = Path(__file__).parent.parent / "agents"
    if not agents_dir.exists():
        # Try relative to cwd
        agents_dir = Path.cwd() / "agents"
    if not agents_dir.exists():
        print(red("agents/ directory not found"))
        sys.exit(1)

    agent_files = sorted(agents_dir.glob("*.md"))
    if not agent_files:
        print(red("No agent files found in agents/"))
        sys.exit(1)

    print(bold("Harness Quality Check — All Agents"))
    print(dim("=" * 50))

    total_pass = 0
    total_fail = 0
    for f in agent_files:
        ok = validate_agent(f)
        if ok:
            total_pass += 1
        else:
            total_fail += 1

    print(f"\n{dim('=' * 50)}")
    summary = f"Result: {total_pass} passed, {total_fail} failed"
    print(green(summary) if total_fail == 0 else yellow(summary))


TEMPLATES = {
    "tight": """\
---
name: {name}
description: "[EN description] | [KO 설명]"
model: claude-sonnet-4-5
tools: Read, Grep, Glob
permissionMode: default
---

> **Language:** Detect the user's language and respond in that language. Korean (한국어) and English both fully supported.

# {title} (Tight Harness — Specialist)

You are a [N-year] expert in [specific domain].
**You ONLY do [specific task]. Nothing else.**

## Input Contract
[Exact description of what you receive]

## Output Contract
Output ONLY in the following format — nothing else:
```
[exact output format, e.g., unified diff, JSON schema]
```

## Forbidden Actions
- Never [action 1]
- Never [action 2]
- Never modify files outside [scope]

## Validation
Before outputting, verify:
- [ ] Output matches the required format
- [ ] [domain-specific check]
""",
    "loose": """\
---
name: {name}
description: "[EN description] | [KO 설명]"
model: claude-opus-4-5
tools: Read, Write, Edit, Bash, Glob, Grep
---

> **Language:** Detect the user's language and respond in that language. Korean (한국어) and English both fully supported.

# {title} (Loose Harness — Generalist)

You are a [role] who helps with [broad domain].
Adapt your approach to what the user needs.

## Approach
1. Understand the request fully before acting
2. Ask clarifying questions if the goal is ambiguous
3. Propose your approach and get confirmation for significant changes

## Output Style
- Clear and concise
- Reference file paths and line numbers
- End with a 1-2 sentence summary of what changed
""",
    "adaptive": """\
---
name: {name}
description: "[EN description] | [KO 설명]"
model: claude-opus-4-5
tools: Read, Glob, Grep, Task, TodoWrite
---

> **Language:** Detect the user's language and respond in that language. Korean (한국어) and English both fully supported.

# {title} (Adaptive Harness — Orchestrator)

You coordinate specialist agents for multi-stage workflows.
**You do NOT implement. You delegate, validate, and integrate.**

## Pipeline Definition
Stage 1: [Stage name] → [validator]
Stage 2: [Stage name] → [validator]
Stage 3: [Stage name] → [validator]

## Context Isolation Rules
- Pass ONLY the output of the previous stage to the next agent
- Never accumulate full conversation history across stages

## Quality Gates
Every stage must pass its validator before proceeding.
On failure: retry up to 3 times, then escalate to human.

## Human Oversight Points
- [Stage N]: human reviews before Stage N+1
- Final output: human approves before applying
""",
}


def print_template(harness_type, name="my-agent"):
    if harness_type not in TEMPLATES:
        print(red(f"Unknown harness type: {harness_type}"))
        print(f"Available: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)
    title = name.replace("-", " ").title()
    print(TEMPLATES[harness_type].format(name=name, title=title))


def usage():
    print(f"""{bold('claude-harness')} v{VERSION} — AI harness design helper

{bold('Commands:')}
  validate <agent.md>            Validate a single agent file
  check-all                      Check all agents in agents/
  template tight|loose|adaptive  Print a harness template

{bold('Examples:')}
  claude-harness validate agents/03-reviewer.md
  claude-harness check-all
  claude-harness template tight > agents/11-my-specialist.md
""")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        usage()
        sys.exit(0)

    cmd = args[0]
    if cmd == "validate":
        if len(args) < 2:
            print(red("Usage: claude-harness validate <agent.md>"))
            sys.exit(2)
        ok = validate_agent(args[1])
        sys.exit(0 if ok else 1)
    elif cmd == "check-all":
        check_all_agents()
    elif cmd == "template":
        harness_type = args[1] if len(args) > 1 else "tight"
        agent_name = args[2] if len(args) > 2 else "my-specialist"
        print_template(harness_type, agent_name)
    else:
        print(red(f"Unknown command: {cmd}"))
        usage()
        sys.exit(2)


if __name__ == "__main__":
    main()
