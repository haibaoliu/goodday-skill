# Dead-End Registry — Format & Conventions

> Shared between kanban workers (write) and orchestrators (read).  
> Location: `<project>/.hermes/dead-ends.md` or `<shared_workspace>/.hermes/dead-ends.md`

## Purpose

Records failed approaches so subsequent agents don't repeat them. Workers MUST write an entry before cancelling a task. Orchestrators MUST read before decomposing new work.

## Entry format

```markdown
## dead-end: <terse approach name>
- **Task**: <kanban_task_id>
- **Date**: YYYY-MM-DD
- **Reason**: <concrete reason — why this approach failed, not "didn't work">
- **Evidence**: <what was tried, what result was observed>
- **Alternative**: <if known, what to try instead; "unknown" if not>
- **Severity**: block | warn
```

### Severity rules

- **block** — This exact approach is proven dead. No task should retry it.
- **warn** — Approach has known pitfalls. Can be retried with modifications if explicitly justified.

## Anti-patterns (do NOT write)

```markdown
# BAD — too vague, not actionable
## dead-end: tried DSPy
- Reason: didn't work
```

```markdown
# BAD — records task outcome, not dead approach
## dead-end: task timed out
- Reason: ran out of time
```

## Good examples

```markdown
## dead-end: DSPy BootstrapFewShot for prompt optimization
- **Task**: t_a1b2c3d4
- **Date**: 2026-05-31
- **Reason**: BootstrapFewShot requires 50+ labeled examples; project has only 12
- **Evidence**: Ran 3 iterations, all produced degenerate prompts (empty or 1-token)
- **Alternative**: Use static few-shot examples hardcoded in prompt template
- **Severity**: block
```

```markdown
## dead-end: fine-tuning BGE-small for retrieval
- **Task**: t_e5f6g7h8
- **Date**: 2026-05-30
- **Reason**: Training data too small (200 pairs) for meaningful embedding shift
- **Evidence**: Fine-tuned model scored 0.02 higher on MRR than base — within noise
- **Alternative**: Try BGE-large zero-shot or switch to ColBERT late interaction
- **Severity**: block
```

```markdown
## dead-end: async httpx for API calls
- **Task**: t_i9j0k1l2
- **Date**: 2026-05-29
- **Reason**: Library's event loop conflicts with Hermes's own asyncio loop
- **Evidence**: `RuntimeError: This event loop is already running` on all calls
- **Alternative**: Use `requests` with `concurrent.futures.ThreadPoolExecutor`
- **Severity**: block
```

## When to write

| Task outcome | Write dead-end? |
|---|---|
| Completed with effective change | No |
| Cancelled — approach was tried and failed | **Yes** |
| Cancelled — external failure (OOM, timeout, credential) | No (this is infra, not approach) |
| Blocked for human input | No (not dead yet) |
| Completed but yielded zero improvement | **Yes** (stagnation signal) |

## Reading the registry

Orchestrator reads the registry at `Step 2 — Sketch the task graph`. For each candidate task:

1. Scan entries with `severity: block` — if the proposed approach matches a blocked dead-end, **discard or replace** the task direction.
2. Scan entries with `severity: warn` — if matching, include in task body: "⚠️ Dead-end warning: <approach> previously failed because <reason>. Only proceed if your approach differs in <specific way>."

## Concurrency

Multiple workers may write concurrently. Use append-only writes (no read-modify-write). The orchestrator handles duplicates gracefully (same approach + same reason = deduplicate in display, keep both in file).
