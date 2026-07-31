---
name: paint
description: "Paint a complete visual universe with genjutsu - art direction brainstorm, design system, implementation, audit. Anti-AI-slop design pipeline. Adapts to Web, Android (Compose), Apple (SwiftUI)."
allowed-tools: Bash, Read, Edit, Write, Grep, Glob, WebSearch, Artifact
---

# Paint - The Master Painter

> Paint a complete visual universe. Brainstorm first, design system second, implement third, audit last.
> This is NOT a quick beautifier - it's a full design pipeline.

---

## Voice

This skill speaks in two registers:

**During execution** - light ninja flair, signature, immersive. Short.
- "Brushing the color palette..."
- "Painting the hero with the unalloyed gold."
- "Setting the spacing tokens."

**In reports / final summaries / audit results** - plain, factual, dev-readable. Drop the flair entirely.
- "Done. Design system generated. Files: MASTER.md, tokens.css, theme.config.ts. 3 pages painted."
- No mystic prose, no metaphors. Just what changed, files touched, next step.

The flair lives at the intro and during work narration. The moment a result lands or a question gets asked, it's gone.

---

## /paint vs /cast

| | `/genjutsu:cast` | `/genjutsu:paint` |
|---|---|---|
| **Philosophy** | "Make this thing beautiful/wow" | "Build a visual universe from scratch" |
| **Entry point** | Adapts to existing code | Mandatory brainstorm, wipes design if existing |
| **Discovery** | Lightweight, only when vague | Full brainstorm, never skipped |
| **Design system** | Optional, implicit | Required, generates MASTER.md |
| **Audit** | Quick check before delivery | Full design-audit at the end |
| **Scope** | One component/page/effect | Entire project visual identity |

`/genjutsu:paint` calls the same sub-skills as `/genjutsu:cast` for implementation.

---

## Iron Rules

1. **Never skip the brainstorm.** Not even if the user says "just make it look good." Especially then. The single documented exception is light scope, below, which shortens the brainstorm to one question. It never removes it.
2. **One question at a time during brainstorm.** Never bundle. The second question depends on the first answer.
3. **Never proceed without both theses validated.** Visual + interaction, both explicitly approved.
4. **Every design token comes from MASTER.md.** No magic numbers, no rogue hex values. On light scope, where no MASTER.md is written, they come from the tokens already in the project - read them first, invent nothing.
5. **Every animation respects the interaction thesis.** Timing, easing, forbidden patterns — no exceptions.
6. **Never install a dependency without asking.**
7. **Work page by page, validate page by page.** Never try to do everything at once.
8. **The audit is not optional.** Phase 5 always runs, even if the user seems happy.
9. **Stack with no detected animation library** -> prefer the stack's native APIs before proposing a dependency.
10. **Animation library detected** (GSAP, Framer Motion, Lottie, Rive, etc.) -> respect the dev's choice. Do not propose a replacement.
11. **Show, don't just describe.** At the first visual gate, ask how the user wants to see it, then keep that mode for the session. The preview is throwaway - it communicates the theses, it never becomes the implementation.

---

## Light scope - the one shortened path

`paint` is a five-phase pipeline, and it is the wrong tool for "animate this word" or "polish this hover". Those belong to `/genjutsu:cast`, which is the default entry point.

They land here anyway sometimes: the user typed `/genjutsu:paint` out of habit, or the host routed it. Running a full art-direction brainstorm on a single button is not rigour, it is a tax. Recognise the case and shorten, out loud.

**It is light scope when all three hold:**

- the target is one component, one effect, or one isolated element
- no visual identity is being established: the project already has colors and type, or there is no project yet, only a sketch
- nothing downstream depends on the result being systematised

If two or more fail, it is not light scope. Run the full pipeline and say in one line why.

**What changes:**

| Phase | Full | Light |
|---|---|---|
| 1 BRAINSTORM | five domains, one question at a time | **one question**, the least obvious one, then stop |
| 2 THESIS | visual + interaction, both validated | interaction thesis only, still validated |
| 3 DESIGN SYSTEM | generate MASTER.md and the stack token files | **skipped.** Read the tokens already in the project and use them. Write no MASTER.md. |
| 4 IMPLEMENT | page by page, validate page by page | the one component |
| 5 AUDIT | full design-audit sub-skill | the quick check: reduced-motion, exit animation, 60fps |

