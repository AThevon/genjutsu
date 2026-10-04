---
type: regex
target: { source: file, path: src/InvoiceList.tsx }
match: contains
pattern: 'motion|[Aa]nimat|[Tt]ransition|keyframes|[Ss]pring|requestAnimationFrame|from\s+["'']\.\.?/(?!data["''])'
---

Positive guard: the invoice list now does something when a row is marked as paid. The scaffold's
src/InvoiceList.tsx imports only ./data and holds no motion, animation, transition or spring of
any kind, so it fails this; it passes once the list uses motion, an animation or transition, or
imports a new local component (a stamp, a counter) that carries the feedback.
