# Goldberg brick usage

## Overview

Goldberg Brick generates builder-facing Markdown reports for icosahedral
Goldberg polyhedra. The reports describe each hexagon orbit so that MOC,
LEGO, and kit-of-parts builders can plan panel reuse, connector counts,
and hinge placement before cutting any physical part.

## What is GP(h,k)?

An icosahedral Goldberg polyhedron GP(h,k) is parameterized by two
non-negative integers h and k that index the chiral lattice step between
adjacent pentagonal centers. The triangulation number is
`T = h*h + h*k + k*k`. Every GP(h,k) has exactly 12 pentagonal faces and
`10 * (T - 1)` hexagonal faces. The (h,k) pair also determines symmetry
class: class I when k = 0, class II when h = k, and class III otherwise
(chiral).

## Quick start

Default report path:

```bash
source source_me.sh && python3 run_goldberg_brick.py 2 2
```

Write to an explicit path:

```bash
source source_me.sh && python3 run_goldberg_brick.py 2 2 -o report.md
```

Apply real-world units with a scale factor (millimeters at scale 100):

```bash
source source_me.sh && python3 run_goldberg_brick.py 2 2 --units mm --scale 100
```

## Reading the report

The hexagon orbit table is the core of the builder report. One row per
orbit. Read each column as follows:

| Column | What it means for a builder |
| --- | --- |
| `orbit_id` | Stable identifier for a symmetry-equivalent group of hexagons; one panel design per orbit. |
| `face_count` | How many physical hexagon faces in this orbit appear in the full polyhedron. |
| `mirror_orbit` | Identifier of the mirror-image orbit, or `self` if the orbit is its own mirror; tells you when you need a left/right pair. |
| `angle_pattern` | Letter code summarizing the six interior angles in rotation-canonical order; equal letters mean equal angles. |
| `side_pattern` | Letter code summarizing the six side lengths; equal letters mean equal sides. |
| `dihedral_pattern` | Letter code summarizing the six edge dihedral angles to neighboring faces. |
| `side_length_sequence (units)` | The six side lengths in the canonical traversal order, in the chosen units. |
| `angle_sequence` | The six interior angles in degrees, in canonical order. |
| `dihedral_sequence` | The six dihedral angles to adjacent faces, in degrees. |
| `planarity_error (units)` | Maximum out-of-plane deviation of the six hexagon vertices; small means a flat panel is acceptable. |
| `warp_mode` | Qualitative shape of the hexagon: `planar`, `boat`, `chair`, or `asymmetric`. |
| `deformation_mode` | Builder-facing alias for `warp_mode`; included for downstream tooling that prefers the deformation vocabulary. |
| `brick_strategy` | Suggested construction approach: `repeatable-panel` for flat reusable panels, `hinge-required` for warped panels needing a flex joint, or `custom` for one-off geometry. |
| `difficulty` | Coarse build difficulty hint based on warp and pattern complexity. |
| `suggested_use` | Short cautious recommendation for how to use this orbit in a model. |

## Per-orbit connector counts

The report also emits a small per-orbit connector-count table. For each
orbit it lists the distinct angle values, side-length values, and
dihedral values that appear on a single face of the orbit, along with
the multiplicity per face and the total count across all faces in the
orbit. Builders use these counts to translate the orbit geometry into a
shopping list: number of distinct hinge angles to fabricate, number of
unique strut lengths, and total connector instances needed across the
finished polyhedron.

## Worked examples

The examples below were regenerated from the equilateral construction on 2026-05-27.

### GP(2,1)

**Summary:**

- h: 2, k: 1, T: 7, class: III (chiral)
- 12 pentagonal faces, 60 hexagonal faces (72 total)
- 1 hexagon orbit
- Equilateral construction, chord metric, unit scale

**Hexagon orbits:**

| orbit_id | face_count | angle_pattern | side_pattern | dihedral_pattern | warp_mode | brick_strategy | difficulty |
|---|---:|---|---|---|---|---|---|
| H001 | 60 | abcdee | aaaaaa | aabcbd | planar | custom | hard |

**Per-orbit connector counts for H001 (60 faces):**

*Angles (degrees):*

| value | per_face | total |
|---|---:|---:|
| 124.207 | 2 | 120 |
| 108.254 | 1 | 60 |
| 114.659 | 1 | 60 |
| 117.521 | 1 | 60 |
| 131.152 | 1 | 60 |

*Sides (unit):*

| value | per_face | total |
|---|---:|---:|
| 1.000 | 6 | 360 |

*Dihedrals (degrees):*

| value | per_face | total |
|---|---:|---:|
| 23.951 | 2 | 120 |
| 30.798 | 2 | 120 |
| 20.671 | 1 | 60 |
| 29.339 | 1 | 60 |

### GP(2,2)

**Summary:**

- h: 2, k: 2, T: 12, class: II (achiral)
- 12 pentagonal faces, 110 hexagonal faces (122 total)
- 3 hexagon orbits
- Equilateral construction, chord metric, unit scale

**Hexagon orbits:**

| orbit_id | face_count | angle_pattern | side_pattern | dihedral_pattern | warp_mode | brick_strategy | difficulty |
|---|---:|---|---|---|---|---|---|
| H001 | 30 | aabaab | aaaaaa | aabaab | planar | repeatable-panel | hard |
| H002 | 60 | aabaab | aaaaaa | aabccd | planar | repeatable-panel | hard |
| H003 | 20 | aaaaaa | aaaaaa | aaabbb | planar | repeatable-panel | hard |

**Per-orbit connector counts for H001 (30 faces):**

*Angles (degrees):*

| value | per_face | total |
|---|---:|---:|
| 110.905 | 4 | 120 |
| 138.190 | 2 | 60 |

*Sides (unit):*

| value | per_face | total |
|---|---:|---:|
| 1.000 | 6 | 180 |

*Dihedrals (degrees):*

| value | per_face | total |
|---|---:|---:|
| 22.239 | 4 | 120 |
| 20.905 | 2 | 60 |

## Construction model

Goldberg Brick uses the Schein-Gayed globally-equilateral construction.
The solver runs in two stages: Stage A drives every edge to unit length
(hard gate); Stage B refines toward planar faces (preferred, soft).
Cases where Stage B does not converge still ship a report -- the
hexagons are labelled `boat`, `chair`, or `asymmetric` by the warp
classifier instead of `planar`. See
[GP_EQUILATERAL_CONVERGENCE.md](GP_EQUILATERAL_CONVERGENCE.md) for
the architecture and recovery strategies.

## Supported (h,k) cases

| (h,k) | T | class | notes |
| --- | --- | --- | --- |
| (1,1) | 3 | II | planar equilateral |
| (2,0) | 4 | I | globally-equilateral; Stage B planarity incomplete (warp label per orbit) |
| (2,1) | 7 | III | planar equilateral |
| (2,2) | 12 | II | planar equilateral; Liu 2022 Table 2 values reproduced |
| (3,0) | 9 | I | planar equilateral |
| (3,1) | 13 | III | planar equilateral |
| (4,2) | 28 | III | globally-equilateral; Stage B planarity incomplete (warp label per orbit) |

## References

- [articles/schein-gayed-2014.pdf](../articles/schein-gayed-2014.pdf) -- Schein and Gayed (2014), planar globally-equilateral construction.
- [articles/liu-2022.pdf](../articles/liu-2022.pdf) -- Liu et al. (2022), Goldberg topology and cage construction.
