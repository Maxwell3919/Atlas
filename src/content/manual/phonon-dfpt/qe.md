参考：

- QE 官方文档 INPUT_PH：<https://www.quantum-espresso.org/Doc/INPUT_PH.html>
- QE 官方文档 INPUT_Q2R：<https://www.quantum-espresso.org/Doc/INPUT_Q2R.html>
- QE 官方文档 INPUT_MATDYN：<https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html>
- PHonon 用户指南：<https://www.quantum-espresso.org/Doc/user_guide/>

## Phonon 声子计算

声子描述的是晶格中原子偏离平衡位置的集体振动。通过计算全布里渊区的声子色散曲线，我们可以确认结构是否具有动力学稳定性（全区无虚频），这是进行后续性质分析的物理基石。

声子计算的数据流具有严格的单向依赖关系：

```text
优化后结构
   ↓
单点 static SCF (高收敛标准 conv_thr = 1d-12)
   ↓
Γ 点测试: gamma/ph.in → dynmat.x (检查 Γ 点声学支与虚频)
   ↓ 确认无误
全布里渊区: 8×8×1 q 网格分批 ph.x
   ↓ 生成全套 .dyn 文件
q2r.x (反变换至实空间力常数 .fc)
   ↓
matdyn.x (插值生成 Γ-M-K-Γ 声子谱)
   ↓ 验收动力学稳定性
[进入后续物理计算]
```

**每一步结束并检查后，再提交下一步，不要把这些 sbatch 一次全部执行。** 依赖链上前一步的产物是后一步的输入；q 分批之间没有依赖，可以并行，但 q2r 必须等全部 q 批完成。

## 第一步：Γ 点之前的 static SCF

进入 `10_phonon/gamma` 目录，SCF 沿用前面提取的候选几何，并把电子收敛阈值收紧到 `1d-12`（声子对密度精度的要求比普通静态 SCF 高）。`nbnd` 与后续密网格保持一致，避免读取本征值时带数不一致：

```bash
[<user>@<cluster> 10_phonon/gamma]$ cat > scf.in <<'EOF'
&CONTROL
  calculation = 'scf'
  outdir = './out/'
  prefix = '<prefix>'
  pseudo_dir = '<赝势库路径>'
  tprnfor = .true.
  tstress = .true.
  verbosity = 'high'
/

&SYSTEM
  ibrav = 0
  nat = 6
  ntyp = 4
  nbnd = 40
  ecutwfc = 90
  ecutrho = 720
  input_dft = 'vdw-DF3-opt1'
  force_symmorphic = .true.
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 3.7d-3
/

&ELECTRONS
  conv_thr = 1.0d-12
  electron_maxstep = 200
  mixing_beta = 4.0d-01
/

ATOMIC_SPECIES
（与结构优化相同，略）

CELL_PARAMETERS (angstrom)
! 此处放入你的结构块：三行晶胞矢量

ATOMIC_POSITIONS (crystal)
! 此处放入你的结构块：原子坐标行

K_POINTS (automatic)
24 24 1 0 0 0
EOF
```

```bash
[<user>@<cluster> 10_phonon/gamma]$ cat > scf.slurm <<'EOF'
#!/bin/bash
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

# unlimit memory
ulimit -s unlimited
ulimit -l unlimited

# load path
source /data/intel/oneapi/setvars.sh

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

cd $SLURM_SUBMIT_DIR

mpirun -np 56 <qe_bin>/pw.x<scf.in>scf.out
EOF
```

```bash
sbatch scf.slurm
```

运行时查看：

```bash
squeue -u <user>
tail -f scf.out
```

结束后检查电子收敛、错误、力与应力：

```bash
grep -E 'convergence has been achieved|convergence NOT achieved|JOB DONE|Error in routine' scf.out
grep '^!' scf.out | tail -n 1
grep 'the Fermi energy is' scf.out | tail -n 1
grep -A9 'Forces acting on atoms' scf.out | tail -n 10
grep -A4 'total   stress' scf.out | tail -n 5
```

先确认 SCF 正常收敛、每个原子的力与面内应力可接受；如果需要继续优化结构，就停在这里处理，统一更新后续输入，不要接声子。

## 第二步：Γ 点声子

同一个 `gamma` 目录准备 `ph.in`。保持与本目录 SCF 相同的 `prefix` 和 `outdir`，先只做 Γ 点，不开启 EPC：

```bash
[<user>@<cluster> 10_phonon/gamma]$ cat > ph.in <<'EOF'
&INPUTPH
  prefix = '<prefix>'
  outdir = './out/'
  tr2_ph = 1.0d-16
  nmix_ph = 16
  verbosity = 'high'
  amass(1) = 178.49
  amass(2) = 35.45
  amass(3) = 207.20
  amass(4) = 15.999
  trans = .true.
  epsil = .false.
  fildyn = 'gamma.dyn'
  ldisp = .false.
  recover = .false.
/
0.0 0.0 0.0
EOF
```

