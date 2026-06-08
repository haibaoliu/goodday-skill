# GBrain — Thin Harness + Fat Skills + Fat Data

> Source: garrytan/gbrain (⭐18,244, MIT License)  
> Author: Garry Tan (YC President)  
> Researched: 2026-05-23

## Overview

GBrain is a personal knowledge brain — not a traditional vector-store RAG, but a **knowledge compounding engine** where every insight from every book, meeting, and conversation feeds into a growing judgment system.

The core philosophy: **Thin Harness + Fat Skills + Fat Data**

```
        ┌──────────────────┐
        │   Fat Skills     │  ← 47 Markdown Skill files, single-task, composable
        │  (Markdown .md)  │
        └────────┬─────────┘
                 │
        ┌────────┴─────────┐
        │  Thin Harness    │  ← ~200 lines core, JSON in / text out, swappable models
        │  (CLI + MCP)     │
        └────────┬─────────┘
                 │
        ┌────────┴─────────┐
        │   Fat Data       │  ← 100K+ "brain pages", interlinked, 100+ cron jobs daily
        │  (Markdown + DB) │
        └──────────────────┘
```

## Key Principles

### 1. Skill as Method Call
Markdown files ARE code. A skill is a reusable procedure that takes parameters. Same skill, different invocation = different capability. Skills encode process, not content.

### 2. Latent vs Deterministic Boundary
- **Latent space** (LLM): reading, interpreting, judging, synthesizing → Skills
- **Deterministic** (code): SQL, math, file ops, lookups → CLI
- Wrong boundary = disasters (LLM seating 800 guests hallucinates)

### 3. Knowledge Compounding
Every book's insight isn't isolated — every meeting, conversation, and action item becomes mapping material for the next book. Context grows thicker, judgment grows sharper. Compound interest for knowledge.

## Brain Page Data Model

Every "brain page" is a Markdown file with YAML frontmatter:

```yaml
---
title: "Page Title"
type: person | company | concept | book-analysis | meeting | reflection
date: YYYY-MM-DD
tags: [...]
context: "..."
---
```

### Directory Structure
| Directory | Content | 
|-----------|---------|
| `people/` | Person profiles with Timeline entries + back-links |
| `companies/` | Company profiles |
| `concepts/` | Reusable mental models |
| `meetings/` | Meeting transcripts + extracted entities |
| `media/books/` | Personalized book analyses (Book Mirror output) |
| `wiki/personal/` | Daily reflections, original ideas, pattern detection |

### Core Rules
1. **Primary subject determines location** — not format, not source
2. **Iron Law: back-linking** — every entity mention MUST link back from entity's page
3. **Every fact carries `[Source: ...]`** citation
4. **Notability gate** — not everything deserves a brain page; junk degrades search

## Book Mirror — Flagship Skill

Personalized chapter-by-chapter book analysis. The core innovation: **two-column table** — left = author's content, right = reader's personal life mapped point-by-point.

### Pipeline (6 steps)
```
EPUB/PDF → Extract chapters → Gather brain context → N read-only subagents → Assemble → Write brain page
```

### Security Trust Model (most instructive part)
- Each chapter = 1 subagent with `allowed_tools: ['get_page', 'search']` (READ-ONLY)
- Subagents produce markdown text as final message; NEVER call `put_page`
- CLI assembles all child outputs and writes ONE `put_page` with operator trust
- Untrusted EPUB content cannot prompt-inject any page — write access closed at tool layer

### Cost
- ~$0.30/chapter at Claude Opus, ~$6 for 20-chapter book
- Idempotency keys (`book-mirror:<slug>:ch-<N>`) for cheap retry

## RESOLVER.md — Skill Dispatch

A routing table that maps triggers to skills. Every inbound message matches against triggers → loads the right skill. Supports:
- **Always-on skills** (run every message, e.g. signal-detector)
- **Disambiguation rules** (prefer specific over generic)
- **Chaining** (ingest → enrich for each entity)

## Quality Conventions (cross-cutting)

- `quality.md`: citation rules, back-link enforcement, notability gate
- `brain-first.md`: check brain before external APIs
- `brain-routing.md`: which brain (DB) and which source (repo)
- `subagent-routing.md`: when to use Minions vs inline work

## Self-Learning Loop

After events: read satisfaction data → extract patterns → **rewrite skill files**. The skill file itself learns and improves over time. Example: "12% OK ratings" → pattern extracted → rule added to skill → next run 4%.

## Comparison to Hermes

| Aspect | GBrain | Hermes |
|--------|--------|--------|
| Skill format | Markdown SKILL.md | Markdown SKILL.md ✅ same |
| Skill dispatch | RESOLVER.md trigger table | `<available_skills>` + descriptions |
| Brain pages | Markdown files with frontmatter | MemOS memory traces |
| Back-links | Mandatory, bidirectional | Not yet |
| Subagent safety | Read-only tools for untrusted input | `delegate_task` with toolsets |
| Cron | 100+ daily jobs | `cronjob` tool |
| Self-evolution | Skill files rewrite themselves | `self-evolution-reflexion` skill |

## What Hermes Can Adopt

1. **Book Mirror** — buildable as a Hermes skill using `delegate_task` + memory
2. **Brain page structure** — enhance MemOS world_model with frontmatter + back-links
3. **Read-only subagent trust model** — restrict toolsets for untrusted-content processing
4. **RESOLVER.md pattern** — already have `<available_skills>`, could add always-on skills
