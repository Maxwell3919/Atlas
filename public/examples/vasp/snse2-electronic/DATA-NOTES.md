# SnSe2 electronic data

Dataset: fixed three-atom SnSe2, VASP 5.4.4, PBE, 400 eV, no spin polarization/SOC. The runtime also records IVDW=11.

scf: uniform 18x18x1 mesh (37 irreducible points), static NSW=0, DOSCAR with 301 energies.
bands: three line-mode segments, 150 points, 20 bands, complete PROCAR.

parameters-from-output.txt is a documented reconstruction from the actual vasprun.xml <incar> plus resolved output parameters. It is not a byte-exact historical INCAR. The archived SCF INCAR was subsequently edited to 520 eV and is intentionally not provided as a run input.
incar-run.xml preserves the actual run's <incar> block; original vasprun.xml is included. IVDW is taken from OUTCAR because VASP 5.4.4 did not echo it in the <incar> block.

SYSTEM=SnS2 is a stale label. POSCAR and PAW identifiers establish Sn1Se2.
POTCAR payload and CHGCAR/wavefunctions are not distributed. PAW/POTCAR startup sections are removed from public OUTCAR; TITEL/ZVAL only retained. Runtime/electronic output is preserved.
The original parent charge-density hash and matching structure/PAW were checked internally, including the density grid mean of 26.0000020568 electrons.

All figures use the parent-SCF efermi (-2.39071823 eV). The path-reported efermi (-2.38897901 eV) is retained in summary.json but not used for a separate zero.
Path extrema are not a full-BZ convergence result. DOS is from the actual static SCF, not a new dense NSCF; its ~0.11 eV energy step exceeds SIGMA=0.05 eV. No smoothing/interpolation was applied to DOS.
extract_inputs.py, analyse.py and plot.py regenerate the published tables and figures from this package. No electronic calculation was performed for this publication step.

In the original archive, bands/CHGCAR is a symbolic link to ../scf/CHGCAR, established before the recorded final band run. readlink resolution and SHA-256 match the same parent file. The public package intentionally does not include that link or the density payload.
