一个候选即使相对元素的形成能较低，也可能通过分解成其他化合物进一步降低能量。凸包要找的是：在固定总成分下，候选集合中哪一种相或哪几个相的混合具有最低能量，以及目标候选比它高多少。本例沿用 [形成能计算](/Atlas/m/formation-energy/qe/) 的五个 Al–Si 候选，求出它们之间的最低能量分解连线；结构优化、SCF 与元素参考从形成能页进入。

本次集合只有 fcc Al、diamond Si、B2 AlSi、L1₂ Al₃Si 与 L1₂ AlSi₃。图上横轴是 **Si 的原子分数** `x=N(Si)/[N(Al)+N(Si)]`，纵轴是 **每原子形成能**。每个成分只放入了这次真正计算的一个原型，因此这是一张有限候选集的下凸包。

[Ong 等的 pymatgen 方法论文](https://perssongroup.lbl.gov/papers/compmatsci2013-pymatgen.pdf)第 4.3 节将相稳定性写成候选相与竞争相的能量比较，第 6 节和 Fig. 4 用 Li–Sn–S 的竞争相集合演示这一分析。本例用已有的 Al–Si 能量表构造同样的成分—能量下边界：候选到所在边界线段的能量差，就是本集合内的 above-hull 距离。原始计算来自 QE，构造凸包的运算读取组成与匹配能量表。

[下载同一批形成能与凸包数据](/Atlas/examples/alsi-formation-hull-files.tar.gz)。解压后进入 `alsi-formation-hull`，可直接从原始输出重算表格和图。

[Materials Project：形成能与相图方法](https://docs.materialsproject.org/methodology/materials-methodology/thermodynamic-stability/phase-diagrams-pds) · [QE：pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [AFLOW：晶体原型库](https://aflow.org/prototype-encyclopedia/)

## 从成分和形成能读出分解组合

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ head -n 6 formation-summary.csv
case,natoms,xSi,total_energy_Ry,formation_eV_atom,above_hull_eV_atom
al-fcc,1,0.0,-5.039590195089586,0.0,0.0
al3si-l12,4,0.25,-26.50736500358702,0.10725675700580338,0.10725675700580338
alsi-b2,2,0.5,-16.420651190216674,0.2657622360640055,0.2657622360640055
alsi3-l12,4,0.75,-39.192394827064,0.36591606137492194,0.36591606137492194
si-diamond,2,1.0,-22.84025464653608,0.0,0.0
[preston@preston-System-Product-Name alsi-formation-hull]$
```

Al 端元的 x=0，Si 端元的 x=1；Al₃Si、AlSi、AlSi₃ 依次在 0.25、0.5、0.75。Si 输入里有两个原子，仍然是 x=1；不能把晶胞原子个数当成组分轴，也不能让四原子晶胞的总能直接和一原子端元的总能比高低。

先用两端元在 x=0.25 处构造一个混合物：其原子分数是 75% Al、25% Si。两端元的形成能都按定义设为零，所以这条连线上任意成分的形成能都是零。与 Al₃Si 晶胞对应的分解反应可写成 `Al₃Si → 3 Al + Si`；方程里的 3:1 是原子数比，图中的权重则是 0.75:0.25。

```text
hull_energy(x) = w_left × ΔE_form(left) + w_right × ΔE_form(right)
w_right = (x − x_left) / (x_right − x_left)
w_left = 1 − w_right
energy_above_hull(x) = ΔE_form(candidate) − hull_energy(x)
```

这些式子也适用于端元之间存在更低中间相的情况；那时要用包住目标成分的两个相邻凸包顶点，不能永远减零。本次三个中间候选都高于 Al–Si 端元连线，所以计算得到的凸包顶点只有两个端元。

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ python3 analyse_alsi.py
case           xSi   total_energy(Ry/cell) formation(eV/atom) above_hull(eV/atom)
al-fcc          0.00        -5.0395901951         0.00000000          0.00000000
al3si-l12       0.25       -26.5073650036         0.10725676          0.10725676
alsi-b2         0.50       -16.4206511902         0.26576224          0.26576224
alsi3-l12       0.75       -39.1923948271         0.36591606          0.36591606
si-diamond      1.00       -22.8402546465         0.00000000          0.00000000
Finite-set hull vertices: al-fcc, si-diamond
Numerical differences: numerical-checks.csv (1 meV/atom teaching comparison line)
[preston@preston-System-Product-Name alsi-formation-hull]$
```

| 候选 | xSi | 下凸包 / eV·atom⁻¹ | 高于下凸包 / meV·atom⁻¹ | 对应端元组合 |
| --- | --- | --- | --- | --- |
| al-fcc | 0.0 | 0.000000 | 0.000 | 1.00 Al + 0.00 Si（原子分数） |
| al3si-l12 | 0.25 | 0.000000 | 107.257 | 0.75 Al + 0.25 Si（原子分数） |
| alsi-b2 | 0.5 | 0.000000 | 265.762 | 0.50 Al + 0.50 Si（原子分数） |
| alsi3-l12 | 0.75 | 0.000000 | 365.916 | 0.25 Al + 0.75 Si（原子分数） |
| si-diamond | 1.0 | 0.000000 | 0.000 | 0.00 Al + 1.00 Si（原子分数） |

三个候选分别高于端元混合物 107.257、265.762、365.916 meV/atom。下凸包由本次五个候选构成；加入新原型、降对称结构或磁态后，以同协议计算并重建边界。

## 构造下边界并画图

提取脚本先按 x 排序，再逐个保留使相邻连线斜率递增的点，得到下边界；然后把每个候选投到对应的边界线段上，计算高度差。处理数值误差时使用很小的几何比较阈值，并保留未四舍五入的形成能。画图时才格式化小数位。代码在 [analyse_alsi.py](/Atlas/examples/alsi-formation-hull/analyse_alsi.py)，输入汇总在 [formation-energy.csv](/Atlas/examples/alsi-formation-hull/formation-energy.csv)；原始 30 项协议对照在 [energy-table.csv](/Atlas/examples/alsi-formation-hull/energy-table.csv)。

从原始输出运行 `analyse_alsi.py` 需要 Python 3 和 NumPy；运行 `plot_alsi.py` 绘图还需要 Matplotlib，并保留同目录的 `atlas_plot_style.py`。后面的 `review_alsi_thermo.py` 只读取已提取的 CSV，使用 Python 标准库。

<details>
<summary>analyse_alsi.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Read actual QE 7.5 outputs; compare matched Al--Si candidate sets."""
from pathlib import Path
import csv, hashlib, json, re, shutil, xml.etree.ElementTree as ET
import numpy as np

ROOT=Path(__file__).resolve().parent
RY_EV=13.605693122994
BOHR_A=0.529177210903
CASES={'al-fcc':(1,0),'al3si-l12':(3,1),'alsi-b2':(1,1),'alsi3-l12':(1,3),'si-diamond':(0,2)}
PROTOCOLS=['k12','k16','k20','sigma005','cutoff80','k24']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def numbers(node):return np.array([float(v) for v in node.text.split()])
def save_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def qexml(path):
    r=ET.parse(path).getroot()
    assert r.get('Units')=='Hartree atomic units'
    assert r.find('general_info/creator').get('VERSION')=='7.5'
    return r
def read_run(case,label):
    folder=ROOT/case/label
    txt=(folder/'scf.out').read_text()
    if txt.count('JOB DONE.')!=1 or 'convergence has been achieved' not in txt:
        raise ValueError(f'Incomplete native SCF: {case}/{label}')
    last_iteration=re.split(r'\n\s+iteration #\s*\d+',txt)[-1]
    if re.search(r'Error in routine|convergence NOT',txt,re.I) or 'not converged' in last_iteration:
        raise ValueError(f'Adverse native SCF: {case}/{label}')
    p=folder/'data-file-schema.xml'
    if not p.exists():shutil.copy2(folder/'tmp'/f'{case}.save'/'data-file-schema.xml',p)
    r=qexml(p);out=r.find('output')
    conv=out.find('convergence_info/scf_conv/convergence_achieved')
    assert conv is not None and conv.text.strip()=='true'
    e_ry=float(out.find('total_energy/etot').text)*2
    printed=float(re.findall(r'!\s+total energy\s+=\s+([-\d.]+)\s+Ry',txt)[-1])
    assert abs(e_ry-printed)<1e-7
    st=out.find('atomic_structure')
    cell=np.array([numbers(st.find('cell/'+a)) for a in ['a1','a2','a3']])
    atoms=st.findall('atomic_positions/atom')
    symbols=[a.get('name') for a in atoms]
    nAl,nSi=CASES[case];nat=nAl+nSi
    assert symbols.count('Al')==nAl and symbols.count('Si')==nSi
    shape={'cell':np.round(cell,9).tolist(),'symbols':symbols,'positions':[np.round(numbers(a),9).tolist() for a in atoms]}
    geometry_hash=hashlib.sha256(json.dumps(shape,sort_keys=True).encode()).hexdigest()
    inp=r.find('input')
    assert inp.find('dft/functional').text.strip()=='PBE'
    assert inp.find('spin/lsda').text.strip()=='false'
    assert inp.find('spin/noncolin').text.strip()=='false'
    assert inp.find('spin/spinorbit').text.strip()=='false'
    assert inp.find('bands/occupations').text.strip()=='smearing'
    smear=inp.find('bands/smearing');assert smear.text.strip()=='mv'
    mesh=inp.find('k_points_IBZ/monkhorst_pack')
    if mesh is None:raise ValueError('Missing echoed automatic mesh')
    k=[int(mesh.get(v)) for v in ['nk1','nk2','nk3']]
    assert len(set(k))==1
    assert [int(mesh.get(v)) for v in ['k1','k2','k3']]==[0,0,0]
    force=out.find('forces')
    fmax=float(np.linalg.norm(numbers(force).reshape(nat,3)*2,axis=1).max())
    row=dict(case=case,protocol=label,nAl=nAl,nSi=nSi,natoms=nat,xSi=nSi/nat,
             k_mesh=k[0],ecutwfc_Ry=float(inp.find('basis/ecutwfc').text)*2,
             ecutrho_Ry=float(inp.find('basis/ecutrho').text)*2,
             degauss_Ry=float(smear.get('degauss'))*2,total_energy_Ry=e_ry,
             energy_per_atom_eV=e_ry*RY_EV/nat,
             final_pressure_kbar=float(re.findall(r'P=\s*([-\d.]+)',txt)[-1]),
             initial_eigensolver_warnings=txt.count('not converged'),final_iteration_eigensolver_warnings=last_iteration.count('not converged'),
             max_force_Ry_per_bohr=fmax,volume_A3=abs(float(np.linalg.det(cell)))*BOHR_A**3,
             input_sha256=sha(folder/'scf.in'),output_sha256=sha(folder/'scf.out'),
             xml_sha256=sha(p),geometry_sha256=geometry_hash)
    return row
def lower_hull(rows):
    points=sorted(rows,key=lambda p:p['xSi'])
    hull=[]
    for p in points:
        while len(hull)>=2:
            a,b=hull[-2:]
            cross=(b['xSi']-a['xSi'])*(p['formation_eV_atom']-a['formation_eV_atom'])-(b['formation_eV_atom']-a['formation_eV_atom'])*(p['xSi']-a['xSi'])
            if cross>1e-12:break
            hull.pop()
        hull.append(p)
    return hull
def main():
    (ROOT/'plots').mkdir(exist_ok=True)
    rows=[read_run(c,p) for p in PROTOCOLS for c in CASES]
    for case in CASES:
        assert len({r['geometry_sha256'] for r in rows if r['case']==case})==1,'Geometry differs across numerical checks'
    for label in PROTOCOLS:
        rr=[r for r in rows if r['protocol']==label]
        for key in ['k_mesh','ecutwfc_Ry','ecutrho_Ry','degauss_Ry']:
            assert len({r[key] for r in rr})==1,f'Mixed {key} in {label}'
        al=next(r for r in rr if r['case']=='al-fcc')['total_energy_Ry']
        si=next(r for r in rr if r['case']=='si-diamond')['total_energy_Ry']/2
        for r in rr:
            r['reference_energy_Ry']=r['nAl']*al+r['nSi']*si
            r['formation_eV_formula']=(r['total_energy_Ry']-r['reference_energy_Ry'])*RY_EV
            r['formation_eV_atom']=r['formation_eV_formula']/r['natoms']
        hull=lower_hull(rr)
        for r in rr:
            for left,right in zip(hull,hull[1:]):
                if left['xSi']-1e-12<=r['xSi']<=right['xSi']+1e-12:
                    wr=(r['xSi']-left['xSi'])/(right['xSi']-left['xSi']);wl=1-wr
                    r.update(hull_eV_atom=wl*left['formation_eV_atom']+wr*right['formation_eV_atom'],
                             hull_left=left['case'],hull_right=right['case'],left_atom_fraction=wl,right_atom_fraction=wr)
                    break
            r['above_hull_eV_atom']=r['formation_eV_atom']-r['hull_eV_atom']
            assert r['above_hull_eV_atom']>=-1e-10
    save_csv(ROOT/'energy-table.csv',rows)
    final=[r for r in rows if r['protocol']=='k24']
    save_csv(ROOT/'formation-energy.csv',final)
    save_csv(ROOT/'formation-summary.csv',[{k:r[k] for k in ['case','natoms','xSi','total_energy_Ry','formation_eV_atom','above_hull_eV_atom']} for r in final])
    checks=[]
    for case in CASES:
        if case in ['al-fcc','si-diamond']:continue
        d={r['protocol']:r for r in rows if r['case']==case}
        for a,b,axis in [('k12','k16','k mesh at sigma .01'),('k16','k20','k mesh at sigma .01'),('k20','sigma005','smearing at k20'),('sigma005','cutoff80','wavefunction cutoff at k20'),('cutoff80','k24','k mesh at sigma .005')]:
            delta=(d[b]['formation_eV_atom']-d[a]['formation_eV_atom'])*1000
            checks.append(dict(case=case,axis=axis,from_protocol=a,to_protocol=b,formation_change_meV_atom=delta,within_1meV_atom=abs(delta)<=1.0))
    save_csv(ROOT/'numerical-checks.csv',checks)
    receipt={'schema':'alsi-evidence-v1','qe_version':'7.5','energy_definition':'QE ! total energy, finite cold-smearing F=E-TS, identical setting for all five candidates within each protocol',
             'scientific_acceptance':'not_assessed','candidate_scope':'Five constrained cubic prototypes only; no global structure search, phonon/free-energy or experimental claim',
             'geometry_optimization':'Native BFGS with cell_dofree=ibrav; initial Davidson warnings preserved. Final independent CG static inputs/outputs are checked separately.',
             'numerical_line_meV_atom':1.0,'reference_per_atom_Ry':{r['case']:r['total_energy_Ry']/r['natoms'] for r in final if r['case'] in ['al-fcc','si-diamond']},
             'hull_vertices':[r['case'] for r in lower_hull(final)],'files':{str(p.relative_to(ROOT)):sha(p) for r in rows for p in [ROOT/r['case']/r['protocol']/name for name in ['scf.in','scf.out','scf.err','data-file-schema.xml']]},
             'checks':checks}
    (ROOT/'evidence/analysis-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('case           xSi   total_energy(Ry/cell) formation(eV/atom) above_hull(eV/atom)')
    for r in final:
        print(f"{r['case']:<15} {r['xSi']:4.2f} {r['total_energy_Ry']:20.10f} {r['formation_eV_atom']:18.8f} {r['above_hull_eV_atom']:19.8f}")
    print('Finite-set hull vertices:',', '.join(receipt['hull_vertices']))
    print('Numerical differences: numerical-checks.csv (1 meV/atom teaching comparison line)')
if __name__=='__main__':main()
```

</details>

```console
[preston@preston-System-Product-Name alsi-formation-hull]$ python3 plot_alsi.py hull
plots/convex-hull.png and plots/convex-hull.svg
[preston@preston-System-Product-Name alsi-formation-hull]$
```

![五个真实计算候选的下凸包](/Atlas/examples/alsi-formation-hull/plots/convex-hull.svg)

蓝线连接本集合中的下凸包顶点；方块是三个构造的中间候选；竖直虚线的长度就是表中的能量差。图的横轴是原子分数，纵轴已除以每个晶胞的总原子数。两种端元的零点来自形成能定义，原始 DFT 总能本身都不是零。

要重建这张有限凸包图，下载 [plot_alsi.py](/Atlas/examples/alsi-formation-hull/plot_alsi.py)、同目录的 [atlas_plot_style.py](/Atlas/examples/alsi-formation-hull/atlas_plot_style.py) 与 [formation-energy.csv](/Atlas/examples/alsi-formation-hull/formation-energy.csv)，然后运行 <code>python3 plot_alsi.py hull</code>。脚本写出 <code>plots/convex-hull.png</code> 和 <code>plots/convex-hull.svg</code>。

<details>
<summary>plot_alsi.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Plot the actual tables produced by analyse_alsi.py; no QE installation needed."""

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import argparse,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
BLUE='#0072b2';ORANGE='#d55e00';GRAY='#657081'
LABELS={'al-fcc':'Al (fcc)','al3si-l12':'Al₃Si (L1₂)','alsi-b2':'AlSi (B2)','alsi3-l12':'AlSi₃ (L1₂)','si-diamond':'Si (diamond)'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
def read(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))
def save(fig,name):
    (ROOT/'plots').mkdir(exist_ok=True)
    for suffix in ['png','svg']:fig.savefig(ROOT/'plots'/f'{name}.{suffix}',bbox_inches='tight')
    plt.close(fig)
    print(f'plots/{name}.png and plots/{name}.svg')
def formation():
    rows=[r for r in read('formation-energy.csv') if r['case'] not in ['al-fcc','si-diamond']]
    checks=read('numerical-checks.csv')
    fig,axes=plt.subplots(1,2,figsize=(12,4.2),layout='constrained',gridspec_kw={'width_ratios':[1,1.8]})
    x=np.arange(len(rows));y=np.array([float(r['formation_eV_atom']) for r in rows])
    axes[0].bar(x,y,color=BLUE,width=.64)
    for xx,yy in zip(x,y):axes[0].text(xx,yy+max(y)*.025,f'{yy:.3f}',ha='center')
    axes[0].set_xticks(x,[LABELS[r['case']].replace(' ','\n',1) for r in rows]);axes[0].set_ylim(0,max(y)*1.2)
    axes[0].set_ylabel('Formation energy (eV/atom)');axes[0].set_title('Same reference energies and protocol')
    transitions=[('k12','k16','k:12→16'),('k16','k20','k:16→20'),('k20','sigma005','σ:0.01→0.005'),('sigma005','cutoff80','cutoff:60→80'),('cutoff80','k24','k:20→24')]
    colors=[BLUE,ORANGE,'#009e73']
    for case,col in zip([r['case'] for r in rows],colors):
        yy=[float(next(c for c in checks if c['case']==case and c['from_protocol']==a and c['to_protocol']==b)['formation_change_meV_atom']) for a,b,_ in transitions]
        axes[1].plot(np.arange(len(transitions)),yy,'o-',label=LABELS[case],color=col,ms=5)
    axes[1].axhspan(-1,1,color='#dde8f0',alpha=.7,label='±1 meV/atom comparison line')
    axes[1].axhline(0,color=GRAY,lw=.7);axes[1].set_xticks(np.arange(len(transitions)),[x[2] for x in transitions],rotation=25,ha='right')
    axes[1].set_ylabel('Change in formation energy (meV/atom)');axes[1].set_title('Controlled numerical checks at fixed geometry')
    axes[1].legend(fontsize=8,loc='best');axes[1].grid(axis='y',alpha=.15)
    save(fig,'formation-energy')
def hull():
    rows=sorted(read('formation-energy.csv'),key=lambda r:float(r['xSi']))
    fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
    x=np.array([float(r['xSi']) for r in rows]);y=np.array([float(r['formation_eV_atom']) for r in rows]);h=np.array([float(r['hull_eV_atom']) for r in rows])
    nodes=[r for r in rows if abs(float(r['above_hull_eV_atom']))<1e-10]
    ax.plot([float(r['xSi']) for r in nodes],[float(r['formation_eV_atom']) for r in nodes],color=BLUE,lw=2,label='Lower hull of these five candidates')
    for r,xx,yy,hh in zip(rows,x,y,h):
        if yy-hh>1e-10:
            ax.vlines(xx,hh,yy,color=ORANGE,ls='--',lw=1)
            ax.scatter([xx],[yy],s=55,marker='s',color=ORANGE,zorder=3)
            ax.annotate(LABELS[r['case']],(xx,yy),xytext=(0,10),textcoords='offset points',ha='center')
            ax.text(xx+.018,(yy+hh)/2,f'{1000*(yy-hh):.1f}\nmeV/atom',rotation=0,va='center',fontsize=8,color=GRAY)
        else:
            ax.scatter([xx],[yy],s=58,color=BLUE,zorder=3)
            ax.annotate(LABELS[r['case']],(xx,yy),xytext=(4,10) if xx==0 else (-4,10),textcoords='offset points',ha='left' if xx==0 else 'right')
    ax.set_xlim(-.04,1.04);ax.set_ylim(-.025,max(y)*1.23);ax.set_xticks([0,.25,.5,.75,1]);ax.set_xlabel('Si atomic fraction x = N(Si) / [N(Al) + N(Si)]')
    ax.set_ylabel('Formation energy (eV/atom)');ax.set_title('Al–Si: a finite set of constrained cubic prototypes')
    ax.legend(fontsize=9,loc='upper right');ax.grid(axis='y',alpha=.12)
    save(fig,'convex-hull')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('figure',choices=['formation','hull','all']);a=p.parse_args()
    if a.figure in ['formation','all']:formation()
    if a.figure in ['hull','all']:hull()
```

</details>

## 把 32³ 的同一组候选再放上来

前面的表和图对应 24³。随后完成的 32³ 结果使用相同候选、相同固定几何与 80/640 Ry、`mv=0.005 Ry` 协议，电子求解和父文件核对见[形成能页的 32³ 对照](/Atlas/m/formation-energy/qe/)。端元也在 32³ 下重新计算，因此能量零点随本组端元重新建立。

[独立补充包](/Atlas/examples/alsi-k32-supplement-files.tar.gz) 包含五对原始 IN/OUT/XML 和提取脚本。在解压后的 `alsi-k32-supplement` 中运行：

```bash
python3 analyse_k32.py
```

该脚本核对输入与原始输出，并生成 [formation-k32.csv](/Atlas/examples/alsi-k32-supplement/formation-k32.csv) 供表格复核。32³ 的结果列于下表：

| 候选 | xSi | 32³ 形成能 / eV·atom⁻¹ | 高于下凸包 / meV·atom⁻¹ |
| --- | ---: | ---: | ---: |
| al-fcc | 0.00 | 0.000000000 | 0.000000 |
| al3si-l12 | 0.25 | 0.109054980 | 109.054980 |
| alsi-b2 | 0.50 | 0.266852871 | 266.852871 |
| alsi3-l12 | 0.75 | 0.366450970 | 366.450970 |
| si-diamond | 1.00 | 0.000000000 | 0.000000 |

32³ 的数据仍给出相同的有限集合顶点：fcc Al 与 diamond Si；三个中间候选继续高于端元连线。顶点相同说明这组候选的最低能量分解组合没有改变。形成能的网格变化另按所选的 1 meV/atom 比较线判断：Al₃Si 与 AlSi 的 24³→32³ 变化分别为 1.798223 与 1.090635 meV/atom，均超过该线。可用 [独立表格复核脚本](/Atlas/examples/thermo-postprocessing/formation-hull/review_alsi_thermo.py) 重建两组凸包，并查看 [逐候选 CSV](/Atlas/examples/thermo-postprocessing/formation-hull/review/alsi-thermo-review.csv) 与 [复核报告](/Atlas/examples/thermo-postprocessing/formation-hull/review/alsi-thermo-review.md)。

前面的 20³→24³ 对照和后续 24³→32³ 对照均已保留，优化与不同静态协议下的压力差也在形成能页中列出。图上的正值来自本次电子能量计算；其中没有声子零点能、振动熵或组态熵，不能把这条线当成某个实验温度下的相界。所有候选均受限于指定立方原型，原子力小也不等于声子稳定。

## 用脚本重算凸包距离

构造下凸包时，先在同一成分保留最低能量，再按成分顺序检查相邻线段斜率。候选的 above-hull 能量是它与所在边界线段的垂直高度差。下面沿用形成能页的表格复核器，同时检查原子数归一化、24³/32³ 的边界和网格差分量。

~~~text
编写 review_alsi_thermo.py，读取 formation-energy.csv、formation-k32.csv 和 comparison-k24-k32.csv。仅用 Python 标准库。分别取 k24/k32 协议的五个候选，核对原子数、成分和 Ry→eV/atom 归一化；同成分取最低能量，再按相邻斜率构造下凸包，用包住 xSi 的两个顶点线性插值，计算 above-hull 高度并与原表核对。24³ 与 32³ 不共享元素参考能。
校验重复候选、缺少端元、原始能量与形成能不符、CSV 中 eV/atom 和 meV/atom 的单位混用，以及 ΔEform=ΔEcandidate−ΔEreference 不闭合。任一不一致报告候选和字段并停止。用 --outdir review 输出 alsi-thermo-review.csv 和 alsi-thermo-review.md，保留 1 meV/atom 比较线；只讨论这五个候选，不生成新图。
~~~

完整源码如下，与上面的下载文件相同。将 `review_alsi_thermo.py` 与 `formation-energy.csv`、`formation-k32.csv`、`comparison-k24-k32.csv` 放在同一目录；三份 CSV 的下载链接和运行命令见源码后。

<details>
<summary>review_alsi_thermo.py 完整源码</summary>

```python
#!/usr/bin/env python3
"""Recompute Al-Si formation energies and finite binary hulls as tables."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

RY_TO_EV = 13.605693122994
EXPECTED = {"al-fcc", "al3si-l12", "alsi-b2", "alsi3-l12", "si-diamond"}
COMPOUNDS = ("al3si-l12", "alsi-b2", "alsi3-l12")


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path}: missing header")
        return reader.fieldnames, list(reader)


def unique_by_case(rows: list[dict[str, str]], protocol: str) -> dict[str, dict[str, str]]:
    selected = [row for row in rows if row.get("protocol") == protocol]
    out: dict[str, dict[str, str]] = {}
    for row in selected:
        case = row.get("case", "")
        if not case or case in out:
            raise ValueError(f"{protocol}: empty or duplicate case {case!r}")
        out[case] = row
    if set(out) != EXPECTED:
        raise ValueError(
            f"{protocol}: expected cases {sorted(EXPECTED)}, found {sorted(out)}"
        )
    return out


def validated_values(rows: dict[str, dict[str, str]], protocol: str) -> dict[str, tuple[float, float]]:
    values: dict[str, tuple[float, float]] = {}
    for case, row in rows.items():
        n_al = int(row["nAl"])
        n_si = int(row["nSi"])
        n_atoms = int(row["natoms"])
        if n_atoms <= 0 or n_al + n_si != n_atoms:
            raise ValueError(f"{protocol}/{case}: nAl+nSi does not equal natoms")
        x = float(row["xSi"])
        expected_x = n_si / n_atoms
        if not math.isclose(x, expected_x, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"{protocol}/{case}: xSi disagrees with stoichiometry")
        total = float(row["total_energy_Ry"])
        reference = float(row["reference_energy_Ry"])
        computed = (total - reference) * RY_TO_EV / n_atoms
        stored = float(row["formation_eV_atom"])
        if not math.isfinite(computed) or not math.isclose(computed, stored, rel_tol=0, abs_tol=1e-9):
            raise ValueError(f"{protocol}/{case}: formation_eV_atom disagrees with raw energies")
        values[case] = (x, computed)
    return values


def lower_hull(values: dict[str, tuple[float, float]]) -> list[tuple[str, float, float]]:
    lowest: dict[float, tuple[str, float]] = {}
    for case, (x, energy) in values.items():
        if x not in lowest or energy < lowest[x][1]:
            lowest[x] = (case, energy)
    points = [(case, x, energy) for x, (case, energy) in sorted(lowest.items())]
    hull: list[tuple[str, float, float]] = []
    for point in points:
        while len(hull) >= 2:
            _, x0, e0 = hull[-2]
            _, x1, e1 = hull[-1]
            _, x2, e2 = point
            if (e1 - e0) / (x1 - x0) >= (e2 - e1) / (x2 - x1) - 1e-12:
                hull.pop()
            else:
                break
        hull.append(point)
    if len(hull) < 2 or not math.isclose(hull[0][1], 0, abs_tol=1e-12) or not math.isclose(hull[-1][1], 1, abs_tol=1e-12):
        raise ValueError("binary lower hull does not include xSi=0 and xSi=1")
    return hull


def hull_energy(x: float, hull: list[tuple[str, float, float]]) -> float:
    for _, xv, energy in hull:
        if math.isclose(x, xv, abs_tol=1e-12):
            return energy
    for left, right in zip(hull, hull[1:]):
        _, x0, e0 = left
        _, x1, e1 = right
        if x0 < x < x1:
            weight = (x - x0) / (x1 - x0)
            return e0 + weight * (e1 - e0)
    raise ValueError(f"xSi={x:g} is outside hull range")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k24", type=Path, default=Path("formation-energy.csv"))
    parser.add_argument("--k32", type=Path, default=Path("formation-k32.csv"))
    parser.add_argument("--comparison", type=Path, default=Path("comparison-k24-k32.csv"))
    parser.add_argument("--outdir", type=Path, default=Path("review"))
    args = parser.parse_args()

    _, raw24 = read_rows(args.k24)
    _, raw32 = read_rows(args.k32)
    _, raw_comparison = read_rows(args.comparison)
    rows24 = unique_by_case(raw24, "k24")
    rows32 = unique_by_case(raw32, "k32")
    comparison: dict[str, dict[str, str]] = {}
    for row in raw_comparison:
        case = row["case"]
        if case in comparison:
            raise ValueError(f"comparison table: duplicate case {case}")
        comparison[case] = row
    if set(comparison) != EXPECTED:
        raise ValueError("comparison table must contain exactly the five reviewed cases")

    values24 = validated_values(rows24, "k24")
    values32 = validated_values(rows32, "k32")
    hull24 = lower_hull(values24)
    hull32 = lower_hull(values32)

    results: list[dict[str, str]] = []
    max_change = 0.0
    max_case = ""
    for case in sorted(EXPECTED, key=lambda item: values24[item][0]):
        x24, e24 = values24[case]
        x32, e32 = values32[case]
        if not math.isclose(x24, x32, rel_tol=0, abs_tol=1e-12):
            raise ValueError(f"{case}: composition changed between meshes")
        above24 = e24 - hull_energy(x24, hull24)
        above32 = e32 - hull_energy(x32, hull32)
        if not math.isclose(above24, float(rows24[case]["above_hull_eV_atom"]), rel_tol=0, abs_tol=2e-8):
            raise ValueError(f"k24/{case}: reconstructed hull distance disagrees")
        if not math.isclose(above32 * 1000.0, float(rows32[case]["above_hull_meV_atom"]), rel_tol=0, abs_tol=2e-5):
            raise ValueError(f"k32/{case}: reconstructed hull distance disagrees")
        delta = (e32 - e24) * 1000.0
        row = comparison[case]
        candidate = float(row["candidate_energy_change_meV_atom"])
        reference = float(row["reference_energy_change_meV_atom"])
        stored_delta = float(row["formation_change_meV_atom"])
        if not math.isclose(delta, stored_delta, rel_tol=0, abs_tol=2e-5):
            raise ValueError(f"{case}: stored mesh change disagrees with recomputed energies")
        if not math.isclose(candidate - reference, delta, rel_tol=0, abs_tol=2e-5):
            raise ValueError(f"{case}: candidate/reference decomposition does not close")
        results.append({
            "case": case,
            "xSi": f"{x24:.8f}",
            "formation_k24_eV_atom": f"{e24:.9f}",
            "above_hull_k24_eV_atom": f"{above24:.9f}",
            "formation_k32_eV_atom": f"{e32:.9f}",
            "above_hull_k32_meV_atom": f"{above32*1000:.6f}",
            "formation_change_meV_atom": f"{delta:.6f}",
            "candidate_energy_change_meV_atom": f"{candidate:.6f}",
            "reference_energy_change_meV_atom": f"{reference:.6f}",
        })
        if case in COMPOUNDS and abs(delta) > max_change:
            max_change, max_case = abs(delta), case

    if max_case != "al3si-l12" or not math.isclose(max_change, 1.79822269267, rel_tol=0, abs_tol=2e-6):
        raise ValueError(f"unexpected maximum intermediate formation-energy change: {max_case} {max_change}")
    if {item[0] for item in hull24} != {"al-fcc", "si-diamond"}:
        raise ValueError("k24 finite hull vertices changed from the reviewed endpoints")
    if {item[0] for item in hull32} != {"al-fcc", "si-diamond"}:
        raise ValueError("k32 finite hull vertices changed from the reviewed endpoints")

    args.outdir.mkdir(parents=True, exist_ok=True)
    csv_path = args.outdir / "alsi-thermo-review.csv"
    md_path = args.outdir / "alsi-thermo-review.md"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    md_lines = [
        "# Al-Si formation-energy and finite-hull review",
        "",
        "- Scope: the five supplied cubic prototypes only; no omitted compositions are inferred.",
        "- Both k24 and k32 finite hulls contain only fcc Al and diamond Si endpoints.",
        "- At 32³, Al3Si L12, B2 AlSi, and AlSi3 L12 remain above the endpoint tie-line.",
        f"- Largest intermediate 24³-to-32³ formation-energy change: {max_change:.6f} meV/atom ({max_case}).",
        "- The 1 meV/atom line is a selected numerical comparison, not a universal criterion.",
        "- Component relation: formation-energy change = candidate energy change − reference energy change.",
        "",
        "| case | xSi | ΔEform k24 (eV/atom) | above hull k24 (eV/atom) | ΔEform k32 (eV/atom) | above hull k32 (meV/atom) | Δ mesh (meV/atom) | candidate Δ (meV/atom) | reference Δ (meV/atom) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in results:
        md_lines.append(
            f"| {row['case']} | {row['xSi']} | {row['formation_k24_eV_atom']} | "
            f"{row['above_hull_k24_eV_atom']} | {row['formation_k32_eV_atom']} | "
            f"{row['above_hull_k32_meV_atom']} | {row['formation_change_meV_atom']} | "
            f"{row['candidate_energy_change_meV_atom']} | {row['reference_energy_change_meV_atom']} |"
        )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"rows={len(results)} k24_hull=Al-fcc,Si-diamond k32_hull=Al-fcc,Si-diamond")
    print(f"max_intermediate_change={max_change:.6f} meV/atom case={max_case}")
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
```

</details>

下载 [24³ 形成能表](/Atlas/examples/thermo-postprocessing/formation-hull/formation-energy.csv)、[32³ 形成能表](/Atlas/examples/thermo-postprocessing/formation-hull/formation-k32.csv) 和 [网格差分量表](/Atlas/examples/thermo-postprocessing/formation-hull/comparison-k24-k32.csv)，与脚本放在同一目录：

```bash
python3 review_alsi_thermo.py --outdir review
```

结果中的两组顶点均为 `Al-fcc,Si-diamond`，最大中间候选形成能变化为 `1.798223 meV/atom`。这说明现有集合的分解组合没有改变；形成能的网格变化仍需按原定比较线判断。生成的逐候选表同时给出两个网格下的 above-hull 距离。

## 文献方法与相图基准

He 等人在 300 GPa 下并列比较 La–Sc–H 体系未计入与计入谐振零点能的凸包结果，说明统一的能量修正会改变相之间的分解关系。本页采用五个 Al–Si 立方原型的静态电子能；加入零点能或温度项时，对全部候选与元素参照采用匹配的处理。[He 等，PNAS 121, e2401840121 (2024)](https://doi.org/10.1073/pnas.2401840121)。

如果后续发现一个新的同成分结构，先按匹配协议计算它的能量，再把对应的真实记录加入候选集合并重建下凸包。要检查现有候选是否存在畸变方向，可接到 [DFPT 声子](/Atlas/m/phonon-dfpt/qe/)；看到负频后，沿 [虚频排查](/Atlas/m/imaginary-phonon/qe/) 核对结构、原始频率和数值设置。

```text
同协议元素与候选总能 → 每原子形成能
                            ↓
                    成分—能量有限候选集
                            ↓
                       构造下凸包
                            ↓
                 相邻顶点组合与 energy above hull
                            ↓
                  新候选 / 声子 / 有限温度项
```
