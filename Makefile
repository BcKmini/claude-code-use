# Claude Code Productivity Tools — Makefile
# Usage: make help

SHELL      := /usr/bin/env bash
RUST_DIR   := rust
TOOLS_DIR  := tools
AGENTS_DIR := agents

CLAUDE_HOME   ?= $(HOME)/.claude
AGENTS_TARGET := $(CLAUDE_HOME)/agents
COMMANDS_TARGET := $(CLAUDE_HOME)/commands
BIN_TARGET    ?= $(HOME)/.local/bin

CARGO := cargo
PYTHON := python3

.DEFAULT_GOAL := help

# ─── help ──────────────────────────────────────────────────────────────────
.PHONY: help
help: ## Show available targets
	@printf "\n\033[1mClaude Code Tools\033[0m\n\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ─── build ─────────────────────────────────────────────────────────────────
.PHONY: build build-dev check
build: ## Build Rust claude-tools (release)
	cd $(RUST_DIR) && $(CARGO) build --release
	@echo "Binary: $(RUST_DIR)/target/release/claude-tools"

build-dev: ## Build Rust claude-tools (debug, faster)
	cd $(RUST_DIR) && $(CARGO) build

check: ## Cargo check (no binary output)
	cd $(RUST_DIR) && $(CARGO) check

# ─── install ───────────────────────────────────────────────────────────────
.PHONY: install install-agents install-commands install-tools install-rust
install: install-agents install-commands install-tools ## Install agents + slash commands + Python tools

