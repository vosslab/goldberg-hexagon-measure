# Changelog

## 2026-05-28

### Behavior or Interface Changes

- Refactored `goldberg_brick.equilateral.force_attempt_solve` into a
  two-stage solver. Stage A (globally-equilateral; edge_stddev < 1e-7)
  is the hard gate; Stage B (planarity plus DAD nulling) is a soft
  refinement that rolls back to Stage A on degenerate intermediate
  configs. All seven currently-tested (h,k) -- (1,1), (2,0), (2,1),
  (2,2), (3,0), (3,1), (4,2) -- now converge Stage A and write reports.
  Hexagons that do not reach planar carry the appropriate `boat`,
  `chair`, or `asymmetric` warp_mode label.
- Removed the `KNOWN_NONCONVERGENT_CASES` constant and its advisory
  shortcut path in `goldberg_brick.equilateral`. Papers (Schein-Gayed
  2014, Liu 2022) do not enumerate "non-convergent" cases; globally-
  equilateral icosahedral cages exist mathematically for every (h,k),
  so solver limitations are debugged, not denylisted.
- Removed `devel/reevaluate_equilateral.py`; the new solver contract
  is verified by `tests/test_equilateral_validation.py` running every
  supported (h,k) end-to-end.
- Speed: `compute_residuals` now accepts an optional `face_orderings`
  argument so Stage B residual evaluations skip the per-call O(F^2)
  rediscovery of vertex IDs. GP(4,2) Stage B drops from ~150 s to ~8 s.
- Rewrote `removed`
  around the two-stage architecture. The "if a case fails Stage A,
  debug the solver" recovery strategies replace the old M0 evidence
  ladder.
- Replaced the [docs/USAGE.md](USAGE.md) Convergence matrix with a
  Supported cases table; the binary "converges? yes/no" column is gone.

### Fixes and Maintenance

- Updated `tests/test_equilateral_validation.py` to assert every
  supported (h,k) writes a report and that GP(4,2) reports carry a
  warp_mode label. Removed the refusal-on-known-nonconvergent test
  (no longer applicable).

### Additions and New Features

- Added `goldberg_brick.equilateral.force_attempt_solve(h, k)` as the
  validation-gated solver entry point that bypasses the advisory shortcut and
  always runs the symmetry-reduced two-stage LM optimizer.
- Added `devel/reevaluate_equilateral.py` (runnable as a script) that iterates
  over `KNOWN_NONCONVERGENT_CASES`, calls `force_attempt_solve` per case, and
  prints current residuals or a `RECONSIDER:` line if a case now passes.
- Promoted the M0 solver-stabilization investigation out of `docs/archive/` to
  `removed`as the canonical
  evidence reference for non-converging (h,k) cases.
- Added a `## Convergence matrix` section to [docs/USAGE.md](USAGE.md) listing every
  supported (h,k), its T number and symmetry class, and whether the equilateral
  solver converges.
- Added `tests/test_equilateral_validation.py` covering the validation-gated
  CLI guard, supported cases, and the `force_attempt_solve` evidence-refresh
  check.

### Behavior or Interface Changes

- Renamed `goldberg_brick.geometry.triangle_centroid_coordinate` to
  `_geodesic_triangle_centroid_on_sphere` (private). Used only as the
  solver's initial-guess seed and for tangent-plane ordering of incident
  triangles; not a geometry-construction entry point. Updated the call
  site in `goldberg_brick.equilateral`.
- Scrubbed stale `--construction centroid` recommendations from
  `removed`;
  M0 experiment descriptions (what was tried) are preserved.
- Removed the `--construction` flag (and the `centroid` construction mode)
  from the CLI. The only supported construction is the Schein-Gayed equilateral
  one; non-converging (h,k) pairs exit with status 2 and write no report.
- Removed the `DIAGNOSTIC REPORT` banner and the `construction:` line from the
  report header; reports now carry a static `model: equilateral-goldberg`
  marker.
