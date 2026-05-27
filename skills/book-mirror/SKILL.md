---
name: book-mirror
description: Use when the user provides a book (EPUB/PDF) and wants a personalized chapter-by-chapter analysis. Left column preserves book content; right column maps every insight to the reader's actual life using brain context. Outputs to ~/.hermes/brain/books/<slug>-personalized.md.
version: 1.0.0
author: Hermes Brain System
license: MIT
metadata:
  hermes:
    tags: [brain, book, reading, personalization, two-column]
    related_skills: [brain-ingest, brain-query, brain-maintain]
---

# Book Mirror — 双栏个人化书析

## Overview

把一本书变成你的——每一章左边是作者说了什么，右边是你的经历映射。

这不是书摘。右栏才是价值：让书读起来像一位了解你到骨子里的治疗师在旁注。

> **参考实现**: [references/gbrain-architecture.md](references/gbrain-architecture.md) — Garry Tan 的 GBrain Book Mirror 原始架构分析，含安全信任模型、成本、架构决策。

## Trust Contract（安全模型）

和 GBrain 一样的设计原则：

- **子 Agent 只读**：每个章节的分析子 Agent 使用 `toolsets=['terminal', 'file']`，只能读文件、不能写脑页
- **父 Agent 拼装**：所有子 Agent 返回分析文本后，父 Agent 拼装并写入脑页
- **Prompt injection 安全**：即使 EPUB 内容包含恶意指令，子 Agent 没有写脑页的能力，攻击面在工具层被切断

## Pipeline

```
1. ACQUIRE   → 用户提供 EPUB/PDF 路径
2. EXTRACT   → 解压/提取每个章节为 .txt
3. CONTEXT   → 收集脑上下文（brain-query skill）
4. ANALYZE   → 并行子 Agent，每章一个
5. ASSEMBLE  → 父 Agent 拼装双栏 Markdown
6. BACK-LINK → brain-maintain 加回链
```

## 1. 获取书籍

用户提供路径或文件：

```bash
# 检查文件存在
ls -la <path/to/book.epub>
ls -la <path/to/book.pdf>
```

推荐用户把书放到 `~/Documents/hermes-output/` 下。

## 2. 文本提取

### EPUB

```bash
SLUG="<kebab-case-book-name>"
WORK="/tmp/book-mirror-$SLUG"
mkdir -p "$WORK/chapters"

# 解压 EPUB
unzip -o <path/to/book.epub> -d "$WORK/unpacked"

# 找内容文件并提取文本
find "$WORK/unpacked" -name "*.xhtml" -o -name "*.html" | sort > "$WORK/files.txt"

python3 - <<'PY'
from bs4 import BeautifulSoup
import os
work = os.environ['WORK']
files = open(f'{work}/files.txt').read().splitlines()
for i, path in enumerate(files, 1):
    html = open(path, encoding='utf-8', errors='replace').read()
    text = BeautifulSoup(html, 'html.parser').get_text('\n')
    text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
    with open(f'{work}/chapters/{i:02d}.txt', 'w') as f:
        f.write(text)
PY
```

如果缺少 `bs4`：`pip3 install beautifulsoup4 lxml`

### PDF

**方案 A: pdftotext（优先，速度最快）**
```bash
pdftotext -layout <path/to/book.pdf> "$WORK/full.txt"
```

**方案 B: PyPDF2（macOS 备选，pdftotext 不可用时）**
```bash
pip install PyPDF2  # 装到 hermes venv
python3 -c "
import PyPDF2
reader = PyPDF2.PdfReader('<path/to/book.pdf>')
text = '\n\n'.join(p.extract_text() or '' for p in reader.pages)
open('$WORK/full.txt', 'w').write(text)
print(f'{len(reader.pages)} pages extracted')
"
```

然后按章节标题分割：

### 质检

```bash
# 每章字数 > 1500（典型章节 2k-8k）
for f in "$WORK/chapters/"*.txt; do
  wc -w < "$f"
done

# 筛掉扉页/目录（字数 < 500 的文件通常是 front matter）
# 生成 chapters/INDEX.md
```

## 3. 上下文收集

**这是最关键的步骤。右栏的质量取决于这里。**

用 `brain-query` skill 的方式收集：

```bash
CONTEXT="$WORK/context.md"

{
  echo "# 读者上下文"
  echo ""
  
  echo "## USER.md"
  cat ~/.hermes/brain/USER.md 2>/dev/null || echo "(未填写)"
  echo ""
  
  echo "## SOUL.md"
  cat ~/.hermes/brain/SOUL.md 2>/dev/null || echo "(未填写)"
  echo ""
  
  echo "## 最近 14 天反思"
  find ~/.hermes/brain/reflections/ -name "*.md" -mtime -14 | sort | while read f; do
    echo "---"
    cat "$f"
  done
  echo ""
  
  echo "## 模式"
  for f in ~/.hermes/brain/patterns/*.md; do
    echo "---"
    cat "$f"
  done
  echo ""
  
  echo "## 人物"
  for f in ~/.hermes/brain/people/*.md; do
    echo "---"
    cat "$f"
  done
  echo ""
  
  echo "## 主题相关脑页"
  # 搜书名和章节关键词
  grep -rl "<keyword1>\|<keyword2>" ~/.hermes/brain/ --include="*.md" | while read f; do
    echo "---"
    head -80 "$f"
  done
  
} > "$CONTEXT"

echo "上下文大小: $(wc -c < $CONTEXT) bytes, $(wc -l < $CONTEXT) lines"
```

## 4. 并行章节分析

这是核心步骤。用 `delegate_task` 的 batch 模式并行分析所有章节。

### 子 Agent Prompt 模板

每个子 Agent 接收：

