# Changelog

All notable changes to this marketplace are documented here.
Versioning: bump plugin versions in `.claude-plugin/marketplace.json` and each
plugin's `plugin.json` — `claude plugin update` only detects updates through a
version bump in `marketplace.json`.

## [2.0.0] - 2026-07-11

### Added
- Evidence-aware Project Model with explicit `KNOWN`, `INFERRED`, `ASSUMED`, `UNKNOWN`, and `CONFLICT` states.
- Adaptive, information-gain discovery for non-expert idea owners plus a mandatory Vision Playback and explicit Vision Lock before planning or code.
- Operating modes independent of filesystem phase: bootstrap, discovery, vision-lock, planning, execution, recovery, stabilization, release, and maintenance.
- Canonical Project Brief / Plan / State / Decisions / Research memory model, assumption expiry, capability inventory, meaningful change ledger, and a three-action runway.
- Specialist-lens routing and a gated capability-gap protocol using `skill-creator`, least privilege, and adversarial evaluations.

### Changed
- SMART now chooses the next best action by information gain, user value, risk reduction, reversibility, effort, and dependencies before selecting capabilities.
- Project Planner now performs viability/responsibility review and sequences plans by learning and risk rather than a fixed seven-question interview.
- Step Pilot refuses execution without confirmed Vision Lock and fresh acceptance evidence, and enters recovery instead of repeating failed fixes.
- Marketplace version `2.0.0`; SMART `2.0.0`; planner, memory, and step-pilot `1.1.0`.

## [1.5.0] - 2026-07-11

### Added
- Unified capability installation in `fetch-skill.sh`: SMART now resolves both standalone skills and native marketplace plugins from one capability name.
- Automatic Context Engineering Kit marketplace setup and selective installation for reflection, SDD, judged subagents, review, DDD, Kaizen, FPF, docs, Git, TDD, tech-stack, MCP, and agent-customization workflows.
- Idempotent native-plugin detection, `cek:<plugin>` direct aliases, plugin-aware `--installed`, and native-plugin `--update` support.

### Changed
- SMART now owns source, package-type, marketplace, and command decisions; users activate SMART only and are never asked where or how to install a capability.
- The three-install limit now counts standalone skills and native plugins together.
- Marketplace version `1.5.0`; SMART version `1.4.0`.

## [1.4.0] - 2026-07-11

### Added
- `coreyhaines31/marketingskills` as a standalone on-demand source for marketing, copy, SEO, CRO, analytics, growth, and RevOps skills.
- `stop-slop` and `remotion-video` root-folder aliases, preserving their reference files and scripts during installation.
- Context Engineering Kit guidance: install its marketplace plugins directly rather than flattening its commands, agents, hooks, and skills into one folder.

### Changed
- SMART triggers, the catalog, and source documentation now cover marketing, prose-quality, programmatic-video, and context-engineering capabilities.
- `fetch-skill.sh` safely supports root-folder skill repositories without copying the clone metadata.
- Marketplace version `1.4.0`; SMART version `1.3.0`.

## [1.3.0] - 2026-07-08

### Added
- **Source #6 — `nextlevelbuilder/ui-ux-pro-max-skill`** (7 skills): `ui-ux-pro-max`
  (67+ UI styles, 161 palettes, 57 font pairings, design-system generator),
  `ui-styling`, `design-system`, `brand`, `banner-design`, `slides`, `design`.
  New Category 12 in the catalog + capability triggers in SMART.
- **Supply-chain gate** in SMART: mandatory 30-second review of every externally
  fetched skill's SKILL.md and scripts before use.
- `LICENSE` (MIT), `CHANGELOG.md`, GitHub Actions CI (`ci/github-workflow-validate.yml` — copy to `.github/workflows/validate.yml` to activate:
  JSON validity, bash syntax, plugin structure, frontmatter, marketplace consistency).
- `fetch-skill.sh` hardening: dependency check (git/curl), heredoc usage text,
  branch fallback to default branch, `--update` re-fetches from the ORIGINAL
  recorded source (`.installed.log`), auto-adds `.claude/skills/` to `.gitignore`.

### Changed
- **BREAKING (layout): all 7 plugins restructured to the standard Claude Code
  plugin layout** — `skills/<plugin>/skills/<skill>/SKILL.md` (previously
  SKILL.md sat at the plugin root and would not load when installed via
  `claude plugin install`).
- SMART's SKILL.md now uses `${CLAUDE_PLUGIN_ROOT}` for script paths (relative
  paths broke when installed as a plugin).
- Frontmatter `tools:` → `allowed-tools:` in all 7 skills (spec-compliant).
- Catalog: `using-superpowers` documented as BLACK-tier (was blocked in the
  script but missing from the catalog); categories renumbered 1–13 with the
  BLACK-tier ruflo internals last; counts updated to 86 installable / 6 sources.
- Version bumps: marketplace 1.3.0, smart 1.2.0, all other plugins 1.0.1.

## [1.2.0] - 2026-07-08

- SMART goes multi-source: 79 installable skills from 5 sources, free-hand
  capability selection, nested-path alias map, BLACK-tier blacklist.

## [1.1.0] - 2026-07-08

- Agent-optimized English rewrite of all skills, new `code-review` skill, `CLAUDE.md`.
- Claude Code plugin marketplace + `debug-detective` & `security-check` skills.

## [1.0.0] - 2026-07-08

- Initial SMART skill-manager system: smart, project-planner, project-memory,
  step-pilot + verified catalog.
