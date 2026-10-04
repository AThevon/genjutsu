---
type: regex
arm: with-only
target: trace
pattern: '"skill"\s*:\s*"(?:[\w-]+:)?cast"|[/]_jutsu\b'
---

Indicator: cast started, by either path. Through the Skill tool, the call names cast (the same check
as evals/). Through the leading /genjutsu:cast, the skill is expanded in place: no Skill call, and
the expanded text is not in the trace either, so the evidence is what that text makes the run do
first, reach into genjutsu's module directory (_jutsu) to resolve and load its modules. Nothing
else points a run there, and the case prompt names one pipeline only.
