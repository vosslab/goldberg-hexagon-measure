"""Validation tests for the Schein-Gayed equilateral Goldberg solver.

Covers Stage A (globally-equilateral) convergence for the seven baseline
(h,k) cases and Stage B (planarity + DAD) for chiral Class III cases that
exercise the C16 perimeter reduction.
"""

import math

import goldberg_brick.dual
import goldberg_brick.equilateral
import goldberg_brick.geometry
import goldberg_brick.orbits
import goldberg_brick.triangulation


# Seven baseline (h,k) cases also used in tests/test_dual.py for count
# validation. Stage A must converge (no ConvergenceError) for each.
BASELINE_CASES = [(1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1), (4, 2)]


#============================================
def _solve_and_measure(h: int, k: int):
	"""Solve GP(h,k) and return (graph, hexagon_orbits, geometries)."""
	# Clear solver cache so each test runs the solver fresh under current code.
	goldberg_brick.equilateral._SOLVED.pop((h, k), None)
	mesh = goldberg_brick.triangulation.build_geodesic_mesh(h, k)
	graph = goldberg_brick.dual.build_goldberg_graph(mesh)
	hexagon_orbits = goldberg_brick.orbits.group_hexagon_orbits(graph)
	# compute_hexagon_orbit_geometries internally calls force_attempt_solve.
	geometries = goldberg_brick.geometry.compute_hexagon_orbit_geometries(
		graph, hexagon_orbits,
	)
	return graph, hexagon_orbits, geometries


#============================================
def test_baseline_cases_solver_converges() -> None:
	"""All seven baseline (h,k) cases reach Stage A convergence."""
	for h, k in BASELINE_CASES:
		goldberg_brick.equilateral._SOLVED.pop((h, k), None)
		positions = goldberg_brick.equilateral.force_attempt_solve(h, k)
		mesh = goldberg_brick.triangulation.build_geodesic_mesh(h, k)
		# Expected vertex count is 20*T.
		expected = 20 * mesh.index_data.t_number
		assert len(positions) == expected, f"GP({h},{k}) vertex count {len(positions)} != {expected}"


#============================================
def test_gp42_planar_warp_mode() -> None:
	"""GP(4,2) Class III: Stage B reaches planar on every hex orbit.

	Validates the Schein-Gayed C16 chiral perimeter reduction (b = a) is
	being applied. Without C16, Stage B settles into a non-planar local
	minimum (warp_mode = boat/chair/asymmetric).
	"""
	_, hexagon_orbits, geometries = _solve_and_measure(4, 2)
	for orbit in hexagon_orbits:
		geometry = geometries[orbit.orbit_id]
		assert geometry.warp_mode == "planar", (
			f"GP(4,2) {orbit.orbit_id}: warp_mode={geometry.warp_mode!r} "
			f"(expected 'planar')"
		)
		assert geometry.planarity_error < 1e-7, (
			f"GP(4,2) {orbit.orbit_id}: planarity_error="
			f"{geometry.planarity_error:.2e} >= 1e-7"
		)


#============================================
def test_gp21_angles_match_schein_gayed_table1() -> None:
	"""GP(2,1) internal angles match SG Table 1 to 1 decimal place.

	Schein-Gayed 2014 Table 1 for T = 7 (chiral, Class III):
	a = 124.2, b = 124.2, c = 131.1, d = 108.2, e = 117.5, f = 114.7 (deg).
	The solved hexagon has six internal angles; compare as a multiset
	(rounded to 1 dp) to be label-order independent.
	"""
	_, hexagon_orbits, geometries = _solve_and_measure(2, 1)
	# GP(2,1) has exactly one hexagon orbit (T = 7, single hex face shape).
	assert len(hexagon_orbits) == 1, (
		f"GP(2,1) expected 1 hex orbit, got {len(hexagon_orbits)}"
	)
	orbit = hexagon_orbits[0]
	geometry = geometries[orbit.orbit_id]
	expected_sorted = sorted([124.2, 124.2, 131.1, 108.2, 117.5, 114.7])
	observed_sorted = sorted(round(a, 1) for a in geometry.angle_sequence)
	for expected, observed in zip(expected_sorted, observed_sorted):
		assert math.isclose(expected, observed, abs_tol=0.1), (
			f"GP(2,1) angle mismatch: expected {expected}, got {observed} "
			f"(full sorted observed: {observed_sorted})"
		)


#============================================
def test_gp42_gp24_mirror_geometry_match() -> None:
	"""GP(2,4) is the mirror enantiomer of GP(4,2); per-orbit geometry matches.

	Sides and angle multisets must match within 1e-6 between (4,2) and (2,4)
	for each hexagon orbit (matched by orbit_id ordering).
	"""
	_, orbits_42, geoms_42 = _solve_and_measure(4, 2)
	_, orbits_24, geoms_24 = _solve_and_measure(2, 4)
	assert len(orbits_42) == len(orbits_24)
	for o42, o24 in zip(orbits_42, orbits_24):
		g42 = geoms_42[o42.orbit_id]
		g24 = geoms_24[o24.orbit_id]
		angles_42 = sorted(g42.angle_sequence)
		angles_24 = sorted(g24.angle_sequence)
		for a, b in zip(angles_42, angles_24):
			assert math.isclose(a, b, abs_tol=1e-6), (
				f"GP(4,2)/GP(2,4) mirror angle mismatch in {o42.orbit_id}: "
				f"{a} vs {b}"
			)
		sides_42 = sorted(g42.side_length_sequence)
		sides_24 = sorted(g24.side_length_sequence)
		for s_a, s_b in zip(sides_42, sides_24):
			assert math.isclose(s_a, s_b, abs_tol=1e-6), (
				f"GP(4,2)/GP(2,4) mirror side mismatch in {o42.orbit_id}: "
				f"{s_a} vs {s_b}"
			)
