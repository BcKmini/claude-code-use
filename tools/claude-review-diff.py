#!/usr/bin/env python3
"""
claude-review-diff v1.0 — Generate a structured code review prompt from git diff.

Reads the current diff and wraps it in a review prompt ready to pipe into Claude.

Usage:
    claude-review-diff                        # review unstaged changes
    claude-review-diff --staged               # review staged (index) changes
    claude-review-diff --base main            # compare current branch to main
    claude-review-diff --focus security       # focus on specific concern
    claude-review-diff | claude               # pipe directly into Claude Code

Homepage: https://github.com/BcKmini/Claudecode-Agent
"""

VERSION = "1.0.0"

import argparse
import os
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
# Git helpers
# ---------------------------------------------------------------------------

def _run(cmd: list) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode, r.stdout.strip()
    except FileNotFoundError:
        return 1, ""


def _require_git() -> None:
    rc, _ = _run(["git", "rev-parse", "--git-dir"])
    if rc != 0:
        print(red("[!] Not inside a git repository."), file=sys.stderr)
        sys.exit(1)


def _branch() -> str:
    _, b = _run(["git", "branch", "--show-current"])
    return b or "HEAD"


def _get_diff(staged: bool, base: str | None, file: str | None) -> str:
    if base:
        cmd = ["git", "diff", base, "HEAD"]
    elif staged:
        cmd = ["git", "diff", "--staged"]
    else:
        cmd = ["git", "diff"]

    if file:
        cmd.append("--")
        cmd.append(file)

    _, diff = _run(cmd)
    return diff


def _diff_stats(staged: bool, base: str | None) -> str:
    if base:
        cmd = ["git", "diff", "--stat", base, "HEAD"]
    elif staged:
        cmd = ["git", "diff", "--staged", "--stat"]
    else:
        cmd = ["git", "diff", "--stat"]
    _, stats = _run(cmd)
    return stats


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

FOCUS_HINTS = {
    "security":     "Focus on security vulnerabilities: injection, auth bypass, data exposure, insecure defaults.",
    "performance":  "Focus on performance: N+1 queries, unnecessary allocations, blocking calls, missing indexes.",
    "correctness":  "Focus on correctness: logic errors, edge cases, off-by-one, null handling, error propagation.",
    "style":        "Focus on code style: naming, duplication, readability, unnecessary complexity.",
    "tests":        "Focus on test coverage: missing cases, flaky assertions, untested edge cases.",
    "all":          "Review for security, performance, correctness, style, and test coverage.",
}


def _build_prompt(diff: str, stats: str, branch: str, args) -> str:
    focus = args.focus or "all"
    hint = FOCUS_HINTS.get(focus, FOCUS_HINTS["all"])

    scope_desc = "staged changes" if args.staged else (
        f"diff against `{args.base}`" if args.base else "uncommitted changes"
    )

    lines = [
        f"You are a senior software engineer performing a code review.",
        f"",
        f"## Review Scope",
        f"Branch: `{branch}` — reviewing {scope_desc}.",
        f"",
        f"## Review Focus",
        f"{hint}",
        f"",
    ]

    if stats:
        lines += [
            "## Changed Files",
            "```",
            stats,
            "```",
            "",
        ]

    lines += [
        "## Diff",
        "```diff",
        diff,
        "```",
        "",
        "## Instructions",
        "For each issue found:",
        "1. Quote the relevant lines",
        "2. Explain the problem clearly",
        "3. Suggest a concrete fix",
        "",
        "Group findings by severity: **Critical** → **Major** → **Minor** → **Nit**.",
        "If the diff looks clean, say so explicitly.",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="claude-review-diff",
        description="Generate a structured code review prompt from git diff",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  claude-review-diff                          # review unstaged changes
  claude-review-diff --staged                 # review staged changes
  claude-review-diff --base main              # compare branch to main
  claude-review-diff --focus security         # security-only review
  claude-review-diff --file src/auth.py       # single file
  claude-review-diff | claude                 # pipe directly to Claude
""",
    )
    parser.add_argument("--staged", "-s", action="store_true",
                        help="Review staged (indexed) changes")
    parser.add_argument("--base", "-b", metavar="REF",
                        help="Compare current HEAD to this ref (branch/commit/tag)")
    parser.add_argument("--focus", "-f",
                        choices=list(FOCUS_HINTS.keys()),
                        default="all",
                        help="Review focus area (default: all)")
    parser.add_argument("--file", metavar="PATH",
                        help="Limit diff to a single file")
    parser.add_argument("--version", action="version",
                        version=f"claude-review-diff {VERSION}")
    args = parser.parse_args()

    _require_git()

    diff = _get_diff(args.staged, args.base, args.file)
    if not diff:
        scope = "staged" if args.staged else ("vs " + args.base if args.base else "unstaged")
        print(yellow(f"[!] No diff found ({scope})."), file=sys.stderr)
        print(dim("    Nothing to review."), file=sys.stderr)
        sys.exit(0)

    stats = _diff_stats(args.staged, args.base)
    branch = _branch()

    prompt = _build_prompt(diff, stats, branch, args)

    # Write prompt to stdout (pipeable to claude)
    print(prompt)

    if sys.stdout.isatty():
        lines = diff.count("\n")
        print(dim(f"\n-- {lines} diff lines | pipe to claude:  claude-review-diff | claude"),
              file=sys.stderr)


if __name__ == "__main__":
    main()
