参考：

- QE 官方文档 INPUT_PW：<https://www.quantum-espresso.org/Doc/INPUT_PW.html>

## vc-relax（变胞结构优化）

这次先让原子位置和允许的晶胞自由度一起调整，观察力怎样变化。二维模型的真空方向不能随意跟着收缩，所以这里使用 `cell_dofree='fixc'`。下面保留这次没有达到 BFGS 收敛的过程：它适合用来学习检查输出，不能当成已接受结构的范例。

### 建目录、写输入文件

输入文件建议先在本地编辑好，再用 cat 指令在服务器中输入（heredoc）。目录用数字编号，在 Linux 里输入数字后 Tab 补全很方便，这是日常使用的小技巧。另外 `outdir = './out_rx/'` 指向的文件夹会在运行时自动创建，不需要手动建：

```bash
[<user>@<cluster> QE]$ cd <工作目录>/QE

[<user>@<cluster> QE]$ mkdir -p 05_relax
[<user>@<cluster> QE]$ cd 05_relax

[<user>@<cluster> 05_relax]$ cat > rx.in <<'EOF'
&CONTROL
  calculation = 'vc-relax'
  etot_conv_thr = 1.0000000000d-08
  forc_conv_thr = 1.0000000000d-10
  outdir = './out_rx/'
  prefix = 'HfCl2_PbO2'
  pseudo_dir = '<赝势库路径>'
  tprnfor = .true.
  tstress = .true.
  verbosity = 'high'
/

&SYSTEM
  ibrav = 0
  nat = 6
  ntyp = 4
  ecutwfc = 90
  ecutrho = 720
  input_dft = 'vdw-DF3-opt1'
  force_symmorphic = .true.
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 3.7d-3
/

&ELECTRONS
  conv_thr = 1.0000000000d-08
  electron_maxstep = 200
  mixing_beta = 7.0000000000d-01
/

&IONS
/

&CELL
  cell_dofree = 'fixc'
/

ATOMIC_SPECIES
Hf  178.49   Hf.pbe-spn-kjpaw_psl.1.0.0.UPF
Cl   35.45   Cl.pbe-n-kjpaw_psl.1.0.0.UPF
Pb  207.20   Pb.pbe-dn-kjpaw_psl.1.0.0.UPF
O    15.999  O.pbe-n-kjpaw_psl.1.0.0.UPF

CELL_PARAMETERS angstrom
! 此处放入你的结构块（CELL_PARAMETERS 三行；本例初始 a≈3.37559 Å，c = 30 Å）

ATOMIC_POSITIONS crystal
! 此处放入你的结构块（ATOMIC_POSITIONS 各行）

K_POINTS automatic
24 24 1 0 0 0
EOF

[<user>@<cluster> 05_relax]$ cat rx.in
```

写完 `cat` 一遍回看，是防止 heredoc 手滑的最低成本检查。

### Slurm 脚本

```bash
[<user>@<cluster> 05_relax]$ cat > rx.slurm <<'EOF'
#!/bin/bash
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

#unlimit memory
ulimit -s unlimited
ulimit -l unlimited

# load path
source /data/intel/oneapi/setvars.sh

cd $SLURM_SUBMIT_DIR

mpirun -np 56 <qe_bin>/pw.x<rx.in>rx.out
EOF
[<user>@<cluster> 05_relax]$
```

np 后的 56 是这个任务占用的 MPI 进程数；`ulimit -s` 设置栈限制，`ulimit -l` 设置可锁定内存限制；它们不能解除 Slurm 的时间或作业内存配额。

### 提交与监控

任务提交后用 `squeue` 看是否在运行，建议提交 5–10 秒后再查，避免短运行后已报错。也可以用 `htop` 对比提交前后的线程数。更完整的优化进展我更推荐：

```bash
watch -n 5 "grep -E 'iteration #|convergence has been achieved|Total force|total stress|CELL_PARAMETERS|ATOMIC_POSITIONS|End of BFGS Geometry Optimization|JOB DONE' rx.out | tail -n 80"
```

也可以单独盯最后输出：`tail -f rx.out`。建议再开一个监控：

```bash
watch -n 10 "squeue -j <jobid>; echo; grep 'Total force' rx.out | tail -n 80"
```

真实输出（每个 BFGS 步内部是一次完整 SCF，力逐级下降）：

```text
Every 5.0s: grep -E 'iteration #|convergence has been achieved|...'  Fri Sep  4 18:44:04 2026

     iteration #  8     ecut=    90.00 Ry     beta= 0.70
     ...
     convergence has been achieved in  14 iterations
     Total force =     0.002185     Total SCF correction =     0.000036
CELL_PARAMETERS (angstrom)
ATOMIC_POSITIONS (crystal)
     iteration #  1     ecut=    90.00 Ry     beta= 0.70
     ...
     convergence has been achieved in  21 iterations
     Total force =     0.001389     Total SCF correction =     0.000278
```

### 结束后验收：JOB DONE 不等于收敛

任务结束后：

```bash
[<user>@<cluster> 05_relax]$ grep -E \
> 'Begin final coordinates|End final coordinates|Total force|total stress|Final enthalpy|End of BFGS Geometry Optimization|JOB DONE' \
> rx.out | tail -n 100
     Total force =     0.037945     Total SCF correction =     0.000117
     Total force =     0.020507     Total SCF correction =     0.000242
     ...
     Total force =     0.000039     Total SCF correction =     0.000054
     Total force =     0.000095     Total SCF correction =     0.000031
     End of BFGS Geometry Optimization
     Final enthalpy           =   -1795.6890425495 Ry
Begin final coordinates
End final coordinates
   JOB DONE.
[<user>@<cluster> 05_relax]$
```

