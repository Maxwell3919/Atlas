对晶体施加一个很小的形变，再让电子重新达到自洽，应力会怎样改变？弹性常数就是这个变化的斜率。Born 判据进一步检查：任意足够小的均匀应变，是让能量升高，还是存在一个能量下降的方向？

这里继续使用 **fcc Al 单原子原胞**，从成对应变的 SCF 应力输出提取 C₁₁、C₁₂ 和 C₄₄。它是三维立方体系，只有三个独立弹性常数 C₁₁、C₁₂、C₄₄；下面的判据不能直接移植到二维薄层或低对称性晶体。原始结构来自 QE 官方金属示例，经 [晶胞优化](/Atlas/m/vc-relax/qe/) 后，立方晶格常数为 3.95606780 Å。优化最后压力约 0.02 kbar，接近这里采用的零外压条件。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

## 留住零应变结构，再建立成对的形变

[Al 声子页的固定结构 SCF](/Atlas/m/phonon-dfpt/qe/) 中保存的晶格作为参考。先复制输入，新的目录只放新的结构和输出，原来的 SCF 保留：

```console
maxwell@maxwell:~/al/elastic$ cp ../dfpt/al.scf.in al.reference.in
maxwell@maxwell:~/al/elastic$ cp al.reference.in xx_+0.005/al.scf.in
maxwell@maxwell:~/al/elastic$ vi xx_+0.005/al.scf.in

```
这里的 `+0.005` 表示笛卡尔 x 方向伸长 0.5%。对每条晶格矢量，只把它的 x 分量乘以 1.005，y、z 分量保持不变；不是把整条矢量一起缩放。实际编辑后的输入如下：

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
原胞只有一个等价 Al 原子，分数坐标保持 (0,0,0)。这一步是受控应变下的 **SCF**，不能再让 `vc-relax` 把施加的形变优化回去。更复杂的多原子晶体还要区分固定内部坐标的弹性响应与固定晶胞、允许内部原子弛豫的响应。

`tstress=.true.` 要求输出后面用于差分的应力张量，`conv_thr=1.0d-12` 收紧每个形变下的电子自洽停止阈值。斜率最后要除以很小的应变，正负两次 SCF 的数值噪声也会被放大；所以不能只把应变无限缩小。下面保留三种幅度，检查小应变噪声与较大形变的非线性是否已影响读出的斜率。

```console
maxwell@maxwell:~/al/elastic$ diff al.reference.in xx_+0.005/al.scf.in
29c29
< -1.97803390040536 0.00000000000000 1.97803390040536
---
> -1.98792406990739 0.00000000000000 1.97803390040536
31c31
< -1.97803390040536 1.97803390040536 0.00000000000000
---
> -1.98792406990739 1.97803390040536 0.00000000000000
```
负应变另开 `xx_-0.005`。成对计算可以用中心差分消掉参考压力的常数偏移。剪切也成对计算：这里把工程剪应变记作 γ，变形矩阵的 xy 和 yx 元素都取 γ/2；因此 σxy 对 γ 的斜率才是 C₄₄。把两个矩阵元素都误填成 γ，会让读出的剪切斜率相差一倍。

本次共做 ±0.003、±0.005、±0.008 三种幅度，每种幅度有 xx 和 xy 两类形变。下面是一份真实剪切输入的结构部分，可与拉伸目录对照：

```console
maxwell@maxwell:~/al/elastic$ tail -11 xy_+0.005/al.scf.in
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.00000000000000 0.00000000000000 0.00000000000000
CELL_PARAMETERS angstrom
-1.97803390040536 -0.00494508475101 1.97803390040536
0.00494508475101 1.97803390040536 1.97803390040536
-1.97308881565435 1.97308881565435 0.00000000000000
K_POINTS automatic
16 16 16 0 0 0
```
## 提交后先检查应力是否真的写出

每个目录各自使用 `outdir=./tmp`，避免并行计算互相覆盖密度。本次把 12 次短 SCF 串在同一个 8 进程 Slurm 作业内，全部输入相同的截断能、展宽和电子阈值。

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
cd "<工作目录>/al/elastic/xx_-0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xx_+0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xx_-0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xx_+0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xx_-0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xx_+0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_-0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_+0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_-0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_+0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_-0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_+0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
```
```console
maxwell@maxwell:~/al/elastic$ sbatch run.slurm
Submitted batch job 1956
```
运行中先看队列，再看正在运行那个子目录的末尾；第一份输出结束后，脚本还会进入下一份结构。

```bash
squeue -j 1956 -o "%.10i %.16j %.2t %.10M %.5C"
tail -f xx_+0.005/al.scf.out
```

```console
maxwell@maxwell:~/al/elastic$ grep -A3 "total   stress" xx_+0.005/al.scf.out
          total   stress  (Ry/bohr**3)                   (kbar)     P=       -4.08
  -0.00005559   0.00000000   0.00000000           -8.18        0.00        0.00
  -0.00000000  -0.00001386   0.00000000           -0.00       -2.04        0.00
   0.00000000   0.00000000  -0.00001386            0.00        0.00       -2.04
