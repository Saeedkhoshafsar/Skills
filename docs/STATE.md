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
| Active task | P3-T4 — make bundled companion activation genuinely zero-configuration. |
| Exact progress | The novice path audit found that SMART's own companions still fell through the standalone third-party quarantine path. The unified installer now recognizes six bundled companions, adds SMART's trusted marketplace when absent, and installs or updates only the selected native plugin. Existing marketplace/plugin state is detected idempotently. Third-party quarantine remains unchanged. |
| Last evidence | Current branch: 50 deterministic tests GREEN; bundled first-party install and idempotency tests GREEN; 8 offline scenarios valid; 9 JSON files valid; Python compile, all Bash syntax, and whitespace checks GREEN. Local ShellCheck was unavailable and remains delegated to required CI. |
| Blocker / waiting on | None for implementation. Required PR checks must confirm ShellCheck and repository validation. |
| Vision Lock | CONFIRMED by repository owner on 2026-07-11: SMART is the central project brain; users activate SMART only and must not manage observer models, evaluator APIs, companion installation, sources, or commands. |
| Machine gates | Vision: owner-confirmed product direction; Verify: 50 local deterministic tests plus required PR checks; Release: N/A for internal orchestration improvement. |
| Branch / head | `genspark_ai_developer`; based on merged PR #11 (`7c7c27b`) with P3-T4 in progress. |

## Epistemic delta
### Newly confirmed
- The repository owner does not want any paid live observer, second model, evaluator API, or related beginner-facing setup — source: explicit owner decision, 2026-07-11.
- Live evaluation was internal QA infrastructure, not part of SMART's product value, and it displaced the core roadmap — source: owner feedback and repository-state review, 2026-07-11.
- PR #11 merged the complete observer/API cleanup at `7c7c27b` — source: Git history, 2026-07-11.
- SMART's six bundled companions are native plugins in the same trusted `saeed-skills` marketplace, so routing them through third-party quarantine was unnecessary friction rather than a safety requirement — source: marketplace manifests and installer audit, 2026-07-11.

### Inferred — confirmation needed
- None. The cleanup scope and core product direction are explicitly confirmed.

### Active assumptions
| Assumption | Why temporary | Validation test | Owner | Expiry/reversal trigger |
|---|---|---|---|---|
| Offline scenario contracts remain useful as free maintainer safeguards. | They describe expected SMART behavior but do not execute a model. | Keep only if their schema validation and review value remain clear and maintenance-light. | Maintainers | They become stale, confusing, or duplicate contract tests. |
| The next highest-value product work after bundled activation is a plain-language third-party approval handoff. | The installer still emits approval mechanics even though SMART promises to own commands and source choices. | Trace quarantine output through SMART's user-facing decision request and add a tested machine-readable handoff that preserves accountable approval. | Maintainers | Audit shows a higher-impact remaining novice-path defect. |

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

## Open errors and risks
| ID | Description | Evidence / location | Impact | Next diagnostic/mitigation | Status |
|---|---|---|---|---|---|
| CORE-001 | The product roadmap was temporarily dominated by live evaluation infrastructure. | Merged PR #11 removed the live runner, paid workflow, observer, secrets, and API setup. | Core SMART improvements were delayed and product intent became unclear. | Keep offline contracts only unless the owner explicitly changes direction. | RESOLVED |
| CORE-002 | Bundled SMART companions were routed through the third-party standalone quarantine path. | Installer aliases and dispatch before P3-T4. | Beginners could encounter unnecessary review/setup mechanics for already trusted first-party plugins. | Merge tested first-party native-plugin routing while preserving third-party quarantine. | IN PROGRESS |
| CORE-003 | Third-party quarantine still exposes approval commands as installer output. | `fetch-skill.sh` quarantine completion output and README maintainer examples. | SMART may relay mechanics instead of presenting one plain-language evidence/approval decision. | Design a machine-readable approval handoff and keep accountable human consent without source/command choices. | OPEN |

## Meaningful change ledger (newest first)
| Date / commit | What changed | Why | Evidence | Records affected |
|---|---|---|---|---|
| 2026-07-11 / current branch | Routed six bundled companions through SMART's trusted native marketplace with idempotent installed-state handling. | Remove companion setup and unnecessary quarantine friction from the beginner path without weakening third-party safety. | 50 tests GREEN; first-party native install and idempotency regressions GREEN; 8 scenarios and 9 JSON files valid; Python compile, Bash syntax, and whitespace GREEN. | SMART contract, installer, tests, README, manifests, changelog, this STATE. |
| 2026-07-11 / PR #11 | Removed live model observation and replaced its runner with an offline-only schema validator. | Restore SMART's zero-configuration product boundary and eliminate paid/API setup. | 47 tests GREEN; 8 scenarios valid; required PR checks GREEN. | Evaluator, workflow template, tests, README, changelog, this STATE. |
| 2026-07-11 / PR #10 | Made semantic observation optional. | Attempted to reduce cost, but retained unnecessary product complexity. | 52 tests and PR checks GREEN; later superseded by owner decision. | Evaluator, workflow template, tests, README, prior STATE. |
| 2026-07-11 / PR #9 | Staged a manual live-evaluation workflow. | Internal QA experiment; later rejected as out of product direction. | PR checks GREEN; superseded by owner decision. | Workflow template, tests, README, prior STATE. |
| 2026-07-11 / PR #8 | Added eight adversarial SMART scenario contracts and a live harness. | Improve behavioral confidence; scenarios remain, live harness is being removed. | Required checks GREEN. | Scenario data, tests, evaluator, versions. |

## Runway
1. **NEXT — complete and merge P3-T4 bundled activation:** Commit one clean change, sync with `origin/main`, push, and require all PR checks GREEN. Completion evidence: native install and idempotency regressions, no companion quarantine, version `2.3.1`, and clean working tree.
2. **THEN — P3-T5 plain-language third-party approval handoff:** Replace command-oriented quarantine completion with structured evidence SMART can translate into one accountable approval decision. Completion evidence: users choose approve/reject in plain language while SMART retains source/command ownership and the installer still fails closed.
3. **THEN — finish the end-to-end novice contract trace:** Cover activation -> understanding -> Vision Lock -> capability decision -> acquisition -> action -> memory consolidation, prioritizing any remaining gap without weakening safety. Completion evidence: deterministic integration contracts and an updated risk-ranked runway.

## Next-session command packet

```bash
cd /home/user/webapp
git fetch origin main
git checkout genspark_ai_developer
python3 -m unittest discover -s tests -v
python3 skills/smart/skills/smart/evals/validate_behavioral_scenarios.py
bash -n skills/smart/skills/smart/scripts/fetch-skill.sh
```

The offline-contract tests also guard against reintroducing network clients, model arguments, evaluator secrets, or a staged live workflow.

## Deferred / debt with activation triggers
- Paid model observation and external evaluation workflows — deliberately removed; reconsider only after an explicit future owner decision, never as a user requirement.
- Multi-model evaluation and semantic scoring — deliberately out of scope.
- Full end-to-end novice-path contract coverage — continue after the P3-T5 approval-handoff gap is closed.
