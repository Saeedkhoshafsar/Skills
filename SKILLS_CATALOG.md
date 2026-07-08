# SKILLS_CATALOG — Verified Skill Catalog (SMART's decision source)

> Input for the **SMART** mother skill. Each skill: name + one-line purpose + tier.
> Verified complete on 2026-07-08: both source repos re-cloned and diffed folder-by-folder — **40/40 skills, nothing missing, nothing extra.**

**Sources:**
| Source | Count | Path |
|---|---|---|
| `Saeedkhoshafsar/Skills` (this repo) | 7 local | `skills/` |
| `Saeedkhoshafsar/ruflo` | 39 | `.claude/skills/` |
| `Saeedkhoshafsar/claude-plugins-official` | 1 | `plugins/claude-code-setup/skills/` |

**Tier legend (selection rules for SMART):**

| Tier | Meaning | Rule |
|---|---|---|
| GREEN | General — useful in any project | Allowed by default |
| YELLOW | Situational — specific conditions only | Only with a stated reason |
| RED | Specialized/heavy — large projects | Only for big/multi-agent projects |
| BLACK | ruflo-internal | NEVER install |

---

## Category 1 — Memory & Learning (7)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| agentdb-memory-patterns | Persistent agent memory across sessions (session + long-term) | YELLOW |
| agentdb-vector-search | Semantic document/code search (RAG, similarity) | RED |
| agentdb-learning | Train the agent with 9 reinforcement-learning algorithms | RED |
| agentdb-optimization | Shrink memory DB 4-32x + 150x faster search | RED |
| agentdb-advanced | Sync the memory database across distributed systems | RED |
| reasoningbank-intelligence | Learn from past success/failure patterns | RED |
| reasoningbank-agentdb | Same as above, backed by the fast AgentDB store | RED |

> WARNING: `agentdb-*` = memory for the AGENT, never the product's database. For the product DB use the project's own plan/architecture.

