# Hermes Skills — 开源技能包

一套面向 Hermes Agent 的通用技能，覆盖大脑系统、自进化、安全合规、创意写作、质量管理、多智能体协作、研究搜索、DevOps、开发工具、效率和旅行领域。

## 技能清单

| 技能 | 中文名 | 一句话 |
|------|--------|--------|
| `brain-ingest` | 大脑摄入 | 想法/观察/笔记 → 结构化 brain page |
| `brain-query` | 大脑查询 | 搜索 brain：关键词/实体/日期/语义 |
| `brain-maintain` | 大脑维护 | 死链/孤立页/反向链接审计 |
| `book-mirror` | 书镜 | EPUB/PDF 逐章分析，左栏原文，右栏映射读者生活 |
| `self-evolution-reflexion` | 自进化反思 | 复杂任务后结构化反思，教训持久化 |
| `task-evolution` | 任务进化 | 多轨迹累积：元数据提取+跨任务合成+经验注入 |
| `agent-safety-compliance` | 安全合规 | 4类风险+扫描规则（PII/秘钥/代码安全） |
| `fable-weaver` | 寓言诊断师 | 现象→概念→寓言→解析→检验 |
| `humanizer` | 去AI腔 | 润色文本，改得像人写的不僵硬 |
| `other-review` | 他者审查 | 独立子Agent审查，v2.0 多模型共识 |
| `angle-interview` | 多角度追问 | 复杂任务前对立角度追问，暴露隐藏矛盾 |
| `roundtable` | 圆桌辩论 | 3-5位人物结构化辩证对话 |
| `devops/kanban-orchestrator` | 看板编排器 | 任务分解+死胡同回避+停滞检测 |
| `devops/kanban-worker` | 看板工人 | 工作器规范：交棒格式/死胡同记录/重试 |
| `research/github-ai-analysis` | GitHub分析 | AI/ML开源项目深度分析和评估 |
| `research/sirchmunk-intel-mac` | Sirchmunk | Intel Mac 文档全文搜索安装运行 |
| `devops/cron-management` | Cron管理 | 调度策略/限流规避/故障模式 |
| `software-development/agent-memory-systems` | 记忆系统 | 评估比较选择 Agent 记忆方案 |
| `software-development/hermes-codebase` | Hermes源码 | 修改/扩展/debug Hermes Agent 代码 |
| `software-development/python-dependency-resolution` | Pip依赖 | pip依赖冲突解决，版本匹配 |
| `software-development/goodday-trading-systems` | 交易系统 | Goodday 量化交易系统分析扩展 |
| `productivity/notebooklm` | NotebookLM | Login/list/create/chat/source管理 |
| `productivity/wechat-article-saver` | 公众号保存 | 微信文章→Markdown+NotebookLM |
| `bilibili-search` | B站搜索 | 零认证搜索+字幕提取 |
| `travel/japan-travel-assistant` | 日本旅行 | 中日双语翻译+交通导航+带娃攻略 |

## 快速安装

```bash
# 克隆到 Hermes 技能目录
git clone https://github.com/haibaoliu/goodday-skill.git
cp -r goodday-skill/skills/* ~/.hermes/skills/

# 或按 profile 安装
cp -r goodday-skill/skills/* ~/.hermes/profiles/<name>/skills/
```

## 技能详解

### 大脑系统（🧠 Brain）

#### brain-ingest — 大脑摄入

用户分享值得记住的内容（想法、观察、会议记录、灵感）时，写入结构化 brain page。触发词：记住/存起来/ingest/消化这篇文章。

#### brain-query — 大脑查询

从 Hermes Brain 搜索和检索信息。搜索方式：关键词/实体/日期/语义相似度，支持跨页矛盾检测。触发词：之前聊过/还记得/查记录/search/recall。

#### brain-maintain — 大脑维护

Brain 健康巡检。死链检测、孤立页检测、反向链接审计、模式识别。触发词：brain检查/巡检/脑检。定期跑或大量摄入后跑。

#### book-mirror — 书镜

EPUB/PDF 逐章个性化分析。双栏格式：左栏保留原文，右栏将每个洞见映射到读者的实际生活。触发词：读书/分析这本书/书镜/book analysis。

### 自进化（🔄 Self-Evolution）

#### self-evolution-reflexion — 自进化反思

复杂任务后结构化反思，提取教训持久化到记忆/技能。基于 TMLR 2026 和 Reflexion 框架。带 cross-validation gate 和 confidence tag。

#### task-evolution — 任务进化

