#!/usr/bin/env python3
"""
claude-pipeline — Pipeline status tracker for Claude Code multi-agent workflows
Tracks stage progress, logs results, and generates pipeline run reports.

Usage:
  claude-pipeline init <name>
  claude-pipeline stage <name> start|pass|warn|fail [--note "..."]
  claude-pipeline status
  claude-pipeline report
  claude-pipeline list
  claude-pipeline clear
"""

import sys
import os
import json
import datetime
from pathlib import Path

VERSION = "1.0.0"
NO_COLOR = os.environ.get("NO_COLOR", "")

PIPELINE_DIR = Path.home() / ".claude" / "pipelines"
PIPELINE_DIR.mkdir(parents=True, exist_ok=True)


def green(s): return s if NO_COLOR else f"\033[32m{s}\033[0m"
def red(s): return s if NO_COLOR else f"\033[31m{s}\033[0m"
def yellow(s): return s if NO_COLOR else f"\033[33m{s}\033[0m"
def blue(s): return s if NO_COLOR else f"\033[34m{s}\033[0m"
def bold(s): return s if NO_COLOR else f"\033[1m{s}\033[0m"
def dim(s): return s if NO_COLOR else f"\033[2m{s}\033[0m"


STATUS_ICONS = {
    "pending":  "○",
    "running":  "●",
    "pass":     "✅",
    "warn":     "⚠️",
    "fail":     "❌",
    "skipped":  "—",
}


def active_pipeline_path():
    marker = PIPELINE_DIR / ".active"
    if marker.exists():
        name = marker.read_text().strip()
        p = PIPELINE_DIR / f"{name}.json"
        if p.exists():
            return p
    return None


