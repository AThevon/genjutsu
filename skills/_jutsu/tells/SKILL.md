---
name: tells
description: "Internal genjutsu module - the reflexes a model falls into when nothing asked for them (invented data, decorative filler, converged layouts, hollow copy), each named by its evidence and a question back to the validated thesis. Loaded by cast and paint on web stacks, after the thesis gate."
metadata:
  internal: true
---

# Tells

A tell is a default the thesis never asked for.

That sentence is the module. The rest explains how to recognise one, how to write one down, and
what to do with it once found. Nothing here names a replacement: a replacement would only be
the next default, and genjutsu does not ship a look.

## The rule: the thesis is the only authority

A pattern is a tell when the validated thesis does not name it. Nothing else decides.

- **Named means named.** The thesis has to name the pattern itself: "the header shows the Paris
  and Tokyo clocks, because the studio works across both". A mood word unlocks nothing.
  "Editorial", "agency", "premium" or "bold" do not name a numbered eyebrow or a display serif,
  and most tells are precisely the clichés those words summon. In practice the pattern is named
  in the thesis's `Allowed patterns:` line, which cast and paint write under the thesis before the
  user validates it.
- **An explicit request goes through the thesis.** When the brief asks for something specific (a
  weather strip, a version badge, a live counter), write it into the thesis by name before you
  build it. The thesis is what allows it, not the brief. A request that never reached the thesis
  still reads as a tell at audit time, because afterwards nobody can tell the two apart.
- **An unvalidated thesis allows nothing.** When no human could validate the thesis, every tell
  counts, and the report says why.

## How an entry is written

Every entry, here and in the references, has exactly three fields. Never a fourth.

- **Marker** - what you can see: a literal string, a pattern, a structure.
- **Why it is a tell** - the model behaviour that produces it. Not a judgement of taste.
- **The question** - one question that sends you back to the thesis or to the project's own
  data. Never a replacement.

Report a tell in the same shape: the marker as found (`file:line` and the text), then your answer
to its question.

## The four families

| Family | The test |
|---|---|
| Invented information | Does this datum come from the project, or from a brief request written into the thesis? If neither, it was invented. |
| Decorative filler | Does this element carry information, or only texture? |
| Reflex convergence | Did this choice (layout, type, palette) come from the thesis, or from the model's habit? |
| Hollow copy | Does this sentence say something true of this project and of no other? |

One element can fail two tests. Report it once, under the family whose question it fails first.

## Platform coverage

- **Web** - `references/web.md`, loaded together with this file.
- **Compose** - not covered yet. There are no entries, and none are to be improvised: a tell is
  observed in real runs, never deduced.
- **SwiftUI** - not covered yet. Same rule.

On a Compose or SwiftUI stack this module is not loaded at all.

## Protocol

**When it loads.** After the thesis gate, before any visual choice is frozen. In cast that is the
LOAD step. In paint it is Phase 3, before the design-system query, so that the dataset's proposal
passes through it. It gets a shell call of its own: with `references/web.md` it is too long to
share a call with another module without the output being cut.

**Right after it loads,** read the thesis's `Allowed patterns:` line against this catalogue. When
it allows entries catalogued here, say so to the user in one line at the next gate (paint: with
the design system; cast: with the variants, or before implementing when there are none), naming
them: "This thesis allows three known reflexes: mono labels, hairline rules, a paper ground."
A validated thesis may keep a reflex. It never keeps one unnoticed.

**While writing.** Read a family's test before writing what it governs: the copy against Hollow
copy, every number and name against Invented information, the layout pass against Reflex
convergence, each ornament against Decorative filler. The cheapest tell is the one never written.

**At audit.** `audit.py --group tells` reports what it can see, and each finding is confronted with
the thesis before it counts:

1. Look for the pattern in the validated thesis's `Allowed patterns:` line.
2. Found: list the finding as **allowed by the thesis**, with that entry quoted.
3. The detection contradicts the entry's own marker (a loop that reports a real loading state, a
   modal backdrop, a matched line that is not displayed text): list it as **not this tell**, with the
   `file:line` that proves it. Never on a matter of taste.
4. Otherwise it is a problem. Fix it only on the lines this run wrote, run the check again (two
   passes at most), and count what remains with the other problems. A tell that was already in the
   project is listed for the user, never changed at audit.

The script never makes this call. It files every tell at `nice-to-have` and leaves them out of its
own problem count, because it cannot read the thesis. You can.

## What the script sees, and what it does not

`audit.py` reads the displayed text of JSX, Vue, Svelte, Astro and HTML files: the text between
tags, plus `alt`, `title`, `aria-label` and `placeholder`. It never reads class names or style
objects as text. The gradient, glass, glow, blob and perpetual-motion checks are the exceptions:
those tells are classes or CSS rules, so they read the source.
It does not read strings held in JavaScript either: copy kept in an array or an object
(`const features = [{ title: "..." }]`) and rendered through `{...}`, or kept in a `.ts` or `.js`
content file, is invisible to it. A clean text check means the markup is clean, not the page.

| Check | Family |
|---|---|
| `tell-invented-status` | Invented information |
| `tell-locale-strip` | Invented information |
| `tell-placeholder-identity` | Invented information |
| `tell-fake-code` | Invented information |
| `tell-round-number` | Invented information |
| `tell-numbered-eyebrow` | Decorative filler |
| `tell-generic-step` | Decorative filler |
| `tell-scroll-cue` | Decorative filler |
| `tell-dot-run` | Decorative filler |
| `tell-glow` | Decorative filler |
| `tell-blob` | Decorative filler |
| `tell-perpetual-motion` | Decorative filler |
| `tell-equal-cards` | Reflex convergence |
| `tell-gradient-text` | Reflex convergence |
| `tell-glass` | Reflex convergence |
| `tell-em-dash` | Reflex convergence |
| `tell-filler-verb` | Hollow copy |
| `tell-duplicate-cta` | Hollow copy |

What stays a manual read, because no pattern can judge it:

- a fake product drawn in divs: a dashboard, a terminal or a task list built from styled boxes;
- one layout family repeated from section to section;
- a headline on one side with a small paragraph floating in the opposite corner;
- the copy register drifting between sections;
- monospace spread across labels, navigation and captions, well beyond code and tabular figures;
- copy held in JavaScript data (arrays, objects, content files) and rendered through expressions:
  read it against every family.

Read the finished page once for those six, and report what you find in the same three fields.
Every other entry of `references/web.md` that has no check above is a manual read too.
