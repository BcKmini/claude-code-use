# /pipeline — Multi-Stage AI Pipeline Runner

Execute and manage multi-stage AI pipelines with context isolation, parallel agents, and review loops.

## Usage

```
/pipeline run <pipeline-spec>
/pipeline status
/pipeline stages
/pipeline retry <stage>
```

---

## What is a Pipeline? (파이프라인이란?)

A pipeline is a sequence of AI stages where each stage:
1. Receives only the context it needs (context isolation)
2. Produces a validated output
3. Passes that output to the next stage

```
Stage 1: Detection / Analysis
    ↓ (validated output)
Stage 2: Parallel specialist analysis
    ↓ (merged findings)
Stage 3: Patch / Fix generation
    ↓ (static + dynamic validation)
Stage 4: Multi-perspective review loop
    ↓ (all findings resolved)
Stage 5: Human approval → apply
```

---

## /pipeline run

```
/pipeline run {{PIPELINE_SPEC_OR_DESCRIPTION}}
```

Invokes `pipeline-orchestrator` to:
1. Parse the pipeline definition
2. Execute each stage with isolated context
3. Run parallel agents where safe
4. Apply quality gates at every stage
5. Produce a full run report

**Example:**
```
/pipeline run analyze the slow queries in logs/, generate patches, run a 3-perspective review loop, output diff files for human approval
```

---

## /pipeline status

Shows the current pipeline run status:
- Which stage is active
- Which stages passed / warned / errored
- Number of review loop iterations
- Estimated remaining cost

---

## /pipeline stages

Lists all stages in the current pipeline definition with their:
- Input requirements
- Output format
- Validator used
- Parallel group (if applicable)

---

## /pipeline retry

```
/pipeline retry {{STAGE_NAME}}
```

Retries a specific failed stage with a fresh context window.
Useful when a stage fails due to a transient error (rate limit, timeout, etc.).

---

## Context Isolation (컨텍스트 격리)

Each agent in a stage is spawned with **only the context it needs**.
This prevents "Context Rot" — the compounding of errors across a long pipeline.

```
❌ Bad:  pass full conversation history to every agent
✅ Good: pass only the relevant output from the previous stage
```

---

*Powered by `pipeline-orchestrator` (agent 10) — see `agents/10-pipeline-orchestrator.md`*
*Inspired by: Musinsa Tech Blog — query-engineer 7-stage pipeline*
