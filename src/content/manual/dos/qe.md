[dos.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_DOS.html) · [projwfc.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html) · [QE 后处理手册](https://www.quantum-espresso.org/Doc/pp_user_guide/)

## 在能量轴上数状态，先用均匀 k 网格

这里接 [Si 的 24³ NSCF](/Atlas/m/nscf/qe/)。那一页已经保留 8 条能带并检查本征值求解；`dos.x` 在这些带能量上做布里渊区加权，不再求一份新的电荷密度。高对称路径的点分布服务于画线，不能代替这里的均匀采样。

本例文件可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。保留解包后的 `si-pbe` 目录结构，绘图只需 NumPy 与 Matplotlib；计算使用的赝势按 [SCF 页](/Atlas/m/scf/qe/)准备。

下载包保留输入、输出、单独保存的 XML和作图数据，没有包含可接续计算的 `tmp/si.save` 电荷密度与波函数。阅读输出和重新作图可直接使用包内文件；重新运行 QE 时，先按 [SCF 页](/Atlas/m/scf/qe/)生成保存目录，再复制到对应计算目录。DOS 和轨道投影还需要先完成匹配的 [NSCF](/Atlas/m/nscf/qe/)。

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

开头的 DOS 约 10⁻⁸⁵，位于本次能带范围以外。这个小数不能单独被命名为某种物理“下限”；应结合采样能区、有限展宽与程序的数值处理来读。再看文件末尾：

```text
[preston@preston-System-Product-Name dos-cg]$ tail -n 4 si.dos.dat
  15.940  0.2460E-01  0.1597E+02
  15.960  0.2901E-01  0.1597E+02
  15.980  0.3403E-01  0.1597E+02
  16.000  0.3945E-01  0.1597E+02
```
积分到 16 eV 时约为 15.97 个态，接近 8 条带乘自旋简并的 16；它包含空态，因此不是应当等于整胞 8 个电子的电子数验收。有限能窗也可能漏掉高能端的部分带和展宽尾部。

## 从原始能量转到相对价带顶的图

在解包后的 `si-pbe` 目录运行：

```bash
python3 plot_si.py dos
```

![Si 的总态密度，能量相对同一 24³ NSCF 的价带顶](/Atlas/examples/si-pbe/plots/dos.png)

脚本读取 `dos-cg/si.dos.dat` 的前两列，并从 `gap-results.json` 读取同一 `gap24-cg` 的 VBM，再平移能量轴。图中的阴影只是曲线下方的填色，不代表某种元素或轨道投影。完整[绘图脚本](/Atlas/examples/si-pbe/plot_si.py)与[原始 DOS 表](/Atlas/examples/si-pbe/dos-cg/si.dos.dat)可以单独下载。

Gaussian 展宽会把带边附近的权重扩展到相邻能量，不能从这一张有展宽的图上量出高精度带隙。带边位置与采样依赖回到 [带隙页](/Atlas/m/band-gap/qe/)核对；DOS 峰形需要另做 k 网格与展宽的交叉比较。

## 下一步

需要 s/p 总贡献时进入 [投影与布居](/Atlas/m/population-analysis/qe/)；需要知道每个 k、每条带的 s/p 权重时进入 [胖带](/Atlas/m/fatband/qe/)。后者保留 k 分辨信息，与沿整个布里渊区积分的 PDOS 用途不同。

```text
SCF → 均匀 NSCF → dos.x → 总 DOS 与累计态数
                 └─ projwfc.x → 轨道投影与布居
SCF → 路径 bands ── projwfc.x → 逐 k 胖带
```
