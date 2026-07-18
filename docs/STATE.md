# STATE — SMART Skill-Manager Ecosystem

> Resume index for cross-session continuity. The product contract lives in
> `skills/smart/skills/smart/SKILL.md`; capability decisions live in
> `SKILLS_CATALOG.md`; offline adversarial contracts live in
> `skills/smart/skills/smart/evals/scenarios.json`.

## Resume packet
| Field | Current value |
|---|---|
| SMART mode / lifecycle phase | MAINTENANCE / 5 |
| Current objective | Keep SMART lean: field-validate; ship only proven gaps. |
| Active task | Ship **2.5.19** soft mid-task harness register/promote (PR + Release). |
| Exact progress | Local code complete: block-version 2, soft trigger table, same-session promote, scenario + contracts, pin **2.5.19**, RELEASE notes. Pending: tests GREEN → commit → PR → merge → Release Latest. |
| Last evidence | 2026-07-18: soft-trigger diffs on main; user `~/.claude/CLAUDE.md` already HARNESS-COMPAT block v2; prior Latest = v2.5.18. |
| Blocker / waiting on | None for product; ship gate = suite + GitHub PR/Release. |
| Next | Publish Release `v2.5.19`; consumer four-step with ensure block v2; field-validate non-Anthropic mid-task OPEN/SOLVED. |
| Vision Lock | CONFIRMED by repository owner on 2026-07-11 (reaffirmed and extended): complete project control brain; mind before code; excellence by default; lean orchestration. Extended 2026-07-18: depth over first-pass polish; creativity ≠ truth; harness-compat before thrash (always-on pointer + SMART ledger); soft mid-task register/promote. |
| Machine gates | Vision: owner-confirmed; Verify: suite (run on ship); Release: pending `v2.5.19`. |
| Branch / head | `main` working tree → ship branch for **2.5.19** soft-trigger. |
| Mind coverage | Applied to this repo implicitly via STATE/BRIEF equivalents; the formal PROJECT-MIND protocol targets user projects. |

## Epistemic delta
### Newly confirmed
- Owner: harness friction ledger should be always-on base knowledge via `~/.claude/CLAUDE.md`, with SMART owning the durable recipes and recovery — source: owner messages 2026-07-18.
- Claude Code loads `~/.claude/CLAUDE.md` every session (user scope) without skill invoke — source: code.claude.com/docs/en/memory, 2026-07-18.
- Existing user skill `claude-code-compat` covers wire dialect (`redacted_thinking`) only; general friction ledger was missing — source: `~/.claude/skills/claude-code-compat`, 2026-07-18.
- PR #26 merged to `main` (`e827b4d`) with validate GREEN — Depth Reprocess + evidence-rooted trees SMART 2.5.17 — source: GitHub PR state, 2026-07-18.
- Release `v2.5.17` published Latest — source: GitHub Releases, 2026-07-18.

### Inferred — confirmation needed
- None for the ship path.

### Active assumptions
| Assumption | Why temporary | Validation test | Owner | Expiry/reversal trigger |
|---|---|---|---|---|
| Offline scenario contracts remain useful as free maintainer safeguards. | They describe expected SMART behavior but do not execute a model. | Keep only if their schema validation and review value remain clear and maintenance-light. | Maintainers | They become stale, confusing, or duplicate contract tests. |
| A compact fast path is sufficient for coherent projects; the full loop should be event-triggered. | Excessive control-plane ceremony can delay the user-visible project outcome. | Require same-invocation action, at most one additional capability, fresh verification, and delta-only memory on the healthy path; retain deep gates only for explicit triggers. | Maintainers | Evidence shows a healthy project needed deeper orientation to avoid a material error. |
| Thin always-on CLAUDE.md pointer + SMART ledger is enough without a separate marketplace plugin for compat. | Skills are not always-on; user CLAUDE.md is. | Field-validate non-Anthropic sessions hit pointer then SMART. | Maintainers | Pointer ignored in practice or ledger grows unmaintainable. |

