#!/usr/bin/env bash
set -euo pipefail

[[ $# -eq 2 ]] || { echo 'usage: verify-video.sh <input-video> <output-directory>' >&2; exit 2; }
INPUT=$1
OUT=$2
[[ -f "$INPUT" ]] || { echo "missing input: $INPUT" >&2; exit 2; }
for command_name in ffprobe ffmpeg jq; do command -v "$command_name" >/dev/null || { echo "$command_name is required" >&2; exit 2; }; done

mkdir -p "$OUT"
ffprobe -v error -show_streams -show_format -of json "$INPUT" > "$OUT/ffprobe.json"
jq -e '.streams | any(.codec_type == "video")' "$OUT/ffprobe.json" >/dev/null
jq -e '.streams | any(.codec_type == "audio")' "$OUT/ffprobe.json" >/dev/null

if ffmpeg -v error -i "$INPUT" -f null - >"$OUT/decode.log" 2>&1; then DECODE='passed'; else DECODE='failed'; fi
ffmpeg -hide_banner -i "$INPUT" -af 'silencedetect=noise=-40dB:d=0.8' -f null - >"$OUT/silence.log" 2>&1 || true
ffmpeg -hide_banner -i "$INPUT" -af 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json' -f null - >"$OUT/loudness.log" 2>&1 || true

VIDEO_CODEC=$(jq -r '.streams[] | select(.codec_type=="video") | .codec_name' "$OUT/ffprobe.json" | head -n1)
AUDIO_CODEC=$(jq -r '.streams[] | select(.codec_type=="audio") | .codec_name' "$OUT/ffprobe.json" | head -n1)
DURATION=$(jq -r '.format.duration' "$OUT/ffprobe.json")
SILENCES=$(grep -c 'silence_start:' "$OUT/silence.log" || true)

{
  echo '# Technical Verification'
  echo
  echo "- Input: $INPUT"
  echo "- Video codec: $VIDEO_CODEC"
  echo "- Audio codec: $AUDIO_CODEC"
  echo "- Duration: $DURATION seconds"
  echo "- Full decode: $DECODE"
  echo "- Silence events longer than 0.8 seconds: ${SILENCES:-0}"
  echo '- Loudness evidence: loudness.log'
} > "$OUT/TECHNICAL_VERIFICATION.md"

[[ "$DECODE" == 'passed' ]]
