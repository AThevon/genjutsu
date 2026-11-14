<p align="center"><img src="./assets/logo.png" alt="genjutsu logo" width="160" /></p>

<h1 align="center">genjutsu</h1>

<p align="center"><em>The art of illusion.</em><br />
Claude Code skills that make an interface move, give a product its look, and build a whole website.</p>

<p align="center"><a href="https://genjutsu.athevon.dev"><strong>Website</strong></a> · <a href="#examples"><strong>Examples</strong></a> · <a href="https://genjutsu.athevon.dev/docs"><strong>Documentation</strong></a> · <a href="https://genjutsu.athevon.dev/docs/install"><strong>Install</strong></a> · <a href="https://github.com/AThevon/genjutsu/discussions"><strong>Discussions</strong></a></p>

<p align="center">
  <a href="https://github.com/AThevon/genjutsu/releases/latest"><img src="https://img.shields.io/github/v/release/AThevon/genjutsu?style=flat-square&color=b11523&label=release" alt="Latest release" /></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-b11523?style=flat-square" alt="MIT license" /></a>
  <img src="https://img.shields.io/badge/tested%20on-Claude%20Code-b11523?style=flat-square" alt="Tested on Claude Code" />
  <a href="https://github.com/sponsors/AThevon"><img src="https://img.shields.io/badge/sponsor-b11523?style=flat-square&logo=githubsponsors&logoColor=white" alt="Sponsor on GitHub" /></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/AThevon/genjutsu-examples/readme-2026-11-06/readme-media/hero-site.webp" alt="A tour of the genjutsu.athevon.dev homepage, laid out as an animation production sheet. A pointer carries a lens over the brushed character 幻, and under it the ink gives way to the curves and brush footprints it is drawn from. Cut to cast: a blue ring clicks an album in a demo gallery and its cover grows into the album page. Cut to paint: a dark screen annotated in blue pencil with its type, colour and timing values. Cut to bunshin: the page scrolls and a line inks down the phases, forking into clones. Last cut: the install command." width="800" /><br />
  <sub>genjutsu.athevon.dev, built with genjutsu: the lens on the 幻, then one cut each for cast (a demo drawn for the page), paint and bunshin.</sub>
</p>

