#!/usr/bin/env python3
"""Read the official BHZ HR and WT outputs; NumPy only; no DFT."""
from pathlib import Path
import itertools, json, re
import numpy as np
root = Path(__file__).resolve().parent
lines = (root / "BHZ_hr.dat").read_text().splitlines()
nw, nr = int(lines[1].split()[0]), int(lines[2].split()[0])
assert (nw, nr) == (4, 5)
# Official generator prints seven unit degeneracies; WT reads five from this line.
deg = np.array([float(x) for x in lines[3].split()][:nr])
raw = np.array([[float(x) for x in s.split()] for s in lines[4:]])
assert raw.shape == (nr*nw*nw, 7) and np.all(deg == 1)
rvec, hr = [], []
for block in raw.reshape(nr, nw*nw, 7):
    assert np.all(block[:, :3] == block[0, :3])
    h = np.zeros((nw,nw), complex)
    for row in block:
        h[int(row[3])-1,int(row[4])-1] = row[5] + 1j*row[6]
    rvec.append(block[0,:3]); hr.append(h)
rvec, hr = np.array(rvec), np.array(hr)
def H(k):
    return np.einsum("r,rij->ij", np.exp(2j*np.pi*(rvec@k))/deg, hr)
T = np.block([[np.zeros((2,2)),np.eye(2)],[-np.eye(2),np.zeros((2,2))]])
P = np.diag([1,-1,1,-1])
gap, herm, tr, inv = float("inf"), 0.0, 0.0, 0.0
for x,y in itertools.product(np.linspace(0,1,101,endpoint=False), repeat=2):
    k = np.array([x,y,0]); h = H(k)
    herm = max(herm, float(np.max(abs(h-h.conj().T))))
    tr = max(tr, float(np.max(abs(T@h.conj()@T.conj().T-H(-k)))))
    inv = max(inv, float(np.max(abs(P@h@P-H(-k)))))
    e = np.linalg.eigvalsh(h); gap = min(gap, float(e[2]-e[1]))
assert herm < 1e-12 and tr < 1e-12 and inv < 1e-12 and gap > 0
parities = []
for k in [[0,0,0],[.5,0,0],[0,.5,0],[.5,.5,0]]:
    e,v = np.linalg.eigh(H(k)); occ = v[:,:2]
    p = np.linalg.eigvalsh(occ.conj().T@P@occ)
    assert np.max(abs(abs(p)-1)) < 1e-12 and abs(p[0]-p[1]) < 1e-12
    parities.append(int(round(p[0])))
z2_parity = int((1-np.prod(parities))//2)
checks = []
for n in [41,81]:
    run = root/f"n{n}-final"; out = (run/"WT.out").read_text()
    assert "ERROR" not in out+(run/"run.out").read_text()
    z2 = int(re.findall(r"Z2 for the plane you choose:\s*(\d+)", out)[-1])
    w = np.loadtxt(run/"wcc.dat")
    assert w.shape == (n,5) and np.isfinite(w).all()
    assert abs(w[0,0]) < 1e-8 and abs(w[-1,0]-.5) < 1e-8
    ends = [float(abs((a[3]-a[4]+.5)%1-.5)) for a in w[[0,-1]]]
    assert max(ends) < 1e-8 and z2 == z2_parity == 1
    l = np.loadtxt(run/"dos.dat_l"); bulk = np.loadtxt(run/"dos.dat_bulk")
    assert l.shape == (n*401,4) and bulk.shape == (n*401,3)
    assert np.isfinite(l).all() and np.isfinite(bulk).all()
    assert np.max(abs(l[:,:2]-bulk[:,:2])) < 1e-10
    # k is an accumulated path length. Middle record corresponds to kx=0.
    center = l.reshape(n,401,4)[n//2]
    j = int(np.argmin(abs(center[:,1])))
    log_l = float(center[j,2]); log_bulk = float(bulk.reshape(n,401,3)[n//2,j,2])
    records = re.findall(r"Wcc integration max_diff, Nk_adaptive\s+([-+0-9.Ee]+)\s+(\d+)", out)
    assert len(records) == n and set(int(x[1]) for x in records) == {64,128}
    counts = {str(k): sum(int(x[1]) == k for x in records) for k in [64,128]}
    tol = float(re.findall(r"wcc_calc_tol\s+([-+0-9.Ee]+)", out)[-1])
    neighbour = float(re.findall(r"wcc_neighbour_tol\s+([-+0-9.Ee]+)", out)[-1])
    max_change = max(float(x[0]) for x in records)
    assert max_change <= tol and tol == .08 and neighbour == .30
    checks.append(dict(mesh=n,input_Nk1=n,input_Nk2=n,
                       wcc_algorithm="dense adaptive integration; initial transverse Nk2 sampling",
                       loop_points_final_counts=counts,loop_max_recorded_change=max_change,
                       wcc_calc_tol=tol,wcc_neighbour_tol=neighbour,
                       z2=z2,wcc_rows=len(w),kramers_endpoint_circular_difference=ends,
                       near_zero_energy_eV=float(center[j,1]),ln_left_ldos=log_l,
                       ln_bulk_ldos=log_bulk,left_over_bulk_ldos=float(np.exp(log_l-log_bulk))))
summary = dict(scope="Official lattice BHZ software check, not a material DFT/Wannier result",
               parameters_model_eV=dict(M=2,B=1,A=1,Delta0=0),occupied_spinor_bands=2,
               full_grid_gap_min_eV=gap,gap_grid="101x101, not a material convergence test",
               hermiticity_max=herm,time_reversal_max=tr,inversion_max=inv,occupied_pair_TRIM_parities=parities,
               z2_inversion_parity=z2_parity,surface_eta_eV=15/401,
               weight_comparison_scope="exp(log-left minus log-bulk) only; projections have different trace dimensions, no equal absolute normalization",
               surface_columns="ln LDOS as written by surfstat.f90; no absolute DOS normalization inferred",
               runs=checks)
(root/"checks.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2))
