from __future__ import print_function
import os,re,json,math,hashlib

def digest(name):
    if os.path.basename(name)=='POTCAR' and not os.path.exists(name):
        record=open(os.path.join(os.path.dirname(name),'POTCAR.identity.txt')).read()
        hashes=re.findall(r'[0-9a-f]{64}',record)
        if len(hashes)!=1:raise ValueError('Expected one recorded PAW hash')
        return hashes[0]
    return hashlib.sha256(open(name,'rb').read()).hexdigest()
def params(name):
    p={}
    for l in open(name):
        l=l.split('#')[0].split('!')[0]
        if '=' in l:
            key,value=l.split('=',1);p[key.strip().upper()]=value.strip()
    return p

def read_case(name):
    p=params(name+'/INCAR');out=open(name+'/OUTCAR').read();osz=open(name+'/OSZICAR').read()
    if 'aborting loop because EDIFF is reached' not in out:raise ValueError(name+': EDIFF not reached')
    if 'General timing and accounting' not in out:raise ValueError(name+': no final accounting')
    if p['LSORBIT']!='.TRUE.' or p['LNONCOLLINEAR']!='.TRUE.':raise ValueError('SOC/noncollinear is required')
    m=list(map(float,re.findall(r'mag=\s*([-+0-9.Ee]+)\s+([-+0-9.Ee]+)\s+([-+0-9.Ee]+)',osz)[-1]))
    axis=list(map(float,p['SAXIS'].split()));anorm=math.sqrt(sum(v*v for v in axis));axis=[v/anorm for v in axis]
    alpha=math.atan2(axis[1],axis[0]);beta=math.atan2(math.hypot(axis[0],axis[1]),axis[2])
    ca,sa,cb,sb=math.cos(alpha),math.sin(alpha),math.cos(beta),math.sin(beta)
    cart=[ca*cb*m[0]-sa*m[1]+ca*sb*m[2],sa*cb*m[0]+ca*m[1]+sa*sb*m[2],-sb*m[0]+cb*m[2]]
    mag=math.sqrt(sum(v*v for v in cart));angle=math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(axis,cart))/mag))))
    if angle>1.0:raise ValueError(name+': magnetization drifted from target direction')
    return {'name':name,'PAW_check_source':'actual POTCAR' if os.path.exists(name+'/POTCAR') else 'recorded original hash','F_eV':float(re.findall(r'free\s+energy\s+TOTEN\s*=\s*([-+0-9.Ee]+)',out)[-1]),'E0_eV':float(re.findall(r'energy\(sigma->0\)\s*=\s*([-+0-9.Ee]+)',out)[-1]),'E_without_entropy_eV':float(re.findall(r'energy\s+without entropy\s*=\s*([-+0-9.Ee]+)',out)[-1]),'elapsed_s':float(re.findall(r'Elapsed time \(sec\):\s*([0-9.]+)',out)[-1]),'nkpoints':int(re.findall(r'NKPTS\s*=\s*(\d+)',out)[-1]),'mag_spinor_muB':m,'mag_cartesian_muB':cart,'mag_angle_from_target_deg':angle,'incar':p,'POSCAR_sha256':digest(name+'/POSCAR'),'POTCAR_sha256':digest(name+'/POTCAR'),'KPOINTS_sha256':digest(name+'/KPOINTS'),'OUTCAR_sha256':digest(name+'/OUTCAR')}

if __name__=='__main__':
    names=['k09_z','k09_x','k15_z','k15_x'];rows=[read_case(n) for n in names]
    if len(set(r['POSCAR_sha256'] for r in rows))!=1 or len(set(r['POTCAR_sha256'] for r in rows))!=1:raise ValueError('Structure or PAW differs')
    protocol=[dict((k,v) for k,v in r['incar'].items() if k not in ['SYSTEM','SAXIS']) for r in rows]
    if any(p!=protocol[0] for p in protocol[1:]):raise ValueError('Protocol mismatch')
    pairs=[]
    for mesh,z,x in [(9,rows[0],rows[1]),(15,rows[2],rows[3])]:
        if z['KPOINTS_sha256']!=x['KPOINTS_sha256'] or z['nkpoints']!=x['nkpoints']:raise ValueError('x/z k point mismatch')
        pairs.append({'mesh':mesh,'delta_F_x_minus_z_meV_per_Fe':1000*(x['F_eV']-z['F_eV']),'delta_E0_x_minus_z_meV_per_Fe':1000*(x['E0_eV']-z['E0_eV'])})
    report={'definition':'Delta E = E_x - E_z; one Fe per cell','energy_for_primary_comparison':'energy(sigma->0); free energy retained as smearing diagnostic','cases':rows,'pairs':pairs,'mesh_change_delta_E0_meV':pairs[1]['delta_E0_x_minus_z_meV_per_Fe']-pairs[0]['delta_E0_x_minus_z_meV_per_Fe']}
    json.dump(report,open('mae-summary.json','w'),indent=2)
    print('same POSCAR/POTCAR; same active INCAR except SYSTEM/SAXIS; x/z k grids match')
    for r in rows:
        print('%s: F=% .8f eV; E0=% .8f eV; NKPTS=%d; wall=%.3f s'%(r['name'],r['F_eV'],r['E0_eV'],r['nkpoints'],r['elapsed_s']))
        print('  m_spinor='+str(r['mag_spinor_muB'])+'; m_Cartesian='+str([round(v,6) for v in r['mag_cartesian_muB']])+'; angle=%.6f deg'%r['mag_angle_from_target_deg'])
    for r in pairs:print('%dx%dx1: DeltaF(x-z)=%+.8f meV/Fe; DeltaE0(x-z)=%+.8f meV/Fe'%(r['mesh'],r['mesh'],r['delta_F_x_minus_z_meV_per_Fe'],r['delta_E0_x_minus_z_meV_per_Fe']))
    print('9 -> 15 change in DeltaE0 = %+.8f meV/Fe'%report['mesh_change_delta_E0_meV'])
