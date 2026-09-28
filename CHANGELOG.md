# Changelog

All notable changes to this plugin are documented here. Format inspired by [Keep a Changelog](https://keepachangelog.com/).

## v4.0.0 - 2026-09-28

genjutsu names the slop instead of promising it, cleans it up before it reports, proves it, and
installs anywhere.

### Added

- **`tells`, a module that names the slop.** v3 promised "anti-AI-slop" and never said what slop
  was. `skills/_jutsu/tells/` writes it down: forty-two defaults a model produces when nobody
  asked for them, in four families. Invented information: a weather-and-clock strip, a build
  status such as `v0.6.2-rc.1`, `ESTD. 2018`, `John Doe`, `99.99%`, a product drawn in divs.
  Decorative filler: `00 / INDEX` eyebrows, `Stage 1 / 2 / 3`, scroll cues, status dots that
  report nothing, glass panels, glows and blurred blobs, animations that never stop. Reflex
  convergence: three equal cards, a display serif taken as the creative default, gradient text,
  U+2014 (em dash). Hollow copy: `Elevate`, `Seamless`, one intent under three CTA labels, a
  register that changes from one section to the next.

  Every entry has three fields and never a fourth: the marker, why a model produces it, and a
  question that sends you back to the thesis. None names a replacement, because a replacement
  would only be the next default: the validated thesis is the only authority. `cast` and `paint`
  now write an `Allowed patterns:` line under every thesis, and a pattern is allowed only when
  that line names it. A mood word such as "editorial" names nothing, since most tells are
  exactly the clichés of an agency portfolio, and something the brief asks for has to be carried
  onto that line by name. Each finding ends in one of three ways: allowed, with the line that
  allows it; "not this tell", only when the match contradicts the entry's own condition and with
  the `file:line` that proves it, never on taste; or a problem.

  The web is covered in `references/web.md`, published entry by entry as the field guide at
  genjutsu.athevon.dev/docs/tells. Compose and SwiftUI are declared not covered yet rather than
  filled with invented material. `cast` loads the module after the thesis gate on a web stack at
  medium or full scope; `paint` loads it in Phase 3, before the design intelligence runs, because
  Phase 3 is where palette and type get fixed. Each time in a shell call of its own (see Fixed).

- **The run cleans up before it reports.** Every tell the run wrote and the thesis does not allow
  is fixed before the final report, in two passes at most, and only on the lines the run wrote,
  read off `git diff` when the project has one. A tell that was in the project before the run is listed and never changed
  by the audit, and nothing on the protected list below is ever changed automatically.

- **`paint` inventories an existing project first.** On a web project that already has a look,
  Phase 1 runs the tells audit over it and shows the result as one short block, **What this
  project already does by reflex**, counted by family with two or three `file:line` examples
  each, before it asks which mode you want. The mode settles every finding in the theses:
  preserve keeps them by default, on the `Allowed patterns:` line as the brand's own; partial
  takes them out by default inside the areas you named; redesign takes them out everywhere. Any
  one of them can be kept or dropped by name at the thesis gate.

- **The audit sees the text and the markup.** `audit.py` gains a `tells` group of eighteen
  checks. Thirteen read the text a page actually displays (between tags, and in `alt`, `title`,
  `aria-label` and `placeholder`, never in a class or a style object) and its markup; five read
  the source for gradient text, glass panels, glows, blurred blobs and animations that never
  stop. A capitalised JSX tag is a component, never a void element, and a TypeScript generic is
  never read as a tag. `.html` files are scanned now. Three inventories join durations and
  easings (distinct colours, radii and font families), and every value keeps a bounded list of
  `file:line`. Tells are reported at `nice-to-have` in a section of their own, counted apart on
  the summary line, and none counts until it has been confronted with the thesis. `--group
  tells` runs them alone, with no model involved:
  `python3 ~/.agents/skills/genjutsu/_jutsu/design-audit/scripts/audit.py . --group tells`.

- **The audit holds the thesis against the code first.** For every promise of the thesis
  (durations, easing, springs, palette, type, layout family): the `file:line` that keeps it, or
  its absence. If the promised motion cannot ship working, the fallback is to ship it static and
  say so, never half-broken. The report now ends with two required lines, `Modules loaded:` and
  `Modules not loaded:`, because a module that failed to load used to leave no trace in the
  result.

- **`npx skills add https://genjutsu.athevon.dev -g`.** The site publishes a well-known index,
  `/.well-known/agent-skills/index.json` (discovery schema 0.2.0), that points at this release's
  `genjutsu.zip` with its sha256 digest, both taken from one download of the release at build
  time. The install is recorded in the npx lock, so `npx skills update -g` sees each new release.
  After an npx install the entry point is `/genjutsu`, the router.

- **An eval suite, with and without genjutsu.** `evals/` holds four cases for
  `claude plugin eval` with an ablation arm: two landings where the tells have to go, one where
  the thesis asks for a tell and it has to stay (a studio genuinely split between Paris and Tokyo
  keeps its two clocks), and a SwiftUI screen where `tells` must never be requested. Run by hand
  before each major release and never in CI, since every run is a billed session. The numbers
  are under Measured.

- **Process grafts.** A declared read before the first question (what, for whom, heading where,
  on which stack), so a wrong assumption gets corrected before it costs a question. A vague brief
  gets options drawn from the product's own moments, never from a famous brand's site, and a
  thesis that could have been written from the product category alone is rewritten. A display
  face stays only when the visual thesis names it and says why that one; the thesis may leave it
  undecided, and then the design-system gate settles it with its reason. Three dials in `paint`,
  variance, motion and density, derived from the validated theses and passed to the design
  intelligence, never read off the raw brief. An existing-project mode asked in Phase 1: preserve
  the brand, change part of it, or redesign; public token names, URLs, navigation labels, form
  field names, the logo and legal text never change without agreement, whatever the mode. And
  the dataset's proposals now go through the thesis and `tells` before they reach you.

- **Sessions with no human.** A sixth guarded region, `headless`, identical in both pipelines:
  take the announced preview default, take the proposed thesis and mark it UNVALIDATED in the
  report, and never install a dependency.

- Checks and release helpers: `check-version.sh` (both manifests, the first entry of this file
  and, under a release, the tag agree), `check-dashes.sh`, `check-no-verbatim.sh`,
  `check-tells.py`, a test of the resolver as it ships inside the packaged bundle,
  `release-notes.sh` and `wait-for-release.sh` with their tests, `showcase-section.py`, and
  `verify-npx-install.sh`, which installs through the real `npx skills` in a throwaway HOME and
  checks what the installed block resolves.

### Changed

- **The resolver looks in the skill's own directory first.** `GENJUTSU_SKILL_DIR`, defaulting to
  `${CLAUDE_SKILL_DIR}`, then `${CLAUDE_PLUGIN_ROOT}`, then bounded probes: the working
  directory's ancestors, `~/.agents/skills` (npx's global directory), `~/.claude/skills`,
  `~/.codex/skills`, `~/.cursor/skills` and the Cowork roots. The Claude Code plugin cache comes
  last, so an old plugin install never wins over a newer bundle. A `_jutsu` directory is accepted
  only if it holds `motion-principles`: npx's shared directory serves dozens of agents, and a
  folder called `cast` proves nothing. claude.ai keeps its priority, and the resolver and the
  router now look under `/mnt/skills/plugins`, where claude.ai mounts uploaded skills since
  September 2026 (v3 only probed `/mnt/skills/user`, and found nothing there any more). The
  unconditional `/mnt/skills/user` fallback is gone: it accepted a directory without checking
  what was in it.
