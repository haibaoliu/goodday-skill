---
name: brain-maintain
description: Use when the brain needs health checks, back-link audits, orphan detection, or pattern synthesis. Run periodically or after heavy ingestion sessions.
version: 2.0.0
author: Hermes Brain System
license: MIT
metadata:
  hermes:
    tags: [brain, maintenance, health-check, back-link]
    related_skills: [brain-ingest, brain-query, book-mirror]
---

# Brain Maintain — 脑页健康维护

## Overview

保持 Hermes Brain 的数据质量。检测孤岛页面、断裂的 back-link、过期内容，
以及从多篇反思中合成跨会话模式。

**v2.0 架构**：确定性数据收集由 `scripts/brain_health.py` 完成（JSON 报告），
LLM 只负责语义决策——哪些孤岛要链接/删除、哪些候选构成真实模式、如何修复。

## When to Use

- 用户问 "脑健康吗？"、"检查一下脑"
- 刚完成大量摄入后（3+ 新页面）
- Book Mirror 运行前做一次健康检查
- 定期（建议每周一次）

## Phase 1: Run Health Scanner (Deterministic)

```bash
python ${SKILL_DIR}/scripts/brain_health.py --brain-dir ~/.hermes/brain
```

This produces a JSON report with these sections:
- `stats` — total pages, breakdown by category
- `orphans` — pages not referenced by any other page (slug, path, category, age)
- `backlink_issues` — recent pages whose mentioned entities lack a back-link
- `frontmatter_issues` — pages with missing/incomplete YAML frontmatter
- `stale_content` — pattern/concept pages untouched for >90 days
- `pattern_candidates` — themes with ≥3 reflection occurrences across ≥7 days
- `summary` — health_score ("healthy" | "needs_attention")

Options:
- `--summary` — print summary only
- `--stale-days 60` — custom stale threshold
- `--recent-days 14` — custom recent window for back-link checks

## Phase 2: LLM Decision (Semantic)

Read the JSON output from Phase 1. For each section, make decisions:

### Orphans
For each orphan:
- **链接**：哪些已有页面应该引用它？补充 back-link。
- **删除**：如果内容已无用，直接删掉 `.md` 文件。
- **保留**：如果是结构页（如 category index），标记为 intentional。

### Back-link Issues
For each `backlink_issues` entry:
- 在 `target` 页面上添加对 `source_slug` 的引用（Timeline 或相关段落）。

### Frontmatter Issues
For each `frontmatter_issues` entry:
- `missing_frontmatter` → 添加完整的 `---` YAML 块
- `incomplete_frontmatter` → 补全 missing_fields

### Stale Content
For each stale pattern/concept:
- 内容是否仍然准确？→ 更新 date 字段 refresh
- 内容已过时？→ 归档或重写
- 标记建议，询问用户

### Pattern Candidates
For `pattern_candidates` with count >= 3 and span >= 7 days:
1. 读取所有源反思（`sources[].path`）
2. 提取：触发情境、用户反应、用户原话、日期
3. 判断是否构成真实模式（非偶然、有共同触发条件）
4. 如构成 → 写入模式页，back-link 所有源
5. 如不构成 → 记录跳过原因

## 模式合成输出模板

```markdown
---
title: "模式名称"
type: pattern
date: YYYY-MM-DD
tags: [pattern, ...]
links:
  - ../reflections/source-1.md
  - ../reflections/source-2.md
---

# 模式名称

## 模式描述
[一句话概括]

## 证据链
- **YYYY-MM-DD** | 简述 → [reflection](reflections/source-N.md)

## 用户原话
> "..."

## 可能的干预
- ...
```

## Common Pitfalls

1. **不跑脚本就决策**。Phase 1 必须跑 `brain_health.py`，不要手动 grep/find。
2. **孤岛不修**。发现孤岛后要么链接它，要么删掉它。孤岛 = 白存。
3. **Back-link 单向**。A 提了 B，B 没回链 A → 断链。
4. **模式合成太早**。脚本已做了 ≥3 次 + ≥7 天的过滤，但仍需判断是否有共同触发条件。
5. **只检查不修复**。健康检查的价值在执行修复。

## Verification Checklist

- [ ] `brain_health.py` 已运行且输出已读取
- [ ] 孤岛页面已处理（链接或删除）
- [ ] 所有 back-link issues 已补全
- [ ] Frontmatter issues 已修复
- [ ] Stale content 已审视
- [ ] ≥3 次出现的 pattern candidates 已评估/合成
- [ ] 健康报告已向用户展示
