# Repomix (2026-06) — Codebase → AI-Friendly Single File Packer

yamadashy/repomix | 25.9k ⭐ | TypeScript | v1.14.1 | MIT | 2024.07

## One-liner

Packs an entire repository into a single XML file for LLM consumption, with
Tree-sitter semantic compression, token counting, and security filtering.

## Architecture

```
searchFiles → sortPaths → collectFiles ─┐
                    │                     │
          ┌─────────┤   processFiles      │  (parallel)
          │         │   ├─ strip comments │
          │         │   └─ compress (tree-sitter)
          │         │                     │
          │         ▼                     ▼
          │   sortOutputFiles ←── securityCheck (secretlint)
          │         │
          │         ▼
          │   produceOutput (XML/MD/Plain via Handlebars)
          │         │
          │         ▼
          │   calculateMetrics (token count)
          │         │
          │         ▼
          │   writeOutputToDisk
          │
    [Skill path] packSkill → skillSectionGenerators → writeSkillOutput
```

## Core Innovations

### 1. Tree-sitter Semantic Compression
Uses `web-tree-sitter` (WASM, no native deps) with per-language AST queries to
extract semantically meaningful nodes (function signatures, type definitions,
class declarations) while discarding implementation bodies. 16 languages
supported, each with a dedicated Tree-sitter query file and parse strategy.

Key files: `src/core/treeSitter/parseFile.ts`, `languageParser.ts`, `languageConfig.ts`,
`parseStrategies/`, `queries/queryPython.ts` etc.

### 2. WASM Runtime (No Native Dependencies)
`web-tree-sitter` (WASM) instead of `node-tree-sitter` (native bindings).
All 16 language parsers bundled in `@repomix/tree-sitter-wasms`.
This is why `npx repomix@latest` works instantly everywhere.

### 3. Agent Skill Auto-Generation
`--skill-generate` produces a SKILL.md with project summary, tech stack
detection, directory structure, and usage guide — consumable by Claude Code,
Cursor, OpenClaw, etc. `src/core/skill/packSkill.ts` → `skillSectionGenerators.ts`.

### 4. Multi-Format Output + MCP Deep Integration
- 3 output formats: XML (default), Markdown, Plain Text
- 8 MCP Tools: packCodebase, packRemote, readOutput, grepOutput, attachOutput,
  fileSystemReadFile, fileSystemReadDirectory, generateSkill
- Remote repo support: `repomix --remote yamadashy/repomix`

## Repomix vs Sirchmunk

| Axis | Sirchmunk | Repomix |
|------|-----------|---------|
| Approach | Search: ask a question, find relevant snippets | Pack: give LLM everything, let it figure out |
| LLM calls | 2-6 (keyword + sampling + synthesis) | 0 (just pack; user feeds to LLM) |
| Latency | 5-36s | <1s (no compress) / 5-30s (compress) |
| Maturity | v0.0.7, new | v1.14.1, 25.9k ⭐, Warp/CodeRabbit sponsored |
| Best for | Targeted queries, limited context window | Global understanding, "review this project" |

**Complementary, not competing.** Use both.

## Hermes Takeaways

| Design | What Hermes Can Absorb | Priority |
|--------|----------------------|----------|
| Tree-sitter compression | Semantic trimming of code in context injection | 🔴 High |
| Agent Skill auto-gen | Auto-produce SKILL.md from repo analysis | 🔴 High |
| MCP tool suite | 8-tool pattern: pack + read + grep + attach | 🟡 Medium |
| XML output format | Structured XML tags best for LLM parsing | 🟡 Medium |
| WASM strategy | If Hermes adds tree-sitter, use WASM | 🟢 Low |

## Quick Start

```bash
npx repomix@latest ~/project --compress
# → repomix-output.xml
# Feed to LLM: "This file contains my entire codebase. Review the architecture."
```
