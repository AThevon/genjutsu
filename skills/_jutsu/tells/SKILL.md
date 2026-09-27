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
  and most tells are precisely the clichés those words summon.
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

**While writing.** Read a family's test before writing what it governs: the copy against Hollow
copy, every number and name against Invented information, the layout pass against Reflex
convergence, each ornament against Decorative filler. The cheapest tell is the one never written.

**At audit.** `audit.py --group tells` reports what it can see, and each finding is confronted with
the thesis before it counts:

1. Look for the sentence of the validated thesis that names the pattern.
2. Found: list the finding as **allowed by the thesis**, with that sentence quoted.
3. Not found: it is a problem, and it counts with the other problems.

The script never makes this call. It files every tell at `nice-to-have` and leaves them out of its
own problem count, because it cannot read the thesis. You can.

## What the script sees, and what it does not

`audit.py` reads the displayed text of JSX, Vue, Svelte, Astro and HTML files: the text between
tags, plus `alt`, `title`, `aria-label` and `placeholder`. It never reads class names or style
objects as text. The gradient check is the one exception, since that tell is a class or a CSS rule.
It does not read strings held in JavaScript either: copy kept in an array or an object
(`const features = [{ title: "..." }]`) and rendered through `{...}`, or kept in a `.ts` or `.js`
content file, is invisible to it. A clean text check means the markup is clean, not the page.

| Check | Family |
|---|---|
| `tell-invented-status` | Invented information |
| `tell-locale-strip` | Invented information |
| `tell-placeholder-identity` | Invented information |
| `tell-round-number` | Invented information |
| `tell-numbered-eyebrow` | Decorative filler |
| `tell-generic-step` | Decorative filler |
| `tell-scroll-cue` | Decorative filler |
| `tell-dot-run` | Decorative filler |
| `tell-equal-cards` | Reflex convergence |
| `tell-gradient-text` | Reflex convergence |
| `tell-em-dash` | Reflex convergence |
| `tell-filler-verb` | Hollow copy |
| `tell-duplicate-cta` | Hollow copy |

What stays a manual read, because no pattern can judge it:

- a fake product drawn in divs: a dashboard, a terminal or a task list built from styled boxes;
- one layout family repeated from section to section;
- a headline on one side with a small paragraph floating in the opposite corner;
- the copy register drifting between sections;
- copy held in JavaScript data (arrays, objects, content files) and rendered through expressions:
  read it against every family.

Read the finished page once for those five, and report what you find in the same three fields.
Every other entry of `references/web.md` that has no check above is a manual read too.
