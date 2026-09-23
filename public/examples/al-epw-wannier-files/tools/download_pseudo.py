#!/usr/bin/env python3
from pathlib import Path
import urllib.request,hashlib
B=Path(__file__).resolve().parents[1];d=B/'pseudo';d.mkdir(exist_ok=True)
u='https://pseudopotentials.quantum-espresso.org/upf_files/Al.pz-vbc.UPF'
e='4eab06b63f87f07ede2d5a193e6d993a09107167fd6b8647afa807342501d6e5'
p=d/'Al.pz-vbc.UPF'
x=p.read_bytes() if p.exists() else urllib.request.urlopen(u,timeout=60).read()
h=hashlib.sha256(x).hexdigest();assert h==e,('Source identity mismatch; no run authorized by this script.',h)
if not p.exists():p.write_bytes(x)
print('Verified Al.pz-vbc.UPF SHA-256:',h)
