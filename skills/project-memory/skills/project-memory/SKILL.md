---
name: project-memory
description: >
  Durable, low-noise project intelligence for continuity across sessions. Owns the
  atomic Project Mind network (docs/PROJECT-MIND.md) that captures the user's
  intended product inch by inch, maintains a compact resume index in docs/STATE.md,
  and coordinates the canonical Project Brief, Plan, Decisions, and Research records
  so facts, assumptions, changes, errors, capability inventory, and future runway
  remain reconstructable without rescanning the whole project. Use at session start
  and every meaningful work event.
allowed-tools: Read, Write, Edit, Bash
---

# Project Memory — Durable Truth, Not a Chat Log

The memory system must let a newly connected agent answer, within minutes:

1. What is this project trying to achieve and for whom?
2. What is confirmed, assumed, unknown, or conflicting?
3. What mode/task is active and exactly how far did work progress?
4. What changed, why, and what evidence supports it?
5. What capabilities are available and when should they be used?
6. What are the next three actions and what blocks them?

## Invariants

1. `docs/STATE.md` is the compact resume index and current operational truth.
2. Product truth lives in `docs/PROJECT-BRIEF.md`; execution truth in `docs/PLAN.md`;
   decisions in `docs/DECISIONS.md`; sourced claims in `docs/RESEARCH.md`.
3. Never duplicate a full plan, brief, or transcript into STATE. Link to canonical sections.
4. Label material statements `KNOWN`, `INFERRED`, `ASSUMED`, `UNKNOWN`, or `CONFLICT`.
5. Memory records evidence and provenance, not model confidence theater.
6. Update memory in the same commit as the work it describes.
7. Never mark DONE without fresh verification evidence.
8. Never erase a contradicted decision; mark it superseded and link its replacement.
9. Keep sensitive values and secrets out of memory files. Record secret names/locations,
   never credentials or personal data that is not required.

## Canonical record map

| Record | Contains | Does not contain |
|---|---|---|
| `PROJECT-MIND.md` | the atomic mind network: addressable nodes for every material product fact, linked into one navigable model of the user's intended final result | narrative prose, implementation history, duplicated plan content |
| `PROJECT-BRIEF.md` | intent, people, final experience, scope, constraints, success, epistemic map, Vision Lock | implementation task history |
| `PLAN.md` | milestones, dependencies, atomic tasks, acceptance, verify, rollback | daily progress narrative |
| `STATE.md` | resume packet, current objective/task, exact progress, blockers, latest deltas, capability inventory, runway | full requirements or chat transcript |
| `DECISIONS.md` | consequential choices, options, rationale, evidence, consequences, reversal trigger | trivial edits |
| `RESEARCH.md` | sourced external claims, dates, confidence, applicability, open verification | unsourced user preferences |

Use existing equivalent files instead of creating parallel records. Create a file only
when it has real content.

## Project Mind — the atomic mental network

`docs/PROJECT-MIND.md` is the engineered replica of the user's mind about the product:
what it is, for whom, how it behaves in every material situation, and what the final
result looks like — inch by inch. It exists so that a resuming agent never faces an
unanswered product question mid-development and the project can never drift toward
“start now, figure it out later.”

### Node rules (atomic like a real mind)

1. **One node = one atomic, testable statement.** If a node contains “and”, consider
   splitting it. A node that cannot be confirmed or falsified is not a node.
2. **Every node is addressable:** `M-<domain>-<number>` (e.g. `M-EXP-04`).
3. **Every node carries:** epistemic label (`KNOWN/INFERRED/ASSUMED/UNKNOWN/CONFLICT`),
   source (user statement date / evidence / decision ID), and links to related nodes.
4. **Links are typed:** `requires`, `refines`, `conflicts`, `serves`, `constrains`.
   A plan task references the node IDs it implements; a decision references the nodes
   it settles.
5. **The network stays current:** when the user corrects the picture, the node is
   updated (or superseded with a link), never silently rewritten.
6. **Size follows the project.** A small tool may need 20 nodes; a platform may need
   hundreds. Empty domains are omitted — the mind network is never bureaucracy.

### Domain skeleton

