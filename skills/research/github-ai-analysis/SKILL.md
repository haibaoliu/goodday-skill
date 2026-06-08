---
name: github-ai-analysis
description: Deep-dive analysis of AI/ML open-source projects on GitHub. When the user sends a GitHub repo link for research, load this skill for the structured analysis methodology. Covers architecture dissection, innovation assessment, relevance to Hermes, performance benchmarks, actionable takeaways, and hands-on evaluation design.
version: 1.2.0
tags: [research, github, ai-projects, deep-dive, technology-radar]
---

# GitHub AI Project Analysis

When the user sends a GitHub repo link asking "研究一下这个" or similar, perform a structured deep-dive. This is NOT a casual browse — the user expects architectural understanding and actionable insights.

## Methodology

### Phase 1: Surface Scan (2-3 minutes)
1. **Repo metadata**: stars, forks, language, created date, license, topics
2. **README**: What problem does it solve? What's the unique value proposition?
3. **Comparison tables**: If the README has them, they reveal the author's positioning
4. **RFD/Design docs**: If there's a `docs/rfds/` directory, read the design rationale

### Phase 2: Source Deep-Dive (5-10 minutes)
1. **Clone the repo** (`git clone --depth 1`)
2. **Measure codebase**: `find . -name "*.rs" | wc -l` (or appropriate extension). Lines of code reveals ambition vs stars.
3. **Key source files**: Focus on the novel parts — the storage engine, query builder, format encoder. Skip boilerplate (error types, config parsing).
4. **Architecture diagram**: Map the crate/module hierarchy. What talks to what?

### Phase 3: Relevance Assessment
For EVERY project, answer:
- What can Hermes absorb WITHOUT adopting the project? (design patterns, formats, algorithms)
- What would Hermes gain by adopting? (concrete features)
- What are the adoption risks? (maturity, license, language mismatch, single-point-of-failure)

### Phase 4: Hands-on Evaluation (if user wants to try it)
When the user asks "how do I know if it works?" or wants to benchmark the tool,
design a structured evaluation. Core pattern:
1. **Multi-baseline comparison**: lower bound (grep/curl) → LLM-direct → tool-fast → tool-deep
2. **Graded query difficulty**: 8-12 queries from simple (single-file lookup) to very hard (cross-file semantic reasoning)
3. **Known ground truth**: every query has a verifiable answer in a test corpus the LLM hasn't seen (your own codebase is ideal)
4. **Scoring rubric**: accuracy (40%) + completeness (25%) + efficiency (20%) + relevance (15%)

Full methodology in `references/evaluation-methodology.md`. Key constraint: don't present token/cost savings as the primary metric — frame efficiency as "how much useful information fits in the same budget."

## Output Format

Always in Chinese, structured as:

```
## 项目名 — 一句话定位

> 语言 · stars · 年龄 · 原名（如有）

### 一句话

[用一句中文说清它是什么]

### 架构分层（如果是数据库/基础设施类项目）

[模块层级图]

### 核心创新（3-5个）

每个创新：设计是什么 → 为什么重要 → 代码证据（文件名+行数）

### 性能数据（如有benchmark）

| 指标 | 该项目 | 竞品A | 竞品B |

### 对 Hermes 的启示

| 该项目设计 | Hermes 可吸收什么 | 优先级 |
|-----------|------------------|--------|

### 风险

- 许可证
- 成熟度
- 已知限制

### 结论

[最终判断：值不值得跟进，怎么跟进]
```

## Key Principles

1. **Depth over breadth**: Better to deeply understand 3 innovations than list 10 features
2. **Code over marketing**: README claims are hypothesis; source code is ground truth. Always verify.
3. **"提升不是省钱"**: When presenting context/token optimizations, frame them as "fitting MORE useful information in the same budget" — never as "saving money". The user cares about quality, not cost.
4. **Actionable takeaways**: Every analysis must end with concrete things the user can DO (adopt pattern X, avoid pitfall Y, try module Z).
5. **Be honest about maturity**: A 29-star project with 300K lines of Rust is noteworthy. A 10K-star project with 500 lines is probably a wrapper. Stars ≠ quality.
6. **Comparison is insight**: When researching 2+ repos in one session, the contrast between them is often more valuable than either analysis alone. See `references/code-intelligence-landscape-2026-05.md` for example.

## Reference Bank

