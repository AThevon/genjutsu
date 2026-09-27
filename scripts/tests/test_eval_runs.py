"""Tests for scripts/eval-runs.py, on synthetic result documents, traces and kept dirs."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("eval_runs", SCRIPTS / "eval-runs.py")
eval_runs = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = eval_runs  # dataclasses resolve annotations through sys.modules
_spec.loader.exec_module(eval_runs)
_spec = importlib.util.spec_from_file_location("check_evals", SCRIPTS / "check-evals.py")
check_evals = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_evals)


def run(score, graders=None, guard=True, guard_name="page-has-content", skipped=False, trace="", error=None):
    """One run in the documented camelCase shape. graders: {name: (passed, scored)}."""
    gs = [{"name": guard_name, "passed": guard, "weight": 1, "explanation": "", "withOnly": False, "scored": True}]
    for name, (passed, scored) in (graders or {}).items():
        gs.append({"name": name, "passed": passed, "weight": 1, "explanation": "",
                   "withOnly": not scored, "scored": scored})
    return {"score": score, "passed": score >= 1, "turns": 40, "costUsd": 2.0, "judgeCostUsd": 0.01,
            "error": error, "tracePath": trace, "skippedPaidGraders": skipped, "graders": gs}


def case(name, with_runs, without_runs=()):
    return {"name": name, "dir": name, "arms": {"with": list(with_runs), "without": list(without_runs)},
            "aggregates": {"score": 0.0}}


def doc(*cases, partial=False):
    return {"schemaVersion": 1, "partial": partial, "partialReason": "cost_ceiling" if partial else None,
            "cases": list(cases)}


TELLS_OK = {"tells-requested": (True, False), "tells-reported-loaded": (True, False)}


def passing_suite():
    return doc(
        case("studio-landing", [run(0.9, TELLS_OK), run(0.8, TELLS_OK)], [run(0.5), run(0.6)]),
        case("saas-landing", [run(0.9, TELLS_OK)], [run(0.7)]),
        case("thesis-allows",
             [run(0.8, {"keeps-both-cities": (True, True), "keeps-time-bar": (True, True)})],
             [run(0.8, {"keeps-both-cities": (True, True), "keeps-time-bar": (True, True)})]),
        case("swiftui-skip",
             [run(1.0, {"tells-never-requested": (True, True), "tells-never-read": (True, True)}, guard_name="swift-screen-written")],
             [run(1.0, {"tells-never-requested": (True, True), "tells-never-read": (True, True)}, guard_name="swift-screen-written")]),
    )


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        for dirpath, dirnames, _ in os.walk(self.tmp):
            for d in dirnames:
                os.chmod(Path(dirpath) / d, 0o700)
        os.chmod(self.tmp, 0o700)
        self._tmp.cleanup()

    def write_json(self, data, name="run.json") -> Path:
        p = self.tmp / name
        p.write_text(json.dumps(data), encoding="utf-8")
        return p

    def cli(self, *argv) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            code = eval_runs.main(["eval-runs.py", *map(str, argv)])
        return code, buf.getvalue()


class GuardsTest(unittest.TestCase):
    def test_guards_match_check_evals(self):
        # check-evals.py requires one of these per case; a name only one side knows
        # would leave every run of that case out of the delta.
        self.assertEqual(eval_runs.GUARDS, check_evals.GUARDS)


class DeltaTest(Base):
    def test_a_run_that_failed_its_guard_is_left_out_of_its_arm(self):
        # The empty page passes every not_contains grader: 1.0 would inflate the with-arm.
        c = eval_runs.load_doc(self.write_json(doc(case("studio-landing", [run(0.9), run(1.0, guard=False)], [run(0.5), run(0.6)]))))[1][0]
        s = eval_runs.arm_stats(c)
        self.assertAlmostEqual(s["with"]["mean"], 0.9)
        self.assertEqual((s["with"]["kept"], s["with"]["total"], s["with"]["guard_failed"]), (1, 2, 1))
        self.assertAlmostEqual(s["delta"], 0.35)

    def test_a_run_no_grader_scored_is_left_out(self):
        # A scaffold failure or a thrown setup error comes back with score 0 and no grader:
        # kept, it would pull the baseline down and fake a positive delta.
        bad = {"score": 0, "error": "scaffold failed (exit 1)", "tracePath": "", "skippedPaidGraders": False, "graders": []}
        c = eval_runs.load_doc(self.write_json(doc(case("studio-landing", [run(0.9)], [run(0.6), bad]))))[1][0]
        s = eval_runs.arm_stats(c)
        self.assertAlmostEqual(s["without"]["mean"], 0.6)
        self.assertEqual((s["without"]["kept"], s["without"]["total"], s["without"]["harness_failed"]), (1, 2, 1))

    def test_a_run_whose_guard_entry_is_absent_is_left_out(self):
        # Graders ran but the guard is not among them: nothing says the page exists,
        # so the run is not trusted (fail closed).
        no_guard = {"score": 1.0, "error": None, "tracePath": "", "skippedPaidGraders": False, "graders": [
            {"name": "no-em-dash", "passed": True, "weight": 1, "explanation": "", "withOnly": False, "scored": True}]}
        c = eval_runs.load_doc(self.write_json(doc(case("studio-landing", [run(0.9), no_guard], [run(0.5)]))))[1][0]
        s = eval_runs.arm_stats(c)
        self.assertAlmostEqual(s["with"]["mean"], 0.9)
        self.assertEqual((s["with"]["kept"], s["with"]["total"]), (1, 2))

    def test_a_run_whose_judges_were_skipped_is_left_out(self):
        c = eval_runs.load_doc(self.write_json(doc(case("studio-landing", [run(0.9), run(0.2, skipped=True)], [run(0.5)]))))[1][0]
        self.assertAlmostEqual(eval_runs.arm_stats(c)["with"]["mean"], 0.9)

    def test_snake_case_results_read_the_same(self):
        snake = {"schema_version": "1.0", "partial": False, "cases": [{
            "name": "studio-landing",
            "runs": [{"score": 0.9, "error": None, "trace_path": "", "graders": [{"name": "page-has-content", "passed": True}]},
                     {"score": 1.0, "error": None, "trace_path": "", "graders": [{"name": "page-has-content", "passed": False}]}],
            "runs_without": [{"score": 0.5, "error": None, "trace_path": "", "skipped_paid_graders": True, "graders": []},
                             {"score": 0.6, "error": None, "trace_path": "", "graders": [{"name": "page-has-content", "passed": True}]}],
        }]}
        c = eval_runs.load_doc(self.write_json(snake))[1][0]
        s = eval_runs.arm_stats(c)
        self.assertAlmostEqual(s["with"]["mean"], 0.9)
        self.assertAlmostEqual(s["without"]["mean"], 0.6)

    def test_unknown_shape_is_an_error(self):
        code, out = self.cli("delta", self.write_json({"cases": [{"name": "x", "results": []}]}))
        self.assertEqual(code, 2)
        self.assertIn("unknown result format", out)

    def test_indicators_count_only_unscored_graders_on_kept_runs(self):
        c = eval_runs.load_doc(self.write_json(doc(case("studio-landing", [
            run(0.9, {"tells-requested": (True, False), "no-em-dash": (True, True)}),
            run(0.8, {"tells-requested": (False, False), "no-em-dash": (True, True)}),
            run(1.0, {"tells-requested": (True, False)}, guard=False),
        ]))))[1][0]
        self.assertEqual(eval_runs.indicators(c), {"tells-requested": (1, 2)})

    def test_gate_passes_on_a_passing_suite(self):
        code, out = self.cli("delta", self.write_json(passing_suite()))
        self.assertEqual(code, 0, out)
        self.assertIn("RELEASE GATE: PASS", out)
        self.assertIn("tells-requested 2/2", out)

    def test_gate_fails_when_a_web_delta_is_zero(self):
        d = passing_suite()
        d["cases"][1] = case("saas-landing", [run(0.7)], [run(0.7)])
        code, out = self.cli("delta", self.write_json(d))
        self.assertEqual(code, 1)
        self.assertIn("FAIL saas-landing: delta +0.00", out)

    def test_gate_fails_when_studio_never_requested_tells(self):
        d = passing_suite()
        d["cases"][0]["arms"]["with"][1] = run(0.8, {"tells-requested": (False, False), "tells-reported-loaded": (True, False)})
        code, out = self.cli("delta", self.write_json(d))
        self.assertEqual(code, 1)
        self.assertIn("FAIL studio-landing: tells-requested 1/2", out)

    def test_gate_fails_when_the_bar_is_dropped_once(self):
        d = passing_suite()
        d["cases"][2]["arms"]["with"].append(run(0.9, {"keeps-both-cities": (True, True), "keeps-time-bar": (False, True)}))
        code, out = self.cli("delta", self.write_json(d))
        self.assertEqual(code, 1)
        self.assertIn("FAIL thesis-allows: keeps-time-bar 1/2", out)

    def test_gate_fails_when_swiftui_requests_tells(self):
        d = passing_suite()
        d["cases"][3]["arms"]["with"][0] = run(0.5, {"tells-never-requested": (False, True), "tells-never-read": (True, True)}, guard_name="swift-screen-written")
        code, out = self.cli("delta", self.write_json(d))
        self.assertEqual(code, 1)
        self.assertIn("FAIL swiftui-skip: tells-never-requested 0/1", out)

    def test_gate_fails_when_every_with_run_failed_its_guard(self):
        d = passing_suite()
        d["cases"][0] = case("studio-landing", [run(1.0, guard=False)], [run(0.5)])
        code, out = self.cli("delta", self.write_json(d))
        self.assertEqual(code, 1)
        self.assertIn("FAIL studio-landing: no delta", out)

    def test_partial_result_never_passes(self):
        d = passing_suite()
        d["partial"], d["partialReason"] = True, "cost_ceiling"
        code, out = self.cli("delta", self.write_json(d))
        self.assertEqual(code, 1)
        self.assertIn("partial result (cost_ceiling)", out)

    def test_no_gate_and_markdown(self):
        code, out = self.cli("delta", self.write_json(doc(case("studio-landing", [run(0.9)], [run(0.5)]))), "--no-gate", "--format", "markdown")
        self.assertEqual(code, 0)
        self.assertIn("| studio-landing | 0.90 | 0.50 | +0.40 | 1/1 | 1/1 | - |", out)
        self.assertNotIn("RELEASE GATE", out)


if __name__ == "__main__":
    unittest.main()
