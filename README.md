# Skills — SMART Skill-Manager Ecosystem

> The user activates only **SMART**; SMART selects the other skills by project phase **and by capability need** and installs them **on-demand from GitHub** — no skill wastes project space.
>
> **79 installable skills** across **5 sources**: 7 local + Anthropic's official skills (pdf/docx/xlsx/pptx, frontend-design, webapp-testing, skill-creator, mcp-builder…) + obra/superpowers engineering-process skills (TDD, brainstorming…) + ruflo + claude-plugins-official plugin-dev skills.

## Repo Map

```
Skills/
├── .claude-plugin/
│   └── marketplace.json      # plugin catalog (install via /plugin in Claude Code)
├── README.md                 # this file
├── CLAUDE.md                 # agent entry point (read this first if you are an AI agent)
├── SKILLS_CATALOG.md         # verified catalog of 40 external skills (SMART's decision source)
└── skills/                   # each skill = one plugin (SKILL.md + .claude-plugin/plugin.json)
    ├── smart/                # MOTHER SKILL (skill manager)
    │   ├── SKILL.md          #   cycle: Sense -> Diagnose -> Select -> Act -> Report
    │   └── scripts/
    │       └── fetch-skill.sh#   single-skill download via sparse-checkout (tested)
    ├── project-planner/      # planner (interview + 13 layers + atomic PLAN.md)
    ├── project-memory/       # project memory (STATE.md — disconnect/amnesia-proof)
    ├── step-pilot/           # gated step-by-step execution (test + verify per step)
    ├── code-review/          # local diff review (correctness, tests, plan conformance)
    ├── debug-detective/      # systematic debugging (reproduce -> root cause -> fix -> regression)
    └── security-check/       # pre-release security audit (secrets, deps, auth, ...)
```

## Install on Claude Code (primary path — plugin marketplace)

```bash
# 1. Add the marketplace (once):
claude plugin marketplace add Saeedkhoshafsar/Skills
#    or inside a session:  /plugin marketplace add Saeedkhoshafsar/Skills

# 2. Install the mother skill (enough — it manages the rest):
claude plugin install smart@saeed-skills

# (optional) install the others directly:
claude plugin install project-planner@saeed-skills
claude plugin install project-memory@saeed-skills
claude plugin install step-pilot@saeed-skills
claude plugin install code-review@saeed-skills
claude plugin install debug-detective@saeed-skills
claude plugin install security-check@saeed-skills

# update later:
claude plugin marketplace update saeed-skills && claude plugin update smart@saeed-skills
```

> If you previously got `Marketplace file not found at ...\.claude-plugin\marketplace.json`,
> remove the broken marketplace and re-add it:
> ```bash
> claude plugin marketplace remove Saeedkhoshafsar-Skills   # or whatever name was registered
> claude plugin marketplace add Saeedkhoshafsar/Skills
> ```
> This repo now has `.claude-plugin/marketplace.json` at the root — the error is fixed.

## Use Without the Marketplace (manual — any agent)

```bash
# 1. Bring only SMART into your project:
mkdir -p .claude/skills
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/Saeedkhoshafsar/Skills.git /tmp/sk
git -C /tmp/sk sparse-checkout set skills/smart
cp -r /tmp/sk/skills/smart .claude/skills/ && rm -rf /tmp/sk

# 2. Tell the agent: "activate the smart skill"
#    It detects and installs everything else by itself.
```

## Project Lifecycle with SMART

| Project state | SMART activates | Notes |
|---|---|---|
| Empty project | `project-planner` | interview + PLAN.md; `brainstorming` first if the idea is vague |
| Plan ready | `project-memory` + `step-pilot` | memory + gated steps |
| Mid-development | `sparc-methodology` + `verification-quality` (from GitHub) | TDD? → `test-driven-development`; UI? → `frontend-design`; recurring bug? → `debug-detective` |
| Ready to release | `security-check` (GATE) + `github-release-management` + `hooks-automation` | security gate is mandatory |
| Maintenance | `github-project-management` | issues, boards |

**Capability triggers (any phase):** the task itself can demand a skill regardless of phase — PDF/Word/Excel/PowerPoint output → `pdf`/`docx`/`xlsx`/`pptx`, web-app testing → `webapp-testing`, building a skill → `skill-creator`, building an MCP server → `mcp-builder`, Claude Code hooks/commands/plugins → the `plugin-dev` suite. Full index in [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md).

## Skill Sources (what fetch-skill.sh pulls from)

| # | Source | Count | Content |
|---|---|---|---|
| 1 | this repo, `skills/` | 7 | smart, planner, memory, step-pilot, code-review, debug-detective, security-check |
| 2 | `anthropics/skills` → `skills/` | 17 | pdf, docx, xlsx, pptx, doc-coauthoring, frontend-design, webapp-testing, skill-creator, mcp-builder, claude-api, canvas-design, theme-factory, … |
| 3 | `obra/superpowers` → `skills/` | 13 | test-driven-development, brainstorming, writing-plans, git-worktrees, parallel agents, … |
| 4 | `Saeedkhoshafsar/ruflo` → `.claude/skills` | 39 | memory, GitHub, swarm, quality, … (14 BLACK-tier internals are blocked) |
| 5 | `Saeedkhoshafsar/claude-plugins-official` → `plugins/*/skills` | 17 | claude-automation-recommender, playground, claude-md-improver, plugin-dev suite, mcp-server-dev suite, … |

Priority: first source that has the skill wins — duplicates (skill-creator vs skill-builder, TDD variants, …) are resolved in the catalog's duplicate-resolution table.

Details and tiers for all skills → [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md)

## Updating (marketplace installs)

Plugins installed from a marketplace are **pinned copies** — they do NOT auto-update.
When this repo changes, update your local install in two steps:

```bash
claude plugin marketplace update saeed-skills   # 1. refresh the marketplace catalog
claude plugin update smart@saeed-skills         # 2. pull the new plugin version
# (or /plugin → manage → update inside a session)
```

Skills fetched on-demand into `.claude/skills/` are also pinned snapshots — refresh any of them with:

```bash
bash skills/smart/scripts/fetch-skill.sh --update <skill-name>
```
