---
name: smart
description: >
  Mother skill / skill manager. On every invocation: (1) senses project state and
  detects the current phase, (2) selects only the skills that phase needs from the
  catalog and installs them on-demand from GitHub, (3) reports a skill roadmap
  (what is active now, what comes next). Use when starting any project, resuming
  work, entering a new phase, or when the user says "smart" / "اسمارت" or asks
  which skills to activate.
tools: Read, Glob, Grep, Bash
---

# SMART — Skill Manager

**Philosophy:** The user activates only SMART. SMART decides the rest.
No skill lives in the project up front — skills are downloaded the moment they are needed.

**Golden rule:** Install the MINIMUM number of skills that moves the work forward. Never hoard.

## Execution Cycle (run these 5 steps in order, every invocation)

### Step 1 — Sense (gather facts)

Run these checks and record the answers:

| Check | Command / File | Question answered |
|---|---|---|
| Project empty? | `ls -la` | Anything beyond git/README? |
| Plan exists? | `docs/PLAN.md` or `PLAN*.md` | Do we have a plan? |
| Memory exists? | `docs/STATE.md` | What is the current task (`-> current`)? |
| Code exists? | `src/`, `apps/`, `package.json`, ... | Are we mid-development? |
| CI/CD exists? | `.github/workflows/` | Ready for release? |
| Installed skills? | `bash scripts/fetch-skill.sh --installed` | What is already installed? |

### Step 2 — Diagnose (detect phase)

Match the facts against the Phase Table below. Pick exactly one phase.

### Step 3 — Select (choose skills)

- Take the phase's skill list from the Phase Table and `SKILLS_CATALOG.md`.
- Apply tier rules: GREEN = allowed by default | YELLOW = only with a stated reason | RED = large projects only | BLACK = never (ruflo-internal).
- Install at most **3 new skills** per invocation.

### Step 4 — Act (install)

```bash
bash scripts/fetch-skill.sh <skill-name>   # only the selected skills
```

### Step 5 — Report (mandatory — never skip)

Emit the status report using the template at the bottom, including:
- Current phase and evidence
- Skills activated now, with one-line reasons
- Skill roadmap: what the next phase will need

## Phase Table

| # | Phase | Detection signal | Skills for this phase (priority order) |
|---|---|---|---|
| 0 | Discovery — empty project | No files beyond git/README | `project-planner` (local) — interview the user, produce PLAN.md |
| 1 | Setup — plan exists, no code | PLAN.md exists, no src | `project-memory` (local) + `step-pilot` (local); `agentdb-memory-patterns` only if needed |
| 2 | Development — coding | src exists, open task in STATE.md | `sparc-methodology` + `verification-quality`; `pair-programming` if TDD |
| 3 | Stabilization — code done, testing/quality | Phase tasks done, not released | `code-review` (local) + `github-code-review` (if PRs); `performance-analysis` if slow; `browser` if UI |
| 4 | Release — ready to deploy | Everything green | `security-check` (local — MANDATORY gate) + `github-release-management` + `github-workflow-automation` + `hooks-automation` |
| 5 | Maintenance — post-release | Release exists, open issues | `github-project-management`; `github-multi-repo` if multi-repo |

**Always active from Phase 1 onward:**
- `project-memory` — STATE.md: current task, errors, bugs, unfinished work. Any agent resumes from it after a disconnect.
- `step-pilot` — step-by-step plan execution with tests and acceptance criteria per step.

**Event-driven skills (any phase, specific trigger):**

| Skill | Trigger |
|---|---|
| `debug-detective` (local) | A bug is reported, a test keeps failing, or step-pilot hits 3 consecutive red verifies |
| `security-check` (local) | Before any deploy/release; after adding auth, payments, or user data |

**RED-tier only if:** project becomes multi-agent/very large → `swarm-orchestration`; RAG needed → `agentdb-vector-search`.
**BLACK-tier (`v3-*`, `flow-nexus-*`, `worker-benchmarks`): never — they are ruflo internals.**

## Installing Skills On-Demand

Skills are NOT stored in the project — they are downloaded when needed:

```bash
bash <path-to-smart>/scripts/fetch-skill.sh --list          # list skills available in sources
bash <path-to-smart>/scripts/fetch-skill.sh <skill-name>    # install one skill (sparse-checkout, not the whole repo)
bash <path-to-smart>/scripts/fetch-skill.sh --installed     # list currently installed skills
```

Local skills (project-planner, project-memory, step-pilot, code-review, debug-detective, security-check) live next to SMART in this repo:

```bash
cp -r <this-repo>/skills/project-planner .claude/skills/
```

Keep `.claude/skills/` in the project's `.gitignore` (except project-specific skills) — everything is re-downloadable, do not bloat the project repo.

## Output Report Template (mandatory)

```
SMART — Status Report [date]

Phase        : 2 - Development
Evidence     : PLAN.md present (phase 1/4) | STATE.md -> current: P1-T3 | last recorded error: <from STATE.md>

Active skills (3):
  - project-memory      project memory
  - step-pilot          step-by-step execution
  - sparc-methodology   development method

Activated now (+why):
  - verification-quality  <- entering the test step of P1-T3

Skill roadmap:
  - after Phase 2  -> code-review + github-code-review
  - before release -> security-check + github-release-management + hooks-automation
```

## Anti-Patterns (SMART never does these)

1. **Install everything at once** — only what the moment needs (max 3 new).
2. **Use `agentdb-*` for the product database** — those are AGENT memory, not the product DB. The product DB comes from the project's own plan/architecture.
3. **Install any BLACK-tier skill** — never (ruflo internals).
4. **Skip the report** — every SMART invocation must end with the status report.
5. **Forget memory** — if STATE.md is missing and the project is past Phase 1, set up `project-memory` first.
6. **Code without a plan** — if PLAN.md is missing, run `project-planner` first.
