---
name: video-frame-ocr
description: Extract on-screen text from videos by sampling frames and running OCR. Use when Codex needs to read text shown inside a video, especially Douyin/TikTok/Bilibili/short-video clips, screen-recorded slides, knowledge cards, screenshot-style videos, or local .mp4/.mov/.mkv/.webm files where audio transcription is insufficient.
---

# Video Frame OCR

Use this skill when the user needs text that appears visually in a video. This is different from speech transcription: if the words are printed on the screen, sample frames and OCR them.

## Workflow

1. Get a local video file.
   - For a Douyin link, first use the configured `douyin` MCP server to resolve/download the video when available.
   - If the MCP server is unavailable, ask for a local video file or use another download tool already configured in the environment.
2. Run `scripts/video_frame_ocr.py` on the local video.
3. Review `ocr_text.md` first.
4. If text cards are missed, rerun with a smaller `--interval`, a useful `--crop`, or a different `--dedupe-threshold`.
5. For very fast Douyin slideshow videos, use `--interval 0.1` and keep frames for manual verification.
6. Deliver the extracted text plus the output folder path. Mention if OCR confidence was poor or if the source video was not available.

## Script

Portable command when the active Python environment already has `rapidocr-onnxruntime`:

```bash
python scripts/video_frame_ocr.py --video /path/to/video.mp4 --out /tmp/video-ocr --interval 1.0
```

PowerShell example:

```powershell
python .\scripts\video_frame_ocr.py --video .\input.mp4 --out .\ocr-output --interval 0.5 --keep-frames
```

Useful options:

- `--interval 0.1`: sample very often for fast slideshow videos.
- `--interval 0.5`: sample more often for fast short videos.
- `--interval 1.5`: sample less often for slow videos.
- `--max-frames 300`: cap long videos.
- `--crop x,y,w,h`: OCR only a region, useful when captions occupy a fixed area.
- `--dedupe-threshold 0.92`: raise to keep more near-duplicates, lower to merge more aggressively.
- `--keep-frames`: preserve extracted frame images for manual review.
- `--ffmpeg`: pass an explicit ffmpeg executable path if it is not on PATH.

Outputs:

- `ocr_text.md`: readable merged text grouped by first timestamp.
- `ocr_results.json`: structured per-frame OCR lines, confidence, and file paths.
- `frames/`: sampled frame images, deleted by default unless `--keep-frames` is set.

## Douyin Notes

Read `references/douyin-mcp.md` when working with Douyin links, login state, or the installed local MCP path.

For Douyin videos dominated by visual text, prefer this OCR workflow over ASR. ASR only captures spoken audio and will miss silent knowledge-card videos.
