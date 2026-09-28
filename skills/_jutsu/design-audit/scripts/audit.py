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
    python3 audit.py [root] --group tells

Exit status is 0 unless the audit itself failed to run. Findings are not errors:
this reports, the caller decides.
"""

from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable

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
HTML = {".html"}

# A check belongs to exactly one group. "hygiene" is motion and accessibility,
# judged by the check itself. "tells" are defaults a model reaches for by reflex:
# the script reports them, the validated thesis decides whether they stay.
GROUPS = ("hygiene", "tells")


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
    group: str = "hygiene"


@dataclass
class Check:
    id: str
    title: str
    severity: str        # critical | important | nice-to-have
    exts: set
    pattern: str = ""
    # A line matching `unless` is not a finding. This is where the false
    # positives die: `:hover` next to a `transition` is fine.
    unless: str | None = None
    # Inverted: the finding is that the pattern is ABSENT from the whole tree.
    absence: bool = False
    zero_means: str = ""
    absent_means: str = ""
    group: str = "hygiene"
    # What the pattern reads: "source" is the raw file line by line, "text" is the
    # displayed text only, "markup" is the class attributes only.
    surface: str = "source"
    # For checks a line regex cannot express. Receives the relevant files and the
    # project root, returns findings; `pattern` is then unused.
    fn: Callable[[list[Path], Path], list[Finding]] | None = None


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

# Each entry: (extensions, extractor, note). The extractor is a regex, whose first
# matching group (or whole match) is the value, or a function from a line to values.
INVENTORY = {
    "durations": (
        STYLE | JSX | SFC | SCRIPT,
        lambda line: collect_durations(line),  # the shorthand needs context
        "Durations in use. A designed system has three to five. Fifteen is an accident.",
    ),
    "easings": (
        STYLE | JSX | SFC | SCRIPT,
        re.compile(r"(cubic-bezier\([^)]*\)|ease-in-out|ease-out|ease-in|linear\b|steps\([^)]*\))", re.I),
        "Easings in use. Same rule: a handful, named, or it is not a system.",
    ),
    "colors": (
        STYLE | JSX | SFC | SCRIPT | HTML,
        re.compile(
            r"(?<![&\w])(#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4}))\b"
            r"|((?:rgba?|hsla?|oklch|oklab)\((?:[^()]|\([^()]*\))*\))"
            r"|(?<![\w-])(?:bg|text|border|from|via|to|ring|fill|stroke|outline|decoration|shadow|accent|caret)-"
            r"((?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky"
            r"|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3})\b"
        ),
        "Colours written as literal values or palette utilities. No verdict: each one should "
        "trace back to a token the design system or the thesis names.",
    ),
    "radii": (
        STYLE | JSX | SFC | SCRIPT | HTML,
        re.compile(
            r"border-radius\s*:\s*([^;}\"'\n]+)"
            r"|borderRadius\s*:\s*[\"'{]?\s*([\w.%-]+)"
            r"|(?<![\w-])(rounded(?:-[trblse]{1,2})?(?:-(?:none|xs|sm|md|lg|xl|2xl|3xl|4xl|full|\[[^\]\s]+\]))?)(?![\w-])"
        ),
        "Corner radii in use. No verdict: compare the spread with the radius scale the design "
        "system declares.",
    ),
    "fonts": (
        STYLE | JSX | SFC | SCRIPT | HTML,
        lambda line: collect_fonts(line),
        "Font families named in the code. No verdict: each one should be a family the thesis "
        "names, for the reason it gives.",
    ),
}
# How many file:line locations an inventory keeps per value. Enough to find the
# stray one, not so many that the report becomes the codebase.
WHERE_LIMIT = 5


# ---------------------------------------------------------------------------
# Surfaces. A tell lives in what the visitor reads, not in the source around it:
# `width: "100%"` in a style object is not a claim of perfection, `99.99% uptime`
# in a paragraph is. So "text" checks never see raw lines, only what this
# extractor returns, and it is tested on its own.
# ---------------------------------------------------------------------------

MARKUP_EXTS = JSX | SFC | HTML
TEXT_ATTRS = ("alt", "title", "aria-label", "placeholder")
CLASS_ATTRS = ("className", "class")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
             "source", "track", "wbr"}
RAW_TAGS = {"script", "style"}
_TAG_NAME = re.compile(r"[A-Za-z][\w.:-]*")
_TYPE_PARAMS = re.compile(r"\s*,|\s+extends\s")
_ATTR_VALUE = r"""\s*=\s*(?:"([^"]*)"|'([^']*)'|\{\s*(?:"([^"]*)"|'([^']*)'|`([^`$]*)`)\s*\})"""


