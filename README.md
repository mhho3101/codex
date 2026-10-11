# codex

Codex 技能包的多设备同步仓库。所有技能以**平铺目录**形式存放在 [`skills/`](skills/) 下。

```text
codex/
├── README.md
└── skills/
    ├── <技能名>/
    │   ├── SKILL.md
    │   └── ...（技能自带的脚本、模板、素材）
    └── ...
```

一个技能 = `skills/` 下的一个目录，目录内顶层必须有 `SKILL.md`。

---

## 内容概览

| 项目 | 值 |
|---|---|
| 技能总数 | **730** |
| 总大小 | 约 162.9 MB |
| 文件数 | 5558 |
| 单文件最大 | 12.22 MB |
| 来源 | 11 个上游插件仓库 |
| 同步日期 | 2026-10-11 |

## 来源插件

技能从下列 11 个上游仓库提取（各仓库的**全部**浅层技能目录，已按内容去重）：

| 名称 | 上游仓库 | 提交 | 上游最近提交 | 贡献技能 | 体积 |
|---|---|---|---|---|---|
| computeruse | [anthropics/claude-quickstarts](https://github.com/anthropics/claude-quickstarts) | `9ec32b9` | 2026-10-07 | 11 | 1.5 MB |
| Superpowers | [obra/superpowers](https://github.com/obra/superpowers) | `bb92a77` | 2026-10-09 | 15 | 0.4 MB |
| claude-mem | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | `fa8ab09` | 2026-10-08 | 31 | 2.0 MB |
| Open Design | [nexu-io/open-design](https://github.com/nexu-io/open-design) | `17e2559` | 2026-10-10 | 538 | 101.7 MB |
| Agent-Reach | [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | `94f06c1` | 2026-10-08 | 1 | <0.1 MB |
| HyperFrames | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | `bb9e507` | 2026-10-10 | 34 | 42.7 MB |
| OpenAI Skills | [openai/skills](https://github.com/openai/skills) | `49f948f` | 2026-06-23 | 44 | 4.5 MB |
| Agent Skills | [Greentor/agent-skills](https://github.com/Greentor/agent-skills) | `1068b1b` | 2026-04-06 | 20 | 0.2 MB |
| UI-UX-Pro-Max | [SuperCodeTool/ui-ux-pro-max-skill](https://github.com/SuperCodeTool/ui-ux-pro-max-skill) | `7f22b57` | 2026-01-12 | 5 | 1.0 MB |
| baoyu-skills | [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) | `1567581` | 2026-09-10 | 22 | 2.6 MB |
| Obsidian Skills | [dengrish/obsidian-skills](https://github.com/dengrish/obsidian-skills) | `762a337` | 2026-10-09 | 9 | 6.2 MB |

> 上游插件的**完整源码**（含 `.git`、测试基准素材等，共约 6.3 GB）体积远超 GitHub 仓库上限，因此**不存放在本仓库**。
> 本机克隆位置：`C:\Users\Administrator\Documents\deepseek-harness\default-workspace\plugins\`
> 需要时按上表仓库地址重新克隆即可。

## 目录命名规则

1. **平铺**：所有技能都在 `skills/<技能名>/`，只有一层，便于工具扫描。
2. **去重**：不同插件为不同 agent 运行时（`.claude/`、`.codex/`、`.cursor/`、`.gemini/` 等）提供的**逐字节相同**副本只保留一份，共合并 18 份。
3. **重名加前缀**：不同插件（或同一插件的不同模板集）里**内容不同但同名**的技能，后出现者加插件前缀，例如：
   - `article-magazine`（来自 open-design 的 `skills/`）
   - `open-design-article-magazine`（来自 open-design 的 `plugins/_official/examples/`）
   - `superpowers-brainstorming`、`claude-mem-agent-cost-report`
   共 178 个技能因重名被加前缀；若加前缀后仍冲突，再追加 `-2`、`-3`。

完整的「目标目录 ← 来源插件/路径」对照表见本机 `codex-upload\skill-mapping.csv`。

## 同步与更新

本仓库用于多设备同步，正常使用：

```powershell
# 在其他设备拉取
git clone https://github.com/mhho3101/codex.git
git pull

# 本机新增/修改技能后推送
git add skills/<技能名>
git commit -m "add: <技能名>"
git push origin main
```

如需从上游插件仓库重新提取技能，在本机运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& "C:\Users\Administrator\Documents\deepseek-harness\default-workspace\stage-skills.ps1"
```

脚本会重建 `codex-upload\skills\`（去重 + 重名加前缀），再用其结果替换本仓库的 `skills/` 后提交。

## 分支说明

- `main` —— 默认分支，当前内容。
- `master` —— 历史分支（`c97188c`），内容已清空，保留仅供追溯。

## 历史

本仓库曾于 2026-10-10 清空（清空前为 32 个技能）。清空前的内容仍保留在 Git 历史中：

- `main` 分支清空前最后一个提交：`34b3f66`
- 旧 `master` 分支：`d3fd016`

需要恢复时：

```powershell
git checkout 34b3f66 -- skills/    # 只取回文件，不切换分支
```
