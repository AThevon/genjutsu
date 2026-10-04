# genjutsu evals

This suite measures what genjutsu changes in the code an agent writes, by running the same brief
with the plugin loaded and without it (`claude plugin eval`, ablation `with-without`). The number
that matters is the delta between the two arms, read from the JSON result with
`scripts/eval-runs.py`, never the runner's exit code.

| Case | Brief | What it checks |
|---|---|---|
| `studio-landing` | Landing page of an independent design studio | The tells are gone: positive delta |
| `saas-landing` | Landing page of an invoicing SaaS | The tells are gone: positive delta |
| `thesis-allows` | A studio really split between Paris and Tokyo that asks for a two-city time bar | The bar stays: over-correction control. A pattern the brief asks for, carried into the thesis, is not a tell |
| `swiftui-skip` | A SwiftUI screen | `tells` is a web module and is never requested |
| `bunshin-escalates` | A whole site for an independent frame builder with two kinds of client, her Instagram profile as the only material, asked of `/genjutsu:paint` | Routing: paint names bunshin in its last message and carries on with the home page; no subagent, no bunshin run |
| `bunshin-steps-down` | A hover and a press state on one existing button, asked of `/genjutsu:bunshin` | Routing: bunshin steps down to cast; no subagent, no `.bunshin/`, and the button gets its interaction |

Each case holds `prompt.md` (the brief and the pre-answered gates), `case.yaml`, `fixture.sh` (the
workspace the run starts from) and `graders/*.md`. Every prompt invokes one genjutsu pipeline by
name (`/genjutsu:paint`, except `bunshin-steps-down`, which invokes `/genjutsu:bunshin`) and
answers its gates up front (inline preview, theses and design system validated as proposed, the
files the work may touch named one by one), so the suite measures the implementation and the
audit, not the brainstorm.

bunshin itself is never run end to end by this suite: a full run costs millions of tokens (about
10.5M subagent tokens on one measured run: a seven-page site in two languages). The two `bunshin-`
cases measure only its routing: the proposal paint makes, with nobody answering, when a brief is a
whole site, and bunshin's step down when the job is one component. Both grant `Agent`, so that a
run that spawns no subagent has decided not to, rather than been unable to.

## Cost: read this first

Every run is a real, billed `claude` session, and so is every `llm` grader vote. The full suite is
6 cases x 3 runs x 2 arms = 36 agent runs, each allowed up to 150 turns and 40 minutes, plus three
judge calls per `llm` grader per run. It runs by hand before a major release, never in CI. Always
pass `--max-cost-usd`; the smoke test tells you what one web run costs, so set the ceiling from
that figure (about 18 times the cost of one with-arm web run, plus 18 without-arm runs).

The ceiling matters most for `bunshin-steps-down`: a with-arm run in which bunshin fails to step
down spawns clones, and can cost many times a web run before its limits stop it. Those limits are
lower than the web cases' (100 turns, 30 minutes) for that reason, and `--max-cost-usd` is what
stops the suite.

What does run in CI is free and offline:

```bash
python3 scripts/check-evals.py                 # every case has its files, every grader a known type
python3 -m unittest discover -s scripts/tests  # the free graders still fire on known pages
```

## Requirements

- Claude Code 2.1.269 or later (`claude --version`), git 2.31 or later (`git --version`).
- macOS, or Linux with `bubblewrap` and `socat`: the runs grant Bash, and Bash only runs inside
  the OS sandbox.
- A terminal for the first run from a given directory: the runner asks `Trust this plugin
  directory?` and a `--json` run cannot ask. Answer `y` during the smoke test; the full suite then
  runs from the same directory without asking.

Every `claude plugin eval` command below passes `--output-dir` explicitly, so the result always
lands at a path you already know, never at whatever timestamped directory the default
(`./<eval dir>/results/<timestamp>/`) happened to pick.

## 1. Smoke test

From the repository root, in a terminal:

```bash
claude plugin eval . --case swiftui-skip --runs 1 --ablation none --scaffold --allow-tools Bash Write Edit --keep-temp --no-publish --output-dir evals/results/smoke-swiftui-skip
```

Then check that the modules were really read, not only requested:

```bash
python3 scripts/eval-runs.py inspect evals/results/smoke-swiftui-skip/aggregate-result.json --case swiftui-skip
```

- Exit 0, `requested:` lists `motion-principles` and `swiftui-motion`, `problems: none`: the
  sandbox reads the plugin. Go on.