@dataclass
class Token:
    kind: str            # "open" | "close" | "text"
    name: str            # tag name, "" for a fragment or for text
    body: str            # attribute source for "open", the raw text for "text"
    offset: int          # where `body` starts in the file
    self_closing: bool = False
    void: bool = False   # an HTML void element: it never has children or a closing tag


def _is_void(name: str, html: bool) -> bool:
    """HTML is case-insensitive, so `<IMG>` is void in an .html file. In JSX and SFC
    files a capitalised name is a component (`<Link>`, `<Input>`), never the void
    `<link>` or `<input>`: there only the exact lowercase name is void."""
    return (name.lower() if html else name) in VOID_TAGS


def _tokens(src: str, html: bool = False) -> list[Token]:
    """Tags and the text between them, for JSX, SFC and HTML (`html=True` for .html).

    Deliberately small. A `<` opens a tag only when a letter, `/` or `>` follows it, and,
    outside any element, only when no identifier sits right before it, so `Array<string>`
    and `a < b` stay code while `word<b>bold</b>` inside a paragraph stays markup. A name
    followed by `,` or ` extends ` is a type-parameter list, so the TSX generic arrow
    `<T,>(x: T) => x` stays code too. Inside a tag, braces and quotes are tracked, so
    `onClick={() => go()}` does not end the tag at the arrow. `<script>` and `<style>`
    bodies, HTML comments and an Astro frontmatter fence are skipped whole.
    """
    out: list[Token] = []
    n = len(src)
    i = 0
    level = 0
    if src.startswith("---"):
        fence = src.find("\n---", 3)
        if fence != -1:
            eol = src.find("\n", fence + 4)
            i = n if eol == -1 else eol + 1
    text_start = i

    def flush(end: int) -> None:
        if end > text_start:
            out.append(Token("text", "", src[text_start:end], text_start))

    while i < n:
        if src[i] != "<":
            i += 1
            continue
        if src.startswith("<!--", i):
            flush(i)
            close = src.find("-->", i + 4)
            i = n if close == -1 else close + 3
            text_start = i
            continue
        nxt = src[i + 1:i + 2]
        prev = src[i - 1] if i else "\n"
        closing = nxt == "/"
        after = src[i + 2:i + 3] if closing else nxt
        code_like = level == 0 and (prev.isalnum() or prev in "_$.)]")
        if not (after.isalpha() or after == ">") or code_like:
            i += 1
            continue
        j = i + (2 if closing else 1)
        m = _TAG_NAME.match(src, j)
        name = m.group(0) if m else ""
        k = m.end() if m else j
        if name and not closing and _TYPE_PARAMS.match(src, k):
            i += 1
            continue
        body_start = k
        depth, quote = 0, ""
        while k < n:
            ch = src[k]
            if quote:
                if ch == quote:
                    quote = ""
            elif ch in "\"'`":
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth = max(0, depth - 1)
            elif ch == ">" and depth == 0:
                break
            k += 1
        if k >= n:
            break
        flush(i)
        if closing:
            out.append(Token("close", name, "", i))
            level = max(0, level - 1)
        else:
            self_closing = src[k - 1] == "/"
            void = _is_void(name, html)
            out.append(Token("open", name, src[body_start:k], body_start, self_closing, void))
            if not self_closing and not void:
                level += 1
            if name.lower() in RAW_TAGS and not self_closing:
                end = re.compile(r"</\s*" + re.escape(name) + r"\s*>", re.I).search(src, k + 1)
                k = n - 1 if end is None else end.start() - 1
        i = k + 1
        text_start = i
    flush(n)
    return out


