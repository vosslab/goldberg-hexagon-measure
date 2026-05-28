# Fix: missing chiral b=a reduction for Class III GP(h,k)

## Context

Audit `docs/active_plans/active/solver_paper_parity.md` identified Schein-Gayed
2014 C16 (chiral b=a perimeter reduction) as not implemented in
`goldberg_brick/equilateral.py`. For Class III cages (h != k, h,k > 0),
Schein-Gayed C16 specifies that internal angles around the 5gon perimeter
satisfy b=a, reducing both independent-variable count and zero-DAD-equation
count by one. The audit verdict on Open Question 4 (GP(4,2) Stage B rollback
-- bug, missing constraint, or real geometric limitation?) is **missing
constraint**: without the C16 reduction, the LM solver has one extra free
DOF for Class III cages, and Stage B (planarity + DAD) can settle into a
local non-planar minimum (warp_mode = boat/chair/asymmetric) instead of the
unique polyhedral solution Schein-Gayed C14 guarantees.

GP(4,2) is the most visible affected case: h=4, k=2, T=28, Class III. Per
CHANGELOG 2026-05-28, it currently converges Stage A (edge_stddev < 1e-7)
but does not reach planar and is reported with a warp_mode label.

## Objectives

- Add the Schein-Gayed C16 chiral reduction (b=a around 5gon perimeter) as
  an additional residual / symmetry-tying constraint for Class III cages.
- Verify GP(4,2) reaches Stage B planar (planarity_error < 1e-7 on every
  hex orbit, warp_mode = planar) after the change.
- Re-validate all seven currently-tested (h,k) cases still converge Stage A
  and where applicable Stage B.
- Decide whether to extend the same reduction logic to chiral cases not yet
  in the tested set (e.g. GP(2,1) = T=7 chiral).

## Design philosophy

Fix the design (Schein-Gayed C16 is required for chiral cages), not the
symptom (current code labels the resulting non-planar hexagons as warp).
The audit suspects Class III under-constraint; verify by adding C16 first
and observing whether Stage B reaches planar. If GP(4,2) still rolls back
after C16, escalate to a full symmetry-reduced solver redesign (Liu 2022
L4/L6 (C,R) parametrization).

## Scope

In scope:
- `goldberg_brick/equilateral.py` `compute_residuals` and
  `build_dad_edge_specs`: emit the additional perimeter b=a residuals for
  Class III.
- `goldberg_brick/orbits.py`: identify the 5gon-perimeter hexagon orbit
  (the orbit whose hex faces share an edge with a pentagon).
- `tests/test_equilateral_validation.py`: extend assertions to require
  GP(4,2) warp_mode == planar.

Out of scope:
- Liu 2022 (C,R) parametrization rewrite -- only if the C16 fix alone is
  insufficient.
- k-means edge-length grouping (Liu L16) -- separate feature, not
  correctness.
- Tet/oct dispatch -- icosahedral-only by design.

## Non-goals

- Not redesigning the solver from LM to a symmetry-reduced angle solver.
- Not removing the Stage A / Stage B split.

## Architecture boundaries

Single-component change in `equilateral.py` plus a small helper in
`orbits.py`. No new module. No API change at the `force_attempt_solve`
boundary.

## Verification

- `tests/test_equilateral_validation.py` extended: assert GP(4,2)
  `warp_mode == planar` and `planarity_error < 1e-7` per hex orbit.
- All seven currently-tested (h,k) cases continue to converge Stage A.
- Spot-check internal angles against Schein-Gayed Table 1 reference where
  available (T=4, T=7, T=9, T=12, T=16 in the paper). If close, the C16
  reduction is correct; if off, the reduction is being applied to the
  wrong orbit.
- Run `source source_me.sh && python3 run_goldberg_brick.py -H 4 -K 2
  -o /tmp/gp42_report.md` and inspect the report's `warp mode` column
  and planarity_status.

## Risks

| Risk | Trigger | Mitigation |
|---|---|---|
| C16 alone insufficient | GP(4,2) still rolls back after b=a residuals added | Escalate to Liu L4/L6 symmetry-reduced parametrization in a new plan |
| Reduction applied to wrong orbit | Stage A converges but internal angles drift from Schein-Gayed Table 1 | Use SG Table 1 as regression check; identify perimeter orbit by graph adjacency to pentagon faces |
| Breaks Class II (h=k) | sole-degree b=a reduction over-constrains Class II | Guard C16 emission on `class == "III"` only |
| Numerical conditioning worsens | LM converges slower or fails Stage A | Tune dad_weight; verify Stage A gate edge_stddev < 1e-7 still passes |

## Open decisions

- Owner: TBD (assign at user return).
- Whether to emit the b=a residual unconditionally for Class III or behind
  a flag. Recommendation: unconditional; the reduction is mandatory per
  Schein-Gayed for a polyhedral solution to exist.
