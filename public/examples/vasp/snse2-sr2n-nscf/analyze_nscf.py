"""Extract the existing uniform-grid, non-spin-polarized VASP DOS."""
from pathlib import Path
import csv, hashlib, json, math, re

def main():
    root = Path(__file__).resolve().parent
    parent = root / 'scf'
    child = root / 'dos'
    texts = [(p / 'OUTCAR').read_text() for p in (parent, child)]

    def number(t, key):
        return float(re.search('\\b' + key + '\\s*=\\s*([-+0-9.]+)', t).group(1))

    def digest(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()
    fields = ['ENCUT', 'ISPIN', 'ISMEAR', 'SIGMA', 'NELECT', 'NBANDS', 'NKPTS', 'LMAXMIX', 'IVDW']
    ps = {k: number(texts[0], k) for k in fields}
    cs = {k: number(texts[1], k) for k in fields}
    if ps != cs:
        raise ValueError('Parent/child effective parameters differ.')
    if (parent / 'POSCAR').read_bytes() != (child / 'POSCAR').read_bytes():
        raise ValueError('Parent and child structure differs.')
    if int(cs['ISPIN']) != 1:
        raise ValueError('This parser expects the actual ISPIN=1 case.')
    ls = (child / 'DOSCAR').read_text().splitlines()
    head = list(map(float, ls[5].split()))
    n = int(head[2])
    ef = head[3]
    rows = [list(map(float, s.split())) for s in ls[6:6 + n]]
    if len(rows) != n or any((len(x) != 3 or not all((math.isfinite(v) for v in x)) for x in rows)):
        raise ValueError('Unexpected total DOS block.')
    el = (child / 'EIGENVAL').read_text().splitlines()
    ne, nk, nb = map(int, el[5].split())
    if (ne, nk, nb) != (int(cs['NELECT']), int(cs['NKPTS']), int(cs['NBANDS'])):
        raise ValueError('EIGENVAL counts disagree.')
    out = root / 'results'
    out.mkdir(exist_ok=True)
    with (out / 'total-dos.csv').open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['energy_eV', 'energy_minus_EF_eV', 'DOS_states_per_eV_cell', 'integrated_states_per_cell'])
        for energy, dos, integ in rows:
            w.writerow([energy, energy - ef, dos, integ])
    idx = min(range(n), key=lambda i: abs(rows[i][0] - ef))
    summary = dict(version=texts[1].splitlines()[0].strip(), parent_parameters=ps, child_parameters=cs, parent_ICHARG=number(texts[0], 'ICHARG'), child_ICHARG=number(texts[1], 'ICHARG'), parent_EDIFF_reached='aborting loop because EDIFF is reached' in texts[0], child_EDIFF_reached='aborting loop because EDIFF is reached' in texts[1], parent_timing_footer='General timing and accounting' in texts[0], child_timing_footer='General timing and accounting' in texts[1], parent_CHGCAR_sha256=digest(parent / 'CHGCAR'), same_POSCAR=True, same_KPOINTS=(parent / 'KPOINTS').read_bytes() == (child / 'KPOINTS').read_bytes(), NEDOS=n, fermi_energy_eV=ef, energy_min_eV=head[1], energy_max_eV=head[0], mean_DOS_energy_spacing_eV=(rows[-1][0] - rows[0][0]) / (n - 1), nearest_EF_sample=dict(energy_eV=rows[idx][0], energy_minus_EF_eV=rows[idx][0] - ef, DOS_states_per_eV_cell=rows[idx][1], integrated_states_per_cell=rows[idx][2]), EIGENVAL_counts=dict(NELECT=ne, NKPTS=nk, NBANDS=nb))
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('ICHARG: parent={} child={}; counts: NELECT={} NKPTS={} NBANDS={}'.format(int(summary['parent_ICHARG']), int(summary['child_ICHARG']), ne, nk, nb))
    print('NEDOS={}; EF={:.8f} eV; mean_DOS_spacing={:.8f} eV'.format(n, ef, summary['mean_DOS_energy_spacing_eV']))
    print('nearest_EF_sample: E-EF={:.8f} eV; DOS={:.4f} states/eV/cell'.format(rows[idx][0] - ef, rows[idx][1]))
    print('same_POSCAR={} same_KPOINTS={} parent_EDIFF={} child_EDIFF={}'.format(summary['same_POSCAR'], summary['same_KPOINTS'], summary['parent_EDIFF_reached'], summary['child_EDIFF_reached']))
if __name__ == '__main__':
    main()
