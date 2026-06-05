#!/usr/bin/env python3
"""
claude-handoff v1.0 -- Session continuity tool for Claude Code

End a session cleanly. Resume it perfectly.
Save your work context before closing and pipe it back into Claude
at the start of your next session.

Homepage: https://github.com/BcKmini/Claudecode-Agent
"""

VERSION = "1.0.0"

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HANDOFFS_DIR = Path.home() / ".claude" / "handoffs"

# ---------------------------------------------------------------------------
# Color support
# ---------------------------------------------------------------------------

def _enable_win_vt() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)
    except Exception:
        pass


_enable_win_vt()
_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def green(s):   return _c("32", s)
def yellow(s):  return _c("33", s)
def cyan(s):    return _c("36", s)
def red(s):     return _c("31", s)
def bold(s):    return _c("1",  s)
def dim(s):     return _c("2",  s)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _git(args: list, cwd: str = None) -> str:
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True,
            cwd=cwd or os.getcwd()
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except FileNotFoundError:
        return ""


def _git_info() -> dict:
    return {
        "branch":   _git(["branch", "--show-current"]),
        "log":      _git(["log", "--oneline", "-5"]),
        "status":   _git(["status", "--short"]),
        "diff_stat":_git(["diff", "--stat", "HEAD"]),
        "remote":   _git(["remote", "get-url", "origin"]),
        "root":     _git(["rev-parse", "--show-toplevel"]),
    }


def _project_name() -> str:
    root = _git(["rev-parse", "--show-toplevel"])
    if root:
        return Path(root).name
    return Path.cwd().name


def _find_todo() -> str:
    """Look for a TODO/TASKS file in cwd and parents."""
    cwd = Path.cwd()
    for directory in [cwd] + list(cwd.parents)[:2]:
        for name in ("TODO.md", "TASKS.md", "TODO.txt", "TASKS.txt"):
            f = directory / name
            if f.exists():
                try:
                    content = f.read_text(encoding="utf-8")
                    lines = [l for l in content.splitlines() if l.strip()]
                    return "\n".join(lines[:20])
                except Exception:
                    pass
    return ""


# ---------------------------------------------------------------------------
# Handoff data
# ---------------------------------------------------------------------------

def _handoff_id() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _handoff_path(hid: str) -> Path:
    return HANDOFFS_DIR / f"{hid}.md"


def _list_handoffs() -> list:
    if not HANDOFFS_DIR.exists():
        return []
    files = sorted(HANDOFFS_DIR.glob("*.md"), reverse=True)
    items = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            # Extract first line after the header
            lines = content.splitlines()
            project = ""
            note = ""
            for line in lines:
                if line.startswith("**Project:**"):
                    project = line.replace("**Project:**", "").strip()
                if line.startswith("**Note:**"):
                    note = line.replace("**Note:**", "").strip()[:60]
                    break
            items.append({
                "id": f.stem,
                "path": f,
                "project": project,
                "note": note,
            })
        except Exception:
            pass
    return items


