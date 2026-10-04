---
name: bunshin
description: "Summon shadow clones: genjutsu's full-scale pipeline for a whole website or web app, from scratch or as a full redesign. Harvests the client's real material, researches in parallel, lets Impeccable lead the direction and genjutsu the motion, builds the pages with parallel agents, then loops fixes, verdicts and a cold-eyes art director until only minor issues remain, the round cap of the chosen tier is reached, or a round fixes nothing. Announces its cost first and asks twice. Web. Needs a host that can spawn subagents."
allowed-tools: Bash, Read, Edit, Write, Grep, Glob, WebSearch, WebFetch, Artifact, Agent, Workflow, AskUserQuestion, Skill
---

# Bunshin - The Shadow Clones

> One art director, many clones. You keep the vision; the clones carry the width.
> This is genjutsu's heaviest pipeline. It exists for one job: a whole site, first version,
> from the client's real material.

You direct. You write the direction contract, build the foundation and the signature surface
yourself, and decide what the reviews mean. Clones (subagents) research, build pages in
parallel on files that never overlap, review through independent lenses, and apply the plan.
Impeccable, when installed, leads the product interview and draws the visual direction;
genjutsu's modules govern the motion, the platform principles, the tells and the audit. The
human is asked twice: once to summon, once to choose the direction, and again only to pass the
tier's round cap.

---

## Voice

This skill speaks in two registers:

**During execution** - light ninja flair, short.
- "Summoning four clones for the research."
- "The clones return: six pages, five builds green."
- "Sealing round two."

**In reports, summaries and gate messages** - plain, factual, dev-readable. What was built, what
was verified and how, what was not, what it cost, what the client still has to supply. No mystic
prose. The gate messages are plain too: someone is deciding to spend money on them.

---

## bunshin, paint, cast

| | `/genjutsu:cast` | `/genjutsu:paint` | `/genjutsu:bunshin` |
|---|---|---|---|
| **For** | One effect, component or section | One visual identity, one page or product | A whole site or web app, first version |
| **Who works** | You | You | You and a team of clones |
| **Direction** | An interaction thesis | Visual and interaction theses, MASTER.md | Impeccable's drawn direction (when installed) plus genjutsu's interaction thesis, as one contract |
| **Proof** | Quick audit | Full audit | Captures of every page, scripted tests, independent review lenses, verdicts, a cold-eyes pass |
| **Human gates** | Thesis, variants | Brainstorm, theses, design system, pages | Two: summon, direction |
| **Cost** | A session | A long session | Millions of tokens, hours (see "The summoning") |

---

## Iron Rules

1. **The summoning comes first.** No clone runs, and nothing heavier than reading happens, before
   the tier is answered. With nobody answering, see "When nobody is answering".
2. **Ask twice, then decide from evidence.** The summoning and the direction are the user's.
   Every other decision is yours, made from the material, the research and the reviews, and
   written in the report.
3. **One art director.** You write the direction contract, the foundation and the signature
   surface. Clones build inside the contract and never redefine it.
4. **Never code without a validated thesis.** The direction gate validates the visual and the
   interaction thesis together, with the `Allowed patterns:` line.
5. **Disjoint ownership.** Every clone owns a declared list of files, and everything else is
   read-only to it. A shared need is a request, never an edit.
6. **No dev server, no shared browser.** Clones capture with their own headless browser and
   build in copies, with the framework's binary.
7. **Evidence or it did not happen.** Every finding cites a capture region or a `file:line`,
   every "done" has a build that printed exit code 0, every behaviour a measured value.
8. **Nothing invented.** Facts come from the material and the answers. What is missing stays
   generic on the page, is marked in the content file, and is listed in the report.
9. **The loop ends on a rule.** Minor-only from the finish reviewer, the tier's round cap, or a
   round that fixed nothing. Never open-ended, never past the cap without asking.
10. **Never install a dependency without asking.** Impeccable and browser tooling included. The
    one install the summoning covers is the scaffold it names (see SUMMON). With nobody
    answering, nothing beyond it.
11. **Nothing leaves the machine unasked.** No commit, no push, no deploy, no publish.
12. **Web only, for now.** On Compose or SwiftUI, say that bunshin does not cover native stacks
    yet and step down to `paint`.

---

## Step down, when this is not the job

bunshin is the wrong tool for anything smaller than a whole site. Recognise it at READ and say so
in one line before anything is spent:

| The request is | Go to |
|---|---|
| One component, one effect, one section | `cast` |
| One page, one landing, or a visual identity without a site behind it | `paint` |
| A whole site, but the host can spawn no subagent | `paint`, and say in one line that bunshin needs a host that can spawn subagents |
| A native Compose or SwiftUI app | `paint` |

> "This is one landing page, so paint is the right pipeline, not bunshin. Running paint."

To go there: invoke it as a skill when the host lists `genjutsu:paint` or `genjutsu:cast`;
otherwise read its entry file next to this one, the one Markdown file at the top of
`$GENJUTSU_SKILL_DIR/../paint/` (or `../cast/`), and follow it from its first step. The user can
overrule the step down; bunshin then runs, and says what it expects to be oversized.

---

## What this host can summon

Check once, at READ. Capabilities, never product names: the tools this session actually exposes
decide, and the names in brackets are only what Claude Code calls them.

- **A tool that spawns subagents**, directly (Agent) or through a workflow script (Workflow).
  Without either there are no clones: step down. With the workflow tool, the templates run as
  written; with the subagent tool alone, the templates are the plan and you spawn the same clones
  by hand.
- **A structured question tool** (AskUserQuestion), for the two gates. Without one, one message
  per gate.
- **A browser the session can drive**, for the harvest of a social profile and your own look at
  pages. Clones never use it.
- **Permissions.** Clones run `rsync`, `ln`, `find`, `node`, the framework's binary and a
  headless Chrome, in parallel, with new paths every time. When this session asks before each
  command, say so at the summoning and list the allow rules the run needs (for example
  `Bash(rsync:*)`, `Bash(find:*)`, `Bash(node:*)`, `Bash(./node_modules/.bin/astro:*)`); never
  write them into a settings file yourself.

Then, in one shell call:

```bash
for d in .claude/skills/impeccable .agents/skills/impeccable "$HOME/.claude/skills/impeccable" "$HOME/.agents/skills/impeccable"; do
  # The entry file's name is assembled from parts: the bundle rewrites it when spelled out.
  e="$d/SKILL"
  if [ -f "$e.md" ]; then echo "impeccable: $d ($(sed -n 's/^version: //p' "$e.md" | head -1))"; break; fi
done
node -e 'process.exit(typeof WebSocket === "function" ? 0 : 1)' 2>/dev/null && echo "node: 22+ (shoot.mjs runs)" || echo "node: missing or older than 22 (shoot.mjs cannot run)"
for c in "${CHROME_PATH:-}" "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "/Applications/Chromium.app/Contents/MacOS/Chromium" \
    "$(command -v google-chrome google-chrome-stable chromium chromium-browser chrome 2>/dev/null | head -1)"; do
  [ -n "$c" ] && [ -x "$c" ] && { echo "chrome: $c"; break; }
done
command -v magick >/dev/null 2>&1 && echo "imagemagick: yes" || echo "imagemagick: no"
python3 -c 'import PIL, numpy' 2>/dev/null && echo "python PIL + numpy: yes" || echo "python PIL + numpy: no"
```

What each missing piece costs, said at the summoning, never discovered at phase 8:

| Missing | Consequence |
|---|---|
| Both the subagent and the workflow tool | bunshin does not run. Step down to paint. |
| The workflow tool (the subagent tool is there) | Same phases, clones spawned by hand with the prompts `scripts/brief.mjs` prints, slower. |
| Impeccable | The direction is drawn by bunshin's own round (`references/impeccable.md`, "Without Impeccable"): weaker. Offer `npx impeccable install --project -y` once; an install during the run gives its agents only after the host reloads them, and until then its finish review runs from its degraded role file. |
| A browser the session can drive | No harvest of a social profile, whose posts are listed by script: ask for the images and texts as files, or for the current site's address. |
| Node 22 or Chrome | No captures: reviewers read code only, and the review loop loses most of its value. Say so; install nothing. |
| ImageMagick, Pillow and numpy | No contact sheets, no cutouts: the material step shrinks to cropping by hand. |

---

## The summoning - tiers and cost

One run has been measured: a seven-page site in two languages, built from a professional's social
profile, with two human touches. It spent about 10.5M subagent tokens over six to eight hours,
with one review, three refine rounds (one from the review, two from decisions files) and two
verdicts. The main session's own tokens were not measured. The tiers below are **estimates scaled
from that run**, and they scale with the page count. Say so every time you quote them.

