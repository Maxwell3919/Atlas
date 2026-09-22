"""FHS determinant links from native QE/Wannier90 overlaps; NumPy only."""
from pathlib import Path
import csv
import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)

def block(text, name):
    return re.search(r"begin\s+"+name+r"\s*\n(.*?)end\s+"+name,
                     text, re.S | re.I).group(1).strip().splitlines()

def write_csv(name, rows):
    with (OUT / name).open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def read_case(n):
    directory = ROOT / "source" / f"k{n}"
    win = (directory / "silicon.win").read_text()
    points = np.array([list(map(float, line.split())) for line in block(win, "kpoints")])
    indices = np.rint(points * n).astype(int)
    assert np.max(np.abs(points * n - indices)) < 1e-8
    assert len(set(map(tuple, indices))) == n**3
    lookup = {tuple(v): i for i, v in enumerate(indices)}
    nnkp = (directory / "silicon.nnkp").read_text()
    nn_points = block(nnkp, "kpoints")
    assert int(nn_points[0]) == len(points)
    assert np.allclose(points, np.array([list(map(float, x.split())) for x in nn_points[1:]]), atol=1e-8, rtol=0)
    bvecs = np.array([list(map(float, line.split())) for line in block(nnkp, "recip_lattice")])
    real = np.array([list(map(float, line.split())) for line in block(nnkp, "real_lattice")])
    reciprocal_error = float(np.max(np.abs(real @ bvecs.T - 2*np.pi*np.eye(3))))
    assert reciprocal_error < 1e-6
    nn_lines = block(nnkp, "nnkpts")
    nnb = int(nn_lines[0])
    declared = {tuple(map(int, line.split())) for line in nn_lines[1:]}
    with (directory / "silicon.mmn").open() as stream:
        stream.readline()
        nb, nk, nn = map(int, stream.readline().split())
        assert (nb, nk, nn) == (4, n**3, nnb)
        matrices = {}
        for _ in range(nk*nn):
            header = tuple(map(int, stream.readline().split()))
            assert len(header) == 5 and header not in matrices
            values = [complex(*map(float, stream.readline().split())) for _ in range(nb*nb)]
            matrices[header] = np.array(values).reshape((nb, nb), order="F")
        assert not stream.read().strip()
    assert set(matrices) == declared
    tree = ET.parse(directory / "nscf.data-file-schema.xml").getroot()
    vals = lambda tag: [e.text.strip() for e in tree.iter() if e.tag.split('}')[-1] == tag]
    assert set(vals("nbnd")) == {"4"} and set(vals("nks")) == {str(n**3)}
    assert all(float(x) == 8 for x in vals("nelec"))
    for tag in ["lsda", "noncolin", "spinorbit"]:
        assert set(vals(tag)) == {"false"}
    occ = [e for e in vals("occupations") if e != "fixed"]
    assert len(occ) == n**3 and all(np.array_equal(np.fromstring(x, sep=" "), np.ones(4)) for x in occ)
    for stem in ["si.scf", "si.nscf", "pw2wan"]:
        text = (directory / (stem+".out")).read_text()
        assert text.count("JOB DONE.") == 1
        assert not re.search(r"Error in routine|convergence NOT|eigenvalues not converged|MPI_ABORT", text)
        assert (directory / (stem+".err")).stat().st_size == 0
    selected = {}
    reverse_error = 0.0
    for header, matrix in matrices.items():
        i, j, *g = header
        reverse = (j, i, *[-v for v in g])
        assert reverse in matrices
        reverse_error = max(reverse_error, float(np.max(np.abs(matrix-matrices[reverse].conj().T))))
        delta = (points[j-1]+g-points[i-1])*n
        step = np.rint(delta).astype(int)
        assert np.max(np.abs(delta-step)) < 1e-8
        for axis in [0, 1]:
            unit = np.eye(3, dtype=int)[axis]
            if np.array_equal(step, unit):
                assert (i-1, axis) not in selected
                assert j-1 == lookup[tuple((indices[i-1]+unit) % n)]
                selected[i-1, axis] = (j-1, tuple(g), matrix)
    assert len(selected) == 2*n**3 and reverse_error < 1e-9
    return directory, points, indices, lookup, selected, bvecs, reciprocal_error, reverse_error

def links_and_flux(n, indices, lookup, selected, gauge=None):
    links = {}
    for (i, axis), (j, g, matrix) in selected.items():
        if gauge is not None:
            matrix = gauge[i].conj().T @ matrix @ gauge[j]
        determinant = np.linalg.det(matrix)
        assert abs(determinant) > 1e-12
        links[i, axis] = determinant / abs(determinant)
    flux = np.empty(n**3)
    for i, coord in enumerate(indices):
        i1 = lookup[tuple((coord + [1, 0, 0]) % n)]
        i2 = lookup[tuple((coord + [0, 1, 0]) % n)]
        flux[i] = np.angle(links[i,0]*links[i1,1]*np.conj(links[i2,0])*np.conj(links[i,1]))
    return links, flux

