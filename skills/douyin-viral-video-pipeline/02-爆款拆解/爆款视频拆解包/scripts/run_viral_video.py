import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DH_PYTHON = Path(os.environ.get("VIRAL_BREAKDOWN_DH_PYTHON", os.environ.get("DOUYIN_BREAKDOWN_DH_PYTHON", sys.executable)))
FW_PYTHON = Path(os.environ.get("VIRAL_BREAKDOWN_FW_PYTHON", os.environ.get("DOUYIN_BREAKDOWN_FW_PYTHON", sys.executable)))
TORCH_LIB = Path(os.environ.get("VIRAL_BREAKDOWN_TORCH_LIB", os.environ.get("DOUYIN_BREAKDOWN_TORCH_LIB", "")))
SENSEVOICE_MODEL_DIR = Path(os.environ.get("SENSEVOICE_MODEL_DIR", ""))
AI_MODEL_CACHE = Path(os.environ.get("AI_MODEL_CACHE", Path.home() / ".cache" / "viral-video-breakdown"))
DEFAULT_COMMENT_BROWSER_ID = os.environ.get("BROWSER_ACT_BROWSER_ID", "")
DEFAULT_YTDLP_COOKIES = os.environ.get(
    "VIRAL_BREAKDOWN_YTDLP_COOKIES",
    os.environ.get("DOUYIN_BREAKDOWN_YTDLP_COOKIES", ""),
)
DEFAULT_YTDLP_COOKIES_FROM_BROWSER = os.environ.get(
    "VIRAL_BREAKDOWN_YTDLP_COOKIES_FROM_BROWSER",
    os.environ.get("DOUYIN_BREAKDOWN_YTDLP_COOKIES_FROM_BROWSER", ""),
)


def run(cmd: list[str], env: dict | None = None) -> None:
    print("RUN", " ".join(f'"{item}"' if " " in item else item for item in cmd), flush=True)
    subprocess.run(cmd, check=True, env=env)


def run_capture(
    cmd: list[str],
    timeout: int = 120,
    check: bool = True,
    print_output: bool = True,
) -> subprocess.CompletedProcess:
    print("RUN", " ".join(f'"{item}"' if " " in item else item for item in cmd), flush=True)
    proc = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    if print_output and proc.stdout:
        print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n", flush=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return proc


def extract_url(text: str) -> str | None:
    match = re.search(r"https?://[^\s]+", text)
    if not match:
        return None
    return match.group(0).rstrip("，。,.!！)")


def is_douyin_url(url: str | None) -> bool:
    if not url:
        return False
    lowered = url.lower()
    return "douyin.com" in lowered or "iesdouyin.com" in lowered


def sanitize_name(text: str, fallback: str) -> str:
    text = re.sub(r"[\\/:*?\"<>|]+", "-", text or "")
    text = re.sub(r"\s+", "-", text).strip("-")
    return (text[:60] or fallback).strip("-")


def url_id(url: str) -> str:
    cleaned = url.rstrip("/")
    value = cleaned.rsplit("/", 1)[-1]
    return sanitize_name(value, "video")


