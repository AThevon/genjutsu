#!/usr/bin/env python3
"""Static motion and accessibility audit for a web project.

Replaces nineteen shell greps that had two defects the shell could not fix.

The first: they were anchored on `src/`, which does not exist in a default
Next.js app-router or Nuxt 3 project, so they matched nothing and the pipeline
read "no findings" as a clean bill of health. This detects its roots.

The second, and the reason this is a script rather than better greps: a grep
cannot tell "I looked and found nothing" from "there was nothing here to look
at". Both print zero lines. Every check below declares what its own zero result
means, so a project with no `.tsx` files reports the AnimatePresence check as
NOT APPLICABLE rather than as passing. An audit that cannot fail is worse than
no audit.

Findings are evidence, never verdicts: each one carries the file, the line and
the matched text, because the caller has to report what established the claim.

Usage:
    python3 audit.py [root]              # markdown, for a human or a model
    python3 audit.py [root] --json       # machine-readable
    python3 audit.py [root] --only hover-no-transition

Exit status is 0 unless the audit itself failed to run. Findings are not errors:
this reports, the caller decides.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Directories that are never the user's source.
SKIP_DIRS = {
    "node_modules", ".git", ".next", ".nuxt", ".output", ".svelte-kit", ".astro",
    "dist", "build", "out", "coverage", "vendor", ".venv", "__pycache__",
    ".turbo", ".cache", "storybook-static", ".vercel", "ios", "android",
}

# Where a web project keeps its source, in the order we would guess.
ROOT_CANDIDATES = ["src", "app", "pages", "components", "layouts", "lib", "islands", "features", "widgets"]

JSX = {".tsx", ".jsx"}
SFC = {".vue", ".svelte", ".astro"}
STYLE = {".css", ".scss", ".sass", ".less"}
SCRIPT = {".ts", ".js", ".mjs"}


@dataclass
class Finding:
    check: str
    severity: str
    file: str
    line: int
    text: str


@dataclass
class Result:
    check: str
    title: str
    severity: str
    status: str          # "clean" | "findings" | "not-applicable"
    scanned: int         # files actually examined
    meaning: str         # what this result means, in words
    findings: list = field(default_factory=list)


@dataclass
class Check:
    id: str
    title: str
    severity: str        # critical | important | nice-to-have
    exts: set
    pattern: str
    # A line matching `unless` is not a finding. This is where the false
    # positives die: `:hover` next to a `transition` is fine.
    unless: str | None = None
    # Inverted: the finding is that the pattern is ABSENT from the whole tree.
    absence: bool = False
    zero_means: str = ""
    absent_means: str = ""


CHECKS = [
    Check(
        id="conditional-render-no-exit",
        title="Conditional render with no exit animation",
        severity="important",
        exts=JSX | SFC,
        pattern=r"\{\s*\w[\w.?]*\s*&&\s*<|\?\s*<\w+[\s/>]",
        unless=r"AnimatePresence|v-if|transition|\bexit\b|Transition",
        zero_means="No unguarded conditional mounts found in the files scanned.",
        absent_means="",
    ),
    Check(
        id="hover-no-transition",
        title="Hover state with no transition",
        severity="important",
        exts=STYLE | SFC,
        pattern=r":hover",
        unless=r"transition|animation|@media\s*\(\s*hover",
        zero_means="Every :hover rule found sits next to a transition or animation.",
    ),
    Check(
        id="animated-layout-property",
        title="Animating a layout property",
        severity="critical",
        exts=STYLE | SFC,
        pattern=r"transition\s*:[^;]*\b(width|height|top|left|right|bottom|margin|padding)\b",
        unless=r"transform|opacity",
        zero_means="No transition targets a layout property. Nothing forces layout per frame.",
    ),
    Check(
        id="outline-none",
        title="Focus outline removed with no replacement",
        severity="critical",
        exts=STYLE | SFC,
        pattern=r"outline\s*:\s*(none|0)\b",
        unless=r"focus-visible|box-shadow|outline-offset|:focus\s*\{[^}]*outline\s*:(?!\s*(none|0))",
        zero_means="No rule removes the focus outline, or every one that does replaces it.",
    ),
    Check(
        id="clickable-non-button",
        title="Click handler on a non-interactive element",
        severity="critical",
        exts=JSX | SFC,
        pattern=r"<(div|span|li)\b[^>]*\bon(Click|click)\b",
        unless=r"role\s*=|tabIndex|tabindex",
        zero_means="Every click handler found is on a button, a link, or an element with a role.",
    ),
    Check(
        id="decorative-motion-not-hidden",
        title="Decorative animation not hidden from assistive tech",
        severity="nice-to-have",
        exts=JSX | SFC,
        pattern=r"<(motion\.\w+|animated\.\w+|Lottie|Canvas|Player)\b",
        unless=r"aria-hidden|aria-label|role\s*=|alt\s*=",
        zero_means="Every animated element found carries an aria attribute or a role.",
    ),
    Check(
        id="will-change-broad",
        title="will-change left on permanently",
        severity="nice-to-have",
        exts=STYLE | SFC,
        pattern=r"will-change\s*:",
        unless=r"will-change\s*:\s*auto",
        zero_means="No permanent will-change. Nothing is holding a compositor layer for nothing.",
    ),
    Check(
        id="js-driven-animation",
        title="Animation driven by a timer instead of the compositor",
        severity="important",
        exts=JSX | SCRIPT | SFC,
        pattern=r"\b(setTimeout|setInterval)\s*\(",
        unless=r"debounce|throttle|fetch|poll|retry|timeout\s*[,)]|abort|toast|clearTimeout",
        zero_means="No timer appears to be driving visual state.",
    ),
    Check(
        id="inline-style-object",
        title="Inline style object on an animated element",
        severity="nice-to-have",
        exts=JSX,
        pattern=r"style=\{\{",
        unless=r"transform|opacity|transition|--",
        zero_means="No inline style object outside transform, opacity or custom properties.",
    ),
    Check(
        id="no-reduced-motion",
        title="prefers-reduced-motion is never honoured",
        severity="critical",
        exts=STYLE | SFC | JSX | SCRIPT,
        pattern=r"prefers-reduced-motion",
        absence=True,
        absent_means=(
            "Nothing in the project references prefers-reduced-motion. If anything moves, "
            "this is a critical accessibility gap, not a style preference."
        ),
        zero_means="prefers-reduced-motion is referenced somewhere in the project.",
    ),
]

# Inventories are not pass/fail. They answer "is this a system or an accident?",
# which is a judgement the caller makes from the spread.
DURATION_CONTEXT = re.compile(r"transition|animation|duration|delay|stagger", re.I)
DURATION_VALUE = re.compile(r"(?<![\w.-])(\d+(?:\.\d+)?)(ms|s)(?![\w-])|duration\s*[:=]\s*[\"'{]?\s*(\d+(?:\.\d+)?)", re.I)

INVENTORY = {
    "durations": (
        STYLE | JSX | SFC | SCRIPT,
        None,  # handled by collect_durations, the shorthand needs context
        "Durations in use. A designed system has three to five. Fifteen is an accident.",
    ),
    "easings": (
        STYLE | JSX | SFC | SCRIPT,
        re.compile(r"(cubic-bezier\([^)]*\)|ease-in-out|ease-out|ease-in|linear\b|steps\([^)]*\))", re.I),
        "Easings in use. Same rule: a handful, named, or it is not a system.",
    ),
}


def discover_roots(base: Path) -> tuple[list[Path], str]:
    """Directories to scan, and how they were chosen."""
    hits = [base / d for d in ROOT_CANDIDATES if (base / d).is_dir()]
    if hits:
        return hits, "detected: " + ", ".join(p.name for p in hits)
    return [base], "no conventional source directory found, scanning the whole tree"


def walk(roots: list[Path], base: Path) -> list[Path]:
    files = []
    for root in roots:
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if any(part in SKIP_DIRS for part in p.relative_to(base).parts):
                continue
            if p.suffix in JSX | SFC | STYLE | SCRIPT:
                files.append(p)
    return sorted(set(files))


def read(p: Path) -> list[str] | None:
    try:
        return p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None


def run_check(check: Check, files: list[Path], base: Path) -> Result:
    relevant = [f for f in files if f.suffix in check.exts]
    res = Result(check=check.id, title=check.title, severity=check.severity,
                 status="clean", scanned=len(relevant), meaning=check.zero_means)

    if not relevant:
        res.status = "not-applicable"
        res.meaning = (
            f"No files of the relevant type ({', '.join(sorted(check.exts))}) were found. "
            "This check did not run. Do not report it as passing."
        )
        return res

    pat = re.compile(check.pattern)
    unless = re.compile(check.unless) if check.unless else None
    found_any = False

    for f in relevant:
        lines = read(f)
        if lines is None:
            continue
        for n, line in enumerate(lines, 1):
            if not pat.search(line):
                continue
            found_any = True
            if check.absence:
                continue
            if unless and unless.search(line):
                continue
            res.findings.append(Finding(check.id, check.severity, str(f.relative_to(base)),
                                        n, line.strip()[:200]))

    if check.absence:
        if not found_any:
            res.status = "findings"
            res.meaning = check.absent_means
            res.findings.append(Finding(check.id, check.severity, "(whole project)", 0,
                                        "pattern never appears"))
        return res

    if res.findings:
        res.status = "findings"
        res.meaning = f"{len(res.findings)} occurrence(s) across {len(relevant)} file(s) scanned."
    return res


def collect_durations(line: str) -> list[str]:
    """Times in an animation context.

    `transition: width 300ms` is the common shape and carries no `duration:`
    key, so matching on the key alone found almost nothing. Requiring an
    animation word on the line keeps `maxAge: 3600s` and `timeout: 5000` out.
    """
    if not DURATION_CONTEXT.search(line):
        return []
    out = []
    for m in DURATION_VALUE.finditer(line):
        if m.group(1) is not None:
            value, unit = m.group(1), m.group(2).lower()
            ms = float(value) * (1000 if unit == "s" else 1)
        else:
            # A bare number next to `duration` is seconds in JS motion libraries.
            ms = float(m.group(3)) * 1000
        if 0 < ms <= 60_000:
            out.append(f"{ms:g}ms")
    return out


def run_inventory(files: list[Path], base: Path) -> dict:
    out = {}
    for name, (exts, pat, note) in INVENTORY.items():
        counter: Counter = Counter()
        relevant = [f for f in files if f.suffix in exts]
        for f in relevant:
            lines = read(f)
            if lines is None:
                continue
            for line in lines:
                if pat is None:
                    for v in collect_durations(line):
                        counter[v] += 1
                    continue
                for m in pat.findall(line):
                    counter[m.strip().lower()] += 1
        out[name] = {
            "note": note,
            "scanned": len(relevant),
            "distinct": len(counter),
            "values": counter.most_common(20),
        }
    return out


SEVERITY_ORDER = {"critical": 0, "important": 1, "nice-to-have": 2}


def as_markdown(base: Path, how: str, files: list[Path], results: list[Result], inv: dict) -> str:
    checked = [r for r in results if r.status != "not-applicable"]
    problems = [r for r in checked if r.status == "findings"]
    na = [r for r in results if r.status == "not-applicable"]

    out = [
        "## Static audit",
        "",
        f"Roots: {how}. {len(files)} file(s) examined.",
        "",
        f"**{len(checked)} checked, {len(problems)} with findings, {len(na)} not applicable.**",
        "",
        "Every line below is evidence, not a verdict. A check listed as not applicable did not",
        "run: report it as not checked, never as passed. This covers none of the items that need",
        "a profiler, a device or a pointer.",
        "",
    ]

    if problems:
        out.append("### Findings")
        out.append("")
        for r in sorted(problems, key=lambda x: SEVERITY_ORDER[x.severity]):
            out.append(f"**{r.severity.upper()} - {r.title}** ({r.check})")
            out.append("")
            out.append(f"{r.meaning}")
            out.append("")
            for f in r.findings[:12]:
                loc = f"`{f.file}:{f.line}`" if f.line else f"`{f.file}`"
                out.append(f"- {loc} - `{f.text}`")
            if len(r.findings) > 12:
                out.append(f"- ... and {len(r.findings) - 12} more")
            out.append("")

    clean = [r for r in checked if r.status == "clean"]
    if clean:
        out.append("### Checked, nothing found")
        out.append("")
        for r in sorted(clean, key=lambda x: x.check):
            out.append(f"- **{r.title}** - {r.meaning} ({r.scanned} file(s))")
        out.append("")

    if na:
        out.append("### Not checked")
        out.append("")
        for r in sorted(na, key=lambda x: x.check):
            out.append(f"- **{r.title}** - {r.meaning}")
        out.append("")

    out.append("### Inventory")
    out.append("")
    for name, data in inv.items():
        out.append(f"**{name}** - {data['distinct']} distinct value(s). {data['note']}")
        if data["values"]:
            out.append("")
            out.append("  " + ", ".join(f"`{v}` x{c}" for v, c in data["values"][:12]))
        out.append("")

    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".", help="project root (default: current directory)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--only", action="append", help="run only these check ids")
    args = ap.parse_args()

    base = Path(args.root).resolve()
    if not base.is_dir():
        print(f"audit: {base} is not a directory", file=sys.stderr)
        return 2

    roots, how = discover_roots(base)
    files = walk(roots, base)

    checks = CHECKS
    if args.only:
        wanted = set(args.only)
        checks = [c for c in CHECKS if c.id in wanted]
        unknown = wanted - {c.id for c in CHECKS}
        if unknown:
            print(f"audit: unknown check(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2

    results = [run_check(c, files, base) for c in checks]
    inv = run_inventory(files, base)

    if args.json:
        print(json.dumps({
            "root": str(base),
            "roots_note": how,
            "files_examined": len(files),
            "results": [asdict(r) for r in results],
            "inventory": inv,
        }, indent=2))
    else:
        print(as_markdown(base, how, files, results, inv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
