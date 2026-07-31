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

Each block is self-contained: a fresh shell keeps nothing from the previous one, so the resolution is repeated rather than factored out.

**cast** - enhance or animate existing UI ("add a scroll animation", "make this dropdown snappy", "polish this transition"):

```bash
p=cast; f=""; d="${PWD:-$(pwd)}"
# The entry file is named SKILL or GUIDE depending on the artifact: a plugin
# install keeps the former, the claude.ai bundle renames it to the latter at
# packaging time. Match either, and never spell the full name out here.
pick() { grep -E "/(SKILL|GUIDE)\.md$" | head -1; }
# claude.ai mounts the bundle at /mnt/skills/user/<name>/; Cowork mounts it
# under a per-session root such as /sessions/<id>/mnt/.claude/skills/<name>/.
for r in /mnt/skills/user "$HOME/.claude/skills" /mnt/.claude/skills; do
  [ -d "$r" ] || continue
  f="$(find "$r" -maxdepth 3 -type f -path "*/$p/*" 2>/dev/null | pick)"
  [ -n "$f" ] && break
done
n=0
while [ -z "$f" ] && [ "$n" -lt 24 ]; do
  n=$((n + 1))
  f="$(find "$d/.claude/skills" -maxdepth 3 -type f -path "*/$p/*" 2>/dev/null | pick)"
  case "$d" in /|.|"") break ;; esac
  d="$(dirname "$d")"
done
[ -z "$f" ] && f="$(find /sessions -maxdepth 8 -type f -path "*/.claude/skills/*/$p/*" 2>/dev/null | pick)"
if [ -n "$f" ]; then cat "$f"; else
  echo "genjutsu: could not locate the $p pipeline in this bundle. Re-upload genjutsu.zip, or reinstall the plugin." >&2
fi
```

**paint** - build a visual universe from scratch or a full redesign ("design this landing page", "bootstrap a design system"):

```bash
p=paint; f=""; d="${PWD:-$(pwd)}"
# The entry file is named SKILL or GUIDE depending on the artifact: a plugin
# install keeps the former, the claude.ai bundle renames it to the latter at
# packaging time. Match either, and never spell the full name out here.
pick() { grep -E "/(SKILL|GUIDE)\.md$" | head -1; }
for r in /mnt/skills/user "$HOME/.claude/skills" /mnt/.claude/skills; do
  [ -d "$r" ] || continue
  f="$(find "$r" -maxdepth 3 -type f -path "*/$p/*" 2>/dev/null | pick)"
  [ -n "$f" ] && break
done
n=0
while [ -z "$f" ] && [ "$n" -lt 24 ]; do
  n=$((n + 1))
  f="$(find "$d/.claude/skills" -maxdepth 3 -type f -path "*/$p/*" 2>/dev/null | pick)"
  case "$d" in /|.|"") break ;; esac
  d="$(dirname "$d")"
done
[ -z "$f" ] && f="$(find /sessions -maxdepth 8 -type f -path "*/.claude/skills/*/$p/*" 2>/dev/null | pick)"
if [ -n "$f" ]; then cat "$f"; else
  echo "genjutsu: could not locate the $p pipeline in this bundle. Re-upload genjutsu.zip, or reinstall the plugin." >&2
fi
```

Both pipelines then resolve the sub-skills on their own: their path detection prefers the bundled `_jutsu/`, and falls back to the session-rooted mount when no fixed path exists.
