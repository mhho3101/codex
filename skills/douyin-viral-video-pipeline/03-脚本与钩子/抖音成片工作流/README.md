# Douyin Video Workflow Skill

A strict Codex Skill for turning manuscripts, links, source packages, or existing cuts into structured and technically verified Chinese narrated short-video projects using ChatCut and HyperFrames.

The repository contains no personal media, credentials, provider keys, or fixed user directories. ChatCut and HyperFrames are mandatory production dependencies. If either is unavailable, the Skill stops and asks whether the user wants to install it; it never silently creates a lower-quality fallback.

## Features

- New project scaffolding with production templates
- Narration-first timing and targeted recut routing
- Source, fact, and material traceability
- Non-destructive versioning and cleanup boundaries
- FFmpeg-based stream, decode, silence, and loudness evidence
- Non-overwriting numbered delivery copies
- ChatCut editable timeline as a completion gate
- HyperFrames keyword-timed motion as a completion gate
- Item-by-item entrances with synchronized sound effects within three frames
- Fail-closed environment checks with user-approved installation only

## Install

Copy or symlink the skill directory into your Codex skills folder:

```bash
mkdir -p ~/.codex/skills
cp -R skills/douyin-video-workflow ~/.codex/skills/
```

Restart Codex after installation. You can also keep it project-local under `.agents/skills/douyin-video-workflow`.

## Requirements

- Bash 3.2 or newer
- ChatCut plugin and video-editing skills
- HyperFrames CLI and skills
- FFmpeg (`ffmpeg` and `ffprobe`)
- `jq`
- Standard macOS or Unix tools including `shasum`, `sed`, and `grep`

## Quick start

Check the required environment first:

```bash
bash skills/douyin-video-workflow/scripts/check-environment.sh
```

If anything is missing, the Skill must ask before installing and must not generate a fallback video.

```bash
bash skills/douyin-video-workflow/scripts/new-video-project.sh \
  --title "AI 工具实测" \
  --root "$PWD/projects" \
  --ratio 9:16 \
  --duration 60
```

Verify a final candidate:

```bash
bash skills/douyin-video-workflow/scripts/verify-video.sh final.mp4 verify
```

Run repository checks:

```bash
bash tests/run-all.sh
```

## Safety

The workflow never treats final acceptance as permission to delete source files or previous versions. Publishing, external sends, credentials, and account operations require separate authorization.

## License

MIT
