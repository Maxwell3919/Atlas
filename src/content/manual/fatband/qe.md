界面中的费米能级分支来自 ZrCl₂、Sc₂C，还是两层共同参与？这里先用 Si 检查能量与投影按同一个态配对，再从 ZrCl₂/Sc₂C 历史路径输出读取六个费米交点的轨道权重，进一步区分共同权重、杂化线索和间隙态证据。

普通 Si 能带只有能量，不能告诉我们某条分支的 s、p 成分如何沿路径变化。这里把同一个态的轨道投影叠在能带上，用点面积表示权重，比较色散相近的分支是否也有相近的轨道组成。本例沿 Si 的 Γ–X–W–K–Γ–L–X 路径，读取 121 个 k 点、每点八条带的本征值和投影，分别比较两个 Si 原子合计的 s、p 成分。能量、波矢和投影必须按同一个态配对。

[Ba₂N 原文 Fig. 2(a,b,d)](https://doi.org/10.1103/PhysRevB.105.165101)用轨道来源、PDOS 与空间电子分布联读近费米态。下面 Si 的 s/p 投影先说明逐态配对；界面的层来源另从其实际原子编号归并。

下载包保留输入、输出、XML 与作图数据，未打包 `tmp/si.save` 中的电荷密度和波函数。阅读输出、重新作图可直接使用包内文件；重新计算投影时，先完成 [Si 路径能带](/Atlas/m/bands/qe/)，本页读取其中 121 个路径点的波函数。

[projwfc.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html) · [后处理用户手册](https://www.quantum-espresso.org/Doc/pp_user_guide/)

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/si-pbe-electronic-files.tar.gz)。解包后保留目录结构，进入 `si-pbe` 运行文中的绘图命令；赝势按正文的官方来源准备。

## 让投影读取同一路径的波函数

前置能带计算的输入和路径含义见[能带](/Atlas/m/bands/qe/)。这里直接接已经完成的 `bands-cg/tmp/si.save`；它保存的是路径上的波函数。初次路径计算曾出现单个本征值未收敛提示，因此保留旧 `bands` 目录，并在 `bands-cg` 使用 CG 对角化完成复核。以下投影、CSV 和图片全部来自新的同一条链。

下面的复制命令记录了作者将旧 `bands` 目录中的后处理输入迁移到 `bands-cg` 的过程。跟算时直接使用完整下载包中已有的 `bands-cg/projwfc.in` 与 `bands-cg/bands-post.in`；它们读取本页要求的路径波函数。将后面列出的实际提交脚本保存为 `bands-cg/post.sh`，把 `<qe_bin>` 换成本机 QE 路径，再从 `bands-cg` 提交。

```text
[preston@preston-System-Product-Name si-pbe]$ cp bands/projwfc.in bands/bands-post.in bands/post.sh bands-cg/
```

`projwfc.in` 如下。`prefix` 和 `outdir` 指向实际波函数；`filproj` 让程序保存逐 k、逐带的投影。它还会同时生成 PDOS 文件，但下面胖带图读取的是逐态投影表。

```text
[preston@preston-System-Product-Name si-pbe]$ cat bands-cg/projwfc.in
&PROJWFC
  prefix = 'si'
  outdir = './tmp'
  filpdos = 'si-path'
  filproj = 'si-path-projections'
  ngauss = 0
  degauss = 0.01
  DeltaE = 0.02
/
[preston@preston-System-Product-Name si-pbe]$
```

`ngauss=0`、`degauss=0.01 Ry` 和 `DeltaE=0.02 eV` 管理同时写出的 Gaussian 展宽数据；`degauss` 对应约 0.1361 eV 的展宽，`DeltaE` 是能量步长。本页胖带直接读取每个波函数的投影幅度，不用这组展宽生成点的大小。这里只选择 Si 的 s、p 两组，是因为实际赝势给出了这些投影态。路径上的点和权重也不是均匀布里渊区积分，因此同时产生的 PDOS 文件不在本页作为总 DOS 使用。

```text
[preston@preston-System-Product-Name si-pbe]$ cat bands-cg/post.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-pathproj
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
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/projwfc.x -in projwfc.in > projwfc.out 2> projwfc.err
<qe_bin>/bands.x -in bands-post.in > bands-post.out 2> bands-post.err
[preston@preston-System-Product-Name si-pbe]$
```

这个后处理脚本先运行 `projwfc.x`，再用 `bands.x` 生成普通能带数据，分别写 stdout 和 stderr。后者便于单独画普通能带；胖带的能量与投影在下面通过同一 k 点和能带索引合并。

```text
[preston@preston-System-Product-Name bands-cg]$ sbatch post.sh
Submitted batch job 799
[preston@preston-System-Product-Name bands-cg]$ cd ..
```

现在读 `projwfc.out` 的开头和第一个完整 k 点。这一段同时给出程序版本、读入路径、问题规模、原子轨道编号，以及 Γ 点的八条能带投影，值得完整看一次。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 102 bands-cg/projwfc.out

     Program PROJWFC v.7.5 starts on 22Sep2026 at 22: 2:49

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org",
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on     4 processors

     MPI processes distributed on     1 nodes
     R & G space division:  proc/nbgrp/npool/nimage =       4
     5848 MiB available memory on the printing compute node when the environment starts


     Reading xml data from directory:

     ./tmp/si.save/

     IMPORTANT: XC functional enforced from input :
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)
     Any further DFT definition will be discarded
     Please, verify this is what you really want


     Parallelization info
     --------------------
     sticks:   dense  smooth     PW     G-vecs:    dense   smooth      PW
     Min         571     214     63                18093     4156     682
     Max         572     217     64                18095     4157     686
     Sum        2287     859    253                72377    16625    2733

     Using Slab Decomposition


     Gaussian broadening (read from input): ngauss,degauss=   0    0.010000


     Calling projwave ....
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used


  Problem Sizes
  natomwfc =            8
  nbnd     =            8
  nkstot   =          121
  npwx     =          534
  nkb      =           36


     Atomic states used for projection
     (read from pseudopotential files):

     state #   1: atom   1 (Si ), wfc  1 (l=0 m= 1)
     state #   2: atom   1 (Si ), wfc  2 (l=1 m= 1)
     state #   3: atom   1 (Si ), wfc  2 (l=1 m= 2)
     state #   4: atom   1 (Si ), wfc  2 (l=1 m= 3)
     state #   5: atom   2 (Si ), wfc  1 (l=0 m= 1)
     state #   6: atom   2 (Si ), wfc  2 (l=1 m= 1)
     state #   7: atom   2 (Si ), wfc  2 (l=1 m= 2)
     state #   8: atom   2 (Si ), wfc  2 (l=1 m= 3)

 k =   0.0000000000  0.0000000000  0.0000000000
