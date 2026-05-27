"""Geodesic triangulation for icosahedral Goldberg indices."""

import dataclasses
import math

import goldberg_brick.icosahedron
import goldberg_brick.indices


VertexKey = tuple
LatticePoint = tuple[int, int]


@dataclasses.dataclass(frozen=True)
class GeodesicMesh:
	"""Geodesic triangulation graph."""

	index_data: goldberg_brick.indices.GoldbergIndices
	icosahedron: goldberg_brick.icosahedron.Icosahedron
	vertices: tuple[VertexKey, ...]
	edges: tuple[tuple[VertexKey, VertexKey], ...]
	faces: tuple[tuple[VertexKey, VertexKey, VertexKey], ...]


#============================================
def canonical_vertex_key(weights: dict[int, int], t_number: int) -> VertexKey:
	"""Create a canonical geodesic vertex key from base-vertex weights."""
	support = {}
	for vertex_id, weight in weights.items():
		if weight:
			support[vertex_id] = weight
	if len(support) == 1:
		vertex_id = next(iter(support))
		key = ("V", vertex_id)
	elif len(support) == 2:
		vertices = sorted(support)
		first, second = vertices
		key = ("E", first, second, support[first])
	elif len(support) == 3:
		vertices = tuple(sorted(support))
		key = (
			"F",
			vertices[0],
			vertices[1],
			vertices[2],
			support[vertices[0]],
			support[vertices[1]],
		)
	else:
		raise ValueError("geodesic vertex weights must use one, two, or three vertices")
	weight_total = sum(support.values())
	if weight_total != t_number:
		raise ValueError("geodesic vertex weights do not sum to T")
	return key


#============================================
def key_weights(key: VertexKey, t_number: int) -> dict[int, int]:
	"""Convert a canonical geodesic vertex key back to base-vertex weights."""
	if key[0] == "V":
		weights = {key[1]: t_number}
	elif key[0] == "E":
		_, first, second, first_weight = key
		weights = {
			first: first_weight,
			second: t_number - first_weight,
		}
	elif key[0] == "F":
		_, first, second, third, first_weight, second_weight = key
		weights = {
			first: first_weight,
			second: second_weight,
			third: t_number - first_weight - second_weight,
		}
	else:
		raise ValueError(f"unknown vertex key type: {key[0]}")
	return weights


#============================================
def normalized_coordinate(
	key: VertexKey,
	t_number: int,
	base: goldberg_brick.icosahedron.Icosahedron,
) -> tuple[float, float, float]:
	"""Build a normalized coordinate for nearest-neighbor graph recovery."""
	weights = key_weights(key, t_number)
	x_coord = 0.0
	y_coord = 0.0
	z_coord = 0.0
	for vertex_id, weight in weights.items():
		coordinate = base.coordinates[vertex_id]
		x_coord += coordinate[0] * weight
		y_coord += coordinate[1] * weight
		z_coord += coordinate[2] * weight
	length = math.sqrt(x_coord * x_coord + y_coord * y_coord + z_coord * z_coord)
	value = (x_coord / length, y_coord / length, z_coord / length)
	return value


#============================================
def target_valence(key: VertexKey) -> int:
	"""Return expected geodesic valence for a vertex key."""
	if key[0] == "V":
		valence = 5
	else:
		valence = 6
	return valence


#============================================
def coordinate_distance_squared(
	first: tuple[float, float, float],
	second: tuple[float, float, float],
) -> float:
	"""Return squared distance between normalized coordinates."""
	dx_coord = first[0] - second[0]
	dy_coord = first[1] - second[1]
	dz_coord = first[2] - second[2]
	value = dx_coord * dx_coord + dy_coord * dy_coord + dz_coord * dz_coord
	return value


#============================================
def build_edges_by_distance(
	vertices: tuple[VertexKey, ...],
	t_number: int,
	base: goldberg_brick.icosahedron.Icosahedron,
) -> tuple[tuple[VertexKey, VertexKey], ...]:
	"""Build geodesic graph edges from nearest neighbors and valence targets."""
	coordinates = {}
	for vertex in vertices:
		coordinates[vertex] = normalized_coordinate(vertex, t_number, base)
	candidates = []
	for first_index, first in enumerate(vertices):
		for second in vertices[first_index + 1:]:
			distance = coordinate_distance_squared(coordinates[first], coordinates[second])
			candidates.append((distance, repr(first), repr(second), first, second))
	candidates.sort()
	valences = {}
	for vertex in vertices:
		valences[vertex] = 0
	edges = []
	for _, _, _, first, second in candidates:
		if valences[first] >= target_valence(first):
			continue
		if valences[second] >= target_valence(second):
			continue
		edges.append(sorted_edge(first, second))
		valences[first] += 1
		valences[second] += 1
		if all(valences[vertex] == target_valence(vertex) for vertex in vertices):
			break
	incomplete = []
	for vertex in vertices:
		if valences[vertex] != target_valence(vertex):
			incomplete.append(f"{vertex}: {valences[vertex]} != {target_valence(vertex)}")
	if incomplete:
		raise ValueError("failed to satisfy geodesic valences: " + "; ".join(incomplete[:5]))
	result = tuple(sorted(edges, key=repr))
	return result


