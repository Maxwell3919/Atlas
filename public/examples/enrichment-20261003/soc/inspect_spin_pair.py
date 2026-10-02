#!/usr/bin/env python3
"""Inspect saved projection columns at one path record, without fitting or plotting."""
import argparse
import math
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('data', type=Path)
parser.add_argument('--ik', type=int, default=100)
parser.add_argument('--bands', type=int, nargs=2, default=[51, 52])
args = parser.parse_args()
if args.ik < 1 or min(args.bands) < 1 or args.bands[0] == args.bands[1]:
    parser.error("Choose a positive path record and two distinct positive bands")
rows = {}
for line in args.data.read_text().splitlines():
    if not line.strip() or line.lstrip().startswith('#'):
        continue
    values = [float(x) for x in line.split()]
    if len(values) != 13 or not all(math.isfinite(x) for x in values):
        raise ValueError('Expected thirteen finite spin-path.dat columns')
    ik, band = values[:2]
    if ik != int(ik) or band != int(band):
        raise ValueError('Noninteger record or band index')
    if int(ik) == args.ik and int(band) in args.bands:
        if int(band) in rows:
            raise ValueError('Duplicate requested record')
        rows[int(band)] = values
if set(rows) != set(args.bands):
    raise ValueError('Requested pair is incomplete')
a, b = [rows[n] for n in args.bands]
if a[2:6] != b[2:6]:
    raise ValueError('Pair does not share the same path coordinate')
print('ik band E-EF_eV occupation charge mz/charge inplane/abs(mz)')
for row in (a, b):
    q, mx, my, mz = row[9:13]
    if q <= 0 or mz == 0:
        raise ValueError('Ratio requires positive weight and nonzero mz')
    print(f'{int(row[0])} {int(row[1])} {row[7]:+.9f} {row[8]:.3f} '
          f'{q:.3f} {mz/q:+.6f} {math.hypot(mx,my)/abs(mz):.6f}')
print(f'energy_difference_meV={(b[6]-a[6])*1000:.6f}')
print('Ratios describe the saved atomic projections; no full-state spin or TR test.')
