# SnSe₂ / Sr₂N isolated-layer band alignment

This evidence package stages two fixed-geometry, scalar nonmagnetic VASP SCF outputs and the scripts used to inspect them. It contains no POTCAR payload. Each `POTCAR.identity.txt` contains only dataset titles, valence counts, and a SHA-256 identity.

## Analysis logic

1. Check that the two layer POSCARs preserve the shared in-plane cell and their intended rigid-layer shifts from the six-atom reference.
2. Confirm matching INCAR/KPOINTS, SCF completion, electron count, EIGENVAL k-point weights, and sampled band occupation.
3. Compute planar averages and inspect both vacuum windows (6–10 Å and 29–33 Å). Cross-check the windows against the CHGCAR vacuum density and integrated valence charge.
4. Subtract each surface's own vacuum mean from the corresponding Fermi energy and semiconductor band edges.
5. Export all four surface rows and the two facing-surface energy offsets. Do not assign VBM/CBM to metallic Sr₂N; do not call the isolated-layer offset an interface barrier.

## Run

From this directory:

```bash
python3 analyze_alignment.py
python3 check_vacuum_density.py
python3 export_alignment_tables.py
```

The first two scripts use the packaged input/output and NumPy. The table exporter uses only the Python standard library. `plane_average.py` can also be run on each LOCPOT as described in the article.

## Reproduced output

- SnSe₂: 48 sampled k points, E_F = −4.116000 eV, VBM = −4.254365 eV, CBM = −3.976262 eV, sampled gap = 0.278103 eV.
- Sr₂N: bands 13–14 cross E_F = −2.158200 eV on the sampled mesh; treat this model as metallic.
- Facing surfaces: SnSe₂ lower-z and Sr₂N upper-z.
- CBM(SnSe₂) − E_F(Sr₂N) = −2.282607260 eV.
- E_F(Sr₂N) − VBM(SnSe₂) = +2.560710260 eV.
- The two offsets use vacuum-referenced isolated layers with frozen geometry; they do not describe the joined interface.

Generated files: `alignment-summary.json`, `vacuum-density.json`, `band-edges-vacuum-referenced.csv`, and `facing-surface-offsets.csv`. See `../provenance/source-record.md` for source and literature notes.
