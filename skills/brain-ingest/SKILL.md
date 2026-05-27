---
name: brain-ingest
description: Use when the user shares content worth remembering (thoughts, observations, meeting notes, ideas, reflections). Write structured brain pages into ~/.hermes/brain/ following the brain-page format spec.
version: 1.0.0
author: Hermes Brain System
license: MIT
metadata:
  hermes:
    tags: [brain, memory, ingestion, knowledge-management]
    related_skills: [brain-query, brain-maintain, book-mirror]
---

# Brain Ingest — 通用脑页摄入

## Overview

将用户的任何值得记住的内容写入结构化的脑页（`~/.hermes/brain/`）。不只是保存——是结构化、关联化，让知识可以复利。

## When to Use

- 用户说 "记住这个"、"存下来"、"这个想法不错"
- 对话中出现了值得记住的洞察、模式、决定
- 用户分享了一条反思或观察
- 你识别到一个可能复现的模式

**不要用于**：临时任务状态、一次性对话、无长期价值的信息。

## 决策树：存到哪里

```
用户分享的内容
├─ 关于某个人？              → people/<slug>.md
├─ 日记/反思/情绪？          → reflections/YYYY-MM-DD-<topic>.md
├─ 跨会话反复出现的模式？    → patterns/<pattern-name>.md
├─ 可复用的心智模型/框架？   → concepts/<concept-name>.md
├─ 关于我本人的事实/偏好？   → 更新 USER.md
└─ 不确定？                  → reflections/（先存，日后归类）
```

## 脑页格式

每个新建的脑页必须包含 YAML frontmatter：

```yaml
---
title: "页面标题"
type: person | reflection | pattern | concept
date: YYYY-MM-DD
tags: [至少一个标签]
links:
  - ../related/page.md  # 如果有
---
```

## 操作流程

### 1. 判断价值

问自己：7 天后用户还会想找回这条信息吗？如果答案为否，不存。

### 2. 确定位置

按上面的决策树选择目录。Slug 规则：小写字母+数字+连字符，无空格。

### 3. 读取现有脑页（如果更新）

```bash
# 检查是否已有该实体的脑页
ls ~/.hermes/brain/people/ | grep -i <name>
# 如果有，读取并追加 Timeline
cat ~/.hermes/brain/people/<slug>.md
```

### 4. 写入脑页

用 `write_file` 写入 Markdown 文件。

**人物页模板**：
```markdown
---
title: "<名字>"
type: person
date: YYYY-MM-DD
tags: [person, <role>, <context>]
---

# <名字>

## 基本信息
- 关系：
- 上下文：
- 首次记录：YYYY-MM-DD

## Timeline
- **YYYY-MM-DD** | 事件描述 [Source: user conversation, YYYY-MM-DD]

## 相关脑页
```

**反思页模板**：
```markdown
---
title: "<主题>"
type: reflection
date: YYYY-MM-DD
tags: [<emotion>, <domain>]
---

# <主题>

## 发生了什么

## 我的反应

## 洞察

> "<用户原话>"
```

**模式页模板**：
```markdown
---
title: "<模式名>"
type: pattern
date: YYYY-MM-DD
tags: [pattern, <domain>]
links:
  - ../reflections/YYYY-MM-DD-<first-occurrence>.md
---

# <模式名>

## 模式描述

## 证据链
- **YYYY-MM-DD** | 第N次出现 → [reflection](reflections/...)
- **YYYY-MM-DD** | 第N次出现 → [reflection](reflections/...)

## 可能的干预
```

### 5. Back-link

如果新页面提到了已有脑页的人或概念，必须去对方页面加 back-link：

```markdown
- **YYYY-MM-DD** | 被 [新页面标题](path/to/new.md) 引用 — 简要上下文
```

### 6. 向用户确认

用简短的一句话告诉用户存了什么、存在哪。

## USER.md / SOUL.md 更新

如果用户分享了关于自己的新事实或偏好变更：

```bash
# 读取当前版本
cat ~/.hermes/brain/USER.md
# 用 patch 更新对应字段
```

不要重写整个 USER.md——用 `patch` 工具做精准更新。

## Common Pitfalls

1. **存太多垃圾**。重要性门槛要高。如果犹豫，不存。
2. **忘记 back-link**。不链回去 = 孤岛页面，搜索找不到。
3. **Slug 不规范**。空格、中文、大写都会导致引用断裂。
4. **不引用来源**。每个事实/洞察必须可追溯到原始对话。
5. **覆盖已有页面**。更新时追加 Timeline 或 Facts，不要重写。

## Verification Checklist

- [ ] 脑页在正确目录下
- [ ] Frontmatter 完整（title, type, date, tags）
- [ ] Slug 是小写字母+数字+连字符
- [ ] 所有事实有 Source 引用
- [ ] 相关实体页面已加 back-link
- [ ] 向用户确认了存档位置
