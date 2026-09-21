参考：

- QE 官方文档 INPUT_PW：<https://www.quantum-espresso.org/Doc/INPUT_PW.html>

## DOS 专用 NSCF：加密 k 网格复用 SCF 电荷

DOS 计算需要比 SCF 更密的 k 采样，但不需要重新自洽。做法是：沿用已完成 static SCF 的电荷密度，结构、赝势、泛函、cutoff、smearing 全部保持一致，只把 calculation 改成 `nscf`、k 网格加密到 `36×36×1`。这个 36×36×1 目前作为 DOS 采样网格使用，不把它宣称为重新做过收敛测试的最终参数。

### 复制 SCF 数据

先建目录，把 static SCF 的 `.save` 目录整个拷过来（`cp -a` 保留权限与时间戳）：

```bash
[<user>@<cluster> QE]$ cd <工作目录>/QE

[<user>@<cluster> QE]$ mkdir -p 07_dos/nscf
[<user>@<cluster> QE]$ cd 07_dos/nscf

[<user>@<cluster> nscf]$ mkdir -p out

[<user>@<cluster> nscf]$ cp -a ../../06_static/out/HfCl2_PbO2.save out/

[<user>@<cluster> nscf]$ ls out/HfCl2_PbO2.save | head
```

先确认 SCF 数据复制成功，再写输入。

### 输入文件

```bash
[<user>@<cluster> nscf]$ cat > nscf.in <<'EOF'
&CONTROL
  calculation = 'nscf'
  outdir = './out/'
  prefix = 'HfCl2_PbO2'
  pseudo_dir = '<赝势库路径>'
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

ATOMIC_SPECIES
Hf  178.49   Hf.pbe-spn-kjpaw_psl.1.0.0.UPF
Cl   35.45   Cl.pbe-n-kjpaw_psl.1.0.0.UPF
Pb  207.20   Pb.pbe-dn-kjpaw_psl.1.0.0.UPF
O    15.999  O.pbe-n-kjpaw_psl.1.0.0.UPF

CELL_PARAMETERS (angstrom)
! 此处放入结构优化输出的三行晶胞矢量（本例 3.356510437 …，c = 30 Å）

ATOMIC_POSITIONS (crystal)
! 此处放入结构优化输出的六行原子坐标

K_POINTS (automatic)
36 36 1 0 0 0
EOF

[<user>@<cluster> nscf]$ cat nscf.in
```

与 scf.in 逐项对比：CONTROL 里 `calculation = 'nscf'`、没有 tprnfor/tstress（不重新算力）；SYSTEM/ELECTRONS/结构块全部一致，唯一数值变化是 K_POINTS 从 24×24×1 到 36×36×1。

### Slurm 脚本：sed 改一行

直接复用已经跑通的脚本：

```bash
[<user>@<cluster> nscf]$ cp ../../05_relax/rx.slurm nscf.slurm

[<user>@<cluster> nscf]$ sed -i \
> 's#pw.x<rx.in>rx.out#pw.x -in nscf.in > nscf.out#' \
> nscf.slurm

[<user>@<cluster> nscf]$ cat nscf.slurm
```

如果你的 rx.slurm 最后一行确实还是 `mpirun -np 56 <qe_bin>/pw.x<rx.in>rx.out`，修改后应该变成 `mpirun -np 56 <qe_bin>/pw.x -in nscf.in > nscf.out`。提交前 `cat` 一遍核对。

### 提交与监控

```bash
[<user>@<cluster> nscf]$ sbatch nscf.slurm
```

运行时可以看 `squeue`，以及 `tail -f nscf.out`。

### 验收：nscf 看 JOB DONE / Error，不看 convergence

结束后执行这一组：

```bash
grep "JOB DONE" nscf.out

grep "the Fermi energy is" nscf.out | tail

grep -E "number of electrons|number of Kohn-Sham states|number of k points" nscf.out

grep -E "convergence has been achieved|Error in routine" nscf.out | tail -n 20
```

真实输出：

```bash
[<user>@<cluster> nscf]$ grep "JOB DONE" nscf.out
   JOB DONE.
[<user>@<cluster> nscf]$
[<user>@<cluster> nscf]$ grep "the Fermi energy is" nscf.out | tail
     the Fermi energy is     0.0500 ev
[<user>@<cluster> nscf]$
[<user>@<cluster> nscf]$ grep -E \
> "number of electrons|number of Kohn-Sham states|number of k points" \
> nscf.out
     number of electrons       =        52.00
     number of Kohn-Sham states=           31
     number of k points=   127  Gaussian smearing, width (Ry)=  0.0037
[<user>@<cluster> nscf]$
[<user>@<cluster> nscf]$ grep -E \
> "convergence has been achieved|Error in routine" \
> nscf.out | tail -n 20
[<user>@<cluster> nscf]$ ls
_err.<jobid>.log  nscf.in  nscf.out  nscf.slurm  out  _out.<jobid>.log
[<user>@<cluster> nscf]$
```

逐条判读：`36×36×1` 在当前对称性下被约化成 **127 个不可约 k 点**，这是正常的；最后一条 grep 什么都没抓到也**不构成异常**——这是 `nscf`，不做 SCF 迭代，判断是否成功主要看 `JOB DONE.`、是否存在 `Error in routine`，以及能带数据是否正常生成。这是和 scf 验收思路完全不同的一点，别拿 convergence 的尺子来量 nscf。

另外把 `number of Kohn-Sham states = 31` 这一条专门记下来：它会告诉后续能带计算这次 NSCF 实际算了多少条带（bands 页要用它定 nbnd）。

### 下一步

NSCF 正常 `JOB DONE.` 后，在同一个 07_dos 下建 tdos 和 pdos：

```text
07_dos/
├── nscf/    ← 本页
├── tdos/    → dos.x → TDOS
└── pdos/    → projwfc.x → PDOS
```

TDOS 和 PDOS 都读取 `07_dos/nscf/out/HfCl2_PbO2.save`，所以不需要再复制一份波函数目录——直接依次跑 dos.x 和 projwfc.x（见 DOS 后处理页）。
