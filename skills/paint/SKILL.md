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
3. **Never proceed without the theses validated.** Visual + interaction, both explicitly approved. The one exception is light scope, below: no visual identity is at stake there, so the interaction thesis alone is required - and it is still validated explicitly, never assumed.
4. **Every design token comes from MASTER.md.** No magic numbers, no rogue hex values. On light scope, where no MASTER.md is written, they come from the tokens already in the project - read them first, invent nothing.
5. **Every animation respects the interaction thesis.** Timing, easing, forbidden patterns - no exceptions.
6. **Never install a dependency without asking.**
7. **Work page by page, validate page by page.** Never try to do everything at once.
8. **The audit is not optional.** Phase 5 always runs, even if the user seems happy. On light scope it shortens to the quick check - reduced-motion, exit animation, 60fps - but it never disappears.
9. **Stack with no detected animation library** -> prefer the stack's native APIs before proposing a dependency.
10. **Animation library detected** (GSAP, Motion / Framer Motion, Lottie, Rive, etc.) -> respect the dev's choice. Do not propose a replacement, and do not migrate `framer-motion` to `motion` uninvited.
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
> **A. Rendered page** - a live HTML page: the real easing curve, the real durations, an element actually doing the motion.
> **B. Live preview** - a throwaway route in your project, real stack, real tokens. Native: a `@Preview` / `#Preview` scratch file.
> **C. Inline** - written out here in the conversation.

**Recommended default** - state it in the menu, never apply it silently:

| Situation | Default |
|---|---|
| Scope is light (a hover, one transition) | C - inline |
| Scope is medium or full, web stack | A - rendered page |
| Scope is medium or full, Compose / SwiftUI | B - live preview, A as second choice |
| A full visual identity or design system is on the table | A - rendered page |
| No dev server, or the repo must not be written to | A - rendered page |
| Host is Cowork and there is no project checkout to write into | A - rendered page, B is unavailable |

**The choice sticks for the whole session.** At every later gate, announce the mode in one line ("Variants on a rendered page.") and go. Do not reopen the menu. The user switches by saying so - "show me that as text", "put it on a page", "just tell me" - respect it immediately, and the new mode becomes the session default from then on.

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

| Host | A - rendered page | C - inline |
|---|---|---|
| claude.ai | Rendered natively as an artifact. Just produce one. | Written out in the conversation. |
| Cowork | The host's persistent artifact. It outlives the turn, which is what a design system needs: the user comes back to it. | The host's inline widget, rendered in place. Right default for a short task. |
| Claude Code | The `Artifact` tool when the session has it, else the capability rule below. | Written out in the conversation. |
| unknown (any other host) | The capability rule below. | Written out in the conversation. |

**A, by capability.** Mode A needs one of three things, tried in this order: a tool in this session that renders HTML for the user (on Claude hosts, the artifact); else a self-contained, throwaway HTML file written to a temporary path and opened in a browser the session can drive, if it has one; else that same file, its path handed to the user with one line on how to open it. Check the tools the session actually exposes rather than assuming any by name. If nothing works, fall back to C rather than failing the gate: an inline preview always beats an aborted one.

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

**Tell the block where this skill lives.** The block's first line reads `GENJUTSU_SKILL_DIR`.
Claude Code fills it in by itself. On any other host, put one line in front of the block, in the
same shell call, naming the directory you read this file from:
`GENJUTSU_SKILL_DIR='/absolute/path/to/paint'`. When the genjutsu router printed a
`GENJUTSU_SKILL_DIR=` line, use that value as it is.

<!-- genjutsu:shared:skill-base:start -->
**This block defines shell state, and shell state does not survive between shell calls.**
`$SKILL_BASE`, `load_skill` and `load_ref` exist only inside the single shell call that ran
this block. Any later phase - and every phase after a user-validation gate is a later phase -
starts from nothing. So: **re-emit this whole block in the same shell call as the
`load_skill` lines you are about to run.** Never `cat "$SKILL_BASE/..."` in a call that did
not define it: the path resolves to `/<name>/...`, the `cat` fails, and the module is lost.

