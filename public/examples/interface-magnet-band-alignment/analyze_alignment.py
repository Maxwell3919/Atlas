from __future__ import print_function
import os,re,json,math,hashlib

def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
def poscar(p):
 l=open(p).read().splitlines(); s=float(l[1]); cell=[[s*float(x) for x in r.split()] for r in l[2:5]]
 if s<=0 or not l[7].lower().startswith('d'): raise ValueError('Expected positive-scale direct-coordinate POSCAR')
 species=l[5].split(); counts=list(map(int,l[6].split())); n=sum(counts)
 xyz=[list(map(float,r.split()[:3])) for r in l[8:8+n]]
 if len(xyz)!=n: raise ValueError('Truncated POSCAR')
 return cell,species,counts,xyz

def geometry():
 ref,sp,n,r=poscar('POSCAR.reference')
 if sp!=['Sn','Se','N','Sr'] or n!=[1,2,1,2]: raise ValueError('Reference species changed')
 out={}
 for name,offset,expect in [('snse2',0,['Sn','Se']),('sr2n',3,['N','Sr'])]:
  cell,species,counts,xyz=poscar(name+'/POSCAR')
  if cell!=ref or species!=expect or counts!=[1,2]: raise ValueError('Cell/species mismatch')
  old=r[offset:offset+3]; shifts=[x[2]-y[2] for x,y in zip(xyz,old)]
  if max(shifts)-min(shifts)>1e-12: raise ValueError('Internal layer geometry changed')
  if any(abs(x[i]-y[i])>1e-12 for x,y in zip(xyz,old) for i in [0,1]): raise ValueError('In-plane registry changed')
  z=[x[2]*cell[2][2] for x in xyz]
  out[name]={'atoms':3,'z_shift_fractional':sum(shifts)/3,'z_min_A':min(z),'z_max_A':max(z),'thickness_A':max(z)-min(z),'empty_height_A':cell[2][2]-(max(z)-min(z))}
  print('%s: 3 atoms; rigid dz=%.12f fractional; thickness=%.9f A; empty height=%.9f A'%(name,out[name]['z_shift_fractional'],out[name]['thickness_A'],out[name]['empty_height_A']))
 if open('snse2/INCAR').read()!=open('sr2n/INCAR').read(): raise ValueError('INCAR protocols differ')
 if open('snse2/KPOINTS').read()!=open('sr2n/KPOINTS').read(): raise ValueError('KPOINTS protocols differ')
 out['common_cell_A']=ref
 print('Common cell, INCAR and KPOINTS: identical')
 return out

def read_eigenval(p):
 f=open(p); head=[f.readline() for _ in range(5)]
 if int(head[0].split()[-1])!=1: raise ValueError('Only ISPIN=1 scalar EIGENVAL is supported')
 ne,nk,nb=map(int,f.readline().split()); points=[]
 for ik in range(nk):
  l=f.readline()
  while l and not l.strip(): l=f.readline()
  k=list(map(float,l.split()))
  if len(k)!=4: raise ValueError('Invalid or truncated k-point header')
  bands=[]
  for ib in range(nb):
   row=list(map(float,f.readline().split()))
   if len(row)!=3 or row[0]!=ib+1: raise ValueError('Invalid band row')
   if not all(not math.isnan(x) and not math.isinf(x) for x in row): raise ValueError('Non-finite eigenvalue')
   if row[2]<-1e-6 or row[2]>1+1e-6: raise ValueError('Unexpected non-spin occupation convention')
   bands.append(row[1:])
  points.append((k,bands))
 f.close()
 w=sum(k[3] for k,rows in points)
 if abs(w-1)>1e-6: raise ValueError('Expected normalized SCF k weights')
 # VASP 5.4.4 scalar EIGENVAL occupations are per spin, in [0,1].
 count=2*sum(k[3]*sum(row[1] for row in rows) for k,rows in points)
 if abs(count-ne)>2e-4: raise ValueError('Weighted occupations do not reproduce NELECT: %.9f vs %d'%(count,ne))
 return ne,nk,nb,points,count

