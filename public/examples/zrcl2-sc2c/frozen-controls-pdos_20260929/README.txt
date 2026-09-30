Frozen-Control PDOS Package
Generated: 2026-09-29 (Asia/Shanghai)
Slurm job: 8272
Attempt: frozen-pdos-20260929-a1
Source directory:
<calculation-directory>/frozen_controls_pdos_20260929/

Purpose
Compare near-Fermi projected DOS for frozen-geometry
ZrCl2/Sc2C heterostructures and matched isolated Sc2C controls
at 0% and +1.5% strain.

Cases and Fermi energies from QE pw.x
heterostructure 0%: 0.3522 eV
isolated Sc2C 0%: -2.1388 eV
heterostructure +1.5%: 0.3133 eV
isolated Sc2C +1.5%: -2.1362 eV

Electronic-structure protocol
Quantum ESPRESSO 7.2; PBE; vdW-DF3-opt1.
ecutwfc=100 Ry; ecutrho=800 Ry; 32x32x1 k mesh.
SCF Gaussian smearing 0.0037 Ry; conv_thr=1e-12 Ry.
projwfc: ngauss=0; degauss=0.0022 Ry;
DeltaE=0.005 eV; lsym=true.

Projection grouping and numerical checks
Heterostructure atoms: #1 Zr, #2 C, #3/#4 Cl, #5/#6 Sc.
Atoms #2/#5/#6 are summed as the Sc2C layer;
atoms #1/#3/#4 are summed as the ZrCl2 layer.
All m-resolved columns from every atom/wfc file are summed.
Isolated controls sum all Sc2C atom/wfc projectors.
The energy grid is 0.005 eV; 10,378-10,533 rows per case.
Projected layer sums are checked against column 3 of pdos_tot.
Integrated L1 mismatch within EF +/- 0.1 eV: 0.070-0.086%.
Maximum absolute mismatch is 0.146-0.186% of total-PDOS peak.

Interpretation limits
Each plotted spectrum is shifted by its own Fermi energy.
The plot compares spectral shape and weight near EF only.
It does not establish absolute band offsets or charge transfer.
All coordinates are frozen; these are not relaxed equilibria.
Parent heterostructure force residuals: 2.40e-4 Ry/Bohr at 0%;
1.20e-4 Ry/Bohr at +1.5%.

Package files
frozen_pdos.png and frozen_pdos.pdf: two-panel comparison.
frozen_pdos_long.csv: energy-resolved group and total PDOS.
frozen_pdos_summary.csv: Fermi levels, grids and sum checks.
plot_frozen_pdos.py: reproducible plotting and validation script.
Re-run from the project calculation directory with:
python3 delivery/plot_frozen_pdos.py


Atom mapping (QE ATOMIC_POSITIONS order)
Heterostructure: #1 Zr, #2 C, #3-4 Cl, #5-6 Sc.
Sc2C layer = #2 C + #5-6 Sc; ZrCl2 layer = #1 Zr + #3-4 Cl.
Isolated Sc2C control: #1-2 Sc, #3 C.

