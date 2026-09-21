## 需要 / 产出

- 前置：每个应变目录（`compress/001–003`、`tensile/001–003` 等）的 `rx/` 弛豫已完成，能从 `rx.out` 取到收敛后的 `CELL_PARAMETERS` 与 `ATOMIC_POSITIONS`。
- 产出：各应变目录 `scf/` 下的自洽电荷密度 + 沿高对称路径的非自洽本征值，最终得到可绘图的 `bands.dat.gnu`（附 `bands.dat.rap`）。
- 参考体系：nat = 6, ntyp = 4（Zr, Cl, Sc, C），vdw-DF3-opt1，ecutwfc = 100，ecutrho = 800，prefix = 'zrclscc'。

## 本步与相邻步骤不同之处

- bands 链在 `scf/` 目录按三段执行：`pw.x < pwx.in`（自洽，产生 `./out/` 下电荷与波函数）→ `pw.x < bands.in`（沿高对称点非自洽解本征值）→ `bands.x < bandspp.in`（提取能带数据）。
- 与 dos 步的差别：dos/PDOS 在独立的 `pdos/` 目录另跑一套 scf + projwfc.x，两条链互不复用输出目录。
- bands 是非自洽计算：复用同目录 scf 的电荷密度/波函数，只沿 `K_POINTS` 路径解本征值，不再自洽迭代。

## 参数（只列本步）

- bands.in 的 CONTROL 段核心行：`calculation = 'bands'`、`outdir = './out/'`、`prefix = 'zrclscc'`、`pseudo_dir = '<赝势库路径>'`（其余与同目录 scf 输入保持一致）。
- 输入文件片段（ELECTRONS）：`conv_thr = 1.0000000000d-12`、`mixing_beta = 4.0000000000d-01`。
- 批处理层：`export OMP_NUM_THREADS=1`；执行命令 `mpirun -np 32 pw.x`、`mpirun -np 32 bands.x`。

## 命令与输出

批处理对每个应变目录三步串行，前一步 `JOB DONE` 验收通过才进入下一步（脚本节选）：

```bash
$PW_CMD < pwx.in > pwx.out 2>&1
if grep -q "JOB DONE" pwx.out; then
    echo "[ ${d} ] 2/3: Running NSCF Bands..."
    $PW_CMD < bands.in > bands.out 2>&1
    if grep -q "JOB DONE" bands.out; then
        echo "[ ${d} ] 3/3: Running bands.x data extraction..."
        $BANDS_CMD < bandspp.in > bandspp.out 2>&1
        echo "[ ${d} ] 能带计算全部完成！"
    fi
fi
```

bands.in 的 CONTROL 段（`head -n 25 bands.in` 节选，K_POINTS 高对称路径卡待填充）：

```fortran
&CONTROL
 calculation = 'bands'
 outdir = './out/'
 prefix = 'zrclscc'
 pseudo_dir = '<赝势库路径>'
! tprnfor = .true.
/
```

## 后处理

- bands.x 生成 `bands.dat.gnu`（gnuplot 或 Python 可直接读取的网格数据）与 `bands.dat.rap`。
- 作图以各应变的费米能为零点，批量提取 E_F：

```bash
for d in compress/00{3,2,1} tensile/00{1,0015,2,3}; do
  ef=$(grep "the Fermi energy is" $d/scf/pwx.out | tail -n 1 | awk '{print $(NF-1)}')
  echo -e "$d\t E_F = $ef eV"
done
```

## 失败与假阳性

- 「提取结构失败」：python 提取器在 `rx.out` 中找不到 `CELL_PARAMETERS` 就退出。原因是固定晶格弛豫（`calculation = 'relax'`）输出里只打印 `ATOMIC_POSITIONS`，不会重新打印 `CELL_PARAMETERS`；只有变胞弛豫（`calculation = 'vc-relax'`）才输出。先确认弛豫类型与末尾输出格式：

```bash
grep -E "calculation|CELL_PARAMETERS|ATOMIC_POSITIONS" compress/001/rx/rx.in
tail -n 35 compress/001/rx/rx.out
```

- 批处理报 `[错误] ${d}/scf pwx.x (SCF) 失败，请检查 ${SCF_DIR}/pwx.out`：该应变没有 `JOB DONE`，先查 pwx.out 再重投。
- 作业残留：中断清理用 `scancel -u <user>`（也可按作业名 `-n <jobname>` 精确取消）。

## 可选脚本 + 检查清单

Slurm 串行批处理骨架（逐应变目录执行）：

```bash
#!/bin/bash
#SBATCH --job-name=strain_bands_pdos
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --output=_out.strain_%j.log
#SBATCH --error=_err.strain_%j.log
export OMP_NUM_THREADS=1
PW_CMD="mpirun -np 32 pw.x"
BANDS_CMD="mpirun -np 32 bands.x"
PROJ_CMD="mpirun -np 32 projwfc.x"
# DIRS=(compress/001 ... tensile/003)，逐目录 scf -> bands -> bandspp
```

检查清单：
- [ ] 每个应变的 `pwx.out` / `bands.out` / `bandspp.out` 均含 `JOB DONE`。
- [ ] bands.in 的 `outdir`/`prefix`/`pseudo_dir` 与同目录 pwx.in 完全一致。
- [ ] 各应变间截断、泛函、赝势、smearing、k 路径完全一致，仅 `CELL_PARAMETERS`/`ATOMIC_POSITIONS` 不同。
- [ ] 已记录各应变 E_F（作图取零点用）。
- [ ] `bands.dat.gnu` 已生成且非空。
