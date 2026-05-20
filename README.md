<p align="center">
  <img src="assets/syncmind-logo.png" alt="SyncMind logo" width="996">
</p>

# SyncMind

SyncMind is a Codex skill for keeping project memory in sync across people, computers, and Codex threads.

It does not try to make a chat session remember everything forever. Instead, it puts the working memory in your repository, records every memory change, and lets each new thread read only what changed.

## The Problem

Codex threads are useful, but they do not share the same live memory.

In a team, that becomes painful quickly:

- one teammate's Codex does not know what another teammate's Codex already changed
- a new thread cannot see the old thread's decisions
- handoffs live in chat history instead of the project
- everyone rereads too much context just to find what changed
- long memory files eventually waste tokens
- existing notes can be accidentally overwritten by a setup script

SyncMind keeps those parts explicit and versioned.

## What It Does

SyncMind adds a `.codex-memory/` folder to your project.

Inside that folder it keeps:

- current work and active file ownership
- per-thread memory files
- handoff notes
- task logs
- decisions, risks, and deployment notes
- a machine-readable memory commit log
- a human-readable memory commit log
- per-thread sync cursors
- compacted summaries and archives

Every memory update gets a numbered memory commit. Each commit records who wrote it, when it happened, which thread wrote it, what changed, and the exact file location to read next.


## Install

Install the skill from GitHub:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

On Windows, the command is usually:

```powershell
python C:\Users\ssema\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py --repo FairChan/codex-memory-sync --path .
```

Restart Codex after installing the skill.

## Start a New Project

In a brand-new project, ask Codex:

```text
Use $codex-memory-sync to initialize shared memory for this repository.
```

Or run the script directly:

```bash
python scripts/memory_sync.py init --project /path/to/repo --actor "your-name" --thread "your-thread"
```

This creates `.codex-memory/` and `AGENTS.md` if needed.

It does not overwrite existing files by default.

## Join an Existing Project

If your teammate already has `.codex-memory/`, ask Codex:

```text
Use $codex-memory-sync to adopt the existing memory in this project without overwriting anything.
```

Or run:

```bash
python scripts/memory_sync.py adopt --project /path/to/repo --actor "your-name" --thread "your-thread" --record-existing
```

This scans the existing memory and creates a first indexed memory commit if one does not already exist.

## Use It in Natural Language

You can use SyncMind without remembering every command.

Start work:

```text
Use $codex-memory-sync to sync this thread. Only show me new memory since my last cursor.
```

Record progress:

```text
Use $codex-memory-sync to commit this thread's memory. Include what changed, tests, risks, next step, and touched files.
```

Prepare a handoff:

```text
Use $codex-memory-sync to write a handoff for my teammate. Do not overwrite existing notes.
```

Compress long memory:

```text
Use $codex-memory-sync to compact the project memory and keep the latest context easy to reload.
```

Import old notes:

```text
Use $codex-memory-sync to import my old thread notes into this project without replacing the current memory.
```

## Direct Commands

Sync this thread:

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a"
```

After reading the reported memory locations, mark them as seen:

```bash
python scripts/memory_sync.py sync --project /path/to/repo --thread "thread-a" --mark-seen
```

Commit thread memory:

```bash
python scripts/memory_sync.py commit \
  --project /path/to/repo \
  --actor "alice" \
  --thread "alice-thread" \
  --summary "Finished login session refresh" \
  --body "Implemented refresh-token happy path and left browser expiry QA as the next step." \
  --files app/auth.ts app/session.ts \
  --tests "auth unit tests passed" \
  --risks "browser expiry flow still needs manual QA" \
  --next "Run browser login regression" \
  --handoff \
  --current
```

Compact memory:

```bash
python scripts/memory_sync.py compact --project /path/to/repo --actor "alice" --thread "alice-thread"
```

Check status:

```bash
python scripts/memory_sync.py status --project /path/to/repo
```

## How Incremental Sync Saves Context

SyncMind writes every memory change to:

```text
.codex-memory/MEMORY_COMMITS.jsonl
.codex-memory/MEMORY_COMMITS.md
```

Each record includes:

- memory number
- memory id
- actor
- thread
- summary
- changed memory file
- entry number inside that file
- line range
- related code files

So a new thread can read only the exact new entries instead of loading every memory file.

Example sync output:

```text
New memory commits for thread `bob-thread`: 1

## #12 mem-c91fafcdcbc5 | 2026-05-20T14:00:00+08:00 | Alice
Summary: Finished login session refresh
Read locations:
- .codex-memory/THREADS/alice-thread.md entry #3 lines 42-78
- .codex-memory/HANDOFF.md entry #5 lines 80-116
```

## File Layout

```text
.codex-memory/
  CURRENT_WORK.md
  CURRENT_WORK.codex.md
  HANDOFF.md
  TASK_LOG.md
  DECISIONS.md
  RISKS.md
  DEPLOYMENT.md
  SUMMARY.md
  MEMORY_INDEX.md
  MEMORY_COMMITS.jsonl
  MEMORY_COMMITS.md
  COMPACTION_STATE.json
  THREADS/
  CURSORS/
  ARCHIVE/
  IMPORTED/
```

## Safety

SyncMind is conservative by default.

- `init` creates missing files and keeps existing files
- `adopt` never overwrites existing memory
- `import` copies old notes into a timestamped folder
- `commit` appends new entries
- `compact` archives memory before updating the summary
- destructive replacement is not part of the normal workflow

## Why This Exists

Project memory works best when it is visible.

Files are easy to diff, review, commit, roll back, and share. SyncMind keeps the process simple: write down what changed, record where it was written, and let the next thread read only the new parts.
