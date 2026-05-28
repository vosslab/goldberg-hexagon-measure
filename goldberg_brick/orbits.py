"""Hexagon orbit grouping under icosahedral rotations."""

import dataclasses

import goldberg_brick.dual
import goldberg_brick.triangulation


@dataclasses.dataclass(frozen=True)
class HexagonOrbit:
	"""One deterministic hexagon orbit row."""

	orbit_id: str
	face_count: int
	mirror_orbit: str
	faces: tuple[str, ...]


#============================================
def make_orbit_id(index: int) -> str:
	"""Build a deterministic hexagon orbit ID."""
	orbit_id = f"H{index:03d}"
	return orbit_id


#============================================
def hexagon_source_vertices(
	graph: goldberg_brick.dual.GoldbergGraph,
) -> set[goldberg_brick.triangulation.VertexKey]:
	"""Collect source vertices for Goldberg hexagon faces."""
	items = set()
	for face in graph.faces:
		if face.face_type == "hexagon":
			items.add(face.source_vertex)
	return items


#============================================
def build_orbit_for_source(
	source_vertex: goldberg_brick.triangulation.VertexKey,
	graph: goldberg_brick.dual.GoldbergGraph,
	hexagon_sources: set[goldberg_brick.triangulation.VertexKey],
) -> set[goldberg_brick.triangulation.VertexKey]:
	"""Build one rotation orbit for a hexagon source vertex."""
	t_number = graph.mesh.index_data.t_number
	orbit = set()
	for rotation in graph.mesh.icosahedron.rotations:
		rotated = goldberg_brick.triangulation.rotate_vertex_key(
			source_vertex,
			rotation,
			t_number,
		)
		if rotated not in hexagon_sources:
			raise ValueError("rotation mapped a hexagon outside the hexagon set")
		orbit.add(rotated)
	return orbit


#============================================
def pentagon_adjacent_hex_orbits(
	graph: goldberg_brick.dual.GoldbergGraph,
) -> tuple[str, ...]:
	"""Return orbit IDs of hexagons sharing an edge with a pentagon face.

	Used by the Schein-Gayed C16 chiral perimeter reduction: the perimeter
	angles a, b live on hex faces that touch a pentagon. Reuses the dual
	graph adjacency built in goldberg_brick.dual.
	"""
	# Find face IDs of all pentagons.
	pentagon_face_ids = set()
	for face in graph.faces:
		if face.face_type == "pentagon":
			pentagon_face_ids.add(face.face_id)
	# Find hexagon faces adjacent to any pentagon.
	pent_adjacent_hex_face_ids = set()
	for face in graph.faces:
		if face.face_type != "hexagon":
			continue
		neighbors = graph.adjacency[face.face_id]
		for neighbor_id in neighbors:
			if neighbor_id in pentagon_face_ids:
				pent_adjacent_hex_face_ids.add(face.face_id)
				break
	# Group all hexagons into orbits and pick those that contain any
	# pent-adjacent hex face.
	hex_orbits = group_hexagon_orbits(graph)
	result_orbit_ids = []
	for orbit in hex_orbits:
		for face_id in orbit.faces:
			if face_id in pent_adjacent_hex_face_ids:
				result_orbit_ids.append(orbit.orbit_id)
				break
	return tuple(result_orbit_ids)


#============================================
def group_hexagon_orbits(graph: goldberg_brick.dual.GoldbergGraph) -> tuple[HexagonOrbit, ...]:
	"""Group Goldberg hexagon faces by orientation-preserving rotations."""
	goldberg_brick.dual.validate_goldberg_counts(graph)
	hexagon_sources = hexagon_source_vertices(graph)
	unassigned = set(hexagon_sources)
	orbits = []
	while unassigned:
		source_vertex = sorted(unassigned, key=repr)[0]
		orbit_sources = build_orbit_for_source(source_vertex, graph, hexagon_sources)
		unassigned -= orbit_sources
		face_ids = []
		for orbit_source in orbit_sources:
			face_ids.append(graph.source_to_face_id[orbit_source])
		face_ids.sort()
		orbits.append(
			HexagonOrbit(
				orbit_id=make_orbit_id(len(orbits) + 1),
				face_count=len(face_ids),
				mirror_orbit="NA",
				faces=tuple(face_ids),
			)
		)
	result = tuple(orbits)
	return result
