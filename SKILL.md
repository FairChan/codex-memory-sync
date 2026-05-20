---
name: codex-memory-sync
description: Set up and maintain external Codex working memory for multi-person, multi-computer, or multi-thread coding workflows. Use when teammates share a repository with Codex, when different Codex chats need synchronized project context, when handoffs drift, when a user asks to create CURRENT_WORK, HANDOFF, TASK_LOG, AGENTS collaboration rules, or when Codex should bootstrap a durable markdown memory system that survives stateless sessions.
---

# Codex Memory Sync

Use this skill to make Codex coordination file-based instead of chat-memory-based. The goal is a single source of truth inside the repository that every Codex thread reloads before work and updates before handoff.

## Core Model

Treat code and memory as two synchronized layers:

- Code state lives in Git branches and commits.
- Working memory lives in `.codex-memory/` markdown files.
- `AGENTS.md` tells future Codex sessions to read and update that memory.
- Chat history is never the source of truth.

## Quick Setup

From this skill directory, run the initializer against the target repository:

```bash
python scripts/init_memory_sync.py --project /path/to/repo --owner "team-or-person"
```

On Windows PowerShell:

```powershell
python .\scripts\init_memory_sync.py --project C:\path\to\repo --owner "team-or-person"
```

The script creates:

- `.codex-memory/CURRENT_WORK.md`
- `.codex-memory/CURRENT_WORK.codex.md`
- `.codex-memory/HANDOFF.md`
- `.codex-memory/TASK_LOG.md`
- `.codex-memory/DECISIONS.md`
- `.codex-memory/RISKS.md`
- `.codex-memory/DEPLOYMENT.md`
- `.codex-memory/THREADS/.gitkeep`
- `AGENTS.md` if missing, or a managed Codex Memory Sync block if present

Safety behavior:

- If `.codex-memory/` does not exist, the script creates it and writes starter files.
- If `.codex-memory/` already exists, the script creates only missing files and keeps existing files unchanged.
- If a teammate already wrote their workflow into any memory file, the script does not overwrite it.
- If `AGENTS.md` exists without a Codex Memory Sync block, the script appends one managed block and first backs up `AGENTS.md`.
- If `AGENTS.md` already has the managed block, the script keeps it unchanged.
- `--force` is deprecated and does not enable overwrites.
- Use `--replace-existing` only when the user explicitly wants replacement; existing files are backed up under `.codex-memory/.backups/` before replacement.
- Use `--dry-run` before touching important repositories to show exactly what would happen.

## Operating Workflow

When starting work in a repo using this skill:

1. Run `git pull` or otherwise synchronize the repository.
2. Read `AGENTS.md`.
3. Read `.codex-memory/CURRENT_WORK.md`, `.codex-memory/CURRENT_WORK.codex.md`, `.codex-memory/HANDOFF.md`, and `.codex-memory/TASK_LOG.md`.
4. Summarize active owners, locked files, risks, and the next safe action.
5. Before editing, check whether the intended files appear under active `Files locked`.
6. If there is a collision, stop and ask for a coordination decision.

When ending work:

1. Summarize what changed and why.
2. Update `.codex-memory/CURRENT_WORK.md`.
3. Append to `.codex-memory/TASK_LOG.md`.
4. Update `.codex-memory/HANDOFF.md` if another person or thread may continue.
5. Update `.codex-memory/DEPLOYMENT.md` after production deploys.
6. Run relevant tests or record why tests were not run.
7. Commit and push memory updates together with the code changes when appropriate.

## Handoff Rules

Use `HANDOFF.md` for any work that crosses a person, computer, day, or Codex thread. Include:

- owner and branch
- current state
- files touched
- files locked
- decisions made
- tests run
- known risks
- exact next step

For same-computer thread switching, still use the same handoff file. A new thread must reload from files, not from assumptions about previous chats.

## Conflict Rules

If `CURRENT_WORK.md` says another active task owns or locks a file:

1. Do not edit the file yet.
2. Record the intended change and conflicting owner.
3. Read the latest relevant `TASK_LOG.md` and `HANDOFF.md` entries.
4. Propose a merge or sequencing plan.
5. Continue only after the user confirms.

## References

Load these only when needed:

- `references/team-protocol.md`: detailed Chinese team operating procedure and daily commands.
- `references/templates.md`: canonical templates for every memory file.
- `references/prompts.md`: reusable Chinese prompts for start, stop, handoff, conflict review, and deployment.

## Maintenance

Prefer the initializer for fresh setup. For existing repos, preserve user-written content, create missing files only, and append managed sections only where needed. Keep memory entries short, specific, and timestamped. Remove stale file locks when tasks complete.
