---
name: motion-principles
description: "Motion design foundation - timing, easing, enter/exit patterns, accessibility, performance."
---

# Motion Principles

> The foundation. Loaded by every creative skill invocation.
> Concise rules here. Deep-dive in `references/`.

---

## Timing Rules

| Context | Duration | Why |
|---|---|---|
| Micro-interaction (toggle, hover, focus) | 100-150ms | Instant feedback, no perceived delay |
| UI transition (modal, drawer, tab switch) | 200-300ms | Smooth but never sluggish |
| Page/route transition | 300-500ms | Establishes spatial narrative |
| Scroll-driven / 3D | Free (progress-based) | Tied to user input, no fixed duration |

**Frequency rule:** The more often an animation plays, the shorter and subtler it must be.
A button hover (1000x/day) = 100ms opacity. An onboarding reveal (1x ever) = 600ms+ full choreography.

---

## Easing Cheat Sheet

| Action | Easing | Why |
|---|---|---|
| Element enters | `ease-out` / spring | Decelerates into resting position (natural arrival) |
| Element exits | `ease-in` | Accelerates away (gets out of the way) |
| Element moves between states | `ease-in-out` | Smooth start and stop |
| Scroll-synced | `linear` / `none` | Matches 1:1 with input, no lag perception |
| Bouncy/playful | spring (underdamped) | Overshoot creates life |
| Snappy UI | `cubic-bezier(0.2, 0, 0, 1)` | Fast start, smooth land |

> **Exit is always more subtle than enter.**
> Enter: 300ms ease-out, full choreography. Exit: 200ms ease-in, opacity only.

---

## Accessibility (Non-Negotiable)

### prefers-reduced-motion -- MANDATORY

Every animated component must respect this. No exceptions.

**CSS:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**JS (hook pattern):**
```js
function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(() =>
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handler = (e) => setReduced(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);
  return reduced;
}
```

**GSAP:**
```js
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
gsap.defaults({ duration: reduced ? 0 : 0.5 });
```

### Other a11y requirements
- Focus indicators must never be hidden by animations
- Animated content must meet WCAG contrast ratios at every frame (no mid-transition fading to invisible text)
- Looping animations: provide a pause mechanism

---

## Universal "Do Not" Rules

### 1. Never animate width/height/top/left

Triggers layout recalculation every frame = jank.

```css
/* BAD */
.drawer { transition: height 0.3s ease; }
.drawer.open { height: 400px; }

/* GOOD */
.drawer { transition: transform 0.3s ease-out; transform: translateY(100%); }
.drawer.open { transform: translateY(0); }
```

### 2. Never scale to 0

`scale(0)` causes elements to vanish in a black hole. Always keep a minimum.

```css
/* BAD */
.modal-exit { transform: scale(0); }

/* GOOD */
.modal-exit { transform: scale(0.95); opacity: 0; }
```

### 3. Never ease-in on an entry

Ease-in = slow start. An entering element that hesitates feels broken.

```css
/* BAD */
.card-enter { animation: fadeIn 0.3s ease-in; }

/* GOOD */
.card-enter { animation: fadeIn 0.3s ease-out; }
/* OR spring via JS for natural feel */
```

### 4. Never exceed 500ms on a UI interaction

Modals, dropdowns, tooltips, tabs -- users are waiting. Respect their time.

```js
// BAD
gsap.to(modal, { opacity: 1, y: 0, duration: 0.8 });

// GOOD
gsap.to(modal, { opacity: 1, y: 0, duration: 0.25, ease: "power2.out" });
```

### 5. Never skip prefers-reduced-motion

This is an accessibility requirement, not a nice-to-have.

```js
// BAD
gsap.from('.hero-title', { opacity: 0, y: 40, duration: 0.6 });

// GOOD
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!prefersReduced) {
  gsap.from('.hero-title', { opacity: 0, y: 40, duration: 0.6 });
}
```

---

## Performance Checklist

- Only animate `transform` and `opacity` (composite-only properties)
- Use `will-change` sparingly and remove it after animation completes
- Prefer `requestAnimationFrame` over `setTimeout`/`setInterval` for JS animations
- For scroll-driven: CSS `animation-timeline` > JS `IntersectionObserver` > scroll listeners
- Test on low-end devices (throttle CPU 4x in DevTools)

---

## Quick Reference: Loading Sub-skills

| Need | Load |
|---|---|
| Easing deep-dive, spring configs | `references/easing-guide.md` |
| Copy-paste enter/exit patterns | `references/enter-exit-recipes.md` |
| Designer-weighted style choice | `references/designers.md` |
| GSAP specifics | `../gsap/SKILL.md` |
| Framer Motion specifics | `../framer-motion/SKILL.md` |
| CSS-only animations | `../css-native/SKILL.md` |
