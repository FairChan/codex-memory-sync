#!/usr/bin/env python3
"""Repository-local Codex memory synchronization.

This script intentionally uses plain files:
- Markdown for human-readable memory.
- JSONL for append-only machine-readable commit logs.
- Per-thread cursors for token-efficient incremental reads.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


BEGIN = "<!-- BEGIN CODEX MEMORY SYNC -->"
END = "<!-- END CODEX MEMORY SYNC -->"
MEMORY_DIR = ".codex-memory"
THREADS_DIR = "THREADS"
LOGS_DIR = "LOGS"
CURSORS_DIR = "CURSORS"
ARCHIVE_DIR = "ARCHIVE"
BACKUPS_DIR = ".backups"
COMMIT_LOG = "MEMORY_COMMITS.jsonl"
COMMIT_LOG_MD = "MEMORY_COMMITS.md"
INDEX_FILE = "MEMORY_INDEX.md"
SUMMARY_FILE = "SUMMARY.md"
COMPACTION_STATE = "COMPACTION_STATE.json"


def now() -> dt.datetime:
    return dt.datetime.now().astimezone()


def now_iso() -> str:
    return now().isoformat(timespec="seconds")


def now_display() -> str:
    return now().strftime("%Y-%m-%d %H:%M %Z")


def stamp() -> str:
    return now().strftime("%Y%m%d-%H%M%S")


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "memory"


def default_actor() -> str:
    return os.environ.get("CODEX_MEMORY_ACTOR") or os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"


def run_git(project: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(project),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return result.stdout.strip()
    except OSError:
        return ""


def current_branch(project: Path) -> str:
    return run_git(project, ["branch", "--show-current"]) or "unknown"


def current_commit(project: Path) -> str:
    return run_git(project, ["rev-parse", "--short", "HEAD"]) or "unknown"


def memory_root(project: Path) -> Path:
    return project / MEMORY_DIR


def rel(path: Path, project: Path) -> str:
    try:
        return path.resolve().relative_to(project.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str, dry_run: bool = False) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def append_text(path: Path, content: str, dry_run: bool = False) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def append_jsonl(path: Path, record: dict[str, Any], dry_run: bool = False) -> None:
    append_text(path, json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n", dry_run=dry_run)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def backup_existing(path: Path, project: Path, dry_run: bool = False) -> Path:
    backup_root = memory_root(project) / BACKUPS_DIR / stamp()
    backup_path = backup_root / rel(path, project)
    if not dry_run:
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
    return backup_path


def line_count(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def section_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.startswith("## "))


def file_location(path: Path, before: str, appended: str, project: Path) -> dict[str, Any]:
    start_line = line_count(before) + 1
    appended_lines = max(1, line_count(appended))
    end_line = start_line + appended_lines - 1
    heading = ""
    for line in appended.splitlines():
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            break
    return {
        "path": rel(path, project),
        "heading": heading,
        "entry_number": section_count(before) + 1,
        "start_line": start_line,
        "end_line": end_line,
    }


def commit_id(actor: str, thread: str, purpose: str, files: list[dict[str, Any]]) -> str:
    payload = json.dumps(
        {"time": now_iso(), "actor": actor, "thread": thread, "purpose": purpose, "files": files},
        ensure_ascii=False,
        sort_keys=True,
    )
    return "mem-" + hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]


def ensure_memory_dirs(project: Path, dry_run: bool = False) -> list[str]:
    root = memory_root(project)
    dirs = [
        root,
        root / THREADS_DIR,
        root / LOGS_DIR,
        root / CURSORS_DIR,
        root / ARCHIVE_DIR,
        root / BACKUPS_DIR,
    ]
    actions = []
    for directory in dirs:
        if directory.exists():
            actions.append(f"kept existing directory {rel(directory, project)}")
        else:
            actions.append(f"created directory {rel(directory, project)}" if not dry_run else f"would create directory {rel(directory, project)}")
            if not dry_run:
                directory.mkdir(parents=True, exist_ok=True)
    return actions


def starter_files(actor: str, branch: str, task: str) -> dict[str, str]:
    return {
        "CURRENT_WORK.md": f"""# Current Work

Last updated: {now_display()}
Updated by: {actor}

## Active Tasks

### 1. {task}

Status: pending
Owner: {actor}
Branch: {branch}

Files touched:
- None yet.

Files locked:
- None yet.

Current state:
- Memory sync has been initialized. No active implementation work recorded yet.

Next step:
- Register the first task before editing code.

Blockers:
- None.

## Conflicts

- None.
""",
        "CURRENT_WORK.codex.md": """# Codex Quick Context

Read this before editing.

