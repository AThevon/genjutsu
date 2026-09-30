---
name: orchestration
description: "Running a team of subagents on one design build: clone briefs, disjoint file ownership, isolated builds, the evidence packet, review lenses, the fix plan, verdicts, cold eyes and the stop rule, with the workflow templates bunshin runs."
metadata:
  internal: true
---

> **Version-sensitive.** The workflow tool contract (`scriptPath`, `args`, `agent`, `parallel`,
> `phase`) and the Impeccable verbs named here were checked on **2026-09-30**. What against is
> in `_jutsu/VERSIONS.md`, section "Orchestration". If that date is old, re-check before relying
> on a verb.

# Orchestration

> Loaded by `/genjutsu:bunshin`. One art director, many clones. This module is how the clones
> are briefed, fenced, checked and stopped, so that ten agents in parallel produce one site and
> not ten opinions.

A clone is a subagent. It starts from nothing: no conversation, no memory of the thesis, no idea
which files its siblings are editing. Everything it knows is in its brief. Everything that goes
wrong in a fan-out goes wrong because a brief left something out.

---

## The five templates

Each phase that fans out has a template under `workflows/`, next to this file. Each one is a
workflow script: a pure `meta` literal, then a body that calls `agent()`, `parallel()` and
`phase()`, parameterised entirely by `args`. `scripts/check-workflows.mjs` runs every template
against stubs in CI: to the end with every agent answering, and again with every agent
answering null, where a template must end or stop on its own named error (`research.js` and
`review.js` do, with nothing to synthesise or plan), never crash. `build.js` and `refine.js`
share one isolated-build block, which the check holds identical in both.

| Template | Phase | Clones | Writes to disk | Returns |
|---|---|---|---|---|
| `research.js` | 3, research | 4 angles, then 1 synthesis | the synthesis, at `args.out` | per angle the URLs read and the patterns; the synthesis |
| `build.js` | 7, build | 1 per owner, each capturing its own page when `build` names `static`, `shoot` and its `routes` | the owner's files | per owner: files, summary, open questions, shared change requests, build status |
| `review.js` | 9, review | 1 per lens (the finish lens asked twice when its first answer is empty), then 1 plan (none on recapture or rebuild) | each lens's review beside `args.planOut`, and `{ round, disposition, reviews, plan }` at `args.planOut` | the round, the disposition and its recapture list, per lens its overall verdict and a finding count, the plan (null on recapture or rebuild) |
| `refine.js` | 10, refine | the shared owner alone, then 1 per owner | the owners' files | per owner: done, not done, files, build status, notes |
| `verdict.js` | 10, verdict | the finish reviewer, plus cold eyes when asked, then 1 to write the plan | the next round's plan at `args.planOut`, built by the script from the finish reviewer's remaining points | both verdicts, and the plan path |

The header comment of each template documents its `args`. Read it before the call; do not guess
a field.

**Running one.** When the session has a workflow tool (Claude Code: `Workflow`), pass the
template by path and its arguments as a JSON value, never as a JSON string:

```
Workflow({ scriptPath: "<SKILL_BASE>/orchestration/workflows/review.js", args: { ... } })
```

`<SKILL_BASE>` is the absolute path the skill-base block printed (`genjutsu: modules from ...`).
The call returns at once; the result arrives when the workflow finishes. Do not poll it.

**Without a workflow tool, with a subagent tool** (Claude Code: `Agent`; other hosts name it
differently): the template is the plan. `node "$SKILL_BASE/orchestration/scripts/brief.mjs"
<template> <args.json>` prints every clone it would spawn, with its label, agent type, schema and
exact prompt, so nothing is rebuilt by hand. Spawn them several in one message when the host runs
them concurrently, one by one otherwise, each schema as the "return exactly this JSON" part.
Calls marked `afterAnswers` carry a placeholder where an earlier answer goes: rebuild those
prompts with the real answers.

**Without either**, there are no clones. bunshin does not run: say so and step down to `paint`.
Never play ten clones in one context: that is one long session reviewing its own work, which
is exactly what the independent lenses exist to avoid.

**Return small, write big.** A template returns what you need to decide the next step and
writes the rest to disk: the full reviews go into the plan file, not into your context. Keep it
that way when you adapt one.

---

## The brief every clone gets

A brief has six parts, in this order. A clone that is missing one of them improvises it.

