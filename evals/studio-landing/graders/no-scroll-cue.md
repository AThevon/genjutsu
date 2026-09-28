---
type: regex
target: { source: file, path: app/page.tsx }
match: not_contains
flags: i
pattern: '>\s*(\u2193\s*)?scroll(\s+(down|to\s+\w+|for\s+more))?\s*(\u2193|\u2192)?\s*<|aria-label=["\x27]scroll|>\s*[\u2193\u2304]\s*<'
---

Decorative filler: a scroll cue in the hero (Scroll, Scroll to explore, a lone down arrow).