**If the block prints `could not find the genjutsu modules`, stop the pipeline.** Show the
user the message, install command included, and do nothing else: every later step depends
on the modules, and running without them produces exactly the generic output this skill
exists to prevent.

```bash
GENJUTSU_SKILL_DIR="${GENJUTSU_SKILL_DIR:-${CLAUDE_SKILL_DIR}}"
# Resolution order, first hit wins:
#   0. claude.ai, /mnt/skills/user: the genjutsu bundle, else individual uploads.
#   1. This skill's own directory: its _jutsu, or the _jutsu next to it.
#   2. ${CLAUDE_PLUGIN_ROOT}/skills/_jutsu, when Claude Code substituted it.
#   3. Bounded probes: .claude/skills and .agents/skills from $PWD upward, then
#      the skills directories installers write to, then /sessions (Cowork).
#   4. The Claude Code plugin cache, newest version. Last on purpose: an old
#      plugin install must never win over a newer bundle.
# Resolved from scratch every time. A cache was tried here and removed: after a
# plugin update the old version directory is still on disk, so a cached path
# passes an "is it a directory" check and serves the previous release.

# A _jutsu directory counts only if it holds motion-principles. The shared
# skills directory of npx serves about 80 agents, so a directory name proves
# nothing. The entry file is named SKILL or GUIDE depending on the artifact
# (the bundle renames it at packaging time), so the name is assembled from
# parts: spelled out in full, the packaging step would rewrite it too.
genjutsu_is_jutsu() {
  for d in SKILL GUIDE; do
    [ -f "$1/motion-principles/$d.md" ] && return 0
  done
  return 1
}

# Print the first genjutsu _jutsu among the candidate paths read on stdin.
genjutsu_first_jutsu() {
  while read -r jutsu_c; do
    genjutsu_is_jutsu "$jutsu_c" && { printf '%s\n' "$jutsu_c"; return 0; }
  done
  return 1
}

SKILL_BASE=""
# 0. claude.ai. Individual uploads: the mount itself is the base, even without
# motion-principles, so a partial upload still loads what it has.
if [ -d /mnt/skills/user ]; then
  SKILL_BASE="$(find -L /mnt/skills/user -maxdepth 2 -type d -name _jutsu 2>/dev/null | genjutsu_first_jutsu)"
  [ -n "$SKILL_BASE" ] || SKILL_BASE="/mnt/skills/user"
fi
# 1. This skill's own directory. Empty means unknown: never probe "/_jutsu".
if [ -z "$SKILL_BASE" ] && [ -n "$GENJUTSU_SKILL_DIR" ]; then
  SKILL_BASE="$(printf '%s\n' "$GENJUTSU_SKILL_DIR/_jutsu" "$GENJUTSU_SKILL_DIR/../_jutsu" | genjutsu_first_jutsu)"
fi
# 2. Claude Code plugin root.
if [ -z "$SKILL_BASE" ] && [ -n "${CLAUDE_PLUGIN_ROOT}" ]; then
  SKILL_BASE="$(printf '%s\n' "${CLAUDE_PLUGIN_ROOT}/skills/_jutsu" | genjutsu_first_jutsu)"
fi
# 3. Bounded probes, following symlinks (npx links .claude/skills/<name> to
# .agents/skills/<name>). The case guard stops the walk at "/", "." or "".
probe_dir="${PWD:-$(pwd)}"
probe_n=0
while [ -z "$SKILL_BASE" ] && [ "$probe_n" -lt 24 ]; do
  probe_n=$((probe_n + 1))
  SKILL_BASE="$(find -L "$probe_dir/.claude/skills" "$probe_dir/.agents/skills" -maxdepth 2 -type d -name _jutsu 2>/dev/null | genjutsu_first_jutsu)"
  case "$probe_dir" in /|.|"") break ;; esac
  probe_dir="$(dirname "$probe_dir")"
done
for probe_root in "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.codex/skills" \
    "$HOME/.cursor/skills" /mnt/.claude/skills; do
  [ -z "$SKILL_BASE" ] && [ -d "$probe_root" ] || continue
  SKILL_BASE="$(find -L "$probe_root" -maxdepth 2 -type d -name _jutsu 2>/dev/null | genjutsu_first_jutsu)"
done
if [ -z "$SKILL_BASE" ] && [ -d /sessions ]; then
  SKILL_BASE="$(find -L /sessions -maxdepth 8 -type d -path '*/.claude/skills/*/_jutsu' 2>/dev/null | genjutsu_first_jutsu)"
fi
# 4. Claude Code plugin cache, newest version first. Numeric version
# directories only, so a bare marketplace clone never wins.
if [ -z "$SKILL_BASE" ] && [ -d "$HOME/.claude/plugins/cache" ]; then
  SKILL_BASE="$(find "$HOME/.claude/plugins/cache" -maxdepth 6 -type d -path '*/genjutsu/[0-9]*/skills/_jutsu' 2>/dev/null | sort -V -r | genjutsu_first_jutsu)"
fi
[ -n "$SKILL_BASE" ] && SKILL_BASE="$(cd "$SKILL_BASE" 2>/dev/null && pwd -P)"

# Stop instead of running the pipeline without its modules. Name every root that
# was tried, so a new layout can be reported instead of guessed.
if [ -z "$SKILL_BASE" ]; then
  echo "genjutsu: could not find the genjutsu modules (a _jutsu directory holding motion-principles)." >&2
  echo "  cast and paint do not work without them. Install the full bundle:" >&2
  echo "    any agent    npx skills add https://genjutsu.athevon.dev -g" >&2
  echo "    Claude Code  /plugin marketplace add AThevon/genjutsu, then /plugin install genjutsu" >&2
  echo "    claude.ai    upload genjutsu.zip in Customize > Skills" >&2
  echo "  npx skills add AThevon/genjutsu installs cast and paint without their modules." >&2
  echo "  Tried: /mnt/skills/user, GENJUTSU_SKILL_DIR (${GENJUTSU_SKILL_DIR:-empty}) and its parent," >&2
  echo "         \$CLAUDE_PLUGIN_ROOT, .claude/skills and .agents/skills from \$PWD upward," >&2
  echo "         ~/.agents/skills, ~/.claude/skills, ~/.codex/skills, ~/.cursor/skills," >&2
  echo "         /mnt/.claude/skills, /sessions, ~/.claude/plugins/cache." >&2
  echo "genjutsu: stop the pipeline here and show this message to the user." >&2
  return 1 2>/dev/null || exit 1
fi
echo "genjutsu: modules from $SKILL_BASE" >&2

# Print a module's entry file. A missing module does not stop the pipeline (a
# partial claude.ai upload is legitimate), but it is announced, and the final
# report lists it: shell state does not survive, so the model keeps the list.
load_skill() {
  for d in SKILL GUIDE; do
    if [ -f "$SKILL_BASE/$1/$d.md" ]; then
      cat "$SKILL_BASE/$1/$d.md"
      return 0
    fi
  done
  echo "genjutsu: sub-skill '$1' NOT LOADED - not found under $SKILL_BASE. Carry on, and list it under 'Modules not loaded' in the final report." >&2
  return 1
}

# Print one reference file of a module: load_ref <module> <path inside it>.
load_ref() {
  if [ -f "$SKILL_BASE/$1/$2" ]; then
    cat "$SKILL_BASE/$1/$2"
    return 0
  fi
  echo "genjutsu: reference '$1/$2' NOT LOADED - not found under $SKILL_BASE. Carry on, and say so in the final report." >&2
  return 1
}
```
<!-- genjutsu:shared:skill-base:end -->

