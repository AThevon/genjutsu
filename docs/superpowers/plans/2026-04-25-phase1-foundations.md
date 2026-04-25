# Phase 1 - Mobile Creative Excellence Foundations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Phase 1 of the mobile creative excellence v2.0 (foundations cross-platform): create `mobile-principles` and `desktop-principles` shared layers, neutralize web-bias in `motion-principles` and `design-audit`, and extend the two orchestrators (`creative-excellence`, `design-excellence`) to detect Android/iOS/macOS stacks and load the right sub-skills dynamically.

**Architecture:** The plan adds two new shared layers (`mobile-principles`, `desktop-principles`) that any stack can load when context matches. Existing skills are extended (not rewritten) to handle cross-platform cases. The orchestrators get an extended SCAN block, a layered LOAD table, generalized Iron Rules, cross-platform THESIS examples, a conditional DISCOVER question for legacy projects, and (for design-excellence) stack-aware MASTER.md generation. No new orchestrator skills are created. After Phase 1, the foundation is in place but no Compose / SwiftUI sub-skill exists yet (Phases 2-4 add them).

**Tech Stack:** Markdown skills with YAML frontmatter, bash detection scripts inside SKILL.md files. No code compilation. Validation is done via `yq` / `python -c "import yaml"` for frontmatter, manual review for content quality, and the existing `package-for-claude-ai.sh` script for packaging.

**Reference:** [Mobile Creative Excellence Design Spec](../specs/2026-04-25-mobile-creative-excellence-design.md)

**Hard rules to honor throughout:**
- Never use em-dash (`-`) anywhere in new content. Use `-` or rephrase. (CLAUDE.md global rule.)
- Never include `Co-Authored-By: Claude` in commit messages. (CLAUDE.md global rule.)
- Frontmatter `name` and `description` fields required for claude.ai compatibility.
- Sources cited at the bottom of each new SKILL.md (consistency with existing web sub-skills).
- Each SKILL.md must include at least one BAD/GOOD section (anti-AI-slop philosophy).

**Validation pattern (used at the end of every file creation task):**

```bash
python3 -c "
import yaml, sys
with open('$FILE') as f:
    txt = f.read()
parts = txt.split('---', 2)
if len(parts) < 3:
    print('FAIL: no frontmatter'); sys.exit(1)
fm = yaml.safe_load(parts[1])
assert 'name' in fm and 'description' in fm, 'missing name or description'
print('OK: frontmatter valid for', fm['name'])
"
grep -c '-' "$FILE" | grep -q '^0$' && echo "OK: no em-dash" || (echo "FAIL: em-dash present"; exit 1)
```

---

## Task 1: Create `mobile-principles` directory and SKILL.md skeleton

**Files:**
- Create: `skills/_creative/mobile-principles/SKILL.md`
- Create: `skills/_creative/mobile-principles/references/` (empty directory)

- [ ] **Step 1: Create the directory structure**

```bash
mkdir -p skills/_creative/mobile-principles/references
```

- [ ] **Step 2: Write the SKILL.md with frontmatter and full content**

Write `skills/_creative/mobile-principles/SKILL.md` with the following structure. Each section must be filled out, no placeholders.

**Frontmatter:**
```yaml
---
name: mobile-principles
description: "Mobile-specific UX principles - touch targets, hover-less doctrine, thumb zones, safe areas, gestures, mobile perf budgets. Cross-platform (web mobile, iOS, Android)."
---
```

**Required sections (in order):**

1. **Header + intro** (6 lines max):
   ```
   # Mobile Principles

   > Touch-first UX context. Loaded when mobile is detected (web mobile, iOS, Android).
   > Concise rules here. Deep-dive in `references/`.
   ```

2. **Touch Targets** - cross-platform table:
   | Platform | Minimum | Recommended | Spec |
   | Apple iOS | 44pt | 44pt + 8pt spacing | Apple HIG |
   | Android | 48dp | 48dp + 8dp spacing | Material Design |
   | Web mobile | 44px | 44px + 8px spacing | WCAG 2.5.5 |
   Followed by a 2-3 line rule of thumb: "any tap target smaller than the platform minimum is a usability bug, period."

3. **No-Hover Doctrine** - 1 paragraph + 3 code blocks (CSS, SwiftUI, Compose):
   - Explain that `:hover` must never be the unique trigger on mobile.
   - CSS: `@media (hover: hover) { ... }` to gate hover styles.
   - SwiftUI: use `onTapGesture` and `.contextMenu` for long-press equivalents.
   - Compose: use `Modifier.combinedClickable` with `onLongClick` for long-press.

4. **Thumb Zones (Hoober)** - explain the easy/ok/hard zones (bottom-third easy on portrait phones, top-corners hard), with one ASCII diagram:
   ```
   ┌─────────────┐
   │     hard    │  ← top of phone
   │             │
   │     ok      │
   │             │
   │    easy     │  ← bottom (thumb naturally rests)
   │             │
   └─────────────┘
   ```
   Rule: primary CTA goes in the bottom half. Secondary actions in top.

5. **Safe Areas** - cross-platform table:
   | Platform | API | Insets respected |
   | Web | `env(safe-area-inset-top|right|bottom|left)` + `viewport-fit=cover` | notch, home indicator |
   | SwiftUI | `.safeAreaInset(edge: ...)`, `safeAreaInsets` env | nav bar, tab bar, notch, home |
   | Compose | `Modifier.windowInsetsPadding(WindowInsets.safeDrawing)` | system bars, IME, cutouts |

6. **Reduced Motion (cross-platform unified)** - the table promised in the spec:
   | Platform | API |
   | Web CSS | `@media (prefers-reduced-motion: reduce)` |
   | Web JS | `window.matchMedia('(prefers-reduced-motion: reduce)')` |
   | SwiftUI | `@Environment(\.accessibilityReduceMotion) var reduceMotion` |
   | UIKit | `UIAccessibility.isReduceMotionEnabled` |
   | Compose | `LocalAccessibilityManager.current.isReduceTransitions` (custom helper, see references) |
   Plus 3 short code examples (one per native API).

7. **Mobile Gestures (canonical patterns)** - bullet list of the 5 must-know gestures with 1-line description:
   - Swipe-back (iOS edge swipe to navigate)
   - Pull-to-refresh (top of scroll, downward drag)
   - Drag-to-dismiss (modal, downward drag past threshold)
   - Pinch-to-zoom (two-finger, common on images and maps)
   - Swipe actions on rows (delete, archive)

8. **Mobile Performance Budgets** - bullet list:
   - Cold start: <2s on mid-range devices (Android Pixel 4a baseline, iPhone SE 2nd gen)
   - Frame budget: 16.67ms (60fps) or 8.33ms (120fps ProMotion)
   - APK/IPA size budget: aim for <30MB APK, <50MB IPA before adding heavy libs (Lottie, Rive add 500KB-2MB)
   - Battery: avoid continuous CPU activity in background
   - Network: respect `Save-Data` header on web, `URLSessionConfiguration.allowsCellularAccess` on iOS, `ConnectivityManager` checks on Android

9. **Anti-Patterns (BAD / GOOD)** - 3 examples minimum:
   - BAD: relying on `:hover` to reveal interactive elements; GOOD: visible-by-default + `@media (hover: hover)` for enhancement.
   - BAD: 32dp tap targets on Android; GOOD: 48dp minimum even if it requires extra padding.
   - BAD: ignoring `safeAreaInsets` and putting buttons under the home indicator; GOOD: always wrap with `.safeAreaPadding()` or `Modifier.windowInsetsPadding()`.

10. **Quick Reference: Loading sub-skills** (mirror the table from `motion-principles`):
    | Need | Load |
    | Gesture deep-dive | `references/gestures-deep.md` |
    | Mobile a11y deep-dive | `references/accessibility-mobile.md` |
    | Compose-specific anim | `../compose-motion/SKILL.md` |
    | SwiftUI-specific anim | `../swiftui-motion/SKILL.md` |

