#!/usr/bin/env python3
"""B站搜索 — 零认证，直接调公开 API。"""
import json, sys, urllib.request, urllib.parse

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
API = "https://api.bilibili.com/x/web-interface/search/all/v2"
TIMEOUT = 10


def search(query: str, page: int = 1) -> dict:
    params = urllib.parse.urlencode({"keyword": query, "page": page})
    url = f"{API}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read())


def clean_html(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", str(text))


def format_results(data: dict) -> str:
    if data.get("code") != 0:
        return f"❌ API 错误: {data.get('message', '未知')}"

    lines = []
    for item in data.get("data", {}).get("result", []):
        rt = item.get("result_type", "?")
        results = item.get("data", [])
        if not results:
            continue
        type_names = {"video": "📺 视频", "media_bangumi": "🎬 番剧",
                      "article": "📝 专栏", "live_room": "🔴 直播",
                      "bili_user": "👤 用户", "topic": "💬 话题"}
        lines.append(f"\n## {type_names.get(rt, rt)} ({len(results)}条)")
        for i, r in enumerate(results[:8]):
            title = clean_html(r.get("title", r.get("name", "?")))
            if rt == "video":
                bvid = r.get("bvid", "")
                play = r.get("play", 0)
                danmu = r.get("video_review", 0)
                author = r.get("author", "?")
                lines.append(f"{i+1}. [{title}](https://www.bilibili.com/video/{bvid})")
                lines.append(f"   UP: {author} | ▶️ {_fmt_num(play)} | 💬 {_fmt_num(danmu)}")
            elif rt == "bili_user":
                mid = r.get("mid", "")
                fans = r.get("fans", 0)
                lines.append(f"{i+1}. {title} — 粉丝 {_fmt_num(fans)}")
                lines.append(f"   https://space.bilibili.com/{mid}")
            else:
                url = r.get("arcurl", r.get("url", ""))
                desc = clean_html(r.get("description", r.get("desc", "")))[:100]
                lines.append(f"{i+1}. {title}")
                if url:
                    lines.append(f"   {url}")
                if desc:
                    lines.append(f"   {desc}")

    return "\n".join(lines)


def _fmt_num(n) -> str:
    if n >= 10000:
        return f"{n/10000:.1f}万"
    return str(n)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: bilibili-search.py <关键词> [页码]")
        sys.exit(1)
    query = sys.argv[1]
    page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    data = search(query, page)
    print(format_results(data))
