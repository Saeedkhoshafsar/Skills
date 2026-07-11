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
| Active task | P3-T6 — make SMART progress-first and fast on healthy projects without weakening safety gates. |
| Exact progress | PR #13 merged plain-language third-party approval at `118bf75`. The end-to-end trace found the next bottleneck in SMART itself: the detailed ten-stage loop and full report were phrased as mandatory every invocation. SMART now defaults to a one-pass fast path when STATE/gates/task are coherent, activates at most one additional capability, advances project work in the same invocation, verifies, and writes only the memory delta. Step Pilot likewise collapses healthy execution into one internal pass. Restricted workflow edits are staged under `ci/` with a precise manual destination instead of blocking work. |
| Last evidence | Current branch: 54 deterministic tests GREEN; SMART fast path, one-pass Step Pilot, restricted-workflow staging, safety gates, and existing installer contracts GREEN; 8 offline scenarios valid; 9 JSON files valid; all Bash syntax and whitespace checks GREEN. Local ShellCheck remains delegated to required CI. |
| Blocker / waiting on | None for implementation. Required PR checks must confirm ShellCheck and repository validation. |
| Vision Lock | CONFIRMED by repository owner on 2026-07-11: SMART must be the complete project control brain while remaining lean enough that orchestration never stalls or materially slows project progress. |
| Machine gates | Vision: owner-confirmed product direction; Verify: 54 local deterministic tests plus required PR checks; Release: N/A for internal orchestration improvement. |
| Branch / head | `genspark_ai_developer`; based on merged PR #13 (`118bf75`) with P3-T6 in progress. |

## Epistemic delta
### Newly confirmed
- The repository owner does not want any paid live observer, second model, evaluator API, or related beginner-facing setup — source: explicit owner decision, 2026-07-11.
- Live evaluation was internal QA infrastructure, not part of SMART's product value, and it displaced the core roadmap — source: owner feedback and repository-state review, 2026-07-11.
- PR #11 merged the complete observer/API cleanup at `7c7c27b` — source: Git history, 2026-07-11.
- SMART's six bundled companions are native plugins in the same trusted `saeed-skills` marketplace, so routing them through third-party quarantine was unnecessary friction rather than a safety requirement — source: marketplace manifests and installer audit, 2026-07-11.
- PR #12 merged the bundled companion auto-install path at `6a4c7b2` with both required validation checks GREEN — source: GitHub PR state and Git history, 2026-07-11.
- Accountable third-party approval does not require exposing installation mechanics: SMART can consume a structured evidence handoff, explain risk, collect one explicit decision, and invoke the locked activation itself — source: P3-T5 implementation and tests, 2026-07-11.
- PR #13 merged that approval handoff at `118bf75` with both required checks GREEN — source: GitHub PR state and Git history, 2026-07-11.
- The owner explicitly requires SMART to be highly capable but operationally lean: it must orient quickly, establish control through companion capabilities, and advance real project work rather than consume the session with its own ceremony — source: owner clarification, 2026-07-11.
- When credentials cannot modify `.github/workflows/*`, ready-to-copy workflow files should be staged elsewhere and reported as an exact manual source-to-destination action after the PR — source: owner instruction, 2026-07-11.

### Inferred — confirmation needed
- None. The cleanup scope and core product direction are explicitly confirmed.

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