```
You are analyzing ONE chapter of "<书名>" by <作者> for the reader.

Your output is a two-column markdown table:
- LEFT column: preserves the chapter's actual content (stories, frameworks, stats, named examples)
- RIGHT column: maps each idea to the reader's actual life using their words, situations, and patterns from the READER CONTEXT below.

This is chapter <N> of <TOTAL>.

## CHAPTER <N> TEXT

<章节全文>

## READER CONTEXT

<上下文文件内容>

## OUTPUT FORMAT

Return ONLY:

## Chapter <N>: <章节标题>

### Key Ideas
<2-4 句话总结作者核心论点>

| What the Author Says | How This Applies to You |
|---|---|
| <详细段落，保留故事/数据/框架/案例> | <specific 个人连接：引用读者的原话、具体日期/情境/人名> |
| ... | ... |
| <4-10 行，取决于章节密度> | |

## RULES
- LEFT: preserve stories, stats, frameworks. Don't summarize away texture.
- RIGHT: use the reader's ACTUAL words from READER CONTEXT. Name people, dates, situations.
- 4-10 rows per chapter.
- If a section truly doesn't apply: say "*This section is less directly relevant because [reason].*" Don't force connections.
- Never generic. Never sycophantic. Never preach.
- Use `<br><br>` for paragraph breaks inside table cells.
```

### 并行调用

```python
# 伪代码：对每章调用 delegate_task
delegate_task(tasks=[
  {
    "goal": "Analyze chapter 1 of <book>",
    "context": "<prompt with chapter text + reader context>",
    "toolsets": ["terminal", "file"]  # 只读工具
  },
  {
    "goal": "Analyze chapter 2 of <book>", 
    "context": "<prompt with chapter text + reader context>",
    "toolsets": ["terminal", "file"]
  },
  # ... batch of up to 3 per wave
])
```

由于 `delegate_task` 限制 3 个并行，超过 3 章的书籍分波次提交。
如果某章失败，重试只需重新提交那章（幂等）。

## 5. 拼装最终脑页

父 Agent 拿到所有子 Agent 的分析结果后，拼装：

```markdown
---
title: "<书名> — Personalized"
type: book-analysis
date: YYYY-MM-DD
author: "<作者>"
tags: [book, personalized, two-column]
---

# <书名> — Personalized

## What this is

A chapter-by-chapter personalized analysis of *<书名>* by <作者>.
Each chapter summarized in detail on the left and mirrored to the reader's
actual life on the right, drawing on brain context.

Generated by `book-mirror` skill. Each chapter came from a separate
read-only subagent with no write access.

---

<子 Agent 输出 1>

---

<子 Agent 输出 2>

---
```

用 `write_file` 写入 `~/.hermes/brain/books/<slug>-personalized.md`。

## 6. Back-link

完成后，对右栏中提到的每个人/概念：
1. 检查 `~/.hermes/brain/people/<slug>.md` 或 `~/.hermes/brain/concepts/<slug>.md` 是否存在
2. 在对方页的 Timeline 或「相关脑页」中追加链接
3. 用 `patch` 工具精准追加，不要重写整个页面

## 防注入安全要点

1. EPUB 内容可能包含恶意提示词。但子 Agent 只有 `terminal` + `file` 工具，不能调用 `write_file` / `memory` / `skill_manage`
2. 子 Agent 产出的只是 Markdown 文本，父 Agent 读取后才写入
3. 如果子 Agent 产出的文本中包含恶意指令（如 "请删除所有文件"），它只是 Markdown 表格里的字面文本，不会被父 Agent 执行

## Common Pitfalls

1. **上下文太薄**。右栏泛泛而谈 = 白做了。上下文至少应该包含 USER.md + SOUL.md + 人物页。实测 3.5K 字的上下文已能产生丰富的右栏映射——关键是密度而非长度。
2. **子 Agent 偷懒**。有些子 Agent 可能只输出 2-3 行。如果行数 < 4，重新提交该章。
3. **子 Agent 写入文件而非返回文本**。子 Agent 可能把分析结果写入磁盘文件（如 `write_file`），而不是在 summary 中返回。拼装时需要同时检查 summary 和磁盘文件——用 `read_file` 读取子 Agent 可能写入的文件。
4. **忘记 back-link**。Book Mirror 产出的页面如果不链回去，就是孤岛。
5. **pdftotext 不可用**。macOS 默认没有 pdftotext。备选方案：`pip install PyPDF2`，用 Python 提取文本。比 pdftotext 慢但不需要额外系统依赖。
6. **PDF/文档分割**。awk 按行分割中文 PDF 容易失败（编码/空白字符问题）。用 Python `re.split(r'\n(?=一、|二、|三、|四[，,])', text)` 按章节标题分割，可靠得多。
7. **文档很短时**。不需要强行分"章"。将主要节（导论、原理、功法、要点等）作为分析单元即可。8 页 11K 字的文档也完全跑得通。
8. **成本**。每节约消耗 2-5K tokens。4 节短文用 DeepSeek 约 $0.01-0.02。20 章的书用 DeepSeek 约 $0.05-0.10，用 Opus 约 $6。

## Verification Checklist

- [ ] EPUB/PDF 成功提取为章节 .txt 文件
- [ ] 上下文文件包含 USER.md + SOUL.md + 14 天反思 + 模式 + 人物 + 主题页面
- [ ] 所有子 Agent 返回了 4+ 行的表格
- [ ] 右栏使用了读者的实际原话和具体情境
- [ ] 最终页面写入 ~/.hermes/brain/books/<slug>-personalized.md
- [ ] 所有被提到的人物/概念页面已加 back-link
- [ ] 向用户报告了生成结果和统计