### Unknowns / conflicts
| Item | Impact if wrong | Resolution action | Status |
|---|---|---|---|
| Exact Claude CLI JSON shape across supported versions | Incorrect detection could cause a redundant add/install attempt. | Keep detection fail-safe and confirm required CI; later replace text matching with stable CLI fields if Claude publishes a versioned schema. | OPEN, NON-BLOCKING |

## Capability inventory
| Capability | Type/source | Status | Invoked when | Last result / review |
|---|---|---|---|---|
| SMART orchestrator | Local skill | ACTIVE CORE | Every user project | Product contract requires evidence-aware orientation, Vision Lock, autonomous capability selection, action, and consolidation. |
| Harness-compat ledger | SMART references + user CLAUDE.md pointer | ACTIVE CORE (2.5.19 soft mid-task) | Model↔Claude Code friction | Soft trigger first/second failure; lookup/apply/register/promote same session; ensure block v2. |
| Unified capability installer | Local shell/Python tooling | VERIFIED | SMART needs a bundled companion, standalone skill, or native plugin | Bundled companions use idempotent trusted-marketplace routing; third-party capabilities retain quarantine, review, lock, and update tests. |
| Machine gates | Local Python tooling | VERIFIED | Vision confirmation, task verification, release readiness | Deterministic gate tests are present. |
| Offline behavioral contracts | JSON + Python stdlib validator | ACTIVE, FREE | Maintainers edit adversarial scenario definitions | No network, model, secret, endpoint, or paid workflow. |
| Learning-memory dual stores | project-memory + memory_store.py | VERIFIED | Personalization / operational lessons | Phase 1–2: bounded USER/AGENT-MEMORY, threat scan, write_approval. |
| Self-learning loop | loop-state + consolidate review | VERIFIED | Interval/event nudges | Phase 3: counters, intervals 10/15, memory/skill review protocols, non-blocking. |
| Skill self-improve | skill_usage.py + CREATE/patch protocol | VERIFIED | How-to corrections / learn | Phase 4: usage sidecar, view-before-patch, authoring standards, protected set. |
| Skill library curator | skill_curator.py + lifecycle | VERIFIED | Idle / maintenance hygiene | Phase 5: active/stale/archived/pinned, archive path, never auto-delete, protected. |
| Episodic session search | session_store.py + FTS5/LIKE | VERIFIED | Historical specifics / pre-compact extract | Phase 6: discovery/scroll/browse, redaction, extract-durable. |
| External memory providers | memory_provider.py + memory_manager.py | VERIFIED | Optional deep personalization | Phase 7: ABC, one-external, fence, builtin/null/local, catalog. |
| Identity / dashboard | identity_store.py | VERIFIED | SOUL, personality, migrate, status UX | Phase 8: SOUL scan, presets, light profiles, dashboard, migrate. |

## Open errors and risks
| ID | Description | Evidence / location | Impact | Next diagnostic/mitigation | Status |
|---|---|---|---|---|---|
| SHIP-006 | Single-pass fluent confidence; creative branches mislabeled as truth. | Owner philosophy + TryAI arena lessons 2026-07-18. | Shallow maxed-looking work; false confidence trees. | PR #26 + Release `v2.5.17`. | RESOLVED |
| SHIP-007 | Non-Anthropic models thrash on Claude Code harness mismatches; knowledge not always-on. | Owner field report 2026-07-18; multi-model settings (Bifrost). | Long trial-and-error; lost recipes across sessions/models. | PR #27 + Release `v2.5.18` + four-step install docs. | RESOLVED |
| SHIP-008 | Soft mid-task: models delay OPEN until long thrash; fixed issues left forever-OPEN. | Owner: soften register/promote trigger 2026-07-18. | Recipes not captured mid-task; weaker models lose fixes. | 2.5.19 soft trigger + same-session promote + block v2. | IN PROGRESS (ship) |
| CORE-005 | Workflow updates may be rejected when the GitHub credential lacks `workflows` permission. | Prior push rejection and owner instruction. | Repeated retries can block unrelated product progress. | Stage exact workflow files under `ci/` and report the manual replacement after the PR. | MITIGATED |