install-agents: ## Install agents to ~/.claude/agents/
	@mkdir -p $(AGENTS_TARGET)
	@count=0; \
	for f in $(AGENTS_DIR)/*.md; do \
	  cp "$$f" $(AGENTS_TARGET)/; count=$$((count+1)); \
	done; \
	echo "Installed $$count agents → $(AGENTS_TARGET)"

install-commands: ## Install slash commands to ~/.claude/commands/
	@mkdir -p $(COMMANDS_TARGET)
	@count=0; \
	for f in .claude/commands/*.md; do \
	  cp "$$f" $(COMMANDS_TARGET)/; count=$$((count+1)); \
	done; \
	echo "Installed $$count commands → $(COMMANDS_TARGET)"

install-tools: ## Install Python tools to ~/.local/bin/
	@mkdir -p $(BIN_TARGET)
	@for tool in snippet claude-handoff claude-cost claude-review-diff claude-remind claude-harness claude-pipeline; do \
	  src="$(TOOLS_DIR)/$$tool.py"; \
	  dst="$(BIN_TARGET)/$$tool"; \
	  if [ -f "$$src" ]; then \
	    cp "$$src" "$$dst" && chmod +x "$$dst"; \
	    echo "  ✓ $$tool → $(BIN_TARGET)/$$tool"; \
	  fi; \
	done

install-rust: build ## Build Rust binary and install to ~/.local/bin/
	@mkdir -p $(BIN_TARGET)
	cp $(RUST_DIR)/target/release/claude-tools $(BIN_TARGET)/claude-tools
	@echo "Installed claude-tools → $(BIN_TARGET)/claude-tools"

# ─── test ──────────────────────────────────────────────────────────────────
.PHONY: test test-rust test-python test-agents
test: test-rust test-python ## Run all tests

test-rust: ## Cargo check + clippy
	cd $(RUST_DIR) && $(CARGO) check
	cd $(RUST_DIR) && $(CARGO) clippy -- -D warnings 2>/dev/null || true

test-python: ## Smoke-test Python tools
	@echo "Testing claude-handoff..."
	@$(PYTHON) $(TOOLS_DIR)/claude-handoff.py save --note "make test" \
	  && echo "  ✓ handoff save" || echo "  ✗ handoff save"
	@echo "Testing claude-cost..."
	@$(PYTHON) $(TOOLS_DIR)/claude-cost.py month \
	  && echo "  ✓ cost month" || echo "  ✗ cost month"
	@echo "Testing claude-remind..."
	@$(PYTHON) $(TOOLS_DIR)/claude-remind.py --quiet \
	  && echo "  ✓ remind --quiet" || echo "  ✗ remind"
	@echo "Testing claude-harness..."
	@$(PYTHON) $(TOOLS_DIR)/claude-harness.py --help > /dev/null \
	  && echo "  ✓ harness --help" || echo "  ✗ harness"
	@echo "Testing claude-pipeline..."
	@$(PYTHON) $(TOOLS_DIR)/claude-pipeline.py --help > /dev/null \
	  && echo "  ✓ pipeline --help" || echo "  ✗ pipeline"

test-agents: ## Verify agent files exist and are non-empty
	@ok=0; fail=0; \
	for f in $(AGENTS_DIR)/*.md; do \
	  if [ -s "$$f" ]; then ok=$$((ok+1)); \
	  else echo "  empty: $$f"; fail=$$((fail+1)); fi; \
	done; \
	echo "Agents: $$ok OK, $$fail empty"

# ─── lint / format ─────────────────────────────────────────────────────────
.PHONY: lint fmt fmt-check
lint: ## Clippy lint (Rust)
	cd $(RUST_DIR) && $(CARGO) clippy -- -D warnings

fmt: ## Format all code (Rust + Python)
	bash scripts/fmt.sh

fmt-check: ## Check formatting without modifying (CI mode)
	bash scripts/fmt.sh --check

# ─── dev helpers ───────────────────────────────────────────────────────────
.PHONY: watch-cost env status dogfood container validate
watch-cost: ## Live cost monitor (requires claude-tools build)
	@$(RUST_DIR)/target/release/claude-tools watch --interval 2

dogfood: ## Build from source with provenance check (like claw-code)
	@bash scripts/dogfood-build.sh

container: ## Build Containerfile (requires Docker / Podman)
	@command -v docker >/dev/null 2>&1 && docker build -f Containerfile -t claude-agents:dev . \
	  || command -v podman >/dev/null 2>&1 && podman build -f Containerfile -t claude-agents:dev . \
	  || { echo "docker or podman required"; exit 1; }

validate: ## Validate agent MD files
	@bash scripts/validate-agents.sh

env: ## Show Claude environment status
	@$(RUST_DIR)/target/release/claude-tools env

status: ## Show git + agent + tool install status
	@echo "=== Git ==="
	@git log --oneline -3
	@echo ""
	@echo "=== Agents installed ==="
	@ls $(AGENTS_TARGET)/*.md 2>/dev/null | wc -l | xargs -I{} echo "  {} agents in $(AGENTS_TARGET)"
	@echo ""
	@echo "=== Tools in PATH ==="
	@for t in snippet claude-handoff claude-cost claude-review-diff claude-remind claude-harness claude-pipeline claude-tools; do \
	  command -v $$t >/dev/null 2>&1 \
	    && echo "  ✓ $$t" \
	    || echo "  ✗ $$t (not installed)"; \
	done

env: ## Show Claude environment status (requires make install-rust first)
	@$(RUST_DIR)/target/release/claude-tools env 2>/dev/null \
	  || $(PYTHON) -c "print('Run: make install-rust first')"

# ─── release / version ─────────────────────────────────────────────────────
VERSION := $(shell cat VERSION)

.PHONY: tag release bump-patch bump-minor bump-major
tag: ## Create and push a release tag  (usage: make tag v=1.2.0)
ifndef v
	$(error Usage: make tag v=1.2.0)
endif
	@echo "$(v)" > VERSION
	@sed -i.bak 's/^version = .*/version = "$(v)"/' $(RUST_DIR)/claude-tools/Cargo.toml && rm -f $(RUST_DIR)/claude-tools/Cargo.toml.bak
	git add VERSION $(RUST_DIR)/claude-tools/Cargo.toml
	git commit -m "chore: bump version to v$(v)"
	git tag -a "v$(v)" -m "Release v$(v)"
	git push origin HEAD:main
	git push origin "v$(v)"
	@echo ""
	@echo "  Tag v$(v) pushed → GitHub Actions will build & release automatically."
	@echo "  Watch: https://github.com/BcKmini/claude-code-use/actions"

version: ## Show current version
	@echo "Current version: v$(VERSION)"

# ─── clean ─────────────────────────────────────────────────────────────────
.PHONY: clean clean-handoffs
clean: ## Remove Rust build artifacts
	cd $(RUST_DIR) && $(CARGO) clean

clean-handoffs: ## Remove saved handoff files
	@rm -f $(CLAUDE_HOME)/handoffs/*.md \
	  && echo "Cleared handoffs" || true
