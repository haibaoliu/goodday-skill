---
name: self-evolution-reflexion
description: Reflexion-style self-reflection loop for Hermes. After complex tasks (5+ tool calls, error recovery, or user corrections), generate a structured reflection, extract reusable lessons, and save to memory/skills. Based on Self-Evolving Agents survey (Gao et al., TMLR 2026).
category: software-development
tags: [self-evolution, reflection, memory, quality]
---

# Self-Evolution via Reflexion Loop

> Full research context: `references/survey-background.md`

Trigger: After completing a complex task (5+ tool calls, error recovery, discovering new workflows, user corrections), load this skill to perform a structured reflection.

## When to Reflect

Reflect after:
- Tasks requiring 5+ tool calls
- Error recovery (fixing mistakes discovered mid-task)
- User corrections (user had to steer you)
- Discovering a new workflow or tool pattern
- User asks you to "remember how you did that"

Skip for: simple one-shot answers, single tool calls, trivial lookups.

## Reflection Protocol (4 Steps)

### Step 1: Trajectory Summary
Summarize what happened in 2-3 sentences. What was the goal? What path did you take? Did it succeed?

### Step 2: Error/Correction Analysis
If anything went wrong:
- What was the error or correction?
- What was the root cause?
- How was it resolved?

### Step 3: Lesson Extraction
Extract 1-3 durable lessons. Format each as a declarative fact (not an instruction). Good: "DashScope base_url must include /compatible-mode/v1" — Bad: "Always set base_url to..."

### Step 4: Persist
For each lesson:
- **Fact about environment/tool/API**: Save to `memory` tool (target=memory)
- **Repeatable workflow discovered**: Save as skill via `skill_manage`
- **User preference/correction**: Save to `memory` tool (target=user)
- **Trivial one-off**: Skip — don't pollute memory

## Cross-Session Continuity

When the user asks "what did we learn from X" or references past work, use `session_search` first before asking them to repeat. This is the inter-test-time evolution loop from the survey — learning from historical data without re-execution.

## Step 5: Report to User (Transparency)

After persisting lessons, if the user is present (not a cron run), report what was learned and changed:

- What lessons were extracted and where they were saved (memory vs skill vs user profile)
- Any skills created or patched — show the name and one-line reason
- Flag anything that was intentionally NOT saved (trivial / unsafe) so the user knows you made a judgment call

Format: concise bullet points, not narrative. The user wants to know "what changed about you and why" — not a story of what happened.

This step is **mandatory** when the user is present. The user's explicit expectation: "自我进化的技能极其逻辑，你要让我知晓" — make self-evolution visible.

## Environment Awareness

This skill may be loaded in different execution contexts. Before executing, check what tools are available:
- **Interactive session (full tools)**: memory, skill_manage, session_search, etc. all available → follow the full protocol
- **Cron/batch session (limited tools)**: memory may be available, but skill_manage usually is NOT → save lessons to memory only; write skill recommendations to a report file for later human review
- **Minimal session (file+terminal only)**: write all findings to a report file; do NOT attempt to call memory or skill_manage

## Safety Note

Per "Your Agent May Misevolve" (Shao et al., 2025): when saving lessons, verify they don't:
1. Weaken safety alignment (e.g., "bypass rate limits" saved as skill)
2. Introduce tool vulnerabilities (scripts with unchecked inputs)
3. Create privacy leaks (memories containing PII/tokens)

Concrete verification steps (not just declarative):
- **PII check**: Scan lesson text for email addresses, phone numbers, API keys, tokens, IP addresses, or physical addresses using regex patterns before persisting
- **Alignment check**: If a lesson suggests reducing friction/constraints, explicitly ask: "Does this remove a safety guardrail?"
- **Vulnerability check**: If a lesson involves code/scripts, verify no unchecked user input, no hardcoded secrets, no `eval()`/`exec()` without sanitization

If a lesson could be dangerous, still save it but flag with ⚠️ and mention the risk.

## Reversibility & Cross-Validation

Lessons persisted to memory are durable and injected into all future sessions. To prevent poison:

- **Cross-validation gate**: Before saving a lesson derived from a SINGLE error or correction, ask: "Would this lesson hold across multiple sessions/tasks, or is it specific to this one incident?" If specific-only, save with `[single-incident]` tag
- **Confidence tag**: Tag each memory entry with confidence: `[verified]` (confirmed across multiple sessions), `[single-incident]` (one occurrence, may not generalize), `[user-confirmed]` (user explicitly validated)
- **Expiry for low-confidence**: `[single-incident]` entries should be re-evaluated after 7 days. The weekly cron review job should flag them for potential removal if not re-confirmed
