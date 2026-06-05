# Contributing Guide

Thank you for helping improve this project!

---

## Ways to contribute

| Type | How |
|------|-----|
| Bug fix | Open a bug report → submit a PR with the fix |
| New snippet | Add to `snippets/defaults.json` → PR |
| New agent | Add `.md` file to `agents/` → update README tables → PR |
| Documentation | Edit any `.md` file → PR |
| Translation | Improve `README.md` (EN) or `README.ko.md` (KO) |
| Feature idea | Open a Feature Request issue first |

---

## Development setup

```bash
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent
python --version   # 3.8+ required
```

`snippet.py` uses only the Python standard library — no `pip install` needed.

---

## Adding a new snippet

1. Open `snippets/defaults.json`
2. Add your entry following the existing format:

```json
"my-snippet": {
  "prompt": "Your prompt text here. Use {{VARIABLE}} for template vars.",
  "tags": ["tag1", "tag2"],
  "created": "YYYY-MM-DD",
  "uses": 0
}
```

3. Test it locally:
```bash
python tools/snippet.py import snippets/defaults.json --overwrite
python tools/snippet.py show my-snippet
python tools/snippet.py run my-snippet --dry-run
```

4. Update the snippet table in both `README.md` and `README.ko.md`

---

## Adding a new agent

1. Create `agents/NN-agent-name.md` following the format of existing agents
2. Add a row to the agent table in `README.md` and `README.ko.md`
3. Add a row to the table in `SETUP.md`
4. Update both install scripts (`setup-agents.ps1`, `setup-agents.sh`) if they hardcode agent names

---

## Code style (snippet.py)

- Standard library only — no external dependencies
- Python 3.8+ compatible (no walrus operator `:=` in loops, no `match`)
- All user-visible strings in English (Korean kept to comments only)
- `NO_COLOR` environment variable must be respected for color output
- Exit codes: `0` success, `1` not found / already exists, `2` usage error

---

## Pull Request checklist

- [ ] `python tools/snippet.py --help` still works
- [ ] All existing commands still work
- [ ] `snippet import snippets/defaults.json` still works
- [ ] README tables updated if new snippets / agents added
- [ ] No new external dependencies introduced

---

## License

By contributing, you agree your contributions will be released under the [MIT License](LICENSE).
