#!/usr/bin/env python3
"""
snippet v2.0 -- Personal prompt manager for Claude Code
Save, organize, and reuse prompts by name.

Homepage: https://github.com/BcKmini/claude-code-multi-agent
"""

VERSION = "2.0.0"

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

SNIPPETS_FILE = Path.home() / ".claude" / "snippets.json"
TEMPLATE_VAR_RE = re.compile(r"\{\{(\w+)\}\}")

# ---------------------------------------------------------------------------
# Color support  (no external deps -- ANSI + Windows VT mode)
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


def green(s):  return _c("32", s)
def yellow(s): return _c("33", s)
def cyan(s):   return _c("36", s)
def red(s):    return _c("31", s)
def bold(s):   return _c("1",  s)
def dim(s):    return _c("2",  s)
def magenta(s):return _c("35", s)


# ---------------------------------------------------------------------------
# Data I/O
# ---------------------------------------------------------------------------

def load() -> dict:
    if not SNIPPETS_FILE.exists():
        return {}
    with open(SNIPPETS_FILE, encoding="utf-8") as f:
        return json.load(f)


def dump(data: dict) -> None:
    SNIPPETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SNIPPETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Template variable helpers
# ---------------------------------------------------------------------------

def fill_vars(prompt: str, var_pairs: list) -> tuple:
    """
    Replace {{VAR}} placeholders with --var KEY=VALUE values.
    Returns (filled_prompt, list_of_missing_var_names).
    """
    values = {}
    for pair in (var_pairs or []):
        if "=" not in pair:
            print(red(f"[!] --var requires KEY=VALUE format, got: '{pair}'"),
                  file=sys.stderr)
            sys.exit(2)
        k, v = pair.split("=", 1)
        values[k.strip()] = v.strip()

    found = set(TEMPLATE_VAR_RE.findall(prompt))
    missing = sorted(v for v in found if v not in values)
    filled = TEMPLATE_VAR_RE.sub(
        lambda m: values.get(m.group(1), m.group(0)), prompt
    )
    return filled, missing


# ---------------------------------------------------------------------------
# Table formatters
# ---------------------------------------------------------------------------

_W = (20, 52, 26)   # column widths: name, preview, tags


def _row(name: str, data: dict, highlight: str = "") -> str:
    tags = (
        "[" + ", ".join(data.get("tags", [])) + "]"
        if data.get("tags") else ""
    )
    raw_preview = data["prompt"].split("\n")[0]
    preview = raw_preview[:_W[1]]
    uses = f"{data.get('uses', 0)}x"

    # Highlight keyword in name
    disp_name = name
    if highlight and highlight.lower() in name.lower():
        idx = name.lower().index(highlight.lower())
        disp_name = (
            name[:idx]
            + yellow(name[idx: idx + len(highlight)])
            + name[idx + len(highlight):]
        )

    # Pad based on raw (uncolored) lengths
    name_pad  = " " * max(0, _W[0] - len(name))
    tags_pad  = " " * max(0, _W[2] - len(tags))

    return (
        f"  {cyan(disp_name)}{name_pad}  "
        f"{preview:<{_W[1]}}  "
        f"{dim(tags)}{tags_pad}  "
        f"{dim(uses)}"
    )


def _sep() -> str:
    return "  " + dim("-" * (_W[0] + _W[1] + _W[2] + 10))


