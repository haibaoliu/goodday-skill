---
name: cron-management
description: Hermes cron job 管理：调度策略、限流规避、交付可靠性、常见故障模式。当创建/调试/修改 cron job、cron 交付失败、或需要优化 cron 调度时加载。
version: 1.0.0
tags: [cron, scheduling, reliability, delivery, operations]
---

# Cron Job Management

## 调度策略

### 错峰原则

同一平台多个 cron job 不要同时触发 → 会触发交付限流。

| 平台 | 建议间隔 | 说明 |
|------|---------|------|
| WeChat (iLink) | **≥ 1 小时** | iLink rate limit 窗口分钟级，Hermes 重试（4次×3s=12s）远不足以穿越，5分钟间隔实测仍被拒（ret=-2） |
| 通用 | ≥ 2 分钟 | 安全余量 |

示例（WeChat 平台）：
```
Job A: 0 9 * * 1    (周一 9:00)
Job B: 0 10 * * 1   (周一 10:00) — 整 1 小时间隔
Job C: 0 11 * * 1   (周一 11:00) — 如果未来增加第三个
```

详见 `references/ilink-rate-limiting.md` — iLink 限流机制源码级分析。

### 天级错峰

如果多个 daily cron，按内容类型分散：
- 报告类：早上 9:00-9:30（用户醒来看到）
- 监控类：整点（与系统节奏对齐）
- 数据采集：避开整点（减少与其他系统的碰撞）

## 交付可靠性

### 常见故障

| 症状 | 根因 | 修复 |
|------|------|------|
| `last_status=ok` 但用户没收到 | delivery error（如 rate limited） | 错峰 + 检查 `last_delivery_error` |
| `Script not found` | 脚本路径不存在，但 job 仍正常完成 | 创建缺失脚本 或 让 prompt 自给自足 |
| cron 环境下 memory 工具不可用 | cron session toolset 受限 | 将待保存内容写入报告文件，手动处理 |
| **单条 cron 也被限流** | 长消息分 chunk 过多，自触发 iLink 限流 | 增加 `WEIXIN_SEND_CHUNK_DELAY_SECONDS` 或精简输出 |

### 主动巡检（周一/报告日必做）

当与用户对话且当天是周一（或任何 cron 报告预定日）时，**主动**检查：

```python
cronjob(action='list')  # 看 last_delivery_error 是否非空
```

如果 `last_delivery_error` 非空，**在用户抱怨之前**触发重跑：

```python
cronjob(action='run', job_id='<job_id>')
```

不要等用户说「周报没收到」——主动补发。

### 诊断命令

```bash
# 查看所有 cron job 状态
hermes cron list  # 或在对话中用 cronjob(action='list')

# 重点看 last_status 和 last_delivery_error
```

### 手动补发

如果 cron 执行成功但交付失败（`last_delivery_error` 非空），**首选触发重跑**：

```python
cronjob(action='run', job_id='<job_id>')
```

这会重新执行 job 并通过 gateway 自动投递，比手动提取内容+发送更可靠。

备选方案（重跑不可用时）：
1. 从 session_search 找到 cron session（source=cron）
2. 提取报告内容
3. 直接发到对应平台

## Cron 环境限制

cron session 的工具集可能比交互式会话少，注意：
- `memory` 工具可能不可用 → 关键发现写报告文件
- `skill_manage` 可能不可用 → 建议写进报告等人工处理
- toolset 由 job 创建时的 `enabled_toolsets` 决定

## Job 设计原则

1. **Prompt 自给自足**：cron job 不能问问题，prompt 必须包含完整指令
2. **容错脚本**：`script` 挂了，prompt 应该能独立完成任务
3. **[SILENT] 约定**：没有新内容时返回 `[SILENT]` 阻止空交付
4. **去重意识**：数据处理类 job 要先查已有数据，避免重复入库

## UNCHANGED 偏见（Token 节省模式）

大规模周期性输出（GitHub trending、RSS 摘要、日报）中，大部分内容每周不变。
不要每次都让 LLM 重新生成——用哈希比对跳过未变化项。

### 实现方式

**方式 1：脚本内置（推荐）**

在数据采集脚本中直接加哈希比对，输出带状态标记的 JSON：

```python
# 输出格式
{
  "stats": {"new": 3, "changed": 1, "unchanged": 14, "dropped": 2},
  "new": [...],       # 新上榜 → LLM 生成摘要
  "changed": [...],   # 数据变了 → LLM 更新摘要
  "unchanged": [...], # 完全相同 → 复用 _prev_summary，不重新生成！
  "dropped": [...]    # 上周有本周没 → 一句话带过
}
```

参考：`fetch_trending.py`（~/.hermes/scripts/）。

**方式 2：通用过滤器**

```bash
your_script.py | python unchanged_filter.py \
    --state ~/.hermes/cron/your_state.json \
    --id-field full_name \
    --hash-fields description stars
```

参考：`unchanged_filter.py`（~/.hermes/profiles/chuck/scripts/）。

### Cron Prompt 写法

在 prompt 中明确告诉 agent：

```
- `unchanged` — 和上周完全相同，已有 `_prev_summary`，直接用！！不要重新生成！
- 只有 `new` 和 `changed` 的 item 需要 LLM 生成新内容。
```

### 效果

典型周报型 cron job：25 个 item 中 15-20 个 UNCHANGED → 节省 60-80% token。