**Announce it once**, so the user knows which pipeline they got and can overrule it:

> "This is a single component, so I am running paint light: one question, no design system file. Say so if you want the full pipeline."

**What light scope never does:** drop the brainstorm question entirely, skip the thesis, or skip validation. Every gate stays. Only their number goes down.

---

<!-- genjutsu:shared:preview:start -->
## Showing Your Work - The Preview Gate

Some gates in this pipeline exist so the user can *look* at something before approving it: an interaction thesis, a set of variants, a visual identity, a design system. Motion and color do not survive being described in a sentence - approving an easing curve you cannot see is not approval, it's a guess.

So before the first gate of that kind, ask how they want to see it. Then never ask again.

**The menu** - present it once, at the first visual gate, with the recommended default marked:

> Before I show you this - how do you want to see it?
>
> **A. Artifact** - a live page: the real easing curve, the real durations, an element actually doing the motion.
> **B. Live preview** - a throwaway route in your project, real stack, real tokens. Native: a `@Preview` / `#Preview` scratch file.
> **C. Inline** - written out here in the conversation.

**Recommended default** - state it in the menu, never apply it silently:

| Situation | Default |
|---|---|
| Scope is light (a hover, one transition) | C - inline |
| Scope is medium or full, web stack | A - artifact |
| Scope is medium or full, Compose / SwiftUI | B - live preview, A as second choice |
| A full visual identity or design system is on the table | A - artifact |
| No dev server, or the repo must not be written to | A - artifact |
| Host is Cowork and there is no project checkout to write into | A - artifact, B is unavailable |

**The choice sticks for the whole session.** At every later gate, announce the mode in one line ("Variants in artifact.") and go. Do not reopen the menu. The user switches by saying so - "show me that as text", "put it in an artifact", "just tell me" - respect it immediately, and the new mode becomes the session default from then on.

**Which host is this?** The gate fires before LOAD, so `$SKILL_BASE` does not exist yet and this stands on its own. Detect once, cheaply, then map:

```bash
if [ -d /mnt/skills/user ]; then
  GENJUTSU_HOST=claude-ai
elif [ -d /mnt/.claude/skills ] \
  || [ -n "$(find /sessions -maxdepth 6 -type d -path '*/.claude/skills' 2>/dev/null | head -1)" ]; then
  GENJUTSU_HOST=cowork
elif [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || [ -d "$HOME/.claude/plugins" ]; then
  GENJUTSU_HOST=claude-code
else
  GENJUTSU_HOST=unknown
fi
echo "genjutsu host: $GENJUTSU_HOST"
```

Cowork is tested before Claude Code on purpose: both can have a `~/.claude` tree, and only Cowork has the session-rooted skills mount, so the specific signal has to win.

**Producing the preview** - resolve the host, degrade, never fail:

| Host | A - artifact | C - inline |
|---|---|---|
| claude.ai | Rendered natively. Just produce one. | Written out in the conversation. |
| Cowork | The host's persistent artifact. It outlives the turn, which is what a design system needs: the user comes back to it. | The host's inline widget, rendered in place. Right default for a short task. |
| Claude Code | The `Artifact` tool, when it is available. | Written out in the conversation. |
| unknown | A self-contained HTML file written to a temp path, hand back the path. | Written out in the conversation. |

Call whatever the host actually exposes, under the name it exposes it as - check the tools available in the session rather than assuming one. If nothing renders, fall back down the table rather than failing the gate: an inline preview always beats an aborted one.

**B - live preview needs a project to write into.** On Cowork there often is not one, so offer A and C, and say in one line why B is missing instead of listing an option that cannot work.

**What goes in it.** A preview that restates the sentence in a nicer font is worthless. Carry what a sentence cannot:

