"""Measured spherical geometry for Goldberg hexagon orbit representatives."""

import dataclasses
import math

import goldberg_brick.dual
import goldberg_brick.orbits
import goldberg_brick.triangulation


Point3D = tuple[float, float, float]


@dataclasses.dataclass(frozen=True)
class HexagonGeometry:
	"""Measured geometry for one representative hexagon orbit."""

	orbit_id: str
	side_length_sequence: tuple[float, ...]
	angle_sequence: tuple[float, ...]
	planarity_error: float
	dihedral_angle_sequence: tuple[float, ...]


@dataclasses.dataclass(frozen=True)
class BuilderSummary:
	"""Builder-facing interpretation of measured hexagon geometry."""

	orbit_id: str
	angle_pattern: str
	angle_pattern_unoriented: str
	side_pattern: str
	side_pattern_unoriented: str
	dihedral_pattern: str
	dihedral_pattern_unoriented: str
	warp_mode: str
	orientation: str
	difficulty: str
	shape_summary: str
	max_angle_deviation: float
	side_length_spread_percent: float
	dihedral_spread: float
	planarity_status: str
	suggested_use: str
	reuse_group: str


#============================================
def dot(first: Point3D, second: Point3D) -> float:
	"""Return a vector dot product."""
	value = first[0] * second[0] + first[1] * second[1] + first[2] * second[2]
	return value


#============================================
def add(first: Point3D, second: Point3D) -> Point3D:
	"""Add two vectors."""
	value = (first[0] + second[0], first[1] + second[1], first[2] + second[2])
	return value


#============================================
def subtract(first: Point3D, second: Point3D) -> Point3D:
	"""Subtract second vector from first vector."""
	value = (first[0] - second[0], first[1] - second[1], first[2] - second[2])
	return value


#============================================
def scale(point: Point3D, factor: float) -> Point3D:
	"""Scale a vector."""
	value = (point[0] * factor, point[1] * factor, point[2] * factor)
	return value


#============================================
def cross(first: Point3D, second: Point3D) -> Point3D:
	"""Return a vector cross product."""
	value = (
		first[1] * second[2] - first[2] * second[1],
		first[2] * second[0] - first[0] * second[2],
		first[0] * second[1] - first[1] * second[0],
	)
	return value


#============================================
def length(point: Point3D) -> float:
	"""Return vector length."""
	value = math.sqrt(dot(point, point))
	return value


#============================================
def normalize(point: Point3D) -> Point3D:
	"""Return a normalized vector."""
	point_length = length(point)
	if point_length == 0.0:
		raise ValueError("cannot normalize zero-length vector")
	value = scale(point, 1.0 / point_length)
	return value


#============================================
def clamp(value: float, minimum: float, maximum: float) -> float:
	"""Clamp a floating-point value."""
	if value < minimum:
		result = minimum
	elif value > maximum:
		result = maximum
	else:
		result = value
	return result


#============================================
def angle_degrees(first: Point3D, second: Point3D) -> float:
	"""Return the angle between vectors in degrees."""
	cosine = dot(first, second) / (length(first) * length(second))
	cosine = clamp(cosine, -1.0, 1.0)
	value = math.degrees(math.acos(cosine))
	return value


#============================================
def vertex_coordinate(
	mesh: goldberg_brick.triangulation.GeodesicMesh,
	vertex: goldberg_brick.triangulation.VertexKey,
) -> Point3D:
	"""Return the spherical coordinate for a geodesic vertex."""
	coordinate = goldberg_brick.triangulation.normalized_coordinate(
		vertex,
		mesh.index_data.t_number,
		mesh.icosahedron,
	)
	return coordinate


#============================================
def triangle_centroid_coordinate(
	mesh: goldberg_brick.triangulation.GeodesicMesh,
	triangle: tuple[goldberg_brick.triangulation.VertexKey, ...],
) -> Point3D:
	"""Return projected spherical centroid for a geodesic triangle."""
	total = (0.0, 0.0, 0.0)
	for vertex in triangle:
		total = add(total, vertex_coordinate(mesh, vertex))
	centroid = scale(total, 1.0 / 3.0)
	coordinate = normalize(centroid)
	return coordinate


