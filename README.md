# creative-excellence

> Two skills. One standard. Zero AI slop.

Creative coding plugin for [Claude Code](https://claude.ai/code) — transforms any interface from functional to exceptional through motion design, interaction patterns, and visual systems.

---

## Skills

### `/creative-excellence` — The Craftsman

Takes any creative request and makes it exceptional. Adapts to your stack and scope.

**Pipeline:** Scan stack → Evaluate scope → Propose interaction thesis → Load sub-skills → Implement → Mini-audit

- Detects your dependencies automatically (GSAP, Framer Motion, Three.js, CSS...)
- Proposes an **interaction thesis** before writing a single line of code
- Scales from a hover effect to a full page of scroll-driven animations
- Runs a quick audit on exit: `prefers-reduced-motion`, exit animations, layout performance

### `/design-excellence` — The Architect

Builds a complete visual universe from scratch. Brainstorm first, implement second.

**Pipeline:** Brainstorm → Define visual + interaction thesis → Generate design system → Implement → Full audit

- Mandatory creative direction session before any code
- Generates a persistent `MASTER.md` design system (palette, typography, spacing, motion tokens)
- Full audit at the end: motion gaps, accessibility, color consistency, responsive, performance
- Optional MCP integration (Stitch, Nano Banana, 21st.dev Magic)

### When to use which

| Situation | Skill |
|---|---|
| "Add a scroll animation to this section" | `/creative-excellence` |
| "Make this dropdown feel snappy" | `/creative-excellence` |
| "Redesign the entire landing page" | `/design-excellence` |
| "Build me a portfolio from scratch" | `/design-excellence` |

---

## Sub-skills

Internal modules loaded dynamically by the orchestrators. Not invocable directly.

| Sub-skill | Scope | Files |
|---|---|---|
| **motion-principles** | Timing, easing, enter/exit, accessibility | SKILL + 3 references |
| **gsap** | Core, timeline, ScrollTrigger, plugins | SKILL + 4 references |
| **framer-motion** | AnimatePresence, layout, gestures, motion values | SKILL + 1 reference |
| **css-native** | Scroll-driven, View Transitions, @starting-style | SKILL + 1 reference |
| **threejs-r3f** | Three.js, React Three Fiber, shaders, postprocessing | SKILL + 2 references |
| **canvas-generative** | Particles, flow fields, noise, fractals, L-systems | SKILL + 1 reference |
| **design-audit** | Motion Gap Analysis, a11y, performance, consistency | SKILL |
| **ui-ux-pro-max** | Design system intelligence (50 styles, 21 palettes, 9 stacks) | SKILL + data + scripts |

---

## Installation

```bash
# Add the plugin marketplace
/plugin marketplace add git@github.com:AThevon/creative-excellence.git

# Install
/plugin install creative-excellence
```

Or as a git submodule in your dotfiles:

```bash
git submodule add git@github.com:AThevon/creative-excellence.git claude/plugins/creative-excellence
ln -sf ~/.dotfiles/claude/plugins/creative-excellence ~/.claude/plugins/creative-excellence
```

---

## Architecture

```
creative-excellence/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   ├── creative-excellence/SKILL.md      ← orchestrator
│   ├── design-excellence/SKILL.md        ← orchestrator
│   └── _creative/                        ← internal sub-skills
│       ├── motion-principles/
│       ├── gsap/
│       ├── framer-motion/
│       ├── css-native/
│       ├── threejs-r3f/
│       ├── canvas-generative/
│       ├── design-audit/
│       └── ui-ux-pro-max/
└── README.md
```

Orchestrators detect the plugin root at runtime and load sub-skills via `Read`. Sub-skills in `_creative/` are never invoked directly — the underscore prefix keeps them internal.

---

## Credits

Built by studying the best creative coding resources available:

- **[mxyhi/ok-skills](https://github.com/mxyhi/ok-skills)** — Granular GSAP decomposition, "Do Not" patterns, interaction thesis concept
- **[freshtechbro/claudedesignskills](https://github.com/freshtechbro/claudedesignskills)** — BAD/GOOD pitfall patterns, reference file separation
- **[kylezantos/design-motion-principles](https://github.com/kylezantos/design-motion-principles)** — Designer perspectives (Emil Kowalski, Jakub Krehel, Jhey Tompkins), Motion Gap Analysis
- **[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)** — `frontend-design` plugin, anti-AI slop philosophy

---

## License

[MIT](LICENSE)
