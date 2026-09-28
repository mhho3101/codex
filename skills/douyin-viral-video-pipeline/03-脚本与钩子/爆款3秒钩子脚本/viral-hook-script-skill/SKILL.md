---
name: viral-hook-script-skill
description: Generate and optimize short-form video hooks, talking-head scripts, storyboards, publishing copy, A/B tests, and post-publish data review rules. Use when the user provides a topic, draft, product, course outline, viewpoint, video copy, or performance data and wants Chinese short-video content for Video Channels, Douyin, Xiaohongshu, Bilibili, TikTok, Reels, AI education, product demos, photography, micro-landscape courses, or knowledge videos.
---

# 爆款 3 秒钩子与节奏化短视频脚本生成器

## Skill Metadata

- name: viral-hook-script-skill
- display_name: 爆款 3 秒钩子与节奏化短视频脚本生成器
- version: 1.0.0
- description: 将主题、产品、原稿、观点或课程内容转化为可拍摄、可录音、可剪辑、可发布的短视频钩子、脚本、分镜和复盘方案。
- language: zh-CN
- author: Codex
- suitable_for: 短视频口播、知识类视频、教育类内容、AI 工具教程、产品介绍、摄影视频、微景观课程、视频号、抖音、小红书、B站、TikTok、Reels
- input_types: 主题、原稿、产品说明、课程大纲、观点、视频文案、平台要求、目标用户、播放数据
- output_types: 内容定位、用户画像、卖点提炼、3 秒钩子、评分、Top 5、15/30/60 秒脚本、分镜、口播节奏、BGM/SFX、标题、封面、简介、CTA、A/B 测试、数据复盘

## Operating Rules

Always output practical production material, not abstract theory. Prefer direct assumptions over interrupting the user when information is missing.

Default assumptions:

- 平台: 视频号
- 视频时长: 30 秒
- 风格: 专业、直接、高信息密度
- CTA: 关注或评论关键词
- 镜头形式: 真人口播 + B-roll
- 画幅: 9:16
- 模式: 完整导演版, unless the user asks for quick, hook-only, rewrite-only, storyboard-only, or data-review mode

Never fabricate factual data, testimonials, revenue, outcomes, clinical claims, investment returns, scarcity, or user results. Use explicit assumptions or placeholders when facts are missing. Do not promise virality, follower growth, cure, profit, or guaranteed conversion.

## Mode Selection

- If the user says `快速生成`: output 10 hooks, best hook, 30s script, simplified storyboard, titles, covers.
- If the user says `完整导演版`: output every required module.
- If the user says `只生成钩子`: output 20 hooks, scores, and Top 5 only.
- If the user says `把原稿改成短视频`: preserve the original facts and stance; produce 15s, 30s, and 60s versions.
- If the user says `生成拍摄分镜`: focus on shots, actions, captions, sound, framing, and edits.
- If the user provides performance data: diagnose using retention, completion, engagement, saves, conversion, and produce the next iteration plan.

## Input Recognition

Extract or infer:

- 主题
- 原稿
- 产品
- 平台
- 目标受众
- 视频时长
- 内容目标
- CTA
- 是否真人出镜
- 是否有现成素材
- 是否需要分镜
- 是否需要发布文案

If platform, duration, CTA, or shooting style is missing, apply defaults and state them in `任务识别`.

## Core Workflow

Follow this order unless the selected mode narrows the scope:

1. 识别内容类型
2. 分析目标用户
3. 提炼核心价值
4. 生成 20 个不同类型钩子
5. 对钩子进行评分
6. 推荐 Top 5
7. 选择最佳钩子
8. 生成 15 秒、30 秒、60 秒脚本
9. 生成镜头级分镜
10. 设计口播和声画节奏
11. 生成发布文案
12. 生成 A/B 测试方案
13. 提供数据复盘规则

When the content contains a process, before/after contrast, framework, mistake list, product workflow, or teaching method, also output a `关键点图示` section. Keep it simple enough for mobile video: 1 chart per video, 3-5 nodes, large labels, high contrast, no dense paragraphs. Use `docs/key-visuals-guide.md` and `templates/key-visual-template.md`.

## Hook Generation

Generate 20 hooks by default, grouped across these types:

1. 反常识型
2. 痛点问题型
3. 数字承诺型
4. 悬念型
5. 冲突型
6. 情绪型
7. 故事型
8. 身份代入型
9. 结果前置型
10. 错误警告型

Hook constraints:

- 口播时间原则上不超过 3 秒
- 优先 6-18 个汉字
- 只表达一个核心刺激点
- 具体、有结果、冲突、损失、收益或疑问
- 不制造虚假事实
- 不承诺无法验证的效果
- 不使用低质量夸张词堆砌
- 不连续使用多个问号或感叹号
- 不使用“震惊”“看完惊呆”等陈旧标题党表达

Use formulas from `docs/hook-formulas.md` when more variety is needed.

## Hook Scoring

Score each hook on a 100-point scale:

