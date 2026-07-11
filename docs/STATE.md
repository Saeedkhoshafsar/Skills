# STATE — SMART Skill-Manager Ecosystem

> Resume index for cross-session continuity. Product and behavioral contracts live in
> `README.md` and `skills/smart/skills/smart/SKILL.md`; executable evaluation scenarios
> live in `skills/smart/skills/smart/evals/scenarios.json`.

## Resume packet
| Field | Current value |
|---|---|
| SMART mode / lifecycle phase | STABILIZATION / 3 |
| Current objective | Produce the first reproducible live-model behavioral baseline for SMART and preserve its report as evidence. |
| Active task | P3-T1 — activate and run the live behavioral-evaluation workflow — BLOCKED ON OWNER CONFIGURATION |
| Exact progress | PR #8 merged the evaluator, 8 scenarios, 10 harness tests, and SMART 2.3.0. PR #9 stages `ci/github-workflow-behavioral-eval.yml` for manual activation and adds one workflow contract test. The template supports one/all scenarios, separate generation/judge models, fail threshold, logs, JSON report, and 30-day artifact upload. |
| Last evidence | `python3 -m unittest discover -s tests -v` -> 49 GREEN on PR #9 content; 8 scenarios and all JSON valid; workflow template passed PyYAML parsing; shell syntax passed. PR #8 required `validate` checks -> SUCCESS. Local live smoke reached the configured endpoint but returned `401 Invalid or expired token`. |
| Blocker / waiting on | Repository owner must configure valid Actions secrets and activate the staged workflow through GitHub UI; the available GitHub App cannot read secrets (`403`) or modify `.github/workflows/*` (`workflows` permission denied). |
| Vision Lock | CONFIRMED by completed SMART 2.3.0 milestone scope; no product-scope change in P3-T1. |
| Machine gates | Vision: existing SMART contract; Verify: PR checks required; Release: N/A until a live behavioral baseline passes. |
| Branch / head | `genspark_ai_developer`; PR #9 |

## Epistemic delta
### Newly confirmed
- PR #8 is merged into `main` at merge commit `18c5b83` — source: GitHub API and local `origin/main`, 2026-07-11.
- The deterministic repository suite contains 49 passing tests, including 11 behavioral-evaluation tests — source: local unittest on PR #9 content, 2026-07-11.
- The configured local API token is not usable for a live baseline (`401 Invalid or expired token`) — source: live smoke call, 2026-07-11.
- The current GitHub App cannot list Actions secrets or push active workflow changes — source: GitHub API/push errors (`403` and missing `workflows` permission), 2026-07-11.

### Inferred — confirmation needed
- `SMART_EVAL_API_KEY` and `SMART_EVAL_BASE_URL` have not yet been configured as repository Actions secrets. Secret presence cannot be inspected with the current integration; confirm in repository Settings.

### Active assumptions
| Assumption | Why temporary | Validation test | Owner | Expiry/reversal trigger |
|---|---|---|---|---|
| `gpt-5-mini` is an acceptable first baseline generation and judge model. | No model matrix has been approved yet. | Run all 8 scenarios once, inspect score and judge quality, then compare another judge model if results are unstable. | Repository owner | First full live report or model-policy decision. |
| An on-demand workflow is safer than scheduled execution initially. | Cost, latency, and rate limits are not measured. | Record duration and API usage for the first three runs. | Repository owner | Three stable runs with an approved budget. |

### Unknowns / conflicts
| Item | Impact if wrong | Resolution action | Status |
|---|---|---|---|
| Whether Actions secrets are configured and valid | Live workflow cannot generate a baseline. | Check Settings -> Secrets and variables -> Actions; create/rotate both required secrets. | BLOCKING |
| Whether one model should judge its own output | May bias pass/fail results. | Run a second judge model or human spot-check all critical failures and a sample of passes. | OPEN |
| Acceptable live-evaluation cadence and API budget | Determines whether scheduling is appropriate. | Measure first three manual runs and record cost/latency policy. | OPEN |

