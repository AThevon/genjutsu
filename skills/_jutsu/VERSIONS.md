# VERSIONS

What every technical claim in `_jutsu/` was verified against, and when.

**Why this file exists.** v3.1.0 corrected a batch of stale API references and, in the
same pass, deleted the "April 2026 baseline" labels while keeping the version numbers.
That turned dated claims into evergreen-looking ones: nothing on the page said how old it
was, so nothing invited a re-check. A skill that tells an agent "Firefox 128+ supports
scroll-driven animations" with no date attached is not merely stale, it is confident.

**How to use it.** Before trusting a version-sensitive line in a sub-skill, find its row
here. If the date is old and the subject moves fast (browsers ship every two weeks now,
androidx every month), re-verify before acting rather than after.

**How to update it.** When you correct a file, update its row and the date. When you add
a subject, add a row. `scripts/check-denylist.sh` holds the other half of this contract:
the exact strings that were wrong once and must not come back.

Rows are verified against primary sources - MDN browser-compat-data, caniuse,
`api/current.txt` in androidx-main, Apple's DocC JSON, the npm registry - never against
recollection.

## Web - CSS platform features

| Subject | Verified against | Date | Notes |
|---|---|---|---|
| Scroll-driven animations (animation-timeline, scroll(), view(), animation-range, scroll-timeline, view-timeline) | Chrome/Edge 115+, Safari 26+, Firefox: not shipped (Nightly only, layout.css.scroll-driven-animations.enabled, Nightly-default since 136) | 2026-09-08 | Baseline: Limited. ~84% global. Interop 2026 focus area. animation-range-start/end and timeline-scope unimplemented in Firefox even in Nightly (bug 1676779). Verified via MDN BCD + MDN Experimental features + WebKit Safari 26.0 release post. |
| View Transitions — same-document (document.startViewTransition, view-transition-name, view-transition-class) | Chrome/Edge 111+ (view-transition-class 125+, match-element 137+), Firefox 144+, Safari 18+ (class 18.2+, match-element 18.4+) | 2026-09-08 | Baseline Newly available since 2025-10-14. ~90% global. No `auto` value exists — the auto-naming keyword is `match-element`. |
| View Transitions — cross-document (@view-transition) | Chrome/Edge 126+, Safari 18.2+, Firefox: not shipped (Level 1 only) | 2026-09-08 | Baseline Limited. ~85% global. Interop 2026 focus area (carryover from 2025). |
| @starting-style and transition-behavior: allow-discrete | @starting-style: Chrome/Edge 117+, Firefox 129+, Safari 17.5+. transition-behavior: Chrome/Edge 117+, Firefox 129+, Safari 17.4+ | 2026-09-08 | Baseline Newly available since 2024-08-06, ~90% global. Transitioning `display` / `content-visibility` with allow-discrete is Chrome 117+ / Safari 18+ only — not implemented in Firefox. |
| CSS anchor positioning (anchor-name, position-anchor, position-area, @position-try, position-try-fallbacks, position-visibility) | Chrome/Edge 125+ (position-area 129+, position-try-fallbacks 128+), Firefox 147+ (2026-01-13), Safari 26+ | 2026-09-08 | web-features still rates the feature group Limited (position-anchor: normal only in Chrome 151 / Firefox 151 / Safari 27; position-visibility: anchor-visible Safari 27 only). ~84% global. Interop 2026 focus area. inset-area removed in Chrome 131; position-try-options renamed in Chrome 128. |
| Container queries — size, units, style, scroll-state | Size + units: Chrome/Edge 105+, Firefox 110+, Safari 16+. Style (custom properties): Chrome/Edge 111+, Firefox 151+, Safari 18+. Scroll-state: Chrome/Edge 133+ only (`scrolled` 144+) | 2026-09-08 | Size ~94%. Style queries Baseline Newly available since 2026-05-19, ~90%; standard-property style() not shipped anywhere. Scroll-state Baseline Limited, ~69%. Style queries are an Interop 2026 focus area. |
| sibling-index() / sibling-count() | Chrome/Edge 138+, Safari 26.2+, Firefox 154+ | 2026-09-08 | Baseline Newly available since 2026-08-18, ~80% global. Removes the main reason to reach for JS to stagger a dynamic list. |
| interpolate-size / calc-size() | Chrome/Edge 129+ only; Firefox and Safari not shipped | 2026-09-08 | Baseline Limited, still flagged experimental in BCD. ~70% global. Chromium-only — enhancement layer over grid-template-rows 0fr/1fr. |
| @scope | Chrome/Edge 118+, Firefox 146+, Safari 17.4+ (spec-complete at Safari 26.4) | 2026-09-08 | Baseline Newly available since 2026-03-24, ~90% global. Not currently mentioned anywhere in the skill — no correction needed, listed for completeness. |
| Reference stable browser versions | Chrome 153 (2026-09-08, first two-week-cadence release), Edge 151, Firefox 155 (2026-09-01), Safari 26.6.1 (2026-08-18); Safari 27 in beta | 2026-09-08 | Both Chrome and Firefox moved to two-week release cycles in September 2026, so version numbers now drift roughly twice as fast as this file assumes. |