- Exit 1 with `module directory NOT resolved` or `read(s) denied by the sandbox`: the Bash sandbox
  cannot read the plugin, which lives under `$HOME`. Use the fallback below, then smoke-test again
  from the copy.
- Exit 2: the trace could not be read (the file named after "trace not found:" is missing, or
  `eval-runs.py` recognised no tool call in it). This is not a `$HOME` visibility problem: open the
  named `trace.jsonl` by hand and check it directly.

A second smoke run calibrates the limits of the web cases and checks the loading indicators,
including `tells-read-sentinel` (a regex on `target: trace`):

```bash
claude plugin eval . --case studio-landing --runs 1 --ablation none --scaffold --allow-tools Bash Write Edit --keep-temp --no-publish --output-dir evals/results/smoke-studio-landing
python3 scripts/eval-runs.py inspect evals/results/smoke-studio-landing/aggregate-result.json --case studio-landing
```

Read `turns` and `durationSeconds` of that run in `aggregate-result.json`. If the run hit its turn
cap or its timeout (`error` is not null), raise `max_turns` (at most 200) or `timeout_seconds` (at
most 3600) in the four `prompt.md` files that run paint on the web (`studio-landing`,
`saas-landing`, `thesis-allows`, `bunshin-escalates`) to about 1.5 times what the run used, and
run the smoke test again. The four indicators `paint-fired`, `tells-requested`,
`tells-reported-loaded` and `tells-read-sentinel` must pass; if only `tells-read-sentinel` fails
while `tells-requested` passes, the trace does not carry tool output on this runner version:
delete `graders/tells-read-sentinel.md` from the three web cases and note it in the release notes.

A third smoke run covers the case that costs the most when it fails, with its own ceiling:

```bash
claude plugin eval . --case bunshin-steps-down --runs 1 --ablation none --scaffold --allow-tools Bash Write Edit --keep-temp --max-cost-usd <budget> --no-publish --output-dir evals/results/smoke-bunshin-steps-down
```

In its `aggregate-result.json` every grader must pass: `bunshin-fired` and `cast-fired` show that
bunshin ran and handed over, `button-has-interaction` that the work was done, and the rest that
nothing heavier happened. If the run hit its turn cap or its timeout, raise the limits of
`bunshin-steps-down/prompt.md` the same way.

## 2. Fallback: run from a copy outside $HOME

When Bash is granted, the eval sandbox makes the home directory unreadable. The plugin under test
is this repository, which lives under `$HOME`, so the shell calls that resolve and read the modules
can fail. Run from a copy instead:

```bash
rsync -a --delete --exclude evals/results --exclude .git --exclude dist --exclude docs/superpowers ./ /private/tmp/genjutsu-eval/
cd /private/tmp/genjutsu-eval
claude plugin eval . --case swiftui-skip --runs 1 --ablation none --scaffold --allow-tools Bash Write Edit --keep-temp --no-publish --output-dir evals/results/smoke-swiftui-skip
python3 scripts/eval-runs.py inspect evals/results/smoke-swiftui-skip/aggregate-result.json --case swiftui-skip
```

`.git` is left out because a git worktree's `.git` is a file that points back into `$HOME`. Rerun
the `rsync` after every change to the plugin, and copy the results back when a run is done:

```bash
rsync -a /private/tmp/genjutsu-eval/evals/results/ evals/results/
```

## 3. Full suite

From the directory that passed the smoke test:

```bash
claude plugin eval . --ablation with-without --runs 3 --scaffold --allow-tools Bash Write Edit --keep-temp --max-cost-usd <budget> --threshold 0 --no-publish --json evals/results/run.json --output-dir evals/results/full-suite
```

`--threshold 0` keeps the exit code at 0 whatever the scores: the release is judged on the delta,
below. Exit 2 means the cost ceiling was hit and the result is partial: do not publish it.
`--keep-temp` keeps every run's workspace under `/tmp/e-*`; the showcase needs them, and macOS
cleans `/tmp`, so collect them the same day. Adding `-j 3` shortens the wall-clock time without
changing the results (the runs share one rate limit).

## 4. Reading the delta

```bash
python3 scripts/eval-runs.py delta evals/results/run.json
```

The table gives, per case, the mean score of each arm, the delta, and how many runs were kept. The
runner's own summary averages every run; this does not, for two reasons:

