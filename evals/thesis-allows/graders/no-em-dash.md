---
type: regex
target: { source: file, path: app/page.tsx }
match: not_contains
flags: i
pattern: '\u2014|&mdash;|&#8212;|&#x2014;|\\u2014'
---

Reflex convergence: U+2014 (em dash), as the character, as an HTML entity, or as a JS escape.
