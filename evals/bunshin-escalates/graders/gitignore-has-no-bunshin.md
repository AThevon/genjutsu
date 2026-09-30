---
type: regex
arm: both
target: { source: file, path: .gitignore }
match: not_contains
pattern: '\.bunshin'
---

No bunshin run started, read from a file the scaffold wrote: once its first gate is passed,
bunshin adds .bunshin/ to .gitignore. Unlike no-bunshin-run, this does not depend on how the
runner lists the files a run created.
