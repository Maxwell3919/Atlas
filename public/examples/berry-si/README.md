# Si occupied-overlap slice calculation

This directory reproduces postprocessing of native QE 7.5 / pw2wannier90
four-occupied-band overlap matrices on 4x4x4 and 6x6x6 uniform meshes.
It does not contain QE wavefunction checkpoints or a pseudopotential library.
The original SCF/NSCF workflow is documented on the Atlas Wannier90 page.

Run with Python 3 and NumPy:

    python3 -B analyse.py > analyse.out 2> analyse.err
    python3 -B verify.py > verify.out 2> verify.err

For figures, add Matplotlib and run:

    python3 plot.py

source/ contains native .mmn, .nnkp, .win and .eig bytes unchanged;
absolute machine paths in 12 input/output/XML files were generalized.
publication.json lists original source hashes and path edits.
results/source-sha256.json identifies public source files read by this run.
The source copy was checked against the original calculation host first.
Source files were unchanged during analysis.

The reported C is the FHS-convention integer of a fixed fractional k3 periodic
slice, oriented along reciprocal b1 then b2. It is for one equivalent spin
channel of a nonmagnetic no-SOC calculation. No full-zone insulating-gap,
local-curvature convergence, Z2 invariant, or edge-state claim is established.
The synthetic +1 check in verify.py is an algebra test, not a Si result.

References:
https://arxiv.org/abs/cond-mat/0503172
https://wannier90.readthedocs.io/en/latest/user_guide/wannier90/postproc/
