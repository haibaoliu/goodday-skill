#!/usr/bin/env python3
"""B站字幕提取 — 需 cookie，支持中英双语。"""
import json, sys, hashlib, time, urllib.request, urllib.parse, os, re
from pathlib import Path

COOKIE_FILE = Path(__file__).parent.parent / ".bilibili_cookies"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

MIXIN_KEY_ENC_TAB = [
    46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,
    33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,
    61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,52,34,44,
]


def get_mixin_key(orig: str) -> str:
    return ''.join(orig[n] for n in MIXIN_KEY_ENC_TAB if n < len(orig))[:32]


def load_cookies() -> str:
    """Load B站 cookies from .bilibili_cookies file."""
    if not COOKIE_FILE.exists():
        sys.stderr.write(f"Cookie file not found: {COOKIE_FILE}\n")
        sys.stderr.write("Place SESSDATA and bili_jct in this file.\n")
        sys.exit(1)
    lines = COOKIE_FILE.read_text().strip().split('\n')
    cookies = {}
    for line in lines:
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            cookies[k.strip()] = v.strip()
    if 'SESSDATA' not in cookies:
        sys.stderr.write("SESSDATA not found in cookie file.\n")
        sys.exit(1)
    return f"SESSDATA={cookies['SESSDATA']}; bili_jct={cookies.get('bili_jct', '')}"


def wbi_signed_url(endpoint: str, params: dict, mixin_key: str) -> str:
    """Build WBI-signed URL."""
    params["wts"] = int(time.time())
    query = urllib.parse.urlencode(sorted(params.items()))
    w_rid = hashlib.md5((query + mixin_key).encode()).hexdigest()
    return f"{endpoint}?{query}&w_rid={w_rid}"


def get_mixin_key_from_nav(cookie: str) -> str:
    """Fetch img_key and sub_key from nav API."""
    req = urllib.request.Request(
        "https://api.bilibili.com/x/web-interface/nav",
        headers={"User-Agent": UA, "Referer": "https://www.bilibili.com/", "Cookie": cookie}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        nav = json.loads(resp.read())
    wbi = nav['data']['wbi_img']
    img_key = wbi['img_url'].split('/')[-1].split('.')[0]
    sub_key = wbi['sub_url'].split('/')[-1].split('.')[0]
    return get_mixin_key(img_key + sub_key)


def get_cid(bvid: str) -> dict:
    """Get CID list for a BV video."""
    url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.bilibili.com/"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return {p['cid']: p.get('part', '') for p in data.get('data', [])}


def get_subtitles(bvid: str, cid: str, cookie: str, mixin_key: str) -> list:
    """Get subtitle list and download content."""
    params = {"bvid": bvid, "cid": cid}
    url = wbi_signed_url("https://api.bilibili.com/x/player/wbi/v2", params, mixin_key)
    
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Referer": "https://www.bilibili.com/", "Cookie": cookie
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        player = json.loads(resp.read())

    subs = player.get('data', {}).get('subtitle', {}).get('subtitles', [])
    results = []
    for s in subs:
        raw_url = s.get('subtitle_url', '')
        if raw_url.startswith('//'):
            raw_url = 'https:' + raw_url
        lang = s.get('lan_doc', 'unknown')
        
        if raw_url:
            try:
                req2 = urllib.request.Request(raw_url, headers={
                    "User-Agent": UA, "Referer": "https://www.bilibili.com/"
                })
                with urllib.request.urlopen(req2, timeout=10) as resp2:
                    sub_json = json.loads(resp2.read())
                body = sub_json.get('body', [])
                results.append({
                    'lang': lang,
                    'segments': body,
                    'count': len(body),
                })
            except Exception as e:
                results.append({'lang': lang, 'error': str(e), 'segments': []})
    return results


def format_subtitles(results: list, mode: str = "text") -> str:
    """Format subtitle results."""
    lines = []
    for r in results:
        if r.get('error'):
            lines.append(f"\n## {r['lang']} ❌ {r['error']}")
            continue
        segs = r['segments']
        lines.append(f"\n## {r['lang']} ({len(segs)}段)")
        
        if mode == "text":
            # Pure text - concatenate all segments
            text = ' '.join(s.get('content', '') for s in segs)
            lines.append(text)
        elif mode == "timed":
            # With timestamps
            for s in segs:
                ts = f"[{s.get('from',0):.0f}s]"
                lines.append(f"{ts} {s.get('content','')}")
        else:  # "segments"
            for s in segs[:20]:
                lines.append(f"  [{s.get('from',0):.0f}s-{s.get('to',0):.0f}s] {s.get('content','')}")
            if len(segs) > 20:
                lines.append(f"  ... ({len(segs) - 20} more segments)")
    return '\n'.join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="B站字幕提取")
    parser.add_argument("url_or_bvid", help="B站视频 URL 或 BV 号")
    parser.add_argument("--part", type=int, default=1, help="分P序号 (默认: 1)")
    parser.add_argument("--mode", choices=["text", "timed", "segments"], default="text",
                        help="输出格式: text(纯文本), timed(带时间), segments(分段)")
    parser.add_argument("--lang", default="all", help="语言过滤: all, zh, en (默认: all)")
    args = parser.parse_args()

    # Parse BV from URL or direct input
    m = re.search(r'(BV[a-zA-Z0-9]+)', args.url_or_bvid)
    bvid = m.group(1) if m else args.url_or_bvid

    cookie = load_cookies()
    mixin_key = get_mixin_key_from_nav(cookie)

    # Get CID map
    cid_map = get_cid(bvid)
    if not cid_map:
        print("❌ 无法获取分P信息")
        sys.exit(1)

    # Select the right CID
    cids = list(cid_map.keys())
    if args.part > len(cids):
        print(f"❌ 分P {args.part} 不存在，共 {len(cids)} 个分P")
        sys.exit(1)
    cid = str(cids[args.part - 1])
    part_name = cid_map[int(cid)]

    print(f"📺 {part_name}")
    print(f"   BV: {bvid}  CID: {cid}")

    results = get_subtitles(bvid, cid, cookie, mixin_key)

    # Filter by language
    if args.lang != "all":
        lang_map = {"zh": "中文", "en": "English", "ja": "日语"}
        target = lang_map.get(args.lang, args.lang)
        results = [r for r in results if target in r.get('lang', '')]

    if not results:
        print("❌ 无字幕")
        sys.exit(0)

    print(format_subtitles(results, args.mode))