与 ldisp 网格模式不同：`ldisp=.false.` 时不用 nq1/nq2/nq3，而是像上面那样在文件末尾直接给出 q 点列表（这里就是 Γ 点 `0.0 0.0 0.0`）。Slurm 脚本与 scf 相同，只把执行行换成：

```bash
mpirun -np 56 <qe_bin>/ph.x<ph.in>ph.out
```

提交后一段时间，用这条看当前最有用的进度：

```bash
grep -E \
'There are.*irreducible representations|Representation #|Self-consistent Calculation|iter #|Convergence has been achieved|End of self-consistent calculation|Diagonalizing|omega|JOB DONE' \
ph.out | tail -n 100
```

典型输出结构如下（真实记录节选，附逐行解释）：

```text
      iter #  14 total cpu time :   331.5 secs   av.it.:  22.4
     End of self-consistent calculation      ← 该模式的 SCF 计算结束
     Convergence has been achieved           ← 该模式已收敛（好消息）
     Representation #   2 mode #   2         ← 正在处理第 2 个不可约表示
     Self-consistent Calculation             ← 开始对该模式做 DFPT 自洽
      iter #   1 total cpu time :   346.4 secs   av.it.:  10.8
      ...
      iter #  14 total cpu time :   630.8 secs   av.it.:  20.5
     End of self-consistent calculation
     Convergence has been achieved
     Representation #   3 mode #   3
      ...
```

ph.x 在 Γ 点会把 3N 个原子位移按对称性分解成若干不可约表示，然后逐个求解 DFPT 线性响应；输出就是 `Representation # n → SCF iterations → Convergence → Representation # n+1` 的循环结构。全部表示收敛后出现频率表与 `JOB DONE.`。

## 第三步：全布里渊区 8×8×1 分批

Γ 点确认无误后铺全网格。8×8×1 共 10 个不等价 q 点，按 `start_q/last_q` 切四批，每批一个输入文件、各自 sbatch 并行（批间无依赖）：

| 文件 | start_q | last_q |
|---|---|---|
| phx.in | 1 | 1 |
| phx1.in | 2 | 4 |
| phx2.in | 5 | 7 |
| input_tmp.in | 8 | 10 |

四份文件除 `start_q/last_q` 外逐字相同（diff 核验过），namelist 形如：

```fortran
&inputph
  tr2_ph = 1.0d-16
  nmix_ph = 12
  verbosity = 'high'
  prefix = '<prefix>'
  fildvscf = 'zrclsccdv'
  amass(1) = 91.224
  amass(2) = 35.450
  amass(3) = 44.956
  amass(4) = 12.011
  outdir = './out/'
  fildyn = 'zrclscc.dyn'
  trans = .true.
  ldisp = .true.
  start_q = 1
  last_q = 1
  nq1 = 8
  nq2 = 8
  nq3 = 1
/
```

要接电声链时再加三个键（见电声耦合页）：`electron_phonon = 'interpolated'`、`el_ph_sigma = 0.001`、`el_ph_nsigma = 20`。验收照旧：

```bash
grep -l "JOB DONE" phx*.out
```

## 第四步：q2r.x 合并力常数

全部 q 批 JOB DONE 之后：

```bash
[<user>@<cluster> ph64]$ cat > q2rx.in <<'EOF'
&input
zasr = 'crystal'
fildyn = 'zrclscc.dyn'
flfrc = 'zrclscc.fc'
/
EOF
```

```bash
q2r.x -i q2rx.in > q2rx.out
```

成功标志：输出出现 `fft-check success`，并生成 `zrclscc.fc`。`zasr='crystal'` 施加声学求和规则，消除 Γ 点小残差。

## 第五步：matdyn.x 沿路径内插

```bash
[<user>@<cluster> ph64]$ cat > matdynxline.in <<'EOF'
&input
  asr = 'crystal'
  amass(1) = 91.224
  amass(2) = 35.450
  amass(3) = 44.956
  amass(4) = 12.011
  flfrc = 'zrclscc.fc'
  flfrq = 'zrclscc.freq'
  dos = .false.
  q_in_band_form = .true.
  q_in_cryst_coord = .true.
/
4
0.0000000000   0.0000000000   0.0000000000 50    !G
0.5000000000   0.0000000000   0.0000000000 50    !M
0.3333333333   0.3333333333   0.0000000000 50    !K
0.0000000000   0.0000000000   0.0000000000  1    !G
/
EOF
```

```bash
matdyn.x -i matdynxline.in > matdynxline.out
```

六方体系 G-M-K-G 路径每段 50 个点。产物对号：`.dyn0`（q 清单）→ `.dyn1…dynN`（各 q 动力学矩阵）→ `.fc`（力常数）→ `.freq/.freq.gp`（色散频率）→ `matdyn.modes`（本矢）。

拿到谱之后的第一件事是判虚频——见虚频/软模判据页。

## 下一步

```text
DFPT 声子（本页）
    ↓ 谱无结构失稳
虚频/软模判据 → 电声耦合（la2F 变体）→ λ(ω) 谱函数
```