#============================================
def build_incident_triangles(
	mesh: goldberg_brick.triangulation.GeodesicMesh,
) -> dict[
	goldberg_brick.triangulation.VertexKey,
	tuple[tuple[goldberg_brick.triangulation.VertexKey, ...], ...],
]:
	"""Group mesh triangles by incident geodesic vertex."""
	items = {}
	for vertex in mesh.vertices:
		items[vertex] = []
	for triangle in mesh.faces:
		for vertex in triangle:
			items[vertex].append(triangle)
	result = {}
	for vertex, triangles in items.items():
		result[vertex] = tuple(triangles)
	return result


#============================================
def tangent_basis(center: Point3D) -> tuple[Point3D, Point3D]:
	"""Build a deterministic tangent basis around a spherical point."""
	reference = (0.0, 0.0, 1.0)
	if abs(dot(center, reference)) > 0.9:
		reference = (0.0, 1.0, 0.0)
	first = normalize(cross(reference, center))
	second = normalize(cross(center, first))
	return first, second


#============================================
def order_triangles_around_vertex(
	mesh: goldberg_brick.triangulation.GeodesicMesh,
	source_vertex: goldberg_brick.triangulation.VertexKey,
	triangles: tuple[tuple[goldberg_brick.triangulation.VertexKey, ...], ...],
) -> tuple[tuple[goldberg_brick.triangulation.VertexKey, ...], ...]:
	"""Order incident triangles around a geodesic vertex."""
	center = vertex_coordinate(mesh, source_vertex)
	basis_x, basis_y = tangent_basis(center)
	keyed = []
	for triangle in triangles:
		point = triangle_centroid_coordinate(mesh, triangle)
		delta = subtract(point, center)
		angle = math.atan2(dot(delta, basis_y), dot(delta, basis_x))
		keyed.append((angle, repr(triangle), triangle))
	keyed.sort()
	ordered = tuple(item[2] for item in keyed)
	return ordered


#============================================
def ordered_goldberg_vertices(
	mesh: goldberg_brick.triangulation.GeodesicMesh,
	source_vertex: goldberg_brick.triangulation.VertexKey,
	incident_triangles: dict[
		goldberg_brick.triangulation.VertexKey,
		tuple[tuple[goldberg_brick.triangulation.VertexKey, ...], ...],
	],
) -> tuple[Point3D, ...]:
	"""Return ordered spherical vertices for one Goldberg face."""
	triangles = incident_triangles[source_vertex]
	ordered_triangles = order_triangles_around_vertex(mesh, source_vertex, triangles)
	points = []
	for triangle in ordered_triangles:
		points.append(triangle_centroid_coordinate(mesh, triangle))
	result = tuple(points)
	return result


#============================================
def polygon_normal(points: tuple[Point3D, ...]) -> Point3D:
	"""Return a Newell-style polygon normal."""
	normal = (0.0, 0.0, 0.0)
	for index, point in enumerate(points):
		next_point = points[(index + 1) % len(points)]
		term = cross(point, next_point)
		normal = add(normal, term)
	result = normalize(normal)
	return result


#============================================
def polygon_centroid(points: tuple[Point3D, ...]) -> Point3D:
	"""Return polygon centroid."""
	total = (0.0, 0.0, 0.0)
	for point in points:
		total = add(total, point)
	centroid = scale(total, 1.0 / len(points))
	return centroid


#============================================
def side_lengths(points: tuple[Point3D, ...]) -> tuple[float, ...]:
	"""Return chord side lengths for an ordered spherical polygon."""
	values = []
	for index, point in enumerate(points):
		next_point = points[(index + 1) % len(points)]
		values.append(length(subtract(next_point, point)))
	return tuple(values)


