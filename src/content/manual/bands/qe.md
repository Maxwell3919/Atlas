[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html) · [QE 后处理手册](https://www.quantum-espresso.org/Doc/pp_user_guide/)

## 沿 Γ–X–W–K–Γ–L–X 看 Si 的能级怎样变化

这里沿用 [Si SCF](/Atlas/m/scf/qe/)的固定结构与密度，单独建立一条高对称路径。前面的均匀 [NSCF](/Atlas/m/nscf/qe/)用于 DOS 与布里渊区采样；本页不重做那套流程，而是在相同父 SCF 上求指定路径的本征值。

例子使用 QE 7.5、PBE、两个 Si 原子、无 SOC。当前坐标与原胞约定对应下面的路径；换晶胞基矢后，不能只保留这些点的标签和数字。

本例文件可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。保留解包后的 `si-pbe` 目录结构，绘图只需 NumPy 与 Matplotlib；计算使用的赝势按 [SCF 页](/Atlas/m/scf/qe/)准备。

下载包保留输入、输出、单独保存的 XML和作图数据，没有包含可接续计算的 `tmp/si.save` 电荷密度与波函数。阅读输出和重新作图可直接使用包内文件；重新运行 QE 时，先按 [SCF 页](/Atlas/m/scf/qe/)生成保存目录，再复制到对应计算目录。DOS 和轨道投影还需要先完成匹配的 [NSCF](/Atlas/m/nscf/qe/)。

对应的 [bands.err](/Atlas/examples/si-pbe/bands-cg/bands.err) 为 1604 字节，保留了重复的 `Authorization required, but no authorization protocol specified` 环境提示，以及 `IEEE_DENORMAL` 浮点非正规数提示。本轮最终输出没有未收敛本征值行，后处理读到了完整的 8 条带、121 个路径点；验收时应把这些结果与原始 stderr 一起检查。

## 输入中的四列分别是什么

先把 `scf/tmp` 复制到独立的 `bands-cg` 目录，用 `vi bands.in` 编辑。本次实际输入完整列在下面：

```text
[preston@preston-System-Product-Name bands-cg]$ cat bands.in
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
K_POINTS tpiba_b
7
0.0 0.0 0.0 24
1.0 0.0 0.0 12
1.0 0.5 0.0 12
0.75 0.75 0.0 24
0.0 0.0 0.0 24
0.5 0.5 0.5 24
1.0 0.0 0.0 1
```
`tpiba_b` 的前三列是以 2π/a 为单位的笛卡尔 k 坐标，第四列控制到下一个节点的路径采样。7 行是 7 个节点，程序展开后得到 121 个实际 k 点，不是只算 7 个点。`nbnd=8` 保留 4 条占据带与 4 条空带。

本例使用 CG 复算后的干净结果；此前包含未收敛本征值警告的一轮保留在其他目录。求解器的选择与输出核对见 [NSCF 页](/Atlas/m/nscf/qe/)，图源没有沿用那一轮警告数据。

```text
[preston@preston-System-Product-Name bands-cg]$ cat run.sh
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
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in bands.in > bands.out 2> bands.err
```
提交使用 `sbatch run.sh`，运行时用 `tail -f bands.out` 查看当前点。结束后，除了队列状态，还要读 `bands.err`，检查 121 个点、8 条能带、未收敛本征值警告与正常收尾。

## bands.x 整理刚才的路径结果

`pw.x` 完成路径本征值求解后，`bands.x` 才读取同一份 `prefix/outdir` 并导出作图文件：

```text
[preston@preston-System-Product-Name bands-cg]$ cat bands-post.in
&BANDS
  prefix = 'si'
  outdir = './tmp'
  filband = 'si.bands.dat'
  lsym = .false.
/
```
`lsym=.false.` 在本例中不做不可约表示分类；默认 `no_overlap=.true.` 也没有启用相邻点重叠最大化排序。因此图上的连接按输出带序绘制，在简并与交叉处不要据此断言某条线始终保持同一种轨道身份。需要轨道身份时，继续读取同路径的 [胖带](/Atlas/m/fatband/qe/)。

```bash
<qe_bin>/bands.x -in bands-post.in > bands-post.out 2> bands-post.err
```

```text
     Reading collected, re-writing distributed wavefunctions
     high-symmetry point:  0.0000 0.0000 0.0000   x coordinate   0.0000
     high-symmetry point:  1.0000 0.0000 0.0000   x coordinate   1.0000
     high-symmetry point:  1.0000 0.5000 0.0000   x coordinate   1.5000
     high-symmetry point:  0.7500 0.7500 0.0000   x coordinate   1.8536
     high-symmetry point:  0.0000 0.0000 0.0000   x coordinate   2.9142
     high-symmetry point:  0.5000 0.5000 0.5000   x coordinate   3.7802
     high-symmetry point:  1.0000 0.0000 0.0000   x coordinate   4.6463

     Plottable bands (eV) written to file si.bands.dat.gnu
     Bands written to file si.bands.dat

     BANDS        :      1.02s CPU      1.11s WALL


   This run was terminated on:  22: 2:52  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
`si.bands.dat` 有一个 `&plot` 表头，后面按 k 坐标与能量分组；`.gnu` 则按能带分块，每块两列，块间空行。先看两种文件的开头：

```text
[preston@preston-System-Product-Name bands-cg]$ head -n 6 si.bands.dat
 &plot nbnd=   8, nks=   121 /
            0.000000  0.000000  0.000000
   -5.692    6.397    6.397    6.397    8.967    8.967    8.967    9.969
            0.041667  0.000000  0.000000
   -5.685    6.347    6.363    6.363    8.947    9.010    9.010   10.018
            0.083333  0.000000  0.000000
```

```text
[preston@preston-System-Product-Name bands-cg]$ head -n 6 si.bands.dat.gnu
    0.0000   -5.6925
    0.0417   -5.6848
    0.0833   -5.6616
    0.1250   -5.6231
    0.1667   -5.5691
    0.2083   -5.4998
```
`.gnu` 第一列是沿路径累计的距离，第二列已经是 eV。不能把每一行当作不同能带，也不能再次把能量乘 Ry→eV 的换算常数。

## 画图时明确能量零点

这张图把路径上第 4 条带的最大值设为零，即本例的 VBM；没有使用另一材料的费米能文件。下载包中的 `plot_bands.py` 直接读取 `si.bands.dat.gnu`，核对 8×121 个点和每条带相同的横坐标，再统一减去 6.3970 eV。

```bash
python3 plot_bands.py
```

![Si 路径能带，能量相对同一路径的价带顶](/Atlas/examples/si-pbe/plots/bands-direct.png)

能带图适合看路径上能级如何分散，不能保证路径经过全布里渊区的真实极值。直接/间接带隙的判定与采样对照见 [带隙页](/Atlas/m/band-gap/qe/)；导带谷附近的曲率见 [有效质量](/Atlas/m/effective-mass/qe/)。

下一步：需要 s/p 成分时进入 [逐 k 胖带](/Atlas/m/fatband/qe/)，保留本页的相同 k 点与带号；需要态数分布时进入 [DOS](/Atlas/m/dos/qe/)，读取均匀网格分支。

```text
同一 SCF 密度 → 路径 bands → bands.x → 原始 eV 数据 → 统一能量零点
                              └─ projwfc.x → 逐k逐带投影
均匀 NSCF ──────────────────────────────→ DOS
```
