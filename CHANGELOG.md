# Changelog

All notable changes to this marketplace are documented here.
Versioning: bump plugin versions in `.claude-plugin/marketplace.json` and each
plugin's `plugin.json` — `claude plugin update` only detects updates through a
version bump in `marketplace.json`.

## [2.5.17] - 2026-07-18

Depth Reprocess + evidence-rooted thought trees (no false confidence; creativity ≠ truth).

### Added
- SMART invariant **12** + full **Depth Reprocess** protocol (L0–L4, optional L5):
  depth triggers, operating rules, stop conditions, durable depth record, anti-patterns.
- SMART invariant **13** + **Evidence-rooted thought trees**: truth trunk vs creative
  trunk; label-at-birth; promotion requires a root; training-frequency is never proof;
  creativity stays free; root check before commit.
- Lessons encoded from multi-pass creative failure modes (literalism, no self-review,
  unused budget leverage, single tool-route lock-in) without importing external runtimes.
- Step Pilot verify layer 6 + anti-pattern: no DONE on depth-triggered gen without L4.
- Project-planner budget lever note + creative/paid-gen depth note in Stage 1.5.
- Offline scenarios `depth-reprocess-before-paid-gen`, `surface-pass-not-enough-on-depth`,
  `creative-not-truth-no-false-confidence` (36 scenarios).
- Contract tests for Depth Reprocess + evidence-rooted trees across SMART / step-pilot /
  planner.

### Changed
- SMART `2.5.17`; step-pilot `1.3.0`; project-planner `1.5.0`; marketplace metadata `2.5.17`.
- README excellence section + CLAUDE hard rules 15b/15c; progress-first lists depth triggers.
- DECIDE scores **depth residual** when triggers are live.

### Notes
- Depth is **not** a tax on mechanical fast-path work.
- Honesty does **not** throttle creativity — it forbids mislabeling creative branches as fact.
- Still one orchestrator; no multi-agent company theater.

## [2.5.16] - 2026-07-17

Catalog + installer: `scroll-world` (oso95) as a SMART-managed YELLOW capability;
slash-entry honesty: only **`/smart:smart`** is the canonical invoke path.

### Added
- `fetch-skill.sh` alias: `scroll-world|oso95/scroll-world|main|skills/scroll-world`
  (nested path; not a root-folder skill).
- Full SMART profile in `SKILLS_CATALOG.md` Category 8: when/not-when, prerequisites
  (Higgsfield CLI + ffmpeg + optional Codex stills), cost model (≈N stills + 2N−1
  videos; mobile ≈2×), seam/frame-lock quality rule, architecture A vs B, install
  quarantine path, complements vs `ui-ux-pro-max` / `remotion-video`.
- Duplicate-resolution row: scroll-scrubbed cinematic world landing → `scroll-world`
  (not Remotion, not hand-rolled WebGL).
- Capability-need quick index + Additional External Sources row for `oso95/scroll-world`.
- SMART lifecycle defaults + design lens for scroll-world / Remotion triggers.
- README / CLAUDE.md source list and hard-rule trigger wording.
- Contract tests: scroll-world alias + catalog profile; canonical `/smart:smart` entry;
  marketplace pin `2.5.16`.

### Fixed
- Docs no longer claim bare `/smart` works. Claude Code **always namespaces** plugin
  skills/commands as `/<plugin>:<name>`, so the real entry is **`/smart:smart`**.
  README, catalog Category 0, `commands/smart.md`, and SMART host playbook updated;
  bare `/smart` is explicitly documented as non-resolving.

### Changed
- SMART `2.5.16`; marketplace metadata `2.5.16`.

### Notes
- Third-party MIT skill; install remains fail-closed (quarantine → review → approve).
- Paid generation: SMART must surface budget estimate and get go-ahead before gens.
- Does not replace design systems or programmatic video timelines.
- Historical CHANGELOG entries that said `/smart` remain as ship history; current
  user-facing docs use `/smart:smart` only.

## [2.5.15] - 2026-07-17

Field-validated host-supervision fix: `memory resume-check` must not confuse a later bash fence with the Resume packet.