#============================================
def internal_angles(points: tuple[Point3D, ...]) -> tuple[float, ...]:
	"""Return internal angles for an ordered 3D polygon."""
	normal = polygon_normal(points)
	values = []
	for index, point in enumerate(points):
		prev_point = points[index - 1]
		next_point = points[(index + 1) % len(points)]
		incoming = normalize(subtract(prev_point, point))
		outgoing = normalize(subtract(next_point, point))
		turn_normal = cross(outgoing, incoming)
		angle = math.degrees(math.atan2(dot(turn_normal, normal), dot(incoming, outgoing)))
		if angle < 0.0:
			angle += 360.0
		values.append(angle)
	return tuple(values)


#============================================
def planarity_error(points: tuple[Point3D, ...]) -> float:
	"""Return maximum point distance from the representative best-fit plane."""
	normal = polygon_normal(points)
	centroid = polygon_centroid(points)
	max_distance = 0.0
	for point in points:
		distance = abs(dot(subtract(point, centroid), normal))
		if distance > max_distance:
			max_distance = distance
	return max_distance


#============================================
def face_points_for_source(
	graph: goldberg_brick.dual.GoldbergGraph,
	source_vertex: goldberg_brick.triangulation.VertexKey,
	incident_triangles: dict[
		goldberg_brick.triangulation.VertexKey,
		tuple[tuple[goldberg_brick.triangulation.VertexKey, ...], ...],
	],
) -> tuple[Point3D, ...]:
	"""Return ordered points for a Goldberg face source vertex."""
	points = ordered_goldberg_vertices(graph.mesh, source_vertex, incident_triangles)
	return points


#============================================
def dihedral_angles(
	graph: goldberg_brick.dual.GoldbergGraph,
	source_vertex: goldberg_brick.triangulation.VertexKey,
	points: tuple[Point3D, ...],
	incident_triangles: dict[
		goldberg_brick.triangulation.VertexKey,
		tuple[tuple[goldberg_brick.triangulation.VertexKey, ...], ...],
	],
) -> tuple[float, ...]:
	"""Return dihedral angles against adjacent Goldberg faces."""
	face_normal = polygon_normal(points)
	neighbor_keys = []
	for neighbor_id in graph.adjacency[graph.source_to_face_id[source_vertex]]:
		for candidate, face_id in graph.source_to_face_id.items():
			if face_id == neighbor_id:
				neighbor_keys.append(candidate)
				break
	neighbor_keys.sort(key=repr)
	values = []
	for neighbor_key in neighbor_keys:
		neighbor_points = face_points_for_source(graph, neighbor_key, incident_triangles)
		neighbor_normal = polygon_normal(neighbor_points)
		values.append(angle_degrees(face_normal, neighbor_normal))
	return tuple(values)


#============================================
def round_sequence(values: tuple[float, ...], digits: int) -> tuple[float, ...]:
	"""Round a numeric sequence for deterministic reporting."""
	rounded = []
	for value in values:
		rounded.append(round(value, digits))
	return tuple(rounded)


#============================================
def representative_source_for_orbit(
	graph: goldberg_brick.dual.GoldbergGraph,
	orbit: goldberg_brick.orbits.HexagonOrbit,
) -> goldberg_brick.triangulation.VertexKey:
	"""Return deterministic source vertex for an orbit representative."""
	first_face_id = orbit.faces[0]
	for source_vertex, face_id in graph.source_to_face_id.items():
		if face_id == first_face_id:
			return source_vertex
	raise ValueError(f"missing source vertex for face: {first_face_id}")


#============================================
def compute_hexagon_orbit_geometries(
	graph: goldberg_brick.dual.GoldbergGraph,
	hexagon_orbits: tuple[goldberg_brick.orbits.HexagonOrbit, ...],
) -> dict[str, HexagonGeometry]:
	"""Compute measured geometry for each hexagon orbit representative."""
	incident_triangles = build_incident_triangles(graph.mesh)
	geometries = {}
	for orbit in hexagon_orbits:
		source_vertex = representative_source_for_orbit(graph, orbit)
		points = face_points_for_source(graph, source_vertex, incident_triangles)
		if len(points) != 6:
			raise ValueError(f"hexagon representative does not have 6 vertices: {orbit.orbit_id}")
		side_sequence = round_sequence(side_lengths(points), 6)
		angle_sequence = round_sequence(internal_angles(points), 3)
		planarity = round(planarity_error(points), 9)
		dihedral_sequence = round_sequence(
			dihedral_angles(graph, source_vertex, points, incident_triangles),
			3,
		)
		geometries[orbit.orbit_id] = HexagonGeometry(
			orbit_id=orbit.orbit_id,
			side_length_sequence=side_sequence,
			angle_sequence=angle_sequence,
			planarity_error=planarity,
			dihedral_angle_sequence=dihedral_sequence,
		)
	return geometries


