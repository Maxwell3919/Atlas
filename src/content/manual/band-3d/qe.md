一条高对称路径只是在倒空间里走过几条线。要看 Si 导带谷为什么在不同方向有不同曲率，需要离开那条线。这次在 Γ–X 导带谷附近真正计算一个三维 k 点立方网格，再从中画两张能量曲面。两张图显示的是局部 Γ–X 谷的纵向与横向切面。

前面的[带隙](/Atlas/m/band-gap/qe/)和[有效质量](/Atlas/m/effective-mass/qe/)已经把这个谷定位在 `kx≈0.8443×2π/a`。这里仍使用同一固定 Si 晶胞、同一 `60/640 Ry` 设置和 `12³` 父 SCF 密度，接续方式见 [SCF](/Atlas/m/scf/qe/)。

[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/)

[下载 Si 算例](/Atlas/examples/si-pbe-electronic-files.tar.gz)后保留目录结构，在 `si-pbe` 中运行绘图脚本。本页图直接读取 `band3d/cube.csv`，对应输入、输出和 XML 也在该子目录。包中不含可接续计算的 `tmp/si.save`；重新计算这批 k 点时，需要下文使用的同一份父 SCF 密度。

## 在导带谷周围列出三维点阵

```text
[preston@preston-System-Product-Name si-pbe]$ cp -a k12/tmp band3d/
[preston@preston-System-Product-Name si-pbe]$ cp scf/scf.in band3d/grid.in
[preston@preston-System-Product-Name si-pbe]$ vi band3d/grid.in
```

输入开头和最前几个 k 点如下。与普通路径不同，这里写的是 `K_POINTS tpiba` 的完整点表，数量为 **891**。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 38 band3d/grid.in
&CONTROL
  calculation = 'bands'
  verbosity = 'high'
  prefix = 'si'
  outdir = './tmp'
  pseudo_dir = '../pseudo'
  tprnfor = .true.
  tstress = .true.
/
&SYSTEM
  ibrav = 2
  A = 5.397607551
  nbnd = 8
  nat = 2
  ntyp = 1
  ecutwfc = 60
  ecutrho = 640
  occupations = 'fixed'
/
&ELECTRONS
  conv_thr = 1.0d-12
/
ATOMIC_SPECIES
Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS alat
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25
K_POINTS tpiba
891
0.75000000 -0.08000000 -0.08000000 1.0
0.75000000 -0.08000000 -0.06000000 1.0
0.75000000 -0.08000000 -0.04000000 1.0
0.75000000 -0.08000000 -0.02000000 1.0
0.75000000 -0.08000000 0.00000000 1.0
0.75000000 -0.08000000 0.02000000 1.0
0.75000000 -0.08000000 0.04000000 1.0
0.75000000 -0.08000000 0.06000000 1.0
0.75000000 -0.08000000 0.08000000 1.0
[preston@preston-System-Product-Name si-pbe]$
```

三个方向分别为：x 从 0.75 到 0.95，共 11 点；y、z 从 −0.08 到 0.08，各 9 点，间隔均为 0.02，单位都是 `2π/a`。`11×9×9=891`，所以这里有真实的离面采样，并非把一条曲线绕轴旋转出来。

取值范围决定这张局部图覆盖多大的谷区，点距决定能看清多细的起伏。扩大范围仍可能错过很窄的极值；缩小点距也不会把局部网格变成全布里渊区采样。这两种修改都只是在既有父密度上增加本征值采样。

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 5 band3d/grid.in
0.95000000 0.08000000 0.00000000 1.0
0.95000000 0.08000000 0.02000000 1.0
0.95000000 0.08000000 0.04000000 1.0
0.95000000 0.08000000 0.06000000 1.0
0.95000000 0.08000000 0.08000000 1.0
[preston@preston-System-Product-Name si-pbe]$
```

[完整 grid.in](/Atlas/examples/si-pbe-electronic/band3d/grid.in)包含所有坐标。点表的排列是 x 最慢、z 最快；绘图脚本仍按坐标筛选和重排，不假设屏幕上第几行恰好对应哪一个网格位置。`nbnd=8` 保留本例的四条价带和四条导带，后面只取第 5 条画最低导带。

