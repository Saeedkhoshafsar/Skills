#!/usr/bin/env python3
"""Tests for SMART's offline behavioral-contract scenario suite."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills/smart/skills/smart/evals"
VALIDATOR = EVAL_DIR / "validate_behavioral_scenarios.py"
SUITE = EVAL_DIR / "scenarios.json"
LIVE_WORKFLOW_TEMPLATE = ROOT / "ci/github-workflow-behavioral-eval.yml"

spec = importlib.util.spec_from_file_location("smart_behavioral_contracts", VALIDATOR)
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class BehavioralContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.suite = validator.load_json(SUITE)

    def test_core_suite_is_valid_and_adversarial(self) -> None:
        validator.validate_suite(self.suite)
        scenarios = self.suite["scenarios"]
        self.assertGreaterEqual(len(scenarios), 8)
        categories = {scenario["category"] for scenario in scenarios}
        self.assertTrue(
            {
                "vision-lock",
                "continuity",
                "recovery",
                "capability-selection",
                "supply-chain",
                "release",
                "verification",
            }
            <= categories
        )
        self.assertGreaterEqual(
            sum(scenario.get("critical", False) for scenario in scenarios), 5
        )

    def test_every_scenario_has_a_must_pass_safety_rubric(self) -> None:
        for scenario in self.suite["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                self.assertTrue(
                    any(rubric.get("must_pass") for rubric in scenario["rubrics"])
                )

    def test_duplicate_scenario_ids_fail_closed(self) -> None:
        broken = json.loads(json.dumps(self.suite))
        broken["scenarios"].append(broken["scenarios"][0])
        with self.assertRaisesRegex(validator.ValidationError, "Duplicate scenario id"):
            validator.validate_suite(broken)

    def test_unknown_scenario_filter_fails_closed(self) -> None:
        with self.assertRaisesRegex(validator.ValidationError, "Unknown scenario"):
            validator.select_scenarios(self.suite, ["not-real"])

    def test_invalid_threshold_fails_closed(self) -> None:
        broken = json.loads(json.dumps(self.suite))
        broken["scenarios"][0]["pass_threshold"] = 1.1
        with self.assertRaisesRegex(validator.ValidationError, "between 0 and 1"):
            validator.validate_suite(broken)

    def test_invalid_boolean_contract_fields_fail_closed(self) -> None:
        broken = json.loads(json.dumps(self.suite))
        broken["scenarios"][0]["critical"] = "yes"
        with self.assertRaisesRegex(validator.ValidationError, "critical must be boolean"):
            validator.validate_suite(broken)

    def test_invalid_forbidden_pattern_fails_closed(self) -> None:
        broken = json.loads(json.dumps(self.suite))
        broken["scenarios"][0]["forbidden_patterns"] = ["("]
        with self.assertRaisesRegex(validator.ValidationError, "invalid forbidden pattern"):
            validator.validate_suite(broken)

    def test_validator_has_no_network_model_or_secret_interface(self) -> None:
        source = VALIDATOR.read_text(encoding="utf-8")
        for forbidden in (
            "urllib",
            "chat/completions",
            "--api-key",
            "--judge",
            "SMART_EVAL",
            "OPENAI_API_KEY",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_live_api_workflow_template_is_removed(self) -> None:
        self.assertFalse(LIVE_WORKFLOW_TEMPLATE.exists())


if __name__ == "__main__":
    unittest.main()
