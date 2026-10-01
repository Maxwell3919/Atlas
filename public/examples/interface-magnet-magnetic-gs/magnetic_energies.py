from __future__ import print_function
import re,json,hashlib,os,math

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
    expected_spin=1 if state=='nm' else 2
    incar='\n'.join(re.split(r'[!#]',line,1)[0] for line in open(state+'/INCAR'))
    input_spin=re.findall(r'\bISPIN\s*=\s*(\d+)\b',incar,re.I)
    output_spin=re.findall(r'\bISPIN\s*=\s*(\d+)\b',text)
    if not input_spin or int(input_spin[-1])!=expected_spin or not output_spin or int(output_spin[-1])!=expected_spin:
        raise ValueError('Expected ISPIN='+str(expected_spin)+' in INCAR and OUTCAR for '+state)
    summaries=[line for line in open(state+'/OSZICAR') if re.search(r'\bF\s*=',line)]
    if not summaries:raise ValueError('Missing final OSZICAR summary for '+state)
    mag=re.search(r'\bmag\s*=\s*(\S+)',summaries[-1])
    if mag is None:
        if state!='nm':raise ValueError('Missing final mag for '+state)
        moment=0.0
    else:
        moment=float(mag[1])
        if not math.isfinite(moment):raise ValueError('Non-finite final mag for '+state)
    rows.append({'state':state,'F_eV_cell':f,'E0_eV_cell':e0,'mag_cell_muB':moment})
for row in rows:
    row['dE0_meV_atom']=(row['E0_eV_cell']-rows[0]['E0_eV_cell'])*1000/2
    print('%-3s F=% .8f eV  E0=% .8f eV  dE0=%9.4f meV/atom  M=%7.4f muB/cell'%(row['state'],row['F_eV_cell'],row['E0_eV_cell'],row['dE0_meV_atom'],row['mag_cell_muB']))
json.dump(rows,open('magnetic-energies.json','w'),indent=2)