```text
[preston@preston-System-Product-Name si-pbe]$ cat band3d/run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-3d
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
unset DISPLAY XAUTHORITY
ulimit -s unlimited
ulimit -c 0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in grid.in > grid.out 2> grid.err
[preston@preston-System-Product-Name si-pbe]$
```

```text
[preston@preston-System-Product-Name si-pbe]$ cd band3d
[preston@preston-System-Product-Name band3d]$ sbatch run.sh
Submitted batch job 786
[preston@preston-System-Product-Name band3d]$ cd ..
```

这个计算没有离子优化步骤，时间主要花在给定密度下的 891 组本征态上。输出中应核对实际 k 点数和能带数，而不是只相信输入点表。

```text
[preston@preston-System-Product-Name si-pbe]$ grep -E 'number of k points|number of Kohn-Sham states|JOB DONE' band3d/grid.out
     number of Kohn-Sham states=            8
     number of k points=   891
   JOB DONE.
[preston@preston-System-Product-Name si-pbe]$
```

这次输出确实读入了 891 个 k 点和 8 条 Kohn–Sham 能带，结束前没有本征值未收敛提示。原生 WALL 时间约 2 分 46 秒，完整输出为[grid.out](/Atlas/examples/si-pbe-electronic/band3d/grid.out)。

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 12 band3d/grid.out
     davcio       :      0.05s CPU      0.06s WALL (    1782 calls)

     Parallel routines

     PWSCF        :   2m38.43s CPU   2m45.66s WALL


   This run was terminated on:  21:44:35  22Sep2026

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name si-pbe]$
```

能量从[同一次计算的 XML](/Atlas/examples/si-pbe-electronic/band3d/data-file-schema.xml)提取。XML 本征值的 Hartree 单位转成 eV，k 的 `tpiba` 坐标转成 Å⁻¹；两套 k 坐标一并放进 `cube.csv`，以后换坐标或做拟合时能追得回去。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 7 band3d/cube.csv
kx_tpiba,ky_tpiba,kz_tpiba,kx_inv_A,ky_inv_A,kz_inv_A,band5_eV
0.75,-0.08,-0.08,0.8730514280371566,-0.09312548565729671,-0.09312548565729671,7.244655010325953
0.75,-0.08,-0.06,0.8730514280371566,-0.09312548565729671,-0.06984411424297253,7.20368463842487
0.75,-0.08,-0.04,0.8730514280371566,-0.09312548565729671,-0.046562742828648356,7.175249538627218
0.75,-0.08,-0.02,0.8730514280371566,-0.09312548565729671,-0.023281371414324178,7.158593176093672
0.75,-0.08,0.0,0.8730514280371566,-0.09312548565729671,0.0,7.153117253788684
0.75,-0.08,0.02,0.8730514280371566,-0.09312548565729671,0.023281371414324178,7.158593176093675
[preston@preston-System-Product-Name si-pbe]$
```

其中 `band5_eV` 是每个点的第 5 条能带。图中的零点采用这个立方网格内采样到的最小值，并不宣称它就是连续函数的精确谷底。x 的间隔只有 0.02，采样最低点落在 0.85 附近；[有效质量](/Atlas/m/effective-mass/qe/)中更细的线采样把谷底进一步定位到约 0.8443。

## 把后处理要求写成提示词

上面的单位、点序和能量参考可以整理成下面的编码要求，与示例文件一起交给代码助手：

```text
编写 Si 导带谷局部网格后处理程序，使用 Python 3、NumPy 和 Matplotlib。
输入：band3d/cube.csv，含 kx/ky/kz_tpiba（2π/a）、kx/ky/kz_inv_A（Å⁻¹）、band5_eV。
方法：按坐标恢复 11×9×9 网格，取 kz=0 的 E(kx,ky) 和 kx=0.85×2π/a 的 E(ky,kz)，两图能量均减整个立方网格内采样到的 band 5 最低值。
检查：891 个唯一点、轴取值、坐标换算和切面矩阵顺序，保留全部采样。
输出：源码、依赖、命令、摘要和 PNG/SVG/PDF；竖轴标 E−sampled minimum (meV)，注明局部 Γ–X 谷范围。
```

## 后处理源码与运行

