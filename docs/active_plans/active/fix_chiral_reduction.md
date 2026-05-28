# Fix: missing chiral b=a reduction for Class III GP(h,k)

## Context

Audit `docs/active_plans/active/solver_paper_parity.md` identified Schein-Gayed
2014 C16 (chiral b=a perimeter reduction) as not implemented in
`goldberg_brick/equilateral.py`. For Class III cages (h != k, h,k > 0),
Schein-Gayed C16 specifies that internal angles around the 5gon perimeter
satisfy b=a, reducing both independent-variable count and zero-DAD-equation
count by one.

### Paper citation

Schein-Gayed 2014, main text p. 2923, Fig. 4A (and Fig. S2). SI Text Sec. 4.3
is the controlling source for the algebraic reduction. Verbatim from the
.txt extraction in `articles/`:

> "For chiral icosahedral cages (e.g., with T = 7), we can reduce by one the
> number of both independent variables and DAD equations ... by setting equal
> all of the internal angles around the perimeter of the corner faces (5gons),
> that is, by setting b = a (Fig. 4A)."

Pre-implementation check (REQUIRED before writing residuals): open
`articles/schein-gayed-2014*.pdf` Fig. 4A directly and confirm whether the
constraint is the single pair `b = a` (two named angles around each pentagon)
or "all perimeter angles equal" (stronger; all 5 perimeter angles per pentagon
identical). Plan body below assumes the single-pair form (b - a = 0) per
the verbatim quote; if Fig. 4A shows the stronger form, expand residuals
accordingly and document the change here before coding.

