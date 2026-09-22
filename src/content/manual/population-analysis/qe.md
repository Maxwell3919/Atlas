
本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。解包后保留目录结构，进入 `si-pbe` 运行文中的绘图命令；赝势按正文的官方来源准备。

下载包保留输入、输出、单独保存的 XML和作图数据，没有包含可接续计算的 `tmp/si.save` 电荷密度与波函数。阅读输出和重新作图可直接使用包内文件；重新运行 QE 时，先按 [SCF 页](/Atlas/m/scf/qe/)生成保存目录，再复制到对应计算目录。DOS 和轨道投影还需要先完成匹配的 [NSCF](/Atlas/m/nscf/qe/)。
[projwfc.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html) · [后处理用户手册](https://www.quantum-espresso.org/Doc/pp_user_guide/) · [pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html)

`projwfc.x` 能把波函数投影到赝势提供的原子轨道上，并给出 Löwdin 布居。先从两个完全等价的 Si 原子开始，容易看清哪些数字是电子布居，哪些只是投影没有覆盖的部分。结构和父密度的建立见[SCF](/Atlas/m/scf/qe/)，均匀积分网格见[NSCF](/Atlas/m/nscf/qe/)；这里接 `18³` 网格的 `gap18-cg`，它已重新核对全部本征值求解结束。

布居需要对布里渊区积分，所以这次复制的是均匀网格计算后的完整 `tmp`，包含波函数。普通能带路径只沿几条线走，不能用它的权重积分来代替这一份布居。

```text
[preston@preston-System-Product-Name si-pbe]$ mkdir -p population-cg
[preston@preston-System-Product-Name si-pbe]$ cp -a gap18-cg/tmp population-cg/
[preston@preston-System-Product-Name si-pbe]$ cp population/projwfc.in population/run.sh population-cg/
```

复制后再检查目录。`tmp` 是计算数据，`projwfc.in` 控制后处理，生成的 `si.pdos_*` 是能量分辨的投影态密度；布居数字在 `projwfc.out` 末段。

```text
[preston@preston-System-Product-Name si-pbe]$ ls population-cg
 _err.798.log      data-file-schema.xml   projwfc.in    si-projections.projwfc_up    'si.pdos_atm#2(Si)_wfc#1(s)'   tmp
 _out.798.log      lowdin.csv             projwfc.out  'si.pdos_atm#1(Si)_wfc#1(s)'  'si.pdos_atm#2(Si)_wfc#2(p)'
 atomic_proj.xml   projwfc.err            run.sh       'si.pdos_atm#1(Si)_wfc#2(p)'   si.pdos_tot
[preston@preston-System-Product-Name si-pbe]$
```


```text
[preston@preston-System-Product-Name si-pbe]$ cat population-cg/projwfc.in
&PROJWFC
  prefix = 'si'
  outdir = './tmp'
  filpdos = 'si'
  filproj = 'si-projections'
  ngauss = 0
  degauss = 0.01
  DeltaE = 0.02
/
[preston@preston-System-Product-Name si-pbe]$
```


`prefix='si'` 和 `outdir='./tmp'` 必须对应那次 NSCF 的实际文件。`filproj` 保存逐态投影，`filpdos` 命名 PDOS；`degauss=0.01` 的单位是 Ry，`DeltaE=0.02` 的单位是 eV，二者用于同时生成的展宽 PDOS。不要因为输入里出现了展宽参数，就把投影电子数误读成某个能量点上的 DOS 值。

```text
[preston@preston-System-Product-Name si-pbe]$ cat population-cg/run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-pop
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
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/projwfc.x -in projwfc.in > projwfc.out 2> projwfc.err
[preston@preston-System-Product-Name si-pbe]$
```


```text
[preston@preston-System-Product-Name population-cg]$ sbatch run.sh
Submitted batch job 798
[preston@preston-System-Product-Name population-cg]$ cd ..
```

先读 OUT 开头，确认它从 `./tmp/si.save/` 读到了 PBE 数据。接下来会列出原子波函数数量、能带数量和 k 点数量，再列出每个投影状态属于哪个原子、哪个角动量。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 67 population-cg/projwfc.out

     Program PROJWFC v.7.5 starts on 22Sep2026 at 22: 2:44

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org",
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on     4 processors

     MPI processes distributed on     1 nodes
     R & G space division:  proc/nbgrp/npool/nimage =       4
     5948 MiB available memory on the printing compute node when the environment starts


     Reading xml data from directory:

     ./tmp/si.save/

     IMPORTANT: XC functional enforced from input :
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)
     Any further DFT definition will be discarded
     Please, verify this is what you really want


     Parallelization info
     --------------------
     sticks:   dense  smooth     PW     G-vecs:    dense   smooth      PW
     Min         571     214     63                18093     4156     684
     Max         572     217     64                18095     4157     688
     Sum        2287     859    253                72377    16625    2741

     Using Slab Decomposition


     Gaussian broadening (read from input): ngauss,degauss=   0    0.010000


     Calling projwave ....
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used


  Problem Sizes
  natomwfc =            8
  nbnd     =            8
  nkstot   =          195
  npwx     =          531
  nkb      =           36


     Atomic states used for projection
     (read from pseudopotential files):

     state #   1: atom   1 (Si ), wfc  1 (l=0 m= 1)
     state #   2: atom   1 (Si ), wfc  2 (l=1 m= 1)
     state #   3: atom   1 (Si ), wfc  2 (l=1 m= 2)
     state #   4: atom   1 (Si ), wfc  2 (l=1 m= 3)
     state #   5: atom   2 (Si ), wfc  1 (l=0 m= 1)
     state #   6: atom   2 (Si ), wfc  2 (l=1 m= 1)
     state #   7: atom   2 (Si ), wfc  2 (l=1 m= 2)
     state #   8: atom   2 (Si ), wfc  2 (l=1 m= 3)
