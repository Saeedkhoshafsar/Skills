# SKILLS_CATALOG — Verified Skill Catalog (SMART's decision source)

> Input for the **SMART** mother skill. Each skill: name + one-line purpose + tier.
> Verified on 2026-07-17: includes **native Claude Code host commands** (Category 0) plus standalone skill sources and native plugin capabilities. Duplicate resolution and the supply-chain gate apply to external installs; host commands are supervised, not fetched. Context Engineering Kit remains a plugin marketplace rather than a flat skill source, and the unified installer handles it automatically.

**Sources (priority order — first source that has a skill wins):**
| # | Source | Count | Path | Content |
|---|---|---|---|---|
| 1 | `Saeedkhoshafsar/Skills` (this repo) | 7 local | `skills/<plugin>/skills/<skill>/` | SMART ecosystem |
| 2 | `anthropics/skills` (official Anthropic) | 17 | `skills/` | documents, design, testing, MCP |
| 3 | `obra/superpowers` | 13 (+1 blocked) | `skills/` | engineering-process craft skills |
| 4 | `Saeedkhoshafsar/ruflo` | 39 | `.claude/skills/` | memory, GitHub, swarm, quality |
| 5 | `Saeedkhoshafsar/claude-plugins-official` | 17 | `plugins/*/skills/` | Claude Code plugin dev + tools |
| 6 | `nextlevelbuilder/ui-ux-pro-max-skill` | 7 | `.claude/skills/` | UI/UX design intelligence: styles, palettes, fonts, brand, banners, slides |
| 7 | `coreyhaines31/marketingskills` | many | `skills/` | marketing strategy, copy, SEO, CRO, growth, and RevOps |

**Duplicate resolution (same capability in several sources):**
| Capability | Winner | Losers (do NOT fetch) | Why |
|---|---|---|---|
| Skill authoring | `skill-creator` (anthropics) | `skill-builder` (ruflo), `writing-skills` (obra), `skill-development` (cpo) | official, evals + scripts included |
| Debugging method | `debug-detective` (local) | `systematic-debugging` (obra) | local, integrated with STATE.md |
| TDD | `test-driven-development` (obra) | `pair-programming` TDD-mode (ruflo) | focused, includes anti-patterns file |
| Frontend design | `frontend-design` (anthropics ≡ cpo, identical) | — | fetch-skill resolves to anthropics |
| Design-system depth (palettes, fonts, industry rules) | `ui-ux-pro-max` (nextlevelbuilder) | — complements `frontend-design` | 67+ styles / 161 palettes / 57 font pairings + reasoning engine; use when the task needs a FULL design system, keep `frontend-design` for creative art direction |
| Scroll-scrubbed cinematic world landing | `scroll-world` (oso95) | not `remotion-video`, not WebGL/Three reinvent | Higgsfield pipeline + frame-locked camera chain + portable scrub engine; Remotion is programmatic React video, not scroll-driven world flight |
| Planning | `project-planner` (local) | `writing-plans` (obra) | local interview+13-layer flow; obra's is a good supplement for plan FORMAT only |
| Plan execution | `step-pilot` (local) | `executing-plans` (obra) | local, gated + STATE.md |
| Verify-before-done | `step-pilot` GATE (local) | `verification-before-completion` (obra) | already enforced locally |
| Code review (local diff) | `code-review` (local) | `receiving-code-review` / `requesting-code-review` (obra) | obra pair is for human-loop etiquette; optional |

**Tier legend (selection rules for SMART):**