- **A run that failed its positive guard is left out of its arm.** `page-has-content` (web),
  `swift-screen-written` (SwiftUI) and `button-has-interaction` (the one-button case) check that
  the run produced a real page, screen or interaction. An empty `app/page.tsx` passes every
  `not_contains` grader, and a run that did nothing spawns no subagent, so without this rule a
  with-arm that crashed would look cleaner than a baseline that did the work.
- **A run no grader scored is left out.** A run that failed in the harness (the scaffold exited
  non-zero, a setup step threw) comes back with score 0, an `error` and an empty `graders[]`. Kept,
  one such crash in the without arm would fake a positive delta, and one in the with arm would
  hide a real one.
- **A run whose judge graders were skipped at the cost ceiling is left out** (`skippedPaidGraders`),
  because its score is not comparable.

The with-only indicators (`paint-fired`, `tells-requested`, `tells-reported-loaded`,
`tells-read-sentinel`, and for the routing cases `bunshin-named`, `bunshin-fired`, `cast-fired`,
`stepped-down-to-cast`) are listed beside the scores, never inside them.

For the two routing cases the delta says little: without genjutsu there is no bunshin to switch
to, so most of their scored checks pass in the without arm by construction. Read them on the with
arm instead: the release gate below does. `no-bunshin-run` is a `file_exists` grader,
matched against the files the runner lists as created by the run; `gitignore-has-no-bunshin`
reads the `.gitignore` the scaffold wrote, where bunshin adds `.bunshin/` once its first gate is
passed, so it holds whether or not that listing reaches into dot directories.

Then it applies the release gate and exits 0 only when every line passes:

- `studio-landing` and `saas-landing`: delta strictly positive.
- `studio-landing`: `tells-requested` and `tells-reported-loaded` pass on every kept with-arm run
  (the module is requested and read on a web stack).
- `thesis-allows`: `keeps-both-cities` and `keeps-time-bar` pass on every kept with-arm run.
- `swiftui-skip`: `tells-never-requested` and `tells-never-read` pass on every kept with-arm run.
- `bunshin-escalates`: `bunshin-named`, `agent-never-called`, `bunshin-never-invoked`,
  `no-bunshin-run` and `gitignore-has-no-bunshin` pass on every kept with-arm run.
- `bunshin-steps-down`: `bunshin-fired`, `stepped-down-to-cast`, `agent-never-called`,
  `no-bunshin-run` and `gitignore-has-no-bunshin` pass on every kept with-arm run.
- The result is not partial.

To look at the JSON by hand: each case is `cases[]` with `name`, `aggregates.score`,
`aggregates.delta`, and the runs in `arms.with[]` and `arms.without[]`. A run carries `score`,
`error`, `skippedPaidGraders`, `tracePath` and `graders[]`, each grader with `name`, `passed` and
`scored` (false for the with-only indicators). The runs the delta leaves out are:

```bash
python3 -c "import json,sys; d=json.load(open(sys.argv[1])); [print(c['name'], arm, i + 1) for c in d['cases'] for arm in ('with', 'without') for i, r in enumerate(c['arms'].get(arm) or []) if not r.get('graders') or r.get('skippedPaidGraders') or any(g['name'] in ('page-has-content', 'swift-screen-written', 'button-has-interaction') and not g['passed'] for g in r['graders'])]" evals/results/run.json
```

## 5. When the gate fails

A zero or negative delta means `tells` changes nothing measurable: the release does not announce
it. Iterate on `skills/_jutsu/tells/`, never on the graders to make them pass, then rerun only the
case concerned (`--case studio-landing`), and the full suite before publishing. A failing
`thesis-allows` means the module over-corrects: the rule that the thesis is the only authority
(an element the brief asks for, carried into the thesis by name, is allowed) is not reaching the
model. A failing `bunshin-escalates` points at the `escalate` region of `skills/paint/SKILL.md`
(and its twin in cast), a failing `bunshin-steps-down` at "Step down" in
`skills/bunshin/SKILL.md`; there too, the fix goes in the skill, not in the graders.

## 6. Bonus: against taste-skill

A three-way table (genjutsu, taste-skill, nothing) on the two landing cases. taste-skill is
cloned outside `$HOME` at the commit the tells catalogue was written from, the two cases are
copied without the genjutsu loading graders, and the prompt points at taste-skill's own skill
instead of `/genjutsu:paint`; everything else is identical.

