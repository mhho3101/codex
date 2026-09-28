#!/usr/bin/env python3
"""
Video metadata & transcript extractor for /analyze.
Supports TikTok, Instagram Reels, YouTube Shorts.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

YT_DLP = [sys.executable, "-m", "yt_dlp"]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"


def detect_platform(url: str) -> str:
    if "tiktok.com" in url or "vm.tiktok.com" in url:
        return "tiktok"
    if "instagram.com" in url:
        return "instagram"
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    return "unknown"


def run_ytdlp(args: list, use_cookies: bool = False, timeout: int = 60) -> subprocess.CompletedProcess:
    cmd = YT_DLP + args
    if use_cookies:
        cmd += ["--cookies-from-browser", "chrome"]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="ignore")


def extract_tiktok_from_html(url: str) -> dict:
    """Fallback: parse TikTok page HTML for embedded JSON data."""
    try:
        html = fetch_url(url)
    except Exception as e:
        return {"_error": f"Failed to fetch TikTok page: {e}"}

    for script_id in ["__UNIVERSAL_DATA_FOR_REHYDRATION__", "SIGI_STATE", "__DEFAULT_SCOPE__"]:
        pattern = rf'<script[^>]*id="{script_id}"[^>]*>(.*?)</script>'
        m = re.search(pattern, html, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                return _parse_tiktok_json(data, url)
            except json.JSONDecodeError:
                continue

    # Try extracting any large JSON blob with video data
    for m in re.finditer(r'"videoData"\s*:\s*(\{.*?\})\s*[,}]', html):
        try:
            data = json.loads(m.group(1))
            if "desc" in data or "stats" in data:
                return _parse_tiktok_video_data(data, url)
        except json.JSONDecodeError:
            continue

    return {"_error": "Could not parse TikTok page data. The page may require login or the URL may be invalid."}


def _parse_tiktok_json(data: dict, url: str) -> dict:
    """Navigate the TikTok rehydration JSON to find video info."""
    default_scope = data.get("__DEFAULT_SCOPE__", {})
    video_detail = default_scope.get("webapp.video-detail", {})

    status = video_detail.get("statusCode", 0)
    if status == 10204:
        return {"_error": "TikTok video not found (deleted or URL invalid)"}
    if status and status != 0:
        return {"_error": f"TikTok returned status {status}: {video_detail.get('statusMsg', '')}"}

    item_info = video_detail.get("itemInfo", {}).get("itemStruct", {})

    if not item_info:
        for key in data:
            if isinstance(data[key], dict):
                item_info = data[key].get("itemInfo", {}).get("itemStruct", {})
                if item_info:
                    break

    if not item_info:
        return {"_error": "Found JSON but could not locate video data in page"}

    return _parse_tiktok_video_data(item_info, url)


def _parse_tiktok_video_data(item: dict, url: str) -> dict:
    stats = item.get("stats", {})
    author = item.get("author", {})
    return {
        "title": item.get("desc", ""),
        "description": item.get("desc", ""),
        "uploader": author.get("nickname", "") or author.get("uniqueId", ""),
        "uploader_id": author.get("uniqueId", ""),
        "upload_date": "",
        "duration": item.get("video", {}).get("duration", 0),
        "view_count": stats.get("playCount"),
        "like_count": stats.get("diggCount") or stats.get("heartCount"),
        "comment_count": stats.get("commentCount"),
        "repost_count": stats.get("shareCount"),
        "thumbnail": item.get("video", {}).get("cover", ""),
        "webpage_url": url,
    }


def extract_metadata(url: str, platform: str) -> dict:
    args = ["--dump-json", "--no-download", url]
    result = run_ytdlp(args)

    if result.returncode != 0 and platform == "instagram":
        result = run_ytdlp(args, use_cookies=True)

    if result.returncode != 0 and platform == "tiktok":
        result = run_ytdlp(args, use_cookies=True)

    if result.returncode != 0 and platform == "tiktok":
        return extract_tiktok_from_html(url)

    if result.returncode != 0:
        return {"_error": result.stderr.strip().split("\n")[-1]}

    raw = json.loads(result.stdout)
    return {
        "title": raw.get("title", ""),
        "description": raw.get("description", ""),
        "uploader": raw.get("uploader", "") or raw.get("channel", ""),
        "uploader_id": raw.get("uploader_id", "") or raw.get("channel_id", ""),
        "upload_date": raw.get("upload_date", ""),
        "duration": raw.get("duration", 0),
        "view_count": raw.get("view_count"),
        "like_count": raw.get("like_count"),
        "comment_count": raw.get("comment_count"),
        "repost_count": raw.get("repost_count"),
        "thumbnail": raw.get("thumbnail", ""),
        "webpage_url": raw.get("webpage_url", url),
    }


def parse_srt(text: str) -> str:
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or re.match(r"^\d+$", line) or re.match(r"\d{2}:\d{2}:\d{2}", line):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        if line and line not in lines:
            lines.append(line)
    return "\n".join(lines)


def extract_transcript(url: str, platform: str) -> Optional[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "sub")
        args = [
            "--skip-download",
            "--write-auto-sub", "--write-sub",
            "--sub-lang", "en,zh-Hans,zh,en-orig",
            "--sub-format", "vtt/srt/best",
            "--convert-subs", "srt",
            "-o", out,
            url,
        ]
        use_cookies = platform in ("instagram", "tiktok")
        run_ytdlp(args, use_cookies=use_cookies)

        for f in sorted(Path(tmpdir).glob("*.srt")):
            content = f.read_text(encoding="utf-8", errors="ignore")
            transcript = parse_srt(content)
            if transcript:
                return transcript

    return None


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: analyze-video.py <URL>"}, ensure_ascii=False))
        sys.exit(1)

    url = sys.argv[1].strip().strip("'\"")
    platform = detect_platform(url)

    metadata = extract_metadata(url, platform)
    transcript = None
    if "_error" not in metadata:
        transcript = extract_transcript(url, platform)

    output = {
        "url": url,
        "platform": platform,
        "metadata": metadata,
        "transcript": transcript,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