| Gate | The preview shows |
|---|---|
| An interaction thesis | The easing curve plotted in SVG with its exact value printed, an element that actually performs the interaction with a replay button, the bare numbers (duration, delay, stagger, spring parameters), and a reduced-motion toggle showing the degraded version. |
| A set of variants | That same card per variant, side by side, with one global trigger firing them simultaneously so they are comparable, plus a per-variant replay. |
| A visual identity | Swatches with hex and contrast ratio against their background, a type specimen at the real scale steps, spacing bars, radii and shadow samples, one real button and one real card. |
| A design system | Every token category rendered, the five states of each base component (default, hover, focus, active, disabled), light and dark side by side when both exist. |

**Rules the preview obeys:**

- **It is throwaway. It never becomes the implementation.** Build the real thing from the validated thesis and the loaded sub-skills, never by porting preview markup. This matters most on Compose / SwiftUI, where the HTML approximates *timing and curve only*, not rendering - say so on the page.
- Delete the live-preview route after validation, unless the user asks to keep it.
- Never install a dependency to build a preview.
- Never start a dev server without asking.
- Only show values that are in the thesis. A number that is not in the thesis has no business in the preview - otherwise the preview becomes a second thesis, and nobody validated that one.
<!-- genjutsu:shared:preview:end -->

---

## Sub-skills Path Detection

