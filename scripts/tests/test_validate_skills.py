"""Tests for scripts/validate-skills.py, run on fixture trees through --root.

Run from scripts/: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "validate-skills.py"
REPO = SCRIPT.parent.parent

MODULE_FRONT = '---\nname: {name}\ndescription: "Internal genjutsu module used by the tests of validate-skills."\nmetadata:\n  internal: true\n---\n'
ORCH_FRONT = '---\nname: {name}\ndescription: "An orchestrator used by the tests of validate-skills, long enough."\n---\n'


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
    )


class ValidateSkillsTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.write("skills/cast/SKILL.md", ORCH_FRONT.format(name="cast") + "Body.\n")
        self.write("skills/paint/SKILL.md", ORCH_FRONT.format(name="paint") + "Body.\n")
        self.write("skills/_jutsu/gsap/SKILL.md", MODULE_FRONT.format(name="gsap") + "Body.\n")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def assert_fails(self, needle: str) -> None:
        result = run(self.root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(needle, result.stderr)

    def test_valid_tree_passes(self) -> None:
        result = run(self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_module_without_metadata_fails(self) -> None:
        self.write("skills/_jutsu/gsap/SKILL.md", ORCH_FRONT.format(name="gsap") + "Body.\n")
        self.assert_fails("internal: true")

    def test_module_with_quoted_true_fails(self) -> None:
        text = MODULE_FRONT.format(name="gsap").replace("internal: true", 'internal: "true"')
        self.write("skills/_jutsu/gsap/SKILL.md", text + "Body.\n")
        self.assert_fails("internal: true")

    def test_module_with_flow_style_metadata_fails(self) -> None:
        text = MODULE_FRONT.format(name="gsap").replace("metadata:\n  internal: true", "metadata: {internal: true}")
        self.write("skills/_jutsu/gsap/SKILL.md", text + "Body.\n")
        self.assert_fails("internal: true")

    def test_nested_key_does_not_leak_to_the_next_top_level_key(self) -> None:
        text = (
            "---\nname: gsap\nmetadata:\n  owner: web\n"
            'description: "Internal genjutsu module used by the tests of validate-skills."\n'
            "internal: true\n---\n"
        )
        self.write("skills/_jutsu/gsap/SKILL.md", text + "Body.\n")
        self.assert_fails("internal: true")

    def test_orchestrator_with_internal_fails(self) -> None:
        text = ORCH_FRONT.format(name="cast").replace("\n---\n", "\nmetadata:\n  internal: true\n---\n", 1)
        self.write("skills/cast/SKILL.md", text + "Body.\n")
        self.assert_fails("orchestrator must not carry metadata.internal")

    def test_module_over_the_cap_fails(self) -> None:
        self.write("skills/_jutsu/gsap/SKILL.md", MODULE_FRONT.format(name="gsap") + "x" * 25_001 + "\n")
        self.assert_fails("25000")

    def test_module_at_the_cap_passes(self) -> None:
        front = MODULE_FRONT.format(name="gsap")
        self.write("skills/_jutsu/gsap/SKILL.md", front + "x" * (25_000 - len(front) - 1) + "\n")
        result = run(self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_reference_printed_by_load_ref_over_the_cap_fails(self) -> None:
        self.write("skills/_jutsu/gsap/references/big.md", "x" * 25_001)
        self.write(
            "skills/cast/SKILL.md",
            ORCH_FRONT.format(name="cast") + "```bash\nload_skill gsap\nload_ref gsap references/big.md\n```\n",
        )
        self.assert_fails("load_ref prints it in one call")

    def test_reference_read_otherwise_over_the_cap_only_warns(self) -> None:
        self.write("skills/_jutsu/gsap/references/big.md", "x" * 25_001)
        result = run(self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("WARN skills/_jutsu/gsap/references/big.md", result.stdout)

    def test_load_ref_naming_a_missing_file_fails(self) -> None:
        self.write(
            "skills/paint/SKILL.md",
            ORCH_FRONT.format(name="paint") + "```bash\nload_ref gsap references/gone.md\n```\n",
        )
        self.assert_fails("named by load_ref in an orchestrator, but missing")

    def test_this_repository_passes(self) -> None:
        result = run(REPO)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
