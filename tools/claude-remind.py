#!/usr/bin/env python3
"""
claude-remind v1.0 — Surface incomplete tasks at Claude Code session start.

Scans TODO.md, TASKS.md, and open checklist items in CLAUDE.md, then prints
a ready-to-paste session-start prompt with the pending items listed.

Usage:
    claude-remind                  # show all incomplete items
    claude-remind --quiet          # show count only
    claude-remind --file TODO.md   # specific file
    claude-remind | claude         # pipe directly into Claude

Homepage: https://github.com/BcKmini/Claudecode-Agent
"""

VERSION = "1.0.0"

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def _enable_win_vt() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7
        )
    except Exception:
        pass


_enable_win_vt()
_COLOR = sys.stderr.isatty() and not os.environ.get("NO_COLOR")


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def green(s):  return _c("32", s)
def yellow(s): return _c("33", s)
def cyan(s):   return _c("36", s)
def red(s):    return _c("31", s)
def bold(s):   return _c("1", s)
def dim(s):    return _c("2", s)


# ---------------------------------------------------------------------------
# Task detection
# ---------------------------------------------------------------------------

# Matches: - [ ] item   or   * [ ] item
UNCHECKED_RE = re.compile(r"^[\s]*[-*]\s+\[ \]\s+(.+)$", re.MULTILINE)
# Matches: - [x] item   (done)
CHECKED_RE   = re.compile(r"^[\s]*[-*]\s+\[x\]\s+.+$", re.MULTILINE | re.IGNORECASE)

CANDIDATE_FILES = [
    "TODO.md", "TASKS.md", "TODO.txt", "TASKS.txt",
    "CLAUDE.md", ".claude/CLAUDE.md",
]


def _git_root() -> Path | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(r.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _find_task_files(root: Path, explicit: str | None) -> list[Path]:
    if explicit:
        p = Path(explicit)
        return [p] if p.exists() else []

    found = []
    for name in CANDIDATE_FILES:
        p = root / name
        if p.exists():
            found.append(p)
    return found


def _extract_tasks(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    tasks = []
    for m in UNCHECKED_RE.finditer(text):
        tasks.append({"text": m.group(1).strip(), "source": path.name})

    return tasks


def _count_done(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return len(CHECKED_RE.findall(text))
    except OSError:
        return 0


def _git_branch() -> str:
    try:
        r = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, check=True,
        )
        return r.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(tasks: list[dict], branch: str, project: str) -> str:
    task_lines = "\n".join(f"- [ ] {t['text']}  ({t['source']})" for t in tasks)

    lines = [
        "You are resuming a development session.",
        "",
        f"## Project: {project}",
    ]
    if branch:
        lines.append(f"Branch: `{branch}`")
    lines += [
        "",
        f"## Pending Tasks ({len(tasks)} incomplete)",
        "",
        task_lines,
        "",
        "## Instructions",
        "Acknowledge these pending tasks. Ask which one to work on first,",
        "or proceed with the most logical next step if context is clear.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="claude-remind",
        description="Surface incomplete tasks at Claude Code session start",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  claude-remind                    # scan for all incomplete tasks
  claude-remind --quiet            # show summary only
  claude-remind --file TODO.md     # scan specific file
  claude-remind | claude           # pipe to Claude to resume session
""",
    )
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Print count only, no prompt")
    parser.add_argument("--file", metavar="PATH",
                        help="Scan a specific file instead of auto-detecting")
    parser.add_argument("--version", action="version",
                        version=f"claude-remind {VERSION}")
    args = parser.parse_args()

    root = _git_root() or Path.cwd()
    project = root.name

    task_files = _find_task_files(root, args.file)

    if not task_files:
        print(yellow("[!] No task files found (TODO.md / TASKS.md / CLAUDE.md)."),
              file=sys.stderr)
        print(dim("    Create a TODO.md with checkboxes:  - [ ] item"), file=sys.stderr)
        sys.exit(0)

    all_tasks: list[dict] = []
    done_total = 0
    for f in task_files:
        all_tasks.extend(_extract_tasks(f))
        done_total += _count_done(f)

    if not all_tasks:
        total = done_total
        print(green(f"[OK] No pending tasks found."), file=sys.stderr)
        if total:
            print(dim(f"     {total} completed task(s) in {[f.name for f in task_files]}"),
                  file=sys.stderr)
        sys.exit(0)

    if args.quiet:
        print(f"{len(all_tasks)} pending task(s) in {[f.name for f in task_files]}")
        sys.exit(0)

    branch = _git_branch()
    prompt = _build_prompt(all_tasks, branch, project)
    print(prompt)

    if sys.stdout.isatty():
        print(
            dim(f"\n-- {len(all_tasks)} pending, {done_total} done "
                f"| pipe to claude:  claude-remind | claude"),
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
