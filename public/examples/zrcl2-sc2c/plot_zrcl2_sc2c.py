#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import numpy as np

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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_EXAMPLES = ROOT / 'public' / 'examples'
PUBLIC_FIGURES = ROOT / 'public' / 'figures'
LOCAL_MIRROR_FIGURES = Path('/Users/paquette/Documents/projects/Atlas/案例/Website-Figures')
SCRATCH_DATA = Path('/Users/paquette/.gemini/antigravity/brain/1e3e274d-dc0c-4dad-b800-38478ece630e/scratch/bcgong_data')

CM1_TO_THZ = 1.0 / 33.3564095198152


def apply_atlas_style() -> None:
    atlas_plot_style.install()


def style_axis(ax) -> None:
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def save_figure(fig, stem_path: Path) -> None:
    stem_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem_path.with_suffix('.png'))
    plt.close(fig)


def sync_figure_to_mirror(rel_stem: str) -> None:
    if not LOCAL_MIRROR_FIGURES.exists():
        return
    for ext in ('png', 'svg', 'pdf'):
        src = PUBLIC_FIGURES / f'{rel_stem}.{ext}'
        dst = LOCAL_MIRROR_FIGURES / f'{rel_stem}.{ext}'
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


# ---------------------------------------------------------------------------
# 1. ZrCl2/Sc2C Coupled Electronic Structure: Orbital Fatbands + PDOS + 2D FS
# ---------------------------------------------------------------------------

def parse_zrcl2_fatbands() -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133  # eV from scf/pwx.out
    gnu_path = PUBLIC_EXAMPLES / 'zrcl2-sc2c' / 'scf' / 'bands.dat.gnu'
    raw_blocks = [b.strip() for b in gnu_path.read_text().split('\n\n') if b.strip()]
    k_list = []
    e_list = []
    for block in raw_blocks:
        arr = np.loadtxt(block.splitlines())
        k_list = arr[:, 0]
        e_list.append(arr[:, 1] - ef)
    k_dist = np.array(k_list)
    bands_e = np.array(e_list)  # (31, 151)

    proj_path = SCRATCH_DATA / 'zrcl2_sc2c' / 'scf' / 'fatbands.projwfc_up'
    lines = proj_path.read_text().splitlines()
    header_idx = 0
    for idx, line in enumerate(lines[:30]):
        parts = line.split()
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            natomwfc, nk, nbnd = map(int, parts)
            header_idx = idx + 2
            break

    weights = {
        'Zr-4d': np.zeros((nbnd, nk)),
        'Sc-3d': np.zeros((nbnd, nk)),
        'C-2p': np.zeros((nbnd, nk)),
        'Cl-3p': np.zeros((nbnd, nk)),
    }

    ptr = header_idx
    block_len = nk * nbnd
    for _ in range(natomwfc):
        if ptr >= len(lines):
            break
        hdr = lines[ptr].split()
        elem = hdr[2]
        orb = hdr[3].upper()
        key = None
        if elem == 'Zr' and 'D' in orb:
            key = 'Zr-4d'
        elif elem == 'Sc' and 'D' in orb:
            key = 'Sc-3d'
        elif elem == 'C' and 'P' in orb:
            key = 'C-2p'
        elif elem == 'Cl' and 'P' in orb:
            key = 'Cl-3p'

        sub_lines = lines[ptr + 1 : ptr + 1 + block_len]
        if key is not None and len(sub_lines) == block_len:
            vals = np.fromiter((float(l.split()[2]) for l in sub_lines), dtype=float, count=block_len)
            weights[key] += vals.reshape(nk, nbnd).T
        ptr += 1 + block_len

    return k_dist, bands_e, weights


def parse_zrcl2_pdos() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133
    pdos_dir = SCRATCH_DATA / 'zrcl2_sc2c' / 'pdos'
    tot_arr = np.loadtxt(pdos_dir / 'zrclscc.pdos_tot', comments='#')
    energy = tot_arr[:, 0] - ef
    curves = {'Total': tot_arr[:, 1]}

    def sum_files(patterns: list[str]) -> np.ndarray:
        acc = np.zeros_like(energy)
        for pat in patterns:
            for p in pdos_dir.glob(pat):
                arr = np.loadtxt(p, comments='#')
                acc += arr[:, 1]
        return acc

    curves['Zr-4d'] = sum_files(['*Zr*_wfc*d*'])
    curves['Sc-3d'] = sum_files(['*Sc*_wfc*d*'])
    curves['C-2p'] = sum_files(['*C)*_wfc*p*'])
    curves['Cl-3p'] = sum_files(['*Cl*_wfc*p*'])
    return energy, curves


def parse_zrcl2_bxsf() -> tuple[float, np.ndarray, np.ndarray, dict[int, np.ndarray]]:
    bxsf_path = PUBLIC_EXAMPLES / 'zrcl2-sc2c' / 'FS' / 'zrclscc_fs.bxsf'
    text = bxsf_path.read_text()
    ef = float(re.search(r'Fermi Energy:\s*([-\d.]+)', text).group(1))
    b1 = np.array([1.000000, 0.577350])
    b2 = np.array([0.000000, 1.154701])
    parts = re.split(r'BAND:\s*(\d+)', text)[1:]
    bands_2d: dict[int, np.ndarray] = {}
    for i in range(0, len(parts), 2):
        bnum = int(parts[i])
        body = parts[i + 1].split('END_BANDGRID_3D')[0]
        vals = np.fromstring(body, sep=' ')
        grid = vals.reshape(65, 65, 2)[:, :, 0] - ef
        bands_2d[bnum] = grid
    return ef, b1, b2, bands_2d


