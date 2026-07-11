---
name: step-pilot
description: >
  Evidence-gated step-by-step plan executor. Refuses execution until Vision Lock
  and the plan are approved, runs one atomic task through scope check, implementation,
  tests, acceptance verification, memory consolidation, and commit, and enters
  recovery instead of thrashing after repeated failure. Use for approved PLAN.md
  tasks or when the user says "continue" / "ادامه بده".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Step Pilot — One Approved, Verified Step at a Time

**Goal:** advance the confirmed product vision through the smallest plan step that
produces fresh evidence. Speed never overrides scope, safety, or truth.

## Entry gate — refuse unsafe execution

Before touching code, read:

1. `docs/STATE.md` resume packet and epistemic delta.
2. `docs/PROJECT-BRIEF.md` Vision Lock and relevant outcome/non-goals.
3. Current task in `docs/PLAN.md`: Why now, dependencies, files, acceptance, verify,
   evidence path, and rollback.
4. Linked decisions and open risks.
5. Git status and current task files/tests.

Execution is blocked when any is true:

- Vision Lock is not explicitly `CONFIRMED`;
- plan or current task is absent/unapproved;
- a critical unknown/expired assumption can invalidate this task;
- dependency evidence is missing;
- task has no measurable acceptance or executable verification;
- working-tree changes overlap scope and their ownership is unknown.

On a blocked gate, do not improvise. Update STATE with the blocker and invoke SMART in
DISCOVERY, PLANNING, or RECOVERY mode.

## Cycle per task

### 1. Restate the contract

Summarize before implementation:

```text
Task / intended user outcome | why now | in-scope files | non-goals
acceptance evidence | verify command | rollback | active assumptions/risks
```

If the contract no longer supports the brief or new evidence changes it, revise and
approve the brief/decision/plan first. The plan is a controlled hypothesis, not scripture.

### 2. Split only when necessary

If the task is larger than one working session, split it into ordered sub-steps of
roughly 30 minutes or less. Each sub-step must have a visible checkpoint and leave the
repository coherent. Keep one task active; do not create parallel hidden work.

### 3. Establish evidence before change

- Reproduce current behavior or run the narrow baseline check.
- For behavior changes, add or identify the test that would fail before the change.
- Capture environment/version details when they affect reproducibility.
- Record exact progress before disconnect-prone or destructive operations.

### 4. Implement the minimum scoped change

- Touch only declared files unless a discovered dependency requires a plan amendment.
- Preserve user work and unrelated changes.
- Prefer reversible choices and feature flags for high-risk behavior.
- Do not add speculative abstractions or future features.
- Record out-of-scope findings with measurable activation triggers; do not fix them now.

### 5. Verify in layers

Run fresh checks in this order where applicable:

1. narrow test for changed behavior;
2. regression/integration checks for affected boundaries;
3. task's exact Verify command;
4. acceptance check from the user's perspective;
5. security/privacy/accessibility/performance check when the task risk calls for it.

A command that was green before the change is not completion evidence unless rerun.
“Looks good” and model confidence are never verification.

### 6. Evidence gate

| Result | Action |
|---|---|
| GREEN and acceptance met | consolidate and complete |
| RED with discriminating evidence | record exact failure/hypothesis; make one minimal fix; rerun |
| same symptom RED 3 times | stop changes; set SMART mode RECOVERY; invoke `debug-detective` |
| new scope/vision conflict | stop; invoke SMART to revise approved records |
| safety/security critical finding | stop and escalate; never waive silently |

Do not count repeated commands with no meaningful diagnostic change as separate attempts;
they are thrashing and trigger recovery immediately.

### 7. Consolidate durable memory

In the same change set:

- update STATE exact progress, fresh evidence, blockers/errors, and one NEXT action;
- add a meaningful change-ledger entry explaining what and why;
- resolve, invalidate, or extend assumptions only with evidence;
- update decisions/brief/plan only if their canonical truth changed;
- record installed/created capability results where relevant.

Do not paste logs or chat transcripts. Preserve concise evidence and paths.

### 8. Commit truthfully

Before commit:

```text
[ ] scope matches approved task and non-goals
[ ] dependencies and acceptance are satisfied
[ ] fresh Verify is GREEN
[ ] rollback/recovery remains possible where required
[ ] STATE and canonical records match repository reality
[ ] no secret or unnecessary personal data entered memory/git
```

Then commit using `P<phase>-T<number>: <observable outcome>`. If verification remains
red, never claim DONE; create a clearly labelled checkpoint only when policy requires
preserving work, with the blocker in STATE.

### 9. Select the next action

- Task done: move STATE to the next dependency-ready task from the approved plan.
- Phase done: invoke SMART; the mode and capability needs may change.
- New evidence changes product intent/scope: invoke SMART before the next task.
- Release candidate: invoke SMART RELEASE mode; `security-check` is mandatory.

## End-of-step report

```text
Step Pilot — <task> <DONE/BLOCKED/RECOVERY>
Outcome   : <observable user/project result>
Changed   : <files / behavior>
Evidence  : <fresh command> -> <GREEN/RED> (<time/result>)
Scope     : <matched / approved amendment link>
Memory    : <records updated>
Commit    : <hash, or why none>
Risk      : <remaining material risk/assumption>
Next      : <single next best action>
```

## Anti-patterns

Never:

- execute a task before Vision Lock and plan approval;
- silently turn an inference into scope;
- work on two tasks at once;
- fix unrelated debt “while here”;
- retry the same failing idea without a new diagnostic;
- edit PLAN to make completed work appear compliant;
- claim DONE from stale, partial, or subjective evidence;
- defer security/privacy/operations automatically to the final phase;
- leave STATE saying something different from git/tests.
