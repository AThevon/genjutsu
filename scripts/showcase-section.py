#!/usr/bin/env python3
"""Writes the measured block of the README and of the release notes.

For each eval case: the tells that audit.py finds on the first run of each arm
(its `tells` group only), the grader delta the ablation reported, and the
captures of both arms on desktop and mobile. The release shows instead of
asserting, so a missing capture or page is an error, never a broken image.

The block sits between `<!-- genjutsu:showcase:start -->` and
`<!-- genjutsu:showcase:end -->`. Without --write it is printed; with --write
it replaces that region of the file, which must hold exactly one.

Usage:
    python3 scripts/showcase-section.py \\
        --local-images <captures dir> --images <captures URL or path> \\
        --evals-link ./evals --runs 2 --revision ef31234 \\
        --case "studio-landing|Independent design studio landing|<without dir>|<with dir>|<delta>" \\
        [--case ...] [--captures saas-landing | --captures none] [--write README.md]

The v4.0.0 captures are no longer on main: they are kept at the v4.0.0 tag, in
assets/v4/, and the CHANGELOG links to them there with raw URLs pinned to that
tag. A new set of captures needs a home and a URL of its own.

Every case gets its row. --captures picks the cases whose before / after pair
is shown (repeatable, "none" for no image); without it every case shows its pair.

Stdlib only, like every script here.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

START = "<!-- genjutsu:showcase:start -->"
END = "<!-- genjutsu:showcase:end -->"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = ROOT / "skills" / "_jutsu" / "design-audit" / "scripts" / "audit.py"
ARMS = (("without", "Without genjutsu"), ("with", "With genjutsu"))
VIEWPORTS = (("desktop", 400), ("mobile", 180))


class Fail(Exception):
    pass


def count_tells(audit: Path, page_dir: Path) -> int:
    if not page_dir.is_dir():
        raise Fail(f"page directory not found: {page_dir}")
    r = subprocess.run(
        [sys.executable, str(audit), str(page_dir), "--json", "--group", "tells"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise Fail(f"audit.py failed on {page_dir}: {r.stderr.strip()}")
    data = json.loads(r.stdout)
    return sum(len(res["findings"]) for res in data["results"] if res.get("group") == "tells")


def parse_case(raw: str) -> tuple[str, str, Path, Path, str]:
    parts = raw.split("|")
    if len(parts) != 5:
        raise Fail(f"--case needs slug|label|without dir|with dir|delta, got: {raw}")
    slug, label, without, with_, delta = (p.strip() for p in parts)
    if not slug or not label or not without or not with_ or not delta:
        raise Fail(f"--case has an empty field: {raw}")
    return slug, label, Path(without), Path(with_), delta


def shown(args, cases) -> list[str]:
    slugs = [c[0] for c in cases]
    if not args.captures:
        return slugs
    if args.captures == ["none"]:
        return []
    unknown = [s for s in args.captures if s not in slugs]
    if unknown:
        raise Fail("--captures names no --case: " + ", ".join(unknown))
    return [s for s in slugs if s in args.captures]


def build(args) -> str:
    if args.runs < 1:
        raise Fail(f"--runs must be at least 1, got {args.runs}")
    if not args.revision.strip():
        raise Fail("--revision is empty: name the commit the eval ran on")
    cases = [parse_case(c) for c in args.case]
    pairs = shown(args, cases)
    local = Path(args.local_images)
    missing = []
    for slug in pairs:
        for arm, _ in ARMS:
            for vp, _ in VIEWPORTS:
                name = f"{slug}-{arm}-{vp}.png"
                if not (local / name).is_file():
                    missing.append(str(local / name))
    if missing:
        raise Fail("missing capture(s): " + ", ".join(missing))

    audit = Path(args.audit)
    base = args.images.rstrip("/")
    lines = [
        START,
        "| Brief | Tells, without genjutsu | Tells, with genjutsu | Grader score, with minus without |",
        "|---|---|---|---|",
    ]
    for slug, label, without, with_, delta in cases:
        lines.append(f"| {label} | {count_tells(audit, without)} | {count_tells(audit, with_)} | {delta} |")
    lines += [
        "",
        "Tells are the findings of `audit.py --group tells` on the page of the first run of each arm. "
        f"Scores come from `claude plugin eval --ablation with-without --runs {args.runs}` on genjutsu "
        f"`{args.revision.strip()}`, over the suite in "
        f"[`evals/`]({args.evals_link}). The graders are ours: read this as genjutsu measured against "
        "what it set out to do, not as an independent benchmark.",
    ]
    for slug, label, *_ in cases:
        if slug not in pairs:
            continue
        lines += ["", f"#### {label}", "", "| " + " | ".join(t for _, t in ARMS) + " |", "|---|---|"]
        for vp, width in VIEWPORTS:
            cells = [
                f'<img src="{base}/{slug}-{arm}-{vp}.png" alt="{label}, {title.lower()}, {vp}" width="{width}" />'
                for arm, title in ARMS
            ]
            lines.append("| " + " | ".join(cells) + " |")
    lines.append(END)
    return "\n".join(lines) + "\n"


def write_region(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        raise Fail(f"{path} must hold exactly one {START} ... {END} region")
    head = text[: text.index(START)]
    tail = text[text.index(END) + len(END):]
    path.write_text(head + block.rstrip("\n") + tail, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case", action="append", required=True)
    ap.add_argument("--local-images", required=True, help="directory holding the captures, checked to exist")
    ap.add_argument("--images", required=True, help="base the published block uses for the captures")
    ap.add_argument("--evals-link", required=True)
    ap.add_argument("--runs", type=int, required=True, help="runs per arm the eval was given")
    ap.add_argument("--revision", required=True, help="the genjutsu commit the eval ran on")
    ap.add_argument("--captures", action="append", help="a case whose pair is shown; repeatable; none for no image")
    ap.add_argument("--audit", default=str(DEFAULT_AUDIT))
    ap.add_argument("--write", help="replace the showcase region of this file instead of printing")
    args = ap.parse_args()
    try:
        block = build(args)
        if args.write:
            write_region(Path(args.write), block)
        else:
            sys.stdout.write(block)
    except Fail as e:
        print(f"showcase-section: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
