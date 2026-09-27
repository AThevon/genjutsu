"""Pin the free graders of the real eval suite against known pages and tool inputs.

A grader that can no longer fire is the eval twin of the inert greps design-audit
replaced: every not_contains grader would pass on every page, and the delta would
read as zero for a reason that has nothing to do with the plugin. Python's `re`
stands in for the runner's JavaScript engine (see check-evals.py).
"""

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
EVALS = SCRIPTS.parent / "evals"
_spec = importlib.util.spec_from_file_location("check_evals", SCRIPTS / "check-evals.py")
check_evals = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_evals)

WEB_CASES = ["studio-landing", "saas-landing", "thesis-allows"]

# One line of page source per not_contains grader, each one the tell it exists to catch.
TELL_LINES = {
    "no-numbered-eyebrow": '<p className="text-xs tracking-widest">00 / INDEX</p>',
    "no-locale-strip": '<span>LIS 14:23 \u00b7 18\u00b0C</span>',
    "no-build-status": '<code>v0.6.2-rc.1 \u00b7 last sync 4s ago</code>',
    "no-estd": '<small>ESTD. 2018</small>',
    "no-scroll-cue": '<span className="animate-bounce">Scroll to explore</span>',
    "no-placeholder-identity": '<cite>John Doe, Acme Inc.</cite>',
    "no-filler-verb": '<h1>Elevate your brand with seamless design</h1>',
    "no-em-dash": '<p>Identity \u2014 packaging</p>',
}
EXTRA_TELL_LINES = {
    "no-em-dash": ['<p>Identity &mdash; packaging</p>', '<p>Identity &#8212; packaging</p>', '<p>{"\\u2014"}</p>'],
    "no-numbered-eyebrow": ['<p>01. Work</p>', '<span>(02) Services</span>'],
    "no-locale-strip": ['const t = now.toLocaleTimeString("en-GB", { timeZone: "Europe/Lisbon" });'],
}

CLEAN_PAGE = """\
import { motion } from "motion/react";

export default function Page() {
  return (
    <main className="min-h-screen bg-[var(--paper)] px-6 py-24 text-[var(--ink)]">
      <section className="mx-auto grid max-w-5xl gap-12 md:grid-cols-[2fr_1fr]">
        <h1 className="text-5xl leading-[1.05]">Identity, packaging and small websites for independent food and drink producers.</h1>
        <p className="text-lg opacity-80">Three designers. Recent work: Brasserie Coutant and Moulin Vert.</p>
      </section>
      <section className="mx-auto mt-24 max-w-5xl">
        <motion.a href="mailto:studio@fenwick.test" whileHover={{ y: -2 }} transition={{ duration: 0.18 }}>
          Write to studio@fenwick.test
        </motion.a>
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6" /></svg>
      </section>
      <footer className="mx-auto mt-24 max-w-5xl text-sm">\u00a9 2026 Fenwick. Invoices within 30 days, rates from 0.5 days.</footer>
    </main>
  );
}
"""


def graders_of(case: str) -> dict[str, tuple[dict, str]]:
    return {p.stem: check_evals.load_grader(p) for p in sorted((EVALS / case / "graders").glob("*.md"))}


def regex_of(fm: dict):
    return check_evals.compile_js_regex(fm["pattern"], fm.get("flags"))


def tool_input(**kwargs) -> str:
    # tool_used matches input_match against the JSON-encoded tool input.
    return json.dumps(kwargs)


