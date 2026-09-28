import argparse
import json
import os
from pathlib import Path

from faster_whisper import WhisperModel


def sec_to_srt_time(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    hours = total_ms // 3_600_000
    total_ms %= 3_600_000
    minutes = total_ms // 60_000
    total_ms %= 60_000
    secs = total_ms // 1_000
    millis = total_ms % 1_000
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def sec_to_label(seconds: float) -> str:
    total = max(0, int(seconds))
    minutes = total // 60
    secs = total % 60
    return f"{minutes:02}:{secs:02}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", default=os.environ.get("ASR_AUDIO"))
    parser.add_argument("--out-prefix", default=os.environ.get("ASR_OUT_PREFIX"))
    parser.add_argument("--model", default=os.environ.get("FW_MODEL", "small"))
    parser.add_argument("--device", default=os.environ.get("FW_DEVICE", "cuda"))
    parser.add_argument("--compute-type", default=os.environ.get("FW_COMPUTE_TYPE", "float16"))
    parser.add_argument("--language", default=os.environ.get("FW_LANGUAGE", "zh"))
    parser.add_argument("--beam-size", type=int, default=int(os.environ.get("FW_BEAM_SIZE", "5")))
    parser.add_argument("--initial-prompt", default=os.environ.get("FW_INITIAL_PROMPT"))
    parser.add_argument("--download-root", default=os.environ.get("FW_DOWNLOAD_ROOT"))
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--no-vad-filter", action="store_true")
    args = parser.parse_args()

    if not args.audio:
        raise SystemExit("Missing --audio or ASR_AUDIO")
    if not args.out_prefix:
        raise SystemExit("Missing --out-prefix or ASR_OUT_PREFIX")

    audio = Path(args.audio)
    out_prefix = Path(args.out_prefix)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)

    model = WhisperModel(
        args.model,
        device=args.device,
        compute_type=args.compute_type,
        download_root=args.download_root,
        local_files_only=args.local_files_only,
    )
    segments_iter, info = model.transcribe(
        str(audio),
        language=args.language,
        beam_size=args.beam_size,
        vad_filter=not args.no_vad_filter,
        initial_prompt=args.initial_prompt,
        condition_on_previous_text=True,
    )
    segments = list(segments_iter)

    rows = []
    for segment in segments:
        rows.append(
            {
                "id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "avg_logprob": segment.avg_logprob,
                "no_speech_prob": segment.no_speech_prob,
            }
        )

    json_path = out_prefix.with_suffix(".json")
    md_path = out_prefix.with_suffix(".md")
    srt_path = out_prefix.with_suffix(".srt")

    json_path.write_text(
        json.dumps(
            {
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "model": args.model,
                "device": args.device,
                "compute_type": args.compute_type,
                "segments": rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    md_lines = [
        f"# faster-whisper transcript ({Path(args.model).name})",
        "",
        "> Machine transcript. Not human-corrected.",
        "",
    ]
    srt_lines = []
    for index, row in enumerate(rows, start=1):
        md_lines.append(
            f"- [{sec_to_label(row['start'])}-{sec_to_label(row['end'])}] {row['text']}"
        )
        srt_lines.extend(
            [
                str(index),
                f"{sec_to_srt_time(row['start'])} --> {sec_to_srt_time(row['end'])}",
                row["text"],
                "",
            ]
        )

    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"segments {len(rows)}")


if __name__ == "__main__":
    main()
