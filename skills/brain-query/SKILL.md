---
name: brain-query
description: Use when searching or retrieving information from the Hermes brain (~/.hermes/brain/). Search by keyword, entity, date, or semantic similarity. Detect contradictions across pages.
version: 1.0.0
author: Hermes Brain System
license: MIT
metadata:
  hermes:
    tags: [brain, search, retrieval, contradiction-detection]
    related_skills: [brain-ingest, brain-maintain, book-mirror]
---

# Brain Query — 脑页检索与矛盾检测

## Overview

从 Hermes Brain 中检索结构化脑页。不仅是关键词搜索——支持按类型、日期、实体过滤，并检测跨页面的矛盾声明。

## When to Use

- 用户问 "我们聊过关于 X 的事吗？"
- Book Mirror 收集上下文时需要检索相关脑页
- 做决定前需要回顾过去的反思
- 检查脑页之间是否有矛盾的事实声明

## 检索策略

### 策略 1：关键词搜索（最快）

```bash
# 搜索所有脑页中的关键词
grep -rl "<keyword>" ~/.hermes/brain/ --include="*.md" | head -20

# 搜索特定目录
grep -rl "<keyword>" ~/.hermes/brain/reflections/ --include="*.md"
```

### 策略 2：按类型 + 日期过滤

```bash
# 列出最近 N 天的反思
find ~/.hermes/brain/reflections/ -name "*.md" -mtime -14 | sort

# 列出所有人
ls ~/.hermes/brain/people/

# 列出所有模式
ls ~/.hermes/brain/patterns/
```

### 策略 3：全文读取 + 智能筛选

当关键词搜索不够时：

1. 用 `search_files` 找到候选脑页
2. 用 `read_file` 读取每个候选的 frontmatter 和关键段落
3. 根据用户问题的语义匹配度排序

### 策略 4：向量检索（通过 MemOS）

当需要语义相似度时，走 MemOS：

```
memos_search(query="用户的自然语言问题", maxResults=10)
```

MemOS 返回的 trace 中可能包含脑页引用。

## 矛盾检测

当检索结果中多个页面针对同一事实有不同声明时，检测矛盾：

### 检测流程

```markdown
1. 提取所有关于同一主题的 Facts 表格行
2. 比较：声明 + 持有者 + 置信度 + 日期
3. 如果两个声明冲突：
   - 记录双方声明和来源
   - 判断哪方更可信（按 Source 优先级：用户直接声明 > 已编译事实 > 外部来源）
   - 向用户报告矛盾，不私自裁决
```

### Source 优先级

1. 用户直接声明（最高权威）
2. 已编译的脑页事实（跨会话合成）
3. 外部来源（API、网页搜索——最低）

## Book Mirror 上下文收集

当 book-mirror 需要上下文时，用以下命令：

```bash
# 1. 读取 USER.md 和 SOUL.md
cat ~/.hermes/brain/USER.md
cat ~/.hermes/brain/SOUL.md

# 2. 最近 14 天反思
find ~/.hermes/brain/reflections/ -name "*.md" -mtime -14 | sort | while read f; do
  echo "---"
  cat "$f"
done

# 3. 主题相关页面（用书籍主题词搜）
grep -rl "<book_theme_keyword>" ~/.hermes/brain/ --include="*.md" | while read f; do
  echo "---"
  head -50 "$f"
done

# 4. 所有人物页
for f in ~/.hermes/brain/people/*.md; do
  echo "---"
  cat "$f"
done
```

将以上输出整合成一个 `context.md` 文件，供 book-mirror 子 Agent 使用。

## 输出格式

检索结果按以下格式呈现：

```markdown
## 检索结果：<查询词>

### 匹配的脑页
| 标题 | 类型 | 日期 | 路径 | 匹配度 |
|------|------|------|------|--------|
| ... | ... | ... | ... | high/medium/low |

### 关键发现
- 发现 1（带出处）
- 发现 2（带出处）

### 矛盾（如果有）
| 声明 A | 来源 A | 声明 B | 来源 B | 判断 |
|--------|--------|--------|--------|------|
```

## Common Pitfalls

1. **只搜不读**。grep 找到文件后必须 read_file 确认内容匹配，标题可能误导。
2. **忽略时间衰减**。越新的页面通常越相关，排序时加权。
3. **矛盾不报告**。发现矛盾是 brain-query 的核心价值——不报告 = 脑白存了。
4. **上下文收集不全**。Book Mirror 需要密集上下文——USER.md + 14天反思 + 主题页面 + 人物页，缺一不可。

## Verification Checklist

- [ ] 检索覆盖了文件系统和 MemOS（如果适用）
- [ ] 结果按相关度排序
- [ ] 矛盾已被检测并报告
- [ ] 每条关键发现带出处（页面路径 + 日期）
- [ ] Book Mirror 上下文收集包含了所有 4 类数据
