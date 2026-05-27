"""Command-line interface for Goldberg Brick reports."""

import argparse

import goldberg_brick.dual
import goldberg_brick.geometry
import goldberg_brick.orbits
import goldberg_brick.report
import goldberg_brick.triangulation


SUPPORTED_MODELS = ("graph-only",)


#============================================
def default_output_path(h_index: int, k_index: int) -> str:
	"""Build the default output path for a report."""
	output_path = f"gp_{h_index}_{k_index}_report.md"
	return output_path


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(description="Write a graph-only Goldberg Brick report.")
	parser.add_argument("-H", dest="h", type=int, required=True, help="Goldberg h index")
	parser.add_argument("-K", dest="k", type=int, required=True, help="Goldberg k index")
	parser.add_argument("-o", "--out", dest="output_path", help="Output Markdown path")
	parser.add_argument(
		"-m",
		"--model",
		dest="model",
		choices=SUPPORTED_MODELS,
		default="graph-only",
		help="Report model",
	)
	args = parser.parse_args()
	return args


#============================================
def build_report(output_path: str, h: int, k: int, model: str) -> None:
	"""Build and write one Goldberg Brick report."""
	print(f"Preparing Goldberg Brick report for GP({h},{k}).")
	print(f"Model: {model}")
	print("Building geodesic triangulation graph.")
	mesh = goldberg_brick.triangulation.build_geodesic_mesh(h, k)
	print(
		f"Geodesic graph: {len(mesh.vertices)} vertices, "
		f"{len(mesh.edges)} edges, {len(mesh.faces)} triangular faces."
	)
	print("Constructing Goldberg dual graph.")
	graph = goldberg_brick.dual.build_goldberg_graph(mesh)
	print(f"Goldberg faces: {len(graph.faces)}")
	print("Grouping hexagon faces into rotation orbits.")
	hexagon_orbits = goldberg_brick.orbits.group_hexagon_orbits(graph)
	print(f"Hexagon orbits: {len(hexagon_orbits)}")
	print("Measuring representative hexagon geometry.")
	hexagon_geometries = goldberg_brick.geometry.compute_hexagon_orbit_geometries(
		graph,
		hexagon_orbits,
	)
	print("Writing Markdown report.")
	goldberg_brick.report.write_markdown_report(
		output_path,
		graph,
		hexagon_orbits,
		hexagon_geometries,
		model,
	)
	print(f"Output file: {output_path}")


#============================================
def main() -> None:
	"""Run the command-line interface."""
	args = parse_args()
	output_path = args.output_path
	if output_path is None:
		output_path = default_output_path(args.h, args.k)
	build_report(output_path, args.h, args.k, args.model)


if __name__ == '__main__':
	main()