完整源码：[analyse_electronic.py](/Atlas/examples/si-pbe-electronic/analyse_electronic.py) · [plot_si.py](/Atlas/examples/si-pbe-electronic/plot_si.py) · [atlas_plot_style.py](/Atlas/examples/si-pbe-electronic/atlas_plot_style.py)。Python 3 依赖：NumPy、Matplotlib。

<details>
<summary>analyse_electronic.py 的完整源码</summary>

```python
from pathlib import Path
import csv, json, re, hashlib, xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(__file__).resolve().parent
RY_EV=13.605693122994
HA_EV=2*RY_EV
BOHR_ANG=0.529177210903
HBAR2_OVER_2ME=3.80998211615486 # eV Angstrom^2

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def table(path,header,rows):
    with path.open('w') as f:
        w=csv.writer(f);w.writerow(header);w.writerows(rows)
def read_xml(directory):
    x=ET.parse(ROOT/directory/'data-file-schema.xml').getroot()
    output=x.find('output')
    states=output.find('band_structure').findall('ks_energies')
    k=np.array([[float(v) for v in s.find('k_point').text.split()] for s in states])
    e=np.array([[float(v)*HA_EV for v in s.find('eigenvalues').text.split()] for s in states])
    alat=float(output.find('atomic_structure').attrib['alat'])*BOHR_ANG
    return k,e,alat

# Gap on uniform meshes; a local line refinement is a separate piece of evidence.
gaps=[]
for name in ['gap12','gap18-cg','gap24-cg','gap24-k12-cg']:
    if not (ROOT/name/'data-file-schema.xml').exists():continue
    k,e,a=read_xml(name)
    v=e[:,3]; c=e[:,4];iv=int(v.argmax());ic=int(c.argmin())
    row={'directory':name,'nks':len(k),'vbm_eV':float(v[iv]),'cbm_eV':float(c[ic]),'gap_eV':float(c[ic]-v[iv]),'minimum_direct_gap_eV':float((c-v).min()),'vbm_k_tpiba':k[iv].tolist(),'cbm_k_tpiba':k[ic].tolist()}
    gaps.append(row)
    table(ROOT/name/'edges.csv',['kx_tpiba','ky_tpiba','kz_tpiba','vbm_band4_eV','cbm_band5_eV'],np.c_[k,v,c])
(ROOT/'gap-results.json').write_text(json.dumps(gaps,indent=2)+'\n')

# Fits use physical k in inverse Angstrom, not a path-point index.
k,e,a=read_xml('mass'); kcart=k*2*np.pi/a
imin=int(e[:,4].argmin());center=kcart[imin,0]
fits=[]
for window in [.010,.020,.030]:
    take=np.abs(kcart[:,0]-center)<=window+1e-12
    coeff=np.polyfit(kcart[take,0]-center,e[take,4],2)
    fit=np.polyval(coeff,kcart[take,0]-center)
    x0=center-coeff[1]/(2*coeff[0]);e0=coeff[2]-coeff[1]**2/(4*coeff[0])
    fits.append({'half_window_inv_A':window,'npoints':int(take.sum()),'quadratic_A_eVA2':float(coeff[0]),'minimum_k_inv_A':float(x0),'minimum_k_tpiba':float(x0*a/(2*np.pi)),'minimum_energy_eV':float(e0),'mass_over_me':float(HBAR2_OVER_2ME/coeff[0]),'rms_residual_meV':float(np.sqrt(np.mean((fit-e[take,4])**2))*1000)})
(ROOT/'mass/mass-fits.json').write_text(json.dumps(fits,indent=2)+'\n')
table(ROOT/'mass/longitudinal.csv',['kx_tpiba','kx_inv_A','band5_eV'],np.c_[k[:,0],kcart[:,0],e[:,4]])

# Actual 3D local cube: retain every point, not only a plotted 2D slice.
if (ROOT/'band3d/data-file-schema.xml').exists():
    k,e,a=read_xml('band3d')
    assert len(k)==891
    table(ROOT/'band3d/cube.csv',['kx_tpiba','ky_tpiba','kz_tpiba','kx_inv_A','ky_inv_A','kz_inv_A','band5_eV'],np.c_[k,k*2*np.pi/a,e[:,4]])

# Fatband weights are squared complex projection amplitudes. Take energies
# from PW QEXSD (Hartree); the independent atomic_proj E values use Ry.
k,e,a=read_xml('bands-cg')
pr=ET.parse(ROOT/'bands-cg/atomic_proj.xml').getroot().find('EIGENSTATES')
projs=pr.findall('PROJS'); pk=pr.findall('K-POINT');pe=pr.findall('E')
assert len(projs)==len(k)
rows=[];distance=np.r_[0,np.cumsum(np.linalg.norm(np.diff(k,axis=0),axis=1))]
for ik,proj in enumerate(projs):
    kp=np.array([float(v) for v in pk[ik].text.split()])
    ep=np.array([float(v)*RY_EV for v in pe[ik].text.split()])
    assert np.max(np.abs(kp-k[ik]))<1e-9 and np.max(np.abs(ep-e[ik]))<1e-6
    weights=[]
    for orbital in proj.findall('ATOMIC_WFC'):
        z=np.array([float(v) for v in orbital.text.split()]).reshape(-1,2)
        weights.append((z*z).sum(axis=1))
    weights=np.array(weights)
    assert weights.shape==(8,8)
    for ib in range(8):
        sw=weights[[0,4],ib].sum();pw=weights[[1,2,3,5,6,7],ib].sum()
        rows.append([ik+1,ib+1,distance[ik],*k[ik],e[ik,ib],sw,pw,sw+pw])
table(ROOT/'bands-cg/fatband.csv',['ik','iband','path_distance_tpiba','kx_tpiba','ky_tpiba','kz_tpiba','energy_eV','Si_s_weight','Si_p_weight','projection_norm'],rows)

print('gaps:',len(gaps),'fits:',len(fits),'fatband rows:',len(rows))
```