def _strip_expressions(text: str) -> str:
    """Blank `{...}` expressions out of a text chunk, keeping offsets and newlines.

    A chunk can start inside an expression that opened before the previous tag
    (`{items.map(i => <li>...</li>)}` leaves `)}` behind) or end inside one that
    closes after the next tag. Both halves are code, never copy.
    """
    chars = list(text)
    depth, quote, cut = 0, "", -1
    for idx, ch in enumerate(text):
        if depth:
            if quote:
                if ch == quote:
                    quote = ""
            elif ch in "\"'`":
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            if ch != "\n":
                chars[idx] = " "
            continue
        if ch == "{":
            depth = 1
            chars[idx] = " "
        elif ch == "}":
            cut = idx
    if cut >= 0:
        for idx in range(cut + 1):
            if chars[idx] != "\n":
                chars[idx] = " "
    return "".join(chars)


def _line_index(src: str):
    starts = [0] + [m.end() for m in re.finditer("\n", src)]
    return lambda offset: bisect.bisect_right(starts, offset)


def _attr_values(tok: Token, names: tuple[str, ...]) -> list[tuple[int, str]]:
    """(offset, value) for each literal value of the named attributes on an open tag."""
    alts = "|".join(re.escape(a) for a in names)
    pat = re.compile(r"(?<![\w:@.-])(?:" + alts + r")" + _ATTR_VALUE)
    out = []
    for m in pat.finditer(tok.body):
        for g in range(1, 6):
            if m.group(g) is not None:
                out.append((tok.offset + m.start(g), m.group(g)))
                break
    return out


def displayed_text_lines(path: Path, lines: list[str]) -> list[tuple[int, str]]:
    """(line number, text) for everything a visitor reads in a markup file.

    Text between tags, inside at least one element, with `{...}` expressions blanked
    out, plus the values of alt, title, aria-label and placeholder. Never className,
    class, style or any JS object: those are markup and code, not copy.
    """
    if path.suffix not in MARKUP_EXTS:
        return []
    src = "\n".join(lines)
    line_of = _line_index(src)
    out: list[tuple[int, str]] = []
    depth = 0
    for tok in _tokens(src, html=path.suffix in HTML):
        if tok.kind == "open":
            for off, value in _attr_values(tok, TEXT_ATTRS):
                if value.strip():
                    out.append((line_of(off), " ".join(value.split())))
            if not tok.self_closing and not tok.void:
                depth += 1
        elif tok.kind == "close":
            depth = max(0, depth - 1)
        elif depth:
            cleaned = _strip_expressions(tok.body)
            pos = tok.offset
            for seg in cleaned.split("\n"):
                text = " ".join(seg.split())
                if text:
                    out.append((line_of(pos), text))
                pos += len(seg) + 1
    return out


def markup_class_lines(path: Path, lines: list[str]) -> list[tuple[int, str]]:
    """(line number, class list) for every literal className / class attribute."""
    if path.suffix not in MARKUP_EXTS:
        return []
    src = "\n".join(lines)
    line_of = _line_index(src)
    return [(line_of(off), " ".join(value.split()))
            for tok in _tokens(src, html=path.suffix in HTML) if tok.kind == "open"
            for off, value in _attr_values(tok, CLASS_ATTRS)]


SURFACES = {"text": displayed_text_lines, "markup": markup_class_lines}


# ---------------------------------------------------------------------------
# Tells. Each is a default a model reaches for when nothing asked for it. The
# script cannot know whether the validated thesis names the pattern, so every
# tell is "nice-to-have" in the "tells" group and never counts as a problem on
# its own: the caller confronts each finding with the thesis first.
# ---------------------------------------------------------------------------

TELL = {"group": "tells", "severity": "nice-to-have"}

