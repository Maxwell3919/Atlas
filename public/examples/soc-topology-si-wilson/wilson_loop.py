"""Matrix Wilson loops of the archived scalar Si occupied subspace; no Z2 inference."""
from pathlib import Path
import argparse, csv, itertools, json, re
import xml.etree.ElementTree as ET
import numpy as np

def block(text, name):
    found = re.search(r"begin\s+" + name + r"\s*\n(.*?)end\s+" + name, text, re.S | re.I)
    if found is None:
        raise ValueError("Missing block: " + name)
    return found.group(1).strip().splitlines()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def circle_error(a, b):
    return min(max(abs(((a[i]-b[j]+0.5) % 1)-0.5) for i,j in enumerate(p))
               for p in itertools.permutations(range(len(a))))

def load(data, n):
    folder = data / "source" / f"k{n}"
    points = np.array([list(map(float, x.split())) for x in block((folder/"silicon.win").read_text(), "kpoints")])
    index = np.rint(points*n).astype(int)
    require(points.shape == (n**3, 3) and np.max(abs(points*n-index)) < 1e-8, "Grid mismatch")
    lookup = {tuple(k):i for i,k in enumerate(index)}
    require(len(lookup) == n**3, "Duplicate grid points")
    nnkp = (folder/"silicon.nnkp").read_text()
    nnpoints = block(nnkp, "kpoints")
    require(int(nnpoints[0]) == n**3 and np.allclose(points, np.array([list(map(float,x.split())) for x in nnpoints[1:]]), atol=1e-8, rtol=0), "NNKP order mismatch")
    declared = {tuple(map(int,x.split())) for x in block(nnkp, "nnkpts")[1:]}
    xml = ET.parse(folder/"nscf.data-file-schema.xml").getroot()
    vals = lambda tag: [e.text.strip() for e in xml.iter() if e.tag.split("}")[-1] == tag]
    require(set(vals("nbnd")) == {"4"} and set(vals("nks")) == {str(n**3)}, "XML dimension mismatch")
    require(all(float(x)==8 for x in vals("nelec")), "Not the eight-electron Si case")
    for tag in ["lsda", "noncolin", "spinorbit"]:
        require(set(vals(tag)) == {"false"}, "Not the archived scalar case")
    occupied = [x for x in vals("occupations") if x != "fixed"]
    require(len(occupied)==n**3 and all(np.array_equal(np.fromstring(x, sep=" "), np.ones(4)) for x in occupied), "Occupation mismatch")
    matrices = {}
    with (folder/"silicon.mmn").open() as f:
        f.readline()
        nb,nk,nn = map(int,f.readline().split())
        require((nb,nk,nn)==(4,n**3,8), "MMN dimension mismatch")
        for _ in range(nk*nn):
            h=tuple(map(int,f.readline().split()))
            require(len(h)==5 and h not in matrices, "Duplicate or invalid MMN header")
            matrices[h]=np.array([complex(*map(float,f.readline().split())) for _ in range(nb*nb)]).reshape(nb,nb,order="F")
        require(not f.read().strip(), "Extra MMN records")
    require(set(matrices)==declared, "MMN/NNKP headers mismatch")
    links={}; minsv=1.; reverse=0.
    for h,m in matrices.items():
        i,j,*g=h; step=(points[j-1]+g-points[i-1])*n
        if np.allclose(step,[1,0,0],atol=1e-8,rtol=0):
            require(i-1 not in links and j-1==lookup[tuple((index[i-1]+[1,0,0]) % n)], "Bad periodic link")
            back=(j,i,*[-x for x in g]); require(back in matrices, "Missing reverse link")
            reverse=max(reverse,float(np.max(abs(m-matrices[back].conj().T))))
            u,s,vh=np.linalg.svd(m); minsv=min(minsv,float(s[-1]))
            links[i-1]=(j-1,u@vh)
    require(len(links)==n**3 and minsv>1e-8 and reverse<1e-9, "Singular or inconsistent links")
    return index, lookup, links, minsv, reverse

def run(data,n):
    index,lookup,links,minsv,reverse=load(data,n)
    rng=np.random.default_rng(2026100200+n)
    gauges=[]
    for _ in range(n**3):
        q,r=np.linalg.qr(rng.normal(size=(4,4))+1j*rng.normal(size=(4,4)))
        gauges.append(q)
    rows=[]; maxunit=0.; maxdet=0.; maxgauge=0.
    for k3 in range(n):
        for k2 in range(n):
            w=np.eye(4,dtype=complex); rotated=np.eye(4,dtype=complex); detprod=1.+0j
            for k1 in range(n):
                i=lookup[(k1,k2,k3)]; j,q=links[i]
                w=w@q; rotated=rotated@(gauges[i].conj().T@q@gauges[j]); detprod*=np.linalg.det(q)
            centres=np.sort((-np.angle(np.linalg.eigvals(w))/(2*np.pi)) % 1)
            changed=np.sort((-np.angle(np.linalg.eigvals(rotated))/(2*np.pi)) % 1)
            unit=float(np.max(abs(w.conj().T@w-np.eye(4))))
            deterror=float(abs(np.angle(np.linalg.det(w)/detprod)))
            gauge=circle_error(centres,changed)
            maxunit=max(maxunit,unit); maxdet=max(maxdet,deterror); maxgauge=max(maxgauge,gauge)
            rows.append(dict(grid=n,k2_fraction=k2/n,k3_fraction=k3/n,**{f"wcc{i+1}_mod1":float(x) for i,x in enumerate(centres)},sum_wcc_mod1=float(sum(centres)%1),unitarity_error=unit,det_phase_error_rad=deterror,gauge_spectrum_error_mod1=gauge))
    require(maxunit<1e-12 and maxdet<1e-12 and maxgauge<1e-12, "Wilson loop check failed")
    summary=dict(grid=n,loop_direction="+b1 including periodic G",loops=n*n,loop_points=n,spatial_bands=4,min_link_singular_value=minsv,reverse_overlap_error=reverse,max_unitarity_error=maxunit,max_determinant_phase_error_rad=maxdet,max_random_gauge_spectrum_error_mod1=maxgauge,random_seed=2026100200+n)
    print(f"{n}^3: {n*n} closed matrix loops; {n} links/loop; four spatial-band phases")
    print(f"  unitarity={maxunit:.3e}; determinant phase={maxdet:.3e} rad; gauge spectrum={maxgauge:.3e}")
    return rows,summary

if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--data",type=Path,required=True); parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    rows=[]; summaries=[]
    for n in [4,6]:
        r,s=run(args.data,n); rows.extend(r); summaries.append(s)
    with (args.output/"si-wilson-loops.csv").open("w") as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    record=dict(quantity="-Arg(eigenvalue of product of polar MMN links)/(2*pi), modulo one",subspace="Four occupied spatial bands of eight-electron nonmagnetic scalar Si, no SOC",connection="Closed +b1 loops at each sampled fractional k2,k3",interpretation="Matrix phase extraction only; no spinful Kramers partner tracking, Z2, edge spectrum or gap validation",numpy_version=np.__version__,cases=summaries)
    (args.output/"si-wilson-summary.json").write_text(json.dumps(record,indent=2)+"\n")
    print("WILSON_MATRIX_CHECKS_PASSED; no Z2 or material topology assigned")
