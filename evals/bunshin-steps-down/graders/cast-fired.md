---
type: tool_used
arm: with-only
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?cast"'
---

Indicator: cast was invoked, which is how bunshin steps down when the host lists genjutsu:cast
as a skill (it reads cast's entry file only when the host does not).