CHECKS += [
    Check(
        id="tell-invented-status",
        title="Invented build or release status",
        exts=MARKUP_EXTS, surface="text", **TELL,
        pattern=(r"(?i)\bv\d+\.\d+(?:\.\d+)?(?:-(?:rc|beta|alpha|pre)(?:\.\d+)?)?\b"
                 r"|\blast\s+(?:sync(?:ed)?|deploy(?:ed)?|updated?)\s+\d+\s*(?:s|secs?|m|mins?|h)\b"
                 r"|\bbuild\s+#?\d{3,}\b"),
        zero_means="No version stamp, sync time or build number in the displayed text.",
    ),
    Check(
        id="tell-locale-strip",
        title="Weather, clock or timezone strip",
        exts=MARKUP_EXTS, surface="text", **TELL,
        pattern=(r"\b\d{1,2}:\d{2}\b.{0,24}?-?\d{1,3}\s*(?:\u00b0|&deg;|&#176;)"
                 r"|-?\d{1,3}\s*(?:\u00b0|&deg;|&#176;).{0,24}?\b\d{1,2}:\d{2}\b"
                 r"|\b[A-Z]{3}\s+\d{1,2}:\d{2}\b"
                 r"|\b(?:GMT|UTC)\s?[+-]\d{1,2}\b"),
        zero_means="No clock, temperature or timezone strip in the displayed text.",
    ),
    Check(
        id="tell-numbered-eyebrow",
        title="Numbered eyebrow or tile pagination",
        exts=MARKUP_EXTS, surface="text", **TELL,
        pattern=r"^(?:0\d{1,2}\s*(?:/|\u00b7|\.|:|-)\s*[A-Za-z]|\d{1,2}\s*/\s*\d{1,2}$)",
        zero_means="No zero-padded section number and no `01 / 4` counter in the displayed text.",
    ),
    Check(
        id="tell-fake-code",
        title="Part number or section code that points to nothing",
        exts=MARKUP_EXTS, surface="text", **TELL,
        pattern=r"(?:^|[\s(\[])(?:[A-Z]{2,4}-\d{2,3}|MK[.\s-]?[IVX]{1,4})(?=$|[\s.,;:)\]])",
        zero_means="No code like SEC-01, REF-204 or MK.I in the displayed text.",
    ),
    Check(
        id="tell-generic-step",
        title="Generic step label",
        exts=MARKUP_EXTS, surface="text", **TELL,
        pattern=r"(?i)^(?:stage|step|phase|pass)\s+(?:0?\d{1,2}|one|two|three|four|five)\b",
        zero_means="No text starts with Stage, Step, Phase or Pass followed by a number.",
    ),
    Check(
        id="tell-scroll-cue",
        title="Scroll cue",
        exts=MARKUP_EXTS, surface="text", **TELL,
        pattern=r"(?i)^\W*scroll\b[^.!?]{0,24}$",
        zero_means="No short text telling the visitor to scroll.",
    ),
    Check(
        id="tell-placeholder-identity",
        title="Placeholder name or brand",
        exts=MARKUP_EXTS, surface="text", **TELL,
        pattern=r"\b(?:John|Jane)\s+(?:Doe|Smith)\b|\bAcme\b|(?i:\blorem\s+ipsum\b)",
        zero_means="No John Doe, Jane Doe, Acme or lorem ipsum in the displayed text.",
    ),
    Check(
        id="tell-round-number",
        title="Round or unsourced figure",
        exts=MARKUP_EXTS, surface="text", **TELL,
        pattern=r"\b99(?:\.9+)?%|\b100%|\b\d{1,3}(?:,000)+\+|\b\d+(?:\.\d+)?[KkMB]\+|\b10x\b",
        zero_means="No 99.9%, 100%, 10,000+ or 10x style figure in the displayed text.",
    ),
    Check(
        id="tell-filler-verb",
        title="Filler verb",
        exts=MARKUP_EXTS, surface="text", **TELL,
        pattern=(r"(?i)\b(?:elevate[sd]?|seamless(?:ly)?|unleash(?:es|ed)?|next[- ]gen(?:eration)?"
                 r"|revolutioni[sz](?:e|es|ed|ing)|supercharge[sd]?|effortless(?:ly)?|cutting[- ]edge"
                 r"|game[- ]chang(?:er|ing)|reimagine[sd]?|empower(?:s|ed|ing)?)\b"),
        zero_means="None of the listed filler verbs appears in the displayed text.",
    ),
    Check(
        id="tell-em-dash",
        title="U+2014 (em dash) in displayed text",
        exts=MARKUP_EXTS, surface="text", **TELL,
        # The character itself, and the three ways HTML spells it. Written as an
        # escape: the character is never typed literally anywhere in this repo.
        pattern=r"\u2014|&mdash;|&#8212;|&#[xX]0*2014;",
        zero_means="No U+2014 (em dash) in the displayed text, as a character or as an entity.",
    ),
    Check(
        id="tell-dot-run",
        title="Middle-dot run",
        exts=MARKUP_EXTS, surface="text", **TELL,
        pattern=r"(?:\u00b7|&middot;|&#183;)[^\u00b7&]*(?:\u00b7|&middot;|&#183;)",
        zero_means="No displayed line strings two or more middle dots together.",
    ),
    Check(
        id="tell-gradient-text",
        title="Gradient-filled text",
        # Source, not text: the tell is a class list or a CSS rule.
        exts=STYLE | JSX | SFC | HTML, **TELL,
        pattern=(r"bg-clip-text[^\"'`\n]*text-transparent|text-transparent[^\"'`\n]*bg-clip-text"
                 r"|(?:-webkit-)?background-clip\s*:\s*text"),
        zero_means="No text is clipped to a background, in classes or in CSS.",
    ),
    Check(
        id="tell-glass",
        title="Glassmorphism panel",
        # Source, not text: the tell is a class list or a CSS rule.
        exts=STYLE | JSX | SFC | HTML, **TELL,
        pattern=r"(?<![\w-])backdrop-blur|backdrop-filter\s*:\s*blur",
        zero_means="No panel blurs what sits behind it, in classes or in CSS.",
    ),
    Check(
        id="tell-glow",
        title="Glow or neon shadow",
        exts=STYLE | JSX | SFC | HTML, **TELL,
        # An outer shadow with no offset and a blur of 20px or more is a glow; a
        # focus ring (0 0 0 3px) and a soft drop shadow (0 1px 2px) are not.
        pattern=(r"(?:box|text)-shadow\s*:\s*0(?:px)?\s+0(?:px)?\s+(?:[2-9]\d|\d{3,})px"
                 r"|(?<![\w-])(?:drop-)?shadow-\[0_0_(?:[2-9]\d|\d{3,})px"),
        zero_means="No shadow with zero offset and a blur of 20px or more.",
    ),
    Check(
        id="tell-blob",
        title="Blurred background blob",
        exts=STYLE | JSX | SFC | HTML, **TELL,
        # backdrop-blur and backdrop-filter are glass, not blobs.
        pattern=r"(?<![\w-])blur-(?:2xl|3xl)\b|(?<![\w-])filter\s*:\s*blur\(\s*(?:[4-9]\d|\d{3,})px",
        zero_means="No element blurred by 40px or more (blur-2xl, blur-3xl, filter: blur).",
    ),
    Check(
        id="tell-perpetual-motion",
        title="Animation that never stops",
        exts=STYLE | JSX | SFC | HTML, **TELL,
        pattern=(r"animation[^;{}\n]*\binfinite\b|(?<![\w-])animate-(?:pulse|ping|bounce|spin)\b"
                 r"|repeat\s*:\s*Infinity"),
        zero_means="No infinite animation: no infinite iteration, no animate-pulse/ping/bounce/spin, no repeat: Infinity.",
    ),
]


