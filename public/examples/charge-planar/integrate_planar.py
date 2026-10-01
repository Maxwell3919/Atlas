#!/usr/bin/env python3
"""Integrate matched frozen-fragment CHGCAR first blocks along the a×b normal.
Dependencies: numpy, sibling build_delta_chgcar.py. Input files are read only.
NELECT additivity is checked; fragment neutrality/charge states are not inferred.
Establish each charge state from its own input/OUTCAR and valence protocol.
Boundaries refer to physical normal distance in Angstrom; piecewise linear
interpolation of periodic plane values defines the cumulative integral.
"""
import argparse, csv, json
from pathlib import Path
import numpy as np
from build_delta_chgcar import read_chgcar, check_same_cell_and_grid

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for label in ('ab','a','b'): p.add_argument('--'+label,type=Path,required=True)
    p.add_argument('--nelect',type=float,nargs=3,required=True,metavar=('AB','A','B'))
    p.add_argument('--boundaries',type=float,nargs='+',required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args()
    if a.output_dir.exists(): raise FileExistsError('Choose a new output directory')
    if not all(np.isfinite(a.nelect)) or abs(a.nelect[0]-sum(a.nelect[1:]))>1e-8:
        raise ValueError('Additive fragment electron counts are required; fragment charge states must be established from the input protocol')
    data={k:read_chgcar(getattr(a,k.lower())) for k in ('AB','A','B')}
    check_same_cell_and_grid(data)
    for k,n in zip(('AB','A','B'),a.nelect):
        if not np.isfinite(data[k]['values']).all(): raise ValueError('Nonfinite density')
        integral=float(data[k]['values'].mean())
        if abs(integral-n)>1e-5: raise ValueError(k+': integral differs from stated NELECT')
    ref=data['AB'];cell=ref['cell'];volume=ref['volume_A3']
    area=float(np.linalg.norm(np.cross(cell[0],cell[1])));height=volume/area
    nx,ny,nz=ref['dimensions'];dz=height/nz
    edges=np.array(a.boundaries,dtype=float)
    if len(edges)<2 or not np.isfinite(edges).all() or np.any(np.diff(edges)<=0):
        raise ValueError('Need at least two ordered finite boundaries')
    if edges[0]<0 or edges[-1]>height+1e-8: raise ValueError('Boundary outside cell')
    delta=ref['values']-data['A']['values']-data['B']['values']
    density=delta.reshape(nz,ny,nx).mean(axis=(1,2))/volume
    z=np.arange(nz+1)*dz;plane=np.r_[density,density[0]];linear=area*plane
    cumulative=np.r_[0.,np.cumsum(.5*(linear[:-1]+linear[1:])*dz)]
    def at(x):
        if abs(x-height)<1e-8: return float(cumulative[-1])
        k=int(np.floor(x/dz));h=x-z[k]
        return float(cumulative[k]+linear[k]*h+.5*(linear[k+1]-linear[k])*h*h/dz)
    rows=[]
    for lo,hi in zip(edges[:-1],edges[1:]):
        number=at(hi)-at(lo)
        rows.append(dict(lo_A=float(lo),hi_A=float(hi),delta_e=number,
                         delta_e_per_A2=number/area,delta_e_per_cm2=number/area*1e16))
    residual=float(delta.mean())
    if abs(residual)>1e-6: raise ValueError('Difference electron count does not close')
    if abs(cumulative[-1]-residual)>1e-10: raise ValueError('Periodic integral mismatch')
    summary=dict(definition='delta_n=n_AB-n_A-n_B; positive means electron gain',
      input_integrals_e={k:float(v['values'].mean()) for k,v in data.items()},
      area_A2=area,height_A=height,volume_A3=volume,grid=list(ref['dimensions']),
      full_cell_residual_e=residual,cumulative_endpoint_e=float(cumulative[-1]),
      positive_3d_e=float(np.maximum(delta,0).mean()),negative_3d_e=float(np.minimum(delta,0).mean()),
      boundaries_A=edges.tolist(),regions=rows,
      source_sha256_uncompressed={k:v['sha256_uncompressed'] for k,v in data.items()},
      quadrature='periodic piecewise linear plane density; exact partial-segment integral',
      scope='spatial redistribution relative to frozen fragments; not mobile carrier density')
    a.output_dir.mkdir(parents=True)
    with (a.output_dir/'planar.csv').open('x',newline='') as f:
        w=csv.writer(f);w.writerow(['z_A','delta_n_e_A3','linear_e_A','cumulative_e'])
        w.writerows(zip(z,plane,linear,cumulative))
    with (a.output_dir/'regions.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (a.output_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(f'area={area:.9f} A^2; height={height:.9f} A; grid={nx} {ny} {nz}')
    print(f'full-cell residual={residual:.12e} e; cumulative endpoint={cumulative[-1]:.12e} e')
    for r in rows: print(f'{r["lo_A"]:.6f}:{r["hi_A"]:.6f} A: delta_e={r["delta_e"]:+.12e}; area_density={r["delta_e_per_cm2"]:+.12e} e/cm^2')
    print(f'positive 3D redistribution={summary["positive_3d_e"]:.10f} e')

if __name__=='__main__': main()
