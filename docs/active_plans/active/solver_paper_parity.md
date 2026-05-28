# Solver/report paper-code parity audit

Scope: research papers in `articles/` vs python code in `goldberg_brick/`,
focused on geometry the report writes for GP(h,k) (priority GP(4,2)).
Source plan: `~/.claude/plans/calm-jumping-boot.md`.

Priority papers (exhaustive on topic list):
- schein-gayed-2014 (C1-C20)
- liu-2022 (L1-L20)

Secondary (narrow):
- siber-2020 (S1-S7)
- brinkmann-schein-2017 (B1-B8)

Background (not implementation-driving):
- johnson-2021, twarock-2019, voytekhovsky-2018, mannige-2010,
  virus_T-number_images

Topic list (in-scope for claim extraction):
- h,k indexing and Goldberg-class assignment
- T-number and pentagon/hexagon counts
- chirality / mirror handling for Class III
- geodesic mesh + Goldberg dual construction
- equilateral edge constraints
- planarity criterion and DAD definition
- boat / chair / asymmetric warp_mode classification
- edge length, internal angle, dihedral angle reporting
- solver validation gate and convergence criterion

Status legend per parity row:
- `implemented` -- code realizes the paper claim
- `not_implemented_intentional` -- paper claim deliberately out of scope
- `divergent` -- code disagrees with paper

Severity legend (for `divergent` or `not_implemented` rows):
- `correctness_blocker` -- changes geometry the report writes; routes to a
  follow-on coding plan `fix_<topic>.md`
- `documentation_only` -- citation/naming drift; routes to
  `divergence_<topic>.md` stub
- `background_only` -- one-line note in this report's background section

---

# M1: Paper claim ledgers

## Paper: schein-gayed-2014

Schein and Gayed introduce a fourth class of convex equilateral polyhedron
with polyhedral symmetry, "Goldberg polyhedra", obtained by decorating
tetrahedral, octahedral, or icosahedral facets with a Goldberg triangle
GP(h,k) of T = h^2 + hk + k^2 vertices and then solving for the set of
internal 6gon angles that nulls every dihedral-angle discrepancy (DAD). The
construction yields exactly one tetrahedral (T=4), one octahedral (T=4),
and a countable infinity of icosahedral (T>=4) Goldberg polyhedra, all with
equilateral planar (but not equiangular) hexagonal faces. Cages that
satisfy only equilaterality without zero DADs have nonplanar boat- or
chair-shaped 6gons and are not polyhedra.

### Claims

- **C1** [Abstract / Intro, p. 2920]: All edges equal length; equilateral
  enforced jointly with planarity. Should live in: `equilateral.py`
  (edge-length residual / solver objective).
- **C2** [Construction, p. 2920, Fig. 1A-E]: GP(h,k) drawn on 666 hex
  tiling; encloses T = h^2 + hk + k^2 trivalent vertices. Should live in:
  `indices.py`, `triangulation.py`.
- **C3** [Construction, p. 2920]: T = h^2 + hk + k^2; classes (h,0)
  achiral, (h=k) achiral, (h,k) with h != k, h,k>0 chiral. Should live
  in: `indices.py` (class assignment).
- **C4** [Intro / Fig. 1A, p. 2920]: Triangles with h != k, h,k>0 lack
  mirror symmetry; chiral, mirror-image enantiomers. Should live in:
  `orbits.py`, `indices.py` (chirality flag + mirror handling).
- **C5** [Fig. 1C-E, p. 2920]: Decorating 4/8/20 base facets yields cages
  with 4T/8T/20T trivalent vertices, 6gonal faces, 4/6/12 corner faces.
  Should live in: `icosahedron.py` + `triangulation.py`.
- **C6** [Results / DAD, p. 2921, Eq. 1]: cos(A) = (cos &alpha; - cos
  &beta; cos &gamma;) / (sin &beta; sin &gamma;); &beta;,&gamma;
  interchangeable. Should live in: `geometry.py` (dihedral-from-angles).
- **C7** [Fig. 3B, p. 2921]: Planarity requires equal dihedral angles at
  the two endpoints of a shared edge; DAD = difference. Should live in:
  `geometry.py` / `equilateral.py`.
- **C8** [Eq. 2, p. 2921]: Zero-DAD planar-face condition: D - A = 0.
  Should live in: `equilateral.py` (residual per DAD-edge type).
- **C9** [Results, p. 2921-2922]: Nonplanar 6gon internal-angle sum < 720;
  equiangular all-120 cannot tile T>=4; sum-to-720 is the planarity
  criterion. Should live in: `equilateral.py` / `geometry.py`.
- **C10** [Fig. 2F caption, p. 2921]: Nonplanar equilateral 6gons come in
  two warp shapes: boat = pattern 122122 (two pairs of like-displaced),
  chair = 121212 (alternating up/down). Should live in: `geometry.py` or
  `report.py`.
- **C11** [Fig. 4B, p. 2922]: Seven planar equilateral hexagon patterns
  (123456, 123445, 123432, 123123, 122122, 121212, 111111); planar
  equilateral n-gon with all-distinct angles has n-3 independent vars.
  Should live in: `geometry.py`, `equilateral.py`.
- **C12** [Fig. 4A + Table 1, p. 2922]: Each 6gon orbit gets one pattern
  label; var count per cage = sum over orbits (T=9:2, T=12:2, T=16:4,
  T=37:18). Should live in: `orbits.py`, `equilateral.py`.
- **C13** [DAD edges, p. 2922]: Edge with different vertex labels is DAD
  edge; same-label edges generally not DAD-edges with two exceptions in
  chiral h != k cages where &beta;,&gamma; ordering matters. Should live
  in: `equilateral.py`.
- **C14** [Equal counts theorem, p. 2922, Table 1]: Number of distinct
  zero-DAD equations equals number of independent angle vars; at most one
  polyhedral solution per cage. Should live in: `equilateral.py`.