# ---------------------------------------------------------------------------
# Tells a line regex cannot see: they need the element tree, or every button
# label of the project at once.
# ---------------------------------------------------------------------------

@dataclass
class Element:
    name: str
    classes: str
    attrs: str
    line: int
    children: list = field(default_factory=list)


def element_tree(src: str, html: bool = False) -> list[Element]:
    """Top-level elements of a markup file, children nested, void tags as leaves."""
    line_of = _line_index(src)
    roots: list[Element] = []
    stack: list[Element] = []
    for tok in _tokens(src, html=html):
        if tok.kind == "open":
            classes = " ".join(" ".join(v.split()) for _, v in _attr_values(tok, CLASS_ATTRS))
            el = Element(tok.name, classes, tok.body, line_of(tok.offset))
            (stack[-1].children if stack else roots).append(el)
            if not tok.self_closing and not tok.void:
                stack.append(el)
        elif tok.kind == "close":
            names = [e.name for e in stack]
            if tok.name in names:
                while stack and stack.pop().name != tok.name:
                    pass
    return roots


def _elements(nodes: list[Element]):
    for el in nodes:
        yield el
        yield from _elements(el.children)


THREE_COLUMN_CLASS = re.compile(r"(?:^|[\s:])(?:grid-cols-3|columns-3)(?=\s|$)")
REPEAT_THREE = re.compile(r"repeat\(\s*3\s*,")


