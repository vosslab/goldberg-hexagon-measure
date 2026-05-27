Goldberg Brick generates graph-only Markdown reports for icosahedral Goldberg polyhedra, starting with deterministic face counts and hexagon orbit tables for Brick panel planning.

# Goldberg Brick

## Quick start

```bash
source source_me.sh && python3 -m pip install -e .
goldberg-brick -H 4 -K 2
```

The default output path is `gp_4_2_report.md` for `GP(4,2)`. The optional
`--model` flag defaults to `graph-only`, and `--out` overrides the output path:

```bash
goldberg-brick -H 4 -K 2 --model graph-only --out gp_4_2_report.md
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
`dihedral_angle_sequence` under a simple spherical projection model.
It also derives angle and side pattern codes, difficulty, warp mode, and cautious suggested use.
Pattern codes are letter-based and rotation-canonical. Mirror-aware pattern notes appear only
when they differ from the oriented pattern.
Interpretive fields remain `NA` until measured geometry is trustworthy:
`deformation_mode` and `brick_strategy`.
No CSV, JSON, SVG, OBJ, PDF, or HTML export exists yet.

## References

Implementation uses local article PDFs as references:

- `articles/siber-2020.pdf` for the icosadeltahedral T-number model
- `articles/liu-2022.pdf` for Goldberg topology and cage construction
- `articles/brinkmann-schein-2017.pdf` for chiral and mirror-case caution

Schein-Gayed geometry is not implemented in this graph-only version.
