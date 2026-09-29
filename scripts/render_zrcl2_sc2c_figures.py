#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import shutil
import sys

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

sys.path.insert(0, str(PUBLIC_EXAMPLES / 'zrcl2-sc2c'))
from tc_table_audit import piecewise_linear_crossings, write_report

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
    return


# ---------------------------------------------------------------------------
# 1. ZrCl2/Sc2C Coupled Electronic Structure: Orbital Fatbands + PDOS + 2D FS
# ---------------------------------------------------------------------------

def parse_zrcl2_fatbands() -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133  # eV from scf/pwx.out
    data_dir = PUBLIC_EXAMPLES / 'zrcl2-sc2c' / 'scf'
    gnu_path = data_dir / 'bands.dat.gnu'
    proj_path = data_dir / 'fatbands.projwfc_up'
    proj_lines = [line for line in proj_path.read_text().splitlines() if line.strip()]
    header_rows = [
        idx for idx, line in enumerate(proj_lines[:30])
        if len(line.split()) == 3 and all(part.isdigit() for part in line.split())
    ]
    if len(header_rows) != 1:
        raise ValueError(f'Expected one projection header; found {len(header_rows)}.')
    header_idx = header_rows[0]
    natomwfc, nk, nbnd = map(int, proj_lines[header_idx].split())
    if header_idx + 2 >= len(proj_lines):
        raise ValueError('Projection header is missing its spin flags or first state.')
    spin_flags = proj_lines[header_idx + 1].split()
    if len(spin_flags) != 2 or any(flag not in {'T', 'F'} for flag in spin_flags):
        raise ValueError(f'Unexpected projection spin flags: {spin_flags}')
    ptr = header_idx + 2

    # bands.dat.gnu stores each band as one contiguous nk-row block.
    raw = np.loadtxt(gnu_path)
    if raw.shape != (nbnd * nk, 2) or not np.isfinite(raw).all():
        raise ValueError(f'Unexpected bands.dat.gnu shape or nonfinite values: {raw.shape}')
    band_blocks = raw.reshape(nbnd, nk, 2)
    k_blocks = band_blocks[:, :, 0]
    if not np.allclose(k_blocks, k_blocks[0:1], rtol=0.0, atol=1e-8):
        raise ValueError('The k-distance sequence differs between band blocks.')
    k_dist = k_blocks[0]
    if not np.isclose(k_dist[0], 0.0, rtol=0.0, atol=1e-8):
        raise ValueError(f'Band path does not start at zero: {k_dist[0]}')
    if np.any(np.diff(k_dist) < -1e-8) or k_dist[-1] <= k_dist[0]:
        raise ValueError('Band path distances are not a forward, nonzero path.')
    bands_e = band_blocks[:, :, 1] - ef

    atom_elements = {1: 'Zr', 2: 'C', 3: 'Cl', 4: 'Cl', 5: 'Sc', 6: 'Sc'}
    group_by_site_orbital = {
        (1, 'D'): 'Zr-4d',
        (5, 'D'): 'Sc-3d',
        (6, 'D'): 'Sc-3d',
        (2, 'P'): 'C-2p',
        (3, 'P'): 'Cl-3p',
        (4, 'P'): 'Cl-3p',
    }
    expected_state_counts = {'Zr-4d': 5, 'Sc-3d': 10, 'C-2p': 3, 'Cl-3p': 6}
    weights = {key: np.zeros((nbnd, nk)) for key in expected_state_counts}
    state_counts = {key: 0 for key in expected_state_counts}
    expected_ik = np.repeat(np.arange(1, nk + 1), nbnd)
    expected_ib = np.tile(np.arange(1, nbnd + 1), nk)
    block_len = nk * nbnd
    seen_state_ids = set()

    for expected_state in range(1, natomwfc + 1):
        if ptr >= len(proj_lines):
            raise ValueError(f'Projection file ended before state {expected_state}.')
        hdr = proj_lines[ptr].split()
        if len(hdr) < 4:
            raise ValueError(f'Malformed state header at line {ptr + 1}: {hdr}')
        state_id, atom_id = int(hdr[0]), int(hdr[1])
        element, orbital = hdr[2], hdr[3].upper()
        if state_id != expected_state or state_id in seen_state_ids:
            raise ValueError(f'Unexpected or duplicate state id {state_id}; expected {expected_state}.')
        seen_state_ids.add(state_id)
        if atom_id not in atom_elements or element != atom_elements[atom_id]:
            raise ValueError(f'State {state_id} has atom/element mismatch: #{atom_id} {element}.')
        angular_parts = [char for char in orbital if char in 'SPDF']
        if len(angular_parts) != 1:
            raise ValueError(f'State {state_id} has unrecognized orbital label {orbital}.')
        key = group_by_site_orbital.get((atom_id, angular_parts[0]))
        ptr += 1
        rows = []
        for row_index in range(block_len):
            if ptr >= len(proj_lines):
                raise ValueError(f'State {state_id} ended at projection row {row_index}.')
            fields = proj_lines[ptr].split()
            if len(fields) != 3:
                raise ValueError(f'Malformed projection row at line {ptr + 1}: {fields}')
            rows.append((int(fields[0]), int(fields[1]), float(fields[2])))
            ptr += 1
        state_data = np.asarray(rows, dtype=float)
        if not np.array_equal(state_data[:, 0].astype(int), expected_ik):
            raise ValueError(f'State {state_id} has an unexpected k-index sequence.')
        if not np.array_equal(state_data[:, 1].astype(int), expected_ib):
            raise ValueError(f'State {state_id} has an unexpected band-index sequence.')
        state_weights = state_data[:, 2]
        if not np.isfinite(state_weights).all():
            raise ValueError(f'State {state_id} contains nonfinite projection weights.')
        if key is not None:
            weights[key] += state_weights.reshape(nk, nbnd).T
            state_counts[key] += 1

    if ptr != len(proj_lines) or len(seen_state_ids) != natomwfc:
        raise ValueError(f'Projection records do not close cleanly: consumed {ptr}/{len(proj_lines)} lines.')
    if state_counts != expected_state_counts:
        raise ValueError(f'Unexpected selected state counts: {state_counts}')
    if any(not np.isfinite(curve).all() for curve in weights.values()):
        raise ValueError('Grouped projection weights contain nonfinite values.')
    return k_dist, bands_e, weights