### Fixed
- `smart-gates.py extract_resume_packet`: bound the packet to the Resume section
  (heading → next heading). Accept table-form packets; only honor a fenced body
  when the fence opens near the section start. Prevents false RED when
  `## Next-session command packet` appears later in real STATE files.
- Regression test:
  `test_memory_resume_check_accepts_table_packet_despite_later_command_fence`.

### Changed
- SMART `2.5.15`; marketplace metadata `2.5.15`.
- Unittest suite **219 OK** (was 218).

## [2.5.14] - 2026-07-17

Discovery elevation: landscape research + budget×quality (SMART-shaped, not MetaGPT).

### Added
- project-planner **Stage 1.5 — Landscape research** before Vision Lock: competitors,
  similar public repos, substitutes, cost-of-quality; writes `docs/RESEARCH.md` and
  promotes only decision-changing claims into Project Mind.
- **Budget × quality bar**: money/time/skill floor + quality ceiling; best-within-budget.
- Vision Lock gates: landscape coverage (or explicit N/A) and budget×quality when relevant.
- SMART specialist lenses + lifecycle routes for landscape, UI system, SEO/marketing.
- Offline scenarios `landscape-research-before-code`, `budget-quality-tradeoff-recorded`
  (33 scenarios).
- Contract test for landscape/budget gates and anti multi-agent-company simulation.

### Changed
- SMART `2.5.14`; project-planner `1.4.0`; marketplace metadata `2.5.14`.
- Explicit non-goal: do **not** become MetaGPT / multi-agent software-company runtime.

### Notes
- Patterns inspired by MetaGPT SOPs (research before build, specialist-on-decision) only.
  No MetaGPT dependency, no permanent agent cast, max-3 capabilities unchanged.

## [2.5.13] - 2026-07-17

Hermes-port **Phase 8**: identity, personality, dashboard, migration polish.

### Added
- `identity_store.py`: optional `docs/SOUL.md` load/seed/scan/truncate;
  personality presets; light multi-profile metadata; memory dashboard;
  non-destructive `migrate` for empty USER/AGENT-MEMORY.
- SMART CONSOLIDATE step 12 + anti-patterns (SOUL ≠ product truth; no wipe).
- CLAUDE.md hard rule 22 + README learning-memory section.
- Offline scenarios `identity-soul-not-product-truth`,
  `identity-migrate-preserves-existing` (31 scenarios).

### Changed
- project-memory `1.11.0`; SMART `2.5.13`; marketplace metadata `2.5.13`.
- project-memory **Identity / personality / dashboard** protocol.

### Notes
- Phase 8 of `docs/HERMES-PORT-PLAN.md` complete (C-14 DONE; C-13 light/LATER
  full isolation). Hermes learning-memory port phases 0–8 closed; Phase 9 is
  product-surface backlog (explicit opt-in only).

## [2.5.12] - 2026-07-17

Hermes-port **Phase 7**: external memory providers / mind-clone interface.

### Added
- `memory_provider.py`: MemoryProvider ABC; `<memory-context>` fence + scrub;
  **builtin** (USER/AGENT-MEMORY), **null**, **local** SQLite fact adapter.
- `memory_manager.py`: one-external limit; prefetch/sync/tools orchestration;
  `build_manager`; CLI status/catalog/system-prompt/prefetch/tool-call/scrub.
- Config `memory.provider` = `builtin` (default) | `null` | `local` | catalog.
- Provider catalog docs (Honcho, Mem0, Supermemory, Hindsight, … optional).
- SMART CONSOLIDATE step 11 + anti-patterns (one external, fence, no Mind replace).
- Offline scenarios `memory-provider-builtin-default`,
  `memory-provider-fence-external-recall` (29 scenarios).

### Changed
- project-memory `1.10.0`; SMART `2.5.12`; marketplace metadata `2.5.12`.
- project-memory **External memory providers** protocol + commit checklist.

### Notes
- Phase 7 of `docs/HERMES-PORT-PLAN.md` complete for MVP (C-18…C-20, C-23, C-24;
  C-21/C-22 catalog LATER). CI stays offline-green. Phase 8 next: identity/profiles.