<!-- genjutsu:shared:skill-base:start -->
```bash
# Environment detection, most specific first:
# - claude.ai: skills are uploaded individually to /mnt/skills/user/<name>/
# - Claude Code: ${CLAUDE_PLUGIN_ROOT} resolves to THIS plugin version's
#   install directory. Claude Code substitutes it anywhere in skill content.
# - Cowork and skills-directory installs: no fixed path exists. The tree is
#   mounted under a session root that changes every run, e.g.
#   /sessions/<id>/mnt/.claude/skills/genjutsu/_jutsu. Probed last, so the two
#   environments above keep resolving exactly as they did before.
# Single-bundle upload (genjutsu.zip) first: sub-skills live under this skill's
# own dir, e.g. /mnt/skills/user/genjutsu/_jutsu/<name>/.

# Probe for a mounted _jutsu when no fixed path applies. Bounded on purpose:
# every root is either shallow or depth-capped, so this never walks the disk.
genjutsu_probe_jutsu() {
  probe_hit=""
  # Walk up from the working directory first: cheapest, and correct whenever
  # the session root is an ancestor of wherever the pipeline is running. Hard
  # bounded, and the case guard catches "." and "": an empty or relative PWD
  # would otherwise never reach "/" and the loop would spin forever.
  probe_dir="${PWD:-$(pwd)}"
  probe_n=0
  while [ "$probe_n" -lt 24 ]; do
    probe_n=$((probe_n + 1))
    probe_hit="$(find "$probe_dir/.claude/skills" -maxdepth 2 -type d -name _jutsu 2>/dev/null | head -1)"
    [ -n "$probe_hit" ] && { printf '%s\n' "$probe_hit"; return 0; }
    case "$probe_dir" in /|.|"") break ;; esac
    probe_dir="$(dirname "$probe_dir")"
  done
  # Then the fixed roots. A skills directory holds _jutsu two levels down, so
  # that is all they get: no reason to traverse a populated one any deeper.
  for probe_root in "$HOME/.claude/skills" /mnt/.claude/skills; do
    [ -d "$probe_root" ] || continue
    probe_hit="$(find "$probe_root" -maxdepth 2 -type d -name _jutsu 2>/dev/null | head -1)"
    [ -n "$probe_hit" ] && { printf '%s\n' "$probe_hit"; return 0; }
  done
  # A session root is the one layout that needs more, for the session id and
  # its mnt/ wrapper. Still capped, and skipped entirely when absent.
  if [ -d /sessions ]; then
    probe_hit="$(find /sessions -maxdepth 8 -type d -path '*/.claude/skills/*/_jutsu' 2>/dev/null | head -1)"
    [ -n "$probe_hit" ] && { printf '%s\n' "$probe_hit"; return 0; }
  fi
  return 1
}

BUNDLE_JUTSU="$(find /mnt/skills/user -maxdepth 2 -type d -name _jutsu 2>/dev/null | head -1)"
if [ -n "$BUNDLE_JUTSU" ]; then
  # claude.ai - single self-contained genjutsu bundle
  SKILL_BASE="$BUNDLE_JUTSU"
elif [ -d "/mnt/skills/user" ]; then
  # claude.ai - each sub-skill is its own uploaded skill (detect the mount, not
  # one specific sub-skill, so a partial upload still resolves the base).
  SKILL_BASE="/mnt/skills/user"
else
  # Claude Code plugin
  SKILL_BASE="${CLAUDE_PLUGIN_ROOT}/skills/_jutsu"
  # Fallback if the placeholder was not substituted: newest installed version.
  # Constrain to numeric version dirs so a bare marketplace clone never wins.
  if [ ! -d "$SKILL_BASE" ]; then
    SKILL_BASE=$(find ~/.claude/plugins/cache -type d -path '*/genjutsu/[0-9]*/skills/_jutsu' 2>/dev/null | sort -V | tail -1)
  fi
  # Cowork / skills-directory install: session-rooted mount, nothing fixed to
  # match, so probe for it only once the two fixed layouts have both missed.
  if [ -z "$SKILL_BASE" ] || [ ! -d "$SKILL_BASE" ]; then
    SKILL_BASE="$(genjutsu_probe_jutsu)"
  fi
fi

# Abort clearly instead of cat-ing bogus paths if resolution failed. Name every
# root that was tried, so a new host layout can be reported instead of guessed.
if [ -z "$SKILL_BASE" ] || [ ! -d "$SKILL_BASE" ]; then
  echo "genjutsu: could not resolve the sub-skills directory." >&2
  echo "  claude.ai   - upload the genjutsu skill ZIP(s) via Customize > Skills." >&2
  echo "  Claude Code - reinstall the plugin, then run /reload-plugins." >&2
  echo "  Cowork      - expected a _jutsu directory under a */.claude/skills/<name>/ mount." >&2
  echo "  Tried: /mnt/skills/user, \$CLAUDE_PLUGIN_ROOT, ~/.claude/plugins/cache," >&2
  echo "         \$PWD ancestors, ~/.claude/skills, /mnt/.claude/skills, /sessions." >&2
fi

# Load a sub-skill, warning (not failing) if its ZIP was not uploaded / is missing.
# The entry filename depends on the artifact, not on the host: a plugin install
# ships SKILL.md, while the claude.ai bundle renames every inner one to GUIDE.md
# at packaging time. Either can end up mounted under a Cowork session root, so
# try both. The name is assembled from parts on purpose - spelled out in full it
# would be rewritten by the same packaging step, defeating the fallback.
load_skill() {
  for jutsu_doc in SKILL GUIDE; do
    if [ -f "$SKILL_BASE/$1/$jutsu_doc.md" ]; then
      cat "$SKILL_BASE/$1/$jutsu_doc.md"
      return 0
    fi
  done
  echo "genjutsu: sub-skill '$1' not found - upload its ZIP (claude.ai) or reinstall the plugin; continuing without it." >&2
}
```
<!-- genjutsu:shared:skill-base:end -->

All sub-skills are loaded via `load_skill <name>` (defined above), which cat's `$SKILL_BASE/<name>/SKILL.md` and warns instead of failing if a sub-skill was not uploaded.

---

## Pipeline

### Phase 1 — BRAINSTORM (mandatory, never skip)

This is the foundation. Rush it and everything downstream is wrong. The goal: understand the user's vision well enough to write two theses they'd agree with without hesitation.

#### Stack scan (run before brainstorm)

Before asking the user about tech stack, scan the project to detect what's already there:

<!-- genjutsu:shared:scan:start -->
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

