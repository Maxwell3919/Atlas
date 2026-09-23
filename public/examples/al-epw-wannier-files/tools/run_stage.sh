#!/usr/bin/env bash
# Run only inside an allocation with NPROC CPUs, or on an idle authorized host.
# Stage preparation always refuses an existing directory.
set -euo pipefail
cd "$(dirname "$0")/.."
NPROC=${NPROC:-8}
QE_BIN=${QE_BIN:-}
PW=${QE_BIN:+$QE_BIN/}pw.x
PH=${QE_BIN:+$QE_BIN/}ph.x
Q2R=${QE_BIN:+$QE_BIN/}q2r.x
EPW=${QE_BIN:+$QE_BIN/}epw.x
export OMP_NUM_THREADS=1
stage=${1:?Use parent, nscf, wannier, coarse, fine, bandcheck, or phononcheck}
python3 tools/prepare_stage.py "$stage"
case "$stage" in
 parent)
  cd 00-phonon
  mpirun -np "$NPROC" "$PW" -in al.dense.in > al.dense.out 2> al.dense.err
  cp tmp/al.a2Fsave al.a2Fsave.k32
  mpirun -np "$NPROC" "$PW" -in al.scf.in > al.scf.out 2> al.scf.err
  cmp tmp/al.a2Fsave al.a2Fsave.k32
  mpirun -np "$NPROC" "$PH" -in al.elph.in > al.elph.out 2> al.elph.err
  "$Q2R" -in q2r.in > q2r.out 2> q2r.err
  cd ..
  python3 tools/collect_phonons.py 00-phonon phonon-save
  ;;
 nscf)
  cd 01-nscf
  mpirun -np "$NPROC" "$PW" -nk "$NPROC" -in al.nscf.in > al.nscf.out 2> al.nscf.err
  ;;
 wannier)
  cd 02-wannier
  mpirun -np 1 "$EPW" -nk 1 -in epw1.in > epw1.out 2> epw1.err
  ;;
 coarse)
  cd 03-coarse
  mpirun -np "$NPROC" "$EPW" -nk "$NPROC" -in epw-coarse.in > epw-coarse.out 2> epw-coarse.err
  ;;
 fine)
  cd 04-fine
  mpirun -np "$NPROC" "$EPW" -nk "$NPROC" -in epw2.in > epw2.out 2> epw2.err
  ;;
 phononcheck)
  cd 06-phononcheck
  mpirun -np 1 "$EPW" -nk 1 -in epw-phcheck.in > epw-phcheck.out 2> epw-phcheck.err
  ;;
 bandcheck)
  cd 05-bandcheck
  mpirun -np "$NPROC" "$PW" -nk "$NPROC" -in al.bands.in > al.bands.out 2> al.bands.err
  ;;
esac
