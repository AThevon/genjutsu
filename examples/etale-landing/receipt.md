# etale-landing - receipt

`/genjutsu:paint` on a new product: the landing page for Étale, a fictional cold-water swimming app for Aquatic Park, San Francisco, built from one real day of NOAA tide and current predictions (2 October 2026). React 19 + Vite + TypeScript, vanilla CSS, no animation library (template react).

## The prompt

> /genjutsu:paint build the landing page for Étale.
>
> The brief. Étale is a fictional product made up for this example, and this is everything its founders have given us:
>
> - Étale is an iPhone app for people who swim in the cold water of Aquatic Park, San Francisco, all year round. It answers one question before you walk down to the beach: when is the water slack (étale is the French word for slack water, the still moment between ebb and flood, when the current is weakest), and how strong the current runs between two slacks.
> - Its numbers come from two NOAA CO-OPS stations, and data/tide.json holds one real day of both, 2 October 2026, as fetched from NOAA: the tide predictions of station 9414290 San Francisco, and the slack water and current predictions of station SFB1204 (Alcatraz Island, southwest of, the closest predicted current station, in the bay off the cove). The file names each station, where it is, its datum and its units. Use those numbers and label each one with its date and its station. Slack water is not high or low tide: take the slack times from the current predictions. The app shows no water temperature, so the page must not either. Do not invent any other figure.
> - The swimmers it is for train there before work, mostly without a wetsuit. They already know the cove and read the tide themselves on a printed table or a weather site. They want the next slack window at a glance, and an alert the evening before.
> - What exists: an iOS beta on TestFlight. No Android, no web app, no prices, no user numbers, no testimonials. The page has one job: get a swimmer onto the TestFlight beta, at /beta.
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
| Cost | $2.87 (both runs: $5.61) |
| Turns | 42 |
| Duration | 534 s |
| Selection | selected from 2 runs (workspace-1) |
| Human edits | 0 (builds as the run left it) |

Which run is which: workspace-1 is the output of the harness's run 2/2 (trace `/private/tmp/e-elnz6V`), workspace-2 of run 1/2 (`/private/tmp/e-ybGOkd`), checked by the files each trace writes and by file times. Cost, turns and duration above are run 2's. Run 1: $2.74, 34 turns, 516 s.

Modules loaded (from the trace, each by `cat` of its SKILL.md or GUIDE.md): tells, ui-ux-pro-max, motion-principles, css-native, mobile-principles, design-audit; reference `tells/references/web.md`; scripts `ui-ux-pro-max/scripts/search.py --design-system` (variance 3, motion 2, density 4), `design-audit/scripts/audit.py` and `audit.py --group tells`.

It loaded the modules by hand because the skill's resolver block reached it with broken paths (`the/...`): the known 4.1.0 bug where Claude Code substitutes `$1`/`$2` in the resolver with words of the typed request (fixed on `fix/skill-arguments`, to ship as 4.1.1). The run said so in its report. The paint skill itself came in through the `/genjutsu:paint` slash command, not a Skill tool call, and its text is not in the trace, so the harness graders `paint-fired` and `paint-loaded` scored it as not loaded (case score 0.33 on both runs).

## What it proposed

Marked **UNVALIDATED** in its own report (headless run, nobody to confirm the theses).

**Visual thesis:**

