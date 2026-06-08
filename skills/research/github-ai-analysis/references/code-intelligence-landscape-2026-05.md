# Code Intelligence Tools Comparison (2026-05)

Two landmark projects, same space, opposite philosophies.

## GitNexus (40K⭐, Aug 2025)

**"Agent's nervous system for code"** — pre-computes every dependency into a queryable graph, exposes via MCP tools. AI agents use it to avoid blind edits.

- **Approach**: Pure static analysis (tree-sitter), deterministic 12-phase DAG
- **Storage**: LadybugDB (custom graph DB, migrated from KuzuDB)
- **Output**: MCP tools (13 tools: query, impact, context, detect_changes, rename...)
- **Killer feature**: PreToolUse hooks — blocks edits if impact analysis returns HIGH risk
- **Scale**: 327K lines TypeScript, 16 languages, 31 node types × 21 edge types
- **License**: PolyForm Noncommercial (commercial use requires payment)
- **For Hermes**: "executable context" paradigm — skills as constraints, not suggestions

## Understand-Anything (36K⭐, Mar 2026)

**"Human's textbook for code"** — LLM-driven multi-agent pipeline produces interactive knowledge graphs for learning.

- **Approach**: LLM agents (9 specialized agents), deterministic + LLM hybrid
- **Storage**: Single knowledge-graph.json
- **Output**: Interactive dashboard (React Flow) with guided tours, domain views, personas
- **Killer feature**: Guided tours (topological learning order) + LLM output Zod normalization
- **Scale**: 403 files, 21 node types × 35 edge types
- **License**: MIT
- **For Hermes**: Multi-Agent pipeline (write to disk, not context) + schema validation for LLM outputs

## The Axis

| | GitNexus | Understand-Anything |
|---|---|---|
| For whom | AI agents writing code | Humans learning code |
| Method | Compiler-grade static analysis | LLM-driven semantic analysis |
| Precision | High (deterministic) | Lower (LLM-dependent, with Zod guardrails) |
| Depth of understanding | Structural only | Semantic ("this function claims to do X but actually does Y") |
| When to use | "Don't let my AI break prod" | "Help me grok this 200K-line codebase" |

## ljg-roundtable (197⭐, ljg-skill ecosystem 5.3K⭐)

Not a code analysis tool at all — a prompt-engineering artifact for structured dialectical discussion.

- 4 files total (SKILL.md + original Lisp DSL design prompt)
- Multi-agent: moderator + 3-5 historical figures debate any topic
- Killer design: "简言之" forced compression, ASCII topology diagrams, "挖深不铺广"
- For Hermes: Prompt DSL first (model the system before writing instructions)