</details>

<details>
<summary>plot_si.py 的完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import argparse,csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'plots';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':130,'savefig.dpi':300,'axes.titleweight':'bold'})
BLUE='#0072b2';ORANGE='#e69f00';GRAY='#667080'

def read(name):return np.genfromtxt(ROOT/name,delimiter=',',names=True,encoding='utf-8')
def save(fig,name):
    fig.savefig(OUT/(name+'.png'),bbox_inches='tight');fig.savefig(OUT/(name+'.svg'),bbox_inches='tight');plt.close(fig);print(OUT/(name+'.png'))
def clean(ax):ax.grid(alpha=.18);ax.set_axisbelow(True)
def convergence():
    rows=list(csv.DictReader((ROOT/'convergence.csv').open()))
    fig,axes=plt.subplots(1,3,figsize=(12,3.6),layout='constrained')
    for ax,param,label in zip(axes,['ecutwfc','ecutrho','kmesh'],['Wavefunction cutoff (Ry)','Charge-density cutoff (Ry)','Uniform mesh n × n × n']):
        r=[x for x in rows if x['parameter']==param];x=[float(v['setting']) for v in r];y=[float(v['delta_meV_per_atom_vs_last']) for v in r]
        ax.plot(x,y,'o-',color=BLUE);ax.set_xlabel(label);ax.set_ylabel('ΔE vs last point (meV/atom)');clean(ax)
        if param=='kmesh':ax.set_yscale('symlog',linthresh=.1);ax.axhline(1,color=ORANGE,ls='--',label='Example comparison: 1 meV/atom');ax.legend(fontsize=8)
        ax.set_title({'ecutwfc':'Fixed 640 Ry, 8³ mesh','ecutrho':'Fixed 60 Ry, 8³ mesh','kmesh':'Fixed 60 / 640 Ry'}[param],fontsize=11)
    save(fig,'convergence')
