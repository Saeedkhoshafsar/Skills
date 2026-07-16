# STATE — SMART Skill-Manager Ecosystem

> Resume index for cross-session continuity. The product contract lives in
> `skills/smart/skills/smart/SKILL.md`; capability decisions live in
> `SKILLS_CATALOG.md`; offline adversarial contracts live in
> `skills/smart/skills/smart/evals/scenarios.json`.

## Resume packet
| Field | Current value |
|---|---|
| SMART mode / lifecycle phase | MAINTENANCE / 5 |
| Current objective | Make SMART the single brain over installable skills **and** Claude Code host commands. |
| Active task | M-T4 — native host-command supervision (2.5.5) — DONE. |
| Exact progress | Category 0 host commands + SMART supervision policy + anti-patterns + rule 21 + 2 scenarios; **86 tests GREEN**, **15 scenarios valid**; SMART `2.5.5`. |
| Last evidence | `python3 -m unittest discover -s tests -q` → OK (86); scenarios 15 valid. |
| Blocker / waiting on | none |
| Vision Lock | CONFIRMED by repository owner on 2026-07-11 (reaffirmed and extended twice): SMART must be the complete project control brain for professional development teams first, capture the user's intended product inch by inch in an atomic Project Mind network before any planning/code, never accept "start and figure it out later", deliver expert-grade quality by default, and remain lean enough that orchestration never stalls or slows project progress. |
| Machine gates | Vision: owner-confirmed product direction; Verify: full local deterministic test suite GREEN; Release: GitHub Releases published through `v2.5.4`. |
| Branch / head | `main` SMART `2.5.5` host-command supervision. |
| Mind coverage | Applied to this repo implicitly via STATE/BRIEF equivalents; the formal PROJECT-MIND protocol targets user projects. |

## Epistemic delta
### Newly confirmed
- PR #21 merged to `main` (`6befc8a`) with required checks GREEN — source: GitHub PR state, 2026-07-16.
- Owner granted full delivery authority for a stable final Skills project on GitHub including public releases and install polish — source: explicit owner directive, 2026-07-16.
- Marketplace root `metadata.version` must track the current SMART release pin so catalog consumers see `2.5.4` — source: marketplace audit, 2026-07-16.
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

## Open errors and risks
| ID | Description | Evidence / location | Impact | Next diagnostic/mitigation | Status |
|---|---|---|---|---|---|
| CORE-001 | The product roadmap was temporarily dominated by live evaluation infrastructure. | Merged PR #11 removed the live runner, paid workflow, observer, secrets, and API setup. | Core SMART improvements were delayed and product intent became unclear. | Keep offline contracts only unless the owner explicitly changes direction. | RESOLVED |
| CORE-002 | Bundled SMART companions were routed through the third-party standalone quarantine path. | PR #12 routes six companions through trusted native-plugin installation with idempotency coverage. | Beginners could encounter unnecessary review/setup mechanics for already trusted first-party plugins. | Keep third-party quarantine separate and retain first-party routing regressions. | RESOLVED |
| CORE-003 | Third-party quarantine exposed approval commands as installer output. | PR #13 merged the structured handoff, explicit-consent contract, and no-command runtime behavior. | SMART could relay mechanics instead of presenting one plain-language evidence/approval decision. | Preserve fail-closed quarantine and accountable activation regressions. | RESOLVED |
| CORE-004 | SMART's full ten-stage loop and large report were framed as mandatory on every invocation. | PR #14 merged the progress-first fast path and one-pass Step Pilot at `f455f9a`. | The control layer could consume the session, repeatedly re-orient, and slow or prevent actual project progress. | Fast path is now the default; retain explicit escalation triggers and fast-path regressions. | RESOLVED |
| CORE-006 | Output quality for novices depended on the user knowing what to ask for. | P3-T7: excellence-by-default contract, anti-patterns, tests, scenario. | The core product promise (expert-grade result from one activation) was not contractually guaranteed. | PR #15 merged; keep quality-bar regressions. | RESOLVED |
| CORE-007 | SMART's product understanding lived in prose records and conversation; interruption could leave unanswered product questions and let the project drift. | Project Mind protocol + coverage-gated Vision Lock. | Resume-time gaps could send a project down the wrong path. | PR #16 merged; keep mind-coverage regressions. | RESOLVED |
| CORE-008 | Mid-mission progress and late-session context pressure could vanish without chat history. | M-T2 + M-T3 on main (`2.5.3`/`2.5.4`). | Zero-context resume could rebuild ceremony or lose progress. | Keep mid-mission, budget, archive, and pre-existing bootstrap contracts. | RESOLVED |
| CORE-005 | Workflow updates may be rejected when the GitHub credential lacks `workflows` permission. | Prior push rejection and owner instruction. | Repeated retries can block unrelated product progress. | Stage exact workflow files under `ci/` and report the manual `ci/<file> -> .github/workflows/<file>` action after the PR. | MITIGATED |
| SHIP-001 | GitHub Releases lagged code on main (`v2.5.1` only while code was `2.5.4`). | Release list audit 2026-07-16. | Marketplace consumers could stay on older pins and miss install/continuity fixes. | Publish `v2.5.2`–`v2.5.4` and document the two-step update path. | RESOLVED |