## Capability inventory
| Capability | Type/source | Status | Invoked when | Last result / review |
|---|---|---|---|---|
| SMART behavioral evaluator | Python stdlib / repository | VERIFIED deterministic layer; live baseline pending | Model-level regression evaluation | 11 behavioral-evaluation tests GREEN; 8 scenarios schema-valid |
| Manual live-eval workflow | GitHub Actions template at `ci/github-workflow-behavioral-eval.yml` | STAGED, NOT ACTIVE | Owner configures secrets and copies template to `.github/workflows/behavioral-eval.yml` | Local structure review; active GitHub validation pending |

## Open errors and risks
| ID | Description | Evidence / location | Impact | Next diagnostic/mitigation | Status |
|---|---|---|---|---|---|
| EVAL-001 | Injected local API token is invalid or expired. | Live evaluator returned HTTP 401. | No local live baseline. | Rotate/inject a valid key; do not commit it. | BLOCKED |
| EVAL-002 | Automation identity lacks GitHub `workflows` permission. | Push rejected for `.github/workflows/behavioral-eval.yml`. | Workflow cannot be activated by this agent. | Owner copies staged template using GitHub web editor or a workflow-authorized token. | BLOCKED |
| EVAL-003 | Integration cannot inspect Actions secrets. | `gh secret list` returned HTTP 403. | Secret readiness cannot be confirmed automatically. | Owner verifies secret names in repository Settings. | BLOCKED |

## Meaningful change ledger (newest first)
| Date / commit | What changed | Why | Evidence | Records affected |
|---|---|---|---|---|
| 2026-07-11 / PR #9 | Staged a manually dispatchable live-evaluation workflow with artifact retention. | Make model-level evaluation reproducible without making nondeterministic API calls a PR-required check. | 49 tests GREEN; workflow parses as YAML; 8 scenarios and all JSON valid; shell syntax GREEN. | Workflow template, test, README, this STATE |
| 2026-07-11 / PR #8 | Added SMART 2.3.0 behavioral harness, 8 adversarial scenarios, and 10 tests. | Move from instruction-presence tests to model-behavior evidence. | 48 unit tests and required GitHub checks GREEN. | Evaluator, scenarios, tests, README, versions |

## Runway
1. **NEXT — owner configuration and workflow activation:** In GitHub, create/rotate Actions secrets `SMART_EVAL_API_KEY` and `SMART_EVAL_BASE_URL`; copy `ci/github-workflow-behavioral-eval.yml` to `.github/workflows/behavioral-eval.yml` using the web editor. Completion evidence: the workflow appears under Actions and no secret value is committed or logged.
2. **THEN — first full baseline:** Dispatch `behavioral-eval` with `scenario=all`, `model=gpt-5-mini`, blank `judge_model`, and `fail_under=0.8`; wait for completion and download `smart-behavioral-eval-<run-id>`. Completion evidence: retained log plus `behavioral-eval.json` containing all 8 scenario results and no infrastructure error.
3. **LATER — calibrate and remediate:** Human-review every critical failure and at least two passes; rerun failures with an independent judge model, then fix SMART/scenarios only where evidence supports it. Completion evidence: reviewed baseline, documented false-positive/false-negative decisions, and a green rerun or explicit accepted exception.

## Next-session command packet
After the owner completes Runway item 1, the next model should run:

```bash
cd /home/user/webapp
git fetch origin main && git checkout genspark_ai_developer
# If PR #9 is merged, sync to main before continuing.
gh workflow list

gh workflow run behavioral-eval.yml \
  -f scenario=all \
  -f model=gpt-5-mini \
  -f judge_model='' \
  -f fail_under=0.8

# Capture the newest run id, watch it, then download evidence.
RUN_ID=$(gh run list --workflow behavioral-eval.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN_ID" --exit-status
gh run download "$RUN_ID" --dir .smart/evidence/downloaded-"$RUN_ID"
```

If the workflow is absent, do not retry a workflow push with the same GitHub App. Report that Runway item 1 is still pending. If the run fails, inspect the uploaded `behavioral-eval.log` before changing code; distinguish infrastructure/authentication failure from a genuine scenario/rubric failure.

## Deferred / debt with activation triggers
- Scheduled behavioral evaluation — activate only after three manual runs establish acceptable reliability, cost, and duration.
- Multi-model matrix — activate when the first baseline reveals judge instability or before claiming provider-independent behavior.
- Human calibration set — create before treating semantic-judge scores as a production release gate.
