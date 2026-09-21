参考：

- QE 官方文档 INPUT_PW：<https://www.quantum-espresso.org/Doc/INPUT_PW.html>

## vc-relax（变胞结构优化）

结构优化确保材料的初步稳定性：所有后续计算（static SCF、DOS、能带、声子）都要站在弛豫后的结构上，初步稳定的结构才能得到可靠结果。`vc-relax` 与普通 `relax` 的区别是它同时弛豫原子位置和晶胞；本例用 `cell_dofree = 'fixc'` 锁住真空方向 c，只放面内晶格自由度。注意：即使结构优化收敛，材料本身仍可能不稳定（声子出现虚频），那是另一层检查，不能混为一谈。

### 建目录、写输入文件

输入文件建议先在本地编辑好，再用 cat 指令在服务器中输入（heredoc）。目录用数字编号，在 Linux 里输入数字后 Tab 补全很方便，这是日常使用的小技巧。另外 `outdir = './out_rx/'` 指向的文件夹会在运行时自动创建，不需要手动建：

```bash
[<user>@<cluster> QE]$ cd <工作目录>/QE

[<user>@<cluster> QE]$ mkdir -p 05_relax
[<user>@<cluster> QE]$ cd 05_relax

[<user>@<cluster> 05_relax]$ cat > vc-relax.in <<'EOF'
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

[<user>@<cluster> 05_relax]$ cat vc-relax.in
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

np 后的 56 是这个任务占用的 MPI 进程数；`ulimit` 两行解除栈与内存限制（一般用来控制内存、时间类限制，此处不设限）。

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

### 提取最终几何

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

不要马上做 DOS。先用这个优化结构建立一个新的高精度 static SCF，确认最终总能、费米能级、力和应力，然后 DOS/PDOS、bands、phonon 都从这个 static 基准继续：

```text
vc-relax（本页，候选几何 + .inc 片段）
    ↓
static SCF
    ↓
DOS 专用 NSCF → dos.x/projwfc.x
    ↓
bands → bands.x
```
