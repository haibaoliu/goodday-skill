# External AI Coding Projects — Analysis for Hermes

Analysis conducted 2026-06-03. Three projects inspected for design patterns
applicable to Hermes Agent.

## 1. vibecode-pro-max-kit (withkynam, ⭐724)

**What it is:** A meta-harness that turns Claude Code / Codex into a 12-agent
engineering team via config/process layer.  Not a framework — it's installed
into your project.  579 files.

**Top patterns applicable to Hermes:**

### RIPER-5 Five-Phase Workflow
RESEARCH → INNOVATE → PLAN → EXECUTE → UPDATE PROCESS.  Strict phase-locking
prevents jumping to implementation.  Each agent has a different model (opus for
EXECUTE, sonnet for planning) and different tool permissions.  Hermes already
has `plan` skill but only covers the PLAN phase — missing RESEARCH, INNOVATE,
and UPDATE PROCESS.

### all-*.md Routing Protocol
Context files use router→leaf pattern.  `all-context.md` is a ROUTER, not
the full knowledge — agents read it, then follow a routing table to the
smallest relevant deep doc.  This dramatically reduces context window usage.
**Adopted in Hermes:** skill routing table (`skills.routing_table`) replaces
full XML listing with compact intent→skill mapping (~71% token savings).

### Session State Hooks
7 hooks survive context compaction.  On compaction, the hook replays saved
state so agents resume exactly where they left off.  Hermes has no equivalent.

### High-Risk Evidence Harness
For auth/billing/schema changes: `risk-gate.json`, `verification.json`,
`adversarial-validation.json`.  Hermes's `other-review` skill is a lightweight
version of this.

### UPDATE PROCESS Six-Phase Reconciliation
Post-execution: analyze conversation → generate improvements (7 categories) →
user approval → implement → final review → plan audit.  Hermes lacks systematic
post-mortem.

---

## 2. filetree-skill (nekocode, ⭐134)

**What it is:** 573-line Python script that auto-maintains `FILETREE.md`.
Claude Code plugin with 3 commands (init, update, lint).

**Core design philosophy:** Deterministic Python script handles all repo
operations (file discovery, hashing, rename detection, atomic writes).
LLM only provides one-line file-purpose summaries.  This is the key insight:

```
Script: file discovery, diff, hash, rename detection, coverage check, atomic write
LLM:    write a 25-word summary of what each file does
```

**Patterns adopted in Hermes plan:**
- "确定性脚本 + LLM 语义" separation pattern (pending #3)
- UNCHANGED bias: 80% of files return `"UNCHANGED"` (4 bytes) instead of
  regenerating a ~100-byte summary.  100x token savings.
- Self-healing coverage gate: `apply` returns `missing_from_manifest` →
  agent loops until clean.  No trust in single-pass LLM output.
- Parallel sub-agents with cheaper models (haiku) for batch processing.

---

## 3. cc-fleet (ethanhq, ⭐72)

**What it is:** Go CLI that process-level swaps Claude Code's LLM backend.
Launches real `claude` processes with vendor-specific `--settings` profiles
(redirecting `ANTHROPIC_BASE_URL`) and `--model` flags.

**Key security pattern adopted in Hermes:**

### apiKeyHelper → api_key_command
Instead of storing keys in env/argv/config, Claude Code calls
`cc-fleet keyget <vendor>` at runtime, which writes the key to stdout once.
The spawn command UNSETS `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN`:
```
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN CLAUDECODE=1 ... claude --settings <profile> ...
```

**Implemented in Hermes as `api_key_command`** (PR #1):
- `ProviderConfig.api_key_command` field
- `_resolve_api_key_provider_secret()` executes command and uses stdout
- Custom providers also support it via `_resolve_named_custom_runtime()`
- Key never enters env/argv/history/configuration files

### Other cc-fleet patterns (not yet adopted):
- **Fingerprint capture**: captures live Agent process argv, parametrizes as
  `{name}@{team}` template — immune to CLI version drift
- **Two-lane architecture**: Lane 1 (stateful teammate via tmux) + Lane 2
  (one-shot headless subagent via `claude -p`).  Hermes only has Lane 2.
- **Triple-lock flock**: VendorsConfigLock → TeamLock → ServerLock.  Deadlock-free
  by design.  Hermes cron jobs have no equivalent.
- **Atomic rollback**: every step in spawn pipeline has failure cleanup.
- **Cross-vendor error classification**: Chinese+English signatures for
  401/403/429/balance errors → unified `error_code` dispatch.

---

## Implementation Plan (4 items)

| # | Item | Status |
|---|------|--------|
| 1 | `api_key_command` provider support | ✅ Done |
| 2 | Skill routing table (`skills.routing_table`) | ✅ Done |
| 3 | Script+LLM separation pattern for skills | Pending |
| 4 | UNCHANGED bias for cron job outputs | Pending |
