# Mobile Creative Excellence - Design Spec

> Extension du plugin `creative-excellence` pour couvrir Android (Kotlin / Jetpack Compose / Compose Multiplatform) et Apple (Swift / SwiftUI iOS + macOS), avec conservation des deux meta-skills existants (`creative-excellence`, `design-excellence`) et leur pipeline de détection auto + chargement dynamique des sub-skills.

**Status** : design validé, prêt pour implémentation.
**Date** : 2026-04-25.
**Author** : AThevon, en collaboration avec l'agent Claude.
**Target version** : v2.0.0.

---

## 1. Context et motivation

Le repo `creative-excellence` couvre actuellement uniquement le web (React, Vue, Svelte, Next.js, Astro - via GSAP, Framer Motion, CSS native, Three.js, Canvas). Les deux orchestrators (`creative-excellence`, `design-excellence`) suivent un pipeline strict : SCAN stack → DISCOVER → SCOPE → THESIS → LOAD sub-skills → IMPLEMENT → AUDIT.

L'écosystème des Claude Skills pour mobile natif (analyse menée 2026-04-25) montre :

- Côté Android : [aldefy/compose-skill](https://github.com/aldefy/compose-skill) (~412⭐), [Drjacky/claude-android-ninja](https://github.com/Drjacky/claude-android-ninja), [Meet-Miyani/compose-skill](https://github.com/Meet-Miyani/compose-skill), [new-silvermoon/awesome-android-agent-skills](https://github.com/new-silvermoon/awesome-android-agent-skills) (~757⭐), [dpconde/claude-android-skill](https://github.com/dpconde/claude-android-skill).
- Côté iOS/macOS : [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) (~3700⭐), [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill), [dpearson2699/swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills) (~480⭐), [rshankras/claude-code-apple-skills](https://github.com/rshankras/claude-code-apple-skills), [twostraws/swift-agent-skills](https://github.com/twostraws/swift-agent-skills) (curated).

**Constat clé** : ces skills couvrent l'architecture, la perf, la nav, les API basiques. **Aucun ne pousse le creative coding, le motion choreography, les shaders, l'interaction thesis "anti-AI-slop"**. C'est exactement le positionnement de ce repo. Il y a une niche claire à occuper.

## 2. Goals

1. Étendre les deux meta-skills (`creative-excellence`, `design-excellence`) à Android natif (Kotlin/Compose), Compose Multiplatform, et Apple (SwiftUI iOS + macOS), **sans changer leur API utilisateur** (un dev mobile lance la même commande qu'un dev web).
2. Garder le pipeline `SCAN → DISCOVER → SCOPE → THESIS → LOAD → IMPLEMENT → AUDIT` strictement identique. Seules les phases SCAN, LOAD et AUDIT sont étendues.
3. Atteindre une qualité équivalente à ce qui existe côté web, en s'appuyant sur les meilleurs repos open-source de l'écosystème (cités explicitement dans les sources et le README).
4. Préserver l'**architecture en couches** existante : foundation toujours chargé, sub-skills techniques chargés selon SCAN, sub-skills avancés chargés à la demande.
5. Permettre les workflows mixtes :
   - `/design-excellence` sur une app Android sans design existant → produit un design system Compose complet (`Theme.kt`, `Color.kt`, `Type.kt`, `Shapes.kt`, `Motion.kt`, `MASTER.md`).
   - `/creative-excellence` sur un écran de l'app (éditeur, dashboard, etc.) → respecte le design system existant + propose une thèse d'interaction adaptée.

## 3. Non-goals

- ❌ **Pas de support legacy explicite** : pas de sub-skill UIKit/Core Animation (iOS), pas de sub-skill Android Views/XML. Bridge minimal mentionné en phase DISCOVER si du legacy est détecté, mais aucun code legacy ne sera généré.
- ❌ **Pas de cibles cross-platform non-natives** : pas de React Native, pas de Flutter, pas d'Ionic.
- ❌ **Pas de cibles Apple niche** : pas de watchOS, tvOS, visionOS dans ce scope. Évaluables en phase 2 si demande.
- ❌ **Pas de migration auto** : les sub-skills enseignent et implémentent, ils ne migrent pas une codebase existante d'un stack à un autre.
- ❌ **Pas de modification de `ui-ux-pro-max`** : ce sub-skill est déjà multi-stack (liste explicitement `swiftui`, `react-native`, `flutter`, `jetpack-compose` parmi les 9 stacks supportés). On le réutilise tel quel.

## 4. Architecture en couches

```
Foundation (toujours chargé par les orchestrators)
└─ motion-principles                         [existant - retouche pour neutraliser web-bias]

Shared layers (chargés selon contexte détecté)
├─ mobile-principles      [NOUVEAU]          ← touch, hover-less, safe areas, thumb zones
├─ desktop-principles     [NOUVEAU]          ← hover, pointer fin, raccourcis, multi-window
├─ design-audit                              [existant - enrichi cross-platform]
└─ ui-ux-pro-max                             [existant - inchangé]

Stack-specific (chargés selon SCAN)

Web (existant, intouché) :
├─ gsap, framer-motion, css-native, threejs-r3f, canvas-generative

Android :
├─ compose-motion         [NOUVEAU]          ← base API d'animation Compose
├─ compose-graphics       [NOUVEAU]          ← M3 Expressive + AGSL + Canvas + graphicsLayer
└─ compose-multiplatform  [NOUVEAU]          ← patterns CMP / KMP + interop iOS

iOS / macOS :
├─ swiftui-motion         [NOUVEAU]          ← base API d'animation SwiftUI
└─ swiftui-graphics       [NOUVEAU]          ← Metal shaders + .visualEffect + Liquid Glass
```

**Total nouveaux sub-skills** : 7. **Existants modifiés** : 3 (motion-principles, design-audit, et les deux orchestrators). **Existants intouchés** : 6 (gsap, framer-motion, css-native, threejs-r3f, canvas-generative, ui-ux-pro-max).

### Pourquoi cette granularité (option C "hybride")

Sur web, le découpage actuel (`gsap`, `framer-motion`, `css-native`, `threejs-r3f`, `canvas-generative`) reflète des **stacks alternatifs** (un projet utilise GSAP OU Framer Motion). Sur mobile natif, dans Compose ou SwiftUI, il n'y a **qu'un seul stack par plateforme** mais plusieurs **niveaux d'avancement** (animation standard vs shaders/expressive). Le split base/advanced reflète mieux cette réalité, et permet de ne pas charger en context les Metal shaders quand le user fait juste un fade-in.

## 5. Détection de stack (phase SCAN étendue)

L'algorithme actuel grep uniquement `package.json`. On étend en cascade :

```bash
# 1. Web (existant, inchangé)
cat package.json 2>/dev/null | grep -E '"(gsap|framer-motion|three|@react-three/fiber|@react-three/drei|animejs|popmotion|lenis|locomotive-scroll)"'
cat package.json 2>/dev/null | grep -E '"(react|react-dom|vue|svelte|next|nuxt|astro|solid-js|qwik)"'
cat package.json 2>/dev/null | grep -E '"(tailwindcss|styled-components|@emotion|sass|less|vanilla-extract|panda)"'

# 2. Android / Compose
ls build.gradle.kts build.gradle settings.gradle.kts settings.gradle 2>/dev/null
grep -rE 'androidx\.compose|implementation\("androidx\.compose' build.gradle* settings.gradle* 2>/dev/null

# 3. Compose Multiplatform / KMP
grep -rE 'org\.jetbrains\.compose|kotlin\("multiplatform"\)|id\("org\.jetbrains\.kotlin\.multiplatform"\)' build.gradle* settings.gradle* 2>/dev/null

# 4. Apple / SwiftUI
ls *.xcodeproj *.xcworkspace Package.swift 2>/dev/null
grep -lE 'import SwiftUI|@main.*App' --include="*.swift" -r . 2>/dev/null | head -1

# 5. Apple platform sub-detection (iOS vs macOS)
# - Package.swift : check .platforms array
grep -E '\.iOS\(|\.macOS\(' Package.swift 2>/dev/null
# - xcodeproj : list schemes / targets (parse via grep dans pbxproj)
grep -E 'SDKROOT = (iphoneos|macosx)' *.xcodeproj/project.pbxproj 2>/dev/null

# 6. Mobile web indicators (charge mobile-principles)
grep -rE 'viewport.*width=device-width|@media.*pointer:\s*coarse|@media.*max-width' --include='*.html' --include='*.css' --include='*.scss' . 2>/dev/null | head -3
ls public/manifest.json public/sw.js 2>/dev/null

# 7. Legacy bridge indicators (mention en DISCOVER, pas auto-load)
ls -- *.xib 2>/dev/null
find . -path '*/res/layout/*.xml' 2>/dev/null | head -1
```

### Mapping détection → stack

| Détection | Stack identifié |
|---|---|
| `androidx.compose.*` | `android-compose` |
| `org.jetbrains.compose` ou `kotlin-multiplatform` + Compose | `compose-multiplatform` |
| `Package.swift` ou `*.xcodeproj` + SwiftUI imports + iOS platform | `swiftui-ios` |
| `Package.swift` ou `*.xcodeproj` + SwiftUI imports + macOS platform | `swiftui-macos` |
| `*.xcodeproj` avec iOS et macOS targets | `swiftui-multi-apple` |
| Aucun match | demander en DISCOVER (cf. orchestrator pipeline) |

### Cas multi-stack

Un projet **CMP avec target iOS+Android** est légitime. Le SCAN identifie `compose-multiplatform` ET `swiftui-ios` (pour l'interop). Les deux groupes de sub-skills sont disponibles, et l'orchestrator priorise selon la THESIS.

## 6. Stratégie de chargement (phase LOAD étendue)

Remplace la table actuelle des sub-skills par une **structure en couches** :

```
TOUJOURS :
  motion-principles

CONTEXTE (chargé selon détection) :
  mobile détecté        → + mobile-principles
  desktop détecté       → + desktop-principles
  scope = full          → + design-audit
  audit explicit        → + design-audit
  questions UI/UX       → + ui-ux-pro-max

STACK-SPECIFIC :
  web                   → (existant inchangé)
  android-compose       → compose-motion
                        + compose-graphics si scope=full OU thèse mentionne shader/expressive/canvas/graphics-layer
  compose-multiplatform → compose-motion + compose-multiplatform
                        + swiftui-motion si target iOS détecté ET demande interop SwiftUI explicite
                        + compose-graphics si scope=full ou thèse advanced
  swiftui-ios           → swiftui-motion
                        + swiftui-graphics si scope=full OU thèse mentionne Metal/liquid-glass/visual-effect
  swiftui-macos         → swiftui-motion + desktop-principles (cf. CONTEXTE)
                        + swiftui-graphics si scope=full ou thèse advanced
  swiftui-multi-apple   → swiftui-motion + mobile-principles + desktop-principles
                        + swiftui-graphics si scope=full ou thèse advanced
```

### Critère "thèse advanced"

Une thèse est dite "advanced" et déclenche le chargement de `compose-graphics` ou `swiftui-graphics` si elle contient l'un des termes suivants :
- `shader`, `Metal`, `AGSL`, `RuntimeShader`, `MSL`
- `liquid-glass`, `glassEffect`, `morphing transition`
- `M3 Expressive`, `MotionScheme`, `expressive motion`
- `colorEffect`, `distortionEffect`, `layerEffect`
- `Canvas` (avec context generative / particle / flow field)
- `holographic`, `CRT`, `displacement`, `ripple`

Sinon, l'orchestrator reste sur le sub-skill base (`compose-motion` / `swiftui-motion`).

## 7. Sub-skills nouveaux (contenu détaillé)

### 7.1 `mobile-principles` (NOUVEAU layer partagé)

**Frontmatter** :
```yaml
---
name: mobile-principles
description: "Mobile-specific UX principles - touch targets, hover-less doctrine, thumb zones, safe areas, gestures, mobile perf budgets. Cross-platform (web mobile, iOS, Android)."
---
```

**SKILL.md** (~400 lignes) :

- **Touch targets** : tableau 44pt iOS (HIG) / 48dp Android (Material) / 44px web (WCAG 2.5.5).
- **No-hover doctrine** : `:hover` ne doit jamais être l'unique trigger sur mobile. Long-press = équivalent contextuel. Detection via `(hover: hover)` en CSS, `UITraitCollection` en SwiftUI, `LocalConfiguration` en Compose.
- **Thumb zones (Hoober)** : zones easy/ok/hard, où placer les CTA primaires (bottom-half pour mobile portrait).
- **Safe areas** : `env(safe-area-inset-*)` web, `safeAreaInsets` SwiftUI, `WindowInsets` Compose. Tableau de patterns par plateforme.
- **Reduced motion unifié** : table cross-platform avec les 3 API (`prefers-reduced-motion`, `accessibilityReduceMotion`, `LocalAccessibilityManager.isReduceTransitions`).
- **Gestures de base** : swipe-back (iOS edge), pull-to-refresh, drag-to-dismiss, pinch-to-zoom. Patterns BAD/GOOD.
- **Perf budgets mobile** : cold start < 2s, frame budget 16.67ms (60fps) ou 8.33ms (120fps ProMotion), batterie/CPU/mémoire considérations, lazy loading images, `Save-Data` header.

**`references/`** :
- `gestures-deep.md` (~200 lignes) : conflits de gestures, patterns nestedScroll, simultaneous gestures, `DragGesture` SwiftUI vs `Modifier.draggable` Compose.
- `accessibility-mobile.md` (~150 lignes) : VoiceOver iOS, TalkBack Android, screen reader web, dynamic type, contrast WCAG.

**Sources** : Steven Hoober (thumb zones research), [Apple HIG iOS](https://developer.apple.com/design/human-interface-guidelines/), [Material Design Mobile](https://m3.material.io/foundations/layout/canonical-layouts/overview).

### 7.2 `desktop-principles` (NOUVEAU layer partagé)

**Frontmatter** :
```yaml
---
name: desktop-principles
description: "Desktop-specific UX principles - hover states, pointer precision, keyboard shortcuts, multi-window, focus management. Covers macOS, Windows, Linux, web desktop."
---
```

**SKILL.md** (~350 lignes) :

- **Hover states obligatoires** : à l'inverse du mobile, le hover est essentiel pour signaler l'interactivité. Tableau d'API (`onHover` SwiftUI, `Modifier.onPointerEvent` Compose Desktop, `:hover` CSS).
- **Pointer fin** : targets peuvent être 24-32px (vs 44 mobile). Mais accessibilité oblige : minimum 24px et zones de tolérance.
- **Raccourcis clavier first-class** : `⌘`/`Ctrl`+lettres canoniques (`⌘N` new, `⌘W` close window, etc.). Tableau Apple HIG / Microsoft Fluent / GNOME.
- **Multi-window** : SwiftUI `.windowResizability`, `WindowGroup` patterns, état partagé entre fenêtres. Compose Desktop `Window` et `MultipleWindowsApplication`.
- **Focus management** : `@FocusState` SwiftUI, `Modifier.focusable` Compose, `tabindex` web. Tab order et focus rings.
- **Densité d'info** : grilles plus serrées, sidebars, palettes de commande. Densité 8px vs 4px mobile.
- **Animations plus subtiles** : le user voit la même UI longtemps, donc les motions doivent être discrètes et utilitaires. Less is more.

**`references/`** :
- `keyboard-patterns.md` (~150 lignes) : raccourcis canoniques par plateforme, conflicts cross-OS, chord shortcuts.
- `multi-window.md` (~120 lignes) : state management entre fenêtres, scene phase iOS, NSWindow macOS.

**Sources** : [Apple HIG macOS](https://developer.apple.com/design/human-interface-guidelines/macos), [Microsoft Fluent Design](https://fluent2.microsoft.design/), [GNOME HIG](https://developer.gnome.org/hig/).

### 7.3 `compose-motion` (NOUVEAU, base Android)

**Frontmatter** :
```yaml
---
name: compose-motion
description: "Jetpack Compose animation foundations - animate*AsState, AnimatedVisibility, Crossfade, updateTransition, SharedTransitionLayout, gestures."
---
```

**SKILL.md** (~600 lignes) :

- Tableau d'API Compose : `animate*AsState` (Float, Color, Dp, Offset, Size...), `AnimatedVisibility`, `AnimatedContent`, `Crossfade`, `updateTransition`, `Animatable`, `rememberInfiniteTransition`.
- **Springs Compose** : `spring(Spring.StiffnessMedium, Spring.DampingRatioLowBouncy, ...)`. Tableau presets pour mood (snappy, bouncy, gentle, playful).
- **Tweens** : `tween(durationMillis, easing = FastOutSlowInEasing | LinearOutSlowInEasing | FastOutLinearInEasing)`.
- **SharedTransitionLayout** (Compose 1.7+) : `Modifier.sharedElement`, `Modifier.sharedBounds`, `SharedContentState`. Patterns hero animations.
- **Gestures** : `Modifier.draggable`, `Modifier.pointerInput`, `detectDragGestures`, `nestedScroll` patterns.
- **Patterns BAD/GOOD** : ne pas animer `width`/`height` directement (use `animateContentSize` ou `Modifier.layout`), ne pas faire de `LaunchedEffect` qui relance à chaque recomposition, ne pas oublier `key` dans les listes animées.
- Section "Decision tree" : "Quel animateur Compose pour quel cas ?".

**`references/`** :
- `shared-transitions.md` (~250 lignes) : patterns avancés `SharedContentState`, `OverlayClip`, `renderInSharedTransitionScopeOverlay`, navigation animée Compose Navigation 3.
- `gestures-compose.md` (~200 lignes) : drag, swipe-to-dismiss, pull-to-refresh, fling, momentum, conflits avec scroll.
- `recomposition-and-anim.md` (~200 lignes) : `derivedStateOf`, `key`, éviter le jank, profiler avec Layout Inspector et Macrobenchmark.

**Sources** : [aldefy/compose-skill](https://github.com/aldefy/compose-skill) (animation.md), [skydoves/Orbital](https://github.com/skydoves/Orbital), [mutualmobile/compose-animation-examples](https://github.com/mutualmobile/compose-animation-examples), [fornewid/material-motion-compose](https://github.com/fornewid/material-motion-compose), [Android docs animations](https://developer.android.com/develop/ui/compose/animation/introduction).

### 7.4 `compose-graphics` (NOUVEAU, advanced Android)

**Frontmatter** :
```yaml
---
name: compose-graphics
description: "Advanced Compose visuals - Material 3 Expressive motion physics, AGSL shaders (Android 13+), Canvas/DrawScope generative, graphicsLayer effects."
---
```

**SKILL.md** (~700 lignes) :

Trois domaines distincts dans un seul SKILL.md (parce que l'advanced se charge sur thèse "wow", c'est cohérent de tout avoir) :

#### 7.4.a M3 Expressive
- `MotionScheme.expressive()` vs `MotionScheme.standard()`, intégration via `MaterialTheme(motionScheme = ...)`.
- Spring physics : stiffness (Spring.StiffnessHigh/Medium/Low/VeryLow) + dampingRatio (DampingRatioHighBouncy/MediumBouncy/LowBouncy/NoBouncy).
- Choreography : timing groupé sur les hero moments, motion delegated to user input.
- Patterns shape morphing avec `Shape` interpolation.

#### 7.4.b AGSL shaders (Android 13+)
- `RuntimeShader` API, ShaderBrush, intégration via `Modifier.graphicsLayer` ou `Canvas`.
- Conversion GLSL → AGSL (table de différences syntaxiques).
- Fallback Android <13 : detection via `Build.VERSION.SDK_INT >= 33` et fallback statique.
- Recipes prêts à l'emploi : ripple touch, glow halo, displacement, glassmorphism, holographic gradient.

#### 7.4.c Canvas / DrawScope
- `Canvas` composable, `DrawScope`, `Path` API, `Brush` (linear/radial/sweep gradients).
- `drawIntoCanvas` pour passer au native android.graphics.Canvas si besoin.
- Generative patterns : particles avec `LaunchedEffect` + `Animatable`, flow fields, noise (Perlin/Simplex via lib KMP).

**`references/`** :
- `agsl-recipes.md` (~300 lignes) : 7 shaders prêts (ripple, glow, distortion, glassmorphism, holographic, CRT, noise overlay), avec code AGSL complet et binding Compose.
- `m3-expressive-deep.md` (~200 lignes) : motion choreography multi-éléments, hero moments, exemples Now in Android.
- `canvas-generative.md` (~250 lignes) : flow fields, L-systems, particle systems, noise.

**Sources** : [drinkthestars/shady](https://github.com/drinkthestars/shady), [Mortd3kay/liquid-glass-android](https://github.com/Mortd3kay/liquid-glass-android), [JumpingKeyCaps/DynamicVisualEffectsAGSL](https://github.com/JumpingKeyCaps/DynamicVisualEffectsAGSL), [m3-expressive blog](https://m3.material.io/blog/m3-expressive-motion-theming), [Material Motion specs](https://m3.material.io/styles/motion/overview/specs), [Android AGSL docs](https://developer.android.com/develop/ui/views/graphics/agsl/using-agsl).

### 7.5 `compose-multiplatform` (NOUVEAU)

**Frontmatter** :
```yaml
---
name: compose-multiplatform
description: "Compose Multiplatform / KMP patterns - expect/actual composables, platform-specific code, density and font handling cross-target, iOS/Android/Desktop interop."
---
```

**SKILL.md** (~500 lignes) :

- Architecture KMP : `commonMain`, `androidMain`, `iosMain`, `desktopMain`, `wasmJsMain`. Quand mettre quoi où.
- `expect`/`actual` patterns pour composables (ex : `expect fun PlatformBlur()`).
- `LocalDensity`, `LocalConfiguration`, `LocalLayoutDirection` cross-platform.
- Gestion fonts : `org.jetbrains.compose.resources` (Compose Resources), patterns par plateforme.
- Interop iOS via `UIViewControllerRepresentable` côté Swift, ou `UIKitView` côté Compose.
- Gotchas : animations qui marchent sur Android mais pas Desktop (ex : drawer state), différences de focus entre platforms, comportement de scroll natif différent.

**`references/`** :
- `cmp-interop.md` (~250 lignes) : passer du SwiftUI à du Compose et inversement, patterns de communication state.
- `cmp-platform-quirks.md` (~200 lignes) : catalogue des différences de comportement par target, troubleshooting.

**Sources** : [Meet-Miyani/compose-skill](https://github.com/Meet-Miyani/compose-skill), [JetBrains Compose Multiplatform docs](https://www.jetbrains.com/lp/compose-multiplatform/), [skydoves/Orbital](https://github.com/skydoves/Orbital) (KMP-aware).

### 7.6 `swiftui-motion` (NOUVEAU, base Apple)

**Frontmatter** :
```yaml
---
name: swiftui-motion
description: "SwiftUI animation foundations - withAnimation, transitions, matchedGeometryEffect, PhaseAnimator, KeyframeAnimator, springs, gestures."
---
```

**SKILL.md** (~600 lignes) :

- `withAnimation` API et types de springs : `.spring(response:dampingFraction:blendDuration:)` vs `.snappy`, `.bouncy`, `.smooth`.
- Transitions implicites/explicites : `.transition(.scale.combined(with: .opacity))`, `AsymmetricTransition`, `.matchedGeometryEffect(id:in:)`.
- `PhaseAnimator` (iOS 17+) : multi-phase choreography, exemples loading states, success animations.
- `KeyframeAnimator` (iOS 17+) : keyframes time-based, `LinearKeyframe`, `SpringKeyframe`, `CubicKeyframe`.
- `@Animatable` macro (iOS 17+) : custom animatable properties.
- Gestures : `DragGesture`, `LongPressGesture`, `MagnifyGesture`, `RotateGesture`, simultaneous/sequenced patterns.
- Patterns BAD/GOOD : ne pas animer dans `body` directly (use `withAnimation`), ne pas oublier `id:` sur `matchedGeometryEffect`, attention aux `.animation()` deprecated.

**`references/`** :
- `springs-cheatsheet.md` (~150 lignes) : presets `.snappy`, `.bouncy`, `.smooth`, custom spring tuning, response/dampingFraction par mood.
- `phase-keyframe-deep.md` (~200 lignes) : multi-phase complex sequences, KeyframeTrack, custom Animatable types.
- `gestures-swiftui.md` (~200 lignes) : combinaisons, conflits, GestureMask, simultaneous gestures.

**Sources** : [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill), [GetStream/swiftui-spring-animations](https://github.com/GetStream/swiftui-spring-animations), [amosgyamfi/open-swiftui-animations](https://github.com/amosgyamfi/open-swiftui-animations), [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill), [dpearson2699/swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills) (swiftui-animation, swiftui-gestures), [Shubham0812/SwiftUI-Animations](https://github.com/Shubham0812/SwiftUI-Animations).

### 7.7 `swiftui-graphics` (NOUVEAU, advanced Apple)

**Frontmatter** :
```yaml
---
name: swiftui-graphics
description: "Advanced SwiftUI visuals - Metal shaders (.colorEffect, .layerEffect, .distortionEffect), .visualEffect, Liquid Glass (iOS 26), Canvas, holographic and CRT effects."
---
```

**SKILL.md** (~700 lignes) :

Trois domaines :

#### 7.7.a Metal shaders SwiftUI
- `.colorEffect`, `.distortionEffect`, `.layerEffect`. ShaderLibrary, fonction Metal Shading Language (MSL).
- Patterns : passing parameters via `.shader(...)`, time-based shaders avec `TimelineView`.
- Recipes : ripple, holographic, CRT, glow, distortion, particle emitter, noise.
- Differences with AGSL (pour devs CMP qui veulent traduire).

#### 7.7.b Visual effects
- `.visualEffect { content, geometry in ... }` (iOS 17+) : modifiers context-aware avec geometry.
- `Canvas` SwiftUI : drawing performant avec `GraphicsContext`, fill/stroke/path.
- `GeometryReader` patterns avancés pour effets parallax, scroll-driven animations.

#### 7.7.c Liquid Glass (iOS 26+)
- `.glassEffect()`, `GlassEffectContainer`, morphing transitions entre éléments avec glass.
- Fallback iOS <26 : check `if #available(iOS 26.0, *)` et `.background(.ultraThinMaterial)` sinon.
- Combos avec `.matchedGeometryEffect` pour transitions fluides.

**`references/`** :
- `metal-recipes.md` (~350 lignes) : 7 shaders Inferno-style avec code MSL complet (ripple, holographic, CRT, glow, particles, distortion, noise).
- `liquid-glass-deep.md` (~200 lignes) : combos morphing, ce qui passe pas avant iOS 26, alternatives avec `.ultraThinMaterial`.
- `canvas-swiftui.md` (~200 lignes) : drawing performant, GraphicsContext, ce qui drift quand on scale.

**Sources** : [twostraws/Inferno](https://github.com/twostraws/Inferno) (Metal shaders SwiftUI référence absolue), [Treata11/iShader](https://github.com/Treata11/iShader), [jamesrochabrun/ShaderKit](https://github.com/jamesrochabrun/ShaderKit), [raphaelsalaja/metallurgy](https://github.com/raphaelsalaja/metallurgy), [eleev/swiftui-new-metal-shaders](https://github.com/eleev/swiftui-new-metal-shaders), [dpearson2699/swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills) (swiftui-liquid-glass), [Apple Metal docs](https://developer.apple.com/documentation/metal).

## 8. Modifications de l'existant

### 8.1 `motion-principles` - neutralisation web-bias

**Sections concrètes à modifier** :

- **Easing Cheat Sheet (ligne 28-)** : conserver `cubic-bezier(0.2, 0, 0, 1)` mais ajouter une colonne pour les équivalents Compose et SwiftUI. Tableau étendu avec springs natifs (`spring(stiffness=Spring.StiffnessMedium, dampingRatio=0.8)` Compose, `.spring(response: 0.4, dampingFraction: 0.8)` SwiftUI).
- **prefers-reduced-motion (ligne 45-)** : la section actuelle est exclusivement CSS/JS. Ajouter une table cross-platform :

  | Plateforme | API |
  |---|---|
  | Web CSS | `@media (prefers-reduced-motion: reduce)` |
  | Web JS | `window.matchMedia('(prefers-reduced-motion: reduce)')` |
  | SwiftUI | `@Environment(\.accessibilityReduceMotion) var reduceMotion` |
  | UIKit | `UIAccessibility.isReduceMotionEnabled` + `UIAccessibility.reduceMotionStatusDidChangeNotification` |
  | Compose | `LocalAccessibilityManager.current` (via custom check) ou `Settings.System.TRANSITION_ANIMATION_SCALE` |

  Donner un exemple par plateforme (3 blocs de code minimum).

- **Examples GSAP (lignes 137-154)** : conserver les exemples GSAP comme référence mais ajouter 2 exemples cross-platform équivalents :
  - Compose : `animateFloatAsState(durationMillis = if (reduceMotion) 0 else 600)`
  - SwiftUI : `withAnimation(reduceMotion ? .none : .spring(...)) { ... }`

- **Follow-up table (lignes 175-180)** : étendre avec :
  ```
  | Compose Android | `../compose-motion/SKILL.md` |
  | Compose Multiplatform | `../compose-multiplatform/SKILL.md` |
  | SwiftUI iOS/macOS | `../swiftui-motion/SKILL.md` |
  | Mobile context | `../mobile-principles/SKILL.md` |
  | Desktop context | `../desktop-principles/SKILL.md` |
  ```

### 8.2 `design-audit` - checklist par stack

**Sections concrètes à modifier** :

- **Section "prefers-reduced-motion" (ligne 61-)** : étendre le grep pour couvrir les fichiers natifs :
  ```bash
  grep -rn 'prefers-reduced-motion' --include='*.css' --include='*.scss' --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' src/
  grep -rn 'accessibilityReduceMotion\|isReduceMotionEnabled' --include='*.swift' --include='*.kt' .
  ```
  Ajouter une note : un projet Compose/SwiftUI avec animations doit avoir au moins une référence à l'API correspondante.

- **Section "Bundle size" (ligne 127)** : la mention "framer-motion ~30KB, GSAP ~25KB" est web-only. Ajouter section parallèle :
  > Sur mobile natif, la taille de l'APK / IPA est sensible. Une lib d'animation tierce (ex : Lottie, Rive) ajoute typiquement 500KB-2MB. Si tu n'as que des fades et slides, les API natives Compose/SwiftUI suffisent.

- **Section "Easing inventory" (ligne 152)** : étendre le grep :
  ```bash
  # Existing CSS/TSX
  grep -rnoE 'ease[A-Za-z]*|cubic-bezier\([^)]+\)|spring\([^)]*\)' --include='*.tsx' --include='*.jsx' --include='*.ts' --include='*.css' src/

  # Compose
  grep -rnoE 'spring\(|tween\(|FastOutSlowInEasing|LinearOutSlowInEasing' --include='*.kt' .

  # SwiftUI
  grep -rnoE '\.spring\(|\.snappy|\.bouncy|\.smooth|\.linear\(|\.easeIn|\.easeOut' --include='*.swift' .
  ```

- **Section "Final checklist" (ligne 175-)** : étendre avec items par stack (Compose recomposition counts, SwiftUI Hitches Instrument).

- **Nouvelles sections par stack** (ajout en fin de fichier) :
  - **Audit Compose** : Layout Inspector, Macrobenchmark frame timing, recomposition counts, baseline profiles.
  - **Audit SwiftUI** : Instruments Time Profiler, Hitches Instrument, GPU Frame Capture pour Metal shaders, environment overrides pour testing.

### 8.3 Orchestrators (`creative-excellence`, `design-excellence`)

**Sections à modifier dans les deux SKILL.md** :

- **SCAN** : remplacer le bloc bash actuel par la version étendue (cf. section 5).
- **LOAD** : remplacer la table actuelle par la structure en couches (cf. section 6).
- **THESIS examples** : ajouter 2-3 exemples cross-platform à côté des web actuels :
  - *"Cette transition entre les onglets utilisera SwiftUI matchedGeometryEffect avec une spring (response: 0.5, damping: 0.8) pour un effet fluide et tactile."*
  - *"Ce header sera animé avec un AGSL shader Compose qui réagit au scrollOffset pour un effet de liquid-glass dynamique."*
  - *"Ce dashboard macOS aura des hover states subtiles (opacity 0.85, scale 0.98, 120ms) et des raccourcis clavier (⌘1-9 pour naviguer entre vues)."*
- **DISCOVER** : ajouter une question conditionnelle si du legacy mixé est détecté (cf. section 9).
- **AUDIT** : étendre la checklist avec les items par stack (cf. modifications de `design-audit`).
- **Iron Rules 7-8** : généraliser :
  - Avant : "React with no detected animation lib → prefer native CSS or propose framer-motion"
  - Après : **"Stack avec aucune lib d'animation détectée → prefer les API natives de la stack avant de proposer une dépendance"**
  - Avant : "GSAP detected in the project → use it"
  - Après : **"Une lib d'animation tierce détectée → respecte le choix du dev, pas de remplacement non sollicité"**

### 8.4 `design-excellence` - génération MASTER.md stack-aware

Le `design-excellence` SKILL.md actuel génère un MASTER.md très orienté CSS/Tailwind (palettes en hex codes, motion en `cubic-bezier`, spacing en `rem`). Il faut **adapter la phase "Generate design system"** :

- Si stack = **web** → MASTER.md génère du CSS/Tailwind (existant, inchangé).
- Si stack = **android-compose** → MASTER.md génère du Kotlin :
  - `MaterialTheme` avec `ColorScheme` light/dark
  - `Typography` avec `TextStyle` presets
  - `Shapes` avec `RoundedCornerShape` presets
  - `MotionScheme` (M3 Expressive) avec spring presets
- Si stack = **swiftui** → MASTER.md génère du Swift :
  - `Color` extensions avec assets catalog references
  - `Font` extensions avec `.system()` ou custom fonts
  - `Animation` presets (`.spring(...)`, `.snappy`, etc.)
  - `View` modifiers réutilisables
- Si stack = **compose-multiplatform** → MASTER.md génère du Kotlin avec patterns expect/actual pour les fonts et color tokens.

Le MASTER.md reste **un seul fichier** (le système design source-of-truth) mais les blocs de code générés sont dans le langage de la stack détectée.

## 9. Détection legacy et bridge minimal

Si la phase SCAN détecte des indicateurs legacy **dans un projet par ailleurs moderne** :

| Indicateur | Stack legacy détectée |
|---|---|
| `*.xib` ou `*.storyboard` | UIKit (iOS) |
| `**/res/layout/*.xml` | Android Views |
| `setContentView(R.layout...)` dans Activity | Android Views |
| `UIViewController` extensions sans SwiftUI | UIKit (iOS) |

L'orchestrator **n'auto-charge pas** de sub-skill legacy (il n'en existe pas). À la place, il pose **une question** en phase DISCOVER :

> "Je vois que ton projet a [du XML / des XIB] en plus du moderne. Pour cette tâche, je reste sur du pur [Compose/SwiftUI], ou tu veux que je m'intègre dans un écran legacy ?"

**Si l'utilisateur dit "intègre dans le legacy"** : l'orchestrator écrit le pont (`AndroidView` Compose, `UIViewControllerRepresentable` SwiftUI) qui expose le moderne *dans* l'ancien. Il ne génère **jamais** de code legacy lui-même (pas de XML layout, pas de XIB, pas de UIKit ViewController).

**Si l'utilisateur dit "pur moderne"** : comportement par défaut, ignore le legacy.

## 10. Packaging et installation

### 10.1 `package-for-claude-ai.sh` - automatique

Le script actuel itère sur `_creative/` et génère 1 ZIP par sub-skill. Aucune modif nécessaire : les nouveaux sub-skills sont packagés automatiquement dès qu'ils existent dans `_creative/`. Le `creative-excellence-all.zip` (all-in-one) inclura les 7 nouveaux sub-skills.

**Total à la release v2.0.0** : 17 ZIPs individuels + 1 all-in-one.

### 10.2 Workflow d'install - Claude Code CLI

Inchangé :
```bash
/plugin marketplace add git@github.com:AThevon/creative-excellence.git
/plugin install creative-excellence
```

Tous les sub-skills sont sur disque, l'orchestrator charge en context uniquement ce que SCAN détecte. Pas de pollution cross-stack.

### 10.3 Workflow d'install - claude.ai (matrice de recommandation)

Le README ajoute une matrice :

| Stack du dev | ZIPs à uploader (en plus des 2 orchestrators) |
|---|---|
| **Web only** | motion-principles, gsap, framer-motion, css-native, threejs-r3f, canvas-generative, mobile-principles, desktop-principles, design-audit, ui-ux-pro-max |
| **Android Compose only** | motion-principles, mobile-principles, compose-motion, compose-graphics, design-audit, ui-ux-pro-max |
| **iOS SwiftUI only** | motion-principles, mobile-principles, swiftui-motion, swiftui-graphics, design-audit, ui-ux-pro-max |
| **macOS SwiftUI only** | motion-principles, desktop-principles, swiftui-motion, swiftui-graphics, design-audit, ui-ux-pro-max |
| **Multi-target SwiftUI (iOS+macOS)** | motion-principles, mobile-principles, desktop-principles, swiftui-motion, swiftui-graphics, design-audit, ui-ux-pro-max |
| **CMP** | motion-principles, mobile-principles, compose-motion, compose-graphics, compose-multiplatform, swiftui-motion (si target iOS), design-audit, ui-ux-pro-max |
| **Tout (full stack)** | l'all-in-one, ou tous les ZIPs |

**Règle simple à retenir** : "uploade toujours les 2 orchestrators + `motion-principles` + `design-audit` + `ui-ux-pro-max`. Pour le reste, prends ce qui matche ta stack."

### 10.4 CI / GitHub Actions

Modif probable : aucune. Le workflow actuel devrait régénérer le all-in-one à chaque tag automatiquement (à vérifier dans `.github/workflows/`).

### 10.5 Versionnage

`v2.0.0` (bump major) :
- Architecture en couches (mobile-principles, desktop-principles) = breaking change conceptuel.
- 7 nouveaux sub-skills + 3 modifs existants = features majeures.
- Iron Rules 7-8 réécrites = breaking change comportemental.

## 11. Plan d'implémentation par phases

### Phase 1 - Fondations cross-platform (1 PR, ~1 jour)

- Modifs `motion-principles` (neutralisation web-bias, table cross-platform, follow-up étendu).
- Création `mobile-principles` (SKILL.md + 2 références).
- Création `desktop-principles` (SKILL.md + 2 références).
- Modifs `design-audit` (sections par stack, grep étendus).
- Modifs des 2 orchestrators (SCAN étendu, LOAD avec couches, Iron Rules réécrites, exemples thèses cross-platform, DISCOVER question legacy, génération MASTER.md stack-aware pour design-excellence).

**Done quand** :
- Un projet web continue de fonctionner exactement comme avant (zéro régression dans les sub-skills web).
- Un projet Compose ou SwiftUI test charge `motion-principles + mobile-principles` (ou `desktop-principles`) + `design-audit` correctement à la phase LOAD.
- Le MASTER.md généré pour un projet Compose contient bien du Kotlin (ColorScheme, Typography, etc.) et pas du CSS.

### Phase 2 - Stack iOS / SwiftUI (1 PR, ~2 jours)

- Création `swiftui-motion` (SKILL.md + 3 références).
- Création `swiftui-graphics` (SKILL.md + 3 références).

**Done quand** :
- Sur un projet SwiftUI, `/creative-excellence` propose une thèse pertinente avec la bonne API (springs, PhaseAnimator, KeyframeAnimator).
- Sur un projet SwiftUI advanced, `/creative-excellence` charge `swiftui-graphics` et propose des Metal shaders ou Liquid Glass selon la thèse.
- `/design-excellence` peut faire un audit avec checklist Instruments Time Profiler / Hitches.
- Test manuel sur un vrai projet SwiftUI iOS (preview iPhone Simulator).

### Phase 3 - Stack Android / Compose (1 PR, ~2 jours)

- Création `compose-motion` (SKILL.md + 3 références).
- Création `compose-graphics` (SKILL.md + 3 références).

**Done quand** :
- Sur un projet Compose, `/creative-excellence` propose une thèse adaptée (springs Compose, AnimatedVisibility, SharedTransitionLayout).
- Sur un projet Compose advanced, charge `compose-graphics` et propose AGSL shaders ou M3 Expressive.
- `/design-excellence` audit avec Layout Inspector / Macrobenchmark / recomposition counts.
- Test manuel sur un vrai projet Android (preview Android Emulator).

### Phase 4 - Compose Multiplatform (1 PR, ~1 jour)

- Création `compose-multiplatform` (SKILL.md + 2 références).
- Test sur un vrai projet CMP (par exemple un simple app KMP avec target Android+iOS).

**Done quand** :
- Un projet CMP charge la stack croisée (`compose-motion + compose-multiplatform`).
- L'orchestrator peut proposer une interop iOS quand demandé.
- Patterns expect/actual sont bien documentés.

### Phase 5 - Polish et release (1 PR, ~1 jour)

- README refonte complète :
  - Mention "now covers Web, Android (Compose / CMP), iOS, macOS"
  - Tableau des sub-skills étendu (les 7 nouveaux)
  - Matrice install par stack (cf. 10.3)
  - Diagramme architecture mis à jour (cf. section 4)
  - **Credits étendus** avec toutes les sources citées dans cette spec
- Test du `package-for-claude-ai.sh` (les 17 ZIPs sortent proprement, le `all.zip` contient tout).
- Test du workflow GitHub Actions sur un tag de pré-release.
- CHANGELOG v2.0.0 (résumé des breaking changes et nouvelles features).
- Bump version dans `plugin.json` + `marketplace.json`.
- Tag `v2.0.0` et release GitHub avec les 17 ZIPs en assets.

**Done quand** :
- La release v2.0.0 est publiée sur GitHub.
- L'install marche en CLI (`/plugin install creative-excellence` puis test sur un projet de chaque stack).
- L'install marche sur claude.ai (test upload des ZIPs critiques pour 1 stack mobile).

## 12. Critères "Phase faite" transverses

Pour chaque phase, ces critères s'appliquent à chaque sub-skill créé/modifié :

- [ ] SKILL.md a YAML frontmatter (`name`, `description`) - required pour claude.ai.
- [ ] Chaque référence est dans `references/` du sub-skill (pas inlinée dans `SKILL.md`).
- [ ] Sources citées en bas du SKILL.md (cohérence avec les sub-skills web actuels).
- [ ] Au moins une section "BAD/GOOD" ou "Anti-patterns" (philosophie anti-AI-slop).
- [ ] Au moins un exemple de thèse cross-platform dans le SKILL.md de l'orchestrator.
- [ ] Le sub-skill teste loadable sur claude.ai (upload du ZIP, frontmatter valide, fichier visible dans la liste des skills disponibles).
- [ ] Aucune référence purement web-only restée dans les sub-skills partagés (`motion-principles`, `design-audit`).

## 13. Hors scope explicitement

- ❌ Pas de sub-skill UIKit / Core Animation (legacy iOS).
- ❌ Pas de sub-skill Android Views / XML / `Animator`/`Transition` (legacy Android).
- ❌ Pas de sub-skill watchOS / tvOS / visionOS / Wear OS (niche, phase future si demande).
- ❌ Pas de sub-skill React Native / Flutter / Ionic (cross-platform non-natifs, hors mission).
- ❌ Pas de migration auto / refacto cross-stack (les sub-skills enseignent et implémentent, ils ne migrent pas).
- ❌ Pas de modification de `ui-ux-pro-max` (déjà cross-platform avec stacks `swiftui` et `jetpack-compose` listés).

## 14. Sources externes citées (pour le README Credits)

### Sub-skills publics qui ont nourri la conception

- [aldefy/compose-skill](https://github.com/aldefy/compose-skill) - granular Compose docs avec androidx source receipts.
- [Meet-Miyani/compose-skill](https://github.com/Meet-Miyani/compose-skill) - Compose / CMP / KMP comprehensive.
- [new-silvermoon/awesome-android-agent-skills](https://github.com/new-silvermoon/awesome-android-agent-skills) - Android architecture skills.
- [Drjacky/claude-android-ninja](https://github.com/Drjacky/claude-android-ninja) - modular architecture, Navigation3.
- [dpconde/claude-android-skill](https://github.com/dpconde/claude-android-skill) - NowInAndroid-aligned best practices.
- [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) - SwiftUI best practices reference.
- [twostraws/swift-agent-skills](https://github.com/twostraws/swift-agent-skills) - curated directory of Swift agent skills.
- [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) - SwiftUI animations, transitions, PhaseAnimator.
- [dpearson2699/swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills) - 83 Swift skills incluant swiftui-animation, gestures, liquid-glass.
- [rshankras/claude-code-apple-skills](https://github.com/rshankras/claude-code-apple-skills) - Apple platform skills.
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) - 1000+ agent skills curated.

### Libraries open-source d'inspiration technique

#### Android / Compose
- [fornewid/material-motion-compose](https://github.com/fornewid/material-motion-compose) - Material Motion patterns Compose + CMP.
- [skydoves/Orbital](https://github.com/skydoves/Orbital) - shared element transitions Compose multiplatform.
- [mutualmobile/compose-animation-examples](https://github.com/mutualmobile/compose-animation-examples) - collection d'exemples d'animation.
- [drinkthestars/shady](https://github.com/drinkthestars/shady) - AGSL shaders rendered in Compose.
- [JumpingKeyCaps/DynamicVisualEffectsAGSL](https://github.com/JumpingKeyCaps/DynamicVisualEffectsAGSL) - AGSL playground avec touch et sensors.
- [Mortd3kay/liquid-glass-android](https://github.com/Mortd3kay/liquid-glass-android) - glassmorphism AGSL Compose.
- [jetpack-compose/jetpack-compose-awesome](https://github.com/jetpack-compose/jetpack-compose-awesome) - curated list Compose libs.

#### Apple / SwiftUI
- [twostraws/Inferno](https://github.com/twostraws/Inferno) - Metal shaders SwiftUI (référence absolue).
- [Treata11/iShader](https://github.com/Treata11/iShader) - Metal Fragment Shaders pour SwiftUI.
- [jamesrochabrun/ShaderKit](https://github.com/jamesrochabrun/ShaderKit) - composable Metal shaders + holographic UI.
- [raphaelsalaja/metallurgy](https://github.com/raphaelsalaja/metallurgy) - SwiftUI Metal Shaders library.
- [eleev/swiftui-new-metal-shaders](https://github.com/eleev/swiftui-new-metal-shaders) - Metal Shader Collection + scroll layouts.
- [amosgyamfi/open-swiftui-animations](https://github.com/amosgyamfi/open-swiftui-animations) - collection SwiftUI animations open source.
- [GetStream/swiftui-spring-animations](https://github.com/GetStream/swiftui-spring-animations) - guide complet SwiftUI Spring.
- [Shubham0812/SwiftUI-Animations](https://github.com/Shubham0812/SwiftUI-Animations) - 20+ custom SwiftUI animations + Metal.
- [b3ll/Motion](https://github.com/b3ll/Motion) - animation engine for gesture-driven UIs.
- [Toni77777/awesome-swiftui-libraries](https://github.com/Toni77777/awesome-swiftui-libraries) - curated SwiftUI libs.

### Documentation officielle référencée

- [Material Design 3 - Motion](https://m3.material.io/styles/motion/overview/specs)
- [Material 3 Expressive Motion blog](https://m3.material.io/blog/m3-expressive-motion-theming)
- [Android AGSL docs](https://developer.android.com/develop/ui/views/graphics/agsl/using-agsl)
- [Apple HIG iOS](https://developer.apple.com/design/human-interface-guidelines/)
- [Apple HIG macOS](https://developer.apple.com/design/human-interface-guidelines/macos)
- [JetBrains Compose Multiplatform](https://www.jetbrains.com/lp/compose-multiplatform/)
- [Apple Metal Shading Language Specification](https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf)

### Crédits déjà en place (existants, à conserver)

- [mxyhi/ok-skills](https://github.com/mxyhi/ok-skills)
- [freshtechbro/claudedesignskills](https://github.com/freshtechbro/claudedesignskills)
- [kylezantos/design-motion-principles](https://github.com/kylezantos/design-motion-principles)
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