- **When the modules cannot be found, the pipeline stops**, printing the install commands and
  every root it tried, instead of running on empty. A single missing module is still reported by
  name and skipped.
- **One claude.ai ZIP.** The release publishes a single `genjutsu.zip`: a router `SKILL.md`, and
  the pipelines and modules as `GUIDE.md` files, so they never show as skills of their own. The
  per-skill ZIPs are gone.
- **The sixteen modules carry `metadata.internal: true`.** `npx skills add AThevon/genjutsu`
  offers only `cast` and `paint`, and installed that way they stop and print the well-known
  command.
- **Host neutrality.** The preview gate describes its first mode by capability: an HTML rendering
  tool if the session has one (Artifact on Claude), otherwise a throwaway HTML file. The skills say
  "shell call" instead of naming a tool. Claude hosts are detected as before, and an unknown host
  gets the generic behaviour.
- **The preview message names the thesis in plain text**, whatever the mode, so a thesis shown
  inside a rendered page is never mistaken for the page's own copy.
- `ui-ux-pro-max` calls its search engine by absolute path, `$UIUX_DIR/scripts/search.py`, instead
  of a path relative to a working directory nothing had set. The vendored files are untouched.
- The release notes are this file's entry for the tag, not GitHub's list of PR titles. The release
  workflow then waits until GitHub serves the new release and its `genjutsu.zip`, and only then
  calls the site's deploy hook, so the install index always names the release just published.
- U+2014 (em dash) is gone from every file genjutsu writes: 193 occurrences in 14 files, and
  `check-dashes.sh` keeps it out.

### Fixed

- **A full web `cast` loaded more than the model could see.** Past about 30,000 characters, the
  output of one shell call no longer arrives inline: the model gets a 2,000-character preview and
  a file path. motion-principles, desktop-principles, design-audit and framer-motion come to about
  34,500 characters together, so a full-scope web cast had been reading a preview of its own
  modules since v3. Loading is now batched under 25,000 characters per call, one call per heavy
  module, `validate-skills.py` flags any module over 25,000, and a load is never piped into
  `head`, `tail`, `sed` or `grep`.
- `load_skill` said "continuing without it" and carried on; a missing module is now named, and
  the report's `Modules not loaded:` line keeps the list across shell calls.

### Measured

<!-- genjutsu:showcase:start -->
| Brief | Tells, without genjutsu | Tells, with genjutsu | Grader score, with minus without |
|---|---|---|---|
| Independent design studio landing | 2 | 0 | +0.20 |
| Invoicing SaaS landing | 2 | 0 | +0.10 |

