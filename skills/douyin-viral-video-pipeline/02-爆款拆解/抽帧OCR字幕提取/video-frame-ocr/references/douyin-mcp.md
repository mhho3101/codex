# Douyin MCP Notes

For Douyin links, use a configured `douyin` MCP server to resolve the share URL and download a local video before running frame OCR.

Recommended upstream project:

```text
https://github.com/pazwusimple-netizen/douyin-mcp
```

Example Codex MCP config:

```toml
[mcp_servers.douyin]
command = 'C:\path\to\douyin-mcp\.venv\Scripts\python.exe'
args = ['C:\path\to\douyin-mcp\main.py']
startup_timeout_sec = 120

[mcp_servers.douyin.env]
PYTHONIOENCODING = 'utf-8'
```

Typical flow:

1. Resolve the Douyin share URL with the MCP server.
2. Download the video to a local `.mp4` file.
3. Run `scripts/video_frame_ocr.py` on that local video.
4. Review `ocr_text.md` and, when needed, manually inspect `frames/`.

Cookie/login handling belongs to the Douyin MCP server. Never commit cookies, downloaded videos, or OCR output folders to a public repository.

For videos with fast text-card transitions, prefer `--interval 0.1 --keep-frames`. If cards are still missed, do a second pass with a shifted sampling strategy or manually inspect dense frames.
