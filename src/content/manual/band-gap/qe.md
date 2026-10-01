Si 的价带顶位于 Γ 附近，导带底却在 Γ–X 之间。只在几个高对称点读数，容易越过真正的导带谷；只看 DOS 的展宽曲线，也很难准确给出能隙。这次从均匀 k 网格中找价带最高值和导带最低值，再把导带谷附近加密，逐步看清误差来自哪里。

[SnSe₂/PtTe₂ 原文 Fig. 1(c,f,i)](https://arxiv.org/pdf/2502.13690v1)以孤立层带边与界面穿越费米能的分支建立对照。本例先用 Si 小体系说明极值搜索，作为[能带](/Atlas/m/bands/qe/)的配套分析。

结构、赝势和父密度沿用[收敛测试](/Atlas/m/convergence/qe/)中的固定两原子 Si 原胞。如何得到父密度见[SCF](/Atlas/m/scf/qe/)，如何让非自洽计算读取它见[NSCF](/Atlas/m/nscf/qe/)。这里保持同一结构、PBE、`60/640 Ry`、无 SOC，比较 `12³`、`18³`、`24³` 三个均匀网格；这三组计算分别读取同一份 8³ 父 SCF 密度的独立副本；后文再单独改变父 SCF 网格。

[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/)

[下载 Si 算例](/Atlas/examples/si-pbe-electronic-files.tar.gz)后保留目录结构，在 `si-pbe` 中运行绘图脚本。本页图读取 `gap-results.json`、`mass/longitudinal.csv` 和 `mass/mass-fits.json`；包内还保留用于核对的输入、输出与 XML。包中不含可接续计算的 `tmp/si.save`，重新求能级时需先按下文前提重建对应父 SCF 密度。

## 从父 SCF 密度生成均匀网格能级

每个 NSCF 目录的 `outdir=./tmp` 中应先有对应父 SCF 的 `si.save/`，其中结构、赝势和电荷密度与本次输入一致。下载包中的独立 XML 用于读取既有结果；重算时需由 SCF 重建保存目录，再分别复制到各网格目录。沿高对称路径计算的能级适合读色散，带边搜索需要这里的均匀 NSCF 网格。

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

`nbnd=8` 在四条占据带之外再求四条空带，保证这次能读到最低导带。增加 `nbnd` 扩大每个 k 点的能级范围；加密 k 网格则改变搜索带边的位置。只增加空带数，不会补上两个 k 点之间尚未采到的导带谷。

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

文件开头记录版本、进程数和读入文件，中间是实际计算出的 k 点与能级。这里的输入、输出分别可下载为[nscf.in](/Atlas/examples/si-pbe-electronic/gap24-cg/nscf.in)和[nscf.out](/Atlas/examples/si-pbe-electronic/gap24-cg/nscf.out)。

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

## 遍历全部采样点，区分直接隙与间接隙

在这组非磁性半导体数据中，间接能隙取 `min(Ec)−max(Ev)`；直接能隙则取同一个 k 点上的 `Ec(k)−Ev(k)`，再找全网格的最小值。两种运算次序不同，这个例子里差别也很明显。

| 均匀 NSCF 网格 | 不可约 k 点 | VBM / eV | CBM / eV | 采样间接隙 / eV | 采样到的 CBM 坐标 / 2πa⁻¹ |
| --- | ---: | ---: | ---: | ---: | --- |
| 12³ | 72 | 6.39702896 | 6.93715852 | 0.54012956 | (0, 0.83333333, 0) |
| 18³ | 195 | 6.39702896 | 6.94734592 | 0.55031696 | (0, 0.88888889, 0) |
| 24³ | 413 | 6.39702896 | 6.93715852 | 0.54012957 | (0, 0.83333333, 0) |

三个网格的 VBM 都在 Γ，CBM 落在与 Γ–X 等价的 y 方向谷附近。`12³` 和 `24³` 恰好都包含 `5/6` 这个坐标，所以两次采样间接隙都约为 0.54013 eV；`18³` 最接近谷的点在 `8/9`，得到约 0.55032 eV。网格更密，采样极值却不一定单调向下。这两个重合的采样结果还需结合谷附近的局部加密，才能判断连续谷底的位置。

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

`edges.csv` 保留每个实际计算点的坐标和第 4、5 条能级。[提取脚本](/Atlas/examples/si-pbe-electronic/analyse_electronic.py)读取 XML 的 Hartree 本征值并转换成 eV，同时保留坐标；[汇总结果](/Atlas/examples/si-pbe-electronic/gap-results.json)中记录了 VBM、CBM 的位置和直接/间接两种差值。

重建 `12³` 父密度时，使用收敛算例的真实 [k12/scf.in](/Atlas/examples/basics-si-convergence/si-pbe/k12/scf.in)，在独立 `k12` 目录准备相同赝势并按 [Si SCF](/Atlas/m/scf/qe/) 的运行方法完成计算，生成 `k12/tmp/si.save`。这份输入保持同一晶胞、PBE、`60/640 Ry` 与无 SOC，网格为 `12 12 12 0 0 0`；不能用入门页的 `8³` 保存目录代替。

再将父 SCF 的网格从 `8³` 加密到 `12³`，在独立 `gap24-k12-cg` 上重复同一个 `24³` 非自洽网格，采样间接隙变为 **0.54082954 eV**，变化约 0.00070 eV。这一步检查的是父密度，而前面的三组检查的是给定密度上的本征值采样，比较时分别标明父 SCF 网格和 NSCF 网格。

随后沿同一个 `12³` 父密度的 Γ–X 谷做密集采样，局部拟合把谷底定位在 `kx≈0.84430088×2π/a`。与同父密度的 VBM 相减，得到约 **0.54017968 eV**。下面保留这一步独立于均匀网格的输入、采样范围与拟合来源。

<details>
<summary>局部谷搜索：12³父密度、101点输入与拟合窗口</summary>

[完整电子算例包](/Atlas/examples/si-pbe-electronic-files.tar.gz)中保留 `mass/mass.in`、`mass/mass.out`、`mass/data-file-schema.xml`、`mass/longitudinal.csv` 与 `mass/mass-fits.json`。公开包不含可接续运行的 `tmp/si.save`；重算先完成上面的 `k12` SCF，再把父保存目录复制到独立 `mass` 分支：

```bash
mkdir -p mass
cp -a k12/tmp mass/
```

直接取用包内 [mass.in](/Atlas/examples/si-pbe-electronic/mass/mass.in)，其原始完整内容如下。`calculation='bands'` 在固定父密度上求指定点的本征值，保留8条带；第5条为本例要搜索的最低导带。`conv_thr=1.0d-12` 参与未另设 `diago_thr_init` 时的默认本征值求解阈值，不表示再做密度自洽。

```text
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
101
0.70000000 0.00000000 0.00000000 1.0
0.70250000 0.00000000 0.00000000 1.0
0.70500000 0.00000000 0.00000000 1.0
0.70750000 0.00000000 0.00000000 1.0
0.71000000 0.00000000 0.00000000 1.0
0.71250000 0.00000000 0.00000000 1.0
0.71500000 0.00000000 0.00000000 1.0
0.71750000 0.00000000 0.00000000 1.0
0.72000000 0.00000000 0.00000000 1.0
0.72250000 0.00000000 0.00000000 1.0
0.72500000 0.00000000 0.00000000 1.0
0.72750000 0.00000000 0.00000000 1.0
0.73000000 0.00000000 0.00000000 1.0
0.73250000 0.00000000 0.00000000 1.0
0.73500000 0.00000000 0.00000000 1.0
0.73750000 0.00000000 0.00000000 1.0
0.74000000 0.00000000 0.00000000 1.0
0.74250000 0.00000000 0.00000000 1.0
0.74500000 0.00000000 0.00000000 1.0
0.74750000 0.00000000 0.00000000 1.0
0.75000000 0.00000000 0.00000000 1.0
0.75250000 0.00000000 0.00000000 1.0
0.75500000 0.00000000 0.00000000 1.0
0.75750000 0.00000000 0.00000000 1.0
0.76000000 0.00000000 0.00000000 1.0
0.76250000 0.00000000 0.00000000 1.0
0.76500000 0.00000000 0.00000000 1.0
0.76750000 0.00000000 0.00000000 1.0
0.77000000 0.00000000 0.00000000 1.0
0.77250000 0.00000000 0.00000000 1.0
0.77500000 0.00000000 0.00000000 1.0
0.77750000 0.00000000 0.00000000 1.0
0.78000000 0.00000000 0.00000000 1.0
0.78250000 0.00000000 0.00000000 1.0
0.78500000 0.00000000 0.00000000 1.0
0.78750000 0.00000000 0.00000000 1.0
0.79000000 0.00000000 0.00000000 1.0
0.79250000 0.00000000 0.00000000 1.0
0.79500000 0.00000000 0.00000000 1.0
0.79750000 0.00000000 0.00000000 1.0
0.80000000 0.00000000 0.00000000 1.0
0.80250000 0.00000000 0.00000000 1.0
0.80500000 0.00000000 0.00000000 1.0
0.80750000 0.00000000 0.00000000 1.0
0.81000000 0.00000000 0.00000000 1.0
0.81250000 0.00000000 0.00000000 1.0
0.81500000 0.00000000 0.00000000 1.0
0.81750000 0.00000000 0.00000000 1.0
0.82000000 0.00000000 0.00000000 1.0
0.82250000 0.00000000 0.00000000 1.0
0.82500000 0.00000000 0.00000000 1.0
0.82750000 0.00000000 0.00000000 1.0
0.83000000 0.00000000 0.00000000 1.0
0.83250000 0.00000000 0.00000000 1.0
0.83500000 0.00000000 0.00000000 1.0
0.83750000 0.00000000 0.00000000 1.0
0.84000000 0.00000000 0.00000000 1.0
0.84250000 0.00000000 0.00000000 1.0
0.84500000 0.00000000 0.00000000 1.0
0.84750000 0.00000000 0.00000000 1.0
0.85000000 0.00000000 0.00000000 1.0
0.85250000 0.00000000 0.00000000 1.0
0.85500000 0.00000000 0.00000000 1.0
0.85750000 0.00000000 0.00000000 1.0
0.86000000 0.00000000 0.00000000 1.0
0.86250000 0.00000000 0.00000000 1.0
0.86500000 0.00000000 0.00000000 1.0
0.86750000 0.00000000 0.00000000 1.0
0.87000000 0.00000000 0.00000000 1.0
0.87250000 0.00000000 0.00000000 1.0
0.87500000 0.00000000 0.00000000 1.0
0.87750000 0.00000000 0.00000000 1.0
0.88000000 0.00000000 0.00000000 1.0
0.88250000 0.00000000 0.00000000 1.0
0.88500000 0.00000000 0.00000000 1.0
0.88750000 0.00000000 0.00000000 1.0
0.89000000 0.00000000 0.00000000 1.0
0.89250000 0.00000000 0.00000000 1.0
0.89500000 0.00000000 0.00000000 1.0
0.89750000 0.00000000 0.00000000 1.0
0.90000000 0.00000000 0.00000000 1.0
0.90250000 0.00000000 0.00000000 1.0
0.90500000 0.00000000 0.00000000 1.0
0.90750000 0.00000000 0.00000000 1.0
0.91000000 0.00000000 0.00000000 1.0
0.91250000 0.00000000 0.00000000 1.0
0.91500000 0.00000000 0.00000000 1.0
0.91750000 0.00000000 0.00000000 1.0
0.92000000 0.00000000 0.00000000 1.0
0.92250000 0.00000000 0.00000000 1.0
0.92500000 0.00000000 0.00000000 1.0
0.92750000 0.00000000 0.00000000 1.0
0.93000000 0.00000000 0.00000000 1.0
0.93250000 0.00000000 0.00000000 1.0
0.93500000 0.00000000 0.00000000 1.0
0.93750000 0.00000000 0.00000000 1.0
0.94000000 0.00000000 0.00000000 1.0
0.94250000 0.00000000 0.00000000 1.0
0.94500000 0.00000000 0.00000000 1.0
0.94750000 0.00000000 0.00000000 1.0
0.95000000 0.00000000 0.00000000 1.0
```

`K_POINTS tpiba` 的101点令 x 从0.70到0.95、步长0.0025，y=z=0，单位为 `2π/a`，覆盖 Γ–X 谷的两侧。[原始输出](/Atlas/examples/si-pbe-electronic/mass/mass.out)与 [XML](/Atlas/examples/si-pbe-electronic/mass/data-file-schema.xml)可直接核对求解结果；运行提交方法沿用上面的独立分支脚本，在 `mass` 目录将输入/输出文件名改为 `mass.in`/`mass.out`。

本页后文完整 [analyse_electronic.py](/Atlas/examples/si-pbe-electronic/analyse_electronic.py) 中的局部拟合段读取该XML，将Hartree能量转为eV，并用XML中的晶格长度将tpiba波矢换为Å⁻¹。先找第5带的采样最低点，以它为中心取 `±0.01/0.02/0.03 Å⁻¹` 窗口，拟合 `E=Aq²+Bq+C`；顶点为 `q₀=−B/(2A)`，谷底能量为 `C−B²/(4A)`。不能以点号替代物理波矢。

| 半窗口 / Å⁻¹ | 拟合点数 | 谷底 kₓ / (2π/a) | 谷底能量 / eV | 残差 RMS / meV |
|---|---:|---:|---:|---:|
| 0.01 | 7 | 0.84431553 | 6.93552215 | 0.000212 |
| 0.02 | 13 | 0.84430088 | 6.93552194 | 0.000866 |
| 0.03 | 21 | 0.84426999 | 6.93552156 | 0.003613 |

采用 `±0.02 Å⁻¹` 的谷底，与 `gap24-k12-cg` 的同父密度 VBM=6.395342259906624eV相减，得到0.54017968eV。三个窗口的谷底位置略有变化，更宽窗口的二次拟合残差增大；这项检查针对局部拟合，不替代全布里渊区的极值搜索。窗口原始量见包内 `mass/mass-fits.json`；[纵向CSV](/Atlas/examples/si-pbe-electronic/mass/longitudinal.csv)、[窗口复核表](/Atlas/examples/si-pbe-electronic/mass/mass-checks.csv)和 [复核源码](/Atlas/examples/si-pbe-electronic/analyse_mass_checks.py)同时保留。复核源码还读取包内 `mass-transverse`、`mass-k14` 的XML，复用时需保留这些目录；只提取本段三个纵向窗口可用后文共用提取器中的 `mass` 拟合段。

</details>

<span id="把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
<span id="h-把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
## 带边搜索的输入与检查

程序需要分别找出每张均匀网格上的 VBM、CBM 和同 k 直接间隙，再读取谷底加密数据。下面的任务说明保留了带序、单位和父密度的区别。

```text
编写 Si 采样带隙分析程序，使用 Python 3、NumPy 和 Matplotlib。
输入：gap12、gap18-cg、gap24-cg 的 edges.csv，gap-results.json，以及 mass/longitudinal.csv、mass-fits.json。k 为 tpiba（2π/a），band 4/5 能量为 eV。
方法：各父 SCF 链分别计算 VBM=max(Ev)、CBM=min(Ec)、间接采样隙=CBM−VBM、直接采样隙=min_k[Ec(k)−Ev(k)]，保留极值坐标。将均匀网格与 12³ 父密度局部谷细化分开。
检查：行数、有限数值、带号及父密度匹配，重算值与 JSON 一致。
输出：源码、依赖、命令、带边及坐标表、PNG/SVG/PDF。图保留网格结果的非单调变化，结果标为固定晶胞 PBE 无 SOC 的 Kohn–Sham 能级差。
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

`analyse_electronic.py` 是完整电子下载包的共用提取器：一次运行读取带隙网格 XML，并同时读取 `mass/data-file-schema.xml`、`bands-cg/data-file-schema.xml` 和 `bands-cg/atomic_proj.xml`，生成带隙、纵向质量及胖带数据；包内的局部三维 XML 存在时也会提取该网格。因此运行它时保留整包目录及这些跨页面数据。上面的提示词描述本页性质的分析逻辑，复用现有共用脚本时还需满足这组文件依赖。只重画已有 CSV/JSON 时，直接执行 `python3 plot_si.py gap`。

解压本页示例包后，在 `si-pbe` 根目录执行：

```bash
python3 -m pip install numpy matplotlib
python3 analyse_electronic.py
python3 plot_si.py gap
```

本例保存的绘图运行输出如下：

```text
[preston@preston-System-Product-Name si-pbe]$ python3 plot_si.py gap
<工作目录>/si-pbe/plots/band-gap.png
```

上面的均匀网格表保留非单调采样值，折叠段的101点输入与窗口表保留局部谷细化依据。采样间隙和局部细化值使用各自配对的父密度；不能把不同父密度的 CBM 与 VBM 相减。[原有采样对照图](/Atlas/examples/si-pbe-electronic/plots/band-gap.png)随完整算例保留。

这里得到的是固定晶胞、PBE、无 SOC 模型的 Kohn–Sham 能级差。带边位置的精度还取决于极值搜索、结构和模型检查；与实验光学吸收比较时，还需考虑准粒子修正与激子效应。后续若改变晶格、赝势或 SOC，原有的数值比较需要重新建立。

## 带边搜索怎样接到界面金属化

[SnSe₂/PtTe₂ 原文 PDF 第3页 Fig. 1(c,f,i)](https://arxiv.org/pdf/2502.13690v1#page=3)共用 Γ–M–K–Γ 路径与 E−E_F 能量读法。(c)、(f)辨认两个孤立层的带边，(i)以红/蓝层权重显示界面近费米分支，M附近插图标出电子口袋深度ΔE。这个量是能量差，不能直接当转移电子数；作者还联读(h)差分密度与正文分析。只看路径上是否穿过零能，也不能保证找到整个BZ的带边。

本页均匀网格表与折叠段101点局部谷数据对应极值搜索环节。按文献面板方式整理本页数据时，保留真实路径距离、同父密度VBM/CBM及其k坐标，局部谷继续用原始点与三个窗口结果，不以论文口袋形状代替本页数据。界面层来源的现有展示见[本站历史三联图](/Atlas/m/bands/qe/)，胖带、PDOS与费米面仍对应各自真实分支；本页没有生成该论文界面。

界面若已有分支穿越 E_F，先明确是整体金属态还是某层的投影带边变化，再进入[轨道投影](/Atlas/m/fatband/qe/)和[费米面](/Atlas/m/fermi-surface/qe/)。在金属中固定取第 4、5 带相减没有带隙定义。不同材料的绝对本征值还应按[共同静电势参考](/Atlas/m/electrostatic-potential/)对齐。

本例数值是固定 PBE 模型的 Kohn–Sham 带边差；接触前后的带边比较也必须固定泛函、结构和 SOC 约定。光学吸收与本征值带隙之间还涉及跃迁与电子—空穴相互作用，不能从这套网格表直接读出光学峰。

```text
SCF 密度 → 均匀 NSCF 网格 → 全点搜索 VBM / CBM
                 ↓                  ↓
           父密度敏感性       谷附近直接加密
                 └──────────┬───────┘
                       说明能隙及模型条件
```
