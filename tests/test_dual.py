import goldberg_brick.dual
import goldberg_brick.icosahedron
import goldberg_brick.triangulation


COUNT_CASES = [(1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1), (4, 2)]


#============================================
def test_icosahedron_counts_and_rotations() -> None:
	"""Build base icosahedron data and validate rotations."""
	base = goldberg_brick.icosahedron.build_icosahedron()
	edge_set = {tuple(sorted(edge)) for edge in base.edges}
	face_sets = {frozenset(face) for face in base.faces}

	assert len(base.vertices) == 12
	assert len(base.edges) == 30
	assert len(base.faces) == 20
	assert len(base.rotations) == 60

	for rotation in base.rotations:
		for first, second in base.edges:
			rotated_edge = tuple(sorted((rotation[first], rotation[second])))
			assert rotated_edge in edge_set
		for face in base.faces:
			rotated_face = frozenset(rotation[vertex] for vertex in face)
			assert rotated_face in face_sets


#============================================
def test_goldberg_dual_counts_for_known_cases() -> None:
	"""Validate Goldberg dual counts for representative cases."""
	for h_index, k_index in COUNT_CASES:
		mesh = goldberg_brick.triangulation.build_geodesic_mesh(h_index, k_index)
		graph = goldberg_brick.dual.build_goldberg_graph(mesh)
		index_data = mesh.index_data

		goldberg_brick.dual.validate_goldberg_counts(graph)
		assert len(graph.faces) == index_data.goldberg_faces
		assert graph.edge_count == index_data.goldberg_edges
		assert graph.vertex_count == index_data.goldberg_vertices
		assert goldberg_brick.dual.count_faces(graph, "pentagon") == 12
		assert goldberg_brick.dual.count_faces(graph, "hexagon") == index_data.hexagons


#============================================
def test_rotations_preserve_geodesic_graph() -> None:
	"""Validate rotations preserve graph edges for representative cases."""
	for h_index, k_index in COUNT_CASES:
		mesh = goldberg_brick.triangulation.build_geodesic_mesh(h_index, k_index)
		edge_set = {frozenset(edge) for edge in mesh.edges}
		vertex_set = set(mesh.vertices)
		for rotation in mesh.icosahedron.rotations:
			for vertex in mesh.vertices:
				rotated_vertex = goldberg_brick.triangulation.rotate_vertex_key(
					vertex,
					rotation,
					mesh.index_data.t_number,
				)
				assert rotated_vertex in vertex_set
			for first, second in mesh.edges:
				rotated_first = goldberg_brick.triangulation.rotate_vertex_key(
					first,
					rotation,
					mesh.index_data.t_number,
				)
				rotated_second = goldberg_brick.triangulation.rotate_vertex_key(
					second,
					rotation,
					mesh.index_data.t_number,
				)
				assert frozenset((rotated_first, rotated_second)) in edge_set
