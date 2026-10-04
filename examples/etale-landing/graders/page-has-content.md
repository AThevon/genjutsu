---
type: regex
target: { source: file, path: src/App.tsx }
match: contains
flags: m
pattern: '<(main|section)(\s[^>]*[^/])?>|^import\s'
---

Positive guard: the run wrote a real page. The scaffold's src/App.tsx is a bare self-closing
<main /> with no import, so it fails this; it passes once App renders a main or section element
with content, or imports the components that make up the page.
