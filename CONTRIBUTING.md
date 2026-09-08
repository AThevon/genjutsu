# Contributing to genjutsu

This is a knowledge repository, not a code repository. Roughly 15,000 lines of markdown that an
AI reads and then acts on. A wrong sentence here does not throw an error, it becomes wrong code
in somebody else's project, quietly, at about 4000 installs a month.

So the most valuable thing you can send is not a feature. It is **"this claim is wrong, here is
the primary source"**.

## The evidence standard

This is the whole contract. Everything else on this page is logistics.

**A correction needs a primary source.** One per platform:

| Platform | Primary source |
|---|---|
| Web, browser support | [MDN browser-compat-data](https://github.com/mdn/browser-compat-data), [caniuse](https://caniuse.com), [webstatus.dev](https://webstatus.dev) |
| Web, packages | The npm registry, and the library's own release notes or API reference |
| Android, Compose | `api/current.txt` in [androidx-main](https://github.com/androidx/androidx), and developer.android.com |
| Apple, SwiftUI | developer.apple.com, including its DocC JSON for exact availability strings |
| Compose Multiplatform | The JetBrains CMP docs and the `androidx.compose.ui.uikit` source |

**These are not evidence:** a blog post, a Stack Overflow answer, your memory, or a model's
output. Several of the errors fixed in v3.4.0 came from exactly those. If the only thing backing
a claim is that an AI said it, that is the failure mode this file exists to prevent.

**What a test proves, and what it does not.** You are welcome to test rather than cite, but be
precise about what your test established. Three real examples from this repo:

- A symbol resolving in your IDE is not proof it ships. `Modifier.recomposeHighlighter()` was in
  the skill for months. It resolves fine if you have vendored the sample; it exists in no
  androidx artifact.
- Compiling is not proof of correct behaviour. `MaterialShapes` are normalized to a 0..1 box, so
  a morph path dropped into `GenericShape` compiles, runs, and renders a one-pixel shape in the
  corner.
- The worst class throws nothing at all. The Compose spring stiffness constants were shifted by
  one rung for months. Everything compiled, everything animated, everything was about 1.75 times
  stiffer than intended, and no test anywhere would have caught it.

If you cannot get to a primary source, open the issue anyway and say so. A reported suspicion
with an honest "I could not verify this" is useful. A confident wrong correction is not.

## What to send

**A wrong or stale claim.** Use the [issue form](https://github.com/AThevon/genjutsu/issues/new/choose).
It asks for the file and line, the text as it reads today, what the truth is, and the source.
A correction with a source attached is usually a same-day merge. Without one it becomes a
conversation.

**A `VERIFY-NEEDED` row.** [`skills/_jutsu/VERSIONS.md`](./skills/_jutsu/VERSIONS.md) records what
every version-sensitive claim was checked against and when. Rows whose note starts with
`VERIFY-NEEDED` are ones nobody has confirmed. Finishing one means: check it against the primary
source, update the row, update its date, and update the content if it changed. That is a complete,
self-contained contribution and it is the easiest way in.

**Owning a platform family.** The real constraint here is that one person maintains roughly 736
API symbols across six targets, and the last verification pass missed six errors of the class it
was hunting. If you work in Compose, SwiftUI or motion-heavy web and would re-derive one family's
claims once a quarter, read [`PLATFORM-CONTRACT.md`](./PLATFORM-CONTRACT.md) and say so in
[Discussions](https://github.com/AThevon/genjutsu/discussions). It is not write access and it is
not a title, it is a standing agreement to check one family and open the PR.

## What not to touch

**`skills/_jutsu/ui-ux-pro-max/`** is vendored from
[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
at v2.11.1, MIT. Hand-edits there are lost on the next sync and make the mirror undiffable. Send
those upstream. The exception is `SKILL.md` and `UPSTREAM.md` in that directory, which are ours.
See [`UPSTREAM.md`](./skills/_jutsu/ui-ux-pro-max/UPSTREAM.md).

**`skills/cast/SKILL.md` and `skills/paint/SKILL.md`** share five regions that must stay
byte-identical, marked `<!-- genjutsu:shared:<name>:start -->`. Editing one without the other
fails CI. They are duplicated rather than shared because each orchestrator ships as a
self-contained skill and these blocks bootstrap sub-skill loading before anything can be read.

**A new platform family** is not a pull request, it is a conversation. Read
[`PLATFORM-CONTRACT.md`](./PLATFORM-CONTRACT.md) first: adding one touches eight sites across two
files, four of them inside byte-identical regions, and commits somebody to keeping it accurate.

## Running the checks

All of these run in CI. Run them before opening the PR and you will not be surprised.

```bash
./scripts/check-shared-blocks.sh        # the five regions are identical in cast and paint
./scripts/check-denylist.sh             # no string that was wrong once has come back
python3 scripts/validate-skills.py      # every SKILL.md against the Agent Skills spec
python3 skills/_jutsu/ui-ux-pro-max/scripts/validate_data.py
( cd skills/_jutsu/ui-ux-pro-max/scripts && python3 -m unittest discover -s tests )
./package-for-claude-ai.sh              # the claude.ai bundle still has exactly one SKILL.md
```

`validate-skills.py` warns when a `SKILL.md` body goes over 500 lines and still exits 0. Three
files are already over it. Treat it as a nudge toward `references/`, not a gate.

If your PR is your first to this repo, GitHub holds the workflow runs until the maintainer
approves them. An empty checks tab on your first PR is that, not a broken pipeline.

## Opening a pull request

Fork, branch off `main`, one concern per branch. Any branch name is fine. PRs are squash-merged,
so the PR title becomes the commit message: write it as one.

Say what you changed and cite the source in the description. If you corrected a version-sensitive
claim, update its `VERSIONS.md` row and its date in the same PR, otherwise the next reader has no
way to know it was rechecked.

The review order is: is the source primary, does the claim match it, does CI pass, is the prose in
the register below. A PR gets closed unread if it is generated content with no source, if it
rewrites the vendored directory, or if it adds a platform family without a prior discussion.

## Security

Do not open a public issue for a vulnerability. This repo ships Python that runs in the user's
environment and shell that runs in their project, and it has taken one such report before
(v3.0.2, the `--persist` arbitrary-write vector). Use
[private vulnerability reporting](https://github.com/AThevon/genjutsu/security/advisories/new),
or contact the maintainer through [athevon.dev](https://athevon.dev).

## Register

You are writing markdown that a model reads and obeys, not documentation a human skims.

- **State the failure the rule prevents, not the rule.** "Never animate `width`" is ignorable.
  "Animating `width` forces layout on every frame, so it drops to 30fps on a mid-range Android"
  is not.
- **Concrete APIs, numbers and versions over adjectives.** "A snappy spring" is unusable.
  `spring(stiffness = Spring.StiffnessMedium, dampingRatio = 0.85f)` is a thesis.
- **Date every version claim**, in `VERSIONS.md`. A version number with no date is a claim about
  the present tense, forever. That is the mistake that caused v3.4.0.
- No emoji. No em dashes. Plain, factual, dev-readable.