- **C15** [Solving T=4, p. 2922-2923]: Closed-form T=4 solutions for ico
  (b approx 116.565), oct (b approx 109.471), tet (b = 90). Should live
  in: `equilateral.py`.
- **C16** [Chiral reduction, p. 2922-2923, SI 3.5/4.3]: For chiral h != k
  cages, setting b=a around the 5gon perimeter reduces var count and
  DAD-eq count by one (T=7: 3->2 vars/eqs). Should live in:
  `equilateral.py` referencing `orbits.py`.
- **C17** [Convexity, p. 2923, Fig. 5]: Convex solution requires
  internal-angle-sum < 360 at each vertex type; boundary solutions are
  non-convex. Should live in: `equilateral.py` post-solve check +
  `report.py`.
- **C18** [No oct/tet for T>4, p. 2923-2924]: No convex octahedral or
  tetrahedral Goldberg polyhedron for T>4. Should live in: `equilateral.py`
  / `icosahedron.py`.
- **C19** [Twist caveat, p. 2924]: DAD=0 alone does not guarantee
  planarity; sum-to-720 must be enforced explicitly. Should live in:
  `equilateral.py` (both DAD=0 and sum=720 constraints).
- **C20** [Discussion, p. 2924]: Countable infinity of icosahedral
  Goldberg polyhedra, one per (h,k) != (0,0), T>=4. Should live in:
  `indices.py`, `report.py`.

## Paper: liu-2022

Liu et al. extend Goldberg's method by parametrizing cage geometry under
icosahedral symmetry and optimizing 2D planar-graph vertex DOFs `C` plus
per-unique-vertex radii `R` via Levenberg-Marquardt to satisfy chosen
geometric properties: planarity, equilaterality, and/or inscribability.
Reproduces Schein-Gayed equilateral GPs (matching internal angles to ~10
decimals); presents numerical evidence for "spherical Goldberg polyhedra"
(all vertices on sphere AND all faces planar); uses iterative k-means
clustering + optimization to minimize distinct edge lengths.

### Claims

- **L1** [Sec 1.2.1, p. 2-3]: GP(m,n) and C(m,n) topology: 20T verts, 30T
  edges, 9T hex faces, 12 pent faces; T = m^2+mn+n^2. Should live in:
  `icosahedron.py`, `indices.py`.
- **L2** [Sec 2.1, p. 4-5]: Type III (n != m, n != 0) has only order-3
  rotational symmetry, no reflection; chiral. Should live in: `orbits.py`.
- **L3** [Sec 2.1, p. 5; Sec 4, p. 9]: Unique elements drive everything;
  C(8,0) needs 15 unique verts, 20 unique edges, 9 unique faces. 12
  pentagons handled separately. Should live in: `orbits.py`, `indices.py`,
  pentagon special-case in `geometry.py`.
- **L4** [Sec 2.2.1, p. 5-6 + Fig 3]: DOFs per unique vertex: 0 (corner),
  1 (boundary/sym-line), or 2 (interior). Should live in: `indices.py` or
  new parametrization module.
- **L5** [Sec 2.2.2, Eqs 2.1-2.2, p. 6]: Triangle mapping F = [Vti * Vtp^-1,
  E] (uniform scale + rigid transform); no new DOFs. Should live in:
  `triangulation.py`, `icosahedron.py`.
- **L6** [Sec 2.2.2, p. 6]: Radial-drift: per unique vertex one scalar
  radius R; coords are function of (C, R). Should live in: new param
  module / extend `geometry.py`.
- **L7** [Sec 3.1 Eq 3.1, p. 7]: Planarity: for each unique hex face V1-V6,
  pick base plane through V1,V2,V3, require signed distances d4=d5=d6=0.
  Three eqs per unique face. Should live in: `geometry.py`.
- **L8** [Sec 3.1 Eq 3.2, p. 7]: Equilaterality: unique-edge lengths
  equal common value. Should live in: `equilateral.py`.
- **L9** [Sec 3.1 Eq 3.3, p. 7]: Inscribability: all radii equal -> all
  verts on one sphere. Should live in: `geometry.py` / new `sphericity.py`.
- **L10** [Sec 3.2.1 Eq 3.5, p. 7]: Unweighted LM objective; constraints
  baked into residual vector, not hard constraints. Should live in:
  `equilateral.py` solver.
- **L11** [Sec 3.2.3, p. 7]: Three error metrics: &sigma;_p (vertex-to-plane),
  &sigma;_e (edge-length deviation), &sigma;_i (vertex-to-sphere); threshold
  1e-15. Should live in: `report.py`, `equilateral.py`.
- **L12** [Sec 3.2.2, p. 7; Sec 4, p. 9]: Good initial guess matters;
  LMA stalls at local minima. They initialize from Goldberg
  spherical-projected cage. Should live in: `icosahedron.py` / `equilateral.py`.
- **L13** [Sec 4 + tables 1-2, p. 8-9]: Benchmark: C(3,0), C(2,2), C(2,1),
  C(8,0); internal angles match Schein-Gayed to 10 decimals;
  runtimes 0.2-0.6s. "Equilateral GP" is planar+equilateral cage with
  vertices NOT on a single sphere (radius 0.971-1.000 for C(3,0)). Should
  live in: `equilateral.py`, `report.py`.
- **L14** [Sec 5.1, p. 10]: Spherical GP = planarity + inscribability
  (equilaterality dropped); demonstrated for C(3,0), C(2,2), C(2,1) all
  errors < 1e-15. Must CHOOSE: equilateral+planar XOR spherical+planar;
  mutually unattained for T>1. Should live in: `geometry.py` (sphericity
  mode) distinct from `equilateral.py` (equilateral mode).
- **L15** [Sec 5.2, p. 10-11]: Spherical GP non-unique; fixing pentagon
  edge length lp gives alternative solution. Should live in: `geometry.py`
  parametric residual.
