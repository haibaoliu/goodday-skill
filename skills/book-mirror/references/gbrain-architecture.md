# GBrain Architecture Reference

> Source: [garrytan/gbrain](https://github.com/garrytan/gbrain) ⭐18K+, MIT License, TypeScript (Bun)

## Core Philosophy: Thin Harness + Fat Skills + Fat Data

Three-layer architecture where the model is NOT the bottleneck — understanding your data is.

### Layer 1: Thin Harness (~200 lines)
- CLI + MCP server, JSON in, text out
- Routes tasks to skills via RESOLVER.md
- Enforces trust boundaries (local CLI = trusted, MCP = untrusted)

### Layer 2: Fat Skills (47 Markdown files)
- Each skill is a reusable procedure, like a method call
- RESOLVER.md dispatches: trigger phrase → skill file
- Always-on skills (signal-detector, brain-ops) run every message
- Skills self-improve: after events, `/improve` reads feedback and rewrites skill rules

### Layer 3: Fat Data (100K+ brain pages)
- Structured markdown with YAML frontmatter (title, type, date, tags)
- 100+ cron jobs keep data fresh daily
- Iron Law: back-links mandatory, every fact carries `[Source: ...]`
- Key directories: people/, companies/, concepts/, meetings/, media/books/

## Book Mirror Design (the model for our implementation)

### Trust Contract (critical security design)
```
Subagents: allowed_tools=['get_page', 'search'] ONLY → read-only
CLI: assembles subagent outputs → writes ONE put_page with operator trust
→ Even if EPUB contains prompt injection, subagents have no write access
```

### Pipeline
1. ACQUIRE → user drops EPUB/PDF
2. EXTRACT → BeautifulSoup/pdftotext → one .txt per chapter
3. CONTEXT → USER.md + SOUL.md + 14d reflections + entity pages + topic search
4. ANALYZE → N parallel subagents (one per chapter), Claude Opus default
5. ASSEMBLE → CLI merges all child outputs into one brain page
6. FACT-CHECK → verify claims about reader (family, jobs, etc.)
7. BACK-LINK → cross-link mentioned entities

### Cost
- ~$0.30/chapter at Opus, ~$0.06 at Sonnet
- 20-chapter book ≈ $6 at Opus

## Key Design Decisions We Copied

| GBrain | Hermes Adaptation |
|--------|-------------------|
| Minions subagents | delegate_task (batch mode, up to 3 parallel) |
| CLI put_page with operator trust | Parent agent does final write_file |
| brain-query context gathering | brain-query skill (grep + read_file + MemOS) |
| RESOLVER.md routing | Hermes `<available_skills>` auto-discovery |
| `_brain-filing-rules.md` | BRAIN_FORMAT.md |
| `USER.md` / `SOUL.md` | Same format, mirrored directly |

## Latent vs Deterministic Boundary
- **Latent** (model): reading, judgment, synthesis, pattern recognition → goes in Skills
- **Deterministic** (code): SQL, math, file ops → goes in CLI / terminal tools
- Wrong: asking LLM to seat 800 people (deterministic problem forced into latent space)

## What We Didn't Copy (yet)
- Schema packs (dynamic type system for brain directories)
- `gbrain doctor --remediate --target-score 90` (auto-healing)
- Skill self-improvement loop (post-event analysis → rewrite skill rules)
- MinionQueue with idempotency keys
