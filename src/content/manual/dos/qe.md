界面前后近费米能级的态数和层来源怎样改变？先用 Si 的均匀网格结果认识 DOS 的单位、积分和投影缺口，再读 ZrCl₂/Sc₂C 的四态冻结对照。窄窗口积分在具体输出后给出，电子态归属与电荷转移采用不同定义。

## 在能量轴上数状态，先用均匀 k 网格

Si 的哪些能量区间聚集了较多电子态，积分后的状态数是否与占据带相符？总 DOS 把整个布里渊区的能级按权重汇到能量轴上，适合回答这两个问题；路径能带上的线密不代表相应能量区间的态数。

把每个 k 点的能级放到能量轴上，每条离散能级先展成一条有单位面积的窄函数，再按布里渊区权重相加，就是这里的 DOS。为说明归一化，若把非磁体系的 k 权重记作 $w_k$ 并约定 $\sum_k w_k=1$，则

$$
D_\sigma(E)=2\sum_{n,k}w_k\,g_\sigma(E-\varepsilon_{nk}),\qquad
\int g_\sigma(E)\,dE=1.
$$

式中的2表示自旋简并；它已经包含在本页程序输出里，不是读完 DOS 后再乘的系数。$g_\sigma$ 的单位是 eV⁻¹，所以一小段能窗的面积近似为 $D(E)\,\Delta E$，才是该能窗内的状态数。将整条带都纳入能窗时，每条非磁性带贡献两个态；电子数还要按占据计算，不能把未占据态一起算成电子。程序文件中的 k 权重也可能已有自旋因子，手工核算时须先查权重和，不能把这个归一化约定直接套给任意 XML。

