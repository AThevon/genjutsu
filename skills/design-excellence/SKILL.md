---
name: design-excellence
description: "Pipeline design d'exception — brainstorm direction artistique, design system, implémentation, audit. Pour construire un univers visuel complet."
allowed-tools: Bash, Read, Edit, Write, Grep, Glob, WebSearch, Agent
---

# Design Excellence — The Architect

> Build a complete visual universe. Brainstorm first, design system second, implement third, audit last.
> This is NOT a quick beautifier — it's a full design pipeline.

---

## /design-excellence vs /creative

| | `/creative` | `/design-excellence` |
|---|---|---|
| **Philosophy** | "Make this thing beautiful/wow" | "Build a visual universe from scratch" |
| **Entry point** | Adapts to existing code | Mandatory brainstorm, wipes design if existing |
| **Design system** | Optional, implicit | Required, generates MASTER.md |
| **Audit** | No final audit | Full design-audit at the end |
| **Scope** | One component/page/effect | Entire project visual identity |

`/design-excellence` calls the same sub-skills as `/creative` for implementation.

---

## Plugin Root Detection

```bash
PLUGIN_ROOT=$(find ~/.claude/plugins -path "*/creative-skills/skills" -type d | head -1 | sed 's|/skills$||')
```

All sub-skills live in `$PLUGIN_ROOT/skills/_creative/`.

---

## Pipeline

### Phase 1 — BRAINSTORM (mandatory, never skip)

Before writing a single line of code, ask and get answers for ALL of these:

1. **Product** — What is it? (app, landing page, portfolio, SaaS, e-commerce, blog, dashboard...)
2. **Audience** — Who uses it? (devs, designers, general public, enterprise, kids, luxury...)
3. **Visual keywords** — 3 to 5 adjectives that define the mood:
   - Examples: "minimal brutal dark", "playful warm organic", "luxury editorial clean", "cyberpunk neon dense"
4. **Visual references** — Sites, screenshots, mood boards, Dribbble/Behance links, anything visual
5. **Tech stack** — What's already in place? Or starting from scratch? (Next.js, Astro, Svelte, vanilla, etc.)

Do NOT proceed until all 5 answers are collected. If the user is vague on references, suggest 2-3 sites that match their keywords using WebSearch.

---

### Phase 2 — THESIS (define direction, get validation)

From the brainstorm answers, produce two theses:

#### Visual Thesis

A single sentence that captures the entire visual identity.

> Example: "Interface dark neo-brutalist avec typo monospace bold, accents fluo chartreuse, espaces genereux, composants aux bords bruts avec ombres decalees."

Must cover: color direction, typography spirit, spacing philosophy, component style.

#### Interaction Thesis

A single sentence that captures the motion and interaction language.

> Example: "Transitions rapides et seches (100-200ms), hover avec scale subtil (1.02), scroll-triggered reveals avec stagger, pas de bounce ni d'elastic — tout en ease-out sharp."

Must cover: timing range, hover behavior, scroll behavior, forbidden patterns.

**Wait for explicit user validation of BOTH theses before moving on.** Iterate if needed.

---

### Phase 3 — DESIGN SYSTEM

Load `_creative/ui-ux-pro-max` sub-skill:

```bash
cat "$PLUGIN_ROOT/skills/_creative/ui-ux-pro-max/SKILL.md"
```

Generate the complete design system based on both theses:

- **Color palette** — Primary, secondary, accent, neutrals, semantic (success/warning/error/info). Light + dark if needed.
- **Typography** — Font stack, size scale (fluid or fixed), weight usage, line-height rules.
- **Spacing** — Base unit, scale (4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px...).
- **Radii** — Border radius scale (none, sm, md, lg, full).
- **Shadows** — Elevation levels (0-4), consistent with visual thesis.
- **Base components** — Button, input, card, badge, link — styled per the theses.
- **Motion tokens** — Duration scale (fast/normal/slow), easing names, stagger delay.

#### MASTER.md

Create a `MASTER.md` at project root with the full design system. This file is the single source of truth. Every implementation decision references it.

#### MCP Tools (if available)

Check if these MCPs are connected and use them when available:
- **Stitch** — Generate mockups/wireframes
- **Nano Banana** — Generate visual assets (illustrations, icons, backgrounds)
- **21st.dev Magic** — Generate UI components from descriptions

If MCPs are not available, skip gracefully — the design system + code implementation is the core path.

---

### Phase 4 — IMPLEMENT

Load sub-skills based on tech stack and interaction thesis. Always load `motion-principles` first, then stack-specific skills:

```bash
# Always first
cat "$PLUGIN_ROOT/skills/_creative/motion-principles/SKILL.md"
# Then per stack: framer-motion, gsap, css-native, threejs-r3f, canvas-generative
cat "$PLUGIN_ROOT/skills/_creative/<skill>/SKILL.md"
```

Implementation rules:
- Work **page by page** or **component by component** — never try to do everything at once.
- Every color, font, spacing, shadow, radius MUST come from MASTER.md tokens. No magic numbers.
- Every animation MUST respect the interaction thesis (timing, easing, forbidden patterns).
- Apply the 5-state rule for interactive elements: **default, hover, focus, active, disabled**.
- Ask the user for validation after each major page/section before moving to the next.

---

### Phase 5 — AUDIT

Load `_creative/design-audit` sub-skill:

```bash
cat "$PLUGIN_ROOT/skills/_creative/design-audit/SKILL.md"
```

Run the full audit checklist:

#### Motion Gap Analysis
- Conditional renders without AnimatePresence
- Hover states without transition
- Dynamic lists without stagger
- Style changes without transition
- Entries without corresponding exits

#### Color & Contrast Consistency
- All interactive elements have 5 states: default, hover, focus, active, disabled
- Contrast ratio >= 4.5:1 for all text
- Color palette matches MASTER.md — no rogue hex values

#### Accessibility
- `prefers-reduced-motion` handler exists (critical)
- Focus visible on all interactives
- Semantic HTML — no clickable divs without role
- `aria-hidden` on decorative animations

#### Responsive (4 breakpoints)
375px (mobile) / 768px (tablet) / 1024px (small desktop) / 1440px (large desktop)

#### Performance
No layout property animations, `will-change` sparingly, `requestAnimationFrame` for custom loops.

Present findings grouped by severity: **Critical > Important > Nice-to-have**.

---

## Existing Project Protocol

When invoked on a project that already has design/styling:

1. Still run the full BRAINSTORM (Phase 1)
2. Acknowledge existing design, but the thesis overrides it
3. In Phase 4, **replace** existing design tokens/styles with the new design system
4. Preserve functionality and layout structure — only replace the visual layer

This is intentional: `/design-excellence` rebuilds the visual universe. To enhance what exists, use `/creative` instead.
