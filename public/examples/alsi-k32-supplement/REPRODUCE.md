# Al–Si 24³ / 32³ comparison

Run `python3 analyse_k32.py` in this directory. The parser uses Python's standard library and the bundled IN/OUT/XML/err files. It verifies source hashes, native SCF completion, matched geometry and parameters, then regenerates three CSV tables and `evidence/k32-analysis-receipt.json`.

To plot on a machine with NumPy and Matplotlib, run `python3 plot_k32.py all`. Outputs are `plots/k32-comparison.{png,svg}` and `plots/hull-k32.{png,svg}`.

The five CG jobs are 844–848. Job 851 is a separate Al3Si Davidson check; its intermediate warnings remain in the original output and it is not substituted into the five-member formation-energy set. There was no k28 calculation.

Inputs, output, stderr and XML retain the original bytes. Public run scripts replace only the private QE installation path with `<qe_bin>`. No charge density or wavefunction is bundled. To rerun QE, prepare the corresponding candidate's own parent density as explained in the formation-energy article, keep the original relative pseudopotential directory, and fill the executable path before submission.

The native QE jobs completed. The 24³→32³ formation-energy change still exceeds the 1 meV/atom comparison line. These are fixed constrained geometries, not re-optimized 32³ zero-pressure structures or a complete phase diagram. Original automated audits retain their blocked status for fields outside the validator's supported core.