#============================================
def build_triangular_faces_from_edges(
	vertices: tuple[VertexKey, ...],
	edges: tuple[tuple[VertexKey, VertexKey], ...],
) -> tuple[tuple[VertexKey, VertexKey, VertexKey], ...]:
	"""Build triangular mesh faces as 3-cliques in the geodesic graph."""
	neighbors = {}
	for vertex in vertices:
		neighbors[vertex] = set()
	for first, second in edges:
		neighbors[first].add(second)
		neighbors[second].add(first)
	vertex_order = {vertex: index for index, vertex in enumerate(vertices)}
	faces = []
	for first in vertices:
		first_neighbors = sorted(neighbors[first], key=repr)
		for second in first_neighbors:
			if vertex_order[second] <= vertex_order[first]:
				continue
			common_neighbors = neighbors[first].intersection(neighbors[second])
			for third in sorted(common_neighbors, key=repr):
				if vertex_order[third] <= vertex_order[second]:
					continue
				faces.append((first, second, third))
	result = tuple(faces)
	return result


#============================================
def rotate_vertex_key(
	key: VertexKey,
	rotation: dict[int, int],
	t_number: int,
) -> VertexKey:
	"""Rotate a geodesic vertex key using a base icosahedron permutation."""
	weights = key_weights(key, t_number)
	rotated_weights = {}
	for vertex_id, weight in weights.items():
		rotated_weights[rotation[vertex_id]] = weight
	rotated_key = canonical_vertex_key(rotated_weights, t_number)
	return rotated_key


#============================================
def barycentric_numerators(
	point: LatticePoint,
	h: int,
	k: int,
	t_number: int,
) -> tuple[int, int, int]:
	"""Calculate barycentric numerators for a lattice point."""
	x_coord, y_coord = point
	beta = (h + k) * x_coord + k * y_coord
	gamma = -k * x_coord + h * y_coord
	alpha = t_number - beta - gamma
	return alpha, beta, gamma


#============================================
def point_inside_triangle(point: LatticePoint, h: int, k: int, t_number: int) -> bool:
	"""Check whether a lattice point is inside the Goldberg triangle."""
	alpha, beta, gamma = barycentric_numerators(point, h, k, t_number)
	inside = (
		alpha >= 0
		and beta >= 0
		and gamma >= 0
	)
	return inside


#============================================
def enumerate_lattice_points(h: int, k: int, t_number: int) -> tuple[LatticePoint, ...]:
	"""Enumerate lattice points inside the Goldberg triangle."""
	corners = ((0, 0), (h, k), (-k, h + k))
	min_x = min(point[0] for point in corners) - 1
	max_x = max(point[0] for point in corners) + 1
	min_y = min(point[1] for point in corners) - 1
	max_y = max(point[1] for point in corners) + 1
	points = []
	for x_coord in range(min_x, max_x + 1):
		for y_coord in range(min_y, max_y + 1):
			point = (x_coord, y_coord)
			if point_inside_triangle(point, h, k, t_number):
				points.append(point)
	points.sort()
	result = tuple(points)
	return result


#============================================
def local_point_key(
	face: tuple[int, int, int],
	point: LatticePoint,
	h: int,
	k: int,
	t_number: int,
) -> VertexKey:
	"""Build a canonical geodesic vertex key for one local lattice point."""
	alpha, beta, gamma = barycentric_numerators(point, h, k, t_number)
	weights = {
		face[0]: alpha,
		face[1]: beta,
		face[2]: gamma,
	}
	key = canonical_vertex_key(weights, t_number)
	return key


#============================================
def sorted_edge(first: VertexKey, second: VertexKey) -> tuple[VertexKey, VertexKey]:
	"""Return a deterministic undirected edge."""
	if repr(first) <= repr(second):
		edge = (first, second)
	else:
		edge = (second, first)
	return edge


#============================================
def orientation(a: LatticePoint, b: LatticePoint, c: LatticePoint) -> int:
	"""Return twice the signed area of a lattice triangle."""
	value = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
	return value


#============================================
def triangle_contains_point(
	triangle: tuple[LatticePoint, LatticePoint, LatticePoint],
	point: LatticePoint,
) -> bool:
	"""Check whether a point is inside or on a triangle boundary."""
	first, second, third = triangle
	area = orientation(first, second, third)
	if area == 0:
		return False
	values = (
		orientation(first, second, point),
		orientation(second, third, point),
		orientation(third, first, point),
	)
	if area > 0:
		inside = all(value >= 0 for value in values)
	else:
		inside = all(value <= 0 for value in values)
	return inside


