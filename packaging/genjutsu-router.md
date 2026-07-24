---
name: genjutsu
description: "Creative coding for interfaces - motion, micro-interactions, and full visual design systems. Use when animating or polishing existing UI, or designing a visual identity from scratch. Covers Web (React/Vue/Svelte/CSS/Three.js), Android (Jetpack Compose), and Apple (SwiftUI). Anti-AI-slop."
---

# genjutsu

The art of illusion: cast motion, paint visual signatures. Anti-AI-slop creative coding.

This single skill bundles both pipelines and all sub-skills. Pick the pipeline by intent, then follow that file exactly:

- **cast** - enhance / animate existing UI ("add a scroll animation", "make this dropdown snappy", "polish this transition"):
  ```bash
  cat "$(find /mnt/skills/user -path '*/cast/SKILL.md' 2>/dev/null | head -1)"
  ```
- **paint** - build a visual universe from scratch or a full redesign ("design this landing page", "bootstrap a design system"):
  ```bash
  cat "$(find /mnt/skills/user -path '*/paint/SKILL.md' 2>/dev/null | head -1)"
  ```

Both pipelines resolve the sub-skills from this bundle automatically (their path detection prefers the bundled `_jutsu/`). If the intent is unclear, ask exactly one question: "Enhance what's already there, or build a new visual identity?"
