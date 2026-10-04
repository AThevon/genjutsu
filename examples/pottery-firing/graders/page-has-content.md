---
type: regex
target: { source: file, path: src/Firings.tsx }
match: contains
pattern: 'gsap|ScrollTrigger|[Tt]imeline|useScroll|requestAnimationFrame|[Ss]croll|from\s+["'']\.\.?/'
---

Positive guard: the firing stages section now moves with the scroll. The scaffold's
src/Firings.tsx imports nothing and mentions no scroll, timeline or animation frame, so it
fails this; it passes once the section uses gsap or ScrollTrigger, any scroll or timeline
binding, or imports a new local module that carries it.
