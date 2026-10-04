# invoice-mark-paid - cast, Motion

**First pass.** One recorded run, built unchanged, 0 human edits. Media re-filmed on the same build after a review (see "Re-film" below).

**What is the run's work here:** only the motion. The page itself (the Folio header, the three summary cards, the invoice table, its rows, colours and type) is the starting fixture written by `fixture.sh`, unchanged in look. The run made the "Mark as paid" click move: the button leaving, the pill stamping to Paid, the two totals counting and the signed amounts on the cards.

| | |
|---|---|
| Skill | `/genjutsu:cast` |
| genjutsu | 4.1.0 at commit `09c177b` |
| Model | claude-opus-5-5 (Claude Code 2.1.289, `claude plugin eval`, headless) |
| Date | 2026-10-04 |
| Cost | $1.88 (1.882439) |
| Turns | 45 |
| Duration | 329 s (5 min 29 s) |
| Subagents | 0 |
| Stack | React 19 + Vite + TypeScript, `motion` 14 installed and unused before the run |
| Build | `npm run build` passed on the first try, no edits (`edits.diff`: none) |
| Human edits | 0 |

## The prompt

```
/genjutsu:cast the "Mark as paid" action in our invoice list is dead, make it feel like the money landed

Folio, its user and its clients are fictional, made up for this example.

Nobody is available to answer questions during this session. Up-front answers to the gates:
- Preview mode: A. Write each preview as a standalone HTML file under preview/ in the project.
- Scope: the invoice list and its "Mark as paid" action. You may edit files under src/ and write previews under preview/; create nothing outside the project.
- Dependencies are installed (node_modules is present) and `npm run build` works. There is no network: install nothing. Do not start a dev server.

Finish with the final report the pipeline asks for.
```

Nobody answered the gates. The skill's "When nobody is answering" rule applied, and the run marked its own thesis **UNVALIDATED**.

## What it decided

**Interaction thesis (UNVALIDATED: nobody was there to approve it)**, quoted from the final report:

> Marking an invoice paid moves its amount across the ledger. The button leaves in 150ms, and the status pill stamps from Sent/Overdue to Paid on a spring (stiffness 520, damping 30). Outstanding counts down while Paid counts up by exactly that amount over 700ms on `cubic-bezier(0.22, 1, 0.36, 1)`, with Paid starting 120ms after Outstanding. Each card shows a signed amount (−€ / +€) for 1.6s, and an aria-live line says what landed.

**Allowed patterns:** counting numbers on the two totals; a temporary signed amount on the summary cards.

**Assumptions it made:** the mood is calm bookkeeping, not celebration; "landed" means the amount moving between the two totals; reduced motion and screen readers are covered.

**Variant picked:** B, "Ledger", from three. A only changes the totals. C also flies a copy of the amount up to the Paid card, which the run judged tiring in a tool used every day.

**Modules loaded** (its `load_skill` calls): motion-principles, framer-motion, desktop-principles, tells (plus the reference `tells/references/web.md`). Not loaded: none.

## It showed before it wrote

- `preview/thesis.html`: the thesis, the allowed patterns, the UNVALIDATED status, the count curve, the spring plot (settles in about 502 ms, 6% overshoot), a replay button and a reduced-motion toggle.
- `preview/variants.html`: the three variants side by side, each with a replay.

## What changed

4 files, 142 insertions, 44 deletions against the fixture.

- `src/InvoiceList.tsx`: the button fades out with an 8 px slide and shrinks on press; the old pill fades while the Paid pill stamps in on the spring; focus moves to the next unpaid invoice; `MotionConfig reducedMotion="user"`.
- `src/LedgerFigure.tsx` (new, 70 lines): a total that counts to its new value and shows the signed amount.
- `src/App.tsx`: the two money totals use `LedgerFigure`, a second click on a paid invoice does nothing, and a hidden `role="status"` line says what moved.
- `src/index.css`: hover, focus and disabled styles for the button, the shared pill slot, the signed amounts.