## Web - animation and 3D libraries

| Subject | Verified against | Date | Notes |
|---|---|---|---|
| motion (formerly framer-motion) — React | 13.2.0 | 2026-09-08 | npm `motion` and `framer-motion` both publish 13.2.0; `motion` depends on `framer-motion` and `motion/react` re-exports it. Peers react/react-dom ^18 \|\| ^19. v13.0.0 (2026-08-05) removed the optional @emotion/is-prop-valid dep. staggerChildren/staggerDirection deprecated in 12.22.0 (2025-07-01) in favour of `delayChildren: stagger()`. |
| GSAP | 3.15.0 | 2026-09-08 | Released 2026-04-13. Free for all uses (GreenSock Standard 'no charge' license) since 3.13 (May 2025, Webflow); every former Club plugin ships in the public npm tarball. 3.15 added `easeReverse` and deprecated `yoyoEase`. `slow`/`rough`/`expoScale` remain outside core (gsap/EasePack); CustomEase/CustomBounce/CustomWiggle are separate files. ScrollTrigger.matchMedia still deprecated-not-removed. |
| @gsap/react (useGSAP) | 2.1.2 | 2026-09-08 | Peers: gsap ^3.12.5, react >=17. |
| greensock/gsap-skills (official GSAP agent skills) | main @ 2026-07-29 | 2026-09-08 | MIT, GreenSock-owned, 8 skills (core, timeline, scrolltrigger, plugins, utils, react, performance, frameworks). ~15k stars. |
| three.js | 0.185.1 (r185) | 2026-09-08 | 0.185.1 published 2026-07-01; src/constants.js REVISION = '185'. WebGPURenderer + TSL are shipped and unflagged, self-falling back to WebGL 2, but documented as 'the new alternative of WebGLRenderer', not the default. r182 deprecated PCFSoftShadowMap for WebGLRenderer; r183 deprecated Clock in favour of Timer. |
| @react-three/fiber | 9.7.0 | 2026-09-08 | Peers: react and react-dom `>=19 <19.3`, three >=0.156. React 19 only. Global JSX namespace no longer augmented — use `ThreeElements` / `ThreeElement` from @react-three/fiber. React latest stable is 19.2.8, so the <19.3 ceiling is live. |
| @react-three/drei | 10.7.8 | 2026-09-08 | Peers: react ^19, react-dom ^19, @react-three/fiber ^9.0.0, three >=0.159. Environment presets unchanged (10 presets). AdaptiveDpr, AdaptiveEvents, Bvh, PerformanceMonitor, MeshTransmissionMaterial, PresentationControls all still exported. |
| @react-three/postprocessing | 3.1.1 | 2026-09-08 | Peers: react ^19, @react-three/fiber >=9.7.0, postprocessing ^6.36.0. Bloom/ChromaticAberration/EffectComposer + BlendFunction from 'postprocessing' all still correct as written in the skill. |
| @react-three/offscreen | 0.0.8 | 2026-09-08 | Separate, still 0.0.x/experimental. This — not the Canvas `eventSource` prop — is what moves R3F rendering to a worker. |
| CSS linear() easing function | Baseline widely available since Dec 2023 | 2026-09-08 | MDN: safe to use as the easing-guide.md recipe presents it. |

## Android - Jetpack Compose