[Yates 等，Sec. II D、Eqs. (33)–(34) 与 Fig. 3](https://arxiv.org/pdf/cond-mat/0702554)用金刚石比较固定展宽和随带速度变化的展宽，说明峰形同时受 k 网格与展宽影响。本页采用 QE 的固定 Gaussian 展宽，后面的积分和采样解释针对这套 Si 数据，没有改用论文的自适应插值方案。

这里接 [Si 的 24³ NSCF](/Atlas/m/nscf/qe/)。那一页已经保留 8 条能带并检查本征值求解；`dos.x` 在这些带能量上做布里渊区加权，不再求一份新的电荷密度。高对称路径的点分布服务于画线，不能代替这里的均匀采样。

本例文件可[一起下载](/Atlas/examples/si-pbe-electronic-files.tar.gz)。保留解包后的 `si-pbe` 目录结构，绘图只需 NumPy 与 Matplotlib；计算使用的赝势按 [SCF 页](/Atlas/m/scf/qe/)准备。

下载包保留输入、输出、XML 与作图数据，未打包 `tmp/si.save` 中的电荷密度和波函数。阅读输出、重新作图可直接使用包内文件；重新计算时，先完成 [24³ NSCF](/Atlas/m/nscf/qe/)，再把这份保存数据复制到本页的 `dos-cg` 目录。

[dos.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_DOS.html) · [projwfc.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html) · [QE 后处理手册](https://www.quantum-espresso.org/Doc/pp_user_guide/)

## 让 dos.x 读取正确的那份保存数据

本次从已检查的 `gap24-cg/tmp` 复制到 `dos-cg/tmp`，后处理有自己的目录。用 `vi dos.in` 保存下列实际输入：

```text
[preston@preston-System-Product-Name dos-cg]$ cat dos.in
&DOS
  prefix = 'si'
  outdir = './tmp'
  fildos = 'si.dos.dat'
  Emin = -8.0
  Emax = 16.0
  DeltaE = 0.02
  ngauss = 0
  degauss = 0.01
/
```
`Emin/Emax/DeltaE` 使用 **eV**，而 `degauss` 使用 **Ry**。这里 0.01 Ry 约为 0.1361 eV，不能把它读成 0.01 eV。`ngauss=0` 选择普通 Gaussian 展宽；能量轴上采样更密只会让曲线绘得更细，并没有增加电子 k 点。

`DeltaE=0.02 eV` 比这次的展宽小，用来在能量轴上取足够细的绘图点；曲线看起来平滑，不等于能分辨 0.02 eV 的细节。减小 `degauss` 后，原先被抹平的细节和 k 采样造成的锯齿都可能出现，需要配合更密的 NSCF 网格比较。`Emin=-8`、`Emax=16` 只规定本次输出能窗；若想分析更高能量，先核对 8 条带是否已经覆盖，而不是只扩大这两个数。

这里有三个独立的改变：加密 NSCF 网格增加进入积分的能级，减小展宽改变每个能级铺开的宽度，减小 `DeltaE` 只增加同一条展宽曲线的输出点。若只把 `DeltaE` 改得很小，稀疏电子网格产生的峰仍在；若只加大展宽，锯齿可能消失，却也可能抹掉真实近费米结构。[QE 7.5 的 `dos.x` 定义](https://github.com/QEF/q-e/blob/qe-7.5/PP/Doc/INPUT_DOS.def)分别规定这些参数和单位，比较峰形时要把三者写在同一图注中。

`dos.x` 根据保存的带能量和权重计算总 DOS，本身不需要再读取所有波函数。需要轨道投影时，`projwfc.x` 才沿另一条依赖读取相应波函数，见 [布居与投影](/Atlas/m/population-analysis/qe/)。

```text
[preston@preston-System-Product-Name dos-cg]$ cat run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-dos
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
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/dos.x -in dos.in > dos.out 2> dos.err
```
这份短后处理仍以 Slurm 脚本运行，`sbatch run.sh` 提交后，先读 `dos.out` 和 `dos.err`，确认保存目录、交换关联设置和展宽都与预期对应。本次输出中的这几段是：

```text
     Reading xml data from directory:

     ./tmp/si.save/

     IMPORTANT: XC functional enforced from input :
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)
     Any further DFT definition will be discarded
     Please, verify this is what you really want
```

```text
     Gaussian broadening (read from input): ngauss,degauss=   0    0.010000


     DOS          :      0.70s CPU      0.73s WALL


   This run was terminated on:  22: 2:58  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
本次实际 WALL 时间为 0.73 s。[dos.err](/Atlas/examples/si-pbe-electronic/dos-cg/dos.err) 为 1300 字节，包含重复的 `Authorization required, but no authorization protocol specified` 环境提示；原始文件随结果保留。这次已写出完整 DOS 表，输出未见致命错误。`JOB DONE.` 表明这一步执行完毕；图的可靠范围仍取决于 NSCF 的空带数、k 网格与后处理展宽。

## 数据文件的第三列不是“又一条 DOS”

```text
[preston@preston-System-Product-Name dos-cg]$ head -n 6 si.dos.dat
#  E (eV)   dos(E)     Int dos(E) EFermi =    6.397 eV
  -8.000  0.9182E-85  0.1836E-86
  -7.980  0.9182E-85  0.3673E-86
  -7.960  0.9182E-85  0.5509E-86
  -7.940  0.9182E-85  0.7345E-86
  -7.920  0.9182E-85  0.9182E-86
```
三列依次为能量 eV、总 DOS（states/eV/cell）和累计态数。这里是非自旋极化体系，总 DOS 已计入自旋简并；不要再额外乘 2。

这里的 cell 是输入中的两原子 Si 原胞。若报告每原子 DOS，曲线与累计态数都除以 2，纵轴同步改成 `states/eV/atom`。换超胞后不归一化，量级会随胞内态数变化，不能据此判断电子态增多。

第三列从文件下限累计态数。在占据区上方、导带开始之前的平台，可结合 8 个价电子检查归一化；高能端继续增长，是因为开始累计空态。共线自旋极化 `nspin=2` 则有 `E、DOSup、DOSdw、Int DOS` 四列，总 DOS 为 up+down；将 down 镜像到负侧只是显示约定，求和不能使用镜像后的负数。SOC/非共线输出需按自己的表头解析，本例脚本限定非自旋三列格式。

开头的 DOS 约 10⁻⁸⁵，位于本次能带范围以外。这个小数不能单独被命名为某种物理“下限”；应结合采样能区、有限展宽与程序的数值处理来读。再看文件末尾：

```text
[preston@preston-System-Product-Name dos-cg]$ tail -n 4 si.dos.dat
  15.940  0.2460E-01  0.1597E+02
  15.960  0.2901E-01  0.1597E+02
  15.980  0.3403E-01  0.1597E+02
  16.000  0.3945E-01  0.1597E+02
```
积分到 16 eV 时约为 15.97 个态，接近 8 条带乘自旋简并的 16；它包含空态，因此不是应当等于整胞 8 个电子的电子数验收。有限能窗也可能漏掉高能端的部分带和展宽尾部。

独立对打印数据做梯形积分得到 `15.97326485`，与第三列末尾 `15.97` 在打印精度内相符。用同一 `gap24-cg` 的价带顶 `6.397028955497 eV` 和采样导带底 `6.937158523640 eV` 定位带隙中点，读取累计列得到 `8.0000`。

在价带顶本身，累计列约为 `7.997`：Gaussian 展宽将部分边缘谱重带到了价带顶以上。不能为了让该端点等于整数而重新缩放曲线。`degauss` 是 QE 的展宽参数，不是能量步长、仪器分辨率或真实温度。

<span id="可复制的-ai-编码提示词" class="legacy-anchor" aria-hidden="true"></span>
<span id="h-可复制的-ai-编码提示词" class="legacy-anchor" aria-hidden="true"></span>
## DOS 数据列与能量参考

将下面的需求和本页示例文件交给代码助手：

```text
编写 Si 总 DOS 后处理程序，使用 Python 3、NumPy 和 Matplotlib。
输入：dos-cg/si.dos.dat 三列为能量（eV）、DOS（states/eV/cell）、累计态数（states/cell）；Gaussian degauss=0.01 Ry。零点取 gap-results.json 的 gap24-cg VBM=6.397028955497 eV。
方法：平移能量轴，保留原始 DOS 和 Gaussian 尾部；本例非自旋总 DOS 已含简并。
检查：1201 个严格递增点、间隔约 0.02 eV、有限值；梯形积分约 15.9733，与累计末值 15.97 在打印精度内相符，带隙中点累计态数约 8。
输出：源码、依赖、命令、摘要、PNG/SVG/PDF；坐标为 E−VBM (eV)、DOS (states/eV/cell)，显示 −13…8 eV。精确带边取本征值，DOS 用于态数分布。
```

## 后处理源码与运行

完整源码：[plot_si.py](/Atlas/examples/si-pbe-electronic/plot_si.py) · [atlas_plot_style.py](/Atlas/examples/si-pbe-electronic/atlas_plot_style.py)。Python 3 依赖：NumPy、Matplotlib。

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
python3 plot_si.py dos
```


## 从原始能量转到相对价带顶的图

脚本读取原始 [si.dos.dat](/Atlas/examples/si-pbe-electronic/dos-cg/si.dos.dat)，将能量减去同一 24³ NSCF 的价带顶。运行上面的命令得到下图：

![Si 的总态密度，能量相对同一 24³ NSCF 的价带顶](/Atlas/examples/si-pbe-electronic/plots/dos.png)


Gaussian 展宽会把带边附近的权重扩展到相邻能量，不能从这一张有展宽的图上量出高精度带隙。带边位置与采样依赖回到 [带隙页](/Atlas/m/band-gap/qe/)核对；DOS 峰形需要另做 k 网格与展宽的交叉比较。

图上 0 eV 是同一父链的价带顶，正能侧的 Gaussian 尾巴不能单独判为金属性。比较峰位和峰高前，先固定每原胞/每原子的归一化、能量参考和展宽。

区分 s/p 可读已有[布居页](/Atlas/m/population-analysis/qe/)的均匀 18³ 分支。它与本页 24³ DOS 的网格不同；下面只核对该 18³ 分支内部的关系，不把它逐行扣到 24³ 曲线上。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 4 population-cg/si.pdos_tot
# E (eV)  dos(E)    pdos(E)
  -6.101  0.475E-06  0.473E-06
  -6.081  0.120E-05  0.119E-05
  -6.061  0.291E-05  0.290E-05
[preston@preston-System-Product-Name si-pbe]$ head -n 4 'population-cg/si.pdos_atm#1(Si)_wfc#2(p)'
# E (eV)   ldos(E)   pdos(E)    pdos(E)    pdos(E)   
  -6.101  0.394E-08  0.131E-08  0.131E-08  0.131E-08
  -6.081  0.104E-07  0.347E-08  0.347E-08  0.347E-08
  -6.061  0.265E-07  0.883E-08  0.883E-08  0.883E-08
```

`si.pdos_tot` 第二列是该分支总 DOS，第三列是所有投影态的 PDOS 和，不能将两列相加。p 文件第二列 `ldos` 已是三个 p 分量之和，后三列依次 `pz、px、py`；加完后三列再加第二列，会把 p 权重数两次。s 文件的 ldos 与唯一 s 分量同样重复表示同一壳层。

整胞投影和应取两个原子的 s 文件各一份 ldos，加上两个原子的 p 文件各一份 ldos，对应 `si.pdos_tot` 第三列。有限投影空间未覆盖的部分保留下来，不能强行放大 PDOS 去等于总 DOS。本例文本只保留有限有效位数，逐行求和最大差 `0.006 states/eV/cell`，全部在各列舍入界内；不能把这点打印差当成额外丢失的物理态。

“原子文件”说明投影来自哪个原子，并不自动把纵轴变成每原子归一化：每个文件仍是该原子在当前计算胞里的贡献。两个 Si 的 p 文件相加得到整胞 p 谱，若再报告平均每个 Si 的 p 谱，才另除以2。先逐行核对能量网格和壳层和，再做这个归一化，能避免把“每原子平均”和“按原子选出的贡献”混成同一种曲线。

共线自旋极化时，`pdos_tot` 变为 `E、DOSup、DOSdw、PDOSup、PDOSdw`；原子文件也分别给 up/down 的 ldos 和 m 分量。按同一自旋、同一能量点求和后，再合并通道。本例非磁数据已含自旋简并，不再乘 2。

## 二维异质结 ZrCl₂/Sc₂C：轨道分辨 PDOS 与能带、二维费米面的共享能量轴对准

在多元素金属异质结中，除总态密度外，常通过 `projwfc.x` 生成按原子和角动量拆解的分波态密度（PDOS）。在 **`ZrCl₂/Sc₂C`**（[完整计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中，子图 **b**（`PDOS`）以 `scf/pwx.out` 的 `E_F = 0.3133 eV` 为能量零点，绘制 `zrclscc.pdos_tot` 的灰色填充总 DOS 以及 `Zr-4d`、`Sc-3d`、`C-2p`、`Cl-3p` 四组投影态密度曲线，与左侧子图 **a** 的轨道投影能带共享纵轴 `E − E_F ∈ [−2.5, 2.0] eV`；右侧子图 **c** 则展示由 `zrclscc_fs.bxsf` 插值得到的第 26、27 带二维六角布里渊区费米面：

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png" alt="ZrCl₂/Sc₂C 的轨道投影能带、共享能量纵轴的水平分波态密度 PDOS 与二维六角费米面" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 的电子结构三联图：(a) 轨道投影能带；(b) 与能带共享 <code>E − E_F</code> 纵轴的水平总 DOS（<code>zrclscc.pdos_tot</code> 灰色填充）及 <code>Zr-4d</code>、<code>Sc-3d</code>、<code>C-2p</code>、<code>Cl-3p</code> 分波态密度；左图投影权重已按实际 <code>scf/fatbands.projwfc_up</code> 中每态头的原子号和角动量逐态求和核对；曲线原子映射：Zr-4d[#1]、Sc-3d[#5+#6]、C-2p[#2]、Cl-3p[#3+#4]；(c) 由 <code>zrclscc_fs.bxsf</code> 提取的第 26、27 带二维六角费米面。</figcaption></figure>

<figure class="research-figure">
<img src="/Atlas/examples/zrcl2-sc2c/site-index-map.svg" alt="QE 7.1 ZrCl2/Sc2C atom sites by fractional z, with atom indices grouped into orbital curves" loading="lazy"/>
<figcaption>QE 7.1 ZrCl2/Sc2C site mapping. Layer labels and fractional z values follow the scf/pwx.in crystal coordinates; horizontal spacing is schematic.</figcaption>
</figure>

这张历史 QE 7.1 图先把能带和 PDOS 的相同能量位置联系起来；平缓路径段只是寻找 DOS 峰来源的线索。具体峰重来自均匀网格积分，且四条选定轨道曲线没有覆盖全部原子轨道。下面的四态冻结对照来自独立的 QE 7.2 链，分别在该链内比较，不将其与历史图拼成一次定量应变扫描。

### 冻结几何对照：异质结与孤立 Sc₂C 的 PDOS

这组控制计算在 0% 与 +1.5% 两种应变设置下，分别比较异质结中的 Sc₂C 层、ZrCl₂ 层与孤立 Sc₂C。所有坐标均保持冻结，因此它们不代表弛豫平衡结构。图中每条谱都以各自计算的费米能级为零点；这种分别对齐可以比较费米能级附近的谱形和权重，不能据此判断绝对能带偏移或电荷转移。

<figure class="research-figure"><img src="/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/frozen_pdos.png" alt="0% 与 +1.5% 设置下，异质结 Sc₂C 层、ZrCl₂ 层以及冻结孤立 Sc₂C 的费米能级附近投影态密度对照" loading="lazy"/>
<figcaption>冻结坐标下的投影态密度，能量窗为各自费米能级附近 −2 至 +2 eV。左、右面板分别为 0% 与 +1.5%；实线为异质结中的 Sc₂C 层，虚线为孤立 Sc₂C 对照，另示异质结中的 ZrCl₂ 层。图例按输入原子编号归并：异质结中 Sc₂C = C#2 + Sc#5-6、ZrCl₂ = Zr#1 + Cl#3-4；孤立 Sc₂C = Sc#1-2 + C#3。
纵轴单位为 states/eV/simulation cell。</figcaption></figure>

从同一长表在 E−E_F=0 做线性插值，并在 −0.1～0 eV 上补入两个窗口端点后用梯形法积分，得到以下具体读数。两种模型各含一份 Sc₂C 化学式，层投影的归并规则与图一致。

| 冻结状态 | Sc₂C 层 D(E_F) / states·eV⁻¹·cell⁻¹ | Sc₂C 层窗口谱重 / states·cell⁻¹ |
|---|---:|---:|
| 异质结 0% | 2.580959 | 0.150760 |
| 孤立 Sc₂C 0% | 4.239773 | 0.364999 |
| 异质结 +1.5% | 2.036121 | 0.158319 |
| 孤立 Sc₂C +1.5% | 4.429229 | 0.463278 |

这张表有两种比较，先固定问题再选行。比较接触效应时，在同一个应变下拿“异质结中的Sc₂C层”与“冻结孤立Sc₂C”配对；比较应变响应时，拿同一种模型的0%与+1.5%配对。两种模型各含一个Sc₂C化学式，层投影定义与图一致，所以这些层谱可以按同一份Sc₂C比较；它们仍不是同一绝对能量轴上的密度差。

以下由原CSV全精度值计算，变化定义为100×(目标/参照−1)，没有重新求谱或改变展宽。

| 比较 | 参照 → 目标 | Sc₂C层 D(E_F) 变化 | −0.1～0eV窗口谱重变化 |
|---|---|---:|---:|
| 0%下的接触对照 | 孤立层 → 界面内层 | −39.1251% | −58.6958% |
| +1.5%下的接触对照 | 孤立层 → 界面内层 | −54.0299% | −65.8264% |
| 界面内层的应变对照 | 0% → +1.5% | −21.1099% | +5.0139% |

同一界面层的费米点读数下降而窄窗口面积略增，说明谱形发生了重新分布；单报一个 D(E_F) 会漏掉后一项。先在既有冻结图上看零能附近曲线的宽度与左右变化，再沿[逐态胖带](/Atlas/m/fatband/qe/)寻找相应分支，最后用空间密度判断态的位置。这里没有由层谱下降推出失去同样比例的电子，也没有由峰高判断有限q的EPC、λ或Tc；这些科研量的未验收状态保持。

<details>
<summary>由四态读数复核两种比较：逻辑、完整源码与实际输出</summary>

处理逻辑是保留前表的三种单位和四个状态名称，只对Sc₂C这一相同层定义作配对。输入是已经由原长表提取的 `frozen-window.csv`，不把图像上的高度再读成数字；脚本用全精度CSV值计算百分比，并拒绝覆盖源或已有结果。可把下面的具体需求交给编程助手：

```text
读取既有 frozen-window.csv，要求四个唯一冻结状态及有限、非负的Sc2C读数。
在0%和+1.5%下分别比较孤立层→界面内层，再比较界面内层0%→+1.5%。
对D(EF)与[-0.1,0]窗口谱重分别保留参照、目标、差值和100*(target/reference-1)。
D的原单位为states/eV/cell，窗口谱重为states/cell，百分比不是电子转移量。
仅用Python标准库输出新CSV和终端记录，不改源CSV，不画重复的柱图，不调用DFT。
```

[完整比较源码](/Atlas/examples/enrichment-20261003/electronic/compare_frozen_spectra.py) · [全精度结果](/Atlas/examples/enrichment-20261003/electronic/frozen-comparisons.csv) · [实际终端记录](/Atlas/examples/enrichment-20261003/electronic/compare-frozen.out.txt)。在脚本和原CSV所在工作目录运行：

```bash
python3 compare_frozen_spectra.py frozen-window.csv --output frozen-comparisons.csv
```

实际输出：

```text
Contact at 0%: D(EF) change=-39.1251% ; window change=-58.6958%
Contact at +1.5%: D(EF) change=-54.0299% ; window change=-65.8264%
Heterostructure strain 0% to +1.5%: D(EF) change=-21.1099% ; window change=+5.0139%
These are changes of broadened projected spectra, not transferred electrons.
```

```python
#!/usr/bin/env python3
"""Compare existing frozen Sc2C spectral readouts; no DFT or source writes."""
from pathlib import Path
import argparse
import csv
import math

D = "sc2c_pdos_at_EF_states_per_eV_cell"
W = "sc2c_pdos_window_weight_states_per_cell"
PAIRS = [
    ("Contact at 0%", "Isolated Sc2C 0%", "Heterostructure 0%"),
    ("Contact at +1.5%", "Isolated Sc2C +1.5%", "Heterostructure +1.5%"),
    ("Heterostructure strain 0% to +1.5%", "Heterostructure 0%", "Heterostructure +1.5%"),
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == args.source.resolve():
        raise ValueError("Output must differ from the source")
    with args.source.open(newline="") as handle:
        items = list(csv.DictReader(handle))
    rows = {item["state"]: item for item in items}
    if len(items) != 4 or len(rows) != 4:
        raise ValueError("Expected four unique frozen states")
    results = []
    for label, ref, target in PAIRS:
        record = dict(comparison=label, reference=ref, target=target)
        for key, name in [(D, "D_EF"), (W, "window_weight")]:
            x, y = float(rows[ref][key]), float(rows[target][key])
            if not all(math.isfinite(v) for v in [x, y]) or x <= 0 or y < 0:
                raise ValueError("Invalid recorded spectral quantity")
            record[name + "_reference"] = x
            record[name + "_target"] = y
            record[name + "_difference"] = y - x
            record[name + "_change_percent"] = 100 * (y / x - 1)
        results.append(record)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    for row in results:
        print("{}: D(EF) change={:+.4f}% ; window change={:+.4f}%".format(
            row["comparison"], row["D_EF_change_percent"],
            row["window_weight_change_percent"]))
    print("These are changes of broadened projected spectra, not transferred electrons.")

if __name__ == "__main__":
    main()
```

</details>

窗口积分来自已有 Gaussian 展宽谱，尚未乘逐态占据函数。它是这组投影在选定能窗内的谱重，不能当成 Sc₂C 失去的电子数，也不能直接除以面积叫载流子浓度。各图独立减去各自 E_F，绝对带偏移另需共同势参考；该四态快照也不能单凭 D(E_F) 判断 EPC 或 Tc。

## 从长表提取费米点与窗口谱重

数据格式为一行一个状态/能量点，`energy_minus_fermi_eV` 已减去该状态的 E_F；`sc2c_pdos`、`zrcl2_pdos` 与 `total_projected_pdos` 的单位均为 states/eV/simulation cell。读取时保留各态各自的原始网格，以插值补窗口边界，不能把两个层的独立能量轴直接相减。

可使用下面的独立编码需求：

```text
读取 frozen_pdos_long.csv，按 state 分组；核对能量严格递增和有限数值。
以线性插值读取 E−EF=0 的各层 PDOS，并在 [-0.1,0] eV 补入端点后梯形积分。
保留每态原始网格、EF与层定义，报告 D(EF) 的 states/eV/cell 和窗口谱重的 states/cell。
同时逐态检查历史路径投影，输出原始权重；两条计算链分开。
输出完整源码、CSV、JSON与运行记录；不归一化为电子数，不生成装饰性图。
```

[完整提取源码 near_fermi.py](/Atlas/examples/research-scope-electronic/near_fermi.py) · [窗口结果 CSV](/Atlas/examples/research-scope-electronic/results/frozen-window.csv) · [全部结果与定义 JSON](/Atlas/examples/research-scope-electronic/results/near-fermi.json)。Python 3 标准库即可运行；让 `DATA_ROOT` 指向包含 `scf/` 和 `frozen-controls-pdos_20260929/` 的既有 `zrcl2-sc2c` 数据目录：

```bash
python3 near_fermi.py DATA_ROOT --output near-fermi-results
```

实际运行输出：

```text
Frozen cases: 4 Path crossings: 6
Heterostructure 0% Sc2C D(EF)= 2.580959 W[-0.1,0]= 0.150760
Isolated Sc2C 0% Sc2C D(EF)= 4.239773 W[-0.1,0]= 0.364999
Heterostructure +1.5% Sc2C D(EF)= 2.036121 W[-0.1,0]= 0.158319
Isolated Sc2C +1.5% Sc2C D(EF)= 4.429229 W[-0.1,0]= 0.463278
```

<details>
<summary>near_fermi.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Read existing ZrCl2/Sc2C tables. No DFT jobs or source writes."""
from pathlib import Path
import argparse, csv, json, math, re


def interp(rows, key, x):
    for a, b in zip(rows, rows[1:]):
        xa, xb = float(a['energy_minus_fermi_eV']), float(b['energy_minus_fermi_eV'])
        if xa <= x <= xb:
            f = (x-xa)/(xb-xa)
            return float(a[key])*(1-f)+float(b[key])*f
    raise ValueError('Energy outside recorded grid')


def integrate(rows, key, lo=-0.1, hi=0.0):
    pts = [(lo, interp(rows,key,lo))]
    pts += [(float(r['energy_minus_fermi_eV']),float(r[key])) for r in rows
            if lo < float(r['energy_minus_fermi_eV']) < hi]
    pts += [(hi, interp(rows,key,hi))]
    return sum((b[0]-a[0])*(a[1]+b[1])/2 for a,b in zip(pts,pts[1:]))


def read_frozen(root):
    groups = {}
    with (root/'frozen-controls-pdos_20260929/frozen_pdos_long.csv').open() as f:
        for r in csv.DictReader(f):
            if not all(math.isfinite(float(r[k])) for k in
                       ['energy_minus_fermi_eV','sc2c_pdos','zrcl2_pdos','total_projected_pdos']):
                raise ValueError('Nonfinite PDOS')
            groups.setdefault(r['state'],[]).append(r)
    out=[]
    for state, rows in groups.items():
        xs=[float(r['energy_minus_fermi_eV']) for r in rows]
        if any(b <= a for a,b in zip(xs,xs[1:])): raise ValueError('Nonmonotonic grid')
        row={'state':state,'rows':len(rows)}
        for key in ['sc2c_pdos','zrcl2_pdos','total_projected_pdos']:
            row[key+'_at_EF_states_per_eV_cell']=interp(rows,key,0.0)
            row[key+'_window_weight_states_per_cell']=integrate(rows,key)
        out.append(row)
    return out


def read_crossings(root):
    # The .gnu energies are eV; use the parent SCF Fermi energy of this historical chain.
    text=(root/'scf/pwx.out').read_text()
    ef=float(re.findall(r'the Fermi energy is\s+([-+0-9.]+)',text)[-1])
    raw=[tuple(map(float,l.split())) for l in (root/'scf/bands.dat.gnu').read_text().splitlines() if l.strip()]
    lines=[l for l in (root/'scf/fatbands.projwfc_up').read_text().splitlines() if l.strip()]
    heads=[i for i,l in enumerate(lines[:30]) if len(l.split())==3 and all(x.isdigit() for x in l.split())]
    if len(heads)!=1: raise ValueError('Projection header not unique')
    idx=heads[0];nw,nk,nb=map(int,lines[idx].split())
    if (nw,nk,nb)!=(45,151,31) or lines[idx+1].split()!=['F','F']: raise ValueError('Wrong model/spin shape')
    if len(raw)!=nk*nb: raise ValueError('Band shape mismatch')
    bands=[raw[b*nk:(b+1)*nk] for b in range(nb)]
    if any([x for x,e in b] != [x for x,e in bands[0]] for b in bands): raise ValueError('Path mismatch')
    elements={1:'Zr',2:'C',3:'Cl',4:'Cl',5:'Sc',6:'Sc'}
    channels={'Zr_d':(1,'D'),'Sc_d':(5,'D'),'C_p':(2,'P'),'Cl_p':(3,'P')}
    w={k:[[0.0]*nk for _ in range(nb)] for k in [*channels,'all_projectors']}
    ptr=idx+2
    for expected in range(1,nw+1):
        h=lines[ptr].split();ptr+=1
        sid,atom=int(h[0]),int(h[1]);el=h[2];orb=h[3].upper()
        if sid!=expected or elements.get(atom)!=el: raise ValueError('State identity mismatch')
        angular=[c for c in orb if c in 'SPDF']
        if len(angular)!=1: raise ValueError('Invalid orbital label')
        c={'Zr':'Zr_d','Sc':'Sc_d','C':'C_p','Cl':'Cl_p'}[el]
        selected=angular[0]==('D' if el in ['Zr','Sc'] else 'P')
        for ik in range(nk):
            for ib in range(nb):
                a,b,v=lines[ptr].split();ptr+=1;v=float(v)
                if (int(a),int(b))!=(ik+1,ib+1) or not math.isfinite(v) or v < -1e-6:
                    raise ValueError('Projection row mismatch')
                w['all_projectors'][ib][ik]+=v
                if selected:w[c][ib][ik]+=v
    if ptr!=len(lines):raise ValueError('Trailing projection data')
    # Sum is diagnostic only. No complement is identified as an interstitial orbital.
    crossings=[]
    for ib,band in enumerate(bands):
        for ik,((xa,ea),(xb,eb)) in enumerate(zip(band,band[1:])):
            a,b=ea-ef,eb-ef
            if a*b < 0:
                f=-a/(b-a)
                row={'band':ib+1,'left_k_index':ik+1,'right_k_index':ik+2,
                     'path_distance_tpiba':xa+(xb-xa)*f,'EF_eV':ef}
                for c,arr in w.items():row[c]=arr[ib][ik]*(1-f)+arr[ib][ik+1]*f
                crossings.append(row)
    diagnostic={'shape':[nw,nk,nb],'EF_eV':ef,'all_projector_sum_min':min(v for b in w['all_projectors'] for v in b),
                'all_projector_sum_max':max(v for b in w['all_projectors'] for v in b),
                'crossing_method':'Linear interpolation of adjacent path energy and weights; not a uniform BZ integral.'}
    return crossings,diagnostic


def write_csv(p, rows):
    if not rows: raise ValueError('No result rows')
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    a=argparse.ArgumentParser();a.add_argument('data_root',type=Path);a.add_argument('--output',type=Path,default=Path('near-fermi-results'))
    args=a.parse_args();frozen=read_frozen(args.data_root);cross,checks=read_crossings(args.data_root)
    args.output.mkdir(parents=True,exist_ok=True)
    write_csv(args.output/'frozen-window.csv',frozen);write_csv(args.output/'path-crossings.csv',cross)
    report={'frozen_window_eV':[-0.1,0.0],'frozen':frozen,'historical_path':checks,'crossings':cross,
            'definitions':'Window integral is broadened projected spectral weight. It is not charge transfer or carrier density. Frozen QE7.2 and historical QE7.1 path chains are analyzed separately.'}
    (args.output/'near-fermi.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Frozen cases:',len(frozen),'Path crossings:',len(cross))
    for r in frozen:
        print(r['state'], 'Sc2C D(EF)=',format(r['sc2c_pdos_at_EF_states_per_eV_cell'],'.6f'),
              'W[-0.1,0]=',format(r['sc2c_pdos_window_weight_states_per_cell'],'.6f'))
    for r in cross:print('Band',r['band'],'k bracket',r['left_k_index'],r['right_k_index'],
                         'Zr_d=',format(r['Zr_d'],'.6f'),'Sc_d=',format(r['Sc_d'],'.6f'))


if __name__=='__main__':main()
```

</details>


四态冻结对照使用 QE 7.2、vdW-DF3-opt1、100/800 Ry、32×32×1 电子网格；SCF Gaussian 展宽为 0.0037 Ry，投影谱展宽为 0.0022 Ry（约 0.0299 eV）。数值 0.3133 eV 与历史图恰好相同，不代表两条链的波函数、版本和几何已经配对。各态费米能与能量网格信息如下：

| 状态 | E_F (eV) | 能量点数（步长 0.005 eV） | 投影文件数 |
|---|---:|---:|---:|
| 异质结，0% | 0.3522 | 10,533 | 19 |
| 孤立 Sc₂C，0% | −2.1388 | 10,387 | 10 |
| 异质结，+1.5% | 0.3133 | 10,527 | 19 |
| 孤立 Sc₂C，+1.5% | −2.1362 | 10,378 | 10 |

母体异质结的力残差为 0% 时 2.40×10⁻⁴、+1.5% 时 1.20×10⁻⁴ Ry/Bohr；本图只用于冻结几何的电子态对照。
数据与复现文件：[矢量 PDF 图](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/frozen_pdos.pdf) · [长表数据 CSV](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/frozen_pdos_long.csv) · [汇总与求和检查 CSV](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/frozen_pdos_summary.csv) · [复现绘图及检查脚本](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/plot_frozen_pdos.py) · [数据说明](/Atlas/examples/zrcl2-sc2c/frozen-controls-pdos_20260929/README.txt)。

<details>
<summary>plot_frozen_pdos.py 的完整源码</summary>

```python
#!/usr/bin/env python3
from pathlib import Path
import csv
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "delivery"
OUT.mkdir(exist_ok=True)
CASES = [
    ("hetero_0", "hetero_0", "Heterostructure 0%", 0.0, True),
    ("0", "sc2c_frozen_0", "Isolated Sc2C 0%", 0.0, False),
    ("hetero_0015", "hetero_0015", "Heterostructure +1.5%", 1.5, True),
    ("0015", "sc2c_frozen_0015", "Isolated Sc2C +1.5%", 1.5, False),
]
WINDOW = (-2.0, 2.0)
def load_case(spec):
    folder, prefix, name, strain, is_hetero = spec
    d = ROOT / folder
    pw = (d / "pwx.out").read_text(errors="replace")
    pr = (d / "projwfc.out").read_text(errors="replace")
    if "convergence has been achieved" not in pw:
        raise ValueError("SCF not converged: " + name)
    if "JOB DONE." not in pw or "JOB DONE." not in pr:
        raise ValueError("QE output incomplete: " + name)
    fm = next((x for x in pw.splitlines()
               if "the Fermi energy is" in x), None)
    if fm is None:
        raise ValueError("Fermi energy missing: " + name)
    ef = float(fm.split()[-2])
    total = np.loadtxt(d / (prefix + ".pdos_tot"), comments="#")
    energy = total[:, 0] - ef
    sc = np.zeros(len(energy))
    zr = np.zeros(len(energy))
    files = sorted(d.glob(prefix + ".pdos_atm#*_wfc#*"))
    expected = 19 if is_hetero else 10
    if len(files) != expected:
        raise ValueError(name + ": wrong projector file count")
    for f in files:
        match = re.search(r"atm#([0-9]+)", f.name)
        if match is None:
            raise ValueError("Bad projector filename: " + f.name)
        atom = int(match.group(1))
        part = np.loadtxt(f, comments="#")
        if len(part) != len(total):
            raise ValueError("PDOS row count differs: " + f.name)
        if not np.allclose(part[:, 0], total[:, 0], atol=1e-9):
            raise ValueError("PDOS energy grid differs: " + f.name)
        value = part[:, 2:].sum(axis=1)
        if not is_hetero or atom in (2, 5, 6):
            sc += value
        elif atom in (1, 3, 4):
            zr += value
        else:
            raise ValueError("Unexpected heterostructure atom")
    diff = sc + zr - total[:, 2]
    mask = np.abs(energy) <= 0.1
    area = np.trapz(np.abs(total[mask, 2]), energy[mask])
    l1 = 100 * np.trapz(np.abs(diff[mask]), energy[mask]) / area
    peak = np.max(np.abs(total[:, 2]))
    maxerr = 100 * np.max(np.abs(diff)) / peak
    return {"name": name, "strain": strain,
            "hetero": is_hetero, "ef": ef, "energy": energy,
            "sc": sc, "zr": zr, "total": total[:, 2],
            "rows": len(total), "step": np.median(np.diff(total[:, 0])),
            "nproj": len(files), "l1": l1, "maxerr": maxerr,
            "diff": diff}
states = [load_case(item) for item in CASES]
with (OUT / "frozen_pdos_long.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["state", "strain_percent", "fermi_eV",
                     "energy_minus_fermi_eV", "sc2c_pdos",
                     "zrcl2_pdos", "total_projected_pdos",
                     "projected_sum_error"])
    for s in states:
        for i, x in enumerate(s["energy"]):
            writer.writerow([s["name"], s["strain"], s["ef"], x,
                             s["sc"][i], s["zr"][i],
                             s["total"][i], s["diff"][i]])
with (OUT / "frozen_pdos_summary.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["state", "fermi_eV", "rows", "grid_step_eV",
                     "projector_files", "L1_sum_error_pct_EF_pm_0p1eV",
                     "max_sum_error_pct_total_peak"])
    for s in states:
        writer.writerow([s["name"], s["ef"], s["rows"], s["step"],
                         s["nproj"], s["l1"], s["maxerr"]])
fig, axes = plt.subplots(1, 2, figsize=(11, 6), sharex=True,
                         sharey=True)
blue, orange = "#0072B2", "#D55E00"
peaks = []
for strain, ax in zip((0.0, 1.5), axes):
    h = next(s for s in states if s["hetero"]
             and s["strain"] == strain)
    iso = next(s for s in states if not s["hetero"]
               and s["strain"] == strain)
    mask = (h["energy"] >= WINDOW[0]) & (h["energy"] <= WINDOW[1])
    mi = (iso["energy"] >= WINDOW[0]) & (iso["energy"] <= WINDOW[1])
    ax.plot(h["energy"][mask], h["sc"][mask], color=blue,
            lw=1.8, label="Sc2C layer: C#2 + Sc#5-6")
    ax.plot(iso["energy"][mi], iso["sc"][mi], color=blue,
            lw=1.8, ls="--", label="isolated Sc2C: Sc#1-2 + C#3")
    ax.plot(h["energy"][mask], h["zr"][mask], color=orange,
            lw=1.8, label="ZrCl2 layer: Zr#1 + Cl#3-4")
    peaks.extend([np.max(h["sc"][mask]),
                  np.max(iso["sc"][mi]), np.max(h["zr"][mask])])
    ax.axvline(0, color="#555555", lw=0.8, ls=":")
    ax.set_xlim(*WINDOW)
    ax.set_title("0% strain" if strain == 0 else "+1.5% strain")
    ax.set_xlabel("Energy relative to each Fermi level (eV)")
    ax.grid(axis="y", color="#DDDDDD", lw=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
for ax in axes:
    ax.set_ylim(0, max(peaks) * 1.05)
axes[0].set_ylabel("Projected DOS (states / eV / simulation cell)")
fig.suptitle("Frozen-cell projected DOS near the Fermi level",
             y=0.985, fontsize=14)
fig.text(0.5, 0.94,
         "Atom index = QE input order: hetero #1 Zr, #2 C, #3-4 Cl, #5-6 Sc.",
         ha="center", fontsize=9)
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center",
           bbox_to_anchor=(0.5, 0.895), ncol=3,
           frameon=False, fontsize=8)
fig.text(0.5, 0.02,
         "Frozen coordinates, not relaxed equilibrium. EF alignment gives no absolute band offsets or charge transfer.",
         ha="center", fontsize=8, color="#444444")
fig.tight_layout(rect=[0, 0.07, 1, 0.83])
fig.savefig(OUT / "frozen_pdos.png", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "frozen_pdos.pdf", bbox_inches="tight")
plt.close(fig)
print("Wrote products to", OUT)
for s in states:
    print(s["name"], "EF", s["ef"], "rows", s["rows"],
          "projectors", s["nproj"], "L1 error %", s["l1"],
          "max error %", s["maxerr"])
```

</details>

## 把近费米谱重连回空间中的电子态

[Ba₂N 原文 PDF 第3页 Fig. 2(b,d)](https://doi.org/10.1103/PhysRevB.105.165101)应合起来读：(b)横轴为相对费米能的Energy(eV)，纵轴DOS标states/eV，黑线总DOS与Ba-d、N-p、X分量没有各自缩成峰高一；(d)在无量纲ELF=0.5的俯视/侧视图中标出空球X的位置。作者在无核区域放四个半径1.1Å的Wigner–Seitz空球并读取PDOS，又明确有限空球不能覆盖全部电子气。原子投影差额不能直接命名为间隙电子。

复现这类图法，先让总DOS与各分量保持同一零点、单位和能量网格，再用叠加结构的ELF核对投影位置。本站PDOS长表只含实际原子投影，没有空球X，按states/eV/simulation cell归一；跨结构须保持每化学式定义。空间显示接[本站ELF例程](/Atlas/m/elf/)，使用 [VESTA支持的体数据与结构叠加](https://jp-minerals.org/vesta/en/)；不能由DOS曲线生成空间等值面。

同文PDF第4页Fig. 4(a–c)用不同颜色叠加0%至4%双轴应变，三栏分别显示总DOS、Ba-5d与N-2p，保持各自纵轴尺度，在零能附近比较峰形；不能因视觉高度相近就比较跨栏绝对权重。(d)用相同−0.1～0eV能窗、0.0005e/Å³密度等值和侧视方向比较空间分布，作者据此联系表面电子气向层内的积累。本站冻结四态图按应变分栏，匹配层用同色实/虚线并统一纵轴；窗口表积分的是展宽原子PDOS，单位states/cell，尚无该窗口空间密度。重画长表时保留同色/同尺度和原始采样，不把谱面积画成论文(d)的空间云团。

界面或掺杂前后，先问同一个近费米峰属于哪一层，再问它对应哪条带、在哪个 k 区域出现。两个层的 PDOS 在同一能量都非零，可能来自不同 k 或不同带；[逐态胖带](/Atlas/m/fatband/qe/)才能检查它们是否共同出现在同一个态中。若要确定空间转移，再接[差分电荷](/Atlas/m/delta-charge/)；若要讨论阴离子电子位置，再联读[ELF](/Atlas/m/elf/)与选带/选能窗密度。

```text
SCF → 均匀 NSCF → dos.x → 总 DOS 与累计态数
                 └─ projwfc.x → 轨道投影与布居
SCF → 路径 bands ── projwfc.x → 逐 k 胖带
```
