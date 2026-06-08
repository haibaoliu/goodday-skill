---
name: task-evolution
description: Multi-trajectory task evolution — accumulate structured execution metadata across sessions, synthesize cross-task insights, and proactively inject past strategies when similar tasks arise. Inspired by SE-Agent's trajectory pool + genetic operators.
version: 1.0.0
tags: [self-evolution, reflection, memory, crossover, task-pool]
category: self-evolution
---

# Task Evolution — Multi-Trajectory Learning

> Inspired by SE-Agent (arxiv.org/abs/2508.02085): trajectory pool + crossover + revision operators applied to agent task execution.

## What This Skill Does

Unlike `self-evolution-reflexion` (single-task reflection → memory), this skill:

1. **Extracts structured execution metadata** after each complex task (9-field summary)
2. **Accumulates to a task pool** (`~/.hermes/profiles/chuck/task-pool.json`) — cumulative, not overwrite
3. **Synthesizes cross-task insights** when 2+ attempts on the same task type exist
4. **Proactively injects past strategies** before starting a new task of a known type

## The Task Pool

File: `<HERMES_PROFILE_ROOT>/task-pool.json` (typically `~/.hermes/profiles/chuck/task-pool.json`; resolve at runtime via `$HERMES_HOME` or fallback to `~/.hermes/profiles/<profile>/task-pool.json`)

```json
{
  "pool": {
    "<task_fingerprint>": {
      "problem": "one-line task description",
      "domain": "github-research | code-review | debugging | deployment | data-analysis | creative | system-config | ...",
      "iterations": [
        {
          "timestamp": "2026-05-29T14:30:00Z",
          "session_id": "...",
          "success": true,
          "approach_summary": "What was the main approach",
          "strategy": "Abstract problem-solving strategy used",
          "key_techniques": ["technique1", "technique2"],
          "tools_used": ["terminal", "web_search", "delegate_task"],
          "tools_heavy": ["terminal"],
          "reasoning_pattern": "breadth-first | depth-first | divide-conquer | trial-error | systematic",
          "assumptions_made": ["assumption1"],
          "pitfalls_hit": ["pitfall1"],
          "what_worked": "Key insight that led to success",
          "failure_reason": null
        }
      ],
      "cross_task_insights": null
    }
  },
  "meta": {
    "version": "1.0",
    "total_tasks": 0,
    "last_synthesis": null
  }
}
```

**Task fingerprint**: Use a hash of the user's first message + domain tag. This groups similar tasks (e.g., "github repo research" tasks get the same domain but different fingerprints since repos differ).

## When to Use

### Extract (after task completion)

Trigger after a complex task (5+ tool calls, or user says "研究一下/分析一下/帮我做X"). Load this skill and:

1. **Extract metadata**: Use the `_extract_metadata` procedure below to generate structured summary
2. **Save to pool**: Append to task-pool.json via the `_update_pool` procedure
3. **Check for crossover opportunity**: If this task domain has 2+ iterations, run `_synthesize_cross_task_insights`
4. **Report to user**: What was saved to the pool (brief, 1-2 lines)

### Inject (before starting a task)

When the user gives a task that matches a known domain, check the pool FIRST:

1. Load task-pool.json
2. If same-domain tasks exist with cross_task_insights, inject into your reasoning
3. If same-domain tasks exist without cross_task_insights, summarize past attempts briefly
4. Offer the user: "这个任务类型之前做过 N 次，要不要参考历史经验？"

## Procedures

### `_extract_metadata(task_description, success, session_id) → dict`

Generate a structured summary by reflecting on the just-completed task:

```python
# Mental checklist for extraction:
approach_summary = "What was the overall approach? (1 sentence)"
strategy = "Abstract strategy pattern: e.g., breadth-first exploration, systematic debugging, divide-and-conquer"
key_techniques = ["Specific techniques used, e.g., 'grep-then-read', 'API-first-then-source'"]
tools_used = ["terminal", "web_search", "delegate_task", ...]  # from actual tool calls
tools_heavy = ["Which tools were used heavily"]
reasoning_pattern = "breadth-first | depth-first | divide-conquer | trial-error | systematic"
assumptions_made = ["Assumptions that held true"]
pitfalls_hit = ["Things that went wrong or nearly went wrong"]
what_worked = "The key insight or decision that made this succeed"
failure_reason = "If failed, why? Otherwise null"
```

**Writing rules** (same as self-evolution-reflexion):
- Declarative facts, not instructions
- Tag confidence: `[single-incident]` if from one occurrence, `[verified]` if confirmed across sessions
- No PII, tokens, or secrets

### `_update_pool(metadata, task_fingerprint, domain, problem)`

1. Read `~/.hermes/profiles/chuck/task-pool.json` (create if missing)
2. If task_fingerprint exists → append to iterations array
3. If task_fingerprint is new → create new entry with problem + first iteration
4. If domain has 2+ iterations now → set `needs_synthesis = true`
5. Update meta counters
6. Write back

### `_synthesize_cross_task_insights(domain)`

When 2+ iterations exist for a domain:

1. Load all iterations for this domain
2. Extract patterns:
   - **Common pitfalls**: Pitfalls that appear in 2+ iterations → systemic blind spots
   - **Convergent strategies**: Strategies that led to success → best practices
   - **Divergent assumptions**: Assumptions that were wrong → domain-specific gotchas
   - **Tool patterns**: Most-used tools and tool combinations
