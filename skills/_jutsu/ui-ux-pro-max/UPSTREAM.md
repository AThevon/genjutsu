# Upstream: ui-ux-pro-max

The `ui-ux-pro-max` sub-skill's dataset, references and search engine are **vendored**
from an external open-source project.

- **Source**: [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill),
  in that repo at `.claude/skills/ui-ux-pro-max/`.
- **License**: MIT, Copyright (c) 2024 Next Level Builder. Their permission notice is
  vendored at [`LICENSE-upstream.txt`](./LICENSE-upstream.txt) and is referenced from the
  repository root `LICENSE`. It covers the vendored `data/`, `scripts/` and `references/`.
- **Synced to**: upstream **v2.11.1**, verified 2026-09-08 by comparing git blob hashes
  file by file, not by reading a version string.

## What "v2.11.1" means, precisely

Every vendored file - `data/` (all CSVs), `scripts/` (`core.py`, `design_system.py`,
`search.py`, `validate_data.py`, `tests/`) and `references/` (`pro-rules.md`,
`quick-reference.md`) - matches upstream's blob at tag v2.11.1.

Two things follow, and both correct what this file used to claim:

- It is **not** v2.11.0. That tag has no `references/`, no `validate_data.py` and no
  `tests/`; all three arrived in v2.11.1. A sync described as v2.11.0 would have deleted
  them.
- Those same blobs are **unchanged upstream through v2.14.0**. So despite the tag gap,
  the vendored tree is not drifting: v2.15.0 is the first release that actually diverges.

## Divergence as of 2026-09-08 (upstream is at v2.15.0)

| Upstream change | Landed in |
|---|---|
| `core.py` grows 464 -> 993 lines | v2.15.0 |
| New `scripts/reasoning_contract.py`, imported by the other scripts | v2.15.0 |
| New data files: `catalog-summary.json`, `data-provenance.json`, `google-font-licenses.json`, `phosphor-icons-upstream.json` | v2.15.0 |

A sync is therefore a single jump from v2.11.1 to v2.15.0, and it is an engine rewrite
rather than a data refresh. Whether it is worth taking is an open question, not a chore:
no orchestrator invokes `search.py` directly - `paint` Phase 3 loads this `SKILL.md`, and
the script runs only if the model chooses to follow the workflow described in it. Decide
whether this sub-skill is load-bearing before spending a sync on it.

## Vendored vs genjutsu-authored

- **Vendored verbatim**: `data/`, `scripts/`, `references/`, `LICENSE-upstream.txt`.
- **genjutsu-authored, never overwrite on a sync**: `SKILL.md` (rewritten for genjutsu:
  voice, "internal module" framing, orchestrator path resolution, no agent-run install
  commands) and this file. `SKILL.md`'s dataset counts are kept in sync with the vendored
  data by hand.

## Notes

- The `--persist` path-traversal hardening is upstream's `safe_slug()` (upstream PR #417).
  It supersedes genjutsu's earlier standalone `safe_path_component()` fix (v3.0.2, thanks
  @reevesc88, still credited in the CHANGELOG). Both close the same arbitrary-write vector.
- Eight vendored stacks (WPF, WinUI, UWP, JavaFX, Avalonia, Uno, Laravel, Angular) sit
  outside genjutsu's creative-coding focus of Web / Compose / SwiftUI. They are kept so
  this stays a clean mirror; the orchestrators only load this sub-skill for
  design-intelligence lookups, never for per-stack detection.

## Re-syncing later

1. `gh api repos/nextlevelbuilder/ui-ux-pro-max-skill/contents/.claude/skills/ui-ux-pro-max?ref=<tag>`
   to see the tree, then copy its `data/`, `scripts/` and `references/` over this folder.
2. Copy its `LICENSE` to `LICENSE-upstream.txt` as well - it can change.
3. Keep genjutsu's `SKILL.md`; update the dataset counts in its frontmatter and body
   (plus the README and `motion-principles`) to match the new data.
4. Verify the sync by hash rather than by tag name:
   `git hash-object scripts/core.py` against
   `gh api .../scripts/core.py?ref=<tag> --jq .sha`.
5. Smoke-test: `python3 scripts/validate_data.py`, then
   `python3 -m unittest discover -s scripts/tests`, then
   `python3 scripts/search.py "test query" --design-system`.
6. Update the "Synced to" line above with the tag and the date you verified it.
