#!/usr/bin/env python3
"""Validate every SKILL.md against the Agent Skills spec.

genjutsu ships to Claude Code, to claude.ai and to Cowork, and the same tree is
readable by every runtime that implements the open Agent Skills spec. The spec
allows exactly six frontmatter fields, and the claude.ai upload path rejects a
seventh with a hard error rather than ignoring it. This check keeps the tree
inside that intersection, and catches the mechanical mistakes the spec makes
easy to commit: a `name` that no longer matches its directory after a rename, a
description too long to be indexed, a body past the recommended budget.

Two genjutsu rules sit on top of the spec. Every module under skills/_jutsu/
carries `metadata:` with `internal: true`, so `npx skills add` does not offer it
as a skill of its own; cast and paint never carry it. And every file that one
shell call prints in full stays under 25,000 characters: past about 30,000 the
output of a shell call no longer arrives inline, and the model sees a preview.

Run: python3 scripts/validate-skills.py [--root <repo root>]
"""

from __future__ import annotations

import argparse
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
# One shell call prints a module entry file, or a reference named by load_ref,
# in full. Past about 30,000 characters the output no longer arrives inline.
MAX_LOADED_CHARS = 25_000
LOAD_REF_RE = re.compile(r"\bload_ref\s+([a-z0-9-]+)\s+([^\s`|]+)")

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


def parse_block(front: list[str], parent: str) -> dict[str, str] | None:
    """The indented `key: value` lines under a top-level `parent:` with no inline value.

    None when the parent key is absent or carries an inline value (flow style):
    the npx CLI reads the block form, so that is the form this repo writes.
    """
    out: dict[str, str] | None = None
    for line in front:
        if out is None:
            if line.rstrip() == f"{parent}:":
                out = {}
            continue
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1] not in (" ", "\t"):
            break  # the next top-level key ends the block
        key, sep, value = line.strip().partition(":")
        if sep:
            out[key.strip()] = value.strip()
    return out


def is_module(path: Path) -> bool:
    return path.parent.parent.name == "_jutsu"


def check_internal(path: Path, rel: Path, front: list[str]) -> None:
    metadata = parse_block(front, "metadata") or {}
    if is_module(path):
        if metadata.get("internal") != "true":
            errors.append(
                f"{rel}: a module must carry a `metadata:` block with `  internal: true` "
                "(unquoted), or `npx skills add` offers it as a skill of its own"
            )
    elif "internal" in metadata:
        errors.append(f"{rel}: an orchestrator must not carry metadata.internal, or npx hides it")


def check(path: Path) -> None:
    rel = path.relative_to(ROOT)
    parts = split_frontmatter(path)
    if parts is None:
        errors.append(f"{rel}: no YAML frontmatter delimited by ---")
        return
    front, body = parts
    keys = parse_keys(front)
    check_internal(path, rel, front)

    if is_module(path):
        size = len(path.read_text(encoding="utf-8"))
        if size > MAX_LOADED_CHARS:
            errors.append(
                f"{rel}: {size} characters, over the {MAX_LOADED_CHARS} a single shell call can "
                "print inline. Move detail into references/."
            )

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


def check_references() -> None:
    """References over the cap: an error when load_ref prints them, a warning otherwise."""
    loaded: set[Path] = set()
    for orchestrator in ("cast", "paint"):
        entry = SKILLS / orchestrator / "SKILL.md"
        if entry.is_file():
            for module, rel_path in LOAD_REF_RE.findall(entry.read_text(encoding="utf-8")):
                loaded.add(SKILLS / "_jutsu" / module / rel_path)
    for ref in sorted(loaded):
        if not ref.is_file():
            errors.append(f"{ref.relative_to(ROOT)}: named by load_ref in an orchestrator, but missing")
    for ref in sorted(SKILLS.glob("_jutsu/*/references/*.md")):
        size = len(ref.read_text(encoding="utf-8"))
        if size <= MAX_LOADED_CHARS:
            continue
        message = (
            f"{ref.relative_to(ROOT)}: {size} characters, over the {MAX_LOADED_CHARS} a single "
            "shell call can print inline"
        )
        if ref in loaded:
            errors.append(f"{message}. load_ref prints it in one call: split it.")
        else:
            warnings.append(f"{message}. Read it with a file-reading tool, or split it.")


def main(argv: list[str] | None = None) -> int:
    global ROOT, SKILLS
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    args = parser.parse_args(argv)
    ROOT = args.root.resolve()
    SKILLS = ROOT / "skills"

    files = sorted(SKILLS.rglob("SKILL.md"))
    if not files:
        print(f"FAIL: no SKILL.md found under {SKILLS}", file=sys.stderr)
        return 1

    for f in files:
        check(f)
    check_references()

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