def _header() -> str:
    n_pad = " " * max(0, _W[0] - 4)
    p_pad = " " * max(0, _W[1] - 14)
    t_pad = " " * max(0, _W[2] - 4)
    return (
        f"\n  {bold('name')}{n_pad}  "
        f"{bold('prompt preview')}{p_pad}  "
        f"{bold('tags')}{t_pad}  "
        f"{bold('uses')}"
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_list(args):
    snippets = load()
    filtered = {
        k: v for k, v in snippets.items()
        if not args.tag or args.tag in v.get("tags", [])
    }

    if not filtered:
        msg = (f"No snippets with tag '{args.tag}'."
               if args.tag else "No snippets saved yet.")
        print(yellow(msg))
        print(dim("  Run:  snippet import snippets/defaults.json"))
        return

    key_fn = {
        "name":  lambda x: x[0].lower(),
        "uses":  lambda x: -x[1].get("uses", 0),
        "date":  lambda x: x[1].get("created", ""),
    }.get(args.sort_by, lambda x: x[0].lower())

    items = sorted(filtered.items(), key=key_fn)

    print(_header())
    print(_sep())
    for name, data in items:
        print(_row(name, data))
    print(f"\n  {dim(str(len(filtered)) + ' snippet(s)')}\n")


def cmd_save(args):
    snippets = load()
    name = args.name

    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(red(f"[!] File not found: {args.file}"))
            sys.exit(1)
        prompt = p.read_text(encoding="utf-8").strip()
    elif args.prompt:
        prompt = " ".join(args.prompt)
    else:
        print(red("[!] Provide a prompt string or --file path"))
        sys.exit(2)

    if not prompt:
        print(red("[!] Prompt cannot be empty"))
        sys.exit(2)

    if name in snippets and not args.force:
        print(yellow(f"[!] '{name}' already exists. Use --force to overwrite."))
        sys.exit(1)

    existed = name in snippets
    snippets[name] = {
        "prompt":  prompt,
        "tags":    [t.strip() for t in args.tags.split(",")] if args.tags else [],
        "created": datetime.now().strftime("%Y-%m-%d"),
        "uses":    snippets.get(name, {}).get("uses", 0),
    }
    dump(snippets)

    action = "overwritten" if existed else "saved"
    print(green(f"[OK] '{name}' {action}"))

    vars_found = sorted(set(TEMPLATE_VAR_RE.findall(prompt)))
    if vars_found:
        print(dim(f"     template vars: {', '.join(vars_found)}"))
        print(dim(f"     run with:  snippet run {name} "
                  + " ".join(f"--var {v}=..." for v in vars_found)))


def cmd_run(args):
    snippets = load()
    name = args.name

    if name not in snippets:
        print(red(f"[!] Snippet '{name}' not found."), file=sys.stderr)
        print(dim("    snippet list"), file=sys.stderr)
        sys.exit(1)

    prompt = snippets[name]["prompt"]

    # Fill template variables
    if args.var or TEMPLATE_VAR_RE.search(prompt):
        prompt, missing = fill_vars(prompt, args.var or [])
        if missing:
            print(yellow(f"[!] Unfilled template vars: {', '.join(missing)}"),
                  file=sys.stderr)
            print(dim(
                "    Re-run with: "
                + " ".join(f"--var {v}=<value>" for v in missing)
            ), file=sys.stderr)

    if args.dry_run:
        print(dim("--- dry run (not saving usage count) ---"), file=sys.stderr)
        print(prompt)
        return

    snippets[name]["uses"] = snippets[name].get("uses", 0) + 1
    dump(snippets)

    # Pure stdout -- pipeable to: snippet run name | claude
    print(prompt)


def cmd_show(args):
    snippets = load()
    name = args.name

    if name not in snippets:
        print(red(f"[!] '{name}' not found"))
        sys.exit(1)

    data = snippets[name]
    sep = dim("-" * 54)

    print(f"\n{sep}")
    print(f"  {bold(name)}")
    tags_str = ", ".join(data.get("tags", [])) or dim("—")
    print(f"  {dim('tags  :')} {tags_str}")
    print(f"  {dim('date  :')} {data.get('created', '?')}   "
          f"{dim('uses  :')} {data.get('uses', 0)}")

    vars_found = sorted(set(TEMPLATE_VAR_RE.findall(data["prompt"])))
    if vars_found:
        print(f"  {dim('vars  :')} {cyan(', '.join(vars_found))}")

    print(sep)
    print(data["prompt"])
    print(f"{sep}\n")


def cmd_edit(args):
    snippets = load()
    name = args.name

    if name not in snippets:
        print(red(f"[!] '{name}' not found"))
        sys.exit(1)

    editor = (
        os.environ.get("EDITOR")
        or os.environ.get("VISUAL")
        or ("notepad" if sys.platform == "win32" else "nano")
    )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as tf:
        tf.write(snippets[name]["prompt"])
        tmp = tf.name

    try:
        subprocess.run([editor, tmp], check=True)
        new_prompt = Path(tmp).read_text(encoding="utf-8").strip()
        if new_prompt and new_prompt != snippets[name]["prompt"]:
            snippets[name]["prompt"] = new_prompt
            dump(snippets)
            print(green(f"[OK] '{name}' updated"))
        else:
            print(dim("No changes."))
    finally:
        Path(tmp).unlink(missing_ok=True)


def cmd_delete(args):
    snippets = load()
    name = args.name

    if name not in snippets:
        print(red(f"[!] '{name}' not found"))
        sys.exit(1)

    if not args.force:
        sys.stdout.write(f"Delete {cyan(name)}? [y/N] ")
        sys.stdout.flush()
        ans = sys.stdin.readline().strip().lower()
        if ans not in ("y", "yes"):
            print(dim("Cancelled."))
            return

    del snippets[name]
    dump(snippets)
    print(green(f"[OK] '{name}' deleted"))


def cmd_search(args):
    snippets = load()
    kw = args.keyword.lower()
    tag_filter = args.tag

    results = {}
    for k, v in snippets.items():
        tag_ok = not tag_filter or tag_filter in v.get("tags", [])
        kw_ok = (
            kw in k.lower()
            or kw in v["prompt"].lower()
            or any(kw in t.lower() for t in v.get("tags", []))
        )
        if tag_ok and kw_ok:
            results[k] = v

    if not results:
        print(yellow(f"No results for '{args.keyword}'"))
        return

    print(f"\n{bold('Search:')} {cyan(args.keyword)}  "
          f"{dim('(' + str(len(results)) + ' result(s))')}")
    print(_sep())
    for name, data in sorted(results.items()):
        print(_row(name, data, highlight=args.keyword))
    print()


def cmd_tags(args):
    snippets = load()
    counts: dict = {}
    for data in snippets.values():
        for t in data.get("tags", []):
            counts[t] = counts.get(t, 0) + 1

    if not counts:
        print(dim("No tags in use."))
        return

    print(f"\n{bold('Tags:')}")
    for tag, n in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        bar = dim("|" * min(n, 20))
        print(f"  {cyan(f'{tag:<22}')}  {bar}  {dim(str(n))}")
    print()


def cmd_cp(args):
    snippets = load()
    src, dst = args.src, args.dst

    if src not in snippets:
        print(red(f"[!] '{src}' not found"))
        sys.exit(1)

    if dst in snippets and not args.force:
        print(yellow(f"[!] '{dst}' already exists. Use --force."))
        sys.exit(1)

    snippets[dst] = copy.deepcopy(snippets[src])
    snippets[dst]["created"] = datetime.now().strftime("%Y-%m-%d")
    snippets[dst]["uses"] = 0
    dump(snippets)
    print(green(f"[OK] '{src}'  ->  '{dst}'"))


def cmd_stats(args):
    snippets = load()
    if not snippets:
        print(dim("No snippets."))
        return

    total = len(snippets)
    total_uses = sum(v.get("uses", 0) for v in snippets.values())

    top5 = sorted(snippets.items(), key=lambda x: -x[1].get("uses", 0))[:5]

    counts: dict = {}
    for data in snippets.values():
        for t in data.get("tags", []):
            counts[t] = counts.get(t, 0) + 1

    print(f"\n{bold('Snippet Stats')}")
    print(dim("=" * 44))
    print(f"  {bold('Total snippets')}  {cyan(str(total))}")
    print(f"  {bold('Total runs    ')}  {cyan(str(total_uses))}")
    print()

    if total_uses > 0:
        print(bold("  Most used:"))
        for name, data in top5:
            u = data.get("uses", 0)
            if u == 0:
                break
            bar = green("#" * min(u, 24)) + dim("." * max(0, 24 - u))
            print(f"    {cyan(f'{name:<22}')}  {bar}  {u}x")
        print()

    if counts:
        print(bold("  Tags:"))
        for tag, n in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"    {cyan(f'{tag:<22}')}  {dim(str(n) + ' snippet(s)')}")
        print()