[preston@preston-System-Product-Name si-pbe]$
```


本例 `natomwfc=8`：每个 Si 有一组 s 和三组 p，两个原子一共八个投影通道。`state #1` 是第一个 Si 的 s，`#2–4` 是它的 p；`#5` 是第二个 Si 的 s，`#6–8` 是它的 p。这些编号由本次赝势中的原子态决定，换赝势后应重新读这一段。

中间部分逐 k 点、逐能带列出投影，最后才对占据态和 k 权重求和得到布居。末尾的完整关键段如下：

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 25 population-cg/projwfc.out
==== e(   7) =    11.86270 eV ====
     psi = 0.108*[#   1]+0.108*[#   5]+0.083*[#   2]+0.083*[#   3]+0.083*[#   4]
          +0.083*[#   6]+0.083*[#   7]+0.083*[#   8]
    |psi|^2 = 0.713
==== e(   8) =    11.86270 eV ====
     psi = 0.108*[#   1]+0.108*[#   5]+0.083*[#   2]+0.083*[#   3]+0.083*[#   4]
          +0.083*[#   6]+0.083*[#   7]+0.083*[#   8]
    |psi|^2 = 0.713

Lowdin Charges:

     Atom #   1: total charge =   3.9634, s =  1.1520,
     Atom #   1: total charge =   3.9634, p =  2.8114, pz=  0.9371, px=  0.9371, py=  0.9371,
     Atom #   2: total charge =   3.9634, s =  1.1520,
     Atom #   2: total charge =   3.9634, p =  2.8114, pz=  0.9371, px=  0.9371, py=  0.9371,
     Spilling Parameter:   0.0092

     PROJWFC      :      1.15s CPU      1.23s WALL


   This run was terminated on:  22: 2:45  22Sep2026

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name si-pbe]$
```


同一个原子被打印在两行，是为了分开展示 s 和 p，不是两份需要再相加的总电荷。每个 Si 的 `total charge` 是 **3.9634 e**，其中 s 为 **1.1520 e**，p 合计 **2.8114 e**；p 的三个分量各为 0.9371 e，舍入后相加可能出现最后一位的小差别。

两个原子的结果一致，这是这个对称结构首先应该满足的核对。再看 `Spilling Parameter=0.0092`：两个原子的投影电子数合计为 7.9268 e，相比原胞的 8 个价电子少了约 0.0732 e，比例约 0.00915，与报告的 spilling 舍入值一致。

这部分差额反映有限原子轨道投影对波函数的覆盖，并不意味着两个等价 Si 同时把 0.0366 个电子转移给了某个不存在的受体。把 `4−3.9634` 直接当作净失电子量，就会在这个最简单的同质晶体中得出不合理的电荷转移结论。

```text
[preston@preston-System-Product-Name si-pbe]$ cat population-cg/lowdin.csv
atom,total_electrons,s_electrons,p_electrons,pz_electrons,px_electrons,py_electrons
1,3.9634,1.1520000000000001,2.8114,0.9371,0.9371,0.9371
2,3.9634,1.1520000000000001,2.8114,0.9371,0.9371,0.9371
[preston@preston-System-Product-Name si-pbe]$
```


画图时分别把 s、p 叠加，保留 4 个价电子的参照线。[布居表](/Atlas/examples/si-pbe/population-cg/lowdin.csv)、[完整 projwfc.out](/Atlas/examples/si-pbe/population-cg/projwfc.out)和[绘图脚本](/Atlas/examples/si-pbe/plot_si.py)可直接下载。

```text
[preston@preston-System-Product-Name si-pbe]$ python3 plot_si.py population
<工作目录>/si-pbe/plots/population-analysis.png
```

![等价 Si 原子的 s 和 p 投影布居，以及价电子数参照](/Atlas/examples/si-pbe/plots/population-analysis.png)

这张图首先展示两个原子的等价性和投影构成。换成异质结构后，要比较的是相同赝势、相同投影定义和充分 k 采样下各个原子的变化，同时检查 spilling 是否显著改变。Löwdin 布居依赖所选择的原子轨道子空间；它不会自动等同于按实空间分区得到的 Bader 电荷，也不单独证明氧化态。

下一步：看逐 k 点的轨道组成接[胖带](/Atlas/m/fatband/qe/)；看实空间分区接[Bader 电荷](/Atlas/m/bader/qe/)；看成键前后的空间变化接[差分电荷](/Atlas/m/delta-charge/qe/)。

```text
均匀 NSCF 网格 + 波函数 → projwfc.x → 轨道编号与逐态投影
                                             ↓
                                  占据数与 k 权重积分
                                             ↓
                               Löwdin 布居 + spilling 核对
```
