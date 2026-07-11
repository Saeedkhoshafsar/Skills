# CLAUDE.md — Agent Entry Point

You are working with the **SMART skill-manager ecosystem**. Read this file first, then act.

## What this repo is

A set of 7 local skills plus a curated external catalog. Standalone sources include
anthropics/skills, obra/superpowers, ruflo, claude-plugins-official,
nextlevelbuilder/ui-ux-pro-max-skill, coreyhaines31/marketingskills, stop-slop,
and remotion-video. Context Engineering Kit remains a native plugin marketplace because it
ships commands, agents, and hooks alongside skills, but SMART now installs its selected
plugins automatically through the same unified capability installer. The design: the user
activates only `smart`; `smart` senses the project phase AND the task's capability needs,
then installs the minimum set of standalone skills or native plugins on demand. SMART has
a free hand across all sources — it selects by capability, not by source or package type.

## Reading order for an agent

1. `skills/smart/skills/smart/SKILL.md` — the orchestrator. Its 5-step cycle (Sense → Diagnose → Select → Act → Report) drives everything.
2. `SKILLS_CATALOG.md` — the decision source: 79 external skills with tiers (GREEN/YELLOW/RED/BLACK), a duplicate-resolution table, and a capability-need quick index.
3. The individual local skills, only when activated.

## The 7 local skills (one line each)

| Skill | One-line contract |
|---|---|
| `smart` | Detect phase → install ≤3 needed capabilities (skill or plugin) → report roadmap. Every invocation ends with a status report. |
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
4. **Max 3 new capabilities per SMART invocation.** Count standalone skills and native plugins together; install the minimum set that moves work forward.
5. **BLACK-tier skills (`v3-*`, `flow-nexus-*`, `dual-mode`, `worker-benchmarks`, `using-superpowers`) are never installed** — internals of other ecosystems. `fetch-skill.sh` refuses them.
6. **`agentdb-*` is agent memory, never the product database.**
7. **security-check is a mandatory gate before every release.** A CRITICAL finding blocks the release.
8. **Duplicates are resolved by the catalog table, not ad hoc.** e.g. skill authoring → `skill-creator` (anthropics), debugging → local `debug-detective`, TDD → `test-driven-development` (obra).
9. **Capability triggers override phase defaults.** "Produce an Excel report" in any phase → fetch `xlsx` now; "design a full UI" → fetch `ui-ux-pro-max`.
10. **Context Engineering Kit stays plugin-only but is auto-installed.** SMART passes a capability name to `fetch-skill.sh`; the script adds the CEK marketplace once and installs only the selected native plugin. Never flatten CEK into `.claude/skills/`, ask the user to choose a plugin/source, or merely print manual setup steps when `claude` is available.
11. **Supply-chain gate.** After fetching any EXTERNAL skill, skim its SKILL.md and scripts once (30 seconds) before using it — delete and report anything suspicious.

## Conventions

- Task IDs: `P<phase>-T<number>` (e.g. `P1-T3`), defined in PLAN.md, tracked in STATE.md.
- Commits: `P<x>-T<y>: <what happened>` for tasks, `fix(scope): <root> — <solution>` for bug fixes.
- Language: all skills, plans, STATE files, and reports are written in **English** (agents perform best on English content). Speak to the user in the user's language.
