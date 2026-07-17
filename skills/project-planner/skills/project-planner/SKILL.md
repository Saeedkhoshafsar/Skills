---
name: project-planner
description: >
  Evidence-aware project discovery and planning for non-expert idea owners. Builds
  a confirmed final-product picture through an adaptive interview, separates facts
  from assumptions, assesses viability and risk, and only after Vision Lock creates
  an atomic, verifiable execution plan. Use for new ideas, unclear requirements,
  scope changes, roadmaps, or when the user asks for a plan / "پلن".
allowed-tools: Read, Glob, Grep, Bash, Write
---

# Project Planner — From Idea to Confirmed Execution Model

**Outputs:**

- `docs/PROJECT-MIND.md` — the atomic mind network of the intended product (node
  protocol in `project-memory`), grown with every reliable discovery answer.
- `docs/PROJECT-BRIEF.md` — the confirmed product model and uncertainty map.
- `docs/PLAN.md` — an ordered, risk-aware execution plan created only after Vision Lock.

The user may know the desired change but not product, technical, legal, or delivery
terminology. Ask in plain language, perform the expert translation, and show it back
for correction. Never mistake fluent synthesis for user confirmation.

## Stage 0 — Load before asking

Read existing STATE, brief, plan, decisions, research, README, manifests, and relevant
code. Build a question ledger:

```text
Settled facts | Inferences awaiting confirmation | Assumptions | Unknowns | Conflicts
```

Do not ask for information already present. If code and stated intent conflict, surface
the conflict rather than silently treating code as truth.

## Stage 1 — Adaptive discovery

Cover the dimensions below, but do **not** ask a fixed questionnaire. At each turn ask
only 1–3 questions with the highest decision impact and uncertainty.

| Dimension | What must become clear | Example plain-language prompt |
|---|---|---|
| Intent | personal/business reason and desired change | “If this succeeds, what becomes meaningfully better?” |
| Problem | pain, frequency, severity, current workaround | “What happens today when this problem appears?” |
| People | primary user, buyer, operator, affected parties | “Who feels the pain, and who decides to use or pay?” |
| Outcome | job-to-be-done, not a feature list | “What can the user accomplish at the end?” |
| Final experience | trigger-to-success journey and recovery | “Walk me through one successful use from start to finish.” |
| Value | alternative and reason to switch/trust | “Why would they choose this over what they do now?” |
| Scope | must-haves, non-goals, MVP learning objective | “What is the smallest version that proves the idea?” |
| Reality | time, budget, assets, skills, platform, data | “What limits are real today?” |
| Viability | acquisition, economics, support, ownership | “How will the first ten real users find and keep using it?” |
| Risk | privacy, safety, misuse, regulation, dependency | “What data or harm would be unacceptable?” |
| Success | observable outcome and guardrail | “What evidence would convince you it works?” |
| Future | likely evolution without fantasy scaling | “If the first version succeeds, what changes next?” |

### Question policy

1. Resolve contradictions and safety-critical unknowns first.
2. Explain in one sentence why an answer affects the project.
3. Offer examples/options and “I don't know” when abstraction is difficult.
4. Reflect the answer as `KNOWN` or `INFERRED`; ask for correction where material.
5. Write every reliable answer into the mind network as atomic node(s) in the same
   turn; an answer that never becomes a node is lost to the next session.
5. When the user does not know, propose a reversible assumption plus a validation test.
6. Do not ask implementation questions before they are decision-relevant.
7. Stop interviewing when additional answers no longer change the next product decision.

Use research or a relevant specialist capability when a domain fact cannot be learned
from the user. Record sourced claims, date, and confidence in `docs/RESEARCH.md`.

## Stage 1.5 — Landscape research (before Vision Lock)

Humans rarely know the full landscape at the start. After the idea is understandable
(Intent / Problem / People / Outcome are at least `INFERRED`), and **before** Vision
Lock, run a **decision-changing landscape pass**. This is a SMART protocol, not a
multi-agent company simulation and not a MetaGPT runtime.