## [2.5.11] - 2026-07-17

Hermes-port **Phase 6**: episodic session search (FTS5 / LIKE).

### Added
- `session_store.py`: per-project `.smart/sessions/state.db` with sessions +
  messages, FTS5 when available, LIKE fallback.
- Search shapes: **discovery** / **scroll** / **browse**; automation sources
  demoted/hidden by default.
- Privacy: redaction hooks on append (API keys, PEMs, tokens); local-only.
- `extract-durable` candidates for pre-compact / handoff promotion (C-26 protocol).
- SMART CONSOLIDATE step 10 + routing: prefer USER/AGENT-MEMORY first.
- Offline scenarios `session-search-prefer-always-on`,
  `session-search-historical-decision` (27 scenarios).

### Changed
- project-memory `1.9.0`; SMART `2.5.11`; marketplace metadata `2.5.11`.
- project-memory **Episodic session search** protocol + commit checklist.

### Notes
- Phase 6 of `docs/HERMES-PORT-PLAN.md` complete (C-15, C-16, C-26 protocol).
  Phase 7 next: external memory providers.

## [2.5.10] - 2026-07-17

Hermes-port **Phase 5**: skill library curator (lifecycle hygiene).

### Added
- `skill_curator.py`: deterministic active → stale → archived transitions;
  pin; archive/restore under `.smart/skills-archive/`; curator-state sidecar;
  idle/interval gate (`should-run` / `run`).
- Defaults: stale after **30d**, archive after **90d**, **never auto-delete**;
  consolidate **OFF** by default (Hermes parity).
- Lifecycle APIs on `skill_usage.py`: `set-state`, `set-pinned`,
  `list-agent-created`, `can-archive`, activity derivation.
- Protected builtins never archived (same 7 companions as Phase 4).
- Offline scenarios `curator-archive-stale-agent-skill`,
  `curator-protected-never-archived` (25 scenarios).

### Changed
- project-memory `1.8.0`; SMART `2.5.10`; marketplace metadata `2.5.10`.
- SMART CONSOLIDATE step 9 + anti-patterns for curator hygiene.
- project-memory **Skill library curator** protocol (idle-triggered).

### Notes
- Phase 5 of `docs/HERMES-PORT-PLAN.md` complete (C-39…C-42).
  Phase 6 next: episodic session search.

## [2.5.9] - 2026-07-17

Hermes-port **Phase 4**: procedural skill self-improvement.

### Added
- `skill_usage.py`: `.smart/memory/skill-usage.json` sidecar (view/use/patch
  counters, agent-created provenance, protected builtins).
- CLI: `status`, `bump`, `mark-created`, `can-delete`, `check-create`,
  `scan-content`, `check-path`.
- Patch-on-correction protocol: view-before-patch; support layout
  `references/` / `templates/` / `scripts/`; authoring standards (description
  ≤60 chars).
- `/learn`-equivalent distill path in SMART CREATE + project-memory.
- Agent-created skill threat scan via shared `scan_threats`.
- Offline scenarios `skill-self-improve-how-to-preference`,
  `skill-self-improve-protected-no-delete` (23 scenarios).

### Changed
- project-memory `1.7.0`; SMART `2.5.9`; marketplace metadata `2.5.9`.
- SMART CREATE steps include authoring standards, security gate, patch-on-correction.
- CONSOLIDATE step 8 + anti-patterns for skill self-improve.

### Notes
- Phase 4 of `docs/HERMES-PORT-PLAN.md` complete (C-35…C-38, C-43, C-45).
  Phase 5 next: curator (library hygiene).

## [2.5.8] - 2026-07-17

Hermes-port **Phase 3**: self-learning loop — nudges + background/inline review.

### Added
- `memory_store.py` **loop** sidecar: `.smart/memory/loop-state.json` with
  `user_turn_count`, `turns_since_memory`, `turns_since_skill`; CLI
  `loop status|tick|mark-reviewed|reset`.
- Configurable intervals: `memory_nudge_interval` default **10**,
  `skill_nudge_interval` default **15** (config top-level or nested `loop.*`;
  `0` disables).