## Its own audit

**11 checks, 1 problem, 4 for you to run.**

- Problem: a new raw colour, `#000`, for the button hover (`index.css:191`). The project has no design tokens.
- Tells: `audit.py --group tells` reported no findings. Read by hand, the counting totals and signed amounts show real figures, so neither counts as decoration.
- Kept on purpose: the 700 ms count is over the 500 ms limit in motion-principles; nobody waits on it.
- Left unverified, for you to run: `npm run build` (its sandbox had no Node binary, so it checked the types by hand against motion 14), a DevTools Performance recording, the 375 / 768 / 1024 / 1440 px widths, and the OS reduce-motion setting.

What the captures add to that: the build passes unchanged, and the counts, signed amounts and reduced-motion path behave as the thesis says. They also show a defect the audit missed (the focus hand-off scrolls the page, below). The 375 px check it left open fails too, but on layout the run never touched (see `mobile.png`).

## Defects the run introduced

- **The focus hand-off scrolls the page on a mouse click.** `src/InvoiceList.tsx:25`, `if (document.activeElement === button) next?.focus();`, written by the run so the keyboard is not dropped on `<body>` when the button leaves. It calls `focus()` without `{ preventScroll: true }`, so when the next unpaid invoice's button is not fully inside the viewport, the browser scrolls it into view. A mouse click focuses the button in Chrome (the recorder's browser), so this hits mouse users too, not only the keyboard. When it shows: at 1200x656, after marking FOL-2026-032, clicking "Mark as paid" on FOL-2026-034 hands focus to FOL-2026-036 (below the fold) and the page jumps 242 px (`scrollY` 0 to 242 in the probe of `takes/focus-scroll.json`) in the same frame the totals start counting, so the heading and the summary cards leave the screen and the count plays out of sight (`media/defect-focus-scroll.png`). It does not show at 1440x900, where every row fits (`scrollY` stays 0 for the whole clip). The audit did not catch it. Not fixed here: the build is shown as the run left it.

## Re-film

The first capture of this build was rejected by a cold-eyes review. It was filmed at 1200x656, where the defect above scrolled the page on the second click, so the clip lost the totals halfway; the whole page at 1200 px made the motion too small to read in a thumbnail; and this receipt described `sent-mid.png` and `sent-settled.png` as showing totals they did not show (the page had scrolled them away). Re-filmed on the same build (`build-20261004T162510Z-1`, unchanged): a 1440x900 viewport so the hand-off target stays visible and nothing scrolls, the clip cropped to the cards and the clicked rows, the four stills retaken at 1440x900, and the defect filmed on its own.

## Media

All captured from `build-20261004T162510Z-1/dist` as built, served from disk over CDP with no server, by `bin/record.mjs` in virtual time (takes in `takes/`). No console errors, no exceptions, no failed requests in any take.