### When it is mandatory

Run Stage 1.5 when **any** of these hold:

- the product is new (no existing competitors already documented in RESEARCH/mind);
- the user asks for “best quality for my budget”, market fit, or “is this already solved?”;
- stack/API/vendor choices would be expensive or hard to reverse;
- a public similar project (GitHub / SaaS / open-source) could replace most of the build.

Skip or keep tiny only for pure internal scripts, one-off personal tools, or when STATE
already has a fresh landscape section with sources.

### What to research (minimum useful set)

| Lens | Question | Where it lands |
|---|---|---|
| Similar products / competitors | Who already solves this? Pros, cons, pricing signal | `docs/RESEARCH.md` + mind `M-INT` / `M-SCP` / Value |
| Public repos / open source | Is there a maintained project that is “our product already”? | `docs/RESEARCH.md` + decision: reuse / fork / build |
| Substitutes | What do users do today if we never ship? | Brief Value + mind |
| Cost of quality | API, infra, compliance, and time cost of “best” options | Constraints + DECISIONS |
| Differentiation | Why would someone switch to us? | Brief Value; never invent without evidence |

### Method (evidence over ceremony)

1. Form 2–4 search queries from the problem + audience + category (not from a fantasy brand).
2. Prefer multi-source host research (`/deep-research` when decision-changing) and/or
   targeted web/`gh` repository search for similar public projects.
3. Read sources enough to extract **claims with URL + date + confidence**; do not dump
   raw pages into the mind.
4. Promote only decision-changing findings into Project Mind nodes (`KNOWN`/`INFERRED`)
   and leave bulk notes in `docs/RESEARCH.md`.
5. Stop when further browsing no longer changes scope, build-vs-buy, budget, or success
   criteria. Landscape research is not infinite market theater.

### Budget × quality bar (same stage)

“Best” means **best within real constraints**, not maximum spend or maximum process.

Capture in Brief **Constraints and assets** and mind `M-QLT-*` / `M-SCP-*`:

| Input | Must become explicit |
|---|---|
| Money budget | monthly/one-time cap; paid APIs allowed or not |
| Time budget | calendar deadline or hours available |
| Skill budget | what the team can operate after ship |
| Quality floor | what must never be amateur (security, data loss, core journey) |
| Quality ceiling | what is overkill for this size (enterprise process on a weekend MVP) |

Rules:

- A free project can still use expensive **your** time/API quota — count that cost.
- Prefer reversible, cheaper validation before irreversible paid commitments.
- Excellence-by-default still applies: expert structure and verification stay on; luxury
  architecture and unused specialist packs stay off.
- Record the chosen quality tier as a decision when options materially differ
  (e.g. managed auth vs custom, hosted search vs DIY).

### Research record shape (`docs/RESEARCH.md`)

```markdown
## <topic> — <date>
- Claim:
- Source URL(s):
- Confidence: HIGH / MEDIUM / LOW
- Applies to decision:
- Implication for us:
- Open verification:
```

Also keep a short **Landscape snapshot** in the Brief (5–7 bullets max): top alternatives,
reuse candidates, and the differentiation hypothesis.

## Stage 2 — Build the Project Brief incrementally

Create or update `docs/PROJECT-BRIEF.md` after reliable facts emerge:

```markdown
# <Project> — Project Brief

## One-sentence intent
For <primary user> in <situation>, enable <meaningful outcome> through <core mechanism>.

## Why this should exist
- Problem and current workaround:
- User impact:
- Value / differentiation hypothesis:

## People and stakeholders
| Role | Need / responsibility | Evidence | Confidence |
|---|---|---|---|

## Final product picture
### Day-in-the-life
<concrete narrative before, during, and after use>
### Core journey
1. Trigger -> 2. Entry -> 3. Key action -> 4. Outcome -> 5. Failure/recovery

## Scope
### Must deliver outcomes
### Explicit non-goals
### MVP learning objective

## Constraints and assets
| Item | Type | Effect | Status |
|---|---|---|---|

## Success and guardrails
| Measure | Baseline | Target / signal | How measured |
|---|---|---|---|

## Risk and responsibility
| Risk | Who/what is affected | Mitigation / validation | Owner |
|---|---|---|---|

## Epistemic map
### Confirmed
### Inferred — awaiting confirmation
### Time-boxed assumptions — test + expiry
### Unknowns that can change decisions
### Conflicts

## Vision Lock
Status: NOT READY / READY FOR CONFIRMATION / CONFIRMED
Confirmed by / date:
```

Keep it concise and decision-useful. This is a living model, not a requirements dump.

## Stage 3 — Viability and risk review

Before proposing a build, inspect the idea through only the relevant lenses:

- **Desirability:** real user/problem evidence and adoption friction.
- **Feasibility:** technology, data, integration, team, and operations.
- **Viability:** value capture, costs, distribution, support, maintenance.
- **Responsibility:** privacy, security, accessibility, safety, legal/compliance, ethics.
- **Landscape:** build vs buy/reuse; competitor and open-source displacement risk
  (Stage 1.5 evidence, not vibes).
- **Budget-fit quality:** can the intended quality floor be met inside money/time/skill
  budgets without silent amateur shortcuts?

For each material risk, choose one: avoid, reduce, transfer/escalate, accept explicitly,
or validate with an experiment. Legal/medical/financial conclusions require qualified
professional review; record jurisdiction and unknowns.

## Stage 4 — Vision Playback and lock

Before sizing or planning, present this in the user's language:

```text
What I believe you mean
- User and situation:
- Problem and present alternative:
- Desired outcome:
- Final experience / core journey:
- Must-haves and non-goals:
- Success evidence:

Confidence map
- Confirmed:
- Inferred — please correct:
- Temporary assumptions:
- Decision-changing unknowns/conflicts:

Is this the product you mean? Please correct it, or explicitly confirm Vision Lock.
```

### Gate conditions

Vision Lock may be `READY FOR CONFIRMATION` only when:

- primary user, problem, outcome, final journey, and scope boundary are coherent;
- failure conditions and non-goals are visible;
- material constraints and sensitive-data/safety/compliance risks are surfaced;
- success evidence and the MVP learning objective are explicit;
- remaining assumptions have a test, owner, and expiry/reversal trigger;
- the Project Mind coverage sweep is COMPLETE: every relevant domain has nodes or an
  explicit `not applicable`, and no critical-path node is `UNKNOWN` or `CONFLICT`;
- **landscape coverage** for a new product is present or explicitly waived with reason:
  at least a short competitive/similar-project pass in `docs/RESEARCH.md` (or STATE note
  “landscape N/A — <reason>”), and build-vs-reuse is not an unexamined `UNKNOWN`;
- **budget × quality** constraints are visible (money/time/skill floor) when the user
  cares about “best” outcomes or paid APIs/infra are likely.