def render_zrcl2_sc2c_electronic() -> None:
    apply_atlas_style()
    k_dist, bands_e, weights = parse_zrcl2_fatbands()
    e_dos, pdos = parse_zrcl2_pdos()
    _, b1, b2, fs_bands = parse_zrcl2_bxsf()

    fig = plt.figure(figsize=(10.2, 4.35))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.985, bottom=0.17, top=0.86,
        width_ratios=[1.32, 0.66, 1.08], wspace=0.26
    )
    gs_left = gs[0, :2].subgridspec(1, 2, width_ratios=[2.05, 1.0], wspace=0.07)
    ax_band = fig.add_subplot(gs_left[0, 0])
    ax_dos = fig.add_subplot(gs_left[0, 1], sharey=ax_band)
    ax_fs = fig.add_subplot(gs[0, 2])

    style_axis(ax_band)
    style_axis(ax_dos)
    style_axis(ax_fs)

    k_ticks = [k_dist[0], k_dist[50], k_dist[100], k_dist[150]]
    for x in k_ticks[1:-1]:
        ax_band.axvline(x, color='#ced8e3', lw=0.85, zorder=1)
    ax_band.axhline(0.0, color=PALETTE['Muted'], ls='--', lw=0.95, zorder=2)
    ax_band.axhspan(-0.16, 0.16, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)

    for ib in range(bands_e.shape[0]):
        ax_band.plot(k_dist, bands_e[ib], color='#9aa8b8', lw=0.8, alpha=0.75, zorder=2)

    orb_styles = [
        ('Cl-3p', PALETTE['Amber'], 48.0, 0.45),
        ('C-2p', PALETTE['Rust'], 54.0, 0.55),
        ('Sc-3d', PALETTE['Teal'], 60.0, 0.60),
        ('Zr-4d', PALETTE['Navy'], 64.0, 0.65),
    ]
    for ib in range(bands_e.shape[0]):
        if np.max(bands_e[ib]) < -2.8 or np.min(bands_e[ib]) > 2.2:
            continue
        for key, color, scale, alpha in orb_styles:
            w = weights[key][ib]
            mask = w > 0.04
            if np.any(mask):
                ax_band.scatter(
                    k_dist[mask],
                    bands_e[ib, mask],
                    s=(w[mask] * scale) + 2.5,
                    facecolors='none',
                    edgecolors=color,
                    linewidths=0.95,
                    alpha=alpha,
                    zorder=4,
                )

    ax_band.set_xlim(k_ticks[0], k_ticks[-1])
    ax_band.set_ylim(-2.5, 2.0)
    ax_band.set_xticks(k_ticks, [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$'])
    ax_band.set_ylabel(r'Energy $E - E_F$ (eV)')
    ax_band.set_title('Orbital fatbands', pad=8)

    legend_handles = [
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Navy'], markeredgewidth=1.3, markersize=5.2, label=r'Zr-$4d$'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Teal'], markeredgewidth=1.3, markersize=5.2, label=r'Sc-$3d$'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Rust'], markeredgewidth=1.3, markersize=5.2, label=r'C-$2p$'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Amber'], markeredgewidth=1.3, markersize=5.2, label=r'Cl-$3p$'),
    ]
    ax_band.legend(handles=legend_handles, loc='lower left', ncol=2, fontsize=8.0)

    ax_band.annotate(
        'Bands 26, 27\n(Zr-$4d$ / Sc-$3d$)',
        xy=(k_dist[24], 0.04),
        xytext=(k_dist[8], 0.92),
        fontsize=8.0,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.8),
    )

    # Panel (b): Horizontal PDOS
    mask_dos = (e_dos >= -2.6) & (e_dos <= 2.1)
    ed = e_dos[mask_dos]
    ax_dos.axhline(0.0, color=PALETTE['Muted'], ls='--', lw=0.95, zorder=2)
    ax_dos.axhspan(-0.16, 0.16, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)

    ax_dos.fill_betweenx(ed, 0, pdos['Total'][mask_dos], color='#dfe6ef', alpha=0.55)
    ax_dos.plot(pdos['Total'][mask_dos], ed, color=PALETTE['Ink'], lw=1.05, label='Total')
    ax_dos.plot(pdos['Zr-4d'][mask_dos], ed, color=PALETTE['Navy'], lw=1.1, label=r'Zr-$4d$')
    ax_dos.plot(pdos['Sc-3d'][mask_dos], ed, color=PALETTE['Teal'], lw=1.1, label=r'Sc-$3d$')
    ax_dos.plot(pdos['C-2p'][mask_dos], ed, color=PALETTE['Rust'], lw=1.05, label=r'C-$2p$')
    ax_dos.plot(pdos['Cl-3p'][mask_dos], ed, color=PALETTE['Amber'], lw=0.95, label=r'Cl-$3p$')

    ax_dos.set_xlim(0, 6.8)
    ax_dos.set_xticks([0, 3, 6])
    ax_dos.set_xlabel('PDOS (eV$^{-1}$)')
    ax_dos.set_title('PDOS', pad=8)
    ax_dos.tick_params(labelleft=False)

    # Panel (c): 2D Hexagonal BZ Fermi Surface
    B = np.column_stack([b1, b2])
    B_inv = np.linalg.inv(B)
    angles = np.deg2rad(np.arange(0, 360, 60))
    R_k = 2.0 / 3.0
    bz_verts = np.column_stack([R_k * np.cos(angles), R_k * np.sin(angles)])

    nx = 220
    kx_lin = np.linspace(-0.75, 0.75, nx)
    ky_lin = np.linspace(-0.75, 0.75, nx)
    KX, KY = np.meshgrid(kx_lin, ky_lin)
    uv = B_inv @ np.vstack([KX.ravel(), KY.ravel()])
    u_mod = np.mod(uv[0], 1.0) * 64.0
    v_mod = np.mod(uv[1], 1.0) * 64.0

    def interp_periodic(grid65: np.ndarray) -> np.ndarray:
        i0 = np.floor(u_mod).astype(int) % 64
        j0 = np.floor(v_mod).astype(int) % 64
        i1 = (i0 + 1) % 64
        j1 = (j0 + 1) % 64
        du = u_mod - np.floor(u_mod)
        dv = v_mod - np.floor(v_mod)
        val = (
            (1 - du) * (1 - dv) * grid65[i0, j0]
            + du * (1 - dv) * grid65[i1, j0]
            + (1 - du) * dv * grid65[i0, j1]
            + du * dv * grid65[i1, j1]
        )
        return val.reshape(KX.shape)

    E26 = interp_periodic(fs_bands[26])
    E27 = interp_periodic(fs_bands[27])

    m_angles = np.deg2rad([30.0, 90.0, 150.0])
    inside_bz = np.ones_like(KX, dtype=bool)
    for ang in m_angles:
        inside_bz &= np.abs(KX * np.cos(ang) + KY * np.sin(ang)) <= (1.0 / np.sqrt(3.0) + 0.004)

    E26_masked = np.where(inside_bz, E26, np.nan)
    E27_masked = np.where(inside_bz, E27, np.nan)

    ax_fs.contourf(
        KX, KY, E26_masked,
        levels=np.linspace(-0.6, 0.4, 22),
        cmap='Blues_r', alpha=0.25, zorder=1,
    )
    ax_fs.contour(KX, KY, E26_masked, levels=[0.0], colors=[PALETTE['Navy']], linewidths=1.85, zorder=4)
    ax_fs.contour(KX, KY, E27_masked, levels=[0.0], colors=[PALETTE['Rust']], linewidths=1.85, zorder=5)

    bz_poly = Polygon(bz_verts, closed=True, fill=False, edgecolor=PALETTE['Ink'], lw=1.2, zorder=6)
    ax_fs.add_patch(bz_poly)

    gamma_pt = np.array([0.0, 0.0])
    m_pt = np.array([0.5, 1.0 / (2.0 * np.sqrt(3.0))])
    k_pt = np.array([1.0 / 3.0, 1.0 / np.sqrt(3.0)])
    path_pts = np.vstack([gamma_pt, m_pt, k_pt, gamma_pt])
    ax_fs.plot(path_pts[:, 0], path_pts[:, 1], color=PALETTE['Slate'], ls='--', lw=0.95, zorder=6)
    ax_fs.scatter([gamma_pt[0], m_pt[0], k_pt[0]], [gamma_pt[1], m_pt[1], k_pt[1]], color=PALETTE['Ink'], s=16, zorder=7)
    ax_fs.text(-0.07, -0.08, r'$\Gamma$', fontsize=8.5, fontweight='bold')
    ax_fs.text(m_pt[0] + 0.03, m_pt[1] - 0.02, r'$M$', fontsize=8.5, fontweight='bold')
    ax_fs.text(k_pt[0] + 0.02, k_pt[1] + 0.03, r'$K$', fontsize=8.5, fontweight='bold')

    fs_handles = [
        Line2D([0], [0], color=PALETTE['Navy'], lw=1.8, label='Band 26'),
        Line2D([0], [0], color=PALETTE['Rust'], lw=1.8, label='Band 27'),
    ]
    ax_fs.legend(handles=fs_handles, loc='lower center', ncol=2, fontsize=8.0)
    ax_fs.set_aspect('equal')
    ax_fs.set_xlim(-0.74, 0.74)
    ax_fs.set_ylim(-0.74, 0.74)
    ax_fs.set_xticks([-0.5, 0.0, 0.5])
    ax_fs.set_yticks([-0.5, 0.0, 0.5])
    ax_fs.set_xlabel(r'$k_x$ ($2\pi/a$)')
    ax_fs.set_ylabel(r'$k_y$ ($2\pi/a$)')
    ax_fs.set_title('2D Fermi surface', pad=8)

    save_figure(fig, PUBLIC_FIGURES / 'zrcl2-sc2c' / 'zrcl2-sc2c-electronic')
    sync_figure_to_mirror('zrcl2-sc2c/zrcl2-sc2c-electronic')


