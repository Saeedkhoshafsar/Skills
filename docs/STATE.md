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
| Active task | P3-T5 — make third-party approval a plain-language decision instead of an installation procedure. |
| Exact progress | PR #12 merged first-party companion auto-install at `6a4c7b2`. The installer now emits a structured `third_party_approval_required` event with immutable provenance, candidate/report paths, status, and residual-risk guidance instead of printing an activation command. SMART's contract requires evidence review, one plain-language approve-or-reject question, and SMART-owned activation only after explicit consent. README command mechanics were removed. |
| Last evidence | Current branch: 51 deterministic tests GREEN; structured handoff, no-command output, quarantine, accountable activation, and SMART interaction contracts GREEN; 8 offline scenarios valid; 9 JSON files valid; all Bash syntax and whitespace checks GREEN. Local ShellCheck remains delegated to required CI. |
| Blocker / waiting on | None for implementation. Required PR checks must confirm ShellCheck and repository validation. |
| Vision Lock | CONFIRMED by repository owner on 2026-07-11: SMART is the central project brain; users activate SMART only and receive understandable decisions rather than evaluator, companion, source, package, or command mechanics. |
| Machine gates | Vision: owner-confirmed product direction; Verify: 51 local deterministic tests plus required PR checks; Release: N/A for internal orchestration improvement. |
| Branch / head | `genspark_ai_developer`; based on merged PR #12 (`6a4c7b2`) with P3-T5 in progress. |

## Epistemic delta
### Newly confirmed
- The repository owner does not want any paid live observer, second model, evaluator API, or related beginner-facing setup — source: explicit owner decision, 2026-07-11.
- Live evaluation was internal QA infrastructure, not part of SMART's product value, and it displaced the core roadmap — source: owner feedback and repository-state review, 2026-07-11.
- PR #11 merged the complete observer/API cleanup at `7c7c27b` — source: Git history, 2026-07-11.
- SMART's six bundled companions are native plugins in the same trusted `saeed-skills` marketplace, so routing them through third-party quarantine was unnecessary friction rather than a safety requirement — source: marketplace manifests and installer audit, 2026-07-11.
- PR #12 merged the bundled companion auto-install path at `6a4c7b2` with both required validation checks GREEN — source: GitHub PR state and Git history, 2026-07-11.
- Accountable third-party approval does not require exposing installation mechanics: SMART can consume a structured evidence handoff, explain risk, collect one explicit decision, and invoke the locked activation itself — source: P3-T5 implementation and tests, 2026-07-11.

### Inferred — confirmation needed
- None. The cleanup scope and core product direction are explicitly confirmed.

### Active assumptions
| Assumption | Why temporary | Validation test | Owner | Expiry/reversal trigger |
|---|---|---|---|---|
| Offline scenario contracts remain useful as free maintainer safeguards. | They describe expected SMART behavior but do not execute a model. | Keep only if their schema validation and review value remain clear and maintenance-light. | Maintainers | They become stale, confusing, or duplicate contract tests. |
| The next highest-value work after P3-T5 is completing the end-to-end novice contract trace. | First-party activation and third-party consent are now individually covered, but the whole activation-to-consolidation path remains layered. | Trace SMART activation through understanding, Vision Lock, capability action, and durable memory; add only the smallest missing integration contracts. | Maintainers | A higher-severity safety or orchestration defect appears. |

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
| CORE-003 | Third-party quarantine exposed approval commands as installer output. | P3-T5 structured handoff and SMART interaction contract. | SMART could relay mechanics instead of presenting one plain-language evidence/approval decision. | Merge P3-T5 after required checks; preserve explicit consent and fail-closed quarantine. | IN PROGRESS |
| CORE-004 | The novice orchestration path is still verified mostly as layered contracts rather than one trace. | SMART, installer, gates, and memory tests cover components independently. | A handoff gap between project understanding, capability action, and durable consolidation may remain hidden. | Perform a narrow end-to-end contract trace after P3-T5. | OPEN |

## Meaningful change ledger (newest first)
| Date / commit | What changed | Why | Evidence | Records affected |
|---|---|---|---|---|
| 2026-07-11 / current branch | Replaced third-party activation command output with a structured SMART approval handoff and a one-decision interaction contract. | Preserve accountable human consent while keeping source, package, and command mechanics inside SMART. | 51 tests GREEN; handoff/no-command/quarantine/consent contracts GREEN; 8 scenarios and 9 JSON files valid; Bash syntax and whitespace GREEN. | SMART contract, installer, tests, README, manifests, changelog, this STATE. |
| 2026-07-11 / PR #12 | Routed six bundled companions through SMART's trusted native marketplace with idempotent installed-state handling. | Remove companion setup and unnecessary quarantine friction from the beginner path without weakening third-party safety. | 50 tests and both required checks GREEN. | SMART contract, installer, tests, README, manifests, changelog, prior STATE. |
| 2026-07-11 / PR #11 | Removed live model observation and replaced its runner with an offline-only schema validator. | Restore SMART's zero-configuration product boundary and eliminate paid/API setup. | 47 tests GREEN; 8 scenarios valid; required PR checks GREEN. | Evaluator, workflow template, tests, README, changelog, this STATE. |
| 2026-07-11 / PR #10 | Made semantic observation optional. | Attempted to reduce cost, but retained unnecessary product complexity. | 52 tests and PR checks GREEN; later superseded by owner decision. | Evaluator, workflow template, tests, README, prior STATE. |
| 2026-07-11 / PR #9 | Staged a manual live-evaluation workflow. | Internal QA experiment; later rejected as out of product direction. | PR checks GREEN; superseded by owner decision. | Workflow template, tests, README, prior STATE. |
| 2026-07-11 / PR #8 | Added eight adversarial SMART scenario contracts and a live harness. | Improve behavioral confidence; scenarios remain, live harness is being removed. | Required checks GREEN. | Scenario data, tests, evaluator, versions. |

## Runway
1. **NEXT — complete and merge P3-T5 approval handoff:** Squash to one commit, sync with `origin/main`, push, and require all checks GREEN. Completion evidence: structured handoff, no runtime approval command, explicit-consent contract, version `2.3.2`, and clean working tree.
2. **THEN — P3-T6 end-to-end novice contract trace:** Cover activation -> understanding -> Vision Lock -> capability decision -> acquisition -> action -> memory consolidation. Completion evidence: a code-linked gap map and deterministic integration coverage for the highest-impact missing transition.
3. **THEN — implement only the next proven gap:** Prefer a small contract/tooling correction over new infrastructure; preserve zero-configuration, Vision Lock, fail-closed supply-chain review, and durable memory. Completion evidence: focused regression, updated STATE, and required PR checks GREEN.

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
- Full end-to-end novice-path contract coverage — activate immediately after P3-T5 merges.
