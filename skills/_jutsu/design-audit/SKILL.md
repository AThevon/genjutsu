---
name: design-audit
description: "Design audit checklist - motion gaps, accessibility, color consistency, responsive, performance."
---

> **Version-sensitive.** Every API name, SDK gate and browser-support claim below was
> verified on **2026-09-08** against primary sources. What against, and when, is in
> `_jutsu/VERSIONS.md`. If that date is old, re-verify before acting on a version number.

# Design Audit

> The final checkpoint. Loaded by `/genjutsu:paint` at the end of the pipeline.
> Scans the codebase for motion gaps, a11y violations, perf issues, and inconsistencies.

---

## How these greps are run

**Define these two helpers first, in the same Bash call as the greps below.**

Every grep in this file used to end in `src/`. A default Next.js app-router or Nuxt 3
project has no `src/` at all, so those greps matched nothing, and the pipeline read
"no findings" as a passing gate immediately before delivery. The audit reported a clean
bill of health on code it had never read.

```bash
# Recursion, root and noise directories in one place. The root is the project, not a
# guessed subdirectory; --include already narrows by file type and the excludes carry
# the rest. Note the arguments are passed as "$@", never through an unquoted variable:
# zsh does not word-split those, so the usual $SRC / $EXCL trick silently collapses
# into a single bogus argument.
gj() {
  grep -rn \
    --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.next \
    --exclude-dir=.nuxt --exclude-dir=.output --exclude-dir=.svelte-kit \
    --exclude-dir=.astro --exclude-dir=dist --exclude-dir=build --exclude-dir=out \
    --exclude-dir=coverage --exclude-dir=vendor --exclude-dir=.venv \
    "$@" .
}

# Same, for the inventory greps: -h drops the filename and -o prints only the match,
# so the output can be counted.
gjo() {
  grep -rhoE \
    --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.next \
    --exclude-dir=.nuxt --exclude-dir=.output --exclude-dir=.svelte-kit \
    --exclude-dir=.astro --exclude-dir=dist --exclude-dir=build --exclude-dir=out \
    --exclude-dir=coverage --exclude-dir=vendor --exclude-dir=.venv \
    "$@" .
}
```

If the project is a monorepo and the scan is too broad, narrow it by appending a path:
`gj ':hover' --include='*.css' packages/web` works, because the trailing `.` is only a
default and grep accepts several roots.

---

## Motion Gap Analysis

Run these greps against the project to detect missing animations. Single-file component
formats (`.vue`, `.svelte`, `.astro`) carry their styles inline, so they are included
wherever a CSS or JSX pattern is being looked for.

### Conditional renders without AnimatePresence

```bash
gj '{.*&&\s*<\|{.*?\s*:\s*<\|{.*ternary.*<' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.tsx' --include='*.jsx' | grep -v 'AnimatePresence'
```

Look for: `{show && <Component />}` or ternary renders without a wrapping `<AnimatePresence>`. Every conditional mount/unmount needs exit animation support.

### Hover states without transition

```bash
gj ':hover' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.css' --include='*.scss' --include='*.module.css' | grep -vE 'transition|animation'
```

Every `:hover` rule must have a corresponding `transition` on the base selector. Instant state flips feel broken.

### Dynamic lists without stagger

```bash
gj '\.map(' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.tsx' --include='*.jsx' | grep -vE 'stagger|delay.*index|variants|transition.*delay'
```

Lists rendered via `.map()` should stagger their entrance. Simultaneous pop-in looks cheap.

### Style changes without transition

```bash
gj 'style={{' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.tsx' --include='*.jsx' | grep -vE 'transition|transform|opacity'
```

Inline style changes (e.g., dynamic background, color) need a CSS transition or motion wrapper.

### Entries without corresponding exits

```bash
gj 'initial=' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.tsx' --include='*.jsx' | grep -v 'exit='
```

Every Framer Motion `initial` + `animate` should have an `exit` prop when inside `AnimatePresence`.

---

