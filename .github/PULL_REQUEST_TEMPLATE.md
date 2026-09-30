<!-- What changed, and the source it was checked against. One concern per PR. -->

**Source:**

---

- [ ] Version-sensitive claim? Its `skills/_jutsu/VERSIONS.md` row and date are updated in this PR.
- [ ] Touched `cast`, `paint` or `bunshin`? Inside the `genjutsu:shared:*` regions the change is byte-identical in every file that carries the region (`escalate` is in `cast` and `paint` only).
- [ ] Touched a workflow template in `skills/_jutsu/orchestration/workflows/`? A new or renamed argument is in its fixtures in `scripts/tests/fixtures/workflows/`, so `scripts/check-workflows.mjs` runs it with a value.
- [ ] Did not hand-edit `skills/_jutsu/ui-ux-pro-max/data|scripts|references` (vendored, see `UPSTREAM.md`).
- [ ] `./scripts/check-shared-blocks.sh`, `./scripts/check-denylist.sh`, `python3 scripts/validate-skills.py` and `node scripts/check-workflows.mjs` pass locally.

<!-- First PR here? GitHub holds the workflow runs until the maintainer approves them,
     so an empty checks tab is that, not a broken pipeline. -->
