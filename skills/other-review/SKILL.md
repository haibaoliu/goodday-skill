---
name: other-review
description: "他者审查 — 用独立子 Agent 审查主 Agent 的工作成果，拒绝自圆其说。v2.0 支持多模型共识审查。"
version: 2.0.0
author: Hermes (user-driven)
category: software-development
tags: [review, quality, delegation, adversarial, meta-cognition, multi-model]
---

# 他者审查 (Other-Review) v2.0

**核心原则：自查是废话，自圆其说等于自欺欺人。真正有效的审查必须由他者完成——独立视角、不同立场、不参与创作。**

v2.0 新增：多模型共识审查——用不同模型独立审查，取并集 + 标注共识。不同训练数据 = 不同盲区，单一模型的审查和自查一样有盲区。

## 两种模式

### 模式 A：单模型审查（默认，v1.0）
启动 1 个审查子 Agent，用当前模型。

### 模式 B：多模型共识审查（v2.0 新增）
启动 N 个审查子 Agent，分别用不同模型，各自独立审查，最后合并：
- **共识问题**：≥2 个模型都发现 → 严重度最高
- **单一模型问题**：仅 1 个模型发现 → 不丢弃，标注来源

```
用户触发："审查：all，strict，多模型"
                ↓
      delegate_task(batch):
      ├─ 审查员 A: 当前模型（deepseek）
      ├─ 审查员 B: google/gemini
      └─ 审查员 C: alibaba/qwen-vl-max (或 anthropic/claude)
                ↓
      合并报告：
      🔴 共识问题（A+B+C 都发现）→ 3 个
      🟡 A+B 共识（未包含 C）→ 1 个
      🟢 仅 A 发现 → 2 个（不丢弃！盲区可能藏着关键问题）
```

## 适用场景

- 代码写完后的代码审查
- 方案设计后的逻辑漏洞扫描
- 安全决策的二审
- **高风险场景**（安全、金融、生产部署）→ 建议使用多模型共识模式

## 使用方式

```
# 单模型（默认）
审查一下：代码质量 + 安全性，strict

# 多模型共识
审查：all，adversarial，多模型

# 多模型 + 指定模型
审查：logic，normal，多模型(gemini+claude)
```

## 审查维度

| 维度 | 说明 |
|------|------|
| `code` | 代码质量、可读性、边界条件、类型安全 |
| `security` | 安全漏洞、注入风险、密钥暴露、输入验证 |
| `logic` | 逻辑完整性、推理链断裂、隐藏假设 |
| `completeness` | 遗漏的需求/步骤、未覆盖的边界情况 |
| `correctness` | 事实准确性、幻觉、过期信息 |
| `design` | 架构/设计合理性、耦合/内聚、可扩展性 |
| `all` | 全面审查（上述所有） |

## 审查严格度

| 级别 | 说明 |
|------|------|
| `gentle` | 指出明显问题，不吹毛求疵 |
| `normal` | 标准审查 |
| `strict` | 严格审查，任何小问题都不放过 |
| `adversarial` | 敌对审查——假设你的产出是错的，全力证明它 |

## 审查员系统 Prompt

```
你是一个挑剔的 QA 审查员。你的唯一职责是找问题。
你不是来帮忙的——你是来挑刺的。
你不对产出物负责——你只对发现漏洞负责。

规则：
1. 永远假设被审查的产出有问题，你的任务是找到它
2. 不给出"总体不错"的评价——只列出问题
3. 每个问题必须具体：哪里有问题 + 为什么是问题 + 严重程度(🔴高/🟡中/🟢低)
4. 如果你找不到问题，说明你看得不够仔细
5. 不参与创作，不给出修改建议（除非明确要求）

审查维度：{dimensions}
严格程度：{strictness}
```

## 多模型配置

### 核心原则：跨 Provider > 同 Provider 不同模型

不同训练数据 = 不同盲区。同一个 provider 的不同模型（如 deepseek-v4-pro vs deepseek-chat）共享底层训练分布，盲区高度重叠。跨 provider（如 DeepSeek vs Qwen vs Gemini）才能获得真正独立的审查视角。

### 模型可用性探测（审查前必做）

在启动多模型审查前，先探测实际可用的模型：

