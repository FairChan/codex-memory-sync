---
name: codex-memory-sync
description: Set up and operate external Codex working memory for multi-person, multi-computer, or multi-thread coding workflows. Use when teammates share a repository with Codex, when different Codex chats need synchronized project context, when a user needs non-overwriting memory import, per-thread memory commits, incremental memory sync, memory compaction, memory commit logs, AGENTS collaboration rules, or a durable markdown/JSONL memory system that survives stateless sessions.
---

# Codex Memory Sync

Use this skill to make Codex coordination file-based instead of chat-memory-based. The repository becomes the shared memory source of truth. Every thread writes memory commits, every new thread syncs only new commits, and long memory is compacted into summaries and archives.

## Core Model

- Code state lives in Git branches and commits.
- Working memory lives in `.codex-memory/`.
- Human-readable memory is Markdown.
- Machine-readable memory history is `.codex-memory/MEMORY_COMMITS.jsonl`.
- Every memory change must create a memory commit.
- New Codex threads use cursors in `.codex-memory/CURSORS/` to read only new commits.
- Existing teammate files are never overwritten by default.

## Commands

Use the bundled script:

```bash
python scripts/memory_sync.py <command> --project /path/to/repo
```

Windows PowerShell:

```powershell
python .\scripts\memory_sync.py <command> --project C:\path\to\repo
```

Backward-compatible init still works:

```bash
python scripts/init_memory_sync.py --project /path/to/repo
```

## Fresh Project

For a brand-new project, initialize memory:

```bash
python scripts/memory_sync.py init --project /path/to/repo --actor "name" --thread "thread-a"
```

This creates `.codex-memory/`, `AGENTS.md` if missing, the memory commit log, thread folders, cursors, summary, archive folders, and an initial memory commit. It does not require any existing directory.

After each thread finishes work, commit that thread's memory:

```bash
python scripts/memory_sync.py commit --project /path/to/repo --actor "name" --thread "thread-a" --summary "Finished login refresh flow" --body "What changed, why, risks, and next step." --files app/auth.ts app/session.ts --tests "npm test -- auth passed" --risks "Manual browser session expiry still needs QA" --next "Run browser login regression" --handoff --current
```

## Existing Teammate Project

If a teammate already created `.codex-memory/`, adopt it without overwriting:

```bash
python scripts/memory_sync.py adopt --project /path/to/repo --actor "name" --thread "my-thread" --record-existing
```

This keeps all existing files unchanged. If the teammate did not have a `MEMORY_COMMITS.jsonl`, `adopt --record-existing` scans the existing memory files and records an adoption memory commit so future syncs have an indexed starting point.

To import separate old thread notes without overwriting:

```bash
python scripts/memory_sync.py import --project /path/to/repo --source /path/to/old/thread-notes --actor "name" --thread "my-thread" --summary "Imported previous local thread notes"
```

Imported files go under `.codex-memory/IMPORTED/<timestamp-source>/`.

## Thread Sync

At the start of every Codex thread:

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a"
```

If no cursor exists, read only the baseline files it prints:

- `.codex-memory/SUMMARY.md`
- `.codex-memory/CURRENT_WORK.md`
- `.codex-memory/MEMORY_INDEX.md`

After reading the reported commits, mark them seen:

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a" --mark-seen
```

After that, the same thread only needs to read new memory commits. Sync output gives exact locations:

- memory commit sequence number
- memory commit id
- actor
- summary
- file path
- entry number inside that file
- line range

## Memory Commit Log

Every `commit`, `init`, `adopt`, `import`, and `compact` writes:

- `.codex-memory/MEMORY_COMMITS.jsonl` for tools
- `.codex-memory/MEMORY_COMMITS.md` for humans

Each entry records:

- when
- who
- thread id
- purpose
- summary
- changed memory files
- entry number in each memory file
- line ranges
- related code files
- current Git branch and commit

Do not manually edit `MEMORY_COMMITS.jsonl` unless repairing corruption.

## Compaction

Memory compaction is automatic after `commit` when thresholds are exceeded. Defaults:

- more than 800 memory lines or 80 memory commits
- at least 10 new commits since the last compaction, unless memory is more than twice the line threshold

Manual compaction:

```bash
python scripts/memory_sync.py compact --project /path/to/repo --actor "name" --thread "thread-a"
```

Force compaction:

```bash
python scripts/memory_sync.py compact --project /path/to/repo --actor "name" --thread "thread-a" --force
```

Compaction writes:

- `.codex-memory/SUMMARY.md`
- `.codex-memory/ARCHIVE/memory-archive-<timestamp>.md`
- a `compact` entry in the memory commit log
- `.codex-memory/COMPACTION_STATE.json`

Use `--prune-thread-logs` only when the user explicitly wants old thread logs replaced by archive pointers.

## Non-Overwrite Rules

- `init` creates missing files and keeps existing files.
- `adopt` never overwrites existing files.
- `import` copies into a timestamped imported folder and never overwrites.
- `commit` appends sections; it does not replace previous sections.
- `compact` archives before summary updates.
- `--replace-existing` exists only for explicit repair operations and should not be used during normal collaboration.

## Required Workflow

Start work:

1. Run `git pull`.
2. Run `memory_sync.py sync --thread <thread-id>`.
3. Read only baseline files or new commit locations reported by sync.
4. Check `CURRENT_WORK.md` for owners, locks, and conflicts.

Finish work:

1. Update memory through `memory_sync.py commit`.
2. Include changed code files, tests, risks, and next step.
3. Let auto-compaction run if needed.
4. Commit and push code plus `.codex-memory/` changes together when appropriate.

## References

Load only when needed:

- `references/team-protocol.md`: detailed Chinese team operating procedure.
- `references/templates.md`: canonical templates and file layout.
- `references/prompts.md`: reusable Chinese prompts.
