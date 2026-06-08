---
name: bilibili-search
description: "B站搜索+字幕提取：零认证公开API搜索视频/用户/文章/直播，登录态字幕抓取。触发词：B站/bilibili/哔哩哔哩/搜B站/字幕/弹幕。"
triggers: B站/bilibili/哔哩哔哩/b站搜索/search bilibili
---

# Bilibili Search

Zero-config B站 search using the public API. No login, no API key.

## Quick Search

```bash
python3 ~/.hermes/profiles/chuck/skills/bilibili-search/scripts/bilibili-search.py "<query>" [page]
```

Returns videos with titles, URLs, play counts, and danmu counts. Results are formatted in Markdown with clickable links.

## Video Subtitle Extraction

**Working!** Uses WBI-signed API + SESSDATA cookie. Cookie stored in `.bilibili_cookies` at skill root.

```bash
python3 ~/.hermes/profiles/chuck/skills/bilibili-search/scripts/bilibili-subtitle.py "<BV号>" [--part N] [--mode text|timed|segments] [--lang zh|en|all]
```

**Modes:** `text` (纯文本, default) | `timed` (带时间戳) | `segments` (分段预览)
**Example:** `bilibili-subtitle.py BV1Zt4y1H78P --part 1 --lang zh`

### How it works
1. WBI signing key from nav API
2. CID from pagelist API  
3. Player WBI-signed API → subtitle JSON URLs
4. Download subtitle JSON from `aisubtitle.hdslb.com`
5. Format as text/timed/segments

## Result Types

| API type | Description |
|----------|-------------|
| video | Videos with title, play count, danmu, UP主 |
| media_bangumi | Anime / series |
| article | 专栏文章 |
| live_room | Live streams |
| bili_user | User profiles with follower counts |
| topic | Discussion topics |

## Limitations

- Search only — no comments, no trending, no personalized recommendations
- Subtitle extraction requires B站 login cookies (SESSDATA)
- For trending/hot lists, install `bili-cli` (`pipx install bilibili-cli`)

## References

- `references/wbi-subtitle-extraction.md` — WBI signing mechanism, discovery process, API endpoints
- `references/subtitle-investigation.md` — Earlier investigation notes
- `references/agent-reach-vs-last30days.md` — Comparative analysis
## References

- `references/subtitle-investigation.md` — Detailed findings from B站 subtitle extraction attempts (APIs tested, error codes, auth requirements)
- `references/agent-reach-vs-last30days.md` — Comparative analysis of Agent-Reach and last30days-skill projects
