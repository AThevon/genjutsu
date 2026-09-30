---
type: regex
arm: with-only
target: last_message
flags: i
pattern: 'genjutsu:cast\b|/cast\b|`cast`|\bcast\s+(pipeline|skill)\b|\b(pipeline|skill)\b[^\n]{0,40}\bcast\b|\b(ran|running|via|using|by)\s+`?(genjutsu:)?cast\b|\bstep(ped|s|ping)?\s+down\b[^\n]{0,60}\bcast\b'
---

Indicator: the final report says that cast did the work, or that bunshin stepped down to it (the
prompt asks the report to name the pipeline, without saying which). It reads last_message: the
trace holds the text of bunshin's SKILL.md, which names cast and the step down. "cast" alone is
not enough, since a report on a button can say that a shadow is cast.
