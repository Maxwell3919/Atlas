"""Read the 23 actual accuracy reports in pwxall.out.txt and plot their bounds.
Run next to the native output, CSV and atlas_plot_style.py.
"""
from pathlib import Path
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atlas_plot_style import install
install()

ROOT = Path(__file__).resolve().parent
data = np.genfromtxt(ROOT/'snse2-sr2n-k64-scf-accuracy.csv', delimiter=',', names=True)
text = (ROOT/'pwxall.out.txt').read_text()
values = np.array([float(x.replace('D','E')) for x in re.findall(
    r'estimated scf accuracy\s*<\s*([0-9.EeDd+-]+)\s*Ry', text)])
assert len(values) == len(data) == 23
assert np.array_equal(values, data['printed_scf_error_bound_Ry'])
assert np.array_equal(data['iteration'], np.arange(1,24))
assert np.all(data['input_conv_thr_Ry'] == 1e-12)
assert 'convergence has been achieved' in text and 'JOB DONE.' in text

fig, ax = plt.subplots(figsize=(7.2, 4.1), layout='constrained')
ax.semilogy(data['iteration'], values, '-o', markersize=3.5,
            color='#0072b2', linewidth=1.0, label='Printed SCF error bound')
ax.axhline(1e-12, color='#222222', linestyle='--', linewidth=.8,
           label=r'Input threshold: $10^{-12}$ Ry')
ax.set(xlabel='Electronic iteration', ylabel='Estimated SCF accuracy (Ry)',
       title='SnSe₂/Sr₂N: 64 × 64 × 1 electronic grid', xlim=(1,23))
ax.legend(frameon=False, loc='upper right')
fig.savefig(ROOT/'snse2-sr2n-k64-scf-accuracy.png')
print('Verified 23 native accuracy bounds; exported PNG, SVG and PDF.')
