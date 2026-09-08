<!-- What changed, and the source it was checked against. One concern per PR. -->

**Source:**

---

- [ ] Version-sensitive claim? Its `skills/_jutsu/VERSIONS.md` row and date are updated in this PR.
- [ ] Touched `cast` or `paint`? The change is byte-identical in both inside the `genjutsu:shared:*` regions.
- [ ] Did not hand-edit `skills/_jutsu/ui-ux-pro-max/data|scripts|references` (vendored, see `UPSTREAM.md`).
- [ ] `./scripts/check-shared-blocks.sh`, `./scripts/check-denylist.sh` and `python3 scripts/validate-skills.py` pass locally.

<!-- First PR here? GitHub holds the workflow runs until the maintainer approves them,
     so an empty checks tab is that, not a broken pipeline. -->
