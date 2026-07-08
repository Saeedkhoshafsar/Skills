---
name: debug-detective
description: >
  Systematic debugging method: reproduce -> isolate -> hypothesize -> minimal
  fix -> regression test -> record root cause in STATE.md. Stops agents from
  thrashing in error loops. Use when a bug appears, a test keeps failing,
  step-pilot hits 3 consecutive red verifies, or the user says
  "bug" / "error" / "debug" / "باگ" / "ارور" / "درست نمیشه".
tools: Read, Grep, Glob, Bash, Edit, Write
---

# Debug Detective

**Philosophy:** don't "solve" the bug — UNDERSTAND it first. A fix without understanding = a returning bug.
**Golden rule:** never change more than 2 things at once to test one hypothesis.

## Execution Cycle (in order — skip nothing)

### Step 1 — Reproduce
- Find the smallest command that shows the bug.
- Can't reproduce? Gather more info (env, input, versions).
- Record the reproduction command in STATE.md's bug table.

### Step 2 — Isolate
- Read the EXACT error — the whole stack trace, not just line 1.
- Check `git log`/`git diff`: what was the last related change?
- Binary-search the scope: this half or that half?
- Narrow down to the smallest guilty file/function/line.

### Step 3 — Hypothesize
- Write it explicitly: "I think X is broken because Y."
- Decide how to confirm/refute BEFORE changing code (log, test, breakpoint).
- Hypothesis refuted? → next hypothesis. Do NOT start plowing through the code.

### Step 4 — Minimal fix
- Fix ONLY the root cause — never the symptom (no symptom patching).
- Change ≤ a few lines; refactoring is separate from fixing (record as tech debt).
- Never an empty try/except or silencing the error instead of fixing it.

### Step 5 — Prove (regression test)
- Write a test that is RED before the fix and GREEN after.
- Run the whole test suite — the fix must not break anything else.
- Re-run the Step 1 reproduction command → must be clean.

### Step 6 — Record & close
- STATE.md: bug → "solved" + root cause + solution (one line).
- Commit: `fix(scope): <root cause> — <solution>`.
- Recurring pattern? → add it to STATE.md's "Key decisions".

## Isolation Toolbox

| Situation | Technique |
|---|---|
| Don't know WHEN it broke | `git bisect` or review `git log --oneline -20` |
| Don't know WHERE it breaks | Checkpoint logging (input/output at each stage) |
| Only broken in production | Env diff: versions, ENV vars, data |
| Flaky (sometimes breaks) | Run in a x20 loop + record failure conditions (timing/race?) |
| Cryptic third-party error | Exact package version + search the exact error text |

## Anti-Patterns

1. **Shotgun debugging** — changing 5 places at once hoping something works.
2. **Symptom fix** — e.g. `if x is None: return` without understanding why x became None.
3. **Deleting the red test** instead of fixing the code.
4. **Unbounded debugging** — after 3 failed hypotheses: STOP + full report to the user (findings + refuted hypotheses).
5. **Not recording** — an unrecorded solved bug = a bug the next agent hits again.

## Closing Report Template

```
Debug Detective — bug #N closed
  Symptom : <what was observed>
  Root    : <the real cause — precise: file:line>
  Fix     : <what changed, how many lines>
  Proof   : test <name> (was RED -> now GREEN) + full suite GREEN
  Record  : STATE.md updated + commit <hash>
```