All sub-skills are loaded via `load_skill <name>` (defined above), which prints the module's
entry file, or a `NOT LOADED` line when the module is missing, and carries on: keep the list, the
final report needs it. When the block cannot find the modules at all, it stops, and so does the
pipeline. Every phase below that loads something must re-emit the resolution block in the same
shell call: the phases are separated by user gates, and nothing carries across them.

---

## Pipeline

### Phase 1 - BRAINSTORM (mandatory, never skip)

This is the foundation. Rush it and everything downstream is wrong. The goal: understand the user's vision well enough to write two theses they'd agree with without hesitation.

#### Stack scan (run before brainstorm)

Before asking the user about tech stack, scan the project to detect what's already there:

<!-- genjutsu:shared:scan:start -->
```bash
# 1. Web (existing)
cat package.json 2>/dev/null | grep -E '"(gsap|motion|framer-motion|three|@react-three/fiber|@react-three/drei|animejs|popmotion|lenis|locomotive-scroll)"'
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
- **Animation lib**: gsap, `motion`, `framer-motion`, three/@react-three, anime.js, or none.
  **`motion` and `framer-motion` are the same library at two names.** Framer Motion was renamed
  to Motion; `motion` is the current package and `framer-motion` is the legacy one, still widely
  installed and still published. Note which of the two is in `package.json` - the import path
  differs and the sub-skill needs to know. If both are present, the project is mid-migration:
  say so and follow whichever one the file you are editing already imports.
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

1. **Product** - What is it? (app, landing page, portfolio, SaaS, e-commerce, blog, dashboard...)
2. **Audience** - Who uses it? (devs, designers, general public, enterprise, kids, luxury...)
3. **Mood** - 3 to 5 adjectives that define the visual feel
4. **References** - Sites, screenshots, mood boards, anything visual
5. **Tech stack** - What's already in place? Or starting from scratch?

**How to ask:** One question at a time, starting with the least obvious domain. If you already know the tech stack from scanning `package.json`, don't ask - start with mood or audience instead. Each answer reshapes how you ask the next question.

**How to handle vague answers:**

When the user says "modern" or "clean" or "I don't know, just make it nice":

1. **Validate** - "That's a starting point. Let's make it precise."
2. **Offer concrete options** - "Clean like Stripe's editorial whitespace, clean like Linear's dense-but-organized, or clean like Apple's dramatic minimalism?"
3. **Reframe** - "What would feel *wrong*? What sites make you cringe? That's just as useful."
4. **Name the consequence** - "This choice drives the entire color palette and typography. Worth spending a minute on."

**Never** interpret a vague answer as confirmation. "Yeah something like that" means dig deeper - ask which part of "that" resonates.

**When the user pushes to skip or rush brainstorm:**

Do NOT capitulate. Instead:

> "We've covered [covered areas]. I'm still missing [missing areas], which will directly impact [concrete consequence]. Want me to ask one more question, or would you rather I make assumptions and you correct them afterward?"

This gives them an informed choice. If they choose assumptions, name each assumption explicitly in the thesis.

**Never** negotiate the number of remaining questions ("just two more, I promise"). You don't know how many you need until you hear the answers.

**When to stop:** When you can write both theses (visual + interaction) and you'd bet money the user will say "oui parfait." If you'd be guessing on even one aspect, keep asking.

---

### Phase 2 - THESIS (define direction, get validation)

From the brainstorm, produce two theses:

#### Visual Thesis

A single sentence that captures the entire visual identity. **Must explicitly address all four:**

- **Color direction** - dark/light, palette family, accent color
- **Typography spirit** - serif/sans/mono, weight usage, size contrast
- **Spacing philosophy** - dense/airy, base unit feel
- **Component style** - rounded/sharp, bordered/filled, elevated/flat

> Example: "Dark neo-brutalist interface with bold monospace type, fluorescent chartreuse accents, generous whitespace, raw-edged components with offset shadows."

**Self-check:** read your thesis back. If any of the four areas is missing or vague ("nice typography"), rewrite it before presenting.

#### Interaction Thesis

A single sentence that captures the motion and interaction language. **Must explicitly address all four:**

- **Timing range** - fast (100-200ms), medium (200-400ms), or slow (400ms+)
- **Hover behavior** - what happens on hover
- **Scroll behavior** - reveals, parallax, or nothing
- **Forbidden patterns** - what this project will NOT do

> Example: "Fast and dry transitions (100-200ms), hover with subtle scale (1.02), scroll-triggered reveals with stagger, no bounce or elastic - all sharp ease-out."

**Cross-platform thesis examples:**

- "This Compose hero will use a SharedTransitionLayout with a spring(stiffness=Spring.StiffnessMedium, dampingRatio=0.85) for a fluid card-to-detail transition."
- "This SwiftUI tab transition will use matchedGeometryEffect with a .smooth spring (response: 0.5, dampingFraction: 0.85) for a tactile, spatial feel."
- "This macOS dashboard will use 100ms opacity hover states (no scale on hover, desktop subtlety) and a Cmd+1-9 keyboard shortcut to navigate panels."
- "This Android header will use an AGSL shader bound to scrollOffset for a dynamic liquid-glass effect (Android 13+, with a static fallback below)."

**Self-check:** read your thesis back. If you can't immediately derive the CSS/JS properties from it, it's too vague. Rewrite.

**This is the first visual gate.** Offer the preview menu (see "Showing Your Work" above), then present both theses in the chosen mode. The visual thesis in particular is worth far more shown than described - "fluorescent chartreuse accents" is a guess until it sits next to the neutrals.

**Wait for explicit user validation of BOTH theses before moving on.** If the user pushes back, don't start over - ask what feels wrong and adjust.

---

### Phase 3 - DESIGN SYSTEM

Load the `ui-ux-pro-max` sub-skill and **run it**. **Phase 2 ended in a user gate, so this is a
new Bash call and `$SKILL_BASE` no longer exists.** Re-emit the resolution block from "Sub-skills
Path Detection" above in this same call, then:

```bash
load_skill ui-ux-pro-max

