Diamond QE 7.5 / LOBSTER 6.0.0 teaching example

Replot the native nonmagnetic outputs:
  python3 plot_cohp.py
Requires NumPy >= 2.0 and Matplotlib. The script creates three web PNGs,
three vector PDFs and figures/plot-checks.json. Arial/Helvetica is preferred;
DejaVu Sans is used if neither is installed. No wavefunctions are needed to replot.

The four main cases use the same fixed two-atom diamond geometry and PAW file.
The basis-koga and basis-pbe directories are same-wavefunction diagnostics;
they do not establish independent basis-space convergence.

To rerun QE, first download the exact PAW into a new pseudo/ directory:
https://pseudopotentials.quantum-espresso.org/upf_files/C.pbe-n-kjpaw_psl.0.1.UPF
SHA256: f147c19f79e4539c4490226dc2b68560f335e4a2008b1c7b2fdda94f2456ad32
This is the 2018 atomic 6.3 file, not the older same-named example file.
Replace <qe_bin> and <lobster_bin> in each batch script with your installation.
Adapt only the scheduler/resource lines for your cluster, keeping the calculation
parameters fixed for a comparison. Recreate each .save by running its own SCF.
LOBSTER must be obtained separately from its official distributor.

The archive deliberately omits executables, manuals, UPF and large wavefunctions.
Native numerical input/output text and XML are copied without numerical edits.
Only absolute software locations in batch scripts are replaced for publication.
See provenance.json and SHA256SUMS for the exact public files.
