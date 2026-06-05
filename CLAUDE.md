[← Back to README](./README.md)

**[한국어](CLAUDE.ko.md)** · **English**

# CLAUDE.md — Personal Development Guidelines

Coding behavior principles for a full-stack + AI multi-project environment.
Merge with per-project CLAUDE.md files as needed.

---

## 1. Think Before Coding

**State assumptions explicitly. Don't hide confusion. Surface trade-offs.**

Before implementing:
- If you have assumptions, state them. If uncertain, ask.
- If there are multiple interpretations, present all of them — don't silently pick one.
- If there's a simpler approach, mention it first.
- If something is unclear, stop. Identify what's confusing and ask.

## 2. Simplicity First

**Minimum code that solves the problem. No speculative code.**

- Don't add features that weren't asked for.
- Don't build abstraction layers for single-use code.
- Don't add "flexibility" or "configurability" that wasn't requested.
- Don't add error handling for scenarios that can't happen.
- If you wrote 200 lines and it could be 50, rewrite it.

A senior engineer looking at it shouldn't ask "why is this so complex?"

## 3. Surgical Changes

**Touch only what must be changed. Clean up only your own mess.**

When modifying existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that work fine.
- Match the existing style even if you'd do it differently.
- If you find unrelated dead code, note it — don't delete it.

Clean up what your changes orphan:
- Remove imports/variables/functions that became unused due to your change.
- Don't touch pre-existing dead code unless asked.

Test: every changed line must trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Convert tasks into verifiable goals:
- "add validation" → "write tests for invalid inputs, make them pass"
- "fix bug" → "write a test that reproduces the bug, make it pass"
- "refactor" → "tests must pass before and after"

For multi-step tasks, present a simple plan first:
```
1. [step] → verify: [how to check]
2. [step] → verify: [how to check]
3. [step] → verify: [how to check]
```

---

## Stack-Specific Rules

### Frontend (React / Next.js / Vue)
- Single responsibility per component. If one does too much, propose splitting.
- Clearly separate client state and server state (React Query / Zustand, etc.).
- Never use `any` type. If unsure, ask.
- Follow the existing project's styling pattern (CSS-in-JS vs Tailwind, etc.).

### Backend (Node / Python / FastAPI / Express)
- Validate input only at system boundaries. Trust internal functions.
- Always use parameter binding for SQL queries. Never concatenate strings.
- Never hardcode environment variables — use `.env` or a secrets manager.
- Be consistent with async code (don't mix async/await and callbacks).

### AI / ML
- Version-control prompts (separate files, date tags recommended).
- Always mention LLM call cost estimates (token count, model selection rationale).
- Never trust model output — always handle parse failures.
- RAG pipeline: keep chunking → embedding → retrieval → generation stages separately testable.
- Apply prompt caching by default when using the Claude API.

### General
- Never put secrets, API keys, or personal data in code.
- Confirm before taking actions that affect shared systems (DB, external APIs, CI/CD).
- Never claim something "works" without tests.

---

## Response Style

- Korean is fine.
- Short and clear. For longer explanations: key point first, details after.
- Reference file paths and line numbers (`path/to/file.ts:42`).
- Always add language tags to code blocks.
- End-of-task summary: 1–2 sentences max.

---

**This is working well when:** diffs have no unnecessary changes, no rewrites due to over-abstraction, and clarifying questions come before implementation rather than after mistakes.