# Query it with the validated visual thesis, not with the raw user request. The thesis is the
# thing that was approved; the request was not. Product type, industry and the mood adjectives
# from Phase 2, in that order, work best.
python3 "$SKILL_BASE/ui-ux-pro-max/scripts/search.py" \
  "<product type> <industry> <mood adjectives from the visual thesis>" \
  --design-system -f markdown
```

**`-f markdown` is not optional.** The default `ascii` format emits raw ANSI colour escapes that
survive the pipe and land in context as garbage, at roughly 3.3x the tokens for the same content.

What comes back is a candidate palette with role names and CSS variable names, a font pairing
with a ready Google Fonts URL, an effects note and a list of anti-patterns for the style. Treat
it as **a proposal, not an answer**: it is a lookup against a static dataset and it has never
seen the project. Keep what serves the validated visual thesis, discard what fights it, and say
in one line what you took and what you dropped. A palette that contradicts the thesis the user
approved loses to the thesis every time.

If `python3` is unavailable or the script fails, say so in one line and derive the system from
the thesis by hand. The pipeline does not stop for this.

#### Stack-aware token generation

The MASTER.md design system file is canonical, but the generated **code** files match the detected stack:

- **Web stack detected**: generate Tailwind config / CSS variables (existing format). Tokens in CSS hex, `cubic-bezier(...)` easings, `rem` spacing. Output paired with `tailwind.config.js` extension or `:root { --token: ... }` CSS.
- **Android Compose stack detected**: generate Kotlin design tokens. Output `Theme.kt`, `Color.kt`, `Type.kt`, `Shapes.kt`, `Motion.kt` referenced from MASTER.md. Color tokens in `Color(0xFF...)`, typography in `TextStyle`, shapes in `RoundedCornerShape`, motion in `MotionScheme` (M3 Expressive when scope is hero / impactful). Spacing in `dp`.
- **SwiftUI stack detected (iOS / macOS / multi-target)**: generate Swift extensions. Output `Color+App.swift`, `Font+App.swift`, `Animation+App.swift`, `Shape+App.swift`. Color tokens via `Color("AssetName")` referencing the asset catalog (or `Color(red:green:blue:)` if no catalog), typography via `Font.system(...)` or `.custom(...)`, animations via `.spring(...)` / `.snappy` / `.bouncy` named presets. Spacing in `CGFloat` constants.
- **Compose Multiplatform stack detected**: generate Kotlin tokens in `commonMain` with `expect/actual` for fonts and platform-specific colors. Same structure as Android Compose, plus a section in MASTER.md describing per-platform deviations.
- **Multi-stack project** (e.g., web admin + native mobile app): generate MASTER.md with clearly delimited sections for each stack, and produce code files for each.

The MASTER.md document itself remains a single canonical source-of-truth file. The generated code files (Theme.kt / Color+App.swift / etc.) are children of MASTER.md and reference it.

Generate the complete design system based on both theses:

- **Color palette** - Primary, secondary, accent, neutrals, semantic (success/warning/error/info). Light + dark if needed.
- **Typography** - Font stack, size scale (fluid or fixed), weight usage, line-height rules.
- **Spacing** - Base unit, scale (4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px...).
- **Radii** - Border radius scale (none, sm, md, lg, full).
- **Shadows** - Elevation levels (0-4), consistent with visual thesis.
- **Base components** - Button, input, card, badge, link - styled per the theses.
- **Motion tokens** - Duration scale (fast/normal/slow), easing names, stagger delay.

#### MASTER.md

Create a `MASTER.md` at project root with the full design system. This file is the single source of truth. Every implementation decision references it.

#### MCP Tools (if available)

Check if these MCPs are connected and use them when available:
- **Stitch** - Generate mockups/wireframes
- **Nano Banana** - Generate visual assets (illustrations, icons, backgrounds)
- **21st.dev Magic** - Generate UI components from descriptions

If MCPs are not available, skip gracefully - the design system + code implementation is the core path.

#### Show it before Phase 4

Present the design system in the session's preview mode - announce the mode in one line, don't reopen the menu - and get validation before implementing anything. A palette and a type scale listed as hex codes and pixel values in a transcript are precise and completely unreviewable; every token in MASTER.md is about to be applied everywhere, so this is the cheapest place to catch a wrong one.

---

### Phase 4 - IMPLEMENT

Load sub-skills based on tech stack and interaction thesis.

**Always load** (via `load_skill <name>`, defined above: a missing module prints `NOT LOADED` and the pipeline carries on, so keep the list for the final report):
- `load_skill motion-principles` - the foundation

<!-- genjutsu:shared:load:start -->
**One module per shell call.** The output of a shell call over about 30,000 characters does not
arrive inline: you get a 2,000-character preview and a file path, and a module you could not
read is a module you did not load. So each loading call re-emits the skill-base block and loads
one module, which keeps its output under 25,000 characters: no module entry file is over that
cap, and `validate-skills.py` keeps it that way. Keep the tally as you go: `load_skill` prints
`NOT LOADED` for a missing module and carries on, and the final report lists both.

**Context layers** (load when applicable):

| Detected | Load |
|---|---|
| Mobile context (web mobile OR native iOS / Android) | `load_skill mobile-principles` |
| Desktop context (macOS OR web desktop with no mobile indicators) | `load_skill desktop-principles` |
| Audit explicitly requested OR scope=full | `load_skill design-audit` |
| Advanced UI/UX questions | `load_skill ui-ux-pro-max` |

**Stack-specific** (load by SCAN):

| Detected stack | Sub-skill to load |
|---|---|
| gsap | `load_skill gsap` |
| `motion` or `framer-motion` (same library, two package names) | `load_skill framer-motion` |
| Pure CSS / Tailwind / no lib | `load_skill css-native` |
| three / @react-three | `load_skill threejs-r3f` |
| Canvas / generative | `load_skill canvas-generative` |
| Android Compose | `load_skill compose-motion` (always) + `load_skill compose-graphics` (if scope=full or thesis is advanced - see below) |
| Compose Multiplatform | `load_skill compose-motion` + `load_skill compose-multiplatform` (always); `load_skill swiftui-motion` if iOS target detected and SwiftUI interop demanded; `load_skill compose-graphics` if advanced |
| SwiftUI iOS or macOS | `load_skill swiftui-motion` (always) + `load_skill swiftui-graphics` (if scope=full or thesis is advanced) |

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
- Work **page by page** or **component by component** - never try to do everything at once.
- Every color, font, spacing, shadow, radius MUST come from MASTER.md tokens. No magic numbers.
- Every animation MUST respect the interaction thesis (timing, easing, forbidden patterns).
- Apply the 5-state rule for interactive elements: **default, hover, focus, active, disabled**.
- Ask the user for validation after each major page/section before moving to the next.

---

### Phase 5 - AUDIT (never skip)

Load the `design-audit` sub-skill. **Phase 4 ended in a user gate, so `$SKILL_BASE` is gone
again.** Re-emit the resolution block in this same call, then:

```bash
load_skill design-audit
```

Run the full audit checklist matching the detected stack. `design-audit` supplies the greps; the split below decides what you may claim from them.

<!-- genjutsu:shared:audit:start -->
The closing step of this pipeline used to be twenty-five checkboxes, several of which name a
tool the agent cannot run. Ticking "60fps verified via Chrome DevTools" without opening Chrome
turns "I did not look" into "I looked and it is fine", which is worse than saying nothing.

So the checks are split. **Report the first group with the evidence you used. Never tick the
second group at all** - hand it over.

### Checked here, with evidence

Each line is reported as `check - verdict - the evidence`. The evidence is the grep you ran, the
value you computed, or the `file:line` you read. A verdict with no evidence beside it is not a
finding, and an item you could not check is reported as **not checked** rather than passed.

- [ ] **Reduced motion** honoured. Web: a `prefers-reduced-motion` block that actually degrades
      the animation, not an empty one. SwiftUI: `accessibilityReduceMotion`. Compose: a helper
      on `ValueAnimator.areAnimatorsEnabled()` / `Settings.Global.ANIMATOR_DURATION_SCALE`.
      Evidence: the file and line of the guard, and what it degrades to.
- [ ] **Exit animations** present wherever something unmounts. Evidence: the conditional render
      and its exit path, or the list of unmounts that have none.
- [ ] **No layout-property animation.** Nothing animating `width`, `height`, `top`, `left`,
      `margin` or `padding`; use transform, opacity or `graphicsLayer`. Evidence: the grep and
      its hits, or that it returned nothing.
- [ ] **Focus visible** on every interactive element, and no `outline: none` without a
      replacement. Evidence: the grep.
- [ ] **All five states** on interactive elements: default, hover or press, focus, active,
      disabled. Evidence: the states you found per component, and the ones missing.
- [ ] **Tokens, not magic numbers.** Colours and spacing come from the project's design tokens
      (MASTER.md when one exists). Evidence: the rogue values, with `file:line`.
- [ ] **Contrast** at least 4.5:1 for body text, 3:1 for large text and UI boundaries.
      **Compute it** from the token values you emitted; do not eyeball a swatch. Evidence: the
      pair and the computed ratio, e.g. `#831843 on #FDF2F8 = 9.4:1`.
