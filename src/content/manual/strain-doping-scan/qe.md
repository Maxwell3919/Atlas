晶胞拉长一点，总能量和应力会怎样变？这页从一个已经优化的 fcc Al 原胞出发，沿笛卡尔 x 方向压缩或拉伸，逐点计算固定结构的 SCF。六个纵向应变点都实际运行过，输入、输出和作图数据可以[一起下载](/Atlas/examples/interface-magnet-strain-doping-scan/example-pack.tar.gz)。

这里保持每个原胞的电子数不变，计算的是应变响应。电子掺杂会改变电子数和静电边界，需要另行建立并检查带电体系；下面的曲线没有包含掺杂结果。

## 先确定哪些量可以动

母体结构来自 [Al 晶胞优化](/Atlas/m/vc-relax/qe/#al-vc-relax) 的完成分支，立方晶格常数为 3.95606780081 Å，采用 LDA-PZ 与 `Al.pz-vbc.UPF`。原胞的三条基矢并不沿三个直角坐标轴。要施加 x 方向应变 ε，应把**每一条基矢的 x 分量**乘以 1+ε；y、z 分量保持不变。

例如 +0.5% 应变使 −1.97803390040536 Å 变为 −1.98792406990739 Å。两个含非零 x 分量的基矢都要改。若只把第一条基矢整体放大，得到的是另一种形变。

实际交互中先保存母体输入，再编辑新的应变目录：

```console
maxwell@maxwell:~/al/elastic$ cp ../dfpt/al.scf.in al.reference.in
maxwell@maxwell:~/al/elastic$ cp al.reference.in xx_+0.005/al.scf.in
maxwell@maxwell:~/al/elastic$ vi xx_+0.005/al.scf.in
```

在 `vi` 中用 `/CELL_PARAMETERS` 找到晶胞，修改对应分量，按 Esc 后输入 `:wq` 保存退出。然后重新打开文件核对：

```console
maxwell@maxwell:~/al/elastic$ cat xx_+0.005/al.scf.in
&CONTROL
 calculation = 'scf'
 prefix = 'al'
 pseudo_dir = '<赝势库路径>'
 outdir = './tmp'
 tstress = .true.
 tprnfor = .true.
 verbosity = 'high'
/
&SYSTEM
 ibrav = 0
 nat = 1
 ntyp = 1
 ecutwfc = 40
 ecutrho = 160
 occupations = 'smearing'
 smearing = 'mv'
 degauss = 0.02
 nbnd = 6
/
&ELECTRONS
 conv_thr = 1.0d-12
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.00000000000000 0.00000000000000 0.00000000000000
CELL_PARAMETERS angstrom
-1.98792406990739 0.00000000000000 1.97803390040536
0.00000000000000 1.97803390040536 1.97803390040536
-1.98792406990739 1.97803390040536 0.00000000000000
K_POINTS automatic
16 16 16 0 0 0
```

原胞只有一个 Al 原子，分数坐标仍为 (0,0,0)，没有需要单独优化的内部相对位置。这里使用 `calculation='scf'`；若再次运行自由晶胞的 `vc-relax`，程序会释放人为施加的应变。多原子结构若需要应变下的内部弛豫，应先做固定晶胞的 `relax`，验收力后再进入同协议 SCF，操作见 [固定晶胞优化](/Atlas/m/relax/qe/)。

六个目录分别对应 ε = −0.008、−0.005、−0.003、+0.003、+0.005、+0.008。每个目录保留自己的 `al.scf.in` 和 `tmp`，不共用可写的电荷密度目录。赝势、40/160 Ry 截断能、16³ k 网格、MV 展宽 0.02 Ry 及电子收敛阈值保持一致。

## 把短 SCF 串起来，逐点读取输出

本次作业还同时计算了六个剪切应变点，供 [弹性常数与 Born 条件](/Atlas/m/elastic-born/qe/) 使用。下面保留当时完整的提交脚本，十二次 SCF 在同一份 8 进程作业内串行执行。公开文件中的 `<工作目录>` 和 `<qe_bin>` 需要换成自己的位置。

```console
maxwell@maxwell:~/al/elastic$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-elastic
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
cd "<工作目录>/elastic/xx_-0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xx_+0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xx_-0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xx_+0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xx_-0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xx_+0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_-0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_+0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_-0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_+0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_-0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/elastic/xy_+0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
maxwell@maxwell:~/al/elastic$ sbatch run.slurm
Submitted batch job 1956
```

运行时用 `squeue -j 1956` 看队列状态，用 `tail -f xx_+0.005/al.scf.out` 跟踪这个点的电子迭代。按 Ctrl+C 只退出日志查看。由于脚本依次执行各目录，排在后面的 OUT 尚未出现，可能只是前一个点还在计算；结合当前队列和最近更新的文件判断。

计算结束后，用 `less xx_+0.005/al.scf.out` 阅读输出。`/iteration` 定位电子迭代，`/!` 定位带感叹号的最终能量，`/total   stress` 找到应力，按 `G` 到文件末尾。这个点的能量部分为：

```text
!    total energy              =      -4.19087715 Ry
     estimated scf accuracy    <          1.5E-15 Ry
     smearing contrib. (-TS)   =      -0.00000256 Ry
     internal energy E=F+TS    =      -4.19087459 Ry

     The total energy is F=E-TS. E is the sum of the following terms:
     one-electron contribution =       2.94683257 Ry
     hartree contribution      =       0.00985377 Ry
     xc contribution           =      -1.63714978 Ry
     ewald contribution        =      -5.51041115 Ry

     convergence has been achieved in   7 iterations
```

SCF 在七次电子迭代后收敛，估计误差小于 1.5×10⁻¹⁵ Ry。金属计算用了展宽，程序也明确写出 `The total energy is F=E-TS`。本页表格统一使用感叹号行的 F；不要把部分目录的 F 与另一些目录的 `internal energy E=F+TS` 混在一起拟合。

往下读应力，而不只看总能量：

```text
     Computing stress (Cartesian axis) and pressure

          total   stress  (Ry/bohr**3)                   (kbar)     P=       -4.08
  -0.00005559   0.00000000   0.00000000           -8.18        0.00        0.00
  -0.00000000  -0.00001386   0.00000000           -0.00       -2.04        0.00
   0.00000000   0.00000000  -0.00001386            0.00        0.00       -2.04
```

左侧 3×3 数值的单位是 Ry/bohr³，右侧是 kbar，末尾 `P` 为三个对角分量的平均。QE 这组打印值采用压缩为正的符号；为了按拉伸为正画曲线，表格中的 σ 取相反号，再换成 GPa。于是本例右侧的 −8.18 kbar 对应约 +0.818 GPa 的纵向拉应力。表格从精度更高的左侧数值换算，保留的小数会与两位小数的 kbar 略有差别。

零原子力也不能代替应力检查：这个单原子原胞在均匀应变下依然有零原子力，但有非零应力。应变扫描中这个应力正是要记录的响应。

这里应变沿笛卡尔 x 方向施加，输出应力也按同一笛卡尔坐标系读取，不是沿斜原胞第一条基矢的分量。y、z 没有放松，所以小应变极限的纵向与横向斜率分别联系当前取向下的 C₁₁、C₁₂；不能把纵向斜率直接称为允许横向泊松收缩后的杨氏模量。三维 Al 的应力以体积归一化；若把同样操作换到有真空的单层，GPa 数字还会依赖真空高度，需要重新定义二维弹性量。

文件末尾的计时和结束行说明 pw.x 正常返回；每个目录还应分别确认电子收敛，没有最终的对角化失败，并核对本次输入中的晶胞和 k 网格。当前 +0.5% 点耗时 3.81 s，六个纵向点均保存了独立 OUT。

```text
     PWSCF        :      3.30s CPU      3.81s WALL

   JOB DONE.
```

## 把能量与应力放在同一张图里

提取脚本 [analyse_strain.py](/Atlas/examples/interface-magnet-strain-doping-scan/analyse_strain.py) 从各点 OUT 读取能量和应力，写成 [strain-stress.csv](/Atlas/examples/interface-magnet-strain-doping-scan/elastic/strain-stress.csv)。其中纵向应变的六行为：

| x 应变（%） | F（Ry/原胞） | 拉伸为正的 σxx（GPa） | σyy（GPa） |
|---:|---:|---:|---:|
| -0.8 | -4.19084711 | -1.395292 | -0.343932 |
| -0.5 | -4.19087241 | -0.863654 | -0.212861 |
| -0.3 | -4.19088294 | -0.515015 | -0.127540 |
| +0.3 | -4.19088572 | +0.495891 | +0.121362 |
| +0.5 | -4.19087715 | +0.817757 | +0.203888 |
| +0.8 | -4.190856 | +1.281874 | +0.329074 |

这里一个原胞只有一个原子，因此每原胞和每原子的能量数值相同。绘图时减去这六个采样点中最低的 F，单位换成 meV/atom；该零点只是绘图参考，并非无应变母体能量。图中的连线连接实际采样点。

![Al 的六点纵向应变扫描：能量与应力](/Atlas/examples/interface-magnet-strain-doping-scan/figures/strain-scan.png)

右图的纵向应力随应变近似线性，横向应力也发生变化。它可以用来理解 C₁₁、C₁₂ 从哪里来；弹性常数的精度取决于应力斜率对取样的敏感性。后续将 k 网格加密到 24³、32³、40³、48³ 后，应力斜率仍在变化，具体对照见 [弹性计算中的 k 网格检查](/Atlas/m/elastic-born/qe/)。

要重新画图，解包后进入 `example-pack`，在有 NumPy 和 Matplotlib 的环境运行：

```bash
python3 plot_strain.py
```

[完整绘图脚本](/Atlas/examples/interface-magnet-strain-doping-scan/plot_strain.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/interface-magnet-strain-doping-scan/atlas_plot_style.py)） 只读取这张 CSV，筛选 `mode=xx`，按实际应变排序，输出 `figures/strain-scan.png` 和 SVG。连线用于连接相邻采样点；它没有寻找连续曲线的极小值。

## 对照文献中的分析方法

Alqurashi 等，*The effect of uniaxial compressive and tensile strains on the structural, dynamical, electronic, and optical properties of ZrCl₂ monolayer: Ab-initio calculations*，[DOI: 10.1016/j.chphi.2025.100828](https://doi.org/10.1016/j.chphi.2025.100828)，Table 1 给出实际应变样本的结构与带隙，Fig. 4 绘制带隙随应变变化。该文分析的是 ZrCl₂ 电子响应；本例读取三维 Al 的 F 与应力，纵轴物理量不同。可借鉴的是把实际采样值与明确应变定义对应起来。本页曲线只连接六个 xx 样本，能量零点取最低采样 F，应力保留拉伸为正的单位约定。

## 从原始文件重建结果

逐点读取同一 F 定义和笛卡尔应力，将 QE 压缩为正的应力转换为拉伸为正，再从 CSV 筛选六个 xx 点作图。能量以最低采样 F 为零点。可以把这些读取规则写成下面的请求：

```text
请编写 Python 3 独立后处理程序。读取 elastic/cases.json 所列六个 mode=xx 的 al.scf.in/out/err。检查电子收敛、唯一 JOB DONE 和 stderr；统一读取 QE 感叹号行 F（Ry），应力取左侧 Ry/bohr^3 张量，乘 -14710.5076 转成拉伸为正的 GPa。排序实际应变，输出六行 CSV 与输入 SHA256；图只使用这些样本，F 减最低采样值后乘 13.605693122994*1000 得 meV/atom，不加入零应变或掺杂/DOS/EPC 数据。 缺少文件、格式或非有限数值时明确失败，不猜值、不补零。脚本写入分析结果，保留原始计算文件。
```

[analyse_strain.py 完整源码](/Atlas/examples/interface-magnet-strain-doping-scan/analyse_strain.py) · [plot_strain.py 完整源码](/Atlas/examples/interface-magnet-strain-doping-scan/plot_strain.py) · [atlas_plot_style.py 完整源码](/Atlas/examples/interface-magnet-strain-doping-scan/atlas_plot_style.py)

<details>
<summary>analyse_strain.py 的完整源码</summary>

```python
from pathlib import Path
import csv, re, json, hashlib, math
r=Path(__file__).resolve().parent
rows=[]; hashes={}
def cell(text):
    rows=re.findall(r'CELL_PARAMETERS\s+angstrom\s*\n([^\n]+)\n([^\n]+)\n([^\n]+)',text)
    if len(rows)!=1:raise ValueError('Expected one angstrom cell')
    return [[float(v) for v in line.split()] for line in rows[0]]
reference=cell((r/'elastic/al.reference.in').read_text())

for case in json.loads((r/'elastic/cases.json').read_text()):
    if case['mode']!='xx':continue
    p=r/'elastic'/case['label'];s=(p/'al.scf.out').read_text();err=(p/'al.scf.err').read_text()
    if s.count('JOB DONE.')!=1 or 'convergence has been achieved' not in s or err.strip() or 'convergence NOT achieved' in s or 'Error in routine' in s:
        raise ValueError('Incomplete SCF: '+case['label'])
    inp=(p/'al.scf.in').read_text(); current=cell(inp)
    strain=float(case['engineering_strain'])
    for i in range(3):
        for j in range(3):
            expected=reference[i][j]*(1+strain if j==0 else 1)
            if abs(current[i][j]-expected)>1e-10:raise ValueError('Cell/strain mismatch: '+case['label'])
    energy=float(re.findall(r'!\s+total energy\s+=\s+([-0-9.]+)',s)[-1])
    block=re.findall(r'total\s+stress[^\n]*\n([^\n]+)\n([^\n]+)\n([^\n]+)',s)[-1]
    stress=[[-14710.5076*float(x) for x in line.split()[:3]] for line in block]
    if not math.isfinite(energy) or not all(math.isfinite(v) for row in stress for v in row):raise ValueError('Non-finite result')
    rows.append({**case,'energy_Ry':energy,'sigma_xx_GPa':stress[0][0],'sigma_yy_GPa':stress[1][1],'sigma_zz_GPa':stress[2][2],'sigma_xy_GPa':stress[0][1]})
    for n in ['al.scf.in','al.scf.out','al.scf.err']:
        hashes[str((p/n).relative_to(r))]=hashlib.sha256((p/n).read_bytes()).hexdigest()
rows.sort(key=lambda x:x['engineering_strain'])
if len(rows)!=6:raise ValueError('Expected six xx samples')
with (r/'elastic/strain-stress.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
(r/'strain-summary.json').write_text(json.dumps({'rows':rows,'source_sha256':hashes,'energy':'QE printed F in Ry/one-atom cell','stress':'Tensile-positive; minus QE Ry/bohr^3 * 14710.5076 GPa','scope':'Six xx fixed-cell SCFs, 16^3 k mesh; no doping/DOS/EPC.'},indent=2)+'\n')
print('Six xx SCFs: electronic convergence, one JOB DONE, empty stderr.')
for x in rows:print(f"{x['engineering_strain']:+.3f} F={x['energy_Ry']:.8f} Ry sigma_xx={x['sigma_xx_GPa']:+.6f} sigma_yy={x['sigma_yy_GPa']:+.6f} GPa")
```

</details>

<details>
<summary>plot_strain.py 的完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
rows=sorted((x for x in csv.DictReader((r/'elastic/strain-stress.csv').open()) if x['mode']=='xx'),key=lambda x:float(x['engineering_strain']))
e=np.array([float(x['engineering_strain']) for x in rows])*100
energy=np.array([float(x['energy_Ry']) for x in rows])
sxx=[float(x['sigma_xx_GPa']) for x in rows]
syy=[float(x['sigma_yy_GPa']) for x in rows]
fig,axes=plt.subplots(1,2,figsize=(9,3.8),layout='constrained')
axes[0].plot(e,(energy-energy.min())*13.605693122994*1000,'o-',color='#0072b2')
axes[0].set(xlabel='Applied x strain (%)',ylabel='F - lowest sampled F (meV/atom)')
axes[1].plot(e,sxx,'o-',label='Tensile-positive stress xx',color='#0072b2')
axes[1].plot(e,syy,'s-',label='Tensile-positive stress yy',color='#d55e00')
axes[1].set(xlabel='Applied x strain (%)',ylabel='Stress (GPa)')
axes[1].legend(frameon=False,fontsize=8)
for ax in axes:
    ax.axvline(0,color='.6',lw=.7);ax.grid(alpha=.18)
fig.suptitle('fcc Al | fixed electron number, 16³ k mesh, MV width 0.02 Ry',fontsize=11)
(r/'figures').mkdir(exist_ok=True)
fig.savefig(r/'figures/strain-scan.png',dpi=220)
fig.savefig(r/'figures/strain-scan.svg')
```

</details>

[输入、原始输出与完整后处理包](/Atlas/examples/interface-magnet-strain-doping-scan/example-pack.tar.gz)解压后，在 `example-pack` 目录执行：

```bash
python3 analyse_strain.py
python3 plot_strain.py
```

实际读取结果见正文表及 [elastic/strain-stress.csv](/Atlas/examples/interface-magnet-strain-doping-scan/elastic/strain-stress.csv) · [strain-summary.json](/Atlas/examples/interface-magnet-strain-doping-scan/strain-summary.json)。

相关输入说明：[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/)

下一步沿用相同的应变定义检查 k 网格对应力斜率的影响，见 [弹性计算](/Atlas/m/elastic-born/qe/)。