```
左侧 3×3 张量的单位是 Ry/bohr³，右侧是同一张量的 kbar 表示，`P` 是标量压力。这里用于常规拉伸为正的应力定义时，对 QE 输出取负号；再换算为 GPa。转换常数是 1 Ry/bohr³ = 14710.5076 GPa，或直接用 1 kbar = 0.1 GPa。脚本读取左侧较多有效数字，避免用右侧两位小数做很小应变的差分。

```console
maxwell@maxwell:~/al/elastic$ tail -9 xx_+0.005/al.scf.out
 
     PWSCF        :      3.30s CPU      3.81s WALL

 
   This run was terminated on:  21:35:27  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
`JOB DONE.` 只是这一份程序结束。每份输出还检查电子收敛、`Error in routine`、输入对应的结构、应力段与单独的 stderr；不能只统计有几个 `.out` 文件。

## 从正负两份应力读出三个斜率

[analyse.py](/Atlas/examples/al/elastic/analyse.py) 逐份读真实输出，再生成 [strain-stress.csv](/Atlas/examples/al/elastic/strain-stress.csv)。它不会在某份计算未结束时填入默认数值。拉伸对给出

**C₁₁ = [σ<sub>xx</sub>(+ε) − σ<sub>xx</sub>(−ε)] / (2ε)**

**C₁₂ = [σ<sub>yy</sub>(+ε) − σ<sub>yy</sub>(−ε)] / (2ε)**

实际脚本把 yy 和 zz 两个等价分量取平均；剪切对用相同的中心差分求 C₄₄。


后处理的输入字段和单位已经确定，可以用下面的说明让 AI 编程助手写出脚本：

```text
编写 analyse.py，在 elastic 目录读取 cases.json 中的成对应变 SCF。检查每份输出唯一 JOB DONE、电子收敛且 stderr 为空；取最后一份 total stress 的左侧 Ry/bohr³ 张量，乘 -14710.5076 转为拉伸为正的 GPa。按 ±ε 中心差分得到 C11，C12 取 yy、zz 平均；剪切输入工程应变 γ 对应变形矩阵 xy=yx=γ/2，用 σxy 对 γ 的差分求 C44。对 0.003、0.005、0.008 分别保存应力与弹性常数，依立方 Voigt–Reuss–Hill 公式计算 B、Gv、Gr、GH、E、nu 和各向异性比；写 strain-stress.csv 与 elastic-results.csv。保持原始应力符号与原文件。
```

下面是算例实际使用的完整源码。

<details>
<summary>analyse.py 完整源码</summary>