#============================================
def mean(values: tuple[float, ...]) -> float:
	"""Return the arithmetic mean of a numeric sequence."""
	value = sum(values) / len(values)
	return value


#============================================
def sequence_spread(values: tuple[float, ...]) -> float:
	"""Return max minus min for a numeric sequence."""
	value = max(values) - min(values)
	return value


#============================================
def side_length_spread_percent(values: tuple[float, ...]) -> float:
	"""Return side length spread as a percent of mean side length."""
	value = 100.0 * sequence_spread(values) / mean(values)
	return value


#============================================
def max_angle_deviation(values: tuple[float, ...]) -> float:
	"""Return maximum absolute deviation from 120 degrees."""
	deviations = []
	for value in values:
		deviations.append(abs(value - 120.0))
	result = max(deviations)
	return result


#============================================
def pattern_letters(values: tuple[float, ...], tolerance: float) -> str:
	"""Return first-seen letter clusters for a six-value sequence."""
	clusters: list[float] = []
	letters = []
	for value in values:
		matched_index = -1
		for index, center in enumerate(clusters):
			if abs(value - center) <= tolerance:
				matched_index = index
				break
		if matched_index == -1:
			clusters.append(value)
			matched_index = len(clusters) - 1
		letters.append(chr(ord("a") + matched_index))
	pattern = "".join(letters)
	return pattern


#============================================
def pattern_rotations(pattern: str) -> list[str]:
	"""Return all cyclic rotations of a pattern string."""
	rotations = []
	for index in range(len(pattern)):
		rotations.append(pattern[index:] + pattern[:index])
	return rotations


#============================================
def canonical_pattern(pattern: str) -> str:
	"""Return the lexicographically smallest cyclic rotation."""
	canonical = min(pattern_rotations(pattern))
	return canonical


#============================================
def canonical_unoriented_pattern(pattern: str) -> str:
	"""Return the smallest cyclic pattern across both orientations."""
	reversed_pattern = "".join(reversed(pattern))
	all_patterns = pattern_rotations(pattern)
	all_patterns.extend(pattern_rotations(reversed_pattern))
	canonical = min(all_patterns)
	return canonical


#============================================
def classify_planarity(planarity_error: float) -> str:
	"""Classify planarity error into builder-facing status."""
	if planarity_error <= 0.0001:
		status = "planar"
	elif planarity_error <= 0.0004:
		status = "slightly warped"
	else:
		status = "warped"
	return status


#============================================
def classify_warp_mode(planarity_status: str, angle_pattern: str) -> str:
	"""Classify broad warp mode from planarity and angle pattern."""
	if planarity_status == "planar":
		mode = "nearly planar"
	elif angle_pattern == "abbabb":
		mode = "boat-like"
	elif angle_pattern == "ababab":
		mode = "chair-like"
	elif planarity_status == "slightly warped":
		mode = "low asymmetric warp"
	else:
		mode = "asymmetric warp"
	return mode


#============================================
def orientation_label(h_index: int, k_index: int) -> str:
	"""Return explicit orientation handling for an orbit pattern."""
	if k_index == 0 or h_index == k_index:
		label = "achiral"
	else:
		label = f"GP({h_index},{k_index}); mirror GP({k_index},{h_index})"
	return label


#============================================
def classify_difficulty(
	side_spread: float,
	angle_deviation: float,
	dihedral_spread: float,
	planarity_status: str,
) -> str:
	"""Classify builder difficulty from measured geometry."""
	if (
		side_spread >= 12.0
		or angle_deviation >= 5.0
		or dihedral_spread >= 3.0
		or planarity_status == "warped"
	):
		difficulty = "hard"
	elif side_spread >= 6.0 or angle_deviation >= 2.5 or dihedral_spread >= 1.5:
		difficulty = "medium"
	else:
		difficulty = "easy"
	return difficulty


