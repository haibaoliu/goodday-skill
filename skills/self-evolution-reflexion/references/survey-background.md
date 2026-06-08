# Background: Self-Evolving Agents Survey

## Source Paper

**Title**: A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve on the Path to Artificial Super Intelligence
**Authors**: Gao, Geng, Hua, Hu, et al. (Princeton, Tsinghua, CMU, +15 institutions)
**Venue**: Transactions on Machine Learning Research (TMLR), January 2026
**Links**:
- OpenReview: https://openreview.net/forum?id=CTr3bovS5F
- arXiv: https://arxiv.org/abs/2507.21046
- Code: https://github.com/CharlesQ9/Self-Evolving-Agents

## Why This Skill Was Created

User shared a WeChat article about self-evolving agents → Hermes deep-researched the original survey paper (77 pages) → performed gap analysis against Hermes capabilities → executed concrete self-evolution actions.

The reflexion loop in this skill is directly modeled on:
- **Reflexion** (Shinn et al., 2023) — "verbal reinforcement learning" where agents reflect in natural language on past trials
- **Memory Evolution** (Section 3.2.1 of survey) — Mem0, MemInsight, REMEMBER, Expel patterns
- **Inter-test-time evolution** (Section 4.2) — retrospective learning after task completion

## Key Design Decisions

1. **4-step protocol over free-form reflection**: The survey's Table 2 shows Reflexion only evolves Context (not Model/Architecture). Our protocol is deliberately scoped to what Hermes can actually change — memory and skills.
2. **Declarative facts, not instructions**: "DashScope base_url must include /compatible-mode/v1" not "Always set base_url to...". Instructions get re-read as directives in later sessions and override user intent.
3. **Safety gate (Step 4)**: Per "Your Agent May Misevolve" (Shao et al., 2025), every lesson is checked against three failure modes before saving.
4. **Transparency mandate (Step 5)**: User explicitly demanded visibility into self-evolution — "自我进化的技能极其逻辑，你要让我知晓".

## Related Hermes Capabilities

| Hermes Feature | Survey Equivalent |
|----------------|-------------------|
| memory + memos_search | Memory Evolution (3.2.1) |
| session_search | Inter-test-time data source |
| skill_manage | Tool Creation (3.3) |
| delegate_task | Multi-Agent (3.4.2) |
| other-review | Textual Feedback (5.1), external variant |

## Creation Date

2026-05-22, during a session that deep-researched the survey paper and executed self-evolution.