def find_equal_cards(files: list[Path], base: Path) -> list[Finding]:
    """A three-column container whose three children carry the same class list."""
    out = []
    for f in files:
        lines = read(f)
        if lines is None:
            continue
        for el in _elements(element_tree("\n".join(lines), html=f.suffix in HTML)):
            if not (THREE_COLUMN_CLASS.search(el.classes) or REPEAT_THREE.search(el.attrs)):
                continue
            kids = [c for c in el.children if c.name]
            classes = {c.classes for c in kids}
            if len(kids) == 3 and len(classes) == 1 and "" not in classes:
                out.append(Finding("", "", str(f.relative_to(base)), el.line,
                                   f'3 columns, 3 children with class="{kids[0].classes}"'[:200]))
    return out


# Labels that ask for the same thing. Matched on the whole normalized label, or
# on its first words ("learn more about pricing" is still "learn more").
CTA_INTENTS = {
    "start": ["get started", "start now", "start free", "start for free", "start your free trial",
              "start free trial", "try it free", "try for free", "try free", "sign up", "sign up free",
              "create account", "create an account", "join now", "get access", "request access",
              "get early access", "join the waitlist"],
    "contact": ["contact us", "contact sales", "talk to sales", "talk to us", "book a demo", "get a demo",
                "request a demo", "schedule a demo", "book a call", "let's talk", "get in touch"],
    "learn": ["learn more", "read more", "find out more", "discover more", "see how it works", "explore"],
    "buy": ["buy now", "shop now", "order now", "add to cart", "get yours", "purchase"],
}
CTA_TAGS = {"a", "button", "link"}


def _cta_intent(label: str) -> str | None:
    norm = " ".join(re.sub(r"[^a-z0-9' ]+", " ", label.lower()).split())
    for intent, phrases in CTA_INTENTS.items():
        for p in phrases:
            if norm == p or norm.startswith(p + " "):
                return intent
    return None


def cta_labels(path: Path, lines: list[str]) -> list[tuple[int, str]]:
    """(line, label) for every button and link whose label is literal text."""
    if path.suffix not in MARKUP_EXTS:
        return []
    src = "\n".join(lines)
    line_of = _line_index(src)
    out, frames = [], []
    for tok in _tokens(src, html=path.suffix in HTML):
        if tok.kind == "open" and tok.name.lower() in CTA_TAGS and not tok.self_closing:
            frames.append((tok.name, line_of(tok.offset), []))
        elif tok.kind == "text" and frames:
            words = " ".join(_strip_expressions(tok.body).split())
            for _, _, parts in frames:
                if words:
                    parts.append(words)
        elif tok.kind == "close" and frames and frames[-1][0] == tok.name:
            _, line, parts = frames.pop()
            if parts:
                out.append((line, " ".join(parts)))
    return out


def find_duplicate_cta(files: list[Path], base: Path) -> list[Finding]:
    """One intent, several labels: "Get started", "Sign up" and "Try it free" on one site."""
    by_intent: dict[str, list[tuple[str, int, str]]] = {}
    for f in files:
        lines = read(f)
        if lines is None:
            continue
        for line, label in cta_labels(f, lines):
            intent = _cta_intent(label)
            if intent:
                by_intent.setdefault(intent, []).append((str(f.relative_to(base)), line, label))
    out = []
    for intent, hits in sorted(by_intent.items()):
        labels = sorted({label.lower() for _, _, label in hits})
        if len(labels) < 2:
            continue
        for rel, line, label in hits:
            out.append(Finding("", "", rel, line,
                               f'"{label}" ({intent}; labels for this intent: {", ".join(labels)})'[:200]))
    return out


