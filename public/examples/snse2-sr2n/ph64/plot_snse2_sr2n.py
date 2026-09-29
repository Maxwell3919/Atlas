#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

SN_DIR = Path(__file__).resolve().parent
for candidate in (SN_DIR, SN_DIR.parent, SN_DIR.parents[1], SN_DIR.parents[2] / 'scripts'):
    if (candidate / 'atlas_plot_style.py').exists():
        sys.path.insert(0, str(candidate))
        break

import atlas_plot_style

PALETTE = {
    'Ink': '#162232',
    'Slate': '#324255',
    'Muted': '#5a6b80',
    'Navy': '#0072b2',
    'Blue': '#2968a8',
    'SoftBlue': '#d6e6f4',
    'Teal': '#009e73',
    'SoftTeal': '#d7ece8',
    'Amber': '#e69f00',
    'Rust': '#d55e00',
    'Coral': '#cc79a7',
    'WarmTint': '#f4efe6',
}

CM1_TO_THZ = 1.0 / 33.3564095198152
FIG_OUT_DIR = (
    SN_DIR.parents[2] / 'figures' / 'snse2-sr2n'
    if (SN_DIR.parents[2] / 'figures').exists()
    else SN_DIR / 'figures'
)


def style_axis(ax) -> None:
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def parse_elph_inp_lambda(filepath: Path, target_broadening: float = 0.040) -> tuple[np.ndarray, np.ndarray]:
    text = filepath.read_text()
    lines = text.splitlines()
    w2 = np.fromstring('\n'.join(lines[1:4]), sep=' ')
    ry_to_thz = 3289.84196
    freqs_thz = np.sign(w2) * np.sqrt(np.abs(w2)) * ry_to_thz

    blocks = re.split(r'Gaussian Broadening:\s*([\d.]+)\s*Ry', text)[1:]
    for i in range(0, len(blocks), 2):
        bval = float(blocks[i])
        if abs(bval - target_broadening) < 1e-4:
            lam_vals = []
            for l in blocks[i + 1].splitlines():
                m = re.search(r'lambda\(\s*\d+\)=\s*([-\d.]+)', l)
                if m:
                    lam_vals.append(float(m.group(1)))
                if len(lam_vals) == 18:
                    break
            return freqs_thz, np.array(lam_vals)
    raise ValueError(f'Broadening {target_broadening} not found in {filepath}')


