#!/usr/bin/env python3
"""Contract tests for SMART's vision-first project intelligence system."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMART = ROOT / "skills/smart/skills/smart/SKILL.md"
CLAUDE = ROOT / "CLAUDE.md"
PLANNER = ROOT / "skills/project-planner/skills/project-planner/SKILL.md"
MEMORY = ROOT / "skills/project-memory/skills/project-memory/SKILL.md"
PILOT = ROOT / "skills/step-pilot/skills/step-pilot/SKILL.md"
SECURITY = ROOT / "skills/security-check/skills/security-check/SKILL.md"
GATES = ROOT / "skills/smart/skills/smart/scripts/smart-gates.py"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ManifestContractTests(unittest.TestCase):
    def test_every_manifest_is_valid_json(self) -> None:
        for path in ROOT.glob("skills/*/.claude-plugin/plugin.json"):
            with self.subTest(path=path):
                json.loads(text(path))
        json.loads(text(ROOT / ".claude-plugin/marketplace.json"))

    def test_marketplace_versions_match_plugin_manifests(self) -> None:
        marketplace = json.loads(text(ROOT / ".claude-plugin/marketplace.json"))
        listed = {entry["name"]: entry["version"] for entry in marketplace["plugins"]}
        for name, version in listed.items():
            manifest = json.loads(
                text(ROOT / "skills" / name / ".claude-plugin" / "plugin.json")
            )
            self.assertEqual(version, manifest["version"], name)

    def test_skill_frontmatter_has_contract_fields(self) -> None:
        for path in ROOT.glob("skills/*/skills/*/SKILL.md"):
            with self.subTest(path=path):
                source = text(path)
                self.assertTrue(source.startswith("---\n"))
                frontmatter = source.split("---", 2)[1]
                self.assertRegex(frontmatter, r"(?m)^name:\s*\S+")
                self.assertRegex(frontmatter, r"(?m)^description:\s*(>|\S+)")
                self.assertRegex(frontmatter, r"(?m)^allowed-tools:\s*.+")


class SmartCognitionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.smart = text(SMART)

    def test_epistemic_states_are_explicit(self) -> None:
        for state in ("KNOWN", "INFERRED", "ASSUMED", "UNKNOWN", "CONFLICT"):
            with self.subTest(state=state):
                self.assertIn(state, self.smart)

    def test_operating_modes_cover_whole_lifecycle(self) -> None:
        for mode in (
            "BOOTSTRAP",
            "DISCOVERY",
            "VISION-LOCK",
            "PLANNING",
            "EXECUTION",
            "RECOVERY",
            "STABILIZATION",
            "RELEASE",
            "MAINTENANCE",
        ):
            with self.subTest(mode=mode):
                self.assertIn(f"`{mode}`", self.smart)

    def test_vision_gate_appears_before_action_protocol(self) -> None:
        gate = self.smart.index("## Vision Lock — mandatory gate")
        anti_pattern = self.smart.index("- begins coding after one vague prompt")
        self.assertLess(gate, anti_pattern)
        self.assertIn("Do not create an implementation plan or code", self.smart)

    def test_capability_creation_is_bounded_and_evaluated(self) -> None:
        create_section = self.smart.split(
            "### 8. CREATE — capability-gap protocol", 1
        )[1].split("### 9. ACT", 1)[0]
        for requirement in (
            "Gap proof",
            "skill-creator",
            "Contract first",
            "Least privilege",
            "Adversarial evaluation",
            "Register and remember",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, create_section)
        self.assertIn("maximum 3 newly installed capabilities", self.smart)

    def test_first_invocation_lays_memory_runway(self) -> None:
        self.assertIn("First-invocation bootstrap", self.smart)
        self.assertIn("project-planner", self.smart)
        self.assertIn("project-memory", self.smart)
        self.assertIn("next 1–3 actions", self.smart)

    def test_cold_start_defers_execution_capabilities_until_vision_lock(self) -> None:
        normalized = " ".join(self.smart.split())
        self.assertIn(
            "Defer `step-pilot` until the Vision Lock and plan are approved",
            normalized,
        )
        self.assertIn(
            "do not add implementation skills during discovery",
            normalized,
        )

    def test_excellence_is_a_silent_default_not_a_user_question(self) -> None:
        normalized = " ".join(self.smart.split())
        for requirement in (
            "Professional result by default",
            "Excellence by default — the silent quality bar",
            "Expert defaults, not quality questions",
            "Correct-by-construction tasks",
            "Quality travels with the change",
            "Craft caps at project size",
            "The bar never becomes ceremony",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)

    def test_depth_reprocess_is_contracted(self) -> None:
        normalized = " ".join(self.smart.split())
        for requirement in (
            "Depth over first-pass polish",
            "Depth Reprocess — multi-layer thinking before commitment",
            "Draft ≠ done",
            "Self-review is mandatory on depth work",
            "Budget is a design input, not a scoreboard",
            "Literalism check",
            "Stop conditions (required)",
            "Generate → stick → never rewatch",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)
        pilot = text(ROOT / "skills/step-pilot/skills/step-pilot/SKILL.md")
        self.assertIn("Depth / self-critique", pilot)
        self.assertIn(
            "claim DONE on depth-triggered generative work without an L4 self-critique pass",
            pilot,
        )
        planner = text(
            ROOT / "skills/project-planner/skills/project-planner/SKILL.md"
        )
        self.assertIn("Budget is a design lever, not a spend target", planner)
        self.assertIn("Depth note for creative / paid-gen products", planner)

    def test_evidence_rooted_trees_protect_creativity_without_false_confidence(
        self,
    ) -> None:
        normalized = " ".join(self.smart.split())
        for requirement in (
            "No false confidence; evidence-rooted thought trees",
            "Evidence-rooted thought trees — honesty without killing creativity",
            "Two trunks (never merge silently)",
            "Truth trunk",
            "Creative trunk",
            "Label at birth",
            "Promotion requires a root",
            "Frequency-in-training is never a root",
            "Creativity stays free",
            "Root check before commit",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)

    def test_harness_compat_ledger_is_contracted(self) -> None:
        normalized = " ".join(self.smart.split())
        for requirement in (
            "Harness-compat before thrash",
            "Harness compatibility ledger — model ↔ Claude Code without thrash",
            "references/HARNESS-COMPAT.md",
            "ensure-user-claude-md.sh",
            "~/.claude/CLAUDE.md",
            "lookup → apply → register →",
            "model↔Claude Code harness friction",
            "Soft mid-task trigger",
            "Same-session promote",
            "waits for three thrash attempts before looking up or registering",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)
        ledger = text(
            ROOT / "skills/smart/skills/smart/references/HARNESS-COMPAT.md"
        )
        self.assertIn("HC-001", ledger)
        self.assertIn("redacted_thinking", ledger)
        self.assertIn("HC-002", ledger)
        self.assertIn("/smart:smart", ledger)
        script = ROOT / "skills/smart/skills/smart/scripts/ensure-user-claude-md.sh"
        self.assertTrue(script.is_file(), "ensure-user-claude-md.sh must ship")
        script_text = text(script)
        self.assertIn("BEGIN saeed-skills HARNESS-COMPAT", script_text)
        self.assertIn("/smart:smart", script_text)
        self.assertIn("HARNESS-COMPAT.md", script_text)
        agent = text(CLAUDE)
        self.assertIn("Harness-compat before thrash", agent)
        readme = text(ROOT / "README.md")
        for fragment in (
            "claude plugin marketplace update saeed-skills",
            "claude plugin update smart@saeed-skills",
            "ensure-user-claude-md.sh",
            "/smart:smart",
            "full four-step path",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, readme)
        self.assertIn("Consumer update path", text(
            ROOT / "skills/smart/commands/smart.md"
        ))

    def test_project_mind_network_is_the_written_understanding(self) -> None:
        normalized = " ".join(self.smart.split())
        for requirement in (
            "The mind is written, not remembered",
            "docs/PROJECT-MIND.md",
            "an insight that is not a node does not exist for the next session",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)

    def test_vision_lock_requires_complete_mind_coverage(self) -> None:
        normalized = " ".join(self.smart.split())
        self.assertIn(
            "SMART's picture of the product and the user's picture are the same picture",
            normalized,
        )
        self.assertIn(
            "the Project Mind coverage sweep is COMPLETE",
            normalized,
        )

    def test_figure_it_out_later_is_forbidden_under_pressure(self) -> None:
        normalized = " ".join(self.smart.split())
        self.assertIn(
            "\"Start now and figure it out as we go\" is forbidden as a project strategy",
            normalized,
        )
        self.assertIn(
            "never waive the gate",
            normalized,
        )
        self.assertIn(
            "adopts “start building and figure the product out later” under any pressure",
            normalized,
        )

    def test_pro_teams_are_primary_audience_with_novice_safe_rigor(self) -> None:
        normalized = " ".join(self.smart.split())
        self.assertIn(
            "SMART serves professional development teams first",
            normalized,
        )
        self.assertIn(
            "maximum automation, minimum interruption, only key questions",
            normalized,
        )
        self.assertIn(
            "novice support is a property of the rigor, not a separate simplified mode",
            normalized,
        )

    def test_quality_bar_never_slows_or_inflates_the_project(self) -> None:
        normalized = " ".join(self.smart.split())
        self.assertIn(
            "never through new mandatory stages, reports, or user-visible process",
            normalized,
        )
        self.assertIn(
            "Over-engineering a small project is a quality failure",
            normalized,
        )
        self.assertIn(
            "asks a novice to make quality decisions",
            normalized,
        )
        self.assertIn(
            "ships novice-grade output because the user did not explicitly request professional quality",
            normalized,
        )
        self.assertIn(
            "inflates a small project with heavyweight architecture",
            normalized,
        )

    def test_healthy_projects_use_a_progress_first_fast_path(self) -> None:
        normalized = " ".join(self.smart.split())
        for requirement in (
            "Fast path — default for a healthy, known project",
            "do not rebuild the Project Model",
            "Activate at most one additional capability",
            "advance project work in the same invocation",
            "write only the memory delta",
            "Never spend more report space on SMART's mechanics than on the project result",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)

    def test_mid_mission_checkpoint_is_mandatory(self) -> None:
        normalized = " ".join(self.smart.split())
        for requirement in (
            "Mid-mission memory is mandatory",
            "Mid-mission checkpoint protocol",
            "Checkpoint immediately when any of these fire",
            "never postpone memory until the mission ends",
            "never treat the conversation transcript as the recovery database",
            "waits until mission end to write progress that already changed mode, evidence, or files",
            "smart-gates.py memory resume-check",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)
        memory = text(MEMORY)
        self.assertIn("Mid-mission checkpoint rule", memory)
        self.assertIn("mid-mission continuity trigger", memory)

    def test_context_budget_phases_force_earlier_handoff(self) -> None:
        normalized = " ".join(self.smart.split())
        for requirement in (
            "Context-budget phases (40 / 60 / 80)",
            "~40%",
            "~60%",
            "~80%",
            "Hard handoff mode",
            "continues multi-file exploration or coding past ~80% context fill without a complete resume packet",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)
        agent_contract = " ".join(text(CLAUDE).split())
        self.assertIn("Context-budget phases 40/60/80", agent_contract)

    def test_preexisting_project_bootstrap_skips_rebureaucracy(self) -> None:
        normalized = " ".join(self.smart.split())
        for requirement in (
            "Pre-existing project bootstrap (no ceremony rebuild)",
            "docs/STATE2.md",
            "resume and extend",
            "rebuilds discovery/mind/brief ceremony on a project that already has a valid resume packet and confirmed vision",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)
        memory = " ".join(text(MEMORY).split())
        self.assertIn("Pre-existing project continuity", memory)
        self.assertIn("Prefer STATE2 when present", " ".join(self.smart.split()) + " " + memory)
        agent_contract = " ".join(text(CLAUDE).split())
        self.assertIn("Pre-existing projects resume, they do not re-bootstrap", agent_contract)

    def test_hard_archive_rule_keeps_resume_packet_scannable(self) -> None:
        memory = " ".join(text(MEMORY).split())
        for requirement in (
            "Hard archive / compaction rule",
            "200 lines",
            "docs/STATE2.md",
            "`memory resume-check` on the active packet must still pass",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, memory)
        agent_contract = " ".join(text(CLAUDE).split())
        self.assertIn("Hard archive when STATE bloats", agent_contract)


    def test_native_host_command_supervision_is_first_class(self) -> None:
        normalized = " ".join(self.smart.split())
        for requirement in (
            "Native host-command supervision (Claude Code built-ins)",
            "Host commands are first-class capabilities",
            "Memory before amnesia",
            "Vision before autonomy",
            "runs `/compact` or `/clear` before a complete resume packet",
            "starts `/loop` or `/goal` without Vision Lock",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)
        catalog = text(ROOT / "SKILLS_CATALOG.md")
        self.assertIn("Category 0 — Native Claude Code host commands", catalog)
        self.assertIn("| `/compact` |", catalog)
        self.assertIn("| `/loop` |", catalog)
        agent_contract = " ".join(text(CLAUDE).split())
        self.assertIn("Host-command supervision", agent_contract)

    def test_bundled_companions_are_zero_configuration_for_user(self) -> None:
        normalized = " ".join(self.smart.split())
        self.assertIn("bundled first-party capabilities", normalized)
        self.assertIn(
            "SMART runs their marketplace installation itself",
            normalized,
        )
        self.assertIn(
            "never ask the user to install a companion plugin",
            normalized,
        )
        self.assertIn("no user setup step", normalized)

    def test_restricted_workflows_are_staged_instead_of_blocking_progress(self) -> None:
        agent_contract = " ".join(text(CLAUDE).split())
        self.assertIn("Restricted automation staging", agent_contract)
        self.assertIn("cannot modify `.github/workflows/*`", agent_contract)
        self.assertIn("Create the exact ready-to-copy workflow under `ci/`", agent_contract)
        self.assertIn("manual replacement after the PR", agent_contract)

    def test_third_party_approval_is_plain_language_and_smart_owned(self) -> None:
        normalized = " ".join(self.smart.split())
        for requirement in (
            "third_party_approval_required",
            "ask exactly one plain-language approve-or-reject question",
            "SMART then invokes `approve` itself",
            "Rejection leaves the candidate quarantined and unavailable",
            "Never use quarantined content or treat static scan success as user consent",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)

    def test_machine_gate_protocol_is_required(self) -> None:
        self.assertTrue(GATES.is_file())
        for gate in ("vision check", "verify check", "release check"):
            with self.subTest(gate=gate):
                self.assertIn(gate, self.smart)
        self.assertIn("not a substitute for a passing artifact", self.smart)

    def test_learning_memory_read_order_and_routing_are_documented(self) -> None:
        """Hermes-port separation: product truth vs personalization vs lessons."""
        smart = " ".join(self.smart.split())
        memory = " ".join(text(MEMORY).split())
        agent = " ".join(text(CLAUDE).split())
        for requirement in (
            "docs/USER.md",
            "docs/AGENT-MEMORY.md",
            "Learning memory frozen snapshot",
            "not product truth",
        ):
            with self.subTest(surface="smart", requirement=requirement):
                self.assertIn(requirement, smart)
        for requirement in (
            "docs/USER.md",
            "docs/AGENT-MEMORY.md",
            "Two brains",
            "product truth",
            "user prefs / communication style / workflow habits",
            "env facts / tool quirks / operational lessons",
            "Never write product requirements into USER/AGENT-MEMORY",
        ):
            with self.subTest(surface="project-memory", requirement=requirement):
                # project-memory may phrase routing slightly differently; accept
                # either explicit routing table language or the two-brain rule.
                blob = memory
                if requirement not in blob:
                    # fallbacks for common equivalent phrases
                    alts = {
                        "user prefs / communication style / workflow habits": (
                            "communication style",
                            "workflow habits",
                            "USER.md",
                        ),
                        "env facts / tool quirks / operational lessons": (
                            "operational lessons",
                            "tool quirks",
                            "AGENT-MEMORY",
                        ),
                        "Never write product requirements into USER/AGENT-MEMORY": (
                            "never write product",
                            "not product truth",
                            "product what/why",
                        ),
                    }
                    if requirement in alts:
                        self.assertTrue(
                            any(a.lower() in blob.lower() for a in alts[requirement]),
                            msg=f"missing routing signal for {requirement}",
                        )
                    else:
                        self.assertIn(requirement, blob)
        self.assertIn("Learning memory is not product truth", agent)
        self.assertIn("USER.md", agent)
        self.assertIn("AGENT-MEMORY.md", agent)
        # Optional SOUL is identity/tone only
        self.assertIn("SOUL", memory + smart + agent)


class DiscoveryPlanningContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.planner = text(PLANNER)

    def test_discovery_is_adaptive_not_fixed_questionnaire(self) -> None:
        self.assertIn("do **not** ask a fixed questionnaire", self.planner)
        self.assertIn("only 1–3 questions", self.planner)
        self.assertIn("decision impact and uncertainty", self.planner)

    def test_brief_covers_product_reality_and_final_experience(self) -> None:
        for dimension in (
            "Intent",
            "Problem",
            "People",
            "Final experience",
            "Value",
            "Scope",
            "Reality",
            "Viability",
            "Risk",
            "Success",
            "Future",
        ):
            with self.subTest(dimension=dimension):
                self.assertRegex(self.planner, rf"(?m)^\| {re.escape(dimension)} \|")

    def test_plan_is_forbidden_until_vision_lock(self) -> None:
        self.assertIn(
            "Do not create PLAN.md while status is NOT READY", self.planner
        )
        self.assertIn("explicitly confirm Vision Lock", self.planner)

    def test_landscape_research_and_budget_quality_are_gated(self) -> None:
        """SMART-shaped elevation: research + budget before code; not a multi-agent company."""
        planner = " ".join(self.planner.split())
        smart = " ".join(text(SMART).split())
        for requirement in (
            "Stage 1.5 — Landscape research",
            "decision-changing landscape pass",
            "Budget × quality bar",
            "docs/RESEARCH.md",
            "landscape coverage",
            "not a multi-agent company simulation",
        ):
            with self.subTest(surface="planner", requirement=requirement):
                self.assertIn(requirement, planner)
        for requirement in (
            "Landscape researcher",
            "Budget × quality tradeoff",
            "skips landscape/similar-product research",
            "Not a multi-agent company",
        ):
            with self.subTest(surface="smart", requirement=requirement):
                self.assertIn(requirement, smart)
        # Vision Lock must mention landscape / budget when relevant
        self.assertIn("landscape / similar-product evidence", smart)
        self.assertIn("budget × quality floor", smart)

    def test_atomic_tasks_include_evidence_and_reversal(self) -> None:
        for field in (
            "**Why now:**",
            "**Realizes:**",
            "**Depends on:**",
            "**Files:**",
            "**Accept:**",
            "**Verify:**",
            "**Evidence recorded in:**",
            "**Rollback / reversal:**",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.planner)

    def test_planner_grows_the_mind_network_and_gates_on_coverage(self) -> None:
        normalized = " ".join(self.planner.split())
        for requirement in (
            "docs/PROJECT-MIND.md",
            "Write every reliable answer into the mind network",
            "the Project Mind coverage sweep is COMPLETE",
            "is not an acceptable path past this gate under any schedule pressure",
            "Every task cites the mind node IDs it realizes",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)


class ContinuityAndExecutionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.memory = text(MEMORY)
        cls.pilot = text(PILOT)

    def test_memory_has_resume_assumptions_capabilities_ledger_and_runway(self) -> None:
        for section in (
            "## Resume packet",
            "### Active assumptions",
            "## Capability inventory",
            "## Meaningful change ledger",
            "## Runway",
        ):
            with self.subTest(section=section):
                self.assertIn(section, self.memory)

    def test_memory_is_not_transcript_or_secret_store(self) -> None:
        self.assertIn("transcript into STATE", self.memory)
        self.assertIn("Keep sensitive values and secrets out", self.memory)

    def test_memory_owns_an_atomic_addressable_mind_network(self) -> None:
        normalized = " ".join(self.memory.split())
        for requirement in (
            "Project Mind — the atomic mental network",
            "One node = one atomic, testable statement",
            "Every node is addressable",
            "Links are typed",
            "Completeness gate (feeds Vision Lock)",
            "no `UNKNOWN` or `CONFLICT` node remains on a critical path",
            "Planning or code with open critical gaps is forbidden",
            "the mind network is never bureaucracy",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)

    def test_mind_domains_cover_the_product_inch_by_inch(self) -> None:
        for domain in (
            "INT", "PPL", "EXP", "SCP", "BEH", "DAT",
            "IFC", "QLT", "RSK", "SUC", "EVO",
        ):
            with self.subTest(domain=domain):
                self.assertIn(f"M-{domain}-", self.memory)

    def test_execution_refuses_unconfirmed_or_unverifiable_work(self) -> None:
        self.assertIn("Vision Lock is not explicitly `CONFIRMED`", self.pilot)
        self.assertIn("task has no measurable acceptance", self.pilot)
        self.assertIn("fresh Verify is GREEN", self.pilot)

    def test_healthy_execution_advances_in_one_internal_pass(self) -> None:
        normalized = " ".join(self.pilot.split())
        for requirement in (
            "Healthy-task fast path",
            "one internal execution checklist",
            "write the memory delta in the same invocation",
            "Do not stop after restating the task",
            "Escalate back to SMART only when",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized)

    def test_repeated_failure_enters_recovery(self) -> None:
        self.assertIn("same symptom RED 3 times", self.pilot)
        self.assertIn("invoke `debug-detective`", self.pilot)
        self.assertIn("Do not count repeated commands", self.pilot)

    def test_execution_and_memory_require_machine_evidence(self) -> None:
        self.assertIn("smart-gates.py vision check", self.pilot)
        self.assertIn("smart-gates.py verify check", self.pilot)
        self.assertIn(".smart/evidence/vision-lock.json", self.memory)
        self.assertIn(".smart/evidence/release.json", self.memory)

    def test_security_contract_emits_structured_release_verdict(self) -> None:
        security = text(SECURITY)
        self.assertIn(".smart/evidence/security.json", security)
        self.assertIn('"critical_findings": 0', security)
        self.assertIn('"verdict": "PASS"', security)


class CatalogAndEntryContractTests(unittest.TestCase):
    """External capability catalog + canonical slash entry contracts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = text(ROOT / "SKILLS_CATALOG.md")
        cls.readme = text(ROOT / "README.md")
        cls.claude = text(ROOT / "CLAUDE.md")
        cls.smart = text(SMART)
        cls.installer = text(
            ROOT / "skills/smart/skills/smart/scripts/fetch-skill.sh"
        )
        cls.command = text(ROOT / "skills/smart/commands/smart.md")
        cls.marketplace = json.loads(
            text(ROOT / ".claude-plugin/marketplace.json")
        )
        cls.plugin = json.loads(
            text(ROOT / "skills/smart/.claude-plugin/plugin.json")
        )

    def test_scroll_world_alias_is_curated(self) -> None:
        alias = "scroll-world|oso95/scroll-world|main|skills/scroll-world"
        self.assertIn(alias, self.installer)
        self.assertIn("scroll-world", self.catalog)
        self.assertIn("oso95/scroll-world", self.catalog)
        self.assertIn("Higgsfield", self.catalog)
        # YELLOW situational + paid-gen caution must be explicit for SMART.
        self.assertRegex(self.catalog, r"scroll-world[\s\S]{0,400}YELLOW")
        self.assertIn("scroll-world", self.smart)
        self.assertIn("remotion-video", self.smart)
        self.assertIn("scroll-world", self.readme)
        self.assertIn("scroll-world", self.claude)

    def test_scroll_world_not_confused_with_remotion(self) -> None:
        self.assertIn("not `remotion-video`", self.catalog)
        self.assertIn("not `remotion-video`", self.smart)

    def test_canonical_slash_entry_is_namespaced(self) -> None:
        """Plugin skills are always /plugin:name — bare /smart is not claimed."""
        self.assertIn("/smart:smart", self.readme)
        self.assertIn("/smart:smart", self.catalog)
        self.assertIn("/smart:smart", self.command)
        self.assertIn("/smart:smart", self.smart)
        # Must not advertise bare /smart as a working entry point.
        self.assertNotRegex(
            self.readme,
            r"Start SMART with `/smart`(?!:)",
        )
        self.assertNotRegex(
            self.catalog,
            r"\| `/smart`, `/smart:smart`",
        )
        self.assertIn("bare `/smart`", self.readme)
        self.assertIn("bare `/smart`", self.command)

    def test_marketplace_smart_pin_is_current(self) -> None:
        self.assertEqual(self.marketplace["metadata"]["version"], "2.5.19")
        smart = next(p for p in self.marketplace["plugins"] if p["name"] == "smart")
        self.assertEqual(smart["version"], "2.5.19")
        self.assertEqual(self.plugin["version"], "2.5.19")
        pilot = json.loads(
            text(ROOT / "skills/step-pilot/.claude-plugin/plugin.json")
        )
        planner = json.loads(
            text(ROOT / "skills/project-planner/.claude-plugin/plugin.json")
        )
        self.assertEqual(pilot["version"], "1.3.0")
        self.assertEqual(planner["version"], "1.5.0")


if __name__ == "__main__":
    unittest.main()
