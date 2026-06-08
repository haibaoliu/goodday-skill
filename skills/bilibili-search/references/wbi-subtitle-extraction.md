# B站 WBI 签名字幕提取

## 发现过程 (2026-06-08)

1. **yt-dlp 被 412 封杀** — 不加 cookie 时 B站返回 HTTP 412
2. **Player API 不登录返回空 URL** — `player/v2` 返回字幕列表但 `subtitle_url` 为空
3. **加 cookie 后 API 返回字幕列表但 URL 仍为空** — 需要 WBI 签名
4. **WBI 签名后成功** — `player/wbi/v2` + SESSDATA → 返回完整 subtitle JSON URL
5. **直连 CDN 下载** — `aisubtitle.hdslb.com/bfs/subtitle/xxx.json?auth_key=xxx`

## WBI 签名流程

```
1. GET /x/web-interface/nav (with cookie)
   → 拿到 wbi_img.img_url + wbi_img.sub_url
   → 提取 img_key + sub_key → 拼接 → mixin_key

2. 构建参数: {bvid, cid, wts=timestamp}
   → 排序 → URL encode → MD5(query + mixin_key) → w_rid

3. GET /x/player/wbi/v2?bvid=...&cid=...&wts=...&w_rid=...
   → 返回 subtitle.subtitles[].subtitle_url

4. GET subtitle_url (CDN, 有时带 auth_key)
   → JSON: {body: [{from, to, content}, ...]}
```

## Mixin Key Table

```python
MIXIN_KEY_ENC_TAB = [
    46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,
    33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,
    61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,52,34,44,
]
def get_mixin_key(orig: str) -> str:
    return ''.join(orig[n] for n in MIXIN_KEY_ENC_TAB if n < len(orig))[:32]
```

## 已知限制

- SESSDATA 有效期：6个月~1年（勾选"记住我"后）
- 字幕 JSON 携带 `auth_key`，有时效性（通常几分钟）
- 部分视频无字幕（`subtitle.list` 为空）
- WBI mixin key 需要从 nav API 实时获取，不可硬编码

## 参考脚本

`scripts/bilibili-subtitle.py` — 完整实现