- [ ] **Semantics.** Web: no clickable `div` without a role, `aria-hidden` on decorative motion.
      Compose: `Modifier.semantics` on custom interactive components. SwiftUI:
      `.accessibilityLabel` on controls that have no text. Evidence: the grep.
- [ ] **Web only.** Conditional renders wrapped in `AnimatePresence` or the framework's
      equivalent; `will-change` used sparingly and removed after the animation. Evidence: the grep.

### You must run these - not verified here

The agent cannot open a profiler, attach to a device, or move a pointer. These are reported as a
handoff block with the exact invocation, and marked **UNVERIFIED**. Do not tick them, do not
soften them, and do not omit the section because the rest looked clean.

| Target | What to run | Pass condition |
|---|---|---|
| Web | Chrome DevTools > Performance, record across the interaction | no frame over 16.7ms |
| Web | The page at 375 / 768 / 1024 / 1440 | no horizontal scroll, no clipped content |
| Web | The page with the OS "reduce motion" setting on | the degraded path actually runs |
| Compose | Layout Inspector > Component Tree > View Options > **Show Recomposition Counts** | counts stable while scrolling |
| Compose | `androidx.benchmark.macro` Macrobenchmark on a mid-range device | frame time under 16.67ms at 60fps, 8.33ms at 120fps |
| SwiftUI | Instruments > Animation Hitches | no hitch during the transition |
| SwiftUI | Reduce Motion on, Dynamic Type at 200% | nothing clipped, nothing that only moves |
| macOS | Pointer over every interactive element; keyboard through the whole view | hover states fire, focus ring visible, shortcuts bound |

