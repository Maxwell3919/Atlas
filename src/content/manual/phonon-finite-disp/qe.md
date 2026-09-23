[Phonopy 的 QE 接口](https://phonopy.github.io/phonopy/qe.html) · [Phonopy Python API](https://phonopy.github.io/phonopy/phonopy-module.html) · [pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html)

有限位移声子把“推一下原子”变成真正的输入文件。原子位移后，做固定结构 SCF，读取所有原子的力；用正负位移的力差得到力常数，再求不同 q 点的振动频率。

这里沿用 [DFPT 声子](/Atlas/m/phonon-dfpt/qe/) 中的 fcc Al 原胞，改用超胞和 QE 力计算。两条路线的电子结构程序都是 QE 7.5，赝势都是 LDA-PZ 的 `Al.pz-vbc.UPF`。差别在于如何求恢复力，不是换成一个已有势函数来预测它。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

## 从一个原胞变成带位移的超胞

原胞结构取自已结束的 [晶胞优化](/Atlas/m/vc-relax/qe/)，立方晶格常数为 3.95606780 Å。用 2×2×2 个原胞得到 8 原子超胞。这里采用 Phonopy 4.5.0 的 Python API，明确保留输入原胞的基矢定义 `primitive_matrix='P'`：

```python
ph = Phonopy(unitcell, np.eye(3, dtype=int) * 2,
             primitive_matrix='P')
ph.generate_displacements(distance=0.01, is_plusminus=True)
```

这两行是实际输入生成过程的核心。`unitcell` 的晶格单位为 Å，质量单位为原子质量单位；因此这里的 0.01 是 Å。完整的 [结构和位移生成脚本](/Atlas/examples/al/prepare_finite.py) 保存晶格、质量、位移方向和生成顺序，不能只拿一份力文件猜它对应哪个位移。

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ ls
disp-001  disp-002  phonopy_disp.yaml  run.slurm
```
Al 的对称性把独立位移压缩到一个方向。由于这里明确使用正负成对位移，仍有两个 SCF 输入。实际移动的是编号 0 的原子，两个笛卡尔位移分别是 (−0.0070710678, 0, +0.0070710678) Å 和反向；向量长度都是 0.01 Å。它沿这份原胞的一条基矢方向，不应把它口头称作 x 轴位移。

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ cat disp-001/al.scf.in
&CONTROL
 calculation = 'scf'
 prefix = 'al'
 pseudo_dir = '<赝势库路径>'
 outdir = './tmp'
 tstress = .true.
 tprnfor = .true.
 verbosity = 'high'
/
&SYSTEM
 ibrav = 0
 nat = 8
 ntyp = 1
 ecutwfc = 40
 ecutrho = 160
 occupations = 'smearing'
 smearing = 'mv'
 degauss = 0.02
 nbnd = 18
/
&ELECTRONS
 conv_thr = 1.0d-12
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.00178739803459 0.00000000000000 0.00000000000000
Al 0.50000000000000 0.00000000000000 0.00000000000000
Al 0.00000000000000 0.50000000000000 0.00000000000000
Al 0.50000000000000 0.50000000000000 0.00000000000000
Al 0.00000000000000 0.00000000000000 0.50000000000000
Al 0.50000000000000 0.00000000000000 0.50000000000000
Al 0.00000000000000 0.50000000000000 0.50000000000000
Al 0.50000000000000 0.50000000000000 0.50000000000000
CELL_PARAMETERS angstrom
-3.95606780081072 0.00000000000000 3.95606780081072
0.00000000000000 3.95606780081072 3.95606780081072
-3.95606780081072 3.95606780081072 0.00000000000000
K_POINTS automatic
8 8 8 0 0 0
```
`nat=8` 和 8 行原子坐标对应超胞。`calculation=scf` 保持这些位移不动，`tprnfor=.true.` 要求把力写进输出。若把这里改成 `relax`，原子会往平衡位置回去，输出力不再对应最初设定的 0.01 Å。

二阶力常数来自力随位移的变化，位移越小，同样的力噪声在除以位移后就越显著；位移过大又会混入更高阶响应。这里把电子阈值设为 `conv_thr=1.0d-12`，并在同一超胞上比较 0.01、0.02 Å 两个幅度。电子能量残差小不等于力误差已知，最后仍要看两组力得到的频率怎样变化。

超胞增大了实空间体积，同样的电子采样密度需要相应缩小 k 网格。这个 2³ 超胞使用 8³ k 点，等价于原胞约 16³ 的采样密度；后面的 3³ 超胞用 6³，比较超胞大小时另外补算了 2³ 超胞的 9³ k 点，使两者都对应原胞约 18³ 密度。

## 两个 SCF 顺序执行，原始输出各自保留

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-fd2
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /opt/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
set -e
cd "<工作目录>/al/finite-disp/n2-d0.01/disp-001"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/finite-disp/n2-d0.01/disp-002"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
```
这是本次实际使用的串行两步脚本：同一作业分配 8 个 MPI 进程，先完成 `disp-001`，再进入 `disp-002`。每个子目录的 `tmp` 独立，输入和受力对应关系也保持清楚。

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ sbatch --dependency=afterok:1956 run.slurm
Submitted batch job 1959
```
这次依赖前面的弹性短作业释放资源后启动。单独复现实例时，使用 `sbatch run.slurm` 即可；不要把文章中的旧作业号提交为自己机器上的依赖。

```bash
squeue -j 1959 -o "%.10i %.16j %.2t %.10M %.5C"
tail -f disp-001/al.scf.out
```

## 在 OUT 里把位移与力对应起来

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ grep -A12 "Forces acting on atoms" disp-001/al.scf.out
     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =     0.00138549    0.00000000   -0.00138549
     atom    2 type  1   force =    -0.00076171    0.00000000    0.00076171
     atom    3 type  1   force =     0.00006090    0.00039391    0.00036758
     atom    4 type  1   force =    -0.00036758   -0.00039391   -0.00006090
     atom    5 type  1   force =    -0.00036758    0.00039391   -0.00006090
     atom    6 type  1   force =     0.00006090   -0.00039391    0.00036758
     atom    7 type  1   force =     0.00002632    0.00000000   -0.00002632
     atom    8 type  1   force =    -0.00003674    0.00000000    0.00003674
```
这 8 行依次对应输入里的 8 个原子，每行给出 x、y、z 三个力分量。受位移的原子不会是唯一受力的原子；周围原子的恢复力正是力常数需要的信息。原始 QE 输出用 Ry/Bohr，后处理通过 ASE 3.29.0 读取并转换为 eV/Å，随后 Phonopy 使用 Å、eV/Å 和原子质量计算 THz 频率。两套单位不能混着代入。

```console
maxwell@maxwell:~/al/finite-disp/n2-d0.01$ tail -9 disp-001/al.scf.out
 
     PWSCF        :     19.88s CPU     20.40s WALL

 
   This run was terminated on:  21:36:45  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
对第二个位移也做同样检查。后处理脚本要求每份文件有一次 `JOB DONE.`、出现电子收敛、没有 SCF 失败且 stderr 为空，然后才读取受力；目录存在或退出码为零本身不够。完整 [disp-001 输出](/Atlas/examples/al/finite-disp/n2-d0.01/disp-001/al.scf.out) 保留了从结构、电子迭代到力和计时的全部段落。

## 由力重建频率，并记录声学和规则

[analyse.py](/Atlas/examples/al/finite-disp/analyse.py) 从 `phonopy_disp.yaml` 读取位移顺序，从相同编号的 `.out` 读取力，先生成未额外对称化的力常数，再保存平移和规则处理后的力常数与声子路径数据。

```console
maxwell@maxwell:~/al/finite-disp/..$ .venv/bin/python finite-disp/analyse.py
n2-d0.01 raw FC drift= 1.7763568394002505e-15 ; Gamma THz= [-5.29508182e-08  4.25307894e-08  5.00338842e-08] ; X THz= [6.3569392 6.3569392 9.8421396]
n2-d0.02 raw FC drift= 1.8180444808058027e-05 ; Gamma THz= [-5.10637868e-08 -3.78379398e-08  9.25452616e-08] ; X THz= [6.35841564 6.35841564 9.84459054]
n2-d0.01-k9 raw FC drift= 1.818044481011194e-05 ; Gamma THz= [-3.61776110e-08 -1.57964203e-08  7.30035453e-08] ; X THz= [6.28098398 6.28098398 9.87013437]
n3-d0.01 raw FC drift= 1.8180444807003315e-05 ; Gamma THz= [-1.27883366e-07 -5.19769200e-08 -1.74046920e-08] ; X THz= [5.63646925 5.63646925 7.82783897]
```
输出中的 drift 是力常数平移和规则残差，单位 eV/Å²。Γ 点处理后的约 10⁻⁷ THz 是浮点计算残差，应与有限波矢处真正的负频支分开讨论。`phonopy_params.yaml` 留下了用于后续频率计算的力常数；原始 QE 受力输出没有被覆盖。

## 位移幅度和超胞大小是两项不同的检查

首先保持 2³ 超胞、8³ k 网格不变，只把位移从 0.01 Å 加到 0.02 Å。正负成对计算后，X 点频率为：

| 超胞 / k 网格 | 位移 / Å | X 的三支频率 / THz |
|---|---:|---|
| 2³ / 8³ | 0.01 | 6.356939, 6.356939, 9.842140 |
| 2³ / 8³ | 0.02 | 6.358416, 6.358416, 9.844591 |
| 2³ / 9³ | 0.01 | 6.280984, 6.280984, 9.870134 |
| 3³ / 6³ | 0.01 | 5.636469, 5.636469, 7.827839 |

前两行很接近，说明这个测试下位移幅度没有显著改变 X 点频率。后两行保持约 18³ 的原胞电子采样密度，却显示明显的超胞差异；所以不能把“位移幅度稳定”写成“完整有限位移声子已经收敛”。X 点位于 2³ 超胞对应的网格上，却不是 3³ 超胞的直接网格点，后者这里依赖力常数插值，读图时也要记住这层区别。

<figure><img src="/Atlas/examples/al/figures/finite-displacement.png" alt="Al有限位移声子的位移幅度与超胞比较" loading="lazy"/><figcaption>左侧比较同一超胞的两种位移幅度；右侧在相同原胞等效电子采样密度下比较两种超胞。不同检查分别呈现，不混成一条收敛结论。</figcaption></figure>

[plot_finite.py](/Atlas/examples/al/plot_finite.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)） 直接读取各目录的 `bands.csv`，将 Phonopy 的 THz 乘以 33.35640952 转为 cm⁻¹，并按 Γ—X—W—L—Γ 的分段端点放标签。下载整个 Al 示例的数据结构后，在本机运行：

```bash
python3 plot_finite.py
```

这条路线已经从明确结构、真实正负位移输入、SCF 受力走到可复算的声子图；图同时揭示了当前超胞系列还不足以作完整数值收敛声明。下一步增大超胞并维持相当的电子采样密度，再与 [DFPT 声子](/Atlas/m/phonon-dfpt/qe/) 的直接 q 点核对。若出现可见负频支，按 [虚频排查](/Atlas/m/imaginary-phonon/qe/) 检查本征矢和数值来源，不要先把负值改成零。

```text
优化后的原胞 → 超胞和正负位移 → 固定结构 QE SCF
                                     ↓
                               力与位移编号配对
                                     ↓
                       力常数 → 声学和规则记录 → 声子图
                                     ↓
                          位移幅度 / 超胞 / k网格检查
```
