"""Dual Goldberg graph construction."""

import dataclasses

import goldberg_brick.triangulation


@dataclasses.dataclass(frozen=True)
class GoldbergFace:
	"""One Goldberg face derived from a geodesic vertex."""

	face_id: str
	source_vertex: goldberg_brick.triangulation.VertexKey
	side_count: int
	face_type: str


@dataclasses.dataclass(frozen=True)
class GoldbergGraph:
	"""Dual Goldberg graph."""

	mesh: goldberg_brick.triangulation.GeodesicMesh
	faces: tuple[GoldbergFace, ...]
	adjacency: dict[str, tuple[str, ...]]
	source_to_face_id: dict[goldberg_brick.triangulation.VertexKey, str]
	vertex_count: int
	edge_count: int


#============================================
def face_type_for_valence(valence: int) -> str:
	"""Convert geodesic valence to Goldberg face type."""
	if valence == 5:
		face_type = "pentagon"
	elif valence == 6:
		face_type = "hexagon"
	else:
		raise ValueError(f"unexpected geodesic valence: {valence}")
	return face_type


#============================================
def build_valence_map(
	mesh: goldberg_brick.triangulation.GeodesicMesh,
) -> dict[goldberg_brick.triangulation.VertexKey, int]:
	"""Build geodesic vertex valences."""
	neighbors = {}
	for vertex in mesh.vertices:
		neighbors[vertex] = set()
	for first, second in mesh.edges:
		neighbors[first].add(second)
		neighbors[second].add(first)
	valences = {}
	for vertex, items in neighbors.items():
		valences[vertex] = len(items)
	return valences


#============================================
def make_face_id(index: int) -> str:
	"""Build a stable internal face ID."""
	face_id = f"F{index:04d}"
	return face_id


#============================================
def build_goldberg_graph(
	mesh: goldberg_brick.triangulation.GeodesicMesh,
) -> GoldbergGraph:
	"""Build the Goldberg dual graph from a geodesic mesh."""
	goldberg_brick.triangulation.validate_mesh_counts(mesh)
	valences = build_valence_map(mesh)
	source_to_face_id = {}
	faces = []
	for index, source_vertex in enumerate(mesh.vertices, start=1):
		face_id = make_face_id(index)
		source_to_face_id[source_vertex] = face_id
		side_count = valences[source_vertex]
		face_type = face_type_for_valence(side_count)
		faces.append(
			GoldbergFace(
				face_id=face_id,
				source_vertex=source_vertex,
				side_count=side_count,
				face_type=face_type,
			)
		)
	neighbors = {face.face_id: set() for face in faces}
	for first, second in mesh.edges:
		first_id = source_to_face_id[first]
		second_id = source_to_face_id[second]
		neighbors[first_id].add(second_id)
		neighbors[second_id].add(first_id)
	adjacency = {}
	for face_id, items in neighbors.items():
		adjacency[face_id] = tuple(sorted(items))
	graph = GoldbergGraph(
		mesh=mesh,
		faces=tuple(faces),
		adjacency=adjacency,
		source_to_face_id=source_to_face_id,
		vertex_count=len(mesh.faces),
		edge_count=len(mesh.edges),
	)
	return graph


#============================================
def count_faces(graph: GoldbergGraph, face_type: str) -> int:
	"""Count Goldberg faces of one type."""
	count = 0
	for face in graph.faces:
		if face.face_type == face_type:
			count += 1
	return count


#============================================
def validate_goldberg_counts(graph: GoldbergGraph) -> None:
	"""Validate Goldberg dual counts against formulas."""
	index_data = graph.mesh.index_data
	if len(graph.faces) != index_data.goldberg_faces:
		raise ValueError("Goldberg face count mismatch")
	if graph.edge_count != index_data.goldberg_edges:
		raise ValueError("Goldberg edge count mismatch")
	if graph.vertex_count != index_data.goldberg_vertices:
		raise ValueError("Goldberg vertex count mismatch")
	if count_faces(graph, "pentagon") != index_data.pentagons:
		raise ValueError("Goldberg pentagon count mismatch")
	if count_faces(graph, "hexagon") != index_data.hexagons:
		raise ValueError("Goldberg hexagon count mismatch")