If a preview or a dev server is already running and the user agrees, driving the browser to
collect the web rows is better than handing them over. Never start one just for the audit, and
never install anything for it.

**Report the two groups separately**, with the counts. "9 checked, 2 problems found, 8 handed
over" is an honest audit. A single list of ticks is not.

**Close the report with the modules**, always, as two lines of their own:

```
Modules loaded: motion-principles, framer-motion, design-audit
Modules not loaded: none
```

`Modules not loaded` names every module a `load_skill` call reported as `NOT LOADED`, and every
module the load tables called for that was never requested. Write `none` only when both are
empty. Shell state does not survive between calls, so this list is yours to keep from the first
load to the last: nothing in the shell remembers it for you.
<!-- genjutsu:shared:audit:end -->

Within the checked group, order the findings by severity: **Critical > Important > Nice-to-have**. The handed-over group is not ordered and not filtered - it goes over whole, because the user is the one who has to run it.

---

## Existing Project Protocol

When invoked on a project that already has design/styling:

1. Still run the full BRAINSTORM (Phase 1)
2. Acknowledge existing design, but the thesis overrides it
3. In Phase 4, **replace** existing design tokens/styles with the new design system
4. Preserve functionality and layout structure - only replace the visual layer

This is intentional: `/genjutsu:paint` rebuilds the visual universe. To enhance what exists, use `/genjutsu:cast` instead.

