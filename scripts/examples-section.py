#!/usr/bin/env python3
"""Writes the Examples gallery of the README from examples/manifest.json.

Each example is a recorded run: the literal request, how it ran, the genjutsu
version and commit, the model, first pass or selected from N, the cost, and
links to its receipt and, for a conversation, its transcript, the brief the
agent playing the client was given and the first message it sent. The gallery is
generated so that adding an example is one manifest entry plus its media and
receipt, and so that none of those facts can be dropped by hand.

The block sits between `<!-- genjutsu:examples:start -->` and
`<!-- genjutsu:examples:end -->`. Featured entries are shown in manifest order,
each with its media; an entry with `"featured": false` is a recorded run that is
not shown, listed after the gallery on one line with the reason and its receipt,
so that a run left out is still accounted for.

Usage:
    python3 scripts/examples-section.py                    # print the block
    python3 scripts/examples-section.py --write README.md  # replace the region
    python3 scripts/examples-section.py --check README.md  # exit 1 if it differs
    [--manifest examples/manifest.json]

Every path in the manifest is relative to the repository root, the parent of
the manifest's directory. It refuses, instead of publishing a broken or
dishonest block: an entry missing a required field, an unknown kind or mode,
a media, receipt, transcript, client brief or opening path that does not
exist, a conversation without its client brief and opening, a media file over
720 KB, a duplicate id, a multi-line prompt, a plugin_source that does not name
the plugin_commit, a manifest with nothing featured, and U+2014 (em dash)
anywhere in the manifest.

An entry:
    {
      "id": "pottery-firing",                 # [a-z0-9-], unique
      "title": "...",
      "skill": "cast" | "paint" | "bunshin",
      "modules": ["gsap", ...],               # the modules the run loaded
      "kind": "paint-new" | "paint-existing" | "cast" | "bunshin",
      "run": {
        "mode": "headless" | "conversation",
        "harness": "claude plugin eval, Claude Code 2.1.289",
        "plugin_version": "4.1.0",
        "plugin_commit": "09c177b",
        "plugin_source": "fix/skill-arguments on 09c177b (4.1.1 candidate)",  # optional:
                                              # a build that is not the release, said instead
                                              # of the version; must name the commit
        "model": "claude-opus-5-5",
        "date": "2026-10-04",
        "cost_usd": 1.53,                     # what genjutsu cost
        "client_cost_usd": 0.86,              # optional: the agent playing the client
        "exchanges": 8,                       # optional: messages of a conversation
        "turns": 23,
        "selected_from": 1,                   # 1 is a first pass
        "human_edits": 0
      },
      "prompt": "the literal first line of the request",
      "caption": "what the run did and did not do",
      "media": {
        "cover": {"src": "assets/examples/<id>/still.png", "alt": "..."},
        "clip":  {"src": "assets/examples/<id>/clip.webp", "alt": "..."},   # optional
        "stills": [{"src": "...", "alt": "..."}]                           # may be empty
      },
      "receipt": "examples/<id>/receipt.md",
      "transcript": "examples/<id>/transcript.md",   # required for a conversation
      "client": "examples/<id>/client.md",           # required for a conversation: the
                                              # brief the agent playing the client was given
      "opening": "examples/<id>/opening.txt",        # required for a conversation: the
                                              # first message, sent word for word
      "notes": "what else a reader should know, said plainly"
    }

A recorded run that is not featured needs less: id, title, skill, kind, run
(mode, plugin_version, plugin_commit, date, and plugin_source if any), receipt,
an optional transcript, client and opening (both, for a conversation), and the
reason it is not shown:
    {"id": "...", "featured": false, "reason": "one sentence", ...}

Stdlib only, like every script here.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

START = "<!-- genjutsu:examples:start -->"
END = "<!-- genjutsu:examples:end -->"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "examples" / "manifest.json"
DASH = "\u2014"
MAX_MEDIA_BYTES = 720 * 1000
IMG_WIDTH = 720

SKILLS = {"cast", "paint", "bunshin"}
KINDS = {"paint-new", "paint-existing", "cast", "bunshin"}
MODES = {"headless", "conversation"}
TOP_FIELDS = ("id", "title", "skill", "modules", "kind", "run", "prompt", "caption", "media", "receipt", "notes")
RUN_FIELDS = ("mode", "harness", "plugin_version", "plugin_commit", "model", "date",
              "cost_usd", "turns", "selected_from", "human_edits")
UNFEATURED_FIELDS = ("id", "title", "skill", "kind", "run", "receipt", "reason")
UNFEATURED_RUN_FIELDS = ("mode", "plugin_version", "plugin_commit", "date")
MODE_LABEL = {
    "headless": "one-shot headless run",
    "conversation": "conversation with an agent playing the client",
}


class Fail(Exception):
    pass


def find_dashes(node, where: str) -> list[str]:
    if isinstance(node, str):
        return [where] if DASH in node else []
    if isinstance(node, dict):
        return [w for k, v in node.items() for w in find_dashes(k, f"{where}.{k}") + find_dashes(v, f"{where}.{k}")]
    if isinstance(node, list):
        return [w for i, v in enumerate(node) for w in find_dashes(v, f"{where}[{i}]")]
    return []


def need_str(entry: dict, key: str, where: str) -> str:
    v = entry.get(key)
    if not isinstance(v, str) or not v.strip():
        raise Fail(f"{where}: missing or empty field '{key}'")
    return v


def need_int(entry: dict, key: str, where: str, minimum: int) -> int:
    v = entry.get(key)
    if isinstance(v, bool) or not isinstance(v, int) or v < minimum:
        raise Fail(f"{where}: '{key}' must be an integer of at least {minimum}, got {v!r}")
    return v


def check_file(root: Path, rel: str, where: str, media: bool = False) -> None:
    if rel.startswith(("/", "./")) or ".." in Path(rel).parts:
        raise Fail(f"{where}: '{rel}' must be relative to the repository root, without ./ or ..")
    p = root / rel
    if not p.is_file():
        raise Fail(f"{where}: '{rel}' does not exist")
    if media and p.stat().st_size > MAX_MEDIA_BYTES:
        raise Fail(f"{where}: '{rel}' is {p.stat().st_size} bytes, over the {MAX_MEDIA_BYTES} limit")


def check_media_item(root: Path, item, where: str) -> None:
    if not isinstance(item, dict):
        raise Fail(f"{where}: must be an object with src and alt")
    check_file(root, need_str(item, "src", where), where, media=True)
    need_str(item, "alt", where)


def need_cost(run: dict, key: str, where: str) -> None:
    cost = run[key]
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost <= 0:
        raise Fail(f"{where}: {key} must be a positive number, got {cost!r}")


def validate_run(run, where: str, fields: tuple[str, ...]) -> None:
    if not isinstance(run, dict):
        raise Fail(f"{where}: run must be an object")
    rwhere = f"{where}, run"
    for key in fields:
        if key not in run:
            raise Fail(f"{rwhere}: missing field '{key}'")
    if run["mode"] not in MODES:
        raise Fail(f"{rwhere}: mode must be one of {sorted(MODES)}, got {run['mode']!r}")
    for key in fields:
        if key in ("harness", "plugin_version", "plugin_commit", "model", "date"):
            need_str(run, key, rwhere)
    if not re.fullmatch(r"\d+\.\d+\.\d+", run["plugin_version"]):
        raise Fail(f"{rwhere}: plugin_version must look like 4.1.0, got {run['plugin_version']!r}")
    if not re.fullmatch(r"[0-9a-f]{7,40}", run["plugin_commit"]):
        raise Fail(f"{rwhere}: plugin_commit must be a commit hash, got {run['plugin_commit']!r}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", run["date"]):
        raise Fail(f"{rwhere}: date must be YYYY-MM-DD, got {run['date']!r}")
    if "plugin_source" in run:
        source = need_str(run, "plugin_source", rwhere)
        if run["plugin_commit"] not in source:
            raise Fail(f"{rwhere}: plugin_source must name the plugin_commit {run['plugin_commit']!r}")
    if "cost_usd" in fields:
        need_cost(run, "cost_usd", rwhere)
    if "client_cost_usd" in run:
        need_cost(run, "client_cost_usd", rwhere)
    if "exchanges" in run:
        need_int(run, "exchanges", rwhere, 1)
    if "turns" in fields:
        need_int(run, "turns", rwhere, 1)
        need_int(run, "selected_from", rwhere, 1)
        need_int(run, "human_edits", rwhere, 0)


def validate_transcript(root: Path, e: dict, where: str, required: bool) -> None:
    transcript = e.get("transcript")
    if required and not transcript:
        raise Fail(f"{where}: a conversation must link its transcript")
    if transcript is not None:
        if not isinstance(transcript, str) or not transcript.strip():
            raise Fail(f"{where}: transcript must be a path or an https URL")
        if not transcript.startswith("https://"):
            check_file(root, transcript, f"{where}, transcript")


def validate_client(root: Path, e: dict, where: str) -> None:
    """A conversation shows what the agent playing the client was told: its brief
    and the first message it sent. Required for every conversation, featured or not."""
    if e["run"]["mode"] != "conversation":
        for key in ("client", "opening"):
            if key in e:
                raise Fail(f"{where}: '{key}' is only for a conversation")
        return
    for key in ("client", "opening"):
        check_file(root, need_str(e, key, where), f"{where}, {key}")


def validate(entries, root: Path) -> None:
    if not isinstance(entries, list) or not entries:
        raise Fail("the manifest needs a non-empty 'examples' list")
    seen = set()
    for i, e in enumerate(entries):
        where = f"examples[{i}]"
        if not isinstance(e, dict):
            raise Fail(f"{where}: must be an object")
        featured = e.get("featured", True)
        if not isinstance(featured, bool):
            raise Fail(f"{where}: featured must be true or false, got {featured!r}")
        for key in (TOP_FIELDS if featured else UNFEATURED_FIELDS):
            if key not in e:
                raise Fail(f"{where}: missing field '{key}'")
        ex_id = need_str(e, "id", where)
        where = f"example '{ex_id}'"
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", ex_id):
            raise Fail(f"{where}: id must be lowercase letters, digits and hyphens")
        if ex_id in seen:
            raise Fail(f"{where}: duplicate id")
        seen.add(ex_id)
        for key in ("title", "receipt") + (("caption", "notes") if featured else ("reason",)):
            need_str(e, key, where)
        if e["skill"] not in SKILLS:
            raise Fail(f"{where}: skill must be one of {sorted(SKILLS)}, got {e['skill']!r}")
        if e["kind"] not in KINDS:
            raise Fail(f"{where}: kind must be one of {sorted(KINDS)}, got {e['kind']!r}")
        if not e["kind"].startswith(e["skill"]):
            raise Fail(f"{where}: kind {e['kind']!r} does not match skill {e['skill']!r}")
        validate_run(e["run"], where, RUN_FIELDS if featured else UNFEATURED_RUN_FIELDS)
        check_file(root, e["receipt"], f"{where}, receipt")
        validate_transcript(root, e, where, required=featured and e["run"]["mode"] == "conversation")
        validate_client(root, e, where)
        if not featured:
            if "\n" in e["reason"]:
                raise Fail(f"{where}: reason must be one line")
            continue

        mods = e["modules"]
        if not isinstance(mods, list) or not all(isinstance(m, str) and m.strip() for m in mods):
            raise Fail(f"{where}: modules must be a list of module names")
        prompt = need_str(e, "prompt", where)
        if "\n" in prompt or "\r" in prompt:
            raise Fail(f"{where}: prompt must be the literal first line of the request, one line")

        media = e["media"]
        if not isinstance(media, dict) or "cover" not in media:
            raise Fail(f"{where}: media needs at least a cover")
        check_media_item(root, media["cover"], f"{where}, media.cover")
        if media.get("clip") is not None:
            check_media_item(root, media["clip"], f"{where}, media.clip")
        stills = media.get("stills", [])
        if not isinstance(stills, list):
            raise Fail(f"{where}: media.stills must be a list")
        for j, st in enumerate(stills):
            check_media_item(root, st, f"{where}, media.stills[{j}]")
    if not any(e.get("featured", True) for e in entries):
        raise Fail("the manifest needs at least one featured example")


def load(manifest: Path) -> list[dict]:
    if not manifest.is_file():
        raise Fail(f"manifest not found: {manifest}")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Fail(f"{manifest} is not valid JSON: {exc}") from exc
    dashes = find_dashes(data, "manifest")
    if dashes:
        raise Fail("U+2014 (em dash) in " + ", ".join(dashes) + ": use a hyphen or rephrase")
    if not isinstance(data, dict):
        raise Fail("the manifest must be an object with an 'examples' list")
    entries = data.get("examples")
    validate(entries, manifest.resolve().parent.parent)
    return entries


def code_span(text: str) -> str:
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    fence = "`" * (longest + 1)
    pad = " " if longest or text.startswith("`") or text.endswith("`") else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def link(rel: str) -> str:
    return rel if rel.startswith("https://") else f"./{rel}"


def plugin_label(run: dict) -> str:
    if run.get("plugin_source"):
        return f"genjutsu {run['plugin_source']}"
    return f"genjutsu {run['plugin_version']} at `{run['plugin_commit']}`"


def provenance(e: dict) -> str:
    run = e["run"]
    n = run["selected_from"]
    edits = run["human_edits"]
    cost = f"${run['cost_usd']:.2f}"
    if run.get("client_cost_usd"):
        cost += f" (plus ${run['client_cost_usd']:.2f} for the agent playing the client)"
    parts = [
        f"`{e['skill']}`",
        f"{MODE_LABEL[run['mode']]} ({run['harness']})",
        plugin_label(run),
        f"`{run['model']}`",
        "first pass" if n == 1 else f"selected from {n} runs",
        cost,
    ]
    if run.get("exchanges"):
        parts.append(f"{run['exchanges']} exchange" + ("" if run["exchanges"] == 1 else "s"))
    parts += [
        f"{run['turns']} turns",
        f"{edits} human edit" + ("" if edits == 1 else "s"),
        run["date"],
    ]
    return " · ".join(parts)


def intro(entries: list[dict]) -> list[str]:
    modes = {e["run"]["mode"] for e in entries}
    lines = [
        "Recorded runs on fictional clients, captured from a build of the code each run left. Each one gives "
        "the first line of the request, how it ran, what it cost, and a receipt with the full prompt, "
        "what the run checked, and what it left unverified or got wrong."
    ]
    if "headless" in modes:
        lines.append(
            "A one-shot headless run is a single `claude plugin eval` session: the prompt answers the "
            "gates up front and nobody replies after that, so there is no conversation to publish."
        )
    if "conversation" in modes:
        lines.append(
            "A conversation is a session in which an agent plays the client and answers the gates; "
            "its full transcript, the brief that agent was given and the first message it sent "
            "are linked."
        )
    if any(e["run"].get("plugin_source") for e in entries):
        lines.append(
            "A run on a build that is not a release names the branch and commit it ran on "
            "instead of a version."
        )
    return [" ".join(lines)]


def client_links(e: dict) -> list[str]:
    if not e.get("client"):
        return []
    return [f"[Client brief]({link(e['client'])})", f"[First message]({link(e['opening'])})"]


def block_for(e: dict) -> list[str]:
    media = e["media"]
    shown = media.get("clip") or media["cover"]
    receipt = link(e["receipt"])
    img = (
        f'<a href="{html.escape(receipt)}"><img src="{html.escape(link(shown["src"]))}" '
        f'alt="{html.escape(shown["alt"])}" width="{IMG_WIDTH}" /></a>'
    )
    links = [f"[Receipt]({receipt})"]
    if e.get("transcript"):
        links.append(f"[Transcript]({link(e['transcript'])})")
    else:
        links.append("No transcript: a one-shot run has no conversation, the full prompt is in the receipt")
    links += client_links(e)
    return [
        f"### {e['title']}",
        "",
        img,
        "",
        code_span(e["prompt"]),
        "",
        e["caption"],
        "",
        e["notes"],
        "",
        f"<sub>{provenance(e)}</sub>",
        "",
        " · ".join(links),
    ]


def unfeatured_line(e: dict) -> str:
    run = e["run"]
    links = [f"[Receipt]({link(e['receipt'])})"]
    if e.get("transcript"):
        links.append(f"[Transcript]({link(e['transcript'])})")
    links += client_links(e)
    facts = f"`{e['skill']}`, {MODE_LABEL[run['mode']]}, {plugin_label(run)}, {run['date']}"
    return f"- **{e['title']}**: {facts}. {e['reason']} " + " · ".join(links)


def build(entries: list[dict]) -> str:
    shown = [e for e in entries if e.get("featured", True)]
    hidden = [e for e in entries if not e.get("featured", True)]
    lines = [START, *intro(shown)]
    for e in shown:
        lines += ["", *block_for(e)]
    if hidden:
        lines += [
            "",
            "### Recorded, not featured",
            "",
            "These runs were recorded the same way and keep their receipts, but are not shown above, "
            "for the reason given on each line.",
            "",
            *(unfeatured_line(e) for e in hidden),
        ]
    lines.append(END)
    out = "\n".join(lines) + "\n"
    if DASH in out:
        raise Fail("the generated block holds U+2014 (em dash)")
    return out


def region(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8")
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        raise Fail(f"{path} must hold exactly one {START} ... {END} region")
    head = text[: text.index(START)]
    body = text[text.index(START): text.index(END) + len(END)]
    tail = text[text.index(END) + len(END):]
    return head, body, tail


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--write", metavar="FILE", help="replace the examples region of this file")
    mode.add_argument("--check", metavar="FILE", help="exit 1 if the examples region of this file differs")
    args = ap.parse_args()
    try:
        block = build(load(Path(args.manifest)))
        if args.write:
            path = Path(args.write)
            head, _, tail = region(path)
            path.write_text(head + block.rstrip("\n") + tail, encoding="utf-8")
        elif args.check:
            _, body, _ = region(Path(args.check))
            if body != block.rstrip("\n"):
                print(f"examples-section: the examples region of {args.check} is out of date; "
                      f"run python3 scripts/examples-section.py --write {args.check}", file=sys.stderr)
                return 1
            print(f"OK   [examples]: {args.check} matches {args.manifest}")
        else:
            sys.stdout.write(block)
    except Fail as e:
        print(f"examples-section: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
