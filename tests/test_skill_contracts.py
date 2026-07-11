#!/usr/bin/env python3
"""Contract tests for SMART's vision-first project intelligence system."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMART = ROOT / "skills/smart/skills/smart/SKILL.md"
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
            "**Depends on:**",
            "**Files:**",
            "**Accept:**",
            "**Verify:**",
            "**Evidence recorded in:**",
            "**Rollback / reversal:**",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.planner)


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

    def test_execution_refuses_unconfirmed_or_unverifiable_work(self) -> None:
        self.assertIn("Vision Lock is not explicitly `CONFIRMED`", self.pilot)
        self.assertIn("task has no measurable acceptance", self.pilot)
        self.assertIn("fresh Verify is GREEN", self.pilot)

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