def output_dir_for(input_text: str, source_video: Path | None, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    today = datetime.now().strftime("%Y%m%d")
    if source_video:
        slug = sanitize_name(source_video.stem, "local-video")
        return Path.cwd() / f"{today}-local-{slug}"
    url = extract_url(input_text) or "video"
    prefix = "douyin" if is_douyin_url(url) else "video"
    return Path.cwd() / f"{today}-{prefix}-{url_id(url)}"


def find_faster_whisper_snapshot(size: str) -> str:
    root = Path.home() / ".cache" / "huggingface" / "hub" / f"models--Systran--faster-whisper-{size}" / "snapshots"
    if root.exists():
        snapshots = sorted(root.iterdir(), key=lambda item: item.stat().st_mtime, reverse=True)
        if snapshots:
            return str(snapshots[0])
    return size


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def first_json_value(text: str):
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char not in "[{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        return value
    return None


def extract_aweme_id(text: str) -> str | None:
    match = re.search(r"/video/(\d+)", text)
    if match:
        return match.group(1)
    match = re.search(r"\baweme_id=(\d+)", text)
    if match:
        return match.group(1)
    return None


def run_browser_act(
    args: list[str],
    timeout: int = 120,
    check: bool = True,
    print_output: bool = True,
) -> subprocess.CompletedProcess:
    if not command_exists("browser-act"):
        raise RuntimeError("browser-act CLI not found; cannot use Douyin browser fallback.")
    return run_capture(["browser-act", *args], timeout=timeout, check=check, print_output=print_output)


def yt_dlp_cookie_args(cookies_file: str, cookies_from_browser: str) -> list[str]:
    cookies_file = (cookies_file or "").strip()
    cookies_from_browser = (cookies_from_browser or "").strip()
    if cookies_file and cookies_from_browser:
        raise RuntimeError("Use only one of --yt-dlp-cookies or --yt-dlp-cookies-from-browser.")
    if cookies_file:
        path = Path(cookies_file).expanduser()
        if not path.exists():
            raise RuntimeError(f"yt-dlp cookies file not found: {path}")
        return ["--cookies", str(path)]
    if cookies_from_browser:
        return ["--cookies-from-browser", cookies_from_browser]
    return []


def yt_dlp_failure_hint(url: str, cookies_file: str, cookies_from_browser: str) -> str:
    if not is_douyin_url(url):
        return "yt-dlp failed to download the video."
    if cookies_file:
        return (
            "yt-dlp failed with the provided cookies file. If the error above still says "
            "'Fresh cookies', export a new Netscape cookies.txt from the same browser profile "
            "after confirming Douyin is logged in. If fresh cookies still fail, the current "
            "yt-dlp Douyin extractor may be blocked by Douyin's browser verification challenge."
        )
    if cookies_from_browser:
        return (
            "yt-dlp failed while reading browser cookies. If the error above says "
            "'Could not copy Chrome cookie database', close every Chrome window and rerun. "
            "If it says 'Failed to decrypt with DPAPI', this Chrome profile may be using "
            "Chrome v20/app-bound cookie encryption that yt-dlp cannot decrypt; export a "
            "Netscape cookies.txt from a logged-in browser and pass --yt-dlp-cookies. If the "
            "browser cookie read succeeds but the error still says 'Fresh cookies', first "
            "confirm Douyin is logged in and the video page loads in that exact browser profile; "
            "if it does, the current yt-dlp Douyin extractor is likely missing Douyin's browser "
            "verification/signature parameters rather than needing another login."
        )
    return (
        "yt-dlp needs a fresh Douyin cookie source. Re-run with "
        '--yt-dlp-cookies-from-browser "chrome:Default" after logging in to Douyin in that '
        "Chrome profile, or pass --yt-dlp-cookies <Netscape cookies.txt>. If Chrome is open "
        "and yt-dlp cannot copy its cookie database, close Chrome first."
    )


def douyin_detail_eval_script(aweme_id: str) -> str:
    return f"""
(async () => {{
  const awemeId = {json.dumps(aweme_id)};
  const params = new URLSearchParams({{
    device_platform: "webapp",
    aid: "6383",
    channel: "channel_pc_web",
    aweme_id: awemeId,
    request_source: "600",
    origin_type: "video_page",
    update_version_code: "170400",
    pc_client_type: "1",
    pc_libra_divert: "Windows",
    support_h265: "1",
    support_dash: "1",
    version_code: "190500",
    version_name: "19.5.0"
  }});
  const endpoint = `https://www.douyin.com/aweme/v1/web/aweme/detail/?${{params.toString()}}`;
  const response = await fetch(endpoint, {{
    credentials: "include",
    headers: {{ accept: "application/json, text/plain, */*" }}
  }});
  const rawText = await response.text();
  let data;
  try {{
    data = JSON.parse(rawText);
  }} catch (error) {{
    return JSON.stringify({{
      ok: false,
      status: response.status,
      error: `detail JSON parse failed: ${{error.message}}`,
      raw: rawText.slice(0, 500)
    }});
  }}
  const aweme = data.aweme_detail || {{}};
  const video = aweme.video || {{}};
  const entries = [];
  for (const item of (video.bit_rate || [])) {{
    const play = item.play_addr || {{}};
    entries.push({{
      source: "bit_rate",
      gear_name: item.gear_name,
      bit_rate: item.bit_rate || 0,
      data_size: play.data_size || 0,
      width: play.width || 0,
      height: play.height || 0,
      urls: play.url_list || []
    }});
  }}
  for (const key of ["play_addr", "download_addr"]) {{
    const play = video[key] || {{}};
    entries.push({{
      source: key,
      gear_name: key,
      bit_rate: 0,
      data_size: play.data_size || 0,
      width: play.width || 0,
      height: play.height || 0,
      urls: play.url_list || []
    }});
  }}
  return JSON.stringify({{
    ok: Boolean(aweme.aweme_id),
    status: response.status,
    aweme_id: aweme.aweme_id || awemeId,
    title: aweme.desc || "",
    description: aweme.desc || "",
    duration: aweme.duration || null,
    create_time: aweme.create_time || null,
    author: aweme.author ? {{
      nickname: aweme.author.nickname || "",
      sec_uid: aweme.author.sec_uid || ""
    }} : null,
    statistics: aweme.statistics || null,
    webpage_url: `https://www.douyin.com/video/${{aweme.aweme_id || awemeId}}`,
    entries
  }});
}})()
""".strip()


def select_douyin_play_entries(detail: dict) -> list[dict]:
    entries = [entry for entry in detail.get("entries", []) if isinstance(entry, dict)]
    entries = [entry for entry in entries if entry.get("urls")]
    entries.sort(
        key=lambda item: (
            int(item.get("bit_rate") or 0),
            int(item.get("data_size") or 0),
            int(item.get("height") or 0),
            int(item.get("width") or 0),
        ),
        reverse=True,
    )
    return entries


def curl_download(url: str, target: Path, referer: str) -> None:
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        raise RuntimeError("curl not found; cannot download Douyin browser fallback URL.")
    tmp = target.with_suffix(target.suffix + ".part")
    if tmp.exists():
        tmp.unlink()
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
    )
    run_capture(
        [
            curl,
            "-L",
            "--fail",
            "--retry",
            "2",
            "--connect-timeout",
            "20",
            "--speed-time",
            "30",
            "--speed-limit",
            "1024",
            "--max-time",
            "300",
            "--referer",
            referer,
            "-A",
            user_agent,
            "-o",
            str(tmp),
            url,
        ],
        timeout=600,
    )
    if not tmp.exists() or tmp.stat().st_size == 0:
        raise RuntimeError("Douyin browser fallback produced an empty download.")
    tmp.replace(target)


