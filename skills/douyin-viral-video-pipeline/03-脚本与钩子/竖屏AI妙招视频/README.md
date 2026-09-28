# AI 短视频skill · ai-video-creator

> 一个 [Claude Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) —— 把一个生活妙招选题,端到端做成**可直接发布的竖屏 AI 短视频(自带 AI 配音)**。

[![下载 .skill](https://img.shields.io/github/v/release/Frank-oll/ai-video-creator?label=下载%20.skill&color=blueviolet)](https://github.com/Frank-oll/ai-video-creator/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/平台-抖音%20%7C%20小红书%20%7C%20视频号-ff2c55.svg)
![Gateway](https://img.shields.io/badge/单网关-火山引擎%20ARK-orange.svg)

**English:** An end-to-end Claude skill that turns one "life-hack" idea into a publish-ready 9:16 short
video — consistent storyboard images → image-to-video clips with **native AI voiceover** → auto-stitched
final cut. Single gateway (Volcengine ARK), single key. All generation prompts are in Chinese by design
(Seedream / Seedance are ByteDance models tuned for Chinese semantics).


## 它做什么

```
问方向 → 热门检索/对标视频拆解 → 选题对齐 → 双锚定方案(视觉+叙事) → 分镜脚本
→ 生成 N 张一致性分镜静图(火山 Doubao-Seedream-5.0-lite)
→ 并发生成 N 段 I2V 视频,带原生 AI 配音(火山 Doubao-Seedance-1.5-pro)
→ ffmpeg 自动拼接成片
```

默认结构 **3 镜 × 5 秒 = 15 秒,9:16 竖屏**(可调)。最终交付:

- **`final.mp4`** — 成片,自带 AI 配音,可直接发布
- 分镜静图(PNG)+ 分段视频(MP4,各自带配音,供剪映精修)
- `storyboard.xlsx` 分镜表 + `voiceover-script.txt` 口播稿 + 后期指引

## 三档确认模式

| 模式 | 说法示例 | 体验 |
|------|---------|------|
| 标准(默认) | — | 选题/锚定/分镜/成本/基准图逐步确认,适合首次或新方向 |
| 快速 | "快速来一条""老规矩" | 一份完整方案一次确认 + 成本确认,两次交互出片 |
| 托管 | "直接做完给我" | 只确认成本,做完交付并汇报所有决策 |

偏好(方向/人群/音色/模式)会被记住,第二次使用一句话带过。

## 架构:单 key + 火山纯生态

| 用途 | 网关 | 默认模型 |
|------|------|------|
| 图片生成 | 火山引擎 ARK | `doubao-seedream-5-0-lite` |
| 视频生成 + 配音 | 火山引擎 ARK | `doubao-seedance-1-5-pro-251215` |
| 拼接成片 | 本地 ffmpeg | concat + stream copy(失败自动重编码) |

只要一个 `ark-` 开头的 key。模型可用 `--model` 热替换(换 Seedance 1.0 系列更便宜但
**无音频**;成本估算会按实际模型单价算)。

## 安装

### 1. 获取 skill

**方式 A · git clone(推荐,方便 `git pull` 更新):**

```bash
git clone https://github.com/Frank-oll/ai-video-creator.git
```

把整个目录放进你的 agent 的 skills 目录:

- **Claude Code**:放到 `~/.claude/skills/ai-video-creator/`(目录里直接是 `SKILL.md`)
- **claude.ai**:Settings → Skills → Upload(先把目录打包成 `.skill` / zip 再上传)
- 其他遵循 SKILL.md 规范的 agent(Kimi 等):放进各自的 skills 目录

**方式 B · 下载 [`.skill` / `.zip` 包](https://github.com/Frank-oll/ai-video-creator/releases/latest)**(在 Release 页),直接上传到 claude.ai(Settings → Skills → Upload)。

### 2. 安装依赖

```bash
pip install -r requirements.txt      # requests + openpyxl
# ffmpeg(拼接/抽帧用,强烈推荐):
brew install ffmpeg          # macOS
sudo apt install ffmpeg      # Ubuntu/Debian
# Windows: https://www.gyan.dev/ffmpeg/builds/ 下载,bin 加 PATH
```

### 3. 配置火山 ARK key

注册 https://www.volcengine.com/ 并实名 → 进方舟控制台 https://console.volcengine.com/ark →
「模型管理」免费开通 **Doubao-Seedream-5.0-Lite** 和 **Doubao-Seedance-1.5-Pro** →
「API Key 管理」新建 key(以 `ark-` 开头)。余额建议 ≥ ¥10。

## 支持的智能体(跨平台)

本 skill 遵循通用的 **SKILL.md / Agent Skill 规范**,不绑定单一客户端。除了 Claude Code、
claude.ai,理论上也能放进其他兼容该规范的智能体使用,例如 **WorkBuddy、Marvis、OpenClaw、
Hermes** 等。

> ⚠️ **使用效果因模型而异**:本 skill 重度依赖宿主智能体的底层模型能力——多模态自检(看图判断
> 画面一致性)、中文语义理解、命令行/工具调用、长流程编排。不同智能体接入的模型不同,**出片
> 质量与稳定性会有差异**;能力较弱的模型可能需要更多人工确认或重试。建议优先选用多模态和中文
> 能力较强的模型,以获得最佳效果。

## 首次使用

在 chat 里说:**"做一条妙招短视频"**(或直接说方向:"做一条阳台种菜的短视频")。

agent 会:索要并验证 key(配置时就把模型开通问题预检出来)→ 问方向 → 检索热门/拆解你给的
对标 → 出选题和方案 → 确认成本(默认配置约 $0.27 ≈ ¥2)→ 生成(每张图、每段视频 agent
先自检再交付)→ 拼接成片。

## 成本与耗时(默认 3 镜 × 5s)

| 项目 | 估算 |
|------|------|
| Seedream 生图 × 3 | ~$0.06 |
| Seedance 1.5 pro(含配音)15s | ~$0.21 |
| 合计 | **~$0.27 ≈ ¥2**(自检重试可能 +0~2 次生图) |

视频 3 镜并发生成约 1-4 分钟。真实单价以火山控制台账单为准。

## 文件结构

```
ai-video-creator/                   # 仓库根 = skill 根(SKILL.md 里 name: ai-video-sannong)
├── SKILL.md                        # 工作流主干(给 agent 读)
├── README.md                       # 本文件(给人读)
├── LICENSE                         # MIT
├── requirements.txt                # Python 依赖
├── scripts/api_client.py           # 全部 API 调用封装(火山 ARK + ffmpeg)
├── profiles/                       # 题材包(可扩展)
│   ├── _template.md                #   新题材现场生成模板
│   ├── sannong.md                  #   三农园艺
│   └── home-hacks.md               #   家居清洁收纳
├── references/                     # 按需查阅
│   ├── voice-presets.md            #   配音音色详解(6 preset + 方言)
│   ├── troubleshooting.md          #   故障排查
│   └── post-editing-guide.md       #   剪映后期指引模板
├── templates/sample_visual_anchor.md   # 双锚定 + prompt 完整范例
└── examples/case_gemini_analysis.md    # 对标拆解报告范例
```

生成的项目落在 `output/<日期-选题>/`,每条视频独立目录,含 `project.json` 状态档案
(支持断点续传、单镜重做)。

## 常见问题

- **模型未开通?** 不是 bug,火山要求控制台手动点「开通」(免费)。配置阶段的预检会直接
  告诉你差哪个。详见 `references/troubleshooting.md`。
- **配音能换吗?** 6 个内置 preset(含男声)+ 方言 + 完全自定义,见
  `references/voice-presets.md`。
- **想做新题材?** 直接说,agent 会现场生成题材包并可保存复用(`profiles/_template.md`)。
- **想要更便宜?** `--model doubao-seedance-1-0-pro-fast-251015`(省 ~40%,无配音,
  剪映"文本朗读"补)。
- **没装 ffmpeg?** 不阻断,拿 3 段分段 mp4 去剪映手动拼。
- **修改 skill 后**:重新 zip 成 `.skill` 重传 claude.ai(改动不自动同步)。

## 限制

- 不支持人物对话/表演类视频(跨镜身份一致性受限;末镜露脸+CTA 可选但有翻车率)
- 不支持复杂多步骤工艺(镜头数有限)、背景频繁切换的视频
- AI 配音支持中文(普通话 + 四川/粤语等方言)、英文、日韩西语,小语种不支持

## 贡献

欢迎 PR 和 Issue,尤其是这几类:

- **新题材包**:照 `profiles/_template.md` 写一个新 `profiles/<拼音slug>.md`(美食、宠物、
  育儿、手工……),让更多垂类开箱即用。记得认真填「安全红线」字段。
- **音色 preset**:在 `scripts/api_client.py` 的 `VOICE_PRESETS` 里加新音色,并在
  `references/voice-presets.md` 补说明。
- **对标拆解 / 双锚定范例**:好的范例能显著提升新手出片质量,参考 `examples/`、`templates/`。
- **Bug、prompt 翻车 case、新模型适配**:开 Issue 时尽量贴上选题、报错原文和 `project.json`。

提交前请确认**没有把任何 API key、`output/` 产物、本地配置**带进 commit(`.gitignore` 已覆盖常见情况)。

## 免责声明

- **第三方服务**:本 skill 调用火山引擎 ARK(Doubao Seedream / Seedance)生成图片与视频,
  产生的费用、内容合规与服务可用性由火山引擎及使用者自行负责,本项目不收取任何费用。
- **成本仅为估算**:README 与 `estimate-cost` 给出的金额是基于公开报价的估算,**真实账单以
  火山控制台为准**。
- **AI 生成内容**:成片为 AI 生成,发布到各平台时请遵守平台关于「AI 生成内容」的标识要求与
  内容规范;请勿用于生成误导性、违法或侵权内容。
- 本软件按「现状」提供,不附带任何担保,详见 [LICENSE](LICENSE)。

## 许可证

[MIT](LICENSE) © 2026 Frank

---

🎬 觉得有用的话,点个 ⭐ Star 支持一下,也欢迎把你做出来的成片来交流。
