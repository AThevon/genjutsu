# Changelog

All notable changes to this plugin are documented here. Format inspired by [Keep a Changelog](https://keepachangelog.com/).

## v3.0.0 - 2026-04-26

**BREAKING CHANGE - Rebrand**: `creative-excellence` is now `genjutsu`. The two orchestrators have new names that match the new theme.

### Renamed

- Plugin: `creative-excellence` -> `genjutsu`
- Orchestrator (creative coding): `creative-excellence` -> `cast` (The Illusionist)
- Orchestrator (design pipeline): `design-excellence` -> `paint` (The Master Painter)
- Internal sub-skills directory: `_creative/` -> `_jutsu/`
- GitHub repository: `AThevon/creative-excellence` -> `AThevon/genjutsu`

### Migration guide

**For users on Claude Code:**

```bash
# 1. Uninstall the old plugin
/plugin uninstall creative-excellence

# 2. Remove the old marketplace
/plugin marketplace remove creative-excellence

# 3. Add the new marketplace
/plugin marketplace add git@github.com:AThevon/genjutsu.git

# 4. Install
/plugin install genjutsu
```

Old invocations -> new invocations:

| Old | New |
|---|---|
| `/creative-excellence:creative-excellence` | `/genjutsu:cast` |
| `/creative-excellence:design-excellence` | `/genjutsu:paint` |

**For users on claude.ai:**

1. Remove the old `creative-excellence` and `design-excellence` skills from your skills list.
2. Re-download the latest release ZIPs (now named `cast.zip`, `paint.zip`, plus the renamed `genjutsu-all.zip`).
3. Re-upload everything.

**For users with the dotfiles submodule pattern:**

```bash
cd ~/.dotfiles

# Deinit the old submodule
git submodule deinit -f claude/plugins/creative-excellence
git rm -rf claude/plugins/creative-excellence
rm -rf .git/modules/claude/plugins/creative-excellence

# Re-add with the new URL
git submodule add git@github.com:AThevon/genjutsu.git claude/plugins/genjutsu

# Update install.sh and settings.json (replace creative-excellence with genjutsu)
# Then run install
./install.sh
```

### Added

- Voice rules in both `cast/SKILL.md` and `paint/SKILL.md`: light ninja flair during execution, plain factual reports at the end (no mystic prose in summaries).

### Notes

- Zero functional change. All sub-skills (`motion-principles`, `gsap`, `compose-motion`, `swiftui-graphics`, etc.) work identically. Only naming and voice changed.
- The old GitHub URL `github.com/AThevon/creative-excellence` automatically redirects to the new one.

## v2.0.0 - 2026-04-25

Major release: cross-platform expansion. The plugin now covers Web, Android (Jetpack Compose / Compose Multiplatform), and Apple (SwiftUI iOS + macOS) in addition to the existing web stacks.

### Added

- New shared layer `mobile-principles` (touch targets, no-hover doctrine, thumb zones, safe areas, gestures, mobile perf budgets) with 2 deep-dive references (`gestures-deep.md`, `accessibility-mobile.md`).
- New shared layer `desktop-principles` (hover-mandatory, pointer precision, keyboard shortcuts, multi-window, focus management) with 2 deep-dive references (`keyboard-patterns.md`, `multi-window.md`).
- New stack `compose-motion` (Jetpack Compose animation foundations: `animate*AsState`, `AnimatedVisibility`, `SharedTransitionLayout`, springs, gestures) with 3 deep-dives (`shared-transitions.md`, `gestures-compose.md`, `recomposition-and-anim.md`).
- New stack `compose-graphics` (advanced Compose visuals: M3 Expressive motion physics, AGSL shaders Android 13+, Canvas/DrawScope generative) with 3 deep-dives (`agsl-recipes.md`, `m3-expressive-deep.md`, `canvas-generative.md`).
- New stack `compose-multiplatform` (KMP/CMP patterns, expect/actual, iOS/Android/Desktop interop) with 2 deep-dives (`cmp-interop.md`, `cmp-platform-quirks.md`).
- New stack `swiftui-motion` (`withAnimation`, transitions, `matchedGeometryEffect`, `PhaseAnimator`, `KeyframeAnimator`, gestures) with 3 deep-dives (`springs-cheatsheet.md`, `phase-keyframe-deep.md`, `gestures-swiftui.md`).
- New stack `swiftui-graphics` (Metal shaders, `.visualEffect`, Liquid Glass iOS 26, Canvas) with 3 deep-dives (`metal-recipes.md`, `liquid-glass-deep.md`, `canvas-swiftui.md`).
- Stack-aware MASTER.md generation in `design-excellence` (now `genjutsu:paint`): produces Tailwind/CSS for web, Kotlin Theme.kt for Compose, Swift extensions for SwiftUI, KMP commonMain for CMP.
- Cross-platform AUDIT checklist in both orchestrators (Layout Inspector, Macrobenchmark, Instruments Time Profiler, Hitches Instrument, GPU Frame Capture).
- Conditional DISCOVER question for legacy bridge integration (XIB / storyboard / layout XML / setContentView detection).

### Changed

- Phase SCAN extended in both orchestrators to detect Android Compose (`androidx.compose`), Compose Multiplatform (`org.jetbrains.compose` + `kotlin-multiplatform`), SwiftUI (Package.swift / xcodeproj / @main App), and to distinguish iOS vs macOS targets.
- Phase LOAD restructured into layered tables (foundation always / context layers by detection / stack-specific by SCAN). Advanced sub-skills (`compose-graphics`, `swiftui-graphics`) only loaded for advanced thesis containing terms like "shader", "Metal", "AGSL", "Liquid Glass", "M3 Expressive".
- IRON RULES 7-8 generalized to be stack-agnostic (previously React/GSAP-specific).
- THESIS examples extended with cross-platform examples (SwiftUI matchedGeometryEffect, Compose SharedTransitionLayout, macOS hover, AGSL shader).
- `motion-principles` reduced-motion section now covers 5 platforms (Web CSS, Web JS, SwiftUI, UIKit, Compose) with code examples.
- `motion-principles` Universal Do Not Rules now include native (SwiftUI + Compose) BAD/GOOD examples in addition to CSS/JS/GSAP.
- `design-audit` now greps multi-stack (web + Compose + SwiftUI), reports bundle sizes for native libs (Lottie/Rive), and includes a stack-specific audit subsection (Layout Inspector / Macrobenchmark / Instruments Time Profiler / Hitches / GPU Frame Capture).

### Notes

- Zero web regression: existing web sub-skills (`gsap`, `framer-motion`, `css-native`, `threejs-r3f`, `canvas-generative`) and `ui-ux-pro-max` are unchanged.
- The plugin grows from 8 sub-skills to 15. The `package-for-claude-ai.sh` script automatically picks up new sub-skills (no script change needed).

## v1.1.0 and earlier

See git tags for details on previous releases.
