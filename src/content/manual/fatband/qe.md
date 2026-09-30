普通能带告诉我们某个 k 点上有哪些能级；胖带再把这些态的轨道投影画成点的大小或带线的粗细。这次沿 Si 的 Γ–X–W–K–Γ–L–X 路径计算 121 个 k 点，每点保留 8 条能带，再分别画两个原子合计的 s 和 p 权重。横轴始终是这条路径中的位置。

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

`ngauss=0`、`degauss=0.01 Ry` 和 `DeltaE=0.02 eV` 管理同时写出的 Gaussian 展宽数据；前者的宽度约为 0.1361 eV，后者是能量步长。本页胖带直接读取每个波函数的投影幅度，不用这组展宽生成点的大小。这里只选择 Si 的 s、p 两组，是因为实际赝势给出了这些投影态。路径上的点和权重也不是均匀布里渊区积分，因此同时产生的 PDOS 文件不在本页作为总 DOS 使用。

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

## 把后处理要求写成提示词

上面的单位、点序和能量参考可以整理成下面的编码要求，与示例文件一起交给代码助手：

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

<details>
<summary>plot_zrcl2_sc2c.py 的完整源码</summary>

```python
#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import numpy as np

ZR_DIR = Path(__file__).resolve().parent
for candidate in (ZR_DIR, ZR_DIR.parent, ZR_DIR.parents[1] / 'scripts'):
    if (candidate / 'atlas_plot_style.py').exists():
        sys.path.insert(0, str(candidate))
        break

import atlas_plot_style

sys.path.insert(0, str(ZR_DIR))
from tc_table_audit import piecewise_linear_crossings, write_report

PALETTE = {
    'Ink': '#162232',
    'Slate': '#324255',
    'Muted': '#5a6b80',
    'Navy': '#0072b2',
    'Blue': '#2968a8',
    'SoftBlue': '#d6e6f4',
    'Teal': '#009e73',
    'SoftTeal': '#d7ece8',
    'Amber': '#e69f00',
    'Rust': '#d55e00',
    'Coral': '#cc79a7',
    'WarmTint': '#f4efe6',
}

CM1_TO_THZ = 1.0 / 33.3564095198152
FIG_OUT_DIR = (
    ZR_DIR.parents[1] / 'figures' / 'zrcl2-sc2c'
    if (ZR_DIR.parents[1] / 'figures').exists()
    else ZR_DIR / 'figures'
)


def apply_atlas_style() -> None:
    atlas_plot_style.install()


def style_axis(ax) -> None:
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def save_figure(fig, stem_name: str) -> None:
    FIG_OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_OUT_DIR / f'{stem_name}.png')
    plt.close(fig)


def parse_zrcl2_fatbands() -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133  # eV from scf/pwx.out
    data_dir = ZR_DIR / 'scf'
    gnu_path = data_dir / 'bands.dat.gnu'
    proj_path = data_dir / 'fatbands.projwfc_up'
    proj_lines = [line for line in proj_path.read_text().splitlines() if line.strip()]
    header_rows = [
        idx for idx, line in enumerate(proj_lines[:30])
        if len(line.split()) == 3 and all(part.isdigit() for part in line.split())
    ]
    if len(header_rows) != 1:
        raise ValueError(f'Expected one projection header; found {len(header_rows)}.')
    header_idx = header_rows[0]
    natomwfc, nk, nbnd = map(int, proj_lines[header_idx].split())
    if header_idx + 2 >= len(proj_lines):
        raise ValueError('Projection header is missing its spin flags or first state.')
    spin_flags = proj_lines[header_idx + 1].split()
    if len(spin_flags) != 2 or any(flag not in {'T', 'F'} for flag in spin_flags):
        raise ValueError(f'Unexpected projection spin flags: {spin_flags}')
    ptr = header_idx + 2

    raw = np.loadtxt(gnu_path)
    if raw.shape != (nbnd * nk, 2) or not np.isfinite(raw).all():
        raise ValueError(f'Unexpected bands.dat.gnu shape or nonfinite values: {raw.shape}')
    band_blocks = raw.reshape(nbnd, nk, 2)
    k_blocks = band_blocks[:, :, 0]
    if not np.allclose(k_blocks, k_blocks[0:1], rtol=0.0, atol=1e-8):
        raise ValueError('The k-distance sequence differs between band blocks.')
    k_dist = k_blocks[0]
    if not np.isclose(k_dist[0], 0.0, rtol=0.0, atol=1e-8):
        raise ValueError(f'Band path does not start at zero: {k_dist[0]}')
    if np.any(np.diff(k_dist) < -1e-8) or k_dist[-1] <= k_dist[0]:
        raise ValueError('Band path distances are not a forward, nonzero path.')
    bands_e = band_blocks[:, :, 1] - ef

    atom_elements = {1: 'Zr', 2: 'C', 3: 'Cl', 4: 'Cl', 5: 'Sc', 6: 'Sc'}
    group_by_site_orbital = {
        (1, 'D'): 'Zr-4d',
        (5, 'D'): 'Sc-3d',
        (6, 'D'): 'Sc-3d',
        (2, 'P'): 'C-2p',
        (3, 'P'): 'Cl-3p',
        (4, 'P'): 'Cl-3p',
    }
    expected_state_counts = {'Zr-4d': 5, 'Sc-3d': 10, 'C-2p': 3, 'Cl-3p': 6}
    grouped = {key: np.zeros((nbnd, nk)) for key in expected_state_counts}
    state_counts = {key: 0 for key in expected_state_counts}
    expected_ik = np.repeat(np.arange(1, nk + 1), nbnd)
    expected_ib = np.tile(np.arange(1, nbnd + 1), nk)
    block_len = nk * nbnd
    seen_state_ids = set()

    for expected_state in range(1, natomwfc + 1):
        if ptr >= len(proj_lines):
            raise ValueError(f'Projection file ended before state {expected_state}.')
        hdr = proj_lines[ptr].split()
        if len(hdr) < 4:
            raise ValueError(f'Malformed state header at line {ptr + 1}: {hdr}')
        state_id, atom_id = int(hdr[0]), int(hdr[1])
        element, orbital = hdr[2], hdr[3].upper()
        if state_id != expected_state or state_id in seen_state_ids:
            raise ValueError(f'Unexpected or duplicate state id {state_id}; expected {expected_state}.')
        seen_state_ids.add(state_id)
        if atom_id not in atom_elements or element != atom_elements[atom_id]:
            raise ValueError(f'State {state_id} has atom/element mismatch: #{atom_id} {element}.')
        angular_parts = [char for char in orbital if char in 'SPDF']
        if len(angular_parts) != 1:
            raise ValueError(f'State {state_id} has unrecognized orbital label {orbital}.')
        key = group_by_site_orbital.get((atom_id, angular_parts[0]))
        ptr += 1
        rows = []
        for row_index in range(block_len):
            if ptr >= len(proj_lines):
                raise ValueError(f'State {state_id} ended at projection row {row_index}.')
            fields = proj_lines[ptr].split()
            if len(fields) != 3:
                raise ValueError(f'Malformed projection row at line {ptr + 1}: {fields}')
            rows.append((int(fields[0]), int(fields[1]), float(fields[2])))
            ptr += 1
        state_data = np.asarray(rows, dtype=float)
        if not np.array_equal(state_data[:, 0].astype(int), expected_ik):
            raise ValueError(f'State {state_id} has an unexpected k-index sequence.')
        if not np.array_equal(state_data[:, 1].astype(int), expected_ib):
            raise ValueError(f'State {state_id} has an unexpected band-index sequence.')
        state_weights = state_data[:, 2]
        if not np.isfinite(state_weights).all():
            raise ValueError(f'State {state_id} contains nonfinite projection weights.')
        if key is not None:
            grouped[key] += state_weights.reshape(nk, nbnd).T
            state_counts[key] += 1

    if ptr != len(proj_lines) or len(seen_state_ids) != natomwfc:
        raise ValueError(f'Projection records do not close cleanly: consumed {ptr}/{len(proj_lines)} lines.')
    if state_counts != expected_state_counts:
        raise ValueError(f'Unexpected selected state counts: {state_counts}')
    if any(not np.isfinite(curve).all() for curve in grouped.values()):
        raise ValueError('Grouped projection weights contain nonfinite values.')
    return k_dist, bands_e, grouped

def parse_zrcl2_pdos() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133
    pdos_dir = ZR_DIR / 'pdos'

    def read_ldos(filename: str) -> tuple[np.ndarray, np.ndarray]:
        arr = np.loadtxt(pdos_dir / filename, comments='#')
        return arr[:, 0] - ef, arr[:, 1]

    e_grid, zr_4d = read_ldos('zrclscc.pdos_atm#1(Zr)_wfc#5(d)')
    _, c_2p = read_ldos('zrclscc.pdos_atm#2(C)_wfc#2(p)')
    _, cl1_3p = read_ldos('zrclscc.pdos_atm#3(Cl)_wfc#2(p)')
    _, cl2_3p = read_ldos('zrclscc.pdos_atm#4(Cl)_wfc#2(p)')
    _, sc1_3d = read_ldos('zrclscc.pdos_atm#5(Sc)_wfc#4(d)')
    _, sc2_3d = read_ldos('zrclscc.pdos_atm#6(Sc)_wfc#4(d)')
    tot_arr = np.loadtxt(pdos_dir / 'zrclscc.pdos_tot', comments='#')

    return e_grid, {
        'Total': tot_arr[:, 1],
        'Zr-4d': zr_4d,
        'Sc-3d': sc1_3d + sc2_3d,
        'C-2p': c_2p,
        'Cl-3p': cl1_3p + cl2_3p,
    }


def parse_zrcl2_bxsf() -> tuple[float, np.ndarray, np.ndarray, dict[int, np.ndarray]]:
    bxsf_path = ZR_DIR / 'FS' / 'zrclscc_fs.bxsf'
    lines = [l.strip() for l in bxsf_path.read_text().splitlines() if l.strip()]
    ef = 0.3154
    for l in lines[:20]:
        if 'Fermi Energy:' in l:
            ef = float(l.split(':')[1].strip())
            break

    b_idx = [i for i, l in enumerate(lines) if l.startswith('BEGIN_BANDGRID_3D')][0]
    nx, ny, nz = [int(x) for x in lines[b_idx + 2].split()]
    b1 = np.array([float(x) for x in lines[b_idx + 4].split()[:2]])
    b2 = np.array([float(x) for x in lines[b_idx + 5].split()[:2]])

    bands: dict[int, np.ndarray] = {}
    ptr = b_idx + 7
    while ptr < len(lines):
        line = lines[ptr]
        if line.startswith('BAND:'):
            b_num = int(line.split(':')[1].strip())
            ptr += 1
            vals: list[float] = []
            while ptr < len(lines) and not lines[ptr].startswith('BAND:') and not lines[ptr].startswith('END_BANDGRID_3D'):
                vals.extend([float(x) for x in lines[ptr].split()])
                ptr += 1
            arr3d = np.array(vals).reshape((nx, ny, nz))
            bands[b_num] = arr3d[:, :, 0] - ef
        else:
            ptr += 1

    return ef, b1, b2, bands


def render_zrcl2_sc2c_electronic() -> None:
    apply_atlas_style()
    k_dist, bands_e, grouped_w = parse_zrcl2_fatbands()
    e_dos, pdos = parse_zrcl2_pdos()
    _, b1, b2, fs_bands = parse_zrcl2_bxsf()

    fig = plt.figure(figsize=(10.2, 4.35))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.985, bottom=0.17, top=0.85,
        width_ratios=[1.35, 0.72, 1.15], wspace=0.22
    )
    ax_band = fig.add_subplot(gs[0, 0])
    ax_dos = fig.add_subplot(gs[0, 1], sharey=ax_band)
    ax_fs = fig.add_subplot(gs[0, 2])

    for ax in (ax_band, ax_dos, ax_fs):
        style_axis(ax)

    k_ticks = [k_dist[0], k_dist[50], k_dist[100], k_dist[150]]
    for x in k_ticks[1:-1]:
        ax_band.axvline(x, color='#ced8e3', lw=0.85, zorder=1)
    ax_band.axhline(0.0, color=PALETTE['Muted'], ls='--', lw=0.95, zorder=2)
    ax_band.axhspan(-0.16, 0.16, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)

    for ib in range(bands_e.shape[0]):
        e_curve = bands_e[ib]
        if e_curve.max() < -2.7 or e_curve.min() > 2.2:
            continue
        ax_band.plot(k_dist, e_curve, color='#7d8b9d', lw=0.85, alpha=0.75, zorder=2)

    orb_specs = [
        ('Cl-3p', PALETTE['Amber'], 72.0),
        ('C-2p', PALETTE['Rust'], 85.0),
        ('Sc-3d', PALETTE['Teal'], 92.0),
        ('Zr-4d', PALETTE['Navy'], 96.0),
    ]
    for label, color, scale in orb_specs:
        w_mat = grouped_w[label]
        for ib in range(bands_e.shape[0]):
            e_curve = bands_e[ib]
            if e_curve.max() < -2.6 or e_curve.min() > 2.1:
                continue
            w = w_mat[ib]
            mask = w > 0.04
            if np.any(mask):
                ax_band.scatter(
                    k_dist[mask],
                    e_curve[mask],
                    s=w[mask] * scale,
                    facecolors='none',
                    edgecolors=color,
                    linewidths=0.95,
                    alpha=0.88,
                    zorder=4,
                )

    ax_band.set_xlim(k_ticks[0], k_ticks[-1])
    ax_band.set_ylim(-2.5, 2.0)
    ax_band.set_xticks(k_ticks, [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$'])
    ax_band.set_ylabel(r'Energy $E - E_F$ (eV)')
    ax_band.set_title('Orbital fatbands', pad=8)

    legend_handles = [
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Navy'], markeredgewidth=1.3, markersize=5.2, label=r'Zr-$4d$ [#1]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Teal'], markeredgewidth=1.3, markersize=5.2, label=r'Sc-$3d$ [#5+#6]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Rust'], markeredgewidth=1.3, markersize=5.2, label=r'C-$2p$ [#2]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Amber'], markeredgewidth=1.3, markersize=5.2, label=r'Cl-$3p$ [#3+#4]'),
    ]
    ax_band.legend(handles=legend_handles, loc='lower left', ncol=2, fontsize=8.0)

    ax_band.annotate(
        'Bands 26, 27\n(Zr-$4d$ [#1] / Sc-$3d$ [#5+#6])',
        xy=(k_dist[24], 0.04),
        xytext=(k_dist[8], 0.92),
        fontsize=8.0, zorder=10,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.8),
    )

    mask_dos = (e_dos >= -2.6) & (e_dos <= 2.1)
    ed = e_dos[mask_dos]
    ax_dos.axhline(0.0, color=PALETTE['Muted'], ls='--', lw=0.95, zorder=2)
    ax_dos.axhspan(-0.16, 0.16, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)

    ax_dos.fill_betweenx(ed, 0, pdos['Total'][mask_dos], color='#dfe6ef', alpha=0.55)
    ax_dos.plot(pdos['Total'][mask_dos], ed, color=PALETTE['Ink'], lw=1.05, label='Total')
    ax_dos.plot(pdos['Zr-4d'][mask_dos], ed, color=PALETTE['Navy'], lw=1.1, label=r'Zr-$4d$ [#1]')
    ax_dos.plot(pdos['Sc-3d'][mask_dos], ed, color=PALETTE['Teal'], lw=1.1, label=r'Sc-$3d$ [#5+#6]')
    ax_dos.plot(pdos['C-2p'][mask_dos], ed, color=PALETTE['Rust'], lw=1.05, label=r'C-$2p$ [#2]')
    ax_dos.plot(pdos['Cl-3p'][mask_dos], ed, color=PALETTE['Amber'], lw=0.95, label=r'Cl-$3p$ [#3+#4]')

    ax_dos.set_xlim(0, 6.8)
    ax_dos.set_xticks([0, 3, 6])
    ax_dos.set_xlabel('PDOS (eV$^{-1}$)')
    ax_dos.set_title('PDOS', pad=8)
    ax_dos.tick_params(labelleft=False)

    B = np.column_stack([b1, b2])
    B_inv = np.linalg.inv(B)
    angles = np.deg2rad(np.arange(0, 360, 60))
    R_k = 2.0 / 3.0
    bz_verts = np.column_stack([R_k * np.cos(angles), R_k * np.sin(angles)])

    nx = 220
    kx_lin = np.linspace(-0.75, 0.75, nx)
    ky_lin = np.linspace(-0.75, 0.75, nx)
    KX, KY = np.meshgrid(kx_lin, ky_lin)
    uv = B_inv @ np.vstack([KX.ravel(), KY.ravel()])
    u_mod = np.mod(uv[0], 1.0) * 64.0
    v_mod = np.mod(uv[1], 1.0) * 64.0

    def interp_periodic(grid65: np.ndarray) -> np.ndarray:
        i0 = np.floor(u_mod).astype(int) % 64
        j0 = np.floor(v_mod).astype(int) % 64
        i1 = (i0 + 1) % 64
        j1 = (j0 + 1) % 64
        du = u_mod - np.floor(u_mod)
        dv = v_mod - np.floor(v_mod)
        val = (
            (1 - du) * (1 - dv) * grid65[i0, j0]
            + du * (1 - dv) * grid65[i1, j0]
            + (1 - du) * dv * grid65[i0, j1]
            + du * dv * grid65[i1, j1]
        )
        return val.reshape(KX.shape)

    E26 = interp_periodic(fs_bands[26])
    E27 = interp_periodic(fs_bands[27])

    m_angles = np.deg2rad([30.0, 90.0, 150.0])
    inside_bz = np.ones_like(KX, dtype=bool)
    for ang in m_angles:
        inside_bz &= np.abs(KX * np.cos(ang) + KY * np.sin(ang)) <= (1.0 / np.sqrt(3.0) + 0.004)

    E26_masked = np.where(inside_bz, E26, np.nan)
    E27_masked = np.where(inside_bz, E27, np.nan)

    ax_fs.contourf(
        KX, KY, E26_masked,
        levels=np.linspace(-0.6, 0.4, 22),
        cmap='Blues_r', alpha=0.25, zorder=1,
    )
    ax_fs.contour(KX, KY, E26_masked, levels=[0.0], colors=[PALETTE['Navy']], linewidths=1.85, zorder=4)
    ax_fs.contour(KX, KY, E27_masked, levels=[0.0], colors=[PALETTE['Rust']], linewidths=1.85, zorder=5)

    bz_poly = Polygon(bz_verts, closed=True, fill=False, edgecolor=PALETTE['Ink'], lw=1.2, zorder=6)
    ax_fs.add_patch(bz_poly)

    gamma_pt = np.array([0.0, 0.0])
    m_pt = np.array([0.5, 1.0 / (2.0 * np.sqrt(3.0))])
    k_pt = np.array([1.0 / 3.0, 1.0 / np.sqrt(3.0)])
    path_pts = np.vstack([gamma_pt, m_pt, k_pt, gamma_pt])
    ax_fs.plot(path_pts[:, 0], path_pts[:, 1], color=PALETTE['Slate'], ls='--', lw=0.95, zorder=6)
    ax_fs.scatter([gamma_pt[0], m_pt[0], k_pt[0]], [gamma_pt[1], m_pt[1], k_pt[1]], color=PALETTE['Ink'], s=16, zorder=7)
    ax_fs.text(-0.07, -0.08, r'$\Gamma$', fontsize=8.5, fontweight='bold')
    ax_fs.text(m_pt[0] + 0.03, m_pt[1] - 0.02, r'$M$', fontsize=8.5, fontweight='bold')
    ax_fs.text(k_pt[0] + 0.02, k_pt[1] + 0.03, r'$K$', fontsize=8.5, fontweight='bold')

    fs_handles = [
        Line2D([0], [0], color=PALETTE['Navy'], lw=1.8, label='Band 26'),
        Line2D([0], [0], color=PALETTE['Rust'], lw=1.8, label='Band 27'),
    ]
    ax_fs.legend(handles=fs_handles, loc='lower center', ncol=2, fontsize=8.0)
    ax_fs.set_aspect('equal')
    ax_fs.set_xlim(-0.74, 0.74)
    ax_fs.set_ylim(-0.74, 0.74)
    ax_fs.set_xticks([-0.5, 0.0, 0.5])
    ax_fs.set_yticks([-0.5, 0.0, 0.5])
    ax_fs.set_xlabel(r'$k_x$ ($2\pi/a$)')
    ax_fs.set_ylabel(r'$k_y$ ($2\pi/a$)')
    ax_fs.set_title('2D Fermi surface', pad=8)

    save_figure(fig, 'zrcl2-sc2c-electronic')


def parse_gam_lines(filepath: Path, target_broadening: float = 0.0030) -> np.ndarray:
    text = filepath.read_text()
    blocks = re.split(r'Broadening\s+([\d.]+)', text)[1:]
    for i in range(0, len(blocks), 2):
        bval = float(blocks[i])
        if abs(bval - target_broadening) < 1e-5:
            lines = [l.strip() for l in blocks[i + 1].strip().splitlines() if l.strip()]
            gam = np.zeros((151, 18))
            ptr = 0
            for iq in range(151):
                ptr += 1
                vals = []
                while len(vals) < 18 and ptr < len(lines):
                    vals.extend([float(x) for x in lines[ptr].split()])
                    ptr += 1
                gam[iq] = np.maximum(0.0, np.array(vals[:18]) * 1000.0)
            return gam
    raise ValueError(f'Broadening {target_broadening} not found in {filepath}')


def render_zrcl2_sc2c_phonon_epc() -> None:
    apply_atlas_style()
    ph96_dir = ZR_DIR / 'ph96'
    freq_arr = np.loadtxt(ph96_dir / 'zrclscc.freq.gp')
    q_dist = freq_arr[:, 0]
    freqs_thz = freq_arr[:, 1:] * CM1_TO_THZ

    gam_qv = parse_gam_lines(ph96_dir / 'gam.lines', target_broadening=0.0030)
    ry_to_thz = 3289.84196
    nef_003 = 30.772452
    w_ry = np.maximum(freqs_thz, 0.25) / ry_to_thz
    g_ry = (gam_qv / 1000.0) / ry_to_thz
    lam_qv = np.where(freqs_thz > 0.25, g_ry / (np.pi * nef_003 * (w_ry ** 2)), 0.0)

    phdos_arr = np.loadtxt(ph96_dir / 'zrclscc.phdos', comments='#')
    w_dos_thz = phdos_arr[:, 0] * CM1_TO_THZ
    dos_scale = 33.3564095
    phdos_tot = phdos_arr[:, 1] * dos_scale
    phdos_zr = phdos_arr[:, 2] * dos_scale
    phdos_c = phdos_arr[:, 3] * dos_scale
    phdos_cl = (phdos_arr[:, 4] + phdos_arr[:, 5]) * dos_scale
    phdos_sc = (phdos_arr[:, 6] + phdos_arr[:, 7]) * dos_scale

    a2f_lines = (ph96_dir / 'alpha2F.dat').read_text().splitlines()[2:]
    e_a2f, a2f_003, a2f_001 = [], [], []
    for idx in range(0, len(a2f_lines), 2):
        r1 = [float(x) for x in a2f_lines[idx].split()]
        e_a2f.append(r1[0])
        a2f_001.append(max(0.0, r1[1]))
        a2f_003.append(max(0.0, r1[3]))
    e_a2f = np.array(e_a2f)
    a2f_003 = np.array(a2f_003)
    a2f_001 = np.array(a2f_001)

    de = e_a2f[1] - e_a2f[0]
    cum_lam_003 = np.zeros_like(e_a2f)
    cum_lam_003[1:] = np.cumsum(2.0 * a2f_003[1:] / e_a2f[1:] * de)

    fig = plt.figure(figsize=(10.2, 4.45))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.98, bottom=0.17, top=0.84,
        width_ratios=[1.42, 0.76, 1.02], wspace=0.12
    )
    ax_ph = fig.add_subplot(gs[0, 0])
    ax_pdos = fig.add_subplot(gs[0, 1], sharey=ax_ph)
    ax_a2f = fig.add_subplot(gs[0, 2], sharey=ax_ph)

    for ax in (ax_ph, ax_pdos, ax_a2f):
        style_axis(ax)
        ax.axhline(10.0, color=PALETTE['Coral'], ls='--', lw=1.05, zorder=3)
        ax.axhspan(12.2, 17.3, color=PALETTE['WarmTint'], alpha=0.55, zorder=0)

    q_ticks = [q_dist[0], q_dist[50], q_dist[100], q_dist[150]]
    for x in q_ticks[1:-1]:
        ax_ph.axvline(x, color='#ced8e3', lw=0.85, zorder=1)

    for nu in range(18):
        ax_ph.plot(q_dist, freqs_thz[:, nu], color='#4a5a70', lw=0.9, alpha=0.85, zorder=2)
        g_vals = gam_qv[:, nu]
        l_vals = lam_qv[:, nu]
        idx_sub = np.arange(0, 151, 3)
        sizes = np.clip(l_vals[idx_sub] * 26.0 + g_vals[idx_sub] * 0.14, 4.0, 95.0)
        ax_ph.scatter(
            q_dist[idx_sub],
            freqs_thz[idx_sub, nu],
            s=sizes,
            c=np.clip(g_vals[idx_sub], 0.0, 340.0),
            cmap='YlOrRd',
            vmin=0.0,
            vmax=330.0,
            edgecolors='#2b3a4d',
            linewidths=0.3,
            alpha=0.84,
            zorder=4,
        )

    ax_ph.set_xlim(q_ticks[0], q_ticks[-1])
    ax_ph.set_ylim(0.0, 18.0)
    ax_ph.set_xticks(q_ticks, [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$'])
    ax_ph.set_ylabel(r'Frequency $\omega$ (THz)')
    ax_ph.set_title(r'Fat-phonon $\gamma_{\mathbf{q}\nu}$ & $\lambda_{\mathbf{q}\nu}$', pad=8)

    ax_ph.annotate(
        r'C-atom optical modes ($\nu=16\text{–}18$): $\gamma_{\Gamma,17\text{–}18}\approx 322\ \mathrm{GHz}$',
        xy=(q_dist[8], 15.45),
        xytext=(q_dist[10], 11.20),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.95),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )
    ax_ph.text(
        q_dist[54], 9.05,
        'Saved input emax = 10 THz',
        fontsize=7.5,
        color=PALETTE['Coral'],
        fontweight='bold',
    )

    ax_pdos.fill_betweenx(w_dos_thz, 0, phdos_tot, color='#dfe6ef', alpha=0.55)
    ax_pdos.plot(phdos_tot, w_dos_thz, color=PALETTE['Ink'], lw=1.0, label='Total')
    ax_pdos.plot(phdos_zr, w_dos_thz, color=PALETTE['Navy'], lw=1.1, label='Zr')
    ax_pdos.plot(phdos_sc, w_dos_thz, color=PALETTE['Teal'], lw=1.1, label='Sc')
    ax_pdos.plot(phdos_cl, w_dos_thz, color=PALETTE['Amber'], lw=1.0, label='Cl')
    ax_pdos.plot(phdos_c, w_dos_thz, color=PALETTE['Rust'], lw=1.2, label='C')

    ax_pdos.set_xlim(0, 3.8)
    ax_pdos.set_xticks([0, 1.5, 3.0])
    ax_pdos.set_xlabel('PHDOS (THz$^{-1}$)')
    ax_pdos.set_title('PHDOS', pad=8)
    ax_pdos.tick_params(labelleft=False)
    ax_pdos.legend(loc='center right', fontsize=7.8)

    ax_a2f.fill_betweenx(e_a2f, 0, a2f_003, color=PALETTE['SoftBlue'], alpha=0.72)
    ax_a2f.plot(a2f_003, e_a2f, color=PALETTE['Navy'], lw=1.35, label=r'$\alpha^2F$ ($\sigma=0.003$)')
    ax_a2f.plot(a2f_001, e_a2f, color=PALETTE['Blue'], lw=0.85, ls=':', alpha=0.85, label=r'$\alpha^2F$ ($\sigma=0.001$)')
    lam_scale = 0.36
    ax_a2f.plot(cum_lam_003 * lam_scale, e_a2f, color=PALETTE['Rust'], lw=1.65, label=r'$0.36\times \lambda(\omega)$')

    ax_a2f.set_xlim(0, 1.05)
    ax_a2f.set_xticks([0.0, 0.4, 0.8])
    ax_a2f.set_xlabel(r'$\alpha^2F(\omega)$ & scaled $\lambda(\omega)$')
    ax_a2f.set_title(r'Saved $\alpha^2F(\omega)$ (emax = 10 THz)', pad=8)
    ax_a2f.tick_params(labelleft=False)

    ax_a2f.text(
        0.22, 13.3,
        'Input: 10 0.12 1\n18-THz output provenance open',
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
    )
    ax_a2f.legend(loc='center right', bbox_to_anchor=(1.0, 0.36), fontsize=7.6)

    save_figure(fig, 'zrcl2-sc2c-phonon-epc')


def load_zrcl2_lambda_series(tag: str, suffix: str = '') -> dict[str, np.ndarray]:
    base = ZR_DIR / tag
    dat_file = base / (f'lambda{suffix}.dat')
    out_file = base / (f'lambdax{suffix}.out')
    arr = np.loadtxt(dat_file, comments='#')
    lines = out_file.read_text().splitlines()
    tc_idx = [i for i, l in enumerate(lines) if 'omega_log' in l and 'T_c' in l][0] + 1
    tc_vals = [float(lines[tc_idx + i].split()[2]) for i in range(arr.shape[0])]
    return {
        'sigma': arr[:, 0],
        'lambda': arr[:, 1],
        'int_a2f': arr[:, 2],
        'wlog': arr[:, 3],
        'nef': arr[:, 4],
        'tc': np.array(tc_vals),
    }


def render_zrcl2_sc2c_k64_k96_tc() -> None:
    apply_atlas_style()
    p64_10 = load_zrcl2_lambda_series('ph64', '')
    p96_10 = load_zrcl2_lambda_series('ph96', '')
    p64_18 = load_zrcl2_lambda_series('ph64', '.emax18')
    p96_18 = load_zrcl2_lambda_series('ph96', '.emax18')
    sigma = p64_10['sigma']
    write_report(ZR_DIR)
    roots10 = piecewise_linear_crossings(sigma, p64_10['tc'], p96_10['tc'])
    roots18 = piecewise_linear_crossings(sigma, p64_18['tc'], p96_18['tc'])

    fig, (ax_tc, ax_diff) = plt.subplots(1, 2, figsize=(10.0, 4.35))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.18, top=0.85, wspace=0.28)
    style_axis(ax_tc)
    style_axis(ax_diff)

    for ax in (ax_tc, ax_diff):
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.72, zorder=0)
        ax.set_xticks([0.005, 0.010, 0.015, 0.020])

    ax_tc.plot(sigma, p64_18['tc'], color=PALETTE['Navy'], marker='o', ms=3.8, lw=1.6, label=r'$64^2$ stored 18-THz table (source open)')
    ax_tc.plot(sigma, p96_18['tc'], color=PALETTE['Rust'], marker='s', ms=3.6, lw=1.6, label=r'$96^2$ stored 18-THz table (source open)')
    ax_tc.plot(sigma, p64_10['tc'], color=PALETTE['Navy'], ls='--', lw=1.05, alpha=0.7, label=r'$64^2$ matched 10-THz input')
    ax_tc.plot(sigma, p96_10['tc'], color=PALETTE['Rust'], ls='--', lw=1.05, alpha=0.7, label=r'$96^2$ matched 10-THz input')

    for i, root in enumerate(roots10):
        ax_tc.scatter([root['sigma_ry']], [root['tc_k']], marker='^', s=42, color=PALETTE['Amber'], zorder=6, label='10-THz table roots' if i == 0 else None)
    for i, root in enumerate(roots18):
        ax_tc.scatter([root['sigma_ry']], [root['tc_k']], s=58, facecolors='none', edgecolors=PALETTE['Teal'], linewidths=1.8, zorder=7, label='18-THz stored-table root (source open)' if i == 0 else None)
    if roots18:
        root = roots18[0]
        ax_tc.annotate(
            f"Stored 18-THz table\n$\\sigma={root['sigma_ry']:.6f}$ Ry, $T_c={root['tc_k']:.3f}$ K\ninput/run record unlinked",
            xy=(root['sigma_ry'], root['tc_k']),
            xytext=(0.0062, 11.6),
            fontsize=7.7,
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
            arrowprops=dict(arrowstyle='->', color=PALETTE['Teal'], lw=0.95),
        )

    ax_tc.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_tc.set_ylabel(r'Stored Allen–Dynes $T_c(\sigma)$ (K)')
    ax_tc.set_title(r'Stored $T_c$ tables and interpolated roots', pad=8)
    ax_tc.legend(loc='upper right', fontsize=7.4)

    dtc_18 = p64_18['tc'] - p96_18['tc']
    dtc_10 = p64_10['tc'] - p96_10['tc']
    ax_diff.axhline(0.0, color=PALETTE['Ink'], ls='-', lw=0.95, zorder=2)
    ax_diff.plot(sigma, dtc_18, color=PALETTE['Teal'], marker='o', ms=3.8, lw=1.6, label=r'$\Delta T_c$ (18-THz stored tables)')
    ax_diff.plot(sigma, dtc_10, color=PALETTE['Amber'], marker='^', ms=3.6, lw=1.35, ls='--', label=r'$\Delta T_c$ (matched 10-THz inputs)')
    for root in roots10:
        ax_diff.scatter([root['sigma_ry']], [0.0], marker='^', color=PALETTE['Amber'], s=42, zorder=6)
    for root in roots18:
        ax_diff.scatter([root['sigma_ry']], [0.0], color=PALETTE['Teal'], s=48, zorder=7)
    ax_diff.text(
        0.035, 0.055,
        'Prepared ph64.1/ph96.1\nrefinement has no complete Tc pair',
        transform=ax_diff.transAxes,
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
    )

    ax_diff.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_diff.set_ylabel(r'$\Delta T_c(\sigma) = T_{c,64} - T_{c,96}$ (K)')
    ax_diff.set_title(r'Linear-interpolation roots of $\Delta T_c=0$', pad=8)
    ax_diff.set_ylim(-0.135, 0.155)
    ax_diff.legend(loc='upper right', fontsize=7.4)

    save_figure(fig, 'zrcl2-sc2c-k64-k96-tc')


def render_zrcl2_sc2c_k64_k96_moments() -> None:
    apply_atlas_style()
    p64 = load_zrcl2_lambda_series('ph64', '')
    p96 = load_zrcl2_lambda_series('ph96', '')
    sigma = p64['sigma']

    fig, (ax_nef, ax_lam, ax_wlog) = plt.subplots(1, 3, figsize=(10.4, 4.15))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.18, top=0.85, wspace=0.31)
    for ax in (ax_nef, ax_lam, ax_wlog):
        style_axis(ax)
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)
        ax.set_xticks([0.005, 0.012, 0.020])

    ax_nef.plot(sigma, p64['nef'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64\times 64\times 1$')
    ax_nef.plot(sigma, p96['nef'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96\times 96\times 1$')
    ax_nef.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_nef.set_ylabel(r'$N_\sigma(E_F)$ (states/spin/Ry)')
    ax_nef.set_title(r'$N_\sigma(E_F)$ from stored tables', pad=8)
    ax_nef.legend(loc='upper right', fontsize=7.6)
    ax_nef.annotate(
        'Close for $\\sigma\\geq0.004$ Ry\n(two grids; no convergence proof)',
        xy=(0.004, p64['nef'][3]),
        xytext=(0.0075, 28.5),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.85),
    )

    ax_lam.plot(sigma, p64['lambda'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ direct $\lambda$')
    ax_lam.plot(sigma, p96['lambda'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ direct $\lambda$')
    ax_lam.plot(sigma, p64['int_a2f'], color=PALETTE['Navy'], ls='--', lw=1.1, alpha=0.75, label=r'$64^2$ $\int\alpha^2F$ (10 THz)')
    ax_lam.plot(sigma, p96['int_a2f'], color=PALETTE['Rust'], ls='--', lw=1.1, alpha=0.75, label=r'$96^2$ $\int\alpha^2F$ (10 THz)')
    ax_lam.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_lam.set_ylabel(r'Coupling $\lambda(\sigma)$')
    ax_lam.set_title(r'10-THz input: $\lambda$ and $\int\alpha^2F$', pad=8)
    ax_lam.legend(loc='upper right', fontsize=7.2)

    ax_wlog.plot(sigma, p64['wlog'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ (10-THz input)')
    ax_wlog.plot(sigma, p96['wlog'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ (10-THz input)')
    ax_wlog.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_wlog.set_ylabel(r'$\omega_{\log}(\sigma)$ (K)')
    ax_wlog.set_title(r'Stored $\omega_{\log}$ (10-THz input)', pad=8)
    ax_wlog.legend(loc='upper left', fontsize=7.2)
    ax_wlog.text(
        0.04, 0.04,
        'Frequency grid ends at 10 THz',
        transform=ax_wlog.transAxes,
        fontsize=7.3,
        color=PALETTE['Muted'],
    )

    save_figure(fig, 'zrcl2-sc2c-k64-k96-moments')


if __name__ == '__main__':
    render_zrcl2_sc2c_electronic()
    render_zrcl2_sc2c_phonon_epc()
    render_zrcl2_sc2c_k64_k96_tc()
    render_zrcl2_sc2c_k64_k96_moments()
```