- Removed the `construction` argument from
  `goldberg_brick.report.render_markdown_report`,
  `goldberg_brick.report.write_markdown_report`,
  `goldberg_brick.geometry.compute_hexagon_orbit_geometries`,
  `goldberg_brick.geometry.face_points_for_source`,
  `goldberg_brick.geometry.ordered_goldberg_vertices`,
  `goldberg_brick.geometry.dihedral_angles`, and
  `goldberg_brick.cli.build_report`. The centroid placement path is gone;
  geodesic triangle centroids remain as a private initial-guess helper inside
  the solver.
- Replaced `DEMOTED_EQUILATERAL_CASES` (hard rule) with
  `KNOWN_NONCONVERGENT_CASES` (advisory shortcut). The CLI no longer consults
  the list directly; it runs the solver and surfaces validation-gate
  residuals through a narrow `try`/`except ConvergenceError` boundary.
- `solve_schein_gayed_positions(h, k)` is now a thin wrapper that consults the
  advisory list, then delegates to `force_attempt_solve`. The validation gate
  (edge_stddev < 1e-7 AND max_planarity < 1e-7) is the source of truth.

### Removals and Deprecations

- Removed `goldberg_brick.equilateral.DEMOTED_EQUILATERAL_CASES` (renamed to
  `KNOWN_NONCONVERGENT_CASES` with advisory semantics).
- Removed `tests/test_demotion_hardening.py`; replaced by
  `tests/test_equilateral_validation.py`.
- Deleted the centroid-construction code paths in `goldberg_brick.geometry`
  and the centroid-report tests in `tests/test_counts.py` and
  `tests/test_orbits.py`; those tests were locking in dead code.

### Removals and Deprecations

- Removed the dead `--model`/`-m` argparse flag and `SUPPORTED_MODELS` constant
  from `goldberg_brick.cli`. Dropped the `model: str` parameter from
  `goldberg_brick.cli.build_report`, `goldberg_brick.report.render_markdown_report`,
  and `goldberg_brick.report.write_markdown_report`. Removed the
  `print(f"Model: {model}")` line and updated the parser description to
  "Write a Goldberg Brick report." Updated `tests/test_counts.py` call sites.

### Decisions and Failures

- Decided to delete the centroid construction mode entirely rather than keep
  it as an opt-in diagnostic. With only one supported construction, the
  `--construction` flag, the `DIAGNOSTIC REPORT` banner, and the `construction`
  argument threaded through the report and geometry layers all dropped out.
- Decided against a hard-coded `DEMOTED_EQUILATERAL_CASES` list: it disguised
  the validation gate as the source of truth. The list became an advisory
  shortcut (`KNOWN_NONCONVERGENT_CASES`) and the CLI now runs the real solver
  and surfaces its residuals.
- GP(4,2) is kept in `KNOWN_NONCONVERGENT_CASES`: the equilateral solver
  raises `ConvergenceError` from the validation gate before reaching the
  `polygon_normal` `ValueError` path that previously crashed the report.

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
- Added Schein-Gayed equilateral solver in `goldberg_brick/equilateral.py` with symmetry-reduced
  two-stage least-squares fit; converges to ~1e-15 residual for five of six target cases.
- Added `--construction {equilateral,centroid}` CLI flag with equilateral as default construction
  method for hexagon orbits.
- Added `connector_counts()` API in `goldberg_brick.geometry` returning per-orbit angle/side/dihedral
  classes with per-face and orbit-total multiplicities.
- Added `## Per-orbit connector counts` section to reports with one sub-block per hexagon orbit.
- Added `classify_brick_strategy()` returning `repeatable-panel` / `hinge-required` / `custom` based
  on warp mode, side spread, and angle-pattern complexity.
- Added `docs/USAGE.md` MOC-builder walkthrough with GP(2,1) and GP(2,2) worked examples and
  connector-count tables.

### Behavior or Interface Changes

- Removed the `--h` and `--k` long flags so `-h` and `--help` remain normal help options.
- Made `--out` optional with default report path `gp_H_K_report.md`.
- Made the CLI print progress messages and end with the output report path.
- Updated the hexagon orbit report table to include measured geometry columns while keeping
  `deformation_mode` and `brick_strategy` as `NA`.
