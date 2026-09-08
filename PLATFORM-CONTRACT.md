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
and still passes; three files are already over it.

Internal modules carry `metadata.internal` so they do not surface as separately invocable skills.

## The wiring: ten sites across two files

Adding or renaming a family is not one edit. It is ten, and four of the regions they sit in are
compared byte for byte between `cast` and `paint` by `scripts/check-shared-blocks.sh`. Edit one
file without the other and CI rejects the PR.

| Site | Where | Guarded |
|---|---|---|
| Detection commands | `scan` region | yes |
| "Map the results" bullets | `scan` region | yes |
| Context-layers table (mobile / desktop / audit) | `load` region | yes |
| Stack-specific load table | `load` region | yes |
| "Advanced thesis" trigger terms | `load` region | yes |
| Stack-specific audit checklist | `audit` region | yes |
| Preview-mode default for the stack | `preview` region | yes |
| Interaction-thesis exemplars | `cast` step 4, `paint` Phase 2 | no, and they differ |
| Legacy-bridge question | `cast` DISCOVER, `paint` Phase 1 | no |
| Stack-aware token generation | `paint` Phase 3 only | n/a |

The `skill-base` region is the exception: it resolves paths and knows nothing about families.
Do not touch it.

Three of these sites are duplicated across the two orchestrators with no CI guard. That is a
known weakness, not a design: the audit checklist was in the same state until v3.4.0 and had
already drifted.

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
2. **Who owns it?** Ten wiring sites and a quarterly re-derivation, with no owner, is a family
   that is wrong within a year. The answer cannot be "the maintainer".
3. **What is the primary source?** If there is no equivalent of `api/current.txt` or DocC, every
   claim is unverifiable and the family cannot meet the evidence standard.
4. **Can you measure a dropped frame on it?** Question 7 is not optional. A family whose audit
   step cannot be run is a family that ships assertions.

The cost, measured on the v2.0 expansion that added Android and Apple: four to five thousand
lines across sixteen files, plus the ten wiring sites, plus the ongoing symbol count.

## Removing a family

This is a normal outcome, not a failure. **The plugin that is right about three platforms beats
the plugin that is stale about six.**

A family is a candidate for removal when its `VERSIONS.md` dates are more than two quarters old
with no owner, or when its content has produced a correctness issue that nobody could verify.

Removal is the ten wiring sites in reverse, the module directories deleted, its `VERSIONS.md`
section moved to a "formerly covered" note with its last-verified date, and the README and the
`plugin.json` keywords narrowed to match. The CHANGELOG entry says why, plainly. Someone
arriving from a search engine deserves to know the coverage ended and when, rather than finding
advice that quietly stopped being checked.