```python
from pathlib import Path
import json,re,hashlib,csv
import numpy as np
RY_BOHR3_GPA=14710.5076
rows=[]
for case in json.loads(Path('cases.json').read_text()):
 p=Path(case['label']);s=(p/'al.scf.out').read_text();err=(p/'al.scf.err').read_text()
 assert s.count('JOB DONE.')==1 and 'convergence has been achieved' in s and not err
 assert 'convergence NOT achieved' not in s and 'Error in routine' not in s
 energy=float(re.findall(r'!\s+total energy\s+=\s+([-0-9.]+)',s)[-1])
 block=re.findall(r'total\s+stress[^\n]*\n([^\n]+)\n([^\n]+)\n([^\n]+)',s)[-1]
 stress=-RY_BOHR3_GPA*np.array([[float(x) for x in line.split()[:3]] for line in block])
 row={**case,'energy_Ry':energy,'sigma_xx_GPa':stress[0,0],'sigma_yy_GPa':stress[1,1],'sigma_zz_GPa':stress[2,2],'sigma_xy_GPa':stress[0,1]}
 rows.append(row)
with open('strain-stress.csv','w') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
results=[]
for mag in [.003,.005,.008]:
 def pair(mode):
  a=[r for r in rows if r['mode']==mode and r['engineering_strain']==mag][0]
  b=[r for r in rows if r['mode']==mode and r['engineering_strain']==-mag][0]
  return a,b
 a,b=pair('xx');c11=(a['sigma_xx_GPa']-b['sigma_xx_GPa'])/(2*mag)
 c12=sum(a[f'sigma_{i}_GPa']-b[f'sigma_{i}_GPa'] for i in ['yy','zz'])/(4*mag)
 a,b=pair('xy');c44=(a['sigma_xy_GPa']-b['sigma_xy_GPa'])/(2*mag)
 B=(c11+2*c12)/3;Gv=(c11-c12+3*c44)/5;Gr=5*(c11-c12)*c44/(4*c44+3*(c11-c12));G=(Gv+Gr)/2
 r={'strain':mag,'C11_GPa':c11,'C12_GPa':c12,'C44_GPa':c44,'C11-C12_GPa':c11-c12,'C11+2C12_GPa':c11+2*c12,'B_GPa':B,'Gv_GPa':Gv,'Gr_GPa':Gr,'GH_GPa':G,'E_GPa':9*B*G/(3*B+G),'nu':(3*B-2*G)/(2*(3*B+G)),'anisotropy':2*c44/(c11-c12)}
 results.append(r)
with open('elastic-results.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
print('All 12 SCFs: one JOB DONE., electronic convergence, empty stderr.')
print('strain     C11       C12       C44       B         GH        E        nu')
for r in results:print(f"{r['strain']:.3f} {r['C11_GPa']:10.4f} {r['C12_GPa']:9.4f} {r['C44_GPa']:9.4f} {r['B_GPa']:9.4f} {r['GH_GPa']:9.4f} {r['E_GPa']:9.4f} {r['nu']:8.4f}")
```

</details>

```console
maxwell@maxwell:~/al/elastic$ ../.venv/bin/python analyse.py
All 12 SCFs: one JOB DONE., electronic convergence, empty stderr.
strain     C11       C12       C44       B         GH        E        nu
0.003   168.4843   41.4836   52.3694   83.8172   56.5700  138.5417   0.2245
0.005   168.1411   41.6749   52.4871   83.8303   56.5504  138.5065   0.2246
0.008   167.3228   42.0629   52.7004   83.8162   56.4705  138.3425   0.2249
```
三种幅度的结果接近，说明这一段应力—应变关系看起来近似线性。到这里还不能说弹性常数已经收敛；下一组真实计算正好展示了原因。

## 幅度检查通过后，金属 k 网格仍然会改变答案

固定 ±0.005 的应变、结构、赝势、40/160 Ry 截断和 0.02 Ry 展宽，只把电子网格逐级加密，得到：

| 电子网格 | C₁₁ / GPa | C₁₂ / GPa | C₄₄ / GPa | B / GPa |
|---|---:|---:|---:|---:|
| 16³ | 168.141 | 41.675 | 52.487 | 83.830 |
| 24³ | 116.625 | 66.212 | 27.273 | 83.016 |
| 32³ | 127.158 | 61.475 | 36.659 | 83.369 |
| 40³ | 129.364 | 60.504 | 42.690 | 83.458 |
| 48³ | 125.995 | 62.122 | 39.277 | 83.413 |

16³ 的三个幅度几乎给出相同斜率，可是换到 24³，C₁₁ 和 C₄₄ 明显改变。与此同时体模量 B 的变化很小。这说明检查一个稳定的能量或一个稳定的 B，不能替其他弹性分量作数值收敛证明。因此，后面的网格系列继续比较每个弹性分量。

<figure><img src="/Atlas/examples/al/figures/elastic-kmesh.png" alt="Al 三个弹性分量和体模量随k网格变化" loading="lazy"/><figcaption>同一组 ±0.5% 应变的电子网格检查。不同分量对网格的敏感程度明显不同。</figcaption></figure>


画图时沿用上面的数据列。给 AI 编程助手的说明可以写成：

```text
编写 plot_elastic.py，在 Al 根目录按列名读取 elastic/kmesh-comparison.csv。横轴 kmesh，单位为 n×n×n 电子网格；一图比较 C11_GPa、C12_GPa、C44_GPa、B_GPa，另一图比较 B_GPa、GH_GPa、E_GPa。纵轴 GPa，使用全部已保存的网格行，分别输出 figures/elastic-kmesh 与 figures/elastic-moduli 的 PNG/PDF，复用 atlas_plot_style.py。
```

下面是算例实际使用的完整源码。

