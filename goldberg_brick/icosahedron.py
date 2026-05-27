"""Base icosahedron graph and orientation-preserving rotations."""

import dataclasses
import math


FLOAT_TOLERANCE = 1e-6


@dataclasses.dataclass(frozen=True)
class Icosahedron:
	"""Base icosahedron combinatorial data."""

	vertices: tuple[int, ...]
	coordinates: dict[int, tuple[float, float, float]]
	edges: tuple[tuple[int, int], ...]
	faces: tuple[tuple[int, int, int], ...]
	rotations: tuple[dict[int, int], ...]


#============================================
def dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
	"""Return a vector dot product."""
	value = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
	return value


#============================================
def subtract(
	a: tuple[float, float, float],
	b: tuple[float, float, float],
) -> tuple[float, float, float]:
	"""Subtract vector b from vector a."""
	value = (a[0] - b[0], a[1] - b[1], a[2] - b[2])
	return value


#============================================
def cross(
	a: tuple[float, float, float],
	b: tuple[float, float, float],
) -> tuple[float, float, float]:
	"""Return a vector cross product."""
	value = (
		a[1] * b[2] - a[2] * b[1],
		a[2] * b[0] - a[0] * b[2],
		a[0] * b[1] - a[1] * b[0],
	)
	return value


#============================================
def norm(a: tuple[float, float, float]) -> float:
	"""Return vector length."""
	value = math.sqrt(dot(a, a))
	return value


#============================================
def normalize(a: tuple[float, float, float]) -> tuple[float, float, float]:
	"""Return a unit vector."""
	length = norm(a)
	value = (a[0] / length, a[1] / length, a[2] / length)
	return value


#============================================
def matrix_vector(
	matrix: tuple[tuple[float, float, float], ...],
	vector: tuple[float, float, float],
) -> tuple[float, float, float]:
	"""Multiply a 3 by 3 matrix by a vector."""
	value = (
		dot(matrix[0], vector),
		dot(matrix[1], vector),
		dot(matrix[2], vector),
	)
	return value


#============================================
def transpose(
	matrix: tuple[tuple[float, float, float], ...],
) -> tuple[tuple[float, float, float], ...]:
	"""Transpose a 3 by 3 matrix."""
	value = (
		(matrix[0][0], matrix[1][0], matrix[2][0]),
		(matrix[0][1], matrix[1][1], matrix[2][1]),
		(matrix[0][2], matrix[1][2], matrix[2][2]),
	)
	return value


#============================================
def matrix_multiply(
	a: tuple[tuple[float, float, float], ...],
	b: tuple[tuple[float, float, float], ...],
) -> tuple[tuple[float, float, float], ...]:
	"""Multiply two 3 by 3 matrices."""
	b_columns = transpose(b)
	rows = []
	for a_row in a:
		row = []
		for b_column in b_columns:
			row.append(dot(a_row, b_column))
		rows.append(tuple(row))
	value = tuple(rows)
	return value


#============================================
def build_coordinates() -> dict[int, tuple[float, float, float]]:
	"""Build standard icosahedron coordinates."""
	phi = (1.0 + math.sqrt(5.0)) / 2.0
	points = [
		(0.0, -1.0, -phi),
		(0.0, -1.0, phi),
		(0.0, 1.0, -phi),
		(0.0, 1.0, phi),
		(-1.0, -phi, 0.0),
		(-1.0, phi, 0.0),
		(1.0, -phi, 0.0),
		(1.0, phi, 0.0),
		(-phi, 0.0, -1.0),
		(phi, 0.0, -1.0),
		(-phi, 0.0, 1.0),
		(phi, 0.0, 1.0),
	]
	coordinates = {}
	for index, point in enumerate(points):
		coordinates[index] = point
	return coordinates


#============================================
def distance_squared(
	a: tuple[float, float, float],
	b: tuple[float, float, float],
) -> float:
	"""Return squared distance between two points."""
	delta = subtract(a, b)
	value = dot(delta, delta)
	return value


#============================================
def build_edges(
	coordinates: dict[int, tuple[float, float, float]],
) -> tuple[tuple[int, int], ...]:
	"""Build icosahedron edges from nearest-neighbor distances."""
	distances = []
	vertex_ids = sorted(coordinates)
	for index, first in enumerate(vertex_ids):
		for second in vertex_ids[index + 1:]:
			distances.append(distance_squared(coordinates[first], coordinates[second]))
	edge_distance = min(distances)
	edges = []
	for index, first in enumerate(vertex_ids):
		for second in vertex_ids[index + 1:]:
			distance = distance_squared(coordinates[first], coordinates[second])
			if abs(distance - edge_distance) < FLOAT_TOLERANCE:
				edges.append((first, second))
	result = tuple(edges)
	return result


