#!/usr/bin/env python3
"""Read the supplied Si QE SCF files and tabulate total-energy changes.

Usage: python3 analyze_si_convergence.py si-pbe --outdir reproduced
Python standard library only. SHA256SUMS.raw is read beside this script.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path

RY_EV = 13.6056931229905
AXES = {
    'ecutwfc': ['cutoff40', 'cutoff50', 'cutoff60', 'cutoff70', 'cutoff80'],
    'ecutrho': ['rho320', 'rho480', 'scf'],
    'kmesh': ['k4', 'k6', 'k8', 'k10', 'k12', 'k14'],
}
LOGISTICS = {'prefix', 'outdir', 'pseudo_dir', 'wfcdir'}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sources(package):
    records = []
    for line in (package / 'SHA256SUMS.raw').read_text().splitlines():
        digest, name = line.split('  ', 1)
        path = package / name
        if not path.is_file() or sha256(path) != digest:
            raise ValueError(f'Raw-file checksum mismatch: {name}')
        records.append({'file': name, 'sha256': digest})
    return records


def read_input(path):
    lines = [re.sub(r'\s+', ' ', line.split('!', 1)[0].strip()).lower()
             for line in path.read_text().splitlines() if line.split('!', 1)[0].strip()]
    params = {}
    for line in lines:
        match = re.fullmatch(r'([a-z][a-z0-9_]*)\s*=\s*(.*?)\s*,?', line)
        if match:
            params[match[1]] = match[2].rstrip(',').strip().strip("'\"")
    index = lines.index('k_points automatic')
    grid = tuple(int(value) for value in lines[index + 1].split())
    if len(grid) != 6 or len(set(grid[:3])) != 1:
        raise ValueError(f'{path}: expected an n x n x n automatic grid')
    return params, grid, lines, index


def read_run(directory, source_names, package):
    inp = directory / 'scf.in'
    out = directory / 'scf.out'
    err = directory / 'scf.err'
    for path in (inp, out, err):
        if path.exists() and path.relative_to(package).as_posix() not in source_names:
            raise ValueError(f'Raw file missing from SHA256SUMS.raw: {path.name}')
    params, grid, lines, index = read_input(inp)
    text = out.read_text(errors='replace') if out.is_file() else ''
    energies = re.findall(r'^\s*!\s*total energy\s*=\s*([-+\d.eEdD]+)\s+Ry', text, re.M)
    completed = 'JOB DONE.' in text and len(re.findall('convergence has been achieved', text)) == 1
    reasons = []
    if not out.is_file():
        reasons.append('missing scf.out')
    if len(energies) != 1 or not completed:
        reasons.append('one converged SCF energy and normal end required')
    energy = float(energies[0].replace('D', 'E').replace('d', 'e')) if len(energies) == 1 else None
    if energy is not None and not math.isfinite(energy):
        reasons.append('nonfinite energy')
    version = re.search(r'Program PWSCF v\.([^\s]+)', text)
    if text:
        echoes = {'nat': r'number of atoms/cell\s*=\s*(\d+)',
                  'ecutwfc': r'kinetic-energy cutoff\s*=\s*([-+\d.]+)',
                  'ecutrho': r'charge density cutoff\s*=\s*([-+\d.]+)'}
        for key, pattern in echoes.items():
            match = re.search(pattern, text)
            if not match or not math.isclose(float(match[1]), float(params[key]), abs_tol=1e-6):
                reasons.append(f'{key} input/output mismatch')
        if not version or version[1] != '7.5':
            reasons.append('expected QE 7.5')
        if not re.search(r'Exchange-correlation\s*=\s*PBE', text):
            reasons.append('expected PBE output')
    if params.get('calculation') != 'scf' or int(params['nat']) != 2:
        reasons.append('expected a two-atom SCF input')
    stderr = [line.strip() for line in err.read_text(errors='replace').splitlines() if line.strip()] if err.is_file() else []
    errclass = ('empty' if not stderr else 'X11 authorization notice' if all(
        line == 'Authorization required, but no authorization protocol specified' for line in stderr
    ) else 'inspect stderr')
    if errclass == 'inspect stderr':
        reasons.append('unclassified stderr')
    return {'directory': directory.name, 'params': params, 'grid': grid,
            'lines': lines, 'grid_line': index + 1, 'energy': energy,
            'complete': not reasons, 'reasons': '; '.join(reasons),
            'stderr': errclass, 'input_sha256': sha256(inp),
            'output_sha256': sha256(out) if out.is_file() else ''}


def signature(run, axis):
    kept = []
    for index, line in enumerate(run['lines']):
        assignment = re.match(r'([a-z][a-z0-9_]*)\s*=', line)
        if assignment and (assignment[1] in LOGISTICS or assignment[1] == axis):
            continue
        if axis == 'kmesh' and index == run['grid_line']:
            kept.append(' '.join(str(value) for value in run['grid'][3:]))
        else:
            kept.append(line)
    return tuple(kept)


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def scf_history(path):
    history = []
    for match in re.finditer(r'iteration #\s*(\d+)(.*?)(?=iteration #|\Z)', path.read_text(), re.S):
        energy = re.search(r'(?:!\s*)?total energy\s*=\s*([-+\d.]+)\s+Ry', match[2])
        accuracy = re.search(r'estimated scf accuracy\s*<\s*([-+\d.Ee]+)\s+Ry', match[2])
        if not energy or not accuracy:
            raise ValueError(f'incomplete SCF iteration {match[1]}')
        history.append({'iteration': int(match[1]), 'energy_Ry_per_cell': float(energy[1]),
                        'estimated_scf_accuracy_Ry': float(accuracy[1])})
    return history


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw', type=Path)
    parser.add_argument('--outdir', type=Path, default=Path('results'))
    parser.add_argument('--tolerance', type=float, default=1.0, help='meV/atom')
    args = parser.parse_args()
    if not math.isfinite(args.tolerance) or args.tolerance <= 0:
        raise ValueError('tolerance must be finite and positive')
    raw = args.raw.resolve()
    package = Path(__file__).resolve().parent
    sources = verify_sources(package)
    source_names = {row['file'] for row in sources}
    runs = [read_run(path.parent, source_names, package) for path in sorted(raw.glob('*/scf.in'))]
    by_name = {run['directory']: run for run in runs}
    base = by_name['scf']
    for name in ('cutoff60', 'k8'):
        other = by_name[name]
        if signature(other, '') != signature(base, '') or not other['complete'] or not base['complete']:
            raise ValueError(f'{name}: baseline copy differs')
        if abs(other['energy'] - base['energy']) > 1e-8:
            raise ValueError(f'{name}: baseline energies differ beyond output precision')
    rows, selections = [], []
    for axis, names in AXES.items():
        members = [by_name[name] for name in names]
        if not all(run['complete'] for run in members):
            raise ValueError(f'{axis}: a required scan point is incomplete')
        if len({signature(run, axis) for run in members}) != 1:
            raise ValueError(f'{axis}: fixed input settings differ')
        reference = members[-1]['energy']
        series = []
        previous = None
        for run in members:
            setting = run['grid'][0] if axis == 'kmesh' else float(run['params'][axis])
            adjacent = None if previous is None else abs(run['energy'] - previous) * RY_EV * 1000 / 2
            series.append({'parameter': axis, 'directory': run['directory'], 'setting': setting,
                'natoms': 2, 'energy_Ry_per_cell': run['energy'],
                'delta_meV_per_atom': abs(run['energy'] - reference) * RY_EV * 1000 / 2,
                'adjacent_meV_per_atom': adjacent, 'selected': False,
                'input_sha256': run['input_sha256'], 'output_sha256': run['output_sha256']})
            previous = run['energy']
        chosen = next(i for i, row in enumerate(series) if row['delta_meV_per_atom'] <= args.tolerance
                      and all(later['adjacent_meV_per_atom'] <= args.tolerance for later in series[i + 1:]))
        series[chosen]['selected'] = True
        selections.append({'parameter': axis, 'selected': series[chosen]['setting'],
            'reference': series[-1]['setting'], 'delta_meV_per_atom': series[chosen]['delta_meV_per_atom']})
        rows.extend(series)
    inventory = [{key:run[key] for key in ('directory','complete','reasons','stderr','input_sha256','output_sha256')} for run in runs]
    args.outdir.mkdir(parents=True, exist_ok=True)
    write_csv(args.outdir / 'convergence.csv', rows)
    write_csv(args.outdir / 'run-inventory.csv', inventory)
    write_csv(args.outdir / 'scf-history.csv', scf_history(raw/'scf/scf.out'))
    summary = {'QE_version': '7.5', 'Ry_to_eV': RY_EV, 'natoms': 2,
        'tolerance_meV_per_atom': args.tolerance, 'candidate_runs': len(runs),
        'complete_runs': sum(run['complete'] for run in runs), 'table_rows': len(rows),
        'reference': 'highest sampled setting in each axis', 'selections': selections,
        'independent_scans': True, 'joint_selected_settings_calculated': False}
    (args.outdir/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    (args.outdir/'source-files.json').write_text(json.dumps(sources,indent=2)+'\n')
    report = ['# Si 固定晶胞总能量扫描', '',
        f'QE 7.5；两个原子/原胞；1 Ry = {RY_EV} eV。', '',
        '| 参数 | 设置 | 总能量 (Ry/原胞) | 与最高点差值 (meV/atom) | 相邻变化 (meV/atom) | 选择 |',
        '| --- | ---: | ---: | ---: | ---: | --- |']
    for row in rows:
        adjacent = '—' if row['adjacent_meV_per_atom'] is None else f"{row['adjacent_meV_per_atom']:.6f}"
        report.append(f"| {row['parameter']} | {row['setting']:g} | {row['energy_Ry_per_cell']:.8f} | {row['delta_meV_per_atom']:.6f} | {adjacent} | {'✓' if row['selected'] else ''} |")
    report.extend(['', f'按 {args.tolerance:g} meV/atom 比较线，选择同时满足参照差和后续相邻差的最低采样点。',
        '参照是每组最高已测设置。三组分别固定其余参数；所选最低设置尚未组合为同一次计算。',
        'conv_thr 控制单次电子自洽；力、应力及后续性质按各自目标量继续比较。', ''])
    (args.outdir/'energy-report.md').write_text('\n'.join(report),encoding='utf-8')
    print(f"raw_checksums={len(sources)} complete_runs={summary['complete_runs']} excluded_runs={len(runs)-summary['complete_runs']} table_rows={len(rows)}")
    for item in selections:
        setting = f"{int(item['selected'])}x{int(item['selected'])}x{int(item['selected'])}" if item['parameter']=='kmesh' else f"{item['selected']:g} Ry"
        print(f"{item['parameter']}: {setting}; difference to reference = {item['delta_meV_per_atom']:.6f} meV/atom")
    print(f'Results: {args.outdir}')


if __name__ == '__main__':
    main()
