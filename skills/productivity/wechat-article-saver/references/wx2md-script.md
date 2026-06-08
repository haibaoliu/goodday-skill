# wx2md.py — Script Reference

## What
Python CLI that wraps `url-md` to fetch WeChat public account articles and save them as Markdown files with YAML frontmatter to a local knowledge base.

## Path
`/Users/macbook/Documents/hermes-output/wx2md.py`

## Dependencies
- `url-md` Rust binary at `~/.url-md/bin/url-md` (anti-crawler bypass + Markdown extraction)
- Python 3.12+

## Key Design Decisions

### REAL_HOME env var
Inside Hermes terminal sessions, `os.path.expanduser("~")` resolves to the Hermes profile home (`~/.hermes/profiles/chuck/home/`), NOT the real macOS home. The script uses `REAL_HOME` env var as the first priority, falling back to `os.path.expanduser("~")`. Always set `REAL_HOME=/Users/macbook` when calling from Hermes:

```bash
REAL_HOME=/Users/macbook python3 /Users/macbook/Documents/hermes-output/wx2md.py "<URL>"
```

### url-md PATH
The `find_urlmd()` function checks:
1. `$REAL_HOME/.url-md/bin/url-md`
2. `/usr/local/bin/url-md`
3. Adds `~/.url-md/bin` to PATH and uses `shutil.which()`

### Anti-crawler
url-md handles anti-crawler internally (exit code 11 = blocked). The wrapper script does NOT re-implement crawling. url-md's Rust binary uses reqwest for WeChat permanent links with CDP fallback.

### WeChat article metadata limitations
- `publish_time` may be empty in url-md frontmatter (WeChat doesn't expose it consistently)
- `author` is the public account name
- `word_count` and `reading_time_minutes` are available
- `cover_url` references the mmbiz CDN (may expire)

## Output format
Files saved as: `YYYY-MM-DD-Author-Title.md`

Frontmatter:
```yaml
---
title: <article title>
author: <account name>
source: 微信公众号
publish_time: <date or empty>
source_url: <original mp.weixin.qq.com URL>
fetched_at: <ISO timestamp>
cover_url: <mmbiz CDN URL>
tags: [tag1, tag2]
word_count: <N>
---
```

Default output directory: `~/Documents/hermes-output/wx-articles/`