def _build_handoff_doc(note: str, git: dict) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    project = _project_name()
    todo = _find_todo()

    lines = [
        f"# Session Handoff — {ts}",
        "",
        f"**Project:** {project}",
        f"**Branch:**  {git['branch'] or '(not a git repo)'}",
        f"**Note:**    {note}",
        "",
    ]

    if git["log"]:
        lines += [
            "## Recent Commits",
            "```",
            git["log"],
            "```",
            "",
        ]

    if git["status"]:
        lines += [
            "## Uncommitted Changes",
            "```",
            git["status"],
            "```",
            "",
        ]

    if git["diff_stat"]:
        lines += [
            "## Changed Files (since HEAD)",
            "```",
            git["diff_stat"],
            "```",
            "",
        ]

    if todo:
        lines += [
            "## TODO / Tasks",
            "```",
            todo,
            "```",
            "",
        ]

    lines += [
        "---",
        "",
        "## Resume Prompt",
        "",
        "You are resuming a development session. The context above summarizes",
        "what was worked on and what changed.",
        "",
        f"Branch: `{git['branch'] or 'main'}`  |  Project: `{project}`",
        "",
        "Please acknowledge this handoff and confirm what we should focus on next.",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_save(args):
    HANDOFFS_DIR.mkdir(parents=True, exist_ok=True)

    note = args.note
    if not note:
        sys.stdout.write("Session note (what did you work on?): ")
        sys.stdout.flush()
        note = sys.stdin.readline().strip()
        if not note:
            note = "No note provided."

    git = _git_info()
    doc = _build_handoff_doc(note, git)

    hid = _handoff_id()
    path = _handoff_path(hid)
    path.write_text(doc, encoding="utf-8")

    print(green(f"[OK] Handoff saved: {hid}"))
    print(dim(f"     {path}"))
    print()
    print(dim("Resume next session with:"))
    print(f"  claude-handoff load | claude")
    print(f"  claude-handoff load --id {hid} | claude")


def cmd_load(args):
    items = _list_handoffs()
    if not items:
        print(red("[!] No handoffs found. Run: claude-handoff save"),
              file=sys.stderr)
        sys.exit(1)

    if args.id:
        matches = [i for i in items if i["id"] == args.id]
        if not matches:
            print(red(f"[!] Handoff '{args.id}' not found."), file=sys.stderr)
            sys.exit(1)
        item = matches[0]
    else:
        item = items[0]  # most recent

    content = item["path"].read_text(encoding="utf-8")

    # Print to stdout — pipeable to claude
    print(content)

    if sys.stdout.isatty():
        print(dim("\n-- Tip: pipe to claude:  claude-handoff load | claude"),
              file=sys.stderr)


def cmd_list(args):
    items = _list_handoffs()
    if not items:
        print(yellow("No handoffs saved yet."))
        print(dim("  Run: claude-handoff save"))
        return

    n = args.limit or 10
    items = items[:n]

    print(f"\n  {bold('id'):<22}  {bold('project'):<18}  {bold('note')}")
    print("  " + dim("-" * 80))
    for item in items:
        ts = item["id"][:8]  # YYYYMMDD
        ts_fmt = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
        print(f"  {cyan(item['id']):<{22+9}}  "
              f"{item['project']:<18}  "
              f"{dim(item['note'])}")
    print(f"\n  {dim(str(len(items)) + ' handoff(s)')}\n")


def cmd_show(args):
    items = _list_handoffs()
    if not items:
        print(yellow("No handoffs saved yet."))
        return

    if args.id:
        matches = [i for i in items if i["id"] == args.id]
        if not matches:
            print(red(f"[!] Handoff '{args.id}' not found."))
            sys.exit(1)
        item = matches[0]
    else:
        item = items[0]

    print(item["path"].read_text(encoding="utf-8"))


def cmd_clean(args):
    items = _list_handoffs()
    if not items:
        print(dim("Nothing to clean."))
        return

    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=args.days)
    to_delete = []

    for item in items:
        try:
            # id format: YYYYMMDD-HHMMSS
            dt = datetime.strptime(item["id"][:15], "%Y%m%d-%H%M%S")
            if dt < cutoff:
                to_delete.append(item)
        except ValueError:
            pass

    if not to_delete:
        print(dim(f"No handoffs older than {args.days} days."))
        return

    print(f"Will delete {len(to_delete)} handoff(s) older than {args.days} days.")
    if not args.force:
        sys.stdout.write("Proceed? [y/N] ")
        sys.stdout.flush()
        if sys.stdin.readline().strip().lower() not in ("y", "yes"):
            print(dim("Cancelled."))
            return

    for item in to_delete:
        item["path"].unlink(missing_ok=True)
    print(green(f"[OK] Deleted {len(to_delete)} handoff(s)."))


def cmd_version(args):
    print(f"claude-handoff {bold(VERSION)}")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="claude-handoff",
        description="Session continuity tool for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  claude-handoff save --note "finished auth module, reviewer next"
  claude-handoff load | claude
  claude-handoff list
  claude-handoff show
  claude-handoff clean --days 30
""",
    )
    p.add_argument("--version", action="version", version=f"claude-handoff {VERSION}")

    sub = p.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    s = sub.add_parser("save", help="Save current session context as a handoff")
    s.add_argument("--note", "-n", help="Short note about what you worked on")
    s.set_defaults(func=cmd_save)

    s = sub.add_parser("load",
                       help="Print handoff to stdout  (pipe to claude to resume)")
    s.add_argument("--id", help="Handoff ID (default: most recent)")
    s.set_defaults(func=cmd_load)

    s = sub.add_parser("list", help="List saved handoffs")
    s.add_argument("--limit", "-n", type=int, default=10,
                   help="Max entries to show (default: 10)")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="Show full handoff content")
    s.add_argument("--id", help="Handoff ID (default: most recent)")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("clean", help="Delete old handoffs")
    s.add_argument("--days", type=int, default=30,
                   help="Delete handoffs older than N days (default: 30)")
    s.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    s.set_defaults(func=cmd_clean)

    s = sub.add_parser("version", help="Print version")
    s.set_defaults(func=cmd_version)

    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
