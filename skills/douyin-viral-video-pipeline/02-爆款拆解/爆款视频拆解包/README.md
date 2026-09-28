# Viral Video Breakdown

一个用于拆解爆款短视频的 Codex Skill。它可以把本地视频、抖音链接或其他 `yt-dlp` 支持的视频链接，整理成一个可复盘、可改写、可沉淀的创作者研究包。

## 给 Agent 看的一句话安装

把下面这句话复制给你的 Agent 即可：

```text
请帮我安装并配置这个 Codex Skill：https://github.com/KINNONG/viral-video-breakdown ，先做安全检查，然后克隆到我的 Codex skills 目录，按 README 检查 ffmpeg、yt-dlp、Python 依赖和本机模型路径，最后用一个本地视频做最小验证。
```

你不需要先学习 Git、Python 或 Codex Skill 的目录规则，让 Agent 按这句话执行就行。

## 它能做什么

运行后会为每条视频生成一个独立文件夹，默认只展示这 4 类核心结果：

- `source.mp4`：原始视频
- `keyframes/`：关键帧和 contact sheet
- `speaker_transcript.md`：带时间戳的说话人逐字稿
- `story_analysis.md`：剧情、钩子、冲突、反转、画面和评论区洞察

中间文件会放在隐藏的 `_work/` 目录里，包括音频、ASR JSON、日志、下载信息和评论原始数据。这样最终文件夹看起来干净，同时也方便后续重跑和排错。

## 适合什么场景

- 拆解爆款短视频
- 复盘 AI 短片、剧情短片、账号对标视频
- 提取标题、标签、前 3 秒钩子、剧情节拍、反转设计
- 分析画风、镜头、字幕、道具、场景变化和视听节奏
- 采集少量抖音评论，用来判断观众为什么会共鸣、争论或接梗
- 把一个视频总结成可迁移的创作结构，而不是照搬内容

## 重要提醒

`story_analysis.md` 是脚本生成的初稿，不是最终稿。真正交付前，建议让 Agent 读取逐字稿、关键帧、contact sheet 和评论数据，再把它改写成更具体的创作者研究报告。

## 手动安装方式

如果你想自己安装，可以把仓库克隆到 Codex skills 目录：

```powershell
git clone https://github.com/KINNONG/viral-video-breakdown.git `
  "$env:USERPROFILE\.codex\skills\viral-video-breakdown"
```

然后重启 Codex，或让 Codex 重新加载 skills。

## 依赖环境

基础依赖：

- Python 3.10+
- FFmpeg，并确保 `ffmpeg` 和 `ffprobe` 在 `PATH` 里
- `yt-dlp` 或 `uvx yt-dlp`
- `requirements.txt` 里的 Python 包
- faster-whisper 环境，用于带时间戳转写
- FunASR / SenseVoice 环境，用于中文 ASR 和可选说话人区分
- BrowserAct，仅在采集抖音评论或使用抖音浏览器兜底下载时需要

安装 Python 依赖：

```powershell
python -m pip install -r requirements.txt
```

PyTorch 建议根据你的 CPU / CUDA 环境单独安装。不同机器差异比较大，所以这里不强行写死版本。

## 本机配置

第一次使用前，打开 `references/local-setup.md`，把里面的占位符替换成你自己电脑上的路径。

至少需要配置：

```powershell
$env:PYTHONUTF8='1'
$env:AI_MODEL_CACHE='<your-model-cache-dir>'
$env:VIRAL_BREAKDOWN_DH_PYTHON='<path-to-python-with-funasr>\python.exe'
$env:VIRAL_BREAKDOWN_FW_PYTHON='<path-to-python-with-faster-whisper>\python.exe'
```

如果要采集抖音评论，或使用抖音浏览器兜底下载，还需要：

```powershell
$env:BROWSER_ACT_BROWSER_ID='<browser-act-browser-id>'
```

查看可用 BrowserAct 浏览器：

```powershell
browser-act browser list
```

## 使用示例

拆本地视频：

```powershell
python -X utf8 -u .\scripts\run_viral_video.py `
  --source-video "<path-to-video.mp4>" `
  --out-dir "<output-dir>" `
  --title "<video title>" `
  --comments off
```

拆普通视频链接：

```powershell
python -X utf8 -u .\scripts\run_viral_video.py `
  "<video URL>" `
  --out-dir "<output-dir>" `
  --title "<video title>" `
  --comments off
```

拆抖音链接，并保守采集评论：

```powershell
python -X utf8 -u .\scripts\run_viral_video.py `
  "<douyin share text or URL>" `
  --out-dir "<output-dir>" `
  --title "<title plus tags>" `
  --comments auto `
  --comment-browser-id "<browser-act-browser-id>" `
  --comment-limit 30 `
  --comment-scrolls 5 `
  --comment-delay 3
```

## 隐私和平台规则

- 不要提交下载的视频、生成的 `_work/`、模型文件、导出的 cookies、浏览器 profile、含有账号信息的截图或任何平台凭证。
- 抖音浏览器兜底下载会使用你本机已经登录的浏览器会话读取视频详情页，并尝试获得可播放地址。
- 抖音评论采集器会读取页面文本；如果不加 `--skip-network`，还可能检查浏览器捕获到的网络响应。主流程默认使用 `--skip-network` 做保守采集。
- 请只分析你有权分析的内容，并遵守对应平台规则和当地法律。

## 仓库结构

```text
SKILL.md
scripts/
  run_viral_video.py
  build_viral_package.py
  run_faster_whisper_asr.py
  run_funasr_asr.py
  collect_douyin_comments_browser_act.py
references/
  local-setup.md
  output-style.md
  portable-setup.md
```

## License

MIT
