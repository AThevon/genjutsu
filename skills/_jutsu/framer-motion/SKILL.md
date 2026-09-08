---
name: framer-motion
description: "Framer Motion / Motion sub-skill - AnimatePresence, layout animations, gestures, motion values."
---

> **Version-sensitive.** Every API name, SDK gate and browser-support claim below was
> verified on **2026-09-08** against primary sources. What against, and when, is in
> `_jutsu/VERSIONS.md`. If that date is old, re-verify before acting on a version number.

# Framer Motion — Sub-skill

> **Two package names, one library.** Framer Motion was renamed to Motion. `motion` and
> `framer-motion` both publish the same version (13.2.0 as of 2026-09-08): `motion` declares
> `"framer-motion": "^13.2.0"` as a dependency and `motion/react` re-exports it. Neither is
> broken, and `framer-motion` is still the one most installed projects have.
>
> **Read `package.json` and follow what is there.** Do not migrate a project from one to the
> other unless the user asks - that is Iron Rule 8 in `cast` / 10 in `paint`.
>
> | In `package.json` | Import from | Install line |
> |---|---|---|
> | `motion` | `"motion/react"` | `npm install motion` |
> | `framer-motion` | `"framer-motion"` | `npm install framer-motion` |
> | both | whichever the file you are editing already imports; say the project is mid-migration | - |
>
> Every API in this skill is identical across the two names at v13. Where a symbol is newer
> than v11, it is flagged inline. Peers: `react` / `react-dom` `^18 || ^19`.

## When to use Framer Motion vs alternatives

| Criteria | Framer Motion | GSAP | Native CSS |
|---------|--------------|------|-----------|
| Layout animations | Excellent (layoutId) | Manual | Impossible |
| Exit animations | AnimatePresence | Timeline reverse | Limited (display) |
| Gestures (drag, hover) | Native, declarative | Draggable plugin | Basic |
| Scroll-driven | useScroll + useTransform | ScrollTrigger (more powerful) | scroll-timeline |
| Complex orchestration | Variants + propagation | Timeline (more flexible) | @keyframes |
| Bundle size | ~50kb tree-shaken | ~30kb core | 0kb |
| React integration | Native, component-first | Refs + useGSAP | className toggle |

**Rule**: Framer Motion for React UI interactions (modals, toasts, reorder, shared layout). GSAP for complex timelines, cinematic scroll-driven, SVG morphing.

## AnimatePresence — Exit animations

```tsx
<AnimatePresence mode="wait">
  {isVisible && (
    <motion.div
      key="unique-key"        // REQUIRED — identifies the component
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    />
  )}
</AnimatePresence>
```

- `mode="wait"` — waits for exit to finish before enter (page transitions)
- `mode="sync"` — exit and enter simultaneously
- `mode="popLayout"` — removes from flow immediately (good for lists)
- `onExitComplete` — callback when all exit animations are finished

## Layout animations

```tsx
// Shared layout — the element "slides" between two positions
<motion.div layoutId="highlight" className={activeTab === id ? "active" : ""} />

// Auto layout — animates position/size when layout changes
<motion.div layout>
  {isExpanded && <motion.p layout>Additional content</motion.p>}
</motion.div>

// layout="position" — animates position only (not size)
// layout="size" — animates size only
// layout="preserve-aspect" — preserves the ratio during the transition
```

## Variants — Propagation and orchestration

```tsx
import { stagger } from "motion/react";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      // staggerChildren + staggerDirection are DEPRECATED (Motion 12.22, Jul 2025).
      // Pass a stagger() function to delayChildren instead.
      delayChildren: stagger(0.08, { startDelay: 0.2 }),
      // reverse order: stagger(0.08, { from: "last" })
      // also available: from: "first" | "center" | "last" | index, and ease
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

<motion.ul variants={container} initial="hidden" animate="show">
  {items.map((i) => (
    <motion.li key={i.id} variants={item} />
  ))}
</motion.ul>
```

Variants **automatically propagate** to motion children — no need for `initial`/`animate` on children.

## Gestures

```tsx
<motion.div
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  whileFocus={{ borderColor: "#3b82f6" }}
  // Drag
  drag               // true = x+y, "x" = horizontal only, "y" = vertical only
  dragConstraints={{ left: -100, right: 100, top: -50, bottom: 50 }}
  dragElastic={0.2}  // 0 = rigid, 1 = free (default 0.35)
  dragSnapToOrigin   // returns to initial position
  onDragEnd={(e, info) => {
    if (info.offset.x > 100) handleSwipe("right");
  }}
/>
```

## Motion values — Reactive without re-render

```tsx
const x = useMotionValue(0);
const opacity = useTransform(x, [-200, 0, 200], [0, 1, 0]);
const background = useTransform(x, [-200, 200], ["#ff0000", "#00ff00"]);

// Spring-based smoothing
const smoothX = useSpring(x, { stiffness: 300, damping: 30 });

// Scroll tracking
const { scrollY, scrollYProgress } = useScroll();
const parallaxY = useTransform(scrollYProgress, [0, 1], [0, -300]);

// Element-scoped scroll
const ref = useRef(null);
const { scrollYProgress } = useScroll({
  target: ref,
  offset: ["start end", "end start"],
});
```

**Motion values do NOT trigger React re-renders** — they update the DOM directly via `style`.

## Do Not

### Do not use motion with styled-components / Emotion without `isValidProp` (v13+)

Motion 13.0 removed `@emotion/is-prop-valid` as an optional dependency. Without explicit injection, motion-only props leak onto the DOM.

```tsx
import isPropValid from "@emotion/is-prop-valid";
import { MotionConfig } from "motion/react";

<MotionConfig isValidProp={isPropValid}>
  <App />
</MotionConfig>
```

Or reverse the composition so the styling library owns prop forwarding: `const MotionDiv = motion.create(StyledDiv)`.

### Do not setState in callbacks without a guard

```tsx
// BAD — infinite re-render if animate depends on state
onUpdate={(latest) => setPosition(latest.x)}

// GOOD — guard or useMotionValueEvent
const x = useMotionValue(0);
useMotionValueEvent(x, "change", (latest) => {
  if (latest > threshold) onThresholdReached();
});
```

### Do not use layout animation without a stable key

```tsx
// BAD — key changes every render, breaks layout tracking
<motion.div layout key={Math.random()} />

// GOOD — stable key derived from data
<motion.div layout key={item.id} />
```

### Do not forget the unique key on AnimatePresence

```tsx
// BAD — no key, exit animation does not trigger
<AnimatePresence>
  {isOpen && <motion.div exit={{ opacity: 0 }} />}
</AnimatePresence>

// GOOD — unique key for each conditional child
<AnimatePresence>
  {isOpen && <motion.div key="modal" exit={{ opacity: 0 }} />}
</AnimatePresence>
```

### Do not wrap an already animated component with motion.div

```tsx
// BAD — double animation, transform conflicts
<motion.div animate={{ x: 100 }}>
  <motion.div animate={{ x: -50 }}>Content</motion.div>
</motion.div>

// GOOD — single animation level per transform axis
<motion.div animate={{ x: 100 }}>
  <motion.div animate={{ opacity: 0.5 }}>Content</motion.div>
</motion.div>

// GOOD — use variants to coordinate parent/child
<motion.div variants={parent} animate="active">
  <motion.div variants={child} />
</motion.div>
```