---

## Red Flags - You're About to Violate This Skill

| Thought | Reality |
|---------|---------|
| "The user already said 'minimal dark' - I have enough for a thesis" | Two words aren't five domains. Keep asking. |
| "I'll ask all five brainstorm questions at once" | One at a time. The answer to 'audience' changes how you ask about 'mood'. |
| "The user seems impatient, let's skip to coding" | Use the pressure protocol. A bad thesis costs days, not minutes. |
| "I'll pick colors that feel right" | Every token comes from MASTER.md. No freelancing. |
| "I'll do the whole site in one pass" | Page by page. Validate page by page. |
| "This animation would be cool even though the thesis says no bounce" | The thesis is law. Change it? Re-validate with the user first. |
| "The audit can wait, the user seems happy" | The audit is not optional. Phase 5 always runs - shortened on light scope, never skipped. |
| "The audit items all look fine, I'll tick them" | A tick is not a finding. Report the grep, the ratio, the file:line - or report it as not checked. |
| "I can't profile, so I'll leave that part out" | The handoff block is the deliverable for those. Omitting it reads as a pass. |
| "I'll interpret 'yeah something like that' as a yes" | That's not confirmation. Ask which part resonates. |
| "I'll list the palette as hex codes, that's precise" | Precise and unreviewable. Show it in the session's preview mode. |
| "I'll ask again how they want to see the design system" | Asked once, sticks for the session. Announce the mode and go. |
| "The preview page looks good, I'll build the app from it" | The preview is throwaway. Build from MASTER.md. |
