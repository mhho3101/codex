# Codex 技能包

将你的 Codex 自定义技能托管在 GitHub 上，实现多设备同步。

## 包含的技能

| 技能 | 说明 |
|------|------|
| claude-vision | Claude Vision 集成 |
| 	meet | 腾讯会议 CLI 操作 |

## 安装方法

在每台电脑的 Codex 对话中，直接使用 skill-installer 安装：

### 安装 claude-vision

`
install-skill-from-github.py --repo mhho3101/codex --path skills/claude-vision
`

### 安装 tmeet

`
install-skill-from-github.py --repo mhho3101/codex --path skills/tmeet
`

或者让 Codex 帮你安装："帮我从 mhho3101/codex 安装 skills/claude-vision 技能"

## 更新技能流程

在一台电脑上修改技能后：

`ash
# 1. 更新仓库中的技能文件
# 2. 提交并推送
git add .
git commit -m "更新技能描述"
git push

# 3. 在另一台电脑上重新安装（会覆盖旧的）
install-skill-from-github.py --repo mhho3101/codex --path skills/技能名
`

## 环境变量

claude-vision 需要 .env 配置（已在 .gitignore 中排除）。
参考 .env.example 创建自己的配置，**不要提交真实密钥到仓库**。
