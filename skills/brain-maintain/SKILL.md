---
name: brain-maintain
description: Use when the brain needs health checks, back-link audits, orphan detection, or pattern synthesis. Run periodically or after heavy ingestion sessions.
version: 1.0.0
author: Hermes Brain System
license: MIT
metadata:
  hermes:
    tags: [brain, maintenance, health-check, back-link]
    related_skills: [brain-ingest, brain-query, book-mirror]
---

# Brain Maintain — 脑页健康维护

## Overview

保持 Hermes Brain 的数据质量。检测孤岛页面、断裂的 back-link、过期内容，以及从多篇反思中合成跨会话模式。

## When to Use

- 用户问 "脑健康吗？"、"检查一下脑"
- 刚完成大量摄入后（3+ 新页面）
- Book Mirror 运行前做一次健康检查
- 定期（建议每周一次）

## 健康检查清单

### 1. 孤岛检测

找出没有被任何其他页面引用的页面：

```bash
# 收集所有脑页
find ~/.hermes/brain/ -name "*.md" ! -name "BRAIN_FORMAT.md" ! -name "USER.md" ! -name "SOUL.md" > /tmp/brain_pages.txt

# 检查每个页面是否被其他页面引用
while read page; do
  slug=$(basename "$page" .md)
  refs=$(grep -rl "$slug" ~/.hermes/brain/ --include="*.md" | grep -v "$page" | wc -l)
  if [ "$refs" -eq 0 ]; then
    echo "ORPHAN: $page"
  fi
done < /tmp/brain_pages.txt
```

### 2. Back-link 完整性

检查新页面是否在提及的人物/概念页上创建了 back-link：

```bash
# 找出最近 7 天创建的页面
find ~/.hermes/brain/ -name "*.md" -mtime -7 -newer ~/.hermes/brain/BRAIN_FORMAT.md

# 对每个新页面，检查它提到的实体是否有 back-link
# 手动检查：读新页面 → 提取提到的实体 → 检查实体页的 Timeline
```

### 3. Frontmatter 完整性

```bash
# 检查所有脑页是否有完整的 frontmatter
for f in $(find ~/.hermes/brain/ -name "*.md" ! -name "BRAIN_FORMAT.md"); do
  if ! head -1 "$f" | grep -q "^---$"; then
    echo "MISSING FRONTMATTER: $f"
  fi
done
```

### 4. 过期内容提醒

```bash
# 找出超过 90 天未更新的模式页（可能需要重新审视）
find ~/.hermes/brain/patterns/ -name "*.md" -mtime +90
```

## 模式合成

当 `reflections/` 中有 ≥3 篇涉及相似主题时，合成一个新模式：

### 合成流程

1. **收集候选**：
```bash
grep -rl "<theme_keyword>" ~/.hermes/brain/reflections/ --include="*.md" | sort
```

2. **读取所有候选反思**，提取：
   - 触发情境
   - 用户反应
   - 用户的原话（verbatim quotes）
   - 日期

3. **判断是否构成模式**：
   - ≥3 次独立出现
   - 跨 ≥7 天
   - 有共同触发条件或反应模式

4. **写入模式页**，用 `brain-ingest` 的模板

5. **Back-link 所有源反思**到新模式

### 合成输出示例

```markdown
---
title: "截止前冲刺模式"
type: pattern
date: 2026-05-23
tags: [pattern, productivity, procrastination]
links:
  - ../reflections/2026-05-01-blog-deadline.md
  - ../reflections/2026-05-10-report-delay.md
  - ../reflections/2026-05-20-presentation-rush.md
---

# 截止前冲刺模式

## 模式描述
在截止前 24-48 小时进入高效冲刺状态，但前期的拖延导致不必要的压力和睡眠不足。

## 证据链
- **2026-05-01** | 博客在发布前 3 小时完成 → [reflection](reflections/2026-05-01-blog-deadline.md)
- **2026-05-10** | 季报在截止日当天提交 → [reflection](reflections/2026-05-10-report-delay.md)
- **2026-05-20** | PPT 在演示前一夜做完 → [reflection](reflections/2026-05-20-presentation-rush.md)

## 用户原话
> "我好像总是在最后一刻才真正动起来"

## 可能的干预
- 设置假截止日（提前 2 天）
- 公开承诺（social accountability）
```

## 一键健康报告

```bash
echo "=== Hermes Brain 健康报告 $(date +%Y-%m-%d) ==="
echo ""
echo "--- 页面统计 ---"
find ~/.hermes/brain/ -name "*.md" ! -name "BRAIN_FORMAT.md" | wc -l | xargs echo "总页面数:"
for dir in people reflections patterns books concepts; do
  count=$(find ~/.hermes/brain/$dir/ -name "*.md" 2>/dev/null | wc -l)
  echo "  $dir: $count"
done
echo ""
echo "--- 最近 7 天新增 ---"
find ~/.hermes/brain/ -name "*.md" -mtime -7 ! -name "BRAIN_FORMAT.md" | sort
echo ""
echo "--- 孤岛页面 ---"
# (运行上面的孤岛检测脚本)
echo ""
echo "--- 待合成模式 ---"
# (运行模式合成检测)
```

## Common Pitfalls

1. **孤岛不修**。发现孤岛后要么链接它，要么删掉它。孤岛 = 白存。
2. **Back-link 单向**。A 提了 B，B 没回链 A → 断链。
3. **模式合成太早**。2 次不算模式，至少 3 次 + 跨 7 天。
4. **只检查不修复**。健康检查的价值在执行修复。

## Verification Checklist

- [ ] 孤岛页面已处理（链接或删除）
- [ ] 所有新页面的 back-link 已补全
- [ ] Frontmatter 完整性已验证
- [ ] >=3 次出现的主题已合成模式
- [ ] 健康报告已向用户展示
