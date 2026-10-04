# The platform contract

What a platform family has to answer to be in this repo, and to stay in it.

Three families ship today: **Web**, **Android** (Jetpack Compose, Compose Multiplatform) and
**Apple** (SwiftUI, iOS and macOS). Between them they cover six targets and roughly 736 distinct
API symbols. One person maintains all of it, and the v3.1.0 verification pass missed six errors
of the exact class it was hunting. That is the problem this document exists to bound.

It is written to be read twice: once by somebody considering owning a family, and once by
somebody proposing a new one. Both need the same answer, which is what the job actually costs.

## What a family must answer

Derived from what the three existing families have in common, not invented. The reference
implementation for each is named, because copying a working one beats reading a spec.

| # | The question | Reference implementation |
|---|---|---|
| 1 | How does SCAN detect this stack from files on disk? | the `scan` guarded region in `cast`, signals 2 to 5 |
| 2 | What is the reduced-motion API, and what does honouring it look like? | `compose-motion/SKILL.md`, the three toggles behind `ValueAnimator.areAnimatorsEnabled()` |
| 3 | Which properties must never be animated, and what happens if you do? | `motion-principles`, the BAD/GOOD tables |
| 4 | What is the idiomatic spring or easing vocabulary, with real parameter values? | `swiftui-motion/SKILL.md`, the named-preset table |
| 5 | How do gestures compose, and what conflicts? | `swiftui-motion/references/gestures-swiftui.md`, sections *Composition operators* and *GestureMask + simultaneousGesture* |
| 6 | What is the shared-element or continuity story? | `compose-motion/references/shared-transitions.md` |
| 7 | How do you measure a dropped frame on this platform, with the exact tool invocation? | `design-audit/SKILL.md`, the Compose subsection: the exact Layout Inspector menu path and the 16.67ms budget |
| 8 | What does a design token look like in this stack? | `paint` Phase 3, `Theme.kt` for Compose, `Color+App.swift` for SwiftUI |
| 9 | What is the legacy-integration answer, if the platform has one? | `cast` DISCOVER, the XIB / layout-XML bridge question |
| 10 | Where do version-sensitive claims get recorded? | A section in `skills/_jutsu/VERSIONS.md` |

Questions 1 to 9 are content. Question 10 is the one that decides whether the family is still
true in a year.

A family does not need a fixed number of `references/` files. The tree ranges from zero
(`design-audit`) to four (`gsap`). Split when the `SKILL.md` body gets long enough that most of
it is dead weight for most requests, not to hit a count.

## Mechanical constraints

`scripts/validate-skills.py` enforces: `name` and `description` present, `name` matching the
directory, the Agent Skills six-field allowlist (`name`, `description`, `license`,
`compatibility`, `metadata`, `allowed-tools` - only the first two are required, and no module in
the tree uses more than three), length limits, no duplicate names. A body over 500 lines warns
and still passes; four files are already over it. It also requires `metadata.internal` on
every module and forbids it on the three orchestrators (`cast`, `paint`, `bunshin`), and it caps
at 25,000 characters every module entry file and every reference an orchestrator prints with
`load_ref`: one shell call prints each of them whole, and past about 30,000 characters that
output stops arriving inline. Any other reference over the cap warns.

Every module under `skills/_jutsu/` carries a `metadata:` block with `internal: true`, an
unquoted YAML boolean, because the `npx skills` CLI tests it with `=== true`. It hides the modules
from `npx skills add`, so the repository route offers only `cast`, `paint` and `bunshin`.
genjutsu ships a single claude.ai bundle in which modules are `GUIDE.md` files, so they never
show as skills there; `metadata.internal` is what hides them from
`npx skills add AThevon/genjutsu`.

## The wiring: eleven sites across three files

Adding or renaming a family is not one edit. It is eleven, and seven of them sit in four regions
(`scan`, `load`, `audit`, `preview`) that `scripts/check-shared-blocks.sh` compares byte for
byte across all three orchestrators: `cast` against `paint`, and `cast` against `bunshin`. Edit
one file without the other two and CI rejects the PR.

