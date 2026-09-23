# Native EPW interpolation spectrum to isotropic Tc

This independent package uses the exact native al.a2f and crystal.fmt from EPW6.0 interpolation job2013: coarse12^3 k /4^3 q; fine24^3 k /12^3 q; electronic smearing0.10eV, phonon smearing0.5meV, acoustic cutoff0.1cm^-1, crystal ASR. It is separate from the QE lambda.x spectrum solver package.

The 500 positive-frequency native rows are read directly, without unit conversion or deletion. Each native row has frequency(meV), alpha2F, and cumulative lambda. EPW reads the first two columns and ignores the footer after nqstep=500. The source spectrum SHA is f48a3230b47468b6fb813d9b5cabe6df5b7133ae1f13af1f2317300e3dd3cabf, crystal SHA d7eb5bf83ce9635747149b54582171bad4071f4f86ed00e59b55d557e356cbf2.

Run python3 analyse_tc.py in this directory to regenerate linear.csv, gap.csv, source-spectrum.csv, solver-status.json, and tc-brackets.json. The script needs only Python standard library. Paths in inputs/outputs are redacted; source-public-sha256.json pairs raw and public hashes. Replace <qe_bin> and <软件环境> before using the actual run.sh files to recalculate.

Jobs905,906,907 completed with exit0:0. The conditional crossing is [0.84,0.85]K at input mu*=0.10 and cutoff0.10eV; the low-temperature nonlinear solution at0.25K has Delta(iomega0)=0.12821328449meV after11iterations. Native integrated spectrum lambda=.3508982 differs from discrete summed lambda=.3507955; do not substitute one for the other. This is not a materialTc convergence claim. A single low-temperature gap value is not a temperature sweep or real-axis excitation gap.

Redraw the native spectrum and Tc plot with `python3 plot_native_tc.py`. Keep atlas_plot_style.py in the same folder; NumPy and Matplotlib are required. PNG/SVG and a 183 mm vector PDF are written to figures/.
