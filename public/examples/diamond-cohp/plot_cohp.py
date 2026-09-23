"""Plot this non-magnetic diamond example from native QE/LOBSTER output.

Run in the unpacked cohp-diamond directory: python3 plot_cohp.py
Requires NumPy >= 2.0 and Matplotlib. No LOBSTER executable is needed to replot.
"""
from pathlib import Path
import argparse
import json
import re
import xml.etree.ElementTree as ET

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent
BOHR_TO_ANGSTROM = 0.529177210903
HARTREE_TO_EV = 27.211386245988
BLUE, ORANGE, INK, GREY = '#0072b2', '#d55e00', '#111111', '#777777'
MODE = 'web'


def set_style(mode):
    global MODE
    MODE = mode
    available = {f.name for f in font_manager.fontManager.ttflist}
    family = next((name for name in ('Arial', 'Helvetica') if name in available), 'DejaVu Sans')
    plt.rcParams.update({
        'font.family': family, 'font.size': size(10, 7),
        'axes.labelsize': size(10.5, 7), 'axes.titlesize': size(10.5, 7),
        'xtick.labelsize': size(9, 6), 'ytick.labelsize': size(9, 6),
        'legend.fontsize': size(9, 6), 'mathtext.fontset': 'dejavusans',
        'axes.labelcolor': INK, 'text.color': INK, 'xtick.color': INK,
        'ytick.color': INK, 'axes.edgecolor': INK, 'axes.linewidth': .65,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.grid': False, 'savefig.facecolor': 'white',
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
        'xtick.direction': 'out', 'ytick.direction': 'out',
        'xtick.major.width': .65, 'ytick.major.width': .65,
    })


def size(web, paper):
    return paper if MODE == 'paper' else web


def panel(ax, letter):
    ax.text(-.16, 1.075, letter, transform=ax.transAxes,
            fontsize=size(12, 8), fontweight='bold', va='bottom')


def load_case(name):
    folder = ROOT / name
    lines = (folder / 'COHPCAR.lobster').read_text().splitlines()
    meta = lines[1].split()
    sets, spins, points = map(int, meta[:3])
    if spins != 1:
        raise ValueError('This lesson parser handles its non-magnetic, one-block output only.')
    pairs = sets - 1
    assert pairs == 4 and lines[2].strip() == 'Average'
    data = np.loadtxt(folder / 'COHPCAR.lobster', skiprows=sets + 2)
    assert data.shape == (points, 1 + 2 * sets)
    assert np.all(np.diff(data[:, 0]) > 0) and np.all(np.isfinite(data))
    assert np.max(np.abs(data[:, 1] - data[:, 3::2].mean(axis=1))) <= 1.1e-5
    assert np.max(np.abs(data[:, 2] - data[:, 4::2].mean(axis=1))) <= 1.1e-5

    rows = []
    for line in (folder / 'ICOHPLIST.lobster').read_text().splitlines():
        tokens = line.split()
        if not tokens or not tokens[0].isdigit():
            continue
        assert len(tokens) == 8, 'Unexpected ICOHPLIST spin/vector layout'
        index = int(tokens[0])
        atoms = [int(re.fullmatch(r'C(\d+)', token)[1]) for token in tokens[1:3]]
        rows.append({'index': index, 'atoms': atoms, 'distance_A': float(tokens[3]),
                     'translation': list(map(int, tokens[4:7])), 'icohp_eV': float(tokens[7])})
    assert len(rows) == pairs and [row['index'] for row in rows] == list(range(1, 5))

    xml_file = folder / 'data-file-schema.xml'
    if not xml_file.exists():
        xml_file = folder / 'tmp/diamond.save/data-file-schema.xml'
    tree = ET.parse(xml_file).getroot()
    structure = tree.find('./output/atomic_structure')
    lattice = np.array([np.fromstring(node.text, sep=' ') for node in structure.find('cell')]) * BOHR_TO_ANGSTROM
    atoms = np.array([np.fromstring(node.text, sep=' ') for node in structure.find('atomic_positions')]) * BOHR_TO_ANGSTROM
    assert lattice.shape == (3, 3) and atoms.shape == (2, 3)
    bs = tree.find('./output/band_structure')
    ef = float(bs.findtext('fermi_energy')) * HARTREE_TO_EV
    ho = float(bs.findtext('highestOccupiedLevel')) * HARTREE_TO_EV
    lu = float(bs.findtext('lowestUnoccupiedLevel')) * HARTREE_TO_EV
    assert int(bs.findtext('nbnd')) == 8 and float(bs.findtext('nelec')) == 8
    assert abs(ef - ho) < 1e-8
    assert abs(ef - float(meta[5])) < 5.1e-5
    for row in rows:
        first, second = [atoms[i - 1] for i in row['atoms']]
        row['vector_A'] = (second + np.array(row['translation']) @ lattice - first).tolist()
        row['xml_distance_A'] = float(np.linalg.norm(row['vector_A']))
        assert abs(row['xml_distance_A'] - row['distance_A']) < 6e-6

    text = (folder / 'diamond.scf.in').read_text()
    cutoff = float(re.search(r'ecutwfc\s*=\s*([\d.]+)', text, re.I)[1])
    rho = float(re.search(r'ecutrho\s*=\s*([\d.]+)', text, re.I)[1])
    mesh = list(map(int, re.search(r'K_POINTS\s+automatic\s*\n\s*(\d+)\s+(\d+)\s+(\d+)', text, re.I).groups()))
    output = (folder / 'lobsterout').read_text()
    charge = float(re.search(r'abs\. charge spilling:\s*([\d.]+)%', output)[1])
    total = float(re.search(r'abs\. total\s+spilling:\s*([\d.]+)%', output)[1])
    assert 'C (bunge)' in output
    ef_column = float(np.interp(0, data[:, 0], data[:, 2]))
    below = data[:, 0] < 0
    integral_x = np.r_[data[below, 0], 0.0]
    integral_y = np.r_[data[below, 1], np.interp(0, data[:, 0], data[:, 1])]
    trapezoid = float(np.trapezoid(integral_y, integral_x))
    return dict(name=name, data=data, bonds=rows, lattice=lattice, atoms=atoms,
                ef=ef, ho=ho, lu=lu, cutoff=cutoff, rho=rho, mesh=mesh,
                charge_spilling=charge, total_spilling=total,
                native_icohp=float(np.mean([row['icohp_eV'] for row in rows])),
                cumulative_at_zero=ef_column, trapezoid_at_zero=trapezoid)