Map the results:
- **Animation lib**: gsap, framer-motion, three/@react-three, anime.js, or none
- **Framework**: React, Vue, Svelte, Next.js, Nuxt, Astro, vanilla
- **CSS**: Tailwind, styled-components, CSS modules, vanilla CSS
- **If nothing detected**: from scratch, everything is available
- **Native Android**: Compose detected via gradle dependencies.
- **Native Apple**: SwiftUI detected via Package.swift / xcodeproj + swift files. Distinguish iOS vs macOS via Package.swift platforms or pbxproj SDKROOT.
- **Compose Multiplatform**: kotlin-multiplatform plugin + jetbrains.compose plugin.
- **Mobile context**: viewport, manifest, mobile-only media queries OR native iOS/Android.
- **Desktop context**: macOS target OR no mobile indicators on web.
- **Legacy mixed**: presence of `.xib`, `.storyboard`, layout XML, `setContentView(R.layout.*)`. Mention only, no auto-load.
<!-- genjutsu:shared:scan:end -->

**If legacy mixed detected** (XIB / storyboard / layout XML / setContentView(R.layout.\*)):

Ask exactly one question during brainstorm:

> "I see your project mixes [XML layouts / XIBs / classic Activities] with modern UI. For this task, should I stay on pure [Compose/SwiftUI], or integrate into a legacy screen?"

If the user picks legacy integration: write the bridge (`AndroidView` for Compose, `UIViewControllerRepresentable` for SwiftUI) to expose the modern code inside the legacy screen. Never generate new legacy code (no XML, no XIB, no setContentView).

**The five domains to cover:**

1. **Product** — What is it? (app, landing page, portfolio, SaaS, e-commerce, blog, dashboard...)
2. **Audience** — Who uses it? (devs, designers, general public, enterprise, kids, luxury...)
3. **Mood** — 3 to 5 adjectives that define the visual feel
4. **References** — Sites, screenshots, mood boards, anything visual
5. **Tech stack** — What's already in place? Or starting from scratch?

**How to ask:** One question at a time, starting with the least obvious domain. If you already know the tech stack from scanning `package.json`, don't ask — start with mood or audience instead. Each answer reshapes how you ask the next question.

**How to handle vague answers:**

When the user says "modern" or "clean" or "I don't know, just make it nice":

1. **Validate** — "That's a starting point. Let's make it precise."
2. **Offer concrete options** — "Clean like Stripe's editorial whitespace, clean like Linear's dense-but-organized, or clean like Apple's dramatic minimalism?"
3. **Reframe** — "What would feel *wrong*? What sites make you cringe? That's just as useful."
4. **Name the consequence** — "This choice drives the entire color palette and typography. Worth spending a minute on."

**Never** interpret a vague answer as confirmation. "Yeah something like that" means dig deeper — ask which part of "that" resonates.

**When the user pushes to skip or rush brainstorm:**

Do NOT capitulate. Instead:

> "We've covered [covered areas]. I'm still missing [missing areas], which will directly impact [concrete consequence]. Want me to ask one more question, or would you rather I make assumptions and you correct them afterward?"

This gives them an informed choice. If they choose assumptions, name each assumption explicitly in the thesis.

**Never** negotiate the number of remaining questions ("just two more, I promise"). You don't know how many you need until you hear the answers.

**When to stop:** When you can write both theses (visual + interaction) and you'd bet money the user will say "oui parfait." If you'd be guessing on even one aspect, keep asking.

---

### Phase 2 — THESIS (define direction, get validation)

From the brainstorm, produce two theses:

#### Visual Thesis

A single sentence that captures the entire visual identity. **Must explicitly address all four:**

- **Color direction** — dark/light, palette family, accent color
- **Typography spirit** — serif/sans/mono, weight usage, size contrast
- **Spacing philosophy** — dense/airy, base unit feel
- **Component style** — rounded/sharp, bordered/filled, elevated/flat

> Example: "Dark neo-brutalist interface with bold monospace type, fluorescent chartreuse accents, generous whitespace, raw-edged components with offset shadows."

**Self-check:** read your thesis back. If any of the four areas is missing or vague ("nice typography"), rewrite it before presenting.

#### Interaction Thesis

A single sentence that captures the motion and interaction language. **Must explicitly address all four:**

