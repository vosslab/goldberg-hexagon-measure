"""Markdown report rendering for Goldberg polyhedron reports."""

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
	units: str,
	scale: float,
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
	]
	lines.extend([
		f"h: {index_data.h}",
		f"k: {index_data.k}",
		f"T: {index_data.t_number}",
		f"class: {index_data.goldberg_class}",
		f"units: {units}",
		f"scale: {scale}",
		"model: equilateral-goldberg",
		"metric: chord",
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
		"| orbit | count | angle pattern | side pattern | dihedral pattern | warp mode | orientation | difficulty | shape summary | max angle deviation | side spread | planarity | dihedral spread | suggested use |",
		"|---|---:|---|---|---|---|---|---|---|---:|---:|---|---:|---|",
	])
	for orbit in hexagon_orbits:
		summary = builder_summaries[orbit.orbit_id]
		lines.append(
			f"| {orbit.orbit_id} | {orbit.face_count} | "
			f"{summary.angle_pattern} | {summary.side_pattern} | "
			f"{summary.dihedral_pattern} | {summary.warp_mode} | {summary.orientation} | "
			f"{summary.difficulty} | {summary.shape_summary} | "
			f"{summary.max_angle_deviation:.2f} deg | "
			f"{summary.side_length_spread_percent:.2f}% | {summary.planarity_status} | "
			f"{summary.dihedral_spread:.2f} deg | {summary.suggested_use} |"
		)
	mirror_notes = build_mirror_notes(hexagon_orbits, builder_summaries)
	if mirror_notes:
		lines.extend([
			"",
			"Mirror pattern notes:",
		])
		lines.extend(mirror_notes)
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
		f"| orbit_id | face_count | mirror_orbit | angle_pattern | side_pattern | dihedral_pattern | side_length_sequence ({units}) | angle_sequence | planarity_error ({units}) | dihedral_angle_sequence | deformation_mode | brick_strategy |",
		"|---|---:|---|---|---|---|---|---|---:|---|---|---|",
	])
	for orbit in hexagon_orbits:
		geometry = hexagon_geometries[orbit.orbit_id]
		summary = builder_summaries[orbit.orbit_id]
		scaled_planarity_error = geometry.planarity_error * scale
		# Raw absolute spread (max - min) in unit-edge space for the side
		# sequence; brick_strategy uses an absolute threshold, not a percent.
		raw_side_spread = goldberg_brick.geometry.sequence_spread(
			geometry.side_length_sequence
		)
		distinct_angle_count = len(set(summary.angle_pattern))
		brick_strategy = goldberg_brick.geometry.classify_brick_strategy(
			geometry, raw_side_spread, distinct_angle_count
		)
		deformation_mode = geometry.warp_mode
		lines.append(
			f"| {orbit.orbit_id} | {orbit.face_count} | {orbit.mirror_orbit} | "
			f"{summary.angle_pattern} | {summary.side_pattern} | {summary.dihedral_pattern} | "
			f"{format_sequence_scaled(geometry.side_length_sequence, scale)} | "
			f"{format_sequence(geometry.angle_sequence)} | "
			f"{scaled_planarity_error:.9f} | "
			f"{format_sequence(geometry.dihedral_angle_sequence)} | "
			f"{deformation_mode} | {brick_strategy} |"
		)
	# Per-orbit connector counts section.
	lines.extend(build_connector_counts_section(
		hexagon_orbits, hexagon_geometries, units, scale
	))
	text = "\n".join(lines)
	text += "\n"
	return text


#============================================
def write_markdown_report(
	output_path: str,
	graph: goldberg_brick.dual.GoldbergGraph,
	hexagon_orbits: tuple[goldberg_brick.orbits.HexagonOrbit, ...],
	hexagon_geometries: dict[str, goldberg_brick.geometry.HexagonGeometry],
	units: str,
	scale: float,
) -> None:
	"""Write a Markdown report to disk."""
	text = render_markdown_report(
		graph, hexagon_orbits, hexagon_geometries, units, scale
	)
	with open(output_path, "w", encoding="utf-8") as handle:
		handle.write(text)


#============================================
def build_mirror_notes(
	hexagon_orbits: tuple[goldberg_brick.orbits.HexagonOrbit, ...],
	builder_summaries: dict[str, goldberg_brick.geometry.BuilderSummary],
) -> list[str]:
	"""Build notes for any pattern whose mirror-aware form differs."""
	notes = []
	for orbit in hexagon_orbits:
		summary = builder_summaries[orbit.orbit_id]
		differences = []
		if summary.angle_pattern != summary.angle_pattern_unoriented:
			differences.append(f"angle {summary.angle_pattern_unoriented}")
		if summary.side_pattern != summary.side_pattern_unoriented:
			differences.append(f"side {summary.side_pattern_unoriented}")
		if summary.dihedral_pattern != summary.dihedral_pattern_unoriented:
			differences.append(f"dihedral {summary.dihedral_pattern_unoriented}")
		if differences:
			note = f"- {orbit.orbit_id} mirror-aware patterns: " + ", ".join(differences)
			notes.append(note)
	return notes


#============================================
def build_connector_counts_section(
	hexagon_orbits: tuple[goldberg_brick.orbits.HexagonOrbit, ...],
	hexagon_geometries: dict[str, goldberg_brick.geometry.HexagonGeometry],
	units: str,
	scale: float,
) -> list[str]:
	"""Build the per-orbit connector counts Markdown sub-section lines."""
	section = ["", "## Per-orbit connector counts", ""]
	for orbit in hexagon_orbits:
		geometry = hexagon_geometries[orbit.orbit_id]
		counts = goldberg_brick.geometry.connector_counts(geometry, orbit.face_count)
		section.append(f"### {orbit.orbit_id} (face_count: {orbit.face_count})")
		section.append("")
		# Angles table
		section.append("| angle (deg) | count_per_face | total |")
		section.append("| --- | --- | --- |")
		for cls in counts.angles:
			section.append(
				f"| {cls.value:.3f} | {cls.count_per_face} | {cls.total_in_orbit} |"
			)
		section.append("")
		# Sides table; multiply by scale and label with units.
		section.append(f"| side ({units}) | count_per_face | total |")
		section.append("| --- | --- | --- |")
		for cls in counts.sides:
			scaled_value = cls.value * scale
			section.append(
				f"| {scaled_value:.3f} | {cls.count_per_face} | {cls.total_in_orbit} |"
			)
		section.append("")
		# Dihedrals table.
		section.append("| dihedral (deg) | count_per_face | total |")
		section.append("| --- | --- | --- |")
		for cls in counts.dihedrals:
			section.append(
				f"| {cls.value:.3f} | {cls.count_per_face} | {cls.total_in_orbit} |"
			)
		section.append("")
	return section


#============================================
def format_sequence(values: tuple[float, ...]) -> str:
	"""Format a numeric sequence for one Markdown table cell."""
	text_values = []
	for value in values:
		text_values.append(f"{value:g}")
	text = "[" + ", ".join(text_values) + "]"
	return text


#============================================
def format_sequence_scaled(values: tuple[float, ...], scale: float) -> str:
	"""Format a numeric sequence scaled by the given factor."""
	text_values = []
	for value in values:
		scaled_value = value * scale
		text_values.append(f"{scaled_value:g}")
	text = "[" + ", ".join(text_values) + "]"
	return text