```bash
TASTE_SHA=$(grep -rhi 'taste' skills/_jutsu/VERSIONS.md skills/_jutsu/tells/ | grep -oE '\b[0-9a-f]{40}\b' | head -1)
[ -n "$TASTE_SHA" ] || { echo "no pinned taste-skill commit found"; exit 1; }
rm -rf /private/tmp/taste-skill-eval
git clone -q https://github.com/Leonxlnx/taste-skill /private/tmp/taste-skill-eval
git -C /private/tmp/taste-skill-eval checkout -q "$TASTE_SHA"
for c in studio-landing saas-landing; do
  dest="/private/tmp/taste-skill-eval/evals/$c"
  rsync -a --exclude 'graders/tells-*' --exclude graders/paint-fired.md "evals/$c/" "$dest/"
  perl -pi -e 's#/genjutsu:paint#/taste-skill:design-taste-frontend#g' "$dest/prompt.md"
  cat > "$dest/graders/taste-fired.md" <<'EOF'
---
type: tool_used
arm: with-only
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?design-taste-frontend"'
---

Indicator: taste-skill's design-taste-frontend skill was invoked.
EOF
done
claude plugin eval /private/tmp/taste-skill-eval --trust-plugin --ablation with-without --runs 3 --scaffold --allow-tools Bash Write Edit --keep-temp --max-cost-usd <budget> --threshold 0 --no-publish --json evals/results/taste-run.json --output-dir evals/results/taste-run
python3 scripts/eval-runs.py delta evals/results/taste-run.json --no-gate
```

Present the table with its bias: these are our graders, written against the tells genjutsu names.

## 7. Showcase inputs

```bash
python3 scripts/eval-runs.py collect evals/results/run.json --case studio-landing --case saas-landing --out evals/results/showcase
python3 scripts/eval-runs.py tells evals/results/showcase --format markdown
```

`collect` copies, for each arm, the workspace of the first run that passed its guard out of the
directories kept by `--keep-temp` (it opens their sealed `home/` the way the runner says to, with
`chmod 700`). `tells` runs design-audit's tells group on each `app/page.tsx` and sums the findings
per arm. The copies stay under `evals/results/`: the pages of the arm without genjutsu are
full of tells, U+2014 (em dash) included, and must never be committed.

## The last published result

The table in the root README and in the v4.0.0 CHANGELOG entry comes from `--runs 2` per arm on
genjutsu `ef31234`: on both landings, 2 tells without genjutsu and 0 with it, and a grader delta of
+0.20 (studio) and +0.10 (SaaS).

What moved, over the runs kept in each arm: on both landings, the judge that fails a product
screen faked in divs or a page stuck on one layout family (studio 0/2 to 2/2, SaaS 0/2 to 1/2), and
the U+2014 (em dash) check (1/2 to 2/2 on each); on the studio page, the numbered eyebrow (1/2 to
2/2). The other checks already passed without genjutsu: today's models rarely write an invented
build status or an `ESTD. 2018` on their own, so those graders guard against a regression more than
they measure a gain.

The two control cases held. In `thesis-allows`, a studio genuinely split between Paris and Tokyo
asks for its two clocks, the thesis names them, and both stay on every run: the module does not
over-correct. In `swiftui-skip`, measured on the run before (`5735e65`), `tells` is never requested
or read, because it only covers the web so far.

Read these numbers for what they count: tells and the checks our graders make. They are not a
judgement of which page looks better, and the page of the arm without genjutsu can look as designed
as the one with it. For that reason the README shows the table without the before / after captures
(`showcase-section.py --captures none`); the v4.0.0 captures are kept at the `v4.0.0` tag, in
`assets/v4/`, where the CHANGELOG entry still points.

## Results

`evals/results/` is gitignored: runs, reports, `run.json` and the showcase notes stay local. The
kept run directories under `/tmp/e-*` are read-only once sealed. When the showcase is done, remove
exactly the ones the results name (each run's `tracePath` is `<root>/out/trace.jsonl`), never a
`/tmp/e-*` glob that would also catch unrelated entries:

```bash
python3 -c "
import json, pathlib, sys
roots = set()
for f in sys.argv[1:]:
    for c in json.load(open(f)).get('cases') or []:
        for runs in (c.get('arms') or {}).values():
            for r in runs:
                root = pathlib.Path(r.get('tracePath') or '/').parent.parent
                if root.name.startswith('e-') and str(root.parent) in ('/tmp', '/private/tmp'):
                    roots.add(str(root))
print('\n'.join(sorted(roots)))" evals/results/*.json | while read -r d; do chmod -R u+rwx "$d" && rm -rf "$d" && echo "removed $d"; done
```