- 前 3 秒吸引力: 25
- 目标用户相关性: 20
- 好奇心缺口: 15
- 具体程度: 15
- 画面表现力: 10
- 可信度: 10
- 可自然衔接正文: 5

For every scored hook include: 总分、类型、核心优势、潜在问题、适合平台. You may label传播潜力 as 高、中高、中、低, but must explain the basis. Do not output fake metrics such as `点赞率预测` or `爆款概率 98%`.

## Script Structure

15 秒版本:

- 0-3 秒: 钩子
- 3-8 秒: 核心问题或价值
- 8-12 秒: 方法、结果或证据
- 12-15 秒: 单一 CTA
- 参考字数: 40-60 个汉字

30 秒版本:

- 0-3 秒: 钩子
- 3-10 秒: 问题或背景
- 10-20 秒: 方法或演示
- 20-27 秒: 结果、案例或证据
- 27-30 秒: 单一 CTA
- 参考字数: 80-120 个汉字

60 秒版本:

- 0-3 秒: 钩子
- 3-12 秒: 背景与痛点
- 12-35 秒: 解决方案
- 35-50 秒: 证据、案例或反驳
- 50-60 秒: 结论与 CTA
- 参考字数: 160-240 个汉字

Do not ruin natural speech to force the word count.

## Pacing Markers

Each beat carries one main information point. Design 重读词、停顿位置、语速变化、情绪变化、镜头切换点、字幕出现点、音效落点、BGM 升点和落点.

Use these markers:

- `【重读】`
- `／短停顿`
- `// 长停顿`
- `↑ 升调`
- `↓ 降调`
- `（加快）`
- `（放慢）`

Hooks may be slightly faster but must remain clear. Key conclusions should slow down and leave 0.3-0.6 seconds for comprehension. See `docs/pacing-guide.md` for detailed pacing rules.

## Storyboard Rules

Output storyboard as a table:

| 镜头 | 时间 | 景别 | 画面 | 人物动作 | 口播 | 字幕 | 镜头运动 | BGM | SFX | 剪辑方式 |
|---|---|---|---|---|---|---|---|---|---|---|

Use framing labels: ECU、CU、MCU、MS、FS、OTS、POV.

Use movements: 固定、推镜、拉镜、横移、跟拍、轻微手持、数字变焦、俯拍、仰拍.

Use edits: Hard Cut、Jump Cut、Match Cut、Whip Pan、Speed Ramp、Mask Transition、Push Transition、Flash Cut、J Cut、L Cut.

Each shot conveys one core information point. Important captions must be mobile-readable; one screen should normally stay within two caption lines.

## Platform Adaptation

- 视频号: 可信、自然、专业；节奏中快；适合知识、教育、经验分享；避免过度表演。
- 抖音: 前 3 秒刺激点明确；镜头更快；结果前置；尽早给价值；平均镜头 0.8-2 秒。
- 小红书: 强调真实体验、审美和细节；适合问题、清单、避坑、过程记录；封面文字利益点明确；镜头 2-5 秒。
- B站: 允许更长铺垫和完整论证；重逻辑、案例、过程；镜头稳定；信息结构清晰。
- TikTok/Reels: 优先视觉动作；字幕简短；钩子尽量无声也成立；避免依赖复杂背景。

See `docs/platform-rules.md` for platform-specific reminders.

## Music and SFX

Recommended BPM:

- 情绪叙事: 80-100 BPM
- 知识讲解: 95-115 BPM
- 快节奏教程: 110-130 BPM
- 高冲击宣传: 120-140 BPM

Common SFX: Whoosh、Click、Impact、Boom、Rise、Drop、Pop、Glitch、Camera Shutter、Notification.

Use sound to strengthen information beats. Do not stack SFX on every shot. CTA music should close the story instead of opening a new expectation.

## Default Output Structure

Use this structure in full mode:

1. `# 一、任务识别`
2. `# 二、内容定位`
3. `# 三、20 个 3 秒钩子`
4. `# 四、推荐 Top 5`
5. `# 五、最佳钩子`
6. `# 六、15 秒脚本`
7. `# 七、30 秒脚本`
8. `# 八、60 秒脚本`
9. `# 九、导演分镜`
10. `# 十、声画节奏设计`
11. `# 十一、发布文案`
12. `# 十二、A/B 测试`
13. `# 十三、发布后复盘`

Use `templates/output-template.md` as the canonical output skeleton.

## Quality Gate

Before final output, check:

- 钩子是否能在 3 秒内完成
- 钩子是否具体
- 是否在前 10 秒给出价值
- 每个镜头是否只有一个信息点
- 字幕是否适合手机阅读
- 口播字数是否匹配时长
- CTA 是否只有一个主要动作
- 是否存在无法验证的承诺
- 是否存在重复内容
- 15 秒、30 秒、60 秒版本是否有明显差异
- 分镜是否可直接拍摄
- 音效是否过度
- 平台适配是否准确

If a user asks for data review, use `docs/metrics-guide.md` and `prompts/data-reviewer.md`.
