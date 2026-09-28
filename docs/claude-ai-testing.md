# Testing the genjutsu bundle on claude.ai

`genjutsu.zip` packs the router + `cast` + `paint` + all `_jutsu` sub-skills into one uploadable skill. Because claude.ai skill mounting has had regressions (anthropics/claude-code#26254), verify it end to end on a real account before relying on it.

> **Bundle structure.** claude.ai accepts exactly **one `SKILL.md`** per uploaded skill, so inside the bundle only the router is `SKILL.md`. `cast`, `paint` and every sub-skill ship as `GUIDE.md` (renamed at packaging time, references repointed) and are `cat`'d by the router and orchestrators at runtime.

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
- `SKILL.md  cast  paint  _jutsu` inside `genjutsu/`.

If the `find` prints nothing, the bundle's files did not mount (the #26254 regression). Stop and open an issue with the step 2 output.

## 3. Functional test - cast (enhance existing UI)
> "Add a subtle scroll-reveal animation to a hero section in plain HTML/CSS."

Confirm the assistant: routes to the **cast** pipeline, resolves sub-skills with no `genjutsu: sub-skill '<name>' NOT LOADED` line, and proposes an interaction thesis before writing code.

## 4. Functional test - paint (build from scratch)
> "Design a visual identity for a fintech landing page from scratch."

Confirm it routes to **paint** (brainstorm first), and that `ui-ux-pro-max` loads (e.g. it runs `scripts/search.py ... --design-system`).

## 5. Resolution failure signals
If at any point you see `genjutsu: could not find the genjutsu modules` (the pipeline must then stop) or `sub-skill '<name>' NOT LOADED`, path detection failed. Capture the `/mnt/skills/user` layout from step 2 and open an issue.

## 6. Log

| Date | Release commit | Upload | Mount (step 2) | cast (step 3) | paint (step 4) | Notes |
|---|---|---|---|---|---|---|

## Pass criteria
- One upload, one skill.
- Both pipelines reachable from the single skill.
- No missing-sub-skill warnings.
- `ui-ux-pro-max`'s `--design-system` runs.
