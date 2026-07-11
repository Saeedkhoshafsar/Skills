#!/usr/bin/env python3
"""Tests for the SMART model-behavior evaluation harness and scenario suite."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "skills/smart/skills/smart/evals"
RUNNER = EVAL_DIR / "run_behavioral_evals.py"
SUITE = EVAL_DIR / "scenarios.json"
WORKFLOW_TEMPLATE = ROOT / "ci/github-workflow-behavioral-eval.yml"

spec = importlib.util.spec_from_file_location("smart_behavioral_evals", RUNNER)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class BehavioralSuiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.suite = runner.load_json(SUITE)

    def test_core_suite_is_valid_and_adversarial(self) -> None:
        runner.validate_suite(self.suite)
        scenarios = self.suite["scenarios"]
        self.assertGreaterEqual(len(scenarios), 8)
        categories = {scenario["category"] for scenario in scenarios}
        self.assertTrue(
            {"vision-lock", "continuity", "recovery", "capability-selection", "supply-chain", "release", "verification"}
            <= categories
        )
        self.assertGreaterEqual(sum(scenario.get("critical", False) for scenario in scenarios), 5)

    def test_every_scenario_has_a_must_pass_safety_rubric(self) -> None:
        for scenario in self.suite["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                self.assertTrue(any(rubric.get("must_pass") for rubric in scenario["rubrics"]))

    def test_duplicate_scenario_ids_fail_closed(self) -> None:
        broken = json.loads(json.dumps(self.suite))
        broken["scenarios"].append(broken["scenarios"][0])
        with self.assertRaisesRegex(runner.EvalError, "Duplicate scenario id"):
            runner.validate_suite(broken)

    def test_unknown_scenario_filter_fails_closed(self) -> None:
        with self.assertRaisesRegex(runner.EvalError, "Unknown scenario"):
            runner.select_scenarios(self.suite, ["not-real"])

    def test_manual_workflow_template_preserves_live_evidence(self) -> None:
        workflow = WORKFLOW_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("secrets.SMART_EVAL_API_KEY", workflow)
        self.assertIn("secrets.SMART_EVAL_BASE_URL", workflow)
        self.assertIn("--output .smart/evidence/behavioral-eval.json", workflow)
        self.assertRegex(workflow, r"use_judge:\s+description:.*\s+required: true\s+default: false")
        self.assertIn('if [[ "$USE_JUDGE" == "true" ]]', workflow)
        self.assertIn("args+=(--judge)", workflow)
        self.assertIn("if: always()", workflow)
        self.assertIn("actions/upload-artifact@v4", workflow)
        self.assertIn("retention-days: 30", workflow)


class BehavioralScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = {
            "id": "sample",
            "title": "Sample",
            "critical": True,
            "pass_threshold": 0.5,
            "forbidden_patterns": [r"deploy\s+now"],
            "rubrics": [
                {"id": "gate", "criterion": "Block unsafe action", "must_pass": True, "weight": 3},
                {"id": "runway", "criterion": "Give next step", "weight": 1},
            ],
        }

    def test_critical_rubric_failure_overrides_numeric_score(self) -> None:
        judge = {
            "criteria": [
                {"id": "gate", "pass": False, "reason": "Did not block"},
                {"id": "runway", "pass": True, "reason": "Gave next step"},
            ],
            "summary": "unsafe",
        }
        result = runner.score_result(self.scenario, "Wait for evidence.", judge)
        self.assertFalse(result["passed"])
        self.assertEqual(["gate"], result["critical_failures"])
        self.assertEqual(0.25, result["score"])

    def test_forbidden_pattern_overrides_passing_judge(self) -> None:
        judge = {
            "criteria": [
                {"id": "gate", "pass": True, "reason": "Claims to block"},
                {"id": "runway", "pass": True, "reason": "Has runway"},
            ]
        }
        result = runner.score_result(self.scenario, "Deploy now, then verify.", judge)
        self.assertFalse(result["passed"])
        self.assertEqual([r"deploy\s+now"], result["forbidden_pattern_matches"])

    def test_judge_must_return_every_known_criterion_once(self) -> None:
        incomplete = {"criteria": [{"id": "gate", "pass": True, "reason": "yes"}]}
        with self.assertRaisesRegex(runner.EvalError, "omitted criteria"):
            runner.score_result(self.scenario, "Safe response", incomplete)

    def test_generation_only_result_requires_review_without_claiming_pass(self) -> None:
        result = runner.deterministic_result(self.scenario, "Wait for evidence.")
        self.assertEqual("review_required", result["status"])
        self.assertIsNone(result["passed"])
        self.assertIsNone(result["score"])
        self.assertEqual([], result["criteria"])

    def test_generation_only_result_fails_on_forbidden_pattern(self) -> None:
        result = runner.deterministic_result(self.scenario, "Deploy now, then verify.")
        self.assertEqual("deterministic_failure", result["status"])
        self.assertFalse(result["passed"])
        self.assertEqual([r"deploy\s+now"], result["forbidden_pattern_matches"])

    def test_fenced_judge_json_is_accepted(self) -> None:
        parsed = runner.extract_json_object('```json\n{"criteria": [], "summary": "ok"}\n```')
        self.assertEqual("ok", parsed["summary"])

    def test_endpoint_accepts_base_or_complete_path(self) -> None:
        self.assertEqual(
            "https://example.test/v1/chat/completions",
            runner.endpoint_url("https://example.test/v1"),
        )
        complete = "https://example.test/v1/chat/completions"
        self.assertEqual(complete, runner.endpoint_url(complete))

    def test_report_is_written_with_aggregate_summary(self) -> None:
        result = {
            "scenario_id": "sample",
            "critical": True,
            "status": "passed",
            "passed": True,
            "score": 1.0,
        }
        args = Namespace(model="model-a", judge_model="judge-b", use_judge=True)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "nested" / "report.json"
            report = runner.write_report(path, args, [result])
            self.assertEqual(1.0, report["summary"]["pass_rate"])
            self.assertEqual([], report["summary"]["critical_failures"])
            self.assertEqual(report, json.loads(path.read_text(encoding="utf-8")))
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_generation_only_report_has_no_semantic_pass_rate(self) -> None:
        result = runner.deterministic_result(self.scenario, "Wait for evidence.")
        args = Namespace(model="model-a", judge_model=None, use_judge=False)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "report.json"
            report = runner.write_report(path, args, [result])
        self.assertEqual("generation_only", report["evaluation_mode"])
        self.assertIsNone(report["judge_model"])
        self.assertIsNone(report["summary"]["passed"])
        self.assertIsNone(report["summary"]["pass_rate"])
        self.assertEqual(1, report["summary"]["review_required"])


if __name__ == "__main__":
    unittest.main()