Tells are the findings of `audit.py --group tells` on the page of the first run of each arm. Scores come from `claude plugin eval --ablation with-without --runs 2` on genjutsu `ef31234`, over the suite in [`evals/`](https://github.com/AThevon/genjutsu/tree/v4.0.0/evals). The graders are ours: read this as genjutsu measured against what it set out to do, not as an independent benchmark.

#### Invoicing SaaS landing

| Without genjutsu | With genjutsu |
|---|---|
| <img src="https://raw.githubusercontent.com/AThevon/genjutsu/v4.0.0/assets/v4/saas-landing-without-desktop.png" alt="Invoicing SaaS landing, without genjutsu, desktop" width="400" /> | <img src="https://raw.githubusercontent.com/AThevon/genjutsu/v4.0.0/assets/v4/saas-landing-with-desktop.png" alt="Invoicing SaaS landing, with genjutsu, desktop" width="400" /> |
| <img src="https://raw.githubusercontent.com/AThevon/genjutsu/v4.0.0/assets/v4/saas-landing-without-mobile.png" alt="Invoicing SaaS landing, without genjutsu, mobile" width="180" /> | <img src="https://raw.githubusercontent.com/AThevon/genjutsu/v4.0.0/assets/v4/saas-landing-with-mobile.png" alt="Invoicing SaaS landing, with genjutsu, mobile" width="180" /> |
<!-- genjutsu:showcase:end -->

What moved, over the runs kept in each arm: on both landings, the judge that fails a product
screen faked in divs or a page stuck on one layout family (studio 0/2 to 2/2, SaaS 0/2 to 1/2),
and the U+2014 (em dash) check (1/2 to 2/2 on each); on the studio page, the numbered eyebrow
(1/2 to 2/2). The other checks already passed without genjutsu.

The control cases held: in `thesis-allows` the two clocks the thesis names stayed on every run,
and in `swiftui-skip`, measured on `5735e65`, `tells` was never requested or read.

### Notes

- Credit: tells catalogue inspired by taste-skill (MIT, Leonxlnx). What came from it is the idea of
  writing a model's reflexes down, and a set of observed markers. Every entry is rewritten as
  detection with no prescribed replacement, and nothing is copied: no passage, no asset, no module
  named after it. `scripts/check-no-verbatim.sh` compares ten-word windows against the pinned
  upstream commit.
- npx installs genjutsu for Codex, Cursor and the other agents it knows, and it runs there. It is
  not tested by the maintainer and not supported; a bug that does not reproduce under Claude Code
  is labelled `community`.
- Not in this release: behaviour written for one host, native Codex or Cursor plugin manifests,
  tells for Compose and SwiftUI (they need observation first, not invention), and the
  ui-ux-pro-max v2.15.0 sync.

## v3.6.0 - 2026-09-08

The audit greps become a script with tests, and the resolver loses the cache that served the
previous release.

This entry was written after the release: v3.6.0 was tagged and published with `plugin.json` and
`marketplace.json` still reading 3.5.0 and no CHANGELOG entry. Both manifests now read 3.6.0.

### Changed

- **`design-audit` runs a script instead of nineteen greps.** Fifteen of the greps were anchored
  on `src/`, which a default Next.js app-router or Nuxt 3 project does not have, so they matched
  nothing, and the pipeline read the empty output as a clean bill of health right before
  delivery. A grep cannot tell "I looked and found nothing" from "there was nothing here to look
  at": both print zero lines. Every check now declares what its own zero result means, and a
  project with no `.tsx` files gets NOT APPLICABLE rather than a pass. The report ends with all
  three counts.
- **The `$SKILL_BASE` cache is gone.** It was added in v3.4.0 and it was a staleness bug: after a
  plugin update the previous version directory is still on disk, so a cached path passed the "is
  it a directory" guard and the current orchestrator silently loaded the previous release's
  sub-skills. Reproduced against a two-version fixture: the cache served 3.1.0 while 3.5.0 was
  installed. The block already says to re-emit it in the same shell call as the loads, and
  resolution is a handful of depth-capped finds. Being right is cheaper than being fast here.
- **`design-audit/SKILL.md` drops from 298 lines to 101.** The greps moved into the script. What
  remains is how to run it, how to read the three statuses, the contrast computation the script
  deliberately does not do, and the device handoffs it cannot do.

### Added

- **`design-audit/scripts/audit.py`.** Ten checks, root detection, `node_modules` and build
  output skipped, `.vue`, `.svelte` and `.astro` alongside JSX and CSS, and findings that carry
  `file:line` and the matched text, so the caller reports evidence rather than a verdict.
  Markdown or JSON. The exit status is 0 unless the audit itself failed to run: findings are not
  errors. Each check carries an `unless` clause, which is where the false positives die: a
  `:hover` next to a `transition` is not a finding.
- **`design-audit/scripts/tests/test_audit.py`**, wired into CI. Every check has a fixture that
  must make it fire and one that must not, and a check added without a fixture fails the suite. A
  check that goes silently inert breaks the build instead of reporting a clean audit.
- **`scripts/test-resolver.sh`**, wired into CI. It extracts the guarded resolver block from
  `cast/SKILL.md` and runs it byte for byte against fixture layouts: `$CLAUDE_PLUGIN_ROOT` wins
  when substituted, the versioned cache is the fallback, the newest version wins and ordering is
  numeric (3.10.0 beats 3.9.0), a skills directory under `$HOME` and a session root above `$PWD`
  both resolve, nothing installed resolves empty, a plugin root pointing nowhere is discarded, no
  cache file is written, and a stale cache file left on disk is never consulted. The block had
  shipped two silent total failures with zero tests: nothing resolved on Cowork in v3.3.0, and the
  wrong version resolved in v3.4.0.

### Fixed

- **The duration inventory missed the common case.** It keyed on `duration:`, so it skipped
  `transition: width 300ms`. It now reads times in an animation context, normalises them, and
  ignores `maxAge: 3600s`.

## v3.5.0 - 2026-09-08

The audit stops asserting and starts reporting, and the design intelligence actually runs.

### Changed

- **The closing audit is split in two, and neither half is a tick.** Both pipelines ended in
  twenty-five checkboxes, several of which name a tool the agent cannot run: Chrome DevTools,
  Macrobenchmark on a device, Instruments Hitches. Ticking "60fps verified via Chrome DevTools"
  without opening Chrome turns "I did not look" into "I looked and it is fine", and it was the
  last thing the user read.

  What can be established from the code is now reported **with the evidence used**: the grep and
  its hits, the computed value, the `file:line`. Contrast is computed from the emitted tokens
  rather than eyeballed, so a finding reads `#831843 on #FDF2F8 = 9.4:1`. An item that could not
  be checked is reported as **not checked**, never as passed.

  What needs a profiler, a device or a pointer becomes a **handoff table** with the exact
  invocation and the pass condition, marked UNVERIFIED. The agent may not tick those, soften
  them, or drop the section because the rest looked clean. The report ends with the counts of
  both groups, because "9 checked, 2 problems, 8 handed over" is an audit and a list of ticks is
  not. Two new Red Flags rows in each orchestrator guard the two ways this gets undone.

  Where a dev server or preview is already running and the user agrees, driving it to collect the
  web rows beats handing them over. Nothing is started or installed for an audit.

- **`paint` Phase 3 now runs the design intelligence instead of hoping.** It loaded
  `ui-ux-pro-max` and stopped, so whether the search engine behind it ever ran was left to the
  model. 1.8 MB of vendored data, 55% of the tracked repo, sat behind a judgement nobody
  measured. Phase 3 now invokes `search.py --design-system -f markdown` directly, queried with
  the **validated visual thesis** rather than the raw user request, since the thesis is what was
  approved.

  The result is framed as a proposal, not an answer: it is a lookup against a static dataset that
  has never seen the project, so keep what serves the thesis, discard what fights it, and say in
  one line what was taken and what was dropped. If `python3` is unavailable the pipeline says so
  and derives the system by hand rather than stopping.

- **`-f markdown` is mandatory on `--design-system`**, applied to all six invocations. The
  default `ascii` emits about 7,000 bytes carrying raw ANSI colour escapes - `hex_to_ansi` has no
  isatty guard, so they survive the pipe and land in context as garbage. Markdown returns the
  same content in about 2,100 bytes. A 3.3x token reduction on the most-run command in the skill.

### Added

- **`CONTRIBUTING.md`.** The evidence standard, stated once: a correction needs a primary source,
  the acceptable one is named per platform, and a blog post, your memory and a model's output are
  not among them. It also says what a test proves and what it does not, with three real examples
  from the v3.4.0 pass, because the worst class of error here throws nothing at all. Plus a
  private security path, which the repo lacked despite having taken one vulnerability report.
- **`PLATFORM-CONTRACT.md`.** What a platform family must answer, with the reference
  implementation for each of ten questions; the ten wiring sites across `cast` and `paint` and
  which four are compared byte for byte; an honest quarterly cost written to let someone decline;
  and how a family gets removed, because the plugin that is right about three platforms beats the
  plugin that is stale about six.
- Four issue forms and a pull-request template. The wrong-claim form requires the source URL and
  asks separately how you established it, since a URL is easy to paste and a method is not.
- **`VERIFY-NEEDED`** as a marker in `VERSIONS.md`: one public list of unconfirmed rows rather
  than a second tracker that would drift from the first. Two genuinely unverified rows are marked.

### Notes

- No CODEOWNERS. It silently ignores owners without write access, GitHub never requests a review
  from the pull-request author, and only organisation teams can own a path, so on a personal repo
  with one maintainer it would document a routing guarantee it does not provide.
- `docs/superpowers/` is no longer tracked. Agent working notes are not part of a plugin.
- The vendored dataset question is settled in `UPSTREAM.md`: load-bearing, keep it, and the
  v2.11.1 to v2.15.0 sync is worth taking when there is an afternoon. The eight out-of-scope
  stack CSVs stay, because the clean-mirror property is worth more than the 184 KB.

## v3.4.0 - 2026-09-08

Correctness release. The pipelines were fine; the knowledge base underneath them had started
to lie. 78 corrections across the skill tree, each verified against a primary source - MDN
browser-compat-data, caniuse, `api/current.txt` in androidx-main, Apple's DocC JSON, the npm
registry - plus a handful found while checking, and the machinery to stop the class of error
coming back. What was verified against what, and when, is now recorded in
`skills/_jutsu/VERSIONS.md`.

### Fixed - the pipeline

- **Sub-skills silently failed to load in `paint`.** `$SKILL_BASE` and `load_skill` are shell
  state, and shell state does not survive between Bash tool calls. `paint` resolved them once
  and then dereferenced them in Phase 3 and Phase 5, both separated from the definition by
  mandatory user-validation gates. Those `cat`s resolved to `/ui-ux-pro-max/SKILL.md` and
  `/design-audit/SKILL.md`, failed, and the run carried on without the sub-skill - so the
  design system was generated without the design intelligence, and the final audit ran without
  the audit module. Every raw `cat "$SKILL_BASE/..."` is now a `load_skill` call, the
  resolution block states the constraint in the text and caches its result so re-emitting it is
  cheap, and each loading phase says out loud that it must re-emit it.
  `packaging/genjutsu-router.md` had documented this exact hazard since v3.1.0, for the router
  and not for the two files that needed it more.
- **`design-audit` reported a clean bill of health on code it had never read.** 15 of its 19
  greps ended in `src/`. A default Next.js app-router or Nuxt 3 project has no `src/`, so they
  matched nothing, and the pipeline treats "no findings" as a passing gate immediately before
  delivery. The greps now go through two helpers that own the root and the noise directories,
  and pass their arguments as `"$@"` rather than through an unquoted variable - zsh does not
  word-split those, so the usual `$SRC` / `$EXCL` idiom collapses into one bogus argument.
- `.vue`, `.svelte` and `.astro` are now included wherever the audit looks for a CSS or JSX
  pattern. SCAN has always detected those stacks; the audit had zero coverage of them.
- The duration histogram never worked: `uniq -c -f2` skips two whitespace-separated fields and
  the line has none, so every value collapsed into one empty group.

### Fixed - symbols that do not compile

Each of these made the agent emit code that fails to build.

- `Modifier.recomposeHighlighter()` is not an androidx API at any version - it is a sample in
  `android/snippets`. Replaced with Layout Inspector's **Show Recomposition Counts**, in the
  reference, in `design-audit` and in both orchestrator checklists.
- `Morph.toPath().asAndroidPath().asComposePath()`: `androidx.graphics.shapes.Morph.toPath()`
  already returns an `android.graphics.Path`, which has no `asAndroidPath()`. There are two
  `Morph.toPath` extensions with the same shape and different return types, so the import now
  names which one. Also: `MaterialShapes` are normalized to a 0..1 box, so dropping the path
  into `GenericShape` rendered a ~1px shape in the corner.
- `UIBlurEffect.systemMaterial()` is not a Kotlin/Native binding.
- `IOSKeyboardEventListener` does not exist in Compose Multiplatform, at any version. The real
  knob is `ComposeUIViewControllerConfiguration.onFocusBehavior`.
- `.hoverEffect(.highlight)` is `@available(macOS, unavailable)` - a compile error in a macOS
  target, not the no-op the comment claimed. It is now gated with `#if os(macOS)`.
- `sharedElement` / `sharedBounds` take `sharedContentState`, not `state` - renamed in
  compose-animation 1.8.0-alpha06, and stable Compose is now 1.12.0.
- Spring constants were shifted by one rung: the real values are `StiffnessVeryLow` 50f,
  `StiffnessLow` 200f, `StiffnessMediumLow` 400f, `StiffnessMedium` 1500f, `StiffnessHigh`
  10000f. An agent trusting "MediumLow 700" picked a spring 1.75x stiffer than it meant to,
  and the recipe table above it uses the symbolic names.

### Fixed - claims that were wrong in the dangerous direction

- **Firefox does not support scroll-driven animations.** The table said "Firefox 128+,
  Supported (shipped July 2024)". No stable Firefox ships them - Nightly only, behind
  `layout.css.scroll-driven-animations.enabled`. The false claim invited the agent to drop the
  `@supports` guard, which serves a static page to roughly one visitor in six. Safari shipped
  them in 26, not 18.4. Every browser-support table in `modern-css.md` was re-derived: View
  Transitions (Firefox 144, not 133), anchor positioning (Firefox 147, shipped, not "Nightly"),
  container style queries (Firefox 151, shipped, not "Not yet"), and the coverage percentages.
- `transition-behavior: allow-discrete` is Baseline, but *transitioning `display`* with it is
  not implemented in Firefox. The exit animation silently does not run there, which the file
  never said.
- The anchor-positioning example could not anchor anything: it used the non-standard HTML
  `anchor` attribute, on the wrong element, pointing at an id that did not exist, with no
  `anchor-name` declared anywhere.
- WCAG target sizes: 2.5.8 Target Size (Minimum) is AA at 24x24 CSS px; 2.5.5 Enhanced is AAA
  at 44x44. The "BAD" Compose example also overstated its case - Material 3's `IconButton`
  applies `minimumInteractiveComponentSize()` itself, so the target stays 48dp there.
- `response` in a SwiftUI spring is the period, not the settling time.

### Changed - Motion and Framer Motion

`framer-motion` and `motion` are the same library under two package names, both publishing
13.2.0: `motion` depends on `framer-motion` and `motion/react` re-exports it. Plenty of
projects still have the old name and nothing is broken.

- SCAN detects both, and reports which one is installed - the import path differs.
- The sub-skill leads with a table mapping each package name to its import and install line,
  and says to follow what `package.json` already has. Iron rule 8 in `cast` / 10 in `paint`
  now states it explicitly: **do not migrate a project from `framer-motion` to `motion`
  uninvited.** If both are present, the project is mid-migration - say so and follow whichever
  the file being edited imports.
- `staggerChildren` and `staggerDirection` were deprecated in Motion 12.22 in favour of
  `delayChildren: stagger(...)`. The skill taught the old form in four places; `stagger()`
  returns `startDelay + duration * distance`, so the rewrites preserve the timing exactly.
- The sub-skill directory keeps the name `framer-motion` this release. Renaming it breaks
  anyone who uploaded the individual ZIP, and packaging is not being touched here.

### Added

- **`skills/_jutsu/VERSIONS.md`** - 42 rows: what each library, SDK and browser feature was
  verified against, on what date, with the caveats. Every sub-skill now opens with a pointer to
  it. v3.1.0 corrected a batch of stale references and deleted the "April 2026 baseline"
  labels in the same pass, which turned dated claims into evergreen-looking ones. This is the
  fix for the class, not the instance.
- **`scripts/check-denylist.sh`** - the other half of that contract: the exact strings that
  were wrong once and must not come back. Entries carry an optional exemption pattern, because
  the best place to document a non-existent API is next to its name.
- **`scripts/validate-skills.py`** - checks all 17 `SKILL.md` against the Agent Skills spec:
  the six allowed frontmatter fields, `name` matching its directory, the length limits, no
  duplicate names. genjutsu already used only `name`, `description` and `allowed-tools`, so the
  tree runs unmodified on any runtime that reads the open spec; this keeps it that way. A field
  outside the six is a hard error on the claude.ai upload path, not a warning.
- **`.github/workflows/checks.yml`**, called by the release workflow. `release.yml` triggers on
  `push: tags: v*` and the only existing check triggered on `pull_request` and
  `push: branches: [main]` - a tag push matched neither, so **cutting a release ran zero
  checks**. The suite now runs the drift check, the denylist, the spec validator, the dataset
  validator, the 16 unittest cases that had never run in CI, and a packaging assertion that
  `genjutsu.zip` contains exactly one `SKILL.md`.
- **A fifth guarded region, `audit`.** 34 lines of the audit checklist were duplicated between
  `cast` and `paint`, differed on one, and were the block most likely to be touched by any
  future platform work - and the only duplicated block CI did not watch. The differing line is
  reconciled. `check-shared-blocks.sh` also fails now if the markers found in the files do not
  match its `REGIONS` list, in either direction, so a region cannot be added and forgotten.
- `skills/_jutsu/css-native`: `sibling-index()` / `sibling-count()`, Baseline since 18 Aug
  2026, and `interpolate-size` / `calc-size()`. The decision table used to route "stagger
  across a dynamic list of unknown count" to GSAP or Framer Motion; that is a CSS-native case
  now.
- `LICENSE-upstream.txt` under `ui-ux-pro-max`, and a scope section in the root `LICENSE`. The
  repo asserted MIT (c) Adrien Thevon over the whole tree, including 1.5 MB of Next Level
  Builder's MIT-licensed data and code whose permission notice was vendored nowhere.

### Changed

- `paint`'s Iron Rules 3 and 8 named the light-scope exception. Rule 3 said "never proceed
  without both theses validated" while the light-scope table says "interaction thesis only";
  rule 8 said the audit always runs while light scope substitutes a quick check. v3.3.0 patched
  rules 1 and 4 and stopped. A weaker model weights a numbered "Never" over a table thirty
  lines below it.
- `UPSTREAM.md` was wrong on the one thing it exists to record. The vendored tree is upstream
  **v2.11.1**, not v2.11.0 - verified by comparing git blob hashes file by file, not by reading
  a version string. v2.11.0 has no `references/`, no `validate_data.py` and no `tests/`; a sync
  described as v2.11.0 would have deleted all three. The same blobs are unchanged upstream
  through v2.14.0, so despite the tag gap the mirror is not drifting: v2.15.0 is the first
  release that actually diverges, and it is an engine rewrite (`core.py` 464 -> 993 lines) plus
  a new module. The re-sync instructions now verify by hash.

### Notes

- No new platform, framework or language. No pipeline restructuring. No sub-skill renames.
- Known follow-ups, found while verifying and deliberately left out of this release: three r182
  deprecated `PCFSoftShadowMap` for `PCFShadowMap`; `swiftui-motion` does not mention
  `navigationTransition` / `matchedTransitionSource` (iOS 18+); the `MaterialShapes` list is
  incomplete; Motion 13.2 added a `motion/three` entry point; the Compose "since 1.6+/1.7+"
  markers read as "this is new" against a 1.12.0 baseline. Three items that were on this list
  when it was first drafted are not on it any more: `.pointerStyle` and `.onContinuousHover`
  landed in `desktop-principles` as part of this release's Apple corrections, and `yoyoEase`
  turned out not to appear anywhere in the tree, so there was nothing to deprecate.

## v3.3.0 - 2026-07-31

Cowork compatibility: the pipelines now find themselves on a third surface, and stop being too heavy for it.

### Fixed

- **Sub-skill resolution on Cowork.** `cast` and `paint` resolved `$SKILL_BASE` from two fixed layouts only: `/mnt/skills/user` (claude.ai) and `${CLAUDE_PLUGIN_ROOT}` / `~/.claude/plugins/cache` (Claude Code). Cowork mounts the tree under a per-session root instead, for example `/sessions/<session-id>/mnt/.claude/skills/genjutsu/_jutsu`, so the `find` returned nothing, `$SKILL_BASE` stayed empty and every `load_skill` call failed. The pipeline ran without a single one of its fifteen sub-skills. A fourth branch now probes for `*/.claude/skills/*/_jutsu`: `$PWD` and its ancestors first, then `~/.claude/skills`, `/mnt/.claude/skills` and `/sessions`. Every probe is depth-capped, so none of them can walk the filesystem.
- The same fix landed in the claude.ai bundle router, which hardcoded `find /mnt/skills/user -path '*/cast/SKILL.md'` for both pipelines.
- Resolution failure is now explicit. The error message names each root that was tried and what to do per host, instead of leaving a silent `cat` of an empty path.

### Added

- **Preview gate host mapping.** The gate offered "artifact / live preview / inline" as if every surface implemented them the same way. It now detects the host before `LOAD` runs and maps each option: on Cowork, artifact means the host's persistent artifact and inline means its inline widget, while live preview is usually unavailable because there is no project checkout to write into. Cowork is tested before Claude Code, since both can have a `~/.claude` tree and only Cowork has the session-rooted mount.
- **Light scope in `paint`.** The five-phase pipeline is disproportionate for the short requests that dominate on Cowork. When the target is one isolated component, no visual identity is at stake, and nothing downstream depends on the result being systematised, `paint` now shortens to a single brainstorm question, the interaction thesis alone, and no `MASTER.md`. It announces the shortened path in one line so it can be overruled. The gates themselves stay: only their number goes down.

### Changed

- `cast` is now the documented default entry point. The bundle router used to spend a question on ambiguous intent; it now runs `cast` and says so in one line, since a `paint` that turns out to be a single component has its own shortened path.
- Iron rules 1 and 4 in `paint` name the light-scope exception rather than reading as absolutes that the shortened path would contradict.
- Cowork is named as a supported surface in the README: the badge, the opening line, its own install section, and a `Cowork compatibility` section documenting the resolution order and the preview mapping.
- Both ancestor walks are hard-bounded and guard against a `.` or empty `$PWD`, which would otherwise never reach `/` and spin the shell. The fixed skills roots are capped at depth 2, where `_jutsu` actually sits; only a session root gets more.

### Notes

- No change to claude.ai or Claude Code resolution. The new branch runs only after both existing ones miss, and the `genjutsu:shared:skill-base` and `genjutsu:shared:preview` regions stay byte-identical between the two orchestrators, enforced by the CI drift check.

## v3.2.0 - 2026-07-31

Presentation release: the validation gates now show their work instead of describing it.

### Added

- **The preview gate.** `cast` and `paint` stop at a handful of points to have you approve something visual - an interaction thesis, a set of variants, a visual identity, a design system. Until now each was described in prose and rendered as plain text in the transcript, which meant approving an easing curve you could not see and a palette you could not look at. Both skills now ask **how you want to see it** before the first of those gates:
  - **Artifact** - a live page: the easing curve plotted with its exact value, an element actually performing the motion with a replay button, the raw numbers (duration, delay, stagger, spring parameters), a reduced-motion toggle. For a design system: swatches with their contrast ratios, a real type specimen, the five states of every component, light and dark side by side.
  - **Live preview** - a throwaway route in your own project with your real stack and tokens; a `@Preview` / `#Preview` scratch file on Compose / SwiftUI, where an HTML page can only approximate.
  - **Inline** - the existing behavior, and still the recommended default for a 150ms hover.

  The question is asked **once**. The choice holds for the session, later gates only announce the mode in one line, and you switch by saying so.
- The gate is a cross-cutting protocol rather than a new pipeline stage, so `cast` keeps its seven steps and `paint` its five phases. It ships as a new `genjutsu:shared:preview` guarded region, byte-identical in both orchestrators and enforced by the existing CI drift check.
- New iron rule in both skills: **the preview is throwaway and never becomes the implementation.** This matters most on Compose / SwiftUI, where an HTML preview approximates timing and curve only, not rendering - and now says so on the page. Supporting rules: the live-preview route is deleted after validation, no dependency is installed to build a preview, no dev server is started without asking, and only values that are already in the thesis may appear in it (otherwise the preview becomes a second, unvalidated thesis).

### Changed

- `allowed-tools` in `cast` and `paint` now includes `Artifact`. Artifact production degrades cleanly across surfaces: native on claude.ai, the `Artifact` tool on Claude Code, and a self-contained HTML file written to a temp path when neither is available.

### Notes

- `paint`'s page-by-page validation (Phase 4) is deliberately excluded - it is judged in the real project, where a preview would only add a copy step.
- The docs site ([genjutsu.athevon.dev](https://genjutsu.athevon.dev)) lives in a separate repository; its `cast` and `paint` pages do not describe the gate yet.

## v3.1.0 - 2026-07-24

Correctness + reach release: the design dataset is refreshed, the technical guidance is more accurate across every stack, and claude.ai now installs in a single upload.

### Added

- **Single-upload claude.ai bundle.** `package-for-claude-ai.sh` now produces `genjutsu.zip` - one self-contained skill (a router `SKILL.md` + `cast` + `paint` + every sub-skill) that installs in **one** upload instead of ~18. It resolves its sub-skills from its own bundled `_jutsu/`; the à-la-carte individual ZIPs still work unchanged. New install section + `docs/claude-ai-testing.md`. (#13)

### Changed

- **`ui-ux-pro-max` synced to upstream v2.11.0** ([nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), MIT). Data roughly doubled: 84 styles, 192 palettes, 74 font pairings, 161 UI-reasoning rows, 192 products, plus new `google-fonts` (1923) and `motion` datasets and 22 stacks. The engine gains the design dials (`--variance` / `--motion` / `--density`), `--force`, and a test suite. Now properly attributed (README credits + `UPSTREAM.md`). (#8)
- Item counts stated across the skill and README corrected to match the shipped data. (#8)

### Fixed

- **API accuracy across the sub-skills** (#7): Liquid Glass used non-existent `.glassEffect(.thin/.thick)` (iOS 26 `Glass` exposes only `.regular` / `.clear` / `.identity`); the Android reduce-motion signal `AccessibilityManager.areTransitionsEnabled()` does not exist (now `ValueAnimator.areAnimatorsEnabled()`); the `@Animatable` macro is iOS 26+, not 17+; CSS `inset-area` renamed to `position-area`; GSAP `ScrollTrigger.matchMedia()` deprecated (now `gsap.matchMedia()`) and all former Club plugins are free since 3.13; `.snappy` spring duration corrected.
- **claude.ai sub-skill resolution hardened** (#9): detect the mount robustly, warn instead of failing on a missing sub-skill, and stop the cache fallback from picking a stale clone.
- **`/cast`'s audit checklist drift** with `/paint` (missing web checks) fixed, plus a CI guard so the shared cast/paint blocks can no longer diverge silently. (#11)

### Security / hygiene

- Removed the agent-run `sudo` / `brew` / `winget` install commands from `ui-ux-pro-max` (supply-chain trust). (#8)
- Pinned CI actions to commit SHAs and added `homepage` / `repository` / `license` / `keywords` to `plugin.json`. (#10)

## v3.0.3 - 2026-07-23

### Fixed

- `paint`: the brainstorm question shown when the user tries to skip brainstorming was still in French and got emitted verbatim to the user. It is now English, matching the rest of the skill (same class of leak as #3, one occurrence had been missed).

### Changed

- Translated the `gsap` reference docs (`_jutsu/gsap/references/core.md` and `timeline.md`) from French to English, so the sub-skill is fully English like the rest of the plugin. Translation only, no API or code changes (the remaining French flagged in #3).

## v3.0.2 - 2026-07-23

### Security

- `ui-ux-pro-max`: the `--persist` flow no longer lets `--project-name` or `--page` escape the output directory. Both values were turned into filesystem paths with only lowercase + space-to-dash, so a `../` or an absolute value could write outside `design-system/` (an arbitrary-write primitive when the script is agent-driven). They now pass through a shared `safe_path_component()` that collapses each value to a single safe path segment. Thanks to @reevesc88 (#4).

### Fixed

- `cast` and `paint` now resolve `_jutsu` sub-skills from the installed plugin version via `${CLAUDE_PLUGIN_ROOT}`, instead of a `find | head -1` that could pick the marketplace clone (a stale version after `/plugin marketplace update`). A guarded, cache-restricted fallback covers the case where the placeholder is not substituted. Thanks to @malle-van-moa (#3).
- Removed a stale v2.0 rollout note in `cast` and `paint` that told the agent to skip the Compose/SwiftUI sub-skills; those shipped in v3.0.1 and the note contradicted the LOAD table above it. (#3)

### Changed

- Translated the remaining French user-facing strings in `cast` and `paint` (the legacy-bridge question and one DISCOVER example) to English. (#3)

## v3.0.1 - 2026-07-18

### Fixed

- Sub-skill resolution in `cast` and `paint` now works when genjutsu is installed via the marketplace. The `PLUGIN_ROOT` lookup is version-tolerant and matches the versioned cache layout (`~/.claude/plugins/cache/genjutsu/genjutsu/<version>/skills/`) in addition to git-clone installs. Previously the versioned path never matched, so all 15 `_jutsu` sub-skills failed to load on marketplace installs. Thanks to @SatishRockzz (#2).

## v3.0.0 - 2026-04-26

**BREAKING CHANGE - Rebrand**: `creative-excellence` is now `genjutsu`. The two orchestrators have new names that match the new theme.

### Renamed

- Plugin: `creative-excellence` -> `genjutsu`
- Orchestrator (creative coding): `creative-excellence` -> `cast` (The Illusionist)
- Orchestrator (design pipeline): `design-excellence` -> `paint` (The Master Painter)
- Internal sub-skills directory: `_creative/` -> `_jutsu/`
- GitHub repository: `AThevon/creative-excellence` -> `AThevon/genjutsu`

### Migration guide

**For users on Claude Code:**

```bash
# 1. Uninstall the old plugin
/plugin uninstall creative-excellence

# 2. Remove the old marketplace
/plugin marketplace remove creative-excellence

# 3. Add the new marketplace
/plugin marketplace add git@github.com:AThevon/genjutsu.git

# 4. Install
/plugin install genjutsu
```

Old invocations -> new invocations:

| Old | New |
|---|---|
| `/creative-excellence:creative-excellence` | `/genjutsu:cast` |
| `/creative-excellence:design-excellence` | `/genjutsu:paint` |

**For users on claude.ai:**

1. Remove the old `creative-excellence` and `design-excellence` skills from your skills list.
2. Re-download the latest release ZIPs (now named `cast.zip`, `paint.zip`, plus the renamed `genjutsu-all.zip`).
3. Re-upload everything.

**For users with the dotfiles submodule pattern:**

```bash
cd ~/.dotfiles

# Deinit the old submodule
git submodule deinit -f claude/plugins/creative-excellence
git rm -rf claude/plugins/creative-excellence
rm -rf .git/modules/claude/plugins/creative-excellence

# Re-add with the new URL
git submodule add git@github.com:AThevon/genjutsu.git claude/plugins/genjutsu

# Update install.sh and settings.json (replace creative-excellence with genjutsu)
# Then run install
./install.sh
```

### Added

- Voice rules in both `cast/SKILL.md` and `paint/SKILL.md`: light ninja flair during execution, plain factual reports at the end (no mystic prose in summaries).

### Notes

- Zero functional change. All sub-skills (`motion-principles`, `gsap`, `compose-motion`, `swiftui-graphics`, etc.) work identically. Only naming and voice changed.
- The old GitHub URL `github.com/AThevon/creative-excellence` automatically redirects to the new one.

## v2.0.0 - 2026-04-25

Major release: cross-platform expansion. The plugin now covers Web, Android (Jetpack Compose / Compose Multiplatform), and Apple (SwiftUI iOS + macOS) in addition to the existing web stacks.

### Added

- New shared layer `mobile-principles` (touch targets, no-hover doctrine, thumb zones, safe areas, gestures, mobile perf budgets) with 2 deep-dive references (`gestures-deep.md`, `accessibility-mobile.md`).
- New shared layer `desktop-principles` (hover-mandatory, pointer precision, keyboard shortcuts, multi-window, focus management) with 2 deep-dive references (`keyboard-patterns.md`, `multi-window.md`).
- New stack `compose-motion` (Jetpack Compose animation foundations: `animate*AsState`, `AnimatedVisibility`, `SharedTransitionLayout`, springs, gestures) with 3 deep-dives (`shared-transitions.md`, `gestures-compose.md`, `recomposition-and-anim.md`).
- New stack `compose-graphics` (advanced Compose visuals: M3 Expressive motion physics, AGSL shaders Android 13+, Canvas/DrawScope generative) with 3 deep-dives (`agsl-recipes.md`, `m3-expressive-deep.md`, `canvas-generative.md`).
- New stack `compose-multiplatform` (KMP/CMP patterns, expect/actual, iOS/Android/Desktop interop) with 2 deep-dives (`cmp-interop.md`, `cmp-platform-quirks.md`).
- New stack `swiftui-motion` (`withAnimation`, transitions, `matchedGeometryEffect`, `PhaseAnimator`, `KeyframeAnimator`, gestures) with 3 deep-dives (`springs-cheatsheet.md`, `phase-keyframe-deep.md`, `gestures-swiftui.md`).
- New stack `swiftui-graphics` (Metal shaders, `.visualEffect`, Liquid Glass iOS 26, Canvas) with 3 deep-dives (`metal-recipes.md`, `liquid-glass-deep.md`, `canvas-swiftui.md`).
- Stack-aware MASTER.md generation in `design-excellence` (now `genjutsu:paint`): produces Tailwind/CSS for web, Kotlin Theme.kt for Compose, Swift extensions for SwiftUI, KMP commonMain for CMP.
- Cross-platform AUDIT checklist in both orchestrators (Layout Inspector, Macrobenchmark, Instruments Time Profiler, Hitches Instrument, GPU Frame Capture).
- Conditional DISCOVER question for legacy bridge integration (XIB / storyboard / layout XML / setContentView detection).

### Changed

- Phase SCAN extended in both orchestrators to detect Android Compose (`androidx.compose`), Compose Multiplatform (`org.jetbrains.compose` + `kotlin-multiplatform`), SwiftUI (Package.swift / xcodeproj / @main App), and to distinguish iOS vs macOS targets.
- Phase LOAD restructured into layered tables (foundation always / context layers by detection / stack-specific by SCAN). Advanced sub-skills (`compose-graphics`, `swiftui-graphics`) only loaded for advanced thesis containing terms like "shader", "Metal", "AGSL", "Liquid Glass", "M3 Expressive".
- IRON RULES 7-8 generalized to be stack-agnostic (previously React/GSAP-specific).
- THESIS examples extended with cross-platform examples (SwiftUI matchedGeometryEffect, Compose SharedTransitionLayout, macOS hover, AGSL shader).
- `motion-principles` reduced-motion section now covers 5 platforms (Web CSS, Web JS, SwiftUI, UIKit, Compose) with code examples.
- `motion-principles` Universal Do Not Rules now include native (SwiftUI + Compose) BAD/GOOD examples in addition to CSS/JS/GSAP.
- `design-audit` now greps multi-stack (web + Compose + SwiftUI), reports bundle sizes for native libs (Lottie/Rive), and includes a stack-specific audit subsection (Layout Inspector / Macrobenchmark / Instruments Time Profiler / Hitches / GPU Frame Capture).

### Notes

- Zero web regression: existing web sub-skills (`gsap`, `framer-motion`, `css-native`, `threejs-r3f`, `canvas-generative`) and `ui-ux-pro-max` are unchanged.
- The plugin grows from 8 sub-skills to 15. The `package-for-claude-ai.sh` script automatically picks up new sub-skills (no script change needed).

## v1.1.0 and earlier

See git tags for details on previous releases.
