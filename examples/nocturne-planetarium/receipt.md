# nocturne-planetarium - receipt

`/genjutsu:paint` on a new product: the landing page for Nocturne, the late program of a fictional planetarium in Lisbon, with the real sky over Lisbon at 22:00 on Friday 9 October 2026 as its hero (data/stars.json: Yale Bright Star Catalogue, IAU star names, NASA JPL Horizons). React 19 + Vite + TypeScript, plain CSS, no animation library (template react).

## The prompt

> /genjutsu:paint build the landing page for Nocturne, the late program of a planetarium in Lisbon.
>
> The brief. The planetarium and its program are fictional, made up for this example: give the planetarium no name and do not name or suggest any real planetarium or venue. This is everything it has given us:
>
> - Nocturne is the planetarium's after-hours program. On Friday and Saturday nights the dome first shows the night sky above Lisbon as it is that evening, with a narrator, then a 40-minute show. Doors 21:30, first show 22:00, last show 23:30. Tickets 12 EUR, 8 EUR for students, booked at /tickets.
> - The hero is the sky over Lisbon as the dome will show it at 22:00 on Friday 9 October 2026. data/stars.json holds the brightest stars of the Yale Bright Star Catalogue (public domain) and the one bright planet above the horizon then, Saturn (from NASA JPL Horizons), with their altitude and azimuth already computed for that place and time, their magnitude and, for stars, their proper name when they have one. It also lists the Moon and the other planets, which are below the horizon or too faint at that time: do not draw them. Use it. Do not invent stars, constellation lines, events or claims that are not in the data or in this brief.
> - The page scrolls from dusk to the first show: the program, what is in tonight's sky, the practical information.
> - It is for adults in their 20s to 40s looking for an evening out, not school groups. There are no reviews and no attendance numbers yet: the program launches with this page.
>
> Nobody is available to answer questions during this session. Up-front answers to the gates:
> - Preview mode: A. Write each preview as a standalone HTML file under preview/ in the project.
> - Scope: the landing page. You may write src/, index.html, public/, preview/ and MASTER.md; create nothing outside the project.
> - Dependencies are installed (node_modules is present) and `npm run build` works. There is no network: install nothing. Do not start a dev server.
>
> Finish with the final report the pipeline asks for.

## The run

| | |
|---|---|
| genjutsu | 4.1.0 at commit `09c177b` |
| Model | `claude-opus-5-5` |
| Harness | `claude plugin eval`, Claude Code 2.1.289, headless: nobody answered the gates |
| Date | 2026-10-04 |
| Cost | $2.53 (the run shown); $4.91 for both runs recorded |
| Turns | 34 |
| Duration | 496 s |
| Selection | selected from 2 runs (run 1 shown, see below) |
| Human edits | 0 (builds as the run left it) |

