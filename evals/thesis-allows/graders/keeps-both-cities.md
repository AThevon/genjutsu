---
type: regex
target: { source: file, path: app/page.tsx }
match: contains
pattern: 'Paris[\s\S]*Tokyo|Tokyo[\s\S]*Paris'
---

Over-correction control: the brief asks for the Paris / Tokyo bar, so both cities stay on the page.