def parse_zrcl2_pdos() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133
    pdos_dir = PUBLIC_EXAMPLES / 'zrcl2-sc2c' / 'pdos'
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
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Navy'], markeredgewidth=1.3, markersize=5.2, label=r'Zr-$4d$ [#1]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Teal'], markeredgewidth=1.3, markersize=5.2, label=r'Sc-$3d$ [#5+#6]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Rust'], markeredgewidth=1.3, markersize=5.2, label=r'C-$2p$ [#2]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Amber'], markeredgewidth=1.3, markersize=5.2, label=r'Cl-$3p$ [#3+#4]'),
    ]
    ax_band.legend(handles=legend_handles, loc='lower left', ncol=2, fontsize=8.0)

    ax_band.annotate(
        'Bands 26, 27\n(Zr-$4d$ [#1] / Sc-$3d$ [#5+#6])',
        xy=(k_dist[24], 0.04),
        xytext=(k_dist[8], 0.92),
        fontsize=8.0, zorder=10,
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
    ax_dos.plot(pdos['Zr-4d'][mask_dos], ed, color=PALETTE['Navy'], lw=1.1, label=r'Zr-$4d$ [#1]')
    ax_dos.plot(pdos['Sc-3d'][mask_dos], ed, color=PALETTE['Teal'], lw=1.1, label=r'Sc-$3d$ [#5+#6]')
    ax_dos.plot(pdos['C-2p'][mask_dos], ed, color=PALETTE['Rust'], lw=1.05, label=r'C-$2p$ [#2]')
    ax_dos.plot(pdos['Cl-3p'][mask_dos], ed, color=PALETTE['Amber'], lw=0.95, label=r'Cl-$3p$ [#3+#4]')

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

    stem_path = PUBLIC_FIGURES / 'zrcl2-sc2c' / 'zrcl2-sc2c-electronic'
    fig.savefig(stem_path.with_suffix('.pdf'))
    fig.savefig(stem_path.with_suffix('.svg'))
    save_figure(fig, stem_path)

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

    gam_qv = parse_gam_lines(ph96_dir / 'gam.lines', target_broadening=0.0030)
    # Exact dimensionless mode coupling lambda_qv = gamma_qv / (pi * N(Ef) * omega_qv^2) in Ry units
    ry_to_thz = 3289.84196
    nef_003 = 30.772452  # states/spin/Ry/cell from ph96/elph.inp_lambda.1 at sigma=0.003 Ry
    w_ry = np.maximum(freqs_thz, 0.25) / ry_to_thz
    g_ry = (gam_qv / 1000.0) / ry_to_thz
    lam_qv = np.where(freqs_thz > 0.25, g_ry / (np.pi * nef_003 * (w_ry ** 2)), 0.0)

    phdos_arr = np.loadtxt(ph96_dir / 'zrclscc.phdos', comments='#')
    w_dos_thz = phdos_arr[:, 0] * CM1_TO_THZ
    dos_scale = 33.3564095
    phdos_tot = phdos_arr[:, 1] * dos_scale
    phdos_zr = phdos_arr[:, 2] * dos_scale
    phdos_c = phdos_arr[:, 3] * dos_scale
    phdos_cl = (phdos_arr[:, 4] + phdos_arr[:, 5]) * dos_scale
    phdos_sc = (phdos_arr[:, 6] + phdos_arr[:, 7]) * dos_scale

    a2f_lines = (ph96_dir / 'alpha2F.dat').read_text().splitlines()[2:]
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
        sizes = np.clip(l_vals[idx_sub] * 26.0 + g_vals[idx_sub] * 0.14, 4.0, 95.0)
        ax_ph.scatter(
            q_dist[idx_sub],
            freqs_thz[idx_sub, nu],
            s=sizes,
            c=np.clip(g_vals[idx_sub], 0.0, 340.0),
            cmap='YlOrRd',
            vmin=0.0,
            vmax=330.0,
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
        r'C-atom optical modes ($\nu=16\text{–}18$): $\gamma_{\Gamma,17\text{–}18}\approx 322\ \mathrm{GHz}$',
        xy=(q_dist[8], 15.45),
        xytext=(q_dist[10], 11.20),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.95),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )
    ax_ph.text(
        q_dist[54], 9.05,
        'Saved input emax = 10 THz',
        fontsize=7.5,
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
    lam_scale = 0.36
    ax_a2f.plot(cum_lam_003 * lam_scale, e_a2f, color=PALETTE['Rust'], lw=1.65, label=r'$0.36\times \lambda(\omega)$')

    ax_a2f.set_xlim(0, 1.05)
    ax_a2f.set_xticks([0.0, 0.4, 0.8])
    ax_a2f.set_xlabel(r'$\alpha^2F(\omega)$ & scaled $\lambda(\omega)$')
    ax_a2f.set_title(r'Saved $\alpha^2F(\omega)$ (emax = 10 THz)', pad=8)
    ax_a2f.tick_params(labelleft=False)

    ax_a2f.text(
        0.22, 13.3,
        'Input: 10 0.12 1\n18-THz output provenance open',
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
    sigma = p64_10['sigma']
    write_report(PUBLIC_EXAMPLES / 'zrcl2-sc2c')
    roots10 = piecewise_linear_crossings(sigma, p64_10['tc'], p96_10['tc'])
    roots18 = piecewise_linear_crossings(sigma, p64_18['tc'], p96_18['tc'])

    fig, (ax_tc, ax_diff) = plt.subplots(1, 2, figsize=(10.0, 4.35))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.18, top=0.85, wspace=0.28)
    style_axis(ax_tc)
    style_axis(ax_diff)

    for ax in (ax_tc, ax_diff):
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.72, zorder=0)
        ax.set_xticks([0.005, 0.010, 0.015, 0.020])

    ax_tc.plot(sigma, p64_18['tc'], color=PALETTE['Navy'], marker='o', ms=3.8, lw=1.6, label=r'$64^2$ stored 18-THz table (source open)')
    ax_tc.plot(sigma, p96_18['tc'], color=PALETTE['Rust'], marker='s', ms=3.6, lw=1.6, label=r'$96^2$ stored 18-THz table (source open)')
    ax_tc.plot(sigma, p64_10['tc'], color=PALETTE['Navy'], ls='--', lw=1.05, alpha=0.7, label=r'$64^2$ matched 10-THz input')
    ax_tc.plot(sigma, p96_10['tc'], color=PALETTE['Rust'], ls='--', lw=1.05, alpha=0.7, label=r'$96^2$ matched 10-THz input')

    for i, root in enumerate(roots10):
        ax_tc.scatter([root['sigma_ry']], [root['tc_k']], marker='^', s=42, color=PALETTE['Amber'], zorder=6, label='10-THz table roots' if i == 0 else None)
    for i, root in enumerate(roots18):
        ax_tc.scatter([root['sigma_ry']], [root['tc_k']], s=58, facecolors='none', edgecolors=PALETTE['Teal'], linewidths=1.8, zorder=7, label='18-THz stored-table root (source open)' if i == 0 else None)
    if roots18:
        root = roots18[0]
        ax_tc.annotate(
            f"Stored 18-THz table\n$\\sigma={root['sigma_ry']:.6f}$ Ry, $T_c={root['tc_k']:.3f}$ K\ninput/run record unlinked",
            xy=(root['sigma_ry'], root['tc_k']),
            xytext=(0.0062, 11.6),
            fontsize=7.7,
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
            arrowprops=dict(arrowstyle='->', color=PALETTE['Teal'], lw=0.95),
        )

    ax_tc.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_tc.set_ylabel(r'Stored Allen–Dynes $T_c(\sigma)$ (K)')
    ax_tc.set_title(r'Stored $T_c$ tables and interpolated roots', pad=8)
    ax_tc.legend(loc='upper right', fontsize=7.4)

    dtc_18 = p64_18['tc'] - p96_18['tc']
    dtc_10 = p64_10['tc'] - p96_10['tc']
    ax_diff.axhline(0.0, color=PALETTE['Ink'], ls='-', lw=0.95, zorder=2)
    ax_diff.plot(sigma, dtc_18, color=PALETTE['Teal'], marker='o', ms=3.8, lw=1.6, label=r'$\Delta T_c$ (18-THz stored tables)')
    ax_diff.plot(sigma, dtc_10, color=PALETTE['Amber'], marker='^', ms=3.6, lw=1.35, ls='--', label=r'$\Delta T_c$ (matched 10-THz inputs)')
    for root in roots10:
        ax_diff.scatter([root['sigma_ry']], [0.0], marker='^', color=PALETTE['Amber'], s=42, zorder=6)
    for root in roots18:
        ax_diff.scatter([root['sigma_ry']], [0.0], color=PALETTE['Teal'], s=48, zorder=7)
    ax_diff.text(
        0.035, 0.055,
        'Prepared ph64.1/ph96.1\nrefinement has no complete Tc pair',
        transform=ax_diff.transAxes,
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
    )

    ax_diff.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_diff.set_ylabel(r'$\Delta T_c(\sigma) = T_{c,64} - T_{c,96}$ (K)')
    ax_diff.set_title(r'Linear-interpolation roots of $\Delta T_c=0$', pad=8)
    ax_diff.set_ylim(-0.135, 0.155)
    ax_diff.legend(loc='upper right', fontsize=7.4)

    save_figure(fig, PUBLIC_FIGURES / 'zrcl2-sc2c' / 'zrcl2-sc2c-k64-k96-tc')
    sync_figure_to_mirror('zrcl2-sc2c/zrcl2-sc2c-k64-k96-tc')


