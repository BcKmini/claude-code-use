# /review-diff — Code Review from Git Diff

Generate a structured code review prompt from the current git diff and pipe it to Claude.

## Usage

```
/review-diff                        # review unstaged changes
/review-diff --staged               # review staged changes
/review-diff --base main            # compare current branch to main
/review-diff --focus security       # focus on one concern
/review-diff --file src/auth.py     # single file only
```

## Focus options

| Flag | What Claude checks |
|------|--------------------|
| `--focus security` | Injection, auth bypass, data exposure |
| `--focus performance` | N+1, allocations, blocking calls |
| `--focus correctness` | Logic errors, edge cases, null handling |
| `--focus style` | Naming, duplication, readability |
| `--focus tests` | Missing coverage, flaky assertions |
| `--focus all` | All of the above (default) |

## Output format

Claude will group findings by severity:

```
Critical → Major → Minor → Nit
```

Each finding includes the quoted lines, the problem, and a concrete fix suggestion.

## Tool

Runs `python tools/claude-review-diff.py` (or `claude-review-diff` if installed globally).

Install: `make install-tools`
