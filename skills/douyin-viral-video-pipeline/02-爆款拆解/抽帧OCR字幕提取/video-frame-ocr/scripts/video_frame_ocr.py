#!/usr/bin/env python
"""Extract video frames and OCR visible text.

Requires ffmpeg on PATH and rapidocr-onnxruntime in the Python environment.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from pathlib import Path


@dataclass
class OcrLine:
    text: str
    confidence: float | None


@dataclass
class FrameResult:
    timestamp: float
    frame_path: str
    text: str
    lines: list[OcrLine]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample video frames and OCR visible text.")
    parser.add_argument("--video", required=True, help="Path to local video file.")
    parser.add_argument("--out", required=True, help="Output directory.")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between sampled frames.")
    parser.add_argument("--max-frames", type=int, default=240, help="Maximum frames to OCR.")
    parser.add_argument("--crop", default="", help="Optional crop as x,y,w,h in pixels.")
    parser.add_argument("--dedupe-threshold", type=float, default=0.9, help="Similarity threshold for merging repeated text.")
    parser.add_argument("--keep-frames", action="store_true", help="Keep extracted frame images.")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg executable path.")
    return parser.parse_args()


def require_rapidocr():
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError as exc:
        raise SystemExit(
            "rapidocr-onnxruntime is not installed. Install it or run this script with the douyin-mcp .venv Python."
        ) from exc
    return RapidOCR()


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise SystemExit(f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr[-4000:]}")


def probe_duration(ffmpeg: str, video: Path) -> float | None:
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-i",
        str(video),
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", proc.stderr)
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def build_vf(interval: float, crop: str) -> str:
    filters = [f"fps=1/{interval}"]
    if crop:
        parts = [p.strip() for p in crop.split(",")]
        if len(parts) != 4 or not all(p.isdigit() for p in parts):
            raise SystemExit("--crop must be x,y,w,h with integer pixels.")
        x, y, w, h = parts
        filters.append(f"crop={w}:{h}:{x}:{y}")
    return ",".join(filters)


def extract_frames(ffmpeg: str, video: Path, frames_dir: Path, interval: float, max_frames: int, crop: str) -> list[Path]:
    frames_dir.mkdir(parents=True, exist_ok=True)
    frame_pattern = frames_dir / "frame_%05d.jpg"
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-y",
        "-i",
        str(video),
        "-vf",
        build_vf(interval, crop),
        "-frames:v",
        str(max_frames),
        "-q:v",
        "2",
        str(frame_pattern),
    ]
    run(cmd)
    return sorted(frames_dir.glob("frame_*.jpg"))


def extract_lines(ocr_result) -> list[OcrLine]:
    lines: list[OcrLine] = []
    for item in ocr_result or []:
        if not item or len(item) < 2:
            continue
        text = str(item[1]).strip()
        if not text:
            continue
        confidence = None
        if len(item) >= 3:
            try:
                confidence = float(item[2])
            except (TypeError, ValueError):
                confidence = None
        lines.append(OcrLine(text=text, confidence=confidence))
    return lines


def normalize(text: str) -> str:
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "", text)
    return text.lower()


def is_duplicate(text: str, seen: list[str], threshold: float) -> bool:
    current = normalize(text)
    if not current:
        return True
    for previous in seen:
        if current == previous:
            return True
        if SequenceMatcher(None, current, previous).ratio() >= threshold:
            return True
    seen.append(current)
    return False


def write_outputs(out_dir: Path, results: list[FrameResult], merged: list[FrameResult], args: argparse.Namespace) -> None:
    payload = {
        "video": str(Path(args.video).resolve()),
        "interval": args.interval,
        "max_frames": args.max_frames,
        "crop": args.crop,
        "dedupe_threshold": args.dedupe_threshold,
        "frames_with_text": len([r for r in results if r.text.strip()]),
        "merged_blocks": len(merged),
        "results": [
            {
                **asdict(result),
                "lines": [asdict(line) for line in result.lines],
            }
            for result in results
        ],
    }
    (out_dir / "ocr_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md: list[str] = [
        "# Video Frame OCR",
        "",
        f"- Video: `{Path(args.video).resolve()}`",
        f"- Interval: {args.interval}s",
        f"- Crop: {args.crop or 'none'}",
        f"- Frames with text: {payload['frames_with_text']}",
        f"- Merged text blocks: {payload['merged_blocks']}",
        "",
    ]
    if not merged:
        md.append("No readable text was detected.")
    for result in merged:
        stamp = format_timestamp(result.timestamp)
        md.extend([f"## {stamp}", "", result.text.strip(), ""])
    (out_dir / "ocr_text.md").write_text("\n".join(md), encoding="utf-8")


def format_timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    minutes = int(seconds // 60)
    secs = seconds - minutes * 60
    return f"{minutes:02d}:{secs:05.2f}"


def main() -> int:
    args = parse_args()
    video = Path(args.video).expanduser().resolve()
    if not video.exists():
        raise SystemExit(f"Video file not found: {video}")
    if args.interval <= 0:
        raise SystemExit("--interval must be greater than 0.")

    out_dir = Path(args.out).expanduser().resolve()
    frames_dir = out_dir / "frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    duration = probe_duration(args.ffmpeg, video)
    if duration is not None:
        expected = math.ceil(duration / args.interval)
        if expected > args.max_frames:
            print(f"Sampling capped at {args.max_frames} frames from about {expected} possible frames.", file=sys.stderr)

    engine = require_rapidocr()
    frames = extract_frames(args.ffmpeg, video, frames_dir, args.interval, args.max_frames, args.crop)
    results: list[FrameResult] = []
    merged: list[FrameResult] = []
    seen: list[str] = []

    for index, frame in enumerate(frames):
        timestamp = index * args.interval
        ocr_result, _ = engine(str(frame))
        lines = extract_lines(ocr_result)
        text = "\n".join(line.text for line in lines)
        result = FrameResult(timestamp=timestamp, frame_path=str(frame), text=text, lines=lines)
        results.append(result)
        if text.strip() and not is_duplicate(text, seen, args.dedupe_threshold):
            merged.append(result)

    write_outputs(out_dir, results, merged, args)
    if not args.keep_frames:
        shutil.rmtree(frames_dir, ignore_errors=True)

    print(f"Wrote {out_dir / 'ocr_text.md'}")
    print(f"Wrote {out_dir / 'ocr_results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
