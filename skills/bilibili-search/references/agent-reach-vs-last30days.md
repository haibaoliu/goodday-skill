# Agent-Reach vs last30days-skill — 深度对比

日期：2026-06-08 | 代码已 clone 到 `~/Documents/hermes-output/`

## 项目概况

| | last30days-skill | Agent-Reach |
|---|---|---|
| **GitHub** | mvanhorn/last30days-skill | Panniantong/Agent-Reach |
| **Stars** | 31,293 (2026.01 创建) | 23,219 (2026.02 创建) |
| **代码规模** | 46,625 行 / 160 py / 92 测试 | 5,485 行 / 38 py / 10 测试 |
| **Python** | 3.12+ | 3.10+ |
| **定位** | 研究引擎 + 自动综述 | 安装器 + 工具路由器 |

## 架构差异

### last30days-skill — 研究引擎

```
用户输入 → Planner(LLM) → 多源并行抓取(ThreadPool)
         → 去重(URL+语义) → 相关度打分(token overlap)
         → RRF融合(加权倒数排名) → 重排序(LLM意图感知)
         → 聚类(实体MMR) → 合成输出
```

**核心文件**：
- `SKILL.md` — 1709 行"指令合同"，防止 LLM 即兴发挥
- `pipeline.py` — 1138 行编排引擎
- `rerank.py` — LLM 驱动的重排序，意图感知评分
- `cluster.py` — 实体重叠聚类 + MMR 多样性
- `fusion.py` — RRF 跨源融合 + per-author cap
- `providers.py` — 多 LLM 后端（Gemini/OpenAI/xAI/OpenRouter）

**覆盖源**：Reddit(5种方法)、X(4种)、YouTube、TikTok、Instagram、HN、Polymarket、GitHub、Bluesky、TruthSocial、Threads、Digg、Perplexity、小红书

**Hermes 集成**：有 `HERMES_SETUP.md`，`hermes skills install mvanhorn/last30days-skill --force`

### Agent-Reach — 工具应用商店

**核心哲学**："NOT a wrapper — agents call upstream tools directly"

```
SKILL.md路由表 → 识别意图 → 加载 references/*.md → Agent 调用上游 CLI
                        ↑
                 agent-reach doctor 检查可用性
```

**核心文件**：
- `core.py` — 42 行，仅 doctor 和状态检查
- `doctor.py` — 108 行，检查所有 channel 可用性
- `channels/*.py` — 每个平台一个文件，继承 `BaseChannel`
- `integrations/mcp_server.py` — MCP 集成
- `skill/SKILL.md` — 106 行路由表

**16 个 Channel**：

| Tier | 渠道 | 上游工具 | 认证要求 |
|------|------|---------|---------|
| 0 | Web | jina.ai/curl | 无 |
| 0 | GitHub | gh CLI | 需配置 |
| 0 | V2EX | curl API | 无 |
| 0 | RSS | curl | 无 |
| 0 | Exa Search | mcporter | 需 key |
| 1 | Twitter | twitter-cli | AUTH_TOKEN |
| 1 | Reddit | rdt CLI | 需安装 |
| 1 | YouTube | yt-dlp | 无 |
| 1 | B站 | yt-dlp + API | 无(搜索)/需登录(字幕) |
| 1 | 微博 | mcporter + mcp-server-weibo | 需安装 |
| 1 | 小红书 | xhs-cli | 需登录(Cookie) |
| 2 | 抖音 | mcporter + douyin-mcp-server | 需安装+MCP服务 |
| 2 | LinkedIn | voyager-cli | 需安装 |
| 2 | 微信 | 公众号 API | 需配置 |
| 2 | 小宇宙 | 转录脚本 | 需安装 |
| 2 | 雪球 | API | 需配置 |

## 关键差异

| 维度 | last30days-skill | Agent-Reach |
|------|-----------------|-------------|
| **答案形式** | 结构化综述报告 | 原始数据 |
| **LLM 依赖** | 重度 | 零 |
| **中文平台** | 小红书(API only) | 小红书+抖音+B站+微博+V2EX+雪球+微信+小宇宙 |
| **可组合性** | 低(黑盒流水线) | 高(每工具独立调用) |
| **适合场景** | "X 最近 30 天怎么讨论 Y" | "帮我在小红书搜 Z" |
| **token 效率** | LLM 压缩过 | 上游工具决定 |

## 互补性

两者不是竞争，是上下游：

```
Agent-Reach（装工具）→ last30days-skill（用工具做研究）
         ↓                          ↓
   提供数据管道              提供研究脑
```

## 对 Hermes 的建议

### 短期（已做）
- ✅ B站搜索 — 用自建 `bilibili-search` skill，比 Agent-Reach 更直接

### 中期
- pip install agent-reach → 获取 twitter-cli、小红书-cli 等工具
- 但每个渠道仍需单独安装上游工具+认证

### 长期
- 自建缝合层：cron job 调用多源工具 → last30days 式流水线 → 自动周报/日报
