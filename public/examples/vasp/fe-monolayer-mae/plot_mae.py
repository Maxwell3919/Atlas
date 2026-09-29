import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atlas_plot_style import install as install_atlas_style

install_atlas_style()

# Load MAE summary
r = json.load(open('mae-summary.json'))
k = [p['mesh'] for p in r['pairs']]
e0 = [p['delta_E0_x_minus_z_meV_per_Fe'] for p in r['pairs']]
f = [p['delta_F_x_minus_z_meV_per_Fe'] for p in r['pairs']]

fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.2))
fig.subplots_adjust(top=0.88, bottom=0.15, left=0.07, right=0.98, wspace=0.32)
a, b, c = axes

# Panel a: Mesh convergence
a.axhline(0, color='#888888', lw=0.9, linestyle=':')
a.plot(k, e0, 'o-', color='#0072b2', lw=1.8, ms=7, label=r'$E(\sigma \to 0)$')
a.plot(k, f, 's--', color='#d55e00', lw=1.5, ms=6, label=r'Free energy $F$')
a.set_xticks(k)
a.set_xlabel('In-plane k-mesh division ($N \\times N$)')
a.set_ylabel(r'$\Delta E = E_{[100]} - E_{[001]}$ (meV / Fe)')
a.set_title('(a) MAE k-mesh Convergence')
a.legend(frameon=False, loc='upper left')

for vals, color, shift in [(e0, '#0072b2', 0.07), (f, '#d55e00', -0.09)]:
    for x_val, y_val in zip(k, vals):
        a.text(x_val + 0.35 if x_val == min(k) else x_val - 0.35, y_val + shift,
               f'{y_val:+.4f} meV', ha='left' if x_val == min(k) else 'right',
               color=color, fontsize=8.5, fontweight='bold')
a.margins(y=0.25)
a.text(0.05, 0.22, r'Signs flip from 9$\times$9 to 15$\times$15!' + '\nDense mesh is critical for MAE',
       transform=a.transAxes, fontsize=8, bbox=dict(boxstyle='round,pad=0.3', fc='#fdf6e3', ec='#d0a354', alpha=0.9))

# Panel b: Spin magnetization and orbital anisotropy
for axis, color, mark in [('x', '#d55e00', 's'), ('z', '#0072b2', 'o')]:
    rows = [case for case in r['cases'] if case['name'].endswith('_' + axis)]
    mags = [np.linalg.norm(case['mag_cartesian_muB']) for case in rows]
    b.plot(k, mags, f'{mark}-', color=color, lw=1.6, ms=7, label=f'Moment along [{1 if axis=="x" else 0}0{1 if axis=="z" else 0}]')
    for x_val, y_val in zip(k, mags):
        b.text(x_val, y_val + 0.015, f'{y_val:.4f} ' + r'$\mu_B$', ha='center', color=color, fontsize=8)

b.set_xticks(k)
b.set_xlabel('In-plane k-mesh division ($N \\times N$)')
b.set_ylabel(r'Total Magnetic Moment ($\mu_B$ / Fe)')
b.set_title('(b) Spin Moment vs Orientation')
b.legend(frameon=False, loc='lower right')
b.set_ylim(2.75, 3.05)

# Panel c: Angular energy surface E(theta) = K1 * sin^2(theta)
theta_deg = np.linspace(0, 90, 100)
theta_rad = np.radians(theta_deg)
k1_conv = e0[1] # converged K1 = +0.6399 meV
e_theta = k1_conv * np.sin(theta_rad)**2

c.plot(theta_deg, e_theta, '-', color='#2a9d8f', lw=2.2, label=r'$E(\theta) = K_1 \sin^2\theta$')
c.fill_between(theta_deg, 0, e_theta, color='#2a9d8f', alpha=0.15)
c.scatter([0, 90], [0, k1_conv], color=['#0072b2', '#d55e00'], s=60, zorder=5)
c.text(2, 0.05, 'Easy axis: [001]\n(out-of-plane)', ha='left', color='#0072b2', fontsize=8.5, fontweight='bold')
c.text(88, k1_conv - 0.08, 'Hard axis: [100]\n(in-plane)', ha='right', color='#d55e00', fontsize=8.5, fontweight='bold')

c.set_xticks([0, 30, 45, 60, 90])
c.set_xticklabels([r'0° [001]', r'30°', r'45°', r'60°', r'90° [100]'])
c.set_xlabel(r'Magnetization Polar Angle $\theta$')
c.set_ylabel(r'Relative Energy $E(\theta)$ (meV / Fe)')
c.set_title(r'(c) Angular Energy Profile ($K_1 = +0.64$ meV)')
c.grid(alpha=0.2)
c.legend(frameon=False, loc='center left')

for ax in axes:
    ax.grid(alpha=0.18)

fig.suptitle('Fe Monolayer: Fixed Geometry, $\\sigma = 0.1$ eV (VASP SOC Diagnostics)', fontsize=12, fontweight='bold')
fig.savefig('mae-mesh-check.png', dpi=220)
fig.savefig('mae-mesh-check.pdf')
fig.savefig('mae-mesh-check.svg')
print('mae-mesh-check updated successfully.')
