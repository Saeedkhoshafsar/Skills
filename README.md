# Skills — SMART Skill-Manager Ecosystem

> The user activates only **SMART**. SMART first builds a truthful shared picture of the idea, labels uncertainty, and refuses to plan or code until the user confirms **Vision Lock**. It then preserves durable project memory and runway, selects capabilities by the next decision/action, and installs or creates only what is needed — the user never chooses a source, marketplace, package type, or command.
>
> A curated set of installable skills across multiple standalone sources: 7 local + Anthropic's official skills (pdf/docx/xlsx/pptx, frontend-design, webapp-testing, skill-creator, mcp-builder…) + obra/superpowers engineering-process skills (TDD, brainstorming…) + ruflo + claude-plugins-official plugin-dev skills + nextlevelbuilder/ui-ux-pro-max UI/UX design intelligence (67+ styles, 161 palettes, 57 font pairings…).

## Repo Map

```
Skills/
├── .claude-plugin/
│   └── marketplace.json      # plugin catalog (install via /plugin in Claude Code)
├── LICENSE                   # MIT
├── CHANGELOG.md              # version history (bump versions here + marketplace.json)
├── README.md                 # this file
├── CLAUDE.md                 # agent entry point (read this first if you are an AI agent)
├── SKILLS_CATALOG.md         # verified catalog of 86 skills across 6 sources (SMART's decision source)
└── skills/                   # each plugin uses the standard Claude Code layout:
    ├── smart/                #   <plugin>/.claude-plugin/plugin.json + <plugin>/skills/<skill>/SKILL.md
    │   ├── .claude-plugin/plugin.json
    │   └── skills/smart/
    │       ├── SKILL.md      #   project brain: Sense -> Orient -> Model -> Decide -> Act -> Consolidate
    │       └── scripts/
    │           └── fetch-skill.sh  # unified skill + native-plugin capability installer
    ├── project-planner/      # adaptive discovery + Project Brief + Vision Lock + atomic PLAN.md
    ├── project-memory/       # canonical truth + resume packet + decisions/assumptions/runway
    ├── step-pilot/           # Vision-Lock + evidence-gated step execution and recovery
    ├── code-review/          # local diff review (correctness, tests, plan conformance)
    ├── debug-detective/      # systematic debugging (reproduce -> root cause -> fix -> regression)
    └── security-check/       # pre-release security audit (secrets, deps, auth, ...)
```

> **Prerequisites for on-demand fetching:** `git` and `curl` (the script checks and tells you if they are missing). On Windows use Git Bash. Some fetched skills (e.g. `ui-ux-pro-max`) additionally need Python 3 for their own scripts.

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
git -C /tmp/sk sparse-checkout set skills/smart/skills/smart
cp -r /tmp/sk/skills/smart/skills/smart .claude/skills/ && rm -rf /tmp/sk

# 2. Tell the agent: "activate the smart skill"
#    It detects and installs everything else by itself.
```

## Project Lifecycle with SMART

| Project state | SMART activates | Notes |
|---|---|---|
| New / unclear idea | `project-planner` + `project-memory` | adaptive discovery, epistemic map, Project Brief; `brainstorming` first only when the idea is too vague to model |
| Vision ready | no implementation yet | SMART plays back the final product picture; explicit Vision Lock confirmation is mandatory |
| Plan approved | `project-memory` + `step-pilot` | one scoped task, fresh evidence, durable runway; no execution before Vision Lock |
| Mid-development | task-specific capabilities | select only for the current decision/action; recurring bug → `debug-detective`; material new evidence → SMART re-orientation |
| Ready to release | `security-check` (GATE) + `github-release-management` + `hooks-automation` | security gate is mandatory |
| Maintenance | `github-project-management` | issues, boards |

**Capability triggers (any mode):** the current decision/action can demand a skill regardless of lifecycle phase — PDF/Word/Excel/PowerPoint output → `pdf`/`docx`/`xlsx`/`pptx`, full design system → `ui-ux-pro-max`, web-app testing → `webapp-testing`, building a skill → `skill-creator`, building an MCP server → `mcp-builder`, Claude Code hooks/commands/plugins → the `plugin-dev` suite. Full index in [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md).

## Skill Sources (what fetch-skill.sh pulls from)

| # | Source | Count | Content |
|---|---|---|---|
| 1 | this repo, `skills/*/skills/*` | 7 | smart, planner, memory, step-pilot, code-review, debug-detective, security-check |
| 2 | `anthropics/skills` → `skills/` | 17 | pdf, docx, xlsx, pptx, doc-coauthoring, frontend-design, webapp-testing, skill-creator, mcp-builder, claude-api, canvas-design, theme-factory, … |
| 3 | `obra/superpowers` → `skills/` | 13 | test-driven-development, brainstorming, writing-plans, git-worktrees, parallel agents, … (`using-superpowers` is blocked) |
| 4 | `Saeedkhoshafsar/ruflo` → `.claude/skills` | 39 | memory, GitHub, swarm, quality, … (14 BLACK-tier internals are blocked) |
| 5 | `Saeedkhoshafsar/claude-plugins-official` → `plugins/*/skills` | 17 | claude-automation-recommender, playground, claude-md-improver, plugin-dev suite, mcp-server-dev suite, … |
| 6 | `nextlevelbuilder/ui-ux-pro-max-skill` → `.claude/skills` | 7 | ui-ux-pro-max (67+ styles / 161 palettes / 57 font pairings / design-system generator), ui-styling, design-system, brand, banner-design, slides, design |
| 7 | `coreyhaines31/marketingskills` → `skills/` | many | marketing strategy, copy, SEO, CRO, analytics, growth, and RevOps |

Priority: first source that has the skill wins — duplicates (skill-creator vs skill-builder, TDD variants, …) are resolved in the catalog's duplicate-resolution table.

Two root-folder skills are also available: `stop-slop` for prose quality and `remotion-video` for programmatic React videos. `NeoLabHQ/context-engineering-kit` stays a native plugin marketplace so its agents, commands, hooks, and skills are preserved, but SMART handles marketplace setup and selective plugin installation automatically through `fetch-skill.sh`. For example, `fetch-skill.sh spec-driven-development` resolves to CEK's `sdd` plugin.

Details and tiers for all skills → [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md)

## Updating (marketplace installs)

Plugins installed from a marketplace are **pinned copies** — they do NOT auto-update.
When this repo changes, update your local install in two steps:

```bash
claude plugin marketplace update saeed-skills   # 1. refresh the marketplace catalog
claude plugin update smart@saeed-skills         # 2. pull the new plugin version
# (or /plugin → manage → update inside a session)
```

Capabilities installed on demand are pinned snapshots/packages — refresh a standalone skill or native plugin with:

```bash
bash skills/smart/skills/smart/scripts/fetch-skill.sh --update <skill-name>
```
(`--update` re-downloads standalone skills from their recorded original source and delegates native plugin updates to Claude Code.)
