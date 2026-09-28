# video-story-clip

Turn a full movie into **8-15 ready-to-post short clips** (50-75s each) — AI plans the segments, a script cuts them losslessly. Built for Douyin / Kuaishou / short-drama / film-recap creators.

English | [中文](./README.zh.md)

## About the Author

Created and maintained by **Han Yang** — a developer who builds AI workflows for content creation.

Why I made this: cutting a 2-hour movie into short clips used to take me a whole day of watching, rewinding, and hand-trimming. Now it only takes minutes — the Skill untangles the story and cuts the segments for you, and ships a matching `.txt` file per clip, so you just add narration and polish it yourself in Jianying (CapCut) or any other editor. And with every movie I cut, I distill the pitfalls I've hit into new rules, and the Skill keeps improving.

- WeChat: `hhhhhh_h` (add me with "**GitHub**" in the verification message)
- Email: `hanyang_cg@126.com`

## What This Skill Does

1. **AI reads your subtitle file** (SRT) and plans 8-15 themed segments — each 50-75s, one story per segment, fast-cut style with 3-7 fragments per clip
2. **Lossless cutting** — 100% identical to the source video quality (`-c copy`), instant; or precise-to-the-second with `--reencode`
3. **Auto-merge** — fragments of each segment are merged into one complete mp4 (same name as the folder), fragments kept as well; disable with `--no-merge`
4. **Correspondence file** — every segment ships with a `.txt` listing its fragments, narration suggestions, and source-dialogue references
5. **Gap detection** — finds subtitle-free scenes (`find_gaps.py`) and validates output (`verify_clips.py`)

## Installation

**One-command install** (recommended):

```bash
git clone https://github.com/hanyangcg/video-story-clip.git && cd video-story-clip

# WorkBuddy
./install.sh --target ~/.workbuddy/skills

# Claude Code
./install.sh --target ~/.claude/skills

# Codex
./install.sh --target ~/.codex/skills

# Custom directory
AGENT_SKILLS_DIR=~/.agents/skills ./install.sh
```

**Manual install**: clone the repo, then copy this folder into your agent's skills directory (e.g. `~/.workbuddy/skills/`). Keep the folder name unchanged.

**Requirements**: Python 3.9+, ffmpeg/ffprobe (in PATH, or full path in the JSON config), and an AI assistant that supports Skills.

**Environment status**: The Skill uses the standard `SKILL.md` layout (with `name` + `description` frontmatter) and the install script works on any bash environment. It is **verified** on WorkBuddy. Claude Code and Codex follow the same skill-folder convention — if your first load does not trigger it, check that your assistant actually reads skills from the target directory.

## How to Use

This Skill is not a standalone program — it works with an AI assistant (WorkBuddy / Claude Code / Codex):

1. **Prepare your materials**: the movie file + SRT subtitle; ideally also tell the AI the opening/ending timestamps and give a plot summary (for more precise cuts)
2. **Ask the AI**: hand the subtitle to the AI and say "cut this movie into 8-15 short clips, 50-75s each" — the AI follows the workflow in SKILL.md
3. **Confirm the plan**: the AI first lists a plot-timeline scene breakdown for you to confirm, then generates the cutting plan (SEGMENTS)
4. **Auto-cut**: the AI runs `cut_clips.py` to cut losslessly and merge, outputting each clip plus a matching txt file
5. **Polish & publish**: add narration, subtitles, and music in Jianying / CapCut, then export

For command-line usage, see "Quick Start" below.

## Quick Start

```bash
# 1. Copy the template and fill in your movie paths
cp assets/movie_config_template.json 我的电影.json
#    edit: src / out_dir / ffmpeg / ffprobe

# 2. Ask your AI assistant to analyze the SRT and generate SEGMENTS
#    "帮我分析 我的电影.srt，生成剪辑方案写入 我的电影.json"
#    (AI follows references/style_guide.md to plan segments)

# 3. Cut (lossless by default)
python scripts/cut_clips.py --config 我的电影.json

#    Precise-to-the-second
python scripts/cut_clips.py --config 我的电影.json --reencode

# 4. Validate output
python scripts/verify_clips.py "输出目录"
```

## Tips

- **Provide the opening/ending timestamps**: before cutting, manually tell the AI where the movie's opening titles and end credits are — it makes the segments more precise and keeps them out of your clips.
- **Provide a plot summary**: when using the Skill, it's best to give the AI a brief summary of the movie's plot — this helps it understand the story and makes the segments more precise.

## Project Structure

```text
video-story-clip/
├─ SKILL.md                     # Skill entry (workflow, constraints)
├─ install.sh                   # One-command install script
├─ manifest.json                # Skill manifest (name / version / entrypoint)
├─ README.md                    # English docs
├─ README.zh.md                 # 中文文档
├─ LICENSE                      # MIT License
├─ references/
│  ├─ style_guide.md            # Basic editing style rules (AI reads this)
│  └─ requirements.md           # Requirements spec
├─ assets/
│  └─ movie_config_template.json # Config template
├─ scripts/
│  ├─ cut_clips.py              # Core: reads JSON config, cuts & merges
│  ├─ find_gaps.py              # Subtitle-gap scanning
│  └─ verify_clips.py           # Output validation
├─ tools/
│  └─ validate_skills.py        # Publish-time validator (frontmatter + leak scan)
└─ tests/
   └─ test_validate_skills.py   # Validator unit tests
```

## Requirements

- Python 3.9+
- ffmpeg / ffprobe (in PATH, or full path in the JSON config)
- **An AI assistant that supports Skills** (WorkBuddy / Claude Code / Codex / OpenClaw) — this is not a standalone program: the AI plans, the scripts execute

## Support

If this Skill saves you time, great — that is what it is for.

- For **custom AI workflows** (film-recap studios, clip matrices, personal pipelines) or commercial use, email me and describe your scene — I will recommend the right setup.
- WeChat: `hhhhhh_h` · Email: `hanyang_cg@126.com`

## License

MIT License. This repository contains only tool scripts and documentation — no copyrighted movie material of any kind.

## Disclaimer

Use this tool on footage you have the right to use. Confirm copyright before publishing, and follow platform rules and local laws.