def cmd_import(args):
    path = Path(args.file)
    if not path.exists():
        print(red(f"[!] File not found: {args.file}"))
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        imported: dict = json.load(f)

    snippets = load()
    added = overwritten = skipped = 0

    for name, data in imported.items():
        if name in snippets:
            if args.overwrite:
                snippets[name] = data
                overwritten += 1
            else:
                skipped += 1
        else:
            snippets[name] = data
            added += 1

    dump(snippets)
    parts = [green(f"+{added} added")]
    if overwritten:
        parts.append(yellow(f"~{overwritten} overwritten"))
    if skipped:
        parts.append(dim(f"{skipped} skipped"))
    print("[OK] " + "  ".join(parts))


def cmd_export(args):
    snippets = load()

    if args.tag:
        snippets = {
            k: v for k, v in snippets.items()
            if args.tag in v.get("tags", [])
        }

    with open(args.file, "w", encoding="utf-8") as f:
        json.dump(snippets, f, ensure_ascii=False, indent=2)
    print(green(f"[OK] {len(snippets)} snippet(s)  ->  {args.file}"))


def cmd_version(args):
    print(f"snippet {bold(VERSION)}")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="snippet",
        description="Personal prompt manager for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  snippet list
  snippet list --tag pipeline --sort uses
  snippet save myfix "Fix the bug in {{FILE}}" --tags bug
  snippet run myfix --var FILE=src/auth.ts
  snippet run full-pipeline | claude
  snippet search security
  snippet stats
  snippet import snippets/defaults.json
