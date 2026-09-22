[Wannier90 的 nnkp/mmn 文件](https://wannier90.readthedocs.io/en/latest/user_guide/wannier90/postproc/) · [QE 的 Wannier 接口](https://www.quantum-espresso.org/Doc/INPUT_pw2wannier90.html) · [Fukui–Hatsugai–Suzuki 原文](https://arxiv.org/abs/cond-mat/0503172)

先完成 [Si 的 Wannier 数据准备](/Atlas/m/wannier90/qe/)。那一步除了插值能带，还留下了 `silicon.mmn`：相邻 k 点之间，占据波函数的重叠矩阵。这里接着读取这份文件，沿倒空间的小闭合回路计算相位，再把一个周期切片上的相位加起来。

本次使用 Maxwell 上实际运行的 4×4×4 和 6×6×6 网格，后处理在 Talos 完成。材料是金刚石 Si，QE 与 `pw2wannier90.x` 都为 7.5，赝势为 `Si.pbe-n-van.UPF`，平面波截断能为 40/320 Ry。两套 NSCF 都保留四条占据带，没有加入 SOC，也没有自旋极化。这里不重新计算 SCF，也不从四轨道模型的单位投影矩阵生成重叠。

可以下载[完整后处理示例](/Atlas/examples/berry-si-files.tar.gz)，其中包括两套原始重叠矩阵、邻接表、输入输出和 XML 摘录，另有 [分析脚本](/Atlas/examples/berry-si/analyse.py)、[独立核对脚本](/Atlas/examples/berry-si/verify.py) 与 [绘图脚本](/Atlas/examples/berry-si/plot.py)。公开输入输出只改写了机器上的绝对路径；mmn、nnkp、win 和 eig 保留原始字节，哈希在包内列出。

## 先看重叠文件，而不是先找一个 Chern 数字

这次先在独立目录核对两套输入：

```console
talos@talos-MS-7D54:~/berry-si$ ls source/k4/silicon.mmn source/k6/silicon.mmn
source/k4/silicon.mmn  source/k6/silicon.mmn
talos@talos-MS-7D54:~/berry-si$ head -19 source/k4/silicon.mmn
 Created on 22Sep2026 at 22:45:14                            
           4          64           8
         1         2         0         0         0
   -0.492079364532   -0.864070322919
   -0.024177177982    0.008600504483
   -0.006954094848    0.003688934480
   -0.001458974393   -0.021727581454
   -0.060856117366    0.048384679989
   -0.262666119688   -0.485599056620
   -0.101388769672   -0.135677036682
    0.457089147976   -0.102725998209
   -0.000000202901   -0.000001069679
    0.115052856308    0.541838603776
   -0.334765187801   -0.314273374432
    0.498220387446    0.106823013203
    0.000000704714   -0.000000049065
    0.069682647808   -0.192779368150
   -0.448005764193   -0.570464905859
   -0.450781211753   -0.077055319059
```

第二行表示四条带、64 个 k 点、每个 k 点八个邻居。第三行开始第一个矩阵块：第 1 个 k 点指向第 2 个 k 点，末尾三个整数是周期平移 G，这一条恰好为零。随后是 16 行复数，依次给出一个 4×4 矩阵；每行两个数分别为实部和虚部，第一指标 m 变化最快。因此读取时使用 `reshape((4, 4), order="F")`。

不要把八个邻居都当成同一个方向。这组 fcc 原胞的邻接表包括 ±e₁、±e₂、±e₃ 和 ±(e₁+e₂+e₃)。本页固定第三个倒格坐标，只取 +e₁ 与 +e₂ 两个方向。脚本逐条检查

```text
Δk = k[j] + G - k[i]
```

是否分别等于 (1/N,0,0) 或 (0,1/N,0)。4³ 网格选出 128 条有向链接，其中 32 条跨越周期边界；6³ 网格选出 432 条，其中 72 条跨越边界。越过边界后，G 不能丢掉，否则 k≈1 到 k=0 的链接会被误认成长距离反向跳跃。

`silicon.nnkp` 与 mmn 的每一个五整数块头也要一致。仅有矩阵数目正确不够：索引相同、周期 G 不同，就是另一条链接。脚本还用 nnkp 的实空间与倒空间基矢检查 aᵢ·bⱼ≈2πδᵢⱼ，避免把不同原胞的邻接表混进来。

占据子空间同样要查。两套 `nscf.data-file-schema.xml` 都给出八个电子、四条带，每个 k 点的四个占据数均为 1，`lsda`、`noncolin`、`spinorbit` 均为 false。非磁、无 SOC 的四条空间轨道对应两个等价的自旋通道；下面对其中一个等价通道计算 C，不把八个电子错误地当成八条独立波函数。XML 中的占据数约定也不能直接拿来当自旋分辨的实验电子数。

这份 mmn 是原 USPP 计算经 QE 接口生成的重叠数据，保留接口对该赝势的处理；本页没有另外用伪波函数系数的普通点积替代它。SCF、NSCF 和接口的 OUT 均保留在下载包中，三步各自正常结束，错误文件为空。这些记录证明这批文件的来源与执行状态，不能单靠它们宣布整个布里渊区有绝缘能隙。

## 从四条带的矩阵得到一条链接

同一个占据子空间可以选不同基底，单个矩阵元素因此会改变。本页按照 FHS 的多带形式，先取整个 4×4 占据重叠矩阵的行列式，再除去模长：

```python
determinant = np.linalg.det(matrix)
link = determinant / abs(determinant)
```

这一步得到单位模的复数 U₁(k) 或 U₂(k)。如果行列式接近零，直接归一化会放大噪声，所以脚本先检查每条链接的奇异值，再进行相位运算。这里没有将四条价带分别当作互不简并的单带处理。

沿一个小四边形按 +e₁、+e₂、−e₁、−e₂ 绕一圈，取主值相位：

```python
phase = np.angle(
    U1[k] * U2[k_plus_e1]
    * np.conj(U1[k_plus_e2]) * np.conj(U2[k])
)
```

本文使用这一定向和 FHS 原文的相位约定。固定 k₃ 后，所有 N×N 小格子的 `phase` 相加，再除以 2π，得到该周期二维切片的离散 Chern 和。改变绕行方向会改变符号；这里的零结果不能免除方向检查。

在 Talos 的普通 Python 环境中运行即可，本次 NumPy 为 2.4.6，没有安装新软件，也不需要 MPI 或 Slurm：

```console
talos@talos-MS-7D54:~/berry-si$ export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
talos@talos-MS-7D54:~/berry-si$ python3 -B analyse.py > analyse.out 2> analyse.err; echo "exit=$?"
exit=0
talos@talos-MS-7D54:~/berry-si$ cat analyse.out
GRID 4x4x4: 64 k points, 4 occupied bands, 128 directed links
  singular values: min=0.666896722552 max=0.998430651070; min|det M|=0.576844510352
  reverse overlap residual=1.000e-12; max plaquette phase=9.874075e-06 rad
  12 random U(4) gauges: max phase difference=1.332e-15 rad
  k3=0.000000000: C=+1.574251189688e-17, integer=0, max|phase|=9.630715e-06
  k3=0.250000000: C=-6.222967392051e-17, integer=0, max|phase|=9.874075e-06
  k3=0.500000000: C=+5.227911654458e-18, integer=0, max|phase|=9.729170e-06
  k3=0.750000000: C=-3.775905701703e-17, integer=0, max|phase|=8.864300e-06
GRID 6x6x6: 216 k points, 4 occupied bands, 432 directed links
  singular values: min=0.732745165478 max=0.999355558794; min|det M|=0.670831043483
  reverse overlap residual=1.000e-12; max plaquette phase=8.863247e-06 rad
  12 random U(4) gauges: max phase difference=1.332e-15 rad
  k3=0.000000000: C=-1.698033254699e-17, integer=0, max|phase|=3.947378e-06
  k3=0.166666667: C=-1.554629669799e-17, integer=0, max|phase|=8.863247e-06
  k3=0.333333333: C=-2.903216529575e-17, integer=0, max|phase|=6.946146e-06
  k3=0.500000000: C=-1.026092924293e-16, integer=0, max|phase|=8.344797e-06
  k3=0.666666667: C=+7.990651649978e-17, integer=0, max|phase|=5.314122e-06
  k3=0.833333333: C=+2.368818267856e-17, integer=0, max|phase|=6.676991e-06
POSTPROCESS_CHECKS_PASSED; full-zone gap and material topological classification not established.
talos@talos-MS-7D54:~/berry-si$ cat analyse.err
```

最小奇异值分别约为 0.667 与 0.733，选中的链接没有接近奇异。正向矩阵与反向矩阵的共轭转置最大差约 10⁻¹²，与 mmn 打印精度相当。最大相位只有约 10⁻⁵ rad，远离 ±π 的主值分支边界；这说明这两组离散数据没有遇到这一类相位跳变，不能据此补出尚未计算的导带或全区能隙。

`C` 列保留未取整的浮点和。`integer` 只是在先检查离最近整数小于 10⁻¹⁰ 后用于显示；它没有修改原始相位。4³ 的四个切片、6³ 的六个切片都得到数值零。离散 FHS 和本来就有整数结构，因此“接近整数”是一项算法检查，单独不能作为网格收敛证据。两种网格结果一致，是这次有限对照的结果。

## 换一套占据基底，结果会不会改变

脚本在每个 k 点独立生成一个随机 U(4) 矩阵 G(k)，将重叠变为

```text
M'(k,k+b) = G(k)† M(k,k+b) G(k+b)
```

这只是同一个四维占据子空间的基底变换，不是重新做 DFT。每种网格各检查十二组随机规范，同时检查 G†G=I；全部小格子的相位变化不超过 1.33×10⁻¹⁵ rad。跨周期边界的链接也参与检查，不能只测切片内部。

另一个脚本直接从原 mmn 的矩阵做 SVD 极分解，把四条酉矩阵按回路顺序相乘，再求整个回路的行列式相位。它没有复用主脚本的标量链接计算：

```console
talos@talos-MS-7D54:~/berry-si$ python3 -B verify.py > verify.out 2> verify.err; echo "exit=$?"
exit=0
talos@talos-MS-7D54:~/berry-si$ cat verify.out
k4: independent SVD polar-matrix loop phase difference = 1.681e-15 rad
k6: independent SVD polar-matrix loop phase difference = 1.587e-15 rad
Synthetic periodic link field: C = 1.000000000000 (expected +1; algebra check only)
INDEPENDENT_CHECKS_PASSED
```

两种方法的相位一致到约 10⁻¹⁵ rad。第三行是单独构造的周期链接场，已知总相位为 2π，用于检查脚本确实能返回非零整数以及周期包裹的方向。它只是代数检验，不属于 Si 数据，也不会画进材料结果图。原始三十个源文件的哈希在分析前后核对一致。

## 把小回路相位放回倒空间

![Si 两种网格的切片相位与离散 Chern 和](/Atlas/examples/berry-si/figures/berry-slices.png)

前两幅图画 k₃=0 切片，色标是每个小格子的回路相位，单位为微弧度。这里的横纵坐标是沿 b₁、b₂ 的分数坐标；fcc 的这两条倒格基矢并不正交，所以图上的方格表示坐标网格，不是笛卡尔倒空间中的正方形。

一个实际小格子的面积为 |b₁×b₂|/N²，本例 4³ 与 6³ 分别约为 0.23954227 和 0.10646323 Å⁻²。CSV 另外保留 `phase_per_area_A2`，即回路相位除以该面积，单位 Å²，可看作该有限小格子沿 b₁×b₂ 方向的面积平均量。它采用上面的定向相位约定，不应直接标成笛卡尔 Ωz。C 的求和使用原始无量纲相位，不再额外乘面积。

右图保留所有切片的原始和，约 10⁻¹⁶ 的纵轴尺度显示的是数值残差。相位图的局部小值也没有被改成严格零；仅凭两个粗网格，不能把这些约 10⁻⁵ rad 的结构解释为已收敛的局部 Berry 曲率。

![占据重叠的最小奇异值与随机规范检查](/Atlas/examples/berry-si/figures/berry-checks.png)

左图显示每条已选链接的最小奇异值，右图显示十二次随机基底变换引起的最大相位变化。两图分别回答“链接是否接近不可逆”和“结果是否依赖任意基底选择”，不能代替导带能量的检查。

重新出图时，将完整压缩包解压，进入 `berry-si`，在已有 NumPy、Matplotlib 的环境中运行：

```bash
python3 plot.py
```

脚本只读取 `results/` 中的 CSV，不访问远端机器，生成 `figures/berry-slices.png`、`berry-checks.png` 和对应 PDF。切片相位来自 [k4](/Atlas/examples/berry-si/results/k4-plaquettes.csv)、[k6](/Atlas/examples/berry-si/results/k6-plaquettes.csv)，切片总和在 [slices.csv](/Atlas/examples/berry-si/results/slices.csv)，完整检查数值在 [summary.json](/Atlas/examples/berry-si/results/summary.json) 与 [independent-check.json](/Atlas/examples/berry-si/results/independent-check.json)。

这次可以确认：在两套真实 QE 占据波函数重叠数据上，固定第三个倒格坐标的十个周期切片都给出离散 C=0，链接与规范检查通过。这里没有 SOC，四条带的文件也没有包含导带，因此没有独立证明全布里渊区的绝缘能隙；这条路线不提供 Z₂、边缘态或三维材料的完整拓扑分类。

下一步先沿 [Wannier 父链](/Atlas/m/wannier90/qe/) 核对物理模型与需要保留的能带。如果要把离散切片结果用于材料结论，需要用同一协议检查占据态与未占据态在整个布里渊区的分离，并继续检查采样与基组；不能把本页的四带数据直接补称含 SOC 的拓扑结果。

```text
同一结构 SCF → 全网格 NSCF → pw2wannier90 原始 mmn + nnkp
                                   ↓
                         占据数 / 周期 G / 链接检查
                                   ↓
                     四占据带 det 链接 → 小回路相位
                                   ↓
                     固定 k3 的周期切片 Chern 和
                                   ↓
                 网格对照 / 随机规范 / 独立回路核对
```
