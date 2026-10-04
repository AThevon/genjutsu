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
| **Entry point** | Adapts to existing code | Mandatory brainstorm; on an existing design, asks preserve, partial or redesign |
| **Discovery** | Lightweight, only when vague | Full brainstorm, never skipped |
| **Design system** | Optional, implicit | Required, generates MASTER.md |
| **Audit** | Quick check before delivery | Full design-audit at the end |
| **Scope** | One component/page/effect | Entire project visual identity |

`/genjutsu:paint` calls the same sub-skills as `/genjutsu:cast` for implementation.

A whole site or web app built from real material is the job of the third pipeline,
`/genjutsu:bunshin`: a team of subagents under one art director, with independent reviews
until only minor issues remain or the tier's round cap is reached. paint proposes it right after
the stack scan when the brief is that size, the stack is web or there is no project yet, and the
host can spawn subagents, and switches only on a yes.

---

## Iron Rules

1. **Never skip the brainstorm.** Not even if the user says "just make it look good." Especially then. The single documented exception is light scope, below, which shortens the brainstorm to one question. It never removes it. With nobody answering, see "When nobody is answering": the questions are answered from the brief, as assumptions.
2. **One question at a time during brainstorm.** Never bundle. The second question depends on the first answer.
3. **Never proceed without the theses validated.** Visual + interaction, both explicitly approved. The one exception is light scope, below: no visual identity is at stake there, so the interaction thesis alone is required - and it is still validated explicitly, never assumed. With nobody answering, see "When nobody is answering".
4. **Every design token comes from MASTER.md.** No magic numbers, no rogue hex values. On light scope, where no MASTER.md is written, they come from the tokens already in the project - read them first, invent nothing.
5. **Every animation respects the interaction thesis.** Timing, easing, forbidden patterns - no exceptions.
6. **Never install a dependency without asking.** With nobody answering, never install one (see "When nobody is answering").
7. **Work page by page, validate page by page.** Never try to do everything at once.
8. **The audit is not optional.** Phase 5 always runs, even if the user seems happy. On light scope it shortens to the quick check - thesis against code, reduced-motion, exit animation, 60fps - but it never disappears.
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
| 5 AUDIT | full design-audit sub-skill | the quick check: thesis against code, reduced-motion, exit animation, 60fps |

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
if [ -d /mnt/skills/plugins ] || [ -d /mnt/skills/user ]; then
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

- **The message that carries it names the thesis in plain text.** Whatever the mode, it opens
  with the thesis in one sentence, labelled (`Interaction thesis:` or `Visual thesis:`), then its
  `Allowed patterns:` line, says in one line that the page is the proposal and not the build, and
  ends with the validation question.
  It holds no implementation: code starts in a later turn, after a yes. Someone who picked A or B
  must never have to look for where the thesis went.
- **It is throwaway. It never becomes the implementation.** Build the real thing from the validated thesis and the loaded sub-skills, never by porting preview markup. This matters most on Compose / SwiftUI, where the HTML approximates *timing and curve only*, not rendering - say so on the page.
- Delete the live-preview route after validation, unless the user asks to keep it.
- Never install a dependency to build a preview.
- Never start a dev server without asking.
- Only show values that are in the thesis. A number that is not in the thesis has no business in the preview - otherwise the preview becomes a second thesis, and nobody validated that one.
- A web face the preview cannot load in this session is still shown under its own name, set in its fallback stack and labelled `not rendered in this session`. Never swap it for a face the session can render: what the sandbox can fetch is not what the site will ship.
<!-- genjutsu:shared:preview:end -->

<!-- genjutsu:shared:headless:start -->
## When nobody is answering