1. **Who it is and what it builds.** One paragraph: the project, the page or the lens, the
   audience, the main channel. The project named by its absolute path.
2. **What to read first, in order, by absolute path.** PRODUCT.md, the direction contract (the
   surface brief), the quality floor, the design system files, the reference surface you built
   yourself. "Read the codebase" is not a list.
3. **What it owns.** The exact files and globs it may write. Everything else is read-only, and
   the brief says so. See "Ownership" below.
4. **The rules that do not move.** The validated theses with their forbidden patterns and their
   `Allowed patterns:` line, the tells the thesis does not allow, the voice, the truth rule
   (nothing invented, unknown facts generic on the page and marked in the content file), mobile
   first, reduced motion. Copy them in: a clone cannot read the conversation where they were
   agreed.
5. **How it verifies.** The isolated build recipe, exact, with the framework binary. What counts
   as green.
6. **What it returns.** A schema. Free text from ten clones is ten formats to reconcile.

Add a seventh part when it applies: **what is already verified**, so reviewers do not spend a
lens re-reporting a green build.

Write the brief so it survives being read by a model that has never seen the project. If a
sentence only makes sense with the conversation behind it, rewrite it.

---

## Ownership

Parallel clones on one working tree are safe only when no two of them write the same file.

- **One owner per file, declared before the fan-out.** Split by surface: each page owns its view,
  its content file and a components folder of its own. Everything used by more than one page
  (styles, layouts, shared components, scripts, the content model's common files, the framework
  config) belongs to one owner, named `shared`, or to you.
- **Page clones never edit shared files.** A shared need goes back as a
  `shared_change_requests` entry: the file, the change, why. You apply them, or you give them to
  the `shared` owner in the next round. Two clones editing the global stylesheet at once is how a
  fan-out ends in a merge by hand.
- **When a shared contract changes, `shared` runs first and alone**, then the others run with
  its notes (`refine.js` does this). A page clone that codes against a component prop that does
  not exist yet breaks its own build.
- **The owner map is data.** Keep it in `.bunshin/owners.json`, every owner included. Pass all of
  it to `review.js` and `verdict.js`, so the plan can assign any file; a file no owner lists goes
  to `orchestrator`, which is you. Pass `build.js` only the page owners you did not build
  yourself, each with its `mission`: never `shared`, never the signature surface. Pass
  `refine.js` only the owners that have fixes, or rules of the decisions file that touch their
  files.
- **Every route exists before the fan-out.** Route files are shared: create each page's route in
  every language before `build.js` runs, so a clone's page builds and captures from its first run.

---

## Isolated builds

Clones build in parallel. A build in the shared working tree reads files other clones are
halfway through writing, and every clone chases errors that are not its own.

Each clone builds in a copy of its own, outside the project:

```bash
D='<scratch>/build-<owner>'; rm -rf "$D"; mkdir -p "$D"
rsync -a --exclude '/node_modules' --exclude '/dist' --exclude '/.git' --exclude '/.bunshin' \
  --exclude '/.claude' --exclude '/.agents' --exclude '/.impeccable' \
  --exclude '/.astro' --exclude '/.vercel' --exclude '/.next' --exclude '/.svelte-kit' '<root>/' "$D/"
mkdir -p "$D/node_modules" && find '<root>/node_modules' -mindepth 1 -maxdepth 1 \
  ! -name .astro ! -name .vite ! -name .cache -exec ln -s {} "$D/node_modules/" \;
cd "$D" && ./node_modules/.bin/<framework> build > "$D/.bunshin-build.log" 2>&1; echo "build exit code: $?"; tail -30 "$D/.bunshin-build.log"
```

`build.js` and `refine.js` generate exactly this, with every path quoted.

- **The framework's own binary, never the package manager.** In a copy linked to the project's
  `node_modules`, `pnpm build` decides the install is foreign and reinstalls through the links
  into the real one. The binary just builds. The templates refuse a package manager as `cmd`.
- **Link `node_modules` entry by entry, not as one link.** Frameworks keep caches inside it
  (Astro writes `node_modules/.astro` by default): one link to the whole folder makes parallel
  clones write into the project's own cache at once. Linked entry by entry, each copy gets its
  own cache.
- **Exclude the build output and every cache the framework keeps** (`.astro`, `.vercel`, `.next`,
  `.svelte-kit`, `.output`, ...), so a stale output never passes for a fresh build, and a clone
  never captures yesterday's page.
