# Codex Memory Sync Templates

## AGENTS.md managed block

When adding this block to an existing `AGENTS.md`, append it without deleting the user's existing instructions. Back up `AGENTS.md` before appending.

```markdown
<!-- BEGIN CODEX MEMORY SYNC -->
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
<!-- END CODEX MEMORY SYNC -->
```

## CURRENT_WORK.md

```markdown
# Current Work

Last updated: YYYY-MM-DD HH:mm timezone
Updated by: name / codex-thread

## Active Tasks

### 1. Task title

Status: pending | in_progress | blocked | review | done
Owner: name
Branch: branch-name

Files touched:
- path/to/file

Files locked:
- path/to/file-or-glob

Current state:
- Short factual state.

Next step:
- Exact next action.

Blockers:
- None.

## Conflicts

- None.
```

## CURRENT_WORK.codex.md

```markdown
# Codex Quick Context

Read this before editing.

## Must Know

- This repo uses Git as code source of truth.
- Memory source of truth is `.codex-memory/`.
- Use `scripts/memory_sync.py sync --thread <thread-id>` before editing.
- Do not rely on previous chat history.
- After editing: use `scripts/memory_sync.py commit`.

## Current Warnings

- No active warnings yet.
```

## MEMORY_COMMITS.jsonl record

Each line is one JSON object:

```json
{
  "id": "mem-abc123",
  "sequence": 12,
  "time": "2026-05-20T13:00:00+08:00",
  "actor": "user-a",
  "thread": "thread-a",
  "purpose": "work",
  "summary": "Finished login refresh flow",
  "branch": "codex/login",
  "git_commit": "abc1234",
  "files": [
    {
      "path": ".codex-memory/THREADS/thread-a.md",
      "heading": "2026-05-20 - Finished login refresh flow",
      "entry_number": 3,
      "start_line": 42,
      "end_line": 78
    }
  ],
  "related_files": ["app/auth.ts"]
}
```

## HANDOFF.md

```markdown
# Handoff

## Task title

Owner: name
Branch: branch-name
Last updated: YYYY-MM-DD HH:mm timezone

Context:
- Why this task exists.

What changed:
- Concrete changes.

Why:
- Decision rationale.

Files touched:
- path/to/file

Files locked:
- path/to/file-or-glob

Tests:
- command: result

Known risks:
- Risk or none.

Next step:
- Exact next action.
```

## TASK_LOG.md

```markdown
# Task Log

## YYYY-MM-DD HH:mm - owner / codex thread

Branch: branch-name

Changed:
- Change summary.

Files:
- path/to/file

Tests:
- command: result

Risks:
- Risk or none.

Next:
- Exact next action.
```

## DECISIONS.md

```markdown
# Decisions

## YYYY-MM-DD - Decision title

Decision:
- What was decided.

Reason:
- Why.

Alternatives considered:
- Option and tradeoff.

Impact:
- Files, modules, or workflows affected.
```

## RISKS.md

```markdown
# Risks

## Active Risks

### Risk title

Owner: name
Severity: low | medium | high
Status: open | mitigated | accepted

Description:
- What can go wrong.

Mitigation:
- What to do.
```

## DEPLOYMENT.md

```markdown
# Deployment

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
```
