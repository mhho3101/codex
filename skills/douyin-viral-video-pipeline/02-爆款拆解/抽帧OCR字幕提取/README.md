# Douyin Video Frame OCR Skill

A local Codex skill for reading on-screen text from short videos, especially Douyin/TikTok-style fast slideshow videos.

The intended workflow is:

1. Resolve or download a Douyin video with a configured `douyin` MCP server.
2. Sample video frames at a chosen interval.
3. Run OCR on the sampled frames.
4. Merge repeated text blocks into readable Markdown and JSON outputs.

This is useful when the text is displayed visually in the video and audio transcription would miss it.

## Repository Layout

```text
video-frame-ocr/
  SKILL.md
  agents/openai.yaml
  references/douyin-mcp.md
  scripts/video_frame_ocr.py
requirements.txt
```

## Install As A Codex Skill

Clone this repository, then copy the skill folder into your Codex skills directory:

```powershell
git clone https://github.com/<your-name>/douyin-video-frame-ocr-skill.git
Copy-Item -Recurse -Force .\douyin-video-frame-ocr-skill\video-frame-ocr "$env:USERPROFILE\.codex\skills\video-frame-ocr"
```

Restart Codex Desktop so the new skill metadata is discovered.

## Python Requirements

The OCR script requires Python 3.10+ and these packages:

```powershell
python -m pip install -r requirements.txt
```

It also requires `ffmpeg` on `PATH`, or you can pass an explicit executable with `--ffmpeg`.

## Douyin Setup

For Douyin links, configure a Douyin MCP server first. This skill expects Codex to use that server to resolve and download the video, then pass the local `.mp4` file to the OCR script.

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

Cookie/login handling belongs to the Douyin MCP server. Do not commit cookies to this repository.

## Direct Script Usage

```powershell
python .\video-frame-ocr\scripts\video_frame_ocr.py `
  --video .\input.mp4 `
  --out .\ocr-output `
  --interval 0.5 `
  --max-frames 240 `
  --keep-frames
```

For very fast slideshow videos, use `--interval 0.1` and consider a second pass with a shifted or denser sample if some cards are missed.

Common options:

- `--interval 0.1`: sample more often for fast text cards.
- `--interval 0.5`: good default for moderately fast slides.
- `--crop x,y,w,h`: OCR only a fixed text region.
- `--dedupe-threshold 0.9`: merge near-duplicate frames.
- `--max-frames 300`: cap long videos.
- `--keep-frames`: keep frame images for manual verification.

## Outputs

The script writes:

- `ocr_text.md`: merged readable text grouped by first timestamp.
- `ocr_results.json`: structured per-frame OCR data.
- `frames/`: sampled frame images when `--keep-frames` is used.

## Example Prompt For Codex

```text
Use $video-frame-ocr to read the on-screen text from this Douyin link:
https://v.douyin.com/example/

Download the video through the configured douyin MCP server, sample at 0.1s if it is a fast slideshow, OCR the frames, and summarize the extracted text.
```

## Notes

- OCR quality depends on video resolution, compression, subtitles, motion blur, and font contrast.
- Douyin videos with rapid card changes may require dense sampling and manual frame review.
- The skill is designed for local processing. Keep downloaded videos, cookies, and generated OCR outputs out of Git commits.