Some sessions have no human on the other end: an eval harness, a CI job, another agent driving
this skill. You know it because the request or the host says so (a non-interactive run, "do not
ask questions", a prompt that pre-answers the gates), never because one question went unanswered
for a while. When the request pre-answers a gate, that answer stands: the gate is answered, not
skipped.

In such a session every gate still produces its output. What changes is that nobody validates it:

- **Discovery and brainstorm questions:** do not ask them. Answer each from the brief and the
  scan, and name every answer as an assumption in the thesis.
- **Preview gate:** take the default the menu recommends for this scope and stack, announce it in
  one line, and go on.
- **Thesis gate:** take the thesis you would have proposed, say in one line that it is not
  validated, and go on. The final report prints it, marked **UNVALIDATED**.
- **Dependencies:** never install one. Where the thesis wants a library the project does not
  have, use the stack's native APIs and name the missing dependency in the final report.

Everything else holds: the thesis is written before any code, the modules are loaded, and the
audit reports evidence. A headless run skips the waiting, never the work.
<!-- genjutsu:shared:headless:end -->

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
#   0. claude.ai, /mnt/skills/plugins (or the older /mnt/skills/user): the
#      genjutsu bundle.
#   1. This skill's own directory: its _jutsu, or the _jutsu next to it.
#   2. ${CLAUDE_PLUGIN_ROOT}/skills/_jutsu, when Claude Code substituted it.
#   3. Bounded probes: .claude/skills and .agents/skills from $PWD upward, then
#      the skills directories installers write to, then /sessions (Cowork).
#   4. The Claude Code plugin cache, newest version. Last on purpose: an old
#      plugin install must never win over a newer bundle.
# Resolved from scratch every time. A cache was tried here and removed: after a
# plugin update the old version directory is still on disk, so a cached path
# passes an "is it a directory" check and serves the previous release.

# No function below names a positional parameter (a dollar sign followed by a
# digit, or the whole argument list). Claude Code replaces those tokens in a
# skill's text with the words typed after the slash command, before the model
# reads this block: after "/genjutsu:cast make the cards feel physical", a path
# built from a function's first parameter would read "the/motion-principles/...",
# the second word typed. Each function reads its arguments with a bare
# `for name; do`, which walks the positional parameters without writing any out.

# A _jutsu directory counts only if it holds motion-principles. The shared
# skills directory of npx serves about 80 agents, so a directory name proves
# nothing. The entry file is named SKILL or GUIDE depending on the artifact
# (the bundle renames it at packaging time), so the name is assembled from
# parts: spelled out in full, the packaging step would rewrite it too.
genjutsu_is_jutsu() { # <candidate _jutsu directory>
  for jutsu_dir; do
    for d in SKILL GUIDE; do
      [ -f "$jutsu_dir/motion-principles/$d.md" ] && return 0
    done
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
# 0. claude.ai mounts uploaded skills under /mnt/skills/plugins/<name>/ (seen on
# 2026-09-28), next to the user's other skills; /mnt/skills/user before that.
# GENJUTSU_CLAUDE_AI_ROOT stands in for /mnt/skills in the test suite only.
# Only a _jutsu holding motion-principles counts: a mount without genjutsu in it
# must never pass for a resolved base.
genjutsu_claude_ai="${GENJUTSU_CLAUDE_AI_ROOT:-/mnt/skills}"
for claude_root in "$genjutsu_claude_ai/plugins" "$genjutsu_claude_ai/user"; do
  [ -z "$SKILL_BASE" ] && [ -d "$claude_root" ] || continue
  SKILL_BASE="$(find -L "$claude_root" -maxdepth 2 -type d -name _jutsu 2>/dev/null | genjutsu_first_jutsu)"
done
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
  echo "  genjutsu's pipelines do not work without them. Install the full bundle:" >&2
  echo "    any agent    npx skills add https://genjutsu.athevon.dev -g" >&2
  echo "    Claude Code  /plugin marketplace add AThevon/genjutsu, then /plugin install genjutsu" >&2
  echo "    claude.ai    upload genjutsu.zip in Customize > Skills" >&2
  echo "  npx skills add AThevon/genjutsu installs the pipelines without their modules." >&2
  echo "  Tried: /mnt/skills/plugins, /mnt/skills/user, GENJUTSU_SKILL_DIR (${GENJUTSU_SKILL_DIR:-empty}) and its parent," >&2
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
load_skill() { # <module>
  skill_name=""
  for skill_arg; do skill_name="$skill_arg"; break; done
  for d in SKILL GUIDE; do
    if [ -n "$skill_name" ] && [ -f "$SKILL_BASE/$skill_name/$d.md" ]; then
      cat "$SKILL_BASE/$skill_name/$d.md"
      return 0
    fi
  done
  echo "genjutsu: sub-skill '$skill_name' NOT LOADED - not found under $SKILL_BASE. Carry on, and list it under 'Modules not loaded' in the final report." >&2
  return 1
}

# Print one reference file of a module: load_ref <module> <path inside it>.
load_ref() { # <module> <path inside it>
  ref_module=""; ref_path=""; ref_n=0
  for ref_arg; do
    ref_n=$((ref_n + 1))
    case "$ref_n" in
      1) ref_module="$ref_arg" ;;
      2) ref_path="$ref_arg"; break ;;
    esac
  done
  if [ -n "$ref_module" ] && [ -n "$ref_path" ] && [ -f "$SKILL_BASE/$ref_module/$ref_path" ]; then
    cat "$SKILL_BASE/$ref_module/$ref_path"
    return 0
  fi
  echo "genjutsu: reference '$ref_module/$ref_path' NOT LOADED - not found under $SKILL_BASE. Carry on, and say so in the final report." >&2
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

<!-- genjutsu:shared:escalate:start -->
**When the job is a whole site: propose bunshin.** genjutsu has a third pipeline for the one job
this one is too small for. `bunshin` builds a whole website or web app with a team of subagents
under one art director, with Impeccable drawing the direction when it is installed, and it loops
independent reviews and fixes until only minor issues remain, the tier's round cap is reached, or
a round fixes nothing. It is heavy, so it is proposed, never started on its own.

Propose it once, right after the scan and before anything else you would ask, when **all three**
of these hold:

- the target is a whole site or web app: several pages or screens, from scratch or as a full
  redesign;
- the stack is web, or there is no project yet;
- this session can spawn subagents: a subagent tool or a multi-agent workflow tool is among the
  tools it exposes (in Claude Code, `Agent` or `Workflow`);

and **at least one** of these:

- there is real material to harvest: a social profile, a current site, brand assets, documents;
- the site serves two audiences, or two languages;
- it is a first version meant for a client or a stakeholder;
- the request asks for the best possible, the full treatment, all out.

Before writing the proposal, check whether Impeccable is installed:

```bash
for d in .claude/skills/impeccable .agents/skills/impeccable "$HOME/.claude/skills/impeccable" "$HOME/.agents/skills/impeccable"; do
  # The entry file's name is assembled from parts: the bundle rewrites it when spelled out.
  e="$d/SKILL"
  if [ -f "$e.md" ]; then echo "impeccable: $d"; break; fi
done
```

The proposal is one message, then wait:

> "This is a whole site<, from scratch | , a full redesign>. genjutsu has a pipeline for exactly
> that: `bunshin`. It
> harvests your real material, researches with parallel agents, lets Impeccable draw the
> direction (<installed here | not installed: bunshin runs without it, better with it>), builds
> the pages with parallel agents, and reviews and refines them until only minor issues remain,
> the round cap of the tier you pick is reached, or a round fixes nothing.
> It asks you twice: once to start, with a budget, and once to choose the direction. One run has
> been measured, a seven-page site: about 10.5 million subagent tokens over six to eight hours.
> The tiers are estimated from it, from about 6 to about 13 million, and scale with the pages.
> Say `bunshin` to switch, or I carry on with this pipeline."

- **A yes**: stop this pipeline and load bunshin. Invoke it as a skill when the host lists
  `genjutsu:bunshin`; otherwise read its entry file next to this one, in
  `$GENJUTSU_SKILL_DIR/../bunshin/` (the one Markdown file at the top of that folder), and follow
  it from its first step.
- **Anything else**: carry on here, and do not propose it again in this session.
- **Never** when one of the first three conditions fails: a host that cannot spawn subagents
  cannot run bunshin, and a native stack is not covered by it yet.
- **With nobody answering**: do not propose and wait. Say in one line that bunshin would fit this
  brief, carry on with this pipeline, and name bunshin in the final report.
<!-- genjutsu:shared:escalate:end -->

**Declare your read before the first question.** The scan has run and the request is in front of
you. Before the first brainstorm question, say what you already believe in one line, so the user
corrects a wrong premise before it steers every question after it:

> "My read so far: <what> for <whom>, heading toward <direction>, on <stack>. Correct me before I ask anything."

`<what>` is the product and `<whom>` the audience as the request states them, `<direction>` the
mood the request or the existing design suggests, `<stack>` what the scan found. A slot you cannot
fill is said as unknown ("for an audience I can't tell yet"), never guessed; the unknown slots are
where the brainstorm starts. The line is its own message: send it and wait. A correction replaces
the slot it names; a go-ahead means the read stands. It is not a brainstorm question and does not
count against light scope's single question, and it is not a thesis: nothing in it is validated
until Phase 2. When no human is in the session to answer, state the read and carry on with it as
written.

**If legacy mixed detected** (XIB / storyboard / layout XML / setContentView(R.layout.\*)):

Ask exactly one question during brainstorm:

> "I see your project mixes [XML layouts / XIBs / classic Activities] with modern UI. For this task, should I stay on pure [Compose/SwiftUI], or integrate into a legacy screen?"

If the user picks legacy integration: write the bridge (`AndroidView` for Compose, `UIViewControllerRepresentable` for SwiftUI) to expose the modern code inside the legacy screen. Never generate new legacy code (no XML, no XIB, no setContentView).

**If the project already has a visual identity** (CSS variables or a Tailwind theme, `Theme.kt` /
`Color.kt`, `Color+App.swift` or an asset catalog, a logo, a live brand):

**First, take the inventory of what is already there.** On a web stack, in one shell call,
re-emit the skill-base block and run `python3 "$SKILL_BASE/design-audit/scripts/audit.py" . --group tells`.
Show the result as one short block, **What this project already does by reflex**, counted by
family, with two or three `file:line` examples each. Each of them is settled in the theses,
according to the mode the question below sets: in preserve mode they stay by default and go into
the `Allowed patterns:` line as the brand's own; in partial mode they go by default inside the
areas the user named; in redesign mode they go by default everywhere. The user can keep or drop
any one of them by name at the thesis gate.

Ask exactly one mode question during brainstorm, right after the legacy question when both apply:

> "This project already has a look. Should I preserve the brand and build within it, change part of it, or redesign it?"

- **Preserve** - the theses describe the brand as it is and add only what it lacks (motion,
  states, missing steps in a scale). Existing tokens stay.
- **Partial** - the user names what may change ("type and motion, not the colors"). The theses
  change the values in those areas, under the existing token names, and nothing else.
- **Redesign** - the theses replace the whole visual layer, existing tokens included.

The chosen mode goes into the visual thesis as one explicit clause ("preserving the existing
palette and logo"), so the Phase 2 gate validates it with everything else. What each mode lets
the thesis replace is in "Existing Project Protocol" below. Light scope does not ask: no visual
identity is at stake there, so it is preserve by definition.

**The five domains to cover:**

1. **Product** - What is it (app, landing page, portfolio, SaaS, e-commerce, blog, dashboard...), and what is true of it that its closest neighbour, or a template, could not claim?
2. **Audience** - Who uses it? (devs, designers, general public, enterprise, kids, luxury...)
3. **Mood** - 3 to 5 adjectives that define the visual feel
4. **References** - Sites, screenshots, mood boards the user brings. Never suggest famous ones yourself: that anchors the thesis on someone else's look.
5. **Tech stack** - What's already in place? Or starting from scratch?

**How to ask:** One question at a time, starting with the least obvious domain. If you already know the tech stack from scanning `package.json`, don't ask - start with mood or audience instead. Each answer reshapes how you ask the next question.

**How to handle vague answers:**

When the user says "modern" or "clean" or "I don't know, just make it nice":

1. **Validate** - "That's a starting point. Let's make it precise."
2. **Go back to the product** - "Clean compared to what? Tell me one thing that is true of this product and that its closest competitor could not say about itself." Answer a mood word with a fact about the product, never with another brand's look: "like Stripe, like Linear, like Apple" anchors the thesis on three famous defaults.
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
- **Typography spirit** - the display face by name and why this one, or `display face: undecided, chosen at the design-system gate`; serif/sans/mono, weight usage, size contrast
- **Spacing philosophy** - dense/airy, base unit feel
- **Component style** - rounded/sharp, bordered/filled, elevated/flat

> Example: "Dark neo-brutalist interface with bold monospace type, fluorescent chartreuse accents, generous whitespace, raw-edged components with offset shadows."

**Self-check:** read your thesis back. If any of the four areas is missing or vague ("nice typography"), rewrite it before presenting.

**Guessability test:** could someone write this thesis from the product category alone (a fintech gets navy and a clean sans, a design studio gets an editorial serif on paper)? Then it is the category's default, not a decision: rewrite it from what is true of this product.

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

**Under the two theses, one line naming what it allows.** `Allowed patterns:` followed by every
deliberate device the design relies on that a reader could take for decoration or habit: mono
labels, hairline rules, a paper ground, grain, a glow, a looping animation, a code label, a live
clock. Write `Allowed patterns: none` when there are none. The audit reads this line: a tell
counts as allowed only when it is listed here, so a mood word never lets one through, and the
user sees the list before saying yes.

**This is the first visual gate.** Offer the preview menu (see "Showing Your Work" above), then present both theses in the chosen mode. The visual thesis in particular is worth far more shown than described - "fluorescent chartreuse accents" is a guess until it sits next to the neutrals.

**Wait for explicit user validation of BOTH theses before moving on.** If the user pushes back, don't start over - ask what feels wrong and adjust.

#### The three dials (after validation)

Once both theses are validated, read three values off them. Phase 3 passes them to `search.py`
as 1-10 dials:

| Dial | Read it from | 1 | 10 |
|---|---|---|---|
| `--variance` | the visual thesis: layout and component style | centered, symmetric, minimal | bold, asymmetric, experimental |
| `--motion` | the interaction thesis: timing range, scroll behavior, forbidden patterns | subtle | complex, choreographed |
| `--density` | the visual thesis: spacing philosophy | spacious | dense, dashboard |

Derive each value from a clause of the validated theses, never from the raw brief and
never from a default. "Generous whitespace" settles density low; "fast and dry, no scroll
reveals" settles motion low. A dial the theses do not settle is left out of the call entirely:
an unsent dial changes nothing, a guessed one biases the lookup toward something nobody
approved. Write each value down with the clause it came from; they are shown with the design
system before Phase 4.

Light scope has no Phase 3, so it sets no dial.

---

### Phase 3 - DESIGN SYSTEM

**On a web stack, load `tells` first** (light scope never reaches this phase), in a shell
call of its own, before the design-system query. Phase 2 ended in a user gate, so re-emit the
resolution block in that call:

```bash
# (skill-base block re-emitted above this line)
load_skill tells
load_ref tells references/web.md
```

The query below answers from a static dataset that has never seen the project. `tells` is what
lets you recognise which of its proposals are reflexes the validated thesis never asked for.

Load the `ui-ux-pro-max` sub-skill and **run it**. **Phase 2 ended in a user gate, so this is a
new shell call and `$SKILL_BASE` no longer exists.** Re-emit the resolution block from "Sub-skills
Path Detection" above in this same call, then:

```bash
load_skill ui-ux-pro-max

# Query it with the validated visual thesis, not with the raw user request. The thesis is the
# thing that was approved; the request was not. Product type, industry and the mood adjectives
# from Phase 2, in that order, work best.
# Append only the dials Phase 2 settled (see "The three dials"); drop each flag the theses
# left open, and never send a dial with a made-up value.
python3 "$SKILL_BASE/ui-ux-pro-max/scripts/search.py" \
  "<product type> <industry> <mood adjectives from the visual thesis>" \
  --design-system -f markdown \
  --variance <V> --motion <M> --density <D>
```

**`-f markdown` is not optional.** The default `ascii` format emits raw ANSI colour escapes that
survive the pipe and land in context as garbage, at roughly 3.3x the tokens for the same content.

**What the dials do on this path.** With `--design-system -f markdown`, `--variance` biases which
style the lookup picks and `--motion` attaches a motion snippet of the matching intensity: both
change the proposal. `--density` does not. On this path it only prints its label under "Design
Dials": the spacing scale it maps to is written by `--persist` alone, and paint does not persist.
So derive the spacing scale in MASTER.md by hand, from the spacing philosophy of the visual
thesis, and let the density label say what that scale has to feel like. The motion snippet is
GSAP code: on any other stack read it for its duration and easing only, and never install GSAP
because of it.

What comes back is a candidate palette with role names and CSS variable names, a font pairing
with a ready Google Fonts URL, an effects note and a list of anti-patterns for the style. Treat
it as **a proposal, not an answer**: it is a lookup against a static dataset and it has never
seen the project. Keep what serves the validated visual thesis, discard what fights it, and say
in one line what you took and what you dropped. A palette that contradicts the thesis the user
approved loses to the thesis every time.

Filter it twice before keeping anything: through the thesis, and through `tells`, loaded just
before this call on a web stack (on Compose and SwiftUI `tells` is not loaded, and the thesis
filters alone). The dataset matches keywords, so it hands back exactly the reflex picks `tells`
describes:

- **The display face**, serif or sans, stays only when the visual thesis names it and says why
  that face: what it carries for this product that another would not. "Creative", "premium" and
  "editorial" summon an editorial serif; "clean", "modern" and "SaaS" summon a heavy grotesque.
  Neither set of words is a reason, and trading one reflex for the other is not a decision.
  When the thesis left the face undecided, choose it here: name it and say why in one line. That
  line amends the visual thesis when the design system is validated, and Phase 4 and the audit
  read the amended sentence, never the original gap.
- **A warm paper ground** (a faintly warm off-white behind near-black ink and one red accent) is
  the palette the model reaches for on almost any brief. It stays only when the thesis says why
  this product belongs on paper.
- **Glassmorphism**, which the dataset attaches to "SaaS", does not pass unless the thesis asks
  for it by name.
- Anything else in the output that `tells` lists as a reflex is held to the same test: named in
  the thesis, or dropped. The one line that says what you took and dropped also says what this
  filter removed.

**A face this session cannot render is still the face.** A blocked font request or a sandbox
with no network is a fact about this session, not about the site. When the user has approved a
web face (by name, or by saying a Google Fonts link or a hosted file is fine) or the project
already loads one, never trade it for a face you can render here: that is the system face
winning by default, and the thesis loses a decision it made. Never add a third-party font
request the user has not agreed to, either: ask once, as for any new request. Then use it:

- Load it the way the stack loads fonts (the Google Fonts URL or `next/font` on web, the font
  files bundled on Compose and SwiftUI), with `font-display: swap` on web, behind a fallback
  stack matched to it in width, x-height and figure style, named in MASTER.md
  (`"Fira Sans", "Segoe UI", Roboto, system-ui, sans-serif`), with `size-adjust` and the metric
  overrides when the fallback shifts the layout.
- Check what the thesis needs from it (tabular figures, a weight, a glyph such as the degree
  sign) in its published data when this session can read it: its specimen page, its OpenType
  feature list. When it cannot, say which feature is unchecked. An unchecked feature is a
  reason to tell the user, never a reason to drop the face.
- Say it where the user reads it: in the design-system message, the preview, and the final
  report, as `Fira Sans: approved, loaded with a matched fallback, not rendered in this
  session.` The audit hands the check over: the page online, the face loaded, the features
  the thesis relies on in place.

paint never passes `--persist`, so the component values hardcoded in the MASTER.md template of
`design_system.py` never reach the project: MASTER.md is written here, from the validated theses
and the tokens kept above. If paint ever persists, rewrite those component values from the
tokens before keeping the file.

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

Present the design system in the session's preview mode - announce the mode in one line, don't reopen the menu - and get validation before implementing anything. If Phase 3 chose the display face, show its one-line reason with it: validating the design system validates that amendment to the visual thesis. A palette and a type scale listed as hex codes and pixel values in a transcript are precise and completely unreviewable; every token in MASTER.md is about to be applied everywhere, so this is the cheapest place to catch a wrong one.

Show the dials beside it: each value sent to `search.py` with the thesis clause it came from,
and each dial left out with the reason.

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
`NOT LOADED` for a missing module and carries on, and the final report lists both. Load each
module whole: never pipe `load_skill` or `load_ref` into `head`, `tail`, `sed`, or `grep`, since
the batching rule above already keeps each call under the limit, and a truncated module is a
module not loaded.

**Context layers** (load when applicable):

| Detected | Load |
|---|---|
| Web stack and scope is medium or full | `load_skill tells` (dedicated call, with `references/web.md`, see below) |
| Mobile context (web mobile OR native iOS / Android) | `load_skill mobile-principles` |
| Desktop context (macOS OR web desktop with no mobile indicators) | `load_skill desktop-principles` |
| Audit explicitly requested OR scope=full | `load_skill design-audit` |
| Advanced UI/UX questions | `load_skill ui-ux-pro-max` |

**`tells` gets a shell call of its own.** With its web reference it weighs about 20,000
characters, too close to the point where a shell call's output stops arriving inline to share a
call with any other module. Re-emit the skill-base block in that call, then:

```bash
# (skill-base block re-emitted above this line)
load_skill tells
load_ref tells references/web.md
```

It loads after the thesis gate and before any visual choice is frozen: the validated thesis says
which patterns are wanted, and `tells` names the reflexes nobody asked for. Never on a Compose or
SwiftUI stack, never on light scope. In paint this row is already met: Phase 3 loads `tells`
before the design-system query.

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

- [ ] **Thesis against code.** First, because every check below assumes the code is the thesis
      that was validated. For each promise the validated thesis actually makes (durations,
      easing, springs, palette, type, layout family) give the `file:line` that holds it, or
      "not found". A thesis that makes no palette or type promise, an interaction thesis alone,
      gets no palette or type line. A promise with no `file:line` is a problem found, not a
      pass. Honest downgrade: when promised motion cannot be shipped working, ship the
      static version, say so here, and name the promise that was dropped; it counts as a
      problem found. Never ship motion that is half broken to keep a promise on paper.
      Evidence: one line per promise, e.g. `hover 180ms ease-out - src/Card.tsx:42`.
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
- [ ] **Tells confronted with the thesis.** Only when `tells` was loaded. In one shell call,
      re-emit the skill-base block and run
      `python3 "$SKILL_BASE/design-audit/scripts/audit.py" . --group tells`, whether or not
      `design-audit` was loaded. Evidence, for each finding: either the problem you kept, with its
      `file:line`, or the entry of the thesis's `Allowed patterns:` line that names it. A kept tell
      counts among the problems found. An allowed one is listed as "allowed by the thesis", with
      that entry quoted, and is not a problem. The manual reads `tells` lists (fake product in
      divs, repeated layout family, floating corner paragraph, copy register, copy held in
      JavaScript data) are reported the same way.
      Each finding has one of three outcomes, never a fourth: **allowed by the thesis**, its
      `Allowed patterns:` entry quoted; **not this tell**, only when the detection contradicts the
      entry's own marker (the loop reports a real loading state, the blur is a modal backdrop, the
      matched line is not displayed text), with the `file:line` that proves it and never on a matter
      of taste; or **a problem**. Fix before you report, and only what this run introduced: a problem
      on a line this run wrote (read `git diff` when the project has one) is removed or rewritten,
      then this check runs again, two passes at most, and what still fails is reported with its
      `file:line`. A tell that was already in the project, on a line this run did not write, is
      never changed here: it is listed for the user. Nothing on the protected list of an existing
      project (public token names, URLs, navigation labels, form field names, logo, legal mentions)
      is changed by this step.

### You must run these - not verified here

The agent cannot open a profiler, attach to a device, or move a pointer. These are reported as a
handoff block with the exact invocation, and marked **UNVERIFIED**. Do not tick them, do not
soften them, and do not omit the section because the rest looked clean.

| Target | What to run | Pass condition |
|---|---|---|
| Web | Chrome DevTools > Performance, record across the interaction | no frame over 16.7ms |
| Web | The page at 375 / 768 / 1024 / 1440 | no horizontal scroll, no clipped content |
| Web | The page with the OS "reduce motion" setting on | the degraded path actually runs |
| Web | The page online, when a web face was not rendered in this session | the face loads instead of its fallback, with the figures and weights the thesis relies on |
| Compose | Layout Inspector > Component Tree > View Options > **Show Recomposition Counts** | counts stable while scrolling |
| Compose | `androidx.benchmark.macro` Macrobenchmark on a mid-range device | frame time under 16.67ms at 60fps, 8.33ms at 120fps |
| SwiftUI | Instruments > Animation Hitches | no hitch during the transition |
| SwiftUI | Reduce Motion on, Dynamic Type at 200% | nothing clipped, nothing that only moves |
| macOS | Pointer over every interactive element; keyboard through the whole view | hover states fire, focus ring visible, shortcuts bound |

If a preview or a dev server is already running and the user agrees, driving the browser to
collect the web rows is better than handing them over. Never start one just for the audit, and
never install anything for it.

**Report the two groups separately**, with the counts. "11 checked, 2 problems found, 8 handed
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
2. Ask the mode question in Phase 1: preserve the brand, partial, or redesign. The mode decides what the thesis may replace: nothing already defined in preserve mode, only the areas the user named in partial mode, the whole visual layer in redesign mode
3. In Phase 4, existing design tokens are **replaced only in redesign mode**. In preserve mode, MASTER.md takes the existing tokens as they are and adds the new ones beside them. In partial mode, it keeps every existing token name, changes the values only in the areas the user named, and adds new tokens beside them
4. Preserve functionality and layout structure - only replace the visual layer

In all three modes, none of these change without the user's explicit agreement, asked item by
item: public token names (code outside this project may import them), URLs and routes,
navigation labels, form field names, the logo, legal mentions.

Before writing any token file, show the diff between the existing tokens and the new ones
(renamed, changed, added, removed) and wait for approval. After writing, build with the stack's
own command: `tsc --noEmit` or the project's build script (`npm run build` or its pnpm / yarn
equivalent) on web, `./gradlew assembleDebug` on Android, `xcodebuild -scheme <scheme> build` on
Apple. When the build cannot run here, hand it over marked **UNVERIFIED** with the exact command,
like the handed-over group of the audit.

The mode answers "rebuild or enhance?" inside paint: preserve mode enhances a brand without
replacing it. `/genjutsu:cast` stays the entry point for one effect or one component.

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
| "I can't render the approved font here, the system face is safer" | The sandbox is not the site. Load the approved face behind a matched fallback and say it was not rendered here. |
| "This is a whole site, I'll switch to bunshin, it is clearly better" | Propose it once, with its cost, and switch only on a yes. It spends millions of tokens. |
