BHZ TOOL CHECK — provenance and reproduction

This is the unchanged official WannierTools v2.7.2 BHZ-model case1 generator,
commit 30360705dd8381214e36d259b9f45671bc47fbfb:
https://github.com/quanshengwu/wannier_tools/tree/v2.7.2/examples/BHZ-model
Both original generator and wt.in-normal are in upstream/. No DFT was run.
C s pz are formal model site/orbital labels, not a carbon-material calculation.
M=2 B=1 A=1 Delta0=0 are model eV parameters, not HgTe or heterostructure fits.
The original generator prints seven unit degeneracies for five R points; the
Fortran reader takes five from that header record. verify_bhz.py does the same.

Calculation executable source tag v2.6.2, commit
5f08aafcb6dcb604c184e0b2f3832f42df0b0cce. The embedded banner still says 2.6.1.
The default output line 'obtained from VASP' is a package-format label, not the
provenance of this generated model. Source and input define actual provenance.
GNU Fortran 13.3, system BLAS/LAPACK, serial, OPENBLAS_NUM_THREADS=1.
An optional MKL-only sparse call is guarded in wt262-build-fix.diff so a GNU
build links and rejects that unsupported branch explicitly. Dense adaptive WCC and
surface routines used here are unchanged. GNU GPLv3 source license: COPYING.

Rebuild in an independent directory:
git clone --branch v2.6.2 --depth 1 https://github.com/quanshengwu/wannier_tools wt262
cd wt262
patch -p1 < /absolute/path/to/wt262-build-fix.diff
cd src
make -f Makefile.gfortran f90='gfortran -cpp' libs='-llapack -lblas /lib/x86_64-linux-gnu/libarpack.so.2'
Use the actual system library path on your Linux installation.
No profile/environment modification is needed. V2.7.2 failed this GNU build;
this package does not claim that failed version is operational.

From the package root, Python3 with NumPy generates and verifies:
python3 upstream/BHZ_hr_gen-case1.py
(cd n41-final && OPENBLAS_NUM_THREADS=1 /absolute/path/to/wt262/bin/wt.x > run.out)
(cd n81-final && OPENBLAS_NUM_THREADS=1 /absolute/path/to/wt262/bin/wt.x > run.out)
python3 verify_bhz.py
gnuplot plot_bhz.gnu

Inputs define the same four spinor bands, occupied2, zero Zeeman, KPLANE first
vector full b1 and transverse half b2, with input Nk1=Nk2=41/81. WCC output has41/81 transverse points, not a
fixed41x41/81x81 loop integration. main.f90 calls wannier_center3D_plane_adaptive.
The loop routine starts from32 and doubles until wcc_calc_tol=0.08 is met;
the neighbour tolerance is0.30 and can also add transverse points. This run
added none:41/81 final transverse rows. WT.out records final loop points64/128:
for Nk2=41,39 loops have64 and2 have128; for Nk2=81,79 have64 and2 have128.
Max recorded loop changes are0.0503207641/0.0257763349 respectively.
Nk1=41/81 does not specify the actual loop link count in this call. Agreement
with inversion parity is an interface check, not a high-precision integral
convergence claim. Plot legend labels Nk2 transverse sampling only.
SURFACE uses z,x,y:
periodic x (z has no hopping), open y, same bulk HR, no added boundary potential.
For this WT SlabSS implementation eta=3*(OmegaMax-OmegaMin)/OmegaNum, not an
input Fermi_broadening: eta=15/401=0.0374064837905eV (surfstat.f90 line84).
Omega(j) excludes upper endpoint; nearest to zero is -0.006234414eV.
Output dos.dat_l/bulk column3 is natural-log LDOS (surfstat.f90 lines237/239).
Plot maps accumulated path length linearly to specified fractional kx=-.5..+.5;
this avoids relying on the raw path header's unit label. No interpolation or
branch connection is applied to WCC points. Surface colors are the actual WT
log output; weights are not presented as an absolute normalized physical DOS.
checks.json records TR, inversion, Hermiticity, finite-grid gap, TRIM parity,
WCC endpoint pairs and both numerical Z2 verdicts. This software check does not
validate any material SOC DFT/Wannier Hamiltonian, Ising or superconductivity.

References:
BHZ original four-band TR model and edge discussion:
https://doi.org/10.1126/science.1133734 ; https://arxiv.org/pdf/cond-mat/0611399
Fu-Kane inversion parity test, Eqs1.1/1.2:
https://doi.org/10.1103/PhysRevB.76.045302 ; https://arxiv.org/pdf/cond-mat/0611341
WT:
https://doi.org/10.1016/j.cpc.2017.09.033
https://wannier-tools.readthedocs.io/en/latest/features.html
