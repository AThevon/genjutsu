---
name: genjutsu
description: "Creative coding for interfaces - motion, micro-interactions, and full visual design systems. Use when animating or polishing existing UI, or designing a visual identity from scratch. Covers Web (React/Vue/Svelte/CSS/Three.js), Android (Jetpack Compose), and Apple (SwiftUI). Anti-AI-slop."
---

# genjutsu

The art of illusion: cast motion, paint visual signatures. Anti-AI-slop creative coding.

This single skill bundles both pipelines and all sub-skills.

## Picking the pipeline

**Default to `cast`.** It is the lighter pipeline and it covers the common case: something already exists and it should feel better.

Route to `paint` only on an explicit signal: "from scratch", "redesign everything", "design system", "visual identity", "brand", or a request that names nothing existing to enhance.

When the intent is genuinely ambiguous, do not spend a question on it. Run `cast` and say so in one line:

> "Running cast. Say `paint` if you want a full visual identity instead."

A `paint` that turns out to be a single component has its own shortened path (see "Light scope" in the paint pipeline), so routing upward by mistake is recoverable and cheap.

## Loading it

Run the block for the pipeline you picked, in one shell call. Each block is self-contained: a fresh shell keeps nothing from the previous one, so the search is repeated rather than factored out.

Claude Code tells the block where this skill lives. On any other host, put one line in front of the block, in the same call, naming the directory you read this file from: `GENJUTSU_BUNDLE_DIR='/absolute/path/to/genjutsu'`. Without it the block searches the usual skills directories, which works but is slower.

The block prints a `GENJUTSU_SKILL_DIR=` line, then the pipeline. Keep that line: the pipeline's skill-base block needs it, copied quoted in front of the block, in the same shell call, every time. If the block reports that it could not find the bundle, stop and show the user its message: the pipelines do not work without their modules.

**cast** - enhance or animate existing UI ("add a scroll animation", "make this dropdown snappy", "polish this transition"):

<!-- genjutsu:router:cast:start -->
```bash
p=cast
# The router's own directory: Claude Code substitutes CLAUDE_SKILL_DIR. On any
# other host, set GENJUTSU_BUNDLE_DIR to the directory this file was read from,
# in front of this block. Empty means unknown, and the search takes over.
g="${GENJUTSU_BUNDLE_DIR:-${CLAUDE_SKILL_DIR}}"
f=""
# A candidate is a genjutsu bundle only when it holds this pipeline AND a
# _jutsu with motion-principles side by side. The shared npx skills directory
# serves about 80 agents: a directory that is merely named cast or paint may
# belong to anyone. Entry files are SKILL or GUIDE depending on the artifact,
# so the name is assembled from parts and never spelled out in full.
genjutsu_bundle_entry() {
  for d in SKILL GUIDE; do
    [ -f "$1/_jutsu/motion-principles/$d.md" ] || continue
    for e in SKILL GUIDE; do
      [ -f "$1/$p/$e.md" ] && { printf '%s\n' "$1/$p/$e.md"; return 0; }
    done
  done
  return 1
}
genjutsu_first_bundle() { # candidate bundle directories on stdin
  while read -r c; do
    genjutsu_bundle_entry "$c" && return 0
  done
  return 1
}
[ -n "$g" ] && f="$(genjutsu_bundle_entry "$g")"
[ -z "$f" ] && [ -d /mnt/skills/user ] && \
  f="$(find -L /mnt/skills/user -mindepth 1 -maxdepth 1 -type d 2>/dev/null | genjutsu_first_bundle)"
w="${PWD:-$(pwd)}"; n=0
while [ -z "$f" ] && [ "$n" -lt 24 ]; do
  n=$((n + 1))
  f="$(find -L "$w/.claude/skills" "$w/.agents/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | genjutsu_first_bundle)"
  case "$w" in /|.|"") break ;; esac
  w="$(dirname "$w")"
done
for r in "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.codex/skills" \
    "$HOME/.cursor/skills" /mnt/.claude/skills; do
  [ -z "$f" ] && [ -d "$r" ] || continue
  f="$(find -L "$r" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | genjutsu_first_bundle)"
done
[ -z "$f" ] && [ -d /sessions ] && \
  f="$(find -L /sessions -maxdepth 7 -type d -path '*/.claude/skills/*' 2>/dev/null | genjutsu_first_bundle)"
if [ -n "$f" ]; then
  echo "genjutsu: pipeline file $f"
  echo "GENJUTSU_SKILL_DIR=$(cd "$(dirname "$f")" && pwd -P)"
  echo "genjutsu: put the line above, quoted, in front of every skill-base block you run."
  echo "genjutsu: if this output is cut short, read the pipeline file above in full before going on."
  echo "---"
  cat "$f"
else
  echo "genjutsu: could not find the genjutsu bundle ($p and _jutsu side by side)." >&2
  echo "  any agent    npx skills add https://genjutsu.athevon.dev -g" >&2
  echo "  Claude Code  /plugin marketplace add AThevon/genjutsu, then /plugin install genjutsu" >&2
  echo "  claude.ai    upload genjutsu.zip in Customize > Skills" >&2
  echo "  Tried: GENJUTSU_BUNDLE_DIR or CLAUDE_SKILL_DIR (${g:-empty}), /mnt/skills/user," >&2
  echo "         .claude/skills and .agents/skills from \$PWD upward, ~/.agents/skills," >&2
  echo "         ~/.claude/skills, ~/.codex/skills, ~/.cursor/skills, /mnt/.claude/skills, /sessions." >&2
  echo "genjutsu: stop here and show this message to the user." >&2
  return 1 2>/dev/null || exit 1
fi
```
<!-- genjutsu:router:cast:end -->

