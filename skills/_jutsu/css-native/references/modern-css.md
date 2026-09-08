# Modern CSS — Browser Support, Fallbacks & Progressive Enhancement

> Last verified: 8 September 2026 — against MDN browser-compat-data, caniuse (data of 2026-08-24) and webstatus.dev.
>
> Reference stable versions at time of writing: Chrome/Edge 153, Firefox 155, Safari 26.6 (Safari 27 in beta).

---

## Browser Support Tables

### Scroll-Driven Animations (`animation-timeline`)

| Browser | Version | Status |
|---|---|---|
| Chrome | 115+ | Supported (July 2023) |
| Edge | 115+ | Supported (July 2023) |
| Firefox | **Not shipped** | Nightly only, behind `layout.css.scroll-driven-animations.enabled` (on by default in Nightly since 136, off in Beta and Release). `animation-range-start` / `animation-range-end` and `timeline-scope` are still unimplemented even in Nightly ([bug 1676779](https://bugzil.la/1676779)) |
| Safari | 26+ | Supported (Sept 2025) — **not** in Safari 18.x |

**Global coverage**: ~84% (derived from caniuse usage data, Aug 2026). Baseline: **Limited availability** — roughly one visitor in six is on Firefox and gets nothing.

**The `@supports (animation-timeline: scroll())` guard is mandatory.** Never let a scroll-driven animation be the only thing that makes content visible. Scroll-driven animations are an Interop 2026 focus area, so Firefox intends to ship — but it has not.

### View Transitions API

| Feature | Chrome | Edge | Firefox | Safari |
|---|---|---|---|---|
| Same-document (`startViewTransition`) | 111+ | 111+ | 144+ | 18+ |
| Cross-document (`@view-transition`) | 126+ | 126+ | **Not yet** | 18.2+ |
| `view-transition-class` | 125+ | 125+ | 144+ | 18.2+ |
| `view-transition-name: match-element` | 137+ | 137+ | 144+ | 18.4+ |

**Global coverage**: same-document ~90%, cross-document ~85%.

**Baseline**: same-document view transitions became **Newly available on 14 Oct 2025** (Firefox 144). Cross-document is still **Limited** — Firefox 144+ implements View Transitions Level 1 only, so `@view-transition { navigation: auto }` is still a no-op there.

**Note**: there is no `view-transition-name: auto` — the auto-naming value is `match-element`, and it only works for same-document transitions. View transitions are an Interop 2026 focus area (carried over from 2025).

### @starting-style

| Browser | Version | Status |
|---|---|---|
| Chrome | 117+ | Supported |
| Edge | 117+ | Supported |
| Firefox | 129+ | Supported |
| Safari | 17.5+ | Supported |

**Global coverage**: ~90% — Baseline **Newly available since 6 Aug 2024** (Firefox 129 completed it).

**The gotcha is not `@starting-style`, it is what you transition with it.** `transition-behavior: allow-discrete` itself is Chrome 117+ / Firefox 129+ / Safari 17.4+, but actually *transitioning* `display` or `content-visibility` with it is **Chrome 117+ and Safari 18+ only — Firefox does not implement it**. In Firefox the enter animation plays and the exit animation is skipped (the element just disappears). That is a graceful degradation, not a bug — but never rely on the exit transition firing.

### CSS Anchor Positioning

| Browser | Version | Status |
|---|---|---|
| Chrome | 125+ | Supported. `position-area` since 129 — it shipped as `inset-area` in 125–130 and that old name was removed in 131 |
| Edge | 125+ | Same as Chrome |
| Firefox | 147+ | Supported — enabled by default 13 Jan 2026 |
| Safari | 26+ | Supported (Sept 2025) |

**Global coverage**: ~84%. All three engines now ship `anchor-name`, `position-anchor`, `position-area`, `@position-try`, `position-try-fallbacks` and `position-visibility`.

**Still guard it.** web-features rates anchor positioning **Limited** because sub-features diverge across engines — e.g. `position-anchor: normal` only lands in Chrome 151 / Firefox 151 / Safari 27, and `position-visibility: anchor-visible` is Safari 27 only. Keep `@supports (anchor-name: --a)` plus a `position: absolute` fallback.

**Renames to watch** (old names will silently do nothing): `inset-area` → `position-area`, and `position-try-options` → `position-try-fallbacks` (renamed in Chrome 128). Anchor positioning is an Interop 2026 focus area, carried over from 2025.

### Container Queries

| Feature | Chrome | Edge | Firefox | Safari |
|---|---|---|---|---|
| Size queries (`@container`) | 105+ | 105+ | 110+ | 16+ |
| Container-relative units (`cqw`, `cqh`) | 105+ | 105+ | 110+ | 16+ |
| Style queries on custom properties (`@container style(--x: y)`) | 111+ | 111+ | 151+ | 18+ |
| Scroll-state queries (`@container scroll-state()`) | 133+ | 133+ | Not yet | Not yet |

**Global coverage**: size queries ~94%; custom-property style queries ~90% — **Baseline Newly available since 19 May 2026** (Firefox 151). Scroll-state queries ~69%.

**Note**: `style()` only accepts **custom properties** in Chrome, Edge and Safari — querying a standard property is not shipped, so `@container style(display: flex)` does nothing. Container style queries are an Interop 2026 focus area.

**Scroll-state queries** (`stuck`, `snapped`, `scrollable`, plus `scrolled` from Chrome 144) let you style a sticky header the moment it sticks, or a snapped slide the moment it snaps — with no scroll listener. Chromium-only, no Firefox or Safari implementation; pure enhancement, and no `@supports` syntax detects it, so build the un-stuck state as the default.

### Native Stagger — `sibling-index()` / `sibling-count()`

| Browser | Version | Status |
|---|---|---|
| Chrome | 138+ | Supported (24 June 2025) |
| Edge | 138+ | Supported |
| Firefox | 154+ | Supported (18 Aug 2026) |
| Safari | 26.2+ | Supported (12 Dec 2025) |

**Global coverage**: ~80% — **Baseline Newly available since 18 Aug 2026.**

This kills one of the last real reasons to pull in a JS animation library: the child's index is now a CSS value, so a stagger needs no `nth-child` ladder and no known element count.

```css
@supports (animation-delay: calc(sibling-index() * 1ms)) {
  li {
    animation: rise 400ms var(--ease-out-expo) both;
    animation-delay: calc(sibling-index() * 60ms);
  }
}
```

Without support every item animates simultaneously — acceptable degradation, so the `@supports` guard is optional rather than load-bearing. `sibling-count()` gives the total, which is what you need for percentage-based or reversed staggers.

### `interpolate-size` / `calc-size()` — animating to `height: auto`

| Browser | Version | Status |
|---|---|---|
| Chrome | 129+ | Supported |
| Edge | 129+ | Supported |
| Firefox | **Not shipped** | — |
| Safari | **Not shipped** | — |

**Global coverage**: ~70% — Baseline **Limited**, still marked experimental. Chromium-only.

Use it as a bonus layer on top of a `grid-template-rows: 0fr → 1fr` or `max-height` accordion, never as the mechanism. `interpolate-size: allow-keywords` on `:root` opts the whole document in, so scope it deliberately.

---

## Fallback Patterns

### Scroll-Driven Animations

```css
/* Base: no scroll animation, element is always visible */
.reveal {
  opacity: 1;
  transform: translateY(0);
}

/* Progressive enhancement for supporting browsers */
@supports (animation-timeline: scroll()) {
  .reveal {
    animation: reveal-up linear both;
    animation-timeline: view();
    animation-range: entry 10% entry 90%;
  }

  @keyframes reveal-up {
    from {
      opacity: 0;
      transform: translateY(2rem);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}
```

**Strategy**: Content is always visible by default. Scroll animation is purely decorative enhancement. Never hide content behind a scroll-driven animation without fallback.

### View Transitions (Same-Document)

```js
function navigate(updateFn) {
  // Fallback: just update the DOM instantly
  if (!document.startViewTransition) {
    updateFn();
    return;
  }

  document.startViewTransition(() => updateFn());
}
```

```css
/* Only apply transition styles if supported */
@supports (view-transition-name: none) {
  .hero { view-transition-name: hero; }

  ::view-transition-old(hero) {
    animation: fade-scale-out 250ms ease-out both;
  }
  ::view-transition-new(hero) {
    animation: fade-scale-in 300ms ease-in both;
  }
}
```

### View Transitions (Cross-Document)

```css
/* This rule is safely ignored by browsers that don't support it */
@view-transition {
  navigation: auto;
}

/* Guard transition-specific styles */
@supports (view-transition-name: none) {
  .page-header { view-transition-name: header; }
  .main-content { view-transition-name: content; }

  ::view-transition-group(header) {
    animation-duration: 300ms;
  }
  ::view-transition-group(content) {
    animation-duration: 250ms;
  }
}
```

**Strategy**: Pages load normally in unsupported browsers. The `@view-transition` rule is unknown and ignored — no breakage.

### @starting-style

```css
/* Broad support — but guard with @supports for very old browsers */
.popover {
  opacity: 1;
  transform: scale(1);
  transition: opacity 200ms ease, transform 200ms ease;
}

/* @starting-style is baseline — this works in all modern browsers */
.popover {
  @starting-style {
    opacity: 0;
    transform: scale(0.95);
  }
}

/* For the display transition, check discrete support */
@supports (transition-behavior: allow-discrete) {
  .popover {
    transition: opacity 200ms ease, transform 200ms ease,
                display 200ms allow-discrete, overlay 200ms allow-discrete;
  }

  .popover:not(:popover-open) {
    opacity: 0;
    transform: scale(0.95);
    display: none;
  }
}
```

**Strategy**: `@starting-style` itself is well-supported. The main concern is `transition-behavior: allow-discrete` for `display`/`overlay` transitions. Guard that part specifically.

### Anchor Positioning

```css
/* Feature detection for anchor positioning */
@supports (anchor-name: --a) {
  .trigger { anchor-name: --trigger; }

  .tooltip {
    position: fixed;
    position-anchor: --trigger;
    position-area: top center;
    margin-bottom: 0.5rem;

    position-try-fallbacks: --bottom;
  }

  @position-try --bottom {
    position-area: bottom center;
    margin-top: 0.5rem;
  }
}

/* Fallback for unsupported browsers: manual absolute positioning */
@supports not (anchor-name: --a) {
  .tooltip-wrapper {
    position: relative;
  }

  .tooltip {
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    margin-bottom: 0.5rem;
  }
}
```

**Strategy**: Use `@supports (anchor-name: --a)` to detect. Provide a classic `position: absolute` fallback. For JS-heavy apps, Floating UI remains a solid fallback.

### Container Queries

```css
/* Container queries are baseline — safe for production */
.card-wrapper {
  container-type: inline-size;
  container-name: card;
}

/* Size queries: well supported */
@container card (min-width: 400px) {
  .card { flex-direction: row; }
}

/* Style queries on custom properties: Chrome/Edge 111+, Safari 18+, Firefox 151+ */
@supports (container-type: inline-size) {
  /* Size queries are safe — ~94% coverage */
}

/* Style queries: progressive enhancement only */
@container style(--theme: dark) {
  .card { background: oklch(0.2 0.02 250); }
}
/* Fallback: use a class or media query for unsupported browsers */
```

---

## Progressive Enhancement Strategies

### Strategy 1: Layered Animation (Recommended)

Build in layers — each layer adds richness but nothing breaks without it.

```css
/* Layer 0: Content is visible, no animation */
.section-title {
  opacity: 1;
}

/* Layer 1: Simple transition (universally supported) */
.section-title {
  transition: opacity 400ms ease, transform 400ms ease;
}
.section-title.visible {
  opacity: 1;
  transform: translateY(0);
}

/* Layer 2: Scroll-driven (modern browsers only) */
@supports (animation-timeline: scroll()) {
  .section-title {
    animation: reveal linear both;
    animation-timeline: view();
    animation-range: entry 0% entry 80%;
    /* Remove the JS-toggled class approach */
    transition: none;
  }

  @keyframes reveal {
    from { opacity: 0; transform: translateY(1.5rem); }
    to   { opacity: 1; transform: translateY(0); }
  }
}
```

### Strategy 2: View Transition as Enhancement

```js
// Router integration example (works with any framework)
async function navigateTo(url) {
  const response = await fetch(url);
  const html = await response.text();
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');

  const updateDOM = () => {
    document.title = doc.title;
    document.querySelector('main').replaceWith(
      doc.querySelector('main')
    );
  };

  if (document.startViewTransition) {
    document.startViewTransition(updateDOM);
  } else {
    updateDOM();
  }
}
```

```css
/* Cross-document: progressive by nature */
@view-transition { navigation: auto; }

/* Reduce motion: respect user preferences */
@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) {
    animation-duration: 0.01ms !important;
  }
}
```

### Strategy 3: @starting-style + Popover API

Full native modal with enter/exit animation, zero JavaScript.

```html
<button popovertarget="menu">Open</button>

<div id="menu" popover>
  <p>Menu content</p>
</div>
```

```css
[popover] {
  /* Open state */
  opacity: 1;
  transform: translateY(0) scale(1);
  transition: opacity 250ms ease, transform 250ms ease,
              display 250ms allow-discrete, overlay 250ms allow-discrete;

  /* Entry animation */
  @starting-style {
    opacity: 0;
    transform: translateY(-0.5rem) scale(0.97);
  }
}

/* Exit animation */
[popover]:not(:popover-open) {
  opacity: 0;
  transform: translateY(-0.5rem) scale(0.97);
}
```

### Strategy 4: Anchor + Popover Combo (Animated Tooltip)

```html
<button id="tip-trigger" popovertarget="tip">Hover me</button>

<div id="tip" popover="hint">
  Tooltip content
</div>
```

```css
/* The anchor must declare its name in CSS. The HTML `anchor` attribute is
   non-standard and experimental — never rely on it. */
#tip-trigger {
  anchor-name: --trigger;
}

[popover="hint"] {
  position: fixed;
  position-anchor: --trigger;
  position-area: top center;
  margin-bottom: 0.5rem;

  /* Animation */
  opacity: 1;
  transform: translateY(0);
  transition: opacity 150ms ease, transform 150ms ease,
              display 150ms allow-discrete, overlay 150ms allow-discrete;

  @starting-style {
    opacity: 0;
    transform: translateY(4px);
  }

  position-try-fallbacks: --bottom, --left, --right;
}

@position-try --bottom {
  position-area: bottom center;
  margin-top: 0.5rem;
}
@position-try --left {
  position-area: left center;
  margin-right: 0.5rem;
}
@position-try --right {
  position-area: right center;
  margin-left: 0.5rem;
}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  [popover="hint"] {
    transition-duration: 0.01ms;
  }
}
```

---

## Accessibility Checklist

```css
/* ALWAYS include this in any project with animations */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

For scroll-driven animations specifically:

```css
@media (prefers-reduced-motion: reduce) {
  .reveal {
    animation: none;
    opacity: 1;
    transform: none;
  }
}
```

---

## Performance Notes

| Property | Rendering Cost | GPU Composited |
|---|---|---|
| `transform` | Low | Yes |
| `opacity` | Low | Yes |
| `filter` / `backdrop-filter` | Medium | Yes |
| `clip-path` | Medium | Yes (in most browsers) |
| `background` (gradients) | Medium | No — repaint |
| `width` / `height` | High | No — reflow + repaint |
| `top` / `left` / `right` / `bottom` | High | No — reflow + repaint |
| `box-shadow` | High | No — repaint |

Best practices:
- Use `will-change` sparingly and only on elements about to animate — never `will-change: transform` on 50 elements
- Prefer `translate`, `scale`, `rotate` individual properties over `transform` shorthand when only one axis changes (allows independent transitions)
- For scroll-driven animations, the browser automatically optimizes — no `will-change` needed
- Test with Chrome DevTools > Rendering > "Highlight areas outside the compositing layers" to verify GPU compositing
