[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [Born 稳定性条件原始论文](https://doi.org/10.1103/PhysRevB.90.224104)

对晶体施加一个很小的形变，再让电子重新达到自洽，应力会怎样改变？弹性常数就是这个变化的斜率。Born 判据进一步检查：任意足够小的均匀应变，是让能量升高，还是存在一个能量下降的方向？

这里继续使用新计算的 **fcc Al 单原子原胞**。它是三维立方体系，只有三个独立弹性常数 C₁₁、C₁₂、C₄₄；下面的判据不能直接移植到二维薄层或低对称性晶体。原始结构来自 QE 官方金属示例，经 [晶胞优化](/Atlas/m/vc-relax/qe/) 后，立方晶格常数为 3.95606780 Å。优化最后压力约 0.02 kbar，接近这里采用的零外压条件。

本例的输入、输出、数据表和绘图脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后保留目录结构，进入 `al` 运行文中的绘图命令；赝势按正文的官方来源准备。

## 留住零应变结构，再建立成对的形变

[Al 声子页的固定结构 SCF](/Atlas/m/phonon-dfpt/qe/) 中保存的晶格作为参考。先复制输入，新的目录只放新的结构和输出，原来的 SCF 保留：

```console
maxwell@maxwell:~/al/elastic$ cp ../dfpt/al.scf.in al.reference.in
maxwell@maxwell:~/al/elastic$ cp al.reference.in xx_+0.005/al.scf.in
maxwell@maxwell:~/al/elastic$ vi xx_+0.005/al.scf.in

```
这里的 `+0.005` 表示笛卡尔 x 方向伸长 0.5%。对每条晶格矢量，只把它的 x 分量乘以 1.005，y、z 分量保持不变；不是把整条矢量一起缩放。实际编辑后的输入如下：

```console
maxwell@maxwell:~/al/elastic$ cat xx_+0.005/al.scf.in
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
 nat = 1
 ntyp = 1
 ecutwfc = 40
 ecutrho = 160
 occupations = 'smearing'
 smearing = 'mv'
 degauss = 0.02
 nbnd = 6
/
&ELECTRONS
 conv_thr = 1.0d-12
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.00000000000000 0.00000000000000 0.00000000000000
CELL_PARAMETERS angstrom
-1.98792406990739 0.00000000000000 1.97803390040536
0.00000000000000 1.97803390040536 1.97803390040536
-1.98792406990739 1.97803390040536 0.00000000000000
K_POINTS automatic
16 16 16 0 0 0
```
原胞只有一个等价 Al 原子，分数坐标保持 (0,0,0)。这一步是受控应变下的 **SCF**，不能再让 `vc-relax` 把施加的形变优化回去。更复杂的多原子晶体还要区分固定内部坐标的弹性响应与固定晶胞、允许内部原子弛豫的响应。

```console
maxwell@maxwell:~/al/elastic$ diff al.reference.in xx_+0.005/al.scf.in
29c29
< -1.97803390040536 0.00000000000000 1.97803390040536
---
> -1.98792406990739 0.00000000000000 1.97803390040536
31c31
< -1.97803390040536 1.97803390040536 0.00000000000000
---
> -1.98792406990739 1.97803390040536 0.00000000000000
```
负应变另开 `xx_-0.005`。成对计算可以用中心差分消掉参考压力的常数偏移。剪切也成对计算：这里把工程剪应变记作 γ，变形矩阵的 xy 和 yx 元素都取 γ/2；因此 σxy 对 γ 的斜率才是 C₄₄。把两个矩阵元素都误填成 γ，会让读出的剪切斜率相差一倍。

本次共做 ±0.003、±0.005、±0.008 三种幅度，每种幅度有 xx 和 xy 两类形变。下面是一份真实剪切输入的结构部分，可与拉伸目录对照：

```console
maxwell@maxwell:~/al/elastic$ tail -11 xy_+0.005/al.scf.in
/
ATOMIC_SPECIES
Al 26.9815385 Al.pz-vbc.UPF
ATOMIC_POSITIONS crystal
Al 0.00000000000000 0.00000000000000 0.00000000000000
CELL_PARAMETERS angstrom
-1.97803390040536 -0.00494508475101 1.97803390040536
0.00494508475101 1.97803390040536 1.97803390040536
-1.97308881565435 1.97308881565435 0.00000000000000
K_POINTS automatic
16 16 16 0 0 0
```
## 提交后先检查应力是否真的写出

每个目录各自使用 `outdir=./tmp`，避免并行计算互相覆盖密度。本次把 12 次短 SCF 串在同一个 8 进程 Slurm 作业内，全部输入相同的截断能、展宽和电子阈值。

```console
maxwell@maxwell:~/al/elastic$ cat run.slurm
#!/bin/bash
#SBATCH --job-name=atlas-al-elastic
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
cd "<工作目录>/al/elastic/xx_-0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xx_+0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xx_-0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xx_+0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xx_-0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xx_+0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_-0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_+0.003"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_-0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_+0.005"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_-0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
cd "<工作目录>/al/elastic/xy_+0.008"
mpirun -np 8 <qe_bin>/pw.x -in al.scf.in > al.scf.out 2> al.scf.err
```
```console
maxwell@maxwell:~/al/elastic$ sbatch run.slurm
Submitted batch job 1956
```
运行中先看队列，再看正在运行那个子目录的末尾；第一份输出结束后，脚本还会进入下一份结构。

```bash
squeue -j 1956 -o "%.10i %.16j %.2t %.10M %.5C"
tail -f xx_+0.005/al.scf.out
```

```console
maxwell@maxwell:~/al/elastic$ grep -A3 "total   stress" xx_+0.005/al.scf.out
          total   stress  (Ry/bohr**3)                   (kbar)     P=       -4.08
  -0.00005559   0.00000000   0.00000000           -8.18        0.00        0.00
  -0.00000000  -0.00001386   0.00000000           -0.00       -2.04        0.00
   0.00000000   0.00000000  -0.00001386            0.00        0.00       -2.04
```
左侧 3×3 张量的单位是 Ry/bohr³，右侧是同一张量的 kbar 表示，`P` 是标量压力。这里用于常规拉伸为正的应力定义时，对 QE 输出取负号；再换算为 GPa。转换常数是 1 Ry/bohr³ = 14710.5076 GPa，或直接用 1 kbar = 0.1 GPa。脚本读取左侧较多有效数字，避免用右侧两位小数做很小应变的差分。

```console
maxwell@maxwell:~/al/elastic$ tail -9 xx_+0.005/al.scf.out
 
     PWSCF        :      3.30s CPU      3.81s WALL

 
   This run was terminated on:  21:35:27  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
`JOB DONE.` 只是这一份程序结束。每份输出还检查电子收敛、`Error in routine`、输入对应的结构、应力段与单独的 stderr；不能只统计有几个 `.out` 文件。

## 从正负两份应力读出三个斜率

[analyse.py](/Atlas/examples/al/elastic/analyse.py) 逐份读真实输出，再生成 [strain-stress.csv](/Atlas/examples/al/elastic/strain-stress.csv)。它不会在某份计算未结束时填入默认数值。拉伸对给出

**C₁₁ = [σ<sub>xx</sub>(+ε) − σ<sub>xx</sub>(−ε)] / (2ε)**

**C₁₂ = [σ<sub>yy</sub>(+ε) − σ<sub>yy</sub>(−ε)] / (2ε)**

实际脚本把 yy 和 zz 两个等价分量取平均；剪切对用相同的中心差分求 C₄₄。

```console
maxwell@maxwell:~/al/elastic$ ../.venv/bin/python analyse.py
All 12 SCFs: one JOB DONE., electronic convergence, empty stderr.
strain     C11       C12       C44       B         GH        E        nu
0.003   168.4843   41.4836   52.3694   83.8172   56.5700  138.5417   0.2245
0.005   168.1411   41.6749   52.4871   83.8303   56.5504  138.5065   0.2246
0.008   167.3228   42.0629   52.7004   83.8162   56.4705  138.3425   0.2249
```
三种幅度的结果接近，说明这一段应力—应变关系看起来近似线性。到这里还不能说弹性常数已经收敛；下一组真实计算正好展示了原因。

## 幅度检查通过后，金属 k 网格仍然会改变答案

固定 ±0.005 的应变、结构、赝势、40/160 Ry 截断和 0.02 Ry 展宽，只把电子网格逐级加密，得到：

| 电子网格 | C₁₁ / GPa | C₁₂ / GPa | C₄₄ / GPa | B / GPa |
|---|---:|---:|---:|---:|
| 16³ | 168.141 | 41.675 | 52.487 | 83.830 |
| 24³ | 116.625 | 66.212 | 27.273 | 83.016 |
| 32³ | 127.158 | 61.475 | 36.659 | 83.369 |
| 40³ | 129.364 | 60.504 | 42.690 | 83.458 |
| 48³ | 125.995 | 62.122 | 39.277 | 83.413 |

16³ 的三个幅度几乎给出相同斜率，可是换到 24³，C₁₁ 和 C₄₄ 明显改变。与此同时体模量 B 的变化很小。这说明检查一个稳定的能量或一个稳定的 B，不能替其他弹性分量作数值收敛证明。后面的网格系列继续按同一组形变比较；没有给这些数字贴上已收敛的材料常数标签。

<figure><img src="/Atlas/examples/al/figures/elastic-kmesh.png" alt="Al 三个弹性分量和体模量随k网格变化" loading="lazy"/><figcaption>同一组 ±0.5% 应变的电子网格检查。不同分量对网格的敏感程度明显不同。</figcaption></figure>

[绘图脚本](/Atlas/examples/al/plot_elastic.py) 读取 `elastic/kmesh-comparison.csv` 与原始应力表，在本地运行 `python3 plot_elastic.py`；图上的点由这些计算逐项得到。

## 最后才把常数代入 Born 条件

对接近零外压的立方晶体，三个条件是

**C₁₁ − C₁₂ > 0，C₁₁ + 2C₁₂ > 0，C₄₄ > 0**

已完成的各组参数在这三个符号条件上均给出正值。但目前弹性分量仍显示电子网格敏感性，因此合适的表述是：这些已计算参数下没有出现均匀微小应变的负曲率；定量材料常数的数值收敛尚未建立。有限压力、低对称性与二维体系必须采用对应条件和单位，不能只替换材料名。

Born 条件检验均匀应变的局部响应，不能代替 [完整声子网格](/Atlas/m/phonon-dfpt/qe/) 或热力学相稳定性。下一步到 [弹性模量](/Atlas/m/elastic-moduli/qe/) 看怎样从同一套 Cᵢⱼ 计算 B、G、E 和 ν。

```text
零应变结构 → 成对拉伸 / 剪切 SCF → 应力符号与单位
                                  ↓
                       中心差分 → 幅度检查 → k网格检查
                                                   ├→ Born 条件
                                                   └→ 弹性模量
```
