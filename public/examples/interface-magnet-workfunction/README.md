# SnSe₂ work-function example

This package reproduces the planar potential and vacuum-referenced levels for one fixed-geometry, non-spin-polarized SnSe₂ monolayer SCF run (VASP 5.4.4, executed 2026-09-22). It demonstrates the analysis route; the single calculation does not establish convergence with respect to vacuum thickness, cutoff energy, or k-point density.

## Contents

- <code>POSCAR</code>, <code>INCAR</code>, <code>KPOINTS</code>: the actual calculation inputs.
- <code>OUTCAR</code>, <code>OSZICAR</code>, <code>EIGENVAL</code>, <code>LOCPOT</code>, <code>CHGCAR</code>: the transferred outputs from that same run.
- <code>POTCAR.identity.txt</code>: PAW titles, <code>ZVAL</code>, and the source-file SHA256 only. The licensed POTCAR data are not included; obtain the matching files from your own authorized installation.
- <code>analyze_workfunction.py</code>: strict parser and analysis for this scalar, <code>ISPIN=1</code>, gapped example.
- <code>plot_workfunction.py</code>, <code>atlas_plot_style.py</code>: redraw one full-cell potential profile with the actual vacuum windows, atomic z extent, Fermi level, and work-function marker.
- <code>PLANAR_AVERAGE.dat</code>, <code>potential-summary.json</code>, <code>workfunction-summary.json</code>: generated analysis outputs.
- <code>interface-magnet-workfunction-profile.png</code>, <code>.svg</code>, <code>.pdf</code>: figure exports.
- <code>plane_average.py</code> and <code>workfunction_values.py</code>: original two-step helpers included for line-by-line inspection. <code>analyze_workfunction.py</code> is the strict reconstruction route used for the article figure.
- The earlier three-panel diagnostic and its script remain in the sibling evidence directory <code>provenance/diagnostic-iterations/</code>; its zoom panels magnified only a numerically negligible inter-side difference, so it is not the article figure.

## Run

Install Python 3, NumPy, and Matplotlib. From this directory:

~~~bash
python3 analyze_workfunction.py --windows 1:3 15:17
python3 plot_workfunction.py
~~~

The analyzer rewrites <code>PLANAR_AVERAGE.dat</code> and <code>workfunction-summary.json</code>. It fails on unsupported spin-polarized or metallic inputs, missing convergence markers, a non-<code>LVHAR</code> potential, malformed grids, and partially occupied band-edge states. Window flatness diagnostics are reported rather than silently ignored.

## File format and calculation

<code>LOCPOT</code> begins with a POSCAR-like structure header, followed by the three grid dimensions (<code>60 60 280</code>) and one scalar electrostatic-potential block in eV. The analyzer reads the complete block, reshapes it as <code>(nz, ny, nx)</code> because x varies fastest in VASP's file, and averages each xy plane:

$$
\bar V(z_k)=\frac{1}{N_xN_y}\sum_{i=1}^{N_x}\sum_{j=1}^{N_y}V_{ijk}.
$$

For this cell, the normal height is 18.357298 Å and the z grid spacing is that height divided by 280. <code>OUTCAR</code> supplies <code>E_F</code> and is checked for <code>EDIFF</code> convergence, <code>LVHAR=T</code>, <code>LVTOT=F</code>, <code>ISPIN=1</code>, and <code>NELECT=26</code>. <code>EIGENVAL</code> supplies occupations and eigenvalues on the 33×33×1 SCF mesh; the script checks the k-point weights and electron count before identifying the sampled VBM and CBM.

For each user-selected vacuum window, the script reports the mean, standard deviation, and range of $\bar V(z)$, and calculates

$$
\Phi=\bar V_{\mathrm{vac}}-E_F,\quad I=\bar V_{\mathrm{vac}}-E_{\mathrm{VBM}},\quad A=\bar V_{\mathrm{vac}}-E_{\mathrm{CBM}}.
$$

Here $\Phi$ is the work function, while $I$ and $A$ are the ionization potential and electron affinity estimated from the sampled semilocal DFT band edges. The edge search is limited to the input SCF mesh. In a semiconductor, VASP's printed <code>E-fermi</code> depends on the occupation setup and may lie anywhere within the gap, so the work function must be reported with that convention stated.

## Result and limits

The 1–3 Å and 15–17 Å windows contain 30 and 31 planes. Their means are 3.306283412 and 3.306265353 eV, with local ranges 0.0000607 and 0.0001460 eV. The lower-z window gives $\Phi=5.784583412$ eV at the printed <code>E-fermi</code> of −2.478300 eV. The upper-minus-lower vacuum mean is −0.01806 meV, reported as a numerical check only; it is below the precision at which this calculation supports a material interpretation.

Window spread describes local flatness only. It is not a statistical error bar and says nothing about convergence to another cell, cutoff, or k mesh. The full-cell profile is the only figure retained for analysis: it shows the vacuum plateau, atomic region, and measured vacuum-to-Fermi separation without magnifying the tiny difference between the two sides. Inspect the complete planar profile, confirm each chosen window lies in vacuum and away from a dipole-correction jump, then test larger vacuum and tighter numerical settings before presenting a material value.

