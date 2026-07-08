# CLAUDE.md — Agent Entry Point

You are working with the **SMART skill-manager ecosystem**. Read this file first, then act.

## What this repo is

A set of 7 local skills plus a verified catalog of 40 external skills. The design:
the user activates only `smart`; `smart` senses the project phase and installs the
minimum set of other skills on-demand from GitHub.

## Reading order for an agent

1. `skills/smart/SKILL.md` — the orchestrator. Its 5-step cycle (Sense → Diagnose → Select → Act → Report) drives everything.
2. `SKILLS_CATALOG.md` — the decision source: 40 external skills with tiers (GREEN/YELLOW/RED/BLACK).
3. The individual local skills, only when activated.

## The 7 local skills (one line each)

| Skill | One-line contract |
|---|---|
| `smart` | Detect phase → install ≤3 needed skills → report roadmap. Every invocation ends with a status report. |
| `project-planner` | Interview (≤7 questions) → size S/M/L → 13-layer selection → atomic `docs/PLAN.md` (Files + Accept + Verify per task). |
| `project-memory` | Maintain `docs/STATE.md`: `-> current` task, bugs, decisions, debt. Updated in the SAME commit as the code. |
| `step-pilot` | Execute one plan task at a time: implement → test → verify GATE → record → commit. 3 red verifies → hand off to debug-detective. |
| `code-review` | Review the diff (not the repo) on 5 axes → verdict APPROVE / REQUEST CHANGES with severity-sorted findings. |
| `debug-detective` | Reproduce → isolate → hypothesize → minimal fix → regression proof → record root cause. Never shotgun-debug. |
| `security-check` | 5-axis audit (secrets, deps, injection, auth, defaults) → CRITICAL blocks release. Mandatory gate before every deploy. |

## Hard rules (apply across all skills)

1. **STATE.md is the source of truth.** Read it at session start; update it in the same commit as code.
2. **No plan → no code.** Empty project means `project-planner` first.
3. **Green Verify or no DONE.** Every task's Verify command must pass before a DONE commit.
4. **Max 3 new skills per SMART invocation.** Minimum set that moves work forward.
5. **BLACK-tier skills (`v3-*`, `flow-nexus-*`, `dual-mode`, `worker-benchmarks`) are never installed** — ruflo internals.
6. **`agentdb-*` is agent memory, never the product database.**
7. **security-check is a mandatory gate before every release.** A CRITICAL finding blocks the release.

## Conventions

- Task IDs: `P<phase>-T<number>` (e.g. `P1-T3`), defined in PLAN.md, tracked in STATE.md.
- Commits: `P<x>-T<y>: <what happened>` for tasks, `fix(scope): <root> — <solution>` for bug fixes.
- Language: all skills, plans, STATE files, and reports are written in **English** (agents perform best on English content). Speak to the user in the user's language.
