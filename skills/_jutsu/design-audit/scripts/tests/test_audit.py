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

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import audit  # noqa: E402

AUDIT = Path(__file__).resolve().parent.parent / "audit.py"


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
    # Tells. The positive fixture is the reflex, the negative one the same slot
    # filled from the project. Written with escapes: no U+2014 in this file.
    "tell-invented-status": (
        {"app/page.tsx": "export default () => <footer><span>v0.6.2-rc.1</span><span>last sync 4s ago</span></footer>\n"},
        {"app/page.tsx": "export default () => <footer><span>Version history lives in the changelog.</span></footer>\n"},
    ),
    "tell-locale-strip": (
        {"app/page.tsx": "export default () => <nav><span>LIS 14:23 · 18°C</span></nav>\n"},
        {"app/page.tsx": "export default () => <p>Open 9:00 to 18:00, Tuesday to Saturday.</p>\n"},
    ),
    "tell-numbered-eyebrow": (
        {"app/page.tsx": "export default () => <section><p>00 / INDEX</p><span>01 / 4</span></section>\n"},
        {"app/page.tsx": "export default () => <section><p>Selected work</p></section>\n"},
    ),
    "tell-generic-step": (
        {"app/page.tsx": "export default () => <ol><li>Stage 1</li><li>Stage 2</li></ol>\n"},
        {"app/page.tsx": "export default () => <ol><li>Install</li><li>Configure</li></ol>\n"},
    ),
    "tell-scroll-cue": (
        {"app/page.tsx": "export default () => <div><span>↓ Scroll to explore</span></div>\n"},
        {"app/page.tsx": "export default () => <p>Scrolling back through ten years of work.</p>\n"},
    ),
    "tell-placeholder-identity": (
        {"app/page.tsx": "export default () => <cite>Jane Doe, CEO at Acme</cite>\n"},
        {"app/page.tsx": "export default () => <cite>Mireille Achard, head of product at Ferrand</cite>\n"},
    ),
    "tell-round-number": (
        {"app/page.tsx": "export default () => <p><strong>99.99% uptime</strong> for 10,000+ teams</p>\n"},
        {"app/page.tsx": "export default () => <p><strong>41 releases</strong> since 2019</p>\n"},
    ),
    "tell-filler-verb": (
        {"app/page.tsx": "export default () => <h1>Elevate your workflow</h1>\n"},
        {"app/page.tsx": "export default () => <h1>Invoices that reconcile themselves</h1>\n"},
    ),
    "tell-em-dash": (
        # One file per spelling: the character and the three HTML entities.
        {
            "app/a.html": "<p>Made by hand \u2014 slowly</p>\n",
            "app/b.html": "<p>Made by hand &mdash; slowly</p>\n",
            "app/c.html": "<p>Made by hand &#8212; slowly</p>\n",
            "app/d.tsx": "export default () => <p>Made by hand &#x2014; slowly</p>\n",
        },
        {"app/a.html": "<p>Made by hand - slowly</p>\n"},
    ),
    "tell-dot-run": (
        {"app/page.tsx": "export default () => <p>Brand · Motion · Spatial</p>\n"},
        {"app/page.tsx": "export default () => <p>Lyon · since 2011</p>\n"},
    ),
    "tell-fake-code": (
        {"app/page.tsx": 'export default () => <p className="text-xs">SEC-01 Capabilities</p>\n'},
        {"app/page.tsx": 'export default () => <p>Certified to ISO 9001 since 2011</p>\n'},
    ),
    "tell-glass": (
        {"app/page.tsx": 'export default () => <nav className="bg-white/10 backdrop-blur-md">Menu</nav>\n'},
        {"app/page.tsx": 'export default () => <nav className="bg-white border-b">Menu</nav>\n'},
    ),
    "tell-glow": (
        {"app/globals.css": ".cta { box-shadow: 0 0 40px rgba(255, 0, 128, 0.6); }\n"},
        {"app/globals.css": ".cta { box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1); outline-offset: 2px; }\n"},
    ),
    "tell-blob": (
        {"app/page.tsx": 'export default () => <div className="absolute -z-10 h-96 w-96 rounded-full bg-pink-400 blur-3xl" />\n'},
        {"app/page.tsx": 'export default () => <div className="absolute -z-10 h-96 w-96 bg-stone-100 backdrop-blur-3xl" />\n'},
    ),
    "tell-perpetual-motion": (
        {"app/globals.css": ".dot { animation: pulse 2s ease-in-out infinite; }\n"},
        {"app/globals.css": ".dot { animation: fade-in 200ms ease-out 1; }\n"},
    ),
    "tell-gradient-text": (
        {"app/page.tsx": 'export default () => <h1 className="bg-gradient-to-r from-amber-500 to-rose-500 bg-clip-text text-transparent">Hi</h1>\n'},
        {"app/page.tsx": 'export default () => <h1 className="text-zinc-900">Hi</h1>\n'},
    ),
    "tell-equal-cards": (
        {"app/page.tsx": (
            "export default () => (\n"
            '  <div className="grid md:grid-cols-3 gap-6">\n'
            '    <article className="card p-6">A</article>\n'
            '    <article className="card p-6">B</article>\n'
            '    <article className="card p-6">C</article>\n'
            "  </div>\n"
            ")\n")},
        {"app/page.tsx": (
            "export default () => (\n"
            '  <div className="grid md:grid-cols-3 gap-6">\n'
            '    <article className="card p-6 md:col-span-2">A</article>\n'
            '    <article className="card p-6">B</article>\n'
            '    <article className="card p-6 md:row-span-2">C</article>\n'
            "  </div>\n"
            ")\n")},
    ),
    "tell-duplicate-cta": (
        {"app/page.tsx": (
            "export default () => (\n"
            "  <main>\n"
            '    <a href="/signup">Get started</a>\n'
            "    <button>Start free trial</button>\n"
            '    <Link href="/join">Sign up</Link>\n'
            "  </main>\n"
            ")\n")},
        {"app/page.tsx": (
            "export default () => (\n"
            "  <main>\n"
            '    <a href="/signup">Get started</a>\n'
            "    <button>Get started</button>\n"
            '    <a href="/pricing">Learn more</a>\n'
            "  </main>\n"
            ")\n")},
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


class CheckMechanics(unittest.TestCase):
    """v4: a check belongs to a group, reads a surface, and may be a function."""

    def test_check_defaults_keep_the_old_behaviour(self):
        c = audit.Check(id="x", title="x", severity="important", exts={".css"}, pattern="a")
        self.assertEqual((c.group, c.surface, c.fn), ("hygiene", "source", None))
        bare = audit.Check(id="y", title="y", severity="important", exts={".css"})
        self.assertEqual(bare.pattern, "")

    def test_non_tell_checks_are_hygiene(self):
        for c in audit.CHECKS:
            if not c.id.startswith("tell-"):
                with self.subTest(check=c.id):
                    self.assertEqual(c.group, "hygiene")

    def test_result_carries_the_group(self):
        root = build({"src/a.css": ".btn:hover { color: red; }\n"})
        try:
            res = audit_it(root, only="hover-no-transition")["hover-no-transition"]
            self.assertEqual(res.group, "hygiene")
        finally:
            shutil.rmtree(root)

    def test_walk_includes_html(self):
        root = build({"index.html": "<p>hi</p>\n", "notes.txt": "x\n"})
        try:
            files = audit.walk(audit.discover_roots(root)[0], root)
            self.assertEqual([f.name for f in files], ["index.html"])
        finally:
            shutil.rmtree(root)

    def test_select_checks_by_group(self):
        self.assertEqual({c.group for c in audit.select_checks(None, ["hygiene"])}, {"hygiene"})
        with self.assertRaises(ValueError):
            audit.select_checks(None, ["nope"])
        with self.assertRaises(ValueError):
            audit.select_checks(["nope"], None)

    def test_cli_group_option(self):
        root = build({"src/a.css": ".btn:hover { color: red; }\n"})
        try:
            ok = subprocess.run([sys.executable, str(AUDIT), str(root), "--json", "--group", "hygiene"],
                                capture_output=True, text=True, check=True)
            self.assertEqual({r["group"] for r in json.loads(ok.stdout)["results"]}, {"hygiene"})
            bad = subprocess.run([sys.executable, str(AUDIT), str(root), "--group", "nope"],
                                 capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
            self.assertIn("unknown group", bad.stderr)
        finally:
            shutil.rmtree(root)


class TextSurface(unittest.TestCase):
    """What a text check can see. `width: "100%"` must never read as a claim."""

    def text_of(self, name: str, body: str) -> list[tuple[int, str]]:
        return audit.displayed_text_lines(Path(name), body.splitlines())

    def test_text_between_tags_and_text_attributes(self):
        body = ('export default function P() {\n'
                '  return (\n'
                '    <main>\n'
                '      <h1 title="Studio">Hello there</h1>\n'
                '      <img alt="A kiln at dusk" src="/k.jpg" />\n'
                '      <input placeholder="Your email" aria-label="Email" />\n'
                '    </main>\n'
                '  )\n'
                '}\n')
        self.assertEqual(self.text_of("app/page.tsx", body), [
            (4, "Studio"), (4, "Hello there"), (5, "A kiln at dusk"), (6, "Your email"), (6, "Email"),
        ])

    def test_style_objects_and_class_names_never_come_out(self):
        body = ('const card = { width: "100%", height: "50%" }\n'
                'export const A = () => (\n'
                '  <div style={{ width: "100%" }} className="w-full grid-cols-3">\n'
                '    Ready\n'
                '  </div>\n'
                ')\n')
        texts = [t for _, t in self.text_of("src/A.tsx", body)]
        self.assertEqual(texts, ["Ready"])

    def test_inline_tags_inside_text_stay_markup(self):
        body = '<p>Plain<b>bold</b> end</p>\n'
        self.assertEqual(self.text_of("src/A.tsx", body), [(1, "Plain"), (1, "bold"), (1, "end")])

    def test_arrow_in_an_attribute_does_not_end_the_tag(self):
        body = '<button onClick={() => go(1 > 0)}>Book a call</button>\n'
        self.assertEqual(self.text_of("src/A.tsx", body), [(1, "Book a call")])

    def test_expressions_are_blanked_and_mapped_children_still_read(self):
        body = ('<ul>\n'
                '  {items.map((i) => (\n'
                '    <li key={i.id}>Plate {i.n} of the series</li>\n'
                '  ))}\n'
                '</ul>\n')
        self.assertEqual(self.text_of("src/L.jsx", body), [(3, "Plate of the series")])

    def test_generics_and_comparisons_are_not_tags(self):
        body = ('const [v, setV] = useState<string>("x")\n'
                'if (a < b && c > d) run()\n')
        self.assertEqual(self.text_of("src/A.tsx", body), [])

    def test_a_generic_arrow_is_not_a_tag(self):
        body = ('const id = <T,>(x: T) => x\n'
                'const pair = <A, B>(a: A, b: B) => [a, b]\n'
                'const keep = <T extends object>(o: T) => o\n'
                'export const L = ({ xs }) => <ul>{xs.map(<T,>(x: T) => <li key={String(x)}>Item</li>)}</ul>\n')
        self.assertEqual(self.text_of("src/A.tsx", body), [(4, "Item")])

    def test_script_style_and_comments_are_skipped_in_html(self):
        body = ('<!doctype html>\n<html><head><style>.a{width:100%}</style>\n'
                '<script>const s = "<p>not text</p>"</script></head>\n'
                '<body><!-- <p>hidden</p> --><p>Shown</p></body></html>\n')
        self.assertEqual(self.text_of("index.html", body), [(4, "Shown")])

    def test_astro_frontmatter_and_vue_script_are_code(self):
        astro = '---\nconst title = "<b>not</b>"\n---\n<h2>{title}</h2><p>Visible</p>\n'
        self.assertEqual(self.text_of("src/pages/index.astro", astro), [(4, "Visible")])
        vue = '<template><p>Hi</p></template>\n<script setup>\nconst x = "<i>no</i>"\n</script>\n'
        self.assertEqual(self.text_of("src/C.vue", vue), [(1, "Hi")])

    def test_css_and_scripts_have_no_text_surface(self):
        self.assertEqual(self.text_of("src/a.css", '.a::after { content: "Elevate"; }\n'), [])
        self.assertEqual(self.text_of("src/a.ts", 'export const t = "<p>Elevate</p>"\n'), [])

    def test_copy_in_js_data_is_not_displayed_text(self):
        """A documented limit: copy kept in JS data and rendered through {...} is not seen.
        tells/SKILL.md and design-audit say so; this keeps the docs and the code in step."""
        body = 'const f = [{ t: "Elevate" }]\nexport const A = () => <p>{f[0].t}</p>\n'
        self.assertEqual(self.text_of("src/A.tsx", body), [])


class MarkupSurface(unittest.TestCase):
    def test_class_values_only(self):
        body = ('<div className="grid grid-cols-3" title="x">\n'
                "  <p class='lead'>Text</p>\n"
                '  <span className={`pill`} style={{ color: "red" }} />\n'
                '</div>\n')
        self.assertEqual(audit.markup_class_lines(Path("src/A.tsx"), body.splitlines()),
                         [(1, "grid grid-cols-3"), (2, "lead"), (3, "pill")])


class SurfaceDispatch(unittest.TestCase):
    def run_one(self, check: audit.Check, files: dict[str, str]) -> audit.Result:
        root = build(files)
        try:
            return audit.run_check(check, audit.walk(audit.discover_roots(root)[0], root), root)
        finally:
            shutil.rmtree(root)

    def test_text_surface_ignores_code_that_source_would_match(self):
        files = {"src/A.tsx": 'const s = { width: "100%" }\nexport const A = () => <p>100% organic</p>\n'}
        text = audit.Check(id="t", title="t", severity="nice-to-have", exts=audit.JSX,
                           pattern=r"100%", surface="text")
        source = audit.Check(id="s", title="s", severity="nice-to-have", exts=audit.JSX, pattern=r"100%")
        self.assertEqual([(f.line, f.text) for f in self.run_one(text, files).findings], [(2, "100% organic")])
        self.assertEqual(len(self.run_one(source, files).findings), 2)

    def test_markup_surface_reads_class_attributes(self):
        files = {"src/A.tsx": '<p className="uppercase tracking-widest">uppercase</p>\n'}
        c = audit.Check(id="m", title="m", severity="nice-to-have", exts=audit.JSX,
                        pattern=r"tracking-widest", surface="markup")
        self.assertEqual([f.text for f in self.run_one(c, files).findings], ["uppercase tracking-widest"])

    def test_fn_check_gets_relevant_files_and_its_id(self):
        seen = []

        def fn(files, base):
            seen.extend(p.name for p in files)
            return [audit.Finding("", "", "src/A.tsx", 1, "hit")]

        c = audit.Check(id="f", title="f", severity="nice-to-have", exts=audit.JSX, fn=fn, group="tells")
        res = self.run_one(c, {"src/A.tsx": "<p/>\n", "src/a.css": ".a{}\n"})
        self.assertEqual(seen, ["A.tsx"])
        self.assertEqual((res.status, res.group, res.findings[0].check, res.findings[0].severity),
                         ("findings", "tells", "f", "nice-to-have"))
        self.assertEqual(self.run_one(c, {"src/a.css": ".a{}\n"}).status, "not-applicable")


class EmDashSpellings(unittest.TestCase):
    """Review focus: an em dash typed as an HTML entity is still an em dash."""

    def test_every_spelling_is_found(self):
        bad, _ = CASES["tell-em-dash"]
        root = build(bad)
        try:
            res = audit_it(root, only="tell-em-dash")["tell-em-dash"]
            self.assertEqual({f.file for f in res.findings},
                             {"app/a.html", "app/b.html", "app/c.html", "app/d.tsx"})
        finally:
            shutil.rmtree(root)

    def test_uppercase_hex_entity_and_attribute_values(self):
        root = build({"app/page.tsx": 'export default () => <img alt="Kiln &#X2014; dusk" src="/k.jpg" />\n'})
        try:
            self.assertEqual(audit_it(root, only="tell-em-dash")["tell-em-dash"].status, "findings")
        finally:
            shutil.rmtree(root)

    def test_code_comments_are_not_displayed_text(self):
        root = build({"app/page.tsx": "// spacing \u2014 see tokens\nexport default () => <p>Plain</p>\n"})
        try:
            self.assertEqual(audit_it(root, only="tell-em-dash")["tell-em-dash"].status, "clean")
        finally:
            shutil.rmtree(root)


class StructuralTells(unittest.TestCase):
    """The two tells that need the element tree or the whole project at once."""

    def test_equal_cards_points_at_the_container(self):
        bad, _ = CASES["tell-equal-cards"]
        root = build(bad)
        try:
            res = audit_it(root, only="tell-equal-cards")["tell-equal-cards"]
            self.assertEqual([(f.file, f.line) for f in res.findings], [("app/page.tsx", 2)])
        finally:
            shutil.rmtree(root)

    def test_equal_cards_ignores_two_columns_and_inline_grids_of_four(self):
        body = ('export default () => (<>\n'
                '  <div className="grid grid-cols-2"><p className="c">A</p><p className="c">B</p><p className="c">C</p></div>\n'
                '  <div style={{ gridTemplateColumns: "repeat(4, 1fr)" }}><p className="c">A</p><p className="c">B</p><p className="c">C</p></div>\n'
                '</>)\n')
        root = build({"app/page.tsx": body})
        try:
            self.assertEqual(audit_it(root, only="tell-equal-cards")["tell-equal-cards"].status, "clean")
        finally:
            shutil.rmtree(root)

    def test_equal_cards_reads_a_repeat_three_style(self):
        body = ('<div style="grid-template-columns: repeat(3, 1fr)">'
                '<div class="tile">A</div><div class="tile">B</div><div class="tile">C</div></div>\n')
        root = build({"index.html": body})
        try:
            self.assertEqual(audit_it(root, only="tell-equal-cards")["tell-equal-cards"].status, "findings")
        finally:
            shutil.rmtree(root)

    def test_duplicate_cta_spans_files(self):
        root = build({
            "app/page.tsx": 'export default () => <a href="/signup">Get started</a>\n',
            "app/pricing/page.tsx": "export default () => <button>Sign up free</button>\n",
        })
        try:
            res = audit_it(root, only="tell-duplicate-cta")["tell-duplicate-cta"]
            self.assertEqual({f.file for f in res.findings}, {"app/page.tsx", "app/pricing/page.tsx"})
        finally:
            shutil.rmtree(root)

    def test_cta_label_flattens_nested_markup_and_drops_expressions(self):
        body = '<a href="#demo"><span>Book</span> a demo {arrow}</a>\n'
        self.assertEqual(audit.cta_labels(Path("src/A.tsx"), body.splitlines()), [(1, "Book a demo")])


TELL_IDS = {
    "tell-invented-status", "tell-locale-strip", "tell-numbered-eyebrow", "tell-generic-step",
    "tell-scroll-cue", "tell-placeholder-identity", "tell-round-number", "tell-filler-verb",
    "tell-em-dash", "tell-dot-run", "tell-duplicate-cta", "tell-equal-cards", "tell-gradient-text",
    "tell-fake-code", "tell-glass", "tell-glow", "tell-blob", "tell-perpetual-motion",
}

# Three whole pages. The first is the landing a model writes when nothing stops it,
# the second fills the same slots from a real project, the third has no web source.
TELLS_PAGE = {
    "app/page.tsx": (
        'import Link from "next/link"\n'
        "\n"
        "export default function Page() {\n"
        "  return (\n"
        '    <main className="bg-stone-50">\n'
        '      <div className="absolute -z-10 h-96 w-96 rounded-full bg-pink-400 blur-3xl" />\n'
        '      <nav className="flex justify-between backdrop-blur-md">\n'
        "        <span>LIS 14:23 · 18°C</span>\n"
        '        <a href="/signup">Get started</a>\n'
        "      </nav>\n"
        "      <section>\n"
        '        <p className="text-xs uppercase tracking-widest">00 / INDEX</p>\n'
        '        <span className="animate-pulse">SEC-01</span>\n'
        '        <h1 className="bg-gradient-to-r from-amber-500 to-rose-500 bg-clip-text text-transparent">\n'
        "          Elevate your workflow &mdash; seamlessly\n"
        "        </h1>\n"
        "        <p>Trusted by 10,000+ teams with 99.99% uptime.</p>\n"
        '        <button className="shadow-[0_0_40px_rgba(255,0,128,0.6)]">Start free trial</button>\n'
        "        <span>Scroll to explore</span>\n"
        "      </section>\n"
        '      <section className="grid md:grid-cols-3 gap-6">\n'
        '        <article className="card p-6">Sync</article>\n'
        '        <article className="card p-6">Review</article>\n'
        '        <article className="card p-6">Ship</article>\n'
        "      </section>\n"
        "      <ol>\n"
        "        <li>Stage 1</li>\n"
        "        <li>Stage 2</li>\n"
        "      </ol>\n"
        "      <blockquote>\n"
        "        <p>It changed how we work.</p>\n"
        "        <cite>Jane Doe, CEO at Acme</cite>\n"
        "      </blockquote>\n"
        "      <footer>\n"
        "        <p>Brand · Motion · Spatial</p>\n"
        "        <span>v0.6.2-rc.1</span>\n"
        '        <Link href="/join">Sign up</Link>\n'
        "      </footer>\n"
        "    </main>\n"
        "  )\n"
        "}\n"
    ),
}

CLEAN_PAGE = {
    "app/page.tsx": (
        "export default function Page() {\n"
        "  return (\n"
        "    <main>\n"
        '      <nav className="flex justify-between">\n'
        "        <span>Atelier Ferrand</span>\n"
        '        <a href="/commissions">Start a commission</a>\n'
        "      </nav>\n"
        "      <section>\n"
        '        <h1 className="text-5xl text-stone-900">Tableware thrown in Lyon since 2011</h1>\n'
        "        <p>Forty-one glazes, each tested on a single kiln before it reaches the shop.</p>\n"
        '        <a href="/commissions">Start a commission</a>\n'
        "      </section>\n"
        '      <section className="grid md:grid-cols-3 gap-6">\n'
        '        <article className="md:col-span-2 p-6">Plates</article>\n'
        '        <article className="p-6">Bowls</article>\n'
        '        <article className="p-6 bg-stone-100">Cups</article>\n'
        "      </section>\n"
        "      <ol>\n"
        "        <li>Choose a glaze</li>\n"
        "        <li>Approve a test piece</li>\n"
        "      </ol>\n"
        "      <blockquote>\n"
        "        <p>The test piece arrived before the invoice did.</p>\n"
        "        <cite>Mireille Achard, Restaurant Sauvage</cite>\n"
        "      </blockquote>\n"
        "      <footer>\n"
        "        <p>Lyon · since 2011</p>\n"
        '        <a href="/contact">Write to the studio</a>\n'
        "      </footer>\n"
        "    </main>\n"
        "  )\n"
        "}\n"
    ),
    "app/globals.css": ".lead { color: #1a1a1a; }\n",
}

NON_WEB = {
    "Package.swift": '// swift-tools-version:5.9\nimport PackageDescription\nlet package = Package(name: "Kiln")\n',
    "Sources/Kiln/ContentView.swift": (
        "import SwiftUI\n"
        'struct ContentView: View { var body: some View { Text("Elevate \\u{2014} v0.6.2") } }\n'
    ),
}


class TellsGroup(unittest.TestCase):
    def test_every_tell_exists(self):
        self.assertEqual({c.id for c in audit.CHECKS if c.group == "tells"}, TELL_IDS)

    def test_json_carries_the_group(self):
        root = build(TELLS_PAGE)
        try:
            out = subprocess.run([sys.executable, str(AUDIT), str(root), "--json", "--group", "tells"],
                                 capture_output=True, text=True, check=True)
            results = json.loads(out.stdout)["results"]
            self.assertEqual({r["check"] for r in results}, TELL_IDS)
            self.assertEqual({r["group"] for r in results}, {"tells"})
        finally:
            shutil.rmtree(root)


class PageFixtures(unittest.TestCase):
    def run_all(self, files: dict[str, str]) -> dict[str, audit.Result]:
        root = build(files)
        try:
            return audit_it(root)
        finally:
            shutil.rmtree(root)

    def test_every_tell_fires_on_the_tells_page(self):
        results = self.run_all(TELLS_PAGE)
        for cid in sorted(TELL_IDS):
            with self.subTest(check=cid):
                self.assertEqual(results[cid].status, "findings")

    def test_no_tell_fires_on_the_clean_page(self):
        results = self.run_all(CLEAN_PAGE)
        for cid in sorted(TELL_IDS):
            with self.subTest(check=cid):
                self.assertEqual(results[cid].status, "clean", [f.text for f in results[cid].findings])

    def test_every_tell_is_not_applicable_without_web_source(self):
        results = self.run_all(NON_WEB)
        for cid in sorted(TELL_IDS):
            with self.subTest(check=cid):
                self.assertEqual(results[cid].status, "not-applicable")
                self.assertIn("did not run", results[cid].meaning)


class DesignInventory(unittest.TestCase):
    """Colours, radii and fonts are reported with where they live, never judged."""

    def inv(self, files: dict[str, str]) -> dict:
        root = build(files)
        try:
            return audit.run_inventory(audit.walk(audit.discover_roots(root)[0], root), root)
        finally:
            shutil.rmtree(root)

    def test_colors_radii_and_fonts_are_inventoried(self):
        inv = self.inv({
            "app/globals.css": (":root { --ink: #1A1A1A; --paper: rgb(250, 248, 244); }\n"
                                ".veil { background: rgba(var(--ink-rgb), 0.5); }\n"
                                '.card { border-radius: 12px; font-family: "Fraunces", serif; }\n'
                                "@theme { --font-body: 'Inter', sans-serif; }\n"),
            "app/layout.tsx": ('import { Inter, Instrument_Serif } from "next/font/google"\n'
                               'export default () => <p className="bg-zinc-900 rounded-lg font-mono">x &#8212; y</p>\n'),
        })
        self.assertEqual(set(dict(inv["colors"]["values"])), {"#1a1a1a", "rgb(250, 248, 244)", "rgba(var(--ink-rgb), 0.5)", "zinc-900"})
        self.assertEqual(set(dict(inv["radii"]["values"])), {"12px", "rounded-lg"})
        self.assertEqual(set(dict(inv["fonts"]["values"])), {"fraunces", "inter", "instrument serif", "font-mono"})

    def test_each_value_keeps_a_bounded_list_of_locations(self):
        css = "".join(f".c{i} {{ transition: opacity 300ms; }}\n" for i in range(8))
        inv = self.inv({"src/a.css": css, "src/b.css": ".z { transition: opacity 300ms; }\n"})
        self.assertEqual(dict(inv["durations"]["values"])["300ms"], 9)
        self.assertEqual(inv["durations"]["where"]["300ms"], [f"src/a.css:{n}" for n in range(1, 6)])

    def test_markdown_shows_where_each_value_lives(self):
        root = build({"src/a.css": ".a { transition: opacity 300ms ease-out; }\n"})
        try:
            roots, how = audit.discover_roots(root)
            files = audit.walk(roots, root)
            results = [audit.run_check(c, files, root) for c in audit.CHECKS]
            md = audit.as_markdown(root, how, files, results, audit.run_inventory(files, root))
            self.assertIn("- `300ms` x1 - `src/a.css:1`", md)
        finally:
            shutil.rmtree(root)


def section(md: str, heading: str) -> str:
    """The markdown between `heading` and the next level-3 heading."""
    if heading not in md:
        return ""
    rest = md.split(heading, 1)[1]
    return rest.split("\n### ", 1)[0]


class TellsAreReportedApart(unittest.TestCase):
    def test_tells_are_never_auto_problems(self):
        """Review focus 4. A real version on a docs page is still reported, but apart,
        at nice-to-have, and never among the problems: only the thesis can clear it."""
        for c in audit.CHECKS:
            if c.id in TELL_IDS:
                with self.subTest(check=c.id):
                    self.assertEqual((c.group, c.severity), ("tells", "nice-to-have"))
        root = build({"app/docs/page.tsx": "export default () => <p>Changelog for v2.4.1</p>\n"})
        try:
            roots, how = audit.discover_roots(root)
            files = audit.walk(roots, root)
            results = [audit.run_check(c, files, root) for c in audit.CHECKS]
            res = {r.check: r for r in results}["tell-invented-status"]
            self.assertEqual((res.status, res.group, res.severity), ("findings", "tells", "nice-to-have"))
            md = audit.as_markdown(root, how, files, results, audit.run_inventory(files, root))
            self.assertIn("tell-invented-status", section(md, audit.TELLS_HEADING))
            self.assertNotIn("tell-", section(md, "### Findings"))
            self.assertIn("1 tell check(s) fired", md)
        finally:
            shutil.rmtree(root)


class ComponentsAreNotVoid(unittest.TestCase):
    """`<Link>` is a component, not the void `<link>`: in JSX and SFC files only a
    lowercase name is an HTML void element. HTML itself stays case-insensitive."""

    def equal_cards(self, files: dict[str, str]) -> list[tuple[str, int]]:
        root = build(files)
        try:
            res = audit_it(root, only="tell-equal-cards")["tell-equal-cards"]
            return [(f.file, f.line) for f in res.findings]
        finally:
            shutil.rmtree(root)

    def test_a_grid_of_link_cards_is_equal_cards(self):
        body = ("export default () => (\n"
                '  <div className="grid md:grid-cols-3 gap-6">\n'
                '    <Link href="/plates" className="card"><h3>Plates</h3><p>Thrown</p></Link>\n'
                '    <Link href="/bowls" className="card"><h3>Bowls</h3><p>Turned</p></Link>\n'
                '    <Link href="/cups" className="card"><h3>Cups</h3><p>Pulled</p></Link>\n'
                "  </div>\n"
                ")\n")
        self.assertEqual(self.equal_cards({"app/page.tsx": body}), [("app/page.tsx", 2)])

    def test_text_after_a_closing_component_is_still_displayed(self):
        body = '<footer><Link href="/">Home</Link> Made in Lyon</footer>\n'
        for name in ("app/page.tsx", "src/Footer.jsx", "src/Footer.vue", "src/Footer.svelte",
                     "src/Footer.astro"):
            with self.subTest(file=name):
                self.assertEqual(audit.displayed_text_lines(Path(name), body.splitlines()),
                                 [(1, "Home"), (1, "Made in Lyon")])

    def test_lowercase_input_and_img_stay_void_in_jsx(self):
        body = ("export const A = () => (\n"
                '  <p>Open<img src="/k.jpg" alt="Kiln"><input placeholder="Email"></p>\n'
                ")\n"
                "const later = 1\n")
        self.assertEqual(audit.displayed_text_lines(Path("src/A.tsx"), body.splitlines()),
                         [(2, "Open"), (2, "Kiln"), (2, "Email")])
        grid = ('<div className="grid grid-cols-3"><img className="t" src="/a.png">'
                '<img className="t" src="/b.png"><img className="t" src="/c.png"></div>\n')
        self.assertEqual(self.equal_cards({"src/A.tsx": grid}), [("src/A.tsx", 1)])

    def test_html_void_tags_stay_case_insensitive(self):
        grid = ('<div class="grid grid-cols-3"><IMG class="t" src="/a.png">'
                '<Img class="t" src="/b.png"><img class="t" src="/c.png"></div>\n')
        self.assertEqual(self.equal_cards({"index.html": grid}), [("index.html", 1)])


if __name__ == "__main__":
    unittest.main()
