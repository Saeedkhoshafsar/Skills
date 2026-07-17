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
| Active task | None — **2.5.17** SHIPPED (PR #26 + Release `v2.5.17`): Depth Reprocess + evidence-rooted trees. |
| Exact progress | Depth L0–L4 + truth/creative trunks; 36 scenarios; pin **2.5.17**. PR #26 merged (`e827b4d`); Release Latest. |
| Last evidence | 2026-07-18: PR #26 MERGED validate GREEN; unittest **225 OK** / scenarios **36 valid**; Release https://github.com/Saeedkhoshafsar/Skills/releases/tag/v2.5.17 |
| Blocker / waiting on | None. Consumer: marketplace update → plugin update → pin **2.5.17** → `/smart:smart`. |
| Next | Consumer pin **2.5.17**; field-validate depth/honesty only if a new gap appears. |
| Vision Lock | CONFIRMED by repository owner on 2026-07-11 (reaffirmed and extended): complete project control brain; mind before code; excellence by default; lean orchestration. Extended 2026-07-18: depth over first-pass polish; creativity ≠ truth (evidence-rooted trees). |
| Machine gates | Vision: owner-confirmed; Verify: suite; Release: `v2.5.17` Latest published. |
| Branch / head | `main` @ SMART `2.5.17` shipped (`e827b4d`). |
| Mind coverage | Applied to this repo implicitly via STATE/BRIEF equivalents; the formal PROJECT-MIND protocol targets user projects. |

## Epistemic delta
### Newly confirmed
- PR #26 merged to `main` (`e827b4d`) with validate GREEN — Depth Reprocess + evidence-rooted trees SMART 2.5.17 — source: GitHub PR state, 2026-07-18.
- Release `v2.5.17` published Latest — source: GitHub Releases, 2026-07-18.
- Owner: first-pass “max effort” is still shallow; multi-layer reprocess required — source: owner messages 2026-07-18.
- Owner: creativity must stay free but never be labeled as truth; no false confidence / training-frequency roots — source: owner messages 2026-07-18.
- Public arena pattern: autonomous music-video agents under-spend self-critique (TryAI) — source: https://www.tryai.dev/blog/ai-music-video-arena-claude-vs-gpt-5.6 .
- PR #25 merged — SMART 2.5.16 scroll-world + `/smart:smart` — source: GitHub, 2026-07-17.
- Release `v2.5.16` published — source: GitHub Releases, 2026-07-17.
- Claude Code plugin skills/commands are **always** namespaced `/plugin:name`; bare `/smart` does not resolve — source: code.claude.com plugins docs + field report, 2026-07-17.
- `scroll-world` upstream layout confirmed: `skills/scroll-world/SKILL.md` + `references/*` at main — source: git fetch of `oso95/scroll-world`, 2026-07-17.
- PR #24 merged to `main` (`ae96ee6`) with validate GREEN — resume-check table/fence fix SMART 2.5.15 — source: GitHub PR state, 2026-07-17.
- Release `v2.5.15` published Latest — source: GitHub Releases, 2026-07-17.
- PR #23 merged to `main` (`22b6642`) with validate GREEN — discovery elevation SMART 2.5.14 / project-planner 1.4.0 — source: GitHub PR state, 2026-07-17.
- PR #22 merged to `main` (`8b11a8e`) with validate GREEN — Hermes learning-memory MVP SMART 2.5.13 / project-memory 1.11.0 — source: GitHub PR state, 2026-07-17.
- PR #21 merged to `main` (`6befc8a`) with required checks GREEN — source: GitHub PR state, 2026-07-16.
- Owner granted full delivery authority for a stable final Skills project on GitHub including public releases and install polish — source: explicit owner directive, 2026-07-16.
- Marketplace root `metadata.version` must track the current SMART release pin — source: marketplace audit, 2026-07-16.
- The `/smart` command must prefer `docs/STATE2.md` over `docs/STATE.md` to match the SMART SENSE contract — source: command vs SKILL audit, 2026-07-16.

### Inferred — confirmation needed
- None for the ship path.

### Active assumptions
| Assumption | Why temporary | Validation test | Owner | Expiry/reversal trigger |
|---|---|---|---|---|
| Offline scenario contracts remain useful as free maintainer safeguards. | They describe expected SMART behavior but do not execute a model. | Keep only if their schema validation and review value remain clear and maintenance-light. | Maintainers | They become stale, confusing, or duplicate contract tests. |
| A compact fast path is sufficient for coherent projects; the full loop should be event-triggered. | Excessive control-plane ceremony can delay the user-visible project outcome. | Require same-invocation action, at most one additional capability, fresh verification, and delta-only memory on the healthy path; retain deep gates only for explicit triggers. | Maintainers | Evidence shows a healthy project needed deeper orientation to avoid a material error. |

### Unknowns / conflicts
| Item | Impact if wrong | Resolution action | Status |
|---|---|---|---|
| Exact Claude CLI JSON shape across supported versions | Incorrect detection could cause a redundant add/install attempt. | Keep detection fail-safe and confirm required CI; later replace text matching with stable CLI fields if Claude publishes a versioned schema. | OPEN, NON-BLOCKING |

## Capability inventory
| Capability | Type/source | Status | Invoked when | Last result / review |
|---|---|---|---|---|
| SMART orchestrator | Local skill | ACTIVE CORE | Every user project | Product contract requires evidence-aware orientation, Vision Lock, autonomous capability selection, action, and consolidation. |
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
| CORE-001 | The product roadmap was temporarily dominated by live evaluation infrastructure. | Merged PR #11 removed the live runner, paid workflow, observer, secrets, and API setup. | Core SMART improvements were delayed and product intent became unclear. | Keep offline contracts only unless the owner explicitly changes direction. | RESOLVED |
| CORE-002 | Bundled SMART companions were routed through the third-party standalone quarantine path. | PR #12 routes six companions through trusted native-plugin installation with idempotency coverage. | Beginners could encounter unnecessary review/setup mechanics for already trusted first-party plugins. | Keep third-party quarantine separate and retain first-party routing regressions. | RESOLVED |
| CORE-003 | Third-party quarantine exposed approval commands as installer output. | PR #13 merged the structured handoff, explicit-consent contract, and no-command runtime behavior. | SMART could relay mechanics instead of presenting one plain-language evidence/approval decision. | Preserve fail-closed quarantine and accountable activation regressions. | RESOLVED |
| CORE-004 | SMART's full ten-stage loop and large report were framed as mandatory on every invocation. | PR #14 merged the progress-first fast path and one-pass Step Pilot at `f455f9a`. | The control layer could consume the session, repeatedly re-orient, and slow or prevent actual project progress. | Fast path is now the default; retain explicit escalation triggers and fast-path regressions. | RESOLVED |
| CORE-006 | Output quality for novices depended on the user knowing what to ask for. | Excellence-by-default contract. | The core product promise was not contractually guaranteed. | PR #15 merged; keep quality-bar regressions. | RESOLVED |
| CORE-007 | SMART's product understanding lived in prose records and conversation. | Project Mind protocol + coverage-gated Vision Lock. | Resume-time gaps could send a project down the wrong path. | PR #16 merged; keep mind-coverage regressions. | RESOLVED |
| CORE-008 | Mid-mission progress and late-session context pressure could vanish without chat history. | M-T2 + M-T3 on main (`2.5.3`/`2.5.4`). | Zero-context resume could rebuild ceremony or lose progress. | Keep mid-mission, budget, archive, and pre-existing bootstrap contracts. | RESOLVED |
| CORE-005 | Workflow updates may be rejected when the GitHub credential lacks `workflows` permission. | Prior push rejection and owner instruction. | Repeated retries can block unrelated product progress. | Stage exact workflow files under `ci/` and report the manual replacement after the PR. | MITIGATED |
| SHIP-001 | GitHub Releases lagged code on main. | Release list audit 2026-07-16. | Marketplace consumers could stay on older pins. | Publish `v2.5.2`–`v2.5.4` and document the two-step update path. | RESOLVED |
| SHIP-002 | Learning-memory code (2.5.6–2.5.13) lagged releases after v2.5.5. | Main audit 2026-07-17 pre-ship. | Install pin could stay on host-command-only build. | PR #22 + Release `v2.5.13` Latest. | RESOLVED |
| SHIP-003 | Discovery elevation (2.5.14) code on main before GitHub Release. | PR #23 merge audit 2026-07-17. | Marketplace pin could lag Stage 1.5 landscape/budget gates. | Release `v2.5.14` Latest + STATE ship. | RESOLVED |
| SHIP-004 | Resume-check false RED on real table STATE (later bash fence). | Field validation 2026-07-17 pre-2.5.15. | Host supervision / handoff could refuse compact wrongly. | PR #24 + Release `v2.5.15`. | RESOLVED |
| SHIP-005 | Docs claimed bare `/smart` works; scroll-world missing from SMART catalog. | Field report + oso95/scroll-world review 2026-07-17. | Users hit dead `/smart`; SMART could not select cinematic scroll landings. | PR #25 + Release `v2.5.16`. | RESOLVED |
| SHIP-006 | Single-pass fluent confidence; creative branches mislabeled as truth. | Owner philosophy + TryAI arena lessons 2026-07-18. | Shallow maxed-looking work; false confidence trees. | PR #26 + Release `v2.5.17`. | RESOLVED |

## Meaningful change ledger (newest first)
| Date / commit | What changed | Why | Evidence | Records affected |
|---|---|---|---|---|
| 2026-07-18 / 2.5.17 ship | PR #26 merge + Release v2.5.17 | Pin install to Depth Reprocess + evidence-rooted trees | 225 tests / 36 scenarios; `e827b4d` | RELEASE, STATE, marketplace pin. |
| 2026-07-18 / 2.5.17 depth+honesty | Depth L0–L4; truth vs creative trunks; scenarios+contracts; pin 2.5.17 | Surface pass ≠ maxed; creativity ≠ truth | 225 tests / 36 scenarios; validate GREEN | SMART, step-pilot, planner, tests, changelog, RELEASE, STATE. |
| 2026-07-17 / 2.5.16 ship | PR #25 merge + Release v2.5.16 | Pin Claude Code install to scroll-world catalog + `/smart:smart` honesty | 223 tests / 33 scenarios; `822947b` | RELEASE notes, STATE, marketplace pin. |
| 2026-07-17 / 2.5.16 catalog + slash | scroll-world alias + YELLOW profile; bare `/smart` claims removed; contract tests; pin 2.5.16 | Capability gap + slash confusion | 223 tests / 33 scenarios; validate GREEN | fetch-skill, catalog, SMART, README, command, tests, changelog, RELEASE, marketplace, STATE. |
| 2026-07-17 / 2.5.15 ship | PR #24 merge + Release v2.5.15 | Pin Claude Code install to resume-check field fix | 219 tests / 33 scenarios; `ae96ee6` | RELEASE notes, STATE, marketplace pin. |
| 2026-07-17 / 2.5.15 field fix | `extract_resume_packet` section-bound + table support; regression test; pin 2.5.15 | Real STATE failed resume-check via later bash fence (host supervision) | 219 tests / 33 scenarios; resume-check READY | smart-gates, tests, changelog, RELEASE, marketplace, STATE. |
| 2026-07-17 / 2.5.14 ship | PR #23 merge + Release v2.5.14 | Pin Claude Code install to discovery elevation | 218 tests / 33 scenarios; `22b6642` | RELEASE notes, STATE, marketplace pin. |
| 2026-07-17 / 2.5.14 discovery elevation | Stage 1.5 landscape research + budget×quality + specialist routing; anti multi-agent company | Real projects need research and budget-fit quality before code without MetaGPT runtime | contract + 2 scenarios (33 total) | smart, project-planner, scenarios, tests, changelog, STATE, README. |
| 2026-07-17 / 2.5.13 ship | PR #22 merge + description sync + Release v2.5.13 | Make Claude Code install pin match learning-memory MVP | 217 tests / 31 scenarios; merged commit 8b11a8e | marketplace, plugin.json, STATE, README, RELEASE notes. |
| 2026-07-17 / 2.5.13 Phase 8 | identity_store SOUL/personality/profiles/dashboard/migrate; SMART step 12; CLAUDE #22; README; tests + 2 scenarios. | Operator UX + identity without breaking product truth. | unit/CLI/contract tests + scenarios; plan P8 checkboxes | project-memory, SMART, marketplace, tests, scenarios, changelog, HERMES-PORT-PLAN, STATE, CLAUDE, README. |
| 2026-07-17 / 2.5.12 Phase 7 | memory_provider ABC + fence; memory_manager one-external; builtin/null/local; config memory.provider; catalog; tests + 2 scenarios. | Pluggable deep personalization without core bloat; CI offline. | unit/CLI/contract tests + scenarios; plan P7 checkboxes | project-memory, SMART, marketplace, tests, scenarios, changelog, HERMES-PORT-PLAN, STATE. |
| 2026-07-17 / 2.5.11 Phase 6 | session_store.py FTS5/LIKE; discovery/scroll/browse; redaction; extract-durable; prefer always-on first; tests + 2 scenarios. | Unlimited episodic recall without bloating USER/AGENT-MEMORY. | unit/CLI/contract tests + scenarios; plan P6 checkboxes | project-memory, SMART, marketplace, tests, scenarios, changelog, HERMES-PORT-PLAN, STATE. |
| 2026-07-17 / 2.5.10 Phase 5 | skill_curator.py + lifecycle transitions; archive path; pin; protected; idle gate; consolidate OFF; tests + 2 scenarios. | Agent-created skill library must not rot; never auto-delete. | unit/CLI/contract tests + scenarios; plan P5 checkboxes | project-memory, SMART, marketplace, tests, scenarios, changelog, HERMES-PORT-PLAN, STATE. |
| 2026-07-17 / 2.5.9 Phase 4 | skill_usage.py + skill-usage.json; patch-on-correction; authoring ≤60; support layout; learn protocol; agent-created threat scan; tests + 2 scenarios. | How-to lessons must land in skills, not only USER.md; protected builtins never deleted. | unit/CLI tests + scenarios; plan P4 checkboxes | project-memory, SMART, marketplace, tests, scenarios, changelog, HERMES-PORT-PLAN, STATE. |
| 2026-07-17 / 2.5.8 Phase 3 | Self-learning loop: loop-state counters, intervals 10/15, memory/skill review protocols, non-blocking consolidate, tests + 2 scenarios. | Multi-turn personalization without explicit “remember this” every time. | unit/CLI tests + scenarios; plan P3 checkboxes | project-memory, SMART, marketplace, tests, scenarios, changelog, HERMES-PORT-PLAN, STATE. |
| 2026-07-17 / 2.5.7 Phase 2 | Threat scan + write_approval pending queue. | Poisoned always-on memory and unreviewed auto-saves. | unit/CLI tests + scenarios | project-memory, SMART, marketplace, tests, scenarios, changelog, HERMES-PORT-PLAN, STATE. |
| 2026-07-17 / 2.5.6 Phase 1 | Dual learning-memory stores USER + AGENT-MEMORY. | Hermes closed-loop personalization separate from Project Mind. | unit/CLI tests + scenarios | project-memory, SMART, marketplace, tests, scenarios, changelog, HERMES-PORT-PLAN, STATE. |
| 2026-07-17 / Phase 0 lock | Hermes port Phase 0 defaults frozen. | Need frozen contracts before dual-store implementation. | HERMES-PORT-PLAN §4 Phase 0 | HERMES-PORT-PLAN, STATE. |
| 2026-07-16 / 2.5.5 | Native Claude Code host-command supervision. | SMART masters slash surface. | contract tests + scenarios | catalog, SMART, CLAUDE, command, tests, scenarios, changelog, STATE. |

## Runway
1. **INSTALL (consumer):** `claude plugin marketplace update saeed-skills && claude plugin update smart@saeed-skills` (+ step-pilot / project-planner if installed) → confirm **2.5.17** → restart → **`/smart:smart`**.
2. **NEXT — field-validate** Depth Reprocess + creative≠truth labeling under real paid-gen/creative work if a gap appears.
3. **LATER — optional DB-schema skill** only if product database design keeps recurring as a real gap.
4. **LATER — Phase 9 product-surface backlog** only with explicit owner request.
5. **LATER — full multi-home / cloud memory adapters** on demand.
6. **LATER — periodic catalog refresh + proven bottlenecks only.**

## Next-session command packet

```bash
cd /home/samansofi2028/.claude/plugins/marketplaces/saeed-skills
git fetch origin main && git checkout main && git pull --ff-only
python3 -m unittest discover -s tests -v
python3 skills/smart/skills/smart/evals/validate_behavioral_scenarios.py
bash -n skills/smart/skills/smart/scripts/fetch-skill.sh
# consumers already installed:
# claude plugin marketplace update saeed-skills && claude plugin update smart@saeed-skills
```

The offline-contract tests also guard against reintroducing network clients, model arguments, evaluator secrets, or a staged live workflow.

## Deferred / debt with activation triggers
- Paid model observation and external evaluation workflows — deliberately removed; reconsider only after an explicit future owner decision, never as a user requirement.
- Multi-model evaluation and semantic scoring — deliberately out of scope.
- Broad end-to-end simulation framework — deliberately avoided unless a concrete transition cannot be covered by a small deterministic contract.
- Cloud mind-clone adapters (Honcho, Mem0, …) — catalog only until explicit install demand; local SQLite facts cover offline deep recall.
- Full multi-profile home isolation — light metadata only until multi-project demand.
