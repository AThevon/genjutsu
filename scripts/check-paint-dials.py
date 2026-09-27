#!/usr/bin/env python3
"""Pin what the design dials actually do on the path paint uses.

paint calls search.py with `--design-system -f markdown` and tells the agent
that, on that path, --variance and --motion change the proposal while --density
only prints its label: the spacing scale density maps to is written by
--persist alone, which paint never passes, so paint derives spacing from the
thesis by hand. That sentence is only true of the vendored engine as it is
today. This check fails the day an ui-ux-pro-max sync makes it false, so the
paint instructions get rewritten in the same change instead of lying quietly.

Run: python3 scripts/check-paint-dials.py [path/to/search.py]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEARCH = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "skills/_jutsu/ui-ux-pro-max/scripts/search.py"
QUERY = "design studio portfolio editorial calm precise"
DIALS_HEADING = "### Design Dials"


def run(*dials: str) -> list[str]:
    done = subprocess.run(
        [sys.executable, str(SEARCH), QUERY, "--design-system", "-f", "markdown", *dials],
        capture_output=True, text=True, encoding="utf-8",
    )
    if done.returncode != 0:
        sys.exit(f"FAIL: search.py exited {done.returncode} with {' '.join(dials) or 'no dial'}:\n{done.stderr}")
    return done.stdout.splitlines()


def without_dial_labels(lines: list[str]) -> list[str]:
    """Drop the Design Dials block: the label lines any dial prints, up to its blank line."""
    out, skipping = [], False
    for line in lines:
        if line == DIALS_HEADING:
            skipping = True
            continue
        if skipping:
            skipping = line.strip() != ""
            continue
        out.append(line)
    return out


failures: list[str] = []
base = run()
if DIALS_HEADING in base:
    failures.append("no dial passed, yet the output already has a Design Dials block")

for value in ("1", "5", "9"):
    out = run("--density", value)
    if DIALS_HEADING not in out:
        failures.append(f"--density {value} no longer prints its label")
    if without_dial_labels(out) != base:
        failures.append(
            f"--density {value} now changes the markdown proposal beyond its label: "
            "paint's Phase 3 says it only labels, rewrite that paragraph"
        )

if all(without_dial_labels(run("--variance", v)) == base for v in ("1", "9")):
    failures.append("--variance no longer changes the markdown proposal: paint's Phase 3 says it does")

for value in ("1", "9"):
    extra = [l for l in without_dial_labels(run("--motion", value)) if l not in base]
    if not any(l.startswith("### Motion") for l in extra):
        failures.append(f"--motion {value} no longer attaches a motion snippet: paint's Phase 3 says it does")

if failures:
    for f in failures:
        print(f"FAIL: {f}")
    sys.exit(1)
print("OK   [dials]: variance and motion change the markdown proposal, density only labels it")
