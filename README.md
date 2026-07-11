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
    │           ├── fetch-skill.sh  # unified skill + native-plugin capability installer
    │           └── smart-gates.py  # machine-verifiable Vision, Verify, and Release gates
    ├── project-planner/      # adaptive discovery + Project Brief + Vision Lock + atomic PLAN.md
    ├── project-memory/       # canonical truth + resume packet + decisions/assumptions/runway
    ├── step-pilot/           # Vision-Lock + evidence-gated step execution and recovery
    ├── code-review/          # local diff review (correctness, tests, plan conformance)
    ├── debug-detective/      # systematic debugging (reproduce -> root cause -> fix -> regression)
    └── security-check/       # pre-release security audit (secrets, deps, auth, ...)
```

> **Prerequisites for on-demand fetching:** `git`, `curl`, Python 3, and `file` (the script checks and reports missing tools). On Windows use Git Bash with Python available. Some fetched skills (e.g. `ui-ux-pro-max`) additionally use Python for their own scripts.

## Install on Claude Code (primary path — plugin marketplace)

```bash
# 1. Add the marketplace (once):
claude plugin marketplace add Saeedkhoshafsar/Skills
#    or inside a session:  /plugin marketplace add Saeedkhoshafsar/Skills

# 2. Install the mother skill (enough — it manages the rest):
claude plugin install smart@saeed-skills

# No companion setup is required. SMART installs project-planner, project-memory,
# step-pilot, code-review, debug-detective, or security-check itself when needed.

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

### Progress-first fast path

For a healthy project with current STATE, confirmed gates, and an approved task, SMART does
not rerun the full discovery/orchestration ceremony. It reads the compact resume packet and
current task, reuses active capabilities, performs one approved action, verifies it, and
records only the changed memory. The deeper loop activates only for missing/stale state,
conflict, material risk, phase change, blocked verification, or a real capability gap.

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

Bundled SMART companions are native plugins from the same trusted marketplace. When SMART selects one, its unified installer adds the marketplace if needed and activates only that plugin; the user does not run setup commands or choose a source. Third-party standalone capabilities use a fail-closed trusted-install workflow: a first install resolves the configured ref to a full commit, downloads into quarantine, runs a static pre-screen, and remains unavailable until an accountable review explicitly activates it. Activation writes `.smart-lock.json`; later installs use exactly that commit. Only `update` resolves a newer commit, and the active version remains unchanged until the new candidate is reviewed.

SMART owns this lifecycle end to end. It discovers or receives a narrowly scoped candidate,
resolves immutable provenance, quarantines and scans it, and reviews the candidate before any
activation. When human consent is required, SMART summarizes the source, material findings,
requested access, and residual risk in plain language and asks one approve-or-reject question.
The user never receives an installer command, reviewer flag, source menu, or package choice.
After explicit approval SMART records the accountable identity and performs activation itself;
rejection leaves the candidate unavailable.

Candidate discovery is intentionally not approval. Static scanning cannot prove safety.
Symlinks, hardlinks, path escape, oversized payloads, and unsafe destinations fail closed;
suspicious executables, binaries, secret access, network/bootstrap patterns, and missing
licenses require review. Silent fallback to a default branch is forbidden. Native marketplace
plugins retain their native install/update mechanism and must be reviewed under their
marketplace provenance controls.

## Machine-verifiable execution gates

SMART includes `smart-gates.py` so Vision Lock, task verification, and release readiness are executable checks rather than Markdown promises. Artifacts are written atomically under `.smart/evidence/`, bind evidence by SHA-256, reject paths outside the Git project, and fail closed when the brief, working tree, commit ancestry, or release evidence changes.

```bash
GATES=skills/smart/skills/smart/scripts/smart-gates.py

# Product owner confirms the exact Project Brief.
python3 "$GATES" vision confirm \
  --brief docs/PROJECT-BRIEF.md --confirmed-by <identity>
python3 "$GATES" vision check

# Run and bind fresh task verification to the current commit and working tree.
python3 "$GATES" verify run \
  --task-id P1-T3 --command 'python3 -m unittest discover -s tests -v'
python3 "$GATES" verify check

# Release evidence files must already exist before Verify runs. The security report is
# JSON with at least {"verdict":"PASS","critical_findings":0}.
python3 "$GATES" release create --version <version> --approved-by <identity> \
  --security-report evidence/security.json --migration-plan evidence/migration.txt \
  --backup-evidence evidence/backup.txt --restore-evidence evidence/restore.txt \
  --rollback-command '<tested rollback command>' \
  --smoke-test-evidence evidence/smoke.txt \
  --health-check-evidence evidence/health.txt
python3 "$GATES" release check
```

For projects where migration, backup, or restore is genuinely not applicable, provide a reviewed evidence file that states `NOT_APPLICABLE`, the reason, owner, and date; omitting the evidence is intentionally not allowed.

## Offline behavioral contracts for SMART

SMART ships eight adversarial scenario contracts covering premature implementation, unconfirmed Vision Lock, durable-state resume, conflicting evidence, speculative capability installation, unsafe skill candidates, incomplete release evidence, and stale task verification. They preserve expected behavior as reviewable repository data without introducing a runtime observer.

Validation is deterministic, dependency-free, and part of normal CI:

```bash
EVALS=skills/smart/skills/smart/evals
python3 "$EVALS/validate_behavioral_scenarios.py"

# Validate selected contracts when editing the suite.
python3 "$EVALS/validate_behavioral_scenarios.py" \
  --scenario vague-idea-no-code \
  --scenario release-with-missing-evidence
```

The validator checks scenario structure, safety criteria, thresholds, types, unique identifiers, and forbidden-pattern syntax. It performs no network requests, invokes no model, requires no credentials or repository secrets, and creates no paid evaluation path. SMART itself remains the only skill a user activates; these contracts are free maintainer safeguards, not user configuration.
