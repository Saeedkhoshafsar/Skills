---
name: code-review
description: >
  Local code review before merge/release — works without GitHub. Reviews the
  diff across five axes: correctness, readability, security-smells, tests, and
  plan conformance (Files/Accept from PLAN.md). Outputs a verdict with
  prioritized findings. Use at the end of a phase, before merging a branch,
  or when the user says "review" / "بازبینی".
allowed-tools: Read, Grep, Glob, Bash
---

# Code Review (local, no GitHub required)

**Philosophy:** review the DIFF, not the whole repo. Small scope = deep review.
**Output is always:** a verdict (APPROVE / REQUEST CHANGES) + findings sorted by severity.

## Execution Cycle

### Step 1 — Scope the diff
```bash
git diff main...HEAD --stat     # what changed
git diff main...HEAD            # the actual diff (or the phase's commits)
```
- Also load the related tasks from `docs/PLAN.md` (Files / Accept) and `docs/STATE.md`.

### Step 2 — Review across 5 axes

| # | Axis | What to check |
|---|---|---|
| 1 | Correctness | Logic errors, edge cases (empty/null/huge input), off-by-one, error handling |
| 2 | Readability | Naming, dead code, duplication (DRY), functions doing too much |
| 3 | Security smells | Hardcoded values/secrets, unvalidated input, silenced errors (fast pass — full audit is `security-check`'s job) |
| 4 | Tests | Does every changed behavior have a test? Do tests assert real behavior, not implementation details? |
| 5 | Plan conformance | Only declared Files touched? All Accept criteria met? Out-of-scope changes recorded as debt? |

### Step 3 — Classify findings

| Severity | Meaning | Effect |
|---|---|---|
| BLOCKER | Bug, security smell, broken Accept criterion | REQUEST CHANGES |
| MAJOR | Missing test, significant readability/design issue | fix before merge |
| MINOR | Naming, style, small suggestion | may defer (record as debt) |

### Step 4 — Verdict & record
- Any BLOCKER → REQUEST CHANGES; else APPROVE (MINORs may be deferred).
- Record BLOCKER/MAJOR findings in STATE.md (bug table or tech debt).

## Report Template (mandatory)

```
Code Review — <branch/phase> [date]

Scope: 8 files, +412 / -96

BLOCKER:
  [R1] src/api/user.py:42 — id from user input goes straight into the query -> parameterize

MAJOR:
  [R2] no test for the empty-cart path in checkout()

MINOR:
  [R3] rename `data2` -> `normalized_rows`

Plan conformance: P2-T4 Accept 3/3 met, only declared files touched
VERDICT: REQUEST CHANGES (1 BLOCKER)   |   or: APPROVE
```

## Anti-Patterns

1. **Rubber-stamping** — an APPROVE without reading the diff is worse than no review.
2. **Nitpick flood** — 30 MINOR comments burying 1 BLOCKER. Severity-sort always.
3. **Reviewing the whole repo** — only the diff; old code issues go to tech debt.
4. **Fixing while reviewing** — the reviewer reports; fixes happen after the verdict (step-pilot picks them up).