## Must Know

- This repo uses Git as code source of truth.
- Memory source of truth is `.codex-memory/`.
- Use `scripts/memory_sync.py sync` to load only new memory commits when possible.
- Do not rely on previous chat history.
- After memory changes, use `scripts/memory_sync.py commit` so `MEMORY_COMMITS.jsonl` records the update.

## Current Warnings

- No active warnings yet.
""",
        "HANDOFF.md": f"""# Handoff

## {task}

Owner: {actor}
Branch: {branch}
Last updated: {now_display()}

Context:
- Memory sync has been initialized.

What changed:
- Created repository-local Codex memory files.

Why:
- Codex sessions are stateless, so project memory must live in versioned files.

Files touched:
- .codex-memory/*
- AGENTS.md

Files locked:
- None.

Tests:
- Not applicable.

Known risks:
- Team members must follow the read-before-work and write-before-handoff protocol.

Next step:
- Register active tasks before code edits.
""",
        "TASK_LOG.md": "# Task Log\n",
        "DECISIONS.md": """# Decisions

## Initial memory architecture

Decision:
- Use `.codex-memory/` markdown files as external Codex working memory.

Reason:
- Codex threads and agent sessions are stateless; files provide reloadable context across people, computers, and threads.

Alternatives considered:
- Chat history only, rejected because it does not synchronize reliably.
- Separate per-agent memory folders, rejected because duplicated sources drift.

Impact:
- Every Codex session must read memory files before work and update them before handoff.
""",
        "RISKS.md": """# Risks

## Active Risks

### Memory files may become stale

Owner: team
Severity: medium
Status: open

Description:
- Codex may continue from old chat context if users skip the opening protocol.

Mitigation:
- Require every new or resumed thread to run memory sync before editing.
""",
        "DEPLOYMENT.md": """# Deployment

Production server:
- branch: main
- deploy path: unknown
- deploy command: unknown

Last deploy:
- time: not recorded
- commit: not recorded
- deployed by: not recorded
- result: not recorded

Rollback:
- previous commit: not recorded
- command: not recorded
""",
        SUMMARY_FILE: """# Memory Summary

This file holds compressed memory. Keep it short and update it with `memory_sync.py compact`.

## Current Summary

- No compressed memory yet.
""",
        INDEX_FILE: """# Memory Index

Use this file to locate memory without loading everything.

## Files

- `CURRENT_WORK.md`: active work and locks.
- `HANDOFF.md`: cross-thread and cross-person handoffs.
- `TASK_LOG.md`: chronological task notes.
- `MEMORY_COMMITS.jsonl`: append-only machine-readable memory commit log.
- `MEMORY_COMMITS.md`: human-readable memory commit log.
- `THREADS/`: per-thread memory streams.
- `CURSORS/`: per-thread sync cursors.
- `ARCHIVE/`: compacted or historical memory.
""",
        COMMIT_LOG_MD: "# Memory Commit Log\n",
    }


def agents_block() -> str:
    return f"""{BEGIN}
## Codex Memory Sync

Before code work:

1. Run or emulate `python scripts/memory_sync.py sync --project . --thread <thread-id>`.
2. Read only the new memory commits reported by the sync command.
3. If no cursor exists, read `.codex-memory/SUMMARY.md`, `.codex-memory/CURRENT_WORK.md`, and `.codex-memory/MEMORY_INDEX.md`.

Rules:

- Treat `.codex-memory/` as the external working memory.
- Do not rely on chat history as source of truth.
- Never overwrite a teammate's existing memory files during setup or import.
- Before editing files, check whether another active task owns or locks the same files.
- After memory changes, create a memory commit with `memory_sync.py commit`.
- Every memory commit must update `MEMORY_COMMITS.jsonl` and `MEMORY_COMMITS.md`.
- If memory grows too long, run `memory_sync.py compact` and commit the compacted summary.
- Update `HANDOFF.md` when another person, computer, day, or Codex thread may continue the work.

Every handoff must include what changed, why it changed, files touched, tests run, risks, and the next step.
{END}"""


def init_project(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    if not project.exists() or not project.is_dir():
        raise SystemExit(f"Project path is not a directory: {project}")

    actor = args.actor or default_actor()
    branch = args.branch or current_branch(project)
    actions = ensure_memory_dirs(project, dry_run=args.dry_run)
    root = memory_root(project)
    changed_locations: list[dict[str, Any]] = []

    for relative, content in starter_files(actor, branch, args.task).items():
        path = root / relative
        if path.exists() and not args.replace_existing:
            actions.append(f"kept existing {rel(path, project)}")
            continue
        before = read_text(path)
        if path.exists() and args.replace_existing:
            backup = backup_existing(path, project, dry_run=args.dry_run)
            actions.append(f"backed up {rel(path, project)} to {rel(backup, project)}")
        if args.dry_run:
            actions.append(f"would {'replace' if path.exists() else 'write'} {rel(path, project)}")
        else:
            write_text(path, content)
            changed_locations.append(file_location(path, before, content, project))
            actions.append(f"{'replaced' if path.exists() and args.replace_existing else 'wrote'} {rel(path, project)}")

    for keep in [root / THREADS_DIR / ".gitkeep", root / LOGS_DIR / ".gitkeep", root / CURSORS_DIR / ".gitkeep", root / ARCHIVE_DIR / ".gitkeep"]:
        if keep.exists():
            actions.append(f"kept existing {rel(keep, project)}")
        else:
            if args.dry_run:
                actions.append(f"would write {rel(keep, project)}")
            else:
                before = read_text(keep)
                write_text(keep, "")
                changed_locations.append(file_location(keep, before, "", project))
                actions.append(f"wrote {rel(keep, project)}")

    agents_path = project / "AGENTS.md"
    block = agents_block()
    if args.no_agents:
        actions.append("skipped AGENTS.md")
    elif not agents_path.exists():
        if args.dry_run:
            actions.append("would write AGENTS.md")
        else:
            before = read_text(agents_path)
            write_text(agents_path, "# Project Instructions\n\n" + block)
            changed_locations.append(file_location(agents_path, before, "# Project Instructions\n\n" + block, project))
            actions.append("wrote AGENTS.md")
    else:
        text = read_text(agents_path)
        if (BEGIN in text) != (END in text):
            actions.append("warning: kept AGENTS.md; partial Codex Memory Sync markers need manual repair")
        elif BEGIN in text and END in text:
            if args.replace_existing:
                backup = backup_existing(agents_path, project, dry_run=args.dry_run)
                start = text.index(BEGIN)
                end = text.index(END) + len(END)
                updated = text[:start].rstrip() + "\n\n" + block + "\n" + text[end:].lstrip()
                if args.dry_run:
                    actions.append(f"would back up AGENTS.md to {rel(backup, project)} and replace managed block")
                else:
                    write_text(agents_path, updated)
                    changed_locations.append(file_location(agents_path, text, block, project))
                    actions.append(f"backed up AGENTS.md to {rel(backup, project)}; replaced managed block")
            else:
                actions.append("kept existing AGENTS.md managed block")
        else:
            backup = backup_existing(agents_path, project, dry_run=args.dry_run)
            if args.dry_run:
                actions.append(f"would back up AGENTS.md to {rel(backup, project)} and append managed block")
            else:
                before = read_text(agents_path)
                write_text(agents_path, text.rstrip() + "\n\n" + block + "\n")
                changed_locations.append(file_location(agents_path, before, block, project))
                actions.append(f"backed up AGENTS.md to {rel(backup, project)}; appended managed block")

    if not args.dry_run:
        record_memory_commit(
            project=project,
            actor=actor,
            thread=args.thread,
            purpose="init",
            summary="Initialized or reconciled Codex memory sync files.",
            changed_locations=changed_locations,
            related_files=[MEMORY_DIR, "AGENTS.md" if not args.no_agents else ""],
            dry_run=False,
        )
        actions.append("recorded init memory commit")

    print("Codex memory sync initialization dry run complete." if args.dry_run else "Codex memory sync initialization complete.")
    for action in actions:
        print(f"- {action}")
    return 0


def extract_changed_memory_locations(project: Path, files: list[str]) -> list[dict[str, Any]]:
    locations = []
    root = memory_root(project)
    for file_value in files:
        if not file_value:
            continue
        path = Path(file_value)
        if not path.is_absolute():
            path = project / path
        if not path.exists() or not path.is_file():
            continue
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            continue
        text = read_text(path)
        locations.append(
            {
                "path": rel(path, project),
                "heading": first_heading(text),
                "entry_number": max(1, section_count(text)),
                "start_line": 1,
                "end_line": max(1, line_count(text)),
            }
        )
    return locations


def scan_existing_memory_locations(project: Path) -> list[dict[str, Any]]:
    root = memory_root(project)
    if not root.exists():
        return []
    ignored_parts = {BACKUPS_DIR, CURSORS_DIR, ".git"}
    ignored_names = {COMMIT_LOG, COMMIT_LOG_MD, COMPACTION_STATE}
    locations = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in ignored_parts for part in relative_parts):
            continue
        if path.name in ignored_names:
            continue
        if path.suffix.lower() not in {".md", ".txt", ".json", ".jsonl"}:
            continue
        text = read_text(path)
        locations.append(
            {
                "path": rel(path, project),
                "heading": first_heading(text) or rel(path, project),
                "entry_number": max(1, section_count(text)),
                "start_line": 1,
                "end_line": max(1, line_count(text)),
            }
        )
    return locations


def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def record_memory_commit(
    *,
    project: Path,
    actor: str,
    thread: str,
    purpose: str,
    summary: str,
    changed_locations: list[dict[str, Any]],
    related_files: list[str],
    dry_run: bool,
) -> dict[str, Any]:
    root = memory_root(project)
    files = [location for location in changed_locations]
    existing_records = load_jsonl(root / COMMIT_LOG)
    sequence = len(existing_records) + 1
    memory_id = commit_id(actor, thread, purpose, files)
    record = {
        "id": memory_id,
        "sequence": sequence,
        "time": now_iso(),
        "actor": actor,
        "thread": thread,
        "purpose": purpose,
        "summary": summary,
        "branch": current_branch(project),
        "git_commit": current_commit(project),
        "files": files,
        "related_files": [item for item in related_files if item],
    }
    append_jsonl(root / COMMIT_LOG, record, dry_run=dry_run)
    md_lines = [
        f"\n## {memory_id} - {now_display()}",
        "",
        f"Memory number: {sequence}",
        f"Actor: {actor}",
        f"Thread: {thread}",
        f"Purpose: {purpose}",
        f"Branch: {record['branch']}",
        f"Git commit: {record['git_commit']}",
        "",
        "Summary:",
        f"- {summary}",
        "",
        "Changed memory locations:",
    ]
    if files:
        for file_info in files:
            md_lines.append(
                f"- {file_info.get('path')} entry #{file_info.get('entry_number')} lines {file_info.get('start_line')}-{file_info.get('end_line')} {file_info.get('heading', '')}".rstrip()
            )
    else:
        md_lines.append("- None recorded.")
    md_lines.extend(["", "Related files:"])
    related = [item for item in related_files if item]
    if related:
        md_lines.extend(f"- {item}" for item in related)
    else:
        md_lines.append("- None.")
    md_lines.append("")
    append_text(root / COMMIT_LOG_MD, "\n".join(md_lines), dry_run=dry_run)
    return record


def append_section(path: Path, title: str, body: str, project: Path, dry_run: bool = False) -> dict[str, Any]:
    before = read_text(path)
    heading = f"\n\n## {title}\n\n"
    appended = heading + body.rstrip() + "\n"
    append_text(path, appended, dry_run=dry_run)
    return file_location(path, before, appended, project)


def commit_memory(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    actor = args.actor or default_actor()
    thread = slug(args.thread or actor)
    root = memory_root(project)
    ensure_memory_dirs(project, dry_run=args.dry_run)

    title = args.title or args.summary or args.purpose
    body = args.body or ""
    if args.body_file:
        body = read_text(Path(args.body_file).expanduser().resolve())
    if not body.strip():
        body = args.summary

    files_touched = args.files or []
    tests = args.tests or "Not recorded."
    risks = args.risks or "Not recorded."
    next_step = args.next or "Not recorded."
    timestamp_title = f"{now_display()} - {title}"

    entry = f"""Actor: {actor}
Thread: {thread}
Purpose: {args.purpose}

Summary:
- {args.summary}

Details:
{indent_block(body)}

Files touched:
{bullet(files_touched)}

Tests:
- {tests}

Risks:
- {risks}

Next:
- {next_step}
"""

    changed = []
    thread_path = root / THREADS_DIR / f"{thread}.md"
    if not thread_path.exists() and not args.dry_run:
        write_text(thread_path, f"# Thread Memory: {thread}\n")
    changed.append(append_section(thread_path, timestamp_title, entry, project, dry_run=args.dry_run))

    task_entry = f"""Branch: {current_branch(project)}

Changed:
- {args.summary}

Files:
{bullet(files_touched)}

Tests:
- {tests}

Risks:
- {risks}

Next:
- {next_step}
"""
    changed.append(append_section(root / "TASK_LOG.md", f"{now_display()} - {actor} / {thread}", task_entry, project, dry_run=args.dry_run))

    if args.handoff:
        changed.append(append_section(root / "HANDOFF.md", title, entry, project, dry_run=args.dry_run))

    if args.current:
        changed.append(append_section(root / "CURRENT_WORK.md", title, entry, project, dry_run=args.dry_run))

    changed.extend(extract_changed_memory_locations(project, args.memory_files or []))

    record = record_memory_commit(
        project=project,
        actor=actor,
        thread=thread,
        purpose=args.purpose,
        summary=args.summary,
        changed_locations=changed,
        related_files=files_touched,
        dry_run=args.dry_run,
    )
    update_index(project, dry_run=args.dry_run)
    print("Memory commit dry run complete." if args.dry_run else "Memory commit complete.")
    print(f"- id: {record['id']}")
    for location in changed:
        print(f"- changed {location.get('path')} entry #{location.get('entry_number')} lines {location.get('start_line')}-{location.get('end_line')}")
    if args.auto_compact and not args.dry_run:
        compact_if_needed(project, actor, thread, args.max_lines, args.max_commits, args.min_new_commits)
    return 0


def indent_block(value: str) -> str:
    lines = value.rstrip().splitlines() or ["Not recorded."]
    return "\n".join(f"  {line}" if line.strip() else "" for line in lines)


def bullet(values: list[str]) -> str:
    clean = [value for value in values if value]
    if not clean:
        return "- None recorded."
    return "\n".join(f"- {value}" for value in clean)


def update_index(project: Path, dry_run: bool = False) -> None:
    root = memory_root(project)
    records = load_jsonl(root / COMMIT_LOG)
    thread_files = sorted((root / THREADS_DIR).glob("*.md")) if (root / THREADS_DIR).exists() else []
    latest = records[-10:]
    content = ["# Memory Index", "", f"Last updated: {now_display()}", "", "## Latest Memory Commits", ""]
    if latest:
        for record in latest:
            content.append(f"- #{record.get('sequence')} {record.get('id')} | {record.get('time')} | {record.get('actor')} | {record.get('summary')}")
    else:
        content.append("- None.")
    content.extend(["", "## Thread Files", ""])
    if thread_files:
        for path in thread_files:
            content.append(f"- `{rel(path, project)}`")
    else:
        content.append("- None.")
    content.extend(
        [
            "",
            "## Core Files",
            "",
            "- `.codex-memory/SUMMARY.md`",
            "- `.codex-memory/CURRENT_WORK.md`",
            "- `.codex-memory/HANDOFF.md`",
            "- `.codex-memory/TASK_LOG.md`",
            "- `.codex-memory/MEMORY_COMMITS.jsonl`",
            "- `.codex-memory/MEMORY_COMMITS.md`",
        ]
    )
    write_text(root / INDEX_FILE, "\n".join(content), dry_run=dry_run)


def cursor_path(project: Path, thread: str) -> Path:
    return memory_root(project) / CURSORS_DIR / f"{slug(thread)}.json"


def load_cursor(project: Path, thread: str) -> dict[str, Any]:
    path = cursor_path(project, thread)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_cursor(project: Path, thread: str, commit_id_value: str, dry_run: bool = False) -> None:
    data = {"thread": slug(thread), "last_seen_commit": commit_id_value, "updated_at": now_iso()}
    write_text(cursor_path(project, thread), json.dumps(data, ensure_ascii=False, indent=2), dry_run=dry_run)


def sync_memory(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    thread = slug(args.thread or default_actor())
    root = memory_root(project)
    records = load_jsonl(root / COMMIT_LOG)
    cursor = load_cursor(project, thread)
    last_seen = args.since or cursor.get("last_seen_commit")

    start = 0
    if last_seen:
        for index, record in enumerate(records):
            if record.get("id") == last_seen:
                start = index + 1
                break
    new_records = records[start:]

    if not cursor and not args.since:
        print("No sync cursor found. Read baseline files first:")
        print(f"- {rel(root / SUMMARY_FILE, project)}")
        print(f"- {rel(root / 'CURRENT_WORK.md', project)}")
        print(f"- {rel(root / INDEX_FILE, project)}")
        if records:
            print(f"Then process {len(records)} historical memory commits or run with --mark-seen after reading the baseline.")

    if not new_records:
        print("No new memory commits.")
        if records and args.mark_seen:
            save_cursor(project, thread, records[-1]["id"], dry_run=args.dry_run)
            print(f"- cursor updated to {records[-1]['id']}")
        return 0

    print(f"New memory commits for thread `{thread}`: {len(new_records)}")
    for record in new_records:
        print(f"\n## #{record.get('sequence')} {record.get('id')} | {record.get('time')} | {record.get('actor')}")
        print(f"Summary: {record.get('summary')}")
        print("Read locations:")
        files = record.get("files") or []
        if not files:
            print("- No precise location recorded.")
        for file_info in files:
            print(f"- {file_info.get('path')} entry #{file_info.get('entry_number')} lines {file_info.get('start_line')}-{file_info.get('end_line')} {file_info.get('heading', '')}".rstrip())
    if args.mark_seen and records:
        save_cursor(project, thread, records[-1]["id"], dry_run=args.dry_run)
        print(f"\nCursor updated to {records[-1]['id']}")
    return 0


def import_memory(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    actor = args.actor or default_actor()
    thread = slug(args.thread or f"import-{actor}")
    source = Path(args.source).expanduser().resolve()
    if not source.exists() or not source.is_dir():
        raise SystemExit(f"Source path is not a directory: {source}")
    ensure_memory_dirs(project, dry_run=args.dry_run)
    root = memory_root(project)
    import_dir = root / "IMPORTED" / f"{stamp()}-{slug(source.name)}"
    changed = []
    copied = []
    for source_file in sorted(source.rglob("*")):
        if not source_file.is_file():
            continue
        if args.extensions and source_file.suffix.lower().lstrip(".") not in args.extensions:
            continue
        rel_source = source_file.relative_to(source)
        target = unique_path(import_dir / rel_source)
        text = read_text(source_file)
        if args.dry_run:
            copied.append(f"would import {source_file} -> {rel(target, project)}")
        else:
            write_text(target, text)
            copied.append(f"imported {source_file} -> {rel(target, project)}")
        changed.append(
            {
                "path": rel(target, project),
                "heading": first_heading(text) or rel_source.as_posix(),
                "start_line": 1,
                "end_line": max(1, line_count(text)),
            }
        )
    record = record_memory_commit(
        project=project,
        actor=actor,
        thread=thread,
        purpose="import",
        summary=args.summary or f"Imported existing thread memory from {source}",
        changed_locations=changed,
        related_files=[str(source)],
        dry_run=args.dry_run,
    )
    update_index(project, dry_run=args.dry_run)
    print("Memory import dry run complete." if args.dry_run else "Memory import complete.")
    for item in copied:
        print(f"- {item}")
    print(f"- id: {record['id']}")
    return 0


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    index = 2
    while True:
        candidate = parent / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def adopt_memory(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    actor = args.actor or default_actor()
    ensure_memory_dirs(project, dry_run=args.dry_run)
    root = memory_root(project)
    records = load_jsonl(root / COMMIT_LOG)
    record = None
    if args.record_existing or not records:
        locations = scan_existing_memory_locations(project)
        if locations:
            record = record_memory_commit(
                project=project,
                actor=actor,
                thread=slug(args.thread or actor),
                purpose="adopt",
                summary=args.summary or "Adopted existing teammate memory without overwriting files.",
                changed_locations=locations,
                related_files=[location["path"] for location in locations],
                dry_run=args.dry_run,
            )
    update_index(project, dry_run=args.dry_run)
    records = load_jsonl(root / COMMIT_LOG)
    latest = records[-1]["id"] if records else ""
    if latest and args.mark_seen:
        save_cursor(project, args.thread or actor, latest, dry_run=args.dry_run)
    print("Adopt existing memory complete.")
    print("- Existing files were not overwritten.")
    print(f"- Memory commits: {len(records)}")
    if record:
        print(f"- recorded adoption commit: #{record.get('sequence')} {record.get('id')}")
    if latest:
        print(f"- Latest commit: {latest}")
    print("- Read baseline files:")
    print(f"  - {MEMORY_DIR}/{SUMMARY_FILE}")
    print(f"  - {MEMORY_DIR}/CURRENT_WORK.md")
    print(f"  - {MEMORY_DIR}/{INDEX_FILE}")
    return 0


def compact_memory(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    actor = args.actor or default_actor()
    thread = slug(args.thread or actor)
    root = memory_root(project)
    ensure_memory_dirs(project, dry_run=args.dry_run)
    records = load_jsonl(root / COMMIT_LOG)
    thread_text_files = sorted((root / THREADS_DIR).glob("*.md")) if (root / THREADS_DIR).exists() else []
    text_files = [
        root / "CURRENT_WORK.md",
        root / "HANDOFF.md",
        root / "TASK_LOG.md",
        *thread_text_files,
    ]
    total_lines = sum(line_count(read_text(path)) for path in text_files if path.exists())
    new_since_compaction = commits_since_last_compaction(project, records)
    should_compact = args.force or (
        (total_lines > args.max_lines or len(records) > args.max_commits)
        and (new_since_compaction >= args.min_new_commits or total_lines > args.max_lines * 2)
    )
    if not should_compact:
        print("No compaction needed.")
        print(f"- lines: {total_lines} / {args.max_lines}")
        print(f"- commits: {len(records)} / {args.max_commits}")
        print(f"- new commits since last compaction: {new_since_compaction} / {args.min_new_commits}")
        return 0

    archive_target = root / ARCHIVE_DIR / f"memory-archive-{stamp()}.md"
    archive_parts = [f"# Memory Archive {now_display()}", ""]
    for path in text_files:
        if path.exists():
            archive_parts.append(f"\n## Archived {rel(path, project)}\n")
            archive_parts.append(read_text(path))
    archive_content = "\n".join(archive_parts)
    summary_body = args.summary or build_extractive_summary(project, records, text_files, args.keep_latest)
    summary_content = f"""# Memory Summary

Last compacted: {now_display()}
Compacted by: {actor}
Archive: `{rel(archive_target, project)}`

## Current Summary

{summary_body.rstrip()}

## Recent Memory Commits

{recent_commits_markdown(records, args.keep_latest)}
"""
    changed = []
    before_summary = read_text(root / SUMMARY_FILE)
    before_archive = read_text(archive_target)
    if not args.dry_run:
        write_text(archive_target, archive_content)
        write_text(root / SUMMARY_FILE, summary_content)
    changed.append(file_location(root / SUMMARY_FILE, before_summary, summary_content, project))
    changed.append(file_location(archive_target, before_archive, archive_content, project))

    if args.prune_thread_logs:
        for path in text_files:
            if path.name in {"CURRENT_WORK.md", "HANDOFF.md"}:
                continue
            if not path.exists():
                continue
            keep_content = f"# {first_heading(read_text(path)) or path.stem}\n\nCompacted into `{rel(archive_target, project)}` at {now_display()}.\n"
            before = read_text(path)
            if not args.dry_run:
                write_text(path, keep_content)
            changed.append(file_location(path, before, keep_content, project))

    record = record_memory_commit(
        project=project,
        actor=actor,
        thread=thread,
        purpose="compact",
        summary=f"Compacted memory into {rel(archive_target, project)}.",
        changed_locations=changed,
        related_files=[rel(archive_target, project), rel(root / SUMMARY_FILE, project)],
        dry_run=args.dry_run,
    )
    write_compaction_state(project, records[-1]["id"] if records else record["id"], record["id"], dry_run=args.dry_run)
    update_index(project, dry_run=args.dry_run)
    print("Memory compaction dry run complete." if args.dry_run else "Memory compaction complete.")
    print(f"- id: {record['id']}")
    print(f"- archive: {rel(archive_target, project)}")
    print(f"- total lines before compaction: {total_lines}")
    return 0


def commits_since_last_compaction(project: Path, records: list[dict[str, Any]]) -> int:
    state_path = memory_root(project) / COMPACTION_STATE
    if not state_path.exists():
        return len(records)
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return len(records)
    last_seen = state.get("last_source_commit")
    if not last_seen:
        return len(records)
    for index, record in enumerate(records):
        if record.get("id") == last_seen:
            return max(0, len(records) - index - 1)
    return len(records)


def write_compaction_state(project: Path, source_commit: str, compact_commit: str, dry_run: bool = False) -> None:
    state = {
        "last_source_commit": source_commit,
        "last_compaction_commit": compact_commit,
        "updated_at": now_iso(),
    }
    write_text(memory_root(project) / COMPACTION_STATE, json.dumps(state, ensure_ascii=False, indent=2), dry_run=dry_run)


def compact_if_needed(project: Path, actor: str, thread: str, max_lines: int, max_commits: int, min_new_commits: int) -> None:
    class CompactArgs:
        pass

    args = CompactArgs()
    args.project = str(project)
    args.actor = actor
    args.thread = thread
    args.summary = ""
    args.max_lines = max_lines
    args.max_commits = max_commits
    args.keep_latest = 20
    args.prune_thread_logs = False
    args.force = False
    args.dry_run = False
    args.min_new_commits = min_new_commits
    compact_memory(args)


def build_extractive_summary(project: Path, records: list[dict[str, Any]], files: list[Path], keep_latest: int) -> str:
    lines = ["### Active Context", ""]
    current = read_text(memory_root(project) / "CURRENT_WORK.md").strip()
    if current:
        excerpt = "\n".join(current.splitlines()[:80])
        lines.append(excerpt)
    lines.extend(["", "### Latest Commits", ""])
    for record in records[-keep_latest:]:
        lines.append(f"- #{record.get('sequence')} {record.get('time')} {record.get('actor')}: {record.get('summary')} ({record.get('id')})")
    return "\n".join(lines)


def recent_commits_markdown(records: list[dict[str, Any]], keep_latest: int) -> str:
    if not records:
        return "- None."
    return "\n".join(f"- #{record.get('sequence')} {record.get('id')} | {record.get('time')} | {record.get('summary')}" for record in records[-keep_latest:])


def status_memory(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    root = memory_root(project)
    records = load_jsonl(root / COMMIT_LOG)
    print("Codex memory status")
    print(f"- project: {project}")
    print(f"- memory directory exists: {root.exists()}")
    print(f"- memory commits: {len(records)}")
    if records:
        print(f"- latest commit: #{records[-1].get('sequence')} {records[-1].get('id')} | {records[-1].get('summary')}")
    thread_files = sorted((root / THREADS_DIR).glob("*.md")) if (root / THREADS_DIR).exists() else []
    print(f"- thread files: {len(thread_files)}")
    for thread_file in thread_files:
        print(f"  - {rel(thread_file, project)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codex Memory Sync")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create or reconcile memory files without overwriting existing content.")
    init.add_argument("--project", default=".")
    init.add_argument("--actor")
    init.add_argument("--thread", default="init")
    init.add_argument("--branch")
    init.add_argument("--task", default="Memory sync setup")
    init.add_argument("--replace-existing", action="store_true")
    init.add_argument("--dry-run", action="store_true")
    init.add_argument("--no-agents", action="store_true")
    init.set_defaults(func=init_project)

    commit = sub.add_parser("commit", help="Append a thread memory entry and record a memory commit log entry.")
    commit.add_argument("--project", default=".")
    commit.add_argument("--actor")
    commit.add_argument("--thread", required=True)
    commit.add_argument("--purpose", default="work")
    commit.add_argument("--title", default="")
    commit.add_argument("--summary", required=True)
    commit.add_argument("--body", default="")
    commit.add_argument("--body-file")
    commit.add_argument("--files", nargs="*", default=[])
    commit.add_argument("--memory-files", nargs="*", default=[])
    commit.add_argument("--tests", default="")
    commit.add_argument("--risks", default="")
    commit.add_argument("--next", default="")
    commit.add_argument("--handoff", action="store_true")
    commit.add_argument("--current", action="store_true")
    commit.add_argument("--dry-run", action="store_true")
    commit.add_argument("--no-auto-compact", dest="auto_compact", action="store_false")
    commit.add_argument("--max-lines", type=int, default=800)
    commit.add_argument("--max-commits", type=int, default=80)
    commit.add_argument("--min-new-commits", type=int, default=10)
    commit.set_defaults(auto_compact=True)
    commit.set_defaults(func=commit_memory)

    sync = sub.add_parser("sync", help="Show new memory commits since this thread's cursor.")
    sync.add_argument("--project", default=".")
    sync.add_argument("--thread", required=True)
    sync.add_argument("--since")
    sync.add_argument("--mark-seen", action="store_true")
    sync.add_argument("--dry-run", action="store_true")
    sync.set_defaults(func=sync_memory)

    importer = sub.add_parser("import", help="Import existing thread memory without overwriting current memory.")
    importer.add_argument("--project", default=".")
    importer.add_argument("--source", required=True)
    importer.add_argument("--actor")
    importer.add_argument("--thread")
    importer.add_argument("--summary", default="")
    importer.add_argument("--extensions", nargs="*", default=["md", "txt", "json", "jsonl"])
    importer.add_argument("--dry-run", action="store_true")
    importer.set_defaults(func=import_memory)

    adopt = sub.add_parser("adopt", help="Adopt a teammate's existing memory directory without overwriting content.")
    adopt.add_argument("--project", default=".")
    adopt.add_argument("--actor")
    adopt.add_argument("--thread", default="")
    adopt.add_argument("--summary", default="")
    adopt.add_argument("--record-existing", action="store_true")
    adopt.add_argument("--mark-seen", action="store_true")
    adopt.add_argument("--dry-run", action="store_true")
    adopt.set_defaults(func=adopt_memory)

    compact = sub.add_parser("compact", help="Compact long memory into SUMMARY and ARCHIVE.")
    compact.add_argument("--project", default=".")
    compact.add_argument("--actor")
    compact.add_argument("--thread", default="")
    compact.add_argument("--summary", default="")
    compact.add_argument("--max-lines", type=int, default=800)
    compact.add_argument("--max-commits", type=int, default=80)
    compact.add_argument("--min-new-commits", type=int, default=10)
    compact.add_argument("--keep-latest", type=int, default=20)
    compact.add_argument("--prune-thread-logs", action="store_true")
    compact.add_argument("--force", action="store_true")
    compact.add_argument("--dry-run", action="store_true")
    compact.set_defaults(func=compact_memory)

    status = sub.add_parser("status", help="Show memory sync status.")
    status.add_argument("--project", default=".")
    status.set_defaults(func=status_memory)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
