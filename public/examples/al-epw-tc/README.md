# Al spectrum to EPW 6.0 isotropic Eliashberg solver

This package contains actual inputs and computational outputs, with private absolute paths replaced. Original and public SHA256 values are paired in source-public-sha256.json. Program binaries and libraries are not included.

The source alpha2F.dat comes from a real QE 7.5 double-grid calculation, not EPW Wannier interpolation. It has 2000 rows and ten smearing columns. The converter selects sigma=0.020 Ry, changes THz to meV, and removes only the (0,0) row. The source lambda.in last line is mu*=0.10; its first-line 0.12 is the spectral Gaussian width in THz.

prepare_spectrum.py writes a spectrum-only crystal.fmt adapter from the real parent QE XML. It converts atomic masses to the native Rydberg mass unit, pads unused species slots to ntypx=10, and does not generate Wannier centers. The final replay jobs are 888-904. Job895 is the preserved above-Tc nonlinear sweep failure; the other final cases completed. All successful spectra/eigenvalues/gaps are unchanged by the mass-unit correction, as recorded in mass-unit-replay-check.json. Earlier zero-grid and short-mass-array input failures are retained in failed-* directories.

Reanalyse and redraw in this directory:

    python3 analyse_tc.py
    python3 plot_tc.py

The analysis needs the Python standard library. The converter also needs NumPy; plotting needs Matplotlib. The included plot_tc.py and atlas_plot_style.py reproduce the exact final site layout. They write PNG/SVG web previews and separate 183 mm vector PDFs; data are unchanged.

To rerun EPW, replace <qe_bin> and <软件环境> in run.sh with your installed EPW 6.0 executable directory and environment loader. Source SCF inputs are provenance; their pseudo_dir is redacted to ./pseudo. No SCF/DFPT is run by this package. Do not interpret the nonzero 1³ guard dimensions of the standalone input as an interpolated k/q mesh.

At fixed input muc=0.10, the actual linear crossings are [1.46,1.47] K at requested cutoff0.10 eV, [1.45,1.46] K at0.20eV, and [1.57,1.58] K at0.40eV. These are conditional solver results, not an accepted material Tc or evidence of cutoff convergence. The nonlinear plotted quantity is Delta(i omega0,T), not a real-axis excitation gap. The failed1.50K nonlinear branch is never replaced by an accepted zero-gap point.
