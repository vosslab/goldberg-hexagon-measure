# Divergence: missing paper citations in docstrings

## Source

Audit `docs/active_plans/active/solver_paper_parity.md`, M4 routing.

## Summary

Several functions implement paper claims but do not cite the source paper
in their docstring or comments. documentation_only severity.

## Specific gaps

| file:line | function | implements | missing cite |
|---|---|---|---|
| geometry.py:579 | `classify_warp_mode_from_geometry` | Schein-Gayed Fig. 2F (boat 122122, chair 121212) | "Schein-Gayed 2014, Fig. 2F" |
| geometry.py:317 | `planarity_error` | Schein-Gayed C9 (planarity criterion); Liu L7 (3 d_i=0 per face) | "Schein-Gayed 2014; Liu 2022 Eq. 3.1" |
| equilateral.py:438 | `force_attempt_solve` Stage B planarity residual | Schein-Gayed C19 (DAD=0 alone insufficient) | already cites Schein-Gayed by name; add C19 specifically |
| indices.py:41 | `calculate_t_number` | Schein-Gayed C3 / Siber S1 / Brinkmann B1 | "Caspar-Klug T-number; Schein-Gayed 2014 Eq. (1)" |
| dual.py:67 | `build_goldberg_graph` | Siber S6 (face-center dualization); Brinkmann B6 (Goldberg vs CK duality) | "Siber 2020 Sec. 3; Brinkmann-Schein 2017 Sec. 4" |
| icosahedron.py:267 | `build_rotations` | uses I (60), not Ih (120); correct per Brinkmann B4 | "Brinkmann-Schein 2017 B4: orientation-preserving only for chiral cages" |

## Optional: benchmark harness

Liu L13 / L19 provides angle reproductions to 10 decimals against
Schein-Gayed Table 1 for C(3,0), C(2,2), C(2,1), C(8,0). A regression test
that asserts internal angles match Schein-Gayed reference values would
catch solver regressions. Not implemented; not required for current
report output. Would live under `tests/test_equilateral_angles.py`.

## Severity

documentation_only. No geometry change.

## Proposed owner

TBD. Lowest priority; cosmetic.
