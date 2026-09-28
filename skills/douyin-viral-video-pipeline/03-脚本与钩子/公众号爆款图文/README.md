# wechat-claw

项目总览。Detailed docs:

- 中文文档: [docs/README.zh.md](./docs/README.zh.md)
- English documentation: [docs/README.en.md](./docs/README.en.md)
- OpenClaw 接入: [docs/openclaw.zh.md](./docs/openclaw.zh.md)
- OpenClaw integration: [docs/openclaw.en.md](./docs/openclaw.en.md)

微信公众号文章工具集，用于把结构化 JSON 内容渲染成公众号 HTML，并串联校验、配图规划、图片上传、草稿创建和发布流程。  
`wechat-claw` is a toolkit for turning structured JSON articles into WeChat-ready HTML, with validation, image planning, upload, draft creation, and publishing helpers.

## Overview

当前仓库聚焦结构化的公众号文章生产与发布链路：

- Multi-template WeChat article rendering from JSON
- Article validation for metadata, structure, and unresolved placeholders
- Automatic cover/body image planning
- Optional pipeline hooks for image generation, upload, draft creation, and publish
- Source collection from files, URLs, and raw text

## Visual Samples

功能介绍 / feature overview:

<p align="center">
  <img src="./docs/img/介绍1.jpeg" alt="wechat-claw pain points overview" width="31%" />
  <img src="./docs/img/介绍2.jpeg" alt="wechat-claw capabilities overview" width="31%" />
  <img src="./docs/img/介绍3.jpeg" alt="wechat-claw image planning and pipeline overview" width="31%" />
</p>

文章样例 / article examples:

<p align="center">
  <img src="./docs/img/样例1.jpeg" alt="wechat-claw article sample 1" width="31%" />
  <img src="./docs/img/样例2.jpeg" alt="wechat-claw article sample 2" width="31%" />
</p>

## Support

如果这个项目对你有帮助，欢迎扫码赞赏支持维护。
If this project helps you, you can support its maintenance by scanning the QR code below.

<p align="center">
  <img src="./docs/img/赞赏码.png" alt="wechat-claw donation QR code" width="260" />
</p>

## Templates

Supported templates:

- `daily-intelligence`
- `weekly-financial`
- `deep-analysis`
- `industry-radar`
- `product-release`
- `breaking-watch`
- `studio-brief`
- `neo-brutalism`

Template files live in [`templates/`](./templates).

## Scripts

Core entry points:

- [`scripts/collect_sources.py`](./scripts/collect_sources.py)
- [`scripts/render_article.py`](./scripts/render_article.py)
- [`scripts/validate_article.py`](./scripts/validate_article.py)
- [`scripts/plan_images.py`](./scripts/plan_images.py)
- [`scripts/run_pipeline.py`](./scripts/run_pipeline.py)

## Docs

Choose one of the detailed guides:

- 中文: [docs/README.zh.md](./docs/README.zh.md)
- English: [docs/README.en.md](./docs/README.en.md)
- OpenClaw 接入: [docs/openclaw.zh.md](./docs/openclaw.zh.md)
- OpenClaw integration: [docs/openclaw.en.md](./docs/openclaw.en.md)

## Repository Layout

```text
docs/                   中文 / English 详细文档
templates/              公众号 HTML 模板
scripts/article_lib.py  核心渲染与校验逻辑
scripts/render_article.py
scripts/validate_article.py
scripts/plan_images.py
scripts/run_pipeline.py
scripts/collect_sources.py
references/             写作、标题、图片提示词参考
```

## Star History

<a href="https://www.star-history.com/?repos=th3ee9ine%2Fwechat-claw-skill&type=timeline&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=th3ee9ine/wechat-claw-skill&type=timeline&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=th3ee9ine/wechat-claw-skill&type=timeline&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=th3ee9ine/wechat-claw-skill&type=timeline&legend=top-left" />
 </picture>
</a>