def save(fig, stem):
    directory = ROOT / 'figures'
    directory.mkdir(exist_ok=True)
    extension = 'pdf' if MODE == 'paper' else 'png'
    fig.savefig(directory / f'{stem}.{extension}', dpi=300)
    plt.close(fig)


def spectrum(case):
    data = case['data']
    energy, curve, cumulative = data[:, 0], -data[:, 1], -data[:, 2]
    fig, axes = plt.subplots(1, 2, figsize=(183/25.4, 112/25.4), sharey=True)
    fig.subplots_adjust(top=.88, bottom=.14, left=.10, right=.975, wspace=.24)
    for ax in axes:
        ax.axhline(0, color=INK, linestyle='--', linewidth=.7)
        ax.set_ylim(energy.min(), energy.max())
        ax.tick_params(direction='out')
    axes[0].fill_betweenx(energy, 0, curve, where=curve >= 0, interpolate=True, color=BLUE, alpha=.23)
    axes[0].fill_betweenx(energy, 0, curve, where=curve < 0, interpolate=True, color=ORANGE, alpha=.23)
    axes[0].plot(curve, energy, color=INK, linewidth=.8)
    axes[0].axvline(0, color=GREY, linewidth=.7)
    axes[0].set_xlabel(r'$-$pCOHP')
    axes[0].set_ylabel(r'$E-E_F$ (eV)')
    axes[0].set_title('Antibonding ← 0 → Bonding', pad=11)
    axes[1].plot(cumulative, energy, color=BLUE, linewidth=1.1)
    axes[1].plot(-case['cumulative_at_zero'], 0, marker='o', markerfacecolor='white',
                 markeredgecolor=INK, markersize=4, markeredgewidth=.75)
    axes[1].set_xlabel(r'$-$ICOHP$(E)$ (eV per bond)')
    axes[1].set_title('Integrated contribution', pad=11)
    axes[1].text(.96, .04, 'Four-bond average\n' + r'$E_F = E_{VBM}$',
                 transform=axes[1].transAxes, va='bottom', ha='right', fontsize=size(9, 6))
    panel(axes[0], 'a')
    panel(axes[1], 'b')
    save(fig, 'cohp-spectrum')


def bonds(case):
    fig = plt.figure(figsize=(183/25.4, 88/25.4))
    ax = fig.add_axes([.01, .04, .55, .90], projection='3d')
    origin = np.array([0., 0., 0.])
    for row in case['bonds']:
        end = np.array(row['vector_A'])
        ax.plot(*np.stack([origin, end]).T, color=GREY, linewidth=1.4)
        ax.scatter(*end, color=BLUE, s=90, edgecolor=INK, linewidth=.6, depthshade=False)
        text_at = end * 1.34
        ax.text(*text_at, f"{row['index']}", ha='center', va='center', fontsize=size(10, 7))
    ax.scatter(0, 0, 0, color=INK, s=100, depthshade=False)
    ax.text(0, 0, .25, 'C1', ha='center', va='bottom', color=INK, fontsize=size(10, 7))
    extent = max(np.abs(row['vector_A']).max() for row in case['bonds']) * 1.45
    for setter in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
        setter(-extent, extent)
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(elev=18, azim=30)
    ax.set_proj_type('ortho')
    ax.set_axis_off()
    fig.text(.57, .85, 'Four periodic C2 neighbours', fontsize=size(10.5, 7))
    fig.text(.57, .76, 'Bond    Translation T', fontsize=size(9.5, 6.5))
    for i, row in enumerate(case['bonds']):
        t = ', '.join(map(str, row['translation']))
        fig.text(.58, .65-i*.12, f"{row['index']}          ({t})", fontsize=size(10, 7))
    fig.text(.57, .12, f"C–C = {case['bonds'][0]['xml_distance_A']:.6f} Å", fontsize=size(10, 7))
    save(fig, 'cohp-bonds')