| Tier | Meaning | Rule |
|---|---|---|
| GREEN | General — useful in any project | Allowed by default |
| YELLOW | Situational — specific conditions only | Only with a stated reason |
| RED | Specialized/heavy — large projects | Only for big/multi-agent projects |
| BLACK | Internal/foreign-infrastructure skills (ruflo internals + obra's `using-superpowers`) | NEVER install — fetch-skill.sh refuses them |

---

## Category 0 — Native Claude Code host commands (built-in)

> These are **not** installed via `fetch-skill.sh`. They ship with Claude Code (and
> with plugins already loaded in the session). SMART **supervises** them as host
> capabilities: select, recommend, sequence, and gate them so the user never has to
> juggle slash-command mechanics. When a host command can alter memory, model,
> permissions, or autonomy, SMART applies the same evidence and Vision rules as for
> skills.

### Observational / GREEN (safe defaults)

| Command | Purpose (one line) | SMART trigger |
|---|---|---|
| `/context` | Show context-window usage | context pressure, budget phases 40/60/80, handoff prep |
| `/usage` | Usage / quota signal | rate-limit or free-tier exhaustion signals |
| `/doctor` | Environment / install health check | install friction, broken tools, marketplace issues |
| `/recap` | Summarize recent session work | resume assist only after durable STATE is current |
| `/insights` | Session/project insight surfaces | optional after major milestones |
| `/verify` | End-to-end verify a change | after material code changes when a project verify skill exists |
| `/code-review` | Review current diff | stabilization / before merge (prefer local `code-review` skill when deeper plan conformance is needed) |
| `/simplify` | Simplify recent changes | after green verify when cleanup is the next best action |
| `/security-review` | Security-focused review | release prep; still does not replace local `security-check` gate |

### Session & config / YELLOW (stated reason required)

| Command | Purpose (one line) | SMART trigger / guard |
|---|---|---|
| `/compact` | Compress conversation context | only **after** mid-mission checkpoint + `memory resume-check` GREEN |
| `/clear` | Clear conversation | only after complete resume packet; never as a substitute for STATE |
| `/model` | Switch model | rate limits, capability mismatch, owner-requested model change |
| `/effort` | Adjust reasoning effort | task complexity change; prefer lower effort for mechanical work |
| `/fast` | Faster Opus-style output mode | latency-sensitive healthy fast-path work |
| `/config` / `/update-config` | Harness / settings changes | only when settings truly block progress; never silent permission expansion |
| `/mcp` | MCP server management | when an approved integration is required for the current action |
| `/agents` | Subagent configuration | multi-agent need with stated scope |
| `/init` | Create/update project CLAUDE.md | new repo bootstrap only when no durable agent contract exists |
| `/reload-skills` | Reload skill index | after installing plugins mid-session if commands missing |
| `/run` | Launch/drive the project app | post-change behavioral verification |
| `/review` | Review a GitHub PR | PR review requests (diff review → local `code-review`) |
| `/keybindings-help` | Keyboard shortcut help | only when the user is blocked on bindings |
| `/fewer-permission-prompts` | Allowlist common read-only tools | only with explicit user consent for permission changes |
| `/dataviz` | Chart/visualization design system | when producing charts/dashboards |
| `/claude-api` | Claude API / SDK reference | when building against Anthropic APIs |
| `/claude-code-compat` | Claude Code compatibility guidance | harness/compat questions |

### Autonomy / RED (heavy — evidence + Vision gates)

| Command | Purpose (one line) | SMART guard |
|---|---|---|
| `/loop` | Recurring autonomous prompt | Vision Lock + clear stop condition; never on vague ideas |
| `/goal` | Goal-oriented autonomous work | confirmed objective in STATE; not a substitute for discovery |
| `/batch` | Batch multi-item work | scoped list + verify plan; max blast radius |
| `/deep-research` | Multi-source research harness | only for decision-changing unknowns; record into RESEARCH/mind |
| `/remote-control` | Remote session control | explicit user request only |
| `/_remote-workflow` | Remote workflow harness | explicit user request; not default project path |

### Plugin-exposed companions already under SMART (still host-visible)

| Command | Maps to SMART capability |
|---|---|
| `/smart:smart` | SMART orchestrator (canonical plugin namespace; bare `/smart` is not a host command) |
| `/project-planner` | `project-planner` |
| `/project-memory` | `project-memory` |
| `/step-pilot` | `step-pilot` |
| `/debug-detective` | `debug-detective` |
| `/security-check` | `security-check` |
| `/code-review:code-review` | local `code-review` (prefer over generic etiquette skills) |

**Duplicate resolution for host vs skill:** when a host slash command and a catalog
skill overlap, SMART prefers the **local SMART companion / gated skill** for product
work (`debug-detective`, `security-check`, `code-review`, `step-pilot`) and uses the
host command only when it is the lighter correct tool for the immediate action.

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

## Category 7 — Documents & Files (anthropics/skills) (5)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| pdf | Read/create/merge/split/watermark/fill/OCR PDF files | GREEN |
| docx | Create and edit Word documents (tracked changes, comments, formatting) | GREEN |
| xlsx | Create/edit Excel spreadsheets with formulas and charts | GREEN |
| pptx | Create and edit PowerPoint presentations | GREEN |
| doc-coauthoring | Structured co-authoring workflow for specs, proposals, decision docs | GREEN |

## Category 8 — Frontend, Design & Web (anthropics/skills) (7)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| frontend-design | Distinctive, non-templated UI design direction (palette, type, layout) | GREEN |
| webapp-testing | Test local web apps with Playwright: verify UI, screenshots, browser logs | GREEN |
| web-artifacts-builder | Multi-component claude.ai artifacts (React, Tailwind, shadcn/ui) | YELLOW |
| canvas-design | Visual art/posters/designs as PNG-PDF on a canvas | YELLOW |
| theme-factory | 10 preset visual themes + on-the-fly theme generation for any artifact | YELLOW |
| algorithmic-art | Generative/algorithmic art with p5.js (flow fields, particles) | YELLOW |
| slack-gif-creator | Animated GIFs optimized for Slack | YELLOW |
| scroll-world | Immersive scroll-scrubbed "fly through the world" landing: interview → cohesive AI scene stills → frame-locked dive/connector camera clips (Higgsfield Seedance/Kling) → portable vanilla-JS scrub engine; optional native 9:16 mobile chain | YELLOW |

> **`scroll-world` SMART profile (oso95/scroll-world, alias path `skills/scroll-world`)**
>
> | Field | Detail |
> |---|---|
> | **When to use** | User wants a cinematic landing/hero where **scroll drives a continuous camera** through a little generated world — diorama / miniature / industry walkthrough / Emons-style flight with **no cuts**. Triggers: "scroll world", "fly through", "diorama landing", "scroll cinematic", "3D world hero", "browse-through-the-industry", continuous camera landing. |
> | **When NOT to use** | Full app UI/design system → `ui-ux-pro-max` / `frontend-design`. Programmatic React video/timeline/subtitles → `remotion-video`. Static posters/canvas → `canvas-design`. Marketing copy/SEO alone → `marketingskills`. Ordinary product pages without scroll-driven camera flight. |
> | **Tier** | **YELLOW** — situational; paid external generation; only with a stated trigger and explicit spend approval. |
> | **Prerequisites** | Authenticated [Higgsfield CLI](https://higgsfield.ai) with credits (`higgsfield auth login`); `ffmpeg`/`ffprobe`; Python 3 + Pillow for optional knockout / mobile portrait canvases; optional Codex CLI ≥0.125 with ChatGPT login for subscription-billed stills. |
> | **Cost model** | ≈ **N stills + (2N−1) videos** for N scenes; mobile portrait chain ≈ **2× video gens**. Calibrate against live `higgsfield workspace list` balance before spend; skill must state estimate and get go-ahead. Draft tier `seedance_2_0_mini` for previz. |
> | **What it produces** | Per scene: still + dive-in clip; architecture B also produces connector clips frame-locked on **actual neighbour frames** (seam rule); portable `scrub-engine.js` + config page; optional 9:16 mobile chain. Framework-agnostic (plain HTML / Next / Vue / Python-served). |
> | **Critical quality rule** | Seams must be **frame-identical** — connectors use extracted rendered frames, never diorama stills. One video model for the whole chain (`seedance_2_0` default, `kling3_0`, or `seedance_2_0_mini`). Architecture A (continuous forward take) for grounded walkthroughs; B (dive + aerial connector) only for diorama/god's-eye. |
> | **Install path** | `fetch-skill.sh scroll-world` → third-party quarantine → SMART reviews SKILL.md + `references/*` + scan report → one plain-language approve/reject → lock. Source: `oso95/scroll-world@main` path `skills/scroll-world`. |
> | **Complement** | Brand/palette first via `ui-ux-pro-max` or `brand` when a full system is needed; then `scroll-world` for the hero flight. Do not invent WebGL/Three reimplementations when this skill fits. |
> | **Safety** | Third-party MIT; runs local scripts (`knockout.py`, batch bash, ffmpeg) and calls Higgsfield network APIs with user credentials. Never auto-spend credits; never bypass quarantine/approve. |

## Category 9 — Anthropic Platform & Meta (anthropics/skills) (5)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| skill-creator | Create/edit/eval/benchmark skills — the official skill-authoring tool | GREEN |
| mcp-builder | Build MCP servers in Python or Node/TypeScript | YELLOW |
| claude-api | Integrate the Claude/Anthropic API into apps (agents, tool use, files) | YELLOW |
| brand-guidelines | Apply Anthropic's official brand style to artifacts | YELLOW |
| internal-comms | Write status reports, newsletters, FAQs in internal-comms style | YELLOW |

## Category 10 — Engineering Process (obra/superpowers) (13 installable + 1 blocked)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| test-driven-development | Strict RED-GREEN-REFACTOR TDD + testing anti-patterns reference | GREEN |
| brainstorming | Socratic idea refinement into validated designs before any plan | GREEN |
| systematic-debugging | 4-phase root-cause debugging (overlaps local debug-detective — prefer local) | YELLOW |
| writing-plans | Detailed step plan format for engineers with zero codebase context | YELLOW |
| executing-plans | Batch plan execution with checkpoints (overlaps local step-pilot — prefer local) | YELLOW |
| requesting-code-review | Pre-merge review request etiquette + subagent reviewer flow | YELLOW |
| receiving-code-review | Respond to review feedback with technical rigor, no performative agreement | YELLOW |
| verification-before-completion | Never claim DONE without fresh verification evidence | YELLOW |
| finishing-a-development-branch | Merge/PR/cleanup checklist when a branch's work is complete | YELLOW |
| using-git-worktrees | Parallel work with git worktrees (safe directory selection) | YELLOW |
| dispatching-parallel-agents | Dispatch parallel subagents for independent problems | RED |
| subagent-driven-development | Execute a plan via fresh subagents per task + two-stage review | RED |
| writing-skills | (overlaps skill-creator — prefer skill-creator) | YELLOW |
| using-superpowers | obra's meta-skill that wires its OWN plugin infrastructure — useless outside the superpowers plugin | BLACK (blocked by fetch-skill.sh) |

## Category 11 — Claude Code Plugin/Tooling Dev (claude-plugins-official) (16)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| playground | Self-contained interactive HTML explorers (controls + live preview + prompt out) | GREEN |
| claude-md-improver | Audit and improve CLAUDE.md files against quality templates | GREEN |
| session-report | Explorable HTML report of Claude Code usage (tokens, cost, subagents) | YELLOW |
| project-artifact | Tabbed shareable project-status page (claude.ai Artifact tool needed) | YELLOW |
| math-olympiad | Competition math with adversarial verification (IMO/Putnam) | YELLOW |
| writing-hookify-rules | Author hookify rules (pattern-watching hooks) | YELLOW |
| skill-development | Claude Code skill authoring reference (overlaps skill-creator) | YELLOW |
| plugin-structure | Plugin layout, marketplace.json, manifest reference | YELLOW |
| plugin-settings | Plugin settings/config patterns | YELLOW |
| mcp-integration | Bundle MCP servers inside plugins | YELLOW |
| hook-development | Develop Claude Code hooks (all events, matchers, exit codes) | YELLOW |
| command-development | Develop slash commands | YELLOW |
| agent-development | Develop subagents for plugins | YELLOW |
| build-mcp-server | Design and build production MCP servers | YELLOW |
| build-mcp-app | Build MCP Apps (UI over MCP) | RED |
| build-mcpb | Package MCP servers as one-click .mcpb bundles | RED |

> `claude-automation-recommender` from this repo is already listed in Category 2.
> The repo also ships plugins with no skills (commands/agents/hooks only): code-review, security-guidance, feature-dev, pr-review-toolkit, code-simplifier, ralph-loop, commit-commands, hookify engine, LSP servers, external_plugins (telegram, discord, github MCP...). Those are Claude Code **plugins**, installable via `/plugin`, not fetchable as skills.

## Category 12 — UI/UX Design Intelligence (nextlevelbuilder/ui-ux-pro-max-skill) (7)

| Skill | Purpose (one line) | Tier |
|---|---|---|
| ui-ux-pro-max | Design-intelligence engine: 67+ UI styles, 161 industry color palettes, 57 font pairings, 25 chart types, 99 UX guidelines, 161 reasoning rules — generates a complete tailored design system (pattern + style + colors + typography + anti-patterns + pre-delivery checklist) for 22 stacks (React, Next.js, Vue, Svelte, SwiftUI, Flutter, Tailwind, shadcn/ui, …). Search scripts require Python 3. | GREEN |
| ui-styling | shadcn/ui + Radix + Tailwind implementation: accessible components, theming, dark mode, canvas designs | YELLOW |
| design-system | Three-layer design tokens (primitive→semantic→component), CSS variables, component specs | YELLOW |
| brand | Brand voice, visual identity, messaging frameworks, style-guide consistency | YELLOW |
| banner-design | Social/ad/web/print banners with multiple art-direction options (visuals need an AI image generator) | YELLOW |
| slides | Strategic HTML presentations: Chart.js, design tokens, copywriting formulas | YELLOW |
| design | Umbrella skill: logos, CIP, mockups, icons, social photos (heavy — depends on Gemini image APIs; prefer the focused skills above) | RED |

> `ui-ux-pro-max` is the flagship: SMART's default pick whenever a task needs a FULL design system (industry-matched colors + typography + layout pattern). For pure creative art direction keep `frontend-design` (anthropics); the two complement each other.

## Additional External Sources

| Source | Integration | Use when | License / caution |
|---|---|---|---|
| `coreyhaines31/marketingskills` | `fetch-skill.sh <skill-name>` from `skills/` | marketing strategy, copywriting, SEO, CRO, analytics, growth, and RevOps; start with `product-marketing` to create shared context | MIT; skills intentionally reference `.agents/product-marketing.md` |
| `hardikpandya/stop-slop` | `fetch-skill.sh stop-slop` | editing prose to remove predictable AI phrasing and structures | MIT; intentionally strict style rules, so use only when the requested voice fits |
| `wshuyi/remotion-video-skill` | `fetch-skill.sh remotion-video` | creating React/Remotion videos, animations, subtitles, or TTS-driven scenes | MIT; requires Node.js 18+, Python for TTS, and `ffprobe` for audio-duration detection |
| `oso95/scroll-world` | `fetch-skill.sh scroll-world` (alias → `skills/scroll-world`) | immersive scroll-scrubbed "fly through the world" landing pages — continuous camera flight through AI-generated scenes with no cuts | MIT; **requires** authenticated [Higgsfield CLI](https://higgsfield.ai) credits + `ffmpeg`/`ffprobe` + Python/Pillow; optional Codex CLI for ChatGPT-billed stills. Spends paid generation credits (≈N stills + 2N−1 videos; mobile ≈2×). Third-party — quarantine + explicit approve. Not a substitute for design systems (`ui-ux-pro-max`) or programmatic video (`remotion-video`) |
| `NeoLabHQ/context-engineering-kit` | `fetch-skill.sh <capability>` auto-adds its marketplace and installs the selected native plugin | reflection, spec-driven development, judged subagents, TDD, review, git, docs, or context-engineering workflows | GPL-3.0; unified installation preserves commands, agents, hooks, and skills instead of flattening them |

### Capability additions

| The task needs… | Fetch / install |
|---|---|
| Product marketing context | `product-marketing` |
| Copy, SEO, CRO, launch, pricing, analytics, or RevOps | the focused `marketingskills` entry after checking `product-marketing` |
| Direct, human-sounding prose review | `stop-slop` |
| Programmatic video with React and Remotion | `remotion-video` |
| Scroll-scrubbed cinematic "fly through the world" landing / diorama hero | `scroll-world` |
| Reflection / self-critique / durable lessons | `reflection` → CEK `reflexion` |
| Spec-driven implementation for complex work | `spec-driven-development` → CEK `sdd` |
| Subagent execution with judges | `subagent-development` → CEK `sadd` |
| Multi-agent code or PR review | `context-review` → CEK `review` |
| DDD / SOLID / Clean Architecture guidance | `domain-driven-development` → CEK `ddd` |
| Root-cause and continuous-improvement analysis | `continuous-improvement` → CEK `kaizen` |
| Evidence-audited first-principles decisions | `first-principles-reasoning` → CEK `fpf` (RED: very high token use) |
| CEK Git / TDD / docs / tech-stack / MCP / agent customization | matching capability from `fetch-skill.sh --list` |

## Category 13 — ruflo-internal — NEVER install (14, all BLACK)

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
| smart | Project intelligence: truthful model, mode orientation, Vision Lock, next-best-action capability orchestration/creation, consolidation | Every session start / material evidence or phase change |
| project-planner | Adaptive discovery that grows the atomic Project Mind network (`docs/PROJECT-MIND.md`) node by node + Project Brief + epistemic/viability review + Vision Lock (mind coverage COMPLETE) + risk-ordered atomic plan whose tasks cite mind node IDs | Phase 0 until vision and roadmap approval |
| project-memory | Owner of the atomic Project Mind network (addressable `M-<domain>-<n>` nodes, typed links, coverage sweep) + canonical truth records + compact STATE resume packet, assumptions, capability inventory, change ledger, runway | From first reliable facts onward |
| step-pilot | Vision-Lock and evidence-gated execution: one scoped task -> fresh verify -> consolidate -> commit/recovery | Approved plan onward |
| code-review | Local diff review: correctness, readability, tests, plan conformance | Phase 3 / before merge |
| debug-detective | Systematic debugging: reproduce -> isolate -> hypothesize -> minimal fix -> regression | Trigger: bug / 3 red verifies |
| security-check | 5-axis pre-release security audit: secrets, deps, input, auth/RLS, defaults | Phase 4 gate (mandatory) |

---

## Coverage Map: 13 Professional Project Layers

| Project layer | Covering skills | Coverage |
|---|---|---|
| Frontend | **ui-ux-pro-max** + **frontend-design** + **webapp-testing** + browser + theme-factory + **scroll-world** (cinematic scroll-scrub hero only) | GOOD |
| APIs & Backend Logic | sparc-methodology + test-driven-development + pair-programming | GOOD |
| Database & Storage | agentdb-* is AGENT memory only, NOT the product DB! | NONE |
| Auth & Permissions | security-check (audit only) | PARTIAL |
| Hosting & Deployment | github-release-management + finishing-a-development-branch | PARTIAL |
| Cloud & Compute | flow-nexus-* (their own service only) | NONE |
| CI/CD & Version Control | github-workflow-automation + hooks-automation + using-git-worktrees | GOOD |
| Security & RLS | **security-check (local)** | GOOD |
| Rate Limiting | security-check flags it (audit only) | PARTIAL |
| Caching & CDN | — | NONE |
| Load Balancing & Scaling | swarm-* scales AGENTS, not the app! | NONE |
| Error Tracking & Logs | **debug-detective (local)** + hooks-automation | GOOD |
| Availability & Recovery | verification-quality (code rollback only) | PARTIAL |
| Documents & Reports | pdf + docx + xlsx + pptx + doc-coauthoring | GOOD |
| Skill/Plugin/MCP tooling | skill-creator + plugin-dev suite + mcp-builder | GOOD |

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
1. SENSE focused evidence from STATE, brief, plan, decisions, research, git, and tests.
2. ORIENT one operating mode (BOOTSTRAP, DISCOVERY, VISION-LOCK, PLANNING,
   EXECUTION, RECOVERY, STABILIZATION, RELEASE, or MAINTENANCE).
3. MODEL facts with KNOWN / INFERRED / ASSUMED / UNKNOWN / CONFLICT labels.
4. DECIDE the next best action by information gain, user value, risk reduction,
   reversibility, effort, and dependencies. No plan/code before confirmed Vision Lock.
5. SELECT the minimum capability set for that action (max 3; tier/duplicate rules).
   If a proven recurring capability gap exists, use skill-creator and evaluations.
6. ACT through fetch-skill.sh and apply the mode gate; supply-chain review external skills.
7. CONSOLIDATE canonical truth, current state, assumptions, decisions, capability
   inventory, change ledger, and the next-three-action runway; then REPORT.
```

### Capability-need quick index (SMART's free-hand lookup)

| The task needs… | Fetch |
|---|---|
| PDF / Word / Excel / PowerPoint output | pdf / docx / xlsx / pptx |
| Writing a spec, proposal, decision doc | doc-coauthoring |
| Full design system per industry (styles + palettes + fonts) | ui-ux-pro-max |
| Beautiful, non-generic UI | frontend-design (+ theme-factory) |
| shadcn/ui + Tailwind implementation | ui-styling |
| Design tokens / component specs | design-system |
| Brand identity / style guide | brand |
| Banners & social creatives | banner-design |
| HTML slide decks | slides |
| Testing a local web app | webapp-testing (or browser) |
| Strict TDD discipline | test-driven-development |
| Vague idea → validated design | brainstorming |
| Creating/optimizing a skill | skill-creator |
| Building an MCP server | mcp-builder (or build-mcp-server) |
| Claude Code hook / command / subagent / plugin | hook-development / command-development / agent-development / plugin-structure |
| Improving CLAUDE.md quality | claude-md-improver |
| Interactive visual explorer for a topic | playground |
| Parallel independent workstreams (big project) | dispatching-parallel-agents / using-git-worktrees |
| Usage/cost report of Claude Code sessions | session-report |
| Marketing strategy, copy, SEO, CRO, growth, or RevOps | focused `marketingskills` entry (start with `product-marketing`) |
| Remove predictable AI prose patterns | stop-slop |
| Programmatic Remotion video | remotion-video |
| Scroll-scrubbed cinematic world landing / diorama hero / continuous camera flight | scroll-world |
| Reflection / self-critique | reflection (auto-installs CEK reflexion) |
| Complex spec-driven development | spec-driven-development (auto-installs CEK sdd) |
| Judged subagent development | subagent-development (auto-installs CEK sadd) |
| Multi-agent code / PR review | context-review (auto-installs CEK review) |
| DDD / SOLID / Clean Architecture rules | domain-driven-development (auto-installs CEK ddd) |
| Root-cause / continuous improvement | continuous-improvement (auto-installs CEK kaizen) |
| Auditable first-principles reasoning (large only) | first-principles-reasoning (auto-installs CEK fpf) |

## Install Commands

As a Claude Code plugin (this repo ships `.claude-plugin/marketplace.json`):
```bash
claude plugin marketplace add Saeedkhoshafsar/Skills
claude plugin install smart@saeed-skills
```

Unified on-demand installation (SMART resolves source and package type):
```bash
bash skills/smart/skills/smart/scripts/fetch-skill.sh --list             # what is available
bash skills/smart/skills/smart/scripts/fetch-skill.sh sparc-methodology  # install just this one
bash skills/smart/skills/smart/scripts/fetch-skill.sh ui-ux-pro-max      # standalone UI/UX skill
bash skills/smart/skills/smart/scripts/fetch-skill.sh spec-driven-development # native CEK sdd plugin
bash skills/smart/skills/smart/scripts/fetch-skill.sh --installed        # skills + plugins installed
```
