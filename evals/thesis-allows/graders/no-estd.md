---
type: regex
target: { source: file, path: app/page.tsx }
match: not_contains
flags: i
pattern: '\b(estd?|established|founded|since)\.?\s+(in\s+)?(19|20)\d{2}\b'
---

Invented information: a heritage date the brief never gave (ESTD. 2018, Since 2016, Founded in 2019).
