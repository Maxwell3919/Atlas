[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html)

[下载 Si 算例](/Atlas/examples/si-pbe-lesson-files.tar.gz)后保留目录结构，在 `si-pbe` 中运行绘图脚本。本页图读取 `mass/longitudinal.csv` 和 `mass/mass-fits.json`；横向与父密度复核结果另存于 `mass/mass-checks.csv`。包内输入、输出和 XML 可供复核，但不含可接续计算的 `tmp/si.save`，重新求能级前需重建下文对应的父 SCF 密度。

Si 的导带谷不在 Γ 点，也不刚好落在常用路径的端点。若直接对整条 Γ–X 能带拟合一条抛物线，横轴虽然看起来平滑，算出的曲率却没有明确的带边含义。这次先沿 Γ–X 的导带最低处加密采样，再分别沿谷的纵向和横向求曲率。前面的[带隙](/Atlas/m/band-gap/qe/)用均匀网格找到了这片区域；这里不重复 SCF 和普通能带计算。

`mass` 使用 Si 的 `12³` 父 SCF 密度，`ecutwfc/ecutrho=60/640 Ry`，固定晶胞、PBE、无 SOC。父密度来自独立完成的 `k12/tmp/si.save`。复制后，精细采样在自己的目录中读写；`k12` 保留原样。

```text
[preston@preston-System-Product-Name si-pbe]$ cp -a k12/tmp mass/
[preston@preston-System-Product-Name si-pbe]$ cp scf/scf.in mass/mass.in
[preston@preston-System-Product-Name si-pbe]$ vi mass/mass.in
```

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 38 mass/mass.in
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
[preston@preston-System-Product-Name si-pbe]$
```


这里用 `calculation='bands'` 读取已经得到的密度，并计算明确指定的 k 点。保留 8 条能带，Si 原胞有 8 个价电子，当前非自旋极化模型中前 4 条占据，第 5 条是要跟踪的最低导带。这里保持密度固定，`conv_thr=1.0d-12` 不表示又做了一轮密度自洽；在未另设 `diago_thr_init` 的非自洽计算中，它参与确定默认的本征值求解阈值。收紧这个输入仍不能代替检查每个本征值是否正常求出。

`K_POINTS tpiba` 后的 `101` 是点数。x 从 0.70 取到 0.95，步长 0.0025，y、z 为零；这些坐标的单位是 `2π/a`。文件最后几行如下，实际计算确实覆盖了谷的两侧，而不是只从极小值向一边取点。

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 6 mass/mass.in
0.93750000 0.00000000 0.00000000 1.0
0.94000000 0.00000000 0.00000000 1.0
0.94250000 0.00000000 0.00000000 1.0
0.94500000 0.00000000 0.00000000 1.0
0.94750000 0.00000000 0.00000000 1.0
0.95000000 0.00000000 0.00000000 1.0
[preston@preston-System-Product-Name si-pbe]$
```


完整输入可下载为[mass.in](/Atlas/examples/si-pbe/mass/mass.in)。这份输入比普通能带路径密，是因为最后的曲率来自局部能量差；若只有两三个很远的点，图上像抛物线也不足以保证拟合可靠。

```text
[preston@preston-System-Product-Name si-pbe]$ cat mass/run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-mass
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
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in mass.in > mass.out 2> mass.err
[preston@preston-System-Product-Name si-pbe]$
```


```text
[preston@preston-System-Product-Name si-pbe]$ cd mass
[preston@preston-System-Product-Name mass]$ sbatch run.sh
Submitted batch job 785
[preston@preston-System-Product-Name mass]$ cd ..
```

运行的头部确认了实际版本和 MPI 进程数。中间是每个 k 点的本征值，末尾给出程序计时与结束标志。这里的 `mass.out`、横向采样输出和 `14³` 父密度复核输出均没有 `eigenvalues not converged` 提示。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 33 mass/mass.out

     Program PWSCF v.7.5 starts on 22Sep2026 at 21:40:13

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
     8001 MiB available memory on the printing compute node when the environment starts

     Reading input from mass.in

     Current dimensions of program PWSCF are:
     Max number of different atomic species (ntypx) = 10
     Max number of k-points (npk) =  40000
     Max angular momentum in pseudopotentials (lmaxx) =  4

     Atomic positions and unit cell read from directory:
     ./tmp/si.save/


     R & G space division:  proc/nbgrp/npool/nimage =       4
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used


