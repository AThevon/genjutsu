# genjutsu

> The art of illusion. Cast motion. Paint signatures. Zero AI slop.

Creative coding skills for [Claude Code](https://claude.ai/code) and [claude.ai](https://claude.ai) - transforms any interface from functional to exceptional through motion design, interaction patterns, and visual systems. Covers Web (React, Vue, Svelte, vanilla CSS, Three.js, Canvas), Android (Jetpack Compose, Compose Multiplatform), and Apple (SwiftUI iOS + macOS).

> **v3.0 - rebrand**: this plugin used to be called `creative-excellence`. The skills `/creative-excellence:creative-excellence` and `/creative-excellence:design-excellence` are now `/genjutsu:cast` and `/genjutsu:paint`. See [CHANGELOG.md](./CHANGELOG.md) for the migration steps if you had v2.x installed.

---

## Skills

### `/genjutsu:cast` - The Illusionist

Takes any creative request and makes it exceptional. Adapts to your stack and scope.

**Pipeline:** Scan stack -> Evaluate scope -> Propose interaction thesis -> Load sub-skills -> Implement -> Mini-audit

- Detects your dependencies automatically across web (GSAP, Framer Motion, Three.js, CSS), Android (Jetpack Compose, Compose Multiplatform) and Apple (SwiftUI iOS / macOS)
- Proposes an **interaction thesis** before writing a single line of code
- Scales from a single hover effect to a full scroll-driven page or a Compose `SharedTransitionLayout` flow
- Runs a quick audit on exit: reduced-motion, exit animations, recomposition, hitches, layout performance

### `/genjutsu:paint` - The Master Painter

Builds a complete visual universe from scratch. Brainstorm first, implement second.

**Pipeline:** Brainstorm -> Define visual + interaction thesis -> Generate design system -> Implement -> Full audit

- Mandatory creative direction session before any code
- Generates a persistent stack-aware `MASTER.md` design system (Tailwind/CSS for web, `Theme.kt` for Compose, `Color+App.swift` for SwiftUI, `commonMain` for CMP)
- Full audit at the end: motion gaps, accessibility, color consistency, responsive, performance, native hitches
- Optional MCP integration (Stitch, Nano Banana, 21st.dev Magic)

### When to use which

| Situation | Skill |
|---|---|
| "Add a scroll animation to this section" | `/genjutsu:cast` |
| "Make this dropdown feel snappy" | `/genjutsu:cast` |
| "Add a snappy spring to this Compose button" | `/genjutsu:cast` |
| "Polish the matchedGeometryEffect on this SwiftUI screen" | `/genjutsu:cast` |
| "Redesign the entire landing page" | `/genjutsu:paint` |
| "Build me a portfolio from scratch" | `/genjutsu:paint` |
| "Build a SwiftUI iOS app design system from scratch" | `/genjutsu:paint` |
| "Bootstrap a Compose Multiplatform design system" | `/genjutsu:paint` |

---

## Sub-skills

Internal modules loaded dynamically by the orchestrators. Not invocable directly.

### Foundation (always loaded)

| Sub-skill | Scope | Files |
|---|---|---|
| motion-principles | Timing, easing, cross-platform reduced-motion API, BAD/GOOD do-not rules | SKILL + 3 references |

### Shared layers (loaded by context)

| Sub-skill | Scope | Files |
|---|---|---|
| mobile-principles | Touch targets, no-hover doctrine, thumb zones, safe areas, gestures, mobile perf budgets | SKILL + 2 references |
| desktop-principles | Hover-mandatory, pointer precision, keyboard shortcuts, multi-window, focus management | SKILL + 2 references |
| design-audit | Multi-stack greps (web/Compose/SwiftUI), bundle size, Layout Inspector, Instruments Hitches | SKILL |
| ui-ux-pro-max | Design system intelligence (50 styles, 21 palettes, 50 font pairings, 9 stacks) | SKILL + data + scripts |

### Web stack

| Sub-skill | Scope | Files |
|---|---|---|
| gsap | Core, timeline, ScrollTrigger, plugins | SKILL + 4 references |
| framer-motion | AnimatePresence, layout, gestures, motion values | SKILL + 1 reference |
| css-native | Scroll-driven, View Transitions, @starting-style | SKILL + 1 reference |
| threejs-r3f | Three.js, React Three Fiber, shaders, postprocessing | SKILL + 2 references |
| canvas-generative | Particles, flow fields, noise, fractals, L-systems | SKILL + 1 reference |

### Android stack

| Sub-skill | Scope | Files |
|---|---|---|
| compose-motion | animate*AsState, AnimatedVisibility, SharedTransitionLayout, springs, gestures | SKILL + 3 references |
| compose-graphics | M3 Expressive motion physics, AGSL shaders (Android 13+), Canvas/DrawScope | SKILL + 3 references |
| compose-multiplatform | KMP/CMP patterns, expect/actual, iOS/Android/Desktop interop | SKILL + 2 references |

### Apple stack

| Sub-skill | Scope | Files |
|---|---|---|
| swiftui-motion | withAnimation, transitions, matchedGeometryEffect, PhaseAnimator, KeyframeAnimator, gestures | SKILL + 3 references |
| swiftui-graphics | Metal shaders (.colorEffect / .layerEffect / .distortionEffect), .visualEffect, Liquid Glass (iOS 26), Canvas | SKILL + 3 references |

---

## Installation

### claude.ai (web/app)

**Prerequisites:** Plan Pro, Max, Team or Enterprise with "Code execution" enabled.

Each release provides two ways to download:

- **Individual ZIPs** - one per skill (`cast.zip`, `paint.zip`, `gsap.zip`, `compose-motion.zip`, `swiftui-graphics.zip`...), ready to upload directly
- **`genjutsu-all.zip`** - a single archive containing everything. You need to **extract it first**, then upload each sub-folder as a separate ZIP (claude.ai accepts one skill per upload)

**Option A - From GitHub Releases (recommended):**

1. Go to the [Releases](https://github.com/AThevon/genjutsu/releases) page
2. Download the individual ZIPs (or the all-in-one and extract it)
3. On claude.ai, go to **Customize > Skills > Upload ZIP**
4. Upload each skill ZIP and enable the toggle

**Option B - Build from source:**

```bash
git clone https://github.com/AThevon/genjutsu.git
cd genjutsu
./package-for-claude-ai.sh
# ZIPs are in dist/ (18 total: 15 sub-skills + 2 orchestrators + 1 all-in-one)
```

### Install matrix by stack

On claude.ai you upload one ZIP per skill. Pick what matches your stack. The two orchestrators (`cast`, `paint`) plus `motion-principles`, `design-audit`, `ui-ux-pro-max` are baseline for everyone.

| Your stack | ZIPs to upload (in addition to baseline) |
|---|---|
| Web only | mobile-principles, desktop-principles, gsap, framer-motion, css-native, threejs-r3f, canvas-generative |
| Android Compose only | mobile-principles, compose-motion, compose-graphics |
| iOS SwiftUI only | mobile-principles, swiftui-motion, swiftui-graphics |
| macOS SwiftUI only | desktop-principles, swiftui-motion, swiftui-graphics |
| Multi-target Apple (iOS + macOS) | mobile-principles, desktop-principles, swiftui-motion, swiftui-graphics |
| Compose Multiplatform | mobile-principles, compose-motion, compose-graphics, compose-multiplatform, swiftui-motion (if iOS target) |
| All stacks | use `genjutsu-all.zip` (extract it first, then upload each sub-folder) |

Baseline (always upload these):

- cast (orchestrator)
- paint (orchestrator)
- motion-principles (foundation)
- design-audit (audit checks)
- ui-ux-pro-max (UI intelligence)

### Claude Code (CLI)

```bash
# Add the plugin marketplace
/plugin marketplace add git@github.com:AThevon/genjutsu.git

# Install
/plugin install genjutsu
```

Or as a git submodule in your dotfiles:

```bash
git submodule add git@github.com:AThevon/genjutsu.git claude/plugins/genjutsu
ln -sf ~/.dotfiles/claude/plugins/genjutsu ~/.claude/plugins/genjutsu
```

---

## Architecture

```
genjutsu/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   ├── cast/SKILL.md                       <- orchestrator (Illusionist)
│   ├── paint/SKILL.md                      <- orchestrator (Master Painter)
│   └── _jutsu/                             <- internal sub-skills (never invoked directly)
│       ├── motion-principles/              <- foundation, always loaded
│       ├── mobile-principles/              <- shared (touch contexts)
│       ├── desktop-principles/             <- shared (pointer/keyboard contexts)
│       ├── design-audit/                   <- shared (audit pipeline)
│       ├── ui-ux-pro-max/                  <- shared (design intel)
│       ├── gsap/                           <- web stack
│       ├── framer-motion/                  <- web stack
│       ├── css-native/                     <- web stack
│       ├── threejs-r3f/                    <- web stack
│       ├── canvas-generative/              <- web stack
│       ├── compose-motion/                 <- Android
│       ├── compose-graphics/               <- Android (M3 Expressive, AGSL, Canvas)
│       ├── compose-multiplatform/          <- KMP/CMP
│       ├── swiftui-motion/                 <- Apple
│       └── swiftui-graphics/               <- Apple (Metal, Liquid Glass, Canvas)
├── package-for-claude-ai.sh
├── CHANGELOG.md
└── README.md
```

Orchestrators detect the environment at runtime (Claude Code plugin directory or claude.ai `/mnt/skills/user/`) and pick what to load based on the SCAN phase. Sub-skills in `_jutsu/` are loaded by orchestrator according to detected stack and selected scope - `mobile-principles` and `desktop-principles` are auto-loaded when context matches (touch target vs pointer/keyboard target). The underscore prefix keeps sub-skills internal so they never get invoked directly.

---

## Voice

The skills speak in two registers:

- **During execution**: light ninja flair, short, signature ("Casting parallax on hero scroll.", "Brushing the color palette.")
- **In reports / final summaries / audits**: plain, factual, dev-readable. No mystic prose, no metaphors. Just what changed, files touched, next step.

---

## Credits

Built by studying the best creative coding resources available.

### Web foundation

- [mxyhi/ok-skills](https://github.com/mxyhi/ok-skills) - Granular GSAP decomposition, "Do Not" patterns, interaction thesis concept
- [freshtechbro/claudedesignskills](https://github.com/freshtechbro/claudedesignskills) - BAD/GOOD pitfall patterns, reference file separation
- [kylezantos/design-motion-principles](https://github.com/kylezantos/design-motion-principles) - Designer perspectives (Emil Kowalski, Jakub Krehel, Jhey Tompkins), Motion Gap Analysis
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) - `frontend-design` plugin, anti-AI-slop philosophy

### Android / Compose (v2.0)

- [aldefy/compose-skill](https://github.com/aldefy/compose-skill) - granular Compose docs with androidx source receipts
- [Meet-Miyani/compose-skill](https://github.com/Meet-Miyani/compose-skill) - Compose / CMP / KMP comprehensive
- [new-silvermoon/awesome-android-agent-skills](https://github.com/new-silvermoon/awesome-android-agent-skills) - Android architecture skills
- [skydoves/Orbital](https://github.com/skydoves/Orbital) - shared element transitions Compose multiplatform
- [fornewid/material-motion-compose](https://github.com/fornewid/material-motion-compose) - Material Motion patterns Compose + CMP
- [drinkthestars/shady](https://github.com/drinkthestars/shady) - AGSL shaders rendered in Compose
- [Mortd3kay/liquid-glass-android](https://github.com/Mortd3kay/liquid-glass-android) - glassmorphism AGSL Compose
- [JumpingKeyCaps/DynamicVisualEffectsAGSL](https://github.com/JumpingKeyCaps/DynamicVisualEffectsAGSL) - AGSL playground
- [mutualmobile/compose-animation-examples](https://github.com/mutualmobile/compose-animation-examples) - Compose animation collection

### Apple / SwiftUI (v2.0)

- [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) - SwiftUI best practices reference
- [twostraws/swift-agent-skills](https://github.com/twostraws/swift-agent-skills) - curated directory of Swift agent skills
- [twostraws/Inferno](https://github.com/twostraws/Inferno) - Metal shaders SwiftUI (the absolute reference)
- [Treata11/iShader](https://github.com/Treata11/iShader) - Metal Fragment Shaders for SwiftUI
- [jamesrochabrun/ShaderKit](https://github.com/jamesrochabrun/ShaderKit) - composable Metal shaders + holographic UI
- [raphaelsalaja/metallurgy](https://github.com/raphaelsalaja/metallurgy) - SwiftUI Metal Shaders library
- [eleev/swiftui-new-metal-shaders](https://github.com/eleev/swiftui-new-metal-shaders) - SwiftUI 5 Metal Shader Collection
- [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) - SwiftUI animations + transitions + PhaseAnimator
- [dpearson2699/swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills) - 83 Swift skills (incl. swiftui-animation, gestures, liquid-glass)
- [rshankras/claude-code-apple-skills](https://github.com/rshankras/claude-code-apple-skills) - Apple platform skills
- [GetStream/swiftui-spring-animations](https://github.com/GetStream/swiftui-spring-animations) - guide complete SwiftUI Spring
- [amosgyamfi/open-swiftui-animations](https://github.com/amosgyamfi/open-swiftui-animations) - collection SwiftUI animations
- [Shubham0812/SwiftUI-Animations](https://github.com/Shubham0812/SwiftUI-Animations) - 20+ custom SwiftUI animations + Metal

### UX / motion theory

- Steven Hoober (thumb zones research) - "Designing for Touch"
- [Material Design 3 - Motion](https://m3.material.io/styles/motion/overview/specs) and [M3 Expressive](https://m3.material.io/blog/m3-expressive-motion-theming)
- [Apple HIG iOS](https://developer.apple.com/design/human-interface-guidelines/) and [macOS](https://developer.apple.com/design/human-interface-guidelines/macos)

---

## License

[MIT](LICENSE)
