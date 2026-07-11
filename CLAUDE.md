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
first builds an evidence-aware shared model, enforces Vision Lock before planning/code,
maintains durable project truth and runway, then installs or creates the minimum capability
set needed for the next decision/action. SMART selects by capability, not source or package type.

## Reading order for an agent

1. `skills/smart/skills/smart/SKILL.md` — the project-intelligence orchestrator. Its evidence, mode, Vision Lock, capability, action, and consolidation gates drive everything.
2. `SKILLS_CATALOG.md` — the decision source: 79 external skills with tiers (GREEN/YELLOW/RED/BLACK), a duplicate-resolution table, and a capability-need quick index.
3. The individual local skills, only when activated.

## The 7 local skills (one line each)

| Skill | One-line contract |
|---|---|
| `smart` | Build truthful project model → orient mode → enforce Vision Lock → select/create ≤3 capabilities → act → consolidate/report. |
| `project-planner` | Adaptive discovery → Project Brief + epistemic/viability review → explicit Vision Lock → risk-ordered atomic `docs/PLAN.md`. |
| `project-memory` | Maintain canonical brief/plan/decisions/research plus compact `docs/STATE.md` resume packet, capability inventory, ledger, and runway. |
| `step-pilot` | Refuse unconfirmed execution; run one approved task through scope, fresh evidence, memory, and recovery gates. |
| `code-review` | Review the diff (not the repo) on 5 axes → verdict APPROVE / REQUEST CHANGES with severity-sorted findings. |
| `debug-detective` | Reproduce → isolate → hypothesize → minimal fix → regression proof → record root cause. Never shotgun-debug. |
| `security-check` | 5-axis audit (secrets, deps, injection, auth, defaults) → CRITICAL blocks release. Mandatory gate before every deploy. |

## Hard rules (apply across all skills)

1. **STATE.md is the source of truth.** Read it at session start; update it in the same commit as code.
2. **No confirmed Vision Lock + approved plan → no code.** New/unclear projects enter adaptive discovery first.
3. **Fresh green evidence or no DONE.** Task Verify and measurable acceptance must pass before a DONE commit.
4. **Max 3 new capabilities per SMART invocation.** Count standalone skills and native plugins together; install the minimum set that moves work forward.
5. **BLACK-tier skills (`v3-*`, `flow-nexus-*`, `dual-mode`, `worker-benchmarks`, `using-superpowers`) are never installed** — internals of other ecosystems. `fetch-skill.sh` refuses them.
6. **`agentdb-*` is agent memory, never the product database.**
7. **security-check is a mandatory gate before every release.** A CRITICAL finding blocks the release.
8. **Duplicates are resolved by the catalog table, not ad hoc.** e.g. skill authoring → `skill-creator` (anthropics), debugging → local `debug-detective`, TDD → `test-driven-development` (obra).
9. **Current decision/action overrides phase defaults.** "Produce an Excel report" in any phase → fetch `xlsx` now; "design a full UI" → fetch `ui-ux-pro-max`.
10. **Context Engineering Kit stays plugin-only but is auto-installed.** SMART passes a capability name to `fetch-skill.sh`; the script adds the CEK marketplace once and installs only the selected native plugin. Never flatten CEK into `.claude/skills/`, ask the user to choose a plugin/source, or merely print manual setup steps when `claude` is available.
11. **Supply-chain gate.** External standalone skills are downloaded only into quarantine. Static scan success is not proof of safety: review `SKILL.md`, every script, provenance, license, network/secret access, and the generated manifest before explicit activation. Never approve your own unreviewed candidate, bypass a BLOCKED result, or use quarantined content.
12. **Prefer safe reuse before creation.** Before creating a skill, search the curated catalog and reputable repositories for a narrow candidate. A discovered repository must enter through `fetch-skill.sh candidate`, remain quarantined, and pass the same review and lock workflow; discovery never grants trust.

## Conventions

- Task IDs: `P<phase>-T<number>` (e.g. `P1-T3`), defined in PLAN.md, tracked in STATE.md.
- Commits: `P<x>-T<y>: <what happened>` for tasks, `fix(scope): <root> — <solution>` for bug fixes.
- Language: all skills, plans, STATE files, and reports are written in **English** (agents perform best on English content). Speak to the user in the user's language.
