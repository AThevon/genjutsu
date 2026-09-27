#!/usr/bin/env python3
"""Validate the eval suite under evals/ without calling the model.

`claude plugin eval` is billed per run, so a malformed case must never be the
thing a paid run discovers. This checks, offline and with the stdlib only:

- every case directory holds prompt.md, case.yaml, fixture.sh and graders/*.md;
- prompt.md frontmatter uses only the keys the eval runner accepts, and asks
  only for the read-only tools (Bash, Write and Edit are granted on the command
  line, never by a case);
- case.yaml carries schema_version "1.1", its own name, and a scaffold script
  that exists and parses as bash;
- every grader has a known type, only the keys that type takes, a regex that
  compiles, and double-quoted YAML values with valid escapes (a regex like
  "\\s" in double quotes is a YAML error the runner would only report at run
  time);
- every case invokes /genjutsu:paint explicitly and has exactly one positive
  guard grader, the one the delta reading depends on;
- no file of the suite contains U+2014 (em dash) or the tells sentinel phrase,
  which must exist in exactly one file of the repo.

Regexes are compiled with Python's `re` as a stand-in for the runner's
JavaScript engine: the suite sticks to the common subset (no lookbehind, no
named groups, flags limited to i, m, s, u).

Run: python3 scripts/check-evals.py [evals_dir]
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Cases the release gate reads. Each one is added by the task that writes it.
EXPECTED_CASES: tuple[str, ...] = ("studio-landing", "saas-landing")

# Positive guards: a run that fails its case's guard produced nothing to grade,
# and the delta reading (scripts/eval-runs.py) leaves it out of both arms.
GUARDS = ("page-has-content", "swift-screen-written")
EM_DASH = "\u2014"
# Assembled from parts so that this file never contains the sentence itself.
SENTINEL = " ".join(["A", "tell", "is", "a", "default", "the", "thesis", "never", "asked", "for."])

PROMPT_KEYS = {
    "schema_version", "name", "description", "tags", "plugins", "runs", "expected_outcome",
    "model", "max_turns", "timeout_seconds", "allowed_tools", "append_system_prompt", "env",
}
READ_ONLY_TOOLS = {
    "Read", "Glob", "Grep", "NotebookRead", "Skill", "AskUserQuestion", "Agent", "TodoWrite",
    "TaskCreate", "TaskGet", "TaskList", "TaskUpdate", "TaskStop",
}
COMMON_GRADER_KEYS = {"type", "weight", "arm"}
GRADER_KEYS = {
    "regex": {"pattern", "flags", "match", "target"},
    "tool_used": {"tool", "input_match", "min", "max"},
    "tool_order": {"before", "after"},
    "file_exists": {"path", "exists"},
    "llm": {"criteria", "focus"},
    "baseline": {"baseline_file", "criteria"},
}
TARGETS = {"last_message", "trace", "files", "mock_calls"}
ARMS = {"with-only", "both"}
DOUBLE_QUOTED_ESCAPES = {
    "0": "\0", "a": "\a", "b": "\b", "t": "\t", "n": "\n", "v": "\v", "f": "\f", "r": "\r",
    "e": "\x1b", " ": " ", '"': '"', "/": "/", "\\": "\\", "N": "\x85", "_": "\xa0",
    "L": "\u2028", "P": "\u2029",
}
HEX_ESCAPES = {"x": 2, "u": 4, "U": 8}
KEY_LINE = re.compile(r"^([A-Za-z_][\w-]*):(?:\s+(.*))?$")


class ParseError(ValueError):
    pass


def unescape_double(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c != "\\":
            out.append(c)
            i += 1
            continue
        if i + 1 >= len(s):
            raise ParseError("dangling backslash in a double-quoted value")
        e = s[i + 1]
        if e in DOUBLE_QUOTED_ESCAPES:
            out.append(DOUBLE_QUOTED_ESCAPES[e])
            i += 2
        elif e in HEX_ESCAPES:
            n = HEX_ESCAPES[e]
            digits = s[i + 2:i + 2 + n]
            if len(digits) != n or not re.fullmatch(r"[0-9A-Fa-f]+", digits):
                raise ParseError(f"bad \\{e} escape in a double-quoted value")
            out.append(chr(int(digits, 16)))
            i += 2 + n
        else:
            raise ParseError(f"invalid YAML escape \\{e} in a double-quoted value (single-quote regexes)")
    return "".join(out)


def split_flow(s: str) -> list[str]:
    parts, depth, quote, cur = [], 0, None, []
    for c in s:
        if quote:
            cur.append(c)
            if c == quote:
                quote = None
            continue
        if c in "'\"":
            quote = c
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
            continue
        cur.append(c)
    if quote:
        raise ParseError("unterminated quote in a flow collection")
    tail = "".join(cur)
    if tail.strip():
        parts.append(tail)
    return [p.strip() for p in parts]


def parse_scalar(raw: str | None):
    s = (raw or "").strip()
    if s == "":
        return None
    if s[0] == "'":
        if len(s) < 2 or s[-1] != "'":
            raise ParseError(f"unterminated single-quoted value: {s}")
        return s[1:-1].replace("''", "'")
    if s[0] == '"':
        if len(s) < 2 or s[-1] != '"':
            raise ParseError(f"unterminated double-quoted value: {s}")
        return unescape_double(s[1:-1])
    if s[0] == "[":
        if s[-1] != "]":
            raise ParseError(f"unterminated flow list: {s}")
        return [parse_scalar(p) for p in split_flow(s[1:-1])]
    if s[0] == "{":
        if s[-1] != "}":
            raise ParseError(f"unterminated flow map: {s}")
        out = {}
        for p in split_flow(s[1:-1]):
            k, sep, v = p.partition(":")
            if not sep or not k.strip():
                raise ParseError(f"flow map entry without a key: {p}")
            out[k.strip()] = parse_scalar(v)
        return out
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    if s in ("true", "false"):
        return s == "true"
    if s in ("null", "~"):
        return None
    return s


def parse_mapping(text: str) -> dict:
    """The YAML subset the suite uses: scalars, flow lists and maps, one level of block map."""
    out: dict = {}
    current = None
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indented = line[0] in " \t"
        m = KEY_LINE.match(line.strip())
        if not m:
            raise ParseError(f"line {n}: not a 'key: value' line: {line.strip()}")
        key, value = m.group(1), m.group(2)
        if indented:
            if current is None:
                raise ParseError(f"line {n}: indented key with no parent")
            out[current][key] = parse_scalar(value)
            continue
        if key in out:
            raise ParseError(f"line {n}: duplicate key {key}")
        if value is None or value.strip() == "":
            out[key] = {}
            current = key
        else:
            out[key] = parse_scalar(value)
            current = None
    return out


def split_frontmatter(text: str) -> tuple[dict, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ParseError("missing opening --- frontmatter line")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return parse_mapping("\n".join(lines[1:i])), "\n".join(lines[i + 1:])
    raise ParseError("missing closing --- frontmatter line")


def compile_js_regex(pattern: str, flags: str | None):
    flags = flags or ""
    bad = set(flags) - set("imsu")
    if bad:
        raise ParseError(f"unsupported regex flag(s): {''.join(sorted(bad))}")
    py = 0
    if "i" in flags:
        py |= re.IGNORECASE
    if "m" in flags:
        py |= re.MULTILINE
    if "s" in flags:
        py |= re.DOTALL
    if "(?<" in pattern or "(?i)" in pattern:
        raise ParseError("lookbehind, named groups and inline flags are outside the JS/Python common subset")
    try:
        return re.compile(pattern, py)
    except re.error as e:
        raise ParseError(f"regex does not compile: {e}") from e


def load_grader(path: Path) -> tuple[dict, str]:
    return split_frontmatter(path.read_text(encoding="utf-8"))


def check_grader(path: Path, errors: list[str]) -> dict | None:
    where = str(path)
    try:
        fm, body = load_grader(path)
    except (ParseError, UnicodeDecodeError) as e:
        errors.append(f"{where}: {e}")
        return None
    gtype = fm.get("type")
    if gtype not in GRADER_KEYS:
        errors.append(f"{where}: unknown grader type {gtype!r} (known: {', '.join(sorted(GRADER_KEYS))})")
        return None
    extra = set(fm) - COMMON_GRADER_KEYS - GRADER_KEYS[gtype]
    if extra:
        errors.append(f"{where}: key(s) not valid for a {gtype} grader: {', '.join(sorted(extra))}")
    if "arm" in fm and fm["arm"] not in ARMS:
        errors.append(f"{where}: arm must be one of {sorted(ARMS)}, got {fm['arm']!r}")
    if "weight" in fm and (not isinstance(fm["weight"], (int, float)) or fm["weight"] <= 0):
        errors.append(f"{where}: weight must be a positive number")
    if gtype == "regex":
        pattern = fm.get("pattern")
        if not isinstance(pattern, str) or not pattern:
            errors.append(f"{where}: regex grader needs a pattern")
        else:
            try:
                compile_js_regex(pattern, fm.get("flags"))
            except ParseError as e:
                errors.append(f"{where}: {e}")
        match = fm.get("match", "contains")
        if match not in ("contains", "not_contains") and not re.fullmatch(r"count:\d+", str(match)):
            errors.append(f"{where}: match must be contains, not_contains or count:N, got {match!r}")
        target = fm.get("target", "last_message")
        if isinstance(target, dict):
            if target.get("source") != "file" or not target.get("path") or set(target) != {"source", "path"}:
                errors.append(f"{where}: a file target is {{ source: file, path: <path> }}")
        elif target not in TARGETS:
            errors.append(f"{where}: unknown target {target!r}")
    elif gtype == "tool_used":
        if not fm.get("tool"):
            errors.append(f"{where}: tool_used grader needs a tool")
        if "input_match" in fm:
            try:
                compile_js_regex(str(fm["input_match"]), None)
            except ParseError as e:
                errors.append(f"{where}: input_match {e}")
        lo, hi = fm.get("min", 1), fm.get("max")
        if not isinstance(lo, int) or (hi is not None and not isinstance(hi, int)):
            errors.append(f"{where}: min and max must be integers")
        elif hi is not None and lo > hi:
            errors.append(f"{where}: min {lo} is greater than max {hi}")
    elif gtype == "llm":
        criteria = fm.get("criteria") or body.strip()
        if not criteria:
            errors.append(f"{where}: llm grader needs a rubric in its body")
        elif "PASS" not in criteria or "FAIL" not in criteria:
            errors.append(f"{where}: llm rubric must state concrete PASS and FAIL conditions")
        focus = fm.get("focus", "last_message")
        if isinstance(focus, dict):
            if focus.get("source") != "file" or not focus.get("path"):
                errors.append(f"{where}: a file focus is {{ source: file, path: <path> }}")
        elif focus not in TARGETS:
            errors.append(f"{where}: unknown focus {focus!r}")
    return {"name": path.stem, **fm}


def check_prompt(path: Path, errors: list[str]) -> str:
    try:
        fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    except (ParseError, UnicodeDecodeError) as e:
        errors.append(f"{path}: {e}")
        return ""
    unknown = set(fm) - PROMPT_KEYS
    if unknown:
        errors.append(f"{path}: unknown frontmatter key(s): {', '.join(sorted(unknown))}")
    mt, ts = fm.get("max_turns"), fm.get("timeout_seconds")
    if not isinstance(mt, int) or not 1 <= mt <= 200:
        errors.append(f"{path}: max_turns must be an integer from 1 to 200")
    if not isinstance(ts, int) or not 1 <= ts <= 3600:
        errors.append(f"{path}: timeout_seconds must be an integer from 1 to 3600")
    tools = fm.get("allowed_tools")
    if not isinstance(tools, list) or not tools:
        errors.append(f"{path}: allowed_tools must be a non-empty list")
    else:
        beyond = [t for t in tools if t not in READ_ONLY_TOOLS]
        if beyond:
            errors.append(
                f"{path}: allowed_tools may only list read-only tools; grant {', '.join(beyond)} "
                "with --allow-tools on the command line"
            )
    if not body.strip():
        errors.append(f"{path}: the prompt body is empty")
    return body


def check_case_yaml(path: Path, case: str, errors: list[str]) -> None:
    try:
        data = parse_mapping(path.read_text(encoding="utf-8"))
    except (ParseError, UnicodeDecodeError) as e:
        errors.append(f"{path}: {e}")
        return
    if data.get("schema_version") != "1.1":
        errors.append(f'{path}: schema_version must be the string "1.1"')
    if data.get("name") != case:
        errors.append(f"{path}: name must be {case!r}, got {data.get('name')!r}")
    context = data.get("context")
    script = context.get("scaffold_script") if isinstance(context, dict) else None
    if not script:
        errors.append(f"{path}: context.scaffold_script is missing")
        return
    target = path.parent / script
    if not target.is_file():
        errors.append(f"{path}: scaffold script {script} does not exist in the case directory")
        return
    first = target.read_text(encoding="utf-8").splitlines()[:1]
    if first != ["#!/usr/bin/env bash"]:
        errors.append(f"{target}: must start with #!/usr/bin/env bash")
    r = subprocess.run(["bash", "-n", str(target)], capture_output=True, text=True)
    if r.returncode != 0:
        errors.append(f"{target}: bash -n failed: {r.stderr.strip()}")


def case_dirs(evals_dir: Path) -> list[Path]:
    return sorted(
        p for p in evals_dir.iterdir()
        if p.is_dir() and p.name != "results" and not p.name.startswith((".", "_"))
    )


def check_suite(evals_dir: Path, expected: tuple[str, ...] = ()) -> list[str]:
    errors: list[str] = []
    if not evals_dir.is_dir():
        return [f"{evals_dir}: no eval directory"]
    cases = case_dirs(evals_dir)
    if not cases:
        errors.append(f"{evals_dir}: no case directory")
    for name in expected:
        if not (evals_dir / name).is_dir():
            errors.append(f"{evals_dir}: expected case {name} is missing")
    for case in cases:
        missing = [f for f in ("prompt.md", "case.yaml", "fixture.sh") if not (case / f).is_file()]
        for f in missing:
            errors.append(f"{case}: missing {f}")
        graders_dir = case / "graders"
        grader_files = sorted(graders_dir.glob("*.md")) if graders_dir.is_dir() else []
        if not grader_files:
            errors.append(f"{case}: no grader in graders/*.md")
        body = check_prompt(case / "prompt.md", errors) if "prompt.md" not in missing else ""
        if "case.yaml" not in missing:
            check_case_yaml(case / "case.yaml", case.name, errors)
        graders = [g for g in (check_grader(f, errors) for f in grader_files) if g]
        guards = [g for g in graders if g["name"] in GUARDS]
        if len(guards) != 1:
            errors.append(f"{case}: needs exactly one positive guard grader named one of {', '.join(GUARDS)}")
        else:
            guard = guards[0]
            target = guard.get("target")
            if (
                guard.get("type") != "regex"
                or guard.get("match", "contains") != "contains"
                or not isinstance(target, dict)
                or "arm" in guard
            ):
                errors.append(
                    f"{case}: guard {guard['name']} must be a regex, match contains, on a file target, "
                    "scored in both arms"
                )
        if "/genjutsu:paint" not in body and "prompt.md" not in missing:
            errors.append(f"{case}: the prompt must invoke /genjutsu:paint explicitly")
    for f in sorted(evals_dir.rglob("*")):
        if not f.is_file() or "results" in f.relative_to(evals_dir).parts[:1]:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if EM_DASH in text:
            errors.append(f"{f}: contains U+2014 (em dash); write it as \\u2014")
        if SENTINEL in text:
            errors.append(f"{f}: contains the tells sentinel phrase, which must live only in tells/SKILL.md")
    return errors


def main(argv: list[str]) -> int:
    evals_dir = Path(argv[1]) if len(argv) > 1 else ROOT / "evals"
    errors = check_suite(evals_dir, EXPECTED_CASES)
    if errors:
        for e in errors:
            print(f"FAIL {e}", file=sys.stderr)
        print(f"\n{len(errors)} error(s) in {evals_dir}.", file=sys.stderr)
        return 1
    print(f"OK   [evals]: {len(case_dirs(evals_dir))} case(s) valid in {evals_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
