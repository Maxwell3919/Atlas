[projwfc.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html) · [后处理用户手册](https://www.quantum-espresso.org/Doc/pp_user_guide/)

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。解包后保留目录结构，进入 `si-pbe` 运行文中的绘图命令；赝势按正文的官方来源准备。

下载包保留输入、输出、XML 与作图数据，未打包 `tmp/si.save` 中的电荷密度和波函数。阅读输出、重新作图可直接使用包内文件；重新计算投影时，先完成 [Si 路径能带](/Atlas/m/bands/qe/)，本页读取其中 121 个路径点的波函数。

普通能带告诉我们某个 k 点上有哪些能级；胖带再把这些态的轨道投影画成点的大小或带线的粗细。这次沿 Si 的 Γ–X–W–K–Γ–L–X 路径计算 121 个 k 点，每点保留 8 条能带，再分别画两个原子合计的 s 和 p 权重。横轴始终是这条路径中的位置。

前置能带计算的输入和路径含义见[能带](/Atlas/m/bands/qe/)。这里直接接已经完成的 `bands-cg/tmp/si.save`；它保存的是路径上的波函数。初次路径计算曾出现单个本征值未收敛提示，因此保留旧 `bands` 目录，并在 `bands-cg` 使用 CG 对角化完成复核。以下投影、CSV 和图片全部来自新的同一条链。

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

输出里的 `psi = 0.498*[#1]+...` 是面向阅读的投影权重摘要，系数只保留有限小数，较小项也可能不列出来。画图时读取[atomic_proj.xml](/Atlas/examples/si-pbe/bands-cg/atomic_proj.xml)中的复投影幅度，再逐项取模平方。

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

原子态构成的是有限投影子空间，所以它通常不能覆盖整个平面波波函数。投影范数接近 1 表示覆盖得较好，小于 1 的部分保留下来；本例没有把 s、p 再强行归一化成和为 1。Γ 点价带顶的投影和约 0.960，最深价带约 0.996，已经能看见两者差异。高能空带可能有更明显的未覆盖成分。

在正交归一投影的定义下，子空间投影范数不应超过完整态的范数；数值实现仍应检查舍入和容差。这里 968 个 `(k,band)` 组合中的最大值为约 **0.99704634**。这个检查能发现权重提取或归一化错误，却不会证明有限原子轨道是描述所有能带的完备基底。简并子空间内单个分支的轨道分量也可能随基选择改变，比较时优先看有明确物理意义的轨道组和简并带组。

还有一个容易混淆的单位：本次 `atomic_proj.xml` 的 `E` 值以 Ry 存储，而 `data-file-schema.xml` 的本征值以 Hartree 存储。[提取脚本](/Atlas/examples/si-pbe/analyse_si.py)用后者的能量画图，并独立把前者乘以 `13.605693122994`，逐点核对二者在 `10⁻⁶ eV` 内一致；k 坐标也逐点核对。只有通过配对后才把能量和权重写在同一行。

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


[完整 fatband.csv](/Atlas/examples/si-pbe/bands-cg/fatband.csv)有 `121×8=968` 行数据，保留 k 序号、能带序号、累积路径距离、三个 k 坐标、能量、s/p 权重和投影和。这样既可以重画图，也能回到某个图上的点查原始态。

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


运行末尾确认 `projwfc.x` 正常结束。[完整输出](/Atlas/examples/si-pbe/bands-cg/projwfc.out)尾部还会打印 Löwdin 数字，但这次输入的是能带路径，不把它用于布里渊区积分的布居结论；[布居分析](/Atlas/m/population-analysis/qe/)另用均匀 `18³` 网格演示。

画图使用[绘图脚本](/Atlas/examples/si-pbe/plot_si.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/si-pbe/atlas_plot_style.py)）：

```text
[preston@preston-System-Product-Name si-pbe]$ python3 plot_si.py fatband
<工作目录>/si-pbe/plots/fatband.png
```

![Si 的逐 k 逐带 s 和 p 权重胖带图](/Atlas/examples/si-pbe/plots/fatband.png)

两幅图使用同一路径和参考 `E−6.397028957255 eV`。节点索引仍为 `1、25、37、49、73、97、121`，横轴是实际坐标的累计距离，而非等距 k 点编号；节点和长度见[普通能带页](/Atlas/m/bands/qe/)。

蓝色点面积正比于 s 权重，橙色点面积正比于 p 权重，灰色细线保留本征能带。两个面板必须使用相同面积标度，不能各自把最强点归一化到一样大。`scatter(..., s=...)` 的 s 是面积，权重翻倍意味着面积翻倍、半径仅增为 √2 倍，不能凭直径直接读权重。

Γ 点最深价带几乎完全投到 s，权重约 0.9960；价带顶三条带主要投到 p，各约 0.9604。沿路径移动，点面积随轨道混合变化。简并处单条分支的分量可能依赖该子空间的基选择，读它们合计的 s/p 性质更稳妥。

还有一个明确的弱投影点：K→Γ 段第 53 个 k 点 `(0.625,0.625,0)×2π/a`，第 7 条带位于 `E−VBM=6.224118 eV`；s 为 `0.0168803`，p 为 `0.0446863`，合计仅 `0.0615665`。灰色能带仍存在，两个面板的点却都小，表示所选 s/p 空间对该空态覆盖很少。不能说这条带消失，也不能随意将剩余约 94% 命名为未计算的某个轨道。

没有把 s+p 强制归一化为 1，正是为了保留这种区别。完整 CSV 的投影和范围约 `0.06157–0.99705`，不同态的表示质量差别很大，不能只报告最大值接近 1。

这张图展示了固定 Si 晶胞、PBE、无 SOC 模型下的轨道组成。要分原子、分层或画 d 轨道，可以沿用相同的逐态合并方式，先根据本次 `Atomic states used for projection` 建立分组。没有出现在赝势投影态表中的轨道，不能靠改图例得到。

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
