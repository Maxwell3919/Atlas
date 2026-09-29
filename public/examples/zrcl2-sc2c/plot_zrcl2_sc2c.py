#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import numpy as np

ZR_DIR = Path(__file__).resolve().parent
for candidate in (ZR_DIR, ZR_DIR.parent, ZR_DIR.parents[1] / 'scripts'):
    if (candidate / 'atlas_plot_style.py').exists():
        sys.path.insert(0, str(candidate))
        break

import atlas_plot_style

sys.path.insert(0, str(ZR_DIR))
from tc_table_audit import piecewise_linear_crossings, write_report

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
    ZR_DIR.parents[1] / 'figures' / 'zrcl2-sc2c'
    if (ZR_DIR.parents[1] / 'figures').exists()
    else ZR_DIR / 'figures'
)


def apply_atlas_style() -> None:
    atlas_plot_style.install()


def style_axis(ax) -> None:
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def save_figure(fig, stem_name: str) -> None:
    FIG_OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_OUT_DIR / f'{stem_name}.png')
    plt.close(fig)


def parse_zrcl2_fatbands() -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133  # eV from scf/pwx.out
    data_dir = ZR_DIR / 'scf'
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
    grouped = {key: np.zeros((nbnd, nk)) for key in expected_state_counts}
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
            grouped[key] += state_weights.reshape(nk, nbnd).T
            state_counts[key] += 1

    if ptr != len(proj_lines) or len(seen_state_ids) != natomwfc:
        raise ValueError(f'Projection records do not close cleanly: consumed {ptr}/{len(proj_lines)} lines.')
    if state_counts != expected_state_counts:
        raise ValueError(f'Unexpected selected state counts: {state_counts}')
    if any(not np.isfinite(curve).all() for curve in grouped.values()):
        raise ValueError('Grouped projection weights contain nonfinite values.')
    return k_dist, bands_e, grouped

def parse_zrcl2_pdos() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133
    pdos_dir = ZR_DIR / 'pdos'

    def read_ldos(filename: str) -> tuple[np.ndarray, np.ndarray]:
        arr = np.loadtxt(pdos_dir / filename, comments='#')
        return arr[:, 0] - ef, arr[:, 1]

    e_grid, zr_4d = read_ldos('zrclscc.pdos_atm#1(Zr)_wfc#5(d)')
    _, c_2p = read_ldos('zrclscc.pdos_atm#2(C)_wfc#2(p)')
    _, cl1_3p = read_ldos('zrclscc.pdos_atm#3(Cl)_wfc#2(p)')
    _, cl2_3p = read_ldos('zrclscc.pdos_atm#4(Cl)_wfc#2(p)')
    _, sc1_3d = read_ldos('zrclscc.pdos_atm#5(Sc)_wfc#4(d)')
    _, sc2_3d = read_ldos('zrclscc.pdos_atm#6(Sc)_wfc#4(d)')
    tot_arr = np.loadtxt(pdos_dir / 'zrclscc.pdos_tot', comments='#')

    return e_grid, {
        'Total': tot_arr[:, 1],
        'Zr-4d': zr_4d,
        'Sc-3d': sc1_3d + sc2_3d,
        'C-2p': c_2p,
        'Cl-3p': cl1_3p + cl2_3p,
    }


def parse_zrcl2_bxsf() -> tuple[float, np.ndarray, np.ndarray, dict[int, np.ndarray]]:
    bxsf_path = ZR_DIR / 'FS' / 'zrclscc_fs.bxsf'
    lines = [l.strip() for l in bxsf_path.read_text().splitlines() if l.strip()]
    ef = 0.3154
    for l in lines[:20]:
        if 'Fermi Energy:' in l:
            ef = float(l.split(':')[1].strip())
            break

    b_idx = [i for i, l in enumerate(lines) if l.startswith('BEGIN_BANDGRID_3D')][0]
    nx, ny, nz = [int(x) for x in lines[b_idx + 2].split()]
    b1 = np.array([float(x) for x in lines[b_idx + 4].split()[:2]])
    b2 = np.array([float(x) for x in lines[b_idx + 5].split()[:2]])

    bands: dict[int, np.ndarray] = {}
    ptr = b_idx + 7
    while ptr < len(lines):
        line = lines[ptr]
        if line.startswith('BAND:'):
            b_num = int(line.split(':')[1].strip())
            ptr += 1
            vals: list[float] = []
            while ptr < len(lines) and not lines[ptr].startswith('BAND:') and not lines[ptr].startswith('END_BANDGRID_3D'):
                vals.extend([float(x) for x in lines[ptr].split()])
                ptr += 1
            arr3d = np.array(vals).reshape((nx, ny, nz))
            bands[b_num] = arr3d[:, :, 0] - ef
        else:
            ptr += 1

    return ef, b1, b2, bands


