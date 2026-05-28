"""Schein-Gayed equilateral polyhedron solver for Goldberg indices."""

import math
import warnings

import goldberg_brick.dual
import goldberg_brick.geometry
import goldberg_brick.icosahedron
import goldberg_brick.triangulation

#============================================

GoldbergVertexId = str
RotationIndex = int
Point3D = tuple[float, float, float]

_SOLVED: dict[tuple[int, int], dict[GoldbergVertexId, Point3D]] = {}

class ConvergenceError(Exception):
	"""Raised when solver convergence criteria are not met."""
	pass


#============================================
def make_vertex_id(triangle_index: int) -> GoldbergVertexId:
	"""Create ID for Goldberg vertex from geodesic triangle index."""
	return f"V{triangle_index:04d}"


#============================================
def build_polyhedron_edges(
	mesh: goldberg_brick.triangulation.GeodesicMesh,
) -> tuple[tuple[GoldbergVertexId, GoldbergVertexId], ...]:
	"""Build polyhedron edges from geodesic mesh."""
	edges = set()
	triangle_list = list(mesh.faces)

	for first_idx in range(len(triangle_list)):
		first_triangle = triangle_list[first_idx]
		for second_idx in range(first_idx + 1, len(triangle_list)):
			second_triangle = triangle_list[second_idx]
			shared = set(first_triangle) & set(second_triangle)
			if len(shared) == 2:
				v1_id = make_vertex_id(first_idx)
				v2_id = make_vertex_id(second_idx)
				edges.add(tuple(sorted([v1_id, v2_id])))

	return tuple(sorted(edges))


#============================================
def build_rotation_orbits(
	mesh: goldberg_brick.triangulation.GeodesicMesh,
) -> dict[GoldbergVertexId, list[tuple[GoldbergVertexId, RotationIndex]]]:
	"""Build rotation orbits: maps rep vertex -> [(member, rot_idx), ...]."""
	rotations = mesh.icosahedron.rotations
	t_number = mesh.index_data.t_number
	triangle_count = len(mesh.faces)

	# Pre-compute rotated triangle indices
	rot_maps = []
	for rotation_perm in rotations:
		tri_map = {}
		for tri_idx, triangle in enumerate(mesh.faces):
			# Rotate triangle vertices
			rotated_vertices = tuple(
				goldberg_brick.triangulation.rotate_vertex_key(v, rotation_perm, t_number)
				for v in triangle
			)
			# Find rotated triangle index
			rotated_sorted = tuple(sorted(rotated_vertices, key=repr))
			for search_idx, search_tri in enumerate(mesh.faces):
				if tuple(sorted(search_tri, key=repr)) == rotated_sorted:
					tri_map[tri_idx] = search_idx
					break
		rot_maps.append(tri_map)

	# Build orbits
	visited = set()
	orbit_map = {}

	for start_idx in range(triangle_count):
		if start_idx in visited:
			continue

		rep_id = make_vertex_id(start_idx)
		orbit = []

		for rot_idx in range(len(rotations)):
			rotated_idx = rot_maps[rot_idx][start_idx]
			rotated_id = make_vertex_id(rotated_idx)
			orbit.append((rotated_id, rot_idx))
			visited.add(rotated_idx)

		orbit_map[rep_id] = orbit

	return orbit_map


#============================================
def build_rotation_matrix_from_perm(
	perm: dict[int, int],
	coords: dict[int, tuple[float, float, float]],
) -> tuple[tuple[float, float, float], ...]:
	"""Build 3x3 rotation matrix from vertex permutation."""
	source_face = (0, 1, 2)
	target_face = tuple(perm[v] for v in source_face)

	source_basis = goldberg_brick.icosahedron.face_basis(source_face, coords)
	target_basis = goldberg_brick.icosahedron.face_basis(target_face, coords)

	rotation = goldberg_brick.icosahedron.matrix_multiply(
		goldberg_brick.icosahedron.transpose(target_basis),
		source_basis,
	)

	return rotation