==== e(   1) =    -5.69249 eV ====
     psi = 0.498*[#   1]+0.498*[#   5]
    |psi|^2 = 0.996
==== e(   2) =     6.39703 eV ====
     psi = 0.160*[#   2]+0.160*[#   3]+0.160*[#   4]+0.160*[#   6]+0.160*[#   7]
          +0.160*[#   8]
    |psi|^2 = 0.960
==== e(   3) =     6.39703 eV ====
     psi = 0.160*[#   2]+0.160*[#   3]+0.160*[#   4]+0.160*[#   6]+0.160*[#   7]
          +0.160*[#   8]
    |psi|^2 = 0.960
==== e(   4) =     6.39703 eV ====
     psi = 0.160*[#   2]+0.160*[#   3]+0.160*[#   4]+0.160*[#   6]+0.160*[#   7]
          +0.160*[#   8]
    |psi|^2 = 0.960
==== e(   5) =     8.96656 eV ====
     psi = 0.161*[#   2]+0.161*[#   3]+0.161*[#   4]+0.161*[#   6]+0.161*[#   7]
          +0.161*[#   8]
    |psi|^2 = 0.965
==== e(   6) =     8.96656 eV ====
     psi = 0.161*[#   2]+0.161*[#   3]+0.161*[#   4]+0.161*[#   6]+0.161*[#   7]
          +0.161*[#   8]
    |psi|^2 = 0.965
==== e(   7) =     8.96656 eV ====
     psi = 0.161*[#   2]+0.161*[#   3]+0.161*[#   4]+0.161*[#   6]+0.161*[#   7]
          +0.161*[#   8]
    |psi|^2 = 0.965
==== e(   8) =     9.96909 eV ====
     psi = 0.493*[#   1]+0.493*[#   5]
    |psi|^2 = 0.987

 k =   0.0416666667  0.0000000000  0.0000000000
==== e(   1) =    -5.68477 eV ====
[preston@preston-System-Product-Name si-pbe]$
```

这里 `nkstot=121`、`nbnd=8`，与路径计算一致。`state #1`、`#5` 分别是两个 Si 的 s，`#2–4`、`#6–8` 是 p。Γ 点最深的价带 `e(1)≈−5.69249 eV`，主要由两个 s 态构成，每个打印约 0.498；价带顶的三条近简并带则主要投影到 p。沿路径向下读，轨道混合会随 k 点改变。

输出里的 `psi = 0.498*[#1]+...` 是面向阅读的投影权重摘要，系数只保留有限小数，较小项也可能不列出来。画图时读取[atomic_proj.xml](/Atlas/examples/si-pbe-electronic/bands-cg/atomic_proj.xml)中的复投影幅度，再逐项取模平方。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 25 bands-cg/atomic_proj.xml
<PROJECTIONS>
  <HEADER NUMBER_OF_BANDS="8" NUMBER_OF_K-POINTS="121" NUMBER_OF_SPIN_COMPONENTS="1" NUMBER_OF_ATOMIC_WFC="8" NUMBER_OF_ELECTRONS="8.0000000000000000" FERMI_ENERGY="0.47017480096667780"/>
  <EIGENSTATES>
    <K-POINT Weight="1.6528925619834711E-002">
   0.000000000000000E+00   0.000000000000000E+00   0.000000000000000E+00
    </K-POINT>
    <E>
  -4.183905990614690E-01   4.701729561265998E-01   4.701729560949768E-01
   4.701729562170848E-01   6.590296666173288E-01   6.590296664361792E-01
   6.590296666592196E-01   7.327148044850100E-01
    </E>
    <PROJS>
      <ATOMIC_WFC index="1" spin="1">
 -0.21797427455409485      -0.67120019280928012
  -1.0708443218820918E-006   1.1939152217699256E-006
   7.5150299161386158E-007   3.7511200113721221E-006
   2.0721198735751400E-006   9.6270339196569132E-006
  -5.1028231077068775E-005   1.3564759323458908E-005
   6.3517637404614247E-006   4.2736425026668190E-005
  -3.6827071405134970E-005   3.9544761180232424E-005
  0.27528758630631639      -0.64624055090080490
      </ATOMIC_WFC>
      <ATOMIC_WFC index="2" spin="1">
   4.3409050184961551E-007  -8.6992794760126779E-007
 -0.25354358962640555       -4.1412549225126903E-002
[preston@preston-System-Product-Name si-pbe]$
```

对第 n 条、k 点处的态，记它在第 j 个正交化原子态上的投影幅度为 `cⱼ(n,k)`，则权重为 `|cⱼ|²`。本例的两组数据定义为：

```text
Si_s_weight = |c1|² + |c5|²
Si_p_weight = |c2|² + |c3|² + |c4|² + |c6|² + |c7|² + |c8|²
projection_norm = Si_s_weight + Si_p_weight
```

## 把轨道幅度变成逐态权重

原子态构成有限投影子空间，投影和反映它对平面波波函数的覆盖程度。投影范数接近 1 表示覆盖得较好，小于 1 的部分保留下来；本例没有把 s、p 再强行归一化成和为 1。Γ 点价带顶的投影和约 0.960，最深价带约 0.996，已经能看见两者差异。高能空带可能有更明显的未覆盖成分。

在正交归一投影的定义下，子空间投影范数不应超过完整态的范数；数值实现仍应检查舍入和容差。这里 968 个 `(k,band)` 组合中的最大值为约 **0.99704634**。这个检查能发现权重提取或归一化错误，却不会证明有限原子轨道是描述所有能带的完备基底。简并子空间内单个分支的轨道分量也可能随基选择改变，比较时优先看有明确物理意义的轨道组和简并带组。

还有一个容易混淆的单位：本次 `atomic_proj.xml` 的 `E` 值以 Ry 存储，而 `data-file-schema.xml` 的本征值以 Hartree 存储。[提取脚本](/Atlas/examples/si-pbe-electronic/analyse_electronic.py)用后者的能量画图，并独立把前者乘以 `13.605693122994`，逐点核对二者在 `10⁻⁶ eV` 内一致；k 坐标也逐点核对。只有通过配对后才把能量和权重写在同一行。

`NUMBER_OF_SPIN_COMPONENTS=1` 与 `ATOMIC_WFC` 的 `spin=1` 对应本次非自旋数据。`|cⱼ|²` 是该归一化波函数投到轨道的无量纲权重，画胖带不再乘自旋简并 2；否则权重与点面积都会错。自旋极化计算须把 k 点、带号、自旋共同作为配对键，本例脚本不能未经检查直接套用。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 6 bands-cg/fatband.csv
ik,iband,path_distance_tpiba,kx_tpiba,ky_tpiba,kz_tpiba,energy_eV,Si_s_weight,Si_p_weight,projection_norm
1,1,0.0,0.0,0.0,0.0,-5.6924940963759685,0.9960447859870063,3.6170054105786395e-12,0.9960447859906233
1,2,0.0,0.0,0.0,0.0,6.397028955789438,1.303722630370176e-11,0.9603908906213297,0.9603908906343669
1,3,0.0,0.0,0.0,0.0,6.397028955359185,3.849348316601912e-11,0.9603912217775514,0.9603912218160449
1,4,0.0,0.0,0.0,0.0,6.39702895702055,1.7185514415348437e-10,0.9603921567714943,0.9603921569433495
1,5,0.0,0.0,0.0,0.0,8.966555402944419,5.554953471455121e-09,0.9653691072492603,0.9653691128042138
[preston@preston-System-Product-Name si-pbe]$
```

[完整 fatband.csv](/Atlas/examples/si-pbe-electronic/bands-cg/fatband.csv)有 `121×8=968` 行数据，保留 k 序号、能带序号、累积路径距离、三个 k 坐标、能量、s/p 权重和投影和。这样既可以重画图，也能回到某个图上的点查原始态。

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 12 bands-cg/projwfc.out
     Atom #   2: total charge =   3.9525, s =  1.1116,
     Atom #   2: total charge =   3.9525, p =  2.8408, pz=  0.9469, px=  0.9469, py=  0.9469,
     Spilling Parameter:   0.0119

     PROJWFC      :      0.94s CPU      1.01s WALL


   This run was terminated on:  22: 2:50  22Sep2026

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name si-pbe]$
```

运行末尾确认 `projwfc.x` 正常结束。[完整输出](/Atlas/examples/si-pbe-electronic/bands-cg/projwfc.out)尾部还会打印 Löwdin 数字，但这次输入的是能带路径，不把它用于布里渊区积分的布居结论；[布居分析](/Atlas/m/population-analysis/qe/)另用均匀 `18³` 网格演示。

<span id="把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
<span id="h-把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
## 能量与投影权重的配对

下面的任务把投影权重与路径本征值按 k 点和带编号合并；画图之前先检查记录数、能量参考和投影归并。

```text
编写 Si 逐 k 逐带轨道投影程序，使用 Python 3、NumPy 和 Matplotlib。
输入：bands-cg/atomic_proj.xml、data-file-schema.xml、projwfc.out，对照 fatband.csv。atomic_proj 为 Ry，QEXSD 为 Hartree，换算常数分别为 13.605693122994、27.211386245988 eV。
方法：按 k 点和带号配对，对复幅度求模平方。状态 1、5 合为 Si-s，2–4、6–8 合为 Si-p；projection_norm=s+p，保留原始投影和。本例为一个自旋分量。
检查：121×8=968 行，k 一致、能量差 <1e-6 eV、非负权重；投影和约 0.0615665–0.9970463。
输出：源码、依赖、命令、CSV/JSON、PNG/SVG/PDF。面板共用路径、6.397028957255 eV 的 VBM 参考及散点面积标度，面积正比于权重，灰线保留本征能带。
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

`analyse_electronic.py` 是完整电子下载包的共用提取器：一次运行读取带隙网格 XML，并同时读取 `mass/data-file-schema.xml`、`bands-cg/data-file-schema.xml` 和 `bands-cg/atomic_proj.xml`，生成带隙、纵向质量及胖带数据；包内的局部三维 XML 存在时也会提取该网格。因此运行它时保留整包目录及这些跨页面数据。上面的提示词描述本页性质的分析逻辑，复用现有共用脚本时还需满足这组文件依赖。只重画已有 CSV/JSON 时，直接执行 `python3 plot_si.py fatband`。

解压本页示例包后，在 `si-pbe` 根目录执行：

```bash
python3 -m pip install numpy matplotlib
python3 analyse_electronic.py
python3 plot_si.py fatband
```

```text
[preston@preston-System-Product-Name si-pbe]$ python3 plot_si.py fatband
<工作目录>/si-pbe/plots/fatband.png
```

![Si 的逐 k 逐带 s 和 p 权重胖带图](/Atlas/examples/si-pbe-electronic/plots/fatband.png)

两幅图使用同一路径和参考 `E−6.397028957255 eV`。节点索引仍为 `1、25、37、49、73、97、121`，横轴是实际坐标的累计距离，而非等距 k 点编号；节点和长度见[普通能带页](/Atlas/m/bands/qe/)。

蓝色点面积正比于 s 权重，橙色点面积正比于 p 权重，灰色细线保留本征能带。两个面板必须使用相同面积标度，不能各自把最强点归一化到一样大。`scatter(..., s=...)` 的 s 是面积，权重翻倍意味着面积翻倍、半径仅增为 √2 倍，不能凭直径直接读权重。

Γ 点最深价带几乎完全投到 s，权重约 0.9960；价带顶三条带主要投到 p，各约 0.9604。沿路径移动，点面积随轨道混合变化。简并处单条分支的分量可能依赖该子空间的基选择，读它们合计的 s/p 性质更稳妥。

还有一个明确的弱投影点：K→Γ 段第 53 个 k 点 `(0.625,0.625,0)×2π/a`，第 7 条带位于 `E−VBM=6.224118 eV`；s 为 `0.0168803`，p 为 `0.0446863`，合计仅 `0.0615665`。灰色能带仍存在，两个面板的点却都小，表示所选 s/p 空间对该空态覆盖很少。剩余约 94% 属于这组 s/p 投影未覆盖的分量；具体轨道归属需要相应的投影基。

完整 CSV 的原始投影和为 `0.06157–0.99705`，保留了不同态在所选投影空间中的覆盖程度。

这张图展示了固定 Si 晶胞、PBE、无 SOC 模型下的轨道组成。要分原子、分层或画 d 轨道，可以沿用相同的逐态合并方式，先根据本次 `Atomic states used for projection` 建立分组。所需轨道须实际出现在赝势投影态表中。

## 二维异质结 ZrCl₂/Sc₂C：从 `fatbands.projwfc_up` 提取四通道轨道胖带

除了读取 `atomic_proj.xml` 外，当 `projwfc.x` 输入设置 `filproj = 'fatbands'` 时，QE 会写出文本格式的逐轨道投影文件 `fatbands.projwfc_up`。文件前部列出全部正交化原子波函数的编号、原子序号、元素符号与 `(n, l, m)` 量子数，每个轨道块随后按 `(ik, iband)` 顺序逐行给出投影权重 `|c_j(n,k)|²`。

在 **`ZrCl₂/Sc₂C`**（[完整计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中，`scf/fatbands.projwfc_up` 包含 **`45` 个正交化原子轨道、`151` 个路径 k 点与 `31` 条能带**。绘图脚本 [`plot_zrcl2_sc2c.py`](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py) 将相关轨道按元素与角动量合并为四个通道：
- `Zr-4d`（状态 `#9–13`）、`Sc-3d`（状态 `#31–35` 与 `#41–45`）；
- `C-2p`（状态 `#15–17`）、`Cl-3p`（状态 `#19–21` 与 `#23–25`）。

[电子结构三联图的完整绘图源码](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py)保留逐态投影、PDOS 归并及 BXSF 读取规则。

为避免四个轨道通道在同一能带骨架上互相遮挡，子图 **a** 用空心圆（`facecolors='none'`，仅绘制 `w > 0.04` 的显著权重）编码各通道权重，并与子图 **b** 的水平 PDOS 及子图 **c** 的二维六角费米面并排展示：

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png" alt="ZrCl₂/Sc₂C 的四通道空心圆轨道投影胖带（Zr-4d、Sc-3d、C-2p、Cl-3p）、水平 PDOS 与二维费米面" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 的电子结构三联图：(a) 由 <code>scf/fatbands.projwfc_up</code>（45 个轨道、151 个 k 点、31 条能带）提取的 <code>Zr-4d</code>、<code>Sc-3d</code>、<code>C-2p</code> 与 <code>Cl-3p</code> 空心圆轨道胖带；(b) 共享能量纵轴的水平 PDOS；(c) 二维六角第一布里渊区费米面。</figcaption></figure>

## 在费米交点读取同一个态的层来源

图中不同颜色的圆环可能相互覆盖，不能凭最大外圈直接决定整条带的归属。从实际 `.gnu` 中找相邻点夹住 E_F=0.3133 eV 的区间，再以相同插值系数读取这两个点的投影，得到下面六个交点的近似权重。交点位置受路径采样与 `.gnu` 的文本精度影响；它们是路径读数，不是全区积分。

| 历史路径带号 | 插值交点所在 k 点区间 | Zr-d | Sc-d | C-p | Cl-p | 全部 45 投影之和 |
|---|---|---:|---:|---:|---:|---:|
| 26 | 84–85 | 0.1709 | 0.7108 | 0.0085 | 0.0304 | 0.9458 |
| 26 | 115–116 | 0.2192 | 0.6259 | 0.0096 | 0.0344 | 0.9522 |
| 27 | 17–18 | 0.6878 | 0.0963 | 0.0113 | 0.0957 | 0.9612 |
| 27 | 20–21 | 0.5748 | 0.1747 | 0.0187 | 0.0800 | 0.9602 |
| 27 | 130–131 | 0.2517 | 0.2873 | 0.0576 | 0.0415 | 0.9421 |
| 27 | 138–139 | 0.7494 | 0.0657 | 0.0064 | 0.1020 | 0.9640 |

第 26 带两个交点的 Sc-d 权重均显著高于 Zr-d，支持这些路径交点主要由 Sc 层 d 态贡献；第 27 带多个交点以 Zr-d 较大，但 130–131 区间的 Zr-d 与 Sc-d 接近，不能给整条第 27 带贴一个单层标签。Zr-d 与 Sc-d 在同一态上均非零，体现跨层共同权重；要确认接触造成的杂化强弱，还应比较相同几何的孤立层分支和反交叉附近的权重交换。

最后一列对全部 45 个原子轨道求和，前四列只含选定 d/p 通道，因此两者之差仍包含未列出的 s/p 等原子轨道。全部投影之和以外的余量也没有被标成间隙电子。点面积的显示阈值 0.04 只影响图，不影响这张表或下载的原始权重。

[六个交点及全精度 CSV](/Atlas/examples/research-scope-electronic/results/path-crossings.csv)由 [near_fermi.py](/Atlas/examples/research-scope-electronic/near_fermi.py)逐轨道读取。完整源码、数据格式与实际运行命令见[DOS 的窗口后处理](/Atlas/m/dos/qe/#h-从长表提取费米点与窗口谱重)。脚本同时核对 45×151×31 个投影、元素/原子编号与原始 k/带顺序；不按图像反推数据。


## 分层共同权重与间隙态的判别

[SnSe₂/PtTe₂ 原文 Fig. 1(c,f,i)](https://arxiv.org/pdf/2502.13690v1)将层投影写到界面每条能带上，区分层来源与混合态。PDOS 在同一能量重叠还没有 k 分辨信息；这里的交点表直接保留同一个 (k,n) 上的原始权重，不强行把四组通道加到一。

[Ba₂N 原文 Fig. 2(a–d)](https://doi.org/10.1103/PhysRevB.105.165101)将原子态、空球 X 与 ELF 共同使用。原子轨道之外的未覆盖投影可能含离域成分，也可能反映基组覆盖不足。要识别间隙电子，应在对应 k/带或能窗内读取空间密度，并核对 ELF 中的无核局域区域；不是给投影余量换一个名称。

讨论杂化时，沿同一支能带追踪两层权重怎样交换，再观察接触前后是否出现反交叉。简并点比较整个子空间，带号排序本身不保证分支身份。本文历史路径已经提供共同层权重；冻结单层对照只提供能量积分谱形，尚不构成逐 k 的接触前后反交叉对照。

若要把共同权重进一步落到特定原子对的成键/反键贡献，才选择 COHP；层间电荷重排则接[差分电荷](/Atlas/m/delta-charge/)。

```text
SCF 密度 → 路径能带与波函数 → projwfc.x 逐态投影
                                  ↓
                      对照轨道编号、k 点和本征值
                                  ↓
                       (k, band, energy, weights)
                                  ↓
                          同标度的 s / p 胖带
```
