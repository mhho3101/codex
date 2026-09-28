# Codex 技能包

将你的 Codex 自定义技能托管在 GitHub 上，实现多设备同步。

## 包含的技能（30 个）

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
| slide-maker | 制作、重做和审查演示文稿：先确认受众和目标，再完成叙事、设计和 PPTX 产出。 |
| ppt-design-skill | 基于 pptx-designer 生成、审查和修订可编辑 PowerPoint，包含 brief 到 PNG 视觉验收流程。 |
| gpt-image2-ppt | 使用 gpt-image-2 和多种视觉风格生成整页高分辨率幻灯片，并打包为 16:9 PPTX。 |
| academic-pptx | 面向会议报告、组会、论文答辩和基金汇报的学术演示内容与论证结构。 |
| consulting-pptx-skill | 经营管理与咨询风格幻灯片：约 80 条版式规则、62 种 HTML 版式部件，输出 HTML 和 PDF。 |
| autocad-automation | AutoCAD 自动化：DWG/DXF 绘图、图层、文字、块、标注、批处理、SCR/AutoLISP/.NET 辅助。 |
| solidworks-automation | SolidWorks CAD 自动化：零件、孔槽、装配、工程图、导出和交付复核，能力以 capabilities.yaml 为准。 |
| douyin-viral-video-pipeline | 抖音爆款短视频全流程技能包：67 个开源项目 / 484 个 Agent Skill，覆盖选题→拆解→脚本→分镜→生成→剪辑→发布→复盘完整闭环。 |

## 抖音爆款短视频全流程技能包

`skills/douyin-viral-video-pipeline/` 从 GitHub 精选 **67 个开源项目**，去重、剪枝、本地化，封装为 **67 个技能包 / 484 个 Agent Skill**，
覆盖「选题 → 拆解 → 脚本 → 分镜 → 生成 → 剪辑 → 发布 → 复盘」完整闭环，收录项目累计 **100,700+ Star**。

先读入口文件，再看全流程 SOP：

| 文件 | 用途 |
|------|------|
| `README.md` | 技能包总览与 8 环节选型表 |
| `00-爆款全流程SOP.md` | 核心：一条抖音爆款的 8 阶段完整打法（含提示词模板） |
| `00-快速上手-15分钟出片.md` | 最快跑通路径 |
| `00-技能包评测报告.md` | 67 个包的评分、S 级详解与组合推荐 |
| `00-来源与许可清单.md` | 每包的 GitHub 地址、Star、许可证 |
| `技能包入口索引.csv` | 67 个包的入口文件 + Star + 许可证（先看这个） |
| `技能清单.csv` | 484 条技能总表 |

分类目录（每类下为独立技能包）：

- `01-选题与情报/`（4 包）　`02-爆款拆解/`（8 包）　`03-脚本与钩子/`（9 包）
- `04-分镜与视觉/`（7 包）　`05-AI生成/`（4 包）　`06-剪辑与合成/`（19 包）
- `07-发布与增长/`（6 包）　`08-动效与图形/`（10 包）

安装整套：

```
install-skill-from-github.py --repo mhho3101/codex --path skills/douyin-viral-video-pipeline
```

只装其中某个子包（推荐，按需取用）：

```
install-skill-from-github.py --repo mhho3101/codex --path "skills/douyin-viral-video-pipeline/03-脚本与钩子/爆款3秒钩子脚本"
```

> 起步最小组合（6 包）：`爆款视频拆解包` + `爆款3秒钩子脚本` + `抖音成片工作流` + `剪映AI自动化剪辑` + `电影级镜头配方` + `抖音自动发布`。

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



