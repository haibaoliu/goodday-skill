# Hermes Skills

> Chuck 的 Hermes Agent Skills 合集

## Skills 列表

| Skill | 描述 | 版本 |
|-------|------|------|
| [roundtable](skills/roundtable/SKILL.md) | 结构化圆桌讨论 — 以求真为目标的多人物辩证对话框架。邀请 3-5 位真实人物辩论任意议题，每轮生成 ASCII 思考框架图，输出知识网络。 | 1.0.0 |
| [angle-interview](skills/angle-interview/SKILL.md) | 多角度追问 — 复杂任务启动前，从不同立场追问同一个问题，对比答案发现隐藏假设和矛盾。 | 1.0.0 |
| [other-review](skills/other-review/SKILL.md) | 他者审查 — 用独立子 Agent 审查主 Agent 的工作成果，拒绝自圆其说。 | 1.0.0 |
| [self-evolution-reflexion](skills/self-evolution-reflexion/SKILL.md) | Reflexion 式自省 — 任务完成后回顾得失，提取可复用经验。 | 1.0.0 |
| [agent-safety-compliance](skills/agent-safety-compliance/SKILL.md) | Agent 安全合规检查清单。 | 1.0.0 |
| [fable-weaver](skills/fable-weaver/SKILL.md) | 寓言诊断师 — 将任何现象或概念转化为精炼的寓言故事。 | 1.0.0 |
| [book-mirror](skills/book-mirror/SKILL.md) | 书籍镜像 — 将 EPUB/PDF 书籍转化为结构化知识图谱。 | 1.0.0 |
| [brain-ingest](skills/brain-ingest/SKILL.md) | 记忆摄入 — 将用户分享的有价值内容存入 Brain 知识库。 | 1.0.0 |
| [brain-maintain](skills/brain-maintain/SKILL.md) | Brain 维护 — 健康检查、反向链接审计、去重。 | 1.0.0 |
| [brain-query](skills/brain-query/SKILL.md) | Brain 查询 — 从 Hermes Brain 知识库检索信息。 | 1.0.0 |

## 安装

```bash
git clone https://github.com/haibaoliu/goodday-skill.git
cp -r goodday-skill/skills/* ~/.hermes/profiles/<profile>/skills/
```