受 SE-Agent 启发，多轨迹累积学习。9字段结构化元数据→累积到 task-pool.json→跨任务交叉合成→新任务启动时主动注入历史经验。

### 安全合规（🛡️ Safety）

#### agent-safety-compliance — 安全合规清单

基于 Section 8.3 (Safe Controllable Self-Evolving Agents) 和 "Your Agent May Misevolve"。PII regex、API key 模式匹配、代码危险函数检测。触发词：安全检查/safety/compliance/安全审计。

### 创意写作（✍️ Creative）

#### fable-weaver — 寓言诊断师

完整链路：现象描述→概念收拢→寓言创作→概念解析→检验问题。防套路黑名单杜绝陈词滥调。触发词：寓言/fable/讲故事/换个说法。

#### humanizer — 去AI腔

文本润色，剥离 AI 腔调，改得像真人写的。触发词：润色/改人话/humanize/de-AI/natural voice。@blader/humanizer 移植。

### 质量管理（✅ Quality）

#### other-review — 他者审查 v2.0

独立子 Agent 审查主 Agent 产出，支持多模型共识模式。审查维度：code/security/logic/completeness/correctness/design。严格度：gentle/normal/strict/adversarial。触发词：审查/检查/review/找问题/audit/critique。

#### angle-interview — 多角度追问

复杂任务前从😨恐惧+✂️删除+⏪回退三个对立角度追问，对比答案暴露隐藏矛盾和认知盲区。触发词：多角度/追问/不同立场/多视角。

#### roundtable — 圆桌辩论

结构化圆桌讨论，3-5 位真实历史/当代人物就任意话题辩证对话，主持人引导真理追寻。触发词：辩论/圆桌/roundtable/多角度/多方对话。

### 多智能体协作（🤝 Multi-Agent）

#### kanban-orchestrator — 看板编排器

任务分解、路由与自愈。死胡同注册避免重复失败，停滞检测自动重组，依赖门控确保顺序。编排器只做分解和路由，不亲自执行。

#### kanban-worker — 看板工人

工作器规范与边缘案例手册。结构化交棒格式、方法级死胡同记录、重试避障。与 orchestrator 联动。

### 研究搜索（🔍 Research）

#### github-ai-analysis — GitHub 分析

AI/ML 开源项目深度分析：架构解构、创新评估、Hermes 相关性、benchmark、行动建议。触发词：分析这个项目/github analysis/评估仓库。

#### sirchmunk-intel-mac — Sirchmunk

在 Intel Mac (x86_64) 上安装运行 Sirchmunk 全文搜索。覆盖 kreuzberg stub 绕行、rga 安装和环境配置。

### DevOps

#### cron-management — Cron 管理

Hermes cron job 调度策略、限流规避、交付可靠性、常见故障模式。在创建/调试 cron job 或交付失败时加载。

### 开发工具（🛠️ Dev Tools）

#### agent-memory-systems — 记忆系统

评估、比较和选择 AI Agent 记忆方案的知识库。触发词：agent memory/mem0/memos/memory comparison。

#### hermes-codebase — Hermes 源码

修改、扩展或调试 Hermes Agent 代码库。覆盖 config/providers/prompts/tools/内部架构。触发词：改Hermes/修改agent/hermes源码。

#### python-dependency-resolution — Pip 依赖

解决复杂 pip 依赖冲突。isolation→version-match→unblock install chains。触发词：pip conflict/dependency/pip install failed。

#### goodday-trading-systems — 交易系统

分析、修改或扩展 Goodday 量化交易系统（MT4/MT5 EA、TCN+PPO、Kronos）。触发词：goodday/trading/TCN/PPO/MT5/Kronos。

### 效率工具（⚡ Productivity）

#### notebooklm — NotebookLM

Google NotebookLM 交互管理：login/list/create/chat/source 管理。触发词：NotebookLM/notebook/笔记问答/deep reading。

#### wechat-article-saver — 公众号保存

微信公众平台文章保存为 Markdown，支持 NotebookLM 深度阅读。触发词：公众号/mp.weixin.qq.com。

#### bilibili-search — B站搜索

Bilibili 搜索 + 字幕提取。零认证公开 API 搜索，登录态字幕抓取。触发词：B站/bilibili/哔哩哔哩/b站搜索。

### 旅行（✈️ Travel）

#### japan-travel-assistant — 日本旅行助手

中日双语翻译桥、东京交通导航、菜单标识翻译、带娃出行攻略、紧急联络。触发词：日本/东京/日语/旅行/Japan。

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
