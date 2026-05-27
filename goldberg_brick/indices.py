"""Goldberg index validation and count formulas."""

import dataclasses


@dataclasses.dataclass(frozen=True)
class GoldbergIndices:
	"""Validated Goldberg indices and derived values."""

	h: int
	k: int
	t_number: int
	goldberg_class: str
	geodesic_vertices: int
	geodesic_edges: int
	geodesic_faces: int
	goldberg_faces: int
	goldberg_edges: int
	goldberg_vertices: int
	pentagons: int
	hexagons: int


#============================================
def validate_indices(h: int, k: int) -> None:
	"""Validate Goldberg index values.

	Args:
		h: First Goldberg index.
		k: Second Goldberg index.
	"""
	if h < 0:
		raise ValueError("h must be >= 0")
	if k < 0:
		raise ValueError("k must be >= 0")
	if h == 0 and k == 0:
		raise ValueError("h and k cannot both be zero")


#============================================
def calculate_t_number(h: int, k: int) -> int:
	"""Calculate the triangulation number.

	Args:
		h: First Goldberg index.
		k: Second Goldberg index.

	Returns:
		int: Triangulation number.
	"""
	t_number = h * h + h * k + k * k
	return t_number


#============================================
def classify_indices(h: int, k: int) -> str:
	"""Classify Goldberg indices as class I, II, or III.

	Args:
		h: First Goldberg index.
		k: Second Goldberg index.

	Returns:
		str: Roman class label.
	"""
	if k == 0:
		goldberg_class = "I"
	elif h == k:
		goldberg_class = "II"
	else:
		goldberg_class = "III"
	return goldberg_class


#============================================
def build_indices(h: int, k: int) -> GoldbergIndices:
	"""Build validated Goldberg index metadata.

	Args:
		h: First Goldberg index.
		k: Second Goldberg index.

	Returns:
		GoldbergIndices: Derived index metadata and expected counts.
	"""
	validate_indices(h, k)
	t_number = calculate_t_number(h, k)
	goldberg_class = classify_indices(h, k)
	geodesic_vertices = 10 * t_number + 2
	geodesic_edges = 30 * t_number
	geodesic_faces = 20 * t_number
	pentagons = 12
	hexagons = 10 * t_number - 10
	result = GoldbergIndices(
		h=h,
		k=k,
		t_number=t_number,
		goldberg_class=goldberg_class,
		geodesic_vertices=geodesic_vertices,
		geodesic_edges=geodesic_edges,
		geodesic_faces=geodesic_faces,
		goldberg_faces=geodesic_vertices,
		goldberg_edges=geodesic_edges,
		goldberg_vertices=geodesic_faces,
		pentagons=pentagons,
		hexagons=hexagons,
	)
	return result
