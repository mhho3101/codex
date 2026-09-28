# xuehui — 薛辉·短视频商业化变现思维

基于薛辉（Allin 短视频达人培训中心创始人）的短视频商业化变现思维体系。强调 **内容 > 情绪 > 文案 > 技术** 的价值链条，以「**先赚钱再涨粉**」的商业第一性原理为核心，通过**四大变现脚本模型**（晒过程 / 讲故事 / 教知识 / 说观点）+ **八大爆款元素**指导短视频创作与变现。

> 不讲空泛理论，只给能落地的方法。风格直接、犀利、一针见血。

## 功能

- **商业第一性原理**：先确认产品能卖出去，再考虑涨粉；粉丝量只是结果，商业产品才是起点
- **四大变现脚本模型**：晒过程 / 讲故事 / 教知识 / 说观点
- **八大爆款元素**：特定人群 / 成本 / 名人 / 奇葩 / 女人 / 最差 / 反差 / 怀旧
- **五大误区拆解**：爆款神话、设备论、涨粉焦虑、完美方向、剪辑必须专业
- **可落地方案**：把模糊想法转化为能直接执行的变现脚本

## 安装

### Claude Code

```sh
mkdir -p ~/.claude/skills
git clone https://github.com/paul-xing/xuehui-skill.git ~/.claude/skills/xuehui
```

### Codex

```sh
mkdir -p ~/.codex/skills
git clone https://github.com/paul-xing/xuehui-skill.git ~/.codex/skills/xuehui
```

### 通用（~/.agents）

```sh
mkdir -p ~/.agents/skills
git clone https://github.com/paul-xing/xuehui-skill.git ~/.agents/skills/xuehui
```

安装后在新会话中可用。在对话中说「使用薛辉的短视频商业化变现思维，帮我分析和优化这条短视频脚本」即可触发。

## 目录结构

```
xuehui/
├── SKILL.md               # Skill 主文件（角色设定、核心原则、脚本模型、误区拆解）
└── agents/
    └── openai.yaml        # 模型接口展示信息
```

## 参考来源

本 skill 蒸馏自：
- 薛辉（Allin 短视频达人培训中心创始人）公开课程内容与核心理念
- 抖音头部讲师薛辉的课程大纲与实战方法论

## License

MIT
