#!/usr/bin/env python3
"""Read the results of `claude plugin eval` for the genjutsu suite.

The runner's own summary averages every run, including runs that produced an
empty page. An empty page passes every not_contains grader, so a with-arm that
crashed would look cleaner than a baseline that wrote a real page. This reads
the JSON instead and applies the rules the release is judged on.

    delta   <run.json> [--format text|markdown] [--no-gate]
            Per case: with / without score, delta, runs kept. A run whose
            positive guard failed or is missing, a run no grader scored (the
            harness failed before grading), or a run whose judge graders were
            skipped at the cost ceiling, is left out of its arm. Then the
            release gate.
    inspect <run.json> [--case NAME ...]
            Per run: modules requested, modules reported NOT LOADED, a failed
            resolution, sandbox read denials, the final "Modules loaded:" line.
            Exit 1 if any run shows a problem, 2 if a trace cannot be read.
    collect <run.json> --case NAME [--case NAME ...] --out DIR [--pick CASE:ARM:INDEX]
            Copy the workspace of the first run of each arm that passed its
            guard (from the dirs kept by --keep-temp) to DIR/<case>/<arm>/.
    tells   DIR [--format text|markdown]
            Run design-audit's tells group on DIR/<case>/<arm>/app/page.tsx and
            sum the findings per arm.

Accepts the documented camelCase result (schemaVersion 1: cases[].arms.with)
and the snake_case shape (cases[].runs / runs_without) so that a results file
of either form can be read. Stdlib only.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "skills" / "_jutsu" / "design-audit" / "scripts" / "audit.py"

# Must match GUARDS in scripts/check-evals.py.
GUARDS = ("page-has-content", "swift-screen-written")
ARMS = ("with", "without")
COPY_IGNORE = shutil.ignore_patterns("node_modules", ".next", ".git", ".turbo")

NOT_LOADED = re.compile(r"genjutsu: (?:sub-skill|reference) '([^']+)' NOT LOADED")
RESOLUTION_FAILED = "npx skills add https://genjutsu.athevon.dev -g"
DENIED = re.compile(r"Operation not permitted|Permission denied|EACCES|EPERM")
LOAD_CALL = re.compile(r"\bload_skill\s+([\w-]+)")
# A module read straight from the shell (cat, sed, head...) instead of through
# load_skill / load_ref still counts as requested: SKILL.md, GUIDE.md and any
# references/ path under a module's _jutsu directory name it.
READ_CALL = re.compile(r"/_jutsu/([\w-]+)/(?:SKILL\.md|GUIDE\.md|references/)")
MODULES_LOADED = re.compile(r"Modules loaded:[^\n]*")


class EvalError(Exception):
    pass


@dataclass
class Run:
    index: int
    score: float
    error: str | None
    skipped: bool
    trace: str
    graders: dict[str, bool] = field(default_factory=dict)
    scored: dict[str, bool] = field(default_factory=dict)

    def guard(self) -> bool | None:
        for name in GUARDS:
            if name in self.graders:
                return self.graders[name]
        return None


@dataclass
class Case:
    name: str
    arms: dict[str, list[Run]]


def _run(index: int, raw: dict) -> Run:
    graders, scored = {}, {}
    for g in raw.get("graders") or []:
        graders[g["name"]] = bool(g.get("passed"))
        with_only = g.get("withOnly", g.get("with_only", False))
        scored[g["name"]] = bool(g.get("scored", not with_only))
    return Run(
        index=index,
        score=float(raw.get("score") or 0.0),
        error=raw.get("error"),
        skipped=bool(raw.get("skippedPaidGraders", raw.get("skipped_paid_graders", False))),
        trace=raw.get("tracePath", raw.get("trace_path")) or "",
        graders=graders,
        scored=scored,
    )


def load_doc(path: Path) -> tuple[dict, list[Case]]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise EvalError(f"cannot read {path}: {e}") from e
    cases = []
    for c in doc.get("cases") or []:
        if "arms" in c:
            raw = {"with": c["arms"].get("with") or [], "without": c["arms"].get("without") or []}
        elif "runs" in c:
            raw = {"with": c.get("runs") or [], "without": c.get("runs_without") or []}
        else:
            raise EvalError(f"case {c.get('name')!r}: neither arms nor runs; unknown result format")
        cases.append(Case(c["name"], {arm: [_run(i, r) for i, r in enumerate(raw[arm])] for arm in ARMS}))
    if not cases:
        raise EvalError(f"{path}: no case in this result")
    return doc, cases


def kept(runs: list[Run]) -> list[Run]:
    # Fail closed: only a guard that passed says there is a page to grade. A run
    # with no guard entry, which includes a run no grader scored, is left out.
    return [r for r in runs if r.guard() is True and not r.skipped]


def mean(runs: list[Run]) -> float | None:
    return sum(r.score for r in runs) / len(runs) if runs else None


def arm_stats(case: Case) -> dict:
    out = {}
    for arm in ARMS:
        runs = case.arms[arm]
        k = kept(runs)
        out[arm] = {
            "mean": mean(k),
            "kept": len(k),
            "total": len(runs),
            "guard_failed": sum(1 for r in runs if r.guard() is False),
            "harness_failed": sum(1 for r in runs if not r.graders),
            "skipped": sum(1 for r in runs if r.skipped),
            "errors": sum(1 for r in runs if r.error),
        }
    w, wo = out["with"]["mean"], out["without"]["mean"]
    out["delta"] = None if w is None or wo is None or not case.arms["without"] else w - wo
    return out


def indicators(case: Case) -> dict[str, tuple[int, int]]:
    runs = kept(case.arms["with"])
    names = sorted({n for r in runs for n, s in r.scored.items() if not s})
    return {n: (sum(1 for r in runs if r.graders.get(n)), len(runs)) for n in names}


def all_pass(case: Case, grader: str) -> tuple[bool, str]:
    runs = kept(case.arms["with"])
    if not runs:
        return False, f"{grader}: no with-arm run left to judge"
    ok = sum(1 for r in runs if r.graders.get(grader))
    return ok == len(runs), f"{grader} {ok}/{len(runs)}"


def delta_positive(case: Case) -> tuple[bool, str]:
    d = arm_stats(case)["delta"]
    if d is None:
        return False, "no delta (an arm has no run left after exclusions)"
    return d > 0, f"delta {d:+.2f}"


# The release gate of spec section 4.5, one rule list per case, plus the
# acceptance of section 2.6 on studio-landing: tells requested and read on web.
GATES = {
    "studio-landing": [delta_positive, lambda c: all_pass(c, "tells-requested"),
                       lambda c: all_pass(c, "tells-reported-loaded")],
    "saas-landing": [delta_positive],
    "thesis-allows": [lambda c: all_pass(c, "keeps-both-cities"), lambda c: all_pass(c, "keeps-time-bar")],
    "swiftui-skip": [lambda c: all_pass(c, "tells-never-requested"), lambda c: all_pass(c, "tells-never-read")],
}


def gate(cases: list[Case]) -> tuple[bool, list[str]]:
    by_name = {c.name: c for c in cases}
    ok, lines = True, []
    for name, rules in GATES.items():
        if name not in by_name:
            ok = False
            lines.append(f"FAIL {name}: missing from the result")
            continue
        for rule in rules:
            passed, why = rule(by_name[name])
            ok &= passed
            lines.append(f"{'PASS' if passed else 'FAIL'} {name}: {why}")
    return ok, lines


def fmt(x: float | None, signed: bool = False) -> str:
    if x is None:
        return "n/a"
    return f"{x:+.2f}" if signed else f"{x:.2f}"


def cmd_delta(args) -> int:
    doc, cases = load_doc(Path(args.json))
    partial = doc.get("partial")
    rows = []
    for c in cases:
        s = arm_stats(c)
        ind = ", ".join(f"{n} {a}/{b}" for n, (a, b) in indicators(c).items()) or "-"
        rows.append((c.name, fmt(s["with"]["mean"]), fmt(s["without"]["mean"]), fmt(s["delta"], True),
                     f"{s['with']['kept']}/{s['with']['total']}", f"{s['without']['kept']}/{s['without']['total']}", ind))
    head = ("case", "with", "without", "delta", "kept with", "kept without", "with-only indicators")
    if args.format == "markdown":
        print("| " + " | ".join(head) + " |")
        print("|" + "---|" * len(head))
        for r in rows:
            print("| " + " | ".join(r) + " |")
    else:
        widths = [max(len(str(x)) for x in col) for col in zip(head, *rows)]
        for r in (head, *rows):
            print("  ".join(str(x).ljust(w) for x, w in zip(r, widths)).rstrip())
    print()
    print("Runs left out: a failed or missing positive guard (nothing to grade), a run no grader scored (harness failure), or judge graders skipped at the cost ceiling.")
    if partial:
        print(f"WARNING: partial result ({doc.get('partialReason') or doc.get('partial_reason')}); do not publish these numbers.")
    if args.no_gate:
        return 0
    ok, lines = gate(cases)
    print()
    print("Release gate (spec 4.5):")
    for line in lines:
        print(f"  {line}")
    print(f"RELEASE GATE: {'PASS' if ok and not partial else 'FAIL'}")
    return 0 if ok and not partial else 1


def iter_blocks(obj):
    """Yield tool_use, tool_result and text blocks, without descending into them."""
    if isinstance(obj, dict):
        if obj.get("type") in ("tool_use", "tool_result", "text"):
            yield obj
            return
        for v in obj.values():
            yield from iter_blocks(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_blocks(v)


def result_text(block: dict) -> str:
    content = block.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict))
    return ""


def read_trace(path: str) -> dict:
    p = Path(path)
    if not path or not p.is_file():
        raise EvalError(f"trace not found: {path or '(empty tracePath)'}")
    names, commands, outputs, finals = {}, [], [], []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = entry.get("type") if isinstance(entry, dict) else None
        if isinstance(entry, dict) and isinstance(entry.get("message"), dict):
            role = entry["message"].get("role", role)
        for b in iter_blocks(entry):
            if b["type"] == "tool_use":
                names[b.get("id")] = b.get("name")
                if b.get("name") == "Bash":
                    commands.append(str((b.get("input") or {}).get("command", "")))
            elif b["type"] == "tool_result":
                outputs.append((b.get("tool_use_id"), result_text(b)))
            elif b["type"] == "text" and role == "assistant":
                finals.append(b.get("text", ""))
    if not names:
        raise EvalError(f"no tool call recognised in {path}; read it by hand")
    shell_out = [text for tid, text in outputs if names.get(tid) == "Bash"]
    read_out = [text for tid, text in outputs if names.get(tid) in ("Bash", "Read")]
    loaded_line = ""
    for text in finals:
        for m in MODULES_LOADED.finditer(text):
            loaded_line = m.group(0)
    return {
        "requested": sorted({m for c in commands for m in LOAD_CALL.findall(c)}
                            | {m for c in commands for m in READ_CALL.findall(c)}),
        "not_loaded": sorted({m for t in shell_out for m in NOT_LOADED.findall(t)}),
        "resolution_failed": any(RESOLUTION_FAILED in t for t in shell_out),
        "denied": sum(1 for t in read_out if DENIED.search(t)),
        "modules_loaded": loaded_line,
    }


def selected(cases: list[Case], globs: list[str] | None) -> list[Case]:
    if not globs:
        return cases
    return [c for c in cases if any(fnmatch.fnmatch(c.name, g) for g in globs)]


def cmd_inspect(args) -> int:
    _, cases = load_doc(Path(args.json))
    status = 0
    for c in selected(cases, args.case):
        for arm in ARMS:
            for r in c.arms[arm]:
                label = f"{c.name} [{arm}] run {r.index + 1}"
                try:
                    t = read_trace(r.trace)
                except EvalError as e:
                    print(f"{label}: {e}")
                    status = max(status, 2)
                    continue
                problems = []
                if t["resolution_failed"]:
                    problems.append("module directory NOT resolved")
                if t["not_loaded"]:
                    problems.append(f"NOT LOADED: {', '.join(t['not_loaded'])}")
                if t["denied"]:
                    problems.append(f"{t['denied']} read(s) denied by the sandbox")
                if r.error:
                    problems.append(f"run error: {r.error}")
                print(f"{label}: score {r.score:.2f}")
                print(f"  requested: {', '.join(t['requested']) or 'none'}")
                print(f"  final report: {t['modules_loaded'] or 'no Modules loaded line'}")
                print(f"  problems: {'; '.join(problems) or 'none'}")
                if problems and arm == "with":
                    status = max(status, 1)
    return status


def run_root(trace: str) -> Path:
    p = Path(trace)
    if p.name != "trace.jsonl" or p.parent.name != "out":
        raise EvalError(f"unexpected trace path {trace}: expected <root>/out/trace.jsonl")
    return p.parent.parent


def workspace_of(trace: str) -> Path:
    root = run_root(trace)
    if not root.is_dir():
        raise EvalError(f"{root} is gone: the kept dirs live under /tmp, collect them before they are cleaned")
    direct = root / "home" / "cwd"
    if direct.is_dir():
        return direct
    # --keep-temp seals home/ and tmp/ into one extra directory (mode 000) and
    # leaves the root read-only. The harness itself says how to open them:
    # chmod 700 on the root and on the sealed directory.
    os.chmod(root, 0o700)
    extra = [e for e in os.listdir(root) if e not in ("config", "out")]
    if len(extra) != 1:
        raise EvalError(f"{root}: expected config/, out/ and one sealed directory, found {sorted(os.listdir(root))}")
    sealed = root / extra[0]
    os.chmod(sealed, 0o700)
    ws = sealed / "home" / "cwd"
    if not ws.is_dir():
        raise EvalError(f"{sealed}: no home/cwd inside")
    return ws


def cmd_collect(args) -> int:
    _, cases = load_doc(Path(args.json))
    picks = {}
    for p in args.pick or []:
        try:
            case, arm, index = p.split(":")
            picks[(case, arm)] = int(index)
        except ValueError:
            raise EvalError(f"--pick takes CASE:ARM:INDEX with a 0-based index, got {p!r}")
    out = Path(args.out)
    manifest = []
    for c in selected(cases, args.case):
        for arm in ARMS:
            runs = c.arms[arm]
            if not runs:
                continue
            if (c.name, arm) in picks:
                run = runs[picks[(c.name, arm)]]
            else:
                run = next((r for r in runs if r.graders and r.guard() is not False), None)
                if run is None:
                    print(f"{c.name} [{arm}]: every run failed its guard, nothing to show")
                    continue
            dest = out / c.name / arm
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(workspace_of(run.trace), dest, ignore=COPY_IGNORE)
            manifest.append({"case": c.name, "arm": arm, "runIndex": run.index, "score": run.score,
                             "guardPassed": run.guard(), "tracePath": run.trace})
            if (c.name, arm) in picks:
                note = " (picked)"
            elif run.index:
                note = " (earlier runs failed the guard)"
            else:
                note = ""
            print(f"{c.name} [{arm}]: run {run.index + 1}{note} -> {dest}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return 0


def count_tells(page: Path) -> tuple[int, dict[str, int]]:
    with tempfile.TemporaryDirectory() as tmp:
        app = Path(tmp) / "app"
        app.mkdir()
        shutil.copy(page, app / "page.tsx")
        r = subprocess.run([sys.executable, str(AUDIT), tmp, "--json", "--group", "tells"],
                           capture_output=True, text=True)
    if r.returncode != 0:
        raise EvalError(f"audit.py failed on {page}: {r.stderr.strip()}")
    per_check = {}
    for res in json.loads(r.stdout)["results"]:
        if res.get("group") == "tells" and res.get("findings"):
            per_check[res["check"]] = len(res["findings"])
    return sum(per_check.values()), per_check


def cmd_tells(args) -> int:
    base = Path(args.dir)
    pages = sorted(base.glob("*/*/app/page.tsx"))
    if not pages:
        raise EvalError(f"no <case>/<arm>/app/page.tsx under {base}")
    rows = []
    for page in pages:
        arm_dir = page.parent.parent
        total, per_check = count_tells(page)
        detail = ", ".join(f"{k} {v}" for k, v in sorted(per_check.items())) or "-"
        rows.append((arm_dir.parent.name, arm_dir.name, str(total), detail))
    head = ("case", "arm", "tells", "by check")
    if args.format == "markdown":
        print("| " + " | ".join(head) + " |")
        print("|" + "---|" * len(head))
        for r in rows:
            print("| " + " | ".join(r) + " |")
    else:
        for r in (head, *rows):
            print("  ".join(r))
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("delta")
    d.add_argument("json")
    d.add_argument("--format", choices=("text", "markdown"), default="text")
    d.add_argument("--no-gate", action="store_true", help="print the table only (a suite that is not genjutsu's)")
    i = sub.add_parser("inspect")
    i.add_argument("json")
    i.add_argument("--case", action="append")
    c = sub.add_parser("collect")
    c.add_argument("json")
    c.add_argument("--case", action="append", required=True)
    c.add_argument("--out", required=True)
    c.add_argument("--pick", action="append")
    t = sub.add_parser("tells")
    t.add_argument("dir")
    t.add_argument("--format", choices=("text", "markdown"), default="text")
    return ap


COMMANDS = {"delta": cmd_delta, "inspect": cmd_inspect, "collect": cmd_collect, "tells": cmd_tells}


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv[1:])
    try:
        return COMMANDS[args.cmd](args)
    except EvalError as e:
        print(f"eval-runs: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
