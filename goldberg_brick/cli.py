"""Command-line interface for Goldberg Brick reports."""

import sys
import argparse

import goldberg_brick.dual
import goldberg_brick.equilateral
import goldberg_brick.geometry
import goldberg_brick.orbits
import goldberg_brick.report
import goldberg_brick.triangulation


#============================================
def default_output_path(h_index: int, k_index: int) -> str:
	"""Build the default output path for a report."""
	output_path = f"gp_{h_index}_{k_index}_report.md"
	return output_path


#============================================
def parse_args() -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(description="Write a Goldberg Brick report.")
	parser.add_argument("-H", dest="h", type=int, required=True, help="Goldberg h index")
	parser.add_argument("-K", dest="k", type=int, required=True, help="Goldberg k index")
	parser.add_argument("-o", "--out", dest="output_path", help="Output Markdown path")
	parser.add_argument(
		"-u",
		"--units",
		dest="units",
		choices=["unit", "mm", "stud"],
		default="unit",
		help="Units for linear measurements (default: unit sphere)",
	)
	parser.add_argument(
		"-s",
		"--scale",
		dest="scale",
		type=float,
		default=1.0,
		help="Scale factor for linear measurements (default: 1.0)",
	)
	args = parser.parse_args()
	return args


#============================================
def build_report(
	output_path: str,
	h: int,
	k: int,
	units: str,
	scale: float,
) -> None:
	"""Build and write one Goldberg Brick report."""
	print(f"Preparing Goldberg Brick report for GP({h},{k}).")
	# Validation-gated guard: trigger a real solve+validate so the failure
	# message reflects the current state of the solver, not a stale list.
	# `force_attempt_solve` bypasses the advisory shortcut so the stderr
	# message carries concrete residuals from the validation gate.
	# Narrow try/except at the CLI boundary converts solver validation
	# failure into a clean stderr message and non-zero exit code.
	try:
		goldberg_brick.equilateral.force_attempt_solve(h, k)
	except goldberg_brick.equilateral.ConvergenceError as exc:
		sys.stderr.write(
			f"ERROR: The current equilateral solver does not converge for GP({h},{k}).\n"
			f"Details: {exc}\n"
			"See docs/GP_EQUILATERAL_CONVERGENCE.md for evidence.\n"
		)
		raise SystemExit(2)
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
		units,
		scale,
	)
	print(f"Output file: {output_path}")


#============================================
def main() -> None:
	"""Run the command-line interface."""
	args = parse_args()
	output_path = args.output_path
	if output_path is None:
		output_path = default_output_path(args.h, args.k)
	build_report(
		output_path,
		args.h,
		args.k,
		args.units,
		args.scale,
	)


if __name__ == '__main__':
	main()
