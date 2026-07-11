# Changelog

All notable changes to this marketplace are documented here.
Versioning: bump plugin versions in `.claude-plugin/marketplace.json` and each
plugin's `plugin.json` — `claude plugin update` only detects updates through a
version bump in `marketplace.json`.

## [Unreleased]

### Changed
- SMART's adversarial scenarios are now validated entirely offline with a dependency-free schema validator and CI contract tests.
- Durable `docs/STATE.md` continuity is refocused on SMART's core role as the project's zero-configuration skill-manager brain.
- Bundled companion capabilities now install idempotently as native plugins from SMART's trusted marketplace; users are no longer asked to install companions, choose a source, or run additional setup commands.
- Third-party quarantine now emits a structured approval handoff for SMART instead of printing user-facing activation commands; SMART presents one plain-language approve-or-reject decision and performs approved mechanics itself.
- Healthy projects now use a progress-first SMART fast path: one focused state/task read, one mode decision, immediate approved action, fresh verification, and only the changed memory delta.
- Step Pilot treats green-gate execution as one internal pass rather than nine user-visible phases; deeper orchestration activates only on an explicit trigger.
- Workflow changes that cannot be written with the current GitHub credential are staged under `ci/` with an explicit post-PR manual destination instead of blocking product work.
- SMART and marketplace version `2.3.3`; Step Pilot version `1.2.1`.

### Security
- Third-party standalone capabilities still use the existing fail-closed quarantine, static scan, accountable approval, and immutable lock workflow; first-party routing does not weaken that boundary.
- Static scan success remains explicitly non-consensual: rejected candidates stay quarantined, and activation still requires an accountable human decision.

### Removed
- The live model-evaluation harness, semantic observer, staged paid workflow, API credentials, secrets, model selection, and external endpoint configuration.

## [2.3.0] - 2026-07-11

### Added
- Eight adversarial SMART scenario contracts covering Vision Lock, durable resume, conflict recovery, capability restraint, supply-chain safety, release evidence, and fresh verification.
- Deterministic tests for scenario schema, safety criteria, filtering, thresholds, types, identifiers, and forbidden-pattern syntax.

### Changed
- GitHub Actions runs the complete unit and offline contract-test suite on pushes and pull requests, closing the CI-enforcement gap recorded in `2.2.0`.

## [2.2.0] - 2026-07-11

### Added
- Machine-verifiable Vision Lock artifacts bound to the exact Project Brief SHA-256 and accountable confirmer identity.
- Fresh Verify artifacts bound to the current full commit, command result, and working-tree fingerprint; code or worktree changes invalidate GREEN evidence.
- Release Gate artifacts that require and checksum-bind security, migration, backup, restore, smoke-test, and post-deploy health evidence plus accountable approval and rollback instructions.
- Behavioral gate tests for stale/tampered evidence, failed commands, changed briefs and trees, unsafe evidence paths, and blocked security results.

### Changed
- SMART, Project Planner, Project Memory, Step Pilot, and Security Check now require machine gate results in addition to Markdown state.
- Security Check emits a structured release verdict; SMART `2.2.0`, planner/memory/step-pilot `1.2.0`, and security-check `1.1.0`.
- The CI unit/behavioral-test step is prepared but remains pending because the automation token lacks GitHub's `workflows` permission; local execution is mandatory meanwhile.

## [2.1.1] - 2026-07-11

### Changed
- Internal SMART capability sources now resolve from the stable `main` branch instead of the development branch.

### Security
- Installer targets under `.git`, `.github/workflows`, `node_modules`, `.venv`, and `vendor` are rejected even when they remain inside the project root.
- Scan-report SHA-256 is recorded in installer state and lock entries, checked again before approval, and verified for active installations.
- Behavioral coverage now includes sensitive targets, hardlinks, file/size limits, active-tree tampering, scan-report tampering, and stable internal refs.

## [2.1.0] - 2026-07-11

### Added
- Trusted Installer v1 for standalone skills: commit lockfile, deterministic reinstall, quarantine lifecycle, checksum manifests, static pre-screening, explicit accountable activation, and lock verification.
- Safe `candidate` intake for skills found during repository research, allowing reuse before creation without silently trusting or catalog-promoting third-party code.
- Behavioral installer tests using local Git fixtures; CI execution remains pending until the workflow can be updated with workflow-authorized credentials.

### Security
- Skill names, repositories, refs, repository paths, destinations, symlinks, hardlinks, file counts, and payload sizes are validated fail-closed.
- Removed silent branch-to-default fallback and unsafe in-place replacement. Only explicit `update` resolves a newer commit, which remains quarantined until re-review.
- Static reports flag executables, binaries, bootstrap pipes, privilege/eval patterns, sensitive credential paths and variables, network tooling, and missing license evidence.

### Changed
- SMART requires a documented catalog/repository reuse search before creating a new skill and routes discovered candidates through the same quarantine and lock workflow.
- Marketplace and SMART version `2.1.0`.

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