#============================================
def expand_from_reps(
	rep_positions: dict[GoldbergVertexId, Point3D],
	orbit_map: dict[GoldbergVertexId, list[tuple[GoldbergVertexId, RotationIndex]]],
	icosahedron: goldberg_brick.icosahedron.Icosahedron,
) -> dict[GoldbergVertexId, Point3D]:
	"""Expand representative positions to full vertex set via rotations."""
	full_positions = {}
	rotation_matrices = [
		build_rotation_matrix_from_perm(rot, icosahedron.coordinates)
		for rot in icosahedron.rotations
	]

	for rep_id, orbit in orbit_map.items():
		rep_pos = rep_positions[rep_id]

		for member_id, rot_idx in orbit:
			if rot_idx == 0:
				full_positions[member_id] = rep_pos
			else:
				rotated = goldberg_brick.icosahedron.matrix_vector(
					rotation_matrices[rot_idx],
					rep_pos,
				)
				full_positions[member_id] = rotated

	return full_positions


#============================================
def build_face_vertex_orderings(
	graph: goldberg_brick.dual.GoldbergGraph,
	mesh: goldberg_brick.triangulation.GeodesicMesh,
	incident_triangles: dict,
) -> dict:
	"""Build face_id -> tuple of ordered GoldbergVertexIds around that face.

	Each face corresponds to a geodesic source vertex; the face's polygon
	vertices are the polyhedron vertices (triangle indices) incident to it.
	"""
	face_orderings = {}
	# Build a quick lookup: triangle tuple -> tri_idx
	tri_to_idx = {tri: idx for idx, tri in enumerate(mesh.faces)}
	for face in graph.faces:
		source_vertex = face.source_vertex
		triangles = incident_triangles[source_vertex]
		ordered = goldberg_brick.geometry.order_triangles_around_vertex(
			mesh, source_vertex, triangles
		)
		ids = tuple(make_vertex_id(tri_to_idx[t]) for t in ordered)
		face_orderings[face.face_id] = ids
	return face_orderings


#============================================
def build_dad_edge_specs(
	edges: tuple[tuple[GoldbergVertexId, GoldbergVertexId], ...],
	graph: goldberg_brick.dual.GoldbergGraph,
	mesh: goldberg_brick.triangulation.GeodesicMesh,
	face_orderings: dict,
) -> tuple:
	"""Precompute per-edge DAD specification.

	For each polyhedron edge e=(v1,v2):
	  At each endpoint v in (v1,v2), e is bordered by two Goldberg faces
	  (faces A, B) and a third face (face C) is the remaining face at v.
	  Each polyhedron vertex (a geodesic triangle) has exactly 3 incident
	  faces: the 3 geodesic source vertices forming the triangle.

	Returns a tuple of dicts, one per edge, with:
	  v1, v2 (the endpoints)
	  for each endpoint: (face_A_id, prev_idx_A, idx_A, next_idx_A) where
	  prev/idx/next give positions within face_orderings to compute the
	  internal angle at v in that face. Same for face_B, face_C.
	"""
	# Map: GoldbergVertexId -> the 3 geodesic source vertices (triangle vertices)
	vid_to_sources = {}
	for tri_idx, tri in enumerate(mesh.faces):
		vid_to_sources[make_vertex_id(tri_idx)] = tri

	# Map: face_id -> (vertex_id -> position in ordering)
	face_pos = {}
	for fid, ordering in face_orderings.items():
		face_pos[fid] = {vid: i for i, vid in enumerate(ordering)}

	source_to_face_id = graph.source_to_face_id

	specs = []
	for v1, v2 in edges:
		# Two shared geodesic sources => the two faces of this edge.
		shared = set(vid_to_sources[v1]) & set(vid_to_sources[v2])
		if len(shared) != 2:
			raise ValueError(f"edge {v1}-{v2} has {len(shared)} shared sources")
		shared_list = list(shared)
		face_a_id = source_to_face_id[shared_list[0]]
		face_b_id = source_to_face_id[shared_list[1]]

		endpoint_specs = []
		for v in (v1, v2):
			# Three sources at v; two are shared (faces A,B), one is the "opposite" (face C)
			tri_sources = set(vid_to_sources[v])
			opp = tri_sources - shared
			if len(opp) != 1:
				raise ValueError(f"vertex {v} edge {v1}-{v2}: opposite count {len(opp)}")
			face_c_id = source_to_face_id[next(iter(opp))]

			per_face = []
			for fid in (face_a_id, face_b_id, face_c_id):
				ordering = face_orderings[fid]
				n = len(ordering)
				pos = face_pos[fid][v]
				prev_pos = (pos - 1) % n
				next_pos = (pos + 1) % n
				per_face.append((
					ordering[prev_pos],
					ordering[pos],
					ordering[next_pos],
				))
			endpoint_specs.append(per_face)

		specs.append((v1, v2, endpoint_specs))
	return tuple(specs)


