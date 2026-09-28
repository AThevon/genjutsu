"""Tests for scripts/check-evals.py, on synthetic suites written to a temp dir."""

from __future__ import annotations

import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("check_evals", SCRIPTS / "check-evals.py")
check_evals = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_evals)

PROMPT = textwrap.dedent("""\
    ---
    max_turns: 150
    timeout_seconds: 2400
    allowed_tools: [Read, Glob, Grep, Skill]
    ---

    Use the /genjutsu:paint skill to build the landing page.
    """)
CASE_YAML = textwrap.dedent("""\
    schema_version: "1.1"
    name: demo
    context:
      scaffold_script: fixture.sh
    """)
FIXTURE = "#!/usr/bin/env bash\nset -euo pipefail\nmkdir -p app\n: > app/page.tsx\n"
GUARD = textwrap.dedent("""\
    ---
    type: regex
    target: { source: file, path: app/page.tsx }
    match: contains
    pattern: 'export\\s+default\\s+function[\\s\\S]*<(main|section)\\b'
    ---
    """)
NO_DASH = textwrap.dedent("""\
    ---
    type: regex
    target: { source: file, path: app/page.tsx }
    match: not_contains
    pattern: "\\u2014"
    ---
    """)


class SuiteTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.evals = Path(self._tmp.name) / "evals"
        self.case = self.evals / "demo"
        (self.case / "graders").mkdir(parents=True)
        self.write("prompt.md", PROMPT)
        self.write("case.yaml", CASE_YAML)
        self.write("fixture.sh", FIXTURE)
        self.write("graders/page-has-content.md", GUARD)
        self.write("graders/no-em-dash.md", NO_DASH)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel: str, text: str) -> None:
        (self.case / rel).write_text(text, encoding="utf-8")

    def errors(self, expected=()) -> list[str]:
        return check_evals.check_suite(self.evals, tuple(expected))

    def assertOneError(self, needle: str) -> None:
        errs = self.errors()
        self.assertTrue(any(needle in e for e in errs), f"no error mentions {needle!r}: {errs}")

    def test_valid_suite_has_no_error(self):
        self.assertEqual(self.errors(), [])

    def test_missing_fixture_is_reported(self):
        (self.case / "fixture.sh").unlink()
        self.assertOneError("missing fixture.sh")

    def test_unknown_grader_type_is_reported(self):
        self.write("graders/odd.md", "---\ntype: regexp\npattern: 'x'\n---\n")
        self.assertOneError("unknown grader type 'regexp'")

    def test_key_foreign_to_the_type_is_reported(self):
        self.write("graders/odd.md", "---\ntype: tool_used\ntool: Bash\npattern: 'x'\n---\n")
        self.assertOneError("not valid for a tool_used grader: pattern")

    def test_unknown_prompt_key_is_reported(self):
        self.write("prompt.md", PROMPT.replace("max_turns: 150", "max_turns: 150\nmax_turn: 3"))
        self.assertOneError("unknown frontmatter key(s): max_turn")

    def test_write_tool_in_a_case_is_reported(self):
        self.write("prompt.md", PROMPT.replace("Skill]", "Skill, Write]"))
        self.assertOneError("grant Write with --allow-tools")

    def test_invalid_escape_in_double_quotes_is_reported(self):
        self.write("graders/odd.md", '---\ntype: regex\npattern: "\\s+Elevate"\n---\n')
        self.assertOneError("invalid YAML escape \\s")

    def test_regex_that_does_not_compile_is_reported(self):
        self.write("graders/odd.md", "---\ntype: regex\npattern: '(unclosed'\n---\n")
        self.assertOneError("regex does not compile")

    def test_min_above_max_is_reported(self):
        self.write("graders/odd.md", "---\ntype: tool_used\ntool: Bash\nmin: 2\nmax: 0\n---\n")
        self.assertOneError("min 2 is greater than max 0")

    def test_llm_rubric_without_pass_fail_is_reported(self):
        self.write("graders/odd.md", "---\ntype: llm\n---\n\nIs the page nice?\n")
        self.assertOneError("concrete PASS and FAIL")

    def test_case_yaml_name_mismatch_is_reported(self):
        self.write("case.yaml", CASE_YAML.replace("name: demo", "name: other"))
        self.assertOneError("name must be 'demo'")

    def test_unquoted_schema_version_is_reported(self):
        self.write("case.yaml", CASE_YAML.replace('"1.1"', "1.1"))
        self.assertOneError('schema_version must be the string "1.1"')

    def test_fixture_that_does_not_parse_is_reported(self):
        self.write("fixture.sh", "#!/usr/bin/env bash\nif then\n")
        self.assertOneError("bash -n failed")

    def test_case_without_guard_is_reported(self):
        (self.case / "graders" / "page-has-content.md").unlink()
        self.assertOneError("needs exactly one positive guard grader")

    def test_prompt_that_does_not_invoke_paint_is_reported(self):
        self.write("prompt.md", PROMPT.replace("/genjutsu:paint", "genjutsu"))
        self.assertOneError("must invoke /genjutsu:paint explicitly")

    def test_guard_marked_with_only_is_reported(self):
        self.write("graders/page-has-content.md", GUARD.replace("match: contains", "match: contains\narm: with-only"))
        self.assertOneError("scored in both arms")

    def test_em_dash_anywhere_in_the_suite_is_reported(self):
        self.write("prompt.md", PROMPT + "\nA studio \u2014 in Lyon.\n")
        self.assertOneError("U+2014")

    def test_sentinel_phrase_in_the_suite_is_reported(self):
        self.write("graders/odd.md", "---\ntype: regex\ntarget: trace\npattern: '" + check_evals.SENTINEL + "'\n---\n")
        self.assertOneError("sentinel phrase")

    def test_results_directory_is_ignored(self):
        results = self.evals / "results" / "2026-09-26"
        results.mkdir(parents=True)
        (results / "notes.md").write_text("A \u2014 B", encoding="utf-8")
        self.assertEqual(self.errors(), [])

    def test_missing_expected_case_is_reported(self):
        errs = self.errors(expected=("demo", "swiftui-skip"))
        self.assertEqual(errs, [f"{self.evals}: expected case swiftui-skip is missing"])


class ParserTest(unittest.TestCase):
    def test_flow_map_and_single_quotes(self):
        fm, body = check_evals.split_frontmatter(
            "---\ntarget: { source: file, path: app/page.tsx }\npattern: 'it''s: [a-z]+'\n---\nbody\n"
        )
        self.assertEqual(fm["target"], {"source": "file", "path": "app/page.tsx"})
        self.assertEqual(fm["pattern"], "it's: [a-z]+")
        self.assertEqual(body.strip(), "body")

    def test_double_quoted_unicode_escape_becomes_the_character(self):
        self.assertEqual(check_evals.parse_scalar('"\\u2014"'), "\u2014")

    def test_block_map(self):
        data = check_evals.parse_mapping('schema_version: "1.1"\ncontext:\n  scaffold_script: fixture.sh\n')
        self.assertEqual(data, {"schema_version": "1.1", "context": {"scaffold_script": "fixture.sh"}})


if __name__ == "__main__":
    unittest.main()
