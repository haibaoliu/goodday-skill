---
name: brain-query
description: Use when searching or retrieving information from the Hermes brain (~/.hermes/brain/). Search by keyword, entity, date, or semantic similarity. Detect contradictions across pages.
version: 2.0.0
author: Hermes Brain System
license: MIT
metadata:
  hermes:
    tags: [brain, search, retrieval, contradiction-detection]
    related_skills: [brain-ingest, brain-maintain, book-mirror]
---

# Brain Query — 脑页检索与矛盾检测

## Overview

从 Hermes Brain 中检索结构化脑页。支持关键词搜索、类型/日期过滤、事实表提取、
候选矛盾对检测、以及 Book Mirror 上下文收集。

**v2.0 架构**：确定性搜索、过滤、Facts 提取和候选矛盾检测由
`scripts/brain_query.py` 完成。LLM 只负责语义判断——相关性排序、矛盾真伪判定、
结果摘要。

## When to Use

- 用户问 "我们聊过关于 X 的事吗？"
- Book Mirror 收集上下文时需要检索相关脑页
- 做决定前需要回顾过去的反思
- 检查脑页之间是否有矛盾的事实声明

## Subcommands

### 1. Keyword Search

```bash
python ${SKILL_DIR}/scripts/brain_query.py search "<keyword>" [--type people|reflections|patterns|...] [--recent-days 14]
```

Returns JSON with `total_matches` and `results[]` — each result has path, category, title, type, date, tags, and `match_lines` (top 5 matching lines with context).

### 2. Contradiction Detection

```bash
python ${SKILL_DIR}/scripts/brain_query.py contradictions
```

Returns JSON with `candidates[]` — each candidate has a `key`, grouped `values[]`, and `conflict_likelihood` (high/medium/low). LLM reads the actual sources and judges if it's a real contradiction.

### 3. Book Mirror Context Collection

```bash
python ${SKILL_DIR}/scripts/brain_query.py context [--keyword "theme"] [--recent-days 14]
```

Returns a complete context bundle: `user`, `soul`, `recent_reflections[]`, `related_pages[]`, `people[]`. All content truncated to reasonable sizes. Use for Book Mirror subagent input.

### 4. Semantic Search (MemOS fallback)

When keyword search doesn't find enough, use:

```
memos_search(query="用户的自然语言问题", maxResults=10)
```

MemOS returns traces that may contain brain page references.

## Usage Workflow

### For search queries

1. Run `brain_query.py search "<keyword>"`
2. Read the JSON `results[]` — each result includes `match_lines` for context
3. If matches ≥ 5: sort by relevance (date-weighted, title match bonus)
4. If matches = 0: fall back to MemOS or broader grep
5. Present findings with paths and dates

### For contradiction detection

1. Run `brain_query.py contradictions`
2. For each candidate with `conflict_likelihood: high` or `medium`:
   a. Read the source pages for both sides
   b. Judge: same subject? actually conflicting? or context explains it?
3. Report real contradictions; skip false positives
4. **Source priority**: 用户直接声明 > 已编译脑页 > 外部来源

### For Book Mirror context

1. Run `brain_query.py context --keyword "<book_theme>" --recent-days 14`
2. The JSON output is already structured — pass to Book Mirror subagent as-is
3. No need to manually cat/find/grep individual files

## Output Format

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

1. **不跑脚本就搜**。Phase 1 必须跑 `brain_query.py`，不要手动 grep/find。
2. **忽略时间衰减**。越新的页面通常越相关，排序时加权。
3. **矛盾不报告**。发现矛盾是 brain-query 的核心价值——不报告 = 脑白存了。
4. **上下文收集不全**。Book Mirror 用 `brain_query.py context` 一键收集，不要手动拼。

## Verification Checklist

- [ ] `brain_query.py` 已运行（search / contradictions / context）
- [ ] 结果按相关度排序
- [ ] 矛盾已被检测并报告
- [ ] 每条关键发现带出处（页面路径 + 日期）
- [ ] Book Mirror 上下文收集包含了所有 4 类数据