Modules loaded (from the trace: one `load_skill` / `load_ref` call, then `cat` of each module's SKILL.md): tells, ui-ux-pro-max, motion-principles, css-native, mobile-principles, design-audit; reference `tells/references/web.md`; scripts `ui-ux-pro-max/scripts/search.py --design-system` (dials variance 6, motion 3, density 3), `design-audit/scripts/audit.py` (full) and `audit.py --group tells`.

The run hit the 4.1.0 resolver bug (Claude Code substitutes `$1`/`$2` in the skill's loader block with words of the typed request). Its report says so: "its module-loading block had a substitution error (`the/` where the module name should be). I used a corrected loader with the same lookup order." Fixed on fix/skill-arguments for 4.1.1.

The paint skill itself came in through the `/genjutsu:paint` slash command, not a Skill tool call, so the harness graders `paint-fired` and `paint-loaded` scored it as not loaded (case score 0.33 on both runs). The trace shows the skill's pipeline running (theses, MASTER.md, previews, audit, final report).

## What it proposed

Marked **UNVALIDATED** in its own report: "Nobody was available to approve the theses or the design system, so both are **UNVALIDATED**."

**Visual thesis** (from the final report):

> the page is the dome at night.
> - Ground: dusk blue (#1a2747) at the top, darkening to night (#06080f) as you scroll.
> - Hero: the 22:00 Lisbon sky drawn from `data/stars.json`. Stars are sized by magnitude and tinted by their catalogue B-V colour; Saturn is marked and named.
> - Accent: one dim red (#ef7b6a), used only for booking. It is the light people read star charts by in the dark.
> - Type: the system sans, weight 300 for display and 400 for body, tabular figures, no monospace. There is no webfont because the build is offline.
> - Spacing and shape: airy, 8px base, a sticky dome beside the text on wide screens, flat with 1px hairlines and 2px radii.

**Interaction thesis:**

> the sky follows the scroll, never a timer. The ground goes from dusk to night and stars appear by magnitude, from 1.5 down to 4.5.
> - Hover and focus are 160ms `cubic-bezier(0.2, 0, 0, 1)`, colour and opacity only. The ring that marks a chosen star uses the same curve.
> - Forbidden: scroll reveals, parallax, twinkling or any other loop, bounce, scale, a scroll cue.
> - Reduced motion shows the full sky from the start and sets every transition to 0ms.

**Allowed patterns:**

> the dome chart from the data, its hairline altitude circles (0/30/60°) and N/E/S/W letters, a dark ground, the scroll-linked sky, tabular figures, a 1px rule between star-table rows, the Saturn ring marker, the dim red accent.

It showed before it built: `preview/thesis.html` (the real dome in a scrollable page, the easing curve, a reduced-motion toggle) and `preview/design-system.html` (tokens, contrast, five states of each component). Both written before any file under `src/`.

## Audit (its own)

> Audit: 11 checked, 3 problems found, 3 handed over

Problems it found: (1) Important: on narrow screens, choosing a star rings it on the dome, but the dome has already scrolled out of view; (2) and (3) nice-to-have: a few literal numbers in `Dome.tsx` and the media-query breakpoints are not tokens.

Tells: `audit.py --group tells` returned 0 of 18. One static finding (`hover-no-transition`) argued as a false positive.

The run could not build or open a browser (no Node runtime in the sandbox); it checked the TypeScript by reading it and handed over `npm run build`, a performance trace, the 375 / 768 / 1024 / 1440 px check and the reduced-motion check as UNVERIFIED.

## Selected from 2 runs

Both runs built clean on the first try with node_modules copied from the template (build-1/, build-2/). Each first screen and a still at half the scroll range, 1440x900: `media/desktop.png` and `media/run-1-mid.png` for run 1, `media/run-2-first.png` and `media/run-2-mid.png` for run 2.

**Run 1 is shown.** Why:

- Run 2's first screen has a visible defect: the display word "Nocturne" (Futura at 9rem) is 622 px wide in a 460 px text column, so it runs 114 px under the sky chart and the final "e" is hidden behind the chart's disc (measured in the page: title right edge 766 px, chart left edge 652 px). Run 2 handed "1440px: nothing clipped" over as UNVERIFIED; it fails.
- Run 1 carries the brief's own structure, "the page scrolls from dusk to the first show", in the hero itself: the dome is sticky, the ground darkens with the scroll and the stars come out by magnitude until full night at the practical section. Run 2 draws the full sky at once (a one-time fade-in by magnitude on load) and draws the same chart a second time further down.
- Run 2's hero sky is the richer first image (all 403 stars with halos at load), and its hover label on the chart is a nice touch. Run 1's first screen shows only the brightest few bodies, by design (dusk). That is the cost of the choice.

Run 2 for the record: $2.38, 33 turns, 452 s, same modules, same resolver note, "Audit: 12 checked, 3 problems found, 3 handed over", previews `preview/thesis.html` and `preview/design-system.html`.

## Build

`npm run build` succeeded on the first try for both runs. Human edits: 0, no `edits.diff`.

## The sky against data/stars.json

Checked on the built page, not on its code (`takes/sky-check.json` probe, `takes/sky-check.py`):

1. With reduced motion (every magnitude group at opacity 1), the page draws 403 star discs; the data lists 403 stars. Saturn is the only planet drawn; no Moon, no other planet, no constellation lines.
2. For each star, its expected place was worked out from its alt/az in the data, for a chart seen from below (zenith at the centre, horizon at the rim, north up, east left), scaled by the horizon circle the page drew (radius 470 of a 1000 viewBox). Every star has a drawn disc within 0.07 viewBox units of that place (rounding of the drawn coordinates). The 403 stars land on 401 distinct discs because the catalogue lists 79 Zeta UMa and 13 Delta Ser twice at the same position. Saturn's disc is exactly at its expected place.
3. Orientation from the data alone: Capella (az 40, north-east) is drawn upper left, Altair (az 225, south-west) lower right.
4. In the screenshot, the pixel at the expected screen position of each of the ten brightest named stars (Vega, Capella, Altair, Fomalhaut, Deneb, Alnair, Alioth, Mirfak, Dubhe, Kaus Australis) and of Saturn is a lit star pixel (for example Vega (227, 233, 255), Capella (255, 230, 196), Saturn (233, 207, 154)) on a sky of (6, 8, 15); the labels Vega, Capella, Altair, Fomalhaut, Deneb, Mirfak and Polaris sit 8 px right of their discs.

The page's text claims (Saturn 34° up in the east-south-east, magnitude 0.36, only Vega and Capella brighter; Moon new, 0.8% lit, below the horizon; Deneb 78° up; Polaris 38.8° up against Lisbon's 38.7° N) all restate the data.

## Media

| File | What | Viewport | Output |
|---|---|---|---|
| `media/clip.webp` | 3 s hold on the hero at dusk (nothing moves: the hero has no time-based motion and does not react to the pointer, so no pointer pass), then a steady 5 s scroll through the whole page: the ground darkens and the stars come out by magnitude on the sticky dome | 1440x900 | 1200x750, 41 frames, 8 fps, 8.7 s, 563,894 bytes (551 KB) |
| `media/desktop.png` | Desktop first screen (dusk: only the brightest bodies) | 1440x900 | 1440x900 |
| `media/mobile.png` | Mobile first screen: the intro only, the sky is below the fold | 390x844 @2x | 780x1688 |
| `media/mobile-sky.png` | Mobile, the pinned dome at the end of its pin (full night) | 390x844 @2x | 780x1688 |
| `media/full-desktop.webp` | The whole page as loaded (scroll 0, dusk), one tall capture; the sticky dome is drawn once, where it sits at load | 1440 wide, 3529 tall document | 1000x2451, static, 65,102 bytes |
| `media/reduced.png` | prefers-reduced-motion: reduce; first screen, full sky and night ground from the start | 1440x900 | 1440x900 |
| `media/preview.png` | preview/thesis.html, the thesis page the run wrote before touching src/, scrolled to 45% (limiting magnitude 3.09) | 1440x900 | 1440x900 |
| `media/design-system.png` | preview/design-system.html, first screen: colour tokens with contrast | 1440x900 | 1440x900 |
| `media/run-1-mid.png` | Selection still, run 1 at half the scroll range | 1440x900 | 1440x900 |
| `media/run-2-first.png` | Selection still, run 2 first screen (the clipped "Nocturne") | 1440x900 | 1440x900 |
| `media/run-2-mid.png` | Selection still, run 2 at half the scroll range | 1440x900 | 1440x900 |

Notes:

- Captured with bin/record.mjs: the static build served from disk over CDP, no server, virtual time. Takes are in takes/. No console errors, uncaught exceptions or failed requests in any take.
- clip.webp: record.mjs's own encoding ladder only got under 600 KB at 600 px wide (the ground colour changes every frame, so every frame is new). The frames it kept at 24 fps were re-encoded with `takes/encode-clip.sh`: every 3rd frame of the scroll (8 fps), quality 30, 1200x750, and the 3 s hold (72 identical frames, checked byte for byte) stored as one frame shown for 3000 ms. 8.7 s, a little under the 10 s asked, to fit the budget at 1200 px.
- full-desktop.webp: record.mjs has no full-page mode; `takes/fullpage.mjs` serves the build the same way and takes one `captureBeyondViewport` screenshot at scroll 0.

## Defects the run introduced

- **Narrow screens, the star list rings a dome you cannot see** (the run's own Important finding, confirmed): at 390x844, after scrolling to the list and choosing a star, the ring turns on while the dome is 1241 px above the viewport.
- **Mobile first screen has no sky**: the brief makes the sky the hero, but at 390x844 the first screen is the intro alone, with empty space under the button; the dome only pins after it.
- **Mobile facts grid**: "12 EUR, students 8 EUR" wraps onto two lines and "Last show 23:30" beside it is pushed down out of line (visible in mobile.png).
- Not a defect, worth knowing: on desktop the first screen shows only Capella, Vega, Deneb, Altair, Fomalhaut, Saturn and a half-faded Alnair; the other stars come in with the scroll. That is the thesis, and a reader who never scrolls sees a sparse sky.
