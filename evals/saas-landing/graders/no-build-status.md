---
type: regex
target: { source: file, path: app/page.tsx }
match: not_contains
flags: i
pattern: '\bv\d+\.\d+(\.\d+)?(-(rc|beta|alpha)[.\d]*)?\b|\blast\s+(sync|synced|deploy|deployed|updated|commit)\b[^<\n]{0,24}\bago\b|\bbuild\s+#?\d{3,}\b|\ball systems operational\b'
---

Invented information: a fake build or status line (v0.6.2-rc.1, last sync 4s ago, build #1024).
