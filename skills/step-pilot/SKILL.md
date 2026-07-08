---
name: step-pilot
description: >
  Step-by-step plan executor: splits plan tasks into small testable steps and
  runs each as implement -> test -> verify -> record in STATE.md -> commit.
  No step starts before the previous one passes its gate. Use when executing
  tasks from PLAN.md or when the user says "continue" / "ادامه بده".
tools: Read, Write, Edit, Bash, Glob, Grep
---

# Step Pilot — gated step-by-step execution

**Goal:** the project moves forward in strict order. Every step carries its own test and check.
Pattern (from CTB): atomic task + Accept + Verify + STATE.md record in the same commit.

## Cycle Per Step

### Step 0 — Load context
- `docs/STATE.md` → which task is `-> current`?
- `docs/PLAN.md` → that task's Files / Accept / Verify.

### Step 1 — Split (only if the task is bigger than one session)
- Break into sub-steps of ≤30 minutes, each with a visible output.

### Step 2 — Implement the sub-step
- Touch ONLY the files declared in the task. Out-of-scope work = record as tech debt.

### Step 3 — Test THIS sub-step (not at the end!)
- Write/run unit or integration tests for this change.
- Run the task's Verify command.

### Step 4 — Gate
| Verify result | Action |
|---|---|
| GREEN | Go to Step 5 |
| RED | Record the error in STATE.md → fix → back to Step 3 |
| RED 3 times in a row | Activate `debug-detective` (systematic debugging — do NOT thrash) |

### Step 5 — Record & commit
- Update STATE.md (progress or done) — in the SAME commit.
- `git commit -m "P<x>-T<y>: <what happened>"`

### Step 6 — Next?
- Task done → move `-> current` to the next plan task.
- Phase done → invoke SMART (the next phase may need new skills).

## Strict Rules

1. **One step at a time** — never two open tasks in parallel.
2. **No green Verify → no "DONE" commit** — at most a WIP commit recorded in STATE.md.
3. **Every error gets recorded**, even if solved in 30 seconds — the next agent must not hit it again.
4. **Disconnect mid-step?** The next agent knows exactly where we were, thanks to fine-grained Progress updates.
5. **The plan is not sacred** — if a task turns out to be wrongly defined, fix PLAN.md first (record the decision in STATE.md), then continue.

## End-of-Step Report Template

```
Step Pilot — P1-T3 done
  Built    : <files>
  Verify   : <command> -> GREEN (X tests)
  Recorded : STATE.md updated + commit <hash>
  Next     : P1-T4 - <title>
```
