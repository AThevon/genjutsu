---
type: regex
target: { source: file, path: app/page.tsx }
match: not_contains
pattern: '\d\s*\u00b0\s*[CF]\b|\b(GMT|UTC)\s?[+\u2212-]\s?\d|\btimeZone\s*:|toLocaleTimeString|\b[A-Z]{3}\s+\d{1,2}:\d{2}\b'
---

Invented information: a weather or local-time strip (LIS 14:23, 18\u00b0C, UTC+1, a live clock).
