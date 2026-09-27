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


def trace_line(role, *blocks):
    return json.dumps({"type": role, "message": {"role": role, "content": list(blocks)}})


def tool_use(tid, name, **inp):
    return {"type": "tool_use", "id": tid, "name": name, "input": inp}


def tool_result(tid, text):
    return {"type": "tool_result", "tool_use_id": tid, "content": [{"type": "text", "text": text}]}


def text(t):
    return {"type": "text", "text": t}


class InspectTest(Base):
    def trace(self, *lines, name="trace.jsonl") -> str:
        p = self.tmp / name
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(p)

    def inspect(self, trace_path) -> tuple[int, str]:
        d = doc(case("swiftui-skip", [run(1.0, trace=trace_path, guard_name="swift-screen-written")]))
        return self.cli("inspect", self.write_json(d), "--case", "swiftui-*")

    CLEAN = (
        trace_line("assistant", tool_use("s1", "Skill", skill="genjutsu:paint")),
        # The skill's own source names the failure messages: never count those.
        trace_line("user", tool_result("s1", "echo \"genjutsu: sub-skill '$1' NOT LOADED\" >&2\nnpx skills add https://genjutsu.athevon.dev -g")),
        trace_line("assistant", tool_use("b1", "Bash", command="GENJUTSU_SKILL_DIR=...\nload_skill motion-principles\nload_skill swiftui-motion")),
        trace_line("user", tool_result("b1", "# Motion principles\n...")),
        trace_line("assistant", text("Done.\nModules loaded: motion-principles, swiftui-motion\nModules not loaded: none")),
    )

    def test_clean_run(self):
        code, out = self.inspect(self.trace(*self.CLEAN))
        self.assertEqual(code, 0, out)
        self.assertIn("requested: motion-principles, swiftui-motion", out)
        self.assertIn("final report: Modules loaded: motion-principles, swiftui-motion", out)
        self.assertIn("problems: none", out)

    def test_module_not_loaded_in_a_shell_result(self):
        code, out = self.inspect(self.trace(*self.CLEAN,
            trace_line("assistant", tool_use("b2", "Bash", command="load_skill design-audit")),
            trace_line("user", tool_result("b2", "genjutsu: sub-skill 'design-audit' NOT LOADED"))))
        self.assertEqual(code, 1)
        self.assertIn("NOT LOADED: design-audit", out)

    def test_resolution_failure(self):
        code, out = self.inspect(self.trace(
            trace_line("assistant", tool_use("b1", "Bash", command="load_skill motion-principles")),
            trace_line("user", tool_result("b1", "genjutsu: could not find the genjutsu modules (a _jutsu directory holding motion-principles).\n    any agent    npx skills add https://genjutsu.athevon.dev -g"))))
        self.assertEqual(code, 1)
        self.assertIn("module directory NOT resolved", out)

    def test_sandbox_denial(self):
        code, out = self.inspect(self.trace(*self.CLEAN,
            trace_line("assistant", tool_use("b3", "Bash", command="cat /Users/x/genjutsu/skills/_jutsu/gsap/SKILL.md")),
            trace_line("user", tool_result("b3", "cat: /Users/x/genjutsu/skills/_jutsu/gsap/SKILL.md: Operation not permitted"))))
        self.assertEqual(code, 1)
        self.assertIn("1 read(s) denied by the sandbox", out)

    def test_unrecognised_trace(self):
        code, out = self.inspect(self.trace(json.dumps({"event": "start"})))
        self.assertEqual(code, 2)
        self.assertIn("no tool call recognised", out)

    def test_missing_trace(self):
        code, out = self.inspect(str(self.tmp / "nope" / "trace.jsonl"))
        self.assertEqual(code, 2)
        self.assertIn("trace not found", out)


class CollectTest(Base):
    def kept_run(self, name, page, sealed=True) -> str:
        root = self.tmp / name
        (root / "config").mkdir(parents=True)
        (root / "out").mkdir()
        (root / "out" / "trace.jsonl").write_text("{}\n", encoding="utf-8")
        home = root / ("sealed-x1" if sealed else "") / "home"
        (home / "cwd" / "app").mkdir(parents=True)
        (home / "cwd" / "app" / "page.tsx").write_text(page, encoding="utf-8")
        (home / "cwd" / "node_modules" / "next").mkdir(parents=True)
        if sealed:
            os.chmod(root / "sealed-x1", 0)
            os.chmod(root, 0o500)
        return str(root / "out" / "trace.jsonl")

    def test_first_guarded_run_of_each_arm_is_copied_from_sealed_dirs(self):
        d = doc(case("studio-landing",
                     [run(1.0, guard=False, trace=self.kept_run("w0", "")), run(0.9, trace=self.kept_run("w1", "WITH"))],
                     [run(0.5, trace=self.kept_run("o0", "WITHOUT", sealed=False))]))
        out = self.tmp / "pages"
        code, log = self.cli("collect", self.write_json(d), "--case", "studio-landing", "--out", out)
        self.assertEqual(code, 0, log)
        self.assertEqual((out / "studio-landing" / "with" / "app" / "page.tsx").read_text(), "WITH")
        self.assertEqual((out / "studio-landing" / "without" / "app" / "page.tsx").read_text(), "WITHOUT")
        self.assertFalse((out / "studio-landing" / "with" / "node_modules").exists())
        self.assertIn("run 2 (earlier runs failed the guard)", log)
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertEqual([(m["arm"], m["runIndex"]) for m in manifest], [("with", 1), ("without", 0)])

    def test_pick_overrides_the_choice(self):
        d = doc(case("studio-landing", [run(0.9, trace=self.kept_run("w0", "A")), run(0.9, trace=self.kept_run("w1", "B"))]))
        out = self.tmp / "pages"
        code, log = self.cli("collect", self.write_json(d), "--case", "studio-landing", "--out", out, "--pick", "studio-landing:with:1")
        self.assertEqual(code, 0, log)
        self.assertEqual((out / "studio-landing" / "with" / "app" / "page.tsx").read_text(), "B")

    def test_cleaned_tmp_is_reported(self):
        d = doc(case("studio-landing", [run(0.9, trace=str(self.tmp / "gone" / "out" / "trace.jsonl"))]))
        code, log = self.cli("collect", self.write_json(d), "--case", "studio-landing", "--out", self.tmp / "pages")
        self.assertEqual(code, 2)
        self.assertIn("is gone", log)


class TellsTest(Base):
    def test_tells_are_counted_per_arm_on_the_page_only(self):
        pages = self.tmp / "pages" / "studio-landing"
        for arm, body in (("without", "<h1>Elevate your brand \u2014 seamless design</h1>"), ("with", "<h1>Identity for producers</h1>")):
            (pages / arm / "app").mkdir(parents=True)
            (pages / arm / "app" / "page.tsx").write_text(
                f"export default function Page() {{ return <main>{body}</main>; }}\n", encoding="utf-8")
        # A stylesheet next to the page is not the page: it must not be counted.
        (pages / "with" / "app" / "globals.css").write_text(".t { background-clip: text; }\n", encoding="utf-8")
        code, out = self.cli("tells", self.tmp / "pages", "--format", "markdown")
        self.assertEqual(code, 0, out)
        rows = {line.split("|")[2].strip(): line for line in out.splitlines() if line.startswith("| studio-landing")}
        self.assertIn("| 0 | - |", rows["with"])
        without_count = int(rows["without"].split("|")[3])
        self.assertGreaterEqual(without_count, 2)
        self.assertIn("tell-em-dash", rows["without"])
        self.assertIn("tell-filler-verb", rows["without"])


if __name__ == "__main__":
    unittest.main()
