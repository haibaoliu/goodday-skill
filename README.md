# Hermes Skills — 开源技能包

一套面向 Hermes Agent 的通用技能，覆盖**自进化**、**安全合规**、**创意写作**、**质量管理**和**知识脑系统**五大领域。

## 技能清单

| 技能 | 中文名 | 一句话 |
|------|--------|--------|
| `self-evolution-reflexion` | 自进化反思 | 复杂任务后结构化反思，提取教训持久化到记忆/技能 |
| `agent-safety-compliance` | 安全合规清单 | 4 类风险 + 检查清单 + 具体扫描规则（PII/秘钥/代码安全） |
| `fable-weaver` | 寓言诊断师 | 现象 → 概念收拢 → 寓言故事 → 概念解析 → 检验问题 |
| `other-review` | 他者审查 | 独立子 Agent 审查主 Agent 产出，支持多模型共识模式 |
| `angle-interview` | 多角度追问 | 复杂任务前从对立角度追问，对比答案暴露隐藏矛盾 |
| `book-mirror` | 双栏书镜 | EPUB/PDF → 章节双栏个人化映射，基于脑上下文 |
| `brain-ingest` | 脑页摄入 | 值得记住的内容 → 结构化脑页，自动归类 + back-link |
| `brain-query` | 脑页检索 | 关键词/语义检索 + 跨页面矛盾检测 + 上下文收集 |
| `brain-maintain` | 脑页维护 | 孤岛检测、back-link 审计、跨会话模式合成 |

## Hermes Brain System（🆕）

`book-mirror` + `brain-ingest` + `brain-query` + `brain-maintain` 组成完整的知识复利系统：

```
你说 "记住这个"  ──→ brain-ingest ──→ 写入 people|reflections|patterns
                                         ↓
你说 "检查脑"    ──→ brain-maintain ──→ 孤岛检测 + back-link + 模式合成
                                         ↓
你扔一本书       ──→ book-mirror ──────→ brain-query 收集上下文
                                      → N 个子 Agent 并行 (只读!)
                                      → 拼装双栏 Markdown
                                      → 写入 books/ + back-link
```

基于 GBrain (garrytan/gbrain) 的 Thin Harness + Fat Skills 架构理念。

## 快速安装

```bash
git clone https://github.com/haibaoliu/goodday-skill.git
cp -r goodday-skill/skills/* ~/.hermes/skills/
# 或按 profile 安装
cp -r goodday-skill/skills/* ~/.hermes/profiles/<name>/skills/
```

## 技能详解

### 1. self-evolution-reflexion — 自进化反思

基于 "A Survey of Self-Evolving Agents" (Gao et al., TMLR 2026) 和 Reflexion 框架设计。

**触发**: 复杂任务完成后（5+ tool calls / 错误恢复 / 用户纠正）

**流程**:
1. 轨迹总结 — 做了什么、成功了吗
2. 错误分析 — 根因是什么
3. 教训提取 — 提炼 1-3 条持久化经验
4. 持久化 — 环境事实→memory、可复用工作流→skill、用户偏好→user profile
5. 透明报告 — 向用户展示学了什么

### 2. agent-safety-compliance — 安全合规清单

**4 大风险类别**: 自修改漂移、工具/代码安全、隐私/记忆安全、行为监控。

### 3. fable-weaver — 寓言诊断师

完整链路：现象描述 → 概念收拢 → 寓言创作 → 概念解析 → 检验问题。支持儿童模式。

### 4. other-review — 他者审查 v2.0

独立子 Agent 审查主 Agent 产出。单模型 / 多模型共识两种模式。严格度：gentle → adversarial。

### 5. angle-interview — 多角度追问

复杂任务前从 😨恐惧 + ✂️删除 + ⏪回退 三个对立角度追问，暴露隐藏矛盾。

### 6. book-mirror — 双栏书镜

EPUB/PDF → 提取章节 → 收集脑上下文 → N 个子 Agent 并行分析(只读!) → 拼装双栏对照脑页。基于 GBrain 的信任安全模型：子 Agent 只读，父 Agent 写。

### 7. brain-ingest — 脑页摄入

对话中值得记住的内容自动归档到结构化脑页，按主体归类（people/reflections/patterns/concepts）。

### 8. brain-query — 脑页检索

关键词 + 语义检索脑页，支持跨页面矛盾检测，为 book-mirror 提供上下文收集。

### 9. brain-maintain — 脑页维护

孤岛检测、back-link 完整性审计、≥3 次出现的跨会话模式自动合成。

## 设计理念

1. **经验驱动**: 从交互中学习，不只是预设脚本
2. **持久影响**: 学到的东西跨会话保留
3. **主动探索**: 自己发现盲区、自己提出改进
4. **安全优先**: "Your Agent May Misevolve"——进化的同时必须进化安全

## 兼容性

- Hermes Agent ≥ v2.0
- 所有技能使用标准 SKILL.md 格式
- 跨 profile 兼容（chuck / wawa / default）

## 许可

MIT License
