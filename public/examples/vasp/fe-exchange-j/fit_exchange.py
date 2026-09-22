from __future__ import print_function
import re,json,math,os,hashlib

def active(path):
    d={}
    for line in open(path):
        line=line.split('#')[0].split('!')[0]
        if '=' in line:
            k,v=line.split('=',1);d[k.strip()]=v.strip()
    return d

def file_sha(name):
    if os.path.basename(name)=='POTCAR' and not os.path.exists(name):
        values=re.findall(r'[0-9a-f]{64}',open(os.path.join(os.path.dirname(name),'POTCAR.identity.txt')).read())
        if len(values)!=1:raise ValueError('Expected one recorded PAW hash')
        return values[0]
    return hashlib.sha256(open(name,'rb').read()).hexdigest()

def sampling_length(name):
    pos=open(name+'/POSCAR').readlines();scale=float(pos[1])
    lengths=[math.sqrt(sum(float(x)**2 for x in l.split()[:3]))*scale for l in pos[2:5]]
    nk=list(map(int,open(name+'/KPOINTS').readlines()[3].split()))
    return [x*y for x,y in zip(lengths,nk)]

def read_case(name,enforce_moment=True):
    p=active(name+'/INCAR');out=open(name+'/OUTCAR').read()
    if 'aborting loop because EDIFF is reached' not in out or 'General timing and accounting' not in out:raise ValueError('Unfinished '+name)
    if p.get('ISPIN')!='2':raise ValueError('Expected collinear spin polarization')
    n=sum(map(int,open(name+'/POSCAR').readlines()[6].split()))
    block=out.split('magnetization (x)')[-1]
    moment=[]
    for line in block.splitlines():
        fields=line.split()
        if len(fields)==5 and fields[0].isdigit():moment.append(float(fields[-1]))
        if len(moment)==n:break
    if len(moment)!=n:raise ValueError('Missing local magnetic moments')
    signs=[1 if x>0 else -1 for x in moment]
    if enforce_moment and min(abs(x) for x in moment)<.1:raise ValueError('Local moment collapsed; direction mapping invalid')
    return {'state':name,'n_atoms':n,'E0_eV_cell':float(re.findall(r'energy\(sigma->0\)\s*=\s*([-+0-9.Ee]+)',out)[-1]),'F_eV_cell':float(re.findall(r'free\s+energy\s+TOTEN\s*=\s*([-+0-9.Ee]+)',out)[-1]),'local_moment_muB':moment,'final_spin_signs':signs,'elapsed_s':float(re.findall(r'Elapsed time \(sec\):\s*([0-9.]+)',out)[-1]),'active_incar':p,'OUTCAR_sha256':hashlib.sha256(open(name+'/OUTCAR','rb').read()).hexdigest()}

if __name__=='__main__':
    bonds=json.load(open('bonds-summary.json'));names=['fm2','afm2','fm4','neel4','stripe4'];rows=[read_case(n) for n in names]
    if len(set(file_sha(n+'/POTCAR') for n in names))!=1:raise ValueError('PAW identity differs')
    for family in [['fm2','afm2'],['fm4','neel4','stripe4']]:
        if len(set(file_sha(n+'/POSCAR') for n in family))!=1:raise ValueError('Structure differs within cell family')
        if len(set(file_sha(n+'/KPOINTS') for n in family))!=1:raise ValueError('KPOINTS differ within cell family')
    density=sampling_length('fm2')
    if any(max(abs(x-y) for x,y in zip(sampling_length(n),density))>1e-9 for n in names):raise ValueError('Reciprocal sampling density differs')
    reference=dict((k,v) for k,v in rows[0]['active_incar'].items() if k not in ['SYSTEM','MAGMOM'])
    for r in rows:
        if dict((k,v) for k,v in r['active_incar'].items() if k not in ['SYSTEM','MAGMOM'])!=reference:raise ValueError('Protocol mismatch: '+r['state'])
        want=bonds['states'][r['state']]['spin_directions']
        if r['final_spin_signs']!=want and r['final_spin_signs']!=[-v for v in want]:raise ValueError('Final magnetic pattern changed')
    fm,afm=rows[:2];n2=fm['n_atoms'];cf=bonds['states']['fm2']['correlation_sum'];ca=bonds['states']['afm2']['correlation_sum']
    j=(afm['E0_eV_cell']-fm['E0_eV_cell'])/(cf-ca)
    ref=(fm['E0_eV_cell']+j*cf)/n2
    for r in rows:
        corr=bonds['states'][r['state']]['correlation_sum'];pred=ref*r['n_atoms']-j*corr
        r['correlation_sum']=corr;r['predicted_E0_eV_cell']=pred;r['residual_meV_atom']=1000*(r['E0_eV_cell']-pred)/r['n_atoms']
    report={'definition':bonds['definition'],'J_effective_meV_per_bond':j*1000,'Eref_eV_atom':ref,'fit_states':['fm2','afm2'],'validation_states':['fm4','neel4','stripe4'],'rows':rows,'scope':'two-state effective nearest-neighbor parameter; third-state residual tests transferability; local moment magnitudes are not constrained equal'}
    json.dump(report,open('exchange-summary.json','w'),indent=2)
    print('J_eff = %.8f meV per unique NN bond; Eref = %.10f eV/atom'%(j*1000,ref))
    for r in rows:
        print('%-7s N=%d C=%+3d E0=% .8f predicted=% .8f eV/cell residual=%+.6f meV/atom; moments=%s'%(r['state'],r['n_atoms'],r['correlation_sum'],r['E0_eV_cell'],r['predicted_E0_eV_cell'],r['residual_meV_atom'],r['local_moment_muB']))
