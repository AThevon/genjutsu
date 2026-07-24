# Upstream: ui-ux-pro-max

The `ui-ux-pro-max` sub-skill is **vendored** from an external open-source project.

- **Source**: [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- **License**: MIT (same as genjutsu). The upstream MIT terms apply to the vendored dataset (`data/`) and search engine (`scripts/`). Copyright is held by the upstream author(s) (github.com/nextlevelbuilder).
- **Vendored**: an early/mid-2026 snapshot, adapted for genjutsu.

## genjutsu-specific divergences (do not blindly overwrite on sync)

- `scripts/` carry genjutsu's own `safe_path_component()` fix for the `--persist` path-traversal issue (see CHANGELOG v3.0.2). Upstream fixed the same class of bug independently via `safe_slug()`.
- `SKILL.md` is rewritten for genjutsu (voice, "internal module" framing, orchestrator integration) - it is NOT the upstream SKILL.md.
- The upstream agent-run install commands (`sudo` / `brew` / `winget`) were removed - they trip supply-chain audits, and upstream removed them too.
- Stacks are curated to genjutsu's scope (Web / Compose / SwiftUI). Upstream ships more stacks (Angular, WPF, WinUI, JavaFX, ...) that are intentionally not vendored here.
- The dataset counts stated in `SKILL.md` reflect the **vendored** data, not upstream's (which is larger).

## Keeping it fresh

Upstream keeps growing (palettes and products roughly doubled, plus new `google-fonts.csv` / `motion.csv` and more stacks). A refresh is optional and should be a **manual cherry-pick** of new CSV rows that match this copy's schema (colors, products, ui-reasoning, typography are the high-value ones) - never a blind re-vendor, which would clobber the divergences above.