Do not create PLAN.md while status is NOT READY or merely ready for confirmation.
“Let's just start and figure it out as we build” is not an acceptable path past this
gate under any schedule pressure; the correct response is sharper key questions that
close the remaining gaps quickly.
Do not skip landscape research by role-playing a full software company of agents.
SMART remains one orchestrator that may activate **at most a few** specialist
capabilities for live decisions — never a permanent multi-role simulation and
**not a multi-agent company simulation**.
After explicit confirmation, run SMART's `smart-gates.py vision confirm --brief
docs/PROJECT-BRIEF.md --confirmed-by <identity>`. PLAN.md creation is blocked until
`smart-gates.py vision check` passes. Any later Brief edit invalidates the lock and
requires a new playback and confirmation.

## Stage 5 — Size by uncertainty and consequence

After Vision Lock, size the project. Line count is not project size.

| Size | Typical profile | Planning depth |
|---|---|---|
| S | one user/workflow, low-risk, reversible, few integrations | 3–5 layers |
| M | multi-user MVP, auth/data/deployment, moderate operational risk | 6–9 layers |
| L | commercial/regulated/multi-sided, high consequence or scale | all relevant layers, staged gates |

Increase size for sensitive data, payments, regulated decisions, irreversible migration,
complex integrations, offline/real-time constraints, or multi-team ownership.

## Stage 6 — Select only relevant project layers

| # | Layer | Decision covered |
|---|---|---|
| 1 | Experience / Frontend | journey, UI, accessibility |
| 2 | APIs & Domain Logic | rules and service boundaries |
| 3 | Product Data & Storage | model, lifecycle, retention, migration |
| 4 | Identity & Permissions | authentication, authorization, roles |
| 5 | Hosting & Deployment | runtime, environments, release path |
| 6 | Compute & Integrations | jobs, AI, third parties, external failure |
| 7 | CI/CD & Version Control | repeatable quality and delivery |
| 8 | Security & Privacy | threats, secrets, consent, RLS |
| 9 | Abuse & Rate Limits | misuse and cost controls |
| 10 | Performance & Caching | latency and freshness |
| 11 | Scaling & Capacity | measured bottlenecks and growth triggers |
| 12 | Observability & Support | logs, metrics, alerts, user support |
| 13 | Availability & Recovery | backup, restore, rollback, continuity |

Every selected layer must cite the product/constraint reason. Do not add a layer simply
because the project is labelled “serious”. Deferred layers need an activation trigger.

## Stage 7 — Plan by risk and learning

Sequence work as:

1. validation spikes for assumptions that can invalidate the project;
2. foundation and contracts needed by multiple milestones;
3. thin vertical slice proving the core user outcome end-to-end;
4. safety, quality, and operational hardening proportional to risk;
5. release, measurement, and feedback loop;
6. deferred scale features only when their trigger occurs.

Write `docs/PLAN.md`:

```markdown
# <Project> — Execution Plan

> Vision Lock: CONFIRMED on <date>. Brief: docs/PROJECT-BRIEF.md
> Machine evidence: .smart/evidence/vision-lock.json (`vision check` GREEN)

## Outcomes, non-goals, and release gates
## Locked decisions and reversible defaults
## Milestones and dependency map
## Deferred capabilities with activation triggers

## Task ID convention: `P<phase>-T<number>`

### P0-T1 — <atomic outcome>
**Why now:** <risk, dependency, or learning unlocked>
**Realizes:** <mind node IDs, e.g. M-EXP-04, M-BEH-07>
**Depends on:** <IDs or none>
**Files:** <exact files to create/modify>
**Accept:**
- <observable/measurable criterion>
- <failure or edge-case criterion>
**Verify:** `<fresh executable command>`
**Evidence recorded in:** <test/report/state path>
**Rollback / reversal:** <how to undo or feature-flag>
```

### Plan quality gates

1. Every task is one working session or smaller and produces a visible outcome.
2. Every task has exact files, measurable acceptance, and executable verification.
3. No task relies on hidden context; decisions link to brief/decision records.
4. Risky assumptions are tested before expensive dependent implementation.
5. Security/privacy/accessibility/operations are built where required, not postponed
   automatically to the end.
6. The first product milestone is a thin end-to-end user outcome, not disconnected
   technical layers.
7. Every phase has entry/exit evidence and a rollback or recovery path where relevant.
8. Every task cites the mind node IDs it realizes; must-have nodes not covered by any
   milestone are surfaced as gaps, and node-less tasks are challenged as scope creep.
9. The user approves the roadmap before `project-memory` sets the first current task.

## Stage 8 — Handoff

After plan approval:

1. Apply `project-memory` to create/update STATE with the approved Vision Lock,
   current task, capability inventory, and next three actions.
2. Apply `step-pilot` for one-task-at-a-time execution.
3. Invoke SMART at phase changes, material new evidence, scope changes, or capability gaps.
