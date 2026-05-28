Generates Markdown reports for icosahedral Goldberg polyhedra GP(h,k) using a Schein-Gayed equilateral construction, with per-orbit hexagon geometry and builder-facing connector counts for MOC designers.

# Goldberg Brick

## Quick start

```bash
source source_me.sh && python3 -m pip install -e .
goldberg-brick -H 2 -K 2
```

The default output path is `gp_2_2_report.md` for `GP(2,2)`. Use `--out`
to override the output path:

```bash
goldberg-brick -H 2 -K 2 --out gp_2_2_report.md
```

## Current scope

The first version writes one Markdown report with:

- validated `h,k` indices
- T-number and class I/II/III
- geodesic and Goldberg graph count validation
- deterministic hexagon orbit rows
- measured spherical representative geometry per hexagon orbit
- builder-facing pattern summaries and reuse groups

The report computes `side_length_sequence`, `angle_sequence`, `planarity_error`, and
`dihedral_angle_sequence` under a simple spherical projection model for converging cases.
It also derives angle and side pattern codes, difficulty, warp mode, and cautious suggested use.
Pattern codes are letter-based and rotation-canonical. Mirror-aware pattern notes appear only
when they differ from the oriented pattern.
For converging cases, interpretive fields `deformation_mode` and `brick_strategy` are populated;
for non-converging cases (notably GP(2,0)), they remain `NA`.
No CSV, JSON, SVG, OBJ, PDF, or HTML export exists yet.

## Documentation

- [docs/USAGE.md](docs/USAGE.md) -- builder-facing report walkthrough, CLI examples, and flags (`--units`, `--scale`).

## References

Implementation uses local article PDFs as references:

- `articles/siber-2020.pdf` for the icosadeltahedral T-number model
- `articles/liu-2022.pdf` for Goldberg topology and cage construction
- `articles/brinkmann-schein-2017.pdf` for chiral and mirror-case caution

Equilateral geometry converges for GP(h,k) with k > 0 and some k = 0 cases;
GP(2,0) does not converge due to fundamental incompatibility with rotational symmetry
reduction.
