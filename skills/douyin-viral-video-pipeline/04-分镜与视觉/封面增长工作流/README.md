# CoverCraft Skill v2.0

这是一个面向短视频、自媒体、课程、知识 IP 和产品内容的封面生产 Skill。它不是单句提示词，而是一套完整工作流：

> 标题策略 → 平台适配 → 参考图拆解 → 视觉迁移 → 人像一致性 → 无字底图提示词 → 后期排版 → 质检评分 → 二次优化 → 批量生产

## 文件结构

```text
covercraft-skill/
├── SKILL.md                         # 主 Skill 文件，直接上传或复制到系统提示词
├── README.md                        # 使用说明
├── templates/
│   ├── intake_form.md               # 用户信息收集表
│   ├── output_contract.md           # 标准输出格式
│   ├── style_guide_schema.json      # 账号视觉规范 JSON 模板
│   ├── platform_rules.json          # 平台规则配置
│   └── prompt_pack_schema.json      # 提示词包结构模板
├── examples/                        # 8 个完整使用案例
└── scripts/                         # 可选辅助脚本
    ├── batch_cover_brief.py          # 批量标题 → 封面简报
    ├── thumbnail_technical_qc.py     # 图片技术质检
    └── prompt_pack_builder.py        # brief JSON → 多工具提示词包
```

## 最推荐的使用方式

### 方式 1：纯 Skill 使用

把 `SKILL.md` 上传到支持 Skill 的环境，或复制到 GPT/智能体的系统提示词里。

### 方式 2：顶级工作流使用

1. 用 `templates/intake_form.md` 收集用户输入。
2. 用 `SKILL.md` 生成 A/B/C 三套封面策略。
3. 用图像工具生成无字底图。
4. 用 Canva、Figma、PS、稿定、剪映等工具添加中文标题。
5. 用质检评分表检查并迭代。
6. 多标题时使用 `scripts/batch_cover_brief.py` 做批量简报。

## 什么时候需要脚本？

不需要脚本也能运行。本 Skill 的核心能力在 `SKILL.md`。

脚本只用于三个场景：

- 批量处理几十个标题。
- 检查封面图片尺寸、比例、清晰度等技术指标。
- 把一个结构化 brief 导出成不同图像工具的提示词包。

## 示例命令

### 批量标题生成简报

```bash
python scripts/batch_cover_brief.py tests/sample_titles.csv --out outputs/batch_briefs.md --json-out outputs/batch_briefs.json
```

### 图片技术质检

```bash
python scripts/thumbnail_technical_qc.py path/to/cover.png --out outputs/qc_report.md
```

### 生成提示词包

```bash
python scripts/prompt_pack_builder.py tests/sample_brief.json --out outputs/prompt_pack.md
```

## 注意

- 本 Skill 不承诺必爆，只提高封面策略质量、可读性和平台适配度。
- 默认生成无字底图，中文标题应由后期工具添加。
- 参考封面只用于学习视觉逻辑，不用于照搬具体设计。
- 涉及人像时，一致性受图像模型能力影响，需要小批量生成和人工筛选。