- `references/code-intelligence-landscape-2026-05.md` — GitNexus vs Understand-Anything vs ljg-roundtable comparative analysis (2026-05 session).
- `references/sochdb-2026-05.md` — SochDB deep-dive (2026-05 session).
- `references/clawbench-hermes-benchmark.md` — ClawBench browser-agent benchmark with native Hermes harness support. When analyzing browser-agent or benchmark repos, check this first — Hermes can be evaluated on 153 real-web tasks.
- `references/evaluation-methodology.md` — Reusable benchmark design pattern for AI/infra tools: multi-baseline comparison, graded query difficulty, scoring rubric, test corpus selection. Load when the user asks "how do I test this?" or wants to evaluate a tool after analysis.
- `references/sirchmunk-install-workaround.md` — Worked example of installing ML-heavy Python packages on Intel Mac without GPU. `--no-deps` + stub module pattern. Load when a project's `pip install` fails on heavy deps (sentence-transformers, ONNX Runtime, torch).
- `references/repomix-doc-generation.md` — Repomix: pack codebase → LLM generates architecture docs, code maps, flowcharts, design docs. Covers CLI usage, output structure, document types, and the profile-home workaround for Hermes agents.
- `references/repomix-2026-06.md` — Repomix deep-dive: 25.9k⭐ codebase packer with Tree-sitter semantic compression, MCP integration, and agent skill auto-generation. Contrast with Sirchmunk: complementary approaches (pack-everything vs search-snippets).

## Pitfalls

- Don't just summarize the README — the user can read that themselves
- Don't recommend adoption of immature projects without clear caveats
- Don't skip the source code dive — that's where the real insights are
- Star count can be misleading: check commit history, code volume, and issue quality
- **Clone timeout on large repos**: repos >30MB often time out `git clone --depth 1`. Fall back to GitHub API tree endpoint (`GET /repos/{owner}/{repo}/git/trees/main?recursive=1`) for file listing, directory structure, extension breakdown. Then fetch key source files individually via `raw.githubusercontent.com`. Save full clone for repos where deep source reading is essential.
- **Prompt-only projects** (skills, prompts, frameworks with <10 source files): skip code-counting. The "source" is the prompt/SKILL.md itself. Phase 2 becomes: read the main prompt file(s) in full, map the design decisions, check for a DSL or meta-format. The Lisp DSL in ljg-roundtable's `original-prompt.org` is the kind of signal you're looking for.
- **ML-heavy Python projects on Intel Mac (no GPU)**: `pip install` often hangs or fails on heavy deps like `sentence-transformers` (→ torch → 200MB+ download + slow resolution), `kreuzberg` (→ ONNX Runtime, no prebuilt binary for x86_64-apple-darwin), and `modelscope`. Workaround: `pip install --no-deps <pkg>` to get the core, then install only the lightweight deps individually (loguru, fastapi, openai, duckdb, rapidfuzz, etc.). For deps used only by optional features (e.g., `kreuzberg` for PDF extraction, `sentence-transformers` for embedding reuse), create a stub module with the minimal API surface the package imports. Then pass feature flags (`reuse_knowledge=False`) to skip the heavy paths at runtime. System binaries like `rga` (ripgrep-all) should be downloaded as prebuilt releases rather than built from source. See `references/sirchmunk-install-workaround.md` for a worked example.
- **Hermes profile-home override**: CLI tools run from Hermes agent sessions may have `$HOME` resolved to the Hermes profile path (e.g., `~/.hermes/profiles/chuck/home/`) instead of the real user home. This causes `Path.home()`, `~`, and `$HOME`-based paths to point to the wrong location. Always use absolute paths (`/Users/<name>/...`) in scripts meant to run from within Hermes sessions, or prefix commands with `HOME=/Users/<name>`. This also affects `npx` and other Node.js tools (`npm error config prefix cannot be changed from project config`).

## Comparative Analysis (Multi-Repo Sessions)

When the user sends 2+ repos in the same session, add a comparison table after each individual analysis.

| 维度 | Project A | Project B |
|------|-----------|-----------|
| 定位 | ... | ... |
| 方法 | ... | ... |
| 规模/增速 | ... | ... |
| License | ... | ... |
| 对 Hermes 启示 | ... | ... |

Key: find the axis they differ on (not just "this vs that"). Examples: "Agent 操作手册 vs 人的教科书", "静态分析 vs LLM 驱动", "代码工具 vs 认知脚手架". The contrast itself is the insight. The comparison table goes in the last project's analysis, not as a standalone section.

### Parallel Multi-Repo Discovery

When the user sends 2+ repos to research at once AND the repos are NOT known names (need GitHub search to find), use `delegate_task` to parallelize discovery:

1. Dispatch one subagent per repo to search GitHub + web for the best match
2. Each subagent returns: URL, stars, description, code-quality assessment
3. Once all return, pick the best match for each and deep-dive sequentially

This avoids serial GitHub API rate limiting and cuts discovery time by ~60%. Don't use for single-repo research — overhead isn't worth it. Don't use when the repo URL is already explicit — skip straight to Phase 1.