- **Timing range** — fast (100-200ms), medium (200-400ms), or slow (400ms+)
- **Hover behavior** — what happens on hover
- **Scroll behavior** — reveals, parallax, or nothing
- **Forbidden patterns** — what this project will NOT do

> Example: "Fast and dry transitions (100-200ms), hover with subtle scale (1.02), scroll-triggered reveals with stagger, no bounce or elastic — all sharp ease-out."

**Cross-platform thesis examples:**

- "This Compose hero will use a SharedTransitionLayout with a spring(stiffness=Spring.StiffnessMedium, dampingRatio=0.85) for a fluid card-to-detail transition."
- "This SwiftUI tab transition will use matchedGeometryEffect with a .smooth spring (response: 0.5, dampingFraction: 0.85) for a tactile, spatial feel."
- "This macOS dashboard will use 100ms opacity hover states (no scale on hover, desktop subtlety) and a Cmd+1-9 keyboard shortcut to navigate panels."
- "This Android header will use an AGSL shader bound to scrollOffset for a dynamic liquid-glass effect (Android 13+, with a static fallback below)."

**Self-check:** read your thesis back. If you can't immediately derive the CSS/JS properties from it, it's too vague. Rewrite.

**This is the first visual gate.** Offer the preview menu (see "Showing Your Work" above), then present both theses in the chosen mode. The visual thesis in particular is worth far more shown than described - "fluorescent chartreuse accents" is a guess until it sits next to the neutrals.

**Wait for explicit user validation of BOTH theses before moving on.** If the user pushes back, don't start over — ask what feels wrong and adjust.

---

### Phase 3 — DESIGN SYSTEM

Load `_jutsu/ui-ux-pro-max` sub-skill:

```bash
cat "$SKILL_BASE/ui-ux-pro-max/SKILL.md"
```

#### Stack-aware token generation

The MASTER.md design system file is canonical, but the generated **code** files match the detected stack:

- **Web stack detected**: generate Tailwind config / CSS variables (existing format). Tokens in CSS hex, `cubic-bezier(...)` easings, `rem` spacing. Output paired with `tailwind.config.js` extension or `:root { --token: ... }` CSS.
- **Android Compose stack detected**: generate Kotlin design tokens. Output `Theme.kt`, `Color.kt`, `Type.kt`, `Shapes.kt`, `Motion.kt` referenced from MASTER.md. Color tokens in `Color(0xFF...)`, typography in `TextStyle`, shapes in `RoundedCornerShape`, motion in `MotionScheme` (M3 Expressive when scope is hero / impactful). Spacing in `dp`.
- **SwiftUI stack detected (iOS / macOS / multi-target)**: generate Swift extensions. Output `Color+App.swift`, `Font+App.swift`, `Animation+App.swift`, `Shape+App.swift`. Color tokens via `Color("AssetName")` referencing the asset catalog (or `Color(red:green:blue:)` if no catalog), typography via `Font.system(...)` or `.custom(...)`, animations via `.spring(...)` / `.snappy` / `.bouncy` named presets. Spacing in `CGFloat` constants.
- **Compose Multiplatform stack detected**: generate Kotlin tokens in `commonMain` with `expect/actual` for fonts and platform-specific colors. Same structure as Android Compose, plus a section in MASTER.md describing per-platform deviations.
- **Multi-stack project** (e.g., web admin + native mobile app): generate MASTER.md with clearly delimited sections for each stack, and produce code files for each.

The MASTER.md document itself remains a single canonical source-of-truth file. The generated code files (Theme.kt / Color+App.swift / etc.) are children of MASTER.md and reference it.

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

#### Show it before Phase 4

Present the design system in the session's preview mode - announce the mode in one line, don't reopen the menu - and get validation before implementing anything. A palette and a type scale listed as hex codes and pixel values in a transcript are precise and completely unreviewable; every token in MASTER.md is about to be applied everywhere, so this is the cheapest place to catch a wrong one.

---

### Phase 4 — IMPLEMENT

Load sub-skills based on tech stack and interaction thesis.

**Always load** (load every sub-skill below via `load_skill <name>`, defined above - it warns instead of failing silently if a ZIP is missing):
- `load_skill motion-principles` - the foundation

