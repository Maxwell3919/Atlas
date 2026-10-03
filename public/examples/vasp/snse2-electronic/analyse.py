#!/usr/bin/env python3
"""Read the fixed SnSe2 data set; export paired eigenvalues/projections/DOS."""
from pathlib import Path
import csv
import re
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "tables"
OUT.mkdir(exist_ok=True)

def eigenval(path):
    lines = path.read_text().splitlines()
    assert int(lines[0].split()[-1]) == 1, "This example requires ISPIN=1."
    nelect, nk, nb = map(int, lines[5].split())
    k, weights, energies, occupations = [], [], [], []
    cursor = 6
    for ik in range(nk):
        while not lines[cursor].strip():
            cursor += 1
        head = list(map(float, lines[cursor].split()))
        assert len(head) == 4
        k.append(head[:3])
        weights.append(head[3])
        cursor += 1
        block = [lines[cursor + j].split() for j in range(nb)]
        assert [int(row[0]) for row in block] == list(range(1, nb + 1))
        energies.append([float(row[1]) for row in block])
        occupations.append([float(row[2]) for row in block])
        cursor += nb
    return nelect, np.array(k), np.array(weights), np.array(energies), np.array(occupations)

def table(name, header, rows):
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)

scf_xml = ET.parse(ROOT / "scf/vasprun.xml").getroot()
band_xml = ET.parse(ROOT / "bands/vasprun.xml").getroot()
ef = float(scf_xml.findall('.//i[@name="efermi"]')[-1].text)
ef_path = float(band_xml.findall('.//i[@name="efermi"]')[-1].text)
for model in (scf_xml, band_xml):
    assert float(model.find('./incar/i[@name="ENCUT"]').text) == 400.0
    assert model.find('.//i[@name="ISPIN"]').text.strip() == "1"
    assert model.find('.//i[@name="LSORBIT"]').text.strip() == "F"
    assert model.find('.//i[@name="NSW"]').text.strip() == "0"

poscar = (ROOT / "bands/POSCAR").read_text().splitlines()
scale = float(poscar[1])
assert scale > 0
lattice = scale * np.array([list(map(float, row.split())) for row in poscar[2:5]])
assert poscar[5].split() == ["Sn", "Se"]
assert list(map(int, poscar[6].split())) == [1, 2]
reciprocal = 2 * np.pi * np.linalg.inv(lattice).T

nelect, k, kw, energy, occupation = eigenval(ROOT / "bands/EIGENVAL")
nk, nb = energy.shape
assert (nelect, nk, nb) == (26, 150, 20)
assert np.all(np.isfinite(energy))
cartesian = k @ reciprocal
distance = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(cartesian, axis=0), axis=1))]
nodes = [(0, "Gamma"), (49, "M"), (99, "K"), (149, "Gamma")]
expected = np.array([[0,0,0], [0.5,0,0], [1/3,1/3,0], [0,0,0]])
assert np.allclose(k[[i for i, _ in nodes]], expected, atol=6e-8)
assert np.allclose(k[49], k[50]) and np.allclose(k[99], k[100])
table("path.csv", ["k_index", "kx_frac", "ky_frac", "kz_frac", "distance_Ainv"],
      [(i+1, *k[i], distance[i]) for i in range(nk)])
table("bands.csv", ["k_index", "band", "distance_Ainv", "energy_eV",
                   "energy_minus_scf_EF_eV", "occupation_per_spin"],
      [(i+1, j+1, distance[i], energy[i,j], energy[i,j]-ef, occupation[i,j])
       for i in range(nk) for j in range(nb)])

# Each PROCAR record has one energy and three atom rows plus the tot row.
raw = (ROOT / "bands/PROCAR").read_text().splitlines()
header = re.search(r"# of k-points:\s*(\d+)\s*# of bands:\s*(\d+)\s*# of ions:\s*(\d+)",
                   "\n".join(raw[:4]))