## Accessibility Audit

### Reduced motion - MANDATORY

A project with animation MUST have at least one global handler matching its stack. Run all 3 greps:

```bash
# Web
gj 'prefers-reduced-motion' --include='*.css' --include='*.scss' --include='*.ts' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.tsx' --include='*.js' --include='*.jsx' 2>/dev/null

# SwiftUI / UIKit
grep -rn 'accessibilityReduceMotion\|isReduceMotionEnabled\|reduceMotionStatusDidChangeNotification' --include='*.swift' . 2>/dev/null

# Compose
grep -rn 'LocalAccessibilityManager\|isReduceTransitions\|TRANSITION_ANIMATION_SCALE\|ANIMATOR_DURATION_SCALE\|areAnimatorsEnabled' --include='*.kt' . 2>/dev/null
```

**Zero results across all 3 in an animated project = critical violation.** At least one handler must exist somewhere. Cross-reference `motion-principles/SKILL.md` for canonical implementations per stack.

### Contrast ratio 4.5:1

- Use browser DevTools (Inspect > color swatch > contrast ratio)
- Run `npx pa11y <url>` or Lighthouse accessibility audit
- Check animated text at mid-transition -- fading text must remain readable at every opacity above 0.4

### Focus visible on all interactives

```bash
gj 'outline:\s*none\|outline:\s*0' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.css' --include='*.scss' --include='*.module.css'
```

Any `outline: none` MUST be paired with a custom `:focus-visible` style. Removing focus rings without replacement is a WCAG failure.

### Semantic HTML -- no clickable divs

```bash
gj 'onClick' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.tsx' --include='*.jsx' | grep -E '<div|<span' | grep -v 'role='
```

Every `<div onClick>` or `<span onClick>` must either be a `<button>`, an `<a>`, or have `role="button"` + `tabIndex` + `onKeyDown`.

### ARIA on decorative animations

```bash
gj '<motion\.\|<animated\.\|<Lottie\|<Canvas' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.tsx' --include='*.jsx' | grep -v 'aria-hidden'
```

Purely decorative animations (background particles, ambient motion, Lottie illustrations) must have `aria-hidden="true"` to avoid polluting screen readers.

---

## Performance Audit

### Layout thrashing -- animating layout properties

```bash
gj 'transition.*\(width\|height\|top\|left\|right\|bottom\|margin\|padding\)' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.css' --include='*.scss' --include='*.module.css'
```

Animating layout properties triggers reflow every frame. Replace with `transform: translate/scale` and `opacity`.

### Excessive paint triggers

```bash
gj 'will-change' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.css' --include='*.scss' --include='*.module.css'
```

`will-change` should be rare and scoped. If more than ~5 elements use it permanently, the GPU memory cost outweighs the benefit. Apply it dynamically (add on hover/focus, remove on animation end).

### Animation library bundle cost

Check actual impact:

```bash
npx source-map-explorer dist/**/*.js 2>/dev/null || npx vite-bundle-visualizer 2>/dev/null
```

Reference sizes (gzipped): framer-motion ~30KB, GSAP ~25KB, popmotion ~5KB, CSS-only = 0KB. If the project only uses fade+slide, a 30KB lib is overkill.

On mobile native, the APK / IPA size matters. A third-party animation library adds typically 500KB-2MB:

| Library | Size impact (uncompressed) |
|---|---|
| Lottie (iOS) | ~600KB |
| Lottie (Android) | ~900KB |
| Rive (iOS) | ~1.5MB |
| Rive (Android) | ~2MB |
| Native Compose / SwiftUI animations | 0KB (built-in) |

If the project only uses fades, slides, and springs, native APIs (Compose `animate*AsState` + spring, SwiftUI `withAnimation`) are sufficient. Justify a Lottie / Rive dependency only for genuinely complex pre-designed animations (e.g., onboarding illustrations).

### requestAnimationFrame vs setTimeout

