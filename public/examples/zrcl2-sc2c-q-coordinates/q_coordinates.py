#!/usr/bin/env python3
"""Convert native QE Cartesian q (2*pi/alat) to reciprocal-cell fractions."""
import csv, hashlib, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent
BOHR_TO_ANGSTROM = 0.529177210903
inp = (ROOT / "pwx.in").read_text()
lines = inp.splitlines()
start = next(i for i, s in enumerate(lines) if s.strip().startswith("CELL_PARAMETERS"))
assert "angstrom" in lines[start].lower()
cell = [list(map(float, s.split())) for s in lines[start + 1:start + 4]]
out = (ROOT / "pwxall.out").read_text()
alat_bohr = float(re.search(r"lattice parameter \(alat\)\s*=\s*([0-9.]+)", out).group(1))
alat_angstrom = alat_bohr * BOHR_TO_ANGSTROM
rows = []
files = sorted((ROOT / "elph_dir").glob("elph.inp_lambda.*"), key=lambda p: int(p.name.rsplit(".", 1)[1]))
for f in files:
    q = [float(x) for x in f.read_text().splitlines()[0].split()[:3]]
    # If q_phys = (2*pi/alat)*q and q_phys = sum_i fraction_i*b_i,
    # with a_i dot b_j = 2*pi*delta_ij, fraction_i = q dot a_i / alat.
    fractions = [sum(q[j] * vector[j] for j in range(3)) / alat_angstrom for vector in cell]
    rows.append(dict(q_index=int(f.name.rsplit(".", 1)[1]), q_cart_x=q[0], q_cart_y=q[1], q_cart_z=q[2], q_fraction_1=fractions[0], q_fraction_2=fractions[1], q_fraction_3=fractions[2]))
with (ROOT / "q-coordinates.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
meta = dict(cell_angstrom=cell, alat_bohr=alat_bohr, alat_angstrom=alat_angstrom, input_q_unit="2*pi/alat", definition="fraction_i = q_cart dot a_i / alat", source_sha256={str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT / "pwx.in", ROOT / "pwxall.out", *files]}, precision="Native q header is rounded to six decimals; alat output is rounded. Fractions inherit those rounding errors.")
(ROOT / "q-coordinate-checks.json").write_text(json.dumps(meta, indent=2) + "\n")
for row in rows: print(row)