## Category 2 — Methodology & Planning (3)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| sparc-methodology | 5-step dev method: Specification -> Pseudocode -> Architecture -> Refinement -> Completion | GREEN |
| skill-builder | Build new skills with the standard structure (the tool that built SMART) | GREEN |
| claude-automation-recommender | Scan project and suggest suitable tools/hooks/skills (SMART's ancestor) | GREEN |

## Category 3 — Quality & Testing (3)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| verification-quality | Correctness scoring + automatic rollback below the 0.95 threshold | GREEN |
| pair-programming | AI pair programming: driver/navigator, TDD, debug, refactor modes | GREEN |
| performance-analysis | Find performance bottlenecks + suggest optimizations | YELLOW |

## Category 4 — GitHub & CI/CD (6)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| github-code-review | Automated multi-angle Pull Request review | GREEN |
| github-workflow-automation | Build/manage GitHub Actions pipelines | YELLOW |
| github-release-management | Versioning, testing, automated releases + rollback | YELLOW |
| github-project-management | Issues, project boards, sprints — automated | YELLOW |
| github-multi-repo | Coordinate changes across multiple repos | YELLOW |
| agentic-jujutsu | Experimental git-alternative version control (very niche) | RED |

## Category 5 — Multi-Agent Coordination (5)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| swarm-orchestration | Run multiple agents in parallel on independent tasks | YELLOW |
| swarm-advanced | Advanced agent-group patterns (research/dev/test concurrently) | RED |
| hive-mind-advanced | Queen + workers with collective memory and voting | RED |
| stream-chain | Pipe agent A's output into agent B (pipeline) | RED |
| hooks-automation | Auto-run actions before/after operations: format, lint, commit, log | YELLOW |

## Category 6 — Execution Tools (2)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| browser | Browser automation: UI testing, screenshots, forms, web browsing | GREEN |
| worker-integration | Smart task distribution across workers + performance tracking | YELLOW |

## Category 7 — ruflo-internal — NEVER install (14, all BLACK)

| Skill(s) | What it is |
|---|---|
| v3-core-implementation, v3-ddd-architecture, v3-security-overhaul, v3-memory-unification, v3-performance-optimization, v3-mcp-optimization, v3-cli-modernization, v3-integration-deep, v3-swarm-coordination | 9 skills for building **claude-flow v3 itself** — ruflo team's internal roadmap |
| dual-mode | Claude Code + headless Codex workers coordination (requires Codex) |
| flow-nexus-platform / flow-nexus-swarm / flow-nexus-neural | Proprietary Flow Nexus cloud service (requires account/credits) |
| worker-benchmarks | Benchmarks for ruflo's internal worker system |

---

## Local Skills in This Repo (7)

| Skill | Purpose | Phase / trigger |
|---|---|---|
| smart | Skill manager: detects the project phase, installs the right skills on-demand | Every session start / phase change |
| project-planner | User interview + S/M/L sizing + atomic PLAN.md (13 layers, CTB style) | Phase 0 (empty project) |
| project-memory | File-based memory STATE.md: current task, errors, decisions (disconnect-proof) | Phase 1+ (always active) |
| step-pilot | Step-by-step execution: implement -> test -> verify -> record -> commit | Phase 1+ (always active) |
| code-review | Local diff review: correctness, readability, tests, plan conformance | Phase 3 / before merge |
| debug-detective | Systematic debugging: reproduce -> isolate -> hypothesize -> minimal fix -> regression | Trigger: bug / 3 red verifies |
| security-check | 5-axis pre-release security audit: secrets, deps, input, auth/RLS, defaults | Phase 4 gate (mandatory) |

---

## Coverage Map: 13 Professional Project Layers

| Project layer | Covering skills | Coverage |
|---|---|---|
| Frontend | browser (UI testing) | PARTIAL |
| APIs & Backend Logic | sparc-methodology + pair-programming | GENERIC |
| Database & Storage | agentdb-* is AGENT memory only, NOT the product DB! | NONE |
| Auth & Permissions | security-check (audit only) | PARTIAL |
| Hosting & Deployment | github-release-management | PARTIAL |
| Cloud & Compute | flow-nexus-* (their own service only) | NONE |
| CI/CD & Version Control | github-workflow-automation + hooks-automation | GOOD |
| Security & RLS | **security-check (local)** | GOOD |
| Rate Limiting | security-check flags it (audit only) | PARTIAL |
| Caching & CDN | — | NONE |
| Load Balancing & Scaling | swarm-* scales AGENTS, not the app! | NONE |
| Error Tracking & Logs | **debug-detective (local)** + hooks-automation | GOOD |
| Availability & Recovery | verification-quality (code rollback only) | PARTIAL |

> KEY INSIGHT: most ruflo skills manage the AGENTS themselves, not real product layers.
> SMART must know this so it never suggests the wrong skill — e.g. never `agentdb-*` for "the project's database".

---

## What Else Is in ruflo (besides skills)?

| Folder | Count | Content |
|---|---|---|
| `agents/` | 108 | Role definitions: coder, planner, reviewer, tester, queen-coordinator, pr-manager... (agent personas, not skills) |
| `commands/` | 168 | Slash-command shortcuts for the same skills/agents |
| `helpers/` | 40 | Shell scripts: auto-checkpoint, auto-commit, health-monitor |
| `workflows/` | 2 | Whole-system tests |

---

## SMART Decision Recipe (summary)

```
Every SMART invocation:
1. SENSE the project state
   - empty?              -> Phase 0: discovery + planning
   - plan but no code?   -> Phase 1: setup (memory + steps)
   - mid-development?    -> Phase 2: code + test + git
   - ready to release?   -> Phase 4: security gate + CI/CD + release
2. SELECT skills matching phase and tier from this catalog
   - rule: minimum skill count that moves the work forward (anti-greed)
   - GREEN default-allowed | YELLOW with reason | RED big projects only | BLACK never
3. REPORT the skill roadmap: "these 3 now; those 2 after Phase 2"
```

## Install Commands

As a Claude Code plugin (this repo ships `.claude-plugin/marketplace.json`):
```bash
claude plugin marketplace add Saeedkhoshafsar/Skills
claude plugin install smart@saeed-skills
```

On-demand download (skills never bloat the project):
```bash
bash skills/smart/scripts/fetch-skill.sh --list             # what is available
bash skills/smart/scripts/fetch-skill.sh sparc-methodology  # install just this one
bash skills/smart/scripts/fetch-skill.sh --installed        # what is installed
```
