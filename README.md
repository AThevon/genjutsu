<p align="center">
  <img src="./assets/logo.png" alt="genjutsu logo" width="160" />
</p>

<h1 align="center">genjutsu</h1>

<p align="center"><em>The art of illusion. Cast motion. Paint signatures.</em></p>

<p align="center">
  <a href="https://genjutsu.athevon.dev"><strong>Website</strong></a>
  &nbsp;·&nbsp;
  <a href="https://genjutsu.athevon.dev/docs"><strong>Documentation</strong></a>
  &nbsp;·&nbsp;
  <a href="https://genjutsu.athevon.dev/docs/install"><strong>Install</strong></a>
</p>

<p align="center">
  <a href="https://github.com/AThevon/genjutsu/releases/latest"><img src="https://img.shields.io/github/v/release/AThevon/genjutsu?style=flat-square&color=b11523&label=release" alt="Latest release" /></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-b11523?style=flat-square" alt="MIT license" /></a>
  <img src="https://img.shields.io/badge/works%20with-Claude%20Code%20%2B%20claude.ai%20%2B%20Cowork-b11523?style=flat-square" alt="Works with Claude Code, claude.ai and Cowork" />
</p>

Creative coding skills for [Claude Code](https://claude.ai/code), [claude.ai](https://claude.ai) and [Cowork](https://claude.com/plugins-for/cowork) - transforms any interface from functional to exceptional through motion design, interaction patterns, and visual systems. Covers Web (React, Vue, Svelte, vanilla CSS, Three.js, Canvas), Android (Jetpack Compose, Compose Multiplatform), and Apple (SwiftUI iOS + macOS).

> **v3.0 - rebrand**: this plugin used to be called `creative-excellence`. The skills `/creative-excellence:creative-excellence` and `/creative-excellence:design-excellence` are now `/genjutsu:cast` and `/genjutsu:paint`. See [CHANGELOG.md](./CHANGELOG.md) for the migration steps if you had v2.x installed.

---

## Documentation

[genjutsu.athevon.dev](https://genjutsu.athevon.dev) is built with genjutsu itself. The ink on it is painted by your own scroll, and every mark is drawn in code, no image assets.

| Page | What is in it |
|---|---|
| [Overview](https://genjutsu.athevon.dev/docs) | What genjutsu is, how the pieces fit, the shortest path to seeing something move |
| [Install](https://genjutsu.athevon.dev/docs/install) | Both surfaces, verifying the install, updating, uninstalling |
| [`cast`](https://genjutsu.athevon.dev/docs/cast) | The seven-stage pipeline, its two validation gates, how to write a good request |
| [`paint`](https://genjutsu.athevon.dev/docs/paint) | The five phases, the two theses, what lands in your repo |
| [Modules](https://genjutsu.athevon.dev/docs/jutsu) | All fifteen, by family: [foundations](https://genjutsu.athevon.dev/docs/jutsu/foundations), [web](https://genjutsu.athevon.dev/docs/jutsu/web), [Apple](https://genjutsu.athevon.dev/docs/jutsu/apple), [Android](https://genjutsu.athevon.dev/docs/jutsu/android) |
| [Principles](https://genjutsu.athevon.dev/docs/principles) | The rules the skills enforce, and why each one exists |
| [FAQ](https://genjutsu.athevon.dev/docs/faq) | Plans, dependencies, cast against paint, what to check when output feels generic |

---

## Skills

### `/genjutsu:cast` - The Illusionist

Takes any creative request and makes it exceptional. Adapts to your stack and scope.

**Pipeline:** Scan stack -> Evaluate scope -> Propose interaction thesis -> Load sub-skills -> Implement -> Mini-audit

- Detects your dependencies automatically across web (GSAP, Framer Motion, Three.js, CSS), Android (Jetpack Compose, Compose Multiplatform) and Apple (SwiftUI iOS / macOS)
- Proposes an **interaction thesis** before writing a single line of code, and asks **how you want to see it** first
- Scales from a single hover effect to a full scroll-driven page or a Compose `SharedTransitionLayout` flow
- Runs a quick audit on exit: reduced-motion, exit animations, recomposition, hitches, layout performance

### `/genjutsu:paint` - The Master Painter

Builds a complete visual universe from scratch. Brainstorm first, implement second.

**Pipeline:** Brainstorm -> Define visual + interaction thesis -> Generate design system -> Implement -> Full audit

- Mandatory creative direction session before any code
- Shows the theses and the design system in the format you pick, instead of asking you to approve a palette as a list of hex codes
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

### Seeing what it proposes

Both skills stop and wait for your approval at a handful of points: the interaction thesis, the variants, the visual identity, the design system. A sentence cannot carry an easing curve and a list of hex codes cannot carry a palette, so before the first of those gates the skill asks how you want to see it.

| Mode | What you get |
|---|---|
| **Artifact** | A live page. The easing curve plotted with its exact value, an element actually performing the motion with a replay button, the raw numbers, a reduced-motion toggle. For a design system: swatches with their contrast ratios, a real type specimen, the five states of every component. |
| **Live preview** | A throwaway route in your own project - real stack, real tokens, real components. On Compose or SwiftUI, a `@Preview` / `#Preview` scratch file. Deleted once you have approved. |
| **Inline** | The sentence, in the conversation. Still the right answer for a 150ms hover. |

You are asked once. The choice holds for the rest of the session, later gates just announce the mode, and you switch by saying so. The preview is always throwaway: it exists to be looked at, never to become the implementation.

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
| ui-ux-pro-max | Design system intelligence (84 styles, 192 palettes, 74 font pairings, 25 charts, 22 stacks) | SKILL + data + scripts |

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

The short version is on the site: [genjutsu.athevon.dev/docs/install](https://genjutsu.athevon.dev/docs/install). The long version, including partial installs, is below.

### claude.ai (web/app)

**Prerequisites:** Plan Pro, Max, Team or Enterprise with "Code execution" enabled.

**Option A - single bundle (recommended):**

One upload, everything included (router + `cast` + `paint` + all sub-skills).

1. Download **[`genjutsu.zip`](https://github.com/AThevon/genjutsu/releases/latest/download/genjutsu.zip)**. That link always serves the newest release, so it never goes stale.
2. On claude.ai, go to **Customize > Skills > Upload skill** and upload `genjutsu.zip`.
3. Enable the toggle. Done - one skill, both `cast` and `paint` pipelines, all sub-skills bundled.

> Want to confirm it mounted correctly? Follow the 2-minute smoke test in [docs/claude-ai-testing.md](./docs/claude-ai-testing.md).

**How it shows up.** The bundle installs as a **single skill named `genjutsu`**. In a normal chat it appears as one entry - invoke `/genjutsu` (or just describe your task) and it routes to the `cast` or `paint` pipeline internally. Surfaces that expose skills as individual commands (e.g. a code workspace) show `/cast` and `/paint` directly. Either way the pipelines need **code execution** enabled to load their sub-skills. Prefer `/cast` and `/paint` as separate entries everywhere? Use Option B.

**Option B - individual skills:**

Prefer separate skills, or only part of the stack? Upload the individual ZIPs (one per skill). Baseline for everyone: `cast`, `paint`, `motion-principles`, `design-audit`, `ui-ux-pro-max`. Then add per stack:

| Your stack | ZIPs to upload (in addition to baseline) |
|---|---|
| Web only | mobile-principles, desktop-principles, gsap, framer-motion, css-native, threejs-r3f, canvas-generative |
| Android Compose only | mobile-principles, compose-motion, compose-graphics |
| iOS SwiftUI only | mobile-principles, swiftui-motion, swiftui-graphics |
| macOS SwiftUI only | desktop-principles, swiftui-motion, swiftui-graphics |
| Multi-target Apple (iOS + macOS) | mobile-principles, desktop-principles, swiftui-motion, swiftui-graphics |
| Compose Multiplatform | mobile-principles, compose-motion, compose-graphics, compose-multiplatform, swiftui-motion (if iOS target) |

**Build from source:**

```bash
git clone https://github.com/AThevon/genjutsu.git
cd genjutsu
./package-for-claude-ai.sh
# dist/ has genjutsu.zip (the bundle) + 17 individual skill ZIPs
```

### Claude Code (CLI)

Two slash commands, typed inside a Claude Code session:

```text
/plugin marketplace add AThevon/genjutsu
/plugin install genjutsu
```

Then run `/genjutsu:cast` or `/genjutsu:paint`. You can pass the request on the same line: `/genjutsu:cast make the pricing cards feel physical on hover`.

The marketplace also accepts the full git URL if you prefer it: `/plugin marketplace add git@github.com:AThevon/genjutsu.git`.

Or as a git submodule in your dotfiles:

```bash
git submodule add git@github.com:AThevon/genjutsu.git claude/plugins/genjutsu
ln -sf ~/.dotfiles/claude/plugins/genjutsu ~/.claude/plugins/genjutsu
```

---

### Cowork

Install it from the plugin panel, the same way as any other plugin, then invoke `/genjutsu:cast` or `/genjutsu:paint`.

```text
/plugin marketplace add AThevon/genjutsu
/plugin install genjutsu
```

Cowork mounts skills under a per-session root rather than a fixed path, so sub-skill resolution probes for it - see [Cowork compatibility](#cowork-compatibility) for the resolution order, what the preview gate maps to on this surface, and why `paint` shortens itself for one-component requests here.

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

Orchestrators detect the environment at runtime (Claude Code plugin directory, claude.ai `/mnt/skills/user/`, or a session-rooted Cowork mount - see [Cowork compatibility](#cowork-compatibility)) and pick what to load based on the SCAN phase. Sub-skills in `_jutsu/` are loaded by orchestrator according to detected stack and selected scope - `mobile-principles` and `desktop-principles` are auto-loaded when context matches (touch target vs pointer/keyboard target). The underscore prefix keeps sub-skills internal so they never get invoked directly.

---

## Cowork compatibility

genjutsu runs on three surfaces, and they mount the skill tree in three different places. Claude Code and claude.ai both have a fixed path. Cowork does not: it mounts under a per-session root that changes every run, for example `/sessions/<session-id>/mnt/.claude/skills/genjutsu/_jutsu`.

**Path detection.** The `genjutsu:shared:skill-base` block resolves `$SKILL_BASE` in this order, and stops at the first hit:

| Order | Host | How it resolves |
|---|---|---|
| 1 | claude.ai, single bundle | `_jutsu` found directly under `/mnt/skills/user` |
| 2 | claude.ai, individual skills | the `/mnt/skills/user` mount itself |
| 3 | Claude Code | `${CLAUDE_PLUGIN_ROOT}/skills/_jutsu`, then the newest numbered version under `~/.claude/plugins/cache` |
| 4 | Cowork, skills-directory installs | probed: `$PWD` and its ancestors, then `~/.claude/skills`, `/mnt/.claude/skills`, `/sessions`, matching `*/.claude/skills/*/_jutsu` |

Step 4 is new and runs **last**, so steps 1 to 3 behave exactly as they did before. Every probe is depth-capped, so none of them can walk the filesystem. When all four miss, the failure is now explicit: the error names each root that was tried instead of letting a `cat` fail silently.

**Preview mapping.** The preview gate offers artifact, live preview or inline. What each one means depends on the host:

| Host | A - artifact | B - live preview | C - inline |
|---|---|---|---|
| claude.ai | native artifact | throwaway route in your project | conversation text |
| Cowork | the host's persistent artifact | usually unavailable, no project checkout | the host's inline widget |
| Claude Code | the `Artifact` tool | throwaway route, or a `@Preview` / `#Preview` scratch file | conversation text |
| unknown | self-contained HTML at a temp path | not offered | conversation text |

The gate detects the host itself, before `LOAD` runs. Cowork is tested before Claude Code because both can have a `~/.claude` tree and only Cowork has the session-rooted mount, so the more specific signal has to win.

**Pipeline weight.** `cast` is the default entry point on every surface. `paint` is a five-phase pipeline and is disproportionate for the short requests that dominate on Cowork ("animate this word", "polish this hover"), so it now recognises **light scope** - one isolated component, no visual identity at stake, nothing downstream depending on it - and shortens to a single brainstorm question with no `MASTER.md` written. The gates stay; only their number goes down.

---

## Voice

The skills speak in two registers:

- **During execution**: light ninja flair, short, signature ("Casting parallax on hero scroll.", "Brushing the color palette.")
- **In reports / final summaries / audits**: plain, factual, dev-readable. No mystic prose, no metaphors. Just what changed, files touched, next step.

---

## Credits

Built by studying the best creative coding resources available.

### Design intelligence

- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT) - the `ui-ux-pro-max` sub-skill vendors this project's design dataset (styles, palettes, font pairings, UX guidelines, chart and stack guidance) and its Python search engine. See [skills/_jutsu/ui-ux-pro-max/UPSTREAM.md](./skills/_jutsu/ui-ux-pro-max/UPSTREAM.md) for the vendoring notes and divergences.

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