- project-memory **Self-learning loop** protocol: Memory / Skill review prompts
  (adapted Hermes), event + interval triggers, inline vs forked review,
  notification policy (quiet by default), skill-review anti-patterns.
- SMART CONSOLIDATE step 7: `loop tick` → due/event review → `mark-reviewed`;
  never blocks Task Verify / Vision.
- Offline scenarios `learning-memory-user-correction-nudge`,
  `learning-memory-empty-session-nothing-to-save` (21 scenarios).

### Changed
- project-memory `1.6.0`; SMART `2.5.8`; marketplace metadata `2.5.8`.
- `status` includes `loop` due flags; anti-patterns cover stall-for-review and
  “tool broken forever” / one-off narrative skills.

### Notes
- Phase 3 of `docs/HERMES-PORT-PLAN.md` complete (C-30…C-34, C-44 protocol-level).
  Phase 4 next: procedural skill self-improvement.

## [2.5.7] - 2026-07-17

Hermes-port **Phase 2**: threat scan on learning-memory writes/loads + optional write approval.

### Added
- Threat pattern scanner in `memory_store.py` (instruction override, role markers,
  exfil/credential phrasing, invisible/bidi Unicode). Blocks matching writes;
  on load, blocked raw entries stay inspectable via `status` / `blocked_entries`
  and are excluded from the frozen always-on snapshot.
- Optional `write_approval` (default **false**; recommend **true** for novices)
  via `.smart/memory/config.json` or `--write-approval`. Queues add/replace/remove
  under `.smart/memory/pending.json` until `pending approve` / `pending reject`.
- CLI: `pending list|approve|reject`; status reports `write_approval`,
  `blocked_count`, `pending_count`.
- Offline scenarios `learning-memory-threat-block`,
  `learning-memory-write-approval` (19 scenarios).

### Changed
- project-memory `1.5.0`; SMART `2.5.7`; marketplace metadata `2.5.7`.
- SMART CONSOLIDATE + anti-patterns cover blocked writes and pending-vs-saved claims.
- project-memory Security baseline documents threat scan + approval protocol.

### Notes
- Phase 2 of `docs/HERMES-PORT-PLAN.md` complete (C-09, C-10). Phase 3 next:
  nudges + background review.

## [2.5.6] - 2026-07-17

Hermes-port **Phase 1**: bounded dual learning-memory stores on top of Project Mind.

### Added
- `project-memory` **Learning memory** protocol: `docs/USER.md` (profile, 1375 chars)
  + `docs/AGENT-MEMORY.md` (agent notes, 2200 chars), `§`-delimited entries,
  add/replace/remove, frozen snapshot, write routing vs Project Mind.
- `scripts/memory_store.py` CLI/library for load/save, budgets, substring match,
  overflow-without-silent-drop, duplicate no-op, render/status.
- SMART SENSE reads USER/AGENT-MEMORY frozen snapshot; CONSOLIDATE routes prefs
  vs operational lessons vs product truth.
- Unit/CLI tests `tests/test_memory_store.py` and offline scenarios
  `learning-memory-save-preference`, `learning-memory-no-product-leak` (17 scenarios).

### Changed
- project-memory `1.4.0`; SMART `2.5.6`; marketplace metadata `2.5.6`.
- Anti-patterns forbid product-fact leakage into learning stores and silent overflow drops.

### Notes
- Phase 0 of `docs/HERMES-PORT-PLAN.md` is complete (D1–D4 frozen).
- Threat scan + write approval remain Phase 2.

## [2.5.5] - 2026-07-16

SMART becomes the supervisor of **Claude Code host commands** as well as
installable skills — one brain over the whole slash menu.

### Added
- **Category 0 — Native Claude Code host commands** in `SKILLS_CATALOG.md`
  (GREEN observational, YELLOW session/config, RED autonomy) covering the
  built-in slash surface: `/context`, `/compact`, `/clear`, `/model`, `/effort`,
  `/fast`, `/loop`, `/goal`, `/doctor`, `/mcp`, `/agents`, `/verify`, and related
  host tools. These are supervised, not fetched.
