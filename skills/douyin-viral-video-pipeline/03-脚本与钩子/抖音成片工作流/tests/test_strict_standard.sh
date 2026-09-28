#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd -P)
SKILL="$ROOT/skills/douyin-video-workflow"
CHECKER="$SKILL/scripts/check-environment.sh"

[[ -x "$CHECKER" ]]

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/bin"
mkdir -p "$TMP/home/.codex/skills" "$TMP/home/.agents/skills"

set +e
HOME="$TMP/home" CODEX_HOME="$TMP/home/.codex" PATH="$TMP/bin:/usr/bin:/bin" "$CHECKER" >"$TMP/missing.out" 2>&1
STATUS=$?
set -e
[[ $STATUS -eq 3 ]]
grep -Fq 'BLOCKED' "$TMP/missing.out"
grep -Fq 'ChatCut' "$TMP/missing.out"
grep -Fq 'HyperFrames' "$TMP/missing.out"
grep -Fq 'Ask the user whether to install' "$TMP/missing.out"

for command_name in chatcut hyperframes ffmpeg ffprobe jq; do
  printf '#!/usr/bin/env bash\nexit 0\n' > "$TMP/bin/$command_name"
  chmod +x "$TMP/bin/$command_name"
done
HOME="$TMP/home" CODEX_HOME="$TMP/home/.codex" PATH="$TMP/bin:/usr/bin:/bin" "$CHECKER" >"$TMP/ready.out"
grep -Fq 'READY' "$TMP/ready.out"

grep -Fq 'ChatCut is mandatory' "$SKILL/SKILL.md"
grep -Fq 'HyperFrames is mandatory' "$SKILL/SKILL.md"
grep -Fq 'Do not create a fallback render' "$SKILL/SKILL.md"
grep -Fq 'Static PNG slides joined with FFmpeg are prohibited' "$SKILL/SKILL.md"
grep -Fq '1.5–2.5 seconds' "$SKILL/references/workflow.md"
grep -Fq '0.8 seconds' "$SKILL/references/workflow.md"
grep -Fq 'one primary visual focus' "$SKILL/references/workflow.md"
grep -Fq 'minimal substitution' "$SKILL/references/workflow.md"
grep -Fq 'Main subject is only implied or too small' "$SKILL/references/feedback-routing.md"
grep -Fq 'Original user wording / reference' "$SKILL/assets/templates/ITERATION_FEEDBACK.md"
grep -Fq 'Scan the surrounding 2–3 seconds' "$SKILL/assets/templates/ITERATION_FEEDBACK.md"
grep -Fq '待复现' "$SKILL/assets/templates/ITERATION_FEEDBACK.md"
grep -Fq 'SFX evidence' "$SKILL/assets/templates/VERIFICATION.md"

echo 'strict production standard: PASS'