def render_zrcl2_sc2c_electronic() -> None:
    apply_atlas_style()
    k_dist, bands_e, grouped_w = parse_zrcl2_fatbands()
    e_dos, pdos = parse_zrcl2_pdos()
    _, b1, b2, fs_bands = parse_zrcl2_bxsf()

    fig = plt.figure(figsize=(10.2, 4.35))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.985, bottom=0.17, top=0.85,
        width_ratios=[1.35, 0.72, 1.15], wspace=0.22
    )
    ax_band = fig.add_subplot(gs[0, 0])
    ax_dos = fig.add_subplot(gs[0, 1], sharey=ax_band)
    ax_fs = fig.add_subplot(gs[0, 2])

    for ax in (ax_band, ax_dos, ax_fs):
        style_axis(ax)

    k_ticks = [k_dist[0], k_dist[50], k_dist[100], k_dist[150]]
    for x in k_ticks[1:-1]:
        ax_band.axvline(x, color='#ced8e3', lw=0.85, zorder=1)
    ax_band.axhline(0.0, color=PALETTE['Muted'], ls='--', lw=0.95, zorder=2)
    ax_band.axhspan(-0.16, 0.16, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)

    for ib in range(bands_e.shape[0]):
        e_curve = bands_e[ib]
        if e_curve.max() < -2.7 or e_curve.min() > 2.2:
            continue
        ax_band.plot(k_dist, e_curve, color='#7d8b9d', lw=0.85, alpha=0.75, zorder=2)

    orb_specs = [
        ('Cl-3p', PALETTE['Amber'], 72.0),
        ('C-2p', PALETTE['Rust'], 85.0),
        ('Sc-3d', PALETTE['Teal'], 92.0),
        ('Zr-4d', PALETTE['Navy'], 96.0),
    ]
    for label, color, scale in orb_specs:
        w_mat = grouped_w[label]
        for ib in range(bands_e.shape[0]):
            e_curve = bands_e[ib]
            if e_curve.max() < -2.6 or e_curve.min() > 2.1:
                continue
            w = w_mat[ib]
            mask = w > 0.04
            if np.any(mask):
                ax_band.scatter(
                    k_dist[mask],
                    e_curve[mask],
                    s=w[mask] * scale,
                    facecolors='none',
                    edgecolors=color,
                    linewidths=0.95,
                    alpha=0.88,
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

    save_figure(fig, 'zrcl2-sc2c-electronic')


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
    ph96_dir = ZR_DIR / 'ph96'
    freq_arr = np.loadtxt(ph96_dir / 'zrclscc.freq.gp')
    q_dist = freq_arr[:, 0]
    freqs_thz = freq_arr[:, 1:] * CM1_TO_THZ

    gam_qv = parse_gam_lines(ph96_dir / 'gam.lines', target_broadening=0.0030)
    ry_to_thz = 3289.84196
    nef_003 = 30.772452
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

    save_figure(fig, 'zrcl2-sc2c-phonon-epc')


def load_zrcl2_lambda_series(tag: str, suffix: str = '') -> dict[str, np.ndarray]:
    base = ZR_DIR / tag
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
    write_report(ZR_DIR)
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

    save_figure(fig, 'zrcl2-sc2c-k64-k96-tc')


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

    save_figure(fig, 'zrcl2-sc2c-k64-k96-moments')


if __name__ == '__main__':
    render_zrcl2_sc2c_electronic()
    render_zrcl2_sc2c_phonon_epc()
    render_zrcl2_sc2c_k64_k96_tc()
    render_zrcl2_sc2c_k64_k96_moments()
