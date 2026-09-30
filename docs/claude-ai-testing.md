# Testing the genjutsu bundle on claude.ai

`genjutsu.zip` packs the router + `cast` + `paint` + `bunshin` + all `_jutsu` sub-skills into one uploadable skill. Because claude.ai skill mounting has had regressions (anthropics/claude-code#26254), verify it end to end on a real account before relying on it.

> **Bundle structure.** claude.ai accepts exactly **one `SKILL.md`** per uploaded skill, so inside the bundle only the router is `SKILL.md`. `cast`, `paint`, `bunshin` and every sub-skill ship as `GUIDE.md` (renamed at packaging time, references repointed) and are `cat`'d by the router and orchestrators at runtime.

## Prerequisites
- A claude.ai plan with **Code execution** enabled (Pro, Max, Team, or Enterprise).
- `genjutsu.zip` from the latest [release](https://github.com/AThevon/genjutsu/releases) (or built locally via `./package-for-claude-ai.sh`).

## 1. Upload
1. **Customize > Skills > Upload skill** and upload `genjutsu.zip`.
2. Confirm it appears as a single skill named **genjutsu** and toggle it on.

## 2. Smoke-test the mount (~30s)
Start a chat and paste:

> Run this and paste the output:
> ```bash
> ls /mnt/skills/ ; echo "---" ; find /mnt/skills -maxdepth 3 -type d -name _jutsu ; echo "---" ; ls /mnt/skills/plugins/genjutsu/ /mnt/skills/user/genjutsu/ 2>/dev/null
> ```

Expect:
- `plugins` among the entries of `/mnt/skills/` (claude.ai mounts uploaded skills under
  `/mnt/skills/plugins/<name>/` since 2026-09; accounts on the older layout show
  `/mnt/skills/user/<name>/` instead, and genjutsu resolves both),
- a `_jutsu` directory found (e.g. `/mnt/skills/plugins/genjutsu/_jutsu`),
- `SKILL.md  bunshin  cast  paint  _jutsu` inside `genjutsu/`.

If the `find` prints nothing, the bundle's files did not mount (the #26254 regression). Stop and open an issue with the step 2 output.

## 3. Functional test - cast (enhance existing UI)
> "Add a subtle scroll-reveal animation to a hero section in plain HTML/CSS."

Confirm the assistant: routes to the **cast** pipeline, resolves sub-skills with no `genjutsu: sub-skill '<name>' NOT LOADED` line, and proposes an interaction thesis before writing code.

## 4. Functional test - paint (build from scratch)
> "Design a visual identity for a fintech landing page from scratch."

Confirm it routes to **paint** (brainstorm first), and that `ui-ux-pro-max` loads (e.g. it runs `scripts/search.py ... --design-system`).

## 5. Functional test - bunshin (steps down on claude.ai)

**Not run on claude.ai yet.** No release has logged this step. The expectation below comes from
how the repo reads the host, not from a run: as far as this repo knows, claude.ai gives a skill a
shell and file tools but no tool that spawns a subagent, and bunshin has nothing to run on
without one. Its answer there is to say so and step down to `paint`, never to play the clones
itself in one context.

a. Ask for it by name, since the router picks bunshin on no other signal:

> "Use bunshin to build a five-page website for a neighbourhood bakery, from scratch."

Confirm the assistant:
- runs the router's bunshin block (it prints `genjutsu: pipeline file .../genjutsu/bunshin/GUIDE.md`),
- says in a line or two, before any tier, cost table or product question, that this host cannot
  spawn subagents so bunshin cannot run here, and that it continues with `paint`,
- then reads `genjutsu/paint/GUIDE.md` and starts paint from Phase 1: the stack scan, the
  declared read (`My read so far: ...`), then the brainstorm,
- writes nothing presented as a clone's output (no "Clone 1", no parallel research sections, no
  review lenses), and never asks the bunshin tier question.

b. The same brief without the name:

> "Build a five-page website for a neighbourhood bakery, from scratch."

Confirm it routes to **paint** and that paint does **not** propose bunshin: its escalate step
requires a host that can spawn subagents, and this one cannot.

If bunshin runs instead, look at how. Clones written out as text in one reply are a genjutsu
bug: open an issue with the transcript. Real subagent tool calls mean the host has a tool this
page does not know about: log its name as the session lists it and open an issue, because this
step, and the claude.ai row of the Orchestration section in `skills/_jutsu/VERSIONS.md`, assume it
is absent.

## 6. Resolution failure signals
If at any point you see `genjutsu: could not find the genjutsu modules` (the pipeline must then stop) or `sub-skill '<name>' NOT LOADED`, path detection failed. Capture the `/mnt/skills/` layout from step 2 and open an issue.

## 7. Log

| Date | Release commit | Upload | Mount (step 2) | cast (step 3) | paint (step 4) | bunshin (step 5) | Notes |
|---|---|---|---|---|---|---|---|
| 2026-09-28 | 4c651e7 | accepted: one skill `genjutsu`, 97 files | `/mnt/skills/plugins/genjutsu/` with `_jutsu` (17 entries, `tells` among them); no `/mnt/skills/user` | routed to cast, asked the preview mode, showed the thesis as an artifact plus a text summary, stopped for validation | not run | n/a (before bunshin) | the same test on 3a5e3c0, before the `/mnt/skills/plugins` fix, skipped the pipeline and answered directly |

## Pass criteria
- One upload, one skill.
- The three pipelines reachable from the single skill.
- No missing-sub-skill warnings.
- `ui-ux-pro-max`'s `--design-system` runs.
- bunshin, asked for by name, steps down to paint and says why; paint never proposes bunshin on this host.