## Open errors and risks
| ID | Description | Evidence / location | Impact | Next diagnostic/mitigation | Status |
|---|---|---|---|---|---|
| CORE-001 | The product roadmap was temporarily dominated by live evaluation infrastructure. | Merged PR #11 removed the live runner, paid workflow, observer, secrets, and API setup. | Core SMART improvements were delayed and product intent became unclear. | Keep offline contracts only unless the owner explicitly changes direction. | RESOLVED |
| CORE-002 | Bundled SMART companions were routed through the third-party standalone quarantine path. | PR #12 routes six companions through trusted native-plugin installation with idempotency coverage. | Beginners could encounter unnecessary review/setup mechanics for already trusted first-party plugins. | Keep third-party quarantine separate and retain first-party routing regressions. | RESOLVED |
| CORE-003 | Third-party quarantine exposed approval commands as installer output. | PR #13 merged the structured handoff, explicit-consent contract, and no-command runtime behavior. | SMART could relay mechanics instead of presenting one plain-language evidence/approval decision. | Preserve fail-closed quarantine and accountable activation regressions. | RESOLVED |
| CORE-004 | SMART's full ten-stage loop and large report were framed as mandatory on every invocation. | SMART contract before P3-T6 plus owner feedback. | The control layer could consume the session, repeatedly re-orient, and slow or prevent actual project progress. | Merge the progress-first fast path and one-pass Step Pilot while retaining explicit escalation triggers. | IN PROGRESS |
| CORE-005 | Workflow updates may be rejected when the GitHub credential lacks `workflows` permission. | Prior push rejection and owner instruction. | Repeated retries can block unrelated product progress. | Stage exact workflow files under `ci/` and report the manual `ci/<file> -> .github/workflows/<file>` action after the PR. | MITIGATED |

## Meaningful change ledger (newest first)
| Date / commit | What changed | Why | Evidence | Records affected |
|---|---|---|---|---|
| 2026-07-11 / current branch | Added a progress-first healthy-project path, one-pass Step Pilot execution, compact reporting, and restricted-workflow staging policy. | Keep SMART authoritative without letting its own process delay real project progress. | 54 tests GREEN; fast-path/staging/safety contracts GREEN; 8 scenarios and 9 JSON files valid; Bash syntax and whitespace GREEN. | SMART, Step Pilot, agent contract, tests, README, manifests, changelog, this STATE. |
| 2026-07-11 / PR #13 | Replaced third-party activation command output with a structured SMART approval handoff and a one-decision interaction contract. | Preserve accountable human consent while keeping source, package, and command mechanics inside SMART. | 51 tests and both required checks GREEN. | SMART contract, installer, tests, README, manifests, changelog, prior STATE. |
| 2026-07-11 / PR #12 | Routed six bundled companions through SMART's trusted native marketplace with idempotent installed-state handling. | Remove companion setup and unnecessary quarantine friction from the beginner path without weakening third-party safety. | 50 tests and both required checks GREEN. | SMART contract, installer, tests, README, manifests, changelog, prior STATE. |
| 2026-07-11 / PR #11 | Removed live model observation and replaced its runner with an offline-only schema validator. | Restore SMART's zero-configuration product boundary and eliminate paid/API setup. | 47 tests GREEN; 8 scenarios valid; required PR checks GREEN. | Evaluator, workflow template, tests, README, changelog, this STATE. |
| 2026-07-11 / PR #10 | Made semantic observation optional. | Attempted to reduce cost, but retained unnecessary product complexity. | 52 tests and PR checks GREEN; later superseded by owner decision. | Evaluator, workflow template, tests, README, prior STATE. |
| 2026-07-11 / PR #9 | Staged a manual live-evaluation workflow. | Internal QA experiment; later rejected as out of product direction. | PR checks GREEN; superseded by owner decision. | Workflow template, tests, README, prior STATE. |
| 2026-07-11 / PR #8 | Added eight adversarial SMART scenario contracts and a live harness. | Improve behavioral confidence; scenarios remain, live harness is being removed. | Required checks GREEN. | Scenario data, tests, evaluator, versions. |

## Runway
1. **NEXT — complete and merge P3-T6 progress-first orchestration:** Squash to one commit, sync with `origin/main`, push, and require all checks GREEN. Completion evidence: healthy continuations advance work in one pass, compact report, one-capability default, version `2.3.3` / Step Pilot `1.2.1`, and clean tree.
2. **THEN — trace cold-start control establishment:** Verify a novice can activate SMART once, establish planner/memory, reach a truthful next action quickly, and avoid loading execution capabilities before Vision Lock. Completion evidence: one narrow contract test or a documented no-change conclusion; no new framework.
3. **THEN — continue only on a proven bottleneck:** Prefer deletion, simplification, or a focused contract correction over new infrastructure. Completion evidence: measurable reduction in friction without weakening Vision Lock, verification, supply-chain, or release gates.

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
- Broad end-to-end simulation framework — deliberately avoided unless a concrete transition cannot be covered by a small deterministic contract.
