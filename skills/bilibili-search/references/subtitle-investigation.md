# B站字幕提取调查报告

日期：2026-06-08 | 环境：macOS 12.7.6, x86_64

## 结论

- **搜索 API**：零认证，`api.bilibili.com/x/web-interface/search/all/v2`，完全可用
- **分P列表**：零认证，`api.bilibili.com/x/player/pagelist`，可用
- **字幕**：需要登录。`INITIAL_STATE` 中有字幕条目但 `subtitle_url` 为空字符串。登录后（SESSDATA cookie）才会填充实际 URL。

## 测试记录

### 1. yt-dlp — 被拒

```bash
yt-dlp --write-auto-sub --sub-lang zh-Hans --skip-download \
  "https://www.bilibili.com/video/BV1owrpYKEtP"
# → HTTP Error 412: Precondition Failed
```

即使加 User-Agent 和 Referer，仍然 412。B站最新的反爬机制封锁了无 cookie 的 yt-dlp 请求。

### 2. Player API — 无字幕

```bash
curl "https://api.bilibili.com/x/player/v2?bvid=BV1Zt4y1H78P&cid=..."
# → subtitle.subtitles = []  (空)
```

无认证时 player API 不返回字幕列表。

### 3. 页面 INITIAL_STATE — 字幕条目存在但 URL 为空

```json
// BV1Zt4y1H78P (吴恩达机器学习，标注"双语人译")
"subtitle": {
  "allow_submit": false,
  "list": [
    {"lan_doc": "中文（中国）", "subtitle_url": ""},
    {"lan_doc": "English(US)",  "subtitle_url": ""}
  ]
}
```

字幕元数据存在，但 URL 被服务器端隐藏。需要 SESSDATA cookie 才能获取实际 JSON 地址。

### 4. 全量关键词搜索 INITIAL_STATE

在 120KB 的 JSON 中搜索 `subtitle_url`、`ai_subtitle`、`caption_url` 等关键词，**全部为空字符串**。

## 解决方案

需要用户在浏览器登录 B站 后导出 Cookie：

```
必需的 Cookie:
- SESSDATA=<value>
- bili_jct=<value>
```

获取方式：浏览器 Cookie-Editor 插件 → 登录 bilibili.com → 导出 → 复制上述两个值。

## B站 API 端点总览

| 用途 | 端点 | 认证 |
|------|------|------|
| 搜索 | `api.bilibili.com/x/web-interface/search/all/v2` | 无 |
| 分P列表 | `api.bilibili.com/x/player/pagelist?bvid=` | 无 |
| 播放器信息 | `api.bilibili.com/x/player/v2?bvid=&cid=` | 无(字幕为空) |
| 字幕 JSON | `i0.hdslb.com/bfs/ai_subtitle/...` | 需 Cookie |
| 视频页面 | `www.bilibili.com/video/BV...` | 无(字幕URL为空) |