#============================================
def _face_angle_cos(positions, prev_id, vid, next_id):
	"""Return cos(internal angle at vid) given prev/next neighbors in the face.

	cos = dot(u_prev, u_next) where u_prev = (prev - vid)/|...|, u_next = same.
	"""
	p = positions[vid]
	a = positions[prev_id]
	b = positions[next_id]
	ua = (a[0] - p[0], a[1] - p[1], a[2] - p[2])
	ub = (b[0] - p[0], b[1] - p[1], b[2] - p[2])
	la = math.sqrt(ua[0]*ua[0] + ua[1]*ua[1] + ua[2]*ua[2])
	lb = math.sqrt(ub[0]*ub[0] + ub[1]*ub[1] + ub[2]*ub[2])
	if la < 1e-15 or lb < 1e-15:
		return 0.0
	cos_v = (ua[0]*ub[0] + ua[1]*ub[1] + ua[2]*ub[2]) / (la * lb)
	if cos_v > 1.0:
		cos_v = 1.0
	elif cos_v < -1.0:
		cos_v = -1.0
	return cos_v


#============================================
def _cos_dihedral_at_endpoint(positions, per_face):
	"""Compute cos(dihedral) of an edge at one endpoint via Schein-Gayed Eq. 1.

	per_face: 3 tuples of (prev_id, vid, next_id) for faces A, B, C at v.
	A, B share the edge; C is the opposite face. Dihedral at the edge equals
	the spherical-triangle angle opposite side c (face C's angle at v).
	"""
	c_a = _face_angle_cos(positions, *per_face[0])
	c_b = _face_angle_cos(positions, *per_face[1])
	c_c = _face_angle_cos(positions, *per_face[2])
	# sin^2 = 1 - cos^2; clamp to avoid tiny negatives from FP roundoff.
	sa2 = 1.0 - c_a * c_a
	sb2 = 1.0 - c_b * c_b
	if sa2 < 1e-30:
		sa2 = 1e-30
	if sb2 < 1e-30:
		sb2 = 1e-30
	sa = math.sqrt(sa2)
	sb = math.sqrt(sb2)
	cos_d = (c_c - c_a * c_b) / (sa * sb)
	return cos_d


#============================================
def compute_residuals(
	positions: dict[GoldbergVertexId, Point3D],
	edges: tuple[tuple[GoldbergVertexId, GoldbergVertexId], ...],
	graph: goldberg_brick.dual.GoldbergGraph,
	mesh: goldberg_brick.triangulation.GeodesicMesh,
	incident_triangles: dict,
	include_planarity: bool = True,
	dad_specs: tuple = (),
	dad_weight: float = 0.0,
	face_orderings: dict | None = None,
) -> list[float]:
	"""Compute edge equilaterality, planarity, and optional DAD residuals."""
	residuals = []

	# Edge equilaterality residuals
	for v1_id, v2_id in edges:
		p1 = positions[v1_id]
		p2 = positions[v2_id]
		delta = goldberg_brick.geometry.subtract(p2, p1)
		edge_length = goldberg_brick.geometry.length(delta)
		residuals.append(edge_length - 1.0)

	# DAD nulling residuals (Schein-Gayed Eq. 1, cos form, symbolic from face angles)
	if dad_specs and dad_weight > 0.0:
		for v1, v2, endpoint_specs in dad_specs:
			cos_d1 = _cos_dihedral_at_endpoint(positions, endpoint_specs[0])
			cos_d2 = _cos_dihedral_at_endpoint(positions, endpoint_specs[1])
			residuals.append(dad_weight * (cos_d1 - cos_d2))

	if not include_planarity:
		return residuals

	# Planarity residuals for pentagons and hexagons. When face_orderings is
	# supplied, skip the expensive O(F^2) per-call rediscovery of vertex IDs.
	for face in graph.faces:
		if face_orderings is not None:
			vertex_ids = list(face_orderings[face.face_id])
		else:
			source_vertex = face.source_vertex
			triangles = incident_triangles[source_vertex]
			ordered_triangles = goldberg_brick.geometry.order_triangles_around_vertex(
				mesh, source_vertex, triangles
			)
			vertex_ids = []
			for tri_idx, triangle in enumerate(mesh.faces):
				if triangle in ordered_triangles:
					vertex_ids.append(make_vertex_id(tri_idx))

		if face.face_type == "pentagon" and len(vertex_ids) == 5:
			points = [positions[v_id] for v_id in vertex_ids]
			plane_normal = goldberg_brick.geometry.polygon_normal(tuple(points[:3]))
			for idx in [3, 4]:
				v1 = goldberg_brick.geometry.subtract(points[1], points[0])
				v2 = goldberg_brick.geometry.subtract(points[2], points[0])
				v3 = goldberg_brick.geometry.subtract(points[idx], points[0])
				signed_vol = goldberg_brick.geometry.dot(v3, goldberg_brick.geometry.cross(v1, v2)) / 6.0
				residuals.append(signed_vol)

		elif face.face_type == "hexagon" and len(vertex_ids) == 6:
			points = tuple(positions[v_id] for v_id in vertex_ids)
			plane_normal = goldberg_brick.geometry.polygon_normal(points)
			plane_point = goldberg_brick.geometry.polygon_centroid(points)

			for point in points:
				to_point = goldberg_brick.geometry.subtract(point, plane_point)
				distance = goldberg_brick.geometry.dot(to_point, plane_normal)
				residuals.append(distance)

	return residuals


