---
type: tool_used
arm: both
tool: Agent
min: 0
max: 0
---

bunshin's clones are subagents, and one button is not a job for them: after the step down, no
subagent is spawned. allowed_tools grants Agent, so the run could call it (a withheld tool would
pass this for free) and the step down is bunshin's own decision, not a missing capability.
