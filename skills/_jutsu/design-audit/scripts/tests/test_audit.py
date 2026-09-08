#!/usr/bin/env python3
"""Tests for audit.py.

The point of this suite is not coverage, it is one specific failure. The greps
this script replaces had been returning "no findings" for months on projects
they never opened, and the pipeline read that as a pass. So the load-bearing
assertion here is that **every check can fire**: for each one there is a fixture
that must produce a finding, and a fixture that must not. A check that has gone
silently inert fails this suite rather than reporting a clean audit.

Run: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import audit  # noqa: E402


def build(files: dict[str, str]) -> Path:
    d = Path(tempfile.mkdtemp(prefix="genjutsu-audit-"))
    for rel, body in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return d


def audit_it(root: Path, only: str | None = None) -> dict[str, audit.Result]:
    roots, _ = audit.discover_roots(root)
    files = audit.walk(roots, root)
    checks = [c for c in audit.CHECKS if only is None or c.id == only]
    return {r.check: r for r in (audit.run_check(c, files, root) for c in checks)}


# id -> (fixture that MUST produce a finding, fixture that MUST NOT)
CASES = {
    "conditional-render-no-exit": (
        {"src/A.tsx": "export const A = () => <div>{show && <span/>}</div>\n"},
        {"src/A.tsx": "export const A = () => <AnimatePresence>{show && <span/>}</AnimatePresence>\n"},
    ),
    "hover-no-transition": (
        {"src/a.css": ".btn:hover { color: red; }\n"},
        {"src/a.css": ".btn:hover { color: red; transition: color 150ms; }\n"},
    ),
    "animated-layout-property": (
        {"src/a.css": ".p { transition: width 300ms ease-out; }\n"},
        {"src/a.css": ".p { transition: transform 300ms ease-out; }\n"},
    ),
    "outline-none": (
        {"src/a.css": ".f:focus { outline: none; }\n"},
        {"src/a.css": ".f:focus-visible { outline: none; box-shadow: 0 0 0 2px blue; }\n"},
    ),
    "clickable-non-button": (
        {"src/A.tsx": "<div onClick={go}>go</div>\n"},
        {"src/A.tsx": '<div role="button" tabIndex={0} onClick={go}>go</div>\n'},
    ),
    "decorative-motion-not-hidden": (
        {"src/A.tsx": "<motion.div animate={{x:1}} />\n"},
        {"src/A.tsx": '<motion.div aria-hidden="true" animate={{x:1}} />\n'},
    ),
    "will-change-broad": (
        {"src/a.css": ".l { will-change: transform; }\n"},
        {"src/a.css": ".l { will-change: auto; }\n"},
    ),
    "js-driven-animation": (
        {"src/a.ts": "setInterval(() => el.style.left = x + 'px', 16)\n"},
        {"src/a.ts": "const d = debounce(() => setTimeout(save, 500), 200)\n"},
    ),
    "inline-style-object": (
        {"src/A.tsx": "<div style={{color:'red'}} />\n"},
        {"src/A.tsx": "<div style={{transform:'translateX(4px)'}} />\n"},
    ),
    "no-reduced-motion": (
        {"src/a.css": ".x { transition: opacity 200ms; }\n"},
        {"src/a.css": "@media (prefers-reduced-motion: reduce) { * { transition: none; } }\n"},
    ),
}


class EveryCheckCanFire(unittest.TestCase):
    """The regression that motivated this file. Do not weaken these."""

    def test_every_check_has_a_case(self):
        self.assertEqual(
            {c.id for c in audit.CHECKS}, set(CASES),
            "a check was added or renamed without a fixture proving it can fire",
        )

    def test_positive_fixtures_produce_findings(self):
        for cid, (bad, _) in CASES.items():
            with self.subTest(check=cid):
                root = build(bad)
                try:
                    res = audit_it(root, only=cid)[cid]
                    self.assertEqual(res.status, "findings",
                                     f"{cid} found nothing in a fixture built to violate it")
                    self.assertTrue(res.findings)
                finally:
                    shutil.rmtree(root)

    def test_negative_fixtures_stay_quiet(self):
        for cid, (_, good) in CASES.items():
            with self.subTest(check=cid):
                root = build(good)
                try:
                    res = audit_it(root, only=cid)[cid]
                    self.assertEqual(
                        res.status, "clean",
                        f"{cid} fired on a compliant fixture: {[f.text for f in res.findings]}",
                    )
                finally:
                    shutil.rmtree(root)


class NotApplicableIsNotAPass(unittest.TestCase):
    """The bug in one sentence: zero matches used to read as a clean audit."""

    def test_no_web_files_reports_not_applicable(self):
        root = build({"README.md": "# nothing to audit\n", "main.kt": "fun main() {}\n"})
        try:
            results = audit_it(root)
            for cid, r in results.items():
                with self.subTest(check=cid):
                    self.assertEqual(r.status, "not-applicable",
                                     f"{cid} claimed a verdict on a project with no web source")
                    self.assertIn("did not run", r.meaning)
        finally:
            shutil.rmtree(root)

    def test_clean_and_not_applicable_are_distinguishable(self):
        root = build({"src/a.css": ".btn:hover { color: red; transition: color 150ms; }\n"})
        try:
            results = audit_it(root)
            self.assertEqual(results["hover-no-transition"].status, "clean")
            # No JSX anywhere, so the JSX-only check cannot have an opinion.
            self.assertEqual(results["inline-style-object"].status, "not-applicable")
        finally:
            shutil.rmtree(root)


class RootDiscovery(unittest.TestCase):
    def test_finds_app_router_layout(self):
        root = build({"app/page.tsx": "export default () => <div/>\n"})
        try:
            roots, note = audit.discover_roots(root)
            self.assertEqual([p.name for p in roots], ["app"])
            self.assertIn("detected", note)
        finally:
            shutil.rmtree(root)

    def test_finds_several_roots(self):
        root = build({"pages/a.tsx": "x\n", "components/B.tsx": "y\n"})
        try:
            roots, _ = audit.discover_roots(root)
            self.assertEqual(sorted(p.name for p in roots), ["components", "pages"])
        finally:
            shutil.rmtree(root)

    def test_falls_back_to_whole_tree(self):
        root = build({"weird/place/A.tsx": "<div onClick={go}/>\n"})
        try:
            roots, note = audit.discover_roots(root)
            self.assertEqual(roots, [root])
            self.assertIn("whole tree", note)
            self.assertEqual(audit_it(root, only="clickable-non-button")["clickable-non-button"].status,
                             "findings", "the fallback root must still scan")
        finally:
            shutil.rmtree(root)

    def test_skips_build_output_and_dependencies(self):
        root = build({
            "src/A.tsx": "export default () => <div/>\n",
            "node_modules/x/B.tsx": "<div onClick={go}/>\n",
            "src/.next/C.tsx": "<div onClick={go}/>\n",
            "src/dist/D.tsx": "<div onClick={go}/>\n",
        })
        try:
            res = audit_it(root, only="clickable-non-button")["clickable-non-button"]
            self.assertEqual(res.status, "clean",
                             f"scanned something it should have skipped: {[f.file for f in res.findings]}")
        finally:
            shutil.rmtree(root)


class DurationInventory(unittest.TestCase):
    def test_catches_shorthand_not_just_the_duration_key(self):
        root = build({"src/a.css": ".a { transition: width 300ms ease-out; }\n"
                                   ".b { animation: fade 250ms linear; }\n"
                                   ".c { transition-duration: 0.15s; }\n"})
        try:
            inv = audit.run_inventory(audit.walk(audit.discover_roots(root)[0], root), root)
            values = dict(inv["durations"]["values"])
            self.assertEqual(set(values), {"300ms", "250ms", "150ms"})
        finally:
            shutil.rmtree(root)

    def test_ignores_times_outside_an_animation_context(self):
        root = build({"src/a.ts": "const maxAge = '3600s'\nconst retry = 5000\n"})
        try:
            inv = audit.run_inventory(audit.walk(audit.discover_roots(root)[0], root), root)
            self.assertEqual(inv["durations"]["distinct"], 0)
        finally:
            shutil.rmtree(root)


class OutputShape(unittest.TestCase):
    def test_markdown_states_both_counts(self):
        root = build({"src/a.css": ".btn:hover { color: red; }\n"})
        try:
            roots, how = audit.discover_roots(root)
            files = audit.walk(roots, root)
            results = [audit.run_check(c, files, root) for c in audit.CHECKS]
            md = audit.as_markdown(root, how, files, results, audit.run_inventory(files, root))
            self.assertIn("checked", md)
            self.assertIn("not applicable", md)
            self.assertIn("never as passed", md)
        finally:
            shutil.rmtree(root)

    def test_severities_are_known_values(self):
        for c in audit.CHECKS:
            with self.subTest(check=c.id):
                self.assertIn(c.severity, audit.SEVERITY_ORDER)


if __name__ == "__main__":
    unittest.main()