#============================================
def positions_to_vector(positions: dict[GoldbergVertexId, Point3D]) -> list[float]:
	"""Flatten positions to vector."""
	vector = []
	for vertex_id in sorted(positions.keys()):
		vector.extend(positions[vertex_id])
	return vector


#============================================
def vector_to_positions(
	vector: list[float],
	vertex_ids: list[str],
) -> dict[GoldbergVertexId, Point3D]:
	"""Reconstruct positions from vector."""
	positions = {}
	for idx, vertex_id in enumerate(vertex_ids):
		positions[vertex_id] = (vector[3*idx], vector[3*idx+1], vector[3*idx+2])
	return positions


#============================================
def rescale_to_unit_edges(
	positions: dict[GoldbergVertexId, Point3D],
	edges: tuple[tuple[GoldbergVertexId, GoldbergVertexId], ...],
) -> dict[GoldbergVertexId, Point3D]:
	"""Rescale positions to mean edge length 1.0."""
	if not edges:
		return positions

	edge_lengths = []
	for v1_id, v2_id in edges:
		p1 = positions[v1_id]
		p2 = positions[v2_id]
		d = math.sqrt(sum((p1[i] - p2[i]) ** 2 for i in range(3)))
		edge_lengths.append(d)

	mean_length = sum(edge_lengths) / len(edge_lengths)
	scale = 1.0 / mean_length if mean_length > 1e-10 else 1.0

	return {v_id: (p[0]*scale, p[1]*scale, p[2]*scale) for v_id, p in positions.items()}


#============================================
def center_at_origin(
	positions: dict[GoldbergVertexId, Point3D],
) -> dict[GoldbergVertexId, Point3D]:
	"""Center positions at origin."""
	total = (0.0, 0.0, 0.0)
	for pos in positions.values():
		total = goldberg_brick.geometry.add(total, pos)

	centroid = (total[0]/len(positions), total[1]/len(positions), total[2]/len(positions))

	return {v_id: goldberg_brick.geometry.subtract(p, centroid) for v_id, p in positions.items()}


#============================================
def solve_schein_gayed_positions(
	h: int,
	k: int,
) -> dict[GoldbergVertexId, Point3D]:
	"""Solve for equilateral Goldberg polyhedron vertex positions.

	Thin wrapper around force_attempt_solve, retained for callers that
	prefer the descriptive name.

	Returns: dict[GoldbergVertexId, Point3D] with 20*T_number vertices.

	Raises ConvergenceError when Stage A (globally-equilateral) fails.
	"""
	return force_attempt_solve(h, k)


