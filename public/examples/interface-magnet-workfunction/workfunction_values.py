from __future__ import print_function
import json,re,hashlib
out=open('OUTCAR').read()
if 'aborting loop because EDIFF is reached' not in out:
    raise ValueError('Electronic convergence line is absent')
if 'General timing and accounting' not in out:
    raise ValueError('Normal final accounting section is absent')
ef=float(re.findall(r'E-fermi\s*:\s*([-+0-9.]+)',out)[-1])
p=json.load(open('potential-summary.json'))
with open('EIGENVAL') as f:
    for i in range(5): f.readline()
    ne,nk,nb=map(int,f.readline().split())
    if ne % 2: raise ValueError('This band-edge reader expects even-electron, non-spin-polarized input')
    occupied=[];empty=[]
    for ik in range(nk):
        line=f.readline()
        while line and not line.strip(): line=f.readline()
        if not line: raise ValueError('Truncated EIGENVAL before k point')
        if len(line.split())!=4: raise ValueError('Invalid k-point line')
        bands=[list(map(float,f.readline().split())) for ib in range(nb)]
        if any(len(row)!=3 for row in bands): raise ValueError('Invalid or truncated non-spin EIGENVAL band block')
        occupied.append(bands[ne//2-1][1]);empty.append(bands[ne//2][1])
vbm=max(occupied);cbm=min(empty)
r={'fermi_eV':ef,'vbm_eV':vbm,'cbm_eV':cbm,'indirect_gap_eV':cbm-vbm,'nkpoints':nk,'bands':nb,'electrons':ne,'windows':[]}
for w in p['windows']:
    item=dict(w)
    item['vacuum_minus_fermi_eV']=w['mean_eV']-ef
    item['vacuum_minus_vbm_eV']=w['mean_eV']-vbm
    item['vacuum_minus_cbm_eV']=w['mean_eV']-cbm
    r['windows'].append(item)
json.dump(r,open('workfunction-summary.json','w'),indent=2)
print('E_F = %.6f eV; VBM = %.6f eV; CBM = %.6f eV; gap = %.6f eV'%(ef,vbm,cbm,cbm-vbm))
for w in r['windows']:
    print('z = %.2f:%.2f A; V_vac = %.9f eV; Phi(E_F) = %.9f eV; V_vac-VBM = %.9f eV; V_vac-CBM = %.9f eV'%(w['lo_A'],w['hi_A'],w['mean_eV'],w['vacuum_minus_fermi_eV'],w['vacuum_minus_vbm_eV'],w['vacuum_minus_cbm_eV']))
