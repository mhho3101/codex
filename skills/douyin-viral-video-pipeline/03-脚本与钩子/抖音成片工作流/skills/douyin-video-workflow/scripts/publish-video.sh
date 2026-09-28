#!/usr/bin/env bash
set -euo pipefail

usage() { echo 'usage: publish-video.sh --input <video> --title <text> --output-dir <directory>' >&2; }
INPUT=''; TITLE=''; OUTPUT_DIR=''
while [[ $# -gt 0 ]]; do
  case "$1" in
    --input) INPUT=${2-}; shift 2 ;;
    --title) TITLE=${2-}; shift 2 ;;
    --output-dir) OUTPUT_DIR=${2-}; shift 2 ;;
    *) usage; exit 2 ;;
  esac
done
[[ -f "$INPUT" && -n "$TITLE" && -n "$OUTPUT_DIR" ]] || { usage; exit 2; }
for command_name in ffprobe shasum; do command -v "$command_name" >/dev/null || { echo "$command_name is required" >&2; exit 2; }; done
ffprobe -v error -select_streams v:0 -show_entries stream=codec_type -of csv=p=0 "$INPUT" | grep -qx video
ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "$INPUT" | grep -qx audio

SAFE_TITLE=$(printf '%s' "$TITLE" | tr -d '\r\n' | sed -E 's#[/:：|&\\]#-#g; s/[[:space:]]+/ /g; s/^ +//; s/ +$//')
mkdir -p "$OUTPUT_DIR"
MAX=0
for path in "$OUTPUT_DIR"/[0-9][0-9][0-9]*.mp4; do
  [[ -e "$path" ]] || continue
  prefix=$(basename "$path"); prefix=${prefix:0:3}
  [[ "$prefix" =~ ^[0-9]{3}$ ]] || continue
  value=$((10#$prefix)); (( value > MAX )) && MAX=$value
done
NEXT=$((MAX + 1)); (( NEXT <= 999 )) || { echo 'sequence exceeds 999' >&2; exit 3; }
printf -v SEQUENCE '%03d' "$NEXT"
DEST="$OUTPUT_DIR/${SEQUENCE}${SAFE_TITLE}.mp4"
[[ ! -e "$DEST" ]] || { echo "destination exists: $DEST" >&2; exit 3; }
cp -p "$INPUT" "$DEST"
[[ $(shasum -a 256 "$INPUT" | awk '{print $1}') == $(shasum -a 256 "$DEST" | awk '{print $1}') ]] || { rm -f "$DEST"; echo 'hash mismatch' >&2; exit 4; }
printf '%s\n' "$DEST"
