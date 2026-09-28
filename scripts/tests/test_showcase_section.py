"""Tests for scripts/showcase-section.py.

The generator writes the measured block of the README and of the release
notes: tells counted by audit.py on the showcase pages, the eval delta, and the
before / after captures. What must hold: the counts are the tells group only,
a missing capture or page fails instead of publishing a broken image, and the
block replaces exactly the region between its markers and nothing else.
"""

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "showcase-section.py"

# Stands in for audit.py: reports the number written in <root>/count.txt as
# tells findings, plus one hygiene finding that must never be counted.
FAKE_AUDIT = textwrap.dedent('''\
    import json, sys
    from pathlib import Path
    args = sys.argv[1:]
    assert args[1:] == ["--json", "--group", "tells"], args
    n = int((Path(args[0]) / "count.txt").read_text())
    f = {"check": "x", "severity": "nice-to-have", "file": "app/page.tsx", "line": 1, "text": "t"}
    print(json.dumps({"results": [
        {"check": "tell-a", "group": "tells", "findings": [f] * n},
        {"check": "hover", "group": "hygiene", "findings": [f]},
    ]}))
''')


class ShowcaseSectionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "audit.py").write_text(FAKE_AUDIT)
        self.images = self.tmp / "assets" / "showcase"
        self.images.mkdir(parents=True)
        for arm in ("without", "with"):
            for vp in ("desktop", "mobile"):
                (self.images / f"studio-landing-{arm}-{vp}.png").write_bytes(b"png")
            page = self.tmp / "pages" / arm
            page.mkdir(parents=True)
            (page / "count.txt").write_text("14" if arm == "without" else "2")

    def run_gen(self, *extra, case=None):
        case = case or f"studio-landing|Independent design studio landing|{self.tmp}/pages/without|{self.tmp}/pages/with|+0.43"
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--audit", str(self.tmp / "audit.py"),
             "--local-images", str(self.images), "--images", "./assets/v4",
             "--evals-link", "./evals", "--case", case, *extra],
            capture_output=True, text=True,
        )

    def test_counts_only_the_tells_group(self):
        r = self.run_gen()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("| Independent design studio landing | 14 | 2 | +0.43 |", r.stdout)

    def test_block_is_wrapped_in_its_markers(self):
        out = self.run_gen().stdout.strip().splitlines()
        self.assertEqual(out[0], "<!-- genjutsu:showcase:start -->")
        self.assertEqual(out[-1], "<!-- genjutsu:showcase:end -->")

    def test_images_use_the_published_base(self):
        r = self.run_gen()
        self.assertIn('src="./assets/v4/studio-landing-without-desktop.png"', r.stdout)
        self.assertIn('src="./assets/v4/studio-landing-with-mobile.png"', r.stdout)

    def test_missing_capture_fails(self):
        (self.images / "studio-landing-with-mobile.png").unlink()
        r = self.run_gen()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("studio-landing-with-mobile.png", r.stderr)

    def test_missing_page_dir_fails(self):
        r = self.run_gen(case=f"studio-landing|Studio|{self.tmp}/nope|{self.tmp}/pages/with|+0.43")
        self.assertNotEqual(r.returncode, 0)

    def test_empty_page_dir_fails_instead_of_auditing_the_cwd(self):
        for case in (f"studio-landing|Studio||{self.tmp}/pages/with|+0.43",
                     f"studio-landing|Studio|{self.tmp}/pages/without||+0.43"):
            with self.subTest(case=case):
                r = self.run_gen(case=case)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("empty field", r.stderr)

    def test_empty_delta_fails(self):
        r = self.run_gen(case=f"studio-landing|Studio|{self.tmp}/pages/without|{self.tmp}/pages/with|")
        self.assertNotEqual(r.returncode, 0)

    def test_write_replaces_only_the_region(self):
        target = self.tmp / "README.md"
        target.write_text("before\n<!-- genjutsu:showcase:start -->\nold\n<!-- genjutsu:showcase:end -->\nafter\n")
        r = self.run_gen("--write", str(target))
        self.assertEqual(r.returncode, 0, r.stderr)
        text = target.read_text()
        self.assertTrue(text.startswith("before\n<!-- genjutsu:showcase:start -->\n"))
        self.assertTrue(text.endswith("<!-- genjutsu:showcase:end -->\nafter\n"))
        self.assertNotIn("\nold\n", text)
        self.assertIn("| 14 | 2 | +0.43 |", text)

    def test_write_refuses_a_file_without_exactly_one_region(self):
        target = self.tmp / "README.md"
        target.write_text("no markers here\n")
        r = self.run_gen("--write", str(target))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(target.read_text(), "no markers here\n")


if __name__ == "__main__":
    unittest.main()
