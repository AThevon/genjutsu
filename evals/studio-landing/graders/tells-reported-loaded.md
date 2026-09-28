---
type: regex
arm: with-only
target: last_message
flags: i
pattern: 'Modules loaded:[^\n]*\btells\b'
---

Indicator: the final report lists tells among the modules loaded.