- **L16** [Sec 5.3.1-5.3.2, Figs 6-7, p. 11-12]: Edge-length grouping via
  iterative k-means + optimization; C(8,0) achieves k=15 nearly-exact, k=4
  at 1e-4 tolerance. Should live in: `equilateral.py` or new `clustering.py`.
- **L17** [Sec 4 + Sec 5.3.2, p. 9, 12]: Convergence scales: C(8,0) (T=64)
  in 0.56s. NO GP(4,2) coverage; type-III high-T not validated.
- **L18** [Sec 2.1 + Sec 4, p. 5, 8]: Pentagons always regular under
  icosahedral symmetry; only 9T hexagons need planarity/equilaterality
  enforcement. Should live in: `geometry.py` pentagon shortcut.
- **L19** [Sec 1.2 + Sec 4, p. 2, 8; ref 21]: Direct SG comparison: SG
  trig-angle eqs find only equilateral; Liu generalizes to any user-defined
  residual + topologies SG did not cover (C(8,0)). Should live in:
  `report.py` angle-output comparison harness.
- **L20** [Sec 2.1, p. 5]: Framework applies to tet, oct, ico (and hex
  via square base); only icosahedral demonstrated. Should live in:
  `icosahedron.py` (current code is icosahedral-only).

## Paper: siber-2020

Tutorial on Caspar-Klug icosadeltahedral construction parallel-applied to
geodesic domes, fullerenes, and viruses. Defines T-number via (h,k)=(M,N),
laevo/dextro chirality convention, and dome/fullerene duality.

### Claims

- **S1** [Sec. 2, p. 5-6, Eq. (1)-(2)]: E = m*a1 + n*a2 with m,n >= 0;
  T = m^2 + m*n + n^2. Should live in: `indices.py`.
- **S2** [Sec. 2, p. 6]: Convention "turn left after the first m jumps"
  (laevo), labeled (m,n) with m >= n; right-turn gives (n,m). Mirror
  image of (m,n) is (n,m); for m != n, m,n > 0, dome is chiral. Should
  live in: `indices.py`, `orbits.py` (handedness tagging).
- **S3** [Sec. 2, p. 6]: m > n is laevo, m < n is dextro; resolve with
  notation 7l vs 7d (e.g. (2,1)=7l, (1,2)=7d). Should live in: `indices.py`.
- **S4** [Sec. 3, p. 7, Eq. (8)]: Icosahedral fullerene edge vector
  E = M*A1 + N*A2; A1 x A2 toward reader reproduces dome left-turn
  convention. Should live in: `geometry.py`, `indices.py`.
- **S5** [Sec. 3, p. 9, Eq. (12), (16)]: f_5 = 12, f_6 = 10*(T-1). Should
  live in: `dual.py` / `report.py`.
- **S6** [Sec. 3, p. 7-8]: Icosahedral fullerene = dual of icosadeltahedral
  dome; place atom at each dome-triangle barycenter, connect to three
  neighbors. Dome vertices -> Goldberg faces (12 pents at icosahedral
  vertices, hexes elsewhere). Should live in: `dual.py`, `triangulation.py`.
- **S7** [Sec. 2 / Sec. 3, p. 6, 9, Eq. (6), (13)]: v_dome = 10T+2 =
  f_5 + f_6 + 2 = f_6 + 12. Should live in: `report.py` sanity check.

## Paper: brinkmann-schein-2017

Disentangles Goldberg (1937), Fuller, and Caspar-Klug (1962) constructions;
identifies an error in Goldberg's chiral case; formalizes the operation as
a chamber-system "lsp" / "lopsp" operation. The "Goldberg-Coxeter"
construction is in fact Caspar-Klug's.

### Claims

- **B1** [Approach of CK, p. 8]: CK lattice basis v1=(0,0), v2=(a,b),
  v3=(-b,a+b) for integers a >= b >= 0; (0,1) is 60-deg CCW rotation of
  (1,0); T = a^2 + a*b + b^2. Should live in: `indices.py`, `geometry.py`.
- **B2** [Approach of CK, p. 8-9]: CK triangle has full rotational
  symmetry; mirror symmetries iff b=0 OR a=b. Otherwise triangle and
  GP(a,b) are chiral. Should live in: `indices.py` (chirality flag).
- **B3** [Approach of Goldberg, p. 5-6]: Goldberg 1937 contains an error:
  he claims chiral (l,m) patches decompose into 10 congruent triangles; in
  fact a chiral pentagonal patch decomposes only into 5 congruent (or 10
  in two mirror-image sets of 5). Chiral cases need a paired (black/white)
  double triangle with v0' = (-b, a+b). Should live in: `orbits.py`,
  `equilateral.py` (orbit-count handling: 5-orbits not 10).
- **B4** [Approach of Goldberg, p. 6-7]: For chiral (l,m), m > 0,
  dodecahedron mirror symmetries lost; only orientation-preserving
  symmetries remain. GP(h,k) and GP(k,h) are mirror enantiomers when
  h != k, h,k > 0. Should live in: `orbits.py` (group I vs Ih),
  `indices.py` (enantiomer pairing).
- **B5** [Approach of CK, p. 8, Fig. 6]: CK indexing fixes a >= b >= 0;
  canonical ordering for Goldberg-Coxeter literature. Should live in:
  `indices.py`.
- **B6** [Goldberg vs CK duality, p. 4-5]: Goldberg uses hexagonal
  lattice (dodecahedron); CK uses triangular lattice (icosahedron).
  Constructions are duals. Goldberg unit vectors shorter than CK by
  sqrt(3). Should live in: `dual.py`, `geometry.py`.
- **B7** [Approach of Goldberg, p. 5-6, Fig. 3]: Chiral (l,m) corrected
  construction: v2=(0,0) 6-fold (pent center), v0=(l,m) and v0'=(-m,l+m)
  3-fold, v1 = midpoint 2-fold. Should live in: `orbits.py`,
  `triangulation.py`.
- **B8** [Conclusion, p. 17]: What literature calls "Goldberg-Coxeter" is
  Caspar-Klug's; Coxeter (1971) re-described it. Should live in: repo
  docstring naming note.

