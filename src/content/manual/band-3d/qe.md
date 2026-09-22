[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/)

[下载 Si 算例](/Atlas/examples/si-pbe-lesson-files.tar.gz)后保留目录结构，在 `si-pbe` 中运行绘图脚本。本页图直接读取 `band3d/cube.csv`，对应输入、输出和 XML 也在该子目录。包中不含可接续计算的 `tmp/si.save`；重新计算这批 k 点时，需要下文使用的同一份父 SCF 密度。

一条高对称路径只是在倒空间里走过几条线。要看 Si 导带谷为什么在不同方向有不同曲率，需要离开那条线。这次在 Γ–X 导带谷附近真正计算一个三维 k 点立方网格，再从中画两张能量曲面。它覆盖的是一个局部谷，不是整个第一布里渊区。

前面的[带隙](/Atlas/m/band-gap/qe/)和[有效质量](/Atlas/m/effective-mass/qe/)已经把这个谷定位在 `kx≈0.8443×2π/a`。这里仍使用同一固定 Si 晶胞、同一 `60/640 Ry` 设置和 `12³` 父 SCF 密度；不重复介绍它的 SCF 过程。

```text
[preston@preston-System-Product-Name si-pbe]$ cp -a k12/tmp band3d/
[preston@preston-System-Product-Name si-pbe]$ cp scf/scf.in band3d/grid.in
[preston@preston-System-Product-Name si-pbe]$ vi band3d/grid.in
```

输入开头和最前几个 k 点如下。与普通路径不同，这里写的是 `K_POINTS tpiba` 的完整点表，数量为 **891**。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 38 band3d/grid.in
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
891
0.75000000 -0.08000000 -0.08000000 1.0
0.75000000 -0.08000000 -0.06000000 1.0
0.75000000 -0.08000000 -0.04000000 1.0
0.75000000 -0.08000000 -0.02000000 1.0
0.75000000 -0.08000000 0.00000000 1.0
0.75000000 -0.08000000 0.02000000 1.0
0.75000000 -0.08000000 0.04000000 1.0
0.75000000 -0.08000000 0.06000000 1.0
0.75000000 -0.08000000 0.08000000 1.0
[preston@preston-System-Product-Name si-pbe]$
```


三个方向分别为：x 从 0.75 到 0.95，共 11 点；y、z 从 −0.08 到 0.08，各 9 点，间隔均为 0.02，单位都是 `2π/a`。`11×9×9=891`，所以这里有真实的离面采样，并非把一条曲线绕轴旋转出来。

取值范围决定这张局部图覆盖多大的谷区，点距决定能看清多细的起伏。扩大范围仍可能错过很窄的极值；缩小点距也不会把局部网格变成全布里渊区采样。这两种修改都只是在既有父密度上增加本征值采样。

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 5 band3d/grid.in
0.95000000 0.08000000 0.00000000 1.0
0.95000000 0.08000000 0.02000000 1.0
0.95000000 0.08000000 0.04000000 1.0
0.95000000 0.08000000 0.06000000 1.0
0.95000000 0.08000000 0.08000000 1.0
[preston@preston-System-Product-Name si-pbe]$
```


[完整 grid.in](/Atlas/examples/si-pbe/band3d/grid.in)包含所有坐标。点表的排列是 x 最慢、z 最快；绘图脚本仍按坐标筛选和重排，不假设屏幕上第几行恰好对应哪一个网格位置。`nbnd=8` 保留本例的四条价带和四条导带，后面只取第 5 条画最低导带。

```text
[preston@preston-System-Product-Name si-pbe]$ cat band3d/run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-3d
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
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in grid.in > grid.out 2> grid.err
[preston@preston-System-Product-Name si-pbe]$
```


```text
[preston@preston-System-Product-Name si-pbe]$ cd band3d
[preston@preston-System-Product-Name band3d]$ sbatch run.sh
Submitted batch job 786
[preston@preston-System-Product-Name band3d]$ cd ..
```

这个计算没有离子优化步骤，时间主要花在给定密度下的 891 组本征态上。输出中应核对实际 k 点数和能带数，而不是只相信输入点表。