```bash
gj 'setTimeout\|setInterval' --include='*.ts' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.tsx' --include='*.js' --include='*.jsx' | grep -iE 'anim\|motion\|scroll\|position\|style\|transform'
```

Animation loops must use `requestAnimationFrame`. `setTimeout`/`setInterval` causes frame drops and doesn't pause in background tabs.

---

## Consistency Audit

### Duration consistency

```bash
gjo 'duration[:"'\''= ]+[0-9.]+' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.tsx' --include='*.jsx' --include='*.ts' --include='*.css' --include='*.scss' \
  | sed -E 's/^duration[:"'\''= ]+//' | tr -d ' ' | sort -n | uniq -c | sort -rn
```

A well-designed project uses 3-5 distinct durations max (e.g., 0.15, 0.25, 0.35, 0.5). If you see 15 different values, extract them into a motion tokens file.

### Easing inventory

Run all 3 greps to inventory easing values across the codebase:

```bash
# Web (CSS / JS / TSX)
gjo 'ease[A-Za-z]*|cubic-bezier\([^)]+\)|spring\([^)]*\)' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.tsx' --include='*.jsx' --include='*.ts' --include='*.css' --include='*.scss' 2>/dev/null

# SwiftUI
grep -rnoE '\.spring\([^)]*\)|\.snappy|\.bouncy|\.smooth|\.linear\(|\.easeIn|\.easeOut|\.interpolatingSpring' --include='*.swift' . 2>/dev/null

# Compose
grep -rnoE 'spring\([^)]*\)|tween\([^)]*\)|FastOutSlowInEasing|LinearOutSlowInEasing|FastOutLinearInEasing|CubicBezierEasing' --include='*.kt' . 2>/dev/null
```

Same rule across all stacks: 3-5 named easings max in the design system. Random values scattered across files = visual inconsistency. If the codebase has 12 different `cubic-bezier(...)` values or 8 custom `spring(response:dampingFraction:)` configurations, that's a design-system violation, fix it by centralizing into named tokens.

### Symmetric enter/exit

Scan for motion components and verify that:
- Enter duration >= exit duration (never the reverse)
- Enter uses `ease-out`, exit uses `ease-in`
- Enter has full choreography (translate + opacity + scale), exit is simpler (opacity only or opacity + slight scale)

```bash
gj -A5 'exit=' --include='*.vue' --include='*.svelte' --include='*.astro' --include='*.tsx' --include='*.jsx'
```

Compare `animate` and `exit` props side by side. Asymmetric timing (fast exit, slow enter) is correct. The reverse is wrong.

---

## Stack-specific audit

Pick the subsection matching the project stack.

### Compose (Android / Multiplatform)
- [ ] Run **Layout Inspector** (Android Studio): inspect recompositions, identify components recomposing on every state change.
- [ ] Run **Macrobenchmark** (`androidx.benchmark.macro`): measure frame timing on a real device under representative scrolling / animation load. Target: <16.67ms per frame at 60fps, <8.33ms at 120fps.
- [ ] Inspect **recomposition counts**: Layout Inspector > Component Tree > View Options > **Show Recomposition Counts** (API 29+, Compose 1.2+). Reset the counters before each interaction so the numbers mean something. There is no `Modifier.recomposeHighlighter` in androidx - it is a sample you vendor into a debug source set.
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

---

## Output Format

Structure findings by severity:

### Critical (must fix before ship)
- Missing `prefers-reduced-motion` handling
- Clickable divs without keyboard support
- `outline: none` without `:focus-visible` replacement
- Animating layout properties (width/height/top/left)

### Important (fix in current sprint)
- Conditional renders without `AnimatePresence`
- Hover states without transition
- Missing `aria-hidden` on decorative animations
- `setTimeout` used for animation loops
- Inconsistent durations (>8 unique values)

### Nice-to-have (backlog)
- Lists without stagger animation
- Inline styles without transition
- Excessive `will-change` usage
- Asymmetric enter/exit (wrong direction)
- Animation library oversized for actual usage
