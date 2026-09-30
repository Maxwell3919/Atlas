from __future__ import print_function
import math,sys,json,csv,itertools,hashlib,os

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(a): return math.sqrt(dot(a,a))
def read_poscar(name):
    s=open(name).readlines(); scale=float(s[1])
    if scale<=0:raise ValueError('Positive POSCAR scale required')
    cell=[[float(x)*scale for x in row.split()[:3]] for row in s[2:5]]
    species=s[5].split();counts=list(map(int,s[6].split()))
    if len(species)!=len(counts):raise ValueError('Species/count mismatch')
    if not s[7].strip().lower().startswith('d'):raise ValueError('This example expects Direct coordinates')
    f=[list(map(float,row.split()[:3])) for row in s[8:8+sum(counts)]]
    if len(f)!=sum(counts) or any(len(row)!=3 for row in f):raise ValueError('Incomplete atomic coordinates')
    if any(not 0<=row[2]<1 for row in f):raise ValueError('Unwrap/recenter fractional c coordinates first')
    syms=[el for el,n in zip(species,counts) for _ in range(n)]
    xyz=[[sum(row[i]*cell[i][j] for i in range(3)) for j in range(3)] for row in f]
    n=cross(cell[0],cell[1]);n=[x/norm(n) for x in n]
    height=dot(cell[2],n)
    if height<=0:raise ValueError('Expected right-handed slab cell')
    return cell,f,xyz,syms,n,height

def analyze(name,label):
    cell,f,xyz,symbols,n,height=read_poscar(name)
    if sorted(symbols)!=sorted(['Sn','Se','Se','N','Sr','Sr']):raise ValueError('Expected SnSe2/Sr2N six-atom model')
    zz=[dot(row,n) for row in xyz]
    a=[i for i,x in enumerate(symbols) if x in ['Sn','Se']];b=[i for i,x in enumerate(symbols) if x in ['Sr','N']]
    za=[zz[i] for i in a];zb=[zz[i] for i in b]
    if min(za)<=max(zb):raise ValueError('Expected separated SnSe2 upper layer and Sr2N lower layer')
    def dist(i,j):
        return min(norm([sum((f[i][k]-f[j][k]+shift[k])*cell[k][d] for k in range(3)) for d in range(3)]) for shift in itertools.product([-1,0,1],repeat=3))
    report={'file':os.path.basename(name),'sha256':hashlib.sha256(open(name,'rb').read()).hexdigest(),'n_atoms':len(symbols),'a_A':norm(cell[0]),'b_A':norm(cell[1]),'gamma_deg':math.degrees(math.acos(dot(cell[0],cell[1])/norm(cell[0])/norm(cell[1]))),'normal_height_A':height,'normal_gap_A':min(za)-max(zb),'minimum_interlayer_distance_A':min(dist(i,j) for i in a for j in b),'empty_interval_A':height-max(zz)+min(zz),'slab_center_normal_A':(max(zz)+min(zz))/2,'SnSe2_thickness_A':max(za)-min(za),'Sr2N_thickness_A':max(zb)-min(zb),'cell':cell}
    with open(label+'-atoms.csv','w') as out:
        w=csv.writer(out);w.writerow(['index','element','layer','x_A','y_A','z_A','normal_A'])
        for i,(el,row) in enumerate(zip(symbols,xyz)):w.writerow([i+1,el,'SnSe2' if el in ['Sn','Se'] else 'Sr2N']+row+[zz[i]])
    return report,(cell,f,xyz,symbols,n,height)

if __name__=='__main__':
    before,old=analyze('POSCAR.reference','reference')
    after,new=analyze('POSCAR.gap3p0','gap3p0')
    ref=read_poscar('POSCAR.SnSe2.reference')
    shift_by_layer=[]
    for ids in [[0,1,2],[3,4,5]]:
        shifts=[new[1][i][2]-old[1][i][2] for i in ids]
        if max(shifts)-min(shifts)>1e-12:raise ValueError('Layer was not moved rigidly')
        shift_by_layer.append(shifts[0])
    maxcell=max(abs(x-y) for a,b in zip(old[0],new[0]) for x,y in zip(a,b))
    maxxy=max(abs(old[1][i][j]-new[1][i][j]) for i in range(6) for j in [0,1])
    if maxcell>1e-12 or maxxy>1e-12:raise ValueError('Unexpected cell or lateral-registry change')
    if abs(after['normal_gap_A']-3)>1e-10:raise ValueError('Target gap was not attained')
    if abs(after['slab_center_normal_A']-after['normal_height_A']/2)>1e-10:raise ValueError('Slab is not centered')
    comp={'max_cell_change_A':maxcell,'max_fractional_xy_change':maxxy,'rigid_fractional_c_shifts_SnSe2_Sr2N':shift_by_layer,'SnSe2_reference_a_A':norm(ref[0][0]),'SnSe2_reference_b_A':norm(ref[0][1]),'SnSe2_a_extension_percent':100*(after['a_A']/norm(ref[0][0])-1),'SnSe2_b_extension_percent':100*(after['b_A']/norm(ref[0][1])-1),'a_vector_angle_to_SnSe2_reference_deg':math.degrees(math.atan2(new[0][0][1],new[0][0][0])-math.atan2(ref[0][0][1],ref[0][0][0]))}
    json.dump({'reference':before,'gap3p0':after,'comparison':comp},open('model-check.json','w'),indent=2)
    for label,r in [('reference',before),('gap3p0',after)]:
        print('%s: atoms=%d a=%.10f b=%.10f gamma=%.6f height=%.10f A'%(label,r['n_atoms'],r['a_A'],r['b_A'],r['gamma_deg'],r['normal_height_A']))
        print('  normal gap=%.10f A; nearest interlayer distance=%.10f A; empty interval=%.10f A'%(r['normal_gap_A'],r['minimum_interlayer_distance_A'],r['empty_interval_A']))
        print('  layer thickness: SnSe2=%.10f A; Sr2N=%.10f A; slab center=%.10f A'%(r['SnSe2_thickness_A'],r['Sr2N_thickness_A'],r['slab_center_normal_A']))
    print('cell unchanged; fractional x/y unchanged; both layers moved rigidly')
    print('fractional c shifts SnSe2/Sr2N = %.16f %.16f'%tuple(shift_by_layer))
    print('relative to SnSe2 reference: a extension=%.8f%%; b extension=%.8f%%; a-axis rotation=%.10f deg'%(comp['SnSe2_a_extension_percent'],comp['SnSe2_b_extension_percent'],comp['a_vector_angle_to_SnSe2_reference_deg']))
    print('Wrote model-check.json, reference-atoms.csv and gap3p0-atoms.csv')
