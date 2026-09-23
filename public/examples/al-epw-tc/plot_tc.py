"""Plot native EPW 6.0 solver output. Run beside linear.csv and gap.csv.

No fit, smoothing or fabricated normal-state gap is used. Connecting lines
only guide the eye. The reported intervals use adjacent sampled temperatures.
"""
from pathlib import Path
import argparse
import csv
import json
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import atlas_plot_style


def rows(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def series(records, cutoff, refined=False):
    use = [r for r in records
           if r['complete'] == 'True' and r['solver'] == 'power'
           and float(r['requested_wscut_eV']) == cutoff
           and (not refined or 'refine' in r['run'])]
    # The refined run repeats some coarse endpoints. Verify before merging.
    points = {}
    for r in use:
        t, y = float(r['T_K']), float(r['max_eigenvalue'])
        if t in points:
            assert abs(points[t] - y) < 1e-7, (t, points[t], y)
        points[t] = y
    return np.array(sorted(points.items()), dtype=float)


def bracket(points):
    intervals = [(float(x1), float(x2))
                 for (x1, y1), (x2, y2) in zip(points, points[1:])
                 if y1 > 1 and y2 < 1]
    assert len(intervals) == 1, intervals
    return intervals[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, default=Path('figures'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    atlas_plot_style.install()
    linear, gap = rows(args.data / 'linear.csv'), rows(args.data / 'gap.csv')
    assert all(float(r['muc']) == .10 for r in linear + gap)
    main_points = series(linear, .10)
    lo, hi = bracket(main_points)
    refined = series(linear, .10, refined=True)
    clean_gap = sorted([r for r in gap if r['converged'] == 'True'
                        and r['whole_run_complete'] == 'True'
                        and float(r['requested_wscut_eV']) == .10],
                       key=lambda r: float(r['T_K']))
    assert len({r['T_K'] for r in clean_gap}) == len(clean_gap)
    temperatures = [float(r['T_K']) for r in clean_gap]
    deltas = [float(r['Delta_omega0_meV']) for r in clean_gap]
    native = (args.data / 'linear-w010-refine/epw.out').read_text()
    ad = float(re.search(r'Allen-Dynes modified McMillan expression\s*=\s*([.\d]+)', native)[1])

    fig, ax = plt.subplots(1, 2, figsize=(10, 4.3))
    fig.subplots_adjust(left=.09, right=.97, bottom=.20, top=.78, wspace=.34)
    fig.suptitle('Isotropic Eliashberg solutions from the Al spectrum', x=.09, ha='left', y=.98, fontsize=12)
    fig.text(.09, .88, r'EPW 6.0  |  $\mu^*=0.10$  |  requested $w_{\rm scut}=0.10$ eV', fontsize=10)
    blue, orange = '#0072b2', '#d55e00'
    ax[0].plot(main_points[:, 0], main_points[:, 1], color=blue, lw=1.1,
               marker='o', mfc='white', ms=4, mew=.85)
    ax[0].axhline(1, color='#333333', lw=.8, ls='--')
    ax[0].axvspan(lo, hi, color='#cccccc', alpha=.65, lw=0)
    ax[0].set(xlabel='Temperature (K)', ylabel=r'Leading kernel eigenvalue $\eta$',
              xlim=(.4, 2.08), ylim=(.89, 1.34))
    ax[0].text(.97, .93, f'$T_c$: {lo:.2f}–{hi:.2f} K', transform=ax[0].transAxes,
               ha='right', va='top')
    ax[0].text(.04, .08, r'$\eta(T_c)=1$', transform=ax[0].transAxes)
    ax[1].plot(temperatures, deltas, color=blue, lw=1.1, marker='o', ms=4)
    ax[1].axvspan(lo, hi, color='#cccccc', alpha=.65, lw=0)
    ax[1].axvline(ad, color='#555555', ls=':', lw=.85)
    ax[1].text(ad+.035, .025, f'Allen–Dynes\n{ad:.4f} K', ha='left', fontsize=9)
    ax[1].set(xlabel='Temperature (K)', ylabel=r'$\Delta(i\omega_0,T)$ (meV)',
              xlim=(.18, 1.58), ylim=(0, .265))
    ax[1].text(.96, .94, '9 converged temperatures', transform=ax[1].transAxes,
               ha='right', va='top')
    fig.text(.09, .025, 'Lines connect calculated points. The failed 1.50 K nonlinear run is omitted, not set to zero.', fontsize=9)
    fig.savefig(args.out/'al-spectrum-tc.png')
    plt.close(fig)

    # Two colours plus neutral distinguish the three explicit cutoff choices.
    cutoffs = [.10, .20, .40]
    styles = [(blue, 'o', '-'), ('#555555', 's', '--'), (orange, '^', '-.')]
    intervals = []
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.3), gridspec_kw={'width_ratios':[1.25,1]})
    fig.subplots_adjust(left=.09, right=.97, bottom=.20, top=.78, wspace=.38)
    fig.suptitle('Matsubara cutoff sensitivity at fixed input Coulomb parameter', x=.09, ha='left', y=.98, fontsize=12)
    fig.text(.09, .88, r'Same Al spectrum and $\mu^*=0.10$; each interval is bounded by computed temperatures', fontsize=10)
    for c, (color, marker, linestyle) in zip(cutoffs, styles):
        p = series(linear, c, refined=True)
        a, b = bracket(p)
        intervals.append({'requested_wscut_eV': c, 'Tc_low_K': a, 'Tc_high_K': b})
        ax[0].plot(p[:, 0], p[:, 1], color=color, marker=marker, mfc='white',
                   ms=4, mew=.85, ls=linestyle, lw=1, label=f'{c:.2f} eV')
        ypos = len(intervals)-1
        ax[1].plot([a,b], [ypos,ypos], color=color, lw=2)
        ax[1].plot([a,b], [ypos,ypos], color=color, marker='|', ls='', ms=10)
        ax[1].text(b+.01,ypos,f'{a:.2f}–{b:.2f} K', va='center', fontsize=9)
    ax[0].axhline(1, color='#333333', ls='--', lw=.8)
    ax[0].set(xlabel='Temperature (K)', ylabel=r'Leading kernel eigenvalue $\eta$')
    ax[0].legend(frameon=False, loc='upper right', fontsize=9)
    ax[1].set(xlabel=r'Computed $T_c$ interval (K)', yticks=[0,1,2],
              yticklabels=['0.10 eV','0.20 eV','0.40 eV'],
              xlim=(1.42,1.74), ylim=(2.5,-.5))
    ax[1].set_ylabel(r'Requested $w_{\rm scut}$')
    fig.text(.09,.025,'These are numerical brackets, not uncertainty bars or proof of physical cutoff convergence.',fontsize=9)
    fig.savefig(args.out/'al-cutoff-sensitivity.png')
    plt.close(fig)
    summary={'muc':.10,'linear_brackets':intervals,'nonlinear_valid_points':len(clean_gap),
             'nonlinear_quantity':'Delta at first positive imaginary Matsubara frequency, in meV',
             'Allen_Dynes_native_estimate_K':ad,
             'failed_nonlinear_1p50K':'not plotted; no zero substituted',
             'scientific_limit':'finite k/q sampling; fixed input muc cutoff sensitivity, not a converged material Tc'}
    (args.out/'plot-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
