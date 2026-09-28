#!/usr/bin/env bash
set -euo pipefail

has_skill_matching() {
  local pattern=$1
  local root
  for root in "${CODEX_HOME:-$HOME/.codex}/skills" "$HOME/.agents/skills"; do
    [[ -d "$root" ]] || continue
    find "$root" -maxdepth 2 -type f -name SKILL.md -path "*$pattern*" -print -quit 2>/dev/null | grep -q . && return 0
  done
  return 1
}

has_chatcut() {
  [[ "${CHATCUT_AVAILABLE:-}" == '1' ]] || command -v chatcut >/dev/null 2>&1 || has_skill_matching 'chatcut'
}

has_hyperframes() {
  [[ "${HYPERFRAMES_AVAILABLE:-}" == '1' ]] || command -v hyperframes >/dev/null 2>&1 || has_skill_matching 'hyperframes'
}

missing=()
has_chatcut || missing+=('ChatCut plugin or skills')
has_hyperframes || missing+=('HyperFrames CLI or skills')
for command_name in ffmpeg ffprobe jq; do
  command -v "$command_name" >/dev/null 2>&1 || missing+=("$command_name")
done

if (( ${#missing[@]} > 0 )); then
  echo 'BLOCKED: the required production environment is incomplete.'
  printf 'Missing: %s\n' "${missing[@]}"
  echo 'Ask the user whether to install the missing plugins, skills, or command-line tools.'
  echo 'Do not install without approval. Do not create a fallback render.'
  exit 3
fi

echo 'READY: ChatCut, HyperFrames, FFmpeg, FFprobe, and jq are available.'
