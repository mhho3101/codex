# hook-lab

分析 TikTok / Instagram Reels / YouTube Shorts 视频，拆解 hook、脚本结构、爆款原因，并给出适配中文平台的改写方向。

## 使用方式

在 Claude Code 里运行：

```
/analyze https://www.tiktok.com/@someone/video/1234567890
/analyze https://www.instagram.com/reel/abcDEF123/
/analyze https://www.youtube.com/shorts/abcdefg
```

## 输出内容

1. **数据面板** — 播放量、点赞、评论、转发、互动率
2. **Hook 拆解** — Hook 类型、为什么能让人停下来、改写建议
3. **脚本结构** — 按叙事逻辑分段，标注各段作用和节奏
4. **风格标签** — 呈现方式、内容类型、情绪基调
5. **为什么能爆** — 2-3 个具体原因，不泛泛而谈
6. **改写方向** — 3 个可落地的角度，含 hook 示例和适配平台

每次分析结果自动追加到 `results/analyzed-videos.md`，供跨视频对比使用。

## 安装

```bash
cp -r hook-lab ~/.claude/skills/hook-lab
pip3 install yt-dlp
```

## 提取失败时的回退

1. yt-dlp 失败 → 尝试带 Chrome cookie 重试
2. TikTok 仍失败 → 解析页面内嵌 JSON
3. 以上均失败 → Claude 用 WebFetch 抓取页面
4. 全部失败 → 提示用户手动粘贴文案和数据

## License

MIT
