**[한국어](CONTRIBUTING.ko.md)** · **English**

# Contributing Guide

Thank you for helping improve this project!

---

## Ways to Contribute

| Type | How |
|------|-----|
| Bug fix | Open a bug report → submit a PR with the fix |
| New snippet | Add to `snippets/defaults.json` → PR |
| New agent | Add `.md` file to `agents/` → update README tables → PR |
| Documentation | Edit any `.md` file → PR |
| Translation | Improve `README.md` (EN) or `README.ko.md` (KO) |
| Feature idea | Open a Feature Request issue first |

---

## Development Setup

```bash
git clone https://github.com/BcKmini/Claudecode-Agent.git
cd Claudecode-Agent
python --version   # 3.8+ required
```

`snippet.py`, `claude-handoff.py`, `claude-cost.py` use only the Python standard library — no `pip install` needed.

For the Rust binary:

```bash
cd rust
cargo check   # verify build
cargo build --release
```

---

## Adding a New Snippet

1. Open `snippets/defaults.json`
2. Add your entry:

```json
"my-snippet": {
  "prompt": "Your prompt here. Use {{VARIABLE}} for template vars.",
  "tags": ["tag1", "tag2"],
  "created": "YYYY-MM-DD",
  "uses": 0
}
```

3. Test locally:
```bash
python tools/snippet.py import snippets/defaults.json --overwrite
python tools/snippet.py show my-snippet
python tools/snippet.py run my-snippet --dry-run
```

4. Update the snippet table in both `README.md` and `README.ko.md`

---

## Adding a New Agent

1. Create `agents/NN-agent-name.md` following the format of existing agents
2. Add a row to the agent table in `README.md` and `README.ko.md`
3. Update both install scripts if they hardcode agent names

---

## Code Style

### Python tools
- Standard library only — no external dependencies
- Python 3.8+ compatible
- All user-visible strings in English
- `NO_COLOR` environment variable must be respected
- Exit codes: `0` success, `1` not found / exists, `2` usage error

### Rust (claude-tools)
- `cargo check` must pass with no errors
- Minimize `cargo clippy` warnings
- New subcommands follow the pattern of existing modules in `rust/claude-tools/src/`

---

## Pull Request Checklist

- [ ] `python tools/snippet.py --help` still works
- [ ] All existing commands still work
- [ ] `snippet import snippets/defaults.json` still works
- [ ] `cargo check` passes (Rust changes)
- [ ] README tables updated if new snippets / agents added
- [ ] Both EN and KO docs updated where applicable
- [ ] No new external dependencies introduced

---

## License

By contributing, you agree your contributions will be released under the [MIT License](../LICENSE).
