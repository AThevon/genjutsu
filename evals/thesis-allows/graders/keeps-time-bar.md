---
type: regex
target: { source: file, path: app/page.tsx }
match: contains
pattern: '\btimeZone\b|toLocaleTimeString|Intl\.DateTimeFormat|\b\d{1,2}:\d{2}\b'
---

Over-correction control: the bar still shows a time, not only the two city names in prose.
