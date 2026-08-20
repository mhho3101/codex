# Codex 技能包

将你的 Codex 自定义技能托管在 GitHub 上，实现多设备同步。

## 包含的技能（22 个）

| 技能 | 说明 |
|------|------|
| agent-video-pipeline | Build, resume, and quality-control a cross-agent, editable video pipeline using ChatCut for source ingestion, ... |
| chatcut-plugin-basics | Use for video editing or video creation work that should be editable in ChatCut, even when the user does not e... |
| claude-vision | 让无法原生识图的模型获得图片识别能力。当用户分享本地或网络图片路径、消息中出现图片附件、或要求分析/描述/识别图片内容时使用。通过调用阿里云百炼(DashScope)的视觉模型API，将图片转为base64并发送给视觉模... |
| claude-vision-skill | Use when the user shares, pastes, or references an image (local path or URL) and you need to describe, analyze... |
| data-visualization | 数据可视化——用 Python(matplotlib/plotly)、HTML 图表把数据变成清晰的可视化图形，可导出为视频画面所需的图表素材。需要制作图表、信息图、数据动画时使用本技能。 |
| define-goal | Help the user define a concrete, measurable goal before starting work, especially when they ask to use the goa... |
| ffmpeg-video-processing | ffmpeg 视频处理命令专项——裁剪、拼接、转码、压缩、字幕烧录、音频处理、变速、抽帧与批量处理。处理音视频文件时使用本技能。 |
| firecrawl | Search, scrape, and interact with the web via the Firecrawl CLI. Use this skill whenever the user wants to sea... |
| folder-organizer | Conservative folder organization assistant for scanning directories, reading file names, metadata, and sampled... |
| gepeto | Guide for building 1-click launchers and building apps with launchers built-in using Pinokio |
| hyperframes | Mandatory entry point: read this first for any request to make, create, edit, animate, or render a |
| karpathy-guidelines | Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code t... |
| mcp | 模型上下文协议（Model Context Protocol, MCP）——概念、MCP 服务器配置、客户端接入、工具/资源暴露与故障排查。涉及 MCP、上下文协议、连接外部工具/数据源时使用本技能。 |
| pinokio | Discover, launch, and use apps and tools for the current task. |
| remotion-best-practices | Router for all Remotion skills |
| screenshot | Use when the user explicitly asks for a desktop or system screenshot (full screen, specific app or window, or ... |
| seedance-25 | Create, improve, extend, edit, or troubleshoot Seedance 2.5 videos and paste-ready prompts, especially on 即梦/D... |
| skill-creator | Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to c... |
| superpowers | Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before... |
| tmeet | 腾讯会议 CLI（tmeet）：OAuth 授权登录/登出/状态查询、会议管理（创建/更新/取消/查询/受邀者）、录制管理（列表/播放地址/智能纪要/转写/录制权限申请）、会议报告（参会人/等候室/导出参会成员明细/异步... |
| tmeet-skill | 腾讯会议 CLI（tmeet）：OAuth 授权登录/登出/状态查询、会议管理（创建/更新/取消/查询/受邀者）、录制管理（列表/播放地址/智能纪要/转写/录制权限申请）、会议报告（参会人/等候室/导出参会成员明细/异步... |
| video-production | 端到端视频制作工作流——需求梳理、脚本/分镜、素材准备、剪辑、音频、字幕与导出。用户要求制作任何视频时使用本技能。 |

## 安装方法

在每台电脑的 Codex 对话中，直接使用 skill-installer 安装：

```
install-skill-from-github.py --repo mhho3101/codex --path skills/技能名
```

或者让 Codex 帮你安装："帮我从 mhho3101/codex 安装 skills/技能名 技能"

## 更新技能流程

在一台电脑上修改技能后：

```bash
# 1. 更新仓库中的技能文件
# 2. 提交并推送
git add .
git commit -m "更新技能描述"
git push

# 3. 在另一台电脑上重新安装（会覆盖旧的）
install-skill-from-github.py --repo mhho3101/codex --path skills/技能名
```

## 环境变量

claude-vision-skill 需要 .env 配置（已在 .gitignore 中排除）。
参考 `skills/claude-vision-skill/.env.example` 创建自己的配置，**不要提交真实密钥到仓库**。



