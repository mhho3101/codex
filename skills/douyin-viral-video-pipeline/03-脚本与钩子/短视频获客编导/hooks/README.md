# hooks · 盲预测不可改的物理强制层（可选）

> 原则写在文档里靠自觉，写在 hook 里靠系统。本目录提供 Claude Code 的 PreToolUse hook 样例：
> 拦截对 `predictions/` 目录下预测文件的直接编辑——预测只能由 `director.py predict` 创建、
> 由 `director.py retro` 追加复盘段。

## 安装（Claude Code）

1. 把 `prediction-immutability.sh` 复制到你的内容项目根目录（或任意位置，记下路径）。
2. 在项目 `.claude/settings.json` 中加入：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          { "type": "command", "command": "bash ./prediction-immutability.sh" }
        ]
      }
    ]
  }
}
```

3. 之后任何 Agent 直接编辑 `predictions/*.md` 都会被阻塞（exit 2），只能通过 CLI 的
   `retro` 命令追加复盘段。

## 其他 harness

- Codex / Pi 等无等价 hook 机制时：靠两条设计保证——① CLI 不提供"编辑预测段"的命令；
  ② Refusals 清单（SKILL.md）要求 Agent 拒绝此类请求。
