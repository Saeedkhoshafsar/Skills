# HERMES → SMART Port Plan

> Step-by-step upgrade plan for the Skills / SMART ecosystem, porting Hermes Agent
> learning-memory capabilities without abandoning SMART’s Project Mind, Vision Lock,
> or excellence-by-default contracts.
>
> **Status:** SHIPPED on `main` + GitHub Release `v2.5.13` (Phase 0–8, PR #22) — Phase 9 backlog deferred by owner (Claude Code local, no always-on gateway)  
> **Created:** 2026-07-17  
> **Phase 0 frozen:** 2026-07-17  
> **Phase 1 shipped:** 2026-07-17 (project-memory 1.4.0 / SMART 2.5.6)  
> **Phase 2 shipped:** 2026-07-17 (project-memory 1.5.0 / SMART 2.5.7)  
> **Phase 3 shipped:** 2026-07-17 (project-memory 1.6.0 / SMART 2.5.8)  
> **Phase 4 shipped:** 2026-07-17 (project-memory 1.7.0 / SMART 2.5.9)  
> **Phase 5 shipped:** 2026-07-17 (project-memory 1.8.0 / SMART 2.5.10)  
> **Phase 6 shipped:** 2026-07-17 (project-memory 1.9.0 / SMART 2.5.11)  
> **Owner:** SMART maintainers  
> **Source research:** local clone `../hermes` (Nous Research Hermes Agent) + SMART `2.5.5`  
> **How to use:** check boxes as steps complete; never skip a phase gate; update
> `docs/STATE.md` runway after each completed phase.

---

## 0. Why this plan exists

Hermes has a closed learning loop that makes multi-session conversation feel
personalized: curated memory, user modeling, procedural skill self-improvement,
episodic session search, periodic nudges, and optional deep memory providers.

SMART already owns **project truth** (Project Mind, brief, plan, STATE, decisions).
What it lacks is Hermes-class **personal + operational learning memory**:

| Domain | SMART today | Hermes strength |
|---|---|---|
| Product truth | Project Mind + Brief + Plan | Context files / skills |
| Session resume | `STATE.md` / `STATE2.md` | Session DB + FTS5 |
| User personalization | Implicit in chat / brief | `USER.md` + Honcho dialectic |
| Agent operational notes | Scattered in STATE/ledger | Bounded `MEMORY.md` |
| Procedural reuse | Install/create skills | `skill_manage` + self-patch + curator |
| Auto-learning | Manual consolidate | Nudges + background review |

**Goal:** give SMART a Hermes-grade learning stack **on top of** Project Mind — not
as a replacement for it.

**Non-goal for early phases:** become a full Hermes runtime (messaging gateway,
desktop app, multi-provider tool gateway, terminal backends). Those are catalogued
and scheduled so nothing is “lost,” but they are not the first delivery.

---

## 1. Guiding principles (do not violate)

- [x] **G1 — Two brains, one orchestrator.**  
  Project Mind = product truth. Hermes-port memory = user + agent operational truth.  
  SMART remains the single control brain that decides when each is read/written.
- [x] **G2 — Bounded by default.**  
  Always-on prompt memory stays small (char budgets). Unlimited history lives in
  searchable episodic storage, not in every prompt.
- [x] **G3 — Frozen snapshot for session stability.**  
  Always-on memory injects once per session (or once per SMART invocation packet).  
  Mid-session writes update disk immediately; live tool responses show new state;
  next session sees the new snapshot.
- [x] **G4 — Agent-curated, not silent dump.**  
  No auto-append of raw chat into profile. Writes go through add/replace/remove
  with capacity pressure and consolidation.
- [x] **G5 — Declarative ≠ procedural.**  
  `USER`/`MEMORY` store facts and preferences. Skills store how-to procedures.  
  User style corrections that affect a task class update skills, not only profile.
- [x] **G6 — Cache- and noise-safe.**  
  Prefer stable prefixes; inject volatile recall in a fenced block when needed;
  never poison Project Mind with ephemeral chat trivia.
- [x] **G7 — Consent and safety.**  
  Threat scanning for injection/exfil; optional write approval; no secrets in
  memory files.
- [x] **G8 — SMART contracts still win.**  
  Vision Lock, mind coverage, mid-mission checkpoint, max-3 capabilities,
  excellence-by-default, progress-first fast path remain mandatory.
- [x] **G9 — Port by contract, not by copy-paste.**  
  Reuse Hermes *mechanisms*; rewrite into SMART skill language, gates, and files.
- [x] **G10 — Nothing silently dropped.**  
  Every Hermes capability is either ported, adapted, scheduled, or explicitly
  marked out-of-scope with a reactivation trigger.

---

## 2. Target architecture (SMART + Hermes layers)

```text
┌─────────────────────────────────────────────────────────────┐
│ SMART orchestrator (unchanged role)                         │
│ Sense → Orient → Model → Decide → Act → Consolidate         │
└───────────────┬───────────────────────────┬─────────────────┘
                │                           │
     ┌──────────▼──────────┐     ┌──────────▼──────────────────┐
     │ Project truth        │     │ Learning memory (NEW)       │
     │ PROJECT-MIND.md      │     │ USER.md   (profile)         │
     │ PROJECT-BRIEF.md     │     │ MEMORY.md (agent notes)     │
     │ PLAN.md              │     │ SOUL.md   (optional identity│
     │ STATE.md / STATE2.md │     │           for agent tone)   │
     │ DECISIONS.md         │     │ sessions.db + FTS (episodic)│
     │ RESEARCH.md          │     │ skill self-improve + curator│
     └──────────────────────┘     │ memory providers (plugin)   │
                                  └─────────────────────────────┘
```

### Canonical new paths (user projects)

| Path | Purpose | Hermes analogue |
|---|---|---|
| `docs/USER.md` | Bounded user profile | `~/.hermes/memories/USER.md` |
| `docs/AGENT-MEMORY.md` | Bounded agent operational notes | `~/.hermes/memories/MEMORY.md` |
| `docs/SOUL.md` (optional) | Agent identity/tone for this project | `~/.hermes/SOUL.md` |
| `.smart/memory/` | Machine state: usage, curator, pending writes | Hermes sidecars |
| `.smart/sessions/state.db` | Episodic session index (later phase) | `~/.hermes/state.db` |
| `.smart/evidence/memory-*.json` | Gate artifacts for memory health | — |

> Naming note: use `AGENT-MEMORY.md` (not bare `MEMORY.md`) in user projects so it
> is never confused with human “project memory” / Project Mind. Internally we may
> still call the store `memory`.

### Repo-level delivery surfaces (this Skills repo)

| Surface | Role |
|---|---|
| `skills/project-memory` | Owns project truth **and** new learning-memory protocols |
| `skills/smart` | Orchestrates read/write/nudge/review in the operating loop |
| Optional new skill `user-memory` | Only if project-memory becomes too large — prefer extend first |
| `smart-gates.py` | New gates: memory budget, resume+profile, pending writes |
| Tests + scenarios | Deterministic contracts for every phase |

---

## 3. Capability inventory — full Hermes map (nothing lost)

Check a capability only when it is **implemented in SMART** or **explicitly
deferred with trigger**. Use status tags:

- `TODO` — not started  
- `DOING` — in progress  
- `DONE` — shipped + tests green  
- `ADAPT` — SMART-shaped equivalent shipped  
- `LATER` — scheduled, not abandoned  
- `OUT` — deliberately not porting (with reason + trigger)

### 3.1 Learning & memory core

| ID | Capability | Hermes source | SMART target | Status |
|---|---|---|---|---|
| C-01 | Bounded `MEMORY` store | `tools/memory_tool.py` | `docs/AGENT-MEMORY.md` | DONE |
| C-02 | Bounded `USER` profile | same | `docs/USER.md` | DONE |
| C-03 | `§` entry delimiter + multiline | same | same semantics | DONE |
| C-04 | add / replace / remove tool actions | same | SMART memory protocol + scripts | DONE |
| C-05 | Substring match for replace/remove | same | same | DONE |
| C-06 | Char budgets + overflow consolidation | same | configurable limits | DONE |
| C-07 | Frozen snapshot injection | same + system prompt | SENSE packet / session header | DONE |
| C-08 | Live tool response vs frozen prompt | same | same split | DONE |
| C-09 | Threat scan on memory writes | `threat_patterns` | gate + scanner | DONE |
| C-10 | Write approval / pending queue | `memory.write_approval` | `/memory pending` equivalent | DONE |
| C-11 | Duplicate rejection | memory tool | same | DONE |
| C-12 | Drift guard (external edit safety) | memory tool | same when scripts mutate files | LATER |
| C-13 | Profile-scoped isolation | Hermes profiles | multi-project / multi-persona later | DONE (light metadata); full multi-home LATER |
| C-14 | `SOUL.md` identity | personality / SOUL | optional `docs/SOUL.md` | DONE |
| C-15 | Session FTS5 search | `hermes_state.py` + `session_search_tool` | `.smart/sessions` | DONE |
| C-16 | Discovery / scroll / browse modes | session_search | same three shapes | DONE |
| C-17 | Cron/subagent demotion in recall | session_search | demote automation sources | DONE (hidden/demoted by default) |
| C-18 | Memory providers ABC | `memory_provider.py` | `.smart` provider interface | DONE |
| C-19 | MemoryManager orchestration | `memory_manager.py` | SMART consolidate hooks | DONE |
| C-20 | One external provider at a time | manager limit | same | DONE |
| C-21 | Honcho dialectic user model | `plugins/memory/honcho` | provider plugin + docs | LATER |
| C-22 | Mem0 / Supermemory / others | plugins/memory/* | provider catalog + local shipped | DONE (catalog + local; cloud LATER) |
| C-23 | `<memory-context>` fencing + scrub | memory_manager | when external inject used | DONE |
| C-24 | Prefetch / queue_prefetch / sync_turn | provider lifecycle | same lifecycle | DONE |
| C-25 | on_session_end extraction | provider hooks | session-end consolidate | DONE (hook + extract-durable protocol; same as C-26 path) |
| C-26 | on_pre_compress extract | compression hooks | context-budget 60/80 hooks | DONE (protocol: extract-durable) |
| C-27 | Learning graph visualization | `learning_graph.py` | optional viz later | LATER |

### 3.2 Self-improvement loop

| ID | Capability | Hermes source | SMART target | Status |
|---|---|---|---|---|
| C-30 | Memory nudge interval | run_agent counters | SMART turn/event counter | DONE |
| C-31 | Skill nudge interval | same | same | DONE |
| C-32 | Background review fork | `background_review.py` | post-action review protocol | DONE (inline default; forked optional) |
| C-33 | Memory review prompt | `_MEMORY_REVIEW_PROMPT` | adapted English protocol | DONE |
| C-34 | Skill review prompt | `_SKILL_REVIEW_PROMPT` | adapted; class-level skills | DONE |
| C-35 | `/learn` skill authoring | `learn_prompt.py` | SMART CREATE path + skill-creator | DONE |
| C-36 | `skill_manage` create/edit/patch | skill_manager_tool | SMART skill authoring protocol | DONE (protocol) |
| C-37 | Support files refs/templates/scripts | same | same layout for created skills | DONE |
| C-38 | Skill usage telemetry | `skill_usage.py` | `.smart/memory/skill-usage.json` | DONE |
| C-39 | Curator lifecycle active/stale/archived | `curator.py` | curator protocol + idle trigger | DONE |
| C-40 | Pin skills | curator pin | pin flag | DONE |
| C-41 | Never auto-delete (archive only) | curator | same | DONE |
| C-42 | Protected built-ins | PROTECTED_BUILTIN_SKILLS | protect local 7 + catalog critical | DONE |
| C-43 | Agent-created skill security scan | skills_guard | extend fetch/create gate | DONE |
| C-44 | Autonomous skill after complex task | closed loop | post-milestone skill review | DONE |
| C-45 | Skills self-improve during use | patch on correction | user-correction → skill patch | DONE |

### 3.3 Context, tools, automation (scheduled, not forgotten)

| ID | Capability | Notes for SMART | Status |
|---|---|---|---|
| C-50 | Context files (AGENTS/CLAUDE/SOUL/.cursorrules) | Already partially present; formalize discovery order | ADAPT |
| C-51 | `@` context references | Optional SMART message expansion | LATER |
| C-52 | Checkpoints / rollback | Git + task rollback already; optional snapshot tool | LATER |
| C-53 | Cron / scheduled automations | Host `/loop` exists; full cron gateway later | LATER |
| C-54 | Subagent delegation | Claude Code agents / Task tool; document playbook | ADAPT |
| C-55 | Code execution RPC tool-calling | Out of SMART skill scope unless needed | LATER |
| C-56 | MCP integration | Host MCP + SMART supervision | ADAPT |
| C-57 | Messaging gateway multi-platform | Product expansion; not core skill port | LATER |
| C-58 | TUI / Desktop / Dashboard | Product expansion | LATER |
| C-59 | Provider routing / credential pools | Host/model layer | OUT — host concern |
| C-60 | Trajectory / research batch training | Research product; separate track | OUT — unless owner asks |
| C-61 | Kanban multi-agent | Optional later orchestration | LATER |
| C-62 | Browser / vision / TTS / voice | Capability fetch via catalog when needed | ADAPT |
| C-63 | OpenAI-compatible API server | Host/product | LATER |
| C-64 | ACP IDE integration | Host | LATER |
| C-65 | Plugins system | SMART already plugin marketplace | ADAPT |
| C-66 | OpenClaw migration | Not relevant | OUT |
| C-67 | agentskills.io compatibility | Keep SKILL.md standard; already aligned | ADAPT |

---

## 4. Phased delivery plan

Each phase has: **goal**, **deliverables**, **acceptance**, **tests**, **checkbox steps**.  
Do not start phase N+1 until phase N acceptance is green (unless a step is explicitly parallelizable).

---

### Phase 0 — Spec freeze & repo wiring
**Goal:** agree contracts, paths, and non-goals so implementation does not thrash.

#### Steps
- [x] **P0-T1** Confirm this plan file as the working authority for Hermes-port work.
- [x] **P0-T2** Freeze path names: `docs/USER.md`, `docs/AGENT-MEMORY.md`, optional `docs/SOUL.md`, `.smart/memory/`.
- [x] **P0-T3** Freeze char budgets (defaults): USER 1375, AGENT-MEMORY 2200 (Hermes parity); document override knobs.
- [x] **P0-T4** Write separation rules: what goes to Project Mind vs USER vs AGENT-MEMORY vs skills vs STATE.
- [x] **P0-T5** Add plan pointer to `docs/STATE.md` runway (this repo).
- [x] **P0-T6** Define epistemic labels for user-memory entries (optional `KNOWN/INFERRED` tags in entries).
- [x] **P0-T7** Define security baseline: no secrets, threat scan scope, write-approval default = off (Hermes parity) but recommended on for novices.
- [x] **P0-T8** Produce a one-page architecture note inside this file §2 (done when reviewed).

#### Frozen contracts (Phase 0 lock — 2026-07-17)

| Contract | Frozen value |
|---|---|
| Plan authority | This file (`docs/HERMES-PORT-PLAN.md`) |
| User profile path | `docs/USER.md` (project-local) |
| Agent notes path | `docs/AGENT-MEMORY.md` (project-local; never bare `MEMORY.md`) |
| Optional identity | `docs/SOUL.md` |
| Machine sidecars | `.smart/memory/` (usage, pending, loop-state, curator) |
| Episodic store (P6) | `.smart/sessions/state.db` **per-project** |
| Global profile (later) | `~/.smart/` only after multi-project demand |
| USER char budget | **1375** default |
| AGENT-MEMORY char budget | **2200** default |
| Override knobs | `.smart/memory/config.json` keys `user_char_limit`, `memory_char_limit` |
| Entry delimiter | `§` (section sign); multiline entries allowed |
| Memory actions | `add` / `replace` / `remove` on target `user` \| `memory` |
| Frozen snapshot | Load once per SMART session/invocation packet; disk live, prompt frozen |
| Skill ownership | **Extend `project-memory`** (no new `user-memory` skill until size forces split) |
| External provider default | **builtin** through Phase 6; local before cloud in Phase 7 |
| First deep provider order | local/sqlite-class first; Honcho optional cloud later |
| `write_approval` default | **off** (Hermes parity); docs recommend **on** for novices |
| Secrets policy | Never store secret values — name/location only |
| Threat scan | Block prompt-injection / exfil / invisible Unicode on write + load |
| Epistemic tags | Optional prefix on entries: `[KNOWN]` (user-stated) / `[INFERRED]` (agent-guessed, lower confidence) |
| Host model note | User may use API models (any provider); port is skill/protocol-level, not host-model-bound |

#### Acceptance
- [x] Owner/maintainer agrees paths + budgets + separation rules.
- [x] STATE runway points here.
- [x] No code behavior change required yet.

#### Exit criteria
Plan is the checklist source of truth; implementation may start Phase 1. **MET 2026-07-17.**

---

### Phase 1 — Built-in dual memory stores (P0 core)
**Goal:** Hermes-style bounded USER + AGENT-MEMORY with tool semantics and frozen snapshot.

**Ports:** C-01…C-08, C-11, partial C-09

#### Steps
- [x] **P1-T1** Specify entry format: `§`-delimited entries; multiline allowed; header with usage `%`.
- [x] **P1-T2** Extend `project-memory` SKILL.md with Learning Memory section (USER + AGENT-MEMORY).
- [x] **P1-T3** Define memory actions protocol for agents: `add`, `replace`, `remove` (+ target `user`|`memory`).
- [x] **P1-T4** Implement helper script(s) under SMART or project-memory, e.g. `memory_store.py`:
  - load/save files
  - char counting
  - substring unique match
  - overflow errors with `current_entries`
  - duplicate detection
- [x] **P1-T5** Document frozen-snapshot rule in SMART SENSE/MODEL/CONSOLIDATE.
- [x] **P1-T6** SMART session-start read order becomes: STATE → USER → AGENT-MEMORY → mind/brief as needed.
- [x] **P1-T7** SMART consolidate writes: user prefs → USER; env/lessons → AGENT-MEMORY; product facts → mind.
- [x] **P1-T8** Add “what to save vs skip” table (Hermes-aligned) to skill docs.
- [x] **P1-T9** Unit tests for budget, match, duplicate, delimiter round-trip.
- [x] **P1-T10** Behavioral scenarios: save preference; overflow forces consolidate; no product-fact leakage into USER.

#### Acceptance
- [x] Agent can maintain USER + AGENT-MEMORY without free-form file chaos.
- [x] Overflow never silent-drops.
- [x] Tests green; scenarios valid.
- [x] Project Mind remains canonical for product truth.

#### Version bump (shipped)
`project-memory` **1.4.0**, SMART **2.5.6**, marketplace **2.5.6**.

---

### Phase 2 — Threat scan + write approval
**Goal:** safe personalization; user can gate automatic saves.

**Ports:** C-09, C-10

#### Steps
- [x] **P2-T1** Port/adapt a minimal threat pattern list appropriate for skill-injected memory (strict scope).
- [x] **P2-T2** Block matching writes; keep raw entry inspectable when blocked at load.
- [x] **P2-T3** Implement pending write queue under `.smart/memory/pending.json`.
- [x] **P2-T4** Protocol commands (documented for SMART, not necessarily slash UI): list / approve / reject pending.
- [x] **P2-T5** Config flag `memory.write_approval` (default false; document novice recommendation true).
- [x] **P2-T6** Tests: injection blocked; pending requires approval; approve applies to file.

#### Acceptance
- [x] Poisoned memory cannot enter always-on snapshot.
- [x] Approval path works end-to-end in protocol tests.

#### Version bump (shipped)
`project-memory` **1.5.0**, SMART **2.5.7**, marketplace **2.5.7**. **MET 2026-07-17.**

---

### Phase 3 — Nudges + background review (self-learning loop)
**Goal:** Hermes closed loop: periodic self-extraction without user babysitting.

**Ports:** C-30…C-34, C-44, C-45 (protocol-level)

#### Steps
- [x] **P3-T1** Define counters in STATE or `.smart/memory/loop-state.json`: turns_since_memory, turns_since_skill.
- [x] **P3-T2** Default intervals (start conservative): memory every 10 user turns; skill every 15 — configurable.
- [x] **P3-T3** Port adapted `_MEMORY_REVIEW_PROMPT` into SMART consolidate guidance.
- [x] **P3-T4** Port adapted `_SKILL_REVIEW_PROMPT` with SMART constraints (max capabilities, no BLACK tier, class-level skills).
- [x] **P3-T5** Define **inline review** (same invocation, cheap) vs **forked review** (optional deeper pass).
- [x] **P3-T6** Wire triggers: after meaningful action, after user correction, after milestone, on interval.
- [x] **P3-T7** Notification policy: quiet by default; optional “saved X to USER” line.
- [x] **P3-T8** Anti-patterns from Hermes skill review (no “tool broken forever”, no one-off narrative skills).
- [x] **P3-T9** Scenarios: user correction → USER or skill update; empty session → “Nothing to save.”
- [x] **P3-T10** Ensure review never blocks Task Verify / Vision gates.

#### Acceptance
- [x] Multi-turn personalization happens without explicit “remember this” every time.
- [x] Review cannot stall execution path.
- [x] Tests/scenarios green.

#### Version bump (shipped)
`project-memory` **1.6.0**, SMART **2.5.8**, marketplace **2.5.8**. **MET 2026-07-17.**

---

### Phase 4 — Procedural skill self-improvement
**Goal:** skills become living procedural memory.

**Ports:** C-35…C-38, C-43, C-45

#### Steps
- [x] **P4-T1** Formalize SMART CREATE skill path against Hermes authoring standards (description ≤60 chars, section order — adapt to Claude Code skill norms where they differ).
- [x] **P4-T2** Define patch-on-correction workflow: identify loaded skill → patch pitfalls/steps → optional references file.
- [x] **P4-T3** Support layout for agent-created skills: `references/`, `templates/`, `scripts/`.
- [x] **P4-T4** Usage sidecar `.smart/memory/skill-usage.json` (views, patches, last_used).
- [x] **P4-T5** Security scan for agent-created skills (reuse quarantine principles).
- [x] **P4-T6** `/learn`-equivalent protocol: distill last workflow into skill when user asks or review recommends.
- [x] **P4-T7** Tests: patch requires prior read; protected skills not deleted; usage bumps.

#### Acceptance
- [x] A user preference about “how to do X” lands in a skill, not only USER.md.
- [x] Created skills pass structure + security checks.

#### Version bump (shipped)
`project-memory` **1.7.0**, SMART **2.5.9**, marketplace **2.5.9**. **MET 2026-07-17.**

---

### Phase 5 — Curator (library hygiene)
**Goal:** long-term skill library does not rot.

**Ports:** C-39…C-42

#### Steps
- [x] **P5-T1** Lifecycle states: active / stale / archived / pinned.
- [x] **P5-T2** Defaults: stale after 30d unused; archive after 90d; never auto-delete.
- [x] **P5-T3** Protected set: smart, project-memory, project-planner, step-pilot, code-review, debug-detective, security-check.
- [x] **P5-T4** Idle-triggered curator protocol (document when SMART should run it).
- [x] **P5-T5** Archive path `.smart/skills-archive/` or project-local equivalent.
- [x] **P5-T6** Optional consolidate pass (OFF by default, Hermes parity).
- [x] **P5-T7** Tests for transitions + pin + protected.

#### Acceptance
- [x] Stale agent-created skills archive safely.
- [x] Core skills never auto-archived.

#### Version bump (shipped)
`project-memory` **1.8.0**, SMART **2.5.10**, marketplace **2.5.10**. **MET 2026-07-17.**

---

### Phase 6 — Episodic session search
**Goal:** unlimited recall without bloating always-on memory.

**Ports:** C-15, C-16, C-17 (default demotion), C-26 (protocol)

#### Steps
- [x] **P6-T1** Choose storage: SQLite FTS5 under `.smart/sessions/state.db` (preferred) or markdown index MVP.
- [x] **P6-T2** Session write protocol: what SMART logs per turn/task (roles, timestamps, task id).
- [x] **P6-T3** Implement search shapes: discovery / scroll / browse.
- [x] **P6-T4** Privacy: redaction hooks for secrets; local-only by default.
- [x] **P6-T5** SMART rule: prefer USER/AGENT-MEMORY first; session_search for specifics.
- [x] **P6-T6** Hook context-budget 60/80: before compact/handoff, extract durable facts (C-26).
- [x] **P6-T7** Tests with fixture transcripts.

#### Acceptance
- [x] Agent can answer “what did we decide last week about X?” from store, not chat luck.
- [x] Always-on memory stays bounded.

#### Version bump (shipped)
`project-memory` **1.9.0**, SMART **2.5.11**, marketplace **2.5.11**. **MET 2026-07-17.**

---

### Phase 7 — External memory providers (deep user model / “mind clone”)
**Goal:** pluggable deep personalization (Honcho-class) without core bloat.

**Ports:** C-18…C-24, C-21/C-22 as plugins

**Status:** COMPLETE (2026-07-17) — MVP offline path; cloud adapters catalog-only.

#### Steps
- [x] **P7-T1** Define `MemoryProvider` interface (initialize, system block, prefetch, sync_turn, tools, shutdown + optional hooks).
- [x] **P7-T2** MemoryManager: only one external provider active.
- [x] **P7-T3** Fence external recall as `<memory-context>` (or SMART-equivalent) with scrubber.
- [x] **P7-T4** Ship **null/local** provider first (built-in stores only).
- [x] **P7-T5** Document provider catalog: Honcho, Mem0, Supermemory, Hindsight, etc. — install optional.
- [x] **P7-T6** Implement first real provider adapter (recommend **Honcho** for user-model depth OR **local holographic/sqlite** for zero-cloud).
- [x] **P7-T7** Config: `memory.provider = builtin|honcho|...`
- [x] **P7-T8** Tests with fake provider; no network in default CI.

#### Acceptance
- [x] Built-in path works with provider = builtin.
- [x] One external provider can be enabled without breaking SMART gates.
- [x] CI remains offline-green by default.

---

### Phase 8 — Identity, profiles, multi-surface polish
**Goal:** personality + isolation + operator UX.

**Ports:** C-13, C-14, partial product surfaces

**Status:** COMPLETE (2026-07-17) — light profile metadata; full multi-home still LATER.

#### Steps
- [x] **P8-T1** Optional `docs/SOUL.md` load order and scan.
- [x] **P8-T2** Personality presets protocol (light-weight).
- [x] **P8-T3** Multi-profile design (personal vs work) — only if demanded.
- [x] **P8-T4** Dashboard/status: memory usage %, pending writes, last review.
- [x] **P8-T5** Docs in README + CLAUDE.md hard rules for learning memory.
- [x] **P8-T6** Migration guide: existing projects gain empty USER/AGENT-MEMORY without ceremony.

#### Acceptance
- [x] New projects bootstrap cleanly.
- [x] Existing projects do not break or require rediscovery.

---

### Phase 9 — Product-surface backlog (explicitly not abandoned)

These stay visible so the “I want everything” list is not lost. Activate only with
evidence or explicit owner request.

**Owner decision 2026-07-17:** deferred for Claude Code local use (no always-on
server / Telegram gateway; lean context budget). Do not implement P9-T1…T8 unless
re-requested.

- [ ] **P9-T1** Messaging gateway playbook (Telegram/Discord/…) as optional deployment skill pack.
- [ ] **P9-T2** Cron/gateway automations beyond host `/loop`.
- [ ] **P9-T3** Full checkpoint/rollback tool beyond git.
- [ ] **P9-T4** Kanban multi-agent orchestration pack.
- [ ] **P9-T5** Desktop/TUI/API server packaging.
- [ ] **P9-T6** Learning-graph visualization for USER/AGENT-MEMORY entries.
- [ ] **P9-T7** Advanced session demotion rules for automation noise.
- [ ] **P9-T8** Provider pack: Mem0, Supermemory, Hindsight, ByteRover, OpenViking, RetainDB.

---

## 5. Separation rules (critical — pin early)

### Write routing table

| Signal | Write to |
|---|---|
| Product what/why/for whom / final experience | `PROJECT-MIND` + brief |
| Plan/task/progress/blocker | `STATE` / plan |
| Consequential choice with alternatives | `DECISIONS` |
| Sourced external claim | `RESEARCH` |
| User prefs, communication style, workflow habits | `USER.md` |
| Env facts, tool quirks, operational lessons | `AGENT-MEMORY.md` |
| How to do a class of task (esp. after correction) | Skill patch/create |
| Raw conversation detail | Session store only |
| Secrets | Never — name/location only |

### Epistemic tags (optional, frozen in P0)

Prefix entry text when confidence matters:

| Tag | Meaning | Write rule |
|---|---|---|
| `[KNOWN]` | User stated or verified from durable project evidence | Prefer for USER prefs and confirmed env facts |
| `[INFERRED]` | Agent guessed from behavior; may be wrong | Prefer soft claims; replace/remove eagerly on correction |
| (none) | Default / mixed | OK for compact operational notes |

Never promote an `[INFERRED]` user trait into Project Mind product truth.

### Do not save
- Trivial one-off questions
- Easily re-searched public facts
- Large logs/code dumps
- Session ephemera (temp paths)
- Content already in SOUL/mind/brief
- Negative absolute claims about broken tools without a fix recipe
- Secret values (tokens, passwords, API keys) — store name/location only

---

## 6. SMART loop integration map

| SMART stage | Learning-memory hooks |
|---|---|
| **SENSE** | Load frozen USER + AGENT-MEMORY snapshot; optional provider prefetch |
| **ORIENT** | Mode may become RECOVERY if memory conflicts with repo evidence |
| **MODEL** | Route new facts per separation table; label epistemic status |
| **DECIDE** | Prefer memory-backed personalization; don’t re-ask known USER prefs |
| **ACT** | On user correction mid-task, mark skill/memory review needed |
| **CONSOLIDATE** | Interval nudges; memory/skill review; pending queue; usage bumps |
| **Context 40/60/80** | At 60+ extract durable facts before compact; at 80 hard handoff includes memory delta |
| **Mid-mission checkpoint** | Include learning-memory deltas when prefs/lessons changed |

---

## 7. Testing strategy

- [x] Deterministic unit tests for store math, match, budgets, pending, curator transitions.
- [x] Contract tests that SMART docs mention new read order and routing table. (covered by scenarios + skill docs; unit tests for stores/providers)
- [x] Behavioral scenarios in `evals/scenarios.json` for personalization + overflow + correction→skill. (31 offline scenarios; learning-memory suite present)
- [x] No network/provider calls in default CI. (builtin/null/local only; no network imports in provider scripts)
- [x] Regression: Vision Lock / resume-check / max-3 capabilities unchanged. (existing contract tests + scenarios still green)
- [x] Golden fixtures for USER/AGENT-MEMORY rendering headers. (frozen_snapshot / render_block unit coverage; file format fixtures in tests)

---

## 8. Suggested versioning & release train

| Phase | Suggested versions | Release notes focus |
|---|---|---|
| P0 | docs only | plan authority |
| P1 | project-memory +0.1, SMART +0.0.1 docs/hooks | dual memory stores |
| P2 | SMART patch | safety + approval |
| P3 | SMART minor | self-learning loop |
| P4 | SMART + project-memory minor | skill self-improve |
| P5 | SMART minor | curator |
| P6 | SMART minor + scripts | session search |
| P7 | SMART minor | providers interface |
| P8 | docs + polish | identity/profiles |

Ship each phase as its own PR when possible. Prefer progress-first: a thin green
slice beats a giant unfinished merge.

---

## 9. Immediate next actions (start here)

1. [x] **Complete Phase 0 checkboxes** with any path/budget tweaks you want.
2. [x] **Start Phase 1** implementation on `project-memory` + SMART docs/scripts.
3. [x] **Phase 2** threat scan + write_approval pending queue.
4. [x] **Phase 3** nudges + background review (self-learning loop).
5. [x] **Phase 4** procedural skill self-improvement.
6. [x] **Start Phase 5** curator (library hygiene). **COMPLETE 2026-07-17.**
7. [x] Keep this file’s checkboxes updated every session.
8. [x] After each phase exit: update `docs/STATE.md` resume packet + changelog.

---

## 10. Progress log

| Date | Phase/Task | Result | Evidence |
|---|---|---|---|
| 2026-07-17 | Plan created | ACTIVE | this file |
| 2026-07-17 | Phase 0 complete | D1–D4 resolved; paths/budgets/separation/security frozen; G1–G10 accepted | Frozen contracts table in §4 Phase 0; §11 resolved |
| 2026-07-17 | Phase 1 complete | Dual stores + memory_store.py + SMART hooks + tests/scenarios | project-memory 1.4.0 / SMART 2.5.6; C-01…C-08,C-11 DONE |
| 2026-07-17 | Phase 2 complete | Threat scan + write_approval pending queue + tests/scenarios | project-memory 1.5.0 / SMART 2.5.7; C-09,C-10 DONE |
| 2026-07-17 | Phase 3 complete | loop-state counters, intervals 10/15, memory/skill review protocols, non-blocking consolidate, tests/scenarios | project-memory 1.6.0 / SMART 2.5.8; C-30…C-34,C-44 DONE; C-45 PARTIAL |
| 2026-07-17 | Phase 4 complete | skill_usage sidecar, patch-on-correction, authoring standards, learn protocol, security scan, tests/scenarios | project-memory 1.7.0 / SMART 2.5.9; C-35…C-38,C-42,C-43,C-45 DONE |
| 2026-07-17 | Phase 5 complete | skill curator lifecycle + tests/scenarios | project-memory 1.8.0 / SMART 2.5.10; C-39…C-42 DONE |
| 2026-07-17 | Phase 6 complete | session_store FTS5/LIKE + extract-durable | project-memory 1.9.0 / SMART 2.5.11; C-15,C-16,C-26 DONE |
| 2026-07-17 | Phase 7 complete | memory providers ABC + manager + local adapter | project-memory 1.10.0 / SMART 2.5.12; C-18…C-24 DONE |
| 2026-07-17 | Phase 8 complete | SOUL/personality/dashboard/migrate | project-memory 1.11.0 / SMART 2.5.13; C-14 DONE; C-13 light |
| 2026-07-17 | MVP ship path | Plan audit: unchecked items classified; Phase 9 deferred by owner | 216 tests OK / 31 scenarios; release target v2.5.13 |

---

## 11. Open decisions (resolve in Phase 0)

- [x] **D1** Default `write_approval`: off (Hermes parity) or on (safer for novices)?  
  **RESOLVED:** default **off** (Hermes parity). Document novice recommendation **on**. Optional later heuristic: flip on when SMART detects novice signals — not required for P1.
- [x] **D2** First deep provider: Honcho (best user-model story) vs pure-local SQLite (privacy)?  
  **RESOLVED:** **builtin** through P1–P6. In P7: **local/sqlite-class provider before any cloud**. Honcho remains first *optional cloud* candidate, not the default path.
- [x] **D3** New skill `user-memory` vs extend `project-memory`?  
  **RESOLVED:** **extend `project-memory`**. Split only if SKILL.md/scripts become unmaintainable.
- [x] **D4** Session DB scope: per-project `.smart/sessions` only, or also global user profile across projects?  
  **RESOLVED:** **per-project** `.smart/sessions` first. Global `~/.smart/` profile is a later opt-in, not MVP.

---

## 12. Definition of “Hermes-complete for SMART”

We call the port **MVP complete** when:

- [x] USER + AGENT-MEMORY bounded stores live and tested
- [x] Frozen snapshot + consolidate routing live
- [x] Nudges + review loop live
- [x] Skill patch-on-correction live
- [x] Session search MVP live
- [x] Provider interface exists (even if only builtin)
- [x] Threat scan + optional write approval live
- [x] Curator MVP live
- [x] All C-* items are DONE, ADAPT, LATER, or OUT (none silent TODO)

We call it **mind-clone complete** when MVP + at least one deep user-model
provider (Honcho or equivalent) is production-documented and optional.

---

*End of plan. Tick boxes; do not delete history — move finished phases’ notes into the progress log.*
