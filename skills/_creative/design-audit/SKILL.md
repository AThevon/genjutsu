---
name: design-audit
description: "Design audit checklist - motion gaps, accessibility, color consistency, responsive, performance."
---

# Design Audit

> The final checkpoint. Loaded by `/design-excellence` at the end of the pipeline.
> Scans the codebase for motion gaps, a11y violations, perf issues, and inconsistencies.

---

## Motion Gap Analysis

Run these greps against the project to detect missing animations.

### Conditional renders without AnimatePresence

```bash
grep -rn '{.*&&\s*<\|{.*?\s*:\s*<\|{.*ternary.*<' --include='*.tsx' --include='*.jsx' src/ | grep -v 'AnimatePresence'
```

Look for: `{show && <Component />}` or ternary renders without a wrapping `<AnimatePresence>`. Every conditional mount/unmount needs exit animation support.

### Hover states without transition

```bash
grep -rn ':hover' --include='*.css' --include='*.scss' --include='*.module.css' src/ | grep -vE 'transition|animation'
```

Every `:hover` rule must have a corresponding `transition` on the base selector. Instant state flips feel broken.

### Dynamic lists without stagger

```bash
grep -rn '\.map(' --include='*.tsx' --include='*.jsx' src/ | grep -vE 'stagger|delay.*index|variants|transition.*delay'
```

Lists rendered via `.map()` should stagger their entrance. Simultaneous pop-in looks cheap.

### Style changes without transition

```bash
grep -rn 'style={{' --include='*.tsx' --include='*.jsx' src/ | grep -vE 'transition|transform|opacity'
```

Inline style changes (e.g., dynamic background, color) need a CSS transition or motion wrapper.

### Entries without corresponding exits

```bash
grep -rn 'initial=' --include='*.tsx' --include='*.jsx' src/ | grep -v 'exit='
```

Every Framer Motion `initial` + `animate` should have an `exit` prop when inside `AnimatePresence`.

---

## Accessibility Audit

### prefers-reduced-motion -- MANDATORY

```bash
grep -rn 'prefers-reduced-motion' --include='*.css' --include='*.scss' --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' src/
```

**If zero results: Critical violation.** Every project with animation MUST have at least one global `prefers-reduced-motion` handler (CSS media query or JS hook). Check `motion-principles/SKILL.md` for implementation patterns.

### Contrast ratio 4.5:1

- Use browser DevTools (Inspect > color swatch > contrast ratio)
- Run `npx pa11y <url>` or Lighthouse accessibility audit
- Check animated text at mid-transition -- fading text must remain readable at every opacity above 0.4

### Focus visible on all interactives

```bash
grep -rn 'outline:\s*none\|outline:\s*0' --include='*.css' --include='*.scss' --include='*.module.css' src/
```

Any `outline: none` MUST be paired with a custom `:focus-visible` style. Removing focus rings without replacement is a WCAG failure.

### Semantic HTML -- no clickable divs

```bash
grep -rn 'onClick' --include='*.tsx' --include='*.jsx' src/ | grep -E '<div|<span' | grep -v 'role='
```

Every `<div onClick>` or `<span onClick>` must either be a `<button>`, an `<a>`, or have `role="button"` + `tabIndex` + `onKeyDown`.

### ARIA on decorative animations

```bash
grep -rn '<motion\.\|<animated\.\|<Lottie\|<Canvas' --include='*.tsx' --include='*.jsx' src/ | grep -v 'aria-hidden'
```

Purely decorative animations (background particles, ambient motion, Lottie illustrations) must have `aria-hidden="true"` to avoid polluting screen readers.

---

## Performance Audit

### Layout thrashing -- animating layout properties

```bash
grep -rn 'transition.*\(width\|height\|top\|left\|right\|bottom\|margin\|padding\)' --include='*.css' --include='*.scss' --include='*.module.css' src/
```

Animating layout properties triggers reflow every frame. Replace with `transform: translate/scale` and `opacity`.

### Excessive paint triggers

```bash
grep -rn 'will-change' --include='*.css' --include='*.scss' --include='*.module.css' src/
```

`will-change` should be rare and scoped. If more than ~5 elements use it permanently, the GPU memory cost outweighs the benefit. Apply it dynamically (add on hover/focus, remove on animation end).

### Animation library bundle cost

Check actual impact:

```bash
npx source-map-explorer dist/**/*.js 2>/dev/null || npx vite-bundle-visualizer 2>/dev/null
```

Reference sizes (gzipped): framer-motion ~30KB, GSAP ~25KB, popmotion ~5KB, CSS-only = 0KB. If the project only uses fade+slide, a 30KB lib is overkill.

### requestAnimationFrame vs setTimeout

```bash
grep -rn 'setTimeout\|setInterval' --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' src/ | grep -iE 'anim\|motion\|scroll\|position\|style\|transform'
```

Animation loops must use `requestAnimationFrame`. `setTimeout`/`setInterval` causes frame drops and doesn't pause in background tabs.

---

## Consistency Audit

### Duration consistency

```bash
grep -rnoE 'duration[:"'\''= ]+[0-9.]+' --include='*.tsx' --include='*.jsx' --include='*.ts' --include='*.css' --include='*.scss' src/ | sort -t: -k3 | uniq -c -f2 | sort -rn
```

A well-designed project uses 3-5 distinct durations max (e.g., 0.15, 0.25, 0.35, 0.5). If you see 15 different values, extract them into a motion tokens file.

### Easing consistency

```bash
grep -rnoE 'ease[A-Za-z]*|cubic-bezier\([^)]+\)|spring\([^)]*\)' --include='*.tsx' --include='*.jsx' --include='*.ts' --include='*.css' --include='*.scss' src/ | sort -t: -k3 | uniq -c -f2 | sort -rn
```

Same rule: 3-5 named easings max. Random `cubic-bezier` values scattered across files = visual inconsistency.

### Symmetric enter/exit

Scan for motion components and verify that:
- Enter duration >= exit duration (never the reverse)
- Enter uses `ease-out`, exit uses `ease-in`
- Enter has full choreography (translate + opacity + scale), exit is simpler (opacity only or opacity + slight scale)

```bash
grep -A5 'exit=' --include='*.tsx' --include='*.jsx' -rn src/
```

Compare `animate` and `exit` props side by side. Asymmetric timing (fast exit, slow enter) is correct. The reverse is wrong.

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