def download_douyin_with_browser(url: str, download_dir: Path, browser_id: str) -> Path:
    if not browser_id:
        raise RuntimeError("Douyin browser fallback requires --comment-browser-id or BROWSER_ACT_BROWSER_ID.")

    session = f"viral_douyin_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        open_proc = run_browser_act(
            ["--session", session, "browser", "open", browser_id, url],
            timeout=120,
        )
        aweme_id = extract_aweme_id(open_proc.stdout)
        if not aweme_id:
            meta_proc = run_browser_act(
                ["--session", session, "eval", "location.href"],
                timeout=30,
                check=False,
            )
            aweme_id = extract_aweme_id(meta_proc.stdout)
        if not aweme_id:
            raise RuntimeError("Could not resolve Douyin aweme id from browser session.")

        detail_proc = run_browser_act(
            ["--session", session, "eval", douyin_detail_eval_script(aweme_id)],
            timeout=90,
            print_output=False,
        )
        detail = first_json_value(detail_proc.stdout)
        if not isinstance(detail, dict) or not detail.get("ok"):
            raise RuntimeError(f"Could not read Douyin detail JSON: {detail_proc.stdout[:500]}")

        entries = select_douyin_play_entries(detail)
        if not entries:
            raise RuntimeError("Douyin detail JSON did not contain playable URLs.")

        target = download_dir / "source.mp4"
        referer = detail.get("webpage_url") or f"https://www.douyin.com/video/{aweme_id}"
        errors = []
        for entry in entries:
            for play_url in entry.get("urls", []):
                try:
                    print(
                        "FALLBACK Douyin browser download",
                        entry.get("gear_name") or entry.get("source"),
                        entry.get("width"),
                        "x",
                        entry.get("height"),
                        flush=True,
                    )
                    curl_download(str(play_url), target, str(referer))
                    (download_dir / "source.info.json").write_text(
                        json.dumps(detail, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    return target
                except Exception as exc:
                    errors.append(f"{entry.get('gear_name') or entry.get('source')}: {exc}")
        raise RuntimeError("All Douyin browser fallback URLs failed: " + "; ".join(errors[-3:]))
    finally:
        if command_exists("browser-act"):
            run_browser_act(["session", "close", session], timeout=30, check=False)


def download_video(
    url: str,
    download_dir: Path,
    browser_id: str = "",
    cookies_file: str = "",
    cookies_from_browser: str = "",
) -> Path:
    download_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(download_dir / "source.%(ext)s")
    if command_exists("yt-dlp"):
        base = ["yt-dlp"]
    elif command_exists("uvx"):
        base = ["uvx", "yt-dlp"]
    else:
        raise RuntimeError("yt-dlp not found, and uvx is unavailable")

    try:
        run(
            base
            + yt_dlp_cookie_args(cookies_file, cookies_from_browser)
            + [
                "--no-playlist",
                "--write-info-json",
                "--write-thumbnail",
                "--merge-output-format",
                "mp4",
                "-o",
                output_template,
                url,
            ]
        )
    except subprocess.CalledProcessError as exc:
        hint = yt_dlp_failure_hint(url, cookies_file, cookies_from_browser)
        if is_douyin_url(url) and browser_id:
            print(f"WARN yt-dlp failed: {hint}", flush=True)
            print("WARN using Douyin browser fallback to keep package generation moving.", flush=True)
            return download_douyin_with_browser(url, download_dir, browser_id)
        raise RuntimeError(hint) from exc

    candidates = []
    for ext in ("*.mp4", "*.mov", "*.mkv", "*.webm"):
        candidates.extend(download_dir.glob(ext))
    if not candidates:
        raise RuntimeError(f"No downloaded video found in {download_dir}")
    source = max(candidates, key=lambda item: item.stat().st_size)
    if source.suffix.lower() == ".mp4":
        return source

    normalized = download_dir / "source.mp4"
    run(["ffmpeg", "-y", "-i", str(source), "-c", "copy", str(normalized)])
    return normalized


def copy_local_video(source: Path, work_dir: Path) -> Path:
    work_dir.mkdir(parents=True, exist_ok=True)
    target = work_dir / "source.mp4"
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    return target


def read_title(download_dir: Path, fallback: str) -> str:
    info_files = list(download_dir.glob("source.info.json"))
    if not info_files:
        return fallback
    try:
        info = json.loads(info_files[0].read_text(encoding="utf-8"))
        return info.get("title") or fallback
    except Exception:
        return fallback


def extract_audio(video: Path, audio: Path) -> None:
    audio.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-acodec",
            "pcm_s16le",
            str(audio),
        ]
    )