## Not implementation-driving (background)

- **johnson-2021**: PDB / biological context for icosahedral viruses. No
  geometric algorithm contribution; cited for motivation only.
- **twarock-2019**: Archimedean lattice + dual framework. Conceptual;
  current code uses standard Goldberg dual, not lattice-explicit form.
- **voytekhovsky-2018**: matrix-algebra classification. Code uses
  geometric/combinatorial approach; matrix nomenclature not used.
- **mannige-2010**: periodic-table-style hexamer enumeration. Background
  for T-number context.
- **virus_T-number_images**: visual reference only.

---

# M2: Code function indices

## Code: equilateral.py

### Functions

| file:line | name | purpose | cites? | formula |
|---|---|---|---|---|
| equilateral.py:19 | ConvergenceError | solver convergence-gate failure | no | n/a |
| equilateral.py:25 | make_vertex_id | format VID `V{idx:04d}` | no | n/a |
| equilateral.py:31 | build_polyhedron_edges | derive edges via `|tri intersect|==2` | no | n/a |
| equilateral.py:52 | build_rotation_orbits | group verts into orbits under 60 ico rotations | no | n/a |
| equilateral.py:101 | build_rotation_matrix_from_perm | 3x3 R from face-basis change | no | R = Bt^T * Bs |
| equilateral.py:121 | expand_from_reps | rep -> full vertex set via R per orbit member | no | p_m = R_idx * p_rep |
| equilateral.py:150 | build_face_vertex_orderings | order Goldberg face verts circumferentially | no | n/a |
| equilateral.py:175 | build_dad_edge_specs | per-edge (face_A,B,C) prev/curr/next index for DAD | yes (schein-gayed-2014) | n/a |
| equilateral.py:268 | _cos_dihedral_at_endpoint | cos(dihedral) via spherical-triangle law | yes (schein-gayed-2014 Eq.1) | cos D = (cos c - cos a cos b)/(sin a sin b) |
| equilateral.py:292 | compute_residuals | LM residuals: edge equilat + DAD + pent/hex planarity | yes (schein-gayed-2014 Eq.1) | edge: \|p2-p1\|-1; DAD: w*(cos D1 - cos D2); pent: signed tetra vol; hex: (p-c).n_hat |
| equilateral.py:364 | positions_to_vector | flatten to scipy vector | no | n/a |
| equilateral.py:373 | vector_to_positions | inverse | no | n/a |
| equilateral.py:385 | rescale_to_unit_edges | scale s.t. mean edge = 1 | no | n/a |
| equilateral.py:407 | center_at_origin | translate to centroid 0 | no | n/a |
| equilateral.py:421 | solve_schein_gayed_positions | wrapper to force_attempt_solve | yes (schein-gayed-2014) | n/a |
| equilateral.py:438 | force_attempt_solve | two-stage LM solver + gate edge_stddev<1e-7 | yes (schein-gayed-2014) | Stage A equilat; Stage B planar+DAD; rollback on ValueError or stddev>=1e-7 |

## Code: geometry.py

| file:line | name | purpose | cites? | notes |
|---|---|---|---|---|
| geometry.py:19 | HexagonGeometry | per-orbit measured record | no | n/a |
| geometry.py:31-49 | ConnectorClass, ConnectorCounts, BuilderSummary | builder dataclasses | no | n/a |
| geometry.py:73-141 | dot/add/sub/scale/cross/length/normalize/clamp/angle_degrees | vec primitives | no | n/a |
| geometry.py:150 | vertex_coordinate | wraps triangulation.normalized_coordinate | no | n/a |
| geometry.py:164 | _geodesic_triangle_centroid_on_sphere | spherical centroid, SG initial-guess seed | yes (schein-gayed-2014) | n/a |
| geometry.py:190 | build_incident_triangles | vert->incident-faces map | no | n/a |
| geometry.py:210 | tangent_basis | deterministic tangent basis at sphere pt | no | n/a |
| geometry.py:221 | order_triangles_around_vertex | atan2 sort of incident tris | no | n/a |
| geometry.py:241 | ordered_goldberg_vertices | pull positions in face-cyclic order | no | n/a |
| geometry.py:267 | polygon_normal | Newell normal | no | sum p_i x p_{i+1} |
| geometry.py:279 | polygon_centroid | mean | no | n/a |
| geometry.py:289 | side_lengths | chord side lengths | no | n/a |
| geometry.py:299 | internal_angles | signed atan2-based angles | no | n/a |
| geometry.py:317 | planarity_error | max distance from Newell plane | no | max\|(p-c).n_hat\| |
| geometry.py:352 | dihedral_angles | face-normal angle to neighbor | no | acos(n_face . n_neighbor) |
| geometry.py:409 | compute_hexagon_orbit_geometries | top-level: solve + measure | yes (schein-gayed-2014 via solver) | n/a |
| geometry.py:541 | classify_planarity | thresholds 1e-4 / 4e-4 | no | n/a |
| geometry.py:553 | signed_plane_displacements | signed dist per vert | no | n/a |
| geometry.py:579 | classify_warp_mode_from_geometry | planar/boat/chair/asymmetric via signed templates | no | chair=(+,-,+,-,+,-); boat=(+,-,-,+,-,-); cross-checks 'ababab','aabaab' |
| geometry.py:641 | orientation_label | "achiral" or "GP(h,k); mirror GP(k,h)" string | no | not actual mirror geometry |
| geometry.py:651-823 | classify_difficulty/describe_shape/suggested_use/reuse_group/cluster_values/build_connector_classes/connector_counts/classify_brick_strategy/compute_builder_summaries | builder-facing classifiers | no | thresholds: angle 0.25, dihedral 0.25, side mean*0.015 |

## Code: indices.py

