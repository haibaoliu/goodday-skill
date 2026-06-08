# Hands-on Evaluation Methodology for AI/Infra Tools

When the user asks "how do I know if it works?" after an analysis, design a
structured benchmark. Don't just install and poke — produce a table the user
can read and draw their own conclusions from.

## Core Pattern: Multi-Baseline Comparison

| Baseline | Purpose | When to include |
|----------|---------|-----------------|
| **Lower bound** | Simplest possible approach (e.g., grep for search tools, raw API call for agents) | Always |
| **LLM-direct** | What the model knows without any retrieval/tooling | When the test data is private/unseen |
| **System under test (mode A)** | Fast/cheap/default mode of the tool | Always |
| **System under test (mode B)** | Deep/expensive/thorough mode (if the tool offers one) | If the tool has tiered modes |

The gap between lower bound and LLM-direct reveals whether retrieval helps.
The gap between LLM-direct and the tool reveals the tool's marginal value.

## Query Design: Graded Difficulty

Design 8-12 queries across 4 difficulty tiers, all with known ground truth:

| Tier | Type | Signal |
|------|------|--------|
| 🟢 Simple | Single-file location, exact string match | Does the tool beat grep? |
| 🟡 Medium | Config values, specific parameters | Can it read and extract structured values? |
| 🟠 Hard | Cross-file synthesis, architectural understanding | Can it connect dots across files? |
| 🔴 Very Hard | Semantic reasoning, implicit relationships | Can it understand, not just retrieve? |

**Ground truth rules:**
- Every query MUST have a verifiable answer in the test corpus
- Note the exact files that contain the answer (for grep comparison)
- List key information points (for accuracy/completeness scoring)

## Scoring Rubric (per query, per run)

| Dimension | Weight | 0 | 1-3 | 4-6 | 7-9 | 10 |
|-----------|--------|---|---|-----|-----|----|
| Accuracy | 40% | Wrong | Mostly wrong | Partially correct | Minor gaps | Perfect |
| Completeness | 25% | Nothing | Fragments | Half covered | Most covered | All points |
| Efficiency | 20% | >30s | 15-30s | 5-15s | 2-5s | <2s |
| Relevance | 15% | Off-topic | Mostly irrelevant | Partially relevant | Focused | Laser-focused |

## Test Corpus Selection

The best test corpus is:
1. **Private to the LLM** — so LLM-direct scores near-zero, isolating the tool's value
2. **Diverse in format** — source code, config files, markdown docs, structured data
3. **Known to you** — you have ground truth for every question
4. **Real-world** — not synthetic; reflects actual use patterns

Your own project's codebase is usually ideal.

## Output to the User

After running, produce:
1. A **per-query comparison table** with emoji scores (🟢≥7 🟡≥4 🔴>0 ⚫0) and latency for all baselines
2. A **summary table**: avg accuracy, avg latency, % of queries where tool beat baselines
3. A **verdict**: which query types the tool excels at, which it doesn't, and whether it's worth adopting

**Style**: compact markdown tables with emoji scores, not walls of text. The user wants to glance and see the answer ("能很直观的看到对比就行"). Latency in seconds beside the score. Put the table FIRST, then commentary.

## Pitfalls

- Don't benchmark tools on synthetic toy data — the user wants to know if it works on THEIR data
- Don't skip the lower bound baseline — "is it better than grep/curl" is the first question
- Don't run DEEP/full mode on every query if it's slow — sample 3-5 representative queries for the expensive mode
- Don't score subjectively — define ground truth key points BEFORE running
- Installation failures are NOT part of the evaluation — they're environment issues; fix them, note the fix, then evaluate
- **Do NOT present token/cost "savings" as the primary metric.** Frame efficiency as "how much useful information fits in the same budget." The user cares about quality first, resource usage second.

## Worked Example: Sirchmunk Evaluation (2026-06)

See `~/Documents/hermes-output/sirchmunk-eval/` for a complete harness:
- `queries.json` — 10 graded queries against Hermes source code
- `eval_harness.py` — runs grep → FAST → DEEP, saves results incrementally
- `baseline_llm_direct.py` — LLM with zero retrieval
- `EVAL_CRITERIA.md` — full scoring rubric with ground truth key points

Installation workaround for Intel Mac: `references/sirchmunk-install-workaround.md`.
