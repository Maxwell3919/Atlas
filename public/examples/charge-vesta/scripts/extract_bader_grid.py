#!/usr/bin/env python3
"""Extract the preserved 96³/192³ Fe ACF.dat tables without running Bader."""
import argparse, csv, json, re
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--root', type=Path, default=Path('.'))
p.add_argument('--output', type=Path, default=Path('new-bader-grid.csv'))
a=p.parse_args()
if a.output.exists():raise FileExistsError(f'Refusing to overwrite {a.output}')
rows=[]
for size in (96,192):
    text=(a.root/str(size)/'ACF.dat').read_text()
    entries=[]
    for line in text.splitlines():
        fields=line.split()
        if len(fields)==7 and fields[0].isdigit():
            entries.append([int(fields[0])]+[float(x) for x in fields[1:]])
    if [r[0] for r in entries]!=[1,2]:raise ValueError('Expected two Fe basins')
    footer={}
    for label in ('VACUUM CHARGE','VACUUM VOLUME','NUMBER OF ELECTRONS'):
        match=re.search(re.escape(label)+r':\s*([\d.Ee+-]+)',text)
        if not match:raise ValueError(f'Missing {label}')
        footer[label]=float(match[1])
    basin=sum(r[4] for r in entries);vol=sum(r[6] for r in entries)
    if abs(basin+footer['VACUUM CHARGE']-footer['NUMBER OF ELECTRONS'])>2e-4:raise ValueError('Charge balance outside footer precision')
    if abs(basin-16)>2e-6 or abs(vol-21.952)>2e-6:raise ValueError('Example sum differs')
    check=json.loads((a.root/str(size)/'charge-grid-check.json').read_text())
    if check['grid']!=[size]*3:raise ValueError('Wrong grid')
    for r in entries:
        atom,x,y,z,charge,distance,volume=r
        rows.append([size,atom,x,y,z,charge,charge-8,8-charge,distance,volume,check['AECCAR0_integral'],check['AECCAR2_integral'],check['CHGCAR_integral'],check['reference_integral']])
        print(f'{size}^3 Fe{atom}: N={charge:.6f} e; Q={8-charge:+.6f} e')
    print(f'{size}^3 printed basin sum residual={basin-16:.3e} e; volume residual={vol-21.952:.3e} Å³; core integral={check["AECCAR0_integral"]:.9f} e')
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('x',newline='') as f:
    w=csv.writer(f);w.writerow(['grid','atom','x_A','y_A','z_A','basin_e','delta_e','net_charge_e','min_dist_A','volume_A3','core_integral_e','valence_integral_e','CHGCAR_integral_e','reference_integral_e']);w.writerows(rows)
print(f'wrote: {a.output}; zero printed residual does not establish an exact integral')
