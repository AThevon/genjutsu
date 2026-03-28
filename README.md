# creative-skills

Creative coding skills for Claude Code — animations, 3D, design systems, motion principles.

> Work in progress — private repo, not yet published.

## Skills

### Orchestrators (user-invocable)

- **creative** — The craftsman. Adapts to your stack and scope — from a single dropdown to a full app. Scans dependencies, proposes an interaction thesis, loads the right sub-skills.
- **design-excellence** — The architect. Builds a complete visual universe. Brainstorms direction first, creates a design system, implements, audits.

### Sub-skills (loaded internally by orchestrators)

- **motion-principles** — Timing, easing, enter/exit patterns, accessibility. The foundation.
- **gsap** — GSAP core, timeline, ScrollTrigger, plugins (SplitText, Flip, MorphSVG...)
- **framer-motion** — AnimatePresence, layout animations, gestures, motion values
- **css-native** — Scroll-driven animations, View Transitions, @starting-style, zero dependencies
- **threejs-r3f** — Three.js + React Three Fiber, shaders, postprocessing, performance
- **canvas-generative** — Generative art, particles, flow fields, noise, fractals
- **design-audit** — Motion Gap Analysis, accessibility audit, performance audit
- **ui-ux-pro-max** — Design system intelligence (50 styles, 21 palettes, 9 stacks)

## Installation

```bash
/plugin marketplace add git@github.com:AThevon/creative-skills.git
/plugin install creative-skills@creative
```

## Inspired by

This plugin was built by studying and learning from the best creative coding resources available:

- [mxyhi/ok-skills](https://github.com/mxyhi/ok-skills) — Granular GSAP skill decomposition, "Do Not" patterns, visual/interaction thesis concept
- [freshtechbro/claudedesignskills](https://github.com/freshtechbro/claudedesignskills) — Pitfall BAD/GOOD patterns, reference file separation
- [kylezantos/design-motion-principles](https://github.com/kylezantos/design-motion-principles) — Designer perspectives (Emil Kowalski, Jakub Krehel, Jhey Tompkins), Motion Gap Analysis methodology
- [anthropics/claude-plugins-official/frontend-design](https://github.com/anthropics/claude-plugins-official) — Anti-AI slop philosophy
