[dos.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_DOS.html) · [projwfc.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html) · [QE 后处理手册](https://www.quantum-espresso.org/Doc/pp_user_guide/)

## 在能量轴上数状态，先用均匀 k 网格

这里接 [Si 的 24³ NSCF](/Atlas/m/nscf/qe/)。那一页已经保留 8 条能带并检查本征值求解；`dos.x` 在这些带能量上做布里渊区加权，不再求一份新的电荷密度。高对称路径的点分布服务于画线，不能代替这里的均匀采样。

本例文件可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。保留解包后的 `si-pbe` 目录结构，绘图只需 NumPy 与 Matplotlib；计算使用的赝势按 [SCF 页](/Atlas/m/scf/qe/)准备。

下载包保留输入、输出、XML 与作图数据，未打包 `tmp/si.save` 中的电荷密度和波函数。阅读输出、重新作图可直接使用包内文件；重新计算时，先完成 [24³ NSCF](/Atlas/m/nscf/qe/)，再把这份保存数据复制到本页的 `dos-cg` 目录。

## 让 dos.x 读取正确的那份保存数据

本次从已检查的 `gap24-cg/tmp` 复制到 `dos-cg/tmp`，后处理有自己的目录。用 `vi dos.in` 保存下列实际输入：

```text
[preston@preston-System-Product-Name dos-cg]$ cat dos.in
&DOS
  prefix = 'si'
  outdir = './tmp'
  fildos = 'si.dos.dat'
  Emin = -8.0
  Emax = 16.0
  DeltaE = 0.02
  ngauss = 0
  degauss = 0.01
/
```
`Emin/Emax/DeltaE` 使用 **eV**，而 `degauss` 使用 **Ry**。这里 0.01 Ry 约为 0.1361 eV，不能把它读成 0.01 eV。`ngauss=0` 选择普通 Gaussian 展宽；能量轴上采样更密只会让曲线绘得更细，并没有增加电子 k 点。

`DeltaE=0.02 eV` 比这次的展宽小，用来在能量轴上取足够细的绘图点；曲线看起来平滑，不等于能分辨 0.02 eV 的细节。减小 `degauss` 后，原先被抹平的细节和 k 采样造成的锯齿都可能出现，需要配合更密的 NSCF 网格比较。`Emin=-8`、`Emax=16` 只规定本次输出能窗；若想分析更高能量，先核对 8 条带是否已经覆盖，而不是只扩大这两个数。

`dos.x` 根据保存的带能量和权重计算总 DOS，本身不需要再读取所有波函数。需要轨道投影时，`projwfc.x` 才沿另一条依赖读取相应波函数，见 [布居与投影](/Atlas/m/population-analysis/qe/)。

```text
[preston@preston-System-Product-Name dos-cg]$ cat run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-dos
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
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/dos.x -in dos.in > dos.out 2> dos.err
```
这份短后处理仍以 Slurm 脚本运行，`sbatch run.sh` 提交后，先读 `dos.out` 和 `dos.err`，确认保存目录、交换关联设置和展宽都与预期对应。本次输出中的这几段是：

```text
     Reading xml data from directory:

     ./tmp/si.save/

     IMPORTANT: XC functional enforced from input :
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)
     Any further DFT definition will be discarded
     Please, verify this is what you really want
```

```text
     Gaussian broadening (read from input): ngauss,degauss=   0    0.010000


     DOS          :      0.70s CPU      0.73s WALL


   This run was terminated on:  22: 2:58  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
本次实际 WALL 时间为 0.73 s。[dos.err](/Atlas/examples/si-pbe/dos-cg/dos.err) 为 1300 字节，包含重复的 `Authorization required, but no authorization protocol specified` 环境提示；原始文件随结果保留。本轮已写出完整 DOS 表，输出未见致命错误。`JOB DONE.` 表明这一步执行完毕；图的可靠范围仍取决于 NSCF 的空带数、k 网格与后处理展宽。

## 数据文件的第三列不是“又一条 DOS”

```text
[preston@preston-System-Product-Name dos-cg]$ head -n 6 si.dos.dat
#  E (eV)   dos(E)     Int dos(E) EFermi =    6.397 eV
  -8.000  0.9182E-85  0.1836E-86
  -7.980  0.9182E-85  0.3673E-86
  -7.960  0.9182E-85  0.5509E-86
  -7.940  0.9182E-85  0.7345E-86
  -7.920  0.9182E-85  0.9182E-86
```
三列依次为能量 eV、总 DOS（states/eV/cell）和累计态数。这里是非自旋极化体系，总 DOS 已计入自旋简并；不要再额外乘 2。

这里的 cell 是输入中的两原子 Si 原胞。若报告每原子 DOS，曲线与累计态数都除以 2，纵轴同步改成 `states/eV/atom`。换超胞后不归一化，量级会随胞内态数变化，不能据此判断电子态增多。

第三列从文件下限累计态数。在占据区上方、导带开始之前的平台，可结合 8 个价电子检查归一化；高能端继续增长，是因为开始累计空态。共线自旋极化 `nspin=2` 则有 `E、DOSup、DOSdw、Int DOS` 四列，总 DOS 为 up+down；将 down 镜像到负侧只是显示约定，求和不能使用镜像后的负数。SOC/非共线输出需按自己的表头解析，本例脚本限定非自旋三列格式。

开头的 DOS 约 10⁻⁸⁵，位于本次能带范围以外。这个小数不能单独被命名为某种物理“下限”；应结合采样能区、有限展宽与程序的数值处理来读。再看文件末尾：

```text
[preston@preston-System-Product-Name dos-cg]$ tail -n 4 si.dos.dat
  15.940  0.2460E-01  0.1597E+02
  15.960  0.2901E-01  0.1597E+02
  15.980  0.3403E-01  0.1597E+02
  16.000  0.3945E-01  0.1597E+02
```
积分到 16 eV 时约为 15.97 个态，接近 8 条带乘自旋简并的 16；它包含空态，因此不是应当等于整胞 8 个电子的电子数验收。有限能窗也可能漏掉高能端的部分带和展宽尾部。

独立对打印数据做梯形积分得到 `15.97326485`，与第三列末尾 `15.97` 在打印精度内相符。用同一 `gap24-cg` 的价带顶 `6.397028955497 eV` 和采样导带底 `6.937158523640 eV` 定位带隙中点，读取累计列得到 `8.0000`。

在价带顶本身，累计列约为 `7.997`：Gaussian 展宽将部分边缘谱重带到了价带顶以上。不能为了让该端点等于整数而重新缩放曲线。`degauss` 是 QE 的展宽参数，不是能量步长、仪器分辨率或真实温度。

## 从原始能量转到相对价带顶的图

在解包后的 `si-pbe` 目录运行：

```bash
python3 plot_si.py dos
```

![Si 的总态密度，能量相对同一 24³ NSCF 的价带顶](/Atlas/examples/si-pbe/plots/dos.png)

脚本读取 `dos-cg/si.dos.dat` 的前两列，并从 `gap-results.json` 读取同一 `gap24-cg` 的 VBM，再平移能量轴。图中的阴影只是曲线下方的填色，不代表某种元素或轨道投影。完整[绘图脚本](/Atlas/examples/si-pbe/plot_si.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/si-pbe/atlas_plot_style.py)）与[原始 DOS 表](/Atlas/examples/si-pbe/dos-cg/si.dos.dat)可以单独下载。

Gaussian 展宽会把带边附近的权重扩展到相邻能量，不能从这一张有展宽的图上量出高精度带隙。带边位置与采样依赖回到 [带隙页](/Atlas/m/band-gap/qe/)核对；DOS 峰形需要另做 k 网格与展宽的交叉比较。

图上 0 eV 是同一父链的价带顶，正能侧的 Gaussian 尾巴不能单独判为金属性。比较峰位和峰高前，先固定每原胞/每原子的归一化、能量参考和展宽。

区分 s/p 可读已有[布居页](/Atlas/m/population-analysis/qe/)的均匀 18³ 分支。它与本页 24³ DOS 的网格不同；下面只核对该 18³ 分支内部的关系，不把它逐行扣到 24³ 曲线上。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 4 population-cg/si.pdos_tot
# E (eV)  dos(E)    pdos(E)
  -6.101  0.475E-06  0.473E-06
  -6.081  0.120E-05  0.119E-05
  -6.061  0.291E-05  0.290E-05
[preston@preston-System-Product-Name si-pbe]$ head -n 4 'population-cg/si.pdos_atm#1(Si)_wfc#2(p)'
# E (eV)   ldos(E)   pdos(E)    pdos(E)    pdos(E)   
  -6.101  0.394E-08  0.131E-08  0.131E-08  0.131E-08
  -6.081  0.104E-07  0.347E-08  0.347E-08  0.347E-08
  -6.061  0.265E-07  0.883E-08  0.883E-08  0.883E-08
```

`si.pdos_tot` 第二列是该分支总 DOS，第三列是所有投影态的 PDOS 和，不能将两列相加。p 文件第二列 `ldos` 已是三个 p 分量之和，后三列依次 `pz、px、py`；加完后三列再加第二列，会把 p 权重数两次。s 文件的 ldos 与唯一 s 分量同样重复表示同一壳层。

整胞投影和应取两个原子的 s 文件各一份 ldos，加上两个原子的 p 文件各一份 ldos，对应 `si.pdos_tot` 第三列。有限投影空间未覆盖的部分保留下来，不能强行放大 PDOS 去等于总 DOS。本例文本只保留有限有效位数，逐行求和最大差 `0.006 states/eV/cell`，全部在各列舍入界内；不能把这点打印差当成额外丢失的物理态。

共线自旋极化时，`pdos_tot` 变为 `E、DOSup、DOSdw、PDOSup、PDOSdw`；原子文件也分别给 up/down 的 ldos 和 m 分量。按同一自旋、同一能量点求和后，再合并通道。本例非磁数据已含自旋简并，不再乘 2。

## 下一步

需要 s/p 总贡献时进入 [投影与布居](/Atlas/m/population-analysis/qe/)；需要知道每个 k、每条带的 s/p 权重时进入 [胖带](/Atlas/m/fatband/qe/)。后者保留 k 分辨信息，与沿整个布里渊区积分的 PDOS 用途不同。

```text
SCF → 均匀 NSCF → dos.x → 总 DOS 与累计态数
                 └─ projwfc.x → 轨道投影与布居
SCF → 路径 bands ── projwfc.x → 逐 k 胖带
```
