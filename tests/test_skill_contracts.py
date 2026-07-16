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


if __name__ == "__main__":
    unittest.main()