```text
[preston@preston-System-Product-Name si-pbe]$ grep -E 'number of k points|number of Kohn-Sham states|JOB DONE' band3d/grid.out
     number of Kohn-Sham states=            8
     number of k points=   891
   JOB DONE.
[preston@preston-System-Product-Name si-pbe]$
```


这次输出确实读入了 891 个 k 点和 8 条 Kohn–Sham 能带，结束前没有本征值未收敛提示。原生 WALL 时间约 2 分 46 秒，完整输出为[grid.out](/Atlas/examples/si-pbe/band3d/grid.out)。

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 12 band3d/grid.out
     davcio       :      0.05s CPU      0.06s WALL (    1782 calls)

     Parallel routines

     PWSCF        :   2m38.43s CPU   2m45.66s WALL


   This run was terminated on:  21:44:35  22Sep2026

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name si-pbe]$
```


能量从[同一次计算的 XML](/Atlas/examples/si-pbe/band3d/data-file-schema.xml)提取。XML 本征值的 Hartree 单位转成 eV，k 的 `tpiba` 坐标转成 Å⁻¹；两套 k 坐标一并放进 `cube.csv`，以后换坐标或做拟合时能追得回去。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 7 band3d/cube.csv
kx_tpiba,ky_tpiba,kz_tpiba,kx_inv_A,ky_inv_A,kz_inv_A,band5_eV
0.75,-0.08,-0.08,0.8730514280371566,-0.09312548565729671,-0.09312548565729671,7.244655010325953
0.75,-0.08,-0.06,0.8730514280371566,-0.09312548565729671,-0.06984411424297253,7.20368463842487
0.75,-0.08,-0.04,0.8730514280371566,-0.09312548565729671,-0.046562742828648356,7.175249538627218
0.75,-0.08,-0.02,0.8730514280371566,-0.09312548565729671,-0.023281371414324178,7.158593176093672
0.75,-0.08,0.0,0.8730514280371566,-0.09312548565729671,0.0,7.153117253788684
0.75,-0.08,0.02,0.8730514280371566,-0.09312548565729671,0.023281371414324178,7.158593176093675
[preston@preston-System-Product-Name si-pbe]$
```


其中 `band5_eV` 是每个点的第 5 条能带。图中的零点采用这个立方网格内采样到的最小值，并不宣称它就是连续函数的精确谷底。x 的间隔只有 0.02，采样最低点落在 0.85 附近；[有效质量](/Atlas/m/effective-mass/qe/)中更细的线采样把谷底进一步定位到约 0.8443。

将[完整三维数据表](/Atlas/examples/si-pbe/band3d/cube.csv)、[绘图脚本](/Atlas/examples/si-pbe/plot_si.py)放回示例目录后运行：

```text
[preston@preston-System-Product-Name si-pbe]$ python3 plot_si.py band3d
<工作目录>/si-pbe/plots/band-3d.png
```

![Si 局部三维 k 网格中的两张导带能量切面](/Atlas/examples/si-pbe/plots/band-3d.png)

左图在 `kz=0` 平面上画 `E(kx,ky)`，沿谷的纵向 x 弯得较缓，沿横向 y 弯得较陡。右图固定 `kx=0.85×2π/a`，画 `E(ky,kz)`；两个横向相似。这与同一组模型下约 `0.956 mₑ` 的纵向质量、约 `0.192 mₑ` 的横向质量相互对应：更平的能带有更大的曲率质量。

两张图都是**从实际三维点阵取出的二维切面，能量作为竖轴**。竖轴不是第三个 k 坐标；整份三维采样在 `cube.csv` 中。改变绘图视角不会增加新的 k 点。若要画整个布里渊区的等能面，应先扩展完整采样区域，或者建立经过直接计算核对的插值，再指定等能值；不能把这个局部立方体当作全区费米面。

这次使用的是固定晶胞、PBE、无 SOC 的非磁性 Si。图能展示该模型下这个导带谷的空间形状，不自动提供别的能带、别的谷或金属费米面的完整信息。

下一步：从同一网格可以回到[有效质量](/Atlas/m/effective-mass/qe/)做局部曲率检查；关注金属等能面时接[费米面](/Atlas/m/fermi-surface/qe/)。

```text
SCF 密度 → 已定位的带边区域 → 真实三维 k 点表
                                  ↓
                           逐点本征值与单位转换
                                  ↓
                        保留完整点阵 → 选择切面作图
```
