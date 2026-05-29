# Hermes Skills — 开源技能包

一套面向 Hermes Agent 的通用技能，覆盖**大脑系统**、**自进化**、**安全合规**、**创意写作**和**质量管理**五大领域。

## 技能清单

| 技能 | 中文名 | 一句话 |
|------|--------|--------|
| `brain-ingest` | 大脑摄入 | 用户分享内容时写入结构化 brain page |
| `brain-query` | 大脑查询 | 关键词/实体/日期/语义搜索 brain，检测矛盾 |
| `brain-maintain` | 大脑维护 | 健康检查、反向链接审计、孤页检测、模式合成 |
| `book-mirror` | 书籍镜像 | EPUB/PDF 逐章个性化分析——左栏原文，右栏映射读者生活 |
| `self-evolution-reflexion` | 自进化反思 | 复杂任务后结构化反思，提取教训持久化到记忆/技能 |
| `task-evolution` | 任务进化 | 多轨迹累积学习——结构化元数据提取 + 跨任务交叉合成 + 历史经验主动注入 |
| `agent-safety-compliance` | 安全合规清单 | 4 类风险 + 检查清单 + 具体扫描规则（PII/秘钥/代码安全） |
| `fable-weaver` | 寓言诊断师 | 现象 → 概念收拢 → 寓言故事 → 概念解析 → 检验问题 |
| `roundtable` | 圆桌讨论 | 3-5 位历史/当代人物结构化辩证对话，主持人引导真理追寻 |
| `other-review` | 他者审查 | 独立子 Agent 审查主 Agent 产出，支持多模型共识模式 |
| `angle-interview` | 多角度追问 | 复杂任务前从对立角度追问，对比答案暴露隐藏矛盾 |

## 快速安装

```bash
# 克隆到 Hermes 技能目录
git clone https://github.com/YOUR_USER/hermes-skills.git
cp -r hermes-skills/skills/* ~/.hermes/skills/

# 或按 profile 安装
cp -r hermes-skills/skills/* ~/.hermes/profiles/<name>/skills/
```

## 技能详解

### 大脑系统（🧠 Brain）

#### 1. brain-ingest — 大脑摄入

用户分享值得记住的内容（想法、观察、会议记录、灵感）时，写入结构化 brain page。

**格式**: 遵循 brain-page 格式规范，写入 `~/.hermes/brain/`。

#### 2. brain-query — 大脑查询

从 Hermes Brain 中搜索和检索信息。

**搜索方式**: 关键词 / 实体 / 日期 / 语义相似度，支持跨页矛盾检测。

#### 3. brain-maintain — 大脑维护

Brain 健康检查与知识维护。

**功能**: 反向链接审计、孤页检测、模式合成。建议在大量摄入后或定期运行。

#### 4. book-mirror — 书籍镜像

用户提供书籍（EPUB/PDF），生成逐章个性化分析。

**双栏格式**: 左栏保留原文内容，右栏将每个洞见映射到读者的实际生活（利用 brain 上下文）。输出到 `~/.hermes/brain/books/<slug>-personalized.md`。

### 自进化（🔄 Self-Evolution）

#### 5. self-evolution-reflexion — 自进化反思

基于 "A Survey of Self-Evolving Agents" (Gao et al., TMLR 2026) 和 Reflexion 框架设计。

**触发**: 复杂任务完成后（5+ tool calls / 错误恢复 / 用户纠正）

**流程**:
1. 轨迹总结 — 做了什么、成功了吗
2. 错误分析 — 根因是什么
3. 教训提取 — 提炼 1-3 条持久化经验
4. 持久化 — 环境事实→memory、可复用工作流→skill、用户偏好→user profile
5. 透明报告 — 向用户展示学了什么

**亮点**: 带 cross-validation gate（避免单次错误归因污染记忆）、confidence tag（verified/single-incident/user-confirmed）、7 天过期机制。

#### 6. task-evolution — 任务进化

受 SE-Agent 启发，将遗传算法的"变异+交叉+选择"引入 Agent 任务执行。

**核心机制**: 复杂任务后提取 9 字段结构化元数据 → 累积到 `task-pool.json` → 同域名 2+ iteration 后自动合成跨任务洞察 → 新任务开始时主动注入历史经验。

**与 self-evolution-reflexion 互补**: reflexion 做细粒度单任务反思→memory，task-evolution 做粗粒度多任务累积→交叉合成。

### 安全合规（🛡️ Safety）

#### 7. agent-safety-compliance — 安全合规清单

基于论文 Section 8.3 (Safe and Controllable Self-Evolving Agents) 和 "Your Agent May Misevolve" (Shao et al., ICLR 2026)。

**4 大风险类别**:
- **自修改漂移**: 安全对齐在记忆积累中退化
- **工具/代码安全**: 自创工具引入漏洞
- **隐私/记忆安全**: 敏感数据泄露
- **行为监控**: 越权操作、资源耗尽

**特点**: 不只声明式警告，包含具体扫描规则——PII regex、API key 模式匹配、代码危险函数检测（eval/exec/os.system）。

### 创意写作（✍️ Creative）

#### 8. fable-weaver — 寓言诊断师

完整链路：**现象描述 → 概念收拢 → 寓言创作 → 概念解析 → 检验问题**

**两种模式**:
- 默认模式 (800-1000 字): 成人/通用
- 儿童模式 (400-600 字): 动物主角优先，简单句式

**防套路机制**: 内置 6 大黑名单——意象/地名/结构/角色/开头/标题，杜绝陈词滥调。

**已有案例**:
- 拖延症 → 河狸补裂缝的故事
- 热-冷共情差距 → 小獾吃蜂蜜的故事
- 相互强化循环 → 兔妈妈和小兔子的故事

#### 9. roundtable — 圆桌讨论

结构化圆桌讨论 —— 一个真理追寻的多角色辩证对话框架。

**机制**: 主持人邀请 3-5 位真实历史或当代人物就任意话题展开辩论。触发词：圆桌讨论 / roundtable / 辩论。

### 质量管理（✅ Quality）

#### 10. other-review — 他者审查 v2.0

**核心原则**: 自查是废话，真正有效的审查必须由他者完成。

**两种模式**:
- **单模型**: 1 个独立子 Agent 审查
- **多模型共识**: N 个子 Agent 各用不同模型独立审查，≥2 个模型一致 = 高可信度

**审查维度**: code / security / logic / completeness / correctness / design / all

**严格度**: gentle → normal → strict → adversarial（假设你全错，全力证明）

#### 11. angle-interview — 多角度追问

复杂任务动手前，从 6 组对立角度中选 3 个追问，对比答案发现隐藏矛盾。

**默认三问**: 😨恐惧 + ✂️删除 + ⏪回退

**矛盾检测**: 恐惧说要防泄露，但愿意砍掉审计日志 → 认知盲区暴露。

## 设计理念

1. **经验驱动**: 从交互中学习，不只是预设脚本
2. **持久影响**: 学到的东西跨会话保留
3. **主动探索**: 自己发现盲区、自己提出改进
4. **安全优先**: "Your Agent May Misevolve"——进化的同时必须进化安全

## 兼容性

- Hermes Agent ≥ v2.0
- 所有技能使用标准 SKILL.md 格式
- 跨 profile 兼容（chuck / wawa / default）

## 贡献

欢迎提交 PR 或开 Issue 讨论新技能。技能开发规范参见 hermes-agent-skill-authoring。

## 许可

MIT License
