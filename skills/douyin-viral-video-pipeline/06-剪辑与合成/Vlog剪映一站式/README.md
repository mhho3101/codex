<div align="center">

# 🎬 Vlog Jianying One‑Stop

### 从一句自然语言，到可发布成片与可继续编辑的剪映草稿

面向 Windows + 剪映专业版的 Codex Skill：把创作意图连续转化为拍摄脚本、事实时间线、镜头匹配、字幕、配乐、混音、审片和最终交付。

![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows11&logoColor=white)
![Editor](https://img.shields.io/badge/Editor-剪映专业版-111111?style=for-the-badge)
![Format](https://img.shields.io/badge/Default-9%3A16 · ~100s-FF4B6E?style=for-the-badge)
![Access](https://img.shields.io/badge/Repository-Public-2DA44E?style=for-the-badge&logo=github)

</div>

---

## 它解决什么问题

普通自动剪辑容易“有画面、没故事”。这个 Skill 把叙事和素材状态放在第一位：先建立 beat 故事与事实时间线，再判断镜头是否能承担故事任务，最后才处理节拍、字幕和特效。

```mermaid
flowchart LR
    A["一句自然语言 / 已有素材"] --> B["Beat 故事"]
    B --> C["低门槛拍摄脚本"]
    C --> D["事实时间线"]
    D --> E["宽容匹配与链式选片"]
    E --> F["剪映无 BGM 母版"]
    F --> G["字幕 · 配乐 · 混音"]
    G --> H["本能审片"]
    H --> I["成片 + 可编辑草稿"]
```

## 核心能力

| 模块 | 能力 |
|---|---|
| 🧠 故事规划 | 把自然语言拆成 `beat_00` 与完整故事段，兼顾叙事逻辑和真实时间 |
| 📱 拍摄指导 | 用“远景/中景/近景 + 画面行为 + 可选角度”生成低门槛拍摄清单 |
| 🧩 素材匹配 | 宽容匹配冗余素材，识别镜头起止状态、场景切换和可用过场 |
| ✂️ 剪映执行 | 建立连续时间线，保护原素材与旧草稿，交付可编辑剪映工程 |
| 💬 智能字幕 | 优先使用剪映识别字幕，统一主字幕、章节标题和场景标题 |
| 🎵 自动配乐 | 索引本地曲库、分析节拍、吸附画面切点，并在人声区间自动退让 |
| ✨ 克制特效 | 仅在情绪匹配时使用轻网感特效和音效，固定电视关机 + “晚安”片尾 |
| ✅ 质量检查 | 完整播放、本能审片，并用脚本验证时长、画幅、帧率和音视频流 |

## 两种工作模式

### A. 先规划，后拍摄

适合只有一个想法、还没有素材的项目。Skill 会先给出故事与拍摄方案，完成一次确认后持续推进。

> 使用 `$vlog-jianying-one-stop`，把“周末第一次学做陶艺”规划成一条约 100 秒的竖屏 Vlog。

### B. 已有素材，直接剪

适合素材已经拍完的项目。若故事线明确，会直接建立时间线并继续执行；若只有主题，会先给出少量可实现的故事提案。

> 使用 `$vlog-jianying-one-stop`，整理这个素材目录，剪成一条生活记录 Vlog，并保留可编辑剪映草稿。

## 默认成片规格

- 平台：抖音，也适合小红书竖屏内容
- 画幅：`9:16`
- 时长：约 `100 秒`，通常落在 `90–110 秒`
- 输出：`1080 × 1920`、`30 fps`、H.264、AAC 48 kHz、Rec.709 SDR
- 风格：生活记录、真实情绪、快慢交替，故事优先于炫技
- 声音：人物原声优先；对白和关键互动出现时，BGM 自动退让

## 安装方法（小白版）

安装完成的判断标准很简单：下面这个文件必须存在。

```text
%USERPROFILE%\.agents\skills\vlog-jianying-one-stop\SKILL.md
```

> Codex 官方将 `$HOME/.agents/skills` 作为个人 Skill 目录。安装后通常会自动检测；如果没有出现，重新启动一次 Codex。

### 方法一：让 Codex 自动安装（推荐）

在 Codex 新任务中输入：

```text
$skill-installer
请从 https://github.com/iamcrisiloveyoutoo-commits/vlog-jianying-one-stop 安装这个 Skill
```

Codex 完成安装后，重新打开一个任务并输入 `$vlog-jianying-one-stop` 即可使用。

### 方法二：下载 ZIP，不用命令行

1. 点击本页面右上方绿色 **Code** 按钮。
2. 点击 **Download ZIP**。
3. 解压下载的文件。
4. 按 `Win + R`，输入 `%USERPROFILE%\.agents\skills` 并回车。
5. 如果该目录不存在，就依次新建 `.agents` 和 `skills` 文件夹。
6. 把解压后的仓库文件夹复制进去，并将文件夹命名为 `vlog-jianying-one-stop`。
7. 检查 `SKILL.md` 是否直接位于该文件夹内，然后重新启动 Codex。

正确结构：

```text
%USERPROFILE%\.agents\skills\
└── vlog-jianying-one-stop\
    ├── SKILL.md
    ├── agents\
    ├── references\
    └── scripts\
```

常见错误是多套了一层目录：

```text
# 错误：Codex 可能找不到 SKILL.md
...\vlog-jianying-one-stop\vlog-jianying-one-stop-main\SKILL.md
```

### 方法三：使用 Git 安装

电脑已经安装 [Git for Windows](https://git-scm.com/download/win) 时，在 PowerShell 运行：

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
git clone https://github.com/iamcrisiloveyoutoo-commits/vlog-jianying-one-stop.git "$HOME\.agents\skills\vlog-jianying-one-stop"
```

以后更新 Skill：

```powershell
git -C "$HOME\.agents\skills\vlog-jianying-one-stop" pull
```

如果只想让当前项目使用它，可克隆到项目根目录：

```powershell
git clone https://github.com/iamcrisiloveyoutoo-commits/vlog-jianying-one-stop.git ".agents\skills\vlog-jianying-one-stop"
```

### 安装运行依赖

| 依赖 | 是否必需 | 用途 |
|---|---:|---|
| Windows | 是 | 当前 Skill 面向 Windows 工作流 |
| Codex 桌面端、CLI 或 IDE 扩展 | 是 | 加载和执行 Skill |
| 剪映专业版 | 是 | 时间线、字幕、特效、草稿和导出 |
| FFmpeg / FFprobe | 自动处理视频时需要 | 媒体分析、预览、混音和导出验证 |
| PowerShell | 运行脚本时需要 | 执行素材盘点和媒体处理脚本 |
| Python 3 | 部分流程需要 | 音乐索引与本地转写备用方案 |
| `librosa` | 可选 | 更细致的音乐节拍分析 |

FFmpeg 可从 [官方网站](https://ffmpeg.org/download.html) 获取。安装完成后，在 PowerShell 检查：

```powershell
ffmpeg -version
ffprobe -version
python --version
```

只要前两个命令能显示版本号，视频分析与混音脚本就具备了基础运行条件。没有 `librosa` 时仍可继续半自动配乐流程。

### 检查是否安装成功

你可以任选一种方式验证：

- Codex 桌面端：打开侧边栏的 **Skills**，查找 `vlog-jianying-one-stop`。
- Codex CLI / IDE 扩展：输入 `/skills` 查看列表。
- 在任务中输入 `$`，检查是否能选择 `$vlog-jianying-one-stop`。

如果列表中没有：

1. 确认文件不是 ZIP，而是已经解压的文件夹。
2. 确认 `SKILL.md` 直接位于 `vlog-jianying-one-stop` 文件夹中。
3. 确认安装位置是 `%USERPROFILE%\.agents\skills`。
4. 关闭并重新启动 Codex。

### 第一次怎么用

只有想法、还没拍素材：

```text
使用 $vlog-jianying-one-stop，把“周末第一次学做陶艺”规划成一条约 100 秒的竖屏 Vlog，先给我低门槛拍摄脚本。
```

已经拍完素材：

```text
使用 $vlog-jianying-one-stop，分析 D:\我的Vlog素材，剪成约 100 秒的 9:16 生活记录 Vlog，并保留可编辑剪映草稿。
```

安装与 Skill 机制可参考 [OpenAI 官方 Skills 文档](https://learn.chatgpt.com/docs/build-skills)。

## 自动化脚本

| 脚本 | 用途 |
|---|---|
| `inventory-media.ps1` | 盘点媒体文件与基础元数据 |
| `build-real-timeline.ps1` | 根据媒体时间重建事实时间线 |
| `prepare-review-frames.ps1` | 生成素材预览帧，辅助理解画面 |
| `build-music-index.py` | 建立本地音乐库索引与节拍侧文件 |
| `transcribe-dialogue.py` | 剪映智能字幕失败时的本地转写备用方案 |
| `mix-bgm.ps1` | 画面切点、BGM、人声闪避与最终混音 |
| `verify-export.ps1` | 检查成片时长、画幅、帧率和音视频流 |

## 项目结构

```text
vlog-jianying-one-stop/
├── SKILL.md                     # 主工作流与触发说明
├── agents/
│   └── openai.yaml              # Skill 展示与默认提示词
├── references/
│   ├── l3-planning.md           # 自然语言到拍摄脚本
│   ├── coverage-and-matching.md # 素材覆盖与链式选片
│   ├── editing-defaults.md      # 剪辑默认规则
│   ├── subtitle-system.md       # 字幕与标题系统
│   ├── effects-and-sfx.md       # 特效与音效白名单
│   ├── bgm-auto.md              # 自动/半自动配乐
│   └── jianying-execution.md    # 剪映执行与草稿交付
└── scripts/                     # 素材、音乐、混音与验片工具
```

## 设计原则

1. **故事优先**：画面服务于 beat，不用漂亮素材挤压完整叙事。
2. **宽容匹配**：景别与角度是提示，不是拒绝普通素材的门槛。
3. **时间可信**：高可信拍摄时间用于防穿帮，但不推翻用户明确的故事顺序。
4. **人声优先**：字幕不能补救听不清的人声，BGM 必须主动让位。
5. **保护原件**：不移动、不覆盖、不删除原素材、音乐原件和已有草稿。
6. **可继续编辑**：成片之外，始终保留独立轨道和可编辑剪映草稿。

## 使用前注意

- `SKILL.md` 内的 `E:\codex\VLOG剪辑工作区` 是当前默认备份目录，可按你的机器环境修改。
- 本项目不会下载或分发有版权的音乐；自动配乐只使用你拥有使用权的本地曲库。
- 剪映登录、安全验证、付费扩容等账号操作仍需账号持有人确认。
- 自动化不能替代最终完整播放；画面、情绪和声音仍以人工可感知结果为准。

---

<div align="center">

**让自动剪辑先学会讲故事，再学会踩点。**

</div>