[preston@preston-System-Product-Name si-pbe]$
```


```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 12 mass/mass.out
     davcio       :      0.01s CPU      0.01s WALL (     202 calls)

     Parallel routines

     PWSCF        :     18.61s CPU     19.43s WALL


   This run was terminated on:  21:40:32  22Sep2026

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name si-pbe]$
```


本次纵向采样原生用时约 19 秒。[完整 mass.out](/Atlas/examples/si-pbe/mass/mass.out)适合人工查看；数值提取读取同一次计算的[data-file-schema.xml](/Atlas/examples/si-pbe/mass/data-file-schema.xml)，避免从只打印有限小数的屏幕表中做二阶差分。这个 XML 的本征值以 Hartree 给出，脚本先换算成 eV。k 坐标则用本例实际的 `alat` 转为 Å⁻¹。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 7 mass/longitudinal.csv
kx_tpiba,kx_inv_A,band5_eV
0.7,0.8148479995013461,7.043633109580449
0.7025,0.8177581709281366,7.039997615730428
0.705,0.8206683423549271,7.036421417077702
0.7075,0.8235785137817176,7.032904654922736
0.71,0.8264886852085082,7.029447505916328
0.7125,0.8293988566352989,7.026050133682778
[preston@preston-System-Product-Name si-pbe]$
```


`kx_tpiba` 和 `kx_inv_A` 两列同时保留。换算为

```text
k [Å⁻¹] = k [2π/a] × 2π / a [Å]
E [eV]  = E [Hartree] × 27.211386245988
```

先在采样点中找第 5 条能带的最低值，再以它为中心取对称窗口。拟合的是 `E=Aq²+Bq+C`，其中 `q` 以 Å⁻¹ 计。`B` 允许真实谷底稍微偏离某一个离散点，拟合后的极小值位于 `q₀=−B/(2A)`。这次 `±0.02 Å⁻¹` 的纵向窗口得到谷底 `kx≈0.84430088×2π/a`。

有效质量由能量对波矢的二阶导数决定。对这个二次式，`d²E/dk²=2A`，因此

```text
m*/mₑ = [ℏ²/(2mₑ)] / A
       = 3.80998211615486 [eV·Å²] / A [eV·Å²]
```

这个单位换算不能省略。把第几个 k 点作为横轴、或直接把 `tpiba` 数字塞进该式，都会改变曲率的尺度。

随后固定拟合出的 x 坐标，分别沿 y 和 z 方向取 33 个点。横向输入和输出保存在[mass-transverse/mass.in](/Atlas/examples/si-pbe/mass-transverse/mass.in)、[mass-transverse/mass.out](/Atlas/examples/si-pbe/mass-transverse/mass.out)。另一个独立目录 `mass-k14` 保持同样的 101 个纵向 k 点，只把父 SCF 密度由 `12³` 改为 `14³`。它用于区分“拟合窗口造成的变化”和“父密度采样造成的变化”。

```text
[preston@preston-System-Product-Name si-pbe]$ python3 analyse_mass_checks.py
longitudinal       window=0.01  n= 7  m/me=0.95645509  RMS=0.000212 meV
longitudinal       window=0.02  n=13  m/me=0.95590414  RMS=0.000866 meV
longitudinal       window=0.03  n=21  m/me=0.95557656  RMS=0.003613 meV
longitudinal-k14   window=0.01  n= 7  m/me=0.95645402  RMS=0.000212 meV
longitudinal-k14   window=0.02  n=13  m/me=0.95590308  RMS=0.000866 meV
longitudinal-k14   window=0.03  n=21  m/me=0.95557550  RMS=0.003613 meV
transverse-y       window=0.01  n= 7  m/me=0.19176939  RMS=0.000070 meV
transverse-y       window=0.02  n=13  m/me=0.19193550  RMS=0.000712 meV
transverse-y       window=0.03  n=21  m/me=0.19232024  RMS=0.005181 meV
transverse-z       window=0.01  n= 7  m/me=0.19176939  RMS=0.000070 meV
transverse-z       window=0.02  n=13  m/me=0.19193550  RMS=0.000712 meV
transverse-z       window=0.03  n=21  m/me=0.19232024  RMS=0.005181 meV
[preston@preston-System-Product-Name si-pbe]$
```


