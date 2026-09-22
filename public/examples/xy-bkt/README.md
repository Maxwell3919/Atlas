# Classical square-lattice XY Monte Carlo example

Independent dimensionless numerical model. J=kB=1; no material parameter mapping.
Python 3.12 and NumPy 2.4.6 were used. No software was installed for this run.

## Inspect and draw

`python3 analyse.py` reads saved series and writes results; `python3 verify.py` checks saved snapshots, continuation prefixes and a seed replay.
`python3 plot.py` requires NumPy and Matplotlib; it writes three PNG/PDF pairs to `figures/`.
The archive intentionally contains original numerical data and plotting input; figures are generated from these files.

## Rerun without overwriting these data

Copy mc.py, analyse.py, verify.py and plot.py into a new empty directory.
Set OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1.
Run `python3 mc.py --benchmark`, then `python3 mc.py --base`, then `python3 mc.py --extended`, then analyse.py and verify.py.
The sampler uses at most two worker processes and refuses to overwrite an existing case directory.
Base cases have 5000 warmup and 20000 production sweeps, measurements every 5 sweeps. Extension cases continue their exact RNG and angle states to 40000 production sweeps, preserving the first 20000 sweeps.

The two initializations use independent seeds. One sweep attempts each spin once by two checkerboard Metropolis sublattice updates. All lattice lengths are even.
Helicity modulus is Y/J. The comparison line is 2T/pi for kB=1, not the 2/pi convention used when plotting Y/T.
Displayed error is the larger of combined within-chain jackknife error and half the difference of two seed means. It is a diagnostic error bar, not a calibrated confidence interval.
Finite-size mean-curve crossing brackets do not give a thermodynamic-limit TBKT. These runs do not determine a superconducting transition temperature for any material.