def relax():
    r=read('relax/relaxation.csv')
    fig,axes=plt.subplots(1,2,figsize=(9.6,3.6),layout='constrained')
    e_diff = (r['energy_Ry'] - r['energy_Ry'][-1]) * 13605.693122994
    axes[0].plot(r['scf_cycle'], e_diff, 'o-', color=BLUE, lw=1.5, ms=5, zorder=3)
    axes[0].fill_between(r['scf_cycle'], 0, e_diff, color=BLUE, alpha=0.12, zorder=1)
    axes[0].set_ylabel('Energy above final geometry (meV/cell)')
    axes[0].set_title('Si: Monotonic Energy Descent', fontweight='bold', fontsize=10.5)
    for cycle, de in zip(r['scf_cycle'][:-1], e_diff[:-1]):
        axes[0].annotate(f"{de:.1f} meV", xy=(cycle, de), xytext=(0, 6),
                         textcoords='offset points', ha='center', fontsize=7.5, color=BLUE)
    axes[0].annotate("Final E₀ = -22.838592 Ry", xy=(r['scf_cycle'][-1], 0), xytext=(-55, 18),
                     textcoords='offset points', fontsize=7.5, color='#162232',
                     arrowprops=dict(arrowstyle='->', color='#718096', lw=0.6))
    
    # Total force plot with log-scale threshold lines
    f_vals = np.array(r['total_force_Ry_per_Bohr'])
    # For display of the 0.0 final step, set a small visual floor for the arrow
    f_disp = np.maximum(f_vals, 1e-5)
    axes[1].plot(r['scf_cycle'][:-1], f_vals[:-1], 's-', color=ORANGE, lw=1.5, ms=5, label='Total Force', zorder=3)
    axes[1].plot([r['scf_cycle'][-2], r['scf_cycle'][-1]], [f_vals[-2], f_disp[-1]], 's--', color=ORANGE, lw=1.0, zorder=2)
    axes[1].scatter([r['scf_cycle'][-1]], [f_disp[-1]], marker='o', facecolors='white', edgecolors=ORANGE, s=40, zorder=4)
    axes[1].axhline(1e-3, color='#c0392b', ls='--', lw=0.9, label=r'QE Default $10^{-3}$ Ry/Bohr', zorder=1)
    axes[1].axhline(1e-4, color='#27ae60', ls=':', lw=0.9, label=r'Stringent $10^{-4}$ Ry/Bohr', zorder=1)
    axes[1].set_yscale('log')
    axes[1].set_ylim(5e-6, 1.2e-1)
    axes[1].set_ylabel('Total Force (Ry/Bohr, log scale)')
    axes[1].set_title('Si: BFGS Force Convergence', fontweight='bold', fontsize=10.5)
    axes[1].annotate('Printed as 0.000000\n(Force strictly zero by symmetry)',
                     xy=(r['scf_cycle'][-1], f_disp[-1]), xytext=(-120, 28),
                     textcoords='offset points', fontsize=7.5, color='#8c3b00',
                     arrowprops=dict(arrowstyle='->', color=ORANGE, lw=0.7))
    axes[1].legend(frameon=True, facecolor='#f8fafc', edgecolor='#e2e8f0', fontsize=7.5, loc='upper right')
    
    for label, ax in zip('ab', axes):
        ax.set_xlabel('BFGS Step / SCF Cycle')
        ax.set_xticks(r['scf_cycle'])
        clean(ax)
        ax.text(-0.14, 1.05, label, transform=ax.transAxes, fontweight='bold', fontsize=10)
    save(fig, 'relax')

