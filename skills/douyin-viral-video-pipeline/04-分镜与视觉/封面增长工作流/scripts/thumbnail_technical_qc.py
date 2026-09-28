#!/usr/bin/env python3
"""Technical QC for thumbnail/cover images.

This script checks mechanical properties only:
- file size
- dimensions
- aspect ratio
- color mode
- brightness / contrast proxy
- sharpness proxy

It does not do OCR, does not judge aesthetics, and does not predict CTR.

Usage:
  python scripts/thumbnail_technical_qc.py cover.png --out qc_report.md
  python scripts/thumbnail_technical_qc.py covers/ --out qc_report.md
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Tuple

try:
    from PIL import Image, ImageFilter, ImageStat
except Exception as exc:  # pragma: no cover
    raise RuntimeError("This script requires Pillow. Install with: pip install pillow") from exc

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
TARGET_RATIOS = {
    "16:9": 16 / 9,
    "9:16": 9 / 16,
    "1:1": 1.0,
    "3:4": 3 / 4,
    "4:5": 4 / 5,
    "3:2": 3 / 2,
}


@dataclass
class ImageQC:
    path: str
    width: int
    height: int
    file_size_kb: float
    mode: str
    aspect_ratio: float
    closest_ratio: str
    ratio_error_percent: float
    brightness_0_255: float
    contrast_proxy: float
    sharpness_proxy: float
    min_dimension_ok: bool
    notes: List[str]


def iter_images(path: Path) -> Iterable[Path]:
    if path.is_file():
        if path.suffix.lower() in SUPPORTED:
            yield path
        return
    for p in sorted(path.rglob("*")):
        if p.suffix.lower() in SUPPORTED:
            yield p


def closest_ratio(width: int, height: int) -> Tuple[str, float]:
    ratio = width / height
    name, value = min(TARGET_RATIOS.items(), key=lambda item: abs(item[1] - ratio))
    error = abs(value - ratio) / value * 100
    return name, error


def edge_sharpness_proxy(img: Image.Image) -> float:
    gray = img.convert("L").resize((min(img.width, 512), min(img.height, 512)))
    edges = gray.filter(ImageFilter.FIND_EDGES)
    stat = ImageStat.Stat(edges)
    return float(stat.var[0])


def qc_one(path: Path) -> ImageQC:
    with Image.open(path) as img:
        width, height = img.size
        ratio_name, ratio_error = closest_ratio(width, height)
        gray = img.convert("L")
        stat = ImageStat.Stat(gray)
        brightness = float(stat.mean[0])
        contrast = float(stat.stddev[0])
        sharpness = edge_sharpness_proxy(img)

    notes: List[str] = []
    min_dimension_ok = min(width, height) >= 720
    if not min_dimension_ok:
        notes.append("最短边低于 720px，可能不适合高清封面。")
    if ratio_error > 3:
        notes.append(f"比例接近 {ratio_name}，但误差 {ratio_error:.1f}%，建议按平台比例重新裁切。")
    if brightness < 55:
        notes.append("整体偏暗，标题和人物可能不够突出。")
    elif brightness > 220:
        notes.append("整体过亮，白字或高光区域可能丢失层级。")
    if contrast < 35:
        notes.append("对比度偏低，小屏缩略图可能不够醒目。")
    if sharpness < 120:
        notes.append("清晰度代理指标偏低，可能存在模糊或边缘不清。")
    if not notes:
        notes.append("技术指标未发现明显问题；仍需人工检查标题可读性和视觉策略。")

    return ImageQC(
        path=str(path),
        width=width,
        height=height,
        file_size_kb=path.stat().st_size / 1024,
        mode=Image.open(path).mode,
        aspect_ratio=width / height,
        closest_ratio=ratio_name,
        ratio_error_percent=ratio_error,
        brightness_0_255=brightness,
        contrast_proxy=contrast,
        sharpness_proxy=sharpness,
        min_dimension_ok=min_dimension_ok,
        notes=notes,
    )


def render_markdown(results: List[ImageQC]) -> str:
    lines = [
        "# 封面技术质检报告",
        "",
        "> 本报告只检查尺寸、比例、亮度、对比度、清晰度代理指标，不判断审美，不预测点击率。",
        "",
        "| 文件 | 尺寸 | 接近比例 | 比例误差 | 亮度 | 对比度 | 清晰度代理 | 备注 |",
        "|---|---:|---|---:|---:|---:|---:|---|",
    ]
    for r in results:
        note = "；".join(r.notes)
        lines.append(
            f"| {Path(r.path).name} | {r.width}×{r.height} | {r.closest_ratio} | "
            f"{r.ratio_error_percent:.1f}% | {r.brightness_0_255:.1f} | "
            f"{r.contrast_proxy:.1f} | {r.sharpness_proxy:.1f} | {note} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Technical QC for thumbnail images.")
    parser.add_argument("input", type=Path, help="Image file or directory.")
    parser.add_argument("--out", type=Path, default=Path("thumbnail_qc_report.md"), help="Markdown report path.")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional JSON report path.")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 2

    paths = list(iter_images(args.input))
    if not paths:
        print("No supported image files found.", file=sys.stderr)
        return 1

    try:
        results = [qc_one(p) for p in paths]
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_markdown(results), encoding="utf-8")
    print(f"Wrote {args.out}")

    if args.json_out:
        import json
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
