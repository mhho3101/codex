# viral-hook-script-skill

爆款 3 秒钩子与节奏化短视频脚本生成器，用于把主题、原稿、产品说明、课程内容或播放数据转化为可拍摄、可录音、可剪辑、可发布的短视频方案。

## 功能列表

- 内容定位分析
- 目标用户画像
- 核心卖点提炼
- 20 个 3 秒钩子
- 钩子评分与 Top 5 推荐
- 15 秒、30 秒、60 秒口播稿
- 镜头级导演分镜
- 口播节奏、停顿、重读、字幕、BGM、音效设计
- 关键点图示设计
- 标题、封面文字、简介、标签、置顶评论、CTA
- A/B 测试方案
- 发布后数据诊断建议

## 文件结构

```text
viral-hook-script-skill/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── LICENSE
├── agents/openai.yaml
├── prompts/
├── templates/
├── examples/
├── evals/
└── docs/
```

## 使用方法

在 Codex 中调用：

```text
使用 $viral-hook-script-skill
主题：老师如何用 AI 提高备课效率
平台：视频号
时长：30 秒
目标用户：中小学教师
目标：提高收藏和关注
模式：完整导演版
```

## 输入示例

```text
主题：老师如何用 AI 提高备课效率
平台：视频号
时长：30 秒
目标用户：中小学教师
目标：提高收藏和关注
模式：完整导演版
```

## 输出示例

输出会包含任务识别、内容定位、20 个钩子、Top 5、最佳钩子、15/30/60 秒脚本、导演分镜、声画节奏、发布文案、A/B 测试和复盘规则。

## 快速模式

用户输入 `快速生成` 时，只输出 10 个钩子、最佳钩子、30 秒脚本、简版分镜、标题和封面。

## 完整导演模式

用户输入 `完整导演版` 时，输出全部模块，适合正式拍摄前准备。

## 自定义平台

支持视频号、抖音、小红书、B站、TikTok、Reels。未指定平台时默认视频号。

## 自定义时长

支持 15 秒、30 秒、60 秒。未指定时默认 30 秒，同时可生成三个版本。

## 运行测试

```bash
python3 /Users/keli/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/keli/Documents/口播导演-原创/viral-hook-script-skill
```

人工回归测试见 `evals/test-cases.md` 和 `evals/regression-checklist.md`。

## 如何扩展模板

- 新平台规则加入 `docs/platform-rules.md`
- 新钩子公式加入 `docs/hook-formulas.md`
- 新图示结构加入 `docs/key-visuals-guide.md`
- 新输出格式加入 `templates/output-template.md`
- 新行业示例加入 `examples/`
- 新评测标准加入 `evals/eval-rubric.md`

## 版本记录

见 `CHANGELOG.md`。