#============================================
def is_minimal_triangle(
	triangle: tuple[LatticePoint, LatticePoint, LatticePoint],
	points: tuple[LatticePoint, ...],
) -> bool:
	"""Check that no other local point lies inside a triangle."""
	triangle_points = set(triangle)
	for point in points:
		if point in triangle_points:
			continue
		if triangle_contains_point(triangle, point):
			return False
	return True


#============================================
def orient_triangle(
	triangle: tuple[VertexKey, VertexKey, VertexKey],
) -> tuple[VertexKey, VertexKey, VertexKey]:
	"""Return a deterministic triangle key."""
	ordered = tuple(sorted(triangle, key=repr))
	return ordered


#============================================
def add_face_lattice(
	base_face: tuple[int, int, int],
	h: int,
	k: int,
	t_number: int,
	point_to_key: dict[LatticePoint, VertexKey],
	vertices: set[VertexKey],
	edges: set[tuple[VertexKey, VertexKey]],
	faces: set[tuple[VertexKey, VertexKey, VertexKey]],
) -> None:
	"""Add local lattice edges and triangles for one icosahedron face."""
	directions = ((1, 0), (0, 1), (1, -1))
	local_edges = set()
	for key in point_to_key.values():
		vertices.add(key)
	for point, first_key in point_to_key.items():
		for dx_coord, dy_coord in directions:
			neighbor = (point[0] + dx_coord, point[1] + dy_coord)
			if neighbor not in point_to_key:
				continue
			edge = sorted_edge(first_key, point_to_key[neighbor])
			edges.add(edge)
			local_edges.add(tuple(sorted((point, neighbor))))
	for zero_index in range(3):
		boundary_points = []
		for point in point_to_key:
			weights = barycentric_numerators(point, h, k, t_number)
			if weights[zero_index] != 0:
				continue
			boundary_points.append((weights, point))
		boundary_points.sort()
		for index in range(len(boundary_points) - 1):
			first = boundary_points[index][1]
			second = boundary_points[index + 1][1]
			edge = sorted_edge(point_to_key[first], point_to_key[second])
			edges.add(edge)
			local_edges.add(tuple(sorted((first, second))))
	points = tuple(sorted(point_to_key))
	for first_index, first in enumerate(points):
		for second_index in range(first_index + 1, len(points)):
			second = points[second_index]
			first_edge = tuple(sorted((first, second)))
			if first_edge not in local_edges:
				continue
			for third in points[second_index + 1:]:
				second_edge = tuple(sorted((first, third)))
				third_edge = tuple(sorted((second, third)))
				if second_edge not in local_edges or third_edge not in local_edges:
					continue
				local_triangle = (first, second, third)
				if not is_minimal_triangle(local_triangle, points):
					continue
				triangle = (
					point_to_key[first],
					point_to_key[second],
					point_to_key[third],
				)
				if len(set(triangle)) != 3:
					continue
				faces.add(orient_triangle(triangle))
	_ = base_face


#============================================
def build_geodesic_mesh(h: int, k: int) -> GeodesicMesh:
	"""Build the geodesic triangulation for Goldberg indices."""
	index_data = goldberg_brick.indices.build_indices(h, k)
	base = goldberg_brick.icosahedron.build_icosahedron()
	local_points = enumerate_lattice_points(h, k, index_data.t_number)
	vertices: set[VertexKey] = set()
	edges: set[tuple[VertexKey, VertexKey]] = set()
	faces: set[tuple[VertexKey, VertexKey, VertexKey]] = set()
	for base_face in base.faces:
		point_to_key = {}
		for point in local_points:
			point_to_key[point] = local_point_key(
				base_face,
				point,
				h,
				k,
				index_data.t_number,
			)
		add_face_lattice(
			base_face,
			h,
			k,
			index_data.t_number,
			point_to_key,
			vertices,
			edges,
			faces,
		)
	vertex_tuple = tuple(sorted(vertices, key=repr))
	edge_tuple = build_edges_by_distance(vertex_tuple, index_data.t_number, base)
	face_tuple = build_triangular_faces_from_edges(vertex_tuple, edge_tuple)
	mesh = GeodesicMesh(
		index_data=index_data,
		icosahedron=base,
		vertices=vertex_tuple,
		edges=edge_tuple,
		faces=face_tuple,
	)
	return mesh


#============================================
def validate_mesh_counts(mesh: GeodesicMesh) -> None:
	"""Validate geodesic mesh counts against formulas."""
	index_data = mesh.index_data
	if len(mesh.vertices) != index_data.geodesic_vertices:
		raise ValueError(
			f"geodesic vertex count mismatch: {len(mesh.vertices)} != "
			f"{index_data.geodesic_vertices}"
		)
	if len(mesh.edges) != index_data.geodesic_edges:
		raise ValueError(
			f"geodesic edge count mismatch: {len(mesh.edges)} != "
			f"{index_data.geodesic_edges}"
		)
	if len(mesh.faces) != index_data.geodesic_faces:
		raise ValueError(
			f"geodesic triangular face count mismatch: {len(mesh.faces)} != "
			f"{index_data.geodesic_faces}"
		)
