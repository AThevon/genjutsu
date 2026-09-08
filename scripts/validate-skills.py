#!/usr/bin/env python3
"""Validate every SKILL.md against the Agent Skills spec.

genjutsu ships to Claude Code, to claude.ai and to Cowork, and the same tree is
readable by every runtime that implements the open Agent Skills spec. The spec
allows exactly six frontmatter fields, and the claude.ai upload path rejects a
seventh with a hard error rather than ignoring it. This check keeps the tree
inside that intersection, and catches the mechanical mistakes the spec makes
easy to commit: a `name` that no longer matches its directory after a rename, a
description too long to be indexed, a body past the recommended budget.

Run: python3 scripts/validate-skills.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

# https://agentskills.io/specification
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
REQUIRED = {"name", "description"}

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_COMPATIBILITY = 500
# Spec guidance, not a hard limit: keep the body under 500 lines / 5k tokens.
SOFT_MAX_BODY_LINES = 500

errors: list[str] = []
warnings: list[str] = []


def split_frontmatter(path: Path) -> tuple[list[str], list[str]] | None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None
    return lines[1:end], lines[end + 1 :]


def parse_keys(front: list[str]) -> dict[str, str]:
    """Top-level `key: value` pairs. Nested mappings keep only their parent key."""
    out: dict[str, str] = {}
    for line in front:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1] in (" ", "\t", "-"):
            continue  # part of the previous key's value
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


def check(path: Path) -> None:
    rel = path.relative_to(ROOT)
    parts = split_frontmatter(path)
    if parts is None:
        errors.append(f"{rel}: no YAML frontmatter delimited by ---")
        return
    front, body = parts
    keys = parse_keys(front)

    for missing in sorted(REQUIRED - keys.keys()):
        errors.append(f"{rel}: missing required frontmatter field '{missing}'")

    for extra in sorted(keys.keys() - ALLOWED):
        errors.append(
            f"{rel}: '{extra}' is not in the Agent Skills spec "
            f"({', '.join(sorted(ALLOWED))}). The claude.ai upload path rejects it with a hard error."
        )

    name = keys.get("name", "").strip("\"'")
    if name:
        expected = path.parent.name
        if name != expected:
            errors.append(f"{rel}: name '{name}' must match its directory '{expected}'")
        if len(name) > MAX_NAME:
            errors.append(f"{rel}: name is {len(name)} chars, max is {MAX_NAME}")
        if not NAME_RE.match(name):
            errors.append(
                f"{rel}: name '{name}' must be lowercase letters, digits and single hyphens, "
                "with no leading, trailing or doubled hyphen"
            )

    description = keys.get("description", "").strip("\"'")
    if description and len(description) > MAX_DESCRIPTION:
        errors.append(f"{rel}: description is {len(description)} chars, max is {MAX_DESCRIPTION}")
    if description and len(description) < 40:
        warnings.append(
            f"{rel}: description is only {len(description)} chars. It is the only thing a router "
            "sees when deciding whether to load this skill."
        )

    compatibility = keys.get("compatibility", "").strip("\"'")
    if compatibility and len(compatibility) > MAX_COMPATIBILITY:
        errors.append(f"{rel}: compatibility is {len(compatibility)} chars, max is {MAX_COMPATIBILITY}")

    if len(body) > SOFT_MAX_BODY_LINES:
        warnings.append(
            f"{rel}: body is {len(body)} lines, over the {SOFT_MAX_BODY_LINES}-line guidance. "
            "Move detail into references/ so it loads on demand."
        )


def main() -> int:
    files = sorted(SKILLS.rglob("SKILL.md"))
    if not files:
        print(f"FAIL: no SKILL.md found under {SKILLS}", file=sys.stderr)
        return 1

    for f in files:
        check(f)

    names: dict[str, Path] = {}
    for f in files:
        parts = split_frontmatter(f)
        if parts is None:
            continue
        name = parse_keys(parts[0]).get("name", "").strip("\"'")
        if not name:
            continue
        if name in names:
            errors.append(f"{f.relative_to(ROOT)}: duplicate skill name '{name}', also in {names[name].relative_to(ROOT)}")
        names[name] = f

    for w in warnings:
        print(f"WARN {w}")
    for e in errors:
        print(f"FAIL {e}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} error(s) across {len(files)} skills.", file=sys.stderr)
        return 1

    print(f"OK: {len(files)} skills valid against the Agent Skills spec ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
