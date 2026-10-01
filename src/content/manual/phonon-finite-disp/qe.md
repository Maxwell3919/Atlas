有限位移声子从一个可以直接检查的量出发：原子移动一点，整套结构上的力怎样改变？界面中，移动一层的原子也会让另一层受力；这些跨层力常数与层内力常数一起决定层间剪切、呼吸和混合振动。应变改变键长后，也需要在新的受约束平衡结构上重新求这组恢复力。

这里用真实 fcc Al 正负位移计算讲清位移、受力与力常数的对应关系，并比较位移幅度和超胞范围。Al 的单原子原胞没有层间模式，但它能展示有限位移法的核心操作。结构、QE 7.5 和 LDA-PZ `Al.pz-vbc.UPF` 与[DFPT 算例](/Atlas/m/phonon-dfpt/qe/)相同，差别是恢复力由实际位移后的 SCF 受力求得。

输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的后处理；赝势按官方来源准备。[Baroni 综述第 IV.B 节](https://doi.org/10.1103/RevModPhys.73.515)解释冻结声子与超胞方法，[Phonopy 4.5.0 定义](https://github.com/phonopy/phonopy/blob/v4.5.0/doc/formulation.md)给出力常数到动力学矩阵的转换。

## 从一个原胞变成带位移的超胞

原胞结构取自已结束的 [晶胞优化](/Atlas/m/vc-relax/qe/)，立方晶格常数为 3.95606780 Å。用 2×2×2 个原胞得到 8 原子超胞。这里采用 Phonopy 4.5.0 的 Python API，明确保留输入原胞的基矢定义 `primitive_matrix='P'`：

```python
ph = Phonopy(unitcell, np.eye(3, dtype=int) * 2,
             primitive_matrix='P')
ph.generate_displacements(distance=0.01, is_plusminus=True)
```

这两行是实际输入生成过程的核心。`unitcell` 的晶格单位为 Å，质量单位为原子质量单位；因此这里的 0.01 是 Å。完整的 [结构和位移生成脚本](/Atlas/examples/al/prepare_finite.py) 保存晶格、质量、位移方向和生成顺序，不能只拿一份力文件猜它对应哪个位移。

<details>
<summary>prepare_finite.py 的完整源码</summary>

```python
from pathlib import Path
import json
import numpy as np
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms
r=Path(__file__).resolve().parent
j=json.loads((r/"structure.json").read_text())
u=PhonopyAtoms(symbols=["Al"],cell=j["cell_angstrom"],scaled_positions=[[0,0,0]],masses=[26.9815385])
output=r/"finite-generated-check";output.mkdir(exist_ok=True)
for dim,amp in [(2,.01),(2,.02),(3,.01)]:
    ph=Phonopy(u,np.eye(3,dtype=int)*dim,primitive_matrix="P")
    ph.generate_displacements(distance=amp,is_plusminus=True)
    dst=output/f"n{dim}-d{amp:.2f}";dst.mkdir(exist_ok=True)
    ph.save(dst/"phonopy_disp.yaml")
    for i,sc in enumerate(ph.supercells_with_displacements,1):
        np.savetxt(dst/f"cell-{i:03d}.txt",sc.cell,fmt="%.14f")
        np.savetxt(dst/f"positions-{i:03d}.txt",sc.scaled_positions,fmt="%.14f")
    print(dst.name,len(ph.supercells_with_displacements),"displaced supercells")
```

</details>

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ ls
disp-001  disp-002  phonopy_disp.yaml  run.slurm
```
Al 的对称性把独立位移压缩到一个方向。由于这里明确使用正负成对位移，仍有两个 SCF 输入。实际移动的是编号 0 的原子，两个笛卡尔位移分别是 (−0.0070710678, 0, +0.0070710678) Å 和反向；向量长度都是 0.01 Å。它沿这份原胞的一条基矢方向，不应把它口头称作 x 轴位移。

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ cat disp-001/al.scf.in
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
 nat = 8
 ntyp = 1
 ecutwfc = 40
 ecutrho = 160
 occupations = 'smearing'
 smearing = 'mv'
 degauss = 0.02
 nbnd = 18
/
&ELECTRONS
 conv_thr = 1.0d-12
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.00178739803459 0.00000000000000 0.00000000000000
Al 0.50000000000000 0.00000000000000 0.00000000000000
Al 0.00000000000000 0.50000000000000 0.00000000000000
Al 0.50000000000000 0.50000000000000 0.00000000000000
Al 0.00000000000000 0.00000000000000 0.50000000000000
Al 0.50000000000000 0.00000000000000 0.50000000000000
Al 0.00000000000000 0.50000000000000 0.50000000000000
Al 0.50000000000000 0.50000000000000 0.50000000000000
CELL_PARAMETERS angstrom
-3.95606780081072 0.00000000000000 3.95606780081072
0.00000000000000 3.95606780081072 3.95606780081072
-3.95606780081072 3.95606780081072 0.00000000000000
K_POINTS automatic
8 8 8 0 0 0
```
`nat=8` 和 8 行原子坐标对应超胞。`calculation=scf` 保持这些位移不动，`tprnfor=.true.` 要求把力写进输出。若把这里改成 `relax`，原子会往平衡位置回去，输出力不再对应最初设定的 0.01 Å。

二阶力常数来自力随位移的变化，位移越小，同样的力噪声在除以位移后就越显著；位移过大又会混入更高阶响应。这里把电子阈值设为 `conv_thr=1.0d-12`，并在同一超胞上比较 0.01、0.02 Å 两个幅度。电子能量残差小不等于力误差已知，最后仍要看两组力得到的频率怎样变化。

超胞增大了实空间体积，同样的电子采样密度需要相应缩小 k 网格。这个 2³ 超胞使用 8³ k 点，等价于原胞约 16³ 的采样密度；后面的 3³ 超胞用 6³，比较超胞大小时另外补算了 2³ 超胞的 9³ k 点，使两者都对应原胞约 18³ 密度。

## 两个 SCF 顺序执行，原始输出各自保留

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-fd2
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
cd "<工作目录>/al/finite-disp/n2-d0.01/disp-001"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/finite-disp/n2-d0.01/disp-002"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
```
这是本次实际使用的串行两步脚本：同一作业分配 8 个 MPI 进程，先完成 `disp-001`，再进入 `disp-002`。每个子目录的 `tmp` 独立，输入和受力对应关系也保持清楚。

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ sbatch --dependency=afterok:1956 run.slurm
Submitted batch job 1959
```
1956 是存档中另一短作业的编号。复现实例时使用 `sbatch run.slurm`，或者换成自己确实需要等待的作业号。

```bash
squeue -j 1959 -o "%.10i %.16j %.2t %.10M %.5C"
tail -f disp-001/al.scf.out
```

## 在 OUT 里把位移与力对应起来

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ grep -A12 "Forces acting on atoms" disp-001/al.scf.out
     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =     0.00138549    0.00000000   -0.00138549
     atom    2 type  1   force =    -0.00076171    0.00000000    0.00076171
     atom    3 type  1   force =     0.00006090    0.00039391    0.00036758
     atom    4 type  1   force =    -0.00036758   -0.00039391   -0.00006090
     atom    5 type  1   force =    -0.00036758    0.00039391   -0.00006090
     atom    6 type  1   force =     0.00006090   -0.00039391    0.00036758
     atom    7 type  1   force =     0.00002632    0.00000000   -0.00002632
     atom    8 type  1   force =    -0.00003674    0.00000000    0.00003674
```
这 8 行依次对应输入里的 8 个原子，每行给出 x、y、z 三个力分量。受位移的原子不会是唯一受力的原子；周围原子的恢复力正是力常数需要的信息。原始 QE 输出用 Ry/Bohr，后处理通过 ASE 3.29.0 读取并转换为 eV/Å，随后 Phonopy 使用 Å、eV/Å 和原子质量计算 THz 频率。两套单位不能混着代入。

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ tail -9 disp-001/al.scf.out
 
     PWSCF        :     19.88s CPU     20.40s WALL

 
   This run was terminated on:  21:36:45  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
对第二个位移也做同样检查。后处理脚本要求每份文件有一次 `JOB DONE.`、出现电子收敛、没有 SCF 失败且 stderr 为空，然后才读取受力；目录存在或退出码为零本身不够。完整 [disp-001 输出](/Atlas/examples/al/finite-disp/n2-d0.01/disp-001/al.scf.out) 保留了从结构、电子迭代到力和计时的全部段落。

## 由力重建频率，并记录声学和规则

[analyse.py](/Atlas/examples/al/finite-disp/analyse.py) 从 `phonopy_disp.yaml` 读取位移顺序，从相同编号的 `.out` 读取力，先生成未额外对称化的力常数，保留处理前的 drift 与原始频率；再通过 `symmetrize_force_constants()` 施加置换对称性与平移和规则，保存处理后的力常数与声子路径数据。


后处理先匹配位移超胞与原子力，再构造力常数。下面的任务保留正负位移、单位和 ASR 设置，使不同结果能够按同一约定比较。

```text
编写有限位移后处理 analyse.py。读取四个目录 n2-d0.01、n2-d0.02、n2-d0.01-k9、n3-d0.01，各自将 phonopy_disp.yaml 与 disp-001/002 的 QE 力输出按编号配对。未完成的目录打印 still running 并不填数；已完成输出检查唯一 JOB DONE、电子收敛和空 stderr。用 ASE 读取 eV/Å 的原子力，Phonopy 使用 primitive_matrix=P，先记录未经对称化的平移残差，再对称化力常数并保存 phonopy_params.yaml。保存 Γ、X、W、L 的原始和处理后频率（THz）；路径 bands.csv 的列为 segment,distance_A_minus1,q1,q2,q3,f1_cm_minus1,f2_cm_minus1,f3_cm_minus1，频率在写表时乘 33.3564095198152 换为 cm⁻¹。保留负频，并保存每份力输出的哈希和净力。
```

<details>
<summary>analyse.py 完整源码</summary>

```python
from pathlib import Path
import json,hashlib
import numpy as np
import phonopy
from ase.io import read
from phonopy.phonon.band_structure import get_band_qpoints_and_path_connections
root=Path(__file__).resolve().parent
summary=[]
for label in ['n2-d0.01','n2-d0.02','n2-d0.01-k9','n3-d0.01']:
 d=root/label
 files=[d/'disp-001/al.scf.out',d/'disp-002/al.scf.out']
 if not all(f.exists() and 'JOB DONE.' in f.read_text() for f in files):
  print(label, 'still running');continue
 forces=[];provenance=[]
 for file in files:
  out=file.read_text();err=file.with_suffix('.err').read_text()
  assert out.count('JOB DONE.')==1 and 'convergence has been achieved' in out and not err
  assert 'convergence NOT achieved' not in out
  f=read(file,format='espresso-out').get_forces()
  forces.append(f)
  provenance.append({'file':str(file.relative_to(root)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'net_force_eV_A':f.sum(axis=0).tolist()})
 ph=phonopy.load(d/'phonopy_disp.yaml',produce_fc=False,symmetrize_fc=False,primitive_matrix='P')
 ph.forces = forces
 ph.produce_force_constants(fc_calculator='traditional')
 raw_fc=ph.force_constants.copy();drift=float(np.max(np.abs(raw_fc.sum(axis=1))))
 ph.run_qpoints([[0,0,0],[.5,0,.5],[.5,.25,.75],[.5,.5,.5]],with_eigenvectors=True)
 raw_freq=ph.qpoints.frequencies.copy()
 ph.symmetrize_force_constants()
 ph.run_qpoints([[0,0,0],[.5,0,.5],[.5,.25,.75],[.5,.5,.5]],with_eigenvectors=True)
 freq=ph.qpoints.frequencies.copy()
 # Angstrom cells, ASE forces eV/Angstrom, phonopy's default THz conversion.
 ph.save(d/'phonopy_params.yaml',settings={'force_constants':True})
 path=[[[0,0,0],[.5,0,.5],[.5,.25,.75],[.5,.5,.5],[0,0,0]]]
 q,connections=get_band_qpoints_and_path_connections(path,npoints=41)
 ph.run_band_structure(q,path_connections=connections,labels=['Γ','X','W','L','Γ'])
 b={k:getattr(ph.band_structure,k) for k in ['distances','qpoints','frequencies']};lines=[]
 for segment,(dist,qs,fs) in enumerate(zip(b['distances'],b['qpoints'],b['frequencies'])):
  lines.extend([[segment,float(x),*qpt.tolist(),*(f*33.3564095198152).tolist()] for x,qpt,f in zip(dist,qs,fs)])
 np.savetxt(d/'bands.csv',np.array(lines),delimiter=',',header='segment,distance_A_minus1,q1,q2,q3,f1_cm_minus1,f2_cm_minus1,f3_cm_minus1',comments='')
 data={'label':label,'phonopy_version':phonopy.__version__,'unit_length':'angstrom','force_unit':'eV/angstrom','frequency_unit':'THz','raw_fc_drift_eV_A2':drift,'raw_gamma_X_W_L_THz':raw_freq.tolist(),'symmetrized_gamma_X_W_L_THz':freq.tolist(),'displacements':[{k:(v.tolist() if hasattr(v,'tolist') else v) for k,v in p.items()} for p in ph.dataset['first_atoms'] if 'forces' not in p],'provenance':provenance}
 # Keep compact displacement identity without bulk force arrays in metadata.
 data['displacements']=[{'number':int(p['number']),'displacement_A':np.asarray(p['displacement']).tolist()} for p in ph.dataset['first_atoms']]
 (d/'summary.json').write_text(json.dumps(data,indent=2));summary.append(data)
 print(label, 'raw FC drift=',drift,'; Gamma THz=',freq[0],'; X THz=',freq[1])
(root/'summary.json').write_text(json.dumps(summary,indent=2))
```

</details>

```console
maxwell@maxwell:~/al/finite-disp/..$ .venv/bin/python finite-disp/analyse.py
n2-d0.01 raw FC drift= 1.7763568394002505e-15 ; Gamma THz= [-5.29508182e-08  4.25307894e-08  5.00338842e-08] ; X THz= [6.3569392 6.3569392 9.8421396]
n2-d0.02 raw FC drift= 1.8180444808058027e-05 ; Gamma THz= [-5.10637868e-08 -3.78379398e-08  9.25452616e-08] ; X THz= [6.35841564 6.35841564 9.84459054]
n2-d0.01-k9 raw FC drift= 1.818044481011194e-05 ; Gamma THz= [-3.61776110e-08 -1.57964203e-08  7.30035453e-08] ; X THz= [6.28098398 6.28098398 9.87013437]
n3-d0.01 raw FC drift= 1.8180444807003315e-05 ; Gamma THz= [-1.27883366e-07 -5.19769200e-08 -1.74046920e-08] ; X THz= [5.63646925 5.63646925 7.82783897]
```
输出中的 drift 是处理前的力常数平移和规则残差，单位 eV/Å²。Γ 点经置换对称性与平移和规则处理后的约 10⁻⁷ THz 是浮点计算残差，应与有限波矢处真正的负频支分开讨论。`phonopy_params.yaml` 留下了用于后续频率计算的力常数；原始 QE 受力输出没有被覆盖。

## 位移幅度和超胞大小是两项不同的检查

首先保持 2³ 超胞、8³ k 网格不变，只把位移从 0.01 Å 加到 0.02 Å。正负成对计算后，X 点频率为：

| 超胞 / k 网格 | 位移 / Å | X 的三支频率 / THz |
|---|---:|---|
| 2³ / 8³ | 0.01 | 6.356939, 6.356939, 9.842140 |
| 2³ / 8³ | 0.02 | 6.358416, 6.358416, 9.844591 |
| 2³ / 9³ | 0.01 | 6.280984, 6.280984, 9.870134 |
| 3³ / 6³ | 0.01 | 5.636469, 5.636469, 7.827839 |

前两行很接近，说明这个测试下位移幅度没有显著改变 X 点频率。后两行保持约 18³ 的原胞电子采样密度，却显示明显的超胞差异；所以不能把“位移幅度稳定”写成“完整有限位移声子已经收敛”。X 点位于 2³ 超胞对应的网格上，却不是 3³ 超胞的直接网格点，后者这里依赖力常数插值，读图时也要记住这层区别。

<figure><img src="/Atlas/examples/al/figures/finite-displacement.png" alt="Al有限位移声子的位移幅度与超胞比较" loading="lazy"/><figcaption>左侧比较同一超胞的两种位移幅度；右侧在相同原胞等效电子采样密度下比较两种超胞。不同检查分别呈现，不混成一条收敛结论。</figcaption></figure>

[plot_finite.py](/Atlas/examples/al/plot_finite.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)） 直接读取各目录的 `bands.csv`，`bands.csv` 的后三列已由分析脚本换成 cm⁻¹，绘图直接读取，按 Γ—X—W—L—Γ 的分段端点放标签。下载整个 Al 示例的数据结构后，在本机运行：


下面的绘图任务保留实际计算路径、频率符号和位移幅度，比较时不移动曲线。

```text
编写 plot_finite.py，在 Al 根目录读取 finite-disp 下四个目录的 bands.csv。第二列为累计倒空间距离，最后三列已经是 cm⁻¹，不再换算。左面板对比 n2-d0.01 与 n2-d0.02；右面板对比 n2-d0.01-k9 与 n3-d0.01。用行 0、40、81、122、163 的路径距离标 Γ—X—W—L—Γ，保留频率零线，输出 figures/finite-displacement.png 和 PDF。复用同目录 atlas_plot_style.py。
```

<details>
<summary>plot_finite.py 完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout="constrained",sharey=True)
series=[[("n2-d0.01","0.01 Å", "#256b8e"),("n2-d0.02","0.02 Å", "#d97742")],[("n2-d0.01-k9","2³ supercell, 9³ k", "#256b8e"),("n3-d0.01","3³ supercell, 6³ k", "#d97742")]]
for ax,cases,title in zip(axes,series,["Displacement amplitude","Supercell range"]):
    for name,label,color in cases:
        x=np.genfromtxt(r/"finite-disp"/name/"bands.csv",delimiter=",",skip_header=1)
        for branch in [5,6,7]:ax.plot(x[:,1],x[:,branch],color=color,lw=1.3,label=label if branch==5 else None,alpha=.85)
    ticks=x[[0,40,81,122,163],1]
    ax.set_xticks(ticks,["Γ","X","W","L","Γ"])
    for p in ticks:ax.axvline(p,color="0.8",lw=.6)
    ax.axhline(0,color="0.3",lw=.7);ax.set(xlim=(ticks[0],ticks[-1]),title=title)
    ax.legend(frameon=False,fontsize=9)
axes[1].legend(frameon=False, fontsize=9, loc="lower center", bbox_to_anchor=(0.5, 0.07))
axes[0].set_ylabel("Frequency (cm⁻¹)")
(r/"figures").mkdir(exist_ok=True)
fig.savefig(r/"figures/finite-displacement.png",dpi=220);fig.savefig(r/"figures/finite-displacement.pdf")
```

</details>

```bash
python3 plot_finite.py
```

X 点频率对 0.01 与 0.02 Å 位移的差别很小，而对超胞范围的差别明显。当前下一项有信息量的比较是扩大超胞并保留相近的电子采样密度，再将共同 q 点与 DFPT 对应起来。

## 把这条受力路线用于界面与应变结构

力常数含有原子 I、J 和方向 α、β 两套索引：`C_Iα,Jβ = −∂F_Iα/∂u_Jβ`。正负位移时，可沿实际位移方向取中心差分 `−[F_Iα(+δ)−F_Iα(−δ)]/(2δ)`，再由对称性恢复独立分量。本例位移沿原胞基矢方向而非单一笛卡尔轴，因此应由 Phonopy 读取完整位移向量与力，不能将力表中的 x 分量直接除以 0.01 Å 当成全部力常数。

在异质结里，I 与 J 位于不同层时对应跨层恢复力。将两层分开，只保留各自原子列的受力，会丢掉这组耦合。输入超胞、位移 YAML 和每份输出的原子顺序必须一致；受力表保留全部原子，后面的层投影则在完整动力学矩阵对角化以后进行。

二维超胞沿面内扩大，真空方向通常保留一次周期；这与上面 Al 的 2³、3³ 三维超胞不同。超胞大小约束的是能够解析的实空间力常数范围，电子 k 网格决定每份受力的采样。上表中 2³/9³ 与 3³/6³ 对应相近电子采样密度，仍有明显频率差，正说明只比较位移幅度不足以确定跨胞恢复力。

对[应变结构](/Atlas/m/strain-doping-scan/qe/)，先固定所定义的受应变晶格，再弛豫允许变化的内部位置，随后生成正负位移。若直接把未弛豫结构当平衡点，其残余力与局域曲率会混在一起；若在位移 SCF 中继续弛豫，施加的扰动又会被消去。层间约束也会改变振动问题，例如固定衬底原子与让所有层自由移动得到的模式不能放在同一张图中按编号直接比较。

## 从力常数到可辨认的原子运动

Phonopy 将 Fourier 力常数除以 √(M_I M_J) 后对角化，得到 ω² 和正交本征矢 e；结构显示的相对位移由 `u∝e/√M` 得到。因此投影本征矢与显示原子振幅是相邻的两步，下载的力常数、频率和向量应该属于同一次处理。Al 的质量全部相同，这个差别在相对运动上不明显；到了含 C 或 N 的多元素界面就不能省略质量因子。

[Yang、Jiang 与 Zhao 的 1H-AlH₂ 论文](https://doi.org/10.1088/0256-307X/40/10/107401) Fig. 3(a)（原文第 3 页）给出真实 Γ 模式与对称性标签；Fig. 3(c) 把这些振动、色散和 PHDOS 接在一起。H 的面内同相与反相振动具有不同模式对称性，即使原子投影接近，也会产生不同的耦合。这个例子说明为什么模式分析需要位移方向和相位。当前 Al 数据只展示受力与频率比较，光学模式图属于该论文的 AlH₂。

若要沿有限 q 模式构造畸变，超胞还必须容纳该模式的相位周期。Ba₂N 论文 [Fig. 6(e)](https://doi.org/10.1103/PhysRevB.105.165101)用 √3×√3 超胞显示 K 软模，而本例 Al 的超胞用来求有限范围力常数；两种超胞选择服务于不同的量。有限 q 的相容条件和畸变能量判读见[虚频与软模](/Atlas/m/imaginary-phonon/qe/#h-有限-q-软模对应什么结构变化)。

## 参考资料

[Phonopy QE 接口](https://phonopy.github.io/phonopy/qe.html) · [Phonopy 4.5.0 公式](https://github.com/phonopy/phonopy/blob/v4.5.0/doc/formulation.md) · [AlH₂ 原文 Fig. 3](https://cpl.iphy.ac.cn/article/doi/10.1088/0256-307X/40/10/107401)
