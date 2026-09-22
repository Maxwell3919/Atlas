
本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。解包后保留目录结构，进入 `si-pbe` 运行文中的绘图命令；赝势按正文的官方来源准备。

下载包保留输入、输出、单独保存的 XML和作图数据，没有包含可接续计算的 `tmp/si.save` 电荷密度与波函数。阅读输出和重新作图可直接使用包内文件；重新运行 QE 时，先按 [SCF 页](/Atlas/m/scf/qe/)生成保存目录，再复制到对应计算目录。DOS 和轨道投影还需要先完成匹配的 [NSCF](/Atlas/m/nscf/qe/)。
[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/)

Si 的价带顶位于 Γ 附近，导带底却在 Γ–X 之间。只在几个高对称点读数，容易越过真正的导带谷；只看 DOS 的展宽曲线，也很难准确给出能隙。这次从均匀 k 网格中找价带最高值和导带最低值，再把导带谷附近加密，逐步看清误差来自哪里。

结构、赝势和父密度沿用[收敛测试](/Atlas/m/convergence/qe/)中的固定两原子 Si 原胞。如何得到父密度见[SCF](/Atlas/m/scf/qe/)，如何让非自洽计算读取它见[NSCF](/Atlas/m/nscf/qe/)。这里保持同一结构、PBE、`60/640 Ry`、无 SOC，比较 `12³`、`18³`、`24³` 三个均匀网格；每一个目录都从自己的父密度副本出发。

先看本次实际使用的 `24³` 输入。与普通 SCF 相比，需要关注 `calculation='nscf'`、8 条能带、明确的电子求解设置和末尾的网格。

```text
[preston@preston-System-Product-Name si-pbe]$ cat gap24-cg/nscf.in
&CONTROL
  calculation = 'nscf'
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
  diagonalization = 'cg'
  diago_cg_maxiter = 200
  diago_thr_init = 1.0d-10
  conv_thr = 1.0d-10
/
ATOMIC_SPECIES
Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS alat
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25
K_POINTS automatic
24 24 24 0 0 0
[preston@preston-System-Product-Name si-pbe]$
```


Si 原胞有 8 个价电子，在本例的非自旋极化固定占据模型下，前 4 条能带占据，第 5 条开始未占据。因此提取时使用 `band4` 和 `band5`。这个数不能直接套到含不同价电子数、磁性或部分占据的材料上。

初次用默认对角化运行的部分密网格出现了 `c_bands: 1 eigenvalues not converged`。原文件留在 `gap18`、`gap24` 中，后面的数值使用独立的 `gap18-cg`、`gap24-cg` 复核结果。新输入采用 `diagonalization='cg'`、`diago_cg_maxiter=200` 和 `diago_thr_init=1.0d-10`；重新运行后逐行检查，未再出现本征值未收敛提示。`gap12` 的原始计算没有该警告，保留其原始结果。

```text
[preston@preston-System-Product-Name si-pbe]$ cat gap24-cg/run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-cg
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
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in nscf.in > nscf.out 2> nscf.err
[preston@preston-System-Product-Name si-pbe]$
```


```text
[preston@preston-System-Product-Name gap24-cg]$ sbatch run.sh
Submitted batch job 795
[preston@preston-System-Product-Name gap24-cg]$ cd ..
```

文件开头记录版本、进程数和读入文件，中间是实际计算出的 k 点与能级。这里的输入、输出分别可下载为[nscf.in](/Atlas/examples/si-pbe/gap24-cg/nscf.in)和[nscf.out](/Atlas/examples/si-pbe/gap24-cg/nscf.out)。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 35 gap24-cg/nscf.out

     Program PWSCF v.7.5 starts on 22Sep2026 at 22: 0:36

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
     6585 MiB available memory on the printing compute node when the environment starts

     Reading input from nscf.in

     Current dimensions of program PWSCF are:
     Max number of different atomic species (ntypx) = 10
     Max number of k-points (npk) =  40000
     Max angular momentum in pseudopotentials (lmaxx) =  4

     Atomic positions and unit cell read from directory:
     ./tmp/si.save/


     R & G space division:  proc/nbgrp/npool/nimage =       4
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used


     Parallelization info
     --------------------
[preston@preston-System-Product-Name si-pbe]$
```


`End of band structure calculation` 后，每个 k 点后面跟着 8 个 eV 能级。Γ 点的三条价带顶近简并；可以先在这个位置用肉眼检查第 4、5 条的关系，再由脚本遍历全部点。

```text
[preston@preston-System-Product-Name si-pbe]$ grep -A19 'End of band structure calculation' gap24-cg/nscf.out
     End of band structure calculation

          k = 0.0000 0.0000 0.0000 (  2085 PWs)   bands (ev):

    -5.6925   6.3970   6.3970   6.3970   8.9666   8.9666   8.9666   9.9691

     occupation numbers
     1.0000   1.0000   1.0000   1.0000   0.0000   0.0000   0.0000   0.0000

          k =-0.0417 0.0417-0.0417 (  2085 PWs)   bands (ev):

    -5.6693   6.1411   6.3573   6.3573   9.0242   9.0247   9.0247  10.1269

     occupation numbers
     1.0000   1.0000   1.0000   1.0000   0.0000   0.0000   0.0000   0.0000

          k =-0.0833 0.0833-0.0833 (  2079 PWs)   bands (ev):

    -5.6001   5.5366   6.2502   6.2502   9.0393   9.1823   9.1823  10.6027