def env_for_faster_whisper() -> dict:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    if TORCH_LIB.exists():
        env["PATH"] = str(TORCH_LIB) + os.pathsep + env.get("PATH", "")
    return env


def env_for_funasr() -> dict:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["AI_MODEL_CACHE"] = str(AI_MODEL_CACHE)
    if SENSEVOICE_MODEL_DIR:
        env["SENSEVOICE_MODEL_DIR"] = str(SENSEVOICE_MODEL_DIR)
    if TORCH_LIB:
        env["PATH"] = str(TORCH_LIB) + os.pathsep + env.get("PATH", "")
    return env


def run_faster_whisper(audio: Path, out_prefix: Path, model_size: str) -> Path:
    python = FW_PYTHON if FW_PYTHON.exists() else Path(sys.executable)
    model = find_faster_whisper_snapshot(model_size)
    cmd = [
        str(python),
        str(SCRIPT_DIR / "run_faster_whisper_asr.py"),
        "--audio",
        str(audio),
        "--out-prefix",
        str(out_prefix),
        "--model",
        model,
        "--local-files-only",
        "--no-vad-filter",
    ]
    run(cmd, env_for_faster_whisper())
    return out_prefix.with_suffix(".json")


def run_funasr(audio: Path, out_prefix: Path, mode: str, extra_args: list[str] | None = None) -> Path:
    python = DH_PYTHON if DH_PYTHON.exists() else Path(sys.executable)
    cmd = [
        str(python),
        str(SCRIPT_DIR / "run_funasr_asr.py"),
        "--mode",
        mode,
        "--audio",
        str(audio),
        "--out-prefix",
        str(out_prefix),
    ]
    if extra_args:
        cmd.extend(extra_args)
    run(cmd, env_for_funasr())
    return out_prefix.with_suffix(".json")