#============================================
def orient_face(
	face: tuple[int, int, int],
	coordinates: dict[int, tuple[float, float, float]],
) -> tuple[int, int, int]:
	"""Orient one triangular face outward."""
	a_id, b_id, c_id = face
	a = coordinates[a_id]
	b = coordinates[b_id]
	c = coordinates[c_id]
	normal = cross(subtract(b, a), subtract(c, a))
	centroid = (
		(a[0] + b[0] + c[0]) / 3.0,
		(a[1] + b[1] + c[1]) / 3.0,
		(a[2] + b[2] + c[2]) / 3.0,
	)
	if dot(normal, centroid) < 0.0:
		oriented = (a_id, c_id, b_id)
	else:
		oriented = face
	return oriented


#============================================
def build_faces(
	coordinates: dict[int, tuple[float, float, float]],
	edges: tuple[tuple[int, int], ...],
) -> tuple[tuple[int, int, int], ...]:
	"""Build oriented triangular icosahedron faces."""
	edge_set = {tuple(sorted(edge)) for edge in edges}
	vertex_ids = sorted(coordinates)
	faces = []
	for first_index, first in enumerate(vertex_ids):
		for second_index in range(first_index + 1, len(vertex_ids)):
			second = vertex_ids[second_index]
			for third in vertex_ids[second_index + 1:]:
				pairs = [
					tuple(sorted((first, second))),
					tuple(sorted((first, third))),
					tuple(sorted((second, third))),
				]
				if all(pair in edge_set for pair in pairs):
					faces.append(orient_face((first, second, third), coordinates))
	faces.sort()
	result = tuple(faces)
	return result


#============================================
def face_basis(
	face: tuple[int, int, int],
	coordinates: dict[int, tuple[float, float, float]],
) -> tuple[tuple[float, float, float], ...]:
	"""Build an orthonormal basis for one oriented face."""
	a = coordinates[face[0]]
	b = coordinates[face[1]]
	c = coordinates[face[2]]
	e1 = normalize(subtract(b, a))
	normal = normalize(cross(subtract(b, a), subtract(c, a)))
	e2 = cross(normal, e1)
	basis = (e1, e2, normal)
	return basis


#============================================
def find_matching_vertex(
	point: tuple[float, float, float],
	coordinates: dict[int, tuple[float, float, float]],
) -> int:
	"""Find the vertex matching a rotated point."""
	best_vertex = -1
	best_distance = float("inf")
	for vertex_id, coordinate in coordinates.items():
		distance = distance_squared(point, coordinate)
		if distance < best_distance:
			best_distance = distance
			best_vertex = vertex_id
	if best_distance > FLOAT_TOLERANCE:
		raise ValueError("rotation did not map to an icosahedron vertex")
	return best_vertex


#============================================
def build_rotation_for_faces(
	source_face: tuple[int, int, int],
	target_face: tuple[int, int, int],
	coordinates: dict[int, tuple[float, float, float]],
) -> dict[int, int]:
	"""Build the vertex permutation mapping one oriented face to another."""
	source_basis = face_basis(source_face, coordinates)
	target_basis = face_basis(target_face, coordinates)
	rotation = matrix_multiply(transpose(target_basis), source_basis)
	permutation = {}
	for vertex_id, coordinate in coordinates.items():
		rotated = matrix_vector(rotation, coordinate)
		permutation[vertex_id] = find_matching_vertex(rotated, coordinates)
	return permutation


#============================================
def build_rotations(
	coordinates: dict[int, tuple[float, float, float]],
	faces: tuple[tuple[int, int, int], ...],
) -> tuple[dict[int, int], ...]:
	"""Build all 60 orientation-preserving icosahedron rotations."""
	source_face = faces[0]
	rotations_by_key = {}
	for face in faces:
		cycles = (
			face,
			(face[1], face[2], face[0]),
			(face[2], face[0], face[1]),
		)
		for target_face in cycles:
			permutation = build_rotation_for_faces(source_face, target_face, coordinates)
			key = tuple(permutation[index] for index in sorted(coordinates))
			rotations_by_key[key] = permutation
	rotations = tuple(rotations_by_key[key] for key in sorted(rotations_by_key))
	return rotations


#============================================
def build_icosahedron() -> Icosahedron:
	"""Build the base icosahedron."""
	coordinates = build_coordinates()
	edges = build_edges(coordinates)
	faces = build_faces(coordinates, edges)
	rotations = build_rotations(coordinates, faces)
	result = Icosahedron(
		vertices=tuple(sorted(coordinates)),
		coordinates=coordinates,
		edges=edges,
		faces=faces,
		rotations=rotations,
	)
	return result
