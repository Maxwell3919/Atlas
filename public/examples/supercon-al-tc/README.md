# Al dense-grid Tc comparison (QE 7.5)

Two complete original EPC routes: dense k32^3/k48^3, response k16^3, q4^3; ten electron broadenings .005–.050 Ry, mu*=.10. k32 and k48 contain their own inputs, native outputs, eight elph records, spectra and lambda tables. There is no in-range intersection; the minimum positive Tc difference is .009221798 K.

Saved-data postprocessing (Python 3 standard library):

```bash
python3 rebuild_tc.py k32 k48 --outdir replay
python3 compare_tc.py --a k32 --b k48 --out replay
python3 compare_spectral_grids.py --root . --outdir replay
```

The spectral script reads the reference paired table under comparison-k32-k48/. Replay CSVs can be compared byte-for-byte with that reference. Plotting needs NumPy and Matplotlib:

```bash
python3 plot_supercon_tc_difference.py --data replay/paired-tc.csv --out replay/figures --prefix al-tc-delta
python3 plot_tc_crossings.py --data replay --out replay/figures --prefix al-k32-k48
```

Input files and Slurm scripts document the original full QE calculation. Restart SCF save directories, wavefunctions, a2Fsave copies, private audits and XML metadata are omitted. The saved elph records suffice for reconstruction; a new DFT run needs freshly generated matching SCF state and local executable/pseudopotential paths.

FILE_SHA256.json lists all packaged files except itself. q weights sum to64. Native mode lambda has four printed decimals and Tc has three; reconstruction recovers lambda.x operations on saved inputs, not unprinted DFPT precision. Comparing two fixed grids and broadenings is distinct from a k/q convergence study.
