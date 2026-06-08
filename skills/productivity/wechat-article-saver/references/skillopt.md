# SkillOpt — Microsoft's Self-Evolving Skill Optimizer

> `github.com/microsoft/SkillOpt` ⭐3057 · MIT · 2026-05-08

## What it does
Trains agent skills like neural networks — with epochs, batch sizes, learning rates, and validation gates — but optimizes ONLY the skill text (SKILL.md), never touching model weights.

## Core pipeline
```
原始 Skill → Agent 跑任务 → 收集成功/失败轨迹 → Optimizer LLM 编辑 Skill → 验证门禁 → best_skill.md
```

## Key numbers (from paper)
- GPT-5.5 direct chat: +23.5 分
- Codex agentic loop: +24.8 分
- Claude Code: +19.1 分
- Best or tied on ALL 52 evaluated (model × benchmark × harness) cells

## Setup with DashScope (OpenAI-compatible)

```bash
git clone https://github.com/microsoft/SkillOpt.git
cd SkillOpt
pip install -e .

# Environment
export AZURE_OPENAI_ENDPOINT="https://dashscope.aliyuncs.com/compatible-mode/v1"
export AZURE_OPENAI_API_KEY="<your-dashscope-key>"
export AZURE_OPENAI_AUTH_MODE="openai_compatible"
```

## Supported backends
- Optimizer: `openai_chat`, `claude_chat`
- Target: `openai_chat`, `claude_chat`, `qwen_chat`, `codex_exec`, `claude_code_exec`

## Gap to Hermes
SkillOpt expects QA-format data (`{question, context, answers}`). Hermes skills are procedural documents. To adapt, need:
1. Define task items per skill (user requests that trigger this skill)
2. Define success criteria (agent completed task correctly, not "got right answer")
3. Write Hermes env adapter that calls Hermes Agent as the execution harness

## Installed at
`/Users/macbook/Documents/hermes-output/SkillOpt/`
