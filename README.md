# Codex 技能包

将你的 Codex 自定义技能托管在 GitHub 上，实现多设备同步。

## 包含的技能

| 技能 | 说明 |
|------|------|
| claude-vision | Claude Vision 集成 |
| 	meet | 腾讯会议 CLI 操作 |

## 安装方法

### 方法一：使用 skill-installer（推荐）

在每台电脑的 Codex 中运行：

`
install-skill-from-github.py --repo mhho3101/codex --path skills/claude-vision
install-skill-from-github.py --repo mhho3101/codex --path skills/tmeet
`

### 方法二：手动复制

将 skills/ 下的技能文件夹复制到 ~/.codex/skills/ 目录。

## 更新技能

当在一台电脑上修改了技能后：

`ash
# 在仓库目录提交并推送
git add .
git commit -m "更新技能"
git push

# 在另一台电脑上重新安装
install-skill-from-github.py --repo mhho3101/codex --path skills/技能名
`

## 环境变量

claude-vision 技能需要 .env 配置文件（已加入 .gitignore）。
参考 .env.example 创建自己的配置，不要提交真实密钥到仓库。
