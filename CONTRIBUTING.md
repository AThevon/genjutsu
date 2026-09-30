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

**The three orchestrators share regions that must stay byte-identical**, marked
`<!-- genjutsu:shared:<name>:start -->`. `skills/cast/SKILL.md` and `skills/paint/SKILL.md` carry
seven: `scan`, `skill-base`, `load`, `preview`, `audit`, `headless` and `escalate`.
`skills/bunshin/SKILL.md` carries the first six, byte-identical to cast's, and never `escalate`:
that region is the proposal cast and paint make to switch to bunshin, and in bunshin it would
propose bunshin to itself. Editing a region in one file without the others fails CI, and so does
a region marker in a file that is not expected to carry it. They are duplicated rather than
shared because each orchestrator ships as a self-contained skill and these blocks bootstrap
sub-skill loading before anything can be read. The bundle's router,
`packaging/genjutsu-router.md`, carries its search three times, once per pipeline, between
`<!-- genjutsu:router:<pipeline>:start -->` markers: the three blocks must match line for line
except their `p=cast` / `p=paint` / `p=bunshin` line.

**The workflow templates** in `skills/_jutsu/orchestration/workflows/` are JavaScript that runs
only inside a host's workflow tool, billed per agent, so a mistake in one is found hours into a
paid run: the run bunshin comes from lost a whole fan-out to `fixes.some is not a function`,
because a placeholder string reached a script that expected an array. Every template needs a
fixture, `scripts/tests/fixtures/workflows/<name>.args.json` (further cases as
`<name>.<case>.args.json`), holding the `args` a real call passes, and must pass
`node scripts/check-workflows.mjs`: a pure `meta` literal first, no `Date.now()`, `Math.random()`
or argless `new Date()`, every `phase()` declared in `meta.phases`, a run to the end against
stubbed `agent()`, `parallel()` and `pipeline()` on each fixture, and a throw at once on empty
args. It also runs each fixture with every `agent()` answering null, the way the host answers for
a subagent that died, and fails on a crash; it fails on a thunk or a pipeline stage that throws,
on an unsatisfiable schema, and when the isolated-build block of `build.js` and `refine.js`
drifts. A template with no fixture fails the check. The stubs prove that the template runs, not
that the host still accepts it: the host contract they mirror is dated in
[`VERSIONS.md`](./skills/_jutsu/VERSIONS.md), section Orchestration.

**`skills/_jutsu/orchestration/scripts/shoot.mjs`**, the capture harness, has no dependency and one
test: `--self-test` serves a fixture build to a real headless Chrome and fails unless routes
resolve from disk, a long page is cut into the right number of segments, desktop captures are
scaled, reduced motion is emulated, overflow, console errors, uncaught exceptions and missing
files are all reported, a failing shot fails alone, and nothing outside the build root is served.
CI runs it on Node 22 with the runner's Chrome.

**A new platform family** is not a pull request, it is a conversation. Read
[`PLATFORM-CONTRACT.md`](./PLATFORM-CONTRACT.md) first: adding one touches eleven sites across the
three orchestrators, seven of them inside four byte-identical regions, and commits somebody to
keeping it accurate. bunshin does not take a new family: it steps down to paint on it until the
family has an evidence harness of its own.

## Hosts

Claude Code, claude.ai and Cowork are the supported hosts. genjutsu also installs in other agents
through `npx skills` (Codex, Cursor and others), untested and unsupported. The Hosts section of
[`PLATFORM-CONTRACT.md`](./PLATFORM-CONTRACT.md) says what a host has to provide.

**Triage rule:** a bug that does not reproduce under Claude Code is labelled `community`. It stays
open, and a fix is welcome as long as it changes nothing for the supported hosts. The bug form
asks which surface you used; for another agent, name it and the install command.

bunshin runs only on a host that can spawn subagents. On one that cannot, claude.ai included as
far as this repo knows, it steps down to paint and says why: that is its supported behaviour
there, not a bug. A bunshin that plays the clones itself in one context is the bug.

## Running the checks

All of these run in CI. Run them before opening the PR and you will not be surprised.

```bash
./scripts/test-check-version.sh && ./scripts/check-version.sh   # manifests, CHANGELOG and tag agree
./scripts/test-check-dashes.sh && ./scripts/check-dashes.sh     # no U+2014 in a tracked file
./scripts/test-shared-blocks.sh && ./scripts/check-shared-blocks.sh   # shared regions and router blocks match
./scripts/check-denylist.sh             # no string that was wrong once has come back
./scripts/test-resolver.sh              # the resolver, one fixture per install layout
python3 scripts/validate-skills.py      # every SKILL.md against the Agent Skills spec
node scripts/check-workflows.mjs --self-test && node scripts/check-workflows.mjs   # workflow templates run to the end on their fixtures
node skills/_jutsu/orchestration/scripts/shoot.mjs --self-test   # the capture harness, in headless Chrome (Node 22+)
( cd scripts && python3 -m unittest discover -s tests )
python3 skills/_jutsu/ui-ux-pro-max/scripts/validate_data.py
( cd skills/_jutsu/ui-ux-pro-max/scripts && python3 -m unittest discover -s tests )
./package-for-claude-ai.sh              # the claude.ai bundle still has exactly one SKILL.md
./scripts/test-resolver.sh --bundle dist/genjutsu.zip   # the same fixtures, on the packaged bundle
```

`validate-skills.py` warns when a `SKILL.md` body goes over 500 lines and still exits 0. Four
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