</details>

为避免四个轨道通道在同一能带骨架上互相遮挡，子图 **a** 用空心圆（`facecolors='none'`，仅绘制 `w > 0.04` 的显著权重）编码各通道权重，并与子图 **b** 的水平 PDOS 及子图 **c** 的二维六角费米面并排展示：

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png" alt="ZrCl₂/Sc₂C 的四通道空心圆轨道投影胖带（Zr-4d、Sc-3d、C-2p、Cl-3p）、水平 PDOS 与二维费米面" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 的电子结构三联图：(a) 由 <code>scf/fatbands.projwfc_up</code>（45 个轨道、151 个 k 点、31 条能带）提取的 <code>Zr-4d</code>、<code>Sc-3d</code>、<code>C-2p</code> 与 <code>Cl-3p</code> 空心圆轨道胖带；(b) 共享能量纵轴的水平 PDOS；(c) 二维六角第一布里渊区费米面。</figcaption></figure>

## 文献中的相关图件与表达方式

当体系包含多个过渡金属 `d` 轨道分波或晶格间隙局域电子时，文献常通过分栏展示或空心圆叠加的方式避免多重投影相互遮挡：

### 1. 晶体场分波轨道三列并排胖带、共享纵轴水平 PDOS 与二维费米面

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_OrbitalFatbands_PDOS_FS_TiSH_Li2024_Fig3a.jpg" alt="按 Ti d_xy+d_x²−y²、d_xz+d_yz 与 d_z² 拆分为三列窄能带面板的轨道胖带、水平 PDOS 与二维费米面联立图" loading="lazy"/><figcaption>将过渡金属 Ti-3d 轨道按晶体场对称性拆分为三列并排的窄能带面板，分别展示 <code>d_xy + d_x²−y²</code>、<code>d_xz + d_yz</code> 与 <code>d_z²</code> 权重，并与右侧共享能量轴的水平分波 PDOS 及二维费米面插图组合展示。图片来源：Li et al., <em>Phys. Rev. B</em> <strong>109</strong>, 174516 (2024), Fig. 3a，<a href="https://doi.org/10.1103/PhysRevB.109.174516" target="_blank" rel="noopener noreferrer">DOI: 10.1103/PhysRevB.109.174516</a>。</figcaption></figure>

