# Evidence: captures and tests without a dev server

Reviewers judge what renders, so every review and verdict starts from captures. They are taken
from the **static build on disk**, never from a running server: nothing to start, no fixed port
to collide with the user's own dev server (the browser's DevTools endpoint takes a free port the
OS picks), and several clones can capture at once.

## shoot.mjs

`scripts/shoot.mjs` in this module opens a headless Chrome over the DevTools protocol and
answers every request to a fake origin (`http://site.test`) from the build folder; requests to
other origins go to the network. No dependency: Node 22 or later and a Chrome or Chromium binary (found on the usual macOS paths, on
`PATH` as `google-chrome` or `chromium`, or given with `--chrome` / `CHROME_PATH`).

```bash
# (skill-base block re-emitted above, so $SKILL_BASE is set)
mkdir -p .bunshin/captures/round-1
node "$SKILL_BASE/orchestration/scripts/shoot.mjs" --root <build dir> \
  --shots .bunshin/captures/round-1/<page>-<lang>.json > .bunshin/captures/round-1/<page>-<lang>.result.json
node "$SKILL_BASE/orchestration/scripts/shoot.mjs" --self-test   # proves the harness works here
```

Shots run one after the other, a few seconds each, and the JSON prints at the end: write one
shots file per page and language and run one call per file, with the shell call's timeout
raised to its maximum (or in the background for a long list), and keep the functional tests in
a file of their own. A shot that fails (a selector that matches nothing, an expression that
throws or never settles) is reported with its `error` and the others still run; the exit code
is then 1.

The build dir is whatever the framework emits as static files: `dist` (Astro, Vite),
`.vercel/output/static` (the Vercel adapter), `out` (a Next.js static export), `build`
(SvelteKit static). Routes resolve as the file, then `<route>/index.html`, then `<route>.html`.

The header of the script documents every shot field. The result, per shot: the files written,
`overflow` (the page scrolls sideways), the height, console errors, uncaught exceptions, and
every request the build could not answer (an analytics script injected by the host at deploy
time shows up there, and is expected).

## The standard shot list

Per page and per language, write these shots, then read them:

| Shot | Why |
|---|---|
| 390x664, first screen | The height the measured run used for a social app's in-app browser on a phone, not measured on a device; measure the real one when you can. The first-screen promise is judged here. |
| 390x844, first screen | A tall phone with the browser chrome collapsed. |
| 390x664, `full: true, segment: 1700` | The whole mobile page, in segments a reviewer can actually open. |
| 1280x720, first screen | A laptop. Calls to action above the fold are judged here, not at 1440. |
| 1440x900, `full: true, segment: 1700, width: 1000` | The whole desktop page, scaled to 1000 px wide segments. |
| 390x664, `reduced: true` | The reduced-motion path of the signature moment. |
| With Impeccable: the home page at 1440x900 and 390x664, `full: true`, no `segment`, `out` straight to `.impeccable/review/desktop.png` and `mobile.png` | The two captures its finish reviewer requires, at the paths it reads, shot again at every PROVE. |

For full-page shots, pass `reveal` with the selector of the elements whose entrance animations
start hidden, so a long page is not captured as a column of empty frames. For the signature
moment (a scroll-driven effect), add shots at two or three `scrollY` positions instead: a full
page capture shows it at one arbitrary point.

Name the files `<page>-<lang>-<w>x<h>.png` for a first screen, `<page>-<lang>-<w>x<h>-full-NN.png`
for the segments of a full page (give `out` as `...-full.png`), and `<page>-<lang>-<w>x<h>-reduced.png`
for the reduced-motion shot, under `.bunshin/captures/round-N/`, and put the folder in the
evidence packet. Read the first screens yourself before you hand them over:
a capture of a broken build reviewed by five lenses is five wasted lenses.

## Functional tests

`before` runs an expression in the page, `measure` returns a value with the result, and `wait`
lets transitions settle. That covers the paths a showcase site has to keep working:

```json
[
  { "path": "/", "w": 390, "h": 664, "before": "document.querySelector('#menu-toggle').click()", "wait": 600,
    "measure": "({ open: document.querySelector('dialog').open, focus: document.activeElement.tagName })",
    "out": ".bunshin/captures/round-1/menu-open.png" },
  { "path": "/", "w": 390, "h": 664, "scrollY": 1400,
    "measure": "getComputedStyle(document.querySelector('#sticky-bar')).visibility" },
  { "path": "/contact?plan=team", "w": 390, "h": 664,
    "measure": "document.querySelector('[name=plan]:checked')?.value" }
]
```

The selectors are the project's own: read them in its components.

Write one shot per behaviour: the menu opens, closes on Escape and returns focus; a sticky bar
appears after the hero's own call to action leaves the screen and never sits on top of it; a
selection carries into the request form; each form step validates inline; the endpoint's
failure answer offers the fallback channel and its success answer confirms. Mock an endpoint
by overriding `fetch` in `before`, returning a 503 and then a 200. Then, over every page:
`consoleErrors` and `exceptions` empty, `overflow` false at 390 and 1280.

Report each behaviour with the value `measure` returned. "The menu works" is not a result;
`{ open: true, focus: "BUTTON" }` is.

## When the host has a browser tool instead

A Playwright MCP server (or any browser the session can drive) works too, with the same rule:
intercept the fake origin and answer from disk.

```js
// browser_run_code: `page` is given; require() is not available there.
async (page) => {
  const root = '<absolute build dir>'
  await page.context().route('http://site.test/**', async route => {
    const p = new URL(route.request().url()).pathname
    const tries = p.endsWith('/') ? [p + 'index.html'] : /\.[a-z0-9]+$/i.test(p) ? [p] : [p + '/index.html', p + '.html']
    for (const t of tries) { try { return await route.fulfill({ path: root + t }) } catch {} }
    return route.fulfill({ status: 404, body: '' })
  })
  await page.setViewportSize({ width: 390, height: 664 })
  await page.goto('http://site.test/')
}
```

That browser is one per session: it belongs to you, never to the clones. Clones that need to
see their own page run `shoot.mjs`, each with its own headless browser.

- A long `browser_run_code` call was killed after about thirty minutes in the measured run
  (Playwright MCP, 2026-09-30); batch the pages.
- `click()` waits up to thirty seconds when an overlay covers the target. For a scripted
  click that must not wait, use `page.evaluate(() => document.querySelector(sel).click())`.

## Traps observed in the run this pipeline comes from

Each of these was hit in that run and cost it a fix. They are observations dated 2026-09-30,
with the versions they were seen on; `_jutsu/VERSIONS.md`, section "Orchestration", holds the
rows and their sources.

- **A CSS minifier can fold `animation-timeline` into the `animation` shorthand**, and the
  browser then drops the whole declaration: every scroll-driven animation dies in production
  while the dev server looks fine. Seen with lightningcss as Vite's CSS minifier under Astro 7.
  Check the compiled CSS for `animation-timeline`; switching the minifier (in Vite:
  `build.cssMinify: 'esbuild'`) fixed it.
- **In Chrome, an IntersectionObserver reports an element hidden with `clip-path: inset(100%)`
  as a zero-area intersection** (ratio 0), so a reveal that waits for a threshold above 0 never
  fires and the images stay hidden. Observe an unclipped parent.
- **`view()` timelines inherit `scroll-padding-top`**: a sticky header's padding shifts every
  range. `view(block 0px)` pins the inset.
- **A rule that sets both `translate` and a `transform` animation can lose the `translate`** in
  the build: keep position on a wrapper and the animation on its child.
- **`<hr>` inherits the browser's grey `color`**: set `color` before painting it with
  `background: currentColor`.
- **pnpm before 10.26 reads only `onlyBuiltDependencies`, pnpm 11 only `allowBuilds`**, in
  `pnpm-workspace.yaml`. A host that builds with an older pnpm 10 skips the native builds allowed
  only under the new key. Write both. To reproduce the host's install, ask first, then run
  `npx pnpm@10 install --frozen-lockfile` in a scratch copy of the project, never in its own
  folder: it downloads pnpm 10 and rewrites `node_modules`.
- **A full-page capture puts `position: fixed` elements in the middle of the page**, and lazy
  images stay blank. The preparation step of `shoot.mjs` makes images eager; read fixed bars on
  the first-screen shots, not on the full-page ones.
