from __future__ import print_function
import csv,json,math
rows=[]
for size in (96,192):
    entries=[]
    for line in open(str(size)+'/ACF.dat'):
        fields=line.split()
        if len(fields)==7 and fields[0].isdigit():
            atom=int(fields[0]);charge=float(fields[4])
            entries.append((atom,charge,float(fields[5]),float(fields[6])))
    if [r[0] for r in entries]!=[1,2]:raise ValueError('Expected exactly two Fe basins')
    if abs(sum(r[1] for r in entries)-16)>2e-6:raise ValueError('Basin electron sum differs')
    if abs(sum(r[3] for r in entries)-21.952)>2e-6:raise ValueError('Basin volume sum differs')
    report=json.load(open(str(size)+'/charge-grid-check.json'))
    if report['grid']!=[size]*3:raise ValueError('Wrong grid report')
    for atom,charge,distance,volume in entries:
        rows.append([size,atom,charge,charge-8.,8.-charge,distance,volume,
                     report['AECCAR0_integral'],report['reference_integral']])
        print('%d^3 atom %d: N_Bader=%.6f, delta_N=%+.6f, Q=%+.6f e'%
              (size,atom,charge,charge-8.,8.-charge))
    print('%d^3 basin_sum=%.6f e; volume_sum=%.6f A^3; core_integral=%.9f e'%
          (size,sum(r[1] for r in entries),sum(r[3] for r in entries),report['AECCAR0_integral']))
with open('bader-grid.csv','w') as handle:
    writer=csv.writer(handle,lineterminator='\n')
    writer.writerow(['grid','atom','basin_e','delta_e','net_charge_e','min_dist_A','volume_A3',
                     'core_integral_e','reference_integral_e'])
    writer.writerows(rows)