#============================================
def force_attempt_solve(
	h: int,
	k: int,
) -> dict[GoldbergVertexId, Point3D]:
	"""Run the Schein-Gayed equilateral solver without consulting the shortcut.

	Uses symmetry reduction (1 representative per rotation orbit, expanded via
	icosahedral rotations). Two-stage contract:

	  Stage A (REQUIRED): globally-equilateral only. Edge-length residuals are
	    driven to edge_stddev < 1e-7. Failure raises ConvergenceError.

	  Stage B (PREFERRED, soft): adds planarity + DAD residuals on top of
	    Stage A's result. If the LM iterate hits a degenerate intermediate
	    config (polygon_normal raises ValueError on zero-area), the solver
	    rolls back to the last good iterate from Stage A and returns it.
	    Non-planar hexagons are then labeled boat/chair/asymmetric by the
	    warp_mode classifier; the report still writes.

	Returns: dict[GoldbergVertexId, Point3D] with 20*T_number vertices.
	"""
	cache_key = (h, k)
	if cache_key in _SOLVED:
		return _SOLVED[cache_key]

	import scipy.optimize
	import time

	start_time = time.time()
	timeout_seconds = 30

	# Build geometry
	mesh = goldberg_brick.triangulation.build_geodesic_mesh(h, k)
	graph = goldberg_brick.dual.build_goldberg_graph(mesh)
	edges = build_polyhedron_edges(mesh)
	incident_triangles = goldberg_brick.geometry.build_incident_triangles(mesh)

	# Build DAD specifications (Schein-Gayed dihedral-angle-discrepancy nulling)
	face_orderings = build_face_vertex_orderings(graph, mesh, incident_triangles)
	dad_specs = build_dad_edge_specs(edges, graph, mesh, face_orderings)

	# Build orbits
	orbit_map = build_rotation_orbits(mesh)
	rep_ids = sorted(orbit_map.keys())

	# Initial guess: centroids, rescaled to match intended edge length, centered
	full_positions = {
		make_vertex_id(tri_idx): goldberg_brick.geometry._geodesic_triangle_centroid_on_sphere(mesh, tri)
		for tri_idx, tri in enumerate(mesh.faces)
	}
	# Note: centroid projection produces edges of varying length
	# Rescale so mean edge length is 1.0
	full_positions = rescale_to_unit_edges(full_positions, edges)
	# Center at origin to remove translation DOF
	full_positions = center_at_origin(full_positions)

	# Extract representative positions
	rep_positions = {rep_id: full_positions[rep_id] for rep_id in rep_ids}
	rep_vector = positions_to_vector(rep_positions)

	# Stage A: globally-equilateral only. Edge-length residuals are the entire
	# objective; no planarity, no DAD. This stage MUST converge -- the
	# validation gate below raises ConvergenceError if edge_stddev >= 1e-7.
	def residual_stage_a(vec):
		reps = vector_to_positions(vec, rep_ids)
		full = expand_from_reps(reps, orbit_map, mesh.icosahedron)
		return compute_residuals(
			full, edges, graph, mesh, incident_triangles,
			include_planarity=False,
		)

	result = scipy.optimize.least_squares(
		residual_stage_a,
		rep_vector,
		method="lm",
		ftol=1e-12,
		xtol=1e-12,
		gtol=1e-12,
		max_nfev=50000,
	)

	if time.time() - start_time > timeout_seconds:
		raise ConvergenceError(
			f"GP({h},{k}) stage A exceeded timeout ({timeout_seconds}s); "
			f"status={result.status} nfev={result.nfev} msg={result.message!r}"
		)

	stage_a_vector = result.x

	# Validate Stage A hard gate: globally-equilateral within 1e-7.
	stage_a_reps = vector_to_positions(stage_a_vector, rep_ids)
	stage_a_full = expand_from_reps(stage_a_reps, orbit_map, mesh.icosahedron)
	edge_residuals_a = compute_residuals(
		stage_a_full, edges, graph, mesh, incident_triangles,
		include_planarity=False,
	)
	edge_lengths_a = [1.0 + r for r in edge_residuals_a]
	mean_edge_a = sum(edge_lengths_a) / len(edge_lengths_a)
	edge_stddev_a = math.sqrt(
		sum((e - mean_edge_a) ** 2 for e in edge_lengths_a) / len(edge_lengths_a)
	)
	if edge_stddev_a >= 1e-7:
		raise ConvergenceError(
			f"GP({h},{k}) Stage A (globally-equilateral) failed: "
			f"edge_stddev={edge_stddev_a:.2e}; "
			f"status={result.status} nfev={result.nfev} msg={result.message!r}"
		)

	# Stage B (preferred, soft): refine toward planarity + DAD nulling.
	# Start from Stage A's converged equilateral iterate. If the LM solver
	# wanders into a degenerate intermediate config (polygon_normal raises
	# ValueError on a zero-area face), roll back to Stage A and ship that.
	# The warp_mode classifier in goldberg_brick.geometry will then label
	# the hexagons as planar/boat/chair/asymmetric from signed displacements.
	def residual_stage_b(vec):
		reps = vector_to_positions(vec, rep_ids)
		full = expand_from_reps(reps, orbit_map, mesh.icosahedron)
		return compute_residuals(
			full, edges, graph, mesh, incident_triangles,
			include_planarity=True,
			dad_specs=dad_specs,
			dad_weight=1.0,
			face_orderings=face_orderings,
		)

	# Narrow try/except (numerical solver boundary, per PYTHON_STYLE.md):
	# polygon_normal raises ValueError on zero-length normal; rolling back to
	# the Stage A iterate keeps the equilateral guarantee.
	final_vector = stage_a_vector
	# Skip Stage B if Stage A already consumed the timeout budget.
	remaining = timeout_seconds - (time.time() - start_time)
	if remaining <= 0:
		result_b = None
	else:
		# Estimate per-eval cost so we can cap max_nfev to a wall-clock
		# budget. scipy LM has no per-iteration callback; max_nfev is the
		# only knob. Stage B is soft refinement -- if it cannot planarize
		# within the budget, the warp_mode classifier labels the result.
		probe_t = time.time()
		try:
			residual_stage_b(stage_a_vector)
		except ValueError:
			result_b = None
		else:
			per_eval = max(time.time() - probe_t, 1e-3)
			# Floor per_eval to a realistic minimum (first call may be
			# cache-warm; real Jacobian evals are slower).
			per_eval = max(per_eval, 0.01)
			max_nfev = max(50, min(2000, int(remaining / per_eval)))
			try:
				result_b = scipy.optimize.least_squares(
					residual_stage_b, stage_a_vector, method="lm",
					ftol=1e-12, xtol=1e-12, gtol=1e-12, max_nfev=max_nfev,
				)
			except ValueError:
				result_b = None
	if result_b is not None and time.time() - start_time <= timeout_seconds:
		# Only adopt Stage B if it preserved equilaterality. Otherwise keep A.
		candidate_reps = vector_to_positions(result_b.x, rep_ids)
		candidate_full = expand_from_reps(candidate_reps, orbit_map, mesh.icosahedron)
		try:
			candidate_residuals = compute_residuals(
				candidate_full, edges, graph, mesh, incident_triangles,
				include_planarity=False,
			)
			cand_edge_lengths = [1.0 + r for r in candidate_residuals]
			cand_mean = sum(cand_edge_lengths) / len(cand_edge_lengths)
			cand_stddev = math.sqrt(
				sum((e - cand_mean) ** 2 for e in cand_edge_lengths) / len(cand_edge_lengths)
			)
			if cand_stddev < 1e-7:
				final_vector = result_b.x
		except ValueError:
			pass

	final_reps = vector_to_positions(final_vector, rep_ids)
	solved_positions = expand_from_reps(final_reps, orbit_map, mesh.icosahedron)

	# Final telemetry: equilaterality is the hard contract. Planarity is
	# informational and may be unreachable (Stage B is soft). Compute only
	# the edge residuals here; per-orbit planarity is reported via
	# warp_mode in goldberg_brick.geometry.
	edge_residuals = compute_residuals(
		solved_positions, edges, graph, mesh, incident_triangles,
		include_planarity=False,
	)
	edge_lengths = [1.0 + r for r in edge_residuals]
	mean_edge = sum(edge_lengths) / len(edge_lengths)
	edge_stddev = math.sqrt(
		sum((e - mean_edge) ** 2 for e in edge_lengths) / len(edge_lengths)
	)

	if edge_stddev >= 1e-7:
		raise ConvergenceError(
			f"GP({h},{k}) post-stage-B equilaterality lost: "
			f"edge_stddev={edge_stddev:.2e}"
		)

	if edge_stddev >= 1e-9:
		warnings.warn(
			f"GP({h},{k}) dev target missed: edge_stddev={edge_stddev:.2e}",
			RuntimeWarning,
		)

	_SOLVED[cache_key] = solved_positions
	return solved_positions