- Moved raw hexagon measurements below builder-facing summary and reuse sections.
- Added `-u/--units {unit,mm,stud}` flag (default `unit`) and `-s/--scale FLOAT` flag (default 1.0)
  to scale linear measurements in reports; units and scale are displayed in the Summary section and
  in column headers for side lengths and planarity error; angles and dihedral angles remain
  unchanged regardless of scale.
- Report Summary section now displays `construction:` and `metric:` lines; removed `model: graph-only` line.
- GP(2,0) automatically falls back to centroid construction with stderr notice when equilateral solver
  fails to converge; equilateral construction still used as initial method.
- Report `deformation_mode` column now reflects measured warp (planar / boat / chair / asymmetric)
  instead of hard-coded `NA`.
- Report `brick_strategy` column now classifies each orbit (repeatable-panel / hinge-required / custom)
  instead of hard-coded `NA`.

### Fixes and Maintenance

- GP(2,2) hexagon orbit warped patterns now match Schein-Gayed / Liu 2022 Table 2 literature values;
  equilateral orbits report cddcdd-equivalent and aabaab-equivalent patterns with Liu parameters
  a=125.264°, b=109.471°, c=138.190°, d=110.905°.

### Decisions and Failures

- GP(2,0) class I T=4 demoted to pattern-only coverage and centroid construction; Schein-Gayed's
  spoke-edge DAD-nulling formulation does not yield a planar equilateral solution in the
  icosahedral-symmetric 4-DOF subspace (5 experiments: final residual ~1.36, cost ~0.92,
  independent of weighting and restart).
- GP(4,2) also requires centroid construction fallback; solver does not converge in current
  implementation (outside the six target cases for M1 scope).

### Developer Tests and Notes

- Added tests for index validation, known Goldberg counts, base icosahedron rotations,
  dual graph counts, orbit coverage, and CLI report writing.
- Expanded graph proof tests to `GP(1,0)`, `GP(1,1)`, `GP(2,0)`, `GP(2,1)`, `GP(3,0)`,
  `GP(3,1)`, and `GP(4,2)`, including rotation preservation and measured geometry checks.
- Added `tests/reference_values.py` and `docs/reference_values.md` with Liu (2022) Table 2 literature
  citations for GP(2,2) warped orbits and equilateral angle patterns.
- Removed `xfail` decorator from `test_gp_2_2_60_face_orbit_angle_sequence_literature` (now passes consistently).
- Updated orbit tests to specify `construction="centroid"` for GP(2,0) and GP(4,2); test suite shows
  264 passed, zero xfailed on GP(2,2) angle pattern tests.
- Audit: paper-code parity sweep of `articles/*.txt` against `goldberg_brick/`.
  Master report at
  [docs/active_plans/active/solver_paper_parity.md](active_plans/active/solver_paper_parity.md).
  Scope narrowed to solver/report geometry (priority papers schein-gayed-2014
  and liu-2022; secondary siber-2020 and brinkmann-schein-2017; background
  johnson-2021, twarock-2019, voytekhovsky-2018, mannige-2010,
  virus_T-number_images). Three spot-checks passed (Schein-Gayed Eq. 1
  dihedral formula, T-number formula, face-count formulas). One
  correctness_blocker filed:
  [docs/active_plans/active/fix_chiral_reduction.md](active_plans/active/fix_chiral_reduction.md)
  -- Schein-Gayed C16 chiral b=a perimeter reduction is missing for Class III
  cages and is the most likely cause of GP(4,2) Stage B rollback to a
  non-planar warp_mode (Decisions and Failures item above). Two
  documentation_only stubs filed:
  [docs/active_plans/active/divergence_chirality_labels.md](active_plans/active/divergence_chirality_labels.md)
  (chirality flag / laevo-dextro / canonical ordering) and
  [docs/active_plans/active/divergence_paper_citations.md](active_plans/active/divergence_paper_citations.md)
  (missing paper cites in docstrings).
