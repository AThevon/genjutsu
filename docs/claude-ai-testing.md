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
> ls -d /mnt/skills/user/*/ ; echo "---" ; find /mnt/skills/user -maxdepth 2 -type d -name _jutsu ; echo "---" ; ls /mnt/skills/user/genjutsu/ 2>/dev/null
> ```

Expect:
- a `genjutsu` directory under `/mnt/skills/user/`,
- a `_jutsu` directory found (e.g. `/mnt/skills/user/genjutsu/_jutsu`),
- `SKILL.md  cast  paint  _jutsu` inside `genjutsu/`.

If the `find` prints nothing, the bundle's files did not mount (the #26254 regression). Fall back to uploading the individual skill ZIPs for now and report it.

## 3. Functional test - cast (enhance existing UI)
> "Add a subtle scroll-reveal animation to a hero section in plain HTML/CSS."

Confirm the assistant: routes to the **cast** pipeline, resolves sub-skills with no `genjutsu: sub-skill '<name>' not found` warning, and proposes an interaction thesis before writing code.

## 4. Functional test - paint (build from scratch)
> "Design a visual identity for a fintech landing page from scratch."

Confirm it routes to **paint** (brainstorm first), and that `ui-ux-pro-max` loads (e.g. it runs `scripts/search.py ... --design-system`).

## 5. Resolution failure signals
If at any point you see `genjutsu: could not resolve the sub-skills directory` or `sub-skill '…' not found`, path detection failed. Capture the `/mnt/skills/user` layout from step 2 and open an issue.

## 6. An individual module ZIP carrying `metadata.internal`

Every module declares a `metadata:` block with `internal: true` in its frontmatter: an unquoted
YAML boolean, because the `npx skills` CLI tests it with `=== true`. claude.ai validates the
frontmatter of an uploaded skill, so check once per release that it accepts the field.

1. Build the ZIPs from the release commit: `./package-for-claude-ai.sh`.
2. **Customize > Skills > Upload skill**, and upload `dist/motion-principles.zip`.
3. Expect the upload to succeed and a skill named **motion-principles** to appear, listed like
   any other uploaded skill (the field hides modules from `npx skills`, not from claude.ai).
4. An error that mentions `metadata` or the frontmatter means claude.ai rejects the boolean.
   Stop the release and open an issue with the exact message.
5. Delete the uploaded module again, so the account holds only what you actually use.
6. Add one row to the log below.

| Date | Release commit | ZIP | Result | Exact message, if any |
|---|---|---|---|---|

## Pass criteria
- One upload, one skill.
- Both pipelines reachable from the single skill.
- No missing-sub-skill warnings.
- `ui-ux-pro-max`'s `--design-system` runs.
- An individual module ZIP carrying `metadata.internal` uploads without error (section 6, logged).
