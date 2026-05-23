---
name: agent-memory-systems
description: Knowledge base for evaluating, comparing, and choosing AI agent memory solutions. Trigger when user asks about agent memory systems, compares memory plugins, or wants to add persistent memory to Hermes/OpenClaw.
version: 1.0.0
---

## Purpose

Provide a structured framework for evaluating agent memory solutions — understanding the landscape, comparing candidates, and making informed choices for Hermes integration.

## When to Use

- User asks "what memory system should I use for my agent?"
- User wants to compare two or more memory solutions
- User is evaluating a new agent memory open-source project
- User asks about enabling persistent memory in Hermes/OpenClaw

## Evaluation Framework

When comparing agent memory systems, assess across these dimensions:

### Core Philosophy
- **Passive distillation** vs **self-evolution**: Does the system just extract and summarize, or does it learn from success/failure?
- **Flat storage** vs **layered hierarchy**: Are memories organized in a semantic pyramid or dumped into a flat vector store?

### Technical Capabilities
- Long-term memory layering (conversation → facts → scenes → persona)
- Short-term context compression (token savings)
- Skill crystallization (auto-generating reusable procedures from traces)
- Feedback/learning loop (human corrections → improved behavior)
- Multi-modal support (images, tool traces, code)
- Retrieval strategy (keyword, vector, hybrid, multi-tier)

### Engineering
- Deployment model (local-only, sidecar, cloud)
- Storage backends (SQLite, vector DBs, graph DBs)
- Hermes integration quality (native plugin vs Docker/sidecar)
- Multi-profile support
- LLM provider compatibility (especially DashScope for Chinese users)
- Maturity (stars, age, paper, community, test coverage)
- Operations tooling (CLI, config management, backup)

### Benchmarks
- Long-term accuracy (PersonaMem, LoCoMo, LongMemEval)
- Short-term token savings (WideSearch, SWE-bench)
- Preference learning (PrefEval-10)

## Hermes Deployment

When the user selects a memory system and wants to deploy it to Hermes, follow this flow:

### MemOS local-plugin deployment
1. Run `install.sh --version <ver>` from the repo's `apps/memos-local-plugin/` — auto-detects Hermes and installs to active profile
2. For multi-profile: do NOT re-run the installer. See `references/memos-hermes-deployment.md` for symlink-sharing technique (saves ~830MB per extra profile)
3. Set `algorithm.lightweightMemory.enabled: false` in MemOS config for full self-evolution
4. Configure LLM + embedding: use `openai_compatible` with DashScope for Chinese users (`qwen-plus` for extraction, `text-embedding-v3` for vectors)
5. Set `memory.provider: memtensor` in each Hermes profile's config.yaml
6. Restart gateways: `hermes gateway restart --profile <name>`
7. Bridge process starts lazily on first chat session — viewer unavailable until then

### Pitfalls
- `provider: ''` string appears MULTIPLE times in Hermes config.yaml — provide enough trailing context (e.g. `memory_char_limit: ...\nuser_char_limit: ...`) for unique patching
- install.sh changes HOME to `<hermes_home>/home/` — runtime data lands at `<hermes_home>/home/.hermes/memos-plugin/`, not `<hermes_home>/.hermes/memos-plugin/`
- TencentDB Agent Memory Gateway sidecar uses port 8420 — multi-profile requires Option C (shared Gateway with separate userId namespaces), unlike MemOS which has per-profile independent bridge processes

## Scientific Agent Skills (K-Dense AI)

The [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) repo provides 135 research-grade skills using the open [Agent Skills](https://agentskills.io/) standard. It is NOT a memory system — it's a skill library covering bioinformatics, cheminformatics, ML, scientific writing, and 78+ public databases.

### Installing to Hermes
1. Clone the repo, copy desired skill dirs to `~/.hermes/skills/<name>/`
2. Add Hermes-required frontmatter fields: `version: 1.0.0` and `category: <match>` 
3. The Agent Skills frontmatter (`name`, `description`, `license`, `metadata`) is compatible — only `version` and `category` are missing
4. For skills with `scripts/` or `references/`, copy those directories too
5. Install required pip packages (many skills need scikit-learn, matplotlib, rdkit, etc.)

### Most valuable general-purpose skills
- `scientific-writing`, `peer-review`, `scientific-brainstorming`, `scientific-critical-thinking` — methodology
- `database-lookup` — unified access to 78 public scientific databases via REST API
- `exa-search` — scholarly web search
- `xlsx`, `docx`, `pptx`, `pdf` — document processing
- `matplotlib`, `seaborn`, `markdown-mermaid-writing`, `scientific-visualization` — visualization

## Reference Material

- `references/tencentdb-vs-memos.md` — Detailed comparison of TencentDB Agent Memory vs MemOS (2026-05-16)
- `references/memos-hermes-deployment.md` — MemOS multi-profile Hermes deployment recipe with symlink-sharing technique
