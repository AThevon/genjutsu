# pottery-firing - receipt

`/genjutsu:cast` on a one-page site for Atelier Grès, a fictional pottery studio: pin the four firing stages and scrub them with the scroll. React 19 + Vite + TypeScript, GSAP 3 ScrollTrigger (template react-gsap).

## The prompt

> /genjutsu:cast pin our pottery studio's four firing stages and scrub them with the scroll
>
> Atelier Grès is a fictional pottery studio, made up for this example.
>
> Nobody is available to answer questions during this session. Up-front answers to the gates:
> - Preview mode: A. Write each preview as a standalone HTML file under preview/ in the project.
> - Scope: the firing stages section. You may edit files under src/ and index.html, and write previews under preview/; create nothing outside the project.
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
| Cost | $1.53 |
| Turns | 23 |
| Duration | 333 s |
| Selection | first pass (1 run recorded) |
| Human edits | 0 (builds as the run left it) |

Modules loaded (from its `load_skill` calls): motion-principles, gsap, tells, mobile-principles; reference `tells/references/web.md`; script `design-audit/scripts/audit.py --group tells`.

The cast skill itself came in through the `/genjutsu:cast` slash command, not a Skill tool call, so the harness graders `cast-fired` and `cast-loaded` scored it as not loaded (case score 0.33). The trace shows the skill's own setup script and module loader running.

## What it proposed

Marked **UNVALIDATED** in its own report (headless run, nobody to confirm the thesis).

**Interaction thesis:**

> The firing stages section pins for 300% of the viewport height. A GSAP ScrollTrigger scrub (`scrub: 0.6`, timeline `ease: "none"`) draws the studio's own firing curve as one SVG line: room temperature, up to 950 °C, back down, up to 1280 °C, then a slow fall. As the line crosses into each stage's segment, that stage's text takes over from the previous one: out over 0.2 of a stage (opacity → 0, y → −24px, `power2.in`), then in over 0.2 of a stage (opacity 0 → 1, y 24 → 0, `power2.out`). With reduced motion, or on a viewport under 560px tall, it stays the static list with the full curve drawn.

**Allowed patterns:**

> the pinned section, a schematic line chart (temperature vs. stage, not to scale in time).

It showed before it wrote: `preview/thesis.html` and `preview/variants.html`, then picked A (subtle). B and C add a dot and a temperature readout the run rejected as invented data.

## Audit (its own)

> Audit: 10 checked, 2 problems found (1 in this run, 1 already in the project), 3 handed over

Tells: audit.py --group tells: 18 checked, 0 findings, 0 tells to confront.

The run could not build or open a browser (no Node runtime in the sandbox); it checked types by hand and listed npm run build and browser checks as UNVERIFIED.

## Build

`npm run build` succeeded on the first try with node_modules copied from the template. Human edits: 0, no `edits.diff`.

## Media

| File | What | Viewport |
|---|---|---|
| `media/clip.webp` | Scroll from just above 'The four firings' through the whole pinned, scrubbed section: all four stages play, the firing curve draws | 1440x900 |
| `media/desktop.png` | Desktop first screen | 1440x900 |
| `media/mobile.png` | Mobile first screen | 390x844 @2x |
| `media/mid-page.png` | Desktop, pinned section mid-scrub (glaze firing) | 1440x900 |
| `media/mobile-pinned.png` | Mobile, pinned section mid-scrub (glaze firing); the run handed this check over as UNVERIFIED: the card fits, no horizontal scroll | 390x844 @2x |
| `media/reduced-motion.png` | prefers-reduced-motion: reduce; no pin, full curve drawn, static list | 1440x900 |
| `media/preview.png` | preview/thesis.html, the thesis page the run wrote before touching src/ (inner frame scrolled to 62%) | 1440x900 |
| `media/preview-variants.png` | preview/variants.html, variants A, B, C side by side (inner frames scrolled to 62%) | 1440x900 |

Notes:

- Captured with bin/record.mjs: the static build served from disk over CDP, no server, virtual time. Takes are in takes/.
- No console errors, uncaught exceptions or failed requests in any take.
- In preview/thesis.html, during the scrub the stage text sits on top of the 'Drying' label under the curve (visible in preview.png). That is the preview as written; the built page does not do it.