def run(n):
    start = time.perf_counter()
    directory, points, indices, lookup, selected, bvecs, reciprocal_error, reverse_error = read_case(n)
    area = float(np.linalg.norm(np.cross(bvecs[0], bvecs[1])) / n**2)
    rows = []
    for (i, axis), (j, g, matrix) in selected.items():
        sv = np.linalg.svd(matrix, compute_uv=False)
        rows.append(dict(grid=n,k_index=i+1,axis=axis+1,neighbor_index=j+1,G1=g[0],G2=g[1],G3=g[2],min_singular=float(sv[-1]),max_singular=float(sv[0]),abs_determinant=float(abs(np.linalg.det(matrix)))))
    minsv = min(x["min_singular"] for x in rows)
    maxsv = max(x["max_singular"] for x in rows)
    assert minsv > 1e-8 and maxsv < 1.001
    links, flux = links_and_flux(n, indices, lookup, selected)
    link_norm_error = max(abs(abs(v)-1) for v in links.values())
    assert link_norm_error < 1e-14
    gauge_rows = []
    for trial in range(12):
        seed = 2026092200 + 100*n + trial
        rng = np.random.default_rng(seed)
        gauge = []
        for _ in range(n**3):
            z = rng.normal(size=(4,4)) + 1j*rng.normal(size=(4,4))
            q, rr = np.linalg.qr(z)
            q = q @ np.diag(np.diag(rr)/np.abs(np.diag(rr)))
            gauge.append(q)
        gauge = np.array(gauge)
        norm_error = float(np.max(np.abs(gauge.conj().transpose(0,2,1)@gauge-np.eye(4))))
        _, changed = links_and_flux(n, indices, lookup, selected, gauge)
        flux_error = float(np.max(np.abs(np.angle(np.exp(1j*(changed-flux))))))
        chern_error = max(abs(np.sum(changed[indices[:,2]==s]-flux[indices[:,2]==s])/(2*np.pi)) for s in range(n))
        assert norm_error < 1e-12 and flux_error < 1e-12 and chern_error < 1e-12
        gauge_rows.append(dict(grid=n,trial=trial,seed=seed,unitary_error=norm_error,max_flux_difference_rad=flux_error,max_chern_difference=float(chern_error)))
    slice_rows=[]
    for s in range(n):
        f = flux[indices[:,2]==s]
        chern = float(np.sum(f)/(2*np.pi))
        integer = int(np.rint(chern))
        assert abs(chern-integer) < 1e-10
        slice_rows.append(dict(grid=n,k3_index=s,k3_fraction=s/n,plaquettes=n*n,chern_raw=chern,chern_integer=integer,max_abs_phase_rad=float(np.max(np.abs(f))),plaquette_area_invA2=area))
    write_csv(f"k{n}-links.csv", rows)
    write_csv(f"k{n}-gauge-check.csv", gauge_rows)
    write_csv(f"k{n}-plaquettes.csv", [dict(grid=n,k_index=i+1,k1_index=int(c[0]),k2_index=int(c[1]),k3_index=int(c[2]),k1_fraction=float(points[i,0]),k2_fraction=float(points[i,1]),k3_fraction=float(points[i,2]),phase_rad=float(flux[i]),phase_per_area_A2=float(flux[i]/area)) for i,c in enumerate(indices)])
    summary=dict(grid=n,occupied_bands=4,kpoints=n**3,mmn_neighbors=8,selected_links=len(selected),boundary_links=sum(any(x['G'+str(i)] for i in [1,2,3]) for x in rows),min_link_singular_value=minsv,max_link_singular_value=maxsv,min_abs_determinant=min(x['abs_determinant'] for x in rows),reciprocal_duality_error=reciprocal_error,reverse_link_max_error=reverse_error,normalized_link_norm_error=link_norm_error,max_abs_phase_rad=float(np.max(np.abs(flux))),branch_margin_rad=float(np.pi-np.max(np.abs(flux))),random_gauge_trials=12,max_gauge_flux_difference_rad=max(x['max_flux_difference_rad'] for x in gauge_rows),max_gauge_chern_difference=max(x['max_chern_difference'] for x in gauge_rows),slices=slice_rows,wall_seconds=time.perf_counter()-start)
    print(f"GRID {n}x{n}x{n}: {n**3} k points, 4 occupied bands, {len(selected)} directed links")
    print(f"  singular values: min={minsv:.12f} max={maxsv:.12f}; min|det M|={summary['min_abs_determinant']:.12f}")
    print(f"  reverse overlap residual={reverse_error:.3e}; max plaquette phase={summary['max_abs_phase_rad']:.6e} rad")
    print(f"  12 random U(4) gauges: max phase difference={summary['max_gauge_flux_difference_rad']:.3e} rad")
    for row in slice_rows:
        print(f"  k3={row['k3_fraction']:.9f}: C={row['chern_raw']:+.12e}, integer={row['chern_integer']}, max|phase|={row['max_abs_phase_rad']:.6e}")
    return summary, slice_rows

summaries=[]
slices=[]
for n in [4,6]:
    result, rows = run(n)
    summaries.append(result)
    slices.extend(rows)
write_csv("slices.csv", slices)
record=dict(method="Fukui-Hatsugai-Suzuki determinant links of four occupied native QE/pw2wannier90 bands",phase_convention="Arg(U1(k) U2(k+e1) conj(U1(k+e2)) conj(U2(k)))",surface="fixed fractional k3, oriented reciprocal b1,b2 torus",spin="nonmagnetic scalar calculation: one equivalent spin channel; four spatial bands, eight electrons",claim="Discrete slice Chern calculation and internal numerical checks only; no full-zone insulating-gap or Z2 validation",numpy_version=np.__version__,cases=summaries)
(OUT/"summary.json").write_text(json.dumps(record,indent=2)+"\n")
hashes={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'source').rglob('*')) if f.is_file()}
(OUT/'source-sha256.json').write_text(json.dumps(hashes,indent=2)+"\n")
print("POSTPROCESS_CHECKS_PASSED; full-zone gap and material topological classification not established.")