def comparison(cases):
    assert len(cases) == 4
    for case in cases:
        assert case['rho'] == cases[0]['rho']
        assert np.allclose(case['lattice'], cases[0]['lattice'], rtol=0, atol=1e-12)
        assert [b['translation'] for b in case['bonds']] == [b['translation'] for b in cases[0]['bonds']]
    changes = []
    for previous, current in zip(cases[:-1], cases[1:]):
        delta = np.array([b['icohp_eV'] for b in current['bonds']]) - np.array([b['icohp_eV'] for b in previous['bonds']])
        changes.append({'from': previous['name'], 'to': current['name'],
                        'absolute_mean_change_eV': abs(float(delta.mean())),
                        'maximum_single_bond_change_eV': float(np.abs(delta).max())})
    values = [x['maximum_single_bond_change_eV'] for x in changes]
    labels = ['6³ → 8³', '8³ → 10³', '60 → 80 Ry']
    fig, (left, ax) = plt.subplots(1, 2, figsize=(183/25.4, 105/25.4))
    fig.subplots_adjust(top=.84, bottom=.24, left=.13, right=.98, wspace=.50)
    left.plot(np.arange(3), [c['native_icohp'] for c in cases[:3]], '-o',
              color=BLUE, linewidth=.9, markersize=4)
    left.plot(3, cases[3]['native_icohp'], 's', color=INK, markerfacecolor='white',
              markersize=4, markeredgewidth=.8)
    left.set_xticks(range(4), ['6³', '8³', '10³', '10³\n80 Ry'])
    left.set_xlim(-.35, 3.35)
    left.set_ylim(-9.6092, -9.6033)
    left.set_yticks([-9.609, -9.607, -9.605, -9.6035])
    left.ticklabel_format(axis='y', style='plain', useOffset=False)
    left.set_ylabel('Mean ICOHP (eV per bond)')
    left.set_xlabel('k grid; 60 Ry unless labelled')
    left.set_title('Native occupied-state integral', pad=14)
    ax.plot(np.arange(3), values, linestyle='none', marker='o', color=BLUE,
            markeredgecolor=INK, markeredgewidth=.5, markersize=4)
    ax.axhline(.02, color=INK, linestyle='--', linewidth=.7)
    ax.set_yscale('log')
    ax.set_ylim(5e-5, .08)
    for i, value in enumerate(values):
        ax.annotate(f'{value:.5f}', (i, value), xytext=(0, 8), textcoords='offset points',
                    ha='center', fontsize=size(8.5, 6))
    ax.text(.98, .83, 'Comparison criterion: 0.02', transform=ax.transAxes,
            ha='right', va='bottom', fontsize=size(8, 6))
    ax.set_xticks(np.arange(3), labels)
    ax.set_xlim(-.45, 2.45)
    ax.set_ylabel('Maximum |ΔICOHP| (eV per bond)')
    ax.set_title('Change of matching bonds', pad=14)
    ax.tick_params(axis='x', labelrotation=18)
    panel(left, 'a')
    panel(ax, 'b')
    save(fig, 'cohp-comparison')
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', default='diamond-k10-80')
    parser.add_argument('--skip-comparison', action='store_true')
    args = parser.parse_args()
    case = load_case(args.case)
    fields = ['name', 'mesh', 'cutoff', 'rho', 'ef', 'ho', 'lu', 'native_icohp',
              'cumulative_at_zero', 'trapezoid_at_zero', 'charge_spilling', 'total_spilling', 'bonds']
    report = {'selected_case': {key: case[key] for key in fields}}
    if not args.skip_comparison:
        cases = [load_case(name) for name in ['diamond-k6', 'diamond-k8', 'diamond-k10', 'diamond-k10-80']]
        report['cases'] = [{key: c[key] for key in fields} for c in cases]
    for mode in ('web', 'paper'):
        set_style(mode)
        spectrum(case)
        bonds(case)
        if not args.skip_comparison:
            report['comparisons'] = comparison(cases)
    report['figure_export'] = {'width_mm': 183, 'paper_font_pt': [5, 7],
                               'paper_panel_font_pt': 8, 'pdf_fonttype': 42,
                               'web_png_dpi': 300, 'gridlines': False}
    (ROOT / 'figures/plot-checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