3. Format as `cross_task_insights`:
```
SYSTEMIC BLIND SPOTS: [pitfalls shared across attempts]
BEST PRACTICES: [strategies that consistently work]
DOMAIN GOTCHAS: [assumptions that fail in this domain]
TOOL PATTERNS: [effective tool combinations]
```
4. Write to pool[task_fingerprint]["cross_task_insights"]

### `_inject_past_wisdom(domain, current_task)`

Before starting a new task:

1. Check task-pool.json for same-domain entries
2. If cross_task_insights exists:
   - Mentally incorporate: avoid systemic blind spots, apply best practices
   - Optionally mention to user: "根据历史经验，这类任务需要注意 X"
3. If only raw iterations (no synthesis yet):
   - Quick scan for common pitfalls → avoid proactively
4. If no prior tasks: skip, nothing to inject

### `_generate_task_fingerprint(user_message) → str`

```python
import hashlib
# Use first 100 chars of user message + domain guess
domain = guess_domain(user_message)  # "github-research", "debugging", etc.
key = f"{domain}:{user_message[:100]}"
return hashlib.md5(key.encode()).hexdigest()[:12]
```

## Integration with self-evolution-reflexion

These two skills are complementary:

| | self-evolution-reflexion | task-evolution |
|---|---|---|
| **Scope** | Single task | Multiple tasks (same domain) |
| **Output** | memory entries + skills | task-pool.json entries + cross_task_insights |
| **Granularity** | Fine-grained (API quirks, tool bugs) | Coarse-grained (strategy, approach, pitfalls) |
| **When** | After every complex task | After domain has 2+ iterations |
| **Benefit** | Never repeat the same mistake | Never fall into the same strategic trap |

**Rule**: If an insight is about a specific tool/API/env → save to **memory** (self-evolution-reflexion). If it's about a problem-solving strategy or domain pattern → save to **task pool** (this skill).

## The task-pool.json Bootstrap

Create the initial pool if it doesn't exist:

```json
{
  "pool": {},
  "meta": {
    "version": "1.0",
    "total_tasks": 0,
    "total_iterations": 0,
    "last_synthesis": null
  }
}
```

## Pitfalls

- **Don't over-extract**: Not every task needs pool entry. Threshold: 5+ tool calls or explicit user request for research/analysis.
- **Fingerprint collision**: MD5 on first 100 chars is crude. Two different repos might collide if names are similar. OK for v1 — refine if it becomes a problem.
- **Pool bloat**: task-pool.json could grow large. Cap at 50 task entries; if exceeded, archive old entries to `task-pool-archive.json`.
- **Stale insights**: Cross-task insights from 3+ months ago may be outdated (tool changes, API changes). Tag with timestamp and re-validate periodically.
- **Not a replacement for skills**: A repeatable workflow belongs in a skill (skill_manage). The pool is for strategic patterns, not step-by-step procedures.
- **Path resolution in Hermes profiles**: `~/` resolves to the profile-internal HOME (e.g., `/Users/macbook/.hermes/profiles/chuck/home/`), not the system HOME. When reading/writing task-pool.json programmatically, use absolute paths (e.g., `/Users/macbook/.hermes/profiles/<profile>/task-pool.json`) or resolve via `$HERMES_HOME`. Python's `Path.home()` and `os.path.expanduser('~')` will give the wrong location.

## Safety (from self-evolution-reflexion)

- PII check before saving any task description
- No API keys, tokens, or secrets in pool entries
- [single-incident] tag for one-off observations
- Cross-task insights marked with synthesis date for staleness detection

## Domain Taxonomy

Use these domains for task fingerprinting:

- `github-research`: Analyzing GitHub repos, codebase inspection
- `code-review`: PR review, code quality assessment
- `debugging`: Error investigation, root cause analysis
- `deployment`: CI/CD, server setup, infrastructure
- `data-analysis`: Data processing, visualization, statistics
- `creative`: Content generation, design, writing
- `system-config`: Config files, environment setup, tool installation
- `research`: Academic paper analysis, literature review
- `security`: Security audit, vulnerability assessment
- `general`: Catch-all for tasks that don't fit

## Example: Task Evolution in Action

```
User: "研究一下 https://github.com/QuantaAlpha/SE-Agent"
→ Domain: github-research
→ Extract metadata after task
→ Pool now has 1 iteration for SE-Agent fingerprint

User: "研究一下 https://github.com/xxx/SWE-Bench-RL"
→ Domain: github-research (same domain!)
→ Check pool: found 1 prior github-research task
→ Inject: "上次研究 SE-Agent 的做法是先 clone → 读 README → 深挖核心源文件 → 结构化输出。这次沿用？"
→ User confirms → strategy reused
→ After completion: pool now has 2 iterations for github-research
→ Trigger synthesis: cross_task_insights generated
  "BEST PRACTICES: clone --depth 1 to save time, prioritize operators/ over tests/"
  "SYSTEMIC BLIND SPOTS: don't trust README claims about performance without benchmark code"
  "TOOL PATTERNS: search_files for file discovery + terminal for git clone + vision_analyze for architecture diagrams"
```
