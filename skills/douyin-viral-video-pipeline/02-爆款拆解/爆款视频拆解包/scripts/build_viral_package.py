import argparse
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def safe_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def sec_label(seconds: float) -> str:
    total = max(0, int(seconds))
    return f"{total // 60:02}:{total % 60:02}"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def probe_duration(video: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return float(result.stdout.strip())


def timestamp_slug(seconds: float) -> str:
    return f"{seconds:05.1f}s".replace(".", "p")


def plan_keyframe_times(duration: float, count: int) -> list[float]:
    times: list[float] = []

    def add(timestamp: float) -> None:
        if len(times) >= count:
            return
        if timestamp > duration - 0.2:
            return
        timestamp = max(0.1, timestamp)
        if any(abs(timestamp - existing) < 0.35 for existing in times):
            return
        times.append(timestamp)

    for timestamp in (0.5, 1.5, 3.0, 5.0):
        add(timestamp)

    remaining = count - len(times)
    if remaining > 0:
        fill_start = min(8.0, max(0.5, duration - 1.0))
        fill_end = max(fill_start, duration - 1.0)
        if remaining == 1:
            add((fill_start + fill_end) / 2)
        else:
            for index in range(remaining):
                ratio = index / (remaining - 1)
                add(fill_start + (fill_end - fill_start) * ratio)

    probe_slots = max(count * 2, 8)
    for index in range(probe_slots):
        add(duration * (index + 1) / (probe_slots + 1))

    return sorted(times[:count])


def load_timecoded_segments(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    segments = data.get("segments", data if isinstance(data, list) else [])
    rows = []
    for seg in segments:
        text = safe_text(str(seg.get("text", "")))
        if not text:
            continue
        rows.append(
            {
                "start": float(seg["start"]),
                "end": float(seg["end"]),
                "text": text,
            }
        )
    return sorted(rows, key=lambda item: item["start"])


def load_speaker_segments(path: Path | None) -> list[dict]:
    if not path or not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    item = data[0] if isinstance(data, list) and data else data
    sentence_info = item.get("sentence_info") or []
    rows = []
    for seg in sentence_info:
        text = safe_text(str(seg.get("text", "")))
        if not text:
            continue
        start = float(seg.get("start", 0)) / 1000
        end = float(seg.get("end", start * 1000)) / 1000
        rows.append({"start": start, "end": end, "spk": seg.get("spk"), "text": text})
    return rows


def overlap(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    return max(0.0, min(a_end, b_end) - max(a_start, b_start))


def assign_speaker(segment: dict, speakers: list[dict], aliases: dict) -> str:
    best_spk = None
    best_overlap = 0.0
    for spk_seg in speakers:
        value = overlap(segment["start"], segment["end"], spk_seg["start"], spk_seg["end"])
        if value > best_overlap:
            best_overlap = value
            best_spk = spk_seg["spk"]
    if best_spk is None:
        return "说话人?"
    if best_spk not in aliases:
        aliases[best_spk] = f"说话人{chr(ord('A') + len(aliases))}"
    return aliases[best_spk]


def merge_segments(segments: list[dict], speakers: list[dict]) -> list[dict]:
    aliases: dict = {}
    assigned = []
    for seg in segments:
        speaker = assign_speaker(seg, speakers, aliases) if speakers else "说话人"
        assigned.append({**seg, "speaker": speaker})

    merged = []
    for seg in assigned:
        if merged:
            prev = merged[-1]
            gap = seg["start"] - prev["end"]
            combined = f"{prev['text']} {seg['text']}".strip()
            if (
                prev["speaker"] == seg["speaker"]
                and gap <= 0.8
                and len(combined) <= 90
                and seg["end"] - prev["start"] <= 8
            ):
                prev["end"] = seg["end"]
                prev["text"] = combined
                continue
        merged.append(dict(seg))
    return merged


def extract_keyframes(video: Path, keyframe_dir: Path, count: int) -> list[Path]:
    keyframe_dir.mkdir(parents=True, exist_ok=True)
    for pattern in ("opening_*.jpg", "selected_*.jpg", "contact_sheet.jpg"):
        for old_frame in keyframe_dir.glob(pattern):
            old_frame.unlink()
    duration = probe_duration(video)
    if duration <= 0:
        raise RuntimeError("Could not probe video duration")
    times = plan_keyframe_times(duration, count)

    frames = []
    for index, timestamp in enumerate(times, start=1):
        prefix = "opening" if timestamp <= 5.05 else "selected"
        out = keyframe_dir / f"{prefix}_{index:02}_{timestamp_slug(timestamp)}.jpg"
        run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{timestamp:.2f}",
                "-i",
                str(video),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                "-update",
                "1",
                str(out),
            ]
        )
        frames.append(out)
    return frames


def make_contact_sheet(frames: list[Path], output: Path) -> None:
    if not frames:
        return
    thumbs = []
    for path in frames:
        image = Image.open(path).convert("RGB")
        image.thumbnail((260, 462))
        canvas = Image.new("RGB", (260, 492), "white")
        x = (260 - image.width) // 2
        canvas.paste(image, (x, 0))
        draw = ImageDraw.Draw(canvas)
        draw.text((10, 466), path.stem, fill=(30, 30, 30), font=ImageFont.load_default())
        thumbs.append(canvas)

    cols = min(4, len(thumbs))
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 260, rows * 492), "white")
    for index, thumb in enumerate(thumbs):
        x = (index % cols) * 260
        y = (index // cols) * 492
        sheet.paste(thumb, (x, y))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=92)