def gap():
    r=json.loads((ROOT/'gap-results.json').read_text());base=[x for x in r if x['directory'] in ['gap12','gap18-cg','gap24-cg']]
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),layout='constrained')
    axes[0].plot([12,18,24],[x['gap_eV'] for x in base],'o-',color=BLUE);axes[0].set_xticks([12,18,24]);axes[0].set_xlabel('Uniform NSCF mesh n × n × n');axes[0].set_ylabel('Sampled indirect gap (eV)');axes[0].set_title('The sampled minimum need not vary monotonically',fontsize=10)
    for n,x in zip([12,18,24],base):axes[0].annotate(f"{max(x['cbm_k_tpiba']):.4f} × 2π/a",(n,x['gap_eV']),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
    m=read('mass/longitudinal.csv');fit=json.loads((ROOT/'mass/mass-fits.json').read_text())[1]
    dense=next(x for x in r if x['directory']=='gap24-k12-cg');axes[1].plot(m['kx_tpiba'],m['band5_eV']-dense['vbm_eV'],color=BLUE)
    axes[1].scatter([fit['minimum_k_tpiba']],[fit['minimum_energy_eV']-dense['vbm_eV']],color=ORANGE,zorder=4)
    axes[0].margins(y=.20)
    axes[1].set_xlabel('kx (2π/a), ky = kz = 0');axes[1].set_ylabel('Conduction energy − VBM (eV)');axes[1].set_title('Local Γ–X valley refinement; 12³ parent density',fontsize=10)
    for ax in axes:clean(ax)
    save(fig,'band-gap')
def mass():
    r=read('mass/longitudinal.csv');fits=json.loads((ROOT/'mass/mass-fits.json').read_text());fit=fits[1]
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),layout='constrained')
    dk=r['kx_inv_A']-fit['minimum_k_inv_A'];take=np.abs(dk)<.04
    axes[0].scatter(dk[take],(r['band5_eV'][take]-fit['minimum_energy_eV'])*1000,s=24,color=BLUE,label='Actual QE eigenvalues')
    q=np.linspace(-.035,.035,101);axes[0].plot(q,fit['quadratic_A_eVA2']*q*q*1000,color=ORANGE,label='Quadratic fit, ±0.02 Å⁻¹')
    axes[0].set_xlabel('kx − valley minimum (Å⁻¹)');axes[0].set_ylabel('Energy above minimum (meV)');axes[0].legend(fontsize=8)
    axes[1].plot([f['half_window_inv_A'] for f in fits],[f['mass_over_me'] for f in fits],'o-',color=BLUE)
    axes[1].set_xlabel('Fit half-window (Å⁻¹)');axes[1].set_ylabel('Longitudinal electron mass / me');axes[1].set_xticks([.01,.02,.03]);axes[1].ticklabel_format(useOffset=False,axis='y')
    for ax in axes:clean(ax)
    save(fig,'effective-mass')
def band3d():
    r=read('band3d/cube.csv');emin=r['band5_eV'].min();fig=plt.figure(figsize=(11,4.4),layout='constrained')
    for i,(key,value,xkey,ykey,title) in enumerate([('kz_tpiba',0.,'kx_tpiba','ky_tpiba','kz = 0 plane'),('kx_tpiba',.85,'ky_tpiba','kz_tpiba','kx = 0.85 × 2π/a plane')]):
        d=r[np.isclose(r[key],value)];xs=np.unique(d[xkey]);ys=np.unique(d[ykey]);X,Y=np.meshgrid(xs,ys,indexing='ij');Z=np.empty_like(X)
        for u,x in enumerate(xs):
            for v,y in enumerate(ys):Z[u,v]=(d['band5_eV'][np.isclose(d[xkey],x)&np.isclose(d[ykey],y)][0]-emin)*1000
        ax=fig.add_subplot(1,2,i+1,projection='3d');ax.plot_surface(X,Y,Z,cmap='viridis',linewidth=.2,edgecolor=(0,0,0,.15),antialiased=True)
        ax.set_xlabel(xkey.replace('_tpiba','')+' (2π/a)');ax.set_ylabel(ykey.replace('_tpiba','')+' (2π/a)');ax.set_zlabel('');ax.text2D(0.02, 0.91, 'E − sampled minimum (meV)', transform=ax.transAxes, fontsize=9);ax.set_title(title);ax.view_init(elev=25,azim=-125);ax.xaxis.set_major_locator(plt.MaxNLocator(4));ax.yaxis.set_major_locator(plt.MaxNLocator(4));ax.zaxis.set_major_locator(plt.MaxNLocator(4))
    fig.suptitle('Two cuts through an actual 11 × 9 × 9 local k-point cube',fontsize=12)
    save(fig,'band-3d')
def population():
    r=read('population-cg/lowdin.csv');fig,ax=plt.subplots(figsize=(6,4),layout='constrained');x=np.arange(len(r))
    ax.bar(x,r['s_electrons'],color=BLUE,label='s');ax.bar(x,r['p_electrons'],bottom=r['s_electrons'],color=ORANGE,label='p')
    for i,q in enumerate(r['total_electrons']):ax.text(i,q+.03,f'{q:.4f}',ha='center')
    ax.axhline(4,color=GRAY,ls='--',lw=1,label='4 valence electrons / Si');ax.set_xticks(x,['Si 1','Si 2']);ax.set_ylabel('Projected electrons');ax.set_ylim(0,4.5);ax.legend(ncol=3,fontsize=9,loc='lower center',bbox_to_anchor=(.5,1.));ax.set_title('Equivalent atoms; spilling = 0.0092',pad=38);save(fig,'population-analysis')
