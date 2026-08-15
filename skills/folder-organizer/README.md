# folder-organizer-skill

> 🛡️ Conservative, read-only folder organization assistant for Codex & OpenClaw

A lightweight, safe-by-design skill that helps you **analyze, classify, and plan** the organization of messy folders (e.g., `Downloads`, `Desktop`, course materials, job-search files) — **without moving, renaming, or deleting anything by default**.

Perfect for:
- Students managing lecture notes & assignments
- Job seekers organizing resumes,笔试资料, and interview prep
- Developers curating config files, worldbooks, and scripts
- Anyone who wants *actionable insight before taking action*

---

## ✨ Features

- **Layered classification**: Uses filename, extension, size, time → then samples content only when needed & safe (`.txt`, `.pdf`, `.json`, `.ipynb`, etc.)
- **Clear output**: Markdown report with:
  - Topic categories (`Courses`, `Job Search`, `Code & Config`, `Finance`, `Needs Confirmation`)
  - Action labels (`Keep`, `Archive`, `Suggest rename`, `Possible duplicate`)
  - Rename suggestions (stable, sortable, preserving key info)
  - Proposed folder structure (tree-style)
- **Built-in safety**: Skips `.git`, `node_modules`, passwords, large binaries; never writes to source folder
- **CLI-first**: Works standalone or integrated into Codex/OpenClaw workflows

---

## 🚀 Quick Start

```bash
# 1. Install (requires Python 3.9+)
python3 -m pip install -r requirements.txt  # (if any dependencies — this skill has none!)

# 2. Run on any folder
cd /path/to/your/skill/
python3 scripts/folder_organizer.py ~/Downloads --output ~/Downloads-report.md

# 3. Open the report
code ~/Downloads-report.md  # or open in your editor
```

> 💡 Tip: Use `--max-files 300 --max-depth 3` for faster scans on huge folders.

---

## 📁 Structure

```
folder-organizer-skill/
├── SKILL.md              # Skill spec (for Codex/OpenClaw integration)
├── scripts/
│   └── folder_organizer.py # Main CLI script
└── README.md             # You're reading it!
```

---

## 🛡️ Safety & License

- **Zero side effects**: Pure read-only analysis.
- **No network calls**: Runs entirely offline.
- **MIT License**: Free to use, modify, and share.

---

> Made with ❤️ for [OpenClaw](https://github.com/openclaw/openclaw) & [Codex](https://github.com/codex-team/codex)
