import pytest

import goldberg_brick.indices


#============================================
def test_validate_indices_rejects_invalid_values() -> None:
	"""Reject negative indices and the zero-zero pair."""
	with pytest.raises(ValueError):
		goldberg_brick.indices.build_indices(-1, 0)
	with pytest.raises(ValueError):
		goldberg_brick.indices.build_indices(0, -1)
	with pytest.raises(ValueError):
		goldberg_brick.indices.build_indices(0, 0)


#============================================
def test_t_number_and_classification() -> None:
	"""Calculate T and class labels for representative indices."""
	class_i = goldberg_brick.indices.build_indices(4, 0)
	class_ii = goldberg_brick.indices.build_indices(2, 2)
	class_iii = goldberg_brick.indices.build_indices(4, 2)

	assert class_i.t_number == 16
	assert class_i.goldberg_class == "I"
	assert class_ii.t_number == 12
	assert class_ii.goldberg_class == "II"
	assert class_iii.t_number == 28
	assert class_iii.goldberg_class == "III"


#============================================
def test_expected_counts_for_known_cases() -> None:
	"""Calculate expected counts for known Goldberg cases."""
	cases = [
		(1, 0, 1, 12, 0, 12),
		(1, 1, 3, 12, 20, 32),
		(4, 2, 28, 12, 270, 282),
	]
	for h_index, k_index, t_number, pentagons, hexagons, total_faces in cases:
		index_data = goldberg_brick.indices.build_indices(h_index, k_index)
		assert index_data.t_number == t_number
		assert index_data.pentagons == pentagons
		assert index_data.hexagons == hexagons
		assert index_data.goldberg_faces == total_faces
		assert index_data.geodesic_vertices == total_faces
		assert index_data.geodesic_edges == 30 * t_number
		assert index_data.geodesic_faces == 20 * t_number
