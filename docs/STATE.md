# STATE — SMART Skill-Manager Ecosystem

> Resume index for cross-session continuity. The product contract lives in
> `skills/smart/skills/smart/SKILL.md`; capability decisions live in
> `SKILLS_CATALOG.md`; offline adversarial contracts live in
> `skills/smart/skills/smart/evals/scenarios.json`.

## Resume packet
| Field | Current value |
|---|---|
| SMART mode / lifecycle phase | MAINTENANCE / 5 |
| Current objective | Make SMART the "super brain": one activation gives a novice expert-team output quality, while orchestration stays lean enough never to slow the real project. |
| Active task | M-T1 — fix the two friction points from the first real-world usage report (Codespaces cold start). |
| Exact progress | P3-T8 merged as PR #16: Project Mind network is on `main` at `2.5.0`. P3-T9 executed the planned cold-start field test on a disposable empty repo (idea → node-by-node mind growth → coverage sweep → Vision Lock → plan with `Realizes:` → verified execution → interrupt/resume → sealed release) plus 13 adversarial probes. Confirmed working: pre-lock blocking, brief-edit invalidation, post-verify tree binding, RED rejection, release evidence binding, BLACK-tier refusal, resume packet answering all six memory questions. Three real gaps found and closed: (1) gate JSON was fail-open to hand edits — all three artifacts now carry a domain-separated SHA-256 content seal and `check` rejects any edited field; (2) `vision confirm` accepted an impatient lock while the Brief said NOT READY / STATE recorded Mind-coverage GAPS — confirm now fails closed on those explicit signals; (3) missing evidence paths raised a raw traceback — now a clean `GATE BLOCKED`. Catalog descriptions of planner/memory synced with the Project Mind. 8 new gate regression tests (72 total). Versions: SMART/marketplace `2.5.1`. |
| Last evidence | `python3 -m pytest tests/ -q` → 72 passed, 127 subtests GREEN after hardening; field-test retest: RED→GREEN flip, task-id swap, command swap, approver swap, premature confirm (NOT READY / GAPS), and missing-file paths all BLOCKED; legitimate confirm→verify→release path GREEN end to end. |
| Blocker / waiting on | None for implementation. Required PR checks must confirm ShellCheck and repository validation. |
| Vision Lock | CONFIRMED by repository owner on 2026-07-11 (reaffirmed and extended twice): SMART must be the complete project control brain for professional development teams first, capture the user's intended product inch by inch in an atomic Project Mind network before any planning/code, never accept "start and figure it out later", deliver expert-grade quality by default, and remain lean enough that orchestration never stalls or slows project progress. |
| Machine gates | Vision: owner-confirmed product direction; Verify: full local deterministic test suite plus required PR checks; Release: N/A for internal orchestration improvement. |
| Branch / head | `genspark_ai_developer` on top of `2dd48cd` (merged PR #18); M-T1 in progress toward `2.5.2`. |
| Mind coverage | Applied to this repo implicitly via STATE/BRIEF equivalents; the formal PROJECT-MIND protocol targets user projects. |

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
- PR #14 merged the progress-first fast path at `f455f9a` with required checks GREEN, completing P3-T6 — source: Git history, 2026-07-11.
- The owner explicitly requires excellence by default: a novice invoking only SMART must receive output at the quality of a top professional team, and that bar must never add complexity that slows the real project — source: owner directive, 2026-07-11.
- The owner requires a complete, verified picture of the user's mind and the final result before any planning or code: every material question answered, recorded as an engineered atomic mind network inside the project, so resume never hits an unanswered question and the project cannot drift — "start and see" is explicitly forbidden — source: owner directive, 2026-07-11.
- The primary audience is professional software organizations needing maximum automation with only key questions; novice support means engineering precision, not a simplified product — source: owner clarification, 2026-07-11.
- The owner considers the project-wide memory structure (atomic, mind-like) the most important part of the product — source: owner statement, 2026-07-11.

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
| CORE-004 | SMART's full ten-stage loop and large report were framed as mandatory on every invocation. | PR #14 merged the progress-first fast path and one-pass Step Pilot at `f455f9a`. | The control layer could consume the session, repeatedly re-orient, and slow or prevent actual project progress. | Fast path is now the default; retain explicit escalation triggers and fast-path regressions. | RESOLVED |
| CORE-006 | Output quality for novices depended on the user knowing what to ask for. | P3-T7 on this branch: excellence-by-default contract, anti-patterns, tests, scenario. | The core product promise (expert-grade result from one activation) was not contractually guaranteed. | PR #15 merged; keep quality-bar regressions. | RESOLVED |
| CORE-007 | SMART's product understanding lived in prose records and conversation; interruption could leave unanswered product questions and let the project drift. | SKILL contracts before P3-T8: no atomic node protocol, no coverage gate, no explicit ban on "figure it out later". | Resume-time gaps could send a project down the wrong path — the exact failure the owner flagged as most critical. | Merge the Project Mind protocol, coverage-gated Vision Lock, planner node integration, tests, and scenario. | IN PROGRESS |
| CORE-005 | Workflow updates may be rejected when the GitHub credential lacks `workflows` permission. | Prior push rejection and owner instruction. | Repeated retries can block unrelated product progress. | Stage exact workflow files under `ci/` and report the manual `ci/<file> -> .github/workflows/<file>` action after the PR. | MITIGATED |

## Meaningful change ledger (newest first)
| Date / commit | What changed | Why | Evidence | Records affected |
|---|---|---|---|---|
| 2026-07-13 / current branch | First real-world usage report (Codespaces): bundled installer failed without `claude` on the subshell PATH despite manual UI installs, and `/smart` was not discoverable. Installer now recognizes companions from the Claude plugin cache without the CLI; added the `/smart` command and README troubleshooting; version `2.5.2`. | The MAINTENANCE runway requires fixing only proven real-usage bottlenecks — this was the first one. | 77 tests + 127 subtests GREEN; live reproduction of the exact Codespaces scenario now returns OK instead of ERROR. | fetch-skill.sh, commands/smart.md, installer tests, README, manifests, changelog, this STATE. |
| 2026-07-11 / PR #17 + tag `v2.5.1` | Executed the cold-start field test (full lifecycle + 13 adversarial probes), sealed all gate artifacts against hand edits, blocked `vision confirm` on explicit NOT READY / Mind-coverage GAPS signals, made missing-evidence paths fail closed cleanly, synced the catalog, and published `v2.5.1` as the first field-validated GitHub Release. | The Runway required proving real behavior before release; the test found three fail-open gaps that had to close first. | 72 tests + 127 subtests GREEN; both required PR checks GREEN; live retest of every probe BLOCKED/GREEN as required; release published. | smart-gates.py, SMART contract, catalog, tests, manifests, changelog, this STATE. |
| 2026-07-11 / current branch | Added the atomic Project Mind network protocol, coverage-gated Vision Lock, planner node integration, the "figure it out later" ban, and the professional-teams-first audience contract; released `2.5.0`. | Guarantee SMART's picture equals the user's picture inch by inch, durably recorded, so resume never hits an unanswered question and drift is impossible. | Full test suite GREEN; 10 scenarios valid; JSON and Bash checks GREEN. | SMART, planner, memory, agent contract, tests, scenarios, README, manifests, changelog, this STATE. |
| 2026-07-11 / current branch | Added the excellence-by-default quality contract (invariant, section, anti-patterns, agent rule), cold-start deferral test, quality-bar contract tests, and offline scenario `novice-gets-expert-quality`; released `2.4.0`. | Guarantee that one SMART activation gives a novice expert-team output quality without adding orchestration weight. | Full test suite GREEN including new contracts; 9 scenarios valid; JSON and Bash checks GREEN. | SMART, agent contract, tests, scenarios, README, manifests, changelog, prior STATE. |
| 2026-07-11 / PR #14 | Added a progress-first healthy-project path, one-pass Step Pilot execution, compact reporting, and restricted-workflow staging policy. | Keep SMART authoritative without letting its own process delay real project progress. | 54 tests GREEN; fast-path/staging/safety contracts GREEN; 8 scenarios and 9 JSON files valid; Bash syntax and whitespace GREEN. | SMART, Step Pilot, agent contract, tests, README, manifests, changelog, prior STATE. |
| 2026-07-11 / PR #13 | Replaced third-party activation command output with a structured SMART approval handoff and a one-decision interaction contract. | Preserve accountable human consent while keeping source, package, and command mechanics inside SMART. | 51 tests and both required checks GREEN. | SMART contract, installer, tests, README, manifests, changelog, prior STATE. |
| 2026-07-11 / PR #12 | Routed six bundled companions through SMART's trusted native marketplace with idempotent installed-state handling. | Remove companion setup and unnecessary quarantine friction from the beginner path without weakening third-party safety. | 50 tests and both required checks GREEN. | SMART contract, installer, tests, README, manifests, changelog, prior STATE. |
| 2026-07-11 / PR #11 | Removed live model observation and replaced its runner with an offline-only schema validator. | Restore SMART's zero-configuration product boundary and eliminate paid/API setup. | 47 tests GREEN; 8 scenarios valid; required PR checks GREEN. | Evaluator, workflow template, tests, README, changelog, this STATE. |
| 2026-07-11 / PR #10 | Made semantic observation optional. | Attempted to reduce cost, but retained unnecessary product complexity. | 52 tests and PR checks GREEN; later superseded by owner decision. | Evaluator, workflow template, tests, README, prior STATE. |
| 2026-07-11 / PR #9 | Staged a manual live-evaluation workflow. | Internal QA experiment; later rejected as out of product direction. | PR checks GREEN; superseded by owner decision. | Workflow template, tests, README, prior STATE. |
| 2026-07-11 / PR #8 | Added eight adversarial SMART scenario contracts and a live harness. | Improve behavioral confidence; scenarios remain, live harness is being removed. | Required checks GREEN. | Scenario data, tests, evaluator, versions. |

## Runway
1. **NEXT — merge the M-T1 PR and publish `v2.5.2`:** CLI-independent bundled-companion detection via the plugin cache, `/smart` command, README troubleshooting, 77 tests GREEN. Completion evidence: merged PR, tag + release notes.
2. **THEN — user re-test in the same Codespaces environment:** confirm `/smart` appears after session restart and the bootstrap install path completes without the CLI error. Completion evidence: user confirmation or a new friction report.
3. **LATER — periodic catalog refresh:** re-verify external skill sources, tiers, and duplicate-resolution rows against upstream changes when evidence of drift appears. Completion evidence: updated `SKILLS_CATALOG.md` rows with review dates.

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