""",
    )
    p.add_argument("--version", action="version", version=f"snippet {VERSION}")

    sub = p.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # list
    s = sub.add_parser("list", help="List saved snippets")
    s.add_argument("--tag",     help="Filter by tag")
    s.add_argument("--sort-by", dest="sort_by",
                   choices=["name", "uses", "date"], default="name",
                   help="Sort order (default: name)")
    s.set_defaults(func=cmd_list)

    # save
    s = sub.add_parser("save", help="Save a new snippet")
    s.add_argument("name",   help="Snippet name")
    s.add_argument("prompt", nargs="*",
                   help="Prompt text. Use {{VAR}} for template variables.")
    s.add_argument("--tags",  help="Comma-separated tags, e.g. --tags bug,auth")
    s.add_argument("--file",  help="Read prompt from file instead")
    s.add_argument("--force", action="store_true", help="Overwrite if exists")
    s.set_defaults(func=cmd_save)

    # run
    s = sub.add_parser("run",
                       help="Print prompt to stdout  (pipeable: snippet run X | claude)")
    s.add_argument("name", help="Snippet name")
    s.add_argument("--var", action="append", metavar="KEY=VALUE",
                   help="Fill {{KEY}} template variable (repeatable)")
    s.add_argument("--dry-run", action="store_true",
                   help="Preview filled prompt without incrementing usage counter")
    s.set_defaults(func=cmd_run)

    # show
    s = sub.add_parser("show", help="Show full snippet content")
    s.add_argument("name")
    s.set_defaults(func=cmd_show)

    # edit
    s = sub.add_parser("edit", help="Edit snippet in $EDITOR (or notepad on Windows)")
    s.add_argument("name")
    s.set_defaults(func=cmd_edit)

    # delete
    s = sub.add_parser("delete", aliases=["rm"],
                       help="Delete a snippet")
    s.add_argument("name")
    s.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    s.set_defaults(func=cmd_delete)

    # search
    s = sub.add_parser("search", help="Search by keyword across name, content, tags")
    s.add_argument("keyword")
    s.add_argument("--tag", help="Also filter by tag")
    s.set_defaults(func=cmd_search)

    # tags
    s = sub.add_parser("tags", help="List all tags in use")
    s.set_defaults(func=cmd_tags)

    # cp
    s = sub.add_parser("cp", help="Copy a snippet to a new name")
    s.add_argument("src", help="Source name")
    s.add_argument("dst", help="Destination name")
    s.add_argument("--force", "-f", action="store_true",
                   help="Overwrite destination if it exists")
    s.set_defaults(func=cmd_cp)

    # stats
    s = sub.add_parser("stats", help="Show usage statistics")
    s.set_defaults(func=cmd_stats)

    # import
    s = sub.add_parser("import", help="Import snippets from a JSON file")
    s.add_argument("file", help="Path to JSON file")
    s.add_argument("--overwrite", action="store_true",
                   help="Overwrite existing snippets with the same name")
    s.set_defaults(func=cmd_import)

    # export
    s = sub.add_parser("export", help="Export snippets to a JSON file")
    s.add_argument("file", help="Output path")
    s.add_argument("--tag", help="Export only snippets with this tag")
    s.set_defaults(func=cmd_export)

    # version
    s = sub.add_parser("version", help="Print version")
    s.set_defaults(func=cmd_version)

    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
