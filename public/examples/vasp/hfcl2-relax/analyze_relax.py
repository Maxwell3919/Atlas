"""Read existing VASP relaxation records; no calculation is submitted."""
from pathlib import Path
import csv, json, math, re

def structure(path):
    ls = path.read_text().splitlines()
    scale = float(ls[1])
    cell = [[float(x) * scale for x in ls[i].split()[:3]] for i in range(2, 5)]
    if scale <= 0:
        raise ValueError('This parser expects a positive POSCAR scale.')
    names = ls[5].split()
    counts = list(map(int, ls[6].split()))
    i = 7
    if ls[i].strip().lower().startswith('s'):
        i += 1
    mode = ls[i].strip().lower()
    coords = [list(map(float, ls[i + 1 + j].split()[:3])) for j in range(sum(counts))]
    if not mode.startswith('d'):
        raise ValueError('This example uses Direct coordinates.')
    a, b, c = cell
    volume = abs(a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return dict(elements=names, counts=counts, cell_A=cell, volume_A3=volume, coordinates_fractional=coords)

def main():
    root = Path(__file__).resolve().parent
    t = (root / 'OUTCAR').read_text()
    ls = t.splitlines()
    forces = []
    for i, l in enumerate(ls):
        if 'POSITION' in l and 'TOTAL-FORCE' in l:
            rows = []
            for s in ls[i + 2:]:
                try:
                    vals = list(map(float, s.split()))
                except ValueError:
                    break
                if len(vals) != 6:
                    break
                rows.append(vals)
            if rows:
                forces.append(rows)
    energies = [float(x) for x in re.findall('FREE ENERGIE OF THE ION-ELECTRON SYSTEM[\\s\\S]*?free\\s+energy\\s+TOTEN\\s*=\\s*([-0-9.]+)', t)]
    if len(forces) != len(energies):
        raise ValueError('Force and free-energy block counts differ.')
    initial = structure(root / 'POSCAR')
    final = structure(root / 'CONTCAR')
    steps = [dict(step=i + 1, free_energy_eV=e, max_force_eV_A=max((math.sqrt(sum((v * v for v in row[3:]))) for row in f))) for i, (e, f) in enumerate(zip(energies, forces))]
    osz = (root / 'OSZICAR').read_text()
    dav = re.findall('^DAV:\\s*(\\d+)\\s+(\\S+)\\s+(\\S+)\\s+(\\S+)', osz, re.M)
    out = root / 'results'
    out.mkdir(exist_ok=True)
    with (out / 'ionic-history.csv').open('w', newline='') as g:
        w = csv.DictWriter(g, fieldnames=list(steps[0]))
        w.writeheader()
        w.writerows(steps)
    stresses = re.findall('in kB\\s+([-0-9.\\s]+)\\n', t)
    summary = dict(version=ls[0].strip(), ionic_steps=len(steps), structural_accuracy_reached='reached required accuracy' in t, timing_footer='General timing and accounting' in t, first_free_energy_eV=energies[0], final_free_energy_eV=energies[-1], energy_change_eV=energies[-1] - energies[0], final_max_force_eV_A=steps[-1]['max_force_eV_A'], initial_structure=initial, final_structure=final, cell_unchanged=initial['cell_A'] == final['cell_A'], volume_relative_change=final['volume_A3'] / initial['volume_A3'] - 1, final_electronic_iteration=int(dav[-1][0]), final_electronic_dE_eV=float(dav[-1][2]), final_electronic_d_eps_eV=float(dav[-1][3]), last_stress_compressive_positive_kbar=list(map(float, stresses[-1].split())) if stresses else None)
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('ionic_steps={}; final_F={:.8f} eV; final_fmax={:.6f} eV/A'.format(len(steps), energies[-1], steps[-1]['max_force_eV_A']))
    print('cell_unchanged={}; volume_relative_change={:.9g}; structural_accuracy_reached={}'.format(summary['cell_unchanged'], summary['volume_relative_change'], summary['structural_accuracy_reached']))
    print('final_DAV={}; dE={:.8g} eV; d_eps={:.8g} eV'.format(summary['final_electronic_iteration'], summary['final_electronic_dE_eV'], summary['final_electronic_d_eps_eV']))
if __name__ == '__main__':
    main()