```markdown
# PROJECT MIND — <project name>
> Atomic network of the intended product. Every material question about
> “what are we building and why” must be answerable from a node here.

## INT — Intent & Why            (M-INT-*)
## PPL — People & Stakeholders   (M-PPL-*)
## EXP — Final Experience        (M-EXP-*)  # journeys, states, failure/recovery moments
## SCP — Scope & Non-goals       (M-SCP-*)
## BEH — Behavior & Rules        (M-BEH-*)  # domain rules, edge cases, permissions
## DAT — Data & Content          (M-DAT-*)  # entities, lifecycle, sensitivity
## IFC — Interfaces & Integrations (M-IFC-*)
## QLT — Quality & Constraints   (M-QLT-*)  # performance, reliability, compliance
## RSK — Risks & Misuse          (M-RSK-*)
## SUC — Success & Evidence      (M-SUC-*)
## EVO — Evolution               (M-EVO-*)  # plausible futures, deliberate deferrals

Node format:
- `M-EXP-04` [KNOWN — user 2026-07-11] When payment fails, the user sees the exact
  reason and a retry path; the order is never silently lost.
  links: serves M-INT-01, requires M-IFC-02, constrains M-BEH-07
```

### Completeness gate (feeds Vision Lock)

Before Vision Lock, the mind network must pass a coverage sweep:

- every domain relevant to this project has nodes or an explicit `not applicable`;
- no `UNKNOWN` or `CONFLICT` node remains on a critical path (intent, primary user,
  final experience, scope boundary, sensitive data, safety/legal, success evidence);
- every `ASSUMED` node has an owner, validation test, and expiry trigger;
- every planned milestone can point to the node IDs it realizes — a milestone with no
  nodes is fantasy; nodes with no milestone are conscious deferrals in `EVO`.

The sweep result is recorded in STATE (`Mind coverage: COMPLETE <date> / GAPS: <ids>`).
Planning or code with open critical gaps is forbidden.

## Session-start read protocol

Read in this order:

1. `docs/STATE.md` completely.
2. Only the brief/plan/decision/research sections referenced by the current objective.
3. `git status`, recent relevant commits, and the current task's files/tests.
4. If STATE conflicts with repository evidence, mark a `CONFLICT` and enter recovery;
   repository evidence does not automatically reveal user intent.

Do not modify memory merely because a session started.

## `docs/STATE.md` template

```markdown
# STATE — <project name>

> Resume index. Canonical product: [PROJECT-BRIEF.md](PROJECT-BRIEF.md) |
> execution: [PLAN.md](PLAN.md) | decisions: [DECISIONS.md](DECISIONS.md) |
> evidence: [RESEARCH.md](RESEARCH.md)

## Resume packet
| Field | Current value |
|---|---|
| SMART mode / lifecycle phase | <DISCOVERY / 0> |
| Current objective | <one observable outcome> |
| Active task | <P1-T3 — title — IN PROGRESS, or none> |
| Exact progress | <file/function/checkpoint; what is complete and not complete> |
| Last evidence | `<command>` -> GREEN/RED at <time>, or user confirmation/source |
| Blocker / waiting on | <one precise item or none> |
| Vision Lock | NOT READY / READY FOR CONFIRMATION / CONFIRMED <date> |
| Mind coverage | NOT BUILT / GAPS: <node IDs> / COMPLETE <date> |
| Machine gates | Vision `<artifact/check>`; Verify `<artifact/check>`; Release `<artifact/check or N/A>` |
| Branch / head | <branch / short hash> |

## Epistemic delta
### Newly confirmed
- <fact> — source: <user/file/test/date>
### Inferred — confirmation needed
- <interpretation> — changes decision: <which one>
### Active assumptions
| Assumption | Why temporary | Validation test | Owner | Expiry/reversal trigger |
|---|---|---|---|---|
### Unknowns / conflicts
| Item | Impact if wrong | Resolution action | Status |
|---|---|---|---|

## Capability inventory
| Capability | Type/source | Status | Invoked when | Last result / review |
|---|---|---|---|---|

## Open errors and risks
| ID | Description | Evidence / location | Impact | Next diagnostic/mitigation | Status |
|---|---|---|---|---|---|

## Meaningful change ledger (newest first; keep latest 10)
| Date / commit | What changed | Why | Evidence | Records affected |
|---|---|---|---|---|

## Runway
1. **NEXT:** <single next best action + completion evidence>
2. **THEN:** <dependent action>
3. **LATER:** <next milestone action>

## Deferred / debt with activation triggers
- <item> — do when <measurable trigger>, not merely “later”
```

## Event-driven update protocol

