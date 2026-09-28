#!/usr/bin/env bash
# ============================================================
# video-story-clip-lite - install script
# Installs this Skill into any agent skills directory.
# Usage:
#   ./install.sh                 # install to AGENT_SKILLS_DIR or ~/.codex/skills
#   ./install.sh --target DIR    # install to DIR
#   AGENT_SKILLS_DIR=DIR ./install.sh
#   ./install.sh --list          # show what this package provides
#   ./install.sh --help
# ============================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="video-story-clip-lite"
DEFAULT_TARGET="${AGENT_SKILLS_DIR:-$HOME/.codex/skills}"

# Files/dirs never copied into the target skill dir
EXCLUDE=(.git __pycache__ tests tools docs .gitignore install.sh)

usage() {
  cat <<'EOF'
Usage:
  ./install.sh                 Install to AGENT_SKILLS_DIR or ~/.codex/skills
  ./install.sh --target DIR    Install to a specific skills directory
  AGENT_SKILLS_DIR=DIR ./install.sh
  ./install.sh --list          List what this package provides
  ./install.sh --help          Show this help

Common targets:
  WorkBuddy : ~/.workbuddy/skills
  Claude Code: ~/.claude/skills
  Codex     : ~/.codex/skills

Examples:
  ./install.sh --target ~/.workbuddy/skills
  AGENT_SKILLS_DIR=~/.claude/skills ./install.sh
EOF
}

list_package() {
  echo "This package provides one Skill:"
  echo "  $SKILL_NAME  (movie → 8-15 short clips, AI-planned + lossless cut)"
  echo ""
  echo "Contents: SKILL.md, references/, assets/, scripts/, manifest.json, LICENSE, README.md, README.zh.md"
}

install_skill() {
  local target="$1"
  local target_path="$target/$SKILL_NAME"

  if [[ ! -f "$ROOT_DIR/SKILL.md" ]]; then
    echo "ERROR: SKILL.md not found next to install.sh" >&2
    exit 1
  fi

  mkdir -p "$target"
  rm -rf "$target_path"
  mkdir -p "$target_path"

  # Copy everything except excluded items
  shopt -s dotglob nullglob
  for item in "$ROOT_DIR"/*; do
    local base
    base="$(basename "$item")"
    local skip=false
    for excl in "${EXCLUDE[@]}"; do
      if [[ "$base" == "$excl" ]]; then
        skip=true
        break
      fi
    done
    if [[ "$skip" == false ]]; then
      cp -r "$item" "$target_path/"
    fi
  done
  shopt -u dotglob nullglob

  rm -rf "$target_path/scripts/__pycache__" 2>/dev/null || true

  echo "Installed: $target_path"
  echo "Verify:    ls \"$target_path\""
}

# --- main ---
TARGET="$DEFAULT_TARGET"

case "${1:-}" in
  --help|-h)
    usage
    exit 0
    ;;
  --list)
    list_package
    exit 0
    ;;
  --target)
    if [[ -z "${2:-}" ]]; then
      echo "ERROR: --target requires a directory" >&2
      exit 1
    fi
    TARGET="$2"
    ;;
  "")
    ;;
  *)
    echo "ERROR: unknown option: $1" >&2
    usage
    exit 1
    ;;
esac

install_skill "$TARGET"
