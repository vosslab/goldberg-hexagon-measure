import goldberg_brick.dual
import goldberg_brick.geometry
import goldberg_brick.orbits
import goldberg_brick.triangulation


COUNT_CASES = [(1, 1), (2, 0), (2, 1), (3, 0), (3, 1), (4, 2)]


#============================================
def test_hexagon_orbits_cover_every_hexagon_once() -> None:
	"""Ensure hexagon orbits partition the hexagon set."""
	for h_index, k_index in COUNT_CASES:
		mesh = goldberg_brick.triangulation.build_geodesic_mesh(h_index, k_index)
		graph = goldberg_brick.dual.build_goldberg_graph(mesh)
		hexagon_orbits = goldberg_brick.orbits.group_hexagon_orbits(graph)
		hexagon_count = goldberg_brick.dual.count_faces(graph, "hexagon")
		covered_faces = []

		for orbit in hexagon_orbits:
			assert orbit.orbit_id.startswith("H")
			assert orbit.mirror_orbit == "NA"
			assert orbit.face_count == len(orbit.faces)
			covered_faces.extend(orbit.faces)

		assert len(covered_faces) == hexagon_count
		assert len(set(covered_faces)) == hexagon_count


#============================================
def test_class_iii_mirror_inputs_are_not_collapsed() -> None:
	"""Preserve class III input ordering for mirror pairs."""
	mesh_4_2 = goldberg_brick.triangulation.build_geodesic_mesh(4, 2)
	mesh_2_4 = goldberg_brick.triangulation.build_geodesic_mesh(2, 4)
	graph_4_2 = goldberg_brick.dual.build_goldberg_graph(mesh_4_2)
	graph_2_4 = goldberg_brick.dual.build_goldberg_graph(mesh_2_4)
	orbits_4_2 = goldberg_brick.orbits.group_hexagon_orbits(graph_4_2)
	orbits_2_4 = goldberg_brick.orbits.group_hexagon_orbits(graph_2_4)

	assert mesh_4_2.index_data.h == 4
	assert mesh_4_2.index_data.k == 2
	assert mesh_2_4.index_data.h == 2
	assert mesh_2_4.index_data.k == 4
	assert mesh_4_2.index_data.goldberg_class == "III"
	assert mesh_2_4.index_data.goldberg_class == "III"
	assert sum(orbit.face_count for orbit in orbits_4_2) == 270
	assert sum(orbit.face_count for orbit in orbits_2_4) == 270


#============================================
def test_hexagon_orbit_geometry_is_measured() -> None:
	"""Compute measured geometry for every GP(4,2) hexagon orbit."""
	mesh = goldberg_brick.triangulation.build_geodesic_mesh(4, 2)
	graph = goldberg_brick.dual.build_goldberg_graph(mesh)
	hexagon_orbits = goldberg_brick.orbits.group_hexagon_orbits(graph)
	geometries = goldberg_brick.geometry.compute_hexagon_orbit_geometries(
		graph,
		hexagon_orbits,
	)

	assert set(geometries) == {orbit.orbit_id for orbit in hexagon_orbits}
	for geometry in geometries.values():
		assert len(geometry.side_length_sequence) == 6
		assert len(geometry.angle_sequence) == 6
		assert len(geometry.dihedral_angle_sequence) == 6
		assert all(value > 0.0 for value in geometry.side_length_sequence)
		assert all(value > 0.0 for value in geometry.angle_sequence)
		assert geometry.planarity_error >= 0.0


#============================================
def test_builder_summaries_are_computed() -> None:
	"""Compute builder-facing pattern summaries for GP(4,2)."""
	mesh = goldberg_brick.triangulation.build_geodesic_mesh(4, 2)
	graph = goldberg_brick.dual.build_goldberg_graph(mesh)
	hexagon_orbits = goldberg_brick.orbits.group_hexagon_orbits(graph)
	geometries = goldberg_brick.geometry.compute_hexagon_orbit_geometries(
		graph,
		hexagon_orbits,
	)
	summaries = goldberg_brick.geometry.compute_builder_summaries(graph, geometries)

	assert set(summaries) == {orbit.orbit_id for orbit in hexagon_orbits}
	for summary in summaries.values():
		assert len(summary.angle_pattern_code) == 6
		assert len(summary.side_pattern_code) == 6
		assert summary.orientation == "GP(4,2); mirror GP(2,4)"
		assert summary.difficulty in ("easy", "medium", "hard")
		assert summary.suggested_use
		assert summary.reuse_group in (
			"likely reusable together",
			"needs testing",
			"custom / high distortion",
		)