assert tuple(map(int, header.groups())) == (nk, nb, 3)
channels = np.full((nk, nb, 7), np.nan)
procar_energy = np.full_like(energy, np.nan)
procar_k = np.full_like(k, np.nan)
ik = ib = None
atom_rows = []
seen = set()
for line in raw:
    match_k = re.match(r"\s*k-point\s+(\d+)\s*:\s*(\S+)\s+(\S+)\s+(\S+)", line)
    if match_k:
        ik = int(match_k[1])-1
        procar_k[ik] = list(map(float, match_k.groups()[1:]))
        continue
    match_band = re.match(r"\s*band\s+(\d+)\s*# energy\s+(\S+)", line)
    if match_band:
        ib = int(match_band[1])-1
        assert (ik, ib) not in seen
        procar_energy[ik,ib] = float(match_band[2])
        atom_rows = []
        continue
    fields = line.split()
    if ik is None or ib is None or not fields:
        continue
    if fields[0] == "ion":
        assert fields[1:] == ["s","py","pz","px","dxy","dyz","dz2","dxz","x2-y2","tot"]
    elif fields[0] in ("1", "2", "3") and len(fields) == 11:
        assert int(fields[0]) == len(atom_rows)+1
        atom_rows.append(list(map(float, fields[1:])))
    elif fields[0] == "tot" and len(fields) == 11:
        assert len(atom_rows) == 3, "Reject missing/multiple noncollinear blocks."
        atoms = np.array(atom_rows)
        tin = atoms[0]
        selenium = atoms[1:].sum(axis=0)
        channels[ik,ib] = [tin[0],tin[1:4].sum(),tin[4:9].sum(),
                           selenium[0],selenium[1:4].sum(),selenium[4:9].sum(),
                           float(fields[-1])]
        seen.add((ik,ib))
assert len(seen) == nk*nb and np.isfinite(channels).all()
energy_difference = float(np.max(np.abs(procar_energy-energy)))
assert energy_difference < 6e-7
assert np.allclose(procar_k, k, atol=6e-8)
table("fatband.csv", ["k_index","band","distance_Ainv","energy_minus_scf_EF_eV",
                      "Sn_s","Sn_p","Sn_d","Se_s","Se_p","Se_d","projected_total"],
      [(i+1,j+1,distance[i],energy[i,j]-ef,*channels[i,j])
       for i in range(nk) for j in range(nb)])

# DOS comes from the uniform static SCF, never from the line-mode run.
dos_lines = (ROOT / "scf/DOSCAR").read_text().splitlines()
assert list(map(int, dos_lines[0].split()))[:3] == [3,3,1]
dos_header = list(map(float, dos_lines[5].split()))
nedos = int(dos_header[2])
assert nedos == 301 and abs(dos_header[3]-ef) < 1e-8
total = np.array([list(map(float,row.split())) for row in dos_lines[6:6+nedos]])
assert total.shape == (nedos,3)
cursor = 6+nedos
atom_dos = []
for ion in range(3):
    assert int(float(dos_lines[cursor].split()[2])) == nedos
    block = np.array([list(map(float,row.split()))
                      for row in dos_lines[cursor+1:cursor+1+nedos]])
    assert block.shape == (nedos,10)
    assert np.allclose(block[:,0],total[:,0],atol=1e-8)
    atom_dos.append(block[:,1:])
    cursor += nedos+1
assert not any(row.strip() for row in dos_lines[cursor:])
pdos = np.array(atom_dos)
tin = pdos[0]
selenium = pdos[1:].sum(axis=0)
dos_channels = np.column_stack([tin[:,0],tin[:,1:4].sum(axis=1),tin[:,4:9].sum(axis=1),
                               selenium[:,0],selenium[:,1:4].sum(axis=1),
                               selenium[:,4:9].sum(axis=1)])
table("dos.csv", ["energy_eV","energy_minus_scf_EF_eV","total_DOS_states_per_eV_cell",
                  "integrated_DOS_states_per_cell","Sn_s","Sn_p","Sn_d","Se_s","Se_p","Se_d"],
      [(total[i,0],total[i,0]-ef,*total[i,1:],*dos_channels[i]) for i in range(nedos)])