# ---------------------------------------------------------------------------
# 2. ZrCl2/Sc2C Coupled Phonon Dispersion + Linewidth/Lambda + PHDOS + alpha2F
# ---------------------------------------------------------------------------

def parse_gam_lines(filepath: Path, target_broadening: float = 0.0030) -> np.ndarray:
    text = filepath.read_text()
    blocks = re.split(r'Broadening\s+([\d.]+)', text)[1:]
    for i in range(0, len(blocks), 2):
        bval = float(blocks[i])
        if abs(bval - target_broadening) < 1e-5:
            lines = [l.strip() for l in blocks[i + 1].strip().splitlines() if l.strip()]
            gam = np.zeros((151, 18))
            ptr = 0
            for iq in range(151):
                ptr += 1
                vals = []
                while len(vals) < 18 and ptr < len(lines):
                    vals.extend([float(x) for x in lines[ptr].split()])
                    ptr += 1
                gam[iq] = np.maximum(0.0, np.array(vals[:18]) * 1000.0)
            return gam
    raise ValueError(f'Broadening {target_broadening} not found in {filepath}')


def render_zrcl2_sc2c_phonon_epc() -> None:
    apply_atlas_style()
    ph96_dir = PUBLIC_EXAMPLES / 'zrcl2-sc2c' / 'ph96'
    freq_arr = np.loadtxt(ph96_dir / 'zrclscc.freq.gp')
    q_dist = freq_arr[:, 0]
    freqs_thz = freq_arr[:, 1:] * CM1_TO_THZ

    lam_qv_raw = np.loadtxt(ph96_dir / 'elph.lambda_qv.gp')
    lam_qv = lam_qv_raw[:, 2].reshape(18, 151).T
    gam_qv = parse_gam_lines(ph96_dir / 'gam.lines', target_broadening=0.0030)

    phdos_arr = np.loadtxt(ph96_dir / 'zrclscc.phdos', comments='#')
    w_dos_thz = phdos_arr[:, 0] * CM1_TO_THZ
    dos_scale = 33.3564095
    phdos_tot = phdos_arr[:, 1] * dos_scale
    phdos_zr = phdos_arr[:, 2] * dos_scale
    phdos_c = phdos_arr[:, 3] * dos_scale
    phdos_cl = (phdos_arr[:, 4] + phdos_arr[:, 5]) * dos_scale
    phdos_sc = (phdos_arr[:, 6] + phdos_arr[:, 7]) * dos_scale

    a2f_lines = (ph96_dir / 'alpha2F.emax18.dat').read_text().splitlines()[2:]
    e_a2f, a2f_003, a2f_001 = [], [], []
    for idx in range(0, len(a2f_lines), 2):
        r1 = [float(x) for x in a2f_lines[idx].split()]
        e_a2f.append(r1[0])
        a2f_001.append(max(0.0, r1[1]))
        a2f_003.append(max(0.0, r1[3]))
    e_a2f = np.array(e_a2f)
    a2f_003 = np.array(a2f_003)
    a2f_001 = np.array(a2f_001)

    de = e_a2f[1] - e_a2f[0]
    cum_lam_003 = np.zeros_like(e_a2f)
    cum_lam_003[1:] = np.cumsum(2.0 * a2f_003[1:] / e_a2f[1:] * de)

    fig = plt.figure(figsize=(10.2, 4.45))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.98, bottom=0.17, top=0.84,
        width_ratios=[1.42, 0.76, 1.02], wspace=0.12
    )
    ax_ph = fig.add_subplot(gs[0, 0])
    ax_pdos = fig.add_subplot(gs[0, 1], sharey=ax_ph)
    ax_a2f = fig.add_subplot(gs[0, 2], sharey=ax_ph)

    for ax in (ax_ph, ax_pdos, ax_a2f):
        style_axis(ax)
        ax.axhline(10.0, color=PALETTE['Coral'], ls='--', lw=1.05, zorder=3)
        ax.axhspan(12.2, 17.3, color=PALETTE['WarmTint'], alpha=0.55, zorder=0)

    q_ticks = [q_dist[0], q_dist[50], q_dist[100], q_dist[150]]
    for x in q_ticks[1:-1]:
        ax_ph.axvline(x, color='#ced8e3', lw=0.85, zorder=1)

    for nu in range(18):
        ax_ph.plot(q_dist, freqs_thz[:, nu], color='#4a5a70', lw=0.9, alpha=0.85, zorder=2)
        g_vals = gam_qv[:, nu]
        l_vals = lam_qv[:, nu]
        idx_sub = np.arange(0, 151, 3)
        sizes = np.clip(l_vals[idx_sub] * 170.0 + g_vals[idx_sub] * 0.09, 4.0, 95.0)
        ax_ph.scatter(
            q_dist[idx_sub],
            freqs_thz[idx_sub, nu],
            s=sizes,
            c=np.clip(g_vals[idx_sub], 0.0, 650.0),
            cmap='YlOrRd',
            vmin=0.0,
            vmax=600.0,
            edgecolors='#2b3a4d',
            linewidths=0.3,
            alpha=0.84,
            zorder=4,
        )

    ax_ph.set_xlim(q_ticks[0], q_ticks[-1])
    ax_ph.set_ylim(0.0, 18.0)
    ax_ph.set_xticks(q_ticks, [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$'])
    ax_ph.set_ylabel(r'Frequency $\omega$ (THz)')
    ax_ph.set_title(r'Fat-phonon $\gamma_{\mathbf{q}\nu}$ & $\lambda_{\mathbf{q}\nu}$', pad=8)

    ax_ph.annotate(
        r'C-$2p$ branches ($\nu=16\text{–}18$): $\gamma_{\Gamma,18}\approx 686\ \mathrm{GHz}$',
        xy=(q_dist[16], 12.85),
        xytext=(q_dist[14], 11.05),
        fontsize=7.6,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.95),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )
    ax_ph.text(
        q_dist[52], 9.35,
        'Legacy emax = 10 THz',
        fontsize=7.6,
        color=PALETTE['Coral'],
        fontweight='bold',
    )

    # Panel (b): Atom-resolved PHDOS
    ax_pdos.fill_betweenx(w_dos_thz, 0, phdos_tot, color='#dfe6ef', alpha=0.55)
    ax_pdos.plot(phdos_tot, w_dos_thz, color=PALETTE['Ink'], lw=1.0, label='Total')
    ax_pdos.plot(phdos_zr, w_dos_thz, color=PALETTE['Navy'], lw=1.1, label='Zr')
    ax_pdos.plot(phdos_sc, w_dos_thz, color=PALETTE['Teal'], lw=1.1, label='Sc')
    ax_pdos.plot(phdos_cl, w_dos_thz, color=PALETTE['Amber'], lw=1.0, label='Cl')
    ax_pdos.plot(phdos_c, w_dos_thz, color=PALETTE['Rust'], lw=1.2, label='C')

    ax_pdos.set_xlim(0, 3.8)
    ax_pdos.set_xticks([0, 1.5, 3.0])
    ax_pdos.set_xlabel('PHDOS (THz$^{-1}$)')
    ax_pdos.set_title('PHDOS', pad=8)
    ax_pdos.tick_params(labelleft=False)
    ax_pdos.legend(loc='center right', fontsize=7.8)

    # Panel (c): Eliashberg alpha2F(omega) and cumulative lambda(omega)
    ax_a2f.fill_betweenx(e_a2f, 0, a2f_003, color=PALETTE['SoftBlue'], alpha=0.72)
    ax_a2f.plot(a2f_003, e_a2f, color=PALETTE['Navy'], lw=1.35, label=r'$\alpha^2F$ ($\sigma=0.003$)')
    ax_a2f.plot(a2f_001, e_a2f, color=PALETTE['Blue'], lw=0.85, ls=':', alpha=0.85, label=r'$\alpha^2F$ ($\sigma=0.001$)')
    # Plot scaled cumulative lambda(omega) / 2.6 on same x-axis for clean single-axis layout
    lam_scale = 0.36
    ax_a2f.plot(cum_lam_003 * lam_scale, e_a2f, color=PALETTE['Rust'], lw=1.65, label=r'$0.36\times \lambda(\omega)$')

    ax_a2f.set_xlim(0, 1.05)
    ax_a2f.set_xticks([0.0, 0.4, 0.8])
    ax_a2f.set_xlabel(r'$\alpha^2F(\omega)$ & scaled $\lambda(\omega)$')
    ax_a2f.set_title(r'Eliashberg $\alpha^2F(\omega)$', pad=8)
    ax_a2f.tick_params(labelleft=False)

    ax_a2f.text(
        0.22, 13.3,
        r'emax = 18 THz:' + '\n' + r'$\lambda = 2.451$' + '\n' + r'$\omega_{\log}: 83.3\to 85.7\ \mathrm{K}$',
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
    )
    ax_a2f.legend(loc='center right', bbox_to_anchor=(1.0, 0.36), fontsize=7.6)

    save_figure(fig, PUBLIC_FIGURES / 'zrcl2-sc2c' / 'zrcl2-sc2c-phonon-epc')
    sync_figure_to_mirror('zrcl2-sc2c/zrcl2-sc2c-phonon-epc')


# ---------------------------------------------------------------------------
# 3 & 4. ZrCl2/Sc2C k64 vs k96 Crossing Analysis: Tc(sigma) & Spectral Moments
# ---------------------------------------------------------------------------

def load_zrcl2_lambda_series(tag: str, suffix: str = '') -> dict[str, np.ndarray]:
    base = PUBLIC_EXAMPLES / 'zrcl2-sc2c' / tag
    dat_file = base / (f'lambda{suffix}.dat')
    out_file = base / (f'lambdax{suffix}.out')
    arr = np.loadtxt(dat_file, comments='#')
    lines = out_file.read_text().splitlines()
    tc_idx = [i for i, l in enumerate(lines) if 'omega_log' in l and 'T_c' in l][0] + 1
    tc_vals = [float(lines[tc_idx + i].split()[2]) for i in range(arr.shape[0])]
    return {
        'sigma': arr[:, 0],
        'lambda': arr[:, 1],
        'int_a2f': arr[:, 2],
        'wlog': arr[:, 3],
        'nef': arr[:, 4],
        'tc': np.array(tc_vals),
    }


def render_zrcl2_sc2c_k64_k96_tc() -> None:
    apply_atlas_style()
    p64_10 = load_zrcl2_lambda_series('ph64', '')
    p96_10 = load_zrcl2_lambda_series('ph96', '')
    p64_18 = load_zrcl2_lambda_series('ph64', '.emax18')
    p96_18 = load_zrcl2_lambda_series('ph96', '.emax18')
    sigma = p64_18['sigma']

    fig, (ax_tc, ax_diff) = plt.subplots(1, 2, figsize=(10.0, 4.35))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.18, top=0.85, wspace=0.28)
    style_axis(ax_tc)
    style_axis(ax_diff)

    for ax in (ax_tc, ax_diff):
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.72, zorder=0)
        ax.set_xticks([0.005, 0.010, 0.015, 0.020])

    ax_tc.plot(sigma, p64_18['tc'], color=PALETTE['Navy'], marker='o', ms=3.8, lw=1.6, label=r'$64^2$ (emax = 18 THz)')
    ax_tc.plot(sigma, p96_18['tc'], color=PALETTE['Rust'], marker='s', ms=3.6, lw=1.6, label=r'$96^2$ (emax = 18 THz)')
    ax_tc.plot(sigma, p64_10['tc'], color=PALETTE['Navy'], ls='--', lw=1.05, alpha=0.65, label=r'$64^2$ (emax = 10 THz)')
    ax_tc.plot(sigma, p96_10['tc'], color=PALETTE['Rust'], ls='--', lw=1.05, alpha=0.65, label=r'$96^2$ (emax = 10 THz)')

    ax_tc.scatter([0.0036], [13.58], s=58, facecolors='none', edgecolors=PALETTE['Teal'], linewidths=1.8, zorder=6)
    ax_tc.annotate(
        r'Crossing $\sigma^* \approx 0.0036\ \mathrm{Ry}$' + '\n' + r'$T_c \approx 13.58\ \mathrm{K}$ ($\lambda \approx 2.33$)',
        xy=(0.0036, 13.58),
        xytext=(0.0062, 11.6),
        fontsize=8.0,
        bbox=dict(boxstyle='round,pad=0.22', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Teal'], lw=0.95),
    )

    ax_tc.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_tc.set_ylabel(r'Allen–Dynes $T_c(\sigma)$ (K)')
    ax_tc.set_title(r'Dense-grid $T_c(\sigma)$ convergence', pad=8)
    ax_tc.legend(loc='upper right', fontsize=7.8)

    dtc_18 = p64_18['tc'] - p96_18['tc']
    dtc_10 = p64_10['tc'] - p96_10['tc']
    ax_diff.axhline(0.0, color=PALETTE['Ink'], ls='-', lw=0.95, zorder=2)
    ax_diff.plot(sigma, dtc_18, color=PALETTE['Teal'], marker='o', ms=3.8, lw=1.6, label=r'$\Delta T_c$ (emax = 18 THz)')
    ax_diff.plot(sigma, dtc_10, color=PALETTE['Amber'], marker='^', ms=3.6, lw=1.35, ls='--', label=r'$\Delta T_c$ (emax = 10 THz)')

    ax_diff.scatter([0.00175, 0.0031], [0.0, 0.0], color=PALETTE['Amber'], s=36, zorder=5)
    ax_diff.scatter([0.00358], [0.0], color=PALETTE['Teal'], s=44, zorder=6)

    ax_diff.annotate(
        r'Refined ph64.1 / ph96.1:' + '\n' + r'$\Delta\sigma = 0.0005\ \mathrm{Ry}$, emax = 18 THz',
        xy=(0.00358, 0.0),
        xytext=(0.0056, -0.082),
        fontsize=8.0,
        bbox=dict(boxstyle='round,pad=0.22', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Teal'], lw=0.95),
    )

    ax_diff.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_diff.set_ylabel(r'$\Delta T_c(\sigma) = T_{c,64} - T_{c,96}$ (K)')
    ax_diff.set_title(r'Zero-crossing locus $\Delta T_c(\sigma) = 0$', pad=8)
    ax_diff.set_ylim(-0.135, 0.155)
    ax_diff.legend(loc='upper right', fontsize=7.8)

    save_figure(fig, PUBLIC_FIGURES / 'zrcl2-sc2c' / 'zrcl2-sc2c-k64-k96-tc')
    sync_figure_to_mirror('zrcl2-sc2c/zrcl2-sc2c-k64-k96-tc')


def render_zrcl2_sc2c_k64_k96_moments() -> None:
    apply_atlas_style()
    p64_10 = load_zrcl2_lambda_series('ph64', '')
    p96_10 = load_zrcl2_lambda_series('ph96', '')
    p64_18 = load_zrcl2_lambda_series('ph64', '.emax18')
    p96_18 = load_zrcl2_lambda_series('ph96', '.emax18')
    sigma = p64_18['sigma']

    fig, (ax_nef, ax_lam, ax_wlog) = plt.subplots(1, 3, figsize=(10.4, 4.15))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.18, top=0.85, wspace=0.31)
    for ax in (ax_nef, ax_lam, ax_wlog):
        style_axis(ax)
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)
        ax.set_xticks([0.005, 0.012, 0.020])

    # Panel (a): N_sigma(E_F)
    ax_nef.plot(sigma, p64_18['nef'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64\times 64\times 1$')
    ax_nef.plot(sigma, p96_18['nef'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96\times 96\times 1$')
    ax_nef.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_nef.set_ylabel(r'$N_\sigma(E_F)$ (states/spin/Ry)')
    ax_nef.set_title(r'DOS $N_\sigma(E_F)$', pad=8)
    ax_nef.legend(loc='upper right', fontsize=7.8)
    ax_nef.annotate(
        r'Converged for' + '\n' + r'$\sigma \geq 0.004\ \mathrm{Ry}$',
        xy=(0.004, p64_18['nef'][3]),
        xytext=(0.0075, 28.5),
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.85),
    )

    # Panel (b): Direct lambda vs int alpha2F
    ax_lam.plot(sigma, p64_18['lambda'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ direct $\lambda$')
    ax_lam.plot(sigma, p96_18['lambda'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ direct $\lambda$')
    ax_lam.plot(sigma, p64_10['int_a2f'], color=PALETTE['Navy'], ls='--', lw=1.1, alpha=0.7, label=r'$64^2$ int $\alpha^2F$ (10 THz)')
    ax_lam.plot(sigma, p96_10['int_a2f'], color=PALETTE['Rust'], ls='--', lw=1.1, alpha=0.7, label=r'$96^2$ int $\alpha^2F$ (10 THz)')
    ax_lam.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_lam.set_ylabel(r'Coupling $\lambda(\sigma)$')
    ax_lam.set_title(r'Coupling $\lambda(\sigma)$', pad=8)
    ax_lam.legend(loc='upper right', fontsize=7.5)

    # Panel (c): Logarithmic frequency omega_log(sigma)
    ax_wlog.plot(sigma, p64_18['wlog'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ (18 THz)')
    ax_wlog.plot(sigma, p96_18['wlog'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ (18 THz)')
    ax_wlog.plot(sigma, p64_10['wlog'], color=PALETTE['Navy'], ls='--', lw=1.1, alpha=0.7, label=r'$64^2$ (10 THz)')
    ax_wlog.plot(sigma, p96_10['wlog'], color=PALETTE['Rust'], ls='--', lw=1.1, alpha=0.7, label=r'$96^2$ (10 THz)')
    ax_wlog.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_wlog.set_ylabel(r'$\omega_{\log}(\sigma)$ (K)')
    ax_wlog.set_title(r'Log-frequency $\omega_{\log}(\sigma)$', pad=8)
    ax_wlog.legend(loc='upper left', fontsize=7.5)
    ax_wlog.annotate(
        r'$+1.7\text{ to }+8.7\ \mathrm{K}$' + '\n' + r'from C modes',
        xy=(0.015, p96_18['wlog'][14]),
        xytext=(0.0085, 84.5),
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )

    save_figure(fig, PUBLIC_FIGURES / 'zrcl2-sc2c' / 'zrcl2-sc2c-k64-k96-moments')
    sync_figure_to_mirror('zrcl2-sc2c/zrcl2-sc2c-k64-k96-moments')


# ---------------------------------------------------------------------------
# 5. SnSe2/Sr2N Upgraded 3-Panel Diagnostic: SCF + Mass-Corrected Phonon/PHDOS + q=1,2 EPC
# ---------------------------------------------------------------------------

def render_snse2_sr2n_progress() -> None:
    apply_atlas_style()
    sn_dir = PUBLIC_EXAMPLES / 'snse2-sr2n' / 'qe-epc-ph64'
    freq_true = np.loadtxt(sn_dir / 'srnsnse.freq.gp')
    freq_wrong = np.loadtxt(sn_dir / 'srnsnse.wrong_mass.freq.gp')
    q_dist = freq_true[:, 0]
    w_true = freq_true[:, 1:] * CM1_TO_THZ
    w_wrong = freq_wrong[:, 1:] * CM1_TO_THZ

    phdos_arr = np.loadtxt(sn_dir / 'srnsnse.phdos', comments='#')
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

    # Panel (a): Two-stage SCF convergence
    pwxall_acc = [
        4.3e-1, 3.8e-2, 4.4e-3, 1.1e-3, 1.13e-4, 3.04e-5, 2.09e-6, 4.91e-7,
        5.84e-8, 2.26e-8, 3.16e-9, 2.91e-9, 8.22e-10, 3.21e-10, 1.83e-11,
        1.14e-11, 2.02e-12, 6.26e-13,
    ]
    pwx_acc = [
        4.3e-1, 3.8e-2, 4.4e-3, 1.1e-3, 1.13e-4, 3.04e-5, 2.09e-6, 4.91e-7,
        5.84e-8, 2.26e-8, 3.14e-9, 2.92e-9, 8.21e-10, 3.20e-10, 1.80e-11,
        1.14e-11, 1.99e-12, 6.26e-13,
    ]
    iters = np.arange(1, len(pwxall_acc) + 1)
    ax_scf.plot(iters, np.log10(pwxall_acc), color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'pwxall ($64^2$)')
    ax_scf.plot(iters, np.log10(pwx_acc), color=PALETTE['Rust'], marker='s', ms=3.2, lw=1.2, ls='--', label=r'pwx ($16^2$)')
    ax_scf.axhline(-12.0, color=PALETTE['Teal'], ls=':', lw=1.0, label=r'$10^{-12}\ \mathrm{Ry}$')
    ax_scf.set_xlabel('SCF iteration')
    ax_scf.set_ylabel(r'$\log_{10}(\mathrm{SCF\ accuracy\ [Ry]})$')
    ax_scf.set_title('SCF convergence', pad=8)
    ax_scf.legend(loc='upper right', fontsize=7.6)

    # Panel (b): Wrong mass vs True mass Phonon Dispersion + PHDOS
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

    # Panel (c): Completed q=1 and q=2 mode-resolved lambda_qv
    q1_freqs = np.array([-0.2703, -0.2703, 0.1351, 1.2082, 1.2082, 2.2227, 2.6441, 2.6441, 3.5696, 3.5696, 4.3052, 4.3052, 4.3723, 5.3598, 6.6493, 7.9905, 7.9905, 10.7377])
    q1_lam = np.array([0.0000, 0.0000, 0.0000, 0.0077, 0.0077, 0.0161, 0.0016, 0.0017, 0.0035, 0.0035, 0.0018, 0.0019, 0.0181, 0.0146, 0.0049, 0.0025, 0.0025, 0.0183])

    q2_freqs = np.array([0.5844, 0.7615, 1.2260, 1.4783, 1.7871, 2.1003, 2.7314, 2.9384, 3.4150, 3.6312, 4.0439, 4.3107, 4.7574, 5.0819, 6.1879, 7.9570, 9.3685, 10.3345])
    q2_lam = np.array([0.0000, 0.0644, 0.0421, 0.0070, 0.0241, 0.0073, 0.0015, 0.0234, 0.0254, 0.0039, 0.0066, 0.0019, 0.0081, 0.0042, 0.0014, 0.0020, 0.0118, 0.0099])

    ax_epc.axvline(20.0 * CM1_TO_THZ, color=PALETTE['Amber'], ls=':', lw=1.15, zorder=2)
    ax_epc.axvline(10.0, color=PALETTE['Coral'], ls='--', lw=1.0, zorder=2)

    m1, s1, _ = ax_epc.stem(
        np.maximum(0.0, q1_freqs), q1_lam,
        linefmt='-', markerfmt='o', basefmt=' ', label=r'$q=1\ (\Gamma)$',
    )
    plt.setp(m1, color=PALETTE['Navy'], markersize=4.0)
    plt.setp(s1, color=PALETTE['Navy'], linewidth=1.15)

    m2, s2, _ = ax_epc.stem(
        q2_freqs, q2_lam,
        linefmt='--', markerfmt='s', basefmt=' ', label=r'$q=2$',
    )
    plt.setp(m2, color=PALETTE['Rust'], markersize=3.8)
    plt.setp(s2, color=PALETTE['Rust'], linewidth=1.15)

    ax_epc.annotate(
        r'$q=2,\ \nu=2$: $\lambda=0.0644$' + '\n' + r'($\nu=1 < 20\ \mathrm{cm^{-1}}$ cut)',
        xy=(0.7615, 0.0644),
        xytext=(1.85, 0.046),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )
    ax_epc.annotate(
        r'$\nu=18$ ($10.74\ \mathrm{THz}$)' + '\n' + r'$\gamma=27.7\ \mathrm{GHz}$',
        xy=(10.738, 0.0183),
        xytext=(4.35, 0.025),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.85),
    )

    ax_epc.set_xlim(-0.2, 11.4)
    ax_epc.set_ylim(0.0, 0.075)
    ax_epc.set_xlabel(r'Frequency $\omega_{\mathbf{q}\nu}$ (THz)')
    ax_epc.set_ylabel(r'Mode $\lambda_{\mathbf{q}\nu}$ ($\sigma=0.040\ \mathrm{Ry}$)')
    ax_epc.set_title(r'Completed $q=1,2$ EPC', pad=8)
    ax_epc.legend(loc='upper right', fontsize=7.6)

    save_figure(fig, PUBLIC_FIGURES / 'snse2-sr2n' / 'snse2-sr2n-scf-ph-progress')
    sync_figure_to_mirror('snse2-sr2n/snse2-sr2n-scf-ph-progress')


def render_all() -> None:
    render_zrcl2_sc2c_electronic()
    render_zrcl2_sc2c_phonon_epc()
    render_zrcl2_sc2c_k64_k96_tc()
    render_zrcl2_sc2c_k64_k96_moments()
    render_snse2_sr2n_progress()
    print('Rendered all ZrCl2/Sc2C and SnSe2/Sr2N post-processing figures.')


if __name__ == '__main__':
    render_all()