def render_snse2_sr2n_progress() -> None:
    atlas_plot_style.install()
    freq_true = np.loadtxt(SN_DIR / 'srnsnse.freq.gp')
    freq_wrong = np.loadtxt(SN_DIR / 'srnsnse.wrong_mass.freq.gp')
    q_dist = freq_true[:, 0]
    w_true = freq_true[:, 1:] * CM1_TO_THZ
    w_wrong = freq_wrong[:, 1:] * CM1_TO_THZ

    phdos_arr = np.loadtxt(SN_DIR / 'srnsnse.phdos', comments='#')
    w_dos = phdos_arr[:, 0] * CM1_TO_THZ
    dos_scale = 33.3564095
    dos_tot = phdos_arr[:, 1] * dos_scale
    dos_sr = (phdos_arr[:, 2] + phdos_arr[:, 3]) * dos_scale
    dos_sn = phdos_arr[:, 4] * dos_scale
    dos_se = (phdos_arr[:, 5] + phdos_arr[:, 6]) * dos_scale
    dos_n = phdos_arr[:, 7] * dos_scale

    fig = plt.figure(figsize=(10.4, 4.35))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.985, bottom=0.17, top=0.85,
        width_ratios=[0.95, 1.42, 1.08], wspace=0.33
    )
    ax_scf = fig.add_subplot(gs[0, 0])
    gs_mid = gs[0, 1].subgridspec(1, 2, width_ratios=[2.05, 1.0], wspace=0.07)
    ax_ph = fig.add_subplot(gs_mid[0, 0])
    ax_pdos = fig.add_subplot(gs_mid[0, 1], sharey=ax_ph)
    ax_epc = fig.add_subplot(gs[0, 2])

    for ax in (ax_scf, ax_ph, ax_pdos, ax_epc):
        style_axis(ax)

    pwxall_acc = [
        float(m.group(1))
        for m in re.finditer(r'estimated scf accuracy\s*<\s*([\d.E+-]+)\s*Ry', (SN_DIR / 'pwxall.out.txt').read_text())
    ]
    pwx_acc = [
        float(m.group(1))
        for m in re.finditer(r'estimated scf accuracy\s*<\s*([\d.E+-]+)\s*Ry', (SN_DIR / 'pwx.out.txt').read_text())
    ]
    iters_all = np.arange(1, len(pwxall_acc) + 1)
    iters_pwx = np.arange(1, len(pwx_acc) + 1)
    ax_scf.plot(iters_all, np.log10(pwxall_acc), color=PALETTE['Navy'], marker='o', ms=3.3, lw=1.45, label=r'pwxall ($64^2$)')
    ax_scf.plot(iters_pwx, np.log10(pwx_acc), color=PALETTE['Rust'], marker='s', ms=3.0, lw=1.15, ls='--', label=r'pwx ($16^2$)')
    ax_scf.axhline(-12.0, color=PALETTE['Teal'], ls=':', lw=1.0, label=r'$10^{-12}\ \mathrm{Ry}$')
    ax_scf.set_xlabel('SCF iteration (23 steps)')
    ax_scf.set_ylabel(r'$\log_{10}(\mathrm{SCF\ accuracy\ [Ry]})$')
    ax_scf.set_title('SCF convergence', pad=8)
    ax_scf.legend(loc='upper right', fontsize=7.6)

    q_ticks = [q_dist[0], q_dist[50], q_dist[100], q_dist[150]]
    for x in q_ticks[1:-1]:
        ax_ph.axvline(x, color='#ced8e3', lw=0.85, zorder=1)
    for ax in (ax_ph, ax_pdos):
        ax.axhline(10.0, color=PALETTE['Coral'], ls='--', lw=1.0, zorder=3)
        ax.axhspan(7.4, 12.2, color=PALETTE['WarmTint'], alpha=0.55, zorder=0)

    for nu in range(18):
        lbl_w = r'$M_{\mathrm{N}}=118.71$' if nu == 0 else None
        lbl_t = r'$M_{\mathrm{N}}=14.007$' if nu == 0 else None
        ax_ph.plot(q_dist, w_wrong[:, nu], color='#9aa8b8', lw=0.85, ls='--', alpha=0.75, label=lbl_w, zorder=2)
        color_t = PALETTE['Rust'] if nu >= 15 else PALETTE['Navy']
        lw_t = 1.45 if nu >= 15 else 1.0
        ax_ph.plot(q_dist, w_true[:, nu], color=color_t, lw=lw_t, alpha=0.92, label=lbl_t, zorder=3)

    ax_ph.set_xlim(q_ticks[0], q_ticks[-1])
    ax_ph.set_ylim(-0.3, 12.5)
    ax_ph.set_xticks(q_ticks, [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$'])
    ax_ph.set_ylabel(r'Frequency $\omega$ (THz)')
    ax_ph.set_title('Mass-restored phonons', pad=8)
    ax_ph.legend(loc='lower left', fontsize=7.5)

    ax_pdos.fill_betweenx(w_dos, 0, dos_tot, color='#dfe6ef', alpha=0.55)
    ax_pdos.plot(dos_tot, w_dos, color=PALETTE['Ink'], lw=0.95, label='Total')
    ax_pdos.plot(dos_sn + dos_se, w_dos, color=PALETTE['Navy'], lw=1.05, label='Sn+Se')
    ax_pdos.plot(dos_sr, w_dos, color=PALETTE['Teal'], lw=1.05, label='Sr')
    ax_pdos.plot(dos_n, w_dos, color=PALETTE['Rust'], lw=1.25, label='N')
    ax_pdos.set_xlim(0, 5.2)
    ax_pdos.set_xticks([0, 2, 4])
    ax_pdos.set_xlabel('PHDOS')
    ax_pdos.set_title('PHDOS', pad=8)
    ax_pdos.tick_params(labelleft=False)
    ax_pdos.legend(loc='center right', fontsize=7.4)

    q1_freqs, q1_lam = parse_elph_inp_lambda(SN_DIR / 'elph.inp_lambda.1', target_broadening=0.040)
    q2_freqs, q2_lam = parse_elph_inp_lambda(SN_DIR / 'elph.inp_lambda.2', target_broadening=0.040)

    ax_epc.axvline(20.0 * CM1_TO_THZ, color=PALETTE['Amber'], ls=':', lw=1.15, zorder=2)

    m1, s1, _ = ax_epc.stem(
        np.maximum(0.0, q1_freqs), q1_lam,
        linefmt='-', markerfmt='o', basefmt=' ', label=r'$q=1\ (\Gamma)$',
    )
    plt.setp(m1, color=PALETTE['Navy'], markersize=4.0)
    plt.setp(s1, color=PALETTE['Navy'], linewidth=1.15)

    m2, s2, _ = ax_epc.stem(
        np.maximum(0.0, q2_freqs), q2_lam,
        linefmt='--', markerfmt='s', basefmt=' ', label=r'$q=2$',
    )
    plt.setp(m2, color=PALETTE['Rust'], markersize=3.8)
    plt.setp(s2, color=PALETTE['Rust'], linewidth=1.15)

    ax_epc.annotate(
        r'$q=2,\ \nu=2$: $\lambda=0.0644$' + '\n' + r'($\nu=1 < 20\ \mathrm{cm^{-1}}$ cut)',
        xy=(q2_freqs[1], q2_lam[1]),
        xytext=(1.45, 0.050),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )
    ax_epc.annotate(
        r'$q=1,\ \nu=13$ ($4.23\ \mathrm{THz}$)' + '\n' + r'$\lambda=0.0328$ ($\sigma=0.04\ \mathrm{Ry}$)',
        xy=(q1_freqs[12], q1_lam[12]),
        xytext=(2.35, 0.035),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.85),
    )

    ax_epc.set_xlim(-0.2, 7.2)
    ax_epc.set_ylim(0.0, 0.075)
    ax_epc.set_xlabel(r'Pre-fix $\omega_{\mathbf{q}\nu}$ (THz, $M_{\mathrm{N}}=118.71$)')
    ax_epc.set_ylabel(r'Mode $\lambda_{\mathbf{q}\nu}$ ($\sigma=0.040\ \mathrm{Ry}$)')
    ax_epc.set_title(r'Recorded $q=1,2$ EPC', pad=8)
    ax_epc.legend(loc='upper right', fontsize=7.6)

    FIG_OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_OUT_DIR / 'snse2-sr2n-scf-ph-progress.png')
    plt.close(fig)


if __name__ == '__main__':
    render_snse2_sr2n_progress()
