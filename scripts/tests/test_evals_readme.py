"""Keep evals/README.md runnable: its commands use real flags, real subcommands and real paths."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
README = ROOT / "evals" / "README.md"

# `claude plugin eval --help`, Claude Code 2.1.283.
EVAL_FLAGS = {
    "--ablation", "--allow-real-servers", "--allow-tools", "--case", "--concurrency", "-j", "--eval-dir",
    "--json", "--judge-model", "--keep-temp", "--max-cost-usd", "--mocks", "--model", "--no-publish",
    "--no-scaffold", "--output-dir", "--publish-report", "--report", "--runs", "--scaffold", "--tag",
    "--threshold", "--trust-plugin", "--verbose",
}
EVAL_RUNS_COMMANDS = {"delta", "inspect", "collect", "tells"}

FULL_SUITE = (
    "claude plugin eval . --ablation with-without --runs 3 --scaffold --allow-tools Bash Write Edit "
    "--keep-temp --max-cost-usd <budget> --threshold 0 --no-publish --json evals/results/run.json"
)
SMOKE = "claude plugin eval . --case swiftui-skip --runs 1 --ablation none --scaffold --allow-tools Bash Write Edit --keep-temp"


def case_names() -> list[str]:
    # The case directories check-evals.py validates: results/ and dot or underscore names are not cases.
    return sorted(p.name for p in (ROOT / "evals").iterdir()
                  if p.is_dir() and p.name != "results" and not p.name.startswith((".", "_")))


class ReadmeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = README.read_text(encoding="utf-8")

    def test_spec_commands_are_there_verbatim(self):
        self.assertIn(FULL_SUITE, self.text)
        self.assertIn(SMOKE, self.text)
        self.assertIn("rsync -a --delete --exclude evals/results", self.text)
        self.assertIn("/private/tmp/genjutsu-eval/", self.text)

    def test_every_eval_flag_exists(self):
        for line in self.text.splitlines():
            if "claude plugin eval " not in line:
                continue
            for flag in re.findall(r"(?<![\w-])(--?[a-z][\w-]*)", line.split("claude plugin eval ", 1)[1]):
                self.assertIn(flag, EVAL_FLAGS, f"unknown flag {flag} in: {line.strip()}")

    def test_every_eval_run_stays_local(self):
        # Without --no-publish the runner publishes its report to claude.ai by default.
        lines = [l for l in self.text.splitlines() if "claude plugin eval " in l]
        self.assertTrue(lines)
        for line in lines:
            self.assertIn("--no-publish", line, f"publishes its report: {line.strip()}")

    def test_every_eval_runs_subcommand_exists(self):
        used = set(re.findall(r"scripts/eval-runs\.py (\w+)", self.text))
        self.assertTrue(used)
        self.assertLessEqual(used, EVAL_RUNS_COMMANDS)

    def test_named_files_exist(self):
        for rel in ("scripts/check-evals.py", "scripts/eval-runs.py", "evals/studio-landing/prompt.md",
                    "evals/swiftui-skip/prompt.md", "evals/bunshin-steps-down/prompt.md",
                    "skills/paint/SKILL.md", "skills/bunshin/SKILL.md"):
            self.assertTrue((ROOT / rel).is_file(), rel)
        for rel in set(re.findall(r"`(scripts/[\w./-]+\.py)`", self.text)):
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_cost_warning_and_exclusion_rule(self):
        for needle in ("## Cost: read this first", "never in CI", "--max-cost-usd",
                       "A run that failed its positive guard is left out of its arm",
                       "page-has-content", "swift-screen-written", "button-has-interaction",
                       "skippedPaidGraders"):
            self.assertIn(needle, self.text)

    def test_every_case_is_in_the_table(self):
        rows = set(re.findall(r"^\| `([\w-]+)` \|", self.text, re.M))
        self.assertEqual(rows, set(case_names()))

    def test_suite_size_matches_the_cases(self):
        # The cost warning is only as good as its arithmetic: a case added without it
        # makes the ceiling it tells you to set too low.
        m = re.search(r"(\d+) cases x (\d+) runs x 2 arms = (\d+) agent runs", self.text)
        self.assertIsNotNone(m)
        cases, runs, total = map(int, m.groups())
        self.assertEqual(cases, len(case_names()))
        self.assertIn(f"--runs {runs} ", FULL_SUITE)
        self.assertEqual(total, cases * runs * 2)
        per_arm = cases * runs
        self.assertIn(f"about {per_arm} times the cost of one with-arm web run, plus {per_arm} without-arm runs",
                      " ".join(self.text.split()))

    def test_bunshin_is_never_run_end_to_end(self):
        flat = " ".join(self.text.split())
        self.assertIn("bunshin itself is never run end to end by this suite", flat)
        self.assertIn("one measured run: a seven-page site in two languages", flat)
        for line in self.text.splitlines():
            if "claude plugin eval " in line and "--case bunshin" in line:
                self.assertIn("--max-cost-usd", line, f"a bunshin case without a cost ceiling: {line.strip()}")

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), self.text)


if __name__ == "__main__":
    unittest.main()
