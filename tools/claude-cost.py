#!/usr/bin/env python3
"""
claude-cost v1.0 -- Cost predictor and tracker for Claude Code

Know your cost BEFORE you run the task.
Track spending over time. Break down by agent and model.

Homepage: https://github.com/BcKmini/Claudecode-Agent
"""

VERSION = "1.0.0"

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECTS_DIR  = Path.home() / ".claude" / "projects"
SNIPPETS_FILE = Path.home() / ".claude" / "snippets.json"
BUDGET_FILE   = Path.home() / ".claude" / "cost-budget.json"

# ---------------------------------------------------------------------------
# Pricing  (USD per 1M tokens, June 2026)
# ---------------------------------------------------------------------------

PRICING = {
    "opus":   {"input": 15.00, "output": 75.00},
    "sonnet": {"input":  3.00, "output": 15.00},
    "haiku":  {"input":  0.25, "output":  1.25},
}

# Agent → default model mapping (matches this repo's agents/)
AGENT_MODELS = {
    "orchestrator":        "opus",
    "planner":             "opus",
    "security-auditor":    "opus",
    "implementer":         "sonnet",
    "reviewer":            "sonnet",
    "tester":              "sonnet",
    "performance-optimizer":"sonnet",
    "database-expert":     "sonnet",
    "documenter":          "haiku",
}

# Expected output/input token ratio per model (based on code tasks)
OUTPUT_RATIO = {"opus": 3.5, "sonnet": 2.5, "haiku": 1.5}

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
def magenta(s): return _c("35", s)


# ---------------------------------------------------------------------------
# Cost calculation
# ---------------------------------------------------------------------------

def calc_cost(input_tok: int, output_tok: int, model: str) -> float:
    p = PRICING.get(model, PRICING["sonnet"])
    return (input_tok * p["input"] + output_tok * p["output"]) / 1_000_000


def fmt_cost(amount: float) -> str:
    if amount < 0.001:
        return f"${amount * 1000:.3f}m"
    return f"${amount:.4f}"


def fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)


def estimate_tokens(text: str) -> int:
    """Rough approximation: ~4 chars per token for English/code."""
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Session log parsing
# ---------------------------------------------------------------------------

