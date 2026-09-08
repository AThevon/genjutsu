# genjutsu - correctness pass and what comes after

Design doc, 2026-09-08. Covers the direction agreed for the next four work
blocks, and specifies the first one (v3.4.0) in enough detail to execute.

## Why now

Measured on 2026-09-08 via the GitHub API and the traffic endpoints:

| Signal | Value |
|---|---|
| Unique cloners, 14 days | 1725 (about 130/day, no dips) |
| Clones, 14 days | 5134 |
| Views / unique visitors, 14 days | 3468 / 1376 |
| Stars by month | mar 2, apr 2, may 5, jun 5, jul 141, aug 150, sep 28 in 8 days |
| Top referrer | Google, 2238 views / 844 uniques |
| Release ZIP downloads, all time | 915 |
| Issues since creation | 1 |
| Last commit before this pass | 2026-07-31 |

Two things follow.

The plugin is found. The earlier read that distribution was the bottleneck was
wrong: growth is organic, accelerating, and arrives through people searching the
name on Google. What is missing is not listings, it is a public install counter
and any written account of the project.

The plugin is also dormant while shipping to roughly 4000 installs a month, and
parts of what it ships are false. That makes correctness the first block, not a
hygiene task.

One number settles a later question: 915 ZIP downloads all time against 1725
unique cloners in fourteen days. The ZIP path is about 2% of distribution. The
18-ZIP packaging pipeline and its `SKILL.md` to `GUIDE.md` rewrite serve almost
nobody.

## The four blocks

1. **Correctness (v3.4.0)** - specified below. Roughly three sessions.
2. **Reach** - publish so `npx skills add AThevon/genjutsu` works, which yields a
   public install counter; write one piece about the project. The Anthropic
   community catalogue submission is already pending since 2026-07-31 and is out
   of our hands.
3. **Plumbing** - stop hand-loading sub-skills. Decide the vendored
   `ui-ux-pro-max` dataset (57% of the repo). Trim the README against the docs
   site. Re-test whether plugins now install on claude.ai and Cowork from the UI,
   which would retire `package-for-claude-ai.sh`.
4. **Evidence** - turn the closing 25-item checklist from assertion into
   measurement.

Explicitly not this year: a fourth platform family. Adding Flutter widens the
surface at the moment its depth is failing verification, and it is the most
cloneable thing on the list.

## Non-goals for v3.4.0

- No new platform, framework or language.
- No restructuring of the `cast` or `paint` pipelines.
- No sub-skill directory renames. `framer-motion/` keeps its name this release
  even though the package is now `motion`; renaming it breaks anyone who
  uploaded the individual ZIP, and the packaging path is touched in block 3
  anyway. The *content* and the *detection* cover both packages.
- No README trim, no vendored-dataset decision. Both belong to block 3.

## v3.4.0 scope

### A. The silent loader failure

`$SKILL_BASE` and `load_skill()` are shell state. Shell state does not survive
between Bash tool calls. `paint` defines them at 175-271 and then dereferences
them at 423 and 524, and across the whole Phase 4 load table, with mandatory
WAIT gates at 414, 463 and 515 in between. Those `cat`s resolve to
`/ui-ux-pro-max/SKILL.md` and `/design-audit/SKILL.md`, fail, and the pipeline
continues without the sub-skill. `cast` has the same shape between its
`skill-base` fence and its load table. About 32 references across the two files.

`packaging/genjutsu-router.md:26` already documents this exact hazard and works
around it by repeating the resolution in every block. The orchestrators do not.

Fix, applied identically inside the guarded regions:

1. State the constraint in prose *inside* the `skill-base` region, so it is
   mirrored and cannot drift: this block defines shell state, and every Bash
   invocation that loads a sub-skill must contain the block and the `load_skill`
   calls together.
2. Cache the resolved path to a file and re-read it, validated, so a later phase
   recovers without re-probing. A cache that points at a directory that no longer
   exists is discarded rather than trusted.
3. Replace every raw `cat "$SKILL_BASE/<name>/SKILL.md"` with `load_skill <name>`,
   including in the load tables, which today print paths rather than calls. This
   also removes literal `SKILL.md` strings that the packaging step rewrites
   blindly.

### B. `design-audit` returns a false pass

15 of the 19 greps in `skills/_jutsu/design-audit/SKILL.md` end in `src/`, which
matches nothing on a default Next.js app-router or Nuxt 3 layout. The pipeline
then reads "no findings" as a passing gate immediately before delivery. Nothing
in the file tells the model to adapt the root.

Fix: detect the source roots instead of assuming one, and add `.vue`, `.svelte`
and `.astro` to the include lists, which SCAN already detects and the audit has
no coverage for.

### C. Symbols that do not exist or do not compile

Each of these makes the agent emit code that fails to build. Replacements are
verified against the vendor's primary source before being written.

| File | Symbol |
|---|---|
| `compose-motion/SKILL.md:41` | Spring stiffness and damping constants |
| `compose-graphics/SKILL.md:117`, `m3-expressive-deep.md:141` | `.toPath().asAndroidPath().asComposePath()` |
| `recomposition-and-anim.md:121`, `design-audit/SKILL.md:209` | `Modifier.recomposeHighlighter()` |
| `compose-multiplatform/SKILL.md:93` | `UIBlurEffect.systemMaterial()` |
| `compose-multiplatform/SKILL.md:254`, `cmp-platform-quirks.md:43` | `IOSKeyboardEventListener` |
| `desktop-principles/SKILL.md:46` | `.hoverEffect(.highlight)`, unavailable on macOS |

### D. Version and support claims that mislead

