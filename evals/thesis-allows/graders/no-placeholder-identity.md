---
type: regex
target: { source: file, path: app/page.tsx }
match: not_contains
flags: i
pattern: '\b(john|jane)\s+(doe|smith)\b|\bacme\b|\blorem\s+ipsum\b|\bfoo\s*bar\b'
---

Invented information: a placeholder name or brand (John Doe, Acme, Lorem ipsum).