| Event | Required memory delta |
|---|---|
| reliable discovery answer | add/update the atomic mind node(s); update brief; add only changed truth to Epistemic delta |
| user corrects the picture | update or supersede the affected mind nodes and their links; never leave a stale node |
| Vision Playback confirmation | brief Vision Lock + STATE status + `.smart/evidence/vision-lock.json` produced by `smart-gates.py` |
| temporary assumption | assumption, owner, validation test, expiry/reversal trigger |
| material decision | append decision record; link concise consequence from STATE |
| task starts | current objective/task, exact starting point, expected evidence |
| meaningful checkpoint | exact progress and changed runway; no premature DONE |
| mid-mission continuity trigger | write STATE immediately when files, evidence, mode/task, blocker, decision, capability, or runway changed — before more work |
| error/failing check | exact command/input/output summary, attempt count, next diagnostic |
| task completion | GREEN `.smart/evidence/verify.json`, command/result/time, completed ledger entry, next task |
| scope/plan change | brief/plan/decision first, then STATE pointer and impact |
| capability installed/created | inventory trigger, source/type, supply-chain/eval status |
| before risky/long operation | checkpoint exact progress and rollback/recovery instruction |
| phase/mode change | reason/evidence, new objective, refreshed runway |
| release readiness | READY `.smart/evidence/release.json`, evidence paths/checksums, approver, rollback |
| intentional handoff / context pressure | complete resume packet + single NEXT action; conversation history is not recovery media |

“Meaningful” means the event changes understanding, decisions, progress, risk, or what
the next agent should do. Do not record formatting-only edits as product events.

### Mid-mission checkpoint rule

Do not wait for task completion to write continuity. As soon as a meaningful delta
exists, update the resume packet fields that changed:

1. mode / active task;
2. exact progress (what is done vs not done);
3. last evidence command and GREEN/RED result;
4. blocker or waiting-on item;
5. single NEXT action.

A later session with no chat history must be able to continue from STATE alone.
If `smart-gates.py memory resume-check` fails, repair the packet before coding.

## Decision record protocol

Append to `docs/DECISIONS.md`:

```markdown
## D-<NNN> — <decision> — <PROPOSED/ACCEPTED/SUPERSEDED>
- Date / owner:
- Context and decision pressure:
- Epistemic status: KNOWN / ASSUMED / ...
- Options considered:
- Choice and rationale:
- Evidence:
- Consequences and risks:
- Reversal / review trigger:
- Supersedes / superseded by:
```

Create a decision record when a choice affects product scope, architecture, data,
security/privacy, cost, schedule, operations, or multiple future tasks. Do not create
one for routine implementation details already clear from the plan.

## Error memory and anti-thrashing

Record enough to prevent repeating a failed path:

- exact failing command, test, input, and concise output;
- environment and relevant versions;
- attempted hypotheses and what each result ruled out;
- next discriminating diagnostic, not a random next fix;
- regression test and root cause once solved.

After three failed verification attempts on the same symptom, mark RECOVERY and invoke
`debug-detective`. Preserve all three outcomes.

## Capability memory

The capability inventory distinguishes:

- **installed:** present but not necessarily relevant now;
- **active:** selected for the current decision/action;
- **created-pending-eval:** custom skill not safe to rely on yet;
- **verified:** supply-chain review or custom evaluations passed;
- **retired/quarantined:** no longer used, with reason.

For a custom skill, record its contract location, evaluation result, trigger/non-trigger,
and owner. Never let capability presence silently become permission to invoke it.

## Consolidation and archive

Before ending a meaningful invocation:

1. Reconcile STATE with git and fresh verification evidence.
2. Remove stale `NEXT` entries and ensure only one item is NEXT.
3. Move settled inferences to confirmed, or rejected ones to the change ledger.
4. Mark expired assumptions and force their resolution before dependent irreversible work.
5. Keep latest 10 meaningful changes and completed tasks in STATE.
6. When STATE exceeds about 300 lines, move older history to
   `docs/archive/STATE-YYYY-MM.md`; preserve links and decision IDs.
7. Ensure the next agent can act without reconstructing private chain-of-thought.
   Store conclusions, evidence, and rationale—not hidden reasoning traces.

## Commit rule

Memory and the work it describes belong in one commit. Before committing, verify:

```text
[ ] canonical record updated, not duplicated
[ ] epistemic labels reflect evidence
[ ] exact progress and latest verify result are current
[ ] assumptions have tests/triggers
[ ] one NEXT action and up to two follow-ons exist
[ ] no secrets or unnecessary personal data were written
```
