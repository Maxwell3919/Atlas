# MoS2 acoustic deformation-potential example

Public 3-atom ASE 2H-MoS2 structure, scalar PBE/USPP QE7.5. This example estimates a 300K longitudinal-acoustic deformation-potential model value only. It omits the other scattering channels listed in provenance.json and is not a prediction of complete room-temperature mobility.

- analyse_mobility.py reads native SCF/bands XML, output text, avg.dat and kpoints.csv; use NumPy. It imports mobility_common.py.
- plot_mobility.py reads the CSVs and summary.json; use NumPy and Matplotlib. It generates three PNG/SVG figures.
- The five base-strain configurations have independently accepted fixed-cell internal relaxations. k16 and vacuum28 hold the corresponding accepted k12 positions fixed.
- config.json bands_subdir selects bands-retry for vacuum28-zero, k16-minus005 and k16-plus005, completed by jobs1997,1998,1999. Their original timeout outputs remain in the parent directories. Other configurations use the parent directory bands.
- Native input files, OUT, XML, full scalar potentials averaged along z, Slurm scripts and original/final hashes are included. Three-dimensional potential grids and Bloch wavefunctions are omitted. Accepted SCF charge densities are included, allowing pp.x and fresh bands to be regenerated with their matching archived SCF XML and pseudopotentials.
- Fill in program paths in Slurm scripts before native recalculation. Reproduction starts at base/mos2.vc-relax.in or a supplied accepted strained geometry. Native bands-retry scripts require the matching parent SCF charge density and scf.data-file-schema.xml.
- Run python3 analyse_mobility.py from this directory to recompute tables, then python3 plot_mobility.py. Tables retain units and full precision. Repeated BLAS arithmetic may differ in the last floating-point digits.

manifest.json records hashes before and after public path normalization. Inputs and output numeric values are unchanged. The scientific model assumptions, limits and negative-rho diagnostics are stated in drafts/carrier-mobility/qe.md and provenance.json.
