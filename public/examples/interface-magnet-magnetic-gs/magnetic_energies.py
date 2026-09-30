from __future__ import print_function
import re,json,hashlib,os

def sha(p):
    if os.path.basename(p)=='POTCAR' and not os.path.exists(p):
        record=open('POTCAR.identity.txt').read()
        hashes=re.findall(r'[0-9a-f]{64}',record)
        if len(hashes)!=1:raise ValueError('Expected one recorded PAW hash')
        return hashes[0]
    return hashlib.sha256(open(p,'rb').read()).hexdigest()
rows=[]
for state in ['fm','afm','nm']:
    for name in ['POSCAR','KPOINTS','POTCAR']:
        if sha(state+'/'+name)!=sha('fm/'+name): raise ValueError('Different '+name)
    text=open(state+'/OUTCAR').read()
    reference=open('fm/OUTCAR').read()
    titles=re.findall(r'TITEL\s*=([^\n]+)',text)
    if titles!=re.findall(r'TITEL\s*=([^\n]+)',reference):raise ValueError('OUTCAR PAW identity differs')
    if 'aborting loop because EDIFF is reached' not in text or 'General timing and accounting' not in text: raise ValueError('Incomplete '+state)
    f=float(re.findall(r'free  energy\s+TOTEN\s*=\s*([-0-9.]+)',text)[-1])
    e0=float(re.findall(r'energy\(sigma->0\)\s*=\s*([-0-9.]+)',text)[-1])
    mag=re.findall(r'mag=\s*([-0-9.]+)',open(state+'/OSZICAR').read())
    rows.append({'state':state,'F_eV_cell':f,'E0_eV_cell':e0,'mag_cell_muB':float(mag[-1]) if mag else 0.0})
for row in rows:
    row['dE0_meV_atom']=(row['E0_eV_cell']-rows[0]['E0_eV_cell'])*1000/2
    print('%-3s F=% .8f eV  E0=% .8f eV  dE0=%9.4f meV/atom  M=%7.4f muB/cell'%(row['state'],row['F_eV_cell'],row['E0_eV_cell'],row['dE0_meV_atom'],row['mag_cell_muB']))
json.dump(rows,open('magnetic-energies.json','w'),indent=2)
