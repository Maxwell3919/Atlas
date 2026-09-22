参考：

- QE 官方文档 INPUT_PW：<https://www.quantum-espresso.org/Doc/INPUT_PW.html>

## static SCF（Self-Consistent Field）

上一页提取了这次优化最后输出的晶胞和原子坐标。这里固定它们，重新做电子自洽，记录总能、费米能级、力和应力。

这次几何仍是候选结构：原来的 BFGS 没有收敛。下面的 SCF 用来检查这个固定构型，不能替它补上结构优化通过的结论。输入沿用 HfCl₂/PbO₂ 的赝势与物理设置，先进入 `06_static`。

## 建目录、写输入文件

文件建议先在本地编辑好，再用 cat 指令在服务器中输入（heredoc）。目录用数字编号，在 Linux 里输入数字后 Tab 补全很方便，这是日常使用的小技巧：

```bash
[<user>@<cluster> QE]$ cd <工作目录>/QE

[<user>@<cluster> QE]$ mkdir -p 06_static
[<user>@<cluster> QE]$ cd 06_static

[<user>@<cluster> 06_static]$ cat > scf.in <<'EOF'
&CONTROL
  calculation = 'scf'
  outdir = './out/'
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

ATOMIC_SPECIES
Hf  178.49   Hf.pbe-spn-kjpaw_psl.1.0.0.UPF
Cl   35.45   Cl.pbe-n-kjpaw_psl.1.0.0.UPF
Pb  207.20   Pb.pbe-dn-kjpaw_psl.1.0.0.UPF
O    15.999  O.pbe-n-kjpaw_psl.1.0.0.UPF

CELL_PARAMETERS (angstrom)
! 此处放入结构优化输出的三行晶胞矢量（本例约 3.3565… Å，c = 30 Å）

ATOMIC_POSITIONS (crystal)
! 此处放入结构优化输出的六行原子坐标

K_POINTS (automatic)
24 24 1 0 0 0
EOF
```

两个小点：**outdir = './out/'** 会在运行时自动创建，不需要手动 mkdir；本例使用 `conv_thr = 1e-8`；它只是这次输入的选择。是否足够，需要针对所比较的能量、力或其他目标量测试；不能把静态 SCF 与声子各配一个固定阈值当作普遍保证。

### Slurm 脚本

结构优化的脚本已经跑通过，直接复制过来改一行执行命令：

```bash
[<user>@<cluster> 06_static]$ cp ../05_relax/rx.slurm scf.slurm

[<user>@<cluster> 06_static]$ sed -i 's#pw.x<rx.in>rx.out#pw.x -in scf.in > scf.out#' scf.slurm

[<user>@<cluster> 06_static]$ tail -n 5 scf.slurm
mpirun -np 56 <qe_bin>/pw.x -in scf.in > scf.out
[<user>@<cluster> 06_static]$
```

完整脚本内容如下（首次使用时照此生成）：

```bash
#!/bin/bash
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

# unlimit memory
ulimit -s unlimited
ulimit -l unlimited

# load path
source /data/intel/oneapi/setvars.sh

cd $SLURM_SUBMIT_DIR

mpirun -np 56 <qe_bin>/pw.x -in scf.in > scf.out
```

几处关键行：`-o/-e` 把标准输出与错误分别写进日志文件；`ulimit -s/-l` 分别设置栈与可锁定内存限制；`source` 加载 oneAPI 运行环境；`cd $SLURM_SUBMIT_DIR` 保证在提交目录里执行；`-np 56` 是本任务占用的 MPI 进程数，按集群配额修改。

### 提交与监控

```bash
sbatch scf.slurm
```

```bash
squeue -u <user>
tail -f scf.out
```

提交后先 `squeue` 确认任务在跑，再 `tail -f` 盯进度；也可以用 `watch -n 5 "grep 'iteration #' scf.out | tail"` 做周期性摘要。

### 结束后验收

```bash
grep "JOB DONE" scf.out
grep '^!' scf.out | tail
grep "the Fermi energy is" scf.out | tail
grep "Total force" scf.out | tail
```

真实输出如下：

```bash
[<user>@<cluster> 06_static]$ grep "JOB DONE" scf.out
   JOB DONE.
[<user>@<cluster> 06_static]$ grep '^!' scf.out | tail
!    total energy              =   -1795.68899321 Ry
[<user>@<cluster> 06_static]$ grep "the Fermi energy is" scf.out | tail
     the Fermi energy is     0.0483 ev
[<user>@<cluster> 06_static]$ grep "Total force" scf.out | tail
     Total force =     0.000049     Total SCF correction =     0.000129
[<user>@<cluster> 06_static]$
```

判读：`-1795.68899321 Ry` 是固定弛豫结构上的静态总能，**不要**与 vc-relax 末尾的 `Final enthalpy` 直接当成同一个物理量比较；真正重要的是 SCF 正常收敛，且在固定优化后结构上重新计算时残余总力只有 `4.9×10⁻⁵ Ry/Bohr`。这是该候选几何上的一次电子计算，不能单凭总力较小判断几何已经合格。但要注意：**SCF 正常完成不能替代结构优化收敛检查**，vc-relax 程序结束不等于 BFGS 收敛（这是真实踩过的坑，详见结构优化页）。

### 存档与规模核对

把关键结果存一份摘要：

```bash
{
    echo "===== STATIC SCF ====="
    grep "JOB DONE" scf.out
    grep '^!' scf.out | tail -n 1
    grep "the Fermi energy is" scf.out | tail -n 1
    grep "Total force" scf.out | tail -n 1
} | tee static_summary.txt
```

再确认这次 SCF 的规模（原子数、电子数、KS 态数、k 点数）：

```bash
grep -E "number of atoms/cell|number of electrons|number of Kohn-Sham states|number of k points" scf.out
```

以及把应力也记录下来：

```bash
grep -A4 "total   stress" scf.out | tail -n 5
```

### 下一步

```text
已优化结构
    ↓
static SCF        ← 本页
    ↓
├─ 均匀密 k 网格 NSCF → dos.x / projwfc.x → DOS / PDOS
    └─ 高对称路径 bands → bands.x → 能带图
```

一个提醒：`E_F = 0.0483 eV` 是当前 smearing SCF 给出的费米能级，**单凭这个数值本身不能判断体系是否金属**——要等 DOS/PDOS 算完，看 E_F 附近是否存在有限 DOS 再下结论。
