---
name: folder-organizer
description: Conservative folder organization assistant for scanning directories, reading file names, metadata, and sampled document contents, then producing theme categories, action categories, rename suggestions, archive suggestions, and a proposed folder structure. Use when Codex needs to help organize messy folders, Downloads/Desktop directories, school/work/job-search files, receipts, screenshots, notes, PDFs, DOCX files, images, code files, or mixed personal documents without moving or deleting files by default.
---

# Folder Organizer

## Goal

Act as a cautious file organizer. Read a target folder in layers, classify files by likely topic and handling action, and produce a practical organization report. Prefer recommendations over changes. Do not move, rename, or delete files unless the user explicitly asks for an execution step after reviewing the report.

## Core Principles

- Classify conservatively: if evidence is weak, mark the file as `Needs confirmation` instead of forcing a category.
- Use layered evidence: inspect metadata first, then sample content only when needed and safe.
- Preserve user trust: never delete files, overwrite files, or perform bulk moves during the first pass.
- Separate topic from action: a file can be `Job Search > Resume` and also `Suggest rename`.
- Keep output actionable: include destination folder suggestions, rename suggestions, confidence, and reason.

## V1 Workflow

1. Confirm the target folder if it is ambiguous; otherwise proceed with the folder the user named.
2. Scan files recursively unless the user asks for only the top level.
3. First layer: use file name, extension, path, modified time, and size.
4. Second layer: for unclear common documents, sample content from `.txt`, `.md`, `.csv`, `.json`, `.pdf`, `.docx`, and code/config files.
5. Third layer: output a report with topic categories, action categories, proposed folder structure, rename suggestions, and uncertain files.
6. Stop at recommendations unless the user explicitly asks to apply moves or renames.

## Quick Start Script

Use `scripts/folder_organizer.py` for the standard v1 report:

```bash
python3 /path/to/folder-organizer/scripts/folder_organizer.py /path/to/folder --output /path/to/folder-organization-report.md
```

Helpful options:

```bash
python3 /path/to/folder-organizer/scripts/folder_organizer.py /path/to/folder --max-files 300 --max-depth 4
python3 /path/to/folder-organizer/scripts/folder_organizer.py /path/to/folder --json /path/to/report.json
python3 /path/to/folder-organizer/scripts/folder_organizer.py /path/to/folder --no-content
```

If the script cannot extract content from a format, continue with metadata-based classification and call that out in the report.

## Classification Heuristics

Prefer these broad topic families unless the folder context suggests better names:

- `Job Search`: resumes, cover letters, portfolios, job descriptions, interview prep.
- `Courses`: lecture notes, assignments, readings, syllabi, class slides, week/unit notes.
- `Finance`: invoices, receipts, bills, bank/tax/insurance/payment records.
- `Work Projects`: reports, proposals, meeting notes, product/design/business files.
- `Screenshots and Images`: screenshots, temporary images, exported graphics, camera images.
- `Code and Config`: scripts, notebooks, source files, package/config files, experiments.
- `Personal and Admin`: IDs, forms, travel, health, housing, general life admin.
- `Archive`: old versions, completed material, stale exports, historical copies.
- `Needs Confirmation`: unclear, mixed-purpose, or sensitive files that need human review.

Use action labels independently:

- `Keep`: likely useful and already reasonably named.
- `Archive`: likely not active but worth retaining.
- `Suggest rename`: unclear, generic, duplicate-like, or version-heavy name.
- `Possible duplicate`: same or very similar normalized filename, size, or content hint.
- `Possible cleanup`: temporary/export/cache file; never delete without confirmation.
- `Needs confirmation`: ambiguous, sensitive, or low-confidence classification.

## Rename Guidance

Suggest names that are short, stable, and sortable:

```text
YYYY-MM-DD_topic_detail.ext
topic_detail_v01.ext
course_week03_lecture-notes.ext
company_role_resume_YYYY-MM.ext
vendor_invoice_YYYY-MM-DD.ext
```

Avoid renaming suggestions that remove important original identifiers such as invoice numbers, course codes, company names, dates, or version numbers. For `final/final2/reallyfinal` clusters, recommend a version scheme and identify the likely newest file by modified time.

## Report Format

Include these sections:

- `Summary`: file count, scanned size, content sampling status, notable risks.
- `Theme Categories`: grouped by suggested destination folder.
- `Action Categories`: keep/archive/rename/duplicate/cleanup/needs confirmation.
- `Rename Suggestions`: original path, suggested name, reason, confidence.
- `Proposed Folder Structure`: concise tree.
- `Unclear Files`: what evidence is missing and what to ask the user.
- `Next Safe Step`: usually "review these recommendations before moving anything."

## Safety Rules

- Do not traverse system folders outside the requested root.
- Skip hidden folders, dependency folders, package caches, and version-control folders unless the user asks.
- Do not read very large files in full; sample only the beginning.
- Treat personal documents as sensitive. Summarize evidence without dumping private content.
- Before applying any move or rename plan, produce a dry-run table and ask for explicit confirmation.
