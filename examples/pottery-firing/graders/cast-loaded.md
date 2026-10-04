---
type: regex
arm: with-only
target: trace
pattern: '"skill"\s*:\s*"(?:[\w-]+:)?cast"|Modules\snot\sloaded:'
---

Indicator: cast governed the run to its end, by either path. Through the Skill tool, the call
names cast. Through the leading /genjutsu:cast, the expanded skill leaves no call in the trace, so
the evidence is the report it requires: two closing lines naming the modules loaded and the
modules not loaded, a form only the pipelines ask for. Written with \s so that the line itself
never appears in this file.
