# STATE — SMART Skill-Manager Ecosystem

> Resume index for cross-session continuity. Product and behavioral contracts live in
> `README.md` and `skills/smart/skills/smart/SKILL.md`; executable evaluation scenarios
> live in `skills/smart/skills/smart/evals/scenarios.json`.

## Resume packet
| Field | Current value |
|---|---|
| SMART mode / lifecycle phase | STABILIZATION / 3 |
| Current objective | Make the first live-model baseline cost-controllable, then preserve its report as evidence. |
| Active task | P3-T2 — make semantic Judge calls explicitly optional before workflow activation. |
| Exact progress | PR #9 is merged. The evaluator and staged workflow now default to generation-only mode: one API call per scenario, deterministic forbidden-pattern checks, and explicit manual-review status without a false semantic pass rate. Semantic judging is opt-in and may reuse the same model/API; a separate Judge API is never required. |
| Last evidence | Optional-Judge branch: 52 unit tests GREEN; 8 scenarios schema-valid; Python compile, workflow YAML parsing, and whitespace checks GREEN. PR #9 required checks -> SUCCESS. The prior local live smoke reached the configured endpoint but returned `401 Invalid or expired token`. |
| Blocker / waiting on | Repository owner must configure valid Actions secrets and activate the staged workflow through GitHub UI; the available GitHub App cannot read secrets (`403`) or modify `.github/workflows/*` (`workflows` permission denied). |
| Vision Lock | CONFIRMED by completed SMART 2.3.0 milestone scope; no product-scope change in P3-T1. |
| Machine gates | Vision: existing SMART contract; Verify: PR checks required; Release: N/A until a live behavioral baseline passes. |
| Branch / head | `genspark_ai_developer`; optional-Judge follow-up to merged PR #9 |

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
| `gpt-5-mini` is an acceptable first baseline generation model. | No model matrix has been approved yet. | Run all 8 scenarios in generation-only mode and inspect outputs; enable semantic judging only if its additional cost is approved. | Repository owner | First full live report or model-policy decision. |
| An on-demand workflow is safer than scheduled execution initially. | Cost, latency, and rate limits are not measured. | Record duration and API usage for the first three runs. | Repository owner | Three stable runs with an approved budget. |

### Unknowns / conflicts
| Item | Impact if wrong | Resolution action | Status |
|---|---|---|---|
| Whether Actions secrets are configured and valid | Live workflow cannot generate a baseline. | Check Settings -> Secrets and variables -> Actions; create/rotate both required secrets. | BLOCKING |
| Whether semantic API judging is worth its additional per-scenario call | A Judge may increase cost and introduce self-judging bias. | Start generation-only with human review; optionally rerun selected responses with the same or an independent model. | OPEN |
| Acceptable live-evaluation cadence and API budget | Determines whether scheduling is appropriate. | Measure first three manual runs and record cost/latency policy. | OPEN |

## Capability inventory
| Capability | Type/source | Status | Invoked when | Last result / review |
|---|---|---|---|---|
| SMART behavioral evaluator | Python stdlib / repository | VERIFIED deterministic layer; live baseline pending | Model-level regression evaluation | 11 behavioral-evaluation tests GREEN; 8 scenarios schema-valid |
| Manual live-eval workflow | GitHub Actions template at `ci/github-workflow-behavioral-eval.yml` | STAGED, NOT ACTIVE; Judge opt-in | Owner configures secrets and copies template to `.github/workflows/behavioral-eval.yml` | Defaults to generation-only; active GitHub validation pending |

## Open errors and risks
| ID | Description | Evidence / location | Impact | Next diagnostic/mitigation | Status |
|---|---|---|---|---|---|
| EVAL-001 | Injected local API token is invalid or expired. | Live evaluator returned HTTP 401. | No local live baseline. | Rotate/inject a valid key; do not commit it. | BLOCKED |
| EVAL-002 | Automation identity lacks GitHub `workflows` permission. | Push rejected for `.github/workflows/behavioral-eval.yml`. | Workflow cannot be activated by this agent. | Owner copies staged template using GitHub web editor or a workflow-authorized token. | BLOCKED |
| EVAL-003 | Integration cannot inspect Actions secrets. | `gh secret list` returned HTTP 403. | Secret readiness cannot be confirmed automatically. | Owner verifies secret names in repository Settings. | BLOCKED |

## Meaningful change ledger (newest first)
| Date / commit | What changed | Why | Evidence | Records affected |
|---|---|---|---|---|
| 2026-07-11 / current branch | Made semantic Judge calls opt-in and generation-only reports epistemically honest. | Allow a useful baseline without doubling per-scenario API calls or requiring a separate Judge API. | 52 tests GREEN; suite schema, Python compile, workflow YAML, and whitespace checks GREEN. | Evaluator, workflow template, tests, README, this STATE |
| 2026-07-11 / PR #9 | Staged a manually dispatchable live-evaluation workflow with artifact retention. | Make model-level evaluation reproducible without making nondeterministic API calls a PR-required check. | 49 tests GREEN; workflow parses as YAML; 8 scenarios and all JSON valid; shell syntax GREEN. | Workflow template, test, README, this STATE |
| 2026-07-11 / PR #8 | Added SMART 2.3.0 behavioral harness, 8 adversarial scenarios, and 10 tests. | Move from instruction-presence tests to model-behavior evidence. | 48 unit tests and required GitHub checks GREEN. | Evaluator, scenarios, tests, README, versions |

## Runway
1. **NEXT — merge optional-Judge follow-up:** Review and merge the current branch so the staged template defaults to one generation call per scenario. Completion evidence: required checks GREEN and follow-up PR merged.
2. **THEN — owner configuration and workflow activation:** In GitHub, create/rotate Actions secrets `SMART_EVAL_API_KEY` and `SMART_EVAL_BASE_URL`; copy `ci/github-workflow-behavioral-eval.yml` to `.github/workflows/behavioral-eval.yml` using the web editor. Completion evidence: the workflow appears under Actions and no secret value is committed or logged.
3. **THEN — first cost-minimal baseline:** Dispatch `behavioral-eval` with `scenario=all`, `model=gpt-5-mini`, `use_judge=false`, blank `judge_model`, and `fail_under=0.8` (ignored without Judge); download `smart-behavioral-eval-<run-id>`. Completion evidence: retained log plus a generation-only JSON report containing all 8 responses and no infrastructure error.
4. **LATER — human review and selective judging:** Manually review all deterministic failures and each `review_required` response. If useful and budget-approved, rerun selected saved responses with `--judge`, reusing the generation model/API or choosing an independent model. Change SMART/scenarios only where evidence supports it.

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
  -f use_judge=false \
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
- Semantic Judge — opt in only for selected/full runs whose extra API cost is approved; it may reuse the generation API.
- Multi-model matrix — activate when a judged baseline reveals instability or before claiming provider-independent behavior.
- Human calibration set — create before treating semantic-judge scores as a production release gate.
