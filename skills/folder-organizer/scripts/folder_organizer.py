#!/usr/bin/env python3
"""Create a conservative folder-organization report.

The script is intentionally read-only. It scans a folder, samples lightweight
content where possible, and writes classification suggestions.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".DS_Store",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".cache",
    "Library",
}

TEXT_EXTS = {
    ".txt",
    ".md",
    ".csv",
    ".tsv",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".py",
    ".rb",
    ".go",
    ".rs",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".sh",
    ".sql",
    ".ipynb",
}


@dataclass
class FileInfo:
    path: str
    name: str
    extension: str
    size: int
    modified: str
    topic: str
    subtype: str
    actions: list[str]
    confidence: float
    reason: str
    suggested_folder: str
    suggested_name: str | None
    content_sampled: bool
    content_method: str | None
    duplicate_key: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only folder organization report.")
    parser.add_argument("folder", help="Folder to scan")
    parser.add_argument("--output", help="Markdown report path")
    parser.add_argument("--json", help="JSON report path")
    parser.add_argument("--max-files", type=int, default=500)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--sample-chars", type=int, default=5000)
    parser.add_argument("--no-content", action="store_true", help="Use metadata only")
    parser.add_argument("--include-hidden", action="store_true")
    return parser.parse_args()


def rel_depth(root: Path, path: Path) -> int:
    try:
        return len(path.relative_to(root).parts) - 1
    except ValueError:
        return 0


def iter_files(root: Path, max_files: int, max_depth: int, include_hidden: bool) -> Iterable[Path]:
    count = 0
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        depth = rel_depth(root, current_path)
        if depth >= max_depth:
            dirs[:] = []
        dirs[:] = [
            d
            for d in dirs
            if (include_hidden or not d.startswith(".")) and d not in SKIP_DIRS
        ]
        for filename in files:
            if not include_hidden and filename.startswith("."):
                continue
            yield current_path / filename
            count += 1
            if count >= max_files:
                return


def safe_read_text(path: Path, max_chars: int) -> tuple[str, str] | tuple[None, None]:
    try:
        raw = path.read_bytes()[: max_chars * 4]
    except OSError:
        return None, None
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw.decode(encoding, errors="ignore")[:max_chars], "text"
        except UnicodeError:
            continue
    return None, None


def read_docx(path: Path, max_chars: int) -> tuple[str, str] | tuple[None, None]:
    try:
        with zipfile.ZipFile(path) as zf:
            xml_bytes = zf.read("word/document.xml")
    except (OSError, KeyError, zipfile.BadZipFile):
        return None, None
    try:
        root = ElementTree.fromstring(xml_bytes)
    except ElementTree.ParseError:
        return None, None
    texts = []
    for node in root.iter():
        if node.tag.endswith("}t") and node.text:
            texts.append(node.text)
    return html.unescape(" ".join(texts))[:max_chars], "docx"


def read_pdf(path: Path, max_chars: int) -> tuple[str, str] | tuple[None, None]:
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        try:
            result = subprocess.run(
                [pdftotext, "-f", "1", "-l", "3", "-layout", str(path), "-"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=10,
            )
            text = result.stdout.decode("utf-8", errors="ignore").strip()
            if text:
                return text[:max_chars], "pdftotext"
        except (OSError, subprocess.TimeoutExpired):
            pass
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(str(path))
        pages = reader.pages[:3]
        text = "\n".join(page.extract_text() or "" for page in pages).strip()
        if text:
            return text[:max_chars], "pypdf"
    except Exception:
        return None, None
    return None, None


def sample_content(path: Path, max_chars: int) -> tuple[str | None, str | None]:
    ext = path.suffix.lower()
    if ext == ".docx":
        return read_docx(path, max_chars)
    if ext == ".pdf":
        return read_pdf(path, max_chars)
    if ext in TEXT_EXTS:
        return safe_read_text(path, max_chars)
    return None, None


def normalized_tokens(*parts: str) -> str:
    text = " ".join(parts).lower()
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def classify(path: Path, sample: str | None) -> tuple[str, str, list[str], float, str, str]:
    ext = path.suffix.lower()
    text = normalized_tokens(str(path), sample or "")
    name_text = normalized_tokens(path.name)
    evidence = []
    actions = ["Keep"]
    topic = "Needs Confirmation"
    subtype = "Unclear"
    confidence = 0.35

    rules = [
        ("Job Search", "Resume", 0.88, ["resume", "cv", "curriculum vitae", "简历"]),
        ("Job Search", "Cover Letter", 0.84, ["cover letter", "求职信"]),
        ("Job Search", "Job Description", 0.78, ["job description", "岗位", "jd ", "interview"]),
        ("Courses", "Lecture Notes", 0.82, ["lecture", "week", "notes", "syllabus", "assignment", "课堂", "课程", "作业"]),
        ("Finance", "Invoice or Receipt", 0.86, ["invoice", "receipt", "bill", "payment", "tax", "bank", "账单", "发票", "收据"]),
        ("Work Projects", "Report or Proposal", 0.76, ["report", "proposal", "meeting", "product", "strategy", "brief", "报告", "会议"]),
        ("Personal and Admin", "Form or Admin", 0.7, ["passport", "visa", "insurance", "health", "rent", "contract", "form", "申请"]),
    ]

    for rule_topic, rule_subtype, score, keywords in rules:
        hit = [kw for kw in keywords if kw in text]
        if hit:
            topic = rule_topic
            subtype = rule_subtype
            confidence = score
            evidence.append("keyword match: " + ", ".join(hit[:3]))
            break

    if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".heic", ".tiff", ".bmp"}:
        topic = "Screenshots and Images"
        subtype = "Screenshot" if re.search(r"screenshot|screen shot|截屏|截图", name_text) else "Image"
        confidence = max(confidence, 0.78 if subtype == "Screenshot" else 0.66)
        evidence.append("image extension")

    if ext in {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".sh", ".sql", ".ipynb"}:
        topic = "Code and Config"
        subtype = "Script or Source"
        confidence = max(confidence, 0.8)
        evidence.append("code extension")

    if ext in {".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".lock"}:
        topic = "Code and Config"
        subtype = "Config"
        confidence = max(confidence, 0.75)
        evidence.append("configuration extension")

    if re.search(r"\b(final\d*|reallyfinal|final_final|copy|副本)\b", name_text):
        if "Suggest rename" not in actions:
            actions.append("Suggest rename")
        evidence.append("version-heavy name")

    if re.search(r"\b(tmp|temp|draft|untitled|未命名|screen shot|screenshot)\b", name_text):
        if "Suggest rename" not in actions:
            actions.append("Suggest rename")
        evidence.append("generic or temporary name")

    if topic == "Needs Confirmation":
        actions = ["Needs confirmation"]
        evidence.append("insufficient metadata/content evidence")

    suggested_folder = f"{topic}/{subtype}" if topic != subtype else topic
    reason = "; ".join(evidence) if evidence else "metadata-based guess"
    return topic, subtype, actions, min(confidence, 0.95), reason, suggested_folder


def suggest_name(path: Path, topic: str, subtype: str, actions: list[str]) -> str | None:
    if "Suggest rename" not in actions and topic != "Needs Confirmation":
        return None
    stem = normalized_tokens(path.stem).replace(" ", "-")[:48] or "file"
    clean_topic = normalized_tokens(topic).replace(" ", "-")
    clean_subtype = normalized_tokens(subtype).replace(" ", "-")
    return f"{clean_topic}_{clean_subtype}_{stem}{path.suffix.lower()}"


def sha_key(path: Path, size: int) -> str:
    base = normalized_tokens(path.stem)
    return hashlib.sha1(f"{base}:{size}:{path.suffix.lower()}".encode()).hexdigest()[:12]


def analyze_file(root: Path, path: Path, args: argparse.Namespace) -> FileInfo:
    stat = path.stat()
    modified = dt.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
    sample, method = (None, None) if args.no_content else sample_content(path, args.sample_chars)
    topic, subtype, actions, confidence, reason, folder = classify(path.relative_to(root), sample)
    suggested_name = suggest_name(path, topic, subtype, actions)
    return FileInfo(
        path=str(path.relative_to(root)),
        name=path.name,
        extension=path.suffix.lower() or "[none]",
        size=stat.st_size,
        modified=modified,
        topic=topic,
        subtype=subtype,
        actions=actions,
        confidence=confidence,
        reason=reason,
        suggested_folder=folder,
        suggested_name=suggested_name,
        content_sampled=bool(sample),
        content_method=method,
        duplicate_key=sha_key(path, stat.st_size),
    )


def mark_duplicates(items: list[FileInfo]) -> None:
    buckets: dict[str, list[FileInfo]] = {}
    for item in items:
        buckets.setdefault(item.duplicate_key, []).append(item)
    for bucket in buckets.values():
        if len(bucket) > 1:
            for item in bucket:
                if "Possible duplicate" not in item.actions:
                    item.actions.append("Possible duplicate")


def md_table(rows: list[list[str]]) -> str:
    if not rows:
        return "_None._\n"
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]
    out = []
    out.append("| " + " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(rows[0])) + " |")
    out.append("| " + " | ".join("-" * widths[i] for i in range(len(widths))) + " |")
    for row in rows[1:]:
        out.append("| " + " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)) + " |")
    return "\n".join(out) + "\n"


def render_report(root: Path, items: list[FileInfo], content_disabled: bool) -> str:
    total_size = sum(item.size for item in items)
    sampled = sum(1 for item in items if item.content_sampled)
    topic_map: dict[str, list[FileInfo]] = {}
    action_map: dict[str, list[FileInfo]] = {}
    for item in items:
        topic_map.setdefault(item.suggested_folder, []).append(item)
        for action in item.actions:
            action_map.setdefault(action, []).append(item)

    lines = [
        "# Folder Organization Report",
        "",
        "## Summary",
        "",
        f"- Root: `{root}`",
        f"- Files scanned: {len(items)}",
        f"- Total size: {total_size:,} bytes",
        f"- Content sampling: {'disabled' if content_disabled else f'{sampled} files sampled'}",
        "- Safety: read-only report; no files moved, renamed, or deleted.",
        "",
        "## Theme Categories",
        "",
    ]
    for folder, grouped in sorted(topic_map.items()):
        lines.append(f"### {folder}")
        rows = [["File", "Confidence", "Reason"]]
        for item in sorted(grouped, key=lambda x: x.path):
            rows.append([f"`{item.path}`", f"{item.confidence:.2f}", item.reason])
        lines.append(md_table(rows))

    lines += ["", "## Action Categories", ""]
    for action, grouped in sorted(action_map.items()):
        lines.append(f"### {action}")
        for item in sorted(grouped, key=lambda x: x.path):
            lines.append(f"- `{item.path}` -> `{item.suggested_folder}`")
        lines.append("")

    rename_rows = [["Original", "Suggested name", "Reason", "Confidence"]]
    for item in items:
        if item.suggested_name:
            rename_rows.append([f"`{item.path}`", f"`{item.suggested_name}`", item.reason, f"{item.confidence:.2f}"])
    lines += ["## Rename Suggestions", "", md_table(rename_rows), ""]

    lines += ["## Proposed Folder Structure", ""]
    for folder in sorted(topic_map):
        lines.append(f"- `{folder}/`")
    lines.append("")

    unclear = [item for item in items if "Needs confirmation" in item.actions]
    lines += ["## Unclear Files", ""]
    if unclear:
        for item in sorted(unclear, key=lambda x: x.path):
            lines.append(f"- `{item.path}`: {item.reason}")
    else:
        lines.append("_No low-confidence files detected._")
    lines += ["", "## Next Safe Step", "", "Review these recommendations before asking Codex to create a dry-run move or rename plan."]
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.folder).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"Not a folder: {root}", file=sys.stderr)
        return 2

    items: list[FileInfo] = []
    for path in iter_files(root, args.max_files, args.max_depth, args.include_hidden):
        try:
            if path.is_file():
                items.append(analyze_file(root, path, args))
        except OSError as exc:
            print(f"Skipping {path}: {exc}", file=sys.stderr)

    mark_duplicates(items)
    report = render_report(root, items, args.no_content)

    if args.output:
        Path(args.output).expanduser().write_text(report, encoding="utf-8")
    else:
        print(report)

    if args.json:
        payload = {"root": str(root), "files": [asdict(item) for item in items]}
        Path(args.json).expanduser().write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