| Subject | Verified against | Date | Notes |
|---|---|---|---|
| androidx.compose.animation:animation-core (Spring constants) | 1.12.0 stable / androidx-main api/current.txt | 2026-09-08 | StiffnessVeryLow 50f, StiffnessLow 200f, StiffnessMediumLow 400f, StiffnessMedium 1500f, StiffnessHigh 10000f; DampingRatio HighBouncy 0.2f / MediumBouncy 0.5f / LowBouncy 0.75f / NoBouncy 1.0f; DefaultDisplacementThreshold 0.01f. |
| androidx.compose.animation:animation (SharedTransitionLayout / sharedElement / sharedBounds) | 1.12.0 (stable, released 2026-08-12) | 2026-09-08 | Param is `sharedContentState` (renamed from `state` in 1.8.0-alpha06); `PlaceholderSize` (renamed from `PlaceHolderSize` in 1.10.0-alpha04); `ResizeMode.scaleToBounds(...)` (lower-cased in 1.10.0-alpha01) / `ResizeMode.RemeasureToBounds`. |
| androidx.compose.foundation:foundation (AnchoredDraggable, animateItem) | 1.12.0 (stable, released 2026-08-12) | 2026-09-08 | AnchoredDraggableState's threshold/spec factory is deprecated; use AnchoredDraggableState(initialValue, anchors) + AnchoredDraggableDefaults.flingBehavior(...). `velocityThreshold` removed. `Modifier.animateItem(fadeInSpec, placementSpec, fadeOutSpec)` current. |
| androidx.compose.material3:material3 - MotionScheme / MaterialExpressiveTheme | 1.4.0 (stable, released 2026-08-26) | 2026-09-08 | Stable and non-experimental in 1.4.0. Six specs, all springs. Standard spatial 0.9/1400, 0.9/700, 0.9/300; expressive spatial 0.6/800, 0.8/380, 0.8/200; effects (both) 1.0/3800, 1.0/1600, 1.0/800. |
| androidx.compose.material3:material3 - MaterialShapes, Morph.toPath, RoundedPolygon.toShape | 1.5.0-alpha27 (released 2026-08-26); ABSENT from stable 1.4.0 | 2026-09-08 | Still @ExperimentalMaterial3ExpressiveApi (promotion to stable was reverted in 1.5.0-alpha19). material3's Morph.toPath returns androidx.compose.ui.graphics.Path. All MaterialShapes are .normalized() to a 0..1 box. |
| androidx.graphics:graphics-shapes | 1.1.0 (stable) | 2026-09-08 | Morph.toPath(progress, path) and RoundedPolygon.toPath(path) live in Shapes_androidKt and return android.graphics.Path. Morph also exposes asCubics, forEachCubic, calculateBounds, calculateMaxBounds. |
| android.graphics.RuntimeShader / RenderEffect.createRuntimeShaderEffect (AGSL) | Android API level 33 (Android 13) | 2026-09-08 | Both added in API 33; the skill's Build.VERSION_CODES.TIRAMISU gate is correct as written. |
| androidx.navigation:navigation-compose | 2.10.0 (stable) | 2026-09-08 | composable<Route> content lambda receiver is AnimatedContentScope. No LocalNavAnimatedVisibilityScope exists in this artifact. |
| androidx.navigation3 (navigation3-runtime / navigation3-ui) | 1.1.7 stable (2026-08-26); 1.0.0 shipped 2025-11-19; 1.2.0-beta01 in flight | 2026-09-08 | NavDisplay + rememberNavBackStack + entryProvider. Shared elements via NavDisplay's sharedTransitionScope parameter and androidx.navigation3.ui.LocalNavAnimatedContentScope. |
| Recomposition tooling (Modifier.recomposeHighlighter) | Not an androidx API at any version; android/snippets sample only | 2026-09-08 | Current shipped path: Layout Inspector 'Show Recomposition Counts' (View Options menu, Component Tree) + recomposition highlighting overlay; API 29+ and Compose 1.2+. Then composition tracing and Compose compiler reports. |

## Apple, Compose Multiplatform and cross-platform UX