从输出看，力总体从 0.037945 Ry/Bohr 降到了 10⁻⁴–10⁻⁵ 量级，随后给出了 End of BFGS / Final enthalpy / JOB DONE 的完整结尾——看起来一切正常。**但 `JOB DONE.` 仅表示程序到达结束段，还必须检查 BFGS 是否收敛。**

> **更正（2026-09-05）：本次 vc-relax 程序已结束，但 BFGS 未收敛，不能判定结构优化通过。**

这是事后复核才发现的：上面的 grep 摘录并不完整，缺了收敛判定的关键证据。教训是：验收 vc-relax 要专门确认 BFGS 收敛标志，而不是看到 JOB DONE 就翻篇。

### 把遗漏的失败行一起找出来

2026-09-22 回到原输出重新查找，明确的失败原因就在结束段前面：

```text
[<user>@<cluster> 05_relax]$ grep -Ei 'bfgs failed|End of BFGS|JOB DONE' rx.out
     bfgs failed after  30 scf cycles and  27 bfgs steps, convergence not achieved
     End of BFGS Geometry Optimization
   JOB DONE.
[<user>@<cluster> 05_relax]$
```

![本次结构优化的总力变化，BFGS 未收敛](/Atlas/figures/relax-force.svg)

力整体下降，但末段并非单调下降。图的横轴是输出中的力报告序号，不是保证接受的 BFGS 步数；判断优化通过仍需看明确的收敛条件。这正是保留失败行比只截取结尾更有用的地方。

## 提取最终几何

```bash
[<user>@<cluster> 05_relax]$ sed -n '/Begin final coordinates/,/End final coordinates/p' rx.out \
> > final_structure.txt

[<user>@<cluster> 05_relax]$ cat final_structure.txt
```

想直接得到最后一组晶胞和原子坐标：

```bash
[<user>@<cluster> 05_relax]$ awk '
> /CELL_PARAMETERS/ {
>     cell=$0 ORS
>     for(i=1;i<=3;i++){getline; cell=cell $0 ORS}
> }
> /ATOMIC_POSITIONS/ {
>     pos=$0 ORS
>     for(i=1;i<=6;i++){getline; pos=pos $0 ORS}
> }
> END {
>     print "===== FINAL CELL ====="
>     printf "%s",cell
>     print ""
>     print "===== FINAL ATOMS ====="
>     printf "%s",pos
> }
> ' rx.out | tee final_geometry.txt
```

这次 vc-relax 后，面内晶格从约 `3.37559 Å` 收缩到 `3.35651 Å`，c 保持 `30 Å`——符合 `cell_dofree='fixc'` 的预期；原子分数坐标也更新了，说明离子和允许的面内自由度都发生了优化。

把最终几何放到固定位置，避免以后一直从 rx.out 解析：

```bash
[<user>@<cluster> 05_relax]$ mkdir -p ../01_structure

[<user>@<cluster> 05_relax]$ cp final_geometry.txt ../01_structure/relaxed_geometry.txt

[<user>@<cluster> 05_relax]$ awk '
> /CELL_PARAMETERS/ {
>     print
>     for(i=1;i<=3;i++){getline; print}
> }
> ' final_geometry.txt \
> > ../01_structure/relaxed_cell.inc

[<user>@<cluster> 05_relax]$ awk '
> /ATOMIC_POSITIONS/ {
>     print
>     for(i=1;i<=6;i++){getline; print}
> }
> ' final_geometry.txt \
> > ../01_structure/relaxed_atoms.inc

[<user>@<cluster> 05_relax]$ cat ../01_structure/relaxed_cell.inc
CELL_PARAMETERS (angstrom)
   3.356510437   0.000000000  -0.000000000
  -1.678255218   2.906823306   0.000000000
    0.000000000  -0.000000000  30.000000000
[<user>@<cluster> 05_relax]$ cat ../01_structure/relaxed_atoms.inc
ATOMIC_POSITIONS (crystal)
Hf            0.0000000000        0.0000000000        0.3750750598
Cl            0.6666666667        0.3333333333        0.4300153898
Cl            0.6666666667        0.3333333333        0.3192017432
Pb           -0.0000000000       -0.0000000000        0.5521514583
O             0.6666666667        0.3333333333        0.5876371921
O             0.3333333333        0.6666666667        0.5147767817
[<user>@<cluster> 05_relax]$
```

`relaxed_cell.inc` / `relaxed_atoms.inc` 两个片段后续可以直接 cat 进输入文件。总结本次结果：vc-relax 程序结束但 BFGS 未收敛；最后输出的面内晶格常数约 3.356510437 Å，第三晶格矢量保持 30 Å。候选结构可以记录，但正式声子前仍需闭合结构收敛检查。

### 下一步

下面的 [SCF 页](/Atlas/m/scf/qe/)记录已有候选几何上的电子计算，用于说明数据来源。正式性质计算前应先完成结构收敛检查，不能靠一次 static SCF 替代失败的优化：

```text
vc-relax（本页，候选几何 + .inc 片段）
    ↓
static SCF
    ↓
DOS 专用 NSCF → dos.x/projwfc.x
    ↓
bands → bands.x
```
