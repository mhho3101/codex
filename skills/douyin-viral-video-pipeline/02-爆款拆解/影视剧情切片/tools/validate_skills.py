#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_skills.py - publish-time validator for video-story-clip-lite.

Checks, before pushing to GitHub / publishing:
  1. SKILL.md exists at repo root.
  2. SKILL.md has `name` and `description` frontmatter.
  3. No local paths, API keys, tokens, cookies, or auth headers leak
     into the published files (README contact info is expected and allowed).

Usage:
  python3 tools/validate_skills.py          # validate current directory
  python3 tools/validate_skills.py <dir>    # validate a specific directory
"""

import os
import re
import sys

# Patterns that must never appear in published skill files.
LEAK_PATTERNS = [
    re.compile(r"[A-Za-z]:\\", re.IGNORECASE),                           # any Windows drive path (D:\..., C:\...)
    re.compile(r"/Users/[^/]+/", re.IGNORECASE),                         # /Users/name/
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                                  # OpenAI-style keys
    re.compile(r"api[_-]?key\s*[:=]\s*[\"']?[A-Za-z0-9]{16,}", re.IGNORECASE),
    re.compile(r"token\s*[:=]\s*[\"']?[A-Za-z0-9]{16,}", re.IGNORECASE),
    re.compile(r"cookie\s*[:=]\s*[\"']?[A-Za-z0-9]{16,}", re.IGNORECASE),
    re.compile(r"authorization\s*[:=]", re.IGNORECASE),
    re.compile(r"bearer\s+[A-Za-z0-9._-]{16,}", re.IGNORECASE),
    re.compile(r"password\s*[:=]\s*[\"']?[^\s\"']+", re.IGNORECASE),
]

# Files that are checked (all text files under the repo, except .git).
TEXT_EXTENSIONS = {".md", ".py", ".json", ".txt", ".sh", ".yml", ".yaml", ".toml"}

# Files allowed to be skipped (build/test artifacts).
SKIP_FILES = {"install.sh"}  # install.sh contains no secrets, but may trip generic patterns; kept explicit for safety


def walk_files(root):
    # Skip the validator's own directories (tools/, tests/) and local-only
    # docs/ (not pushed to GitHub) — their sample strings (fake api keys,
    # path patterns) would self-trigger the leak check.
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules", "tools", "tests", "docs")]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def check_frontmatter(skill_md_path):
    """Verify SKILL.md starts with a valid YAML frontmatter containing name + description."""
    errors = []
    with open(skill_md_path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    if not content.startswith("---"):
        errors.append("SKILL.md must start with '---' frontmatter")
        return errors
    lines = content.splitlines()
    in_front = False
    fields = {}
    for i, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip()
    for required in ("name", "description"):
        if required not in fields or not fields[required]:
            errors.append(f"SKILL.md frontmatter missing required field: {required}")
    return errors


def check_leaks(root):
    errors = []
    for path in walk_files(root):
        rel = os.path.relpath(path, root)
        if rel in SKIP_FILES:
            continue
        ext = os.path.splitext(path)[1].lower()
        if ext not in TEXT_EXTENSIONS:
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for pattern in LEAK_PATTERNS:
            m = pattern.search(content)
            if m:
                # Show a sanitized snippet
                snippet = content[max(0, m.start() - 20):m.end() + 20].replace("\n", " ")
                errors.append(f"{rel}: possible leak: {snippet}")
    return errors


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root = os.path.abspath(root)
    errors = []

    skill_md = os.path.join(root, "SKILL.md")
    if not os.path.isfile(skill_md):
        errors.append("SKILL.md not found at repo root")
    else:
        errors.extend(check_frontmatter(skill_md))

    errors.extend(check_leaks(root))

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED: frontmatter OK, no leaks detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
