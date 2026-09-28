#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_srt.py - 字幕信号分析脚本（video-story-clip 开源版）

从 SRT 中提取结构化信号，输出统计报告（JSON + Markdown），
让 AI 只精读重点区域，不再裸读全文。

报告是"给 AI 指路的目录"，不是替代字幕的全文。

用法:
  python scripts/analyze_srt.py "字幕.srt"
  python scripts/analyze_srt.py "字幕.srt" --json out.json --md out.md
  python scripts/analyze_srt.py "字幕.srt" --start 180 --end 7000 --threshold 20

输出:
  默认在 SRT 同目录生成 {字幕名}.report.json 和 {字幕名}.report.md

设计文档: analyze_srt.py-字幕信号分析脚本-方案设计.md (V1.1)
"""

import argparse
import json
import os
import re
import statistics
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- 时间换算

TIME_RE = re.compile(
    r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})"
)


def to_seconds(h, m, s, ms):
    return h * 3600 + m * 60 + s + ms / 1000.0


# ---------------------------------------------------------------- SRT 解析


def detect_encoding(path):
    """依次尝试 utf-8-sig / utf-8 / gbk，全部失败报错。"""
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            with open(path, "r", encoding=enc) as f:
                f.read(4096)
            return enc
        except UnicodeDecodeError:
            continue
    raise ValueError(f"无法识别字幕编码: {path}")


def parse_srt(path):
    """解析 SRT，返回 (entries, warnings)。

    entries: [{"start": float, "end": float, "text": str}, ...] 按时间排序
    """
    encoding = detect_encoding(path)
    warnings = []
    entries = []

    with open(path, "r", encoding=encoding) as f:
        content = f.read()

    # 按空行分块（兼容 \r\n）
    blocks = re.split(r"\n\s*\n", content.replace("\r\n", "\n").strip())
    for block in blocks:
        lines = [ln.strip() for ln in block.strip().split("\n") if ln.strip()]
        if len(lines) < 2:
            continue
        m = TIME_RE.search(lines[1])
        if not m:
            warnings.append(f"第 {lines[0]} 块时间格式异常: {lines[1][:40]}")
            continue
        h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, m.groups())
        start = to_seconds(h1, m1, s1, ms1)
        end = to_seconds(h2, m2, s2, ms2)
        text = " ".join(lines[2:]).strip()
        if not text:
            continue
        entries.append({"start": start, "end": end, "text": text})

    entries.sort(key=lambda e: e["start"])
    return entries, warnings, encoding


# ---------------------------------------------------------------- 清洗


POLLUTION_MARK = re.compile(r"字幕组|翻译|压制|校对|发布|转载|字幕下载|网盘下载|www|http", re.IGNORECASE)
CHINESE = re.compile(r"[\u4e00-\u9fff]")
LATIN = re.compile(r"[a-zA-Z]")


def is_pollution(text):
    if len(text) > 80:
        return True
    if re.fullmatch(r"[\d\s:.,，。、\-]+", text):
        return True
    if POLLUTION_MARK.search(text):
        return True
    if not CHINESE.search(text) and not LATIN.search(text):
        return True
    return False


def clean(entries, gap_merge=3.0):
    """去重 + 滤污染 + 对白块合并。

    返回 (clean_entries, pollution, scene_blocks)
    pollution: [{"start": float, "text": str}, ...]
    scene_blocks: [{"start": float, "end": float, "line_count": int, "text": str}, ...]
    """
    # 1. 去重：完全相同文本 5s 内重复 ≥2 次 → 只保留第一条
    dedup = []
    last_seen = {}  # text -> (index_in_dedup, time)
    for e in entries:
        key = e["text"].strip()
        prev = last_seen.get(key)
        if prev is not None and e["start"] - prev[1] <= 5.0:
            continue
        last_seen[key] = (len(dedup), e["start"])
        dedup.append(e)

    # 2. 滤污染
    clean_entries = []
    pollution = []
    for e in dedup:
        if is_pollution(e["text"]):
            pollution.append({"start": round(e["start"], 1), "text": e["text"][:50]})
        else:
            clean_entries.append(e)

    # 3. 对白块合并：相邻间隔 < gap_merge 并入同一块（对白连续性块，非叙事场景）
    scene_blocks = []
    for e in clean_entries:
        if scene_blocks and e["start"] - scene_blocks[-1]["end"] < gap_merge:
            blk = scene_blocks[-1]
            blk["end"] = max(blk["end"], e["end"])
            blk["line_count"] += 1
            if len(blk["text"]) < 200:
                blk["text"] += " " + e["text"]
        else:
            scene_blocks.append({
                "start": round(e["start"], 1),
                "end": round(e["end"], 1),
                "line_count": 1,
                "text": e["text"][:200],
            })
    for blk in scene_blocks:
        blk["end"] = round(blk["end"], 1)

    return clean_entries, pollution, scene_blocks


# ---------------------------------------------------------------- 片头片尾检测


LYRICS_TAIL_WORDS = ("了", "吧", "啊", "呀", "哦", "啦", "么", "吗", "呢")


def detect_credits(entries, user_head_end=None, user_tail_start=None):
    """片头片尾检测。

    优先级: 用户提供 > 自动检测。
    片尾: 从后往前找连续 ≥3 条 ≤6 字且非对话句式的行；
          歌词行（尾字重复/押韵）标记 lyrics_candidate，跳过找真正人名段；
          整段都是歌词 → tail_start 取歌词段起点（fallback）。
    """
    if user_head_end is not None or user_tail_start is not None:
        return {
            "head_end": round(user_head_end, 1) if user_head_end is not None else None,
            "tail_start": round(user_tail_start, 1) if user_tail_start is not None else None,
            "detection": "user_range",
        }

    # 从后往前收集短行（≤6 字 且 无对话标点）
    short_lines = []  # (index, start, text)
    for i in range(len(entries) - 1, -1, -1):
        text = entries[i]["text"].strip()
        if len(text) <= 6 and not any(p in text for p in "：:？！?…"):
            short_lines.append((i, entries[i]["start"], text))
        elif short_lines:
            # 遇到非短行，短行段结束
            break

    if not short_lines:
        return {"head_end": None, "tail_start": None, "detection": None}

    short_lines.reverse()  # 恢复正序

    # 找连续 ≥3 条的子段
    groups = []
    cur = [short_lines[0]]
    for j in range(1, len(short_lines)):
        if short_lines[j][0] == cur[-1][0] + 1:
            cur.append(short_lines[j])
        else:
            if len(cur) >= 3:
                groups.append(cur)
            cur = [short_lines[j]]
    if len(cur) >= 3:
        groups.append(cur)

    if not groups:
        return {"head_end": None, "tail_start": None, "detection": None}

    # 判断每组是否是歌词（尾字重复）
    def is_lyrics(group):
        if len(group) < 3:
            return False
        tails = [ln[2].strip()[-1:] for ln in group]
        repeat = sum(1 for a, b in zip(tails, tails[1:]) if a == b)
        tail_word_hits = sum(1 for t in tails if t in LYRICS_TAIL_WORDS)
        return repeat >= 1 and tail_word_hits >= 2

    lyrics_groups = [g for g in groups if is_lyrics(g)]
    real_groups = [g for g in groups if not is_lyrics(g)]

    if real_groups:
        # 取最靠后（接近片尾）的非歌词组起点
        start = real_groups[-1][0][1]
        return {"head_end": None, "tail_start": round(start, 1), "detection": "credits_pattern"}

    if lyrics_groups:
        # 全部是歌词 → fallback 取最早歌词组起点（把歌词段也当片尾）
        start = min(g[0][1] for g in lyrics_groups)
        return {"head_end": None, "tail_start": round(start, 1), "detection": "credits_pattern_lyrics_fallback"}

    return {"head_end": None, "tail_start": None, "detection": None}


# ---------------------------------------------------------------- 密度曲线 / 无字幕段


def density_curve(entries, total_seconds, window=60, density_limit=5):
    """按窗口统计字幕条数，输出 density.points 和 visual_segments(low_density)。"""
    points = []
    w_start = 0.0
    idx = 0
    n = len(entries)
    while w_start < total_seconds:
        w_end = w_start + window
        count = 0
        while idx < n and entries[idx]["start"] < w_end:
            count += 1
            idx += 1
        points.append({"start": round(w_start, 1), "count": count, "visual": count < density_limit})
        w_start = w_end

    visual_segments = []
    seg = None
    for pt in points:
        if pt["visual"]:
            if seg is None:
                seg = {"start": pt["start"], "counts": [pt["count"]]}
            else:
                seg["counts"].append(pt["count"])
        else:
            if seg:
                visual_segments.append({
                    "start": round(seg["start"], 1),
                    "end": round(seg["start"] + window * len(seg["counts"]), 1),
                    "reason": "low_density",
                    "avg_density": round(sum(seg["counts"]) / len(seg["counts"]), 1),
                })
                seg = None
    if seg:
        visual_segments.append({
            "start": round(seg["start"], 1),
            "end": round(seg["start"] + window * len(seg["counts"]), 1),
            "reason": "low_density",
            "avg_density": round(sum(seg["counts"]) / len(seg["counts"]), 1),
        })
    return points, visual_segments


def find_gaps(entries, threshold=20):
    """无字幕段：相邻字幕间隔 ≥ threshold。复用 find_gaps.py 的判定逻辑。"""
    gaps = []
    for i in range(1, len(entries)):
        gap = entries[i]["start"] - entries[i - 1]["end"]
        if gap >= threshold:
            gaps.append({
                "start": round(entries[i - 1]["end"], 1),
                "end": round(entries[i]["start"], 1),
                "duration": round(gap, 1),
                "prev_subtitle": entries[i - 1]["text"][:40],
                "next_subtitle": entries[i]["text"][:40],
            })
    return gaps


# ---------------------------------------------------------------- 人物频次


def count_people(entries, people_path):
    """词典匹配人名频次。people_path 不存在则跳过。"""
    if not people_path or not os.path.isfile(people_path):
        return []
    with open(people_path, "r", encoding="utf-8") as f:
        names = [ln.strip() for ln in f if ln.strip()]
    results = []
    for name in names:
        count = 0
        first_at = None
        last_at = None
        for e in entries:
            if name in e["text"]:
                count += 1
                if first_at is None:
                    first_at = e["start"]
                last_at = e["start"]
        if count > 0:
            results.append({
                "name": name,
                "count": count,
                "first_at": round(first_at, 1) if first_at else None,
                "last_at": round(last_at, 1) if last_at else None,
            })
    results.sort(key=lambda r: -r["count"])
    return results


# ---------------------------------------------------------------- 长对白段


def filter_bilingual(entries):
    """双语字幕处理：紧跟中文行之后、间隔 <2s 的全英文行视为翻译行，
    不参与信号统计（密度/长对白），但保留在 entries 里供 AI 参考。

    返回 (有效行列表, 翻译行数)。纯英文电影字幕不受影响（无中文前置行）。
    """
    valid = []
    translation_count = 0
    for i, e in enumerate(entries):
        text = e["text"].strip()
        is_full_english = bool(text) and not CHINESE.search(text) and LATIN.search(text)
        if is_full_english and i > 0:
            prev = entries[i - 1]
            prev_has_chinese = bool(CHINESE.search(prev["text"]))
            if prev_has_chinese and e["start"] - prev["end"] < 2.0:
                translation_count += 1
                continue
        valid.append(e)
    return valid, translation_count


def find_long_dialogues(entries, min_lines=5, min_duration=30, max_gap=10):
    """≥5 条连续字幕 且 首尾 ≥30s 且 期间无 ≥10s 间隔。段结束时结算一次。

    实片验证调整（拆弹专家2）：3 条/20s 会命中 1000+ 段，无法精读；
    收紧到 5 条/30s 后数量可用。修正：每段只输出一次（原实现同一段重复输出）。
    """
    results = []

    def emit(cur):
        if len(cur) >= min_lines:
            duration = cur[-1]["end"] - cur[0]["start"]
            if duration >= min_duration:
                results.append({
                    "start": round(cur[0]["start"], 1),
                    "end": round(cur[-1]["end"], 1),
                    "duration": round(duration, 1),
                    "line_count": len(cur),
                    "text_preview": cur[0]["text"][:80],
                })

    cur = []
    for e in entries:
        if cur and e["start"] - cur[-1]["end"] >= max_gap:
            emit(cur)
            cur = []
        cur.append(e)
    emit(cur)
    return results


# ---------------------------------------------------------------- 报告组装


def build_report(entries, warnings, encoding, args, pollution, scene_blocks,
                 credits, points, visual_segments, gaps, people, dialogues):
    total_seconds = round(entries[-1]["end"], 1) if entries else 0
    durations = [e["end"] - e["start"] for e in entries]
    longest_gap = max((g["duration"] for g in gaps), default=0)

    report = {
        "meta": {
            "srt_file": os.path.basename(args.srt),
            "encoding": encoding,
            "total_subtitles": len(entries),
            "total_seconds": total_seconds,
            "analyze_start": args.start,
            "analyze_end": args.end if args.end else total_seconds,
            "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "warnings": warnings[:20],
        },
        "credits": credits,
        "pollution": {"total_removed": len(pollution), "locations": pollution[:50]},
        "stats": {
            "subtitle_count": len(entries),
            "avg_duration": round(statistics.mean(durations), 2) if durations else 0,
            "median_duration": round(statistics.median(durations), 2) if durations else 0,
            "longest_gap": longest_gap,
        },
        "density": {
            "window_seconds": args.window,
            "points": points,
        },
        "visual_segments": visual_segments,
        "gaps": gaps,
        "people": people,
        "long_dialogues": dialogues,
        "scene_blocks": scene_blocks,
    }
    return report


def render_markdown(report, srt_path):
    m = []
    meta = report["meta"]
    m.append(f"# 字幕信号分析报告：{meta['srt_file']}")
    m.append("")
    m.append(f"- 编码：{meta['encoding']} ｜ 字幕条数：{meta['total_subtitles']} ｜ 总时长：{meta['total_seconds']}s")
    m.append(f"- 分析区间：{meta['analyze_start']} ~ {meta['analyze_end']}s")
    m.append("")
    credits = report["credits"]
    m.append("## 片头片尾")
    m.append("")
    m.append(f"- 片尾起点 tail_start：{credits['tail_start']}（检测来源：{credits['detection']}）")
    m.append(f"- 片头终点 head_end：{credits['head_end']}")
    m.append("- **所有 clips 时间戳必须限定在 [head_end, tail_start] 区间内**；人工提供的片头片尾区间优先于自动检测")
    m.append("")

    pol = report["pollution"]
    if pol["total_removed"] > 0:
        m.append("## 字幕污染（已剔除）")
        m.append("")
        m.append(f"共剔除 {pol['total_removed']} 行，位置（前 50 条）：")
        for loc in pol["locations"]:
            m.append(f"- {loc['start']}s: {loc['text']}")
        m.append("")

    m.append("## 对话密度概览（visual 段 = 低字幕密度，可能是动作/过场）")
    m.append("")
    for seg in report["visual_segments"]:
        m.append(f"- [{seg['start']}s ~ {seg['end']}s] {seg['reason']}（平均 {seg.get('avg_density', '?')} 条/窗口）")
    m.append("")

    m.append("## 无字幕段（≥阈值）")
    m.append("")
    for g in report["gaps"]:
        m.append(f"- {g['start']}s ~ {g['end']}s（{g['duration']}s）前：{g['prev_subtitle']} / 后：{g['next_subtitle']}")
    m.append("")

    if report["people"]:
        m.append("## 人物频次 Top 20")
        m.append("")
        for p in report["people"][:20]:
            m.append(f"- {p['name']}：{p['count']} 次（首 {p['first_at']}s / 末 {p['last_at']}s）")
        m.append("")

    m.append("## 长对白段（文戏冲突点 / 旁白素材池）")
    m.append("")
    for d in report["long_dialogues"][:30]:
        m.append(f"- [{d['start']}s ~ {d['end']}s] {d['line_count']} 条 / {d['duration']}s：{d['text_preview']}")
    m.append("")

    m.append("## 对白连续性块（scene_blocks，注意：非叙事场景，仅供定位密集对白区）")
    m.append("")
    for b in report["scene_blocks"][:30]:
        m.append(f"- [{b['start']}s ~ {b['end']}s] {b['line_count']} 条：{b['text'][:50]}")
    m.append("")

    m.append("## 给 AI 的使用说明")
    m.append("")
    m.append("1. 先读本报告建立全片节奏地图，只精读 visual_segments / gaps / long_dialogues / scene_blocks 标记的区域，禁止全量裸读 SRT")
    m.append("2. visual_segments 与 gaps 标注的段：若计划剪进成片，必须走 find_gaps 交叉验证 + 画面确认")
    m.append("3. SEGMENTS 所有 clips 必须落在 [head_end, tail_start] 内")
    return "\n".join(m)


# ---------------------------------------------------------------- 主流程


def main():
    ap = argparse.ArgumentParser(description="字幕信号分析脚本")
    ap.add_argument("srt", help="SRT 字幕文件路径")
    ap.add_argument("--start", type=float, default=0, help="分析起点秒（跳过片头），默认 0")
    ap.add_argument("--end", type=float, default=None, help="分析终点秒（跳过片尾），默认文件末尾")
    ap.add_argument("--threshold", type=float, default=20, help="无字幕段阈值秒，默认 20")
    ap.add_argument("--window", type=float, default=60, help="对话密度窗口秒，默认 60")
    ap.add_argument("--density-limit", type=int, default=5, help="视觉段密度阈值条/窗口，默认 5")
    ap.add_argument("--gap-merge", type=float, default=3, help="对白块合并间隔秒，默认 3")
    ap.add_argument("--people", default=None, help="人名词典文件（每行一个名字，可选）")
    ap.add_argument("--head-end", type=float, default=None, help="人工提供的片头终点秒（可选）")
    ap.add_argument("--tail-start", type=float, default=None, help="人工提供的片尾起点秒（可选）")
    ap.add_argument("--json", default=None, help="JSON 报告输出路径（默认 SRT 同目录）")
    ap.add_argument("--md", default=None, help="Markdown 报告输出路径（默认 SRT 同目录）")
    args = ap.parse_args()

    if not os.path.isfile(args.srt):
        sys.exit(f"错误: 文件不存在 {args.srt}")

    # 解析
    entries, warnings, encoding = parse_srt(args.srt)
    if not entries:
        sys.exit("错误: SRT 无有效字幕")

    # 区间裁剪
    if args.start > 0 or args.end is not None:
        entries = [e for e in entries if e["start"] >= args.start and (args.end is None or e["end"] <= args.end)]
        if not entries:
            sys.exit("错误: 指定区间内无字幕")

    # 清洗
    clean_entries, pollution, scene_blocks = clean(entries, gap_merge=args.gap_merge)

    # 片头片尾
    credits = detect_credits(clean_entries, user_head_end=args.head_end, user_tail_start=args.tail_start)

    # 密度 + 无字幕段 + 人物 + 长对白
    # 信号统计用过滤双语翻译行后的列表；gaps 用原始列表（与 find_gaps.py 输出一致）
    signal_entries, translation_count = filter_bilingual(clean_entries)
    total_seconds = signal_entries[-1]["end"]
    points, low_density_segs = density_curve(signal_entries, total_seconds, args.window, args.density_limit)
    gaps = find_gaps(clean_entries, threshold=args.threshold)
    # visual_segments = low_density + no_subtitle（gaps 并入）
    visual_segments = list(low_density_segs)
    for g in gaps:
        visual_segments.append({
            "start": g["start"],
            "end": g["end"],
            "reason": "no_subtitle",
            "gap_duration": g["duration"],
            "prev_subtitle": g["prev_subtitle"],
            "next_subtitle": g["next_subtitle"],
        })
    visual_segments.sort(key=lambda s: s["start"])

    people = count_people(signal_entries, args.people)
    dialogues = find_long_dialogues(signal_entries)

    report = build_report(clean_entries, warnings, encoding, args, pollution, scene_blocks,
                          credits, points, visual_segments, gaps, people, dialogues)

    # 输出
    srt_dir = os.path.dirname(os.path.abspath(args.srt))
    srt_base = os.path.splitext(os.path.basename(args.srt))[0]
    json_out = args.json or os.path.join(srt_dir, f"{srt_base}.report.json")
    md_out = args.md or os.path.join(srt_dir, f"{srt_base}.report.md")

    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    with open(md_out, "w", encoding="utf-8") as f:
        f.write(render_markdown(report, args.srt))

    print(f"完成: {len(clean_entries)} 条字幕, 片尾起点={credits['tail_start']} ({credits['detection']}), "
          f"污染剔除={len(pollution)}, 无字幕段={len(gaps)}")
    print(f"JSON: {json_out}")
    print(f"MD  : {md_out}")


if __name__ == "__main__":
    main()