def render_zrcl2_sc2c_k64_k96_moments() -> None:
    apply_atlas_style()
    p64 = load_zrcl2_lambda_series('ph64', '')
    p96 = load_zrcl2_lambda_series('ph96', '')
    sigma = p64['sigma']

    fig, (ax_nef, ax_lam, ax_wlog) = plt.subplots(1, 3, figsize=(10.4, 4.15))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.18, top=0.85, wspace=0.31)
    for ax in (ax_nef, ax_lam, ax_wlog):
        style_axis(ax)
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)
        ax.set_xticks([0.005, 0.012, 0.020])

    ax_nef.plot(sigma, p64['nef'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64\times 64\times 1$')
    ax_nef.plot(sigma, p96['nef'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96\times 96\times 1$')
    ax_nef.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_nef.set_ylabel(r'$N_\sigma(E_F)$ (states/spin/Ry)')
    ax_nef.set_title(r'$N_\sigma(E_F)$ from stored tables', pad=8)
    ax_nef.legend(loc='upper right', fontsize=7.6)
    ax_nef.annotate(
        'Close for $\\sigma\\geq0.004$ Ry\n(two grids; no convergence proof)',
        xy=(0.004, p64['nef'][3]),
        xytext=(0.0075, 28.5),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.85),
    )

    ax_lam.plot(sigma, p64['lambda'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ direct $\lambda$')
    ax_lam.plot(sigma, p96['lambda'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ direct $\lambda$')
    ax_lam.plot(sigma, p64['int_a2f'], color=PALETTE['Navy'], ls='--', lw=1.1, alpha=0.75, label=r'$64^2$ $\int\alpha^2F$ (10 THz)')
    ax_lam.plot(sigma, p96['int_a2f'], color=PALETTE['Rust'], ls='--', lw=1.1, alpha=0.75, label=r'$96^2$ $\int\alpha^2F$ (10 THz)')
    ax_lam.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_lam.set_ylabel(r'Coupling $\lambda(\sigma)$')
    ax_lam.set_title(r'10-THz input: $\lambda$ and $\int\alpha^2F$', pad=8)
    ax_lam.legend(loc='upper right', fontsize=7.2)

    ax_wlog.plot(sigma, p64['wlog'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ (10-THz input)')
    ax_wlog.plot(sigma, p96['wlog'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ (10-THz input)')
    ax_wlog.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_wlog.set_ylabel(r'$\omega_{\log}(\sigma)$ (K)')
    ax_wlog.set_title(r'Stored $\omega_{\log}$ (10-THz input)', pad=8)
    ax_wlog.legend(loc='upper left', fontsize=7.2)
    ax_wlog.text(
        0.04, 0.04,
        'Frequency grid ends at 10 THz',
        transform=ax_wlog.transAxes,
        fontsize=7.3,
        color=PALETTE['Muted'],
    )

    save_figure(fig, PUBLIC_FIGURES / 'zrcl2-sc2c' / 'zrcl2-sc2c-k64-k96-moments')
    sync_figure_to_mirror('zrcl2-sc2c/zrcl2-sc2c-k64-k96-moments')


# ---------------------------------------------------------------------------
# 5. SnSe2/Sr2N Upgraded 3-Panel Diagnostic: SCF + Mass-Corrected Phonon/PHDOS + q=1,2 EPC
# ---------------------------------------------------------------------------

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
    apply_atlas_style()
    sn_dir = PUBLIC_EXAMPLES / 'snse2-sr2n' / 'ph64'
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
    fig.text(0.075, 0.925, '2026-09-29: SCF completed; ph.x stopped at Gamma. Middle/right panels are archived earlier snapshots.', color=PALETTE['Rust'], fontsize=8.2)
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

    # Panel (a): Real 23-step Two-stage SCF convergence from pwxall.out.txt and pwx.out.txt
    pwxall_acc = [
        float(m.group(1))
        for m in re.finditer(r'estimated scf accuracy\s*<\s*([\d.E+-]+)\s*Ry', (sn_dir / 'pwxall.out.txt').read_text())
    ]
    pwx_acc = [
        float(m.group(1))
        for m in re.finditer(r'estimated scf accuracy\s*<\s*([\d.E+-]+)\s*Ry', (sn_dir / 'pwx.out.txt').read_text())
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
    ax_ph.set_title('Archived mass-restored phonons', pad=8)
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

    # Panel (c): Exact q=1 and q=2 mode-resolved lambda_qv from elph.inp_lambda.1,2
    q1_freqs, q1_lam = parse_elph_inp_lambda(sn_dir / 'elph.inp_lambda.1', target_broadening=0.040)
    q2_freqs, q2_lam = parse_elph_inp_lambda(sn_dir / 'elph.inp_lambda.2', target_broadening=0.040)

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
        r'$q=2,\ \nu=2$: $\lambda=' + f'{q2_lam[1]:.4f}' + r'$' + '\n' + r'($\nu=1 < 20\ \mathrm{cm^{-1}}$ cut)',
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
    ax_epc.set_title(r'Archived $q=1,2$ EPC (pre-mass-fix)', pad=8)
    ax_epc.legend(loc='upper right', fontsize=7.6)

    save_figure(fig, PUBLIC_FIGURES / 'snse2-sr2n' / 'snse2-sr2n-scf-ph-progress')
    sync_figure_to_mirror('snse2-sr2n/snse2-sr2n-scf-ph-progress')


# ---------------------------------------------------------------------------
# 6–10. Five New Real Calculation Figures for Manual Pages Previously Missing Plots
# ---------------------------------------------------------------------------

def render_si_and_zrcl2_scf() -> None:
    apply_atlas_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.2))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.18, top=0.85, wspace=0.28)
    style_axis(ax1)
    style_axis(ax2)

    # Panel (a): Diamond Si 8x8x8 SCF from si-pbe/scf/scf.out.txt
    si_iters = np.arange(1, 10)
    si_acc = np.array([0.05540955, 0.00288592, 0.00011028, 0.00001356, 0.00000035, 0.00000016, 5.6e-9, 4.7e-10, 4.3e-11])
    si_etot = np.array([-22.83581101, -22.83770169, -22.83851531, -22.83858648, -22.83859190, -22.83859227, -22.83859229, -22.83859230, -22.83859230])
    si_de = np.maximum(np.abs(si_etot - si_etot[-1]), 1e-11)

    ax1.plot(si_iters, np.log10(si_acc), color=PALETTE['Navy'], marker='o', ms=4.2, lw=1.6, label='Estimated SCF accuracy')
    ax1.plot(si_iters[:-1], np.log10(si_de[:-1]), color=PALETTE['Rust'], marker='s', ms=3.8, lw=1.35, ls='--', label=r'$|E_n - E_{\mathrm{final}}|$')
    ax1.axhline(-10.0, color=PALETTE['Teal'], ls=':', lw=1.05, label=r'$\mathrm{conv\_thr} = 10^{-10}\ \mathrm{Ry}$')
    ax1.set_xlabel('Davidson SCF iteration')
    ax1.set_ylabel(r'$\log_{10}(\mathrm{Energy\ residual\ [Ry]})$')
    ax1.set_title(r'Gapped Si ($8\times 8\times 8$, monotonic)', pad=8)
    ax1.legend(loc='upper right', fontsize=7.8)
    ax1.annotate(
        'Converged at step 9:\n' + r'$F_{\mathrm{tot}} = 0.000\ \mathrm{Ry/au}$' + '\n' + r'$P = +38.45\ \mathrm{kbar}$',
        xy=(9, np.log10(4.3e-11)),
        xytext=(4.5, -9.2),
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.85),
    )

    # Panel (b): 2D metallic ZrCl2/Sc2C 64x64x1 SCF from ph64/pwxall.out
    pwxall_out = (PUBLIC_EXAMPLES / 'zrcl2-sc2c' / 'ph64' / 'pwxall.out').read_text()
    zr_acc = [float(m.group(1)) for m in re.finditer(r'estimated scf accuracy\s*<\s*([-\d.Ee+]+)', pwxall_out)]
    zr_iters = np.arange(1, len(zr_acc) + 1)
    ax2.plot(zr_iters, np.log10(zr_acc), color=PALETTE['Navy'], marker='o', ms=3.2, lw=1.45, label=r'ZrCl$_2$/Sc$_2$C ($64\times 64\times 1$)')
    ax2.axhline(-12.0, color=PALETTE['Teal'], ls=':', lw=1.05, label=r'$\mathrm{conv\_thr} = 10^{-12}\ \mathrm{Ry}$')
    ax2.set_xlabel('Davidson SCF iteration')
    ax2.set_ylabel(r'$\log_{10}(\mathrm{Estimated\ SCF\ accuracy\ [Ry]})$')
    ax2.set_title(r'2D metallic heterostructure (charge sloshing)', pad=8)
    ax2.legend(loc='upper right', fontsize=7.8)
    ax2.annotate(
        f'Converged in {len(zr_acc)} steps\n' + r'($E_F = 0.3130\ \mathrm{eV}$, $\sigma = 0.0037\ \mathrm{Ry}$)',
        xy=(len(zr_acc), np.log10(zr_acc[-1])),
        xytext=(16, -10.8),
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.85),
    )

    save_figure(fig, PUBLIC_FIGURES / 'scf' / 'si-and-zrcl2-scf')
    sync_figure_to_mirror('scf/si-and-zrcl2-scf')


def render_fe_vasp_scf() -> None:
    apply_atlas_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.2))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.18, top=0.85, wspace=0.28)
    style_axis(ax1)
    style_axis(ax2)

    # bcc Fe 18 DAV iterations from fe-scf/OSZICAR
    iters = np.arange(1, 19)
    de = np.array([63.592, 80.118, 1.6570, 9.8735e-3, 1.4064e-4, 1.6080, 8.3938e-2, 1.2719e-2, 1.4696e-2, 1.0035e-4, 3.1870e-5, 4.9697e-6, 2.5440e-6, 1.7455e-6, 9.8581e-8, 2.0253e-8, 1.4517e-8, 3.0582e-9])
    rms = np.array([111.0, 20.7, 4.17, 0.272, 3.22e-2, 6.14, 1.45, 9.12e-2, 7.47e-2, 3.47e-2, 1.03e-2, 2.95e-3, 1.79e-3, 1.13e-3, 1.62e-4, 6.64e-5, 1.89e-5, 9.41e-6])
    rmsc_iters = np.arange(5, 18)
    rmsc = np.array([1.69, 0.695, 0.453, 0.193, 3.38e-2, 9.81e-3, 4.34e-3, 2.95e-3, 1.47e-3, 2.31e-4, 5.04e-5, 2.25e-5, 5.42e-6])

    ax1.axvspan(1, 5.5, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)
    ax1.plot(iters, np.log10(de), color=PALETTE['Navy'], marker='o', ms=3.8, lw=1.55, label=r'$|\Delta E|$ (eV)')
    ax1.plot(iters, np.log10(rms), color=PALETTE['Teal'], marker='^', ms=3.5, lw=1.25, ls='--', label='Wavefunction rms')
    ax1.plot(rmsc_iters, np.log10(rmsc), color=PALETTE['Rust'], marker='s', ms=3.5, lw=1.45, label='Charge mixing rms(c)')
    ax1.axhline(-8.0, color=PALETTE['Coral'], ls=':', lw=1.05, label=r'$\mathrm{EDIFF} = 10^{-8}\ \mathrm{eV}$')
    ax1.set_xlabel('VASP DAV iteration')
    ax1.set_ylabel(r'$\log_{10}(\mathrm{Residual})$')
    ax1.set_title('bcc Fe SCF convergence (NELMDL = -5)', pad=8)
    ax1.legend(loc='upper right', fontsize=7.5)
    ax1.text(1.35, -7.5, 'Frozen rho\n(steps 1–5)', fontsize=7.6, color=PALETTE['Slate'])

    # Panel (b): Orbital charge & magnetization per Fe atom from fe-scf/OUTCAR
    orbs = ['s', 'p', 'd', 'Total / Fe']
    chg_per_fe = [0.502, 0.574, 6.265, 7.341]
    mag_per_fe = [-0.013, -0.058, 2.170, 2.098]
    x = np.arange(len(orbs))
    w = 0.36
    ax2.bar(x - w / 2, chg_per_fe, width=w, color=PALETTE['Navy'], alpha=0.85, label='Charge (e / Fe)')
    ax2.bar(x + w / 2, mag_per_fe, width=w, color=PALETTE['Rust'], alpha=0.88, label=r'Magnetization ($\mu_B$ / Fe)')
    ax2.axhline(0.0, color=PALETTE['Ink'], lw=0.8)
    ax2.set_xticks(x, orbs)
    ax2.set_ylabel(r'Orbital projection ($e$ or $\mu_B$ per Fe)')
    ax2.set_title(r'Spin-resolved Fe-$3d$ moment & stress check', pad=8)
    ax2.legend(loc='upper left', fontsize=7.8)
    ax2.annotate(
        r'$m_d = +2.170\ \mu_B$/Fe' + '\n' + r'Cell $\mathrm{mag} = 4.2127\ \mu_B$' + '\n' + r'$P_{\mathrm{ext}} = +56.94\ \mathrm{kbar}$',
        xy=(2 + w / 2, 2.170),
        xytext=(0.15, 4.1),
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )

    save_figure(fig, PUBLIC_FIGURES / 'scf' / 'fe-vasp-scf-convergence')
    sync_figure_to_mirror('scf/fe-vasp-scf-convergence')


def render_si_nscf_grid() -> None:
    apply_atlas_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.2))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.18, top=0.85, wspace=0.28)
    style_axis(ax1)
    style_axis(ax2)

    # Panel (a): Conduction band valley along Gamma-X and discrete k-grid sampling
    kx_fine = np.linspace(0.55, 1.0, 200)
    vbm_ev = 6.397029
    # Parabolic fit around actual valley minimum k0 = 0.844, E_min = 6.9369 eV
    e_cbm_curve = (6.9369 - vbm_ev) + 4.55 * ((kx_fine - 0.844) ** 2)
    ax1.plot(kx_fine, e_cbm_curve, color='#8a99ad', lw=1.25, ls='-', label=r'$\Delta$-valley CBM dispersion')

    for ngrid, color, marker, offset, label in [
        (8, PALETTE['Amber'], '^', 0.0, r'Parent SCF $8^3$ (4 bands only)'),
        (12, PALETTE['Navy'], 'o', 0.0, r'NSCF $12^3$ ($k_x = 5/6 \approx 0.833$)'),
        (18, PALETTE['Rust'], 's', 0.0, r'NSCF $18^3$ ($k_x = 8/9 \approx 0.889$)'),
        (24, PALETTE['Teal'], 'D', 0.0, r'NSCF $24^3$ ($k_x = 20/24 \approx 0.833$)'),
    ]:
        pts = np.array([i / (ngrid / 2) for i in range(ngrid // 2 + 1) if 0.55 <= i / (ngrid / 2) <= 1.0])
        vals = (6.9369 - vbm_ev) + 4.55 * ((pts - 0.844) ** 2)
        if ngrid == 8:
            ax1.scatter(pts, np.full_like(pts, 0.515), color=color, marker=marker, s=38, zorder=5, label=label)
        else:
            ax1.scatter(pts, vals, color=color, marker=marker, s=42, zorder=6, label=label)

    ax1.axvline(0.844, color=PALETTE['Ink'], ls=':', lw=0.95)
    ax1.set_xlim(0.55, 1.02)
    ax1.set_ylim(0.50, 0.92)
    ax1.set_xlabel(r'Wavevector along $\Gamma\text{–}X$ ($2\pi/a$)')
    ax1.set_ylabel(r'$E_{\mathrm{CBM}}(k_x) - E_{\mathrm{VBM}}$ (eV)')
    ax1.set_title(r'Discrete $k$-mesh sampling near $\Delta$ valley', pad=8)
    ax1.legend(loc='upper left', fontsize=7.4)

    # Panel (b): Indirect gap & IBZ k-point count across NSCF runs from gap-results.json
    labels = [r'$12^3$' + '\n(SCF $8^3$)', r'$18^3$' + '\n(SCF $8^3$)', r'$24^3$' + '\n(SCF $8^3$)', r'$24^3$' + '\n(SCF $12^3$)']
    gaps = [0.54013, 0.55032, 0.54013, 0.54083]
    nks = [72, 195, 413, 413]
    x = np.arange(len(labels))
    ax2.plot(x, gaps, color=PALETTE['Navy'], marker='o', ms=5.0, lw=1.6, label='Indirect band gap (eV)')
    for xi, gi, nk in zip(x, gaps, nks):
        ax2.annotate(
            f'{gi:.4f} eV\n({nk} IBZ k-pts)',
            xy=(xi, gi),
            xytext=(xi - 0.32, gi + (0.0022 if xi != 1 else -0.0042)),
            fontsize=7.6,
            bbox=dict(boxstyle='round,pad=0.16', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        )
    ax2.set_xticks(x, labels)
    ax2.set_ylim(0.534, 0.556)
    ax2.set_ylabel('Extracted indirect gap (eV)')
    ax2.set_title('NSCF grid vs parent charge-density check', pad=8)

    save_figure(fig, PUBLIC_FIGURES / 'nscf' / 'si-nscf-grid-sampling')
    sync_figure_to_mirror('nscf/si-nscf-grid-sampling')


def render_vge2p4_dftu() -> None:
    apply_atlas_style()
    import tarfile
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.2))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.18, top=0.85, wspace=0.28)
    style_axis(ax1)
    style_axis(ax2)

    tar_path = PUBLIC_EXAMPLES / 'vasp' / 'vge2p4-dft-u3-files.tar.gz'
    with tarfile.open(tar_path) as tf:
        osz_lines = tf.extractfile('vge2p4-dft-u3/OSZICAR').read().decode().splitlines()
        eig_lines = tf.extractfile('vge2p4-dft-u3/EIGENVAL').read().decode().splitlines()

    iters, etot, rmsc_iters, rmsc = [], [], [], []
    for l in osz_lines:
        if l.startswith('DAV:'):
            parts = l.split()
            it = int(parts[1])
            iters.append(it)
            etot.append(float(parts[2]))
            if len(parts) >= 7:
                rmsc_iters.append(it)
                rmsc.append(float(parts[6]))

    ax1.plot(iters, etot, color=PALETTE['Navy'], marker='o', ms=3.4, lw=1.5, label=r'Total energy $E_n$ (eV)')
    ax1.set_ylim(-43.0, -33.0)
    ax1.set_xlabel('VASP DAV iteration (31 steps)')
    ax1.set_ylabel('Total energy (eV)')
    ax1.set_title(r'VGe$_2$P$_4$ DFT+$U$ ($U_{\mathrm{eff}}=3.0\ \mathrm{eV}$) convergence', pad=8)
    ax1.annotate(
        'Onset of charge & on-site\noccupancy matrix mixing\n(steps 5–8 jump)',
        xy=(7, -42.117),
        xytext=(11.5, -41.5),
        fontsize=7.6,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )

    # Parse EIGENVAL (37 k-points, 56 bands, spin-polarized)
    ef = 2.4194
    nk, nbnd = 37, 56
    up_bands = np.zeros((nk, nbnd))
    dn_bands = np.zeros((nk, nbnd))
    ptr = 7
    for ik in range(nk):
        while ptr < len(eig_lines) and not eig_lines[ptr].strip():
            ptr += 1
        ptr += 1  # k-point coords line
        for ib in range(nbnd):
            parts = eig_lines[ptr].split()
            up_bands[ik, ib] = float(parts[1]) - ef
            dn_bands[ik, ib] = float(parts[2]) - ef
            ptr += 1

    k_idx = np.arange(1, nk + 1)
    for ib in range(nbnd):
        if np.any((up_bands[:, ib] > -2.2) & (up_bands[:, ib] < 2.2)):
            lbl_u = 'Spin up' if ib == 28 else None
            lbl_d = 'Spin down' if ib == 28 else None
            ax2.plot(k_idx, up_bands[:, ib], color=PALETTE['Navy'], lw=0.95, alpha=0.85, label=lbl_u)
            ax2.plot(k_idx, dn_bands[:, ib], color=PALETTE['Rust'], lw=0.95, ls='--', alpha=0.85, label=lbl_d)

    ax2.axhline(0.0, color=PALETTE['Ink'], ls='--', lw=0.9)
    ax2.set_xlim(1, nk)
    ax2.set_ylim(-1.8, 1.8)
    ax2.set_xlabel('Irreducible k-point index (1..37)')
    ax2.set_ylabel(r'$E_{n\mathbf{k}\sigma} - E_F$ (eV)')
    ax2.set_title(r'Spin-polarized Kohn–Sham states ($\mathrm{mag}=0.578\ \mu_B$)', pad=8)
    ax2.legend(loc='upper right', fontsize=7.8)

    save_figure(fig, PUBLIC_FIGURES / 'dft-plus-u' / 'vge2p4-dftu-diagnostics')
    sync_figure_to_mirror('dft-plus-u/vge2p4-dftu-diagnostics')


def render_al_and_zrcl2_vcrelax() -> None:
    apply_atlas_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.2))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.18, top=0.85, wspace=0.28)
    style_axis(ax1)
    style_axis(ax2)

    # Panel (a): fcc Al 5-step BFGS vc-relax from al/relax-ibrav/al.relax.out
    al_steps = np.arange(1, 6)
    al_press = np.array([-7.91, -4.63, 0.08, 0.05, 0.02])
    al_a_ang = np.array([3.96883, 3.96145, 3.95620, 3.95607, 3.95607])

    ax1.axhline(0.0, color='#9aa8b8', ls=':', lw=0.9)
    ax1.plot(al_steps, al_press, color=PALETTE['Navy'], marker='o', ms=4.5, lw=1.6, label='Hydrostatic pressure P (kbar)')
    ax1.set_xticks(al_steps)
    ax1.set_xlabel('BFGS vc-relax step')
    ax1.set_ylabel('Pressure P (kbar)')
    ax1.set_title('fcc Al 3D vc-relax convergence', pad=8)
    ax1.legend(loc='lower right', fontsize=7.8)
    ax1.annotate(
        r'Converged ($P = +0.02\ \mathrm{kbar}$)' + '\n' + r'$a_0 = 3.95607\ \mathrm{\AA}$',
        xy=(5, 0.02),
        xytext=(2.3, -5.2),
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.85),
    )

    # Panel (b): 2D ZrCl2/Sc2C cell_dofree='2Dxy' 19-step BFGS vc-relax
    zr_forces = np.array([
        0.015061, 0.011906, 0.004416, 0.002965, 0.002221, 0.002367, 0.002641,
        0.001781, 0.000727, 0.000462, 0.000490, 0.000592, 0.000605, 0.000371,
        0.000253, 0.000180, 0.000112, 0.000098, 0.000098
    ])
    zr_steps = np.arange(1, len(zr_forces) + 1)
    ax2.plot(zr_steps, zr_forces * 1000.0, color=PALETTE['Rust'], marker='s', ms=3.5, lw=1.5, label='Total force (mRy/Bohr)')
    ax2.axhline(0.15, color=PALETTE['Teal'], ls=':', lw=1.0, label='forc_conv_thr')
    ax2.set_xlabel('BFGS vc-relax step (cell_dofree = 2Dxy)')
    ax2.set_ylabel('Total force (mRy/Bohr)')
    ax2.set_title(r'ZrCl$_2$/Sc$_2$C 2D in-plane vc-relax', pad=8)
    ax2.legend(loc='upper right', fontsize=7.8)
    ax2.annotate(
        r'Final force $0.098\ \mathrm{mRy/Bohr}$' + '\n' + r'$\Delta E = -0.69\ \mathrm{mRy}$',
        xy=(18, 0.098),
        xytext=(7.5, 6.2),
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )

    save_figure(fig, PUBLIC_FIGURES / 'vc-relax' / 'al-and-zrcl2-vcrelax')
    sync_figure_to_mirror('vc-relax/al-and-zrcl2-vcrelax')


def render_all() -> None:
    render_zrcl2_sc2c_electronic()
    render_zrcl2_sc2c_phonon_epc()
    render_zrcl2_sc2c_k64_k96_tc()
    render_zrcl2_sc2c_k64_k96_moments()
    render_snse2_sr2n_progress()
    render_si_and_zrcl2_scf()
    render_fe_vasp_scf()
    render_si_nscf_grid()
    render_vge2p4_dftu()
    render_al_and_zrcl2_vcrelax()
    print('Rendered all 10 post-processing figure sets.')


if __name__ == '__main__':
    render_all()