- **读图与作图要点**：当同一条能带同时含有多个 `d` 分波分量时，把高对称路径压缩为三列并排的窄面板，分别绘制面内 `d_xy + d_x²−y²`、面外倾斜 `d_xz + d_yz` 和面外 `d_z²` 权重，再在右侧接上共享能量轴的水平 PDOS，可以减少不同 `d` 分波在同一像素位置上的遮挡。

### 2. 空心圆轨道与间隙空球 X 投影胖带及带边同心圆放大图

<figure class="research-figure"><img src="/Atlas/figures/literature/M4_Electride_HZrCl2_He2022_Fig2.png" alt="单层 2H-ZrCl₂ 的空心圆轨道与空球 X 投影胖带、VBM/CBM 局部同心圆放大及 ELF、PDOS、部分电荷密度联立图" loading="lazy"/><figcaption>单层 2H-ZrCl₂ 电子化合物的空心圆轨道投影能带（子图 a）：使用不同颜色的空心圆区分原子轨道与间隙空球 <code>X</code> 的投影权重，并在右侧附上 VBM 与 CBM 附近的局部放大图（多个轨道的空心圆在同一采样点上形成同心圆环）。图片来源：He et al., <em>J. Mater. Chem. C</em> <strong>10</strong>, 7674 (2022), Fig. 2，<a href="https://doi.org/10.1039/D2TC00564F" target="_blank" rel="noopener noreferrer">DOI: 10.1039/D2TC00564F</a>。</figcaption></figure>

- **读图与作图要点**：采用无填充空心圆（`facecolors='none'`）绘制多通道胖带并在 VBM/CBM 极值处给出局部放大插图，不同轨道分量在同一个 `(k, E)` 点上会呈现为半径不同的同心圆环，不会像实心散点那样由后绘制的图层完全盖住先绘制的图层。

下一步：能量分辨的轨道贡献接[DOS](/Atlas/m/dos/qe/)，全区积分的投影电子数接[布居分析](/Atlas/m/population-analysis/qe/)，带边位置接[带隙](/Atlas/m/band-gap/qe/)。

```text
SCF 密度 → 路径能带与波函数 → projwfc.x 逐态投影
                                  ↓
                      对照轨道编号、k 点和本征值
                                  ↓
                       (k, band, energy, weights)
                                  ↓
                          同标度的 s / p 胖带
```
