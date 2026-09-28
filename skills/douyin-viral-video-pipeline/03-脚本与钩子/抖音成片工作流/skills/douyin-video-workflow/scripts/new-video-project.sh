#!/usr/bin/env bash
set -euo pipefail

usage() { echo 'usage: new-video-project.sh --title <text> --root <directory> [--ratio 16:9|9:16] [--duration <seconds>]' >&2; }

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd -P)
TEMPLATE_DIR="$SCRIPT_DIR/../assets/templates"
TITLE=''
ROOT=''
RATIO='9:16'
DURATION='60'

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title) TITLE=${2-}; shift 2 ;;
    --root) ROOT=${2-}; shift 2 ;;
    --ratio) RATIO=${2-}; shift 2 ;;
    --duration) DURATION=${2-}; shift 2 ;;
    *) usage; exit 2 ;;
  esac
done

[[ -n "$TITLE" && -n "$ROOT" ]] || { usage; exit 2; }
[[ "$RATIO" == '16:9' || "$RATIO" == '9:16' ]] || { echo 'ratio must be 16:9 or 9:16' >&2; exit 2; }
[[ "$DURATION" =~ ^[0-9]+$ ]] || { echo 'duration must be an integer' >&2; exit 2; }

SAFE_TITLE=$(printf '%s' "$TITLE" | tr -d '\r\n' | sed -E 's#[/:：|&\\]#-#g; s/[[:space:]]+/ /g; s/^ +//; s/ +$//')
[[ -n "$SAFE_TITLE" ]] || { echo 'title is empty after sanitization' >&2; exit 2; }
DEST="$ROOT/$SAFE_TITLE"
[[ ! -e "$DEST" ]] || { echo "destination exists: $DEST" >&2; exit 3; }

mkdir -p "$DEST"/{assets/{user,official,public,generated,audio},timeline,previews,verify,renders,publish}
for template in "$TEMPLATE_DIR"/*.md; do
  name=$(basename "$template")
  sed -e "s/{{TITLE}}/$SAFE_TITLE/g" -e "s/{{RATIO}}/$RATIO/g" -e "s/{{DURATION}}/$DURATION/g" -e "s/{{CREATED_DATE}}/$(date +%F)/g" "$template" > "$DEST/$name"
done

printf '%s\n' "$DEST"
