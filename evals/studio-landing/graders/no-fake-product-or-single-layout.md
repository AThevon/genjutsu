---
type: llm
focus: { source: file, path: app/page.tsx }
---

You are reading the source of a single landing page (app/page.tsx). Judge two things only.

1. Fake product drawn in divs: a section that imitates a product screen, dashboard, browser
   window (three dots in a bar), terminal, phone screen or chart by stacking styled divs and
   invented numbers, instead of showing a real image or real content.
2. One layout family: every content section below the hero uses the same arrangement (for
   example each one is a grid of equal cards, or each one alternates image and text), so the
   page never changes its layout family.

PASS if neither 1 nor 2 happens: there is no div-built fake product, and at least two
different layout families appear across the sections.
FAIL if a div-built fake product is present, or if all sections share one layout family.