| File | Viewport | Output | What it shows |
|---|---|---|---|
| `media/clip.webp` | 1440x900, dpr 1 | 1100x460, 5.5 s, 24 fps, q82, 452 KB | The page is the starting fixture; only the motion is the run's. Cropped to the three summary cards and the first four rows (x 170-1270, y 134-594 of the viewport; recorded by `takes/clip.json` with `--keep-frames`, then cropped and re-encoded by `takes/clip-crop.sh`, nothing else touched). Click "Mark as paid" on FOL-2026-032 (Overdue, €4,200.00) at about 1.0 s: the button slides out, the pill stamps to Paid, Outstanding counts €9,380.00 to €5,180.00 and Paid €1,770.00 to €5,970.00 with −€4,200.00 / +€4,200.00 on the cards, Overdue 2 to 1. Click FOL-2026-034 (Sent, €1,150.00) at about 3.5 s: €4,030.00 outstanding, €7,120.00 paid. The page never scrolls (`scrollY` 0 in every frame). The pointer is drawn by the recorder, it is not in the build. The loop jumps back to the first state. |
| `media/overdue-mid.png` | 1440x900 | 1440x900 | 350 ms after the FOL-2026-032 click: €5,300.81 outstanding and €5,520.29 paid mid-count, −€4,200.00 / +€4,200.00 showing, pill Paid, button gone, Overdue 1. |
| `media/overdue-settled.png` | 1440x900 | 1440x900 | 2.85 s after: €5,180.00 outstanding, €5,970.00 paid, signed amounts gone. |
| `media/sent-mid.png` | 1440x900 | 1440x900 | 350 ms after the FOL-2026-034 click: €4,063.08 / €6,996.87 mid-count, −€1,150.00 / +€1,150.00 showing, FOL-2026-034 Paid, page not scrolled. |
| `media/sent-settled.png` | 1440x900 | 1440x900 | After both clicks: €4,030.00 outstanding, €7,120.00 paid, Overdue 1, signed amounts gone. |
| `media/defect-focus-scroll.png` | 1200x656 | 1200x656 | The defect: 350 ms after the FOL-2026-034 click at this height, the page has scrolled 242 px; the heading and the summary cards are out of view while they count, and FOL-2026-036's button (the focus target) is now on screen. |
| `media/desktop.png` | 1440x900 | 1440x900 | First screen before any click: the fixture as it looks with the run's code in place (nothing the run did is visible at rest). |
| `media/mobile.png` | 390x844, dpr 2 | 780x1688 | First screen. The fixture has no small-screen rules: the totals overflow their cards and the table scrolls sideways (page 778 px wide). Fixture layout, not the run's. |
| `media/reduced.png` | 1200x656 | 1200x656 | `prefers-reduced-motion: reduce`, 350 ms after the FOL-2026-032 click: totals already final at €5,180.00 / €5,970.00 with no count, signed amounts faded in without moving, the pill swapped by a fade. No scroll at this click (its focus target, FOL-2026-033, is on screen). |
| `media/preview.png` | 1280x1526 | 1280x1526 | `preview/thesis.html`, whole page: thesis, allowed patterns, UNVALIDATED status, count curve, spring plot, the bare numbers, a one-row replay. |
| `media/preview-variants.png` | 1280x560 | 1280x560 | `preview/variants.html`, 500 ms after "Play all three": A Settle, B Ledger (picked), C Transfer, mid-count. |
| `media/clip-probe.json` | | | Per clip frame: `scrollY`, the three summary values, each signed amount with its opacity, and which row holds focus. |

**Caption for the clip:** The Folio page is the starting fixture; the motion is the run's work. Two "Mark as paid" clicks: the amount leaves Outstanding and lands in Paid as both totals count, with a signed amount on each card. 1440x900 viewport, cropped.

## Notes

- **Grader score 0.33 is a harness artifact.** `cast-fired` and `cast-loaded` failed because a slash command expands the skill inline, with no Skill tool call, and the expanded prompt is not in the trace. The run did run cast: its loader points at `skills/cast`, it loaded four cast modules and wrote cast's final report. `button-has-interaction` passed.
- **A skill bug the run found and worked around.** The module loader in the skill text arrived with its `$1`/`$2` placeholders replaced by the invocation's second argument ("Mark as paid"), so as written it could not find any module. The run rebuilt the loader with the placeholders restored. Cause: Claude Code replaces `$N` in a skill's text with the invocation's arguments, and the shell functions in `skills/cast`, `paint` and `bunshin` `SKILL.md` use `$1`/`$2` (fixed on `fix/skill-arguments`, to ship in 4.1.1).
- The Overdue count card goes from 2 to 1 instantly. It is not part of the thesis.
- A code comment says the stamp settles "in about a quarter second"; the run's own preview computes about 502 ms for the same spring.
- The previews use a smaller sample (€8,430.00 outstanding) than the app (€9,380.00). They are throwaway mockups, not the build.