[preston@preston-System-Product-Name si-pbe]$
```


OUT 末端还有一行最高占据和最低未占据能级。它适合快速核对，但打印位数有限，正式差值仍从同一次运行的 XML 提取。

```text
[preston@preston-System-Product-Name si-pbe]$ grep 'highest occupied' gap24-cg/nscf.out
     highest occupied, lowest unoccupied level (ev):     6.3970    6.9372
[preston@preston-System-Product-Name si-pbe]$
```


```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 12 gap24-cg/nscf.out
     davcio       :      0.02s CPU      0.03s WALL (     826 calls)

     Parallel routines

     PWSCF        :   1m38.87s CPU   1m44.29s WALL


   This run was terminated on:  22: 2:20  22Sep2026

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name si-pbe]$
```


在这组非磁性半导体数据中，间接能隙取 `min(Ec)−max(Ev)`；直接能隙则取同一个 k 点上的 `Ec(k)−Ev(k)`，再找全网格的最小值。两种运算次序不同，这个例子里差别也很明显。

| 均匀 NSCF 网格 | 不可约 k 点 | VBM / eV | CBM / eV | 采样间接隙 / eV | 采样到的 CBM 坐标 / 2πa⁻¹ |
| --- | ---: | ---: | ---: | ---: | --- |
| 12³ | 72 | 6.39702896 | 6.93715852 | 0.54012956 | (0, 0.83333333, 0) |
| 18³ | 195 | 6.39702896 | 6.94734592 | 0.55031696 | (0, 0.88888889, 0) |
| 24³ | 413 | 6.39702896 | 6.93715852 | 0.54012957 | (0, 0.83333333, 0) |


三个网格的 VBM 都在 Γ，CBM 落在与 Γ–X 等价的 y 方向谷附近。`12³` 和 `24³` 恰好都包含 `5/6` 这个坐标，所以两次采样间接隙都约为 0.54013 eV；`18³` 最接近谷的点在 `8/9`，得到约 0.55032 eV。网格更密，采样极值却不一定单调向下。前后两次数值相等也不能单独证明已经找到了连续的谷底。

本次这些网格的最小直接隙约为 2.56953 eV。它与约 0.54 eV 的间接隙并不矛盾：直接隙要求电子、空穴位于同一个 k 点；间接隙允许价带顶和导带底出现在不同位置。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 6 gap24-cg/edges.csv
kx_tpiba,ky_tpiba,kz_tpiba,vbm_band4_eV,cbm_band5_eV
0.0,0.0,0.0,6.397028955496858,8.966555400141297
-0.04166666666666666,0.04166666666666666,-0.04166666666666666,6.357275964159993,9.02421776352731
-0.08333333333333333,0.08333333333333333,-0.08333333333333333,6.250233934869697,9.039332515544226
-0.125,0.125,-0.125,6.102261128161904,8.948575859989088
-0.1666666666666667,0.1666666666666667,-0.1666666666666667,5.938184474917871,8.804861375098497
[preston@preston-System-Product-Name si-pbe]$
```


`edges.csv` 保留每个实际计算点的坐标和第 4、5 条能级。[提取脚本](/Atlas/examples/si-pbe/analyse_si.py)读取 XML 的 Hartree 本征值并转换成 eV，同时保留坐标；[汇总结果](/Atlas/examples/si-pbe/gap-results.json)中记录了 VBM、CBM 的位置和直接/间接两种差值。

再将父 SCF 的网格从 `8³` 加密到 `12³`，在独立 `gap24-k12-cg` 上重复同一个 `24³` 非自洽网格，采样间接隙变为 **0.54082954 eV**，变化约 0.00070 eV。这一步检查的是父密度，而前面的三组检查的是给定密度上的本征值采样，二者不能混成同一个横轴。

随后沿同一个 `12³` 父密度的 Γ–X 谷做密集采样，局部拟合把谷底定位在 `kx≈0.84430088×2π/a`。与同父密度的 VBM 相减，得到约 **0.54017968 eV**。这一细化步骤的输入、点距和窗口检查都在[有效质量](/Atlas/m/effective-mass/qe/)页，不在这里重走一次。

将[绘图脚本](/Atlas/examples/si-pbe/plot_si.py)与示例数据放在同一目录后运行：

```text
[preston@preston-System-Product-Name si-pbe]$ python3 plot_si.py gap
<工作目录>/si-pbe/plots/band-gap.png
```

![Si 均匀网格的采样带隙，以及 Γ–X 导带谷的局部细化](/Atlas/examples/si-pbe/plots/band-gap.png)

左图保留了网格采样的非单调变化，右图沿局部谷的横坐标画出第 5 条能带，相对于对应父密度的 VBM 取零。线采样和均匀网格的能量参考经过同一父密度配对；直接把不同父密度的一个 CBM 和另一个 VBM 相减，会破坏这个比较。

这里得到的是固定晶胞、PBE、无 SOC 模型的 Kohn–Sham 能级差。完整能隙还需结合更广的极值搜索、结构和模型检查；它不是直接测得的光学吸收阈值，也没有包含准粒子或激子修正。后续若改变晶格、赝势或 SOC，原有的数值比较需要重新建立。

下一步：轨道组成接[胖带](/Atlas/m/fatband/qe/)，带边曲率接[有效质量](/Atlas/m/effective-mass/qe/)，空间分布接[三维能带](/Atlas/m/band-3d/qe/)。

```text
SCF 密度 → 均匀 NSCF 网格 → 全点搜索 VBM / CBM
                 ↓                  ↓
           父密度敏感性       谷附近直接加密
                 └──────────┬───────┘
                       说明能隙及模型条件
```