**paint** - build a visual universe from scratch or a full redesign ("design this landing page", "bootstrap a design system"):

<!-- genjutsu:router:paint:start -->
```bash
p=paint
# The router's own directory: Claude Code substitutes CLAUDE_SKILL_DIR. On any
# other host, set GENJUTSU_BUNDLE_DIR to the directory this file was read from,
# in front of this block. Empty means unknown, and the search takes over.
g="${GENJUTSU_BUNDLE_DIR:-${CLAUDE_SKILL_DIR}}"
f=""
# A candidate is a genjutsu bundle only when it holds this pipeline AND a
# _jutsu with motion-principles side by side. The shared npx skills directory
# serves about 80 agents: a directory that is merely named cast or paint may
# belong to anyone. Entry files are SKILL or GUIDE depending on the artifact,
# so the name is assembled from parts and never spelled out in full.
genjutsu_bundle_entry() {
  for d in SKILL GUIDE; do
    [ -f "$1/_jutsu/motion-principles/$d.md" ] || continue
    for e in SKILL GUIDE; do
      [ -f "$1/$p/$e.md" ] && { printf '%s\n' "$1/$p/$e.md"; return 0; }
    done
  done
  return 1
}
genjutsu_first_bundle() { # candidate bundle directories on stdin
  while read -r c; do
    genjutsu_bundle_entry "$c" && return 0
  done
  return 1
}
[ -n "$g" ] && f="$(genjutsu_bundle_entry "$g")"
[ -z "$f" ] && [ -d /mnt/skills/user ] && \
  f="$(find -L /mnt/skills/user -mindepth 1 -maxdepth 1 -type d 2>/dev/null | genjutsu_first_bundle)"
w="${PWD:-$(pwd)}"; n=0
while [ -z "$f" ] && [ "$n" -lt 24 ]; do
  n=$((n + 1))
  f="$(find -L "$w/.claude/skills" "$w/.agents/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | genjutsu_first_bundle)"
  case "$w" in /|.|"") break ;; esac
  w="$(dirname "$w")"
done
for r in "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.codex/skills" \
    "$HOME/.cursor/skills" /mnt/.claude/skills; do
  [ -z "$f" ] && [ -d "$r" ] || continue
  f="$(find -L "$r" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | genjutsu_first_bundle)"
done
[ -z "$f" ] && [ -d /sessions ] && \
  f="$(find -L /sessions -maxdepth 7 -type d -path '*/.claude/skills/*' 2>/dev/null | genjutsu_first_bundle)"
if [ -n "$f" ]; then
  echo "genjutsu: pipeline file $f"
  echo "GENJUTSU_SKILL_DIR=$(cd "$(dirname "$f")" && pwd -P)"
  echo "genjutsu: put the line above, quoted, in front of every skill-base block you run."
  echo "genjutsu: if this output is cut short, read the pipeline file above in full before going on."
  echo "---"
  cat "$f"
else
  echo "genjutsu: could not find the genjutsu bundle ($p and _jutsu side by side)." >&2
  echo "  any agent    npx skills add https://genjutsu.athevon.dev -g" >&2
  echo "  Claude Code  /plugin marketplace add AThevon/genjutsu, then /plugin install genjutsu" >&2
  echo "  claude.ai    upload genjutsu.zip in Customize > Skills" >&2
  echo "  Tried: GENJUTSU_BUNDLE_DIR or CLAUDE_SKILL_DIR (${g:-empty}), /mnt/skills/user," >&2
  echo "         .claude/skills and .agents/skills from \$PWD upward, ~/.agents/skills," >&2
  echo "         ~/.claude/skills, ~/.codex/skills, ~/.cursor/skills, /mnt/.claude/skills, /sessions." >&2
  echo "genjutsu: stop here and show this message to the user." >&2
  return 1 2>/dev/null || exit 1
fi
```
<!-- genjutsu:router:paint:end -->

Both pipelines then resolve their modules from the `GENJUTSU_SKILL_DIR` printed above, and stop with the install command if the modules are missing.
