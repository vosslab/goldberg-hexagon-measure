# Changelog

## 2026-05-27

### Additions and New Features

- Added the initial `goldberg_brick` Python package and `goldberg-brick` CLI for graph-only
  Markdown reports.
- Added geodesic triangulation, Goldberg dual graph construction, and deterministic hexagon
  orbit grouping under orientation-preserving icosahedral rotations.
- Added `run_goldberg_brick.py` as a root-level runner for the package CLI.
- Added spherical representative geometry measurements for each hexagon orbit, including side
  lengths, internal angles, planarity error, and dihedral angles.
- Added builder-facing pattern summaries and reuse groups derived from measured geometry.
- Added letter-based angle, side, and dihedral pattern codes with oriented and mirror-aware
  canonical forms.
- Simplified report tables by hiding redundant mirror-aware pattern columns unless they differ.

### Behavior or Interface Changes

- Removed the `--h` and `--k` long flags so `-h` and `--help` remain normal help options.
- Made `--out` optional with default report path `gp_H_K_report.md`.
- Made the CLI print progress messages and end with the output report path.
- Updated the hexagon orbit report table to include measured geometry columns while keeping
  `deformation_mode` and `brick_strategy` as `NA`.
- Moved raw hexagon measurements below builder-facing summary and reuse sections.

### Developer Tests and Notes

- Added tests for index validation, known Goldberg counts, base icosahedron rotations,
  dual graph counts, orbit coverage, and CLI report writing.
- Expanded graph proof tests to `GP(1,0)`, `GP(1,1)`, `GP(2,0)`, `GP(2,1)`, `GP(3,0)`,
  `GP(3,1)`, and `GP(4,2)`, including rotation preservation and measured geometry checks.
