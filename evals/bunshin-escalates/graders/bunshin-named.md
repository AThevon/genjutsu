---
type: regex
arm: with-only
target: last_message
flags: i
pattern: '\bbunshin\b'
---

Indicator: the final report names bunshin, as the escalate region of paint asks when nobody is
answering. It reads last_message and not the trace: the trace holds the text of paint's
SKILL.md, which names bunshin, so a trace regex would pass on every run that loaded paint. The
prompt and the fixture never name it either (pinned in scripts/tests/test_eval_graders.py).