Angle naming convention (per SG Fig. 4A): around each pentagon corner, two
adjacent hexagon internal angles meet the pentagon edge. In Class II / achiral
cages these two angles differ (a, b distinct). In Class III chiral cages
the C16 reduction asserts b = a. The audit verdict on Open Question 4 (GP(4,2) Stage B rollback
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
- `goldberg_brick/equilateral.py` `compute_residuals` (lines 304-360 per
  the M2 sweep): emit the additional perimeter `b - a = 0` residuals for
  Class III only. Insertion point is after the existing pent/hex planarity
  residual block and before the return. Guard on
  `index_data.classify() == "III"` (or equivalent: h != k and h > 0 and k > 0).
- `goldberg_brick/equilateral.py` `build_dad_edge_specs`: only edit if
  the perimeter residual needs new angle bookkeeping that the current spec
  list does not already expose; otherwise leave untouched.
- `goldberg_brick/orbits.py`: add helper to identify the hexagon orbit(s)
  whose member hex faces share an edge with a pentagon face. Reuse existing
  graph adjacency from `dual.py` (pentagons are explicit faces; pentagon-
  adjacent hexes are those sharing exactly one edge with a pentagon). Expect
  one orbit class per icosahedral pentagon corner; orbit size = 60 / orbit
  stabilizer.
- `tests/test_equilateral_validation.py`: extend assertions to require
  GP(4,2) warp_mode == planar AND planarity_error < 1e-7 per hex orbit.

### Residual formula (single-pair form)

For each Class III cage, identify the two perimeter angle variables
`angle_a` and `angle_b` per pentagon corner (already computed inside
`compute_residuals` for DAD evaluation). Emit:

```
residual_C16 = angle_b - angle_a
```

One residual per orbit-distinct (a, b) pair after icosahedral symmetry
reduction. For T=28 (GP(4,2)) the count after reduction is expected to be 1
(matching SG's "reduce by one" statement); confirm against orbit count from
`orbits.py` before commit. If Fig. 4A shows the stronger "all perimeter
angles equal" form, emit (n - 1) residuals per pentagon where n = number
of distinct perimeter angles in the unconstrained model.

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

Tolerances:
- Stage A gate unchanged: `edge_stddev < 1e-7` (current code).
- Stage B planarity: `planarity_error < 1e-7` per hex orbit (current
  code's existing gate).
- Side spread acceptance: `max(edge_length) - min(edge_length) < 1e-6` on
  the final solved geometry (computed from report output's edge_length
  column).

Tests / runs:
- `tests/test_equilateral_validation.py` extended: assert GP(4,2)
  `warp_mode == "planar"` and `planarity_error < 1e-7` per hex orbit.
- All seven currently-tested (h,k) cases continue to converge Stage A.
- Reproduction command (must produce a non-rolled-back Stage B report):
  `source source_me.sh && python3 run_goldberg_brick.py -H 4 -K 2 -o /tmp/gp42_report.md`
  Inspect `warp_mode` column and `planarity_status` row.
- Mirror sanity: run GP(2,4) the same way; geometry and side spread must
  match GP(4,2) within numerical noise (mirror enantiomer); cache keys
  remain distinct `(4,2)` vs `(2,4)` at `equilateral.py:459`.

Reference-angle spot-check:
- Schein-Gayed Table 1 does not tabulate T=28. Cases tabulated for chiral
  Class III are T=7 (2,1), T=13 (3,1), T=37 (4,3). Add GP(2,1) to the
  validation set as a regression check: internal angles must match SG
  Table 1 values for T=7 (a=124.2, b=124.2, c=131.1, d=108.2, e=117.5,
  f=114.7 degrees) to 1 decimal place.
- If GP(2,1) matches but GP(4,2) still rolls back, the reduction is
  correct but applied to the wrong orbit -- escalate to Liu L4/L6
  symmetry-reduced parametrization.

Pre-implementation requirement:
- Open `articles/schein-gayed-2014*.pdf` Fig. 4A and confirm single-pair
  vs all-perimeter-equal form (see Context). Record decision in this plan
  before writing residuals.

## Risks

| Risk | Trigger | Mitigation |
|---|---|---|
| C16 alone insufficient | GP(4,2) still rolls back after b=a residuals added | Escalate to Liu L4/L6 symmetry-reduced parametrization in a new plan |
| Reduction applied to wrong orbit | Stage A converges but internal angles drift from Schein-Gayed Table 1 | Use SG Table 1 as regression check; identify perimeter orbit by graph adjacency to pentagon faces |
| Breaks Class II (h=k) | sole-degree b=a reduction over-constrains Class II | Guard C16 emission on `class == "III"` only |
| Numerical conditioning worsens | LM converges slower or fails Stage A | Tune dad_weight; verify Stage A gate edge_stddev < 1e-7 still passes |

## Fig. 4A inspection result

Source: `articles/schein-gayed-2014.txt` (extracted from
`articles/schein-gayed-2014.pdf`). Direct PDF render of Fig. 4A not available
in this environment; relied on the verbatim text near the figure caption and
the main-text discussion (lines 1891-1892, 1934-1938 of the .txt extraction).

Verbatim quotes:

- "perimeter angle (a for achiral icosahedral Goldberg polyhedra and a = b
  for chiral ones in Fig. 4A and Fig. S2) rises to approach 126 deg"
- "by setting equal all of the internal angles around the perimeter of the
  corner faces (5gons), that is, by setting b = a (Fig. 4A) (SI Text, Sec. 4.3)"

Decision: **single-pair form**. In SG's labeling there are only two distinct
perimeter-angle names around each pentagon (a and b, alternating); the
"all internal angles around the perimeter" phrasing is restated in the same
sentence as "b = a". Therefore the single-pair residual

	residual_C16 = angle_b - angle_a

per orbit-distinct (a, b) pair correctly captures the full C16 reduction. No
stronger n>2 perimeter equality needs to be emitted.

## Open decisions

- Owner: TBD (assign at user return).
- Whether to emit the b=a residual unconditionally for Class III or behind
  a flag. Recommendation: unconditional; the reduction is mandatory per
  Schein-Gayed for a polyhedral solution to exist.