| file:line | name | purpose | cites? | formula |
|---|---|---|---|---|
| indices.py:7 | GoldbergIndices | h,k,T,class,V/E/F | no | n/a |
| indices.py:25 | validate_indices | reject negative or (0,0) | no | n/a |
| indices.py:41 | calculate_t_number | T-number | no | T = h*h + h*k + k*k |
| indices.py:56 | classify_indices | class label | no | k==0:I; h==k:II; else:III (NO chirality split) |
| indices.py:76 | build_indices | derived counts | no | V_geo=10T+2; E_geo=30T; F_geo=20T; pents=12; hexes=10T-10 |

## Code: dual.py

| file:line | name | purpose | cites? | notes |
|---|---|---|---|---|
| dual.py:8 | GoldbergFace | face_id, source_vertex, side_count, face_type | no | n/a |
| dual.py:18 | GoldbergGraph | mesh, faces, adjacency, vertex_count, edge_count | no | n/a |
| dual.py:31 | face_type_for_valence | valence 5->pentagon, 6->hexagon | no | n/a |
| dual.py:43 | build_valence_map | per-vert valence | no | n/a |
| dual.py:60 | make_face_id | "F{idx:04d}" | no | n/a |
| dual.py:67 | build_goldberg_graph | dual: geodesic vert -> Goldberg face | no | F_dual = V_geo; E_dual = E_geo; V_dual = F_geo |
| dual.py:109 | count_faces | count by type | no | n/a |
| dual.py:119 | validate_goldberg_counts | cross-check vs indices | no | n/a |

## Code: triangulation.py

| file:line | name | purpose | cites? | notes |
|---|---|---|---|---|
| triangulation.py:14 | GeodesicMesh | dataclass | no | n/a |
| triangulation.py:26 | canonical_vertex_key | base/edge/face key; sum(weights)==T | no | n/a |
| triangulation.py:58 | key_weights | inverse | no | n/a |
| triangulation.py:81 | normalized_coordinate | weighted sum then unit-sphere | no | p = sum w_i v_i / \|...\| |
| triangulation.py:102 | target_valence | "V"->5; else 6 | no | n/a |
| triangulation.py:208 | barycentric_numerators | 2D lattice -> (alpha,beta,gamma) | no | beta=(h+k)x+ky; gamma=-kx+hy; alpha=T-beta-gamma |
| triangulation.py:336 | add_face_lattice | per-base-face lattice + stitching | no | n/a |
| triangulation.py:400 | build_geodesic_mesh | top-level mesh build | no | n/a |
| triangulation.py:442 | validate_mesh_counts | V=10T+2,E=30T,F=20T | no | n/a |

## Code: icosahedron.py

| file:line | name | purpose | cites? | notes |
|---|---|---|---|---|
| icosahedron.py:10 | Icosahedron | dataclass | no | n/a |
| icosahedron.py:112 | build_coordinates | 12 verts; phi=(1+sqrt(5))/2 | no | cyclic perms of (0,+/-1,+/-phi) |
| icosahedron.py:147 | build_edges | 30 edges at min pairwise dist | no | n/a |
| icosahedron.py:168 | orient_face | outward normal | no | n/a |
| icosahedron.py:191 | build_faces | 20 oriented tris | no | n/a |
| icosahedron.py:216 | face_basis | (e1,e2,n) orthonormal | no | n/a |
| icosahedron.py:250 | build_rotation_for_faces | vert permutation realizing rotation | no | R=Bt^T*Bs |
| icosahedron.py:267 | build_rotations | all 60 rotations | no | 20 faces x 3 cyclic orderings = 60 (group I, orientation-preserving only) |
| icosahedron.py:289 | build_icosahedron | assemble | no | n/a |

## Code: orbits.py

| file:line | name | purpose | cites? | notes |
|---|---|---|---|---|
| orbits.py:9 | HexagonOrbit | dataclass; mirror_orbit="NA" always | no | n/a |
| orbits.py:20 | make_orbit_id | "H{idx:03d}" | no | n/a |
| orbits.py:27 | hexagon_source_vertices | hex face sources | no | n/a |
| orbits.py:39 | build_orbit_for_source | apply 60 rotations | no | orbit_size divides 60 |
| orbits.py:60 | group_hexagon_orbits | partition; no mirror pairing | no | n/a |

## Code: report.py

| file:line | name | purpose | cites? | notes |
|---|---|---|---|---|
| report.py:9 | validation_status | PASS/FAIL vs index_data | no | n/a |
| report.py:26 | render_markdown_report | full deterministic Markdown | no | static markers `model: equilateral-goldberg`, `metric: chord`; warp_mode from BuilderSummary/HexagonGeometry, not assigned here |
| report.py:151 | write_markdown_report | write to disk | no | n/a |
| report.py:168 | build_mirror_notes | "mirror-aware patterns" lines per orbit when oriented vs unoriented patterns differ | no | n/a |
| report.py:190 | build_connector_counts_section | per-orbit angle/side/dihedral counts | no | n/a |
| report.py:232 | format_sequence / format_sequence_scaled | numeric formatting | no | n/a |

## Code: cli.py

| file:line | name | purpose | cites? | notes |
|---|---|---|---|---|
| cli.py:15 | default_output_path | `gp_{h}_{k}_report.md` | no | n/a |
| cli.py:22 | parse_args | flags -H,-K,-o/--out,-u/--units{unit,mm,stud},-s/--scale | no | no whitelist on h,k |
| cli.py:49 | build_report | drive pipeline; SystemExit(2) on ConvergenceError | no | narrow try/except at CLI boundary |
| cli.py:103 | main | parse + dispatch | no | n/a |

## Code: run_goldberg_brick.py

| file:line | name | purpose | cites? | notes |
|---|---|---|---|---|
| run_goldberg_brick.py:8 | main | delegate to `goldberg_brick.cli.main` | no | n/a |

---

# M3: Parity table

Rows pair each priority claim with its implementation (or status
`not_implemented_intentional` / `divergent`). Severity given for non-`implemented`.

