# Upstream: ui-ux-pro-max

The `ui-ux-pro-max` sub-skill's dataset and search engine are **vendored** from an external open-source project and kept in sync with it.

- **Source**: [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- **License**: MIT - "Copyright (c) 2024 Next Level Builder". The upstream MIT terms cover the vendored `data/`, `scripts/` and `references/`.
- **Synced to**: upstream **v2.11.0**.

## Vendored vs genjutsu-authored

- **Vendored verbatim from upstream v2.11.0**: `data/` (all CSVs, including `google-fonts.csv`, `motion.csv`, `app-interface.csv`, and 22 stack files), `scripts/` (`core.py`, `design_system.py`, `search.py`, `validate_data.py`, `tests/`), and `references/`.
- **genjutsu-authored** (do NOT overwrite on the next sync): `SKILL.md` - rewritten for genjutsu (voice, "internal module" framing, orchestrator path resolution, no agent-run install commands). Its dataset counts are kept in sync with the vendored data by hand.

## Notes

- The `--persist` path-traversal hardening is upstream's `safe_slug()` (upstream PR #417). It supersedes genjutsu's earlier standalone `safe_path_component()` fix (v3.0.2, thanks @reevesc88, still credited in the CHANGELOG). Both close the same arbitrary-write vector.
- Some vendored stacks (WPF, WinUI, UWP, JavaFX, Avalonia, Uno, Laravel, Angular) sit outside genjutsu's creative-coding focus (Web / Compose / SwiftUI). They are kept for a clean upstream mirror; the orchestrators only load this skill for design-intelligence lookups, not for per-stack detection.

## Re-syncing later

1. Clone upstream, copy its `ui-ux-pro-max` `data/` + `scripts/` + `references/` over this folder.
2. Keep genjutsu's `SKILL.md`; update the dataset counts in its frontmatter and body (plus README and motion-principles) to match the new data.
3. Smoke-test: `python3 scripts/search.py "test query" --design-system`, then `python3 scripts/validate_data.py`.