1. 读取 `~/.hermes/config.yaml`：
   - `model.provider` → 主模型 provider
   - `auxiliary.*.provider` → 辅助模型 providers
2. 读取 `~/.hermes/.env`（或对应 profile 的 .env）：
   - 检查 `DASHSCOPE_API_KEY`、`GOOGLE_API_KEY`、`ANTHROPIC_API_KEY` 等
3. 汇总可用 provider 列表

### 审查员分级策略

根据探测结果，自动选择策略：

**Tier 3（理想）— 3 个不同 provider**：
```
审查员 A: 当前模型 (如 deepseek-v4-pro)
审查员 B: 不同 provider (如 alibaba/qwen-max，或用 google/gemini)
审查员 C: 第三个不同 provider (如 anthropic/claude)
```
3/3 共识 → 极高可信度。

**Tier 2（可行）— 2 个不同 provider**：
```
审查员 A: 当前模型
审查员 B: 不同 provider 的模型
```
2/2 共识 → 高可信度。单一模型发现 → 标注「未共识，但来自不同训练分布，不应忽略」。

**Tier 1（最低）— 仅 1 个 provider**：
```
审查员 A: 当前模型，temperature=0.3
审查员 B: 同 provider 不同模型（如 deepseek-chat），temperature=0.7
```
⚠️ **显式标注**：「同 provider 审查——盲区高度重叠，可信度有限。以下问题用作参考而非裁决。」

**Tier 0（退化）— 无法启动多模型**：
退化为单模型审查 + 明确告知用户：「当前系统仅有 1 个可用模型，无法执行多模型共识审查。改为单模型模式，结果仅供自我检查。」

### 模型选择优先级

同一 provider 下选择模型时：
1. 优先选**不同架构系列**（如 deepseek-v4 vs deepseek-chat，差异 > v4 vs v4 不同 temperature）
2. 优先选**不同参数量级**（如 qwen-max vs qwen-plus，差异更明显）
3. 同模型不同 temperature 是最后手段

## 执行流程

### 第〇步：模型探测（新增）
```
1. read_file ~/.hermes/config.yaml → 提取 model.provider + auxiliary providers
2. read_file ~/.hermes/.env → 扫描 *_API_KEY 环境变量
3. 汇总可用 provider → 确定 Tier (3/2/1/0)
4. 告知用户当前 Tier 和对应的可信度
```

### 单模型流程
```
1. 我完成主任务
2. delegate_task(goal="审查...", context=产出物)
3. 审查报告返回 → 我修正 → 返回最终结果
```

### 多模型共识流程
```
0. 模型探测 → 确定 Tier (3/2/1)
1. delegate_task(tasks=[
     {goal: 审查, model: 当前模型},
     {goal: 审查, model: 跨provider模型B},
     {goal: 审查, model: 跨provider模型C}  // Tier 3 才有
   ])
2. 合并 N 份报告：
   - 提取所有问题 → 按描述去重归类
   - 标注：共识(≥2模型) vs 单一模型
   - 标注：跨 provider 发现 vs 同 provider 发现
   - 排序：跨provider共识 → 共识 → 严重度高 → 严重度低
3. 我根据合并报告修正 → 返回最终结果
```

## 结果格式

```
🔍 他者审查报告（多模型共识 | 严格程度: strict）

🔴 共识问题（3/3 模型一致）
1. [安全性] XSS 漏洞 - 第 47 行用户输入未转义
2. [逻辑] 密码重置流程缺少邮件验证步骤
3. [完整性] API 错误处理缺少 429 限流响应

🟡 部分共识（2/3 模型）
4. [设计] UserService 耦合度过高，建议拆分 (gemini+claude)

🟢 单一模型发现（仍值得关注）
5. [正确性] 第 12 行时区处理可能出错 (仅 claude)
6. [代码] 第 89 行变量命名可读性差 (仅 gemini)

总计: 6 个问题 | 共识: 3 | 部分共识: 1 | 单一: 2
```

## 关键约束

- **审查员不写代码**——只审查，不创作
- **不同模型 = 不同盲区**——单一模型审查和自查一样有盲区
- **单一模型问题不丢弃**——盲区里的问题可能最关键
- **多模型模式下，审查员必须用完全不同模型**——同模型跑 3 次 = 自圆其说 × 3
- **审查结果优先展示**——修正前的问题先让用户看到