| Tier | Refine rounds | Lenses | Cold eyes | Estimate, subagent tokens |
|---|---|---|---|---|
| **lean** | 1 | 3: finish, mobile, truth-tech | no | about 6M, 3 to 4 hours |
| **standard** (recommended) | up to 2 | 5 | in round 1's verdict, so round 2 applies its decisions | about 8 to 9M, 4 to 6 hours |
| **full** | up to 4 | 5 | every verdict | about 12 to 13M, 6 to 10 hours |

What the measured run spent, per unit, to scale an estimate: research about 0.6M; about 0.4M per
page clone (2.3M for six); a five-lens review with its plan about 1.6M; a refine round from a plan
about 1.6M with eight owners; a refine round that applies a decisions file about 1.75M; a verdict
with cold eyes about 0.35M; the documenter about 0.2M. Two units were not measured and are
estimated from these: a three-lens review with its plan, about 1.1M, and a verdict without cold
eyes, about half of one with them.

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

**How bunshin uses the preview gate.** Its only visual gate is the direction, and its only
questions are the two gates, so it never opens the menu. With Impeccable, the decision page is
the preview. Without it, the direction cards are shown as a rendered page (mode A), announced in
one line. The user can still switch mode by saying so.

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

**What nobody answering means for bunshin.** The tier is a budget, and nobody agreed to one.
A headless run goes past READ only when the request names the tier, and that answer stands.
Without one, stop after READ, print the summoning message as the final report, and spawn
nothing. When it runs: the scaffold is the stack the scan finds, or the one the request names
when it also says installs are allowed (the shared rule above forbids any other install);
otherwise plain static HTML and CSS, with no install (FOUNDATION, "On plain HTML and CSS"); the
direction is the card the draw assigned,
taken without serving the decision page, or without Impeccable the first of the three worlds
carried forward; an Impeccable that is not installed stays not installed; every gate answer is
marked **UNVALIDATED** in the report.

---

## Sub-skills Path Detection

**Tell the block where this skill lives.** The block's first line reads `GENJUTSU_SKILL_DIR`.
Claude Code fills it in by itself. On any other host, put one line in front of the block, in the
same shell call, naming the directory you read this file from:
`GENJUTSU_SKILL_DIR='/absolute/path/to/bunshin'`. When the genjutsu router printed a
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

bunshin needs the absolute `$SKILL_BASE` beyond the shell: the workflow templates are passed by
path, and every clone brief names the modules a clone must read. Note the path the block prints
(`genjutsu: modules from ...`) the first time, and write it in `.bunshin/run.json` with the tier,
the capabilities and the Impeccable directory; the owner map goes in `.bunshin/owners.json` at
FOUNDATION. Shell state still does not survive: re-emit the block in every call that loads
something or runs one of its scripts.

The orchestration module is loaded at SUMMON, before the first clone:

```bash
# (skill-base block re-emitted above this line)
load_skill orchestration
```

Its references load when their phase comes, one per shell call:
`load_ref orchestration references/material.md` (HARVEST, MATERIAL),
`references/impeccable.md` (READ when Impeccable is there, DIRECTION, SEAL),
`references/evidence.md` (FOUNDATION, PROVE).

Every path you hand a template is absolute: `<root>` below is the project's absolute path, and
the scratch directory is resolved before the call (the session's scratch directory when the host
gives one, else the value of `printf '%s\n' "${TMPDIR:-/tmp}/bunshin-<project>"`). The templates
quote what they receive, so a shell expression passed as a path is never expanded.

---

## Pipeline

Twelve phases. Everything a run writes that is not the site goes into `<root>/.bunshin/`, which
you add to `.gitignore` at SUMMON: `run.json`, `owners.json`, `harvest/`, `research/`,
`direction/` (the chosen card's board and hero, and `direction.md` without Impeccable),
`captures/round-N/` (round 1: the evidence of the review; round N+1: the evidence after refine
round N), `reviews/round-N.json` and the lens files beside it, `reviews/round-N-refine.json`,
`reviews/round-N-verdict.json`, `decisions/round-N.md`, `report.md`. Nothing under `.bunshin/`
is ever imported by the site: the isolated copies exclude it.

### 0. READ - the project, the brief, the host

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

Then read the brief and skim every source it names (the profile, the current site, the
documents), without harvesting yet. Run the capability check above. Size the job: pages or
screens, languages, audiences, the main channel. Decide whether bunshin is the right pipeline
(see "Step down"). With Impeccable, `load_ref orchestration references/impeccable.md` now and
read Impeccable's own `reference/init.md` (its Step 3 holds the interview questions, its Step 4
the PRODUCT.md format) and section 2 of its `reference/new-work.md` (the questions asked before
the draw), so the summoning can carry them.