def _parse_sessions(days: int = 30) -> list:
    """
    Parse Claude Code project logs from ~/.claude/projects/.
    Returns list of dicts: {date, model, input_tokens, output_tokens, cost, file}
    """
    if not PROJECTS_DIR.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days)
    records = []

    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        for log_file in project_dir.glob("*.jsonl"):
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff:
                    continue
                with open(log_file, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        # Look for usage data in assistant messages
                        usage = None
                        msg = entry.get("message", {})
                        if isinstance(msg, dict):
                            usage = msg.get("usage")
                        if not usage:
                            usage = entry.get("usage")
                        if not usage:
                            continue

                        inp = usage.get("input_tokens", 0)
                        out = usage.get("output_tokens", 0)
                        if inp == 0 and out == 0:
                            continue

                        # Try to get model
                        model_raw = (
                            msg.get("model", "")
                            or entry.get("model", "")
                        )
                        if "opus" in model_raw:
                            model = "opus"
                        elif "haiku" in model_raw:
                            model = "haiku"
                        else:
                            model = "sonnet"

                        records.append({
                            "date":   mtime.strftime("%Y-%m-%d"),
                            "model":  model,
                            "input":  inp,
                            "output": out,
                            "cost":   calc_cost(inp, out, model),
                            "file":   str(log_file),
                        })
            except Exception:
                continue

    return records


# ---------------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------------

def _load_budget() -> dict:
    if BUDGET_FILE.exists():
        try:
            return json.loads(BUDGET_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_budget(data: dict) -> None:
    BUDGET_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_estimate(args):
    """Predict cost before running a task."""
    prompt_text = ""

    # Get prompt from snippet or direct input
    if args.snippet:
        if not SNIPPETS_FILE.exists():
            print(red("[!] No snippets.json found. Run: snippet import snippets/defaults.json"))
            sys.exit(1)
        snippets = json.loads(SNIPPETS_FILE.read_text(encoding="utf-8"))
        if args.snippet not in snippets:
            print(red(f"[!] Snippet '{args.snippet}' not found."))
            sys.exit(1)
        prompt_text = snippets[args.snippet]["prompt"]
        # Fill template vars if provided
        if args.var:
            import re
            for pair in args.var:
                if "=" not in pair:
                    continue
                k, v = pair.split("=", 1)
                prompt_text = prompt_text.replace("{{" + k.strip() + "}}", v.strip())
    elif args.prompt:
        prompt_text = " ".join(args.prompt)
    else:
        print(red("[!] Provide --snippet <name> or a prompt string"))
        sys.exit(2)

    input_toks = estimate_tokens(prompt_text)

    # Determine which agents to include
    if args.agents:
        agent_list = [(a.strip(), AGENT_MODELS.get(a.strip(), "sonnet"))
                      for a in args.agents.split(",")]
    else:
        # Default: full pipeline
        agent_list = [
            ("orchestrator",         "opus"),
            ("planner",              "opus"),
            ("implementer",          "sonnet"),
            ("reviewer",             "sonnet"),
            ("tester",               "sonnet"),
        ]

    print(f"\n{bold('Cost Estimate')}")
    print(dim("=" * 52))
    print(f"  Prompt tokens (est.)  {cyan(fmt_tokens(input_toks))}")
    print()

    total_cost = 0.0
    rows = []
    for agent_name, model in agent_list:
        out_toks = int(input_toks * OUTPUT_RATIO.get(model, 2.5))
        cost = calc_cost(input_toks, out_toks, model)
        total_cost += cost
        rows.append((agent_name, model, input_toks, out_toks, cost))

    print(f"  {bold('agent'):<22}  {bold('model'):<8}  {bold('in'):<7}  "
          f"{bold('out'):<7}  {bold('cost')}")
    print("  " + dim("-" * 52))
    for agent_name, model, inp, out, cost in rows:
        model_color = {
            "opus": magenta, "sonnet": cyan, "haiku": dim
        }.get(model, cyan)
        print(f"  {agent_name:<22}  {model_color(f'{model:<8}')}  "
              f"{dim(fmt_tokens(inp)):<{7+7}}  "
              f"{dim(fmt_tokens(out)):<{7+7}}  "
              f"{fmt_cost(cost)}")

    print("  " + dim("-" * 52))

    # Compare to budget
    budget = _load_budget()
    month_key = datetime.now().strftime("%Y-%m")
    spent_this_month = budget.get("spent", {}).get(month_key, 0.0)
    monthly_limit = budget.get("monthly_limit")

    color = yellow if total_cost > 0.10 else green
    print(f"  {bold('Total estimate')}          {color(fmt_cost(total_cost))}")

    if monthly_limit:
        remaining = monthly_limit - spent_this_month
        pct_of_remaining = (total_cost / remaining * 100) if remaining > 0 else 999
        print(f"  {dim('Monthly budget remaining')}  "
              f"{dim(fmt_cost(remaining))} "
              f"({dim(f'{pct_of_remaining:.1f}% of remainder')})")

    print()
    print(dim("Note: estimates use fixed output/input ratios. Actual cost may vary."))
    print()


def cmd_history(args):
    """Show past session costs."""
    records = _parse_sessions(days=args.days)

    if not records:
        print(yellow(f"No session data found in the last {args.days} days."))
        print(dim(f"  Sessions are stored in: {PROJECTS_DIR}"))
        return

    # Group by date
    by_date: dict = {}
    for r in records:
        d = r["date"]
        if d not in by_date:
            by_date[d] = {"cost": 0.0, "input": 0, "output": 0, "calls": 0}
        by_date[d]["cost"]   += r["cost"]
        by_date[d]["input"]  += r["input"]
        by_date[d]["output"] += r["output"]
        by_date[d]["calls"]  += 1

    total = sum(v["cost"] for v in by_date.values())

    print(f"\n{bold('Session History')}  {dim('(last ' + str(args.days) + ' days)')}")
    print(dim("=" * 52))
    print(f"  {bold('date'):<14}  {bold('calls'):<8}  "
          f"{bold('tokens in+out'):<18}  {bold('cost')}")
    print("  " + dim("-" * 52))

    for date in sorted(by_date.keys(), reverse=True):
        d = by_date[date]
        tokens_str = f"{fmt_tokens(d['input'])} + {fmt_tokens(d['output'])}"
        cost_color = yellow if d["cost"] > 0.50 else (
            green if d["cost"] < 0.10 else dim
        )
        print(f"  {cyan(date):<{14+9}}  {dim(str(d['calls'])):<{8+7}}  "
              f"{dim(tokens_str):<18}  {cost_color(fmt_cost(d['cost']))}")

    print("  " + dim("-" * 52))
    print(f"  {bold('Total')}  {green(fmt_cost(total))}")
    print()


def cmd_month(args):
    """Monthly cost summary."""
    records = _parse_sessions(days=90)

    target_month = args.month or datetime.now().strftime("%Y-%m")

    by_model: dict = {"opus": 0.0, "sonnet": 0.0, "haiku": 0.0}
    total = 0.0
    calls = 0

    for r in records:
        if not r["date"].startswith(target_month):
            continue
        by_model[r["model"]] = by_model.get(r["model"], 0.0) + r["cost"]
        total += r["cost"]
        calls += 1

    budget = _load_budget()
    monthly_limit = budget.get("monthly_limit")

    print(f"\n{bold('Monthly Summary')}  {cyan(target_month)}")
    print(dim("=" * 44))

    if calls == 0:
        print(yellow(f"  No data for {target_month}"))
    else:
        for model in ("opus", "sonnet", "haiku"):
            cost = by_model.get(model, 0.0)
            if cost == 0:
                continue
            pct = cost / total * 100 if total > 0 else 0
            bar_len = min(20, int(pct / 5))
            bar = green("#" * bar_len) + dim("." * (20 - bar_len))
            model_color = {"opus": magenta, "sonnet": cyan, "haiku": dim}.get(model, dim)
            print(f"  {model_color(f'{model:<8}')}  {bar}  "
                  f"{fmt_cost(cost)}  {dim(f'({pct:.0f}%)')}")

        print("  " + dim("-" * 44))
        print(f"  {bold('Total')}     {green(fmt_cost(total))}  "
              f"{dim('(' + str(calls) + ' API calls)')}")

        if monthly_limit:
            pct_used = total / monthly_limit * 100
            bar_len = min(30, int(pct_used / 100 * 30))
            color = red if pct_used > 80 else (yellow if pct_used > 50 else green)
            bar = color("#" * bar_len) + dim("." * (30 - bar_len))
            print()
            print(f"  Budget: [{bar}] {pct_used:.1f}%")
            print(f"  {fmt_cost(total)} / {fmt_cost(monthly_limit)} used  "
                  f"({dim(fmt_cost(monthly_limit - total) + ' remaining')})")

    print()


def cmd_agents(args):
    """Cost breakdown by agent model."""
    records = _parse_sessions(days=args.days)

    if not records:
        print(yellow("No session data found."))
        return

    by_model: dict = {}
    for r in records:
        m = r["model"]
        if m not in by_model:
            by_model[m] = {"cost": 0.0, "calls": 0, "input": 0, "output": 0}
        by_model[m]["cost"]   += r["cost"]
        by_model[m]["calls"]  += 1
        by_model[m]["input"]  += r["input"]
        by_model[m]["output"] += r["output"]

    total = sum(v["cost"] for v in by_model.values())

    print(f"\n{bold('Agent Cost Breakdown')}  {dim('(last ' + str(args.days) + ' days)')}")
    print(dim("=" * 56))
    print(f"  {bold('model'):<10}  {bold('calls'):<8}  "
          f"{bold('tokens'):<16}  {bold('cost'):<10}  {bold('share')}")
    print("  " + dim("-" * 56))

    for model in ("opus", "sonnet", "haiku"):
        d = by_model.get(model)
        if not d:
            continue
        pct = d["cost"] / total * 100 if total > 0 else 0
        tokens = f"{fmt_tokens(d['input'])}+{fmt_tokens(d['output'])}"
        model_color = {"opus": magenta, "sonnet": cyan, "haiku": dim}.get(model, dim)
        print(f"  {model_color(f'{model:<10}')}  {dim(str(d['calls'])):<{8+7}}  "
              f"{dim(tokens):<16}  {fmt_cost(d['cost']):<10}  "
              f"{dim(f'{pct:.1f}%')}")

    print("  " + dim("-" * 56))
    print(f"  {'Total':<10}  {dim(str(sum(d['calls'] for d in by_model.values()))):<{8+7}}  "
          f"{'':16}  {green(fmt_cost(total))}")
    print()

    print(bold("  Agent → Model mapping in this repo:"))
    for agent, model in sorted(AGENT_MODELS.items()):
        model_color = {"opus": magenta, "sonnet": cyan, "haiku": dim}.get(model, dim)
        print(f"    {agent:<26}  {model_color(model)}")
    print()


def cmd_set_budget(args):
    budget = _load_budget()
    budget["monthly_limit"] = args.amount
    _save_budget(budget)
    print(green(f"[OK] Monthly budget set to {fmt_cost(args.amount)}"))
    print(dim("     Use 'claude-cost month' to track progress."))


def cmd_version(args):
    print(f"claude-cost {bold(VERSION)}")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="claude-cost",
        description="Cost predictor and tracker for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  claude-cost estimate --snippet full-pipeline
  claude-cost estimate --snippet fix-bug --var BUG_DESCRIPTION="null ref"
  claude-cost estimate "Implement OAuth 2.0 login"
  claude-cost history
  claude-cost month
  claude-cost agents
  claude-cost set-budget 20.00
""",
    )
    p.add_argument("--version", action="version", version=f"claude-cost {VERSION}")

    sub = p.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    s = sub.add_parser("estimate",
                       help="Predict cost before running a task")
    s.add_argument("prompt", nargs="*",
                   help="Prompt text to estimate (or use --snippet)")
    s.add_argument("--snippet", "-s",
                   help="Use a saved snippet as the prompt")
    s.add_argument("--var", action="append", metavar="KEY=VALUE",
                   help="Fill {{KEY}} template variables")
    s.add_argument("--agents",
                   help="Comma-separated agents to include "
                        "(default: full pipeline)")
    s.set_defaults(func=cmd_estimate)

    s = sub.add_parser("history", help="Show daily cost history")
    s.add_argument("--days", type=int, default=14,
                   help="Look back N days (default: 14)")
    s.set_defaults(func=cmd_history)

    s = sub.add_parser("month", help="Monthly cost summary")
    s.add_argument("--month",
                   help="Month to show in YYYY-MM format (default: current month)")
    s.set_defaults(func=cmd_month)

    s = sub.add_parser("agents", help="Cost breakdown by agent model")
    s.add_argument("--days", type=int, default=30,
                   help="Look back N days (default: 30)")
    s.set_defaults(func=cmd_agents)

    s = sub.add_parser("set-budget",
                       help="Set monthly budget alert threshold (USD)")
    s.add_argument("amount", type=float, help="Monthly budget in USD")
    s.set_defaults(func=cmd_set_budget)

    s = sub.add_parser("version", help="Print version")
    s.set_defaults(func=cmd_version)

    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
