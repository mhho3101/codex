---
name: claude-vision
description: 让无法原生识图的模型获得图片识别能力。当用户分享本地或网络图片路径、消息中出现图片附件、或要求分析/描述/识别图片内容时使用。通过调用阿里云百炼(DashScope)的视觉模型API，将图片转为base64并发送给视觉模型，返回文字描述。
metadata:
  short-description: 通过阿里云百炼视觉模型识别图片
---

# 识图能力

本技能为不具备原生识图能力的模型提供图片识别功能。遇到图片时，使用 `scripts/vision.js` 脚本调用阿里云百炼视觉模型。

## 触发场景

- 用户分享图片路径（本地或网络 URL）
- 消息中出现 "Saved attachments:" 并列出图片
- 用户要求分析、描述、识别图片内容

## 使用方法

运行脚本，传入图片路径和问题（脚本位于本技能目录下）：

```
node "<技能目录>/scripts/vision.js" "<图片路径>" "用中文描述这张图片"
```

如果图片是网络 URL：

```
node "<技能目录>/scripts/vision.js" --url "<图片链接>" "用中文描述这张图片"
```

## 配置

配置已写入 `scripts/.env` 文件，无需手动修改：

- `DASHSCOPE_API_KEY`：阿里云百炼 API Key
- `VISION_MODEL`：视觉模型名称（qwen3.7-flash-2026-07-15）
- `DASHSCOPE_BASE_URL`：DashScope 兼容模式 API 地址

## 注意事项

- 脚本输出为视觉模型的文字描述，直接将其作为识图结果返回给用户
- 若图片较大，脚本会自动转为 base64 后发送，无需用户干预
- 配置好之后，用户直接发图片即可自动识图，无需手动输入命令