def load_fw_segments(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("segments", [])


def merge_timecoded(segments: list[dict], max_gap: float = 0.6) -> list[dict]:
    merged = []
    for seg in sorted(segments, key=lambda item: item["start"]):
        text = re.sub(r"\s+", " ", str(seg.get("text", ""))).strip()
        if not text:
            continue
        current = {"start": float(seg["start"]), "end": float(seg["end"]), "text": text}
        if merged:
            prev = merged[-1]
            combined = f"{prev['text']} {current['text']}".strip()
            if (
                current["start"] - prev["end"] <= max_gap
                and len(combined) <= 90
                and current["end"] - prev["start"] <= 8
            ):
                prev["end"] = current["end"]
                prev["text"] = combined
                continue
        merged.append(current)
    return merged


def fill_gaps_with_base(small_json: Path, base_json: Path | None, out_json: Path) -> Path:
    small = load_fw_segments(small_json)
    combined = [
        {"start": float(seg["start"]), "end": float(seg["end"]), "text": seg["text"]}
        for seg in small
        if str(seg.get("text", "")).strip()
    ]
    if base_json and base_json.exists():
        base = load_fw_segments(base_json)
        small_sorted = sorted(combined, key=lambda item: item["start"])
        fillers = []
        for prev, nxt in zip(small_sorted, small_sorted[1:]):
            gap_start = prev["end"]
            gap_end = nxt["start"]
            if gap_end - gap_start < 1.8:
                continue
            candidates = [
                {
                    "start": float(seg["start"]),
                    "end": float(seg["end"]),
                    "text": str(seg.get("text", "")).strip(),
                }
                for seg in base
                if float(seg["start"]) >= gap_start - 0.2 and float(seg["end"]) <= gap_end + 0.2
            ]
            if sum(len(item["text"]) for item in candidates) >= 8:
                fillers.extend(candidates)
        combined.extend(fillers)

    merged = merge_timecoded(combined)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps({"segments": merged}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_json


def funasr_to_timecoded_segments(funasr_json: Path, out_json: Path) -> Path:
    data = json.loads(funasr_json.read_text(encoding="utf-8"))
    item = data[0] if isinstance(data, list) and data else data
    sentence_info = item.get("sentence_info") or []
    segments = []
    for seg in sentence_info:
        text = re.sub(r"<\|[^|]+?\|>", "", str(seg.get("text", "")))
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        start = float(seg.get("start", 0)) / 1000
        end = float(seg.get("end", seg.get("start", 0))) / 1000
        segments.append({"start": start, "end": max(end, start + 0.1), "text": text})

    if not segments:
        text = re.sub(r"<\|[^|]+?\|>", "", str(item.get("text", "")))
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            segments.append({"start": 0.0, "end": 0.1, "text": text})

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps({"segments": segments}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_json


def collect_comments(
    input_text: str,
    out_dir: Path,
    browser_id: str,
    limit: int,
    scrolls: int,
    delay: float,
) -> None:
    url = extract_url(input_text)
    if not url:
        print("WARN comments skipped: no URL found", flush=True)
        return
    if not is_douyin_url(url):
        print("WARN comments skipped: current bundled collector only supports Douyin URLs", flush=True)
        return
    if not browser_id:
        print("WARN comments skipped: missing browser-act browser id", flush=True)
        return

    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "collect_douyin_comments_browser_act.py"),
        url,
        "--browser-id",
        browser_id,
        "--package-dir",
        str(out_dir),
        "--limit",
        str(limit),
        "--scrolls",
        str(scrolls),
        "--delay",
        str(delay),
        "--skip-network",
        "--update-story",
    ]
    print("RUN", " ".join(f'"{item}"' if " " in item else item for item in cmd), flush=True)
    proc = subprocess.run(cmd, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        print(f"WARN comments skipped: collector exited with {proc.returncode}", flush=True)


def hide_work_dir(path: Path) -> None:
    if os.name == "nt" and path.exists():
        subprocess.run(["attrib", "+h", str(path)], check=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="")
    parser.add_argument("--source-video")
    parser.add_argument("--out-dir")
    parser.add_argument("--keep-work", action="store_true")
    parser.add_argument("--title")
    parser.add_argument("--comments", choices=["auto", "on", "off"], default="auto")
    parser.add_argument("--speaker", choices=["auto", "off"], default="auto")
    parser.add_argument("--base-gapfill", choices=["auto", "off"], default="auto")
    parser.add_argument("--yt-dlp-cookies", default=DEFAULT_YTDLP_COOKIES)
    parser.add_argument("--yt-dlp-cookies-from-browser", default=DEFAULT_YTDLP_COOKIES_FROM_BROWSER)
    parser.add_argument("--comment-browser-id", default=os.environ.get("BROWSER_ACT_BROWSER_ID", DEFAULT_COMMENT_BROWSER_ID))
    parser.add_argument("--comment-limit", type=int, default=30)
    parser.add_argument("--comment-scrolls", type=int, default=5)
    parser.add_argument("--comment-delay", type=float, default=3.0)
    args = parser.parse_args()

    source_video = Path(args.source_video) if args.source_video else None
    out_dir = output_dir_for(args.input, source_video, args.out_dir)
    work_dir = out_dir / "_work"
    download_dir = work_dir / "download"
    asr_dir = work_dir / "asr"
    out_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    if source_video:
        downloaded = copy_local_video(source_video, download_dir)
        title = args.title or source_video.stem
    else:
        url = extract_url(args.input)
        if not url:
            raise SystemExit("No URL found in input. Provide a supported URL or use --source-video.")
        try:
            downloaded = download_video(
                url,
                download_dir,
                args.comment_browser_id,
                args.yt_dlp_cookies,
                args.yt_dlp_cookies_from_browser,
            )
        except RuntimeError as exc:
            raise SystemExit(f"ERROR: {exc}") from None
        title = args.title or read_title(download_dir, url_id(url))

    audio = work_dir / "audio.wav"
    extract_audio(downloaded, audio)

    timecoded_json = None
    timecoded_from_funasr_fallback = False
    try:
        small_json = run_faster_whisper(audio, asr_dir / "faster_whisper_small", "small")
        base_json = None
        if args.base_gapfill == "auto":
            try:
                base_json = run_faster_whisper(audio, asr_dir / "faster_whisper_base", "base")
            except Exception as exc:
                print(f"WARN base gap-fill skipped: {exc}", flush=True)
        timecoded_json = fill_gaps_with_base(small_json, base_json, asr_dir / "timecoded_hybrid.json")
    except Exception as exc:
        print(f"WARN faster-whisper skipped; falling back to FunASR timecodes: {exc}", flush=True)

    sensevoice_json = run_funasr(audio, asr_dir / "sensevoice", "sensevoice")
    if timecoded_json is None:
        timecoded_json = funasr_to_timecoded_segments(sensevoice_json, asr_dir / "timecoded_hybrid.json")
        timecoded_from_funasr_fallback = True
    speaker_json = None
    if args.speaker == "auto":
        try:
            speaker_json = run_funasr(
                audio,
                asr_dir / "speaker_reference",
                "seaco_spk",
                ["--device", "cpu", "--batch-size-s", "60"],
            )
            if timecoded_from_funasr_fallback:
                timecoded_json = funasr_to_timecoded_segments(speaker_json, asr_dir / "timecoded_hybrid.json")
        except Exception as exc:
            print(f"WARN speaker diarization skipped: {exc}", flush=True)

    build_cmd = [
        str(DH_PYTHON if DH_PYTHON.exists() else Path(sys.executable)),
        str(SCRIPT_DIR / "build_viral_package.py"),
        "--source-video",
        str(downloaded),
        "--out-dir",
        str(out_dir),
        "--timecoded-json",
        str(timecoded_json),
        "--sensevoice-md",
        str(sensevoice_json.with_suffix(".md")),
        "--title",
        title,
    ]
    if speaker_json:
        build_cmd.extend(["--speaker-json", str(speaker_json)])
    run(build_cmd)

    should_collect_comments = args.comments == "on" or (
        args.comments == "auto" and is_douyin_url(extract_url(args.input))
    )
    if should_collect_comments:
        collect_comments(
            args.input,
            out_dir,
            args.comment_browser_id,
            args.comment_limit,
            args.comment_scrolls,
            args.comment_delay,
        )

    if not args.keep_work:
        hide_work_dir(work_dir)

    print(f"DONE {out_dir}", flush=True)


if __name__ == "__main__":
    main()