#============================================
def describe_shape(angle_pattern: str, side_pattern: str, difficulty: str) -> str:
	"""Build a compact shape summary."""
	if angle_pattern == "aaaaaa" and side_pattern == "aaaaaa":
		summary = "regular-like repeated pattern"
	elif angle_pattern[:3] == angle_pattern[3:] and side_pattern[:3] == side_pattern[3:]:
		summary = "repeating 3-position pattern"
	elif difficulty == "hard":
		summary = "high distortion pattern"
	elif difficulty == "medium":
		summary = "moderate asymmetric pattern"
	else:
		summary = "mild asymmetric pattern"
	return summary


#============================================
def suggested_use(difficulty: str, warp_mode: str) -> str:
	"""Suggest a cautious builder use from classification."""
	if difficulty == "easy":
		use = "likely reusable rigid panel"
	elif difficulty == "medium":
		if "warp" in warp_mode:
			use = "test hinge relief"
		else:
			use = "test segmented panel"
	else:
		use = "custom panel likely needed"
	return use


#============================================
def reuse_group(difficulty: str) -> str:
	"""Return coarse reuse group label."""
	if difficulty == "easy":
		group = "likely reusable together"
	elif difficulty == "medium":
		group = "needs testing"
	else:
		group = "custom / high distortion"
	return group


#============================================
def compute_builder_summaries(
	graph: goldberg_brick.dual.GoldbergGraph,
	hexagon_geometries: dict[str, HexagonGeometry],
) -> dict[str, BuilderSummary]:
	"""Compute builder-facing summaries from measured geometry."""
	summaries = {}
	index_data = graph.mesh.index_data
	orientation = orientation_label(index_data.h, index_data.k)
	for orbit_id, geometry in hexagon_geometries.items():
		side_spread = round(side_length_spread_percent(geometry.side_length_sequence), 2)
		angle_deviation = round(max_angle_deviation(geometry.angle_sequence), 2)
		dihedral = round(sequence_spread(geometry.dihedral_angle_sequence), 2)
		planarity = classify_planarity(geometry.planarity_error)
		angle_raw = pattern_letters(geometry.angle_sequence, 0.25)
		angle_pattern = canonical_pattern(angle_raw)
		angle_pattern_unoriented = canonical_unoriented_pattern(angle_raw)
		mean_side = mean(geometry.side_length_sequence)
		side_raw = pattern_letters(geometry.side_length_sequence, mean_side * 0.015)
		side_pattern = canonical_pattern(side_raw)
		side_pattern_unoriented = canonical_unoriented_pattern(side_raw)
		dihedral_raw = pattern_letters(geometry.dihedral_angle_sequence, 0.25)
		dihedral_pattern = canonical_pattern(dihedral_raw)
		dihedral_pattern_unoriented = canonical_unoriented_pattern(dihedral_raw)
		warp_mode = classify_warp_mode(planarity, angle_pattern)
		difficulty = classify_difficulty(side_spread, angle_deviation, dihedral, planarity)
		summaries[orbit_id] = BuilderSummary(
			orbit_id=orbit_id,
			angle_pattern=angle_pattern,
			angle_pattern_unoriented=angle_pattern_unoriented,
			side_pattern=side_pattern,
			side_pattern_unoriented=side_pattern_unoriented,
			dihedral_pattern=dihedral_pattern,
			dihedral_pattern_unoriented=dihedral_pattern_unoriented,
			warp_mode=warp_mode,
			orientation=orientation,
			difficulty=difficulty,
			shape_summary=describe_shape(angle_pattern, side_pattern, difficulty),
			max_angle_deviation=angle_deviation,
			side_length_spread_percent=side_spread,
			dihedral_spread=dihedral,
			planarity_status=planarity,
			suggested_use=suggested_use(difficulty, warp_mode),
			reuse_group=reuse_group(difficulty),
		)
	return summaries