- `css-native/references/modern-css.md` browser-support tables. The scroll-driven
  animations table claims Firefox 128+ shipped support in July 2024. No stable
  Firefox ships it. The agent reads that and drops the `@supports` fallback.
- `framer-motion` pinned at v11 while the package has been renamed and moved on.
  Both `framer-motion` and `motion` are in the wild, so SCAN detects both and the
  sub-skill states which one the project uses and gives the matching import.
- GSAP plugin availability and any remaining Club-era reference.
- Three.js revision and the React Three Fiber React peer range.
- WCAG target-size criteria numbers in `mobile-principles`.

### E. Machinery so it does not come back

- `skills/_jutsu/VERSIONS.md`: one row per library or SDK, the version the content
  was written against, an ISO date. One pointer line at the top of each SKILL.md.
  v3.1.0 removed the "April 2026 baseline" labels and kept the version numbers,
  which turned stale claims into evergreen-looking ones.
- `.github/workflows/checks.yml` running `check-shared-blocks.sh`,
  `validate_data.py`, the 16 unittest cases that have never run in CI, and a
  denylist grep for the symbols fixed in C. **The release job must depend on it.**
  Today `release.yml` triggers on `push: tags: v*` and `check-shared-blocks.yml`
  on `pull_request` and `push: branches: [main]`; a tag push matches neither, so
  publishing runs zero checks.
- Guard the audit checklist. 34 lines are duplicated between `cast:402-435` and
  `paint:529-562` and differ on exactly one, and it is the block most likely to be
  touched by any future platform work. Reconcile that line, wrap both in
  `genjutsu:shared:audit` markers, add `audit` to `REGIONS`.
- Make `check-shared-blocks.sh` self-discovering: fail if the set of
  `genjutsu:shared:*:start` markers found in the files differs from `REGIONS`, so
  a new region cannot be added to the files and forgotten in the checker.

### F. Contradictions and attribution

- `paint` Iron Rule 3 says "never proceed without both theses validated" while the
  light-scope table says "interaction thesis only". Rule 8 says the audit always
  runs while light scope substitutes a quick check. Two Red Flags rows restate
  both absolutely. v3.3.0 patched rules 1 and 4 and stopped. A weaker model
  weights a numbered "Never" over a table thirty lines away.
- `LICENSE` asserts MIT (c) Adrien Thevon over the whole tree, including about
  1.5 MB of Next Level Builder's MIT-licensed data and code whose permission
  notice is vendored nowhere. Add their LICENSE and one scope line.
- `UPSTREAM.md` is wrong on all three things it exists to record: the tag, what
  `references/` contains, and when `validate_data.py` and `tests/` arrived.

## Verification

The pass is done when, from a clean checkout:

- `./scripts/check-shared-blocks.sh` passes and reports the `audit` region.
- The denylist grep returns nothing for every symbol in C.
- `python3 skills/_jutsu/ui-ux-pro-max/scripts/validate_data.py` passes.
- `python3 -m unittest discover -s skills/_jutsu/ui-ux-pro-max/scripts/tests` passes.
- `claude plugin validate .` passes.
- `./package-for-claude-ai.sh` produces the bundle and the individual ZIPs, and
  the bundle contains exactly one `SKILL.md`.
- Every correction in C and D carries a source URL in the commit or in
  `VERSIONS.md`.

## Open, deliberately deferred

- Whether plugins now install on claude.ai and Cowork by syncing a GitHub repo
  from the UI. If they do, `package-for-claude-ai.sh` becomes a free-tier-only
  path. Block 3.
- Whether to rename `framer-motion/` to `motion/`. Block 3, alongside packaging.
- Whether to slim the vendored dataset or wire it into `paint` Phase 3 for real.
  It is 57% of the repo and no orchestrator invokes `search.py` directly. Block 3.
- Contributor infrastructure. 26 forks, 2 external contributors, no
  `CONTRIBUTING.md`, no `CODEOWNERS`, no issue template. One person cannot verify
  six platform families indefinitely; this is the only change that lowers the
  recurring cost rather than paying it down once. Block 2 or 3.

---

## Follow-ups found while verifying, left out of v3.4.0

Surfaced by the fact-check pass, not falsehoods, so out of scope for a correctness release.
Each is one line of work.

- GSAP 3.15 deprecated `yoyoEase` in favour of `easeReverse` (`gsap/references/core.md:74`).
- three r182 deprecated `PCFSoftShadowMap` for `PCFShadowMap`
  (`threejs-r3f/references/scene-setup.md:363, :376`).
- `swiftui-motion` never mentions `navigationTransition(_:)` / `NavigationTransition.zoom` /
  `matchedTransitionSource(id:in:)`, all iOS 18+.
- `desktop-principles` never mentions `.pointerStyle(_:)` (macOS 15+) or
  `.onContinuousHover` (macOS 14+).
- The `MaterialShapes` list in `m3-expressive-deep.md:171` is accurate but incomplete.
- Motion 13.2 added a `motion/three` entry point that drives Three.js objects, materials and
  TSL uniform nodes. Relevant cross-link for `threejs-r3f`.
- The Compose "(Compose 1.6+/1.7+)" since-markers are individually true but read as "this is
  new" against a 1.12.0 baseline.
- `liquid-glass-deep.md:250` cites "Apple iOS 26 release notes", which is not resolvable.
- `framer-motion/SKILL.md:19` claims "~50kb tree-shaken"; no current primary source found, and
  the `m` + `LazyMotion` path is much smaller.
- Nothing covers the 2026 Apple cycle (Xcode 27 / iOS 27, GA 14 Sep 2026) yet.