> - **Colour:** a cold green-black ground (#0F1615) and pale cool ink (#E6ECE9). The current is drawn in sea-glass green (#8DB3A6), flood above the line and ebb below. One warm colour, slack amber (#EDB95E), is used only for slack times and the beta button.
> - **Type:** the iPhone's own system face (SF Pro through `system-ui`) with tabular figures. Slack times are large and light (300), headings medium (500).
> - **Spacing:** airy, on an 8px base.
> - **Shapes:** flat filled surfaces, 2px corners, no borders, no shadows.

**Interaction thesis:**

> nothing moves on load or on scroll.
> - Picking a slack slides the marker in 240ms with `cubic-bezier(0.2, 0, 0, 1)` and crossfades its figures (160ms out, then 160ms in).
> - Hover and press change colour only, in 160ms.
> - Forbidden: scroll reveals, parallax, loops or waves, bounce, scale on hover, and anything that plays on load.

**Allowed patterns:**

> tabular figures (no monospace), and a zero line and hour ticks inside the two charts. Because the thesis is unvalidated, this allows nothing, and the audit found neither as a problem.

It showed before it wrote: `preview/thesis.html` and `preview/design-system.html`, and wrote `MASTER.md`. From the design-system lookup it kept the 150-300ms timing range and dropped the navy-and-gold palette, Inter, 900-weight type and an App Store layout with device mockup, ratings and a Play Store button.

## Audit (its own)

> Audit: checked here (11 checked, 1 small problem)

The problem: `index.html` repeats the ground colour (#0f1615) in `theme-color`, because HTML can't read a CSS token. Tells: `--group tells` ran 18 checks with 0 findings.

The sandbox blocked `node` and `npm`; the run type-checked with the native TypeScript 7 binary from node_modules (`tsc --noEmit` passed) and handed over as not verified: `npm run build`, smoothness while switching slacks, the layout at 375 / 768 / 1024 / 1440 px ("no horizontal scroll; chart labels don't overlap at 375 px") and reduced motion. The layout check fails: see Defects.

## Selection

Both workspaces were built and captured (first screen and mid-page at 1440x900, in `compare/`).

workspace-1 puts the product's answer on the first screen: next to the headline and the beta button sits a panel with the day's three slacks (05:57, 10:31, 16:17 at SFB1204), a picker, the strongest current before and after the picked slack, and a strip of the four current peaks with the slacks marked. Mid-page, its tide curve at 9414290 with the slack lines drawn on it shows the brief's main point (slack is not high or low tide) as a picture, then a table of the gaps. workspace-2 is a good, careful single column, but its first screen is a headline, a paragraph and the button with the first slack below them, and its middle is a list of the strongest currents and a plain table: it reads as a text page, weaker as a homepage example. Both builds are honest to the data. workspace-1 has a horizontal overflow workspace-2 does not have (workspace-2 measured at 390, 768 and 1440: scrollWidth equals the viewport); it was picked anyway as the stronger homepage, and the defect is documented below, not hidden.

## Build

`npm run build` succeeded on the first try for both workspaces with node_modules copied from the template (`build-1/`, `build-2/`). Human edits: 0, no `edits.diff`.

## Media

| File | What | Viewport | Output |
|---|---|---|---|
| `media/desktop.png` | Desktop first screen | 1440x900 | 1440x900, 155 KB |
| `media/mobile.png` | Mobile first screen | 390x844 @2x | 780x1688, 179 KB |
| `media/full-desktop.webp` | The whole page, static, captured in one 1440x3135 viewport (the page is 3135 px tall at 1440 and uses no vh units, so the layout is the same as at 1440x900) and scaled down | 1440x3135 | 1000x2177, 91 KB |
| `media/clip.webp` | First screen held 2 s, then a steady linear scroll from the top to the bottom of the page (0 to 2235 px) in 9 s, then 0.6 s at the footer | 1440x900 | 600x375, 576 KB |
| `media/clip-1200.webp` | The same take at 1200 px, over the 600 KB budget (alternative, not the README clip) | 1440x900 | 1200x750, 1766 KB |
| `media/mid-page.png` | Desktop, scrolled to the middle of the page (1118 px): tide curve with slack lines, the turns table, 'The evening before' | 1440x900 | 1440x900, 125 KB |
| `media/reduced.png` | prefers-reduced-motion: reduce, first screen. Pixel-identical to desktop.png: nothing moves on load in either mode; the probe shows --dur-slide at 0s, so only the slack picker's slide and crossfade change | 1440x900 | 1440x900, 155 KB |
| `media/preview.png` | preview/thesis.html, the thesis page the run wrote before touching src/ (top of the page) | 1440x900 | 1440x900, 184 KB |
| `media/preview-design-system.png` | preview/design-system.html, the design system page (scrolled 210 px: colour tokens with computed contrast, start of the type scale) | 1440x900 | 1440x900, 129 KB |

Notes:

- Captured with bin/record.mjs: the static build served from disk over CDP, no server, virtual time. Takes are in takes/.
- No console errors, uncaught exceptions or failed requests in any take.
- clip.webp is 600 px wide, not 1200: a 9 s scroll through this text-dense page does not fit 600 KB at 1200 px at any watchable frame rate (1200 px at 4 fps, q25: 748 KB; at 8 fps, q50: 1944 KB; record.mjs's own ladder ended at 650 KB at 420 px). It keeps the budget and a steady 8 fps and gives up width. Frames from `takes/clip.json` (`--keep-frames`), re-encoded with `takes/encode-clip.py`. The 1200 px take is `clip-1200.webp`, over budget.
- reduced.png is pixel-identical to desktop.png: nothing moves on load in either mode. Under reduced motion `--dur-slide` reads 0s, so only the slack picker's slide and crossfade change, and a still cannot show that.

## Defects the run introduced

1. **Horizontal overflow from the hero's slack marker.** `.strip__marker` is a full-width layer (`inset: 0`) moved with `translateX(<slack minute as % of the day>)` (`src/CurrentDay.tsx:82`, `src/index.css:378-383`), so it sticks out of the plot by that percentage, and nothing clips it. Document width with 05:57 / 10:31 / 16:17 picked: 421 / 478 / 551 px at a 390 px viewport, 853 / 972 / 1123 at 768, 1053 / 1137 / 1243 at 1024, 1440 / 1442 / 1565 at 1440. The page scrolls sideways on phones and tablets from the start, and on desktop once a later slack is picked. The run handed this check over as not verified. The stills do not show it (the overflow is empty space right of the viewport); measured with `takes/probe-overflow-390.json` and the same probe at other widths.
2. **Slack lines through the high-water labels.** In the tide chart the amber slack lines run through the "H 05:47" and "H 15:58" labels: each label is centred on its high water and the slack 10 and 19 minutes later falls inside it (`src/TideChart.tsx:20-32`). Visible in mid-page.png, full-desktop.webp and clip.webp.
