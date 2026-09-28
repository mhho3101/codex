# video-story-clip

把一部完整电影剪成 **8-15 条可直接发布的短视频**（每条 50-75 秒）——AI 规划片段，脚本无损切割。为抖音 / 快手 / 短剧切片 / 影视解说创作者打造。

[English](./README.md) | 中文

## 关于作者

**韩洋（Han Yang）**——做 AI 内容创作工作流的开发者。

做这个 Skill 的起因：把一部 2 小时的电影剪成短视频，过去我要花一整天看片、回放、精剪。现在只需要几分钟就可以给你把故事捋顺剪辑出片段，同时给出对应的txt文件，然后你自己去剪映或其他地方去加旁白精修。而且每剪一部电影，我都会把踩过的坑沉淀成新的规则，这个 Skill 也随之更新。

- 微信：`hhhhhh_h`（加好友请备注"**GitHub**"）
- 邮箱：`hanyang_cg@126.com`

## 这个 Skill 能做什么

1. **AI 读你的字幕文件**（SRT）规划 8-15 条主题片段——每条 50-75 秒，一条只讲一个事，快剪串烧风（每条 3-7 个碎片）
2. **无损切割**——画质 100% 等于原片（`-c copy`，秒级完成）；需要精确到秒用 `--reencode`
3. **自动拼接**——每条视频的碎片自动拼成一个完整 mp4（与目录同名），碎片同时保留；`--no-merge` 可关闭
4. **对应关系文件**——每条视频附带 `.txt`，列出碎片构成、旁白建议、原片对白参考
5. **无字幕段扫描**（`find_gaps.py`）+ **输出验证**（`verify_clips.py`）

## 安装

**一键安装（推荐）**：

```bash
git clone https://github.com/hanyangcg/video-story-clip.git && cd video-story-clip

# WorkBuddy
./install.sh --target ~/.workbuddy/skills

# Claude Code
./install.sh --target ~/.claude/skills

# Codex
./install.sh --target ~/.codex/skills

# 自定义目录
AGENT_SKILLS_DIR=~/.agents/skills ./install.sh
```

**手动安装**：克隆仓库后，把整个文件夹复制到 AI 助手的 skills 目录（如 `~/.workbuddy/skills/`），保持文件夹名不变。

**环境要求**：Python 3.9+、ffmpeg/ffprobe（加入 PATH 或在 JSON 配置里写全路径）、支持 Skill 的 AI 助手。

**环境兼容状态**：本 Skill 使用标准 `SKILL.md` 结构（含 `name` + `description` frontmatter），安装脚本可在任何 bash 环境运行。**已在 WorkBuddy 验证通过**。Claude Code 与 Codex 使用相同的 skill 目录约定——若首次加载未触发，请确认你的助手确实从目标目录读取 skills。

## 使用方法

这个 Skill 不是独立程序，需要配合 AI 助手（WorkBuddy / Claude Code / Codex）使用：

1. **准备素材**：原片视频 + SRT 字幕文件；最好再告诉 AI 片头片尾的时间点、提供剧情梗概（剪辑更精准）
2. **让 AI 干活**：把字幕交给 AI，说"帮我把这部电影剪成 8-15 条短视频，每条 50-75 秒"——AI 会按 SKILL.md 里的流程执行
3. **确认方案**：AI 会先列出剧情时间线场景清单供你确认，确认后生成切割方案（SEGMENTS）
4. **自动切割**：AI 调用 `cut_clips.py` 无损切割并拼接，输出每条视频 + 对应的 txt 文件
5. **精修发布**：在剪映 / CapCut 里加旁白、字幕、背景音乐，导出发布

命令行操作见下方「快速开始」。

## 快速开始

```bash
# 1. 复制模板，填入电影路径
cp assets/movie_config_template.json 我的电影.json
#    编辑 src / out_dir / ffmpeg / ffprobe

# 2. 让 AI 助手分析字幕并生成剪辑方案
#    "帮我分析 我的电影.srt，生成剪辑方案写入 我的电影.json"
#    （AI 会参照 references/style_guide.md 规划片段）

# 3. 执行切割（默认无损）
python scripts/cut_clips.py --config 我的电影.json

#    精确到秒
python scripts/cut_clips.py --config 我的电影.json --reencode

# 4. 验证输出
python scripts/verify_clips.py "输出目录"
```

## 使用技巧

- **提供片头片尾时间点**：使用前最好人工告诉 AI 电影片头和片尾的时间点，这样剪辑更精准，避免片头片尾混进片段里。
- **提供剧情梗概**：使用时最好提供电影的剧情梗概，这样有助于 AI 理解剧情，剪辑更精准。

## 目录结构

```text
video-story-clip/
├─ SKILL.md                     # Skill 入口（流程 + 强约束）
├─ install.sh                   # 一键安装脚本
├─ manifest.json                # Skill 清单（名称 / 版本 / 入口）
├─ README.md                    # 英文文档
├─ README.zh.md                 # 中文文档
├─ LICENSE                      # MIT 协议
├─ references/
│  ├─ style_guide.md            # 基础剪辑风格规则（AI 生成方案时参照）
│  └─ requirements.md           # 需求规范
├─ assets/
│  └─ movie_config_template.json # 配置文件模板
├─ scripts/
│  ├─ cut_clips.py              # 核心：读 JSON 配置，切割 + 拼接
│  ├─ find_gaps.py              # 无字幕段扫描
│  └─ verify_clips.py           # 输出验证
├─ tools/
│  └─ validate_skills.py        # 发布校验（frontmatter + 泄露扫描）
└─ tests/
   └─ test_validate_skills.py   # 校验器单元测试
```

## 环境要求

- Python 3.9+
- ffmpeg / ffprobe（加入 PATH，或在 JSON 配置里写全路径）
- **支持 Skill 的 AI 助手**（WorkBuddy / Claude Code / Codex / OpenClaw）——这不是独立程序：AI 负责规划，脚本负责执行

## 支持

如果这个 Skill 帮你省了时间，那它就是有价值的。

- **定制 AI 工作流**（影视解说工作室 / 切片矩阵 / 个人生产管线）或商业合作，发邮件描述你的场景，我会推荐最合适的方案
- 微信：`hhhhhh_h` · 邮箱：`hanyang_cg@126.com`

## License

MIT License。本仓库只包含工具脚本与说明文档，不包含任何受版权保护的影视素材。

## 免责声明

请对有使用权的内容使用本工具。发布前自行确认素材版权，遵守平台规则与当地法律。