| 方向 / 父 SCF | 拟合半窗 / Å⁻¹ | 点数 | m*/mₑ | 残差 RMS / meV |
| --- | ---: | ---: | ---: | ---: |
| 纵向 x / 12³ | 0.01 | 7 | 0.956455 | 0.000212 |
| 纵向 x / 12³ | 0.02 | 13 | 0.955904 | 0.000866 |
| 纵向 x / 12³ | 0.03 | 21 | 0.955577 | 0.003613 |
| 纵向 x / 14³ | 0.01 | 7 | 0.956454 | 0.000212 |
| 纵向 x / 14³ | 0.02 | 13 | 0.955903 | 0.000866 |
| 纵向 x / 14³ | 0.03 | 21 | 0.955576 | 0.003613 |
| 横向 y / 12³ | 0.01 | 7 | 0.191769 | 0.000070 |
| 横向 y / 12³ | 0.02 | 13 | 0.191935 | 0.000712 |
| 横向 y / 12³ | 0.03 | 21 | 0.192320 | 0.005181 |
| 横向 z / 12³ | 0.01 | 7 | 0.191769 | 0.000070 |
| 横向 z / 12³ | 0.02 | 13 | 0.191935 | 0.000712 |
| 横向 z / 12³ | 0.03 | 21 | 0.192320 | 0.005181 |


对 `±0.02 Å⁻¹` 窗口，本例纵向质量约 **0.955904 mₑ**，两个横向质量都约 **0.191936 mₑ**。y、z 结果相同，与这个 Si 谷的对称性相容。窗口从 0.01 增到 0.03 Å⁻¹ 时，纵向质量约改变 0.09%，横向约改变 0.29%；更宽的窗口还带来更大的二次拟合残差，说明不能无限扩大所谓“带边区域”。父密度从 `12³` 改到 `14³` 后，纵向结果的变化约为 `10⁻⁶ mₑ`，比本次窗口变化小。

这些是给定 PBE、赝势、晶胞和无 SOC 模型下的方向质量；并没有由此得到实验温度下的输运质量，也没有计算散射时间。带边简并、强非抛物线或明显 SOC 混合时，还要重新检查跟踪的是哪一个分支。

[纵向原始数据](/Atlas/examples/si-pbe/mass/longitudinal.csv)、[窗口和父密度对照表](/Atlas/examples/si-pbe/mass/mass-checks.csv)、[质量复核脚本](/Atlas/examples/si-pbe/analyse_mass_checks.py)都可以下载。画下面这张图只需[绘图脚本](/Atlas/examples/si-pbe/plot_si.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/si-pbe/atlas_plot_style.py)）和对应 CSV/JSON：

```text
[preston@preston-System-Product-Name si-pbe]$ python3 plot_si.py mass
<工作目录>/si-pbe/plots/effective-mass.png
```

![Si 导带谷的真实采样、抛物线拟合和窗口敏感性](/Atlas/examples/si-pbe/plots/effective-mass.png)

左图画能量差而不是约 6.94 eV 的绝对能量，局部弯曲才看得清。右图把三个窗口的质量放在一起；细小的拟合残差说明局部拟合做得好，不能单独证明交换关联模型或所有数值参数已达到研究所需精度。

下一步：可跳到[三维能带采样](/Atlas/m/band-3d/qe/)检查谷的空间形状，或回到[带隙](/Atlas/m/band-gap/qe/)核对带边位置；[载流子迁移率](/Atlas/m/carrier-mobility/qe/)还需要散射模型或电子声子信息。

```text
SCF 密度 → 找到导带谷 → 沿各方向密集 k 点
                           ↓
                  本征值单位与 k 单位转换
                           ↓
                  对称窗口拟合 + 窗口比较
                           ↓
                  方向质量与适用条件
```
