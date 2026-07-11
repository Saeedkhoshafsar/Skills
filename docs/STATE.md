# STATE — SMART Skill-Manager Ecosystem

> Resume index for cross-session continuity. The product contract lives in
> `skills/smart/skills/smart/SKILL.md`; capability decisions live in
> `SKILLS_CATALOG.md`; offline adversarial contracts live in
> `skills/smart/skills/smart/evals/scenarios.json`.

## Resume packet
| Field | Current value |
|---|---|
| SMART mode / lifecycle phase | STABILIZATION / 3 |
| Current objective | Keep SMART the zero-configuration project brain that understands the project and autonomously manages the minimum useful skill set. |
| Active task | P3-T3 — remove the live observer/API detour and restore product focus. |
| Exact progress | Owner explicitly rejected paid or separately configured model observation. The staged live workflow is removed; the network/model runner is replaced by a deterministic offline scenario validator; API, secret, endpoint, and model-selection instructions are removed. PR #10 had already merged before cleanup began, so this branch cleanly reverses both PR #9 and PR #10 live-evaluation direction from current `main`. |
| Last evidence | Cleanup branch: 47 deterministic tests GREEN; 8 offline scenarios valid; Python compile, all JSON parsing, shell syntax, and whitespace checks GREEN. |
| Blocker / waiting on | None for offline development. No API key, paid evaluator, Actions secret, or workflow permission is required. |
| Vision Lock | CONFIRMED by repository owner on 2026-07-11: SMART is the central project brain; users activate SMART only and must not manage observer models or evaluation APIs. |
| Machine gates | Vision: owner-confirmed product direction; Verify: complete local tests plus required PR checks; Release: N/A for internal cleanup. |
| Branch / head | `genspark_ai_developer`; cleanup follow-up from merged PR #10 |

## Epistemic delta
### Newly confirmed
- The repository owner does not want any paid live observer, second model, evaluator API, or related beginner-facing setup — source: explicit owner decision, 2026-07-11.
- Live evaluation was internal QA infrastructure, not part of SMART's product value, and it displaced the core roadmap — source: owner feedback and repository-state review, 2026-07-11.
- PR #10 merged at `74362b5` before it could be closed — source: GitHub API, 2026-07-11.

### Inferred — confirmation needed
- None. The cleanup scope and core product direction are explicitly confirmed.

### Active assumptions
| Assumption | Why temporary | Validation test | Owner | Expiry/reversal trigger |
|---|---|---|---|---|
| Offline scenario contracts remain useful as free maintainer safeguards. | They describe expected SMART behavior but do not execute a model. | Keep only if their schema validation and review value remain clear and maintenance-light. | Maintainers | They become stale, confusing, or duplicate contract tests. |
| The next highest-value product work is a zero-configuration orchestration audit. | The observer detour interrupted core product sequencing. | Trace a novice request from SMART activation through capability selection, installation, action, and durable consolidation; turn gaps into tested tasks. | Maintainers | A more severe core-product defect is discovered. |

### Unknowns / conflicts
| Item | Impact if wrong | Resolution action | Status |
|---|---|---|---|
| Which remaining friction most harms a first-time SMART user | Determines the next implementation task. | Run a repository-level zero-configuration path audit after this cleanup, then prioritize by user impact and safety. | OPEN, NON-BLOCKING |

## Capability inventory
| Capability | Type/source | Status | Invoked when | Last result / review |
|---|---|---|---|---|
| SMART orchestrator | Local skill | ACTIVE CORE | Every user project | Product contract requires evidence-aware orientation, Vision Lock, autonomous capability selection, action, and consolidation. |
| Unified capability installer | Local shell/Python tooling | VERIFIED | SMART needs a standalone skill or native plugin | Trusted quarantine, review, lock, and update tests are present. |
| Machine gates | Local Python tooling | VERIFIED | Vision confirmation, task verification, release readiness | Deterministic gate tests are present. |
| Offline behavioral contracts | JSON + Python stdlib validator | ACTIVE, FREE | Maintainers edit adversarial scenario definitions | No network, model, secret, endpoint, or paid workflow. |

## Open errors and risks
| ID | Description | Evidence / location | Impact | Next diagnostic/mitigation | Status |
|---|---|---|---|---|---|
| CORE-001 | The product roadmap was temporarily dominated by live evaluation infrastructure. | Merged PRs #9 and #10 plus prior STATE runway. | Core SMART improvements were delayed and project intent became unclear. | Remove the detour, document the owner-confirmed product boundary, then audit the novice orchestration path. | IN PROGRESS |
| CORE-002 | Zero-configuration orchestration is promised across several documents but has not yet been traced as one end-to-end contract. | SMART, catalog, installer, and local skill contracts are tested mostly in layers. | Integration friction may remain hidden from first-time users. | Perform an end-to-end contract audit and add the smallest deterministic integration coverage needed. | OPEN |

## Meaningful change ledger (newest first)
| Date / commit | What changed | Why | Evidence | Records affected |
|---|---|---|---|---|
| 2026-07-11 / current branch | Removed live model observation and replaced its runner with an offline-only schema validator. | Restore SMART's zero-configuration product boundary and eliminate paid/API setup. | 47 tests GREEN; 8 scenarios valid; Python compile, JSON, shell syntax, and whitespace checks GREEN. | Evaluator, workflow template, tests, README, changelog, this STATE. |
| 2026-07-11 / PR #10 | Made semantic observation optional. | Attempted to reduce cost, but retained unnecessary product complexity. | 52 tests and PR checks GREEN; later superseded by owner decision. | Evaluator, workflow template, tests, README, prior STATE. |
| 2026-07-11 / PR #9 | Staged a manual live-evaluation workflow. | Internal QA experiment; later rejected as out of product direction. | PR checks GREEN; superseded by owner decision. | Workflow template, tests, README, prior STATE. |
| 2026-07-11 / PR #8 | Added eight adversarial SMART scenario contracts and a live harness. | Improve behavioral confidence; scenarios remain, live harness is being removed. | Required checks GREEN. | Scenario data, tests, evaluator, versions. |

## Runway
1. **NEXT — complete and merge P3-T3 cleanup:** Run all deterministic tests, verify that no live evaluator/API/secret/workflow path remains, and merge one clean PR. Completion evidence: required checks GREEN, no paid-evaluation configuration in product docs or code, and clean working tree.
2. **THEN — P3-T4 zero-configuration path audit:** Trace activation -> project understanding -> Vision Lock -> capability decision -> safe acquisition -> action -> memory consolidation for a novice user. Completion evidence: a gap list ranked by user impact, with each claim linked to code or contract evidence.
3. **THEN — implement the highest-value core gap:** Add the smallest tested change that reduces novice friction without weakening Vision Lock, supply-chain review, or release safety. Completion evidence: deterministic regression coverage, updated product contract/state, and required PR checks GREEN.

## Next-session command packet

```bash
cd /home/user/webapp
git fetch origin main
git checkout genspark_ai_developer
python3 -m unittest discover -s tests -v
python3 skills/smart/skills/smart/evals/validate_behavioral_scenarios.py
```

The offline-contract tests also guard against reintroducing network clients, model arguments, evaluator secrets, or a staged live workflow.

## Deferred / debt with activation triggers
- Paid model observation and external evaluation workflows — deliberately removed; reconsider only after an explicit future owner decision, never as a user requirement.
- Multi-model evaluation and semantic scoring — deliberately out of scope.
- End-to-end zero-configuration contract coverage — activate immediately after P3-T3 cleanup.