- **Native host-command supervision** contract in SMART: memory-before-amnesia
  for `/compact`/`/clear`, Vision-before-autonomy for `/loop`/`/goal`, rate-limit
  model fallbacks, install `/doctor` path, and CREATE-when-missing.
- Offline scenarios `native-command-unsafe-compact` and
  `native-command-premature-loop` (15 scenarios total).
- Agent hard rule 21 + `/smart` command host-supervision step.

### Changed
- SELECT/ACT lifecycle defaults include host playbooks; anti-patterns forbid
  amnesiac compact and premature autonomous loops.
- SMART version `2.5.5`; marketplace metadata `2.5.5`.

## [2.5.4] - 2026-07-16

Continuity under real session pressure — context fill, archive bloat, and
pre-existing projects must not force rediscovery or lost progress.

### Added
- **Context-budget phases 40/60/80** in SMART: short writes → stop exploration →
  hard handoff with complete resume packet + `memory resume-check`.
- **Pre-existing project bootstrap**: prefer `STATE2` → resume confirmed vision;
  never rebuild empty mind/brief ceremony when durable truth already exists.
- **Hard archive / compaction rule** in project-memory (~200 lines / noise /
  surface-track STATE2 split) with post-archive resume-check still GREEN.
- Offline scenarios `context-budget-hard-handoff` and
  `preexisting-project-no-rebureaucracy`.

### Changed
- SENSE / session-start read order prefers `docs/STATE2.md` over `docs/STATE.md`.
- Agent contract (`CLAUDE.md`) adds rules 18–20 for budget, resume-not-rebuild,
  and hard archive.

### Versions
- SMART `2.5.4`
- project-memory `1.3.2`

## [2.5.3] - 2026-07-16

Real-project continuity gap (mid-mission cutover) — progress must survive
context/daily limits without relying on chat history.

### Added
- **Mid-mission checkpoint protocol** in SMART: checkpoint triggers fire during
  the work (file change, verify result, mode/task change, decision, capability
  change, risky op, ~8 tool turns, handoff/context pressure), not only at the end.
- **`smart-gates.py memory resume-check`**: fail-closed machine check that the
  durable resume packet can restart a zero-context session (mode/task, progress,
  evidence, blocker, next).
- Offline scenario `mid-mission-cutover-resume` and contract tests for the
  checkpoint mandate.

### Changed
- `project-memory` event protocol now treats mid-mission continuity triggers and
  intentional handoffs as first-class write events.
- Fast path requires repairing an incomplete resume packet before coding.

## [2.5.2] - 2026-07-13

First real-world usage feedback (Codespaces cold start) — exactly the
usage-driven maintenance loop the Runway prescribed. Two friction points fixed:

### Fixed
- **Bundled companion detection no longer depends on the `claude` CLI being on
  the Bash subshell's PATH.** In Codespaces/containers the CLI is often absent
  from subshells, so `fetch-skill.sh install project-planner` failed with
  `requires Claude Code CLI` even though the user had installed all companions
  manually through the plugin UI. The installer now checks the Claude plugin
  cache (`~/.claude/plugins/cache`, overridable via `SMART_CLAUDE_PLUGIN_CACHE`)
  first: a cached companion counts as installed (short-circuits before any CLI
  call), `--installed` reports `bundled:<name> INSTALLED (plugin cache: …)`,
  `--update` without the CLI degrades to a non-blocking pointer instead of an
  error, and the truly-missing case fails with an actionable message.

### Added
- **`/smart` slash command** shipped with the plugin (`commands/smart.md`), so
  activation is one short, discoverable command instead of relying on skill
  auto-triggering. README documents the post-install step (restart the session
  for autocomplete) and a troubleshooting table for both reported symptoms.
- 5 installer regression tests covering cache detection with/without the CLI,
  `--installed` reporting, non-blocking update, and CLI short-circuit
  (77 tests total). Installer tests now pin `SMART_CLAUDE_PLUGIN_CACHE` to a
  temp directory so the host's real plugin cache can never leak into results.

## [2.5.1] - 2026-07-11

### Fixed (findings from the first cold-start field test)