11. **Sources** (footer):
    - Steven Hoober, "Designing for Touch" (mobile thumb zones research)
    - Apple Human Interface Guidelines (iOS): https://developer.apple.com/design/human-interface-guidelines/
    - Material Design (Android): https://m3.material.io/foundations/layout/canonical-layouts/overview
    - WCAG 2.5.5 Target Size: https://www.w3.org/WAI/WCAG21/Understanding/target-size.html

- [ ] **Step 3: Validate frontmatter and em-dash absence**

Run the validation pattern (see plan header) on `skills/_creative/mobile-principles/SKILL.md`. Expected: `OK: frontmatter valid for mobile-principles` and `OK: no em-dash`.

- [ ] **Step 4: Commit**

```bash
git add skills/_creative/mobile-principles/SKILL.md
git commit -m "feat(skills): add mobile-principles SKILL.md (cross-platform mobile UX foundation)"
```

---

## Task 2: Create `mobile-principles/references/gestures-deep.md`

**Files:**
- Create: `skills/_creative/mobile-principles/references/gestures-deep.md`

- [ ] **Step 1: Write the deep-dive file**

Target ~200 lines. No frontmatter (references don't need it - only the parent SKILL.md does). Sections:

1. **Title + intro** (3 lines): "Deep dive on gestures across mobile platforms. Covers conflict resolution, momentum, and complex composition."

2. **Platform-specific gesture APIs** - 3 subsections (one per platform), each with 1-2 code examples:
   - Web: Pointer Events API (`pointerdown`, `pointermove`, `pointerup`), `touch-action` CSS property, libraries (Hammer.js, use-gesture).
   - SwiftUI: `DragGesture`, `LongPressGesture`, `MagnifyGesture`, `RotateGesture`, `.gesture()` and `.simultaneousGesture()` modifiers. Show one chained example using `SequenceGesture`.
   - Compose: `Modifier.draggable`, `Modifier.scrollable`, `detectDragGestures`, `awaitPointerEventScope`. Show one custom gesture detector example.

3. **Gesture conflicts and resolution** - section explaining:
   - Vertical scroll vs horizontal swipe (newest direction wins after threshold).
   - Long-press vs drag (pointer-up before threshold = press, after threshold = drag).
   - Native back-swipe (iOS edge) vs custom horizontal pan (custom must yield).
   - Code example in SwiftUI using `.simultaneousGesture(_, including:)` with `GestureMask`.
   - Code example in Compose using `nestedScroll` connection.

4. **Momentum and fling** - section on inertia patterns:
   - SwiftUI: `.gestureVelocity` (iOS 17+), or compute via `DragGesture.Value.predictedEndTranslation`.
   - Compose: `Animatable.animateDecay()` with `splineBasedDecay()`.
   - Web: CSS `scroll-snap-type` for native fling, or compute via `requestAnimationFrame`.

5. **Pull-to-refresh canonical implementation** - 3 code examples:
   - Compose: `PullToRefreshBox` (Material 3 1.3+).
   - SwiftUI: `.refreshable { await refresh() }` (iOS 15+).
   - Web: custom `IntersectionObserver` + transform on pull.

6. **Sources**:
   - Apple HIG Gestures: https://developer.apple.com/design/human-interface-guidelines/gestures
   - Material Design Gestures: https://m3.material.io/foundations/interaction/gestures
   - W3C Pointer Events: https://www.w3.org/TR/pointerevents/

- [ ] **Step 2: Validate em-dash absence**

```bash
grep -c '-' skills/_creative/mobile-principles/references/gestures-deep.md | grep -q '^0$' && echo OK
```

- [ ] **Step 3: Commit**

```bash
git add skills/_creative/mobile-principles/references/gestures-deep.md
git commit -m "feat(skills): add mobile-principles/references/gestures-deep.md"
```

---

## Task 3: Create `mobile-principles/references/accessibility-mobile.md`

**Files:**
- Create: `skills/_creative/mobile-principles/references/accessibility-mobile.md`

- [ ] **Step 1: Write the deep-dive file**

Target ~150 lines. No frontmatter. Sections:

1. **Title + intro** (3 lines): "Mobile accessibility patterns. Screen readers, dynamic type, contrast, motor accommodations."

2. **Screen readers** - 3 subsections:
   - VoiceOver (iOS/macOS): `.accessibilityLabel`, `.accessibilityHint`, `.accessibilityValue`, `.accessibilityAddTraits`. Code example labeling a custom slider.
   - TalkBack (Android Compose): `Modifier.semantics { contentDescription = "..." }`, `clearAndSetSemantics`, `traversalIndex`. Code example for a custom button.
   - Web (mobile): `aria-label`, `aria-describedby`, `role="slider"`, `aria-valuemin/max/now`. Note the difference with web desktop (no major API divergence).

3. **Dynamic type / font scaling** - 3 examples:
   - SwiftUI: `Text("...").font(.body)` already scales, custom fonts must use `.dynamicTypeSize(...)` or `UIFontMetrics`.
   - Compose: scale fonts via `MaterialTheme.typography` and respect `LocalDensity.current.fontScale`.
   - Web: relative units (`rem`, `em`) and `font-size: clamp(...)` for caps.

4. **Contrast** - WCAG 2.2 AA requirements (4.5:1 normal text, 3:1 large text, 3:1 non-text components). Reference tools: Stark plugin (Figma), Xcode Accessibility Inspector, Android Accessibility Scanner.

5. **Motor accommodations** - canonical patterns:
   - iOS: `UIAccessibility.isAssistiveTouchRunning`, AssistiveTouch as input.
   - Android: switch access (`AccessibilityService`).
   - Web: `prefers-reduced-motion`, large click targets, no hover-only affordances.

6. **Testing checklist** - 6 items: VoiceOver/TalkBack pass, Dynamic Type at 200%, contrast pass, all interactive elements have labels, no info conveyed by color alone, all gestures have a non-gesture alternative.

7. **Sources**:
   - Apple Accessibility: https://developer.apple.com/accessibility/
   - Android Accessibility: https://developer.android.com/guide/topics/ui/accessibility
   - WCAG 2.2: https://www.w3.org/TR/WCAG22/

- [ ] **Step 2: Validate em-dash absence**

```bash
grep -c '-' skills/_creative/mobile-principles/references/accessibility-mobile.md | grep -q '^0$' && echo OK
```

- [ ] **Step 3: Commit**

```bash
git add skills/_creative/mobile-principles/references/accessibility-mobile.md
git commit -m "feat(skills): add mobile-principles/references/accessibility-mobile.md"
```

---

## Task 4: Create `desktop-principles` directory and SKILL.md

**Files:**
- Create: `skills/_creative/desktop-principles/SKILL.md`
- Create: `skills/_creative/desktop-principles/references/` (empty directory)

- [ ] **Step 1: Create the directory structure**

```bash
mkdir -p skills/_creative/desktop-principles/references
```

- [ ] **Step 2: Write the SKILL.md**

**Frontmatter:**
```yaml
---
name: desktop-principles
description: "Desktop-specific UX principles - hover states, pointer precision, keyboard shortcuts, multi-window, focus management. Covers macOS, Windows, Linux, web desktop."
---
```

**Required sections (in order, ~350 lines total):**

1. **Header + intro** (4 lines): "Desktop UX context. Loaded when desktop is detected (macOS, Windows, Linux desktop, web desktop). Concise rules here. Deep-dive in `references/`."

2. **Hover States Are Mandatory** - 1 paragraph + 3 code examples:
   - Explain hover is the primary affordance signal on desktop (the inverse of mobile).
   - CSS: `:hover` styles for all interactive elements, with `transition` timing 100-200ms.
   - SwiftUI: `.onHover { hovering in ... }`, `.hoverEffect(.highlight)` (iOS only).
   - Compose: `Modifier.onPointerEvent(PointerEventType.Enter / Exit)` (Compose Desktop), or `Modifier.hoverable` + `interactionSource`.

3. **Pointer Precision** - explain target sizes can be smaller than mobile (24-32px), but minimums still apply. WCAG accommodates with 24x24 absolute min for desktop. Add a 1-paragraph note on Fitts's Law and corner/edge targeting.

4. **Keyboard Shortcuts (first-class)** - canonical reference:
   - macOS: `⌘+N` new, `⌘+W` close window, `⌘+Q` quit app, `⌘+,` settings, `⌘+F` find, `⌘+/` toggle.
   - Windows/Linux: `Ctrl+N`, `Ctrl+W`, `Alt+F4`, `Ctrl+,`, `Ctrl+F`, `Ctrl+/`.
   - Web: prefer `Ctrl/Cmd` detection via `navigator.platform` or `event.metaKey`.
   - SwiftUI: `.keyboardShortcut("n", modifiers: .command)`.
   - Compose Desktop: `Modifier.onKeyEvent { ... }` + `KeyShortcut`.

5. **Multi-Window Patterns** - section explaining:
   - When to open a new window (long-running task, parallel context, document-based app).
   - SwiftUI: `WindowGroup`, `.windowResizability(.contentSize)`, `Scene` lifecycle.
   - Compose Desktop: `Window { ... }` composable, `MultipleWindowsApplication`.
   - State sharing between windows: shared model (singleton or DI), avoid duplicate state.

6. **Focus Management** - section explaining tab order and focus rings:
   - SwiftUI: `@FocusState`, `.focusable()`, `.focused($state, equals: ...)`.
   - Compose: `Modifier.focusable()`, `FocusRequester`, `LocalFocusManager`.
   - Web: `tabindex`, `:focus-visible` for keyboard-only focus rings, never `outline: none` without alternative.

7. **Information Density** - 1 paragraph: desktop accepts denser layouts (8px grid vs 4-8px on mobile), sidebars, command palettes (`⌘K`), data tables. Reference Linear, Things 3, Notion as exemplars.

8. **Subtle Animations Doctrine** - 1 paragraph + 1 BAD/GOOD example:
   - Explain animations should be discreet on desktop (user looks at the same UI for hours).
   - BAD: a 600ms bounce on every hover. GOOD: 100ms opacity transition on hover.

9. **Anti-Patterns (BAD / GOOD)** - 3 examples minimum:
   - BAD: hiding sidebar nav behind a hamburger on desktop; GOOD: persistent sidebar, optionally collapsible.
   - BAD: no keyboard shortcuts for primary actions; GOOD: `⌘N`, `⌘S`, `⌘F` baseline.
   - BAD: removing focus rings (`outline: none`); GOOD: `:focus-visible` with custom ring respecting brand.

10. **Quick Reference**:
    | Need | Load |
    | Keyboard patterns deep-dive | `references/keyboard-patterns.md` |
    | Multi-window state | `references/multi-window.md` |
    | SwiftUI animations | `../swiftui-motion/SKILL.md` |
    | Compose Desktop | `../compose-multiplatform/SKILL.md` (when desktop is a CMP target) |

11. **Sources**:
    - Apple Human Interface Guidelines (macOS): https://developer.apple.com/design/human-interface-guidelines/macos
    - Microsoft Fluent Design 2: https://fluent2.microsoft.design/
    - GNOME Human Interface Guidelines: https://developer.gnome.org/hig/

- [ ] **Step 3: Validate frontmatter and em-dash absence**

```bash
python3 -c "
import yaml
with open('skills/_creative/desktop-principles/SKILL.md') as f:
    parts = f.read().split('---', 2)
fm = yaml.safe_load(parts[1])
assert fm['name'] == 'desktop-principles'
print('OK')
"
grep -c '-' skills/_creative/desktop-principles/SKILL.md | grep -q '^0$' && echo "OK no em-dash"
```

- [ ] **Step 4: Commit**

```bash
git add skills/_creative/desktop-principles/SKILL.md
git commit -m "feat(skills): add desktop-principles SKILL.md (cross-platform desktop UX foundation)"
```

---

## Task 5: Create `desktop-principles/references/keyboard-patterns.md`

**Files:**
- Create: `skills/_creative/desktop-principles/references/keyboard-patterns.md`

- [ ] **Step 1: Write the deep-dive file**

Target ~150 lines. Sections:

1. **Title + intro** (3 lines).

2. **Canonical shortcuts by domain** - 4 tables:
   - **App lifecycle**: New (⌘N/Ctrl+N), Open (⌘O/Ctrl+O), Save (⌘S/Ctrl+S), Save As (⌘⇧S/Ctrl+Shift+S), Close window (⌘W/Ctrl+W or Alt+F4), Quit (⌘Q/Ctrl+Q via menu or Alt+F4).
   - **Editing**: Undo (⌘Z/Ctrl+Z), Redo (⌘⇧Z/Ctrl+Y), Cut/Copy/Paste (⌘X/C/V), Select All (⌘A/Ctrl+A), Find (⌘F/Ctrl+F), Replace (⌘⌥F/Ctrl+H).
   - **Navigation**: Switch tab (⌘⌥→/Ctrl+Tab), New tab (⌘T/Ctrl+T), Go back (⌘[/Alt+Left), History (⌘Y/Ctrl+H).
   - **App-specific (creative apps)**: Command palette (⌘K), Settings (⌘,/Ctrl+,), Toggle sidebar (⌘B), Focus mode (⌘. or ⌘⇧F).

3. **Cross-platform detection** - code example showing how to detect modifier on web:
   ```js
   const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
   const modKey = isMac ? event.metaKey : event.ctrlKey;
   ```
   And on SwiftUI, modifiers like `.keyboardShortcut("k", modifiers: [.command])` are platform-agnostic (work on iOS with hardware keyboard).

4. **Chord shortcuts (multi-step)** - section on chord patterns à la VS Code (`⌘K, ⌘S` = open shortcuts).
   - SwiftUI doesn't natively support chords; use `NSEvent.localMonitor` (macOS).
   - Web: maintain a buffer with timeout (300ms typical).
   - Compose Desktop: stateful key event handler.

5. **Conflicts to avoid** - bullet list:
   - Don't override OS shortcuts (`⌘Q`, `⌘Tab`, `⌘Space`).
   - Don't override browser shortcuts on web (`⌘L`, `⌘T`, `⌘W`) without strong justification.
   - Avoid one-letter shortcuts without modifier (kills text input).

6. **Discoverability** - patterns:
   - Show shortcut in menu next to the command.
   - Show shortcut in tooltip on hover after 1s delay.
   - Provide a `⌘?` or `⌘/` "show all shortcuts" overlay.

7. **Sources**:
   - macOS shortcuts: https://support.apple.com/en-us/HT201236
   - Windows shortcuts: https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec

- [ ] **Step 2: Validate**

```bash
grep -c '-' skills/_creative/desktop-principles/references/keyboard-patterns.md | grep -q '^0$' && echo OK
```

- [ ] **Step 3: Commit**

```bash
git add skills/_creative/desktop-principles/references/keyboard-patterns.md
git commit -m "feat(skills): add desktop-principles/references/keyboard-patterns.md"
```

---

## Task 6: Create `desktop-principles/references/multi-window.md`

**Files:**
- Create: `skills/_creative/desktop-principles/references/multi-window.md`

- [ ] **Step 1: Write the deep-dive file**

Target ~120 lines. Sections:

1. **Title + intro** (3 lines).

2. **When to use multiple windows** - 3 scenarios:
   - Document-based apps (each document = one window).
   - Long-running secondary task (export progress, terminal, render preview).
   - Companion / inspector windows (secondary tools, palettes).

3. **SwiftUI multi-window** - code example with `WindowGroup`, `.windowResizability(.contentSize)`, opening via `@Environment(\.openWindow)`:
   ```swift
   @main
   struct MyApp: App {
       var body: some Scene {
           WindowGroup { ContentView() }
           Window("Inspector", id: "inspector") { InspectorView() }
               .windowResizability(.contentSize)
       }
   }
   // Then in any view:
   @Environment(\.openWindow) var openWindow
   Button("Open Inspector") { openWindow(id: "inspector") }
   ```

4. **Compose Desktop multi-window** - code example with `Window` composable:
   ```kotlin
   fun main() = application {
       var inspectorOpen by remember { mutableStateOf(false) }
       Window(onCloseRequest = ::exitApplication, title = "Main") {
           Button(onClick = { inspectorOpen = true }) { Text("Open Inspector") }
       }
       if (inspectorOpen) {
           Window(onCloseRequest = { inspectorOpen = false }, title = "Inspector") {
               InspectorContent()
           }
       }
   }
   ```

5. **State sharing patterns**:
   - Singleton model (simplest, fine for small apps).
   - DI container (Koin / Hilt for Compose, an `ObservableObject` env for SwiftUI).
   - Shared `@Observable` class injected via `.environment(...)` (SwiftUI iOS 17+).

6. **Window lifecycle gotchas**:
   - SwiftUI `Scene.onChange` for active/inactive (not `.onAppear`).
   - Compose `LifecycleEventObserver` doesn't apply to Compose Desktop, use `WindowState` and `LaunchedEffect`.
   - Web: there's no real multi-window unless you `window.open(...)`, and that's usually a popup blocker fight.

7. **Sources**:
   - Apple multi-window: https://developer.apple.com/documentation/swiftui/scene
   - JetBrains Compose Desktop windows: https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-desktop-window-management.html

- [ ] **Step 2: Validate**

```bash
grep -c '-' skills/_creative/desktop-principles/references/multi-window.md | grep -q '^0$' && echo OK
```

- [ ] **Step 3: Commit**

```bash
git add skills/_creative/desktop-principles/references/multi-window.md
git commit -m "feat(skills): add desktop-principles/references/multi-window.md"
```

---

## Task 7: Modify `motion-principles/SKILL.md` - neutralize web-bias

**Files:**
- Modify: `skills/_creative/motion-principles/SKILL.md`

This task makes 4 surgical edits without rewriting the file. Read the file first to confirm line numbers haven't shifted from the spec.

- [ ] **Step 1: Read the current file to confirm structure**

```bash
cat skills/_creative/motion-principles/SKILL.md
```

Expected: file matches the structure described in the spec (Timing Rules, Easing Cheat Sheet, Accessibility, Universal Do Not Rules, Performance Checklist, Quick Reference at the end).

- [ ] **Step 2: Extend the Easing Cheat Sheet**

Find the Easing Cheat Sheet table (around line 27-36). Add a new sub-section directly after it titled `### Native easing equivalents` with this content:

```markdown
### Native easing equivalents (cross-platform)

| Web (CSS / JS) | SwiftUI | Compose |
|---|---|---|
| `cubic-bezier(0.2, 0, 0, 1)` | `.spring(response: 0.4, dampingFraction: 0.85)` or `.snappy` | `spring(stiffness = Spring.StiffnessMedium, dampingRatio = 0.85f)` |
| `ease-out` | `.easeOut(duration: 0.3)` | `tween(durationMillis = 300, easing = LinearOutSlowInEasing)` |
| `ease-in` | `.easeIn(duration: 0.2)` | `tween(durationMillis = 200, easing = FastOutLinearInEasing)` |
| spring (bouncy) | `.bouncy` (iOS 17+) | `spring(stiffness = Spring.StiffnessLow, dampingRatio = Spring.DampingRatioMediumBouncy)` |
| spring (smooth) | `.smooth` (iOS 17+) | `spring(stiffness = Spring.StiffnessMedium, dampingRatio = Spring.DampingRatioNoBouncy)` |
```

- [ ] **Step 3: Replace the Accessibility section to be cross-platform**

Find the section `## Accessibility (Non-Negotiable)` and the subsection `### prefers-reduced-motion -- MANDATORY`. Replace the section's CSS-only opening so it covers all 3 platforms. The section becomes:

```markdown
## Accessibility (Non-Negotiable)

### Reduced motion - MANDATORY

Every animated component must respect the user's reduced-motion preference. No exceptions, regardless of platform.

| Platform | API |
|---|---|
| Web CSS | `@media (prefers-reduced-motion: reduce)` |
| Web JS | `window.matchMedia('(prefers-reduced-motion: reduce)')` |
| SwiftUI | `@Environment(\.accessibilityReduceMotion) var reduceMotion` |
| UIKit | `UIAccessibility.isReduceMotionEnabled` (+ `reduceMotionStatusDidChangeNotification`) |
| Compose | `LocalAccessibilityManager.current.isReduceTransitions` (with helper) |

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

**SwiftUI:**
```swift
struct AnimatedView: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @State var visible = false

    var body: some View {
        Text("Hello")
            .opacity(visible ? 1 : 0)
            .animation(reduceMotion ? .none : .spring(response: 0.4, dampingFraction: 0.85), value: visible)
    }
}
```

**Compose:**
```kotlin
@Composable
fun rememberReduceTransitions(): Boolean {
    val manager = LocalAccessibilityManager.current
    return remember(manager) { manager?.isReduceTransitions ?: false }
}

@Composable
fun AnimatedComponent() {
    val reduce = rememberReduceTransitions()
    val alpha by animateFloatAsState(
        targetValue = if (visible) 1f else 0f,
        animationSpec = if (reduce) snap() else spring(stiffness = Spring.StiffnessMedium)
    )
}
```
```

(Remove the old GSAP-specific block; the GSAP example will be referenced below in the Universal Do Not section instead.)

- [ ] **Step 4: Update the "Universal Do Not Rules" examples to be platform-agnostic**

Find the section `## Universal "Do Not" Rules`. Each rule (1-5) currently has CSS / JS examples. Add native equivalents inline. For example, Rule 1 ("Never animate width/height/top/left") gains:

```markdown
**SwiftUI equivalent (BAD vs GOOD):**
```swift
// BAD - animates frame (causes layout pass)
.frame(height: open ? 400 : 0)
.animation(.easeInOut, value: open)

// GOOD - animates transform via offset
.offset(y: open ? 0 : 400)
.animation(.spring(), value: open)
```

**Compose equivalent (BAD vs GOOD):**
```kotlin
// BAD - animates size (full layout pass)
val height by animateDpAsState(if (open) 400.dp else 0.dp)

// GOOD - animates Y offset via graphicsLayer
val translation by animateFloatAsState(if (open) 0f else 400f)
Box(modifier = Modifier.graphicsLayer { translationY = translation })
```
```

Add similar 3-language BAD/GOOD blocks to Rules 2 ("Never scale to 0"), 4 ("Never exceed 500ms on UI"), and 5 ("Never skip reduced motion"). Rule 3 ("Never ease-in on entry") needs only minor wording.

- [ ] **Step 5: Extend the Quick Reference table**

Find the section `## Quick Reference: Loading Sub-skills` at the bottom. Replace the table with the extended version:

```markdown
| Need | Load |
|---|---|
| Easing deep-dive, spring configs | `references/easing-guide.md` |
| Copy-paste enter/exit patterns | `references/enter-exit-recipes.md` |
| Designer-weighted style choice | `references/designers.md` |
| Mobile UX context | `../mobile-principles/SKILL.md` |
| Desktop UX context | `../desktop-principles/SKILL.md` |
| GSAP specifics | `../gsap/SKILL.md` |
| Framer Motion specifics | `../framer-motion/SKILL.md` |
| CSS-only animations | `../css-native/SKILL.md` |
| Three.js / R3F | `../threejs-r3f/SKILL.md` |
| Canvas / generative | `../canvas-generative/SKILL.md` |
| Compose Android animations | `../compose-motion/SKILL.md` |
| Compose Multiplatform | `../compose-multiplatform/SKILL.md` |
| SwiftUI iOS/macOS animations | `../swiftui-motion/SKILL.md` |
| Compose advanced graphics | `../compose-graphics/SKILL.md` |
| SwiftUI advanced graphics | `../swiftui-graphics/SKILL.md` |
| Visual / motion / a11y audit | `../design-audit/SKILL.md` |
| UI/UX intelligence (50 styles, 21 palettes) | `../ui-ux-pro-max/SKILL.md` |
```

- [ ] **Step 6: Validate em-dash absence**

```bash
grep -c '-' skills/_creative/motion-principles/SKILL.md | grep -q '^0$' && echo OK
```

(Note: this file already had 0 em-dashes per the audit. Just confirm.)

- [ ] **Step 7: Commit**

```bash
git add skills/_creative/motion-principles/SKILL.md
git commit -m "feat(skills): make motion-principles cross-platform (Compose + SwiftUI examples, unified reduced-motion API table)"
```

---

## Task 8: Modify `design-audit/SKILL.md` - cross-platform checks

**Files:**
- Modify: `skills/_creative/design-audit/SKILL.md`

- [ ] **Step 1: Read the current file**

```bash
cat skills/_creative/design-audit/SKILL.md
```

Confirm structure: prefers-reduced-motion section, easing inventory section, bundle size section, final checklist. Note exact line numbers if needed.

- [ ] **Step 2: Extend the prefers-reduced-motion grep section**

Find the section that currently only greps web files (around line 60-67). Replace the grep block with this multi-stack version:

```markdown
### Reduced motion - MANDATORY

A project with animation MUST have at least one global handler matching its stack. Run all 3 greps:

```bash
# Web
grep -rn 'prefers-reduced-motion' --include='*.css' --include='*.scss' --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' src/ 2>/dev/null

# SwiftUI / UIKit
grep -rn 'accessibilityReduceMotion\|isReduceMotionEnabled\|reduceMotionStatusDidChangeNotification' --include='*.swift' . 2>/dev/null

# Compose
grep -rn 'LocalAccessibilityManager\|isReduceTransitions\|TRANSITION_ANIMATION_SCALE' --include='*.kt' . 2>/dev/null
```

**Zero results across all 3 in an animated project = critical violation.** At least one handler must exist somewhere. Cross-reference `motion-principles/SKILL.md` for canonical implementations per stack.
```

- [ ] **Step 3: Extend the bundle size section**

Find the section mentioning `framer-motion ~30KB, GSAP ~25KB`. Add a parallel paragraph for native:

```markdown
On mobile native, the APK / IPA size matters. A third-party animation library adds typically 500KB-2MB:

| Library | Size impact (uncompressed) |
|---|---|
| Lottie (iOS) | ~600KB |
| Lottie (Android) | ~900KB |
| Rive (iOS) | ~1.5MB |
| Rive (Android) | ~2MB |
| Native Compose / SwiftUI animations | 0KB (built-in) |

If the project only uses fades, slides, and springs, native APIs (Compose `animate*AsState` + spring, SwiftUI `withAnimation`) are sufficient. Justify a Lottie / Rive dependency only for genuinely complex pre-designed animations (e.g., onboarding illustrations).
```

- [ ] **Step 4: Extend the easing inventory grep**

Find the easing inventory section (the grep command around line 152). Replace with a multi-stack version:

```markdown
### Easing inventory

Run all 3 greps to inventory easing values across the codebase:

```bash
# Web (CSS / JS / TSX)
grep -rnoE 'ease[A-Za-z]*|cubic-bezier\([^)]+\)|spring\([^)]*\)' --include='*.tsx' --include='*.jsx' --include='*.ts' --include='*.css' --include='*.scss' src/ 2>/dev/null

# SwiftUI
grep -rnoE '\.spring\([^)]*\)|\.snappy|\.bouncy|\.smooth|\.linear\(|\.easeIn|\.easeOut|\.interpolatingSpring' --include='*.swift' . 2>/dev/null

# Compose
grep -rnoE 'spring\([^)]*\)|tween\([^)]*\)|FastOutSlowInEasing|LinearOutSlowInEasing|FastOutLinearInEasing|CubicBezierEasing' --include='*.kt' . 2>/dev/null
```

Same rule across all stacks: 3-5 named easings max in the design system. Random values scattered across files = visual inconsistency. If the codebase has 12 different `cubic-bezier(...)` values or 8 custom `spring(response:dampingFraction:)` configurations, that's a design-system violation, fix it by centralizing into named tokens.
```

- [ ] **Step 5: Add new "Stack-specific audit" section before the final checklist**

Insert this section just before `## Final checklist` (or whatever the last section is named):

```markdown
## Stack-specific audit

Pick the subsection matching the project stack.

### Compose (Android / Multiplatform)
- [ ] Run **Layout Inspector** (Android Studio): inspect recompositions, identify components recomposing on every state change.
- [ ] Run **Macrobenchmark** (`androidx.benchmark.macro`): measure frame timing on a real device under representative scrolling / animation load. Target: <16.67ms per frame at 60fps, <8.33ms at 120fps.
- [ ] Inspect **recomposition counts** via `Modifier.recomposeHighlighter()` (Compose 1.6+) or Layout Inspector.
- [ ] Generate **Baseline Profiles** (`BaselineProfileGenerator`) for production builds.
- [ ] Verify `Modifier.semantics` is set on custom components (TalkBack support).

### SwiftUI (iOS / macOS)
- [ ] Run **Instruments Time Profiler**: identify hot paths during animation (target: zero frames over 16.67ms).
- [ ] Run **Instruments Hitches Instrument** (iOS 14+): detects dropped frames and stalls.
- [ ] Run **Instruments GPU Frame Capture** for Metal shaders: verify shader compile time, GPU vs CPU bottleneck.
- [ ] Verify `.accessibilityLabel` / `.accessibilityHint` on every interactive view.
- [ ] Test with Dynamic Type at 200% size (`Environment Overrides` in Xcode).
- [ ] Test with Reduce Motion ON.

### Web
- [ ] Existing checklist above (Lighthouse, Chrome DevTools Performance, etc.).
```

- [ ] **Step 6: Validate em-dash absence**

```bash
grep -c '-' skills/_creative/design-audit/SKILL.md | grep -q '^0$' && echo OK
```

- [ ] **Step 7: Commit**

```bash
git add skills/_creative/design-audit/SKILL.md
git commit -m "feat(skills): make design-audit cross-platform (Compose + SwiftUI greps + Instruments / Layout Inspector checks)"
```

---

## Task 9: Modify `creative-excellence/SKILL.md` (orchestrator) - extend SCAN, LOAD, IronRules, THESIS

**Files:**
- Modify: `skills/creative-excellence/SKILL.md`

- [ ] **Step 1: Read the current file**

```bash
cat skills/creative-excellence/SKILL.md
```

Identify the sections to modify: SCAN block (around lines 32-42), DISCOVER, IRON RULES (lines 14-22), THESIS examples (lines 92-96), LOAD block (lines 102-138), and AUDIT (lines 162-180).

- [ ] **Step 2: Replace the SCAN block**

Find the current SCAN section (`### 1. SCAN - Detect the stack` and the bash block under it). Replace the entire bash block with the extended version:

```bash
# 1. Web (existing)
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
grep -E '\.iOS\(|\.macOS\(' Package.swift 2>/dev/null
grep -E 'SDKROOT = (iphoneos|macosx)' *.xcodeproj/project.pbxproj 2>/dev/null

# 6. Mobile web indicators
grep -rE 'viewport.*width=device-width|@media.*pointer:\s*coarse|@media.*max-width' --include='*.html' --include='*.css' --include='*.scss' . 2>/dev/null | head -3
ls public/manifest.json public/sw.js 2>/dev/null

# 7. Legacy bridge indicators (mention in DISCOVER, do not auto-load)
ls -- *.xib *.storyboard 2>/dev/null
find . -path '*/res/layout/*.xml' 2>/dev/null | head -1
grep -rE 'setContentView\(R\.layout' --include='*.kt' --include='*.java' . 2>/dev/null | head -1
```

Update the "Map the results" list under SCAN to add:
- **Native Android**: Compose detected via gradle dependencies.
- **Native Apple**: SwiftUI detected via Package.swift / xcodeproj + swift files.
- **Compose Multiplatform**: kotlin-multiplatform plugin + jetbrains.compose plugin.
- **Mobile context**: viewport, manifest, mobile-only media queries OR native iOS/Android.
- **Desktop context**: macOS target OR no mobile indicators on web.
- **Legacy mixed**: presence of `.xib`, `.storyboard`, layout XML, `setContentView(R.layout.*)`. Mention only, no auto-load.

- [ ] **Step 3: Add a conditional question to DISCOVER for legacy detection**

Find the DISCOVER section. Add this paragraph at the end of the DISCOVER section:

```markdown
**If legacy mixed detected** (XIB / storyboard / layout XML / setContentView(R.layout.\*)):

Ask exactly one question:

> "Je vois que ton projet a [du XML / des XIB / des Activities classiques] en plus du moderne. Pour cette tâche, je reste sur du pur [Compose/SwiftUI], ou tu veux que je m'intègre dans un écran legacy ?"

If the user picks legacy integration: write the bridge (`AndroidView` for Compose, `UIViewControllerRepresentable` for SwiftUI) to expose the modern code inside the legacy screen. Never generate new legacy code (no XML, no XIB, no setContentView).
```

- [ ] **Step 4: Replace Iron Rules 7 and 8**

Find the IRON RULES section (lines 14-22). Replace rules 7 and 8 (the React/GSAP-specific ones) with these stack-agnostic rules:

```markdown
7. **Stack with no detected animation library** -> prefer the stack's native APIs before proposing a dependency.
8. **Animation library detected** (GSAP, Framer Motion, Lottie, Rive, etc.) -> respect the dev's choice. Do not propose a replacement.
```

- [ ] **Step 5: Extend the THESIS examples**

Find the THESIS section examples (line ~92-96). Add 3 cross-platform examples after the existing web ones:

```markdown
- "This Compose hero will use a SharedTransitionLayout with a spring(stiffness=Spring.StiffnessMedium, dampingRatio=0.85) for a fluid card-to-detail transition."
- "This SwiftUI tab transition will use matchedGeometryEffect with a .smooth spring (response: 0.5, dampingFraction: 0.85) for a tactile, spatial feel."
- "This macOS dashboard will use 100ms opacity hover states (no scale on hover, desktop subtlety) and a ⌘1-9 keyboard shortcut to navigate panels."
- "This Android header will use an AGSL shader bound to scrollOffset for a dynamic liquid-glass effect (Android 13+, with a static fallback below)."
```

- [ ] **Step 6: Replace the LOAD block with the layered structure**

Find the section `### 5. LOAD - Load the relevant sub-skills`. Keep the bash environment detection block exactly as is (it's already correct). Replace the two tables ("Load based on the detected stack" and "Load based on the need") with this layered version:

```markdown
**Always load:**
- `$SKILL_BASE/motion-principles/SKILL.md` - the foundation

**Context layers** (load when applicable):

| Detected | Load |
|---|---|
| Mobile context (web mobile OR native iOS / Android) | `$SKILL_BASE/mobile-principles/SKILL.md` |
| Desktop context (macOS OR web desktop with no mobile indicators) | `$SKILL_BASE/desktop-principles/SKILL.md` |
| Audit explicitly requested OR scope=full | `$SKILL_BASE/design-audit/SKILL.md` |
| Advanced UI/UX questions | `$SKILL_BASE/ui-ux-pro-max/SKILL.md` |

**Stack-specific** (load by SCAN):

| Detected stack | Sub-skill to load |
|---|---|
| gsap | `$SKILL_BASE/gsap/SKILL.md` |
| framer-motion | `$SKILL_BASE/framer-motion/SKILL.md` |
| Pure CSS / Tailwind / no lib | `$SKILL_BASE/css-native/SKILL.md` |
| three / @react-three | `$SKILL_BASE/threejs-r3f/SKILL.md` |
| Canvas / generative | `$SKILL_BASE/canvas-generative/SKILL.md` |
| Android Compose | `$SKILL_BASE/compose-motion/SKILL.md` (always) + `$SKILL_BASE/compose-graphics/SKILL.md` (if scope=full or thesis is advanced - see below) |
| Compose Multiplatform | `$SKILL_BASE/compose-motion/SKILL.md` + `$SKILL_BASE/compose-multiplatform/SKILL.md` (always); `$SKILL_BASE/swiftui-motion/SKILL.md` if iOS target detected and SwiftUI interop demanded; `$SKILL_BASE/compose-graphics/SKILL.md` if advanced |
| SwiftUI iOS or macOS | `$SKILL_BASE/swiftui-motion/SKILL.md` (always) + `$SKILL_BASE/swiftui-graphics/SKILL.md` (if scope=full or thesis is advanced) |

**"Advanced thesis" trigger** for `compose-graphics` / `swiftui-graphics`:

The thesis is "advanced" (and triggers loading the graphics sub-skill) if it contains any of these terms:
- `shader`, `Metal`, `AGSL`, `RuntimeShader`, `MSL`
- `liquid-glass`, `glassEffect`, `morphing transition`
- `M3 Expressive`, `MotionScheme`, `expressive motion`
- `colorEffect`, `distortionEffect`, `layerEffect`
- `Canvas` (with generative / particle / flow field context)
- `holographic`, `CRT`, `displacement`, `ripple`

Otherwise stick to the base motion sub-skill.

**Note:** Phase 1 of the v2.0 rollout adds `mobile-principles` and `desktop-principles`, but the stack-specific Compose/SwiftUI sub-skills land in Phases 2-4. Until then, on a Compose or SwiftUI project, load only the foundation + context layers + design-audit, and proceed using your general knowledge plus the universal motion-principles. The orchestrator can still write good code; it just won't have the deep-dive references yet.
```

- [ ] **Step 7: Extend the AUDIT checklist**

Find the AUDIT section (`### 7. AUDIT - Verification before delivery`). Replace its contents with:

```markdown
Before delivering, run the checks matching the detected stack.

**All stacks:**
- [ ] Reduced motion respected (CSS `prefers-reduced-motion`, SwiftUI `accessibilityReduceMotion`, or Compose `LocalAccessibilityManager.isReduceTransitions`).
- [ ] Exit animations present (no abrupt vanishings).
- [ ] No layout-property animations (animate transform / opacity / graphicsLayer instead).
- [ ] Focus visible on interactive elements.
- [ ] Interactive elements have all relevant states (default, hover/press, focus, active, disabled).
- [ ] Colors and spacing consistent with detected design tokens.

**Web:**
- [ ] No forced reflow, `will-change` used sparingly.
- [ ] 60fps target verified via Chrome DevTools Performance panel.
- [ ] No clickable divs without role/button.
- [ ] `aria-hidden` on purely decorative animations.

**Compose:**
- [ ] Recomposition counts verified (Layout Inspector / `Modifier.recomposeHighlighter`).
- [ ] No animations on `width`/`height` (use `Modifier.graphicsLayer { translationX/Y, scaleX/Y }`).
- [ ] `Modifier.semantics` set on custom interactive components.
- [ ] Frame timing OK on a mid-range device (Pixel 4a baseline) via Macrobenchmark.

**SwiftUI:**
- [ ] No `body` recomputed on irrelevant state changes (use `@StateObject`, `@ObservableObject` correctly).
- [ ] Hitches Instrument shows no dropped frames during animation.
- [ ] `.accessibilityLabel` / `.accessibilityHint` on all interactive views.
- [ ] Tested with Reduce Motion ON and Dynamic Type at 200%.

**macOS-specific (in addition to SwiftUI):**
- [ ] Hover states present on every interactive element.
- [ ] Keyboard shortcuts (`⌘N`, `⌘W`, `⌘F`, etc.) bound to primary actions.
- [ ] Multi-window state shared coherently if applicable.
- [ ] Focus rings visible on keyboard navigation (no `outline: none` without alternative).
```

- [ ] **Step 8: Validate**

```bash
python3 -c "
import yaml
with open('skills/creative-excellence/SKILL.md') as f:
    parts = f.read().split('---', 2)
fm = yaml.safe_load(parts[1])
assert fm['name'] == 'creative-excellence'
print('OK')
"
# Note: existing file already contains em-dashes; we don't break that constraint here, but DO NOT add new ones.
# Count em-dashes only in the new lines you wrote (manual review):
git diff skills/creative-excellence/SKILL.md | grep '^+' | grep -c '-' | grep -q '^0$' && echo "OK no em-dash in new content"
```

- [ ] **Step 9: Commit**

```bash
git add skills/creative-excellence/SKILL.md
git commit -m "feat(skills): extend creative-excellence orchestrator for Android/iOS/macOS (SCAN, LOAD layered, cross-platform IRON RULES, THESIS examples, AUDIT per stack)"
```

---

## Task 10: Modify `design-excellence/SKILL.md` (orchestrator) - same extensions + stack-aware MASTER.md

**Files:**
- Modify: `skills/design-excellence/SKILL.md`

This task mirrors Task 9 for the second orchestrator, plus an additional change for stack-aware MASTER.md generation.

- [ ] **Step 1: Read the current file**

```bash
cat skills/design-excellence/SKILL.md
```

- [ ] **Step 2: Apply the same SCAN, IRON RULES, THESIS examples, LOAD, AUDIT changes as Task 9**

Repeat steps 2-7 of Task 9 verbatim on `skills/design-excellence/SKILL.md`. The sections have the same structure and the same content applies.

(IRON RULES in design-excellence has 8 rules; the React/GSAP-specific ones are still rules 6-7 in design-excellence's numbering. Adjust the rule numbers but keep the rewording from Task 9.)

- [ ] **Step 3: Adapt the "Generate design system" / MASTER.md generation step to be stack-aware**

design-excellence has a phase that generates a MASTER.md design system file. Currently it generates web-only tokens (CSS hex, `cubic-bezier`, `rem`). Find this phase (likely Phase 2 or Phase 3 in the design-excellence pipeline labeled "Define visual + interaction thesis" or "Generate design system").

Add this dispatch logic at the start of the MASTER.md generation step:

```markdown
**MASTER.md format depends on the detected stack:**

- **Web stack detected**: generate Tailwind config / CSS variables (existing format). Tokens in CSS hex, `cubic-bezier(...)` easings, `rem` spacing. Output paired with `tailwind.config.js` extension or `:root { --token: ... }` CSS.
- **Android Compose stack detected**: generate Kotlin design tokens. Output `Theme.kt`, `Color.kt`, `Type.kt`, `Shapes.kt`, `Motion.kt` referenced from MASTER.md. Color tokens in `Color(0xFF...)`, typography in `TextStyle`, shapes in `RoundedCornerShape`, motion in `MotionScheme` (M3 Expressive when scope is hero / impactful). Spacing in `dp`.
- **SwiftUI stack detected (iOS / macOS / multi-target)**: generate Swift extensions. Output `Color+App.swift`, `Font+App.swift`, `Animation+App.swift`, `Shape+App.swift`. Color tokens via `Color("AssetName")` referencing the asset catalog (or `Color(red:green:blue:)` if no catalog), typography via `Font.system(...)` or `.custom(...)`, animations via `.spring(...)` / `.snappy` / `.bouncy` named presets. Spacing in `CGFloat` constants.
- **Compose Multiplatform stack detected**: generate Kotlin tokens in `commonMain` with `expect/actual` for fonts and platform-specific colors. Same structure as Android Compose, plus a section in MASTER.md describing per-platform deviations.

The MASTER.md document itself remains a single canonical source-of-truth file. The generated *code* files (Theme.kt / Color+App.swift / etc.) are children of MASTER.md and reference it.
```

If the detected stack is multi-stack (e.g., a project with both web admin and a native mobile app), generate a MASTER.md that includes BOTH formats with clearly delimited sections.

- [ ] **Step 4: Validate**

```bash
python3 -c "
import yaml
with open('skills/design-excellence/SKILL.md') as f:
    parts = f.read().split('---', 2)
fm = yaml.safe_load(parts[1])
assert fm['name'] == 'design-excellence'
print('OK')
"
git diff skills/design-excellence/SKILL.md | grep '^+' | grep -c '-' | grep -q '^0$' && echo "OK no em-dash in new content"
```

- [ ] **Step 5: Commit**

```bash
git add skills/design-excellence/SKILL.md
git commit -m "feat(skills): extend design-excellence orchestrator + stack-aware MASTER.md generation (Compose Theme.kt / SwiftUI extensions)"
```

---

## Task 11: Smoke-test the packaging script on the new sub-skills

**Files:**
- Read-only check, no file modifications.

- [ ] **Step 1: Run the packaging script**

```bash
./package-for-claude-ai.sh
```

Expected: the script runs without errors, generates ZIPs in `dist/` (or wherever the script outputs).

- [ ] **Step 2: Verify the new sub-skills are in the output**

```bash
ls dist/*.zip 2>/dev/null | grep -E 'mobile-principles|desktop-principles' && echo "OK: new sub-skills packaged"
```

Expected: both `mobile-principles.zip` and `desktop-principles.zip` are listed.

- [ ] **Step 3: Verify the all-in-one ZIP contains the new sub-skills**

```bash
unzip -l dist/creative-excellence-all.zip 2>/dev/null | grep -E 'mobile-principles|desktop-principles' && echo "OK: all-in-one contains new sub-skills"
```

Expected: paths like `_creative/mobile-principles/SKILL.md` and `_creative/desktop-principles/SKILL.md` appear in the listing.

- [ ] **Step 4: Verify each new ZIP has valid frontmatter**

```bash
for skill in mobile-principles desktop-principles; do
  unzip -p dist/${skill}.zip ${skill}/SKILL.md 2>/dev/null | python3 -c "
import sys, yaml
parts = sys.stdin.read().split('---', 2)
fm = yaml.safe_load(parts[1])
assert 'name' in fm and 'description' in fm
print('OK:', fm['name'])
"
done
```

Expected: `OK: mobile-principles` and `OK: desktop-principles` printed.

- [ ] **Step 5: No commit (verification only).**

If any step fails, the corresponding earlier task has a bug. Go fix it, recommit, then rerun this task.

---

## Task 12: Smoke-test SCAN detection on a fixture project

**Files:**
- Read-only checks. Optionally creates `/tmp/fixture-*` directories for test projects (not committed).

- [ ] **Step 1: Test SCAN on a Compose project fixture**

```bash
mkdir -p /tmp/fixture-compose && cd /tmp/fixture-compose
cat > build.gradle.kts <<'EOF'
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
dependencies {
    implementation("androidx.compose.ui:ui:1.7.0")
    implementation("androidx.compose.material3:material3:1.3.0")
}
EOF

# Run the SCAN bash from the orchestrator (manually)
ls build.gradle.kts && grep -rE 'androidx\.compose' build.gradle*
```

Expected: shows `androidx.compose` in the grep output. The orchestrator's SCAN should map this to `android-compose`.

- [ ] **Step 2: Test SCAN on a SwiftUI iOS project fixture**

```bash
mkdir -p /tmp/fixture-swiftui-ios && cd /tmp/fixture-swiftui-ios
cat > Package.swift <<'EOF'
// swift-tools-version:5.9
import PackageDescription
let package = Package(
    name: "MyApp",
    platforms: [.iOS(.v17)],
    products: [.executable(name: "MyApp", targets: ["MyApp"])]
)
EOF
mkdir -p Sources/MyApp
cat > Sources/MyApp/App.swift <<'EOF'
import SwiftUI

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
    }
}
struct ContentView: View {
    var body: some View { Text("Hello") }
}
EOF

ls Package.swift && grep -E '\.iOS\(' Package.swift
grep -lE 'import SwiftUI|@main.*App' --include="*.swift" -r .
```

Expected: `Package.swift` listed, `.iOS(.v17)` matched, swift file with SwiftUI import detected. Maps to `swiftui-ios`.

- [ ] **Step 3: Test SCAN on a CMP project fixture**

```bash
mkdir -p /tmp/fixture-cmp && cd /tmp/fixture-cmp
cat > build.gradle.kts <<'EOF'
plugins {
    kotlin("multiplatform") version "1.9.0"
    id("org.jetbrains.compose") version "1.6.0"
}
kotlin {
    androidTarget()
    iosX64()
    iosArm64()
}
EOF

ls build.gradle.kts && grep -rE 'org\.jetbrains\.compose|kotlin\("multiplatform"\)' build.gradle*
```

Expected: both patterns matched. Maps to `compose-multiplatform`.

- [ ] **Step 4: No commit (verification only).**

If any fixture fails detection, the SCAN regex in Task 9 / 10 has a bug. Fix and recommit.

---

## Task 13: Final cross-link sanity check

**Files:**
- Read-only verification across all modified files.

- [ ] **Step 1: Verify all internal `../<skill>/SKILL.md` references resolve**

```bash
# List all referenced sub-skills and check each exists
grep -rohE '\.\./[a-z\-]+/SKILL\.md' skills/ | sort -u | while read ref; do
  base=$(echo "$ref" | sed 's|\.\./||; s|/SKILL\.md||')
  if [ -f "skills/_creative/$base/SKILL.md" ]; then
    echo "OK: $ref -> skills/_creative/$base/SKILL.md"
  else
    echo "MISSING: $ref (target: skills/_creative/$base/SKILL.md)"
  fi
done
```

Expected: most references resolve. The references to `compose-motion`, `compose-graphics`, `compose-multiplatform`, `swiftui-motion`, `swiftui-graphics` will show as MISSING - this is expected (they are added in Phases 2-4). Note them but do not fail the task on them. Add a comment in the orchestrator LOAD section if not already there: "Phase 1 lays the foundation; Compose/SwiftUI specific sub-skills land in Phases 2-4."

The references that MUST resolve:
- `motion-principles/SKILL.md`
- `mobile-principles/SKILL.md` (created in Task 1)
- `desktop-principles/SKILL.md` (created in Task 4)
- `design-audit/SKILL.md`
- `ui-ux-pro-max/SKILL.md`
- `gsap/SKILL.md`
- `framer-motion/SKILL.md`
- `css-native/SKILL.md`
- `threejs-r3f/SKILL.md`
- `canvas-generative/SKILL.md`

If any of those are MISSING, fix the broken reference in the file that mentions it.

- [ ] **Step 2: No commit (verification only).**

---

## Task 14: Phase 1 acceptance check

This task verifies all the spec's "Phase 1 done when" criteria are met.

- [ ] **Step 1: Verify zero web regression**

The web sub-skills (`gsap`, `framer-motion`, `css-native`, `threejs-r3f`, `canvas-generative`) must not have been modified. Check via:

```bash
git log --since="$(git log -1 --format=%cs HEAD~14)" --oneline -- skills/_creative/gsap skills/_creative/framer-motion skills/_creative/css-native skills/_creative/threejs-r3f skills/_creative/canvas-generative
```

Expected: empty output (no commits touched these directories during Phase 1).

- [ ] **Step 2: Verify foundation files created**

```bash
test -f skills/_creative/mobile-principles/SKILL.md \
  && test -f skills/_creative/mobile-principles/references/gestures-deep.md \
  && test -f skills/_creative/mobile-principles/references/accessibility-mobile.md \
  && test -f skills/_creative/desktop-principles/SKILL.md \
  && test -f skills/_creative/desktop-principles/references/keyboard-patterns.md \
  && test -f skills/_creative/desktop-principles/references/multi-window.md \
  && echo "OK: all foundation files present"
```

Expected: `OK: all foundation files present`.

- [ ] **Step 3: Verify orchestrators have the new SCAN cases**

```bash
grep -l 'androidx.compose' skills/creative-excellence/SKILL.md skills/design-excellence/SKILL.md
grep -l 'org.jetbrains.compose' skills/creative-excellence/SKILL.md skills/design-excellence/SKILL.md
grep -l 'Package.swift' skills/creative-excellence/SKILL.md skills/design-excellence/SKILL.md
```

Expected: all 3 commands list both files.

- [ ] **Step 4: Verify orchestrators reference the new layers**

```bash
grep -l 'mobile-principles' skills/creative-excellence/SKILL.md skills/design-excellence/SKILL.md
grep -l 'desktop-principles' skills/creative-excellence/SKILL.md skills/design-excellence/SKILL.md
```

Expected: both files listed in both commands.

- [ ] **Step 5: Verify motion-principles and design-audit have cross-platform sections**

```bash
grep -l 'accessibilityReduceMotion' skills/_creative/motion-principles/SKILL.md
grep -l 'LocalAccessibilityManager' skills/_creative/motion-principles/SKILL.md
grep -l 'Layout Inspector\|Macrobenchmark' skills/_creative/design-audit/SKILL.md
grep -l 'Instruments\|Hitches' skills/_creative/design-audit/SKILL.md
```

Expected: all 4 commands return their respective file paths.

- [ ] **Step 6: Verify packaging produces 12 ZIPs (10 existing + 2 new) plus 1 all-in-one**

```bash
./package-for-claude-ai.sh && ls dist/*.zip | wc -l
```

Expected: at least 12 ZIPs (10 existing sub-skills + mobile-principles + desktop-principles + 2 orchestrators + 1 all-in-one = 13 total).

Existing skills count check:
- creative-excellence orchestrator
- design-excellence orchestrator
- motion-principles
- gsap
- framer-motion
- css-native
- threejs-r3f
- canvas-generative
- design-audit
- ui-ux-pro-max
- mobile-principles (new)
- desktop-principles (new)
- creative-excellence-all (combined)

= 13 ZIPs total expected.

- [ ] **Step 7: Final commit (if anything was fixed during verification)**

If verification surfaced a fix (e.g., missing reference, incomplete frontmatter), it should already be committed by the relevant earlier task. If you fixed a small issue inline:

```bash
git add -p
git commit -m "fix(skills): <description of the fix>"
```

If everything is clean, no commit needed.

- [ ] **Step 8: Tag Phase 1 milestone**

```bash
git tag -a phase1-foundations -m "Phase 1 of v2.0 mobile creative excellence: foundations cross-platform complete"
```

This tag is local; push it explicitly if/when ready (`git push origin phase1-foundations`). Do not push automatically.

---

## Self-Review Notes

(Filled out after writing the plan.)

**Spec coverage:**
- Phase 1 scope per spec section 11 covers: motion-principles modifs, mobile-principles creation, desktop-principles creation, design-audit modifs, orchestrator modifs (SCAN/LOAD/IronRules/Thesis examples/DISCOVER/AUDIT), MASTER.md stack-aware. All covered by Tasks 1-10.
- Spec section 12 (criteria for Phase 1 done) covered by Task 14.
- Spec section 5 (SCAN extended) covered by Tasks 9-10 + Task 12.
- Spec section 6 (LOAD layered) covered by Tasks 9-10.
- Spec section 8.1 (motion-principles modifs) covered by Task 7.
- Spec section 8.2 (design-audit modifs) covered by Task 8.
- Spec section 8.4 (design-excellence MASTER.md stack-aware) covered by Task 10 step 3.
- Spec section 9 (legacy bridge in DISCOVER) covered by Task 9 step 3 + Task 10 step 2.

**Type/name consistency:**
- Sub-skills referenced consistently: `mobile-principles`, `desktop-principles`, `compose-motion`, `compose-graphics`, `compose-multiplatform`, `swiftui-motion`, `swiftui-graphics` (the latter five are forward references to Phases 2-4).
- API names verified: `accessibilityReduceMotion` (SwiftUI), `LocalAccessibilityManager` (Compose), `UIAccessibility.isReduceMotionEnabled` (UIKit), `prefers-reduced-motion` (CSS).
- File paths consistent: `skills/_creative/<sub-skill>/SKILL.md` and `skills/<orchestrator>/SKILL.md`.

**No placeholders:**
- All sections have explicit content. Where SKILL.md content is described (Tasks 1-6), the structure is enumerated section-by-section with type of content, sources, and example wording.
- All commit messages are concrete.
- All bash commands are runnable as written.
- Code examples (Compose / SwiftUI / CSS) are syntactically complete enough to be transcribed.

**Known forward references (not bugs):**
- `compose-motion`, `compose-graphics`, `compose-multiplatform`, `swiftui-motion`, `swiftui-graphics` are referenced in `motion-principles` Quick Reference table and in the orchestrator LOAD tables, but are not created until Phases 2-4. Task 13 step 1 explicitly notes this and instructs not to fail on these. Phase 5 will add a CHANGELOG entry making clear that these references resolve only after each successive phase ships.