- **Green means the printed exit code is 0.** A build piped into `tail` exits with `tail`'s code.
- An error in a file the clone does not own is not its problem: retry once later, then report it.
- `<scratch>` is an absolute path outside the project, resolved before the call: the session's
  scratch directory when the host gives one, else the value of
  `printf '%s\n' "${TMPDIR:-/tmp}/bunshin-<project>"`. The templates quote it, so an expression
  passed as a path would never be expanded, and they refuse one that is not absolute.

---

## The evidence packet

Reviewers judge what renders. Before any review or verdict, you produce, and the packet names:

- **Captures** of every page at 390x664 (the height the measured run used for a social app's
  in-app browser on a phone, not measured on a device; measure the real one when you can),
  390x844, 1280x720 and 1440x900: the first screen, and the full page cut into
  segments a reader can actually open (about 1700 px tall on mobile, desktop scaled to 1000 px
  wide). How to take them without a dev server is in `references/evidence.md`.
- **Sources and output**: the source folders and the built static output.
- **The request and the answers** of both gates, verbatim.
- **The contract**: PRODUCT.md, the surface brief (or `.bunshin/direction.md`), the quality floor:
  Impeccable's `reference/craft-floor.md`, or without it the `tells` module and its web
  reference, by absolute path.
- **The material**: `.bunshin/harvest/facts.md`, `missing.md` and `sources.json`, by absolute
  path: the truth lens holds every visible claim against them.
- **With Impeccable, the chosen world's QUALITY BAR**: the board and hero images of the chosen
  card, saved in `.bunshin/direction/`, named as the QUALITY BAR card; a decision comp, when one
  exists, named as a critique reference only.
- **Already verified**, with the evidence: build, type check, `impeccable detect`, the tells
  audit, overflow at each width, functional tests. Reviewers do not report these again unless
  they can show one is wrong.
- **History**, for the verdict only: the previous plan file, the refine results, the decisions
  file.

---

## The lenses

| Lens | Holds | Loads |
|---|---|---|
| `finish` | The render against the request, the answers and the direction contract. Gives the disposition: ship, fix, rebuild, recapture. With Impeccable installed, it is Impeccable's shipped finish reviewer, spawned fresh by the agent type the host lists (`finishAgent`), answering in its own contract (persistence, fidelity, ceiling, material fixes, keep), never a prompt that pastes its definition; it requires `.impeccable/review/desktop.png` and `mobile.png`. | the contract, the quality floor |
| `mobile` | The path from the main channel on a phone: the first three seconds, the thumb zone, sticky bars, page length, forms, menus. | `mobile-principles` |
| `desktop` | Compositions, the grammar carried from page to page, hover states, first screens, repeated layout families, the signature motion and its reduced-motion path. | `desktop-principles`, `motion-principles` |
| `truth` | The copy: voice, consistency across pages, every claim against the sources, promises the owner will have to keep, the quality of each language. | the content files, the harvested facts |
| `tech` | Headings, alternatives, forms and their errors, keyboard paths, computed contrast, metadata and structured data, page weight, the largest image, any endpoint, behaviour without JavaScript, internal links. | the sources and the built output |

The lean tier merges `truth` and `tech` into `truth-tech` and drops `desktop`. Each lens gets
the same packet and never sees the others: a lens that has read another lens agrees with it.

Every finding carries a severity (critical breaks conversion, accessibility or credibility;
major hurts the perceived quality; minor is finish), a page, a viewport, the evidence, the issue,
one precise fix, and the files.

---

## The plan

The plan clone is the only one that sees every review. Its job is judgement, not concatenation:

- **Deduplicate**, then **verify every finding** against the code and the captures. A reviewer
  without a browser misreads a capture as often as a human does.
- **Reject with a reason**: wrong, out of scope, or against the direction the user validated.
  The validated direction outranks a reviewer's taste; the rejected list says so by name.
- **Settle contradictions** between lenses, once.
- **Group by owner**, with the owner map, so the fixes apply in parallel.
- **Prioritise**: P0 before anyone sees it, P1 high value, P2 finish.
- **Write every fix so it applies as written** by someone who never read the reviews. A file no
  owner lists goes to `orchestrator`: you apply those yourself, before refine.

