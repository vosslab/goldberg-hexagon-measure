# Divergence: chirality labels and conventions missing

## Source

Audit `docs/active_plans/active/solver_paper_parity.md`, M4 routing.

## Summary

Code's chirality handling is geometrically correct (uses orientation-preserving
icosahedral group I, 60 rotations, not Ih) but labeling and convention
enforcement are absent. This is documentation_only severity: the report's
geometry is right; the report's wording could be clearer.

## Specific gaps

| Paper claim | Code state | Fix direction |
|---|---|---|
| Schein-Gayed C4: GP(h,k) and GP(k,h) are mirror enantiomers when h != k, h,k > 0 | `orientation_label` emits "GP(h,k); mirror GP(k,h)" string but no chirality flag in `GoldbergIndices` | Add `is_chiral: bool` and `enantiomer: tuple[int,int]` fields to `GoldbergIndices` (set when class III) |
| Siber S2: convention m >= n (laevo); right-turn = (n,m) | `classify_indices` accepts (h,k) in any order; both yield class III | Add `handedness: str` ("laevo" or "dextro") derived from h vs k for class III |
| Siber S3: 7l vs 7d notation | report does not emit handedness suffix | Append "l" / "d" to T-number string in report.py summary |
| Brinkmann B2: chirality iff b != 0 AND a != b | class III returned but no flag | covered by `is_chiral` above |
| Brinkmann B4: dodecahedron mirror symmetries lost for chiral | code uses I (60) not Ih (120) -- already correct | no code change; add docstring note |
| Brinkmann B5: canonical ordering a >= b >= 0 | RESOLVED 2026-05-28: CLI hard-rejects `k > h` via `goldberg_brick.cli.validate_indices`; error names the mirror enantiomer and instructs re-run | done |
| Brinkmann B8: "Goldberg-Coxeter" = Caspar-Klug | not documented | one-line note in `goldberg_brick/__init__.py` docstring or `docs/CODE_ARCHITECTURE.md` |
| `HexagonOrbit.mirror_orbit="NA"` always | no mirror pairing | for class III, populate `mirror_orbit` with the swapped-handedness orbit ID (currently meaningful only if we ever support running the mirror enantiomer in the same session) |

## Reproduction

```bash
source source_me.sh && python3 run_goldberg_brick.py -H 4 -K 2 -o /tmp/r1.md
source source_me.sh && python3 run_goldberg_brick.py -H 2 -K 4 -o /tmp/r2.md
diff /tmp/r1.md /tmp/r2.md
```

Reports are not currently distinguished beyond the orientation_label string;
they should also differ in a handedness suffix on the T-number and in any
mirror-aware orbit pairing.

## Severity

documentation_only. No geometry change.

## Proposed owner

TBD. Low priority; can be batched after the chiral reduction fix.