def fatband():
    r=read('bands-cg/fatband.csv');vbm=r['energy_eV'][r['iband']==4].max();fig,axes=plt.subplots(1,2,figsize=(12,4.6),sharey=True,layout='constrained')
    idx=[1,25,37,49,73,97,121];ticks=[r['path_distance_tpiba'][r['ik']==i][0] for i in idx];labels=['Γ','X','W','K','Γ','L','X']
    for ax,weight,color,title in zip(axes,['Si_s_weight','Si_p_weight'],[BLUE,ORANGE],['Si s projection','Si p projection']):
        for ib in range(1,9):
            q=r[r['iband']==ib];ax.plot(q['path_distance_tpiba'],q['energy_eV']-vbm,color='#b6bdc7',lw=.65,zorder=1);ax.scatter(q['path_distance_tpiba'],q['energy_eV']-vbm,s=34*q[weight],color=color,alpha=.75,edgecolors='none',zorder=2)
        for tick in ticks:ax.axvline(tick,color='#e0e3e8',lw=.65,zorder=0)
        ax.axhline(0,color=GRAY,ls='--',lw=.7);ax.set_xticks(ticks,labels);ax.set_xlim(ticks[0],ticks[-1]);ax.set_ylim(-13,7);ax.set_title(title);ax.set_ylabel('Energy − VBM (eV)')
        handles=[ax.scatter([],[],s=34*w,color='#555555',edgecolors='none',label=f'{w:g}') for w in (.25,.5,1.)]
        ax.legend(handles=handles,title='Projection weight (point area)',ncol=3,
                  loc='lower left',bbox_to_anchor=(0,1.015),frameon=False,fontsize=8)
        ax.set_title('',loc='center')
        ax.set_title(title,loc='left',pad=55)
    save(fig,'fatband')
def bands():
    r=read('bands-cg/fatband.csv');vbm=r['energy_eV'][r['iband']==4].max();fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained');idx=[1,25,37,49,73,97,121];ticks=[r['path_distance_tpiba'][r['ik']==i][0] for i in idx]
    for ib in range(1,9):
        q=r[r['iband']==ib];ax.plot(q['path_distance_tpiba'],q['energy_eV']-vbm,color=BLUE,lw=1)
    for tick in ticks:ax.axvline(tick,color='#dce1e8',lw=.7)
    ax.axhline(0,color=GRAY,ls='--',lw=.7);ax.set_xticks(ticks,['Γ','X','W','K','Γ','L','X']);ax.set_xlim(ticks[0],ticks[-1]);ax.set_ylim(-13,7);ax.set_ylabel('Energy − VBM (eV)');ax.set_title('Si, PBE, fixed example cell; no SOC');save(fig,'bands')
def dos():
    r=np.loadtxt(ROOT/'dos-cg/si.dos.dat');g=json.loads((ROOT/'gap-results.json').read_text());vbm=next(x['vbm_eV'] for x in g if x['directory']=='gap24-cg')
    fig,ax=plt.subplots(figsize=(7.5,3.7),layout='constrained');ax.plot(r[:,0]-vbm,r[:,1],color=BLUE);ax.fill_between(r[:,0]-vbm,r[:,1],alpha=.15,color=BLUE);ax.axvline(0,color=GRAY,ls='--');ax.set_xlim(-13,8);ax.set_xlabel('Energy − VBM (eV)');ax.set_ylabel('DOS (states/eV/cell)');ax.set_title('24³ NSCF mesh; Gaussian broadening 0.01 Ry');clean(ax);save(fig,'dos')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('figure',choices=['convergence','relax','gap','mass','band3d','population','fatband','bands','dos','all']);args=parser.parse_args()
    funcs={'convergence':convergence,'relax':relax,'gap':gap,'mass':mass,'band3d':band3d,'population':population,'fatband':fatband,'bands':bands,'dos':dos}
    for name,fun in funcs.items():
        if args.figure in [name,'all']:fun()
