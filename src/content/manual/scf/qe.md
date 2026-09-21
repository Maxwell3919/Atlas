# QE 自洽（scf）：一次应变扫描批次的完整案例

**参考**：[INPUT_PW 文档](https://www.quantum-espresso.org/Doc/INPUT_PW.html)（&CONTROL/&SYSTEM/&ELECTRONS 全部参数）

本页目标：走一遍 QE 自洽从写输入到验收判读的全流程。案例是一套应变扫描批次（ZrCl2/Sc2C 界面，多个形变目录），每个目录一套 scf，后续能带/态密度链都把「本目录 scf 正常结束」当门槛。

## 输入文件：pwx.in

真实主例逐参数注释（坐标块按你的体系替换）：

```fortran
&CONTROL
  calculation = 'scf'
  outdir = '<outdir>'            ! 原 './out/'，电荷/波函数都写这里
  prefix = '<prefix>'            ! 本例 'zrclscc'，产物文件名随之
  pseudo_dir = '<赝势库路径>'
! tprnfor = .true.                ! 需要打印力时再打开
! tstress = .true.                ! 需要应力时再打开
  verbosity = 'high'             ! 高输出，便于 grep 判读
/
&SYSTEM
  ibrav = 0,                     ! 自定义晶胞，用 CELL_PARAMETERS 卡
  nat = 6,                       ! ZrCl2/Sc2C 界面 6 原子
  ntyp = 4,                      ! Zr, Cl, Sc, C
  ecutwfc = 100,                 ! 已做收敛测试
  ecutrho = 800,                 ! 8 倍关系，PAW 惯例
  input_dft = 'vdw-DF3-opt1'     ! 层状体系必须 vdW 修正
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 3.7d-3               ! Ry；与后续 PROJWFC 展宽配套
/
&ELECTRONS
  conv_thr = 1.0000000000d-12    ! 能量判据很紧，为后处理留余量
  mixing_beta = 4.0000000000d-01
/
&ions
/
&cell
/
ATOMIC_SPECIES
Zr  91.224  Zr.pbe-spn-kjpaw_psl.1.0.0.UPF
Cl  35.450  Cl.pbe-n-kjpaw_psl.1.0.0.UPF
Sc  44.956  Sc.pbe-spn-kjpaw_psl.1.0.0.UPF
C   12.011  C.pbe-n-kjpaw_psl.1.0.0.UPF
CELL_PARAMETERS (angstrom)
（替换为你的结构块；本例 a≈3.31 Å，c=40.0 Å 真空方向）
ATOMIC_POSITIONS (crystal)
（替换为你的结构块）
K_POINTS automatic
  32 32 1 0 0 0                  ! 面内 32×32、真空方向 1
```

注意 `&ions`/`&cell` 是两个空 namelist——从弛豫输入模板继承而来，空着无害。批处理目录间唯一变化的就是结构块。

## 命令主线

提交用作业脚本（目录内备有 pwx.slurm 一类脚本），等价单条命令：

```bash
sbatch pwx.slurm
mpirun -np 32 pw.x < pwx.in > pwx.out 2>&1
squeue -u <user>        # 队列清空 ≠ 全部成功，成败要看输出文件
```

## 判读三件套

```bash
grep "JOB DONE" pwx.out
```

```text
   JOB DONE.
```

```bash
grep "! total energy" pwx.out
```

```text
!    total energy              =    -208.22938097 Ry
```

判据：`JOB DONE.` 存在，且输出末段有一条 `!` 前缀的最终总能量行——不带 `!` 的行是迭代过程值，不能当结果用。若出现 `convergence NOT achieved`，无论其他行多好看，一律 FAIL，调 `mixing_beta` 或放宽 `conv_thr` 重投。

更大范围的批次盘点用本页唯一小工具（三分类循环，逐个 `.out` 判 DONE/ERROR/RUNNING）：

```bash
find . -name '*.out' | while read -r f; do
  if grep -q "JOB DONE" "$f" 2>/dev/null; then st="DONE"
  elif grep -qiE "Error|CRASH|stopped" "$f" 2>/dev/null; then st="ERROR"
  else st="RUNNING/INCOMPLETE"; fi
  calc=$(grep -m1 -E "calculation\s*=" "$f" 2>/dev/null | head -1)
  echo "[$st] $f $calc"
done
```

注意 `RUNNING/INCOMPLETE` 不等于崩溃：可能是被杀或仍在写，先看调度器状态再决定重投。

## 产物与下一步衔接

本例 scf 目录最终留有：`pwx.in/pwx.out`、后续链的 `bands.in/bands.out/bandspp.in/bandspp.out`、以及 `bands.dat`/`bands.dat.gnu`/`bands.dat.rap`（能带提取产物）；`outdir`（原 `./out/`）下保存电荷密度与波函数，供 bands/projwfc 非自洽复用，归档确认后可清理。每个目录的费米能级照例登记（后续作图零点）：

```bash
grep "the Fermi energy is" pwx.out | tail -1
```

## 思考

1. `conv_thr` 收得很紧（1e-12）对 scf 本身几乎无感，为什么对后续 EPC/应变能量差是必要的？
2. 队列清空后 `squeue` 显示无作业，能否直接宣布「五个 scf 全部成功」？为什么？
3. 若把 `degauss` 从 3.7d-3 改成别的值再跑一遍 scf，能量表还能与旧值直接比较吗？