Three skills for [Claude Code](https://claude.ai/code): `cast` animates one interface, `paint` designs a product's look, `bunshin` builds a whole website with a team of agents. The modules cover Web (React, Vue, Svelte, Astro, plain CSS, Three.js, Canvas), Android (Jetpack Compose, Compose Multiplatform) and Apple (SwiftUI); `bunshin` is web only for now. Developed and run on Claude Code only, with one SwiftUI case and no Android run recorded: [what is tested and what is not](#what-is-tested-and-what-is-not).

## Install

```bash
npx skills add https://genjutsu.athevon.dev -g
```

Then describe the task in Claude Code, or type `/genjutsu`. Update with `npx skills update -g`; the `-g` installs for your user instead of into the repository your terminal is in. Use the URL, not the repository: `npx skills add AThevon/genjutsu` installs the skills without their modules.

Or install it as a Claude Code plugin, from inside a session, which adds `/genjutsu:cast`, `/genjutsu:paint` and `/genjutsu:bunshin`: run `/plugin marketplace add AThevon/genjutsu`, then `/plugin install genjutsu`. Project scope, claude.ai, Cowork, other agents (untested) and what `bunshin` needs installed with it are in the [install guide](https://genjutsu.athevon.dev/docs/install).

## Three scales

| | You ask, for example (not a recorded run) | You get |
|---|---|---|
| [**`cast`**](https://genjutsu.athevon.dev/docs/cast)<br />one interface moves | "make the pricing cards feel physical on hover" | An interaction thesis you approve, then the code in the stack you already use, with a short audit of what it wrote. |
| [**`paint`**](https://genjutsu.athevon.dev/docs/paint)<br />a product's whole look | "build me a portfolio from scratch" | A brainstorm, a visual and an interaction thesis, a `MASTER.md` design system, the page and a full audit. On a project that already has a design, it asks first what to keep. |
| [**`bunshin`**](https://genjutsu.athevon.dev/docs/bunshin)<br />a whole site, by a team of agents | "redesign our architecture practice's whole site from the current one and our project PDFs" | It states its cost and asks you for the tier and the direction. An art director agent then runs research, one builder per page, reviewers and fix rounds. You get the site and a report of what was verified and what was not. |

Not sure which one? Describe the result you want and genjutsu picks the skill. The [FAQ](https://genjutsu.athevon.dev/docs/faq) has the long answer, and the docs list [the modules](https://genjutsu.athevon.dev/docs/jutsu) the skills load.

## Examples

Three recorded runs, one for each skill; the `bunshin` one predates the skill, which was extracted from it. Each links its receipt: how it ran, the cost that was measured, and what it got wrong or left unverified. The clips are filmed from the code each run left; Chef Ovatio is filmed from the live site, after one human edit. They ran on genjutsu 4.0.0 and 4.1.x, before the current release.

<!-- genjutsu:examples:start -->
### `cast` · Folio: the "Mark as paid" action (Motion)

<a href="https://github.com/AThevon/genjutsu-examples/blob/readme-2026-11-14/invoice-mark-paid/receipt.md"><img src="https://raw.githubusercontent.com/AThevon/genjutsu-examples/readme-2026-11-14/readme-media/invoice-mark-paid/clip.webp" alt="Two Mark as paid clicks on the Folio invoice list: each time the button slides out, the status pill stamps to Paid, and the Outstanding and Paid totals count by the invoice amount." width="720" /></a>

On a fixture invoice page, asked to make a dead "Mark as paid" action feel like the money landed, the run made the amount leave Outstanding and land in Paid as both totals count, in one headless pass.

<sub>one-shot headless run · `claude-opus-5-5` · first pass · $1.88 · 0 human edits · 2026-10-04. Its thesis was approved by nobody. Defect its own audit missed: on a shorter window than the clip's, the page scrolls while the totals count. The pointer is drawn in by the recorder, not by the build.</sub><br />
[Receipt](https://github.com/AThevon/genjutsu-examples/blob/readme-2026-11-14/invoice-mark-paid/receipt.md) · [Live demo](https://genjutsu-examples.vercel.app/invoice-mark-paid/)

### `paint` · Nocturne: a planetarium's landing page (plain CSS)

<a href="https://github.com/AThevon/genjutsu-examples/blob/readme-2026-11-14/nocturne/receipt.md"><img src="https://raw.githubusercontent.com/AThevon/genjutsu-examples/readme-2026-11-14/readme-media/nocturne/clip.webp" alt="Scrolling the Nocturne page from dusk to night: the ground deepens from dusk blue to near black, the amber glow at the dome&#x27;s rim fades, and the stars come up on the dome brightest first; near the end, the star list passes over the dome." width="720" /></a>

Asked for a planetarium's landing page from an empty template and a star catalogue, the run drew 403 stars and Saturn as they stand over Lisbon at 22:00 on 9 October 2026, lit brightest first as it scrolls to night.

<sub>conversation with an agent playing the client · `claude-opus-5-5` · first pass · $5.93 (plus $0.86 for the client agent) · 0 human edits · 2026-10-04. Defect: from 1100 px wide the star list runs over the dome (end of the clip); two more in the receipt. The run could not open its page in a browser. A headless run of this brief came out plain first.</sub><br />
[Receipt](https://github.com/AThevon/genjutsu-examples/blob/readme-2026-11-14/nocturne/receipt.md) · [Transcript](https://github.com/AThevon/genjutsu-examples/blob/readme-2026-11-14/nocturne/transcript.md) · [Live demo](https://genjutsu-examples.vercel.app/nocturne/)

### `bunshin` · Chef Ovatio: a private chef's seven-page site (Astro)

<a href="https://github.com/AThevon/genjutsu-examples/blob/readme-2026-11-14/chef-ovatio/receipt.md"><img src="https://raw.githubusercontent.com/AThevon/genjutsu-examples/readme-2026-11-14/readme-media/chef-ovatio/clip.webp" alt="Scrolling the Chef Ovatio home: the yellow sky turns orange as the plate sinks into the cobalt sea, the header shrinks to a bar, then &#x27;La même cuisine, deux façons de la partager&#x27;, the Recevoir and Conseiller doors, and the &#x27;Ce qui arrive à table&#x27; section with its first plates." width="720" /></a>

A real private chef's site, seven pages in French and English, made from his public Instagram profile and two answers; scrolling the home, the plate sets like a sun behind a cobalt horizon.

<sub>the run `bunshin` was extracted from, made with genjutsu 4.0.0's `paint`, with Impeccable, before `bunshin` shipped · `claude-opus-5-5` · about 10.5M subagent tokens (main session not measured) · 1 human edit · 2026-09-29. The edit, made since: door titles that could not be read across their photos now stand on them. The last fix round was not reviewed. Filmed from the live site, whose contact details are still blank.</sub><br />
[Receipt](https://github.com/AThevon/genjutsu-examples/blob/readme-2026-11-14/chef-ovatio/receipt.md) · [Live demo](https://chef-ovatio.vercel.app)

Three of nine recorded examples. The other six, including the three that came out plain or thin and [the one SwiftUI case, six runs of one prompt](https://github.com/AThevon/genjutsu-examples/blob/readme-2026-11-14/etale-ios/receipt.md), are in [genjutsu-examples](https://github.com/AThevon/genjutsu-examples/tree/readme-2026-11-14); the site has its own gallery at [genjutsu.athevon.dev/examples](https://genjutsu.athevon.dev/examples).
<!-- genjutsu:examples:end -->

## How it works

`cast` and `paint` stop at a few gates (the interaction thesis, the visual identity, the design system) and ask once how you want to see the proposal: a rendered page with the easing curve plotted and a replay button, a throwaway preview route in your own project, or one sentence in the conversation. The preview route is deleted once you approve.

genjutsu keeps a catalogue of the defaults a model reaches for when nobody asked (the numbered eyebrow, three equal cards, an invented `ESTD. 2018`). One command lists them in any project with their `file:line`: [the tells field guide](https://genjutsu.athevon.dev/docs/tells).

## What is tested and what is not

genjutsu is developed and run on Claude Code with Claude models. The claude.ai bundle was last checked by hand on 2026-09-28, `cast` only ([log](./docs/claude-ai-testing.md#7-log)). No Cowork run is logged. `bunshin` has only been run on Claude Code, and its one recorded run predates the skill. One SwiftUI case is recorded (six runs of one prompt, four of which used the system transition, simulator only: [receipt](https://github.com/AThevon/genjutsu-examples/tree/main/etale-ios)) and no Android run. No other agent or model has been tested.

The measurements are small (one brief or one case, two to six runs each) and graded by us or by a model, so they are not an independent benchmark: [CHANGELOG, v4.2.0](./CHANGELOG.md#v420---2026-11-13), [baseline-2026-11](https://github.com/AThevon/genjutsu-examples/tree/main/baseline-2026-11). The rules were tuned on the baseline's one brief, where the pages came out level with Anthropic's frontend-design and a run cost about four times a run with no plugin. The with and without eval table dates from 2026-09-28 (on the branch that became v4.0.0) and has not been rerun: [last published result](./evals/README.md#the-last-published-result).

## Feedback and contributing

One minute, two answers: [how did it come out?](https://github.com/AThevon/genjutsu/issues/new?template=1-output.yml) A run that came out wrong is as useful as one that came out well. Every finished run ends with the same link, filled in with the skill and, when the run knows them, the version, the host and the model, and with nothing from your project.

Longer write-ups go to [Show and tell](https://github.com/AThevon/genjutsu/discussions/categories/show-and-tell), questions to [Q&A](https://github.com/AThevon/genjutsu/discussions/categories/q-a), ideas to [Ideas](https://github.com/AThevon/genjutsu/discussions/categories/ideas), bugs with a repro to [issues](https://github.com/AThevon/genjutsu/issues/new/choose).

The contribution that helps most is "this claim is wrong, here is the primary source". Start with [CONTRIBUTING.md](./CONTRIBUTING.md); the rows marked `VERIFY-NEEDED` in [`skills/_jutsu/VERSIONS.md`](./skills/_jutsu/VERSIONS.md) are the open work.

## Credits

genjutsu vendors the design dataset and search engine of [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT), hands `bunshin`'s direction and finish review to [Impeccable](https://impeccable.style) (Apache 2.0, not vendored) when it is installed, and took the idea of writing down a model's defaults from [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) (MIT, nothing copied). The detail and the 29 other sources it learned from are in [CREDITS.md](./CREDITS.md).

## License

[MIT](LICENSE). genjutsu is free; if it saved you a few rounds of generic output, you can [sponsor its development](https://github.com/sponsors/AThevon).

<p align="center">
  Built by <a href="https://athevon.dev"><strong>Adrien Thevon</strong></a>, software engineer in Toulouse. Also mine: <a href="https://github.com/AThevon/TokenEater">TokenEater</a>, a native macOS monitor for Claude usage limits, and <a href="https://github.com/AThevon/worktigre">worktigre</a>, a git worktree manager.<br />
  <sub>Formerly <code>creative-excellence</code> (v2.x): the migration steps are in <a href="./CHANGELOG.md#v300---2026-04-26">CHANGELOG.md, v3.0.0</a>. Not related to Higgsfield Genjutsu, the video tool.</sub>
</p>