The plan lands on disk (`.bunshin/reviews/round-1.json`), next to one file per lens that the lens
wrote itself, and `refine.js` clones read it from there. Never pass fifty fixes through `args`.
From round 2 on, `verdict.js` writes the plan: the finish reviewer gives each remaining point an
id, a priority and an owner, and the script builds the file refine reads.

---

## Verdict, and cold eyes

After a refine round, and after new captures:

- **The finish reviewer scores** every fix of the round and lists what stays open: resolved,
  partial or unresolved, and at most three regressions the fixes introduced, with no new hunt
  (Impeccable's scoring contract; the plain reviewer may also mark a fix not-verifiable). Its
  disposition is the loop's signal, and `verdict.js` builds the next plan from its remaining
  points, with an empty fixes list when nothing is left.
- **The cold-eyes art director** has read nothing: no review, no plan, no decision. It receives
  one scenario (how the audience meets the site) and says, in at most eight points, what still
  looks amateur or like a template. It sees what the scorers stopped seeing: the same image on
  three screens, one layout family everywhere, colour fields that talk too much, type that looks
  generic. In the run this pipeline comes from, its notes led to the two decision rounds that
  closed the build. The standard tier runs it in round 1's verdict, so that round 2 applies its
  decisions; the full tier at every verdict (after the last one, its notes go into the report);
  the lean tier does not run it.

**You turn cold-eyes notes into decisions, not into tasks.** Write `.bunshin/decisions/round-N.md`
as rules the next round applies everywhere: the one role of each hero image, where the saturated
colour is allowed and where reading happens on a neutral ground, the type roles, the shape of
controls, the shared contracts that change. Then run the next round against that file. A list of
eight tasks fixes eight spots; a rule fixes the pattern that produced them.

This is the one step you never delegate: deciding what the cold-eyes notes mean is art direction.

---

## The stop rule

The loop is refine, capture, verdict. It stops on a rule, never on a feeling. Read the finish
reviewer's disposition first:

0. **`recapture`**: the evidence failed, not the build. Recapture and run the verdict (or the
   review) again; nothing the invalid round said binds, and the round does not count. **`rebuild`**:
   rebuild the named regions yourself, then run a full review again, never a verdict pass; the
   round counts. `fix` and `ship` go to the rules below.
1. **The finish reviewer leaves nothing above minor**, and the cold eyes (when running) say ship
   or list minor points only. Ship.
2. **The tier's round cap is reached** (lean 1, standard 2, full 4). Stop, and report what is
   left, by severity.
3. **A round made nothing better** (the same critical or major points come back): stop, and
   report them as the decisions only the user can take.

Minor points left after the last round go into the final report. They are not a reason for one
more round.

---

## Cost, honestly

Figures from the one run this pipeline was measured on (a seven-page site in two languages), in
subagent tokens as the host reported them. The run: one review, three refine rounds (one from the
review, two from decisions files), two verdicts with cold eyes; about 10.5M tokens over six to
eight hours, with two human touches. The main session's own tokens were not measured. Per unit:
research about 0.6M; about 0.4M per page clone (2.3M for six); a five-lens review with its plan
about 1.6M; a refine round from a plan about 1.6M with eight owners; a refine round that applies a
decisions file about 1.75M; a verdict about 0.35M with cold eyes, half that without; the
documenter about 0.2M. The tiers bunshin offers are estimates built from these units.

Announce the estimate before the first clone, from the page count and the tier, and say where
the figures come from. After each workflow, note the agent count and, when the host reports it,
the tokens. Never pass a tier's round cap without asking.

---

## Red flags

| Thought | Reality |
|---|---|
| "The clones can read the conversation for context" | They cannot. If it is not in the brief, it does not exist for them. |
| "Two clones touching the stylesheet is fine, it is small" | One owner per file. A shared need is a request. |
| "`pnpm build` in the copy is simpler" | It reinstalls through the symlink. Use the framework's binary. |
| "The reviewers can judge from the code" | They judge what renders. Capture first. |
| "I'll pass the fixes in args, it is quicker" | The plan is a file. Clones read it from disk. |
| "Let the cold eyes read the reviews for context" | Then they are warm eyes. Nothing but the packet and the scenario. |
| "The cold eyes listed eight tasks, I'll assign them" | Turn them into rules in the decisions file first. |
| "One more round will get the last minor ones" | The stop rule decides. Minor goes in the report. |
| "No subagent tool, I'll simulate the clones myself" | Then there is no independent review. Step down to paint. |