| Subject | Verified against | Date | Notes |
|---|---|---|---|
| SwiftUI (Apple platforms) | iOS 26 / macOS 26 shipping; iOS 27 / macOS 27 SDK in beta (Xcode 27), GA 14 Sep 2026 | 2026-09-08 | Availability strings taken from developer.apple.com DocC JSON. iOS 27 entries are still flagged BETA on this date. |
| SwiftUI Liquid Glass API (.glassEffect, Glass, GlassEffectContainer, glassEffectID, glassEffectUnion, glassEffectTransition, GlassButtonStyle) | iOS 26.0 / iPadOS 26.0 / Mac Catalyst 26.0 / macOS 26.0 / tvOS 26.0 / watchOS 26.0 (no visionOS) | 2026-09-08 | Unchanged in the 2026 cycle: nothing renamed or deprecated. Glass has exactly .regular / .clear / .identity plus .tint(_:) and .interactive(_:). Default shape is Capsule (DefaultGlassEffectShape). |
| SwiftUI @Animatable / @AnimatableIgnored macros | Xcode 26 toolchain (WWDC25); declared availability iOS 13.0 / iPadOS 13.0 / Mac Catalyst 13.0 / macOS 10.15 / tvOS 13.0 / visionOS 1.0 / watchOS 6.0 | 2026-09-08 | Toolchain requirement, not a deployment-target requirement. |
| SwiftUI hover APIs (hoverEffect, HoverEffect, onHover, onContinuousHover, pointerStyle) | hoverEffect iOS/iPadOS/Mac Catalyst 13.4, tvOS 16.0, visionOS 1.0 - macOS UNAVAILABLE; onHover iOS 13.4 / macOS 10.15; onContinuousHover iOS 17.0 / macOS 14.0; pointerStyle macOS 15.0 / visionOS 2.0 | 2026-09-08 |  |
| SwiftUI animation primitives (PhaseAnimator, KeyframeAnimator, Spring, Metal effects, Canvas, gestures) | PhaseAnimator/KeyframeAnimator/Spring iOS 17.0 macOS 14.0; colorEffect/distortionEffect/layerEffect/ShaderLibrary iOS 17.0 macOS 14.0 (no watchOS); visualEffect iOS 17.0; Canvas iOS 15.0 macOS 12.0; SpatialTapGesture iOS 16.0 macOS 13.0; MagnifyGesture/RotateGesture iOS 17.0 macOS 14.0; navigationTransition/matchedTransitionSource iOS 18.0 macOS 15.0 | 2026-09-08 |  |
| Compose Multiplatform | 1.12.0 stable (released 2026-08-25); previous line 1.10.3 (2026-03-19); Kotlin 2.2.20+ recommended | 2026-09-08 | iOS interop lives in androidx.compose.ui.viewinterop; androidx.compose.ui.interop.UIKitView overloads are @Deprecated. No IOSKeyboardEventListener type exists in any version. |
| Compose Multiplatform iOS keyboard/focus API | ComposeUIViewControllerConfiguration.onFocusBehavior : OnFocusBehavior = FocusableAboveKeyboard \| DoNothing (androidx.compose.ui.uikit), jb-main as of 2026-09-08 | 2026-09-08 |  |
| Compose Multiplatform Resources | Qualifier directories (values-fr/strings.xml); drawable = PNG/JPEG/BMP/WebP + Android XML vector; SVG on all targets except Android; raw files via Res.readBytes("files/...") with no generated Res.file accessor | 2026-09-08 |  |
| WCAG target size | WCAG 2.2 - SC 2.5.8 Target Size (Minimum), Level AA, 24x24 CSS px; SC 2.5.5 Target Size (Enhanced), Level AAA, 44x44 CSS px | 2026-09-08 |  |
| Apple HIG control sizes (Accessibility > Mobility) | iOS/iPadOS 44x44 pt default / 28x28 pt minimum; macOS 28x28 / 20x20; tvOS 66x66 / 56x56; visionOS 60x60 / 28x28; watchOS 44x44 / 28x28; ~12 pt padding bezeled, ~24 pt unbezeled | 2026-09-08 |  |
| Material Design 3 touch targets | 48x48 dp minimum, 8 dp spacing; Compose Modifier.minimumInteractiveComponentSize() enforces 48 dp | 2026-09-08 |  |
| Android predictive back | Available since Android 13 (API 33) behind android:enableOnBackInvokedCallback; developer-option-gated animations on Android 13-14; automatic for opted-in apps from Android 15 | 2026-09-08 |  |
