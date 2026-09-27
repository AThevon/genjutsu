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
                    "evals/swiftui-skip/prompt.md"):
            self.assertTrue((ROOT / rel).is_file(), rel)
        for rel in set(re.findall(r"`(scripts/[\w./-]+\.py)`", self.text)):
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_cost_warning_and_exclusion_rule(self):
        for needle in ("## Cost: read this first", "never in CI", "--max-cost-usd",
                       "A run that failed its positive guard is left out of its arm",
                       "page-has-content", "swift-screen-written", "skippedPaidGraders"):
            self.assertIn(needle, self.text)

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), self.text)


if __name__ == "__main__":
    unittest.main()
