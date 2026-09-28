# -*- coding: utf-8 -*-
"""无字幕段扫描 - 找出SRT中相邻字幕间隔超过阈值的时间段

用途:
  电影有大量纯画面段落（动作戏、场景转换、无声冲突），字幕里没有的就是
  剪辑工具看不到的。此脚本扫描SRT，找出这些"无字幕段"，辅助判断哪些段
  可能是过场（可删）或关键剧情（需用户确认）。

使用方法:
  python find_gaps.py "字幕.srt" --threshold 20
  python find_gaps.py "字幕.srt" --threshold 15 --start 444 --end 4220

参数:
  srt_path    SRT字幕文件路径
  --threshold 间隔阈值（秒），默认20
  --start     只扫描此秒数之后的内容（跳过片头）
  --end       只扫描此秒数之前的内容（跳过片尾）

输出:
  打印每个无字幕段的: 起止时间、持续秒数、前后字幕文本（帮助判断内容）
"""
import sys, re, argparse

sys.stdout.reconfigure(encoding="utf-8")


def parse_srt(srt_path):
    """解析SRT文件，返回 [(index, start_sec, end_sec, text), ...]"""
    with open(srt_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    # SRT格式: 序号\n开始时间 --> 结束时间\n文本\n空行
    blocks = re.split(r"\n\s*\n", content.strip())
    entries = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        # 第一行: 序号
        try:
            idx = int(lines[0].strip())
        except ValueError:
            continue
        # 第二行: 时间戳
        time_match = re.match(
            r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})",
            lines[1].strip()
        )
        if not time_match:
            continue
        h1, m1, s1, ms1, h2, m2, s2, ms2 = time_match.groups()
        start_sec = int(h1) * 3600 + int(m1) * 60 + int(s1) + int(ms1) / 1000
        end_sec = int(h2) * 3600 + int(m2) * 60 + int(s2) + int(ms2) / 1000
        # 第三行起: 文本
        text = " ".join(lines[2:]).strip()
        entries.append((idx, start_sec, end_sec, text))
    return entries


def fmt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def find_gaps(srt_path, threshold=20, start_sec=0, end_sec=None):
    entries = parse_srt(srt_path)
    if not entries:
        print("错误: 未解析到字幕条目")
        return

    print(f"字幕总数: {len(entries)}")
    print(f"扫描区间: {fmt_time(start_sec)} - {fmt_time(end_sec or entries[-1][2])}")
    print(f"间隔阈值: {threshold}秒")
    print("=" * 70)

    gaps = []
    for i in range(len(entries) - 1):
        cur_end = entries[i][2]
        next_start = entries[i + 1][1]

        # 过滤区间外
        if cur_end < start_sec:
            continue
        if end_sec and next_start > end_sec:
            continue

        gap = next_start - cur_end
        if gap >= threshold:
            gap_info = {
                "gap_start": cur_end,
                "gap_end": next_start,
                "duration": gap,
                "prev_idx": entries[i][0],
                "prev_text": entries[i][3],
                "next_idx": entries[i + 1][0],
                "next_text": entries[i + 1][3],
            }
            gaps.append(gap_info)

    print(f"找到 {len(gaps)} 个无字幕段 (间隔>={threshold}s):\n")
    for i, g in enumerate(gaps):
        print(f"  [{i+1}] {fmt_time(g['gap_start'])} - {fmt_time(g['gap_end'])} "
              f"({g['duration']:.0f}s)")
        print(f"      前字幕 #{g['prev_idx']}: {g['prev_text'][:40]}")
        print(f"      后字幕 #{g['next_idx']}: {g['next_text'][:40]}")
        print()

    # 提示
    long_gaps = [g for g in gaps if g["duration"] >= 60]
    if long_gaps:
        print(f"⚠️ 有 {len(long_gaps)} 个超过60秒的无字幕段，可能是:")
        print("  - 过场/风景/时间流逝（建议删除）")
        print("  - 动作戏/无声冲突（需用户确认内容）")
        print("  - 片头/片尾（可跳过）")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="扫描SRT字幕中的无字幕段")
    parser.add_argument("srt_path", help="SRT字幕文件路径")
    parser.add_argument("--threshold", type=int, default=20,
                        help="间隔阈值（秒），默认20")
    parser.add_argument("--start", type=int, default=0,
                        help="扫描起始秒数（跳过片头）")
    parser.add_argument("--end", type=int, default=None,
                        help="扫描结束秒数（跳过片尾）")
    args = parser.parse_args()
    find_gaps(args.srt_path, args.threshold, args.start, args.end)