def write_speaker_transcript(path: Path, title: str, segments: list[dict]) -> None:
    lines = [
        "# 说话人逐字稿",
        "",
        f"视频：{title}",
        "",
        "> 说明：说话人标签为自动推断，用于内容拆解；最终创作前建议结合原视频快速复核。",
        "",
    ]
    for seg in segments:
        lines.append(
            f"- [{sec_label(seg['start'])}-{sec_label(seg['end'])}] {seg['speaker']}：{seg['text']}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_reference_text(path: Path | None) -> str:
    if not path or not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^#.*?\n+", "", text, flags=re.S)
    text = re.sub(r"^>.*?\n+", "", text, flags=re.M)
    return safe_text(text)


def transcript_until(transcript: list[dict], end: float, limit: int = 220) -> str:
    pieces = []
    for seg in transcript:
        if seg["start"] >= end:
            continue
        text = seg["text"]
        if seg["end"] > end and seg["end"] > seg["start"]:
            ratio = max(0.05, (end - seg["start"]) / (seg["end"] - seg["start"]))
            text = text[: max(1, int(len(text) * ratio))].rstrip() + "..."
        pieces.append(text)
    return safe_text(" ".join(pieces))[:limit]


def split_title_tags(title: str) -> tuple[str, list[str]]:
    tags = re.findall(r"#\s*([^\s#]+)", title or "")
    clean_title = re.sub(r"\s*#\s*[^\s#]+", "", title or "").strip()
    return clean_title or title, tags


def pick_interesting_lines(transcript: list[dict], limit: int = 8) -> list[dict]:
    keywords = (
        "反转",
        "没想到",
        "离谱",
        "崩溃",
        "破防",
        "救命",
        "笑死",
        "心疼",
        "爽",
        "尴尬",
        "误会",
        "真相",
        "秘密",
        "骗",
        "装",
        "原来",
        "结果",
        "但是",
        "怎么办",
        "不行",
        "为什么",
        "凭什么",
        "你敢",
        "别急",
        "等等",
        "最后",
        "第一次",
        "再也不",
        "我以为",
        "他/她居然",
    )
    picked = []
    for seg in transcript:
        text = seg["text"]
        score = sum(1 for keyword in keywords if keyword in text)
        if score:
            picked.append({**seg, "score": score})
    picked.sort(key=lambda item: (-item["score"], item["start"]))
    return sorted(picked[:limit], key=lambda item: item["start"])


def write_story_analysis(path: Path, title: str, transcript: list[dict], sensevoice_text: str) -> None:
    full_text = " ".join(seg["text"] for seg in transcript)
    reference = sensevoice_text or full_text
    opening = safe_text(reference[:180])
    ending = safe_text(reference[-220:])
    first_3s = transcript_until(transcript, 3.0) or "待结合 opening_*.jpg 和原视频补充。"
    first_5s = transcript_until(transcript, 5.0) or "待结合 opening_*.jpg 和原视频补充。"
    interesting_lines = pick_interesting_lines(transcript)
    clean_title, tags = split_title_tags(title)
    tag_text = "、".join(f"#{tag}" for tag in tags) if tags else "未识别到标签"
    lines = [
        "# 剧情分析",
        "",
        f"视频：{title}",
        "",
        "## 1. 一句话总结",
        "",
        "本节需要结合逐字稿和关键帧精修：写清这条视频的核心冲突、反转和情绪出口。",
        "",
        "## 2. 标题 / 标签分析",
        "",
        f"- 原标题：{clean_title}",
        f"- 标签：{tag_text}",
        "- 标题分析：看标题是否包含强冲突、强情绪、反转预告、目标人群暗示。",
        "- 标签分析：看标签如何绑定目标人群、行业痛点、平台推荐语境。",
        "- 通用迁移：保留标题里的情绪钩子、人群标签和承诺，再替换成你的账号领域、目标观众和核心痛点。",
        "",
        "## 3. 前 3 秒 / 前 5 秒钩子",
        "",
        f"- 约 0-3s 台词信息：{first_3s}",
        f"- 约 0-5s 台词信息：{first_5s}",
        "- 重点检查：第一句话是否直接抛出冲突，第一眼画面是否能看出身份/场景，5 秒内有没有制造继续看的悬念。",
        "- 对应画面：优先查看 `keyframes/opening_*.jpg` 和 `keyframes/contact_sheet.jpg` 的第一行。",
        "",
        "## 4. 爆点钩子",
        "",
        f"- 开头信息：{opening}",
        "",
        "## 5. 人物关系",
        "",
        "- 说话人A/B/C：根据逐字稿和画面复核后命名。",
        "- 重点看谁提出期待、谁制造反转、谁完成金句总结。",
        "",
        "## 6. 剧情节奏",
        "",
        "- 0-15s：建立痛点和极端处境。",
        "- 15-60s：抬高期待，让观众以为问题将被解决。",
        "- 中段：通过新角色或新制度制造反转。",
        "- 结尾：用一句高共鸣总结把情绪落地。",
        "",
        "## 7. 画面关键帧分析",
        "",
        "- 先看 opening 关键帧：拆第一眼场景、人物站位、表情、字幕钩子。",
        "- 再看 selected 关键帧：拆冲突升级、反转出现、情绪爆发、结尾落点。",
        "- 优先记录可复刻画面：谁先入镜、谁坐着/站着、谁被围观、字幕如何压缩信息。",
        "",
        "## 8. 梗点 / 笑点拆解",
        "",
        "- 圈层黑话梗：找把简单问题复杂化、把真实痛苦包装成漂亮话的台词。",
        "- 反差梗：找观众以为问题被解决，结果问题升级或方向反转的段落。",
        "- 夸张梗：找把痛苦放大的数字、病态身体反应、荒诞比喻。",
        "- 金句梗：优先挑能单独剪成短句的吐槽，用于二创改写。",
        "",
        "### 候选梗点台词",
        "",
    ]
    if interesting_lines:
        for seg in interesting_lines:
            lines.append(f"- [{sec_label(seg['start'])}] {seg['text']}")
    else:
        lines.append("- 本节需要从逐字稿里人工挑选最适合复用的台词。")
    lines += [
        "",
        "## 9. 粗话 / 语气词 / 破防表达",
        "",
        "- 标记高频语气词：比如“他妈的、特么的、卧槽、老子、啥玩意儿、你放屁”等。",
        "- 分析功能：它是在开头制造破防、在反转处抬高情绪，还是在金句前释放观众怨气。",
        "- 判断强度：粗话应服务于角色真实感和情绪爆点，不要平均撒满全片。",
        "- 迁移建议：保留“崩溃感”和“吐槽口吻”，但根据你的账号定位和发布平台把强粗口替换成更安全的口语词。",
        "",
        "## 10. 冲突点拆解",
        "",
        "- 表层冲突：主角当下最直接的问题是什么，谁被这个问题压住。",
        "- 深层冲突：真正制造痛苦的是人手、制度、身份差、资源错配，还是认知错位。",
        "- 人物冲突：谁想解决问题，谁让问题变复杂，谁承担后果。",
        "- 画面冲突：有没有把矛盾视觉化，例如站着的人压迫坐着的人、白板/PPT压过真实工作。",
        "",
        "## 11. 反转设计",
        "",
        "- 找第一个反转：观众以为问题被解决，实际上问题升级。",
        "- 找反转触发器：新人物、新规则、新任务、新身份、新道具分别带来了什么变化。",
        "- 找反转后的代价：主角失去了时间、尊严、效率、机会，还是情绪稳定。",
        "- 找结尾回扣：最后一句有没有把前面的反转总结成一句可传播的话。",
        "",
        "## 12. 有趣剧情",
        "",
        "- 找连续加压点：新角色、新制度、新表格、新会议是否持续制造麻烦。",
        "- 找情绪出口：结尾有没有一句能让目标观众产生“太真实了”的总结。",
        "",
        "## 13. 有趣画面 / 可复刻镜头",
        "",
        "- 开头画面：第一眼能不能看懂处境，是否有夸张道具、状态、字幕。",
        "- 中段画面：有没有新人物登场、站位压迫、会议/汇报/白板等可视化冲突。",
        "- 结尾画面：有没有能承载金句的定格、对视、崩溃表情或反讽动作。",
        "- 改写时优先替换为：你的主角、对手、旁观者、关键道具、固定场景和账号长期复用的视觉符号。",
        "",
        "## 14. 可复刻模板",
        "",
        "以为解决问题，结果来了一个更大的问题。",
        "",
        "## 15. 可迁移到你的账号 / 项目的方向",
        "",
        "- 把原视频里的痛点替换成你账号受众最熟悉的生活、职业、情感、知识或兴趣痛点。",
        "- 保留“强期待 -> 反转 -> 连续加压 -> 情绪出口 / 金句收尾”的结构。",
        "- 让角色分工清晰：谁制造期待，谁提出阻力，谁承受代价，谁完成情绪总结。",
        "",
        "## 16. 结尾金句参考",
        "",
        f"- 结尾信息：{ending}",
        "",
        "## 17. 人工精修位",
        "",
        "- 将说话人A/B/C改成真实角色身份。",
        "- 根据关键帧补充画面调度、表情和镜头节奏。",
        "- 从候选梗点台词里挑出 3-5 句可复刻金句。",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-video", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--timecoded-json", required=True)
    parser.add_argument("--speaker-json")
    parser.add_argument("--sensevoice-md")
    parser.add_argument("--title", default="参考视频")
    parser.add_argument("--keyframes", type=int, default=8)
    args = parser.parse_args()

    source_video = Path(args.source_video)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    visible_source = out_dir / "source.mp4"
    if source_video.resolve() != visible_source.resolve():
        shutil.copy2(source_video, visible_source)

    keyframe_dir = out_dir / "keyframes"
    frames = extract_keyframes(visible_source, keyframe_dir, args.keyframes)
    make_contact_sheet(frames, keyframe_dir / "contact_sheet.jpg")

    timecoded = load_timecoded_segments(Path(args.timecoded_json))
    speakers = load_speaker_segments(Path(args.speaker_json)) if args.speaker_json else []
    final_segments = merge_segments(timecoded, speakers)
    write_speaker_transcript(out_dir / "speaker_transcript.md", args.title, final_segments)

    sensevoice_text = read_reference_text(Path(args.sensevoice_md)) if args.sensevoice_md else ""
    write_story_analysis(out_dir / "story_analysis.md", args.title, final_segments, sensevoice_text)

    print(f"wrote {out_dir}")


if __name__ == "__main__":
    main()