def result(name):
 out=open(name+'/OUTCAR').read()
 if 'aborting loop because EDIFF is reached' not in out or 'General timing and accounting' not in out:
  raise ValueError(name+': SCF convergence/final accounting missing')
 if int(re.search(r'ISPIN\s*=\s*(\d+)',out).group(1))!=1: raise ValueError('Wrong ISPIN')
 ef=float(re.findall(r'E-fermi\s*:\s*([-+0-9.]+)',out)[-1])
 elapsed=float(re.findall(r'Elapsed time \(sec\):\s*([0-9.]+)',out)[-1])
 ne,nk,nb,points,count=read_eigenval(name+'/EIGENVAL')
 if abs(float(re.search(r'NELECT\s*=\s*([0-9.]+)',out).group(1))-ne)>1e-8: raise ValueError('OUTCAR/EIGENVAL electron counts differ')
 crossing=[]; ext=[]; partial=[]
 for ib in range(nb):
  energies=[r[ib][0] for k,r in points]; occ=[r[ib][1] for k,r in points]
  item={'band':ib+1,'emin_eV':min(energies),'emax_eV':max(energies),'occ_min':min(occ),'occ_max':max(occ)}
  ext.append(item)
  if min(energies)<ef<max(energies): crossing.append(ib+1)
  if any(1e-3<x<1-1e-3 for x in occ): partial.append(ib+1)
 res={'fermi_eV':ef,'electrons':ne,'weighted_electrons':count,'nkpoints':nk,'bands':nb,'crossing_bands':crossing,'partially_occupied_bands':partial,'band_extrema':ext,'elapsed_seconds':elapsed,'windows':[],'hashes':{x:sha(name+'/'+x) for x in ['INCAR','POSCAR','KPOINTS','OUTCAR','OSZICAR','EIGENVAL','LOCPOT']}}
 if ne%2==0:
  ib=ne//2
  val=[(r[ib-1][0],i,k[:3]) for i,(k,r) in enumerate(points)]
  con=[(r[ib][0],i,k[:3]) for i,(k,r) in enumerate(points)]
  vbm=max(val);cbm=min(con);gap=cbm[0]-vbm[0]
  if gap>0 and not crossing:
   res.update({'classification':'gapped_on_sampled_mesh','vbm_eV':vbm[0],'cbm_eV':cbm[0],'gap_eV':gap,'vbm_k_fractional':vbm[2],'cbm_k_fractional':cbm[2],'vbm_band':ib,'cbm_band':ib+1})
  else: res['classification']='metallic_on_sampled_mesh' if crossing else 'no_global_gap'
 else:
  if not crossing: raise ValueError(name+': odd-electron scalar case has no sampled crossing; inspect manually')
  res['classification']='metallic_on_sampled_mesh'
 p=json.load(open(name+'/potential-summary.json'))
 if p['source_sha256']!=sha(name+'/LOCPOT'): raise ValueError('Potential summary is stale')
 if len(p['windows'])!=2: raise ValueError('Expected exactly two vacuum windows')
 for side,w in zip(['lower_z','upper_z'],p['windows']):
  if w['range_eV']>0.005: raise ValueError(name+' '+side+': vacuum not flat within 5 meV')
  item=dict(w); item['side']=side; item['fermi_minus_vacuum_eV']=ef-w['mean_eV'];item['workfunction_eV']=w['mean_eV']-ef
  if 'vbm_eV' in res:
   item['vbm_minus_vacuum_eV']=res['vbm_eV']-w['mean_eV'];item['cbm_minus_vacuum_eV']=res['cbm_eV']-w['mean_eV']
  res['windows'].append(item)
 print('%s: NELECT=%d; weighted electrons=%.8f; NKPTS=%d; NBANDS=%d; elapsed=%.3f s'%(name,ne,count,nk,nb,elapsed))
 print('  E_F=%.6f eV; classification=%s; crossing bands=%s'%(ef,res['classification'],crossing))
 for ib in crossing:
  e=ext[ib-1];print('  band %d: Emin=%.6f eV; Emax=%.6f eV; occupation=%.6f:%.6f'%(ib,e['emin_eV'],e['emax_eV'],e['occ_min'],e['occ_max']))
 if 'gap_eV' in res: print('  VBM=%.6f eV; CBM=%.6f eV; sampled gap=%.6f eV'%(res['vbm_eV'],res['cbm_eV'],res['gap_eV']))
 for w in res['windows']:
  print('  %s V_vac=%.9f eV; range=%.6g eV; Phi=%.9f eV'%(w['side'],w['mean_eV'],w['range_eV'],w['workfunction_eV']))
 return res

if __name__=='__main__':
 import sys
 g=geometry()
 if '--geometry-only' in sys.argv:
  json.dump(g,open('geometry-check.json','w'),indent=2,sort_keys=True)
 else:
  results={name:result(name) for name in ['snse2','sr2n']}
  a=results['snse2'];b=results['sr2n']
  if a['classification']!='gapped_on_sampled_mesh' or b['classification']!='metallic_on_sampled_mesh': raise ValueError('The expected semiconductor/metal scope is not supported')
  av=a['windows'][0];bv=b['windows'][1]
  ref={'snse2_side':'lower_z','sr2n_side':'upper_z','cbm_minus_metal_fermi_eV':av['cbm_minus_vacuum_eV']-bv['fermi_minus_vacuum_eV'],'metal_fermi_minus_vbm_eV':bv['fermi_minus_vacuum_eV']-av['vbm_minus_vacuum_eV'],'scope':'Frozen isolated layers, scalar nonmagnetic PBE-D3 (zero damping); not an interface barrier'}
  summary={'geometry':g,'layers':results,'interface_facing_isolated_reference':ref}
  json.dump(summary,open('alignment-summary.json','w'),indent=2,sort_keys=True)
  print('Facing isolated references: CBM(SnSe2)-E_F(Sr2N)=%.6f eV; E_F(Sr2N)-VBM(SnSe2)=%.6f eV'%(ref['cbm_minus_metal_fermi_eV'],ref['metal_fermi_minus_vbm_eV']))
