#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd -P)
SKILL="$ROOT/skills/douyin-video-workflow"

if [[ -n "${SKILL_VALIDATOR:-}" ]]; then
  python3 "$SKILL_VALIDATOR" "$SKILL"
fi
bash -n "$SKILL"/scripts/*.sh

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
PROJECT=$(bash "$SKILL/scripts/new-video-project.sh" --title '测试：视频' --root "$TMP" --ratio 9:16 --duration 45)
[[ -f "$PROJECT/PROJECT_STATE.md" ]]
grep -Fq '9:16' "$PROJECT/PROJECT_BRIEF.md"
grep -Fq '45 seconds' "$PROJECT/PROJECT_BRIEF.md"

bash "$ROOT/tests/test_strict_standard.sh"

if grep -R -n -E '/Users/[^/< ]+|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|api[_-]?key[[:space:]]*[:=]' "$ROOT" --exclude-dir=.git --exclude='run-all.sh'; then
  echo 'potential private path or secret found' >&2
  exit 1
fi

echo 'open-source skill checks: PASS'