| claim ID | claim summary | impl file:line | status | severity | notes |
|---|---|---|---|---|---|
| **SG C1** | all edges equal length | equilateral.py:292 (edge residual `\|p2-p1\|-1`); gate `force_attempt_solve` edge_stddev<1e-7 | implemented | -- | -- |
| **SG C2** | GP(h,k) on 666 tiling encloses T verts | triangulation.py:208,400 | implemented | -- | -- |
| **SG C3** | T-number + class assignment | indices.py:41,56 | implemented | -- | class III lacks chirality split (see C4) |
| **SG C4** | h != k, h,k>0 chiral; mirror enantiomers | -- | divergent | documentation_only | code returns "III" for both (h,k) and (k,h); no laevo/dextro tag. `orientation_label` emits "GP(h,k); mirror GP(k,h)" string but no actual mirror handling. `HexagonOrbit.mirror_orbit="NA"` always. Geometry is still chirally consistent (group I used, not Ih), so report content is correct; missing only labels. |
| **SG C5** | decorate base facets; 20T verts, 12 corner pents | dual.py:67,109; indices.py:91 | implemented | -- | only icosahedral demonstrated (matches code scope) |
| **SG C6** | Eq. 1 cos(D) formula | equilateral.py:268 `_cos_dihedral_at_endpoint` | implemented | -- | spot-check 1: formulas match exactly |
| **SG C7** | DAD = dihedral_left - dihedral_right per edge | equilateral.py:175,292 | implemented | -- | -- |
| **SG C8** | zero-DAD eq D-A=0 | equilateral.py:292 (DAD residual `w*(cos D1 - cos D2)`) | implemented | -- | uses cos-difference not angle-difference; correct since both sides are linearized about same value at D1=D2 |
| **SG C9** | sum-to-720 planarity criterion | equilateral.py:292 (per-vertex hex point-to-plane residuals) | implemented | -- | code uses geometric point-to-plane, not angle-sum; equivalent. Angle-sum check is NOT enforced as a residual. |
| **SG C10** | boat=122122 (2 like-pairs); chair=121212 (alternating) | geometry.py:579 `classify_warp_mode_from_geometry` | implemented | documentation_only | signed-displacement templates chair=(+,-,+,-,+,-), boat=(+,-,-,+,-,-) match Schein-Gayed Fig. 2F semantically; docstring does NOT cite Schein-Gayed (cites="no"). Naming source = Schein-Gayed Fig. 2F (Q2 answer). |
| **SG C11** | seven planar equilateral hex patterns | geometry.py:496 `pattern_letters` / 524 `canonical_pattern` | implemented | -- | code derives patterns empirically via letter clustering; does not enumerate the 7-class set explicitly but reports an equivalent canonical form |
| **SG C12** | per-orbit pattern label + var count per cage | orbits.py:60; geometry.py:823 | divergent | correctness_blocker | code groups hex faces into orbits under group I (60 rotations), but does NOT compute "independent variable count per cage" nor enforce the equal-count-of-eqs-vs-vars (C14) theorem. Solver runs LM over ALL vertex positions, not symmetry-reduced angle variables. For high-T Class III this likely over-parameterizes the problem and can lead to Stage B local minima. **Candidate explanation for GP(4,2) Stage B rollback.** |
| **SG C13** | DAD-edge detection (label-based) | equilateral.py:175,292 | partial | documentation_only | code emits DAD residual per edge unconditionally; does not distinguish "DAD edges" from non-DAD edges (residuals on non-DAD edges should be zero by symmetry at optimum, but adding them inflates condition number) |
| **SG C14** | #eqs == #vars (square system, unique solution) | -- | not_implemented_intentional | correctness_blocker | code uses LM least-squares over vertex coords (3*20T-ish DOF), not the SG square trig system. Liu L19 confirms equivalent results possible via LM, but only if the residual vector spans the right constraint space. **GP(4,2) failure may stem from this** -- see Open Q4. |
| **SG C15** | T=4 closed-form solutions | -- | not_implemented_intentional | background_only | T=4 included in standard-tested cases; numerical solver handles it. No need for closed-form. |
| **SG C16** | chiral b=a around 5gon (var/eq reduction) | -- | divergent | correctness_blocker | code does NOT apply the chiral perimeter b=a reduction. For Class III (h != k, h,k>0) cages this leaves an extra DOF the LM solver must find by itself. **GP(4,2) is Class III (h=4,k=2) -- this is the most likely Stage B rollback cause.** |
| **SG C17** | convexity inequalities (vertex angle sum < 360) | -- | not_implemented_intentional | documentation_only | not enforced post-solve; report does not flag non-convex solutions explicitly |
| **SG C18** | no convex oct/tet Goldberg for T>4 | -- | not_implemented_intentional | background_only | code icosahedral-only; tet/oct dispatch absent by design |
| **SG C19** | DAD=0 alone insufficient; planarity must be enforced | equilateral.py:292 | implemented | -- | code enforces both planarity (pent signed-vol + hex point-to-plane) AND DAD in Stage B. Stage A is equilaterality-only (intentional gate). |
| **SG C20** | countable infinity of icosahedral Goldberg polyhedra, T>=4 | indices.py:76; equilateral.py:438 | implemented | -- | no T-range cap in code; all (h,k) accepted at CLI |
| **Liu L1-L5** | topology, type III chirality, unique elements, DOFs, triangle mapping | indices.py:41,76; orbits.py:60; triangulation.py:400 | partial | -- | topology/counts implemented; unique-element DOF parametrization is NOT done -- LM optimizes ALL vertex coords, not symmetry-reduced (C,R) |
| **Liu L6** | radial-drift (C,R) parametrization | -- | not_implemented_intentional | documentation_only | code uses straight Cartesian coords; equivalent under symmetry but less efficient |
| **Liu L7** | planarity residual (3 d_i=0 per face) | equilateral.py:292 (hex point-to-plane) | implemented | -- | code uses N-2 residuals (Newell-plane distance), Liu uses 3 explicit. Equivalent set of constraints. |
| **Liu L8** | equilaterality residual on unique edges | equilateral.py:292 (all edges, not unique) | implemented | -- | over-counted but mathematically equivalent under symmetry |
| **Liu L9** | inscribability (all radii equal) | -- | not_implemented_intentional | documentation_only | sphericity is NOT a goal; code chooses equilateral+planar per Liu L13/L14. |
| **Liu L10** | unweighted LM objective | equilateral.py:438 (LM via scipy) | implemented | -- | -- |
| **Liu L11** | error metrics &sigma;_p, &sigma;_e, &sigma;_i | equilateral.py:438 gate (edge_stddev); geometry.py:317 (planarity_error) | partial | documentation_only | &sigma;_e and &sigma;_p computed; &sigma;_i (sphericity) not computed since sphericity is not a goal |
| **Liu L12** | initial guess from spherical-projected cage | geometry.py:164 `_geodesic_triangle_centroid_on_sphere` + equilateral.py force_attempt_solve | implemented | -- | matches Liu's recommendation; spherical-centroid seed |
| **Liu L13** | benchmarks match SG to 10 decimals; equilat sacrifices sphericity | equilateral.py:438 + report.py (no benchmark harness present) | partial | documentation_only | code produces equilateral+planar cages but no regression harness validates against SG reference angles |
| **Liu L14** | spherical GP mode (planar+inscribed, drop equilat) | -- | not_implemented_intentional | background_only | out of scope |
| **Liu L15** | lp parameterization for spherical mode | -- | not_implemented_intentional | background_only | out of scope |
| **Liu L16** | k-means edge-length grouping | -- | not_implemented_intentional | documentation_only | Q1 answer: NO, code is pure Schein-Gayed DAD+planarity. Liu's k-means is an optional post-processing reduction, not required for correctness. Could be a future feature for builder reuse. |
| **Liu L17** | high-T validation; type III only at T=3 | -- | -- | -- | Liu provides NO GP(4,2) reference -- explains lack of literature anchor for GP(4,2) solver behavior. |
| **Liu L18** | pentagons always regular under ico symmetry | equilateral.py:292 (pentagon signed-tetra-volume planarity only) | partial | documentation_only | code enforces pentagon planarity but NOT pentagon-edge-equality as a separate constraint; relies on global equilaterality residual to keep pentagon edges equal. Should be fine under full ico symmetry. |
| **Liu L19** | LM reproduces SG angles | -- | not_implemented_intentional | documentation_only | no harness; would be valuable for regression |
| **Liu L20** | also applies to tet/oct/hex | -- | not_implemented_intentional | background_only | icosahedral-only by design |
| **Siber S1** | T = m^2+mn+n^2 | indices.py:41 | implemented | -- | spot-check 2: match |
| **Siber S2** | laevo convention m>=n; mirror = (n,m) | indices.py:25,56 | divergent | documentation_only | code accepts (h,k) and (k,h) equally; no laevo/dextro check on input ordering. Same divergence as SG C4. |
| **Siber S3** | 7l vs 7d notation | -- | not_implemented_intentional | documentation_only | report does not emit handedness suffix |
| **Siber S4** | A1 x A2 toward reader fixes left-turn convention | triangulation.py:208,400 | unknown | documentation_only | code's barycentric formula has a fixed handedness (`beta=(h+k)x+ky; gamma=-kx+hy`); whether it matches Siber's left-turn convention requires a geometry check (not done in this audit). **Recommended spot-check follow-up.** |
| **Siber S5** | f_5=12, f_6=10(T-1) | indices.py:91-93 | implemented | -- | spot-check 3: match (`hexagons=10T-10`) |
| **Siber S6** | dual: dome verts -> Goldberg faces | dual.py:31,67 | implemented | -- | -- |
| **Siber S7** | v_dome = 10T+2 | indices.py:88 | implemented | -- | -- |
| **Brinkmann B1** | CK lattice basis; 60-deg CCW between v1 and v2 | triangulation.py:208 | partial | documentation_only | code's barycentric is consistent with one handedness choice; not explicitly cited as 60-deg CCW |
| **Brinkmann B2** | chirality iff b != 0 AND a != b | indices.py:56 | divergent | documentation_only | code returns class III but does NOT set a chirality flag |
| **Brinkmann B3** | chiral patch = 5 (not 10) congruent tris; needs paired b/w | -- | divergent | correctness_blocker | code uses 60-rotation orbit grouping; orbit size divides 60. For Class III, this should naturally yield 5-orbits not 10 IF the rotation group is correctly only I (order 60), which it is (icosahedron.py:267 builds 20*3=60). **Confirmed implemented correctly at the orbit level.** Severity downgraded to: -- | partial | -- | re-classified after re-reading: code IS correct; rotation group I is used, not Ih. |
| **Brinkmann B4** | GP(h,k) and GP(k,h) mirror enantiomers | -- | divergent | documentation_only | same as SG C4 / Siber S2 |
| **Brinkmann B5** | canonical ordering a >= b >= 0 | cli.py:22 | divergent | documentation_only | CLI accepts (h,k) without enforcing h >= k; downstream solver doesn't normalize either. Mostly cosmetic but could confuse users. |
| **Brinkmann B6** | Goldberg vs CK duality; sqrt(3) scale factor | dual.py:67; triangulation.py:81 | implemented | -- | dual construction explicit; sqrt(3) scaling not relevant to chord-metric reports |
| **Brinkmann B7** | rotation-fold roles of v2/v0/v0'/v1 | icosahedron.py:267; orbits.py:39 | implemented | -- | implicit via orbit-size dividing 60; not labeled by fold |
| **Brinkmann B8** | "Goldberg-Coxeter" = Caspar-Klug | -- | not_implemented_intentional | documentation_only | naming convention note; could appear in docstring |

