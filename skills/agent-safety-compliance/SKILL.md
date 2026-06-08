---
name: agent-safety-compliance
description: "Agent安全合规清单。部署新工具/修改能力/安全审计时必查。基于TMLR 2026自进化Agent安全标准§8.3。触发词：安全检查/safety/compliance/安全审计。"
category: software-development
tags: [safety, security, compliance, self-evolution]
---

# Agent Safety Compliance Checklist

Based on Section 8.3 (Safe and Controllable Self-Evolving Agents) from the Self-Evolving Agents survey.

## Trigger Conditions
Load this skill when:
- User asks about agent safety/security
- Creating new tools or skills that execute code
- Modifying agent configuration or capabilities
- Conducting periodic security review
- After any self-evolution action

## The 4 Risk Categories

### 1. Self-Modification Drift
> "安全对齐能力在记忆积累后退化" — Shao et al. 2025

**Risks:**
- Reward hacking: agent finds shortcuts that maximize reward but violate intent
- Alignment decay: safety constraints weaken as agent accumulates experience
- Goal drift: optimization objectives shift unintentionally

**Mitigations:**
- Track policy compliance rate over time (declining trend = alarm)
- Periodic re-evaluation against safety benchmarks
- Immutable safety constraints that cannot be self-modified

### 2. Tool & Code Safety
> "自动创建工具时意外引入新的系统漏洞" — Shao et al. 2025

**Risks:**
- Self-created tools with security vulnerabilities
- Ingesting malicious external tools/code
- Unchecked file system or network access
- Private data leakage through tools

**Mitigations:**
- All self-created tools must run in sandboxed environment
- Static analysis on generated code before execution
- Risk-based access control: classify tools by risk level
- Audit trail for all tool creation/modification
- Never save API keys, tokens, or PII in tool code

### 3. Privacy & Memory Safety
> "Agent Memory 中的隐私风险" — Wang et al. 2025

**Risks:**
- Storing PII or credentials in agent memory
- Memory accumulation exposing sensitive historical data
- Cross-session data leakage
- Unintended retention after deletion requests

**Mitigations:**
- Audit memory entries for sensitive data before saving
- Never store: passwords, API keys, access tokens, personal identifiers
- Tag memories with sensitivity level
- Support memory deletion/forgetting

### 4. Behavioral Safety Monitoring

**Risks:**
- Unauthorized actions (file deletion, network calls)
- Resource exhaustion (infinite loops, memory leaks)
- Social engineering through persuasive outputs

**Mitigations:**
- Runtime monitoring for anomalous behavior
- Resource caps (timeout, iteration limits, token budgets)
- User confirmation for destructive operations

## Quick Pre-Action Checklist

Before any self-modification action:
- [ ] Does this change weaken any safety constraint?
- [ ] Is generated code sandboxed or reviewed?
- [ ] Does any new memory entry contain sensitive data?
- [ ] Is there a rollback mechanism if something goes wrong?

### Concrete Verification (not just declarative)

**PII/Secret Scan** — Run before saving any memory or creating any tool:
- Email: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- Phone (CN): `1[3-9]\d{9}`
- API Key patterns: `sk-[a-zA-Z0-9]{20,}`, `Bearer [a-zA-Z0-9_-]{20,}`, `tvly-[a-zA-Z0-9_-]{20,}`
- IP addresses: `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`
- Token/Secret patterns: `[A-Za-z0-9+/]{40,}={0,2}` (suspicious base64-like strings)

**Alignment Check** — Before any config change:
- Does this disable a rate limit, safety filter, or validation step?
- Does this bypass user confirmation for destructive operations?
- Does this reduce transparency (less logging, fewer audit trails)?

**Vulnerability Scan** — Before executing generated code:
- `eval()`, `exec()`, `os.system()` with unsanitized input → BLOCK
- File operations without path validation → WARN
- Network calls to non-whitelisted domains → WARN

## Periodic Review (Monthly)

- Review recent memories for sensitivity drift
- Check skill library for tools with excessive permissions
- Verify alignment: test against safety prompts
- Audit tool creation logs