| Site | Where | Guarded |
|---|---|---|
| Detection commands | `scan` region | yes, in all three |
| "Map the results" bullets | `scan` region | yes, in all three |
| Context-layers table (mobile / desktop / audit) | `load` region | yes, in all three |
| Stack-specific load table | `load` region | yes, in all three |
| "Advanced thesis" trigger terms | `load` region | yes, in all three |
| Stack-specific audit checklist | `audit` region | yes, in all three |
| Preview-mode default for the stack | `preview` region | yes, in all three |
| Interaction-thesis exemplars | `cast` step 4, `paint` Phase 2 | no, and they differ |
| Legacy-bridge question | `cast` DISCOVER, `paint` Phase 1 | no |
| Stack-aware token generation | `paint` Phase 3 only | n/a |
| Declared not covered, with the step down to `paint` | `bunshin` Iron Rule 12 and its "Step down" table | n/a |

The last row differs in kind. bunshin carries the four regions whole, so a new family's rows
land in it by the same edit as in cast and paint, as the guard intends, and are never used
there: its Compose and SwiftUI rows are in that state today. bunshin is web only. On any other
stack it says so at READ and steps down to paint, and a new family joins that list until it is
wired in.

**Wiring a family into bunshin is a separate job, done later, and it starts with an evidence
harness.** bunshin's review loop judges what renders: every lens and every verdict reads
captures that `skills/_jutsu/orchestration/scripts/shoot.mjs` takes of a static web build, with
no dev server, at fixed viewports, with the console errors, the overflow and the values scripted
tests measured. A family gets the same before bunshin runs on it: captures from a build without
a running dev environment, at the platform's real device sizes, scripted checks of the paths
that matter, a `--self-test` that proves the harness can fail, and a `VERSIONS.md` row for what
it rests on. Then come the isolated build recipe with the platform's own build tool, the lenses'
module loads, the `escalate` region's stack condition (cast and paint propose bunshin only on a
web stack or no project yet), and the step down removed. Without the harness, bunshin's
reviewers read code instead of renders, and its own capability table says the review loop then
loses most of its value. This is the rule `tells` already follows: Compose and SwiftUI are
declared not covered yet, rather than filled with entries nobody observed.

The `skill-base` region is the exception: it resolves paths and knows nothing about families.
It is byte-identical in all three orchestrators. Any change to it needs a fixture per install
layout in `scripts/test-resolver.sh`, and no new layout ships without its own fixture. The suite
also runs against the packaged bundle, because packaging rewrites file names inside it.

The bundle's router, `packaging/genjutsu-router.md`, knows nothing about families either. It
carries one search block per pipeline, three today (`cast`, `paint`, `bunshin`), and
`check-shared-blocks.sh` fails unless the three match line for line once their `p=` line is set
aside. A family never touches them; a new install layout touches all three, with its resolver
fixture.

The four sites outside a guarded region have no CI guard. Two of them are duplicated between
`cast` and `paint`. That is a known weakness, not a design: the audit checklist was in the same
state until v3.4.0 and had already drifted.

## Hosts

genjutsu is written against capabilities, not against a product. A host runs it when it gives the
model three things:

- **The skill's own directory, known to the model.** Claude Code substitutes
  `${CLAUDE_SKILL_DIR}` by itself. Anywhere else the model passes the directory it read the file
  from, as `GENJUTSU_SKILL_DIR` for `cast`, `paint` and `bunshin`, or `GENJUTSU_BUNDLE_DIR` for
  the router. When neither is available, the resolver falls back to bounded probes.
- **A shell**, to run the resolver and print the modules. Every shell call is assumed to start
  from nothing: no variable, function or working directory carries over.
- **File writes**, for the code, the tokens and `MASTER.md`.

Optional: a tool that renders HTML for the user. Without one, the preview gate writes a throwaway
HTML file and hands over its path, or falls back to inline.

`bunshin` needs a fourth: **a tool that spawns subagents**, directly (in Claude Code, `Agent`)
or through a multi-agent workflow script (in Claude Code, `Workflow`). With the workflow tool the
templates run as written; with the subagent tool alone they are read as the plan, and
`orchestration/scripts/brief.mjs` prints the prompts to spawn, several in one message when the
host runs them concurrently. With neither, bunshin does not run: it says so and steps down to `paint`, and `cast` and `paint` never
propose it on that host. Playing the clones in one context is not a fallback, because a review
written by the session that built the page is not an independent review. For its captures it
also wants Node 22 or later and a Chrome or Chromium binary; without them it runs, and says that
its reviewers read code instead of renders.