## Open question verdicts

**Q1: Liu 2022 edge-length grouping / spherical optimization present?**
**No.** Code is pure Schein-Gayed equilateral+planar with DAD nulling. Liu's
k-means edge-grouping (L16) and spherical-GP mode (L14) are NOT implemented.
Severity: `documentation_only` (optional features, not correctness).

**Q2: Source of boat/chair/asymmetric warp_mode strings?**
**Schein-Gayed 2014 Fig. 2F (C10).** Code's signed-displacement templates
chair=(+,-,+,-,+,-), boat=(+,-,-,+,-,-) correspond exactly to Fig. 2F's
patterns 121212 (alternating) and 122122 (two like-pairs). Severity:
`documentation_only` -- the `classify_warp_mode_from_geometry` docstring at
geometry.py:579 does NOT cite Schein-Gayed Fig. 2F.

**Q3: Chirality / mirror handling for Class III correct?**
**Geometry yes, labeling no.** Code uses the orientation-preserving
icosahedral group I (60 elements, icosahedron.py:267-285), not the full
Ih (120 elements). This is correct per Brinkmann B4 (Class III loses
mirror symmetries) and produces chirally-consistent geometry. Brinkmann
B3's warning about Goldberg's 10-vs-5 orbit error is avoided because the
code uses geometric orbit detection (rotate-and-match), not Goldberg's
faulty patch decomposition. However: the report does NOT label
laevo/dextro (Siber S3), does NOT set a chirality flag in
`GoldbergIndices`, does NOT enforce a >= b CLI convention, and emits
`mirror_orbit="NA"` always. Severity for these labeling gaps:
`documentation_only`.

