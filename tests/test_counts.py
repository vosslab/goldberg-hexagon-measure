import goldberg_brick.cli
import goldberg_brick.dual
import goldberg_brick.geometry
import goldberg_brick.orbits
import goldberg_brick.report
import goldberg_brick.triangulation


COUNT_CASES = [(1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1), (4, 2)]


#============================================
def test_geodesic_mesh_counts_for_known_cases() -> None:
	"""Validate geodesic triangulation counts before dualization."""
	for h_index, k_index in COUNT_CASES:
		mesh = goldberg_brick.triangulation.build_geodesic_mesh(h_index, k_index)
		index_data = mesh.index_data

		goldberg_brick.triangulation.validate_mesh_counts(mesh)
		assert len(mesh.vertices) == 10 * index_data.t_number + 2
		assert len(mesh.edges) == 30 * index_data.t_number
		assert len(mesh.faces) == 20 * index_data.t_number


#============================================
def test_report_contains_required_gp_4_2_lines() -> None:
	"""Render the required GP(4,2) report lines."""
	mesh = goldberg_brick.triangulation.build_geodesic_mesh(4, 2)
	graph = goldberg_brick.dual.build_goldberg_graph(mesh)
	hexagon_orbits = goldberg_brick.orbits.group_hexagon_orbits(graph)
	hexagon_geometries = goldberg_brick.geometry.compute_hexagon_orbit_geometries(
		graph,
		hexagon_orbits,
	)
	report_text = goldberg_brick.report.render_markdown_report(
		graph,
		hexagon_orbits,
		hexagon_geometries,
		"graph-only",
	)

	assert "h: 4\n" in report_text
	assert "k: 2\n" in report_text
	assert "T: 28\n" in report_text
	assert "class: III\n" in report_text
	assert "pentagons: 12\n" in report_text
	assert "hexagons: 270\n" in report_text
	assert "total faces: 282\n" in report_text
	assert "status: PASS\n" in report_text
	assert "## Builder pattern summary" in report_text
	assert "## Reuse groups" in report_text
	assert "## Raw hexagon geometry" in report_text
	assert "| H001 |" in report_text
	assert "angle pattern" in report_text
	assert "angle_pattern_unoriented" not in report_text
	assert "side pattern" in report_text
	assert "dihedral_pattern" in report_text
	assert "dihedral_pattern_unoriented" not in report_text
	assert "suggested use" in report_text
	assert "side_length_sequence" in report_text
	assert "planarity_error" in report_text
	assert "dihedral_angle_sequence" in report_text
	for line in report_text.splitlines():
		if not line.startswith("| H") or "side_length_sequence" not in report_text:
			continue
		cells = [cell.strip() for cell in line.strip("|").split("|")]
		if len(cells) != 12:
			continue
		assert cells[3] != "NA"
		assert cells[4] != "NA"
		assert cells[5] != "NA"
		assert cells[6] != "NA"
		assert cells[7] != "NA"
		assert cells[8] != "NA"
		assert cells[9] != "NA"
		assert cells[10] == "NA"
		assert cells[11] == "NA"


#============================================
def test_cli_writes_markdown_report(tmp_path) -> None:
	"""Write a Markdown report through the CLI helper."""
	output_path = tmp_path / "gp_4_2_report.md"
	goldberg_brick.cli.build_report(str(output_path), 4, 2, "graph-only")
	report_text = output_path.read_text(encoding="utf-8")

	assert report_text.startswith("# Goldberg Brick Report: GP(4,2)")
	assert "status: PASS\n" in report_text
	assert "| orbit_id | face_count | mirror_orbit |" in report_text


#============================================
def test_cli_main_uses_index_flags_and_default_output(tmp_path, monkeypatch, capsys) -> None:
	"""Run CLI main with required index flags and default output path."""
	monkeypatch.chdir(tmp_path)
	monkeypatch.setattr("sys.argv", ["run_goldberg_brick.py", "-H", "4", "-K", "2"])
	goldberg_brick.cli.main()
	output_path = tmp_path / "gp_4_2_report.md"
	report_text = output_path.read_text(encoding="utf-8")
	output_lines = capsys.readouterr().out.strip().splitlines()

	assert "h: 4\n" in report_text
	assert "k: 2\n" in report_text
	assert "status: PASS\n" in report_text
	assert "Building geodesic triangulation graph." in output_lines
	assert output_lines[-1] == "Output file: gp_4_2_report.md"
