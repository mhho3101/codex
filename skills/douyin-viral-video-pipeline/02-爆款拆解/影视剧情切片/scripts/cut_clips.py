"""按配置切割并默认拼接；碎片保留。流复制受关键帧影响，严格时长用 --reencode。"""
import subprocess, sys, os, json, argparse, tempfile
from pathlib import Path
from clip_checks import executable, probe, validate, check_media

sys.stdout.reconfigure(encoding="utf-8")


# ==================== 工具函数 ====================

def fmt_time(sec):
    """秒数格式化为 HH:MM:SS"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def run_cmd(cmd):
    """运行命令，返回 (成功?, stderr)"""
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return r.returncode == 0, r.stderr


def get_duration(filepath, ffprobe):
    """用 ffprobe 获取视频时长（秒）"""
    cmd = [ffprobe, "-v", "error", "-show_entries", "format=duration",
           "-of", "csv=p=0", filepath]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    try:
        return float(r.stdout.strip())
    except (ValueError, TypeError):
        return 0.0


# ==================== 切割逻辑 ====================

def cut_clip(start, end, out_path, src, ffmpeg, reencode=False, crf=18, preset="fast"):
    """切出一段视频

    无损模式(reencode=False, 默认): -c copy 流复制，100%无损、秒级，切割点受关键帧限制
    重编码模式(reencode=True): libx264 -crf 18 重编码，精确到秒，但慢、文件略大
    """
    dur = end - start
    if reencode:
        cmd = [ffmpeg, "-nostdin", "-y",
               "-ss", str(start),
               "-t", str(dur),
               "-i", src,
               "-map", "0:v:0", "-map", "0:a:0?",
               "-c:v", "libx264", "-crf", str(crf), "-preset", preset,
               "-c:a", "aac",
               "-avoid_negative_ts", "make_zero",
               out_path]
    else:
        cmd = [ffmpeg, "-nostdin", "-y",
               "-ss", str(start),
               "-t", str(dur),
               "-i", src,
               "-map", "0:v:0", "-map", "0:a:0?",
               "-c", "copy",
               "-avoid_negative_ts", "make_zero",
               out_path]
    ok, err = run_cmd(cmd)
    return ok, err


def merge_segment(seg_dir, seg_name, clip_files, ffmpeg):
    """使用 concat demuxer，不假定原片一定是 H.264。"""
    with tempfile.TemporaryDirectory(prefix="merge_", dir=seg_dir) as temp:
        listing = Path(temp)/"list.txt"
        listing.write_text("".join("file '" + Path(f).resolve().as_posix().replace("'", "'\\''") + "'\n" for f in clip_files), encoding="utf-8")
        target = Path(temp)/"merged.mp4"
        ok, err = run_cmd([ffmpeg, "-nostdin", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(target)])
        if not ok:
            print(f"拼接失败：{err[-300:]}")
            return False
        target.replace(Path(seg_dir)/f"{seg_name}.mp4")
        return True


def process_segment(num, title, clips, narrations,
                    movie_name, src, out_dir, ffmpeg, ffprobe,
                    reencode=False, crf=18, preset="fast", merge=True):
    """处理一条视频: 创建目录, 逐段切出, 写txt, 可选拼接完整视频"""
    seg_name = f"{movie_name}（{num}）{title}"
    seg_dir = os.path.join(out_dir, seg_name)
    os.makedirs(seg_dir, exist_ok=True)

    print(f"\n--- 第{num}条: {title} ---")

    clip_infos = []  # [(文件名, 设计时长, 实际时长, 原片start, 原片end), ...]
    total_design = 0
    total_actual = 0

    for i, (start, end) in enumerate(clips):
        clip_num = i + 1
        design_dur = end - start
        out_name = f"{seg_name}-{clip_num}.mp4"
        out_path = os.path.join(seg_dir, out_name)

        ok, err = cut_clip(start, end, out_path, src, ffmpeg,
                            reencode, crf, preset)
        if not ok:
            print(f"  片段{clip_num}切割失败: {err[-300:]}")
            return False

        actual_dur = get_duration(out_path, ffprobe)
        sz_mb = os.path.getsize(out_path) // (1024 * 1024)
        clip_infos.append((out_name, design_dur, actual_dur, start, end))
        total_design += design_dur
        total_actual += actual_dur
        print(f"  片段{clip_num}: {fmt_time(start)}-{fmt_time(end)} "
              f"(设计{design_dur}s/实际{actual_dur:.1f}s) {sz_mb}MB")

    # 拼接完整视频（默认开启，--no-merge 关闭；碎片始终保留）
    merged_ok = False
    merged_dur = 0.0
    if merge:
        clip_files = [os.path.join(seg_dir, f"{seg_name}-{i+1}.mp4")
                      for i in range(len(clips))]
        if merge_segment(seg_dir, seg_name, clip_files, ffmpeg):
            merged_ok = True
            merged_dur = get_duration(
                os.path.join(seg_dir, f"{seg_name}.mp4"), ffprobe)
            print(f"  -> 拼接后总时长: {merged_dur:.1f}s")
        else:
            print(f"  ⚠️ 拼接失败（碎片仍保留，可手动拼接）")

    # 写对应关系文件
    txt_path = os.path.join(seg_dir, f"{seg_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"{seg_name}\n")
        if merged_ok:
            f.write(f"拼接文件: {seg_name}.mp4（{merged_dur:.1f}s，碎片+完整版均保留）\n")
        elif merge:
            f.write("拼接文件: 拼接失败（碎片已保留，请检查 ffmpeg 或手动拼接）\n")
        else:
            f.write("拼接文件: 未拼接（--no-merge 模式，仅碎片）\n")
        f.write(f"设计总时长: {total_design}s / 实际总时长: {total_actual:.1f}s\n")
        f.write(f"原片规格: {'重编码精确切割 (libx264 -crf %d)' % crf if reencode else '无损流复制 (-c copy)'}\n\n")

        f.write("=" * 50 + "\n")
        f.write("【片段构成】\n")
        for i, (fname, design, actual, start, end) in enumerate(clip_infos):
            f.write(f"  片段{i+1}: {fname}\n")
            f.write(f"    原片 {fmt_time(start)} - {fmt_time(end)} "
                    f"(设计{design}s / 实际{actual:.1f}s)\n")
        f.write(f"  合计: 设计{total_design}s / 实际{total_actual:.1f}s")
        if reencode:
            f.write(f"(重编码模式，精确到秒，偏差约{total_actual-total_design:.1f}s)\n\n")
        else:
            f.write(f"(关键帧对齐偏差约{total_actual-total_design:.0f}s)\n\n")

        f.write("=" * 50 + "\n")
        f.write("【旁白花字】(标明在哪个片段的第几秒)\n")
        for n in narrations:
            text = n.get("text", "")
            clip_num = n.get("clip", 1)
            rel_sec = n.get("after_sec", 3)
            f.write(f"  片段{clip_num} [{fmt_time(rel_sec)}] {text}\n")

        f.write("\n" + "=" * 50 + "\n")
        f.write("【原片对白参考】\n")
        for i, (fname, design, actual, start, end) in enumerate(clip_infos):
            f.write(f"\n  片段{i+1} (原片 {fmt_time(start)}-{fmt_time(end)}):\n")
            f.write(f"    请对照原片字幕查看该时段对白\n")

    print(f"  -> 碎片合计: 计划{total_design}s / 实际{total_actual:.1f}s；最终结果以检查清单为准")
    return (not merge) or merged_ok


# ==================== 配置加载 ====================

# ==================== 主入口 ====================

def main():
    ap = argparse.ArgumentParser(
        description="电影剧情短视频剪辑 — 从 JSON 配置文件读取所有参数")
    ap.add_argument("--config", required=True,
                    help="电影 JSON 配置文件路径（模板见 assets/movie_config_template.json）")
    ap.add_argument("--reencode", action="store_true",
                    help="重编码精确切割(默认关，关闭时为无损 -c copy)")
    ap.add_argument("--crf", type=int, default=18,
                    help="重编码质量(默认18，越低质量越好文件越大，范围 0–51)")
    ap.add_argument("--preset", default="fast",
                    help="重编码速度档(默认fast)")
    ap.add_argument("--no-merge", action="store_true",
                    help="不拼接完整视频(默认拼接：碎片+完整版都保留)")
    ap.add_argument("--check-only", action="store_true", help="只检查配置和原片，不生成文件")
    ap.add_argument("--overwrite", action="store_true", help="允许覆盖同名输出；默认拒绝")
    args = ap.parse_args()

    try:
        config_path = Path(args.config).resolve()
        cfg = json.loads(config_path.read_text(encoding="utf-8-sig"))
        for key in ("src", "out_dir"):
            cfg[key] = str((config_path.parent / cfg[key]).resolve())
        ffmpeg = executable(cfg.get("ffmpeg", "ffmpeg"))
        ffprobe = executable(cfg.get("ffprobe", "ffprobe"))
        if not 0 <= args.crf <= 51:
            raise ValueError("crf 必须在 0–51 之间")
        source = probe(cfg["src"], ffprobe)
        validate(cfg, source)
        root = Path(cfg["out_dir"])
        movie = cfg["movie_name"]
        manifest_path = root/f"{movie}_segments_manifest.json"
        if args.check_only:
            print("配置和原片检查通过；没有生成文件。")
            return 0
        outputs = [root/f"{movie}（{seg['num']}）{seg['title']}" for seg in cfg["segments"]]
        if not args.overwrite and any(path.exists() for path in [manifest_path]+outputs):
            raise ValueError("同名输出已经存在；请选择新目录，或明确使用 --overwrite")
        root.mkdir(parents=True, exist_ok=True)
        manifest = dict(version=2, movie=movie, source_info=source, status="running",
                        limits=[cfg.get("min_duration", 50), cfg.get("max_duration", 75)],
                        merge_requested=not args.no_merge, expected_count=len(cfg["segments"]), segments=[])
        def save():
            temp = manifest_path.with_suffix(".tmp")
            temp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            temp.replace(manifest_path)
        save()
        failures = 0
        for seg, directory in zip(cfg["segments"], outputs):
            record = dict(num=seg["num"], title=seg["title"], clips=seg["clips"], pieces=[], status="failed")
            try:
                ok = process_segment(seg["num"], seg["title"], seg["clips"], seg.get("narrations", []),
                                     movie, cfg["src"], str(root), ffmpeg, ffprobe,
                                     args.reencode, args.crf, args.preset, merge=not args.no_merge)
                if not ok:
                    raise ValueError("切割或拼接失败，已经生成的片段保留；本条不算完成")
                for index in range(len(seg["clips"])):
                    piece = directory/f"{directory.name}-{index+1}.mp4"
                    info = probe(piece, ffprobe)
                    check_media(info, source)
                    record["pieces"].append(str(piece.relative_to(root)))
                if not args.no_merge:
                    final = directory/f"{directory.name}.mp4"
                    record["final"] = str(final.relative_to(root))
                    check_media(probe(final, ffprobe), source, manifest["limits"])
                record["status"] = "pieces_only" if args.no_merge else "complete"
            except (OSError, ValueError, KeyError) as exc:
                failures += 1
                record["error"] = str(exc)
                record["preserved_files"] = [str(x.relative_to(root)) for x in directory.glob("*.mp4")]
                print(f"第 {seg['num']} 条未完成：{exc}")
            manifest["segments"].append(record)
            save()
        manifest["status"] = "partial_or_failed" if failures else ("pieces_only" if args.no_merge else "complete")
        save()
        print(f"完成 {len(cfg['segments'])-failures} 条，未完成 {failures} 条。清单：{manifest_path}")
        return 1 if failures else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"无法执行：{exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