**What is supported.** Claude Code (plugin or `npx skills`), claude.ai and Cowork are tested by the
maintainer before a release. bunshin is the exception: its step down on claude.ai and its
behaviour on Cowork are not tested yet, and `docs/claude-ai-testing.md` step 5 has no logged
run. genjutsu also installs and runs in other agents through
`npx skills add https://genjutsu.athevon.dev -g` (Codex, Cursor and others): not tested by the
maintainer, not supported. Nothing in the skills behaves differently per agent, and nothing will.
Knowing which directories an installer writes to is infrastructure; a code path per agent is
not.

**Triage.** A bug report is reproduced under Claude Code first. One that reproduces there is a
genjutsu bug. One that does not is labelled `community`: it stays open for someone who uses that
agent, and a fix is welcome as long as it changes nothing for the supported hosts.

## Detection has to be conservative

A false positive is worse than a miss. If SCAN wrongly concludes a project is Compose, the whole
pipeline loads the wrong knowledge and writes Kotlin into a React app.

- Detect on a build file or a manifest, not on a file extension. A single `.swift` in a
  repository is not an Apple project.
- Every signal is read-only and cannot fail the block. Redirect stderr on the command itself,
  before any pipe: several existing signals end in `| head -1`, so `2>/dev/null` belongs on the
  `grep` or `find`, not at the end of the line.
- Say what happens when two families match at once. The web family already carries this in
  writing for `motion` versus `framer-motion`: read `package.json`, report which is installed,
  and if both are present say the project is mid-migration and follow whichever the file being
  edited imports.

## What owning a family costs

Read this part before volunteering. It is written to let you decline.

Ownership is **not** write access to the repository and it is not a title. GitHub cannot route
reviews to somebody without write access, so nothing is automated: it is a standing agreement
that you are the person who re-derives one family's claims, and the maintainer merges.

Per quarter, for one family:

- **Re-derive every `VERSIONS.md` row for it against the primary source.** Today that is 20 rows
  for Web, 10 for Android, and 12 for Apple and cross-platform. Update the value and the date
  even when nothing changed, because an unchanged row with a fresh date is itself the finding.
  The Orchestration section is in no family: its rows move with the host tools, Impeccable and
  Chrome, and whoever changes bunshin re-reads them.
- **Check what shipped.** One androidx release train, one Apple SDK cycle, or one quarter of
  browser releases. Browsers now ship every two weeks, so Web is the heaviest of the three.
- **Open one PR** with what moved. If nothing moved, the PR is the date bumps, and that is a
  complete contribution.

Realistically, two to four hours a quarter for Android or Apple, more for Web. If that is not
something you would actually do twice, do not sign up. A family with a lapsed owner is worse than
one with none, because the dates say somebody is watching.

To take one, say so in [Discussions](https://github.com/AThevon/genjutsu/discussions) under Ideas.

## Adding a new family

Not a pull request. Open a discussion first, and answer four things:

1. **Is a skill additive here?** If a strong model already writes idiomatic motion code for this
   platform without help, a skill adds tokens and risk and nothing else. Show the gap.
2. **Who owns it?** Eleven wiring sites and a quarterly re-derivation, with no owner, is a family
   that is wrong within a year. The answer cannot be "the maintainer".
3. **What is the primary source?** If there is no equivalent of `api/current.txt` or DocC, every
   claim is unverifiable and the family cannot meet the evidence standard.
4. **Can you measure a dropped frame on it?** Question 7 is not optional. A family whose audit
   step cannot be run is a family that ships assertions.

The cost, measured on the v2.0 expansion that added Android and Apple: four to five thousand
lines across sixteen files, plus the wiring sites, plus the ongoing symbol count. That covered
`cast` and `paint`. Covering a family in `bunshin` as well costs the evidence harness above, on
top.

## Removing a family

This is a normal outcome, not a failure. **The plugin that is right about three platforms beats
the plugin that is stale about six.**

A family is a candidate for removal when its `VERSIONS.md` dates are more than two quarters old
with no owner, or when its content has produced a correctness issue that nobody could verify.

Removal is the eleven wiring sites in reverse, the module directories deleted, its `VERSIONS.md`
section moved to a "formerly covered" note with its last-verified date, and the README's platform
line, the module pages of genjutsu.athevon.dev and the `plugin.json` keywords narrowed to match.
The CHANGELOG entry says why, plainly. Someone arriving from a search engine deserves to know the
coverage ended and when, rather than finding advice that quietly stopped being checked.
