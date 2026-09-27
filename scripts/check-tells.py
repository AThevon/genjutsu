#!/usr/bin/env python3
"""Hold the tells module to the contract it was written against.

The module is markdown, so nothing fails when it drifts: a fourth field creeps
into an entry, a question turns into a recommendation, the two files grow until
the shell call that loads them together is cut to a preview, or the sentence the
evals look for gets copied somewhere else and stops proving anything. Each of
those is checked here.

Run: python3 scripts/check-tells.py [--root <repo>]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Assembled from words so that this file never holds the sentence itself: the evals
# read it as proof that the module was loaded, so it may live in one file only.
SENTINEL = " ".join(["A", "tell", "is", "a", "default", "the", "thesis", "never", "asked", "for."])
FIELDS = ["- **Marker:**", "- **Why it is a tell:**", "- **The question:**"]
FAMILIES = ["Invented information", "Decorative filler", "Reflex convergence", "Hollow copy"]
MAX_SKILL_LINES = 250
MAX_CHARS = 25_000   # per file, and for the two together: they load in one shell call
PRESCRIBES = re.compile(r"(?i)\binstead\b|\breplace (?:it |them )?with\b|\bswap (?:it |them )?for\b"
                        r"|\bswitch to\b|\bprefer\b|\bgo with\b")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    root = Path(ap.parse_args().root).resolve()
    mod = root / "skills" / "_jutsu" / "tells"
    skill, web = mod / "SKILL.md", mod / "references" / "web.md"
    errors: list[str] = []

    for p in (skill, web):
        if not p.is_file():
            print(f"FAIL: {p.relative_to(root)} is missing")
            return 1
    s_text, w_text = skill.read_text(encoding="utf-8"), web.read_text(encoding="utf-8")

    # Size. load_skill tells and load_ref tells references/web.md share one call.
    if len(s_text.splitlines()) > MAX_SKILL_LINES:
        errors.append(f"SKILL.md has {len(s_text.splitlines())} lines, max {MAX_SKILL_LINES}")
    for name, text in (("SKILL.md", s_text), ("references/web.md", w_text)):
        if len(text) >= MAX_CHARS:
            errors.append(f"{name} is {len(text)} characters, must stay under {MAX_CHARS}")
    if len(s_text) + len(w_text) >= MAX_CHARS:
        errors.append(f"SKILL.md + references/web.md = {len(s_text) + len(w_text)} characters: the "
                      f"dedicated load call must stay under {MAX_CHARS}")

    # Frontmatter.
    parts = s_text.split("---", 2)
    front, body = (parts[1], parts[2]) if len(parts) == 3 else ("", s_text)
    if not re.search(r"^name: tells$", front, re.M):
        errors.append("frontmatter: name must be tells")
    if "Internal genjutsu module" not in front:
        errors.append("frontmatter: the description must say Internal genjutsu module")
    if not re.search(r"^metadata:\n  internal: true$", front, re.M):
        errors.append("frontmatter: needs a metadata block with '  internal: true'")

    # The sentinel: early in the body, and in no other file of the plugin.
    if SENTINEL not in body[:2000]:
        errors.append("the sentinel sentence is not in the first 2000 characters of the body")
    candidates = sorted(root.glob("*.md"))
    for base in (root / "skills", root / "packaging", root / "scripts"):
        candidates += sorted(p for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    for p in candidates:
        if p != skill and SENTINEL in p.read_text(encoding="utf-8", errors="ignore"):
            errors.append(f"the sentinel sentence also appears in {p.relative_to(root)}")

    # Tells age: the catalogue carries a dated row in VERSIONS.md.
    versions = (root / "skills" / "_jutsu" / "VERSIONS.md").read_text(encoding="utf-8")
    if not re.search(r"^\| tells catalogue \(web\) \|", versions, re.M):
        errors.append("VERSIONS.md has no dated '| tells catalogue (web) |' row")

    # Platform coverage, stated rather than improvised.
    for platform in ("Compose", "SwiftUI"):
        if not re.search(rf"^- \*\*{platform}\*\* - not covered yet\.", body, re.M):
            errors.append(f"SKILL.md must declare {platform} as not covered yet")

    # web.md: the four families, three fields per entry, questions that stay questions.
    heads = re.findall(r"^## (.+)$", w_text, re.M)
    if heads != FAMILIES:
        errors.append(f"web.md families are {heads}, expected {FAMILIES}")
    entries = re.split(r"^### ", w_text, flags=re.M)[1:]
    if not entries:
        errors.append("web.md has no entries")
    for entry in entries:
        title = entry.splitlines()[0]
        fields = re.findall(r"^- \*\*[^*]+:\*\*", entry, re.M)
        if fields != FIELDS:
            errors.append(f"web.md entry '{title}' has fields {fields}, expected exactly {FIELDS}")
            continue
        question = " ".join(entry.split(FIELDS[2], 1)[1].split("\n## ", 1)[0].split())
        if not question.endswith("?"):
            errors.append(f"web.md entry '{title}': the question does not end with a question mark")
        if PRESCRIBES.search(question):
            errors.append(f"web.md entry '{title}': the question prescribes a replacement: {question}")

    # The detection list in SKILL.md names exactly the tells audit.py runs.
    sys.path.insert(0, str(root / "skills" / "_jutsu" / "design-audit" / "scripts"))
    import audit  # noqa: E402
    listed = set(re.findall(r"`(tell-[a-z-]+)`", body))
    running = {c.id for c in audit.CHECKS if c.group == "tells"}
    if listed != running:
        errors.append(f"SKILL.md lists {sorted(listed)}, audit.py runs {sorted(running)}")

    for e in errors:
        print(f"FAIL: {e}")
    if errors:
        return 1
    print(f"OK   [tells]: {len(entries)} entries in 4 families, {len(s_text) + len(w_text)} characters "
          f"loaded in one call, sentinel unique, {len(running)} checks listed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
