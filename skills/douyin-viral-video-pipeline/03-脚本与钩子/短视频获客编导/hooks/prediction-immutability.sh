#!/usr/bin/env bash
# prediction-immutability.sh — Claude Code PreToolUse hook
# 拦截对 predictions/ 目录下文件的直接编辑/写入（盲预测不可改原则）。
# 合法路径：director.py predict 创建 / director.py retro 追加复盘段（走 Bash，不经此 hook）。
set -euo pipefail

INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*: *"//; s/"$//')

case "$FILE" in
  *predictions/*.md|*predictions\\*.md)
    echo "盲预测文件不可直接编辑（immutable）。请用 director.py retro 追加复盘段；要重做请新开 _redo.md。" >&2
    exit 2
    ;;
esac
exit 0