def load_pipeline(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_pipeline(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")


def cmd_init(args):
    if not args:
        print(red("Usage: claude-pipeline init <name>"))
        sys.exit(2)
    name = args[0].replace(" ", "-").lower()
    path = PIPELINE_DIR / f"{name}.json"
    if path.exists():
        print(yellow(f"Pipeline '{name}' already exists. Use 'status' or 'clear' first."))
        sys.exit(1)

    data = {
        "name": name,
        "created": now_iso(),
        "stages": [],
        "metadata": {}
    }
    save_pipeline(path, data)
    (PIPELINE_DIR / ".active").write_text(name)
    print(green(f"Pipeline '{name}' initialized and set as active."))
    print(dim(f"  Stored at: {path}"))


def cmd_stage(args):
    if len(args) < 2:
        print(red("Usage: claude-pipeline stage <name> start|pass|warn|fail [--note '...']"))
        sys.exit(2)

    stage_name = args[0]
    action = args[1].lower()

    note = ""
    if "--note" in args:
        idx = args.index("--note")
        if idx + 1 < len(args):
            note = args[idx + 1]

    path = active_pipeline_path()
    if not path:
        print(red("No active pipeline. Run: claude-pipeline init <name>"))
        sys.exit(1)

    data = load_pipeline(path)
    ts = now_iso()

    # Find existing stage entry
    existing = next((s for s in data["stages"] if s["name"] == stage_name), None)

    if action == "start":
        if existing:
            existing["status"] = "running"
            existing["started_at"] = ts
        else:
            data["stages"].append({
                "name": stage_name,
                "status": "running",
                "started_at": ts,
                "finished_at": None,
                "note": note
            })
        print(blue(f"  ● {stage_name} — started"))
    elif action in ("pass", "warn", "fail"):
        if existing:
            existing["status"] = action
            existing["finished_at"] = ts
            if note:
                existing["note"] = note
        else:
            data["stages"].append({
                "name": stage_name,
                "status": action,
                "started_at": ts,
                "finished_at": ts,
                "note": note
            })
        icon = STATUS_ICONS.get(action, "?")
        color = green if action == "pass" else (yellow if action == "warn" else red)
        print(color(f"  {icon} {stage_name} — {action}" + (f" ({note})" if note else "")))
    else:
        print(red(f"Unknown action: {action}. Use start|pass|warn|fail"))
        sys.exit(2)

    save_pipeline(path, data)


def cmd_status():
    path = active_pipeline_path()
    if not path:
        print(yellow("No active pipeline."))
        print(dim("  Run: claude-pipeline init <name>"))
        return

    data = load_pipeline(path)
    print(bold(f"Pipeline: {data['name']}"))
    print(dim(f"  Created: {data['created']}"))
    print()

    if not data["stages"]:
        print(dim("  No stages recorded yet."))
        return

    for stage in data["stages"]:
        status = stage["status"]
        icon = STATUS_ICONS.get(status, "?")
        note = f" — {stage['note']}" if stage.get("note") else ""
        color = (green if status == "pass"
                 else yellow if status == "warn"
                 else red if status == "fail"
                 else blue if status == "running"
                 else dim)
        print(color(f"  {icon}  {stage['name']}{note}"))

    counts = {s: sum(1 for x in data["stages"] if x["status"] == s)
              for s in ["pass", "warn", "fail", "running"]}
    print()
    summary_parts = []
    if counts["pass"]: summary_parts.append(green(f"{counts['pass']} passed"))
    if counts["warn"]: summary_parts.append(yellow(f"{counts['warn']} warnings"))
    if counts["fail"]: summary_parts.append(red(f"{counts['fail']} failed"))
    if counts["running"]: summary_parts.append(blue(f"{counts['running']} running"))
    print("  " + " · ".join(summary_parts))


def cmd_report():
    path = active_pipeline_path()
    if not path:
        print(red("No active pipeline."))
        sys.exit(1)

    data = load_pipeline(path)
    stages = data["stages"]

    passed = [s for s in stages if s["status"] == "pass"]
    warned = [s for s in stages if s["status"] == "warn"]
    failed = [s for s in stages if s["status"] == "fail"]

    lines = [
        f"## Pipeline Run Report: {data['name']}",
        f"",
        f"### Summary",
        f"- Total stages: {len(stages)}",
        f"- Passed: {len(passed)} | Warnings: {len(warned)} | Failed: {len(failed)}",
        f"- Run started: {data['created']}",
        f"",
        f"### Stage Results",
        f"| Stage | Status | Notes |",
        f"|-------|--------|-------|",
    ]

    for s in stages:
        icon = STATUS_ICONS.get(s["status"], "?")
        note = s.get("note", "")
        lines.append(f"| {s['name']} | {icon} {s['status'].upper()} | {note} |")

    if failed:
        lines += [f"", f"### Failed Stages — Human Review Required"]
        for s in failed:
            lines.append(f"- **{s['name']}**: {s.get('note', 'no details')}")

    print("\n".join(lines))


def cmd_list():
    files = sorted(PIPELINE_DIR.glob("*.json"))
    active_path = active_pipeline_path()
    active_name = active_path.stem if active_path else None

    if not files:
        print(dim("No pipelines found."))
        return

    print(bold("Saved pipelines:"))
    for f in files:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            marker = green(" ◀ active") if f.stem == active_name else ""
            stage_count = len(d.get("stages", []))
            print(f"  {d['name']}{marker}  {dim(f'{stage_count} stages · created {d[\"created\"][:10]}')}")
        except Exception:
            print(f"  {f.stem} {red('(corrupted)')}")


def cmd_clear():
    path = active_pipeline_path()
    if path:
        path.unlink()
        (PIPELINE_DIR / ".active").unlink(missing_ok=True)
        print(green("Active pipeline cleared."))
    else:
        print(dim("No active pipeline to clear."))


def usage():
    print(f"""{bold('claude-pipeline')} v{VERSION} — Pipeline status tracker

{bold('Commands:')}
  init <name>                     Create and activate a new pipeline
  stage <name> start|pass|warn|fail [--note "..."]
                                  Record a stage result
  status                          Show active pipeline status
  report                          Print a markdown run report
  list                            List all saved pipelines
  clear                           Clear the active pipeline

{bold('Examples:')}
  claude-pipeline init slow-query-fix
  claude-pipeline stage "query-detection" start
  claude-pipeline stage "query-detection" pass --note "found 3 slow queries"
  claude-pipeline stage "patch-generation" start
  claude-pipeline stage "patch-generation" warn --note "1 query had no safe optimization"
  claude-pipeline report
""")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        usage()
        sys.exit(0)

    cmd = args[0]
    rest = args[1:]

    if cmd == "init":
        cmd_init(rest)
    elif cmd == "stage":
        cmd_stage(rest)
    elif cmd == "status":
        cmd_status()
    elif cmd == "report":
        cmd_report()
    elif cmd == "list":
        cmd_list()
    elif cmd == "clear":
        cmd_clear()
    else:
        print(red(f"Unknown command: {cmd}"))
        usage()
        sys.exit(2)


if __name__ == "__main__":
    main()
