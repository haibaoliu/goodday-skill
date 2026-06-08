---
name: wechat-article-saver
description: Save WeChat public account (公众号) articles as Markdown files with frontmatter, and add to NotebookLM for deep reading Q&A. Use when the user shares mp.weixin.qq.com URLs.
triggers:
  - User shares a WeChat article URL (mp.weixin.qq.com/s/*)
  - User says "保存这篇文章" / "下载到知识库" / "存到 obsidian" / "收藏"
  - User says "加到 NotebookLM" / "深度阅读"
tools:
  - terminal (for running wx2md.py)
  - read_file (for verifying output)
---

# WeChat Article Saver + NotebookLM

## Pipeline
```
公众号链接 → url-md 抓取 → Markdown 存本地 → NotebookLM 深度阅读
```

## Dependencies
- **url-md**: `~/.url-md/bin/url-md` (7MB Rust binary, anti-crawler bypass built-in)
- **wx2md.py**: `/Users/macbook/Documents/hermes-output/wx2md.py`
- **notebooklm CLI**: `/Users/macbook/.hermes/hermes-agent/venv/bin/notebooklm` (authenticated ✅)

## Primary: url-md pipeline

```bash
REAL_HOME=/Users/macbook python3 /Users/macbook/Documents/hermes-output/wx2md.py "<URL>" --notebooklm
```

Tries first. If it fails with `blocked by anti-bot`, go to fallback immediately — do NOT retry.

## Fallback: browser_vision (when url-md blocked)

url-md is increasingly blocked by WeChat anti-bot. When it fails:

1. `browser_navigate(url)` — load the article
2. `browser_vision(question="Read ALL text in this article...")` — extract content
3. `write_file(path, markdown)` — save with frontmatter to `~/Documents/hermes-output/wx-articles/`
4. Skip NotebookLM — add source later if needed

The fallback is reliable because WeChat articles are server-rendered HTML — the browser can always access them.

## Save only (no NotebookLM)

```bash
REAL_HOME=/Users/macbook python3 /Users/macbook/Documents/hermes-output/wx2md.py "<URL>"
```

## Output
- Local: `~/Documents/hermes-output/wx-articles/YYYY-MM-DD-Author-Title.md`
- NotebookLM: source added to active notebook ("AI Hero: Practical Skills for Real Engineers")

## Default behavior
**Always use `--notebooklm`** when user shares a URL — article lands in both local vault and NotebookLM. No need to ask.

## After saving
Confirm: file path, word count, and NotebookLM source added. Remind user they can now chat with the article in NotebookLM.

## Related
- **SkillOpt**: Microsoft's self-evolving skill optimizer, installed at `/Users/macbook/Documents/hermes-output/SkillOpt/`. See `references/skillopt.md` for setup and Hermes integration notes.

## Pitfalls

- **url-md anti-bot blocking (FREQUENT)**: url-md gets blocked by WeChat anti-bot (`content marker 'id="js_content"' missing`). Do NOT retry — use the browser_vision fallback immediately. This happened 2026-06-08 and many prior sessions.
- **url-md binary**: Must be at `/Users/macbook/.url-md/bin/url-md`.
- **`~` trap**: Hermes terminal `~` resolves to profile home, not real home. Always use `REAL_HOME=/Users/macbook` + absolute paths.
- **Sogou search blocked**: Article URLs must come directly from user's WeChat feed; Sogou discovery is blocked.