class WebGraderTest(unittest.TestCase):
    def test_every_web_case_exists(self):
        for case in WEB_CASES:
            self.assertTrue((EVALS / case / "prompt.md").is_file(), f"{case} is missing")

    def test_each_not_contains_grader_fires_on_its_tell_and_not_on_the_clean_page(self):
        for case in WEB_CASES:
            for name, (fm, _) in graders_of(case).items():
                if fm.get("type") != "regex" or fm.get("match") != "not_contains":
                    continue
                with self.subTest(case=case, grader=name):
                    self.assertIn(name, TELL_LINES, f"{name} has no pinned tell line in this test")
                    rx = regex_of(fm)
                    for line in [TELL_LINES[name], *EXTRA_TELL_LINES.get(name, [])]:
                        self.assertIsNotNone(rx.search(line), f"{name} misses {line!r}")
                    self.assertIsNone(rx.search(CLEAN_PAGE), f"{name} fires on the clean page: {rx.search(CLEAN_PAGE)}")

    def test_every_tell_line_is_caught_by_its_grader(self):
        fms = {n: fm for n, (fm, _) in graders_of("studio-landing").items() if fm.get("match") == "not_contains"}
        for name, line in TELL_LINES.items():
            with self.subTest(tell=name):
                hits = sorted(n for n, fm in fms.items() if regex_of(fm).search(line))
                self.assertIn(name, hits)

    def test_the_guard_accepts_a_page_and_rejects_an_empty_one(self):
        for case in WEB_CASES:
            with self.subTest(case=case):
                rx = regex_of(graders_of(case)["page-has-content"][0])
                self.assertIsNotNone(rx.search(CLEAN_PAGE))
                helper_first = 'function Hero() { return <section />; }\nexport default async function Page() { return <Hero />; }'
                self.assertIsNotNone(rx.search(helper_first))
                self.assertIsNone(rx.search(""))
                self.assertIsNone(rx.search("export default function Page() { return null; }"))

    def test_shared_graders_are_identical_across_web_cases(self):
        reference = {n: fm for n, (fm, _) in graders_of("studio-landing").items()}
        for case in WEB_CASES[1:]:
            for name, (fm, _) in graders_of(case).items():
                if name in reference:
                    with self.subTest(case=case, grader=name):
                        self.assertEqual(fm, reference[name], f"{case}/{name} drifted from studio-landing")

    def test_fixtures_are_identical_across_web_cases_modulo_their_name(self):
        def normalized(case: str) -> str:
            # The case name is the only thing a case's fixture.sh is allowed to vary on
            # (it appears in the header comment and in the package.json "name" line);
            # blanking it out here must leave the three scaffolds byte-identical.
            return (EVALS / case / "fixture.sh").read_text().replace(case, "<case>")

        reference = normalized(WEB_CASES[0])
        for case in WEB_CASES[1:]:
            with self.subTest(case=case):
                self.assertEqual(
                    normalized(case), reference,
                    f"{case}/fixture.sh drifted from {WEB_CASES[0]}/fixture.sh beyond its own name",
                )

    def test_loading_indicators(self):
        for case in WEB_CASES:
            with self.subTest(case=case):
                g = graders_of(case)
                requested = check_evals.compile_js_regex(g["tells-requested"][0]["input_match"], None)
                self.assertIsNotNone(requested.search(tool_input(command='eval "$BLOCK"\nload_skill tells\nload_ref tells references/web.md')))
                self.assertIsNone(requested.search(tool_input(command="load_skill motion-principles")))
                reported = regex_of(g["tells-reported-loaded"][0])
                self.assertIsNotNone(reported.search("Modules loaded: motion-principles, tells, css-native\nModules not loaded: none"))
                self.assertIsNone(reported.search("Modules loaded: motion-principles\nModules not loaded: tells"))
                sentinel = regex_of(g["tells-read-sentinel"][0])
                self.assertIsNotNone(sentinel.search(json.dumps({"content": "# Tells\n\n" + check_evals.SENTINEL + " Every entry"})))
                for name in ("tells-requested", "tells-reported-loaded", "tells-read-sentinel", "paint-fired"):
                    self.assertEqual(g[name][0].get("arm"), "with-only", f"{case}/{name} must not count in the score")


class ThesisAllowsTest(unittest.TestCase):
    def test_locale_strip_grader_is_absent(self):
        self.assertNotIn("no-locale-strip", graders_of("thesis-allows"))

    def test_bar_graders_need_both_cities_and_a_time(self):
        g = graders_of("thesis-allows")
        cities, clock = regex_of(g["keeps-both-cities"][0]), regex_of(g["keeps-time-bar"][0])
        bar = '<div>{fmt("Europe/Paris")} Paris · Tokyo {fmt("Asia/Tokyo")}</div>\nconst fmt = (tz) => new Intl.DateTimeFormat("en-GB", { timeZone: tz, timeStyle: "short" }).format(now);'
        self.assertIsNotNone(cities.search(bar))
        self.assertIsNotNone(clock.search(bar))
        prose_only = "<p>A studio between Paris and Tokyo.</p>"
        self.assertIsNotNone(cities.search(prose_only))
        self.assertIsNone(clock.search(prose_only), "a page that dropped the bar but kept the prose must fail keeps-time-bar")
        self.assertIsNone(cities.search("<p>A studio in Paris.</p>"))


class SwiftUISkipTest(unittest.TestCase):
    def test_tells_is_caught_by_every_road_in(self):
        g = graders_of("swiftui-skip")
        shell = check_evals.compile_js_regex(g["tells-never-requested"][0]["input_match"], None)
        read = check_evals.compile_js_regex(g["tells-never-read"][0]["input_match"], None)
        for command in ("load_skill tells", "load_ref tells references/web.md", 'cat "$SKILL_BASE/tells/SKILL.md"', "sed -n 1,80p /x/_jutsu/tells/references/web.md"):
            self.assertIsNotNone(shell.search(tool_input(command=command)), command)
        self.assertIsNone(shell.search(tool_input(command="load_skill swiftui-motion\nload_skill motion-principles")))
        self.assertIsNotNone(read.search(tool_input(file_path="/tmp/x/skills/_jutsu/tells/SKILL.md")))
        self.assertIsNone(read.search(tool_input(file_path="/tmp/x/skills/_jutsu/swiftui-motion/SKILL.md")))
        for name in ("tells-never-requested", "tells-never-read"):
            fm = g[name][0]
            self.assertEqual((fm.get("min"), fm.get("max"), fm.get("arm")), (0, 0, "both"), name)

    def test_guard_needs_a_real_screen(self):
        rx = regex_of(graders_of("swiftui-skip")["swift-screen-written"][0])
        placeholder = (EVALS / "swiftui-skip" / "fixture.sh").read_text(encoding="utf-8")
        self.assertIsNone(rx.search(placeholder.split("TodayView.swift <<'SWIFT'", 1)[1]))
        self.assertIsNotNone(rx.search("var body: some View { ScrollView { LazyVStack(spacing: 12) { } } }"))


if __name__ == "__main__":
    unittest.main()
