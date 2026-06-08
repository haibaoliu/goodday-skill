# Repomix: Codebase → Structured Documentation Pipeline

Repomix is a TypeScript CLI that packs entire repositories into AI-friendly
XML files. It doesn't generate docs — the LLM does. But it provides the
raw material in a structured format that makes document generation reliable.

## Quick Start

```bash
# Pack with tree-sitter compression (keeps function signatures, drops bodies)
npx repomix@latest /path/to/project --compress

# Skip release notes
npx repomix@latest /path/to/project --compress --ignore "RELEASE*"
```

⚠️ When running from a Hermes agent context, `$HOME` may resolve to the
Hermes profile home (`~/.hermes/profiles/chuck/home/`). Use absolute
paths or prefix with `HOME=/Users/<user>`.

## Output Structure

```
repomix-output.xml      # ~30MB for a 3,500-file TypeScript/Python codebase
├── <file_summary>       # Meta-instructions for the LLM consumer
├── <directory_structure> # Full directory tree
├── <files>              # All source files (compressed if --compress)
│   └── <file path="...">content</file>
└── <instruction>        # User-provided prompt
```

## Document Types This Enables

When fed to a capable LLM with codebase knowledge, this XML enables:

| Document | What it contains | Key sections |
|----------|-----------------|--------------|
| **Architecture doc** | System panorama, module deep-dive, dependency map | Overview diagram, per-module explanation, transport/config layers |
| **Code map** | "Where is X?" quick-reference table | Lookup table, directory tree, dependency chain, config locations |
| **Flowcharts** | Mermaid diagrams of key processes | Conversation lifecycle, tool discovery, skill loading, cron, gateway routing |
| **Design doc** | Why decisions were made, not just what | Per-decision: what, why, tradeoffs |

## Proven Pattern (from Hermes Agent analysis, 2026-06)

1. `npx repomix --compress` → 3,504 files → 31MB XML (8.1M tokens)
2. Read `<directory_structure>` section for precise file tree
3. Cross-reference with existing codebase knowledge
4. Generate 4 document types with consistent structure
5. Output as Markdown files in `~/Documents/hermes-output/repomix-docs/`

## Built-in Features Worth Using

- `--compress` — Tree-sitter semantic compression. Extracts function/class
  signatures, drops bodies. Token saving: 80-90% for code-heavy repos.
  Supports 16 languages (TS, Python, Go, Rust, Java, C#, Ruby, PHP...).

- `--skill-generate` — Auto-generates an agent SKILL.md with tech stack
  detection, project summary, directory structure, and usage guide.

- `--remote yamadashy/repomix` — Pack any GitHub repo without cloning.

- Secret detection — Secretlint integration excludes 11 suspicious files
  from the Hermes codebase (test fixtures with fake keys, etc.).

## Limitations

- 8M tokens is too large for direct context injection. The LLM must
  either read the XML in chunks or rely on existing knowledge + XML
  as a structural reference.
- Tree-sitter compression only works for 16 languages.
- `--compress` drops implementation details (useful for structure,
  not for bug analysis).