A full cold-start field test (empty repo → discovery → mind network → Vision Lock →
plan → execution → interrupt/resume → release) plus 13 adversarial probes confirmed the
gate chain end to end and exposed three real gaps, all closed here:

- **Gate artifacts are now content-sealed.** Every `vision-lock.json`, `verify.json`,
  and `release.json` carries a domain-separated SHA-256 seal over its own payload.
  Hand-editing any field (flipping a RED verify to GREEN, swapping the task ID or
  command, changing the approver) now fails `check` with a clear seal-mismatch error
  instead of passing silently. Legitimate changes require re-running the producing
  command, exactly as the contract already demanded.
- **`vision confirm` fails closed on explicit not-ready signals.** Confirming is
  machine-blocked while the Project Brief's Vision Lock status is `NOT READY` or STATE
  records open `Mind coverage` gaps (`GAPS: …` / `NOT BUILT`) — an impatient agent can
  no longer produce a lock artifact around an incomplete Project Mind.
- **Missing evidence files fail closed cleanly.** A nonexistent evidence path now
  reports `GATE BLOCKED: required file does not exist` instead of a raw traceback.

### Changed
- SMART contract documents the seal and the readiness precondition of `vision confirm`.
- `SKILLS_CATALOG.md` local-skills table now reflects the Project Mind network in the
  `project-planner` and `project-memory` descriptions.
- 8 new gate regression tests (72 total). SMART and marketplace version `2.5.1`.

## [2.5.0] - 2026-07-11

### Added
- **Project Mind — atomic mental network** (`docs/PROJECT-MIND.md`), owned by `project-memory`: every material product fact becomes one addressable, testable node (`M-<domain>-<n>`) with an epistemic label, source, and typed links (`requires/refines/conflicts/serves/constrains`) across 11 domains (intent, people, experience, scope, behavior, data, interfaces, quality, risk, success, evolution).
- **Mind coverage sweep as a Vision Lock precondition**: no critical `UNKNOWN`/`CONFLICT` node, every `ASSUMED` node owned and time-boxed, every milestone mapped to node IDs; recorded in STATE as `Mind coverage`.
- Plan tasks now carry a **`Realizes:`** field citing the mind node IDs they implement; node-less tasks are challenged as scope creep and uncovered must-have nodes surface as gaps.
- SMART invariant 10 "The mind is written, not remembered" and agent hard rule 16; an insight that is not a node does not exist for the next session.
- Offline behavioral scenario `figure-it-out-later-pressure` (10 scenarios total) and 7 new contract tests (64 total).

### Changed
- **"Start building and figure it out later" is explicitly forbidden as a project strategy** under any seniority or deadline pressure; SMART answers pressure with sharper key questions, never by waiving the gate.
- Audience reframed: SMART serves professional development teams first (maximum automation, minimum interruption, only key questions); novice safety is a property of the engineering rigor, not a simplified mode.
- Vision Lock now certifies that SMART's picture and the user's picture are the same picture, inch by inch, backed by the completed mind network.
- SMART and marketplace version `2.5.0`; `project-planner` and `project-memory` version `1.3.0`.

## [2.4.0] - 2026-07-11

### Added
- "Excellence by default" quality contract in SMART: a novice invoking only SMART receives expert-grade output — professional defaults for structure, validation, error handling, and security posture — without ever being asked quality-decision questions.
- Cold-start contract coverage: execution capabilities (`step-pilot`, implementation skills) are verifiably deferred until Vision Lock and plan approval.
- Offline behavioral scenario `novice-gets-expert-quality` guarding against novice-grade shortcuts, quality questionnaires, and over-engineering (9 scenarios total).
- Root `.gitignore` for Python bytecode and SMART runtime artifacts.

### Changed
- SMART anti-patterns now explicitly forbid delegating quality decisions to a novice, shipping novice-grade output, and inflating small projects with heavyweight architecture.
- The quality bar is enforced through existing gates and per-task expert defaults — never as new mandatory stages, reports, or user-visible ceremony.
- SMART and marketplace version `2.4.0`.

## [2.3.3] - 2026-07-11

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