CHECKS += [
    Check(
        id="tell-equal-cards",
        title="Three equal cards",
        exts=MARKUP_EXTS, surface="markup", fn=find_equal_cards, **TELL,
        zero_means="No three-column container holds three children with the same class list.",
    ),
    Check(
        id="tell-duplicate-cta",
        title="One intent under several button labels",
        exts=MARKUP_EXTS, surface="text", fn=find_duplicate_cta, **TELL,
        zero_means="Every call to action intent found uses a single label.",
    ),
]


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
            if p.suffix in JSX | SFC | STYLE | SCRIPT | HTML:
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
                 status="clean", scanned=len(relevant), meaning=check.zero_means,
                 group=check.group)

    if not relevant:
        res.status = "not-applicable"
        res.meaning = (
            f"No files of the relevant type ({', '.join(sorted(check.exts))}) were found. "
            "This check did not run. Do not report it as passing."
        )
        return res

    if check.fn is not None:
        for fd in check.fn(relevant, base):
            fd.check, fd.severity = check.id, check.severity
            res.findings.append(fd)
        if res.findings:
            res.status = "findings"
            res.meaning = f"{len(res.findings)} occurrence(s) across {len(relevant)} file(s) scanned."
        return res

    pat = re.compile(check.pattern)
    unless = re.compile(check.unless) if check.unless else None
    found_any = False
    extract = SURFACES.get(check.surface)

    for f in relevant:
        lines = read(f)
        if lines is None:
            continue
        pairs = extract(f, lines) if extract else list(enumerate(lines, 1))
        for n, line in pairs:
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


FONT_CSS = re.compile(r"(?:font-family|--font-[\w-]+)\s*:\s*([^;}\n]+)", re.I)
FONT_JS = re.compile(r"fontFamily\s*:\s*(?!\{)\[?\s*([^,\]}\n]+)")
FONT_NEXT = re.compile(r"import\s*\{([^}]*)\}\s*from\s*[\"']next/font/google[\"']")
FONT_GOOGLE = re.compile(r"fonts\.googleapis\.com/css2?\?[^\"'\s)]*")
FONT_UTILITY = re.compile(r"(?<![\w-])font-(sans|serif|mono|display|body|heading|\[[^\]\s]+\])(?![\w-])")


def _first_family(stack: str) -> str:
    return stack.split(",")[0].strip().strip("\"'`").strip()


def collect_fonts(line: str) -> list[str]:
    """Font families named on a line.

    The first family of a CSS or JS stack (the rest are fallbacks), every family
    imported from next/font/google or requested from Google Fonts, and Tailwind
    font utilities, which stand for whatever the theme maps them to.
    """
    out = [_first_family(m.group(1)) for m in FONT_CSS.finditer(line)]
    out += [_first_family(m.group(1)) for m in FONT_JS.finditer(line)]
    for m in FONT_NEXT.finditer(line):
        out += [n.split(" as ")[0].strip().replace("_", " ") for n in m.group(1).split(",") if n.strip()]
    for m in FONT_GOOGLE.finditer(line):
        out += [f.split(":")[0].replace("+", " ") for f in re.findall(r"family=([^&]+)", m.group(0))]
    out += ["font-" + m.group(1) for m in FONT_UTILITY.finditer(line)]
    return [f.lower() for f in out if f]


def _inventory_values(extract, line: str) -> list[str]:
    if callable(extract):
        return extract(line)
    values = []
    for m in extract.finditer(line):
        v = next((g for g in m.groups() if g is not None), m.group(0))
        values.append(" ".join(v.split()).lower())
    return values


