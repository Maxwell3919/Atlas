from __future__ import print_function
import itertools,math,json,csv

def read_poscar(name):
    s=open(name).readlines();scale=float(s[1]);cell=[[float(v)*scale for v in l.split()[:3]] for l in s[2:5]]
    n=sum(map(int,s[6].split()))
    if not s[7].lower().startswith('d'):raise ValueError('Direct coordinates required')
    f=[list(map(float,l.split()[:3])) for l in s[8:8+n]]
    return cell,f

def enumerate_cell(name,label):
    cell,f=read_poscar(name);n=len(f);a=math.sqrt(sum(x*x for x in cell[1]));distance=math.sqrt(3)*a/2
    bonds=set();coordination=[0]*n
    for i,j in itertools.product(range(n),repeat=2):
        for t in itertools.product([-1,0,1],repeat=3):
            delta=[sum((f[j][k]+t[k]-f[i][k])*cell[k][d] for k in range(3)) for d in range(3)]
            r=math.sqrt(sum(v*v for v in delta))
            if abs(r-distance)<1e-9:
                coordination[i]+=1
                forward=(i,j)+t;reverse=(j,i)+tuple(-v for v in t)
                bonds.add(min(forward,reverse))
    if any(z!=8 for z in coordination):raise ValueError('bcc nearest-neighbor coordination is not eight')
    bonds=sorted(bonds)
    with open('bonds-'+label+'.csv','w') as out:
        w=csv.writer(out);w.writerow(['atom_i','atom_j','shift_x','shift_y','shift_z','distance_A'])
        for row in bonds:w.writerow([row[0]+1,row[1]+1]+list(row[2:])+[distance])
    return {'n_atoms':n,'neighbor_distance_A':distance,'coordination':coordination,'n_unique_bonds':len(bonds),'bonds':[list(t) for t in bonds]}

if __name__=='__main__':
    cells={'2fe':enumerate_cell('fm2/POSCAR','2fe'),'4fe':enumerate_cell('fm4/POSCAR','4fe')}
    states=[('fm2','2fe',[1,1]),('afm2','2fe',[1,-1]),('fm4','4fe',[1,1,1,1]),('neel4','4fe',[1,-1,1,-1]),('stripe4','4fe',[1,1,-1,-1])]
    report={'definition':'H = Eref - J * sum_unique_periodic_NN_bonds(e_i dot e_j); unit vectors; each bond counted once','cells':cells,'states':{}}
    for name,label,spin in states:
        corr=sum(spin[b[0]]*spin[b[1]] for b in cells[label]['bonds'])
        report['states'][name]={'cell':label,'spin_directions':spin,'correlation_sum':corr}
        print('%s: N=%d; neighbors/site=%s; unique bonds=%d; correlation sum=%+d'%(name,cells[label]['n_atoms'],cells[label]['coordination'],cells[label]['n_unique_bonds'],corr))
    json.dump(report,open('bonds-summary.json','w'),indent=2)
    print('nearest-neighbor distance = %.10f A'%cells['2fe']['neighbor_distance_A'])
