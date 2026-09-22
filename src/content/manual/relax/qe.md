
本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/si-pbe-lesson-files.tar.gz)。解包后保留目录结构，进入 `si-pbe` 运行文中的绘图命令；赝势按正文的官方来源准备。

下载包保留输入、输出、单独保存的 XML和作图数据，没有包含可接续计算的 `tmp/si.save` 电荷密度与波函数。阅读输出和重新作图可直接使用包内文件；重新运行 QE 时，先按 [SCF 页](/Atlas/m/scf/qe/)生成保存目录，再复制到对应计算目录。DOS 和轨道投影还需要先完成匹配的 [NSCF](/Atlas/m/nscf/qe/)。
[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [QE 的 Si 结构示例](https://github.com/QEF/q-e/blob/qe-7.5/PW/examples/example01/run_example)

这次把金刚石 Si 原胞里的第二个原子沿 x 方向稍微移开，再让 `relax` 把它找回来。晶胞保持不变，第一个原子固定；这样既能看见真实的 BFGS 步骤，也不会把整个晶体的平移混进轨迹。截断和 k 网格的选择过程见[收敛测试](/Atlas/m/convergence/qe/)，这里直接接着那份两原子输入操作。

原始对称位置是 `(0.25, 0.25, 0.25)`，输入改为 `(0.27, 0.25, 0.25)`，单位为 `alat`。本例晶格常数为 5.397607551 Å，这个位移约 0.108 Å。下面是实际运行的完整文件。

```text
[preston@preston-System-Product-Name si-pbe]$ cp scf/scf.in relax/relax.in
[preston@preston-System-Product-Name si-pbe]$ vi relax/relax.in
```

```text
[preston@preston-System-Product-Name si-pbe]$ cat relax/relax.in
&CONTROL
  calculation = 'relax'
  etot_conv_thr = 1.0d-7
  forc_conv_thr = 1.0d-4
  nstep = 40
  prefix = 'si'
  outdir = './tmp'
  pseudo_dir = '../pseudo'
  tprnfor = .true.
  tstress = .true.
/
&SYSTEM
  ibrav = 2
  A = 5.397607551
  nat = 2
  ntyp = 1
  ecutwfc = 60
  ecutrho = 640
  occupations = 'fixed'
/
&ELECTRONS
  conv_thr = 1.0d-10
/
&IONS
  ion_dynamics = 'bfgs'
/
ATOMIC_SPECIES
Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS alat
Si 0.00 0.00 0.00 0 0 0
Si 0.27 0.25 0.25 1 1 1
K_POINTS automatic
8 8 8 0 0 0
[preston@preston-System-Product-Name si-pbe]$
```


相对于 SCF，关键变化在 `calculation='relax'`、`&IONS` 和坐标。`ion_dynamics='bfgs'` 指定离子优化算法；`etot_conv_thr=1.0d-7` 的单位为 Ry，`forc_conv_thr=1.0d-4` 的单位为 Ry/Bohr，`nstep=40` 是允许的离子步数。它们和 `&ELECTRONS` 中的 `conv_thr` 各管一件事：前两项判断离子优化，后者决定每个离子位置上的电子自洽精度。

第一个 Si 后面的 `0 0 0` 固定三个分量，第二个 Si 的 `1 1 1` 允许三个分量移动。输入里没有 `&CELL`；晶格由 `ibrav=2` 和 `A` 固定。这次计算只能回答“给定这个晶胞，原子是否回到力较小的位置”，不能回答平衡晶格常数是多少。要让晶胞参与优化，接[晶格优化](/Atlas/m/vc-relax/qe/)。

```text
[preston@preston-System-Product-Name si-pbe]$ cat relax/run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-relax
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
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in relax.in > relax.out 2> relax.err
[preston@preston-System-Product-Name si-pbe]$
```


输入和脚本可分别下载：[relax.in](/Atlas/examples/si-pbe/relax/relax.in)、[run.sh](/Atlas/examples/si-pbe/relax/run.sh)。这里使用 4 个 MPI 进程。提交后先看队列，再追踪 `relax.out`；空的队列只说明任务不在运行，仍要回到输出中查结束原因。

```text
[preston@preston-System-Product-Name si-pbe]$ cd relax
[preston@preston-System-Product-Name relax]$ sbatch run.sh
Submitted batch job 777
[preston@preston-System-Product-Name relax]$ cd ..
```

先从 OUT 头部核对这次读到了哪一份输入，以及实际运行版本和进程数。不要把上一次留下的文件当成刚提交任务的输出。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 30 relax/relax.out

     Program PWSCF v.7.5 starts on 22Sep2026 at 21:35:40

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
     7463 MiB available memory on the printing compute node when the environment starts

     Reading input from relax.in

     Current dimensions of program PWSCF are:
     Max number of different atomic species (ntypx) = 10
     Max number of k-points (npk) =  40000
     Max angular momentum in pseudopotentials (lmaxx) =  4

     R & G space division:  proc/nbgrp/npool/nimage =       4
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used


     Parallelization info
[preston@preston-System-Product-Name si-pbe]$
```


`relax.out` 的主体是“电子自洽 → 力 → 更新原子位置 → 下一次电子自洽”反复出现。下面把这次的力和 BFGS 结束信息读出来。初始总力为 0.058861 Ry/Bohr；第一步后降到 0.042098，再到 0.023403。第四个电子周期已经接近极小值，最后一个电子周期才出现 BFGS 收敛信息。

```text
[preston@preston-System-Product-Name si-pbe]$ grep -E 'Total force|bfgs converged|Final energy' relax/relax.out
     Total force =     0.058861     Total SCF correction =     0.000001
     Total force =     0.042098     Total SCF correction =     0.000003
     Total force =     0.023403     Total SCF correction =     0.000001
     Total force =     0.000193     Total SCF correction =     0.000001
     Total force =     0.000000     Total SCF correction =     0.000000
     bfgs converged in   5 scf cycles and   4 bfgs steps
     Final energy             =     -22.8385922964 Ry
[preston@preston-System-Product-Name si-pbe]$
```


这里明确写了 **5 个 SCF 周期、4 步 BFGS**。这句话比最后的 `JOB DONE.` 更直接地说明优化为何停止。若输出写的是到达最大步数，或 `bfgs` 没有收敛，即使程序已经结束，也不能把那份结构当成通过优化。

继续读最终坐标。第二个 Si 的 x 分量回到 `0.2500000911`，y、z 保持在 `0.25`；第一个原子保持固定。由于这是 `relax`，最终坐标段没有重新优化出的晶胞。

```text
[preston@preston-System-Product-Name si-pbe]$ grep -A8 'Begin final coordinates' relax/relax.out
Begin final coordinates

ATOMIC_POSITIONS (alat)
Si               0.0000000000        0.0000000000        0.0000000000    0   0   0
Si               0.2500000911        0.2500000000        0.2500000000
End final coordinates



[preston@preston-System-Product-Name si-pbe]$
```


不要把前面打印的 `Total force = 0.000000` 理解成数学上的零。逐原子力保留了更多有用信息：

```text
[preston@preston-System-Product-Name si-pbe]$ grep -A8 'Forces acting' relax/relax.out | tail -n 9
     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =     0.00000029    0.00000000    0.00000000
     atom    2 type  1   force =    -0.00000029    0.00000000    0.00000000

     Total force =     0.000000     Total SCF correction =     0.000000
     SCF correction compared to forces is large: reduce conv_thr to get better values


[preston@preston-System-Product-Name si-pbe]$
```


第二个原子的残余 x 力约为 `−2.9×10⁻⁷ Ry/Bohr`，小于本次输入的 `1.0×10⁻⁴ Ry/Bohr` 条件。后面的提示也保留下来：SCF 修正相对已经很小的残余力仍可能显得大，因此不能用这些末位数字讨论极高精度的力。

为核对这个提示，本次另外保留了 `relax-check`，使用最终坐标做固定结构 SCF，并把 `conv_thr` 收紧为 `1.0d-12`。这是一份新输入、新输出，不覆盖刚才的优化。实时查看时使用了下面的命令，看到电子迭代从第 7 次继续向后推进；按 `Ctrl-C` 只退出 `watch`，不会取消提交给 Slurm 的作业。

```text
[preston@preston-System-Product-Name si-pbe]$ watch -n 2 "tail -n 8 relax-check/scf.out"
```

收紧电子阈值后的力如下。读这一段时，应比较它是否仍远小于离子收敛条件，而不是要求它和上一次输出的最后一位完全相同。

```text
[preston@preston-System-Product-Name si-pbe]$ grep -A8 'Forces acting' relax-check/scf.out
     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =    -0.00000000    0.00000000   -0.00000000
     atom    2 type  1   force =     0.00000000   -0.00000000    0.00000000

     Total force =     0.000000     Total SCF correction =     0.000000


     Computing stress (Cartesian axis) and pressure
[preston@preston-System-Product-Name si-pbe]$
```


最后再看原优化输出的末尾。原生程序用时约 1 分 42 秒；这次前段和其他短作业同时运行，WALL 时间还包含了资源竞争。不能只用这个时间推算复杂材料的优化成本。

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 12 relax/relax.out
     interpolate  :      0.17s CPU      0.55s WALL (      39 calls)

     Parallel routines

     PWSCF        :     51.81s CPU   1m41.71s WALL


   This run was terminated on:  21:37:22  22Sep2026

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name si-pbe]$
```


[完整 relax.out](/Atlas/examples/si-pbe/relax/relax.out)中保留了每一步的坐标、能量、力和计时；[逐步数据表](/Atlas/examples/si-pbe/relax/relaxation.csv)用于画下面的图。横轴是电子周期，第一点是尚未移动原子的初始计算，因此 5 个点对应 4 次 BFGS 位置更新。

```text
[preston@preston-System-Product-Name si-pbe]$ python3 plot_si.py relax
<工作目录>/si-pbe/plots/relax.png
```

![位移后的 Si 在固定晶胞优化中的能量和总力变化](/Atlas/examples/si-pbe/plots/relax.png)

绘图命令使用[同一绘图脚本](/Atlas/examples/si-pbe/plot_si.py)，左图减去最终能量，右图直接使用 OUT 中报告的总力。最后一点标注的是输出中的舍入值；逐分量的验收仍以上面那段力为准。

这条路线得到的是固定示例晶胞下、给定约束和 PBE 设置下的一次成功 BFGS 优化。要把结构用于能带、声子或力常数，继续核对那些量对 k 网格、截断和电子阈值的敏感性；本次操作不能代替全布里渊区的动力学稳定性检查。

下一步：接[固定结构 SCF](/Atlas/m/scf/qe/)，之后按需要跳到[能带](/Atlas/m/bands/qe/)或[声子计算](/Atlas/m/phonon-dfpt/qe/)。

```text
明确结构与约束 → relax 输入 → 每步 SCF 与力
                            ↓
                   BFGS 收敛 + 最终坐标
                            ↓
                   更紧电子阈值的力复核
                            ↓
                   固定结构 SCF / 后续性质
```
