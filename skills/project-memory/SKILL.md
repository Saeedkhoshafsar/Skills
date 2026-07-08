---
name: project-memory
description: >
  Zero-dependency persistent project memory — docs/STATE.md holds the current
  task, errors, bugs, decisions, and unfinished work so any agent resumes
  exactly where the last one stopped after any disconnect. Use at the start of
  every session, after every completed task, after every error, and before
  every disconnect-prone long operation.
tools: Read, Write, Edit, Bash
---

# Project Memory (agent continuity)

**Rule 1:** STATE.md is updated in the **same commit** as the code it describes.
**Rule 2:** A freshly connected agent reads `docs/STATE.md` BEFORE doing anything else.

## docs/STATE.md Template

```markdown
# STATE — <project name>

## -> current (active task)
```
Phase     : <current phase>
Task      : P1-T3 - <title> — IN PROGRESS
Progress  : <exactly how far: which file, which function>
Blockers  : <anything blocking? "none" if not>
Branch    : <active branch>
```

## Open errors & bugs
| # | Description | File | Status |
|---|---|---|---|

## Key decisions (why this way?)
- <date> — <decision + one-line reason>

## Completed tasks (newest first)
- P1-T2 - <title> — DONE — <one line: what was built + verify result>
- P1-T1 - ...

## Unfinished / tech debt
- <anything deferred to "later">
```

## When to Update

| Event | Action |
|---|---|
| Session start | READ only — do not modify |
| New task starts | Update `-> current` |
| Mid long task | Update Progress in small increments (disconnect-proof!) |
| Error occurs | Add to bug table — even if solved, record HOW |
| Task completes | Move to completed + verify result + same commit as the code |
| Architecture decision | Add to decisions with the reason |

## File Growth Rule

If STATE.md exceeds ~400 lines: move old tasks to `docs/STATE-archive.md` and
keep only `-> current` + last 10 tasks + open bugs.

## Optional Upgrade: AgentDB

If the project grows and semantic search over history becomes necessary, SMART
adds the `agentdb-memory-patterns` skill — but STATE.md always remains the
source of truth (it is readable with zero tooling).
