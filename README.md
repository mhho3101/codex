# Codex 技能包

将你的 Codex 自定义技能托管在 GitHub 上，实现多设备同步。

## 包含的技能（15 个）

| 技能 | 说明 |
|------|------|
| agent-video-pipeline | 跨 agent 可编辑视频流水线（ChatCut + HyperFrames + Seedance + Remotion），含 QC 门禁 |
| chatcut-plugin-basics | ChatCut 视频编辑插件操作（字幕/转写/剪辑/生成/导出） |
| claude-vision-skill | 图片识别（阿里云百炼视觉模型，支持本地/URL/剪贴板输入） |
| data-visualization | 数据可视化（matplotlib/plotly/ECharts，可导出视频用图表与动画） |
| define-goal | 把模糊意图定义成可衡量、可验证的目标 |
| ffmpeg-video-processing | ffmpeg 视频处理命令专项（裁剪/拼接/转码/字幕/音频） |
| folder-organizer | 保守式文件夹整理（只读分析→报告→确认后执行） |
| gepeto | 用 Pinokio 构建 1-click 启动器和内置启动器的应用 |
| hyperframes | 视频/动画/动效制作入口技能（HTML 合成、Remotion 移植） |
| mcp | 模型上下文协议（MCP）概念、服务器配置与接入 |
| pinokio | 发现、启动和使用 Pinokio 应用与工具 |
| remotion-best-practices | Remotion 技能路由（创建/字幕/地图/渲染/Studio 等） |
| seedance-25 | Seedance 2.5（即梦/Dreamina）AI 视频生成提示词工作流 |
| tmeet-skill | 腾讯会议 CLI（tmeet）：会议/录制/报告/通讯录/会中控制 |
| video-production | 端到端视频制作工作流（脚本/剪辑/音频/字幕/导出） |

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
