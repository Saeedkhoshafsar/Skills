# Skills — SMART Skill-Manager Ecosystem

> The user activates only **SMART**; SMART selects the other skills by project phase and installs them **on-demand from GitHub** — no skill wastes project space.

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
| Empty project | `project-planner` | interview + PLAN.md |
| Plan ready | `project-memory` + `step-pilot` | memory + gated steps |
| Mid-development | `sparc-methodology` + `verification-quality` (from GitHub) | recurring bug/error? → `debug-detective` |
| Ready to release | `security-check` (GATE) + `github-release-management` + `hooks-automation` | security gate is mandatory |
| Maintenance | `github-project-management` | issues, boards |

## Skill Sources (what fetch-skill.sh pulls from)

| Source | Count | Content |
|---|---|---|
| this repo, `skills/` | 7 | smart, planner, memory, step-pilot, code-review, debug-detective, security-check |
| `Saeedkhoshafsar/ruflo` → `.claude/skills` | 39 | memory, GitHub, swarm, quality, ... (see the catalog) |
| `Saeedkhoshafsar/claude-plugins-official` | 1 | claude-automation-recommender |

Details and tiers for all 40 external skills → [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md)