## Meaningful change ledger (newest first)
| Date / commit | What changed | Why | Evidence | Records affected |
|---|---|---|---|---|
| 2026-07-18 / 2.5.19 soft mid-task | Soft first/second trigger; same-session SOLVED; ensure block v2; scenario+contracts; pin 2.5.19 | Capture harness recipes without thrash-wait | Suite + scenario count 39 (ship pending) | SMART, ensure, ledger, tests, README, CLAUDE, smart.md, CHANGELOG, RELEASE, STATE. |
| 2026-07-18 / 2.5.18 ship | Release v2.5.18 Latest + formal four-step consumer path in README/command/CLAUDE | Marketplace pin + always-on pointer must be taught as product docs | Release tag; harness contract GREEN | RELEASE, README, smart.md, CLAUDE, STATE. |
| 2026-07-18 / 2.5.18 harness-compat | HARNESS-COMPAT ledger; ensure-user-claude-md.sh; invariant 14; scenarios+contracts; pin 2.5.18 | Model↔CC friction needs always-on pointer + SMART-owned recipes | 226 tests / 38 scenarios | SMART, scripts, references, tests, catalog, README, CLAUDE, changelog, RELEASE, STATE. |
| 2026-07-18 / 2.5.17 ship | PR #26 merge + Release v2.5.17 | Pin install to Depth Reprocess + evidence-rooted trees | 225 tests / 36 scenarios; `e827b4d` | RELEASE, STATE, marketplace pin. |
| 2026-07-18 / 2.5.17 depth+honesty | Depth L0–L4; truth vs creative trunks; scenarios+contracts; pin 2.5.17 | Surface pass ≠ maxed; creativity ≠ truth | 225 tests / 36 scenarios; validate GREEN | SMART, step-pilot, planner, tests, changelog, RELEASE, STATE. |

## Runway
1. **SHIP 2.5.19:** commit → PR → merge → Release Latest; mark SHIP-008 RESOLVED.
2. **INSTALL (consumer):** marketplace update → plugin update → ensure (block v2) → restart → **`/smart:smart`**.
3. **NEXT — field-validate** non-Anthropic mid-task: soft OPEN + same-session SOLVED.
4. **LATER — optional** promote more wire rules into `claude-code-compat`; archive long SOLVED entries.

## Next-session command packet

```bash
cd /home/samansofi2028/.claude/plugins/marketplaces/saeed-skills
git fetch origin main && git checkout main && git pull --ff-only
python3 -m unittest discover -s tests -v
python3 skills/smart/skills/smart/evals/validate_behavioral_scenarios.py
bash -n skills/smart/skills/smart/scripts/ensure-user-claude-md.sh
bash skills/smart/skills/smart/scripts/ensure-user-claude-md.sh --check
# consumers:
# claude plugin marketplace update saeed-skills && claude plugin update smart@saeed-skills
```

The offline-contract tests also guard against reintroducing network clients, model arguments, evaluator secrets, or a staged live workflow.

## Deferred / debt with activation triggers
- Paid model observation and external evaluation workflows — deliberately removed; reconsider only after an explicit future owner decision, never as a user requirement.
- Multi-model evaluation and semantic scoring — deliberately out of scope.
- Broad end-to-end simulation framework — deliberately avoided unless a concrete transition cannot be covered by a small deterministic contract.
- Cloud mind-clone adapters (Honcho, Mem0, …) — catalog only until explicit install demand; local SQLite facts cover offline deep recall.
- Full multi-profile home isolation — light metadata only until multi-project demand.