**Declare your read** in one line before the summoning, the way cast and paint do: "My read so
far: <what> for <whom>, heading toward <direction>, on <stack>." A slot you cannot fill is said as
unknown and becomes a question at the gate.

### 1. SUMMON - the first gate

One message, then one structured question call when the host has the tool:

> **bunshin** for <what>: <N> pages in <languages>, from <sources>.
> The plan: harvest the material, research with four clones and a synthesis, you choose a
> direction, I build the
> foundation and the signature surface, <N> page clones build the rest, then refine rounds and
> verdicts until only minor issues remain or the tier's cap is reached.
> This host: <clones in parallel through workflows | clones one by one | cannot summon>.
> Impeccable: <version, it leads the direction | not installed: the direction round is weaker;
> `npx impeccable install --project -y` fixes that>. Captures: <yes | no, and what that costs>.
> Stack: <framework and adapter, already in place | no project yet: each option of the stack
> question below names its exact scaffold command and packages, the type-check ones included>.
> Your answers to the tier and the stack cover that one install and nothing else.
> Cost: one run has been measured, a seven-page bilingual site, about 10.5M subagent tokens over
> six to eight hours. Estimated from it: lean ~6M, standard ~8-9M, full ~12-13M, plus this
> session's own tokens; yours scales with the page count.
> <Permissions: the allow rules the run needs, when this session asks before each command.>

In the same call, up to four questions: **the tier first** (standard marked recommended), then the
product questions that change the work the most, recommended option first. With Impeccable,
those are the questions its `init` Step 3 asks and the ones its `new-work` asks before the draw,
at most three, the stack question first when there is no scaffold; its interview is then done,
and neither is asked again. Without it, paint's brainstorm domains. Anything the four questions
do not settle becomes an assumption, written in PRODUCT.md and in the report.

Wait for the answers. Then: add `.bunshin/` to `.gitignore`, write `.bunshin/run.json`, and load
the orchestration module. With Impeccable, run `<dir>/scripts/impeccable context` once from the
project root (`<dir>` as the capability check printed it; a project install puts nothing on the
`PATH`).

### 2. HARVEST - the real material

`load_ref orchestration references/material.md`, then follow it: the client's own images at
full resolution, their texts, contact sheets you actually read, the palette sampled from the key
images, the facts with their sources, and the list of what is missing. Harvest only what the
client owns. Everything lands in `.bunshin/harvest/`.

### 3. RESEARCH - four clones, then a synthesis

Run `research.js` with the brief (facts and gate answers only) and `out` set to
`<root>/.bunshin/research/synthesis.md`. Read the synthesis. Then write **PRODUCT.md**: with
Impeccable, in its `init` Step 4 format; without it, the same headings. Confirmed facts only, a
section of what must never be invented (prices, reviews, clients, figures), the evidence on hand,
the principles.

### 4. DIRECTION - the second gate

Run the direction round of `references/impeccable.md`: seven worlds ordered before the draw, the
draw, the challengers and their raises, the decision page, and the structured-question fallback
only when the page cannot run or was closed unanswered. **Every card carries the interaction
thesis** (timing range, hover, scroll, forbidden patterns) **and its `Allowed patterns:` line**,
inside a field the page actually shows, so one choice validates both theses. bunshin builds
code-led, always. Without Impeccable, run the round that reference describes, on a rendered page.

The guessability test holds for every card: a direction that could be written from the product
category alone is the category's default, not a direction.

Once the user has chosen, write the contract (`surface-brief write`, or `.bunshin/direction.md`):
THESIS, OWN-WORLD, STORY, FIRST VIEWPORT, FORM, FINISH, the interaction thesis, the allowed
patterns. This file is what every clone and every reviewer holds the work against. With
Impeccable, save the chosen card's board and hero images into `.bunshin/direction/` (the finish
reviewer reads them as the QUALITY BAR card). Then, in a shell call of its own, re-emit the
skill-base block and load `tells` with its web reference (`load_skill tells` then
`load_ref tells references/web.md`): MATERIAL fixes the type next, and `tells` names the reflexes
it has to rule out. Read the chosen card's `Allowed patterns:` line against the catalogue, and
name the catalogued reflexes it allows in one line of your next message (not a question) and in
the report's assumptions.

