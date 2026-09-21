参考：

- QE 官方文档 INPUT_PW（calculation / cell_dofree）：<https://www.quantum-espresso.org/Doc/INPUT_PW.html>

## 应变 / 掺杂扫描

围绕一个母体结构搭一套应变目录（拉伸/压缩 ±1–3%），每个应变点重跑「结构 → 电子结构 → 电声 → Tc」全套链，读出性质随应变的走向。这一页讲目录怎么搭、晶胞怎么锁、每点怎么验收，以及批量造目录时最容易踩的重定向坑。

## 思路

- 母体无应变算例：vc-relax（`cell_dofree='2Dxy'`，真空方向 c 固定、面内自由），得到平衡晶格。
- 应变点：**只改面内晶格常数**，用 `relax`（锁晶胞、只弛豫原子内部坐标）——应变是人为强加的约束，不能再让程序自己优化晶胞，否则应变就不是你设定的值。
- 每个应变点一套完整目录，互不干扰。

cell_dofree 取值速查（真实文件里三种都出现过）：`'2Dxy'` 只弛豫面内两个晶格矢量；`'fixc'` 固定第三矢量整体；`'all'` 三维全自由（体相用）。

## 搭目录：cp + sed 两个动作

以拉伸 3% 为例，从无应变目录复制后，sed 替换 `rx.in` 里 CELL_PARAMETERS 的三个数值（六方格子 b = −a/2 联动）：

```bash
[<user>@<cluster> QE]$ cp -a no_strain tensile_003

[<user>@<cluster> QE]$ cd tensile_003
[<user>@<cluster> tensile_003]$ sed -i 's/3.312897589/3.412284517/' rx.in
[<user>@<cluster> tensile_003]$ sed -i 's/-1.656448795/-1.706137701/' rx.in
[<user>@<cluster> tensile_003]$ sed -i 's/2.869053472/2.955057172/' rx.in
```

（压缩 3% 则换成 3.213510661 / −1.606755331 / 2.782981868；c = 40.0 始终不动。）改完核对一遍数值再提交：

```bash
[<user>@<cluster> tensile_003]$ grep CELL -A 4 rx.in
CELL_PARAMETERS (angstrom)
   3.412284517 0.000000000 0.000000000
  -1.706137701 2.955057172 0.000000000
   0.000000000 0.000000000 40.000000000
[<user>@<cluster> tensile_003]$
```

母体 vc-relax 后的面内晶格 3.312897589 Å 与 ×1.03/×0.97 的换算关系写进每个算例的 README 一行，避免后人不知道数值从哪来。

## 应变点输入：rx.in（relax 锁胞）

与母体 vc-relax 相比只有三处增量：`calculation = 'relax'`、晶胞数值换成应变后的、`&CELL` 留空（程序不再动晶胞）：

```bash
[<user>@<cluster> tensile_003]$ cat > rx.in <<'EOF'
&CONTROL
  calculation = 'relax'        ! 只弛豫原子，晶胞锁死
  outdir = './out_rx/'
  prefix = '<prefix>'
  pseudo_dir = '<赝势库路径>'
  tprnfor = .true.
  etot_conv_thr = 1.0d-8
  forc_conv_thr = 1.0d-6
/

&SYSTEM
  ibrav = 0   nat = 6   ntyp = 4
  ecutwfc = 90   ecutrho = 720
  input_dft = 'vdw-DF3-opt1'
  force_symmorphic = .true.
  occupations = 'smearing'   smearing = 'gaussian'   degauss = 3.7d-3
/

&ELECTRONS
  conv_thr = 1.0d-8   electron_maxstep = 200
  mixing_beta = 4.0d-1
/

&IONS
/

&CELL
/

ATOMIC_SPECIES
（同母体）

CELL_PARAMETERS (angstrom)
! 此处放入应变后的晶胞（三个数值已 sed 替换）

ATOMIC_POSITIONS (crystal)
! 沿用母体坐标

K_POINTS automatic
  16 16 1 0 0 0
EOF
```

## 每个应变点的完整链与验收

结构目录与电声目录分开放：

```text
结构：rx → pwx(32×32×1 SCF) → bands → bandspp
电声：pwxall(64×64×1 la2F) → phx(q=1) → phx1/2/3 → q2rx → matdynxline → lambdax
```

每步验收只认完成标志，再顺手查收敛失败：

```bash
grep -l "JOB DONE" */*.out
grep -l "convergence NOT achieved" */*.out
```

第二条有命中即该算例 FAIL，重交或调参，不要带病进下一步。

## 能量–应变表怎么读

各应变点 scf 总能（真实记录，Ry）：

| 算例 | E (Ry) |
|---|---|
| compress/003 | −208.225061 |
| compress/002 | −208.227747 |
| compress/001 | −208.229295 |
| tensile/001 | −208.229381 |
| tensile/002 | −208.228144 |

能量最低点在 ±1% 之间——与母体平衡晶格一致，这本身就是一个自检：如果最低点偏离无应变平衡太远，先怀疑应变换算写错了。

电声侧同表汇总：无应变 λ≈0.31–0.32、ω_log≈259–262 K；拉伸 3% λ 扫描从 0.54 漂到 0.36，Tc 峰 ≈3.9 K 出现在最小展宽端（读表纪律见 Allen–Dynes 页）。

## 电子掺杂扫描

同一模式可直接平移到掺杂系列：建 0.01–0.3 等浓度的目录树，每个目录只改电子数相关设置，其余输入与母体一致。注意掺杂算例的能量表与 Tc 表要和应变系列分开存档。

## 事故：批量 sed 之后丢了重定向

一次批量改写提交脚本时把 `pw.x < pwxall.in > pwxall.out` 写坏，实际成了 `pw.xpwxall.out`（少个空格、输入重定向整个丢失），作业秒退无输出。定位与修复：

```bash
[<user>@<cluster> ph64]$ cat -A pwxall.slurm | tail -n 5
mpirun -np 56 <qe_bin>/pw.xpwxall.out$
[<user>@<cluster> ph64]$
```

把执行行改回完整重定向再提交。纪律：批量 sed 改脚本后，先 `cat -A`（或 `bash -n`）再 sbatch。

## 下一步

```text
应变/掺杂系列（本页）
    ↓ 逐点全套链
能量表 + λ/Tc 表 → 性质随应变的走向
```
