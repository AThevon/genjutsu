---
type: regex
target: { source: file, path: app/page.tsx }
match: contains
pattern: 'export\s+default\s+(async\s+)?function[\s\S]*<(main|section)\b|<(main|section)\b[\s\S]*export\s+default\s+(async\s+)?function'
---

Positive guard, scored in both arms, the same as the landing cases: app/page.tsx holds a real home
page (a default-exported component that renders a main or section element). A run that fails
this is excluded from the delta reading, so a run that crashed before writing anything never
passes the routing checks below for free.
