"""Markdown report rendering for graph-only Goldberg results."""

import goldberg_brick.dual
import goldberg_brick.geometry
import goldberg_brick.orbits


#============================================
def validation_status(graph: goldberg_brick.dual.GoldbergGraph) -> str:
	"""Return PASS when observed counts match expected counts."""
	index_data = graph.mesh.index_data
	pentagons = goldberg_brick.dual.count_faces(graph, "pentagon")
	hexagons = goldberg_brick.dual.count_faces(graph, "hexagon")
	if (
		len(graph.faces) == index_data.goldberg_faces
		and pentagons == index_data.pentagons
		and hexagons == index_data.hexagons
	):
		status = "PASS"
	else:
		status = "FAIL"
	return status


#============================================
def render_markdown_report(
	graph: goldberg_brick.dual.GoldbergGraph,
	hexagon_orbits: tuple[goldberg_brick.orbits.HexagonOrbit, ...],
	hexagon_geometries: dict[str, goldberg_brick.geometry.HexagonGeometry],
	model: str,
) -> str:
	"""Render a deterministic Markdown report."""
	index_data = graph.mesh.index_data
	pentagons = goldberg_brick.dual.count_faces(graph, "pentagon")
	hexagons = goldberg_brick.dual.count_faces(graph, "hexagon")
	builder_summaries = goldberg_brick.geometry.compute_builder_summaries(
		graph,
		hexagon_geometries,
	)
	lines = [
		f"# Goldberg Brick Report: GP({index_data.h},{index_data.k})",
		"",
		"## Summary",
		"",
		f"h: {index_data.h}",
		f"k: {index_data.k}",
		f"T: {index_data.t_number}",
		f"class: {index_data.goldberg_class}",
		f"model: {model}",
		f"pentagons: {pentagons}",
		f"hexagons: {hexagons}",
		f"total faces: {len(graph.faces)}",
		f"face orbits: {len(hexagon_orbits) + 1 if pentagons else len(hexagon_orbits)}",
		f"hexagon orbits: {len(hexagon_orbits)}",
		"",
		"## Validation",
		"",
		f"expected total faces: {index_data.goldberg_faces}",
		f"observed total faces: {len(graph.faces)}",
		f"expected pentagons: {index_data.pentagons}",
		f"observed pentagons: {pentagons}",
		f"expected hexagons: {index_data.hexagons}",
		f"observed hexagons: {hexagons}",
		f"status: {validation_status(graph)}",
		"",
		"## Builder pattern summary",
		"",
		"| orbit | count | angle pattern | side pattern | warp mode | orientation | difficulty | shape summary | max angle deviation | side spread | planarity | dihedral spread | suggested use |",
		"|---|---:|---|---|---|---|---|---|---:|---:|---|---:|---|",
	]
	for orbit in hexagon_orbits:
		summary = builder_summaries[orbit.orbit_id]
		lines.append(
			f"| {orbit.orbit_id} | {orbit.face_count} | "
			f"{summary.angle_pattern_code} | {summary.side_pattern_code} | "
			f"{summary.warp_mode} | {summary.orientation} | "
			f"{summary.difficulty} | {summary.shape_summary} | "
			f"{summary.max_angle_deviation:.2f} deg | "
			f"{summary.side_length_spread_percent:.2f}% | {summary.planarity_status} | "
			f"{summary.dihedral_spread:.2f} deg | {summary.suggested_use} |"
		)
	lines.extend([
		"",
		"## Reuse groups",
		"",
	])
	for group_name in ("likely reusable together", "needs testing", "custom / high distortion"):
		group_orbits = []
		for orbit in hexagon_orbits:
			summary = builder_summaries[orbit.orbit_id]
			if summary.reuse_group == group_name:
				group_orbits.append(orbit.orbit_id)
		if group_orbits:
			group_text = ", ".join(group_orbits)
		else:
			group_text = "none"
		lines.append(f"- {group_name}: {group_text}")
	lines.extend([
		"",
		"## Raw hexagon geometry",
		"",
		"| orbit_id | face_count | mirror_orbit | side_length_sequence | angle_sequence | planarity_error | dihedral_angle_sequence | deformation_mode | brick_strategy |",
		"|---|---:|---|---|---|---:|---|---|---|",
	])
	for orbit in hexagon_orbits:
		geometry = hexagon_geometries[orbit.orbit_id]
		lines.append(
			f"| {orbit.orbit_id} | {orbit.face_count} | {orbit.mirror_orbit} | "
			f"{format_sequence(geometry.side_length_sequence)} | "
			f"{format_sequence(geometry.angle_sequence)} | "
			f"{geometry.planarity_error:.9f} | "
			f"{format_sequence(geometry.dihedral_angle_sequence)} | NA | NA |"
		)
	text = "\n".join(lines)
	text += "\n"
	return text


#============================================
def write_markdown_report(
	output_path: str,
	graph: goldberg_brick.dual.GoldbergGraph,
	hexagon_orbits: tuple[goldberg_brick.orbits.HexagonOrbit, ...],
	hexagon_geometries: dict[str, goldberg_brick.geometry.HexagonGeometry],
	model: str,
) -> None:
	"""Write a Markdown report to disk."""
	text = render_markdown_report(graph, hexagon_orbits, hexagon_geometries, model)
	with open(output_path, "w", encoding="utf-8") as handle:
		handle.write(text)


#============================================
def format_sequence(values: tuple[float, ...]) -> str:
	"""Format a numeric sequence for one Markdown table cell."""
	text_values = []
	for value in values:
		text_values.append(f"{value:g}")
	text = "[" + ", ".join(text_values) + "]"
	return text