n_scf, sk, sw, se, so = eigenval(ROOT / "scf/EIGENVAL")
assert n_scf == 26 and se.shape == (37,20) and abs(sw.sum()-1)<1e-7
assert so.min() >= 0 and so.max() <= 1
occupied_count = float(2*np.sum(sw[:,None]*so))  # ISPIN=1 EIGENVAL stores 0..1 occupations
assert abs(occupied_count-26)<1e-5  # printed k weights have finite precision
idos_ef = float(np.interp(ef,total[:,0],total[:,2]))
vbm_index = tuple(map(int,np.unravel_index(np.argmax(energy[:,:13]), (nk,13))))
cbm_index_raw = tuple(map(int,np.unravel_index(np.argmin(energy[:,13:]), (nk,nb-13))))
cbm_index = (cbm_index_raw[0],cbm_index_raw[1]+13)
edge_rows = []
for name, (i,j) in [("VBM_path",vbm_index),("CBM_path",cbm_index)]:
    edge_rows.append((name,i+1,j+1,*k[i],energy[i,j],energy[i,j]-ef,*channels[i,j]))
table("path-edges.csv", ["edge","k_index","band","kx_frac","ky_frac","kz_frac","energy_eV",
                        "energy_minus_scf_EF_eV","Sn_s","Sn_p","Sn_d","Se_s","Se_p","Se_d","projected_total"],
      edge_rows)
table("path-nodes.csv",["k_index","label","distance_Ainv"],
      [(i+1,label,float(distance[i])) for i,label in nodes])
dos_step=float(np.median(np.diff(total[:,0])))
path_gap=float(energy[cbm_index]-energy[vbm_index])
values=[("SCF_Fermi",ef,"eV"),("path_Fermi",ef_path,"eV"),
        ("electrons",nelect,"electrons/cell"),("SCF_irreducible_points",len(sk),"points"),
        ("path_points",nk,"points"),("bands",nb,"bands"),
        ("path_length",float(distance[-1]),"A^-1"),
        ("PROCAR_EIGENVAL_max_difference",energy_difference,"eV"),
        ("DOS_points",nedos,"points"),("DOS_step",dos_step,"eV"),
        ("DOS_SIGMA",0.05,"eV"),("weighted_occupied_states",occupied_count,"electrons/cell"),
        ("IDOS_at_SCF_Fermi",idos_ef,"states/cell"),
        ("IDOS_lower_bound",float(total[0,2]),"states/cell"),
        ("IDOS_upper_bound",float(total[-1,2]),"states/cell"),
        ("DOS_integral_full_window",float(np.trapezoid(total[:,1],total[:,0])),"states/cell"),
        ("path_sampled_gap",path_gap,"eV")]
table("electronic-values.csv",["quantity","value","unit"],values)
print(f"SCF: 18x18x1 -> {len(sk)} irreducible points; weighted occupied states = {occupied_count:.8f}")
print(f"Path: {nk} points x {nb} bands; length = {distance[-1]:.8f} A^-1")
print(f"PROCAR: {len(seen)} paired states; max energy difference = {energy_difference:.3e} eV")
print(f"Energy zero: SCF efermi = {ef:.8f} eV; path efermi = {ef_path:.8f} eV")
print(f"DOS: {nedos} energy points; step = {dos_step:.6f} eV; SIGMA = 0.05 eV")
print(f"IDOS: at SCF EF = {idos_ef:.8f}; lower/upper ends = {total[0,2]:.8f}/{total[-1,2]:.8f}")
print(f"Path extrema: VBM k={vbm_index[0]+1}, band={vbm_index[1]+1}; CBM k={cbm_index[0]+1}, band={cbm_index[1]+1}")
print(f"Path sampled gap = {path_gap:.8f} eV")
print("Wrote path.csv, bands.csv, fatband.csv, dos.csv, path-edges.csv, path-nodes.csv and electronic-values.csv")