<details>
<summary>plot_elastic.py 完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
p=np.genfromtxt(r/"elastic/kmesh-comparison.csv",delimiter=",",names=True)
(r/"figures").mkdir(exist_ok=True)
for file,cols in [("elastic-kmesh",["C11_GPa","C12_GPa","C44_GPa","B_GPa"]),("elastic-moduli",["B_GPa","GH_GPa","E_GPa"])]:
    fig,ax=plt.subplots(figsize=(6.8,4.4),layout="constrained")
    for name in cols:ax.plot(p["kmesh"],p[name],"o-",lw=1.6,label=name.replace("_GPa",""))
    ax.set(xlabel="n in the n × n × n electronic mesh",ylabel="Elastic response (GPa)")
    ax.set_xticks(p["kmesh"]);ax.legend(frameon=False);ax.grid(alpha=.2)
    fig.savefig(r/f"figures/{file}.png",dpi=220);fig.savefig(r/f"figures/{file}.pdf")
```

</details>

[绘图脚本](/Atlas/examples/al/plot_elastic.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)） 读取 `elastic/kmesh-comparison.csv` 与原始应力表，在本地运行 `python3 plot_elastic.py`；图上的点由这些计算逐项得到。

```bash
python3 plot_elastic.py
```

## 最后才把常数代入 Born 条件

对接近零外压的立方晶体，三个条件是

**C₁₁ − C₁₂ > 0，C₁₁ + 2C₁₂ > 0，C₄₄ > 0**

已完成的各组参数在这三个符号条件上均给出正值。但目前弹性分量仍显示电子网格敏感性，因此合适的表述是：这些已计算参数下没有出现均匀微小应变的负曲率；定量材料常数的数值收敛尚未建立。有限压力、低对称性与二维体系必须采用对应条件和单位，不能只替换材料名。

## 文献中由弹性刚度检验稳定性与强度极限的展示方式

对于正交或单斜等低对称性二维晶体，弹性刚度张量 C<sub>ij</sub> 满足对应的 Born 正定判据后，通常会进一步变换到面内任意方向角 θ，以极坐标图同时展示各向异性杨氏模量、剪切模量和泊松比，直观确认所有面内方向均保持正刚度。

<figure class="research-figure"><img src="/Atlas/figures/literature/M1_PolarModuli_E_G_nu_ZrI2_Chen2023_Fig3.jpg" alt="α-ZrI2 与 β-ZrI2 单层的面内方向依赖弹性模量与泊松比极坐标图" loading="lazy"/><figcaption>正交与单斜二维晶体 α-ZrI<sub>2</sub>、β-ZrI<sub>2</sub> 的方向依赖杨氏模量 <em>E</em>(θ)、剪切模量 <em>G</em>(θ) 及泊松比 ν(θ) 极坐标分布，用于共同检验力学稳定性判据与面内各向异性。引自 Chen 等人，<em>Phys. Rev. Applied</em> <strong>20</strong>, 064048 (2023)，Fig. 3，<a href="https://doi.org/10.1103/PhysRevApplied.20.064048" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevApplied.20.064048</a>。</figcaption></figure>

在线性小应变刚度之外，将平衡态附近求得的弹性模量与大应变非线性拉伸得到的理想断裂强度放在同一张对数坐标图上，可以检验材料的线性弹性刚度与非线性理想强度极限之间的标度关系。

<figure class="research-figure"><img src="/Atlas/figures/literature/M1_AshbyStrengthModulus_2DMagnets_Wang2022_Fig59.jpg" alt="二维材料的二维杨氏模量与理想断裂强度 Ashby 对照图" loading="lazy"/><figcaption>二维磁性材料与常见二维晶体的二维杨氏模量与理想断裂强度双对数关系图，展示小应变线性弹性刚度与非线性理想强度极限之间的标度关系。引自 Wang 等人，<em>ACS Nano</em> <strong>16</strong>, 6859 (2022)，Fig. 59，<a href="https://doi.org/10.1021/acsnano.1c09150" target="_blank" rel="noopener noreferrer">DOI: 10.1021/acsnano.1c09150</a>。</figcaption></figure>

Born 条件检验均匀应变的局部响应，不能代替 [完整声子网格](/Atlas/m/phonon-dfpt/qe/) 或热力学相稳定性。下一步到 [弹性模量](/Atlas/m/elastic-moduli/qe/) 看怎样从同一套 Cᵢⱼ 计算 B、G、E 和 ν。

```text
零应变结构 → 成对拉伸 / 剪切 SCF → 应力符号与单位
                                  ↓
                       中心差分 → 幅度检查 → k网格检查
                                                   ├→ Born 条件
                                                   └→ 弹性模量
```

## 参考资料

[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [Born 稳定性条件原始论文](https://doi.org/10.1103/PhysRevB.90.224104)
