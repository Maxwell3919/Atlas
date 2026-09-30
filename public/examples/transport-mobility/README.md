# MoS2 acoustic deformation-potential example

QE 7.5 scalar-relativistic PBE/USPP, public ASE 3-atom 2H-MoS2. The model estimates the 300 K longitudinal-acoustic deformation-potential contribution in a parabolic K valley.

## Rebuild the saved analysis

From this directory:
    python3 analyse_mobility.py
    python3 transport_mobility_check.py

The analyzer needs NumPy; the independent SI formula checker uses the standard library. Saved results use Python 3.12.3 / NumPy 2.4.6. Optional plot_mobility.py uses NumPy and Matplotlib (saved figures: 3.11.1), and atlas_plot_style.py in the same directory.

QE OUT, standalone SCF/bands/relax XML, avg.dat, kpoints.csv, configuration files and inputs are supplied. The .save charge-density/wavefunction trees are omitted. Python postprocessing reads the supplied XML snapshots directly. Native pp.x/bands restarts require a newly generated matching SCF .save directory.

## Native QE reproduction

Start from base/mos2.vc-relax.in or the supplied final strained geometry. Replace <qe_bin> and environment setup with your local QE 7.5/MPI paths. The base optimization generates tmp/mos2.save; prepare_mobility_strains.py extracts that final geometry. Each strain run performs relax, copies a standalone XML, then SCF, pp.x, average.x and bands. Run scripts regenerate their matching save trees. The three bands-retry directories need their parent configuration's completed SCF save. Their parent timeout outputs remain historical records; config.json selects the completed retry outputs.

The five strain configurations have fixed transverse lattice components and relaxed internal coordinates. k16 and vacuum28 use the corresponding relaxed baseline positions. quality-gates.json records the accepted scientific criteria.

Coordinate schema: offsetx_invA/offsety_invA hold K-local Cartesian displacements (inverse Angstrom). GammaK_fraction stores the dimensionless t in k=tK for the three Gamma-K scans. Fractional k1/k2/k3 coordinates remain identical to the QE inputs. The coordinate CSV schema was corrected without changing sampling or numerical results.

FILE_SHA256.json lists public-package files. provenance.json gives version, scientific scope and branch selection. Optical, Frohlich, intervalley, piezoelectric, impurity and substrate scattering require additional calculations.