def run_inventory(files: list[Path], base: Path) -> dict:
    out = {}
    for name, (exts, extract, note) in INVENTORY.items():
        counter: Counter = Counter()
        where: dict[str, list[str]] = {}
        relevant = [f for f in files if f.suffix in exts]
        for f in relevant:
            lines = read(f)
            if lines is None:
                continue
            rel = str(f.relative_to(base))
            for n, line in enumerate(lines, 1):
                for v in _inventory_values(extract, line):
                    counter[v] += 1
                    spots = where.setdefault(v, [])
                    spot = f"{rel}:{n}"
                    if len(spots) < WHERE_LIMIT and spot not in spots:
                        spots.append(spot)
        top = counter.most_common(20)
        out[name] = {
            "note": note,
            "scanned": len(relevant),
            "distinct": len(counter),
            "values": top,
            "where": {v: where[v] for v, _ in top},
        }
    return out


SEVERITY_ORDER = {"critical": 0, "important": 1, "nice-to-have": 2}


TELLS_HEADING = "### Tells - confront each with the thesis before counting it"


def _evidence(r: Result) -> list[str]:
    out = []
    for f in r.findings[:12]:
        loc = f"`{f.file}:{f.line}`" if f.line else f"`{f.file}`"
        out.append(f"- {loc} - `{f.text}`")
    if len(r.findings) > 12:
        out.append(f"- ... and {len(r.findings) - 12} more")
    return out


def as_markdown(base: Path, how: str, files: list[Path], results: list[Result], inv: dict) -> str:
    checked = [r for r in results if r.status != "not-applicable"]
    problems = [r for r in checked if r.status == "findings" and r.group != "tells"]
    tells = [r for r in checked if r.status == "findings" and r.group == "tells"]
    na = [r for r in results if r.status == "not-applicable"]

    out = [
        "## Static audit",
        "",
        f"Roots: {how}. {len(files)} file(s) examined.",
        "",
        f"**{len(checked)} checked, {len(problems)} with findings, "
        f"{len(tells)} tell{'' if len(tells) == 1 else 's'} to confront, {len(na)} not applicable.**",
        "",
        "Every line below is evidence, not a verdict. A check listed as not applicable did not",
        "run: report it as not checked, never as passed. This covers none of the items that need",
        "a profiler, a device or a pointer.",
        "",
    ]
    if tells:
        out += [
            f"**{len(tells)} tell check(s) fired.** They are listed apart, and none of them is a",
            "problem until it has been confronted with the validated thesis.",
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
            out += _evidence(r)
            out.append("")

    if tells:
        out.append(TELLS_HEADING)
        out.append("")
        out.append("A tell is evidence that a default slipped in, not a verdict. For each one, quote the")
        out.append("sentence of the validated thesis that names the pattern (it is then allowed by the")
        out.append("thesis), or count it as a problem. A mood word such as \"editorial\" names nothing.")
        out.append("")
        for r in sorted(tells, key=lambda x: x.check):
            out.append(f"**{r.title}** ({r.check})")
            out.append("")
            out += _evidence(r)
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
            for v, c in data["values"][:12]:
                spots = ", ".join(f"`{s}`" for s in data["where"].get(v, []))
                out.append(f"- `{v}` x{c} - {spots}")
        out.append("")

    return "\n".join(out)


def select_checks(only: list[str] | None, groups: list[str] | None) -> list[Check]:
    """The checks to run. Raises ValueError naming an id or a group that does not exist."""
    checks = CHECKS
    if only:
        wanted = set(only)
        unknown = wanted - {c.id for c in CHECKS}
        if unknown:
            raise ValueError(f"unknown check(s): {', '.join(sorted(unknown))}")
        checks = [c for c in checks if c.id in wanted]
    if groups:
        wanted = set(groups)
        unknown = wanted - set(GROUPS)
        if unknown:
            raise ValueError(f"unknown group(s): {', '.join(sorted(unknown))}")
        checks = [c for c in checks if c.group in wanted]
    return checks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".", help="project root (default: current directory)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--only", action="append", help="run only these check ids")
    ap.add_argument("--group", action="append", help="run only the checks of these groups: " + ", ".join(GROUPS))
    args = ap.parse_args()

    base = Path(args.root).resolve()
    if not base.is_dir():
        print(f"audit: {base} is not a directory", file=sys.stderr)
        return 2

    roots, how = discover_roots(base)
    files = walk(roots, base)

    try:
        checks = select_checks(args.only, args.group)
    except ValueError as e:
        print(f"audit: {e}", file=sys.stderr)
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
