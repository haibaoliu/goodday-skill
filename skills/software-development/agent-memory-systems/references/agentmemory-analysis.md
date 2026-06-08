# agentmemory — 记忆服务器深度分析

> `rohitg00/agentmemory` ⭐21.8k | TypeScript 37K行 | Apache 2.0 | 2026-06-08 调研

## 概览

独立运行的记忆服务器（`npx @agentmemory/agentmemory`），所有 AI Agent 通过 MCP / REST / Hook 共享同一份记忆。底层基于 iii-engine（Rust WebSocket 引擎），存储使用 SQLite。

### 关键数据

| 指标 | 数值 |
|------|------|
| LongMemEval-S R@5 | 95.2% (ICLR 2025 基准) |
| Token 节省 (vs 全量) | 92% (22K → 1.9K) |
| 检索延迟 p50 | 14ms |
| MCP 工具 | 53 个 |
| REST 端点 | 128 个 |
| Hook 类型 | 12 种 |
| 测试 | 950+ |
| 外部依赖 | 0 (SQLite 文件存储) |
| 内存分层 | Working → Episodic → Semantic → Procedural |

## 核心记忆流水线

```
PostToolUse hook → SHA-256 去重(5min窗口) → 隐私过滤(剥离API key)
  → 存储原始观察 → LLM压缩为 facts/concepts/narrative
  → 向量嵌入(6 providers + 本地免费) → BM25 + 向量索引

SessionEnd → 会话摘要 → 知识图谱提取(可选) → Slot反思(可选)

SessionStart → 加载project profile → Hybrid搜索(BM25+向量+知识图谱, RRF融合)
  → Token预算控制(默认2000 tokens) → 注入会话上下文
```

## 4 层记忆巩固

| 层 | 内容 | 类比 |
|----|------|------|
| Working | 原始工具使用记录 | 短期记忆 |
| Episodic | 压缩的会话摘要 | "发生了什么" |
| Semantic | 提取的事实和模式 | "我知道什么" |
| Procedural | 工作流和决策模式 | "怎么做" |

记忆按 Ebbinghaus 遗忘曲线衰减，频繁访问增强，陈旧自动驱逐，矛盾检测并解决。

## 搜索架构

三路检索，RRF 融合 (k=60)，每 session 最多 3 条结果：

| 流 | 机制 | 条件 |
|----|------|------|
| BM25 | 词干匹配 + 同义词扩展 | 始终启用 |
| Vector | 余弦相似度 over dense embeddings | embedding provider 配置时 |
| Graph | 知识图谱遍历 via 实体匹配 | 查询中检测到实体时 |

CJK 支持：可选 `@node-rs/jieba` / `tiny-segmenter` 分词。

## 核心差异化 vs 竞争对手

| 能力 | agentmemory | mem0 (58K⭐) | Letta/MemGPT (23K⭐) |
|------|-----------|------------|-------------------|
| 自动捕获 | ✅ 12 hooks | ❌ 手动 add() | Agent 自编辑 |
| 搜索 | BM25+向量+图 RRF | 向量+图 | 向量(archival) |
| 记忆版本控制 | ✅ 版本+超集+回滚 | ❌ | ❌ |
| 隐私过滤 | ✅ 自动剥离 secrets | ❌ | ❌ |
| 跨Agent共享 | ✅ 同一服务器 | ❌ | ❌ |
| 部署 | 本地 SQLite, 零DB | 需外部DB | Agent runtime |

## Hermes 集成

### 方式1: MCP 服务器（零代码）

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  agentmemory:
    command: npx
    args: ["-y", "@agentmemory/mcp"]
memory:
  provider: agentmemory
```

### 方式2: 原生 Python 插件（深集成）

`integrations/hermes/` → `~/.hermes/plugins/agentmemory/`，提供 6 个生命周期钩子：

- `prefetch()` — LLM 调用前注入相关记忆
- `sync_turn()` — 每轮对话自动捕获
- `on_session_end()` — 会话结束标记
- `on_pre_compress()` — 上下文压缩前重新注入
- `on_memory_write()` — MEMORY.md 写入同步
- `system_prompt_block()` — 会话开始注入 project profile

## 对 Hermes 的启示

1. **4 层记忆巩固** → 可引入 MemOS，替代扁平的 MEMORY.md
2. **BM25 + 向量 RRF 融合** → 优于纯 FTS5，HerMS 的 session_search 可借鉴
3. **自动捕获 hooks** → 12 种 hook 类型可作为 Hermes gateway hooks 的参考设计
4. **隐私过滤** → Hermes 的 memory tool 在写入前应自动剥离 secrets
5. **Crystallize 模式** → 将完成的 action chain 压缩为 Crystal（narrative + keyOutcomes + filesAffected + lessons），类似 Hermes 的 session 摘要但更结构化

## 限制

- 依赖 iii-engine 原生二进制（Rust），x86_64 Mac 已验证可用（29MB）
- 引导成本：LLM 压缩需要 API 调用（默认用 OpenAI，可配置 local/minimax/openrouter）
- Windows 支持不完整（需 WSL2）
- 版本固定 iii-engine v0.11.2（新版 sandbox 模型未适配）
- npm 安装包较大，中国网络需镜像源

## 结论

目前 Agent 记忆领域最工程化的产品。22k stars 反映社区共识。对 Hermes 最大的价值在于：4 层记忆架构可作为 MemOS 演进参考，自动捕获 hooks 可作为 gateway 增强方向。已在本机（Intel Mac x86_64）构建成功并验证健康检查通过。