### 5. MATERIAL - by evidence, not by reflex

From `references/material.md`: type specimens rendered in a real miniature of the layout and
compared as captures; photographs trimmed and cropped; cutouts fitted to the object's own edge
and checked on a light and a dark ground; grain as a tile; provenance on every raster. Record the
type choice with its reason in the contract. Every raster the site ships is written into the
project's own asset folder (for example `src/assets/`), owned by `shared`, with an index (file,
subject, which page may use it) that the build packet names.

### 6. FOUNDATION - yours, not a clone's

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

bunshin builds a whole site, so its scope is always full: `tells` (already loaded after the
direction), `mobile-principles`, `desktop-principles` and `design-audit` all apply, each in a call
of its own, before the first line of the foundation. With Impeccable, read its
`reference/craft-floor.md` right before the first UI edit.

Then build, yourself:

- **The scaffold**, when there is no project. The root already holds `.claude/`, `.bunshin/`,
  PRODUCT.md and `.gitignore`, and scaffolders refuse, redirect or offer to empty a folder that is
  not empty: run the command the summoning named, without its install step, in
  `<scratch>/scaffold`, then `rsync -a --ignore-existing '<scratch>/scaffold/' '<root>/'`, append
  the scaffold's `.gitignore` lines to the root's, install the named packages in the root with the
  package manager (the only place it ever runs), and run one build that prints exit code 0
  before anything else.
- **Tokens**: the inks, tone roles (a class that sets background, text, button and focus for a
  whole field), a fluid type scale, spacing, four or five durations and named easings.
- **The content model**: every visible text, in every language, in typed content files, with one
  source for the practical facts (contacts, legal, areas). No copy in the views: that is what
  lets the client edit the site with an AI later.
- **The shared components**: layout (metadata, alternates, structured data, fonts), header,
  footer, the mobile call-to-action bar, the responsive image with its reveal, the page header
  every inner page reuses.
- **Every route, before the fan-out**: the route file of every page in every language, each
  rendering its page's view with an empty content file, and every page linked from the header,
  so each clone's routes build and capture from its first run.
- **The signature surface**: the home page and the one signature interaction, the surface that
  decides everything. Capture it (`references/evidence.md`), fix what the capture shows, capture
  again. Two passes, then move on.

**On plain HTML and CSS** (no build step): pass `build.cmd: 'true'`, `build.static: '.'` and
`build.link: []`. Each page's HTML file is its view and holds its copy, so the content-model rule
cannot apply, and the report says so. Write the header and footer once in the home page and copy
them verbatim into every route file before the fan-out; a change to them is a shared change
request that you apply to every page.

Write `.bunshin/owners.json`, every owner included: one owner per page (its view, its content
file, its components folder), `shared` for everything used by more than one page, the route files
included, and the home page's owner, which is you until the fan-out is over. Pass all of it to
`review.js` and `verdict.js`; pass `build.js` only the page owners you did not build yourself,
each with its mission; pass `refine.js` only the owners that have fixes, or rules of the
decisions file that touch their files.

### 7. CLONES - the pages, in parallel

Run `build.js` with `root`, the packet (what to read first by absolute path: PRODUCT.md, the
contract, the quality floor, the design system, the home page you built; the conventions; the
rules of the theses; the voice; the asset folder and its index), the page owners with their
missions, and `build`: the
framework's binary as `cmd` (and `check` when it has a type check), the resolved absolute
`scratch`, the static output folder as `static`, the absolute path of `shoot.mjs` as `shoot`,
and each owner's routes, so every clone captures its own page from its own copy and looks at it
before it returns. The anatomy of a good brief is in the orchestration module; a clone knows only
what its brief says.

When the clones return: read every `shared_change_requests` entry, apply the ones that hold (you
own the shared files at this point), and note the open questions for the client.

### 8. PROVE - before anyone reviews

`load_ref orchestration references/evidence.md`. Then, in order:

- The build and the type check, each printing exit code 0; `<dir>/scripts/impeccable detect
  --json <source folders>` when Impeccable is installed; the tells audit (in one shell call,
  re-emit the skill-base block, then `python3 "$SKILL_BASE/design-audit/scripts/audit.py" .
  --group tells`); and a grep for U+2014 unless the thesis allows it.
- Captures of every page and language with `shoot.mjs`: the standard shot list, one shots file
  and one call per page and language, into `.bunshin/captures/round-1/`. With Impeccable, add the
  two shots its finish reviewer requires, unsegmented, straight to their files:
  `{ "path": "/", "w": 1440, "h": 900, "full": true, "out": "<root>/.impeccable/review/desktop.png" }`
  and the same at 390x664 to `mobile.png`, with the same `reveal`, at every PROVE: its verdict
  pass reads those exact paths again. Read the first screens yourself.
- The functional tests of the paths that sell (menu, sticky bar, selection into the form, form
  steps, endpoint failure and success), each reported with its measured value.

Fix what is broken before the review: five lenses spent on a broken build are five lenses wasted.
What passed goes into the packet as **already verified**.

### 9. REVIEW - independent lenses

Run `review.js` with the evidence packet, the round, the tier's lenses, the module directories
(`$SKILL_BASE/mobile-principles`, `desktop-principles`, `motion-principles`, as absolute paths),
every owner from `owners.json`, and `planOut` set to `<root>/.bunshin/reviews/round-<N>.json`, N
the round this review opens (1 the first time; after a rebuild, the next round). With Impeccable,
and when the host lists its agent type, pass `finishAgent` set to the name the host gives
Impeccable's finish reviewer (Claude Code: `impeccable-finish-reviewer`), so it is spawned fresh,
the way Impeccable asks; never paste its definition into a prompt. When Impeccable is installed
but the host does not list that agent type, pass `finishRole` set to the absolute path of its
`reference/degraded/finish-reviewer.md` instead, and say so in the report.

Read the finish disposition first. `recapture`: the evidence failed, not the build; recapture what
the `recapture` list names, then run the review again, and the round does not count. No
disposition (the finish reviewer returned nothing twice) is treated the same way. `rebuild`:
rebuild the named regions yourself, then run the review again, a full one; the round counts, as
one of the tier's refine rounds. `fix` or `ship`: read the
plan and its rejected list (a rejection that contradicts the validated direction is the plan's
call to make; a rejection of a real defect is yours to overturn), and apply the `orchestrator`
fixes yourself, before refine.

### 10. REFINE - the loop

Each round, from round 1:

1. Run `refine.js` with `root`, the packet (PRODUCT.md, the contract, the quality floor, by
   absolute path), `planPath` (round 1: the review's plan file; later rounds: the plan the last
   verdict wrote), `decisions` (from round 2: the last decisions file), the owners that have
   fixes or decisions to apply, `shared` when it has some (it runs first and alone), and the
   same `build` as phase 7. Write its result to `.bunshin/reviews/round-N-refine.json`.
2. PROVE again: the checks, then new captures into `.bunshin/captures/round-<N+1>/`, and the two
   `.impeccable/review/` captures shot again over the same files.
3. Run `verdict.js` with the new packet, `history` (the round's plan file, its refine results,
   its decisions file), `round`, every owner, `planOut` set to
   `<root>/.bunshin/reviews/round-<N+1>.json`, the same `finishAgent` as the review, and
   `freshEyes: true` when the tier says so, with the one-sentence scenario of how the audience
   meets the site. It writes the next round's plan from the finish reviewer's remaining points,
   with an empty fixes list when nothing is left. Write its result to
   `.bunshin/reviews/round-N-verdict.json`.
4. **When the verdict ran cold eyes and the loop goes on, turn their notes into decisions**,
   yourself (when the stop rule ends the loop, the notes go into the report): `.bunshin/decisions/round-N.md`, rules
   the next round applies everywhere (the one role of each hero image, where saturated colour is
   allowed, the type roles, the shape of controls, the shared contracts that change). Never hand
   the notes to clones as a task list. Apply the plan's `orchestrator` fixes yourself.
5. Apply the stop rule (orchestration module), the disposition first: `recapture` means
   recapture and run the verdict again; `rebuild` sends you back to the review. Then: ship when
   nothing above minor is left, stop at the tier's round cap, stop when a round fixed nothing.
   Otherwise the next round starts at step 1.

Passing the tier's cap needs the user's yes, with the table of what is left in front of them.

### 11. SEAL - document, audit, report

