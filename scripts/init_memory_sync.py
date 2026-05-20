#!/usr/bin/env python3
"""Initialize repository-local Codex memory sync files."""

from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
from typing import Iterable


BEGIN = "<!-- BEGIN CODEX MEMORY SYNC -->"
END = "<!-- END CODEX MEMORY SYNC -->"


def now_stamp() -> str:
    return dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")


def write_file(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return f"kept existing {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return f"wrote {path}"


def append_or_replace_managed_block(path: Path, block: str, force: bool) -> str:
    if not path.exists():
        return write_file(path, f"# Project Instructions\n\n{block}", force=True)

    text = path.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        if not force:
            return f"kept existing managed block in {path}"
        start = text.index(BEGIN)
        end = text.index(END) + len(END)
        updated = text[:start].rstrip() + "\n\n" + block + "\n" + text[end:].lstrip()
        path.write_text(updated.rstrip() + "\n", encoding="utf-8")
        return f"updated managed block in {path}"

    updated = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(updated, encoding="utf-8")
    return f"appended managed block to {path}"


def bullet_lines(items: Iterable[str]) -> str:
    values = [item.strip() for item in items if item and item.strip()]
    if not values:
        return "- None yet."
    return "\n".join(f"- {item}" for item in values)


def current_work(owner: str, branch: str, task: str) -> str:
    return f"""# Current Work

Last updated: {now_stamp()}
Updated by: {owner}

## Active Tasks

### 1. {task}

Status: pending
Owner: {owner}
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
"""


def quick_context() -> str:
    return """# Codex Quick Context

Read this before editing.

## Must Know

- This repo uses Git as code source of truth.
- Memory source of truth is `.codex-memory/`.
- Do not rely on previous chat history.
- Before editing: read CURRENT_WORK.md, HANDOFF.md, TASK_LOG.md.
- After editing: update CURRENT_WORK.md and TASK_LOG.md.

## Current Warnings

- No active warnings yet.
"""


def handoff(owner: str, branch: str, task: str) -> str:
    return f"""# Handoff

## {task}

Owner: {owner}
Branch: {branch}
Last updated: {now_stamp()}

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
- Register active tasks in CURRENT_WORK.md before code edits.
"""


def task_log(owner: str, branch: str) -> str:
    return f"""# Task Log

## {now_stamp()} - {owner}

Branch: {branch}

Changed:
- Initialized Codex memory sync files.

Files:
- .codex-memory/CURRENT_WORK.md
- .codex-memory/CURRENT_WORK.codex.md
- .codex-memory/HANDOFF.md
- .codex-memory/TASK_LOG.md
- .codex-memory/DECISIONS.md
- .codex-memory/RISKS.md
- .codex-memory/DEPLOYMENT.md
- AGENTS.md

Tests:
- Initialization script completed.

Risks:
- None for initialization.

Next:
- Use the start-work prompt before implementation.
"""


def decisions() -> str:
    return """# Decisions

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
"""


def risks() -> str:
    return """# Risks

## Active Risks

### Memory files may become stale

Owner: team
Severity: medium
Status: open

Description:
- Codex may continue from old chat context if users skip the opening protocol.

Mitigation:
- Require every new or resumed thread to read `.codex-memory/` before editing.
"""


def deployment() -> str:
    return """# Deployment

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
"""


def agents_block() -> str:
    return f"""{BEGIN}
## Codex Memory Sync

Before code work, always read:

1. `.codex-memory/CURRENT_WORK.md`
2. `.codex-memory/CURRENT_WORK.codex.md`
3. `.codex-memory/HANDOFF.md`
4. `.codex-memory/TASK_LOG.md`

Rules:

- Treat `.codex-memory/` as the external working memory.
- Do not rely on chat history as source of truth.
- Before editing files, check whether another active task owns or locks the same files.
- If there is a conflict, stop and report it.
- After making changes, update `CURRENT_WORK.md` and `TASK_LOG.md`.
- Update `HANDOFF.md` when another person, computer, day, or Codex thread may continue the work.
- Update `DEPLOYMENT.md` after production deploys.

Every handoff must include what changed, why it changed, files touched, tests run, risks, and the next step.
{END}"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize Codex memory sync files in a repository.")
    parser.add_argument("--project", default=".", help="Target repository path. Defaults to current directory.")
    parser.add_argument("--owner", default=os.environ.get("USERNAME") or os.environ.get("USER") or "team")
    parser.add_argument("--branch", default="main", help="Initial branch name to record.")
    parser.add_argument("--task", default="Memory sync setup", help="Initial task title.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing memory files and managed AGENTS block.")
    parser.add_argument("--no-agents", action="store_true", help="Do not create or update AGENTS.md.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = Path(args.project).expanduser().resolve()
    if not project.exists():
        raise SystemExit(f"Project path does not exist: {project}")
    if not project.is_dir():
        raise SystemExit(f"Project path is not a directory: {project}")

    memory_dir = project / ".codex-memory"
    threads_dir = memory_dir / "THREADS"
    threads_dir.mkdir(parents=True, exist_ok=True)

    actions = [
        write_file(memory_dir / "CURRENT_WORK.md", current_work(args.owner, args.branch, args.task), args.force),
        write_file(memory_dir / "CURRENT_WORK.codex.md", quick_context(), args.force),
        write_file(memory_dir / "HANDOFF.md", handoff(args.owner, args.branch, args.task), args.force),
        write_file(memory_dir / "TASK_LOG.md", task_log(args.owner, args.branch), args.force),
        write_file(memory_dir / "DECISIONS.md", decisions(), args.force),
        write_file(memory_dir / "RISKS.md", risks(), args.force),
        write_file(memory_dir / "DEPLOYMENT.md", deployment(), args.force),
        write_file(threads_dir / ".gitkeep", "", args.force),
    ]

    if not args.no_agents:
        actions.append(append_or_replace_managed_block(project / "AGENTS.md", agents_block(), args.force))

    print("Codex memory sync initialization complete.")
    for action in actions:
        print(f"- {action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