## Meaningful change ledger (newest first)
| Date / commit | What changed | Why | Evidence | Records affected |
|---|---|---|---|---|
| 2026-07-16 / 2.5.5 | Native Claude Code host-command supervision: catalog Category 0, SMART playbooks, anti-patterns, 2 scenarios, rule 21. | User wants SMART to master the whole slash surface, not only fetchable skills. | contract tests + 15 scenarios. | catalog, SMART, CLAUDE, command, tests, scenarios, changelog, STATE. |
| 2026-07-16 / stable ship | Marketplace metadata → `2.5.4`; `/smart` SENSE prefers STATE2; README install pin + 13 scenarios; gitignore installer temp; STATE handoff; GitHub Releases `v2.5.2`–`v2.5.4`. | Final stable delivery: no install/version/docs drift after continuity merges. | 85 tests GREEN; 13 scenarios valid; versions aligned. | marketplace, command, README, gitignore, STATE, releases. |
| 2026-07-16 / PR #21 | M-T3: context-budget phases 40/60/80, hard archive (~200 lines / STATE2), pre-existing project bootstrap; SMART `2.5.4` / project-memory `1.3.2`. | Late checkpoints, STATE bloat, rediscovery on pre-existing projects. | 85 tests GREEN; 13 scenarios valid; PR merged. | SMART, project-memory, CLAUDE, scenarios, tests, manifests, changelog, prior STATE. |
| 2026-07-16 / PR #20 | M-T2 mid-mission checkpoint protocol + `memory resume-check`; SMART `2.5.3` / project-memory `1.3.1`. | Context/daily cutovers must not erase mid-mission progress. | 82 tests + PR checks GREEN. | SMART, project-memory, gates, tests, scenarios, manifests, changelog. |
| 2026-07-13 / PR #19 | Plugin-cache companion detection without CLI; `/smart` command; version `2.5.2`. | Codespaces cold-start friction. | 77 tests GREEN. | fetch-skill.sh, commands, installer tests, README, manifests, changelog. |
| 2026-07-11 / PR #17 + tag `v2.5.1` | Gate seals, premature Vision Lock block, fail-closed missing evidence; first field-validated release. | Cold-start field test findings. | 72 tests GREEN; release published. | smart-gates.py, SMART, catalog, tests, manifests, changelog. |

## Runway
1. **NEXT — field-validate host supervision:** under context pressure, confirm SMART checkpoints then recommends `/compact`; refuse premature `/loop`.
2. **THEN — periodic catalog refresh:** re-verify external skill sources when drift evidence appears.
3. **LATER — only proven install/usage bottlenecks:** no speculative ceremony; fix only evidence-backed friction.

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