<!-- genjutsu:shared:load:start -->
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
<!-- genjutsu:shared:load:end -->

Implementation rules:
- Work **page by page** or **component by component** — never try to do everything at once.
- Every color, font, spacing, shadow, radius MUST come from MASTER.md tokens. No magic numbers.
- Every animation MUST respect the interaction thesis (timing, easing, forbidden patterns).
- Apply the 5-state rule for interactive elements: **default, hover, focus, active, disabled**.
- Ask the user for validation after each major page/section before moving to the next.

---

### Phase 5 — AUDIT (never skip)

Load `_jutsu/design-audit` sub-skill:

```bash
cat "$SKILL_BASE/design-audit/SKILL.md"
```

Run the full audit checklist matching the detected stack.

**All stacks:**
- [ ] Reduced motion respected (CSS `prefers-reduced-motion`, SwiftUI `accessibilityReduceMotion`, or Compose helper using `ValueAnimator.areAnimatorsEnabled()` / `Settings.Global.ANIMATOR_DURATION_SCALE`).
- [ ] Exit animations present (no abrupt vanishings).
- [ ] No layout-property animations (animate transform / opacity / graphicsLayer instead).
- [ ] Focus visible on interactive elements.
- [ ] Interactive elements have all relevant states (default, hover/press, focus, active, disabled).
- [ ] Colors and spacing consistent with MASTER.md tokens - no rogue hex values.

**Web:**
- [ ] Conditional renders with AnimatePresence (or framework equivalent).
- [ ] Contrast ratio >= 4.5:1 for all text.
- [ ] No forced reflow, `will-change` used sparingly.
- [ ] 60fps target verified via Chrome DevTools Performance panel.
- [ ] No clickable divs without role/button.
- [ ] `aria-hidden` on purely decorative animations.
- [ ] Responsive on 4 breakpoints: 375px (mobile) / 768px (tablet) / 1024px (small desktop) / 1440px (large desktop).

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
- [ ] Keyboard shortcuts (`Cmd+N`, `Cmd+W`, `Cmd+F`, etc.) bound to primary actions.
- [ ] Multi-window state shared coherently if applicable.
- [ ] Focus rings visible on keyboard navigation (no `outline: none` without alternative).

Present findings grouped by severity: **Critical > Important > Nice-to-have**.

---

## Existing Project Protocol

When invoked on a project that already has design/styling:

1. Still run the full BRAINSTORM (Phase 1)
2. Acknowledge existing design, but the thesis overrides it
3. In Phase 4, **replace** existing design tokens/styles with the new design system
4. Preserve functionality and layout structure — only replace the visual layer

This is intentional: `/genjutsu:paint` rebuilds the visual universe. To enhance what exists, use `/genjutsu:cast` instead.

---

## Red Flags — You're About to Violate This Skill

| Thought | Reality |
|---------|---------|
| "The user already said 'minimal dark' — I have enough for a thesis" | Two words aren't five domains. Keep asking. |
| "I'll ask all five brainstorm questions at once" | One at a time. The answer to 'audience' changes how you ask about 'mood'. |
| "The user seems impatient, let's skip to coding" | Use the pressure protocol. A bad thesis costs days, not minutes. |
| "I'll pick colors that feel right" | Every token comes from MASTER.md. No freelancing. |
| "I'll do the whole site in one pass" | Page by page. Validate page by page. |
| "This animation would be cool even though the thesis says no bounce" | The thesis is law. Change it? Re-validate with the user first. |
| "The audit can wait, the user seems happy" | The audit is not optional. Phase 5 always runs. |
| "I'll interpret 'yeah something like that' as a yes" | That's not confirmation. Ask which part resonates. |
| "I'll list the palette as hex codes, that's precise" | Precise and unreviewable. Show it in the session's preview mode. |
| "I'll ask again how they want to see the design system" | Asked once, sticks for the session. Announce the mode and go. |
| "The preview page looks good, I'll build the app from it" | The preview is throwaway. Build from MASTER.md. |