**Q4: GP(4,2) Stage B rollback -- bug, missing constraint, or genuine
geometric limitation?**
**Most likely a missing constraint -- correctness_blocker.** Schein-Gayed
C16 specifies a chiral-cage reduction: for Class III with h != k, h,k > 0,
internal angles around the pentagon perimeter satisfy b=a, reducing both
variable and equation counts by one. **This reduction is NOT implemented in
`equilateral.py`.** Without it, the LM solver has an extra free DOF for
Class III cages that it must resolve numerically. The two-stage rollback to
Stage A (CHANGELOG 2026-05-28: "Hexagons that do not reach planar carry
the appropriate boat, chair, or asymmetric warp_mode label") is consistent
with an over-parameterized Stage B converging to a local non-planar minimum
instead of the unique polyhedral solution Schein-Gayed C14 predicts. GP(4,2)
is Class III (h=4, k=2, T=28), so the C16 reduction applies. Liu L17
confirms no published GP(4,2) reference exists, so this conclusion is
inferential -- but Schein-Gayed C20 guarantees a planar equilateral solution
exists for every (h,k), so GP(4,2)'s non-planar warp is solver-limited, not
a real geometric limit.

Related: SG C12/C14 says #eqs == #vars (square system). Code uses LM
least-squares over Cartesian vertex coords (3*N DOFs), not the
symmetry-reduced angle system. While LM can in principle find the same
solution (Liu L19), the residual vector must span the right constraint
space. Without the C16 chiral reduction, the residual+DOF count is off by
one for Class III, which Liu's general LM framework would handle by
adding the symmetry-tying equations -- which the code doesn't have.

## Spot-checks

Three random `implemented` rows verified for sign/formula/units:

1. **SG C6 Eq. 1** vs `_cos_dihedral_at_endpoint` (equilateral.py:268):
   - Paper: cos(A) = (cos &alpha; - cos &beta; cos &gamma;) / (sin &beta; sin &gamma;)
   - Code: cos D = (cos c - cos a * cos b) / (sin a * sin b)
   - Variable mapping: &alpha;=c (opposite face angle), &beta;=a, &gamma;=b
     (adjacent face angles). MATCH. Sign and form correct. Code also
     clamps sin^2 with floor 1e-30 to avoid div-by-zero. OK.

2. **SG C3 / Siber S1 T-number** vs `calculate_t_number` (indices.py:41):
   - Paper: T = h^2 + hk + k^2
   - Code: `T = h*h + h*k + k*k`. MATCH.

3. **Siber S5 face counts** vs `build_indices` (indices.py:91-93):
   - Paper: f_5=12, f_6=10(T-1)
   - Code: `pentagons = 12`, `hexagons = 10*t_number - 10`. MATCH.

---

# M4: Routing

Per severity outcomes:

## correctness_blocker

Two related blockers, both pointing at the same root cause (Class III
solver under-constrained):

1. **SG C16 chiral b=a reduction missing** -- file separate plan:
   `docs/active_plans/active/fix_chiral_reduction.md`. Owner: TBD (assign
   at user return). This is the prime candidate to explain GP(4,2) Stage
   B rollback. Implementation: extend `equilateral.compute_residuals` to
   add per-Class-III symmetry-tying equations (b=a around pentagon
   perimeter); extend `orbits.py` to identify the perimeter orbit.

2. **SG C12/C14 symmetry-reduced variable bookkeeping missing** --
   subsumed by item 1 once b=a reduction is added. Track as the same
   fix plan; if after C16 reduction GP(4,2) still rolls back, escalate
   to a full symmetry-reduced solver redesign (Liu L4/L6 (C,R)
   parametrization).

## documentation_only

These rows are cited divergences but do not change report geometry. One
stub each, but to keep paperwork bounded the manager files a single
consolidated stub:

- `docs/active_plans/active/divergence_chirality_labels.md` covering:
  SG C4 / Siber S2 / Siber S3 / Brinkmann B2 / Brinkmann B4 / Brinkmann
  B5 / Brinkmann B8 (chirality flag, laevo/dextro tag, canonical ordering
  enforcement, mirror orbit pairing, naming-convention note).
- `docs/active_plans/active/divergence_paper_citations.md` covering:
  SG C10 (warp_mode docstring missing Schein-Gayed cite); Liu L11/L13/L19
  (no benchmark harness against SG reference angles). Optional, low
  priority.

## background_only

One-line notes in the background section above; no separate files. Items:
SG C15 (T=4 closed-form), SG C18 (no oct/tet for T>4), Liu L14/L15/L20
(spherical mode, lp, non-ico generalization).