- **DESIGN.md**: spawn Impeccable's documenter by the agent type the host lists (Claude Code:
  `impeccable-documenter`) with the project root, the artifact paths (the source folders and the
  built output), the direction contract, PRODUCT.md, the absolute path of Impeccable's
  `reference/document.md`, and the write boundary (the project root); it writes DESIGN.md and
  `.impeccable/design.json` from the shipped code. Without
  Impeccable, write DESIGN.md yourself from the shipped code, never from intentions.
- **AGENTS.md** (with a `CLAUDE.md` pointing to it): for the AI that will maintain the site, in
  the client's language. Where each kind of change is made, the design rules, the writing rules,
  the commands, what to check before pushing.
- **A launch guard**: a build-time warning listing every fact still missing (contacts, legal
  details, the domain), with a strict mode that fails the production build.
- **The audit**, below, run over the whole project.
- **The report**, below, also written to `.bunshin/report.md`.

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

---

## The final report

Plain, in this order:

1. **Built**: the routes, per language, and where the design system and the contract live.
2. **Verified, with the evidence**: build, type check, detector, tells, captures (where), each
   functional test with its measured value, the last verdicts and their dispositions.
3. **Not verified**: the handed-over rows of the audit, marked UNVERIFIED, and anything a lens
   could not check.
4. **Left**: the minor points after the last round, by page.
5. **For the client**: every fact still missing, from `missing.md` and the content files, and the
   open questions the clones raised.
6. **Cost**: the tier, the rounds run, the agent count per workflow, and the tokens when the host
   reported them.
7. **Assumptions**, and in a headless run every gate answer marked UNVALIDATED.
8. The two module lines, from the audit.

Nothing is committed, pushed or deployed until the user asks.

---

## Red Flags - You're About to Violate This Skill

| Thought | Reality |
|---------|---------|
| "The user said go all out, I'll skip the summoning" | The tier is asked, every time. Going all out is a tier, and it has a price. |
| "Research first, the questions will be better" | Nothing heavier than reading before the tier. Skim the sources at READ; that is enough to ask well. |
| "I'll ask how they want to see the direction" | Two questions, no third. The decision page, or a rendered page announced in one line. |
| "I'll let a clone do the home page too" | The signature surface is yours. It is the reference every clone copies. |
| "Two clones can share the stylesheet, it is one line each" | One owner per file. Shared needs are requests. |
| "The build is green in the project folder, good enough" | Clones build in copies. A green build in a shared tree proves nothing. |
| "The lenses can judge from the code, captures take time" | They judge what renders. Capture, read the first screens, then review. |
| "The finish reviewer said recapture, I'll apply the plan anyway" | Invalid evidence binds nothing. Recapture first. |
| "The cold eyes gave eight tasks, I'll assign them" | Turn them into rules in the decisions file. That step is art direction, and it is yours. |
| "One more round will get the last minor points" | The stop rule decides. Minor points go in the report. |
| "No subagent tool here, I'll play the clones myself" | Then nothing is reviewed independently. Step down to paint. |
| "Impeccable is not installed, I'll install it, it is free" | Ask. A no stands. |
| "It is ready, I'll push it so they can see it" | Nothing leaves the machine unasked. |

---

## Quick decision tree

```
Whole-site request received
  |
  +- READ: stack, brief, sources, host capabilities, size
  |     |
  |     +- smaller than a site, native stack, or no subagents? -> step down (cast / paint)
  |
  +- SUMMON (gate 1): read, plan, host, Impeccable, stack, cost; tier + product questions
  |
  +- HARVEST -> RESEARCH (four clones, a synthesis) -> PRODUCT.md
  |
  +- DIRECTION (gate 2): seven worlds, the draw, cards with both theses; contract; tells
  |
  +- MATERIAL -> FOUNDATION (yours: scaffold, tokens, content model, shared, routes, signature)
  |
  +- CLONES: one per page, disjoint files, isolated builds, each capturing its own page
  |
  +- PROVE -> REVIEW (lenses + plan; recapture? rebuild? read the disposition first)
  |
  +- REFINE -> PROVE -> VERDICT (+ cold eyes) -> decisions, next plan
  |     |
  |     +- stop rule: minor only, round cap, or nothing fixed? -> SEAL
  |     +- else -> next round
  |
  +- SEAL: DESIGN.md, AGENTS.md, launch guard, audit, report
```
