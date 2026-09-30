#!/usr/bin/env python3
"""Extract the two-atom Si Löwdin table from a completed QE projwfc.out."""
import argparse
import csv
from pathlib import Path
import re

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('input', type=Path)
p.add_argument('--output', required=True, type=Path)
a = p.parse_args()
if a.output.exists():
    raise FileExistsError(f'Refusing to overwrite {a.output}')
text = a.input.read_text()
if 'JOB DONE.' not in text or 'Lowdin Charges:' not in text:
    raise ValueError('Missing completed Löwdin output')
section = text.rsplit('Lowdin Charges:', 1)[1]
rows = {}
for match in re.finditer(r'Atom #\s*(\d+):\s*([^\n]+)', section):
    atom = int(match[1])
    fields = dict((k, float(v)) for k, v in re.findall(r'(total charge|s|p|pz|px|py)\s*=\s*([+-]?[\d.]+)', match[2]))
    row = rows.setdefault(atom, {})
    for key, value in fields.items():
        if key in row and abs(row[key] - value) > 1e-8:
            raise ValueError(f'Inconsistent atom {atom} field {key}')
        row[key] = value
if sorted(rows) != [1, 2]:
    raise ValueError('This example requires atoms 1 and 2')
for atom, row in rows.items():
    if set(row) != {'total charge', 's', 'p', 'pz', 'px', 'py'}:
        raise ValueError(f'Incomplete atom {atom}: {row}')
    if abs(row['s'] + row['p'] - row['total charge']) > 2e-4:
        raise ValueError('s+p differs from total beyond printed precision')
    if abs(row['pz'] + row['px'] + row['py'] - row['p']) > 2e-4:
        raise ValueError('p components differ from p beyond printed precision')
sp = re.search(r'Spilling Parameter:\s*([\d.]+)', section)
if not sp:
    raise ValueError('Missing spilling')
total = sum(row['total charge'] for row in rows.values())
a.output.parent.mkdir(parents=True, exist_ok=True)
with a.output.open('x', newline='') as stream:
    writer = csv.writer(stream)
    writer.writerow(['atom', 'total_electrons', 's_electrons', 'p_electrons', 'pz_electrons', 'px_electrons', 'py_electrons'])
    for atom, row in sorted(rows.items()):
        writer.writerow([atom] + [f'{row[k]:.4f}' for k in ('total charge', 's', 'p', 'pz', 'px', 'py')])
print(f'atoms: {len(rows)}; projected electrons: {total:.4f} e')
print(f'8-total: {8-total:.4f} e; fraction: {(8-total)/8:.5f}; reported spilling: {float(sp[1]):.4f}')
print(f'wrote: {a.output}')