```

</details>

解压本页示例包后，在 `si-pbe` 根目录执行：

```bash
python3 -m pip install numpy matplotlib
python3 analyse_electronic.py
python3 plot_si.py band3d
```

本例保存的绘图运行输出如下：

```text
[preston@preston-System-Product-Name si-pbe]$ python3 plot_si.py band3d
<工作目录>/si-pbe/plots/band-3d.png
```

![Si 局部三维 k 网格中的两张导带能量切面](/Atlas/examples/si-pbe-electronic/plots/band-3d.png)

左图在 `kz=0` 平面上画 `E(kx,ky)`，沿谷的纵向 x 弯得较缓，沿横向 y 弯得较陡。右图固定 `kx=0.85×2π/a`，画 `E(ky,kz)`；两个横向相似。这与同一组模型下约 `0.956 mₑ` 的纵向质量、约 `0.192 mₑ` 的横向质量相互对应：更平的能带有更大的曲率质量。

两张图都是**实际三维点阵中的二维切面，竖轴表示能量**。`cube.csv` 保存整个局部网格。全区等能面需要覆盖完整采样区域，或采用经过直接能带核对的插值。

这组固定晶胞、PBE、无 SOC 的非磁性 Si 数据展示了 Γ–X 导带谷的纵横向曲率。

## 文献中的三维能量曲面与底座等能线投影

在研究二维表面态、鞍点（Van Hove 奇点）或谷电子学能带时，通常将局部二维动量网格上的能量曲面 E(k<sub>x</sub>, k<sub>y</sub>) 绘制为三维曲面，并在底部平面投影出等能轮廓线，再配合沿两个正交动量方向的切面色散与 ARPES 实验谱对照。

<figure class="research-figure"><img src="/Atlas/figures/literature/M7_SurfaceStates_3DVHS_ARPES_ZrAs2_Fig4.jpg" alt="ZrAs2 表面态在鞍点附近的三维能带色散曲面、底部等能线投影及正交方向切面与 ARPES 对比" loading="lazy"/><figcaption>ZrAs<sub>2</sub> 表面态在鞍点附近的三维能带曲面 <em>E</em>(<em>k</em><sub>x</sub>, <em>k</em><sub>y</sub>) 及其底部等能线投影（c），并给出沿正交方向具有相反曲率的电子型与空穴型色散切面及 ARPES 实验对比（d–e）。引自 <em>Nat. Commun.</em> <strong>16</strong>, 2831 (2025)，Fig. 4c–e，<a href="https://doi.org/10.1038/s41467-025-58024-w" target="_blank" rel="noopener noreferrer">DOI: 10.1038/s41467-025-58024-w</a>。</figcaption></figure>

对于具有自旋—轨道耦合劈裂的二维半导体谷区（如过渡金属硫族化合物的 K 谷），三维能带锥 E(k<sub>x</sub>, k<sub>y</sub>) 常与底部的同心费米环及自旋极化箭头结合展示，用来表达自旋—谷锁定特征。

<figure class="research-figure"><img src="/Atlas/figures/literature/M7_SpinValleyLocking_MoS2_Lu2015_Fig4a.jpg" alt="K 谷附近自旋劈裂的三维能带锥与底部同心费米环投影" loading="lazy"/><figcaption>K 谷附近自旋劈裂的三维能带锥 <em>E</em>(<em>k</em><sub>x</sub>, <em>k</em><sub>y</sub>) 及其在底部平面的同心费米环投影，展示面外自旋极化与谷自由度的锁定关系。引自 Saito 等人，<em>Nat. Phys.</em> <strong>12</strong>, 144 (2016)，Fig. 1a，<a href="https://doi.org/10.1038/nphys3580" target="_blank" rel="noopener noreferrer">DOI: 10.1038/nphys3580</a>。</figcaption></figure>

下一步：从同一网格可以回到[有效质量](/Atlas/m/effective-mass/qe/)做局部曲率检查；关注金属等能面时接[费米面](/Atlas/m/fermi-surface/qe/)。

```text
SCF 密度 → 已定位的带边区域 → 真实三维 k 点表
                                  ↓
                           逐点本征值与单位转换
                                  ↓
                        保留完整点阵 → 选择切面作图
```
