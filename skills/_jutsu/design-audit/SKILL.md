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

## The static pass

**Run the script. Do not hand-write the greps.**

```bash
python3 "$SKILL_BASE/design-audit/scripts/audit.py" .
```

Add `--json` if you want to post-process it. `--only <check-id>` runs one check.

It reports three things, and the distinction between the last two is the whole reason it
exists:

- **findings** - the check ran and found something. Every finding carries `file:line` and the
  matched text, so you report the evidence rather than a verdict.
- **clean** - the check ran against real files and found nothing.
- **not applicable** - there were no files of that type, so the check did not run. **Report
  these as not checked. Never as passing.**

These greps used to live in this file, anchored on `src/`. A default Next.js app-router or
Nuxt 3 project has no `src/`, so they matched nothing, and the pipeline read the empty output as
a clean bill of health and said so to the user right before delivery. The script detects its
roots, skips `node_modules` and build output, covers `.vue` / `.svelte` / `.astro` alongside JSX
and CSS, and has a test per check asserting that the check can still fire.

**Contrast is not in the script.** Compute it yourself from the token values you emitted, and
report the pair with the ratio: `#831843 on #FDF2F8 = 9.4:1`. 4.5:1 for body text, 3:1 for large
text and UI boundaries. A swatch you looked at is not a measurement.

**If `python3` is unavailable**, say so in one line and fall back to reading the components you
touched, in this order: reduced-motion guard, exit animations, layout-property animations, focus
visibility, click handlers on non-interactive elements. Report it as a partial audit, and say
which checks you could not run.

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
