异质结的 SOC 能带若出现开隙或轨道次序改变，下一步需要用占据波函数检验正常态拓扑。能带图给出电子的能量，却没有直接告诉我们占据态沿布里渊区变化时积累了怎样的几何相位。陈数把一个闭合二维周期面上的 Berry 曲率通量汇总成整数，用来刻画该面上占据子空间的整体拓扑性质；要理解非零陈数与霍尔响应的联系，还要结合相应体系的能隙和占据。这里先用金刚石 Si 建立可逐项核对的零整数算例：相邻 k 点的原生重叠矩阵经过周期闭合、回路求和之后，是否给出一致的切片陈数，并且不随占据态的换基改变？

这条进阶路线的几何相位基础可以用现存 Si 数据练习。本例读取 QE 7.5 导出的完整 4×4×4 与 6×6×6 网格，在固定分数坐标 k₃ 的平面内沿倒格方向 b₁、b₂ 构造 FHS 回路。十个实际采样切片均得到离散整数 C=0。下面的链接、跨界处理和规范检查共同说明这个整数怎样从文件中算出；这些 Si 数据回答的是周期切片的计算问题。

准备这类文件的前置步骤见 [QE–Wannier90 接口](/Atlas/m/wannier90/qe/)。重叠矩阵格式见 [Wannier90 的后处理文件说明](https://wannier90.readthedocs.io/en/latest/user_guide/wannier90/postproc/)，接口参数见 [pw2wannier90.x 文档](https://www.quantum-espresso.org/Doc/INPUT_pw2wannier90.html)。

[下载输入、原生重叠矩阵、完整源码与结果](/Atlas/examples/topo_berry_si_files.tar.gz)。已有矩阵可以直接用于 Python 后处理；若从 QE 重新生成矩阵，需先完成 SCF、完整均匀网格 NSCF 和 pw2wannier90 接口导出。

## 结构、网格和脚本输入

| 参数 | 本例采用值 |
| --- | --- |
| 结构 | 金刚石 Si；<code>ibrav=2</code>，<code>celldm(1)=10.2</code> bohr，固定离子 |
| 赝势名 | <code>Si.pbe-n-van.UPF</code> |
| 截断能 | <code>ecutwfc=40</code> Ry，<code>ecutrho=320</code> Ry |
| SCF | 10×10×10 网格，<code>conv_thr=1d-12</code> Ry |
| NSCF | 完整均匀 4×4×4 或 6×6×6 网格；<code>nbnd=4</code>，固定占据 |
| 对称性处理 | <code>nosym=.true.</code>，<code>noinv=.true.</code>，保留完整网格 |
| 自旋 | 非磁、标量、无 SOC；XML 中 <code>lsda</code>、<code>noncolin</code>、<code>spinorbit</code> 均为 false |

XML 记录八个电子和四条占据空间带；每条空间带包含两个等价自旋通道。脚本对四维空间带子空间计算一次行列式链接。保存文件只有这四条占据带，没有导带，因而本例没有独立确定全布里渊区绝缘隙。这里得到的是已采样周期切片的离散陈数。

两套输入分别放在 <code>source/k4/</code> 和 <code>source/k6/</code>。当前脚本固定处理 N=4、6 和四条占据空间带，使用下列文件：

| 实际读取的文件 | 读取内容 |
| --- | --- |
| <code>silicon.win</code> | <code>kpoints</code> 块中的分数坐标与点序 |
| <code>silicon.nnkp</code> | k 点、邻接块、整数倒格平移 G、实格及倒格基矢；与 .win 点序核对 |
| <code>silicon.mmn</code> | 带数、k 点数、每点邻居数及完整复重叠矩阵；块头与 .nnkp 核对 |
| <code>nscf.data-file-schema.xml</code> | 带数、k 点数、电子数、占据和自旋设置 |
| <code>si.scf.out/err</code>、<code>si.nscf.out/err</code>、<code>pw2wan.out/err</code> | 每个输出须有一次 <code>JOB DONE.</code>、无列出的失败告警，stderr 为空 |

包中还保存了 SCF XML、QE 输入、接口输入 <code>silicon.pw2wan</code> 和原生 <code>silicon.eig</code>。它们用于查看计算设置及能级；当前分析器不读取 .eig，也不依赖 AMN、HR 或 Wannier 插值模型。输入、日志和 XML 中的机器路径已改为通用路径，原生矩阵字节及数值数据保持原样。复算这里的后处理无需赝势或波函数目录。

SCF 日志显示 10 次迭代后自洽，最终估计误差为 3.1×10⁻¹⁴ Ry；两套 NSCF 和接口程序均正常结束。

## 读取矩阵与周期链接

4³ 网格的 <code>source/k4/silicon.mmn</code> 开头如下：

~~~text
 Created on22Sep2026 at22:45:14
4 64 8
1 2 0 0 0
-.492079364532 -.864070322919
-.024177177982 .008600504483
-.006954094848 .003688934480
-.001458974393 -.021727581454
~~~

第二行表示 4 条带、64 个 k 点、每点 8 个邻居。下一行 <code>1 2 0 0 0</code> 是源点、目标点和三个 G 分量；此后共有 16 行复元素。Wannier90 写矩阵时第一带索引变化最快，因此源码用 <code>reshape((4,4), order="F")</code> 重排。6³ 文件的头部对应 <code>4 216 8</code>。

方向由坐标与 G 确定：

~~~python
delta = N * (k[j] + G - k[i])
~~~

当 <code>delta</code> 是 (1,0,0) 或 (0,1,0)，分别选作 +e₁、+e₂ 链接。跨边界时目标点折回第一周期，G 恢复它的真实邻接位置。4³ 网格选出 128 条有向链接，其中 32 条跨界；6³ 网格为 432 条，其中 72 条跨界。相邻点编号本身不表示方向。

倒格基矢来自 .nnkp。程序核对 $a_i\cdot b_j=2\pi\delta_{ij}$，实际最大残差为 2.15×10⁻⁷，并由 b₁、b₂ 求小格面积。

## FHS 回路与单位

对占据态重叠矩阵 M，先将其行列式归一化为单位模链接；然后按 +e₁、+e₂、−e₁、−e₂ 绕行。以下代码表达了实际采用的相位和切片求和约定：

~~~python
U1 = det(M1) / abs(det(M1))
U2 = det(M2) / abs(det(M2))
phi = angle(U1(k) * U2(k+e1) * conj(U1(k+e2)) * conj(U2(k)))
C_raw = sum(phi_on_fixed_k3_slice) / (2*pi)
~~~

这里的函数记号说明各链接所在的 k 点，完整索引实现见 <code>analyse.py</code>。<code>angle</code> 取弧度主值。绕行方向决定陈数符号；对每个固定 k₃ 的周期面，将 N×N 个小格相位相加。占据态在每个 k 点作任意 U(4) 换基时，闭合回路相位保持不变。这是 [Fukui–Hatsugai–Suzuki 离散陈数方法](https://doi.org/10.1143/JPSJ.74.1674) 在多占据带子空间中的行列式链接形式。原文式 (16) 用多带重叠矩阵的归一化行列式定义链接，式 (8) 取闭合小格的主值相位，式 (9) 将整个周期面求和；这三步分别对应上面的 <code>det(M)</code>、<code>phi</code> 和 <code>C_raw</code>。原文 Fig. 1 比较的是磁通晶格模型在不同网格上的场强与整数，本页把同一离散方法用于 Si 的四条占据空间带。

| 输出字段 | 单位及位置 |
| --- | --- |
| <code>phase_rad</code> | 弧度；逐 plaquette CSV |
| <code>phase_per_area_A2</code> | Å²；相位除以真实倒空间小格面积，逐 plaquette CSV |
| <code>plaquette_area_invA2</code> | Å⁻²；保存在 slices.csv 和 summary.json 的切片条目 |
| <code>chern_raw</code>、<code>chern_integer</code> | 无量纲；逐切片表 |
| 奇异值、行列式模长 | 无量纲；逐链接 CSV 和摘要 |

<code>phase_per_area_A2</code> 是有限小格的面积平均量。解释连续 Berry 曲率分布还需检查局部量随网格加密的变化；两个网格得到相同整数本身不证明局部曲率收敛。

[FHS 原文 Fig. 1(a–c)](https://arxiv.org/pdf/cond-mat/0503172#page=3)（PDF 第 3 页）给出了这种区别：a、b 是同一磁通晶格模型中间带在 3×9、9×27 网格上的逐小格场强，c 是连续场的有限差分近似。两种离散网格得到相同陈数，但纵轴尺度不同，小格相位会随网格加密而缩小；比较连续曲率前必须处理面积因子。横轴是该模型 Landau 规范下的磁布里渊区 kx、ky，长方形取值范围也不能被直接解释为材料的面内各向异性。

本站复现这种比较可直接使用[4³ 逐小格 CSV](/Atlas/examples/topo_berry_si/k4-plaquettes.csv)：选择相同的 <code>k3_fraction</code> 切片，以 <code>k1_fraction</code>、<code>k2_fraction</code> 定位小格，分别读 <code>phase_rad</code> 或 <code>phase_per_area_A2</code>；[6³ 表](/Atlas/examples/topo_berry_si/k6-plaquettes.csv)使用相同字段。用 gnuplot 将相位作为逐格色值时保留实际网格，并统一对应物理量的色标；面积归一化前后的量各用自己的单位，避免平滑插值掩盖网格差异。这复用本页真实 Si 数据，不引入原文磁通模型的曲率分布。

## 十个实际采样切片

固定 k₃=s/N，其中 s=0,…,N−1，就从 N³ 网格取出一个含 N×N 个点的二维面。k₁、k₂ 都按周期闭合：最后一排、最后一列的链接通过 G 接回第一排、第一列，因此每个面有 N² 个小格。4³ 网格给出 4 个面，6³ 网格给出 6 个面，合计下表的十个切片。这里的 k₃ 是倒格基底中的分数坐标，不是笛卡尔 k_z。

| 网格 | 分数坐标 k₃ | 小格数 | C_raw | 最近整数 | 最大相位绝对值 / rad |
| --- | ---: | ---: | ---: | ---: | ---: |
| 4×4×4 | 0.0000 | 16 | +1.5743e-17 | 0 | 9.6307e-06 |
| 4×4×4 | 0.2500 | 16 | -6.2230e-17 | 0 | 9.8741e-06 |
| 4×4×4 | 0.5000 | 16 | +5.2279e-18 | 0 | 9.7292e-06 |
| 4×4×4 | 0.7500 | 16 | -3.7759e-17 | 0 | 8.8643e-06 |
| 6×6×6 | 0.0000 | 36 | -1.6980e-17 | 0 | 3.9474e-06 |
| 6×6×6 | 0.1667 | 36 | -1.5546e-17 | 0 | 8.8632e-06 |
| 6×6×6 | 0.3333 | 36 | -2.9032e-17 | 0 | 6.9461e-06 |
| 6×6×6 | 0.5000 | 36 | -1.0261e-16 | 0 | 8.3448e-06 |
| 6×6×6 | 0.6667 | 36 | +7.9907e-17 | 0 | 5.3141e-06 |
| 6×6×6 | 0.8333 | 36 | +2.3688e-17 | 0 | 6.6770e-06 |

例如，4³ 网格的 k₃=0.25 面有 16 个小格；将它们的相位相加再除以 2π，得到 C_raw=−6.2230×10⁻¹⁷。程序检查这个和到最近整数的距离小于 1e-10，才写出 <code>chern_integer=0</code>。逐小格 CSV 保存每个相位，<code>slices.csv</code> 保存每个面的和；两种表分别回答局部回路和整个周期面的计算结果。

最小奇异值用于判断相邻占据子空间的重叠是否接近奇异；行列式过小时不能直接归一化。正反向重叠残差检查 M(j,i,−G)=M(i,j,G)†。本例的检查结果如下：

| 检查 | 4³ | 6³ | 源码采用条件 |
| --- | ---: | ---: | --- |
| 最小奇异值 | 0.666897 | 0.732745 | 大于 1e-8 |
| 最大奇异值 | 0.998431 | 0.999356 | 小于 1.001 |
| 最小行列式模长 | 0.576845 | 0.670831 | 大于 1e-12 |
| 正反向重叠最大残差 | 1.00e-12 | 1.00e-12 | 小于 1e-9 |
| 最大随机换基相位差 / rad | 1.33e-15 | 1.33e-15 | 小于 1e-12 |
| 独立极分解回路相位差 / rad | 1.68e-15 | 1.59e-15 | 小于 1e-12 |
| 最大切片和绝对值 | 6.22e-17 | 1.03e-16 | 到最近整数的距离小于 1e-10 |

源码还检查倒格对偶残差小于 1e-6、链接单位模残差小于 1e-14，以及随机换基的幺正误差和陈数变化小于 1e-12。每套网格做 12 次随机 U(4) 换基，随机种子写在 <code>kN-gauge-check.csv</code>。最大真实小格相位为 9.87×10⁻⁶ rad，远离主值分支端点 ±π。

<code>verify.py</code> 重新解析 MMN，并对各重叠矩阵作 SVD 极分解，取幺正部分构造矩阵回路，再比较其行列式相位。它读取主分析输出的方向链接表，因此独立核对的是回路计算，周期链接识别仍由主分析器完成。

## 把矩阵处理逻辑写成程序

程序需要把坐标、邻接关系与矩阵点序先对齐，再计算链接和回路，最后检查规范不变性及切片整数。下面的提示词可交给 AI 编写这套后处理；文件名、子空间和数值条件均对应当前 Si 数据。更换网格、占据子空间或自旋设置时，先改输入条件，再改索引与检查。

~~~text
编写 Python 3 / NumPy 程序，重现本包中 QE 7.5 Si 占据态重叠矩阵的 FHS 后处理。

输入固定为 source/k4/ 与 source/k6/，N=4、6，各有四条占据空间带、八个电子，非磁标量无 SOC。
读取 silicon.win 的 kpoints 块与点序；从 silicon.nnkp 读取点、邻接头、整数 G、实/倒格基矢并核对；从 silicon.mmn 读全部 4×4 复矩阵，第一带索引变化最快，以列优先顺序重排。
读取 nscf.data-file-schema.xml 核对 nbnd、nks、nelec、占据及自旋设置；检查 si.scf、si.nscf、pw2wan 的 .out/.err：一次 JOB DONE.、无源码所列失败告警且 stderr 为空。silicon.eig 不参与本程序计算。

由 N*(k[j]+G-k[i]) 选择 +e1/+e2，保留跨界 G，检查完整周期链接和正反向共轭关系。
使用 det(M)/abs(det(M))，按 +e1,+e2,-e1,-e2 的顺序取主值回路相位。固定分数 k3，C_raw=sum(phi)/(2*pi)；核对到最近整数的距离后报告整数。
检查奇异值、行列式模长、倒格对偶、单位模和规范不变性，阈值与 analyse.py 一致。采用其中记录的 12 个随机种子，输出每次 U(4) 换基残差。输入或数值条件失败时终止，不继续输出有效陈数。

输出 results/kN-links.csv、kN-gauge-check.csv、kN-plaquettes.csv、slices.csv、summary.json、source-sha256.json。逐小格表含索引、分数坐标、phase_rad 和 phase_per_area_A2；面积字段 plaquette_area_invA2 放在切片表和摘要。阈值见源码，随机种子放在 gauge CSV，输入文件哈希单独存 JSON。
另写 verify.py：读取上述结果及原生 MMN，用 SVD 极分解矩阵回路比较相位；核对输入哈希，并构造已知 C=+1 的周期合成链接场检查方向。输出 independent-check.json。
提供完整源码、依赖和终端命令；只处理已保存数据，逐切片表直接呈现结果。
~~~

## 源码与结果

| 文件 | 下载及用途 |
| --- | --- |
| 主分析器 | [analyse.py](/Atlas/examples/topo_berry_si/analyse.py) |
| 极分解回路与合成场核对 | [verify.py](/Atlas/examples/topo_berry_si/verify.py) |
| 十个切片的原始和、整数及小格面积 | [slices.csv](/Atlas/examples/topo_berry_si/slices.csv) |
| 逐小格相位 | [4³ CSV](/Atlas/examples/topo_berry_si/k4-plaquettes.csv) · [6³ CSV](/Atlas/examples/topo_berry_si/k6-plaquettes.csv) |
| 数值条件与逐切片摘要 | [summary.json](/Atlas/examples/topo_berry_si/summary.json) |
| 独立核对结果 | [independent-check.json](/Atlas/examples/topo_berry_si/independent-check.json) |

<details>
<summary>analyse.py 的完整源码</summary>

```python
"""FHS determinant links from native QE/Wannier90 overlaps; NumPy only."""
from pathlib import Path
import csv
import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)

def block(text, name):
    return re.search(r"begin\s+"+name+r"\s*\n(.*?)end\s+"+name,
                     text, re.S | re.I).group(1).strip().splitlines()

def write_csv(name, rows):
    with (OUT / name).open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def read_case(n):
    directory = ROOT / "source" / f"k{n}"
    win = (directory / "silicon.win").read_text()
    points = np.array([list(map(float, line.split())) for line in block(win, "kpoints")])
    indices = np.rint(points * n).astype(int)
    assert np.max(np.abs(points * n - indices)) < 1e-8
    assert len(set(map(tuple, indices))) == n**3
    lookup = {tuple(v): i for i, v in enumerate(indices)}
    nnkp = (directory / "silicon.nnkp").read_text()
    nn_points = block(nnkp, "kpoints")
    assert int(nn_points[0]) == len(points)
    assert np.allclose(points, np.array([list(map(float, x.split())) for x in nn_points[1:]]), atol=1e-8, rtol=0)
    bvecs = np.array([list(map(float, line.split())) for line in block(nnkp, "recip_lattice")])
    real = np.array([list(map(float, line.split())) for line in block(nnkp, "real_lattice")])
    reciprocal_error = float(np.max(np.abs(real @ bvecs.T - 2*np.pi*np.eye(3))))
    assert reciprocal_error < 1e-6
    nn_lines = block(nnkp, "nnkpts")
    nnb = int(nn_lines[0])
    declared = {tuple(map(int, line.split())) for line in nn_lines[1:]}
    with (directory / "silicon.mmn").open() as stream:
        stream.readline()
        nb, nk, nn = map(int, stream.readline().split())
        assert (nb, nk, nn) == (4, n**3, nnb)
        matrices = {}
        for _ in range(nk*nn):
            header = tuple(map(int, stream.readline().split()))
            assert len(header) == 5 and header not in matrices
            values = [complex(*map(float, stream.readline().split())) for _ in range(nb*nb)]
            matrices[header] = np.array(values).reshape((nb, nb), order="F")
        assert not stream.read().strip()
    assert set(matrices) == declared
    tree = ET.parse(directory / "nscf.data-file-schema.xml").getroot()
    vals = lambda tag: [e.text.strip() for e in tree.iter() if e.tag.split('}')[-1] == tag]
    assert set(vals("nbnd")) == {"4"} and set(vals("nks")) == {str(n**3)}
    assert all(float(x) == 8 for x in vals("nelec"))
    for tag in ["lsda", "noncolin", "spinorbit"]:
        assert set(vals(tag)) == {"false"}
    occ = [e for e in vals("occupations") if e != "fixed"]
    assert len(occ) == n**3 and all(np.array_equal(np.fromstring(x, sep=" "), np.ones(4)) for x in occ)
    for stem in ["si.scf", "si.nscf", "pw2wan"]:
        text = (directory / (stem+".out")).read_text()
        assert text.count("JOB DONE.") == 1
        assert not re.search(r"Error in routine|convergence NOT|eigenvalues not converged|MPI_ABORT", text)
        assert (directory / (stem+".err")).stat().st_size == 0
    selected = {}
    reverse_error = 0.0
    for header, matrix in matrices.items():
        i, j, *g = header
        reverse = (j, i, *[-v for v in g])
        assert reverse in matrices
        reverse_error = max(reverse_error, float(np.max(np.abs(matrix-matrices[reverse].conj().T))))
        delta = (points[j-1]+g-points[i-1])*n
        step = np.rint(delta).astype(int)
        assert np.max(np.abs(delta-step)) < 1e-8
        for axis in [0, 1]:
            unit = np.eye(3, dtype=int)[axis]
            if np.array_equal(step, unit):
                assert (i-1, axis) not in selected
                assert j-1 == lookup[tuple((indices[i-1]+unit) % n)]
                selected[i-1, axis] = (j-1, tuple(g), matrix)
    assert len(selected) == 2*n**3 and reverse_error < 1e-9
    return directory, points, indices, lookup, selected, bvecs, reciprocal_error, reverse_error

def links_and_flux(n, indices, lookup, selected, gauge=None):
    links = {}
    for (i, axis), (j, g, matrix) in selected.items():
        if gauge is not None:
            matrix = gauge[i].conj().T @ matrix @ gauge[j]
        determinant = np.linalg.det(matrix)
        assert abs(determinant) > 1e-12
        links[i, axis] = determinant / abs(determinant)
    flux = np.empty(n**3)
    for i, coord in enumerate(indices):
        i1 = lookup[tuple((coord + [1, 0, 0]) % n)]
        i2 = lookup[tuple((coord + [0, 1, 0]) % n)]
        flux[i] = np.angle(links[i,0]*links[i1,1]*np.conj(links[i2,0])*np.conj(links[i,1]))
    return links, flux

def run(n):
    start = time.perf_counter()
    directory, points, indices, lookup, selected, bvecs, reciprocal_error, reverse_error = read_case(n)
    area = float(np.linalg.norm(np.cross(bvecs[0], bvecs[1])) / n**2)
    rows = []
    for (i, axis), (j, g, matrix) in selected.items():
        sv = np.linalg.svd(matrix, compute_uv=False)
        rows.append(dict(grid=n,k_index=i+1,axis=axis+1,neighbor_index=j+1,G1=g[0],G2=g[1],G3=g[2],min_singular=float(sv[-1]),max_singular=float(sv[0]),abs_determinant=float(abs(np.linalg.det(matrix)))))
    minsv = min(x["min_singular"] for x in rows)
    maxsv = max(x["max_singular"] for x in rows)
    assert minsv > 1e-8 and maxsv < 1.001
    links, flux = links_and_flux(n, indices, lookup, selected)
    link_norm_error = max(abs(abs(v)-1) for v in links.values())
    assert link_norm_error < 1e-14
    gauge_rows = []
    for trial in range(12):
        seed = 2026092200 + 100*n + trial
        rng = np.random.default_rng(seed)
        gauge = []
        for _ in range(n**3):
            z = rng.normal(size=(4,4)) + 1j*rng.normal(size=(4,4))
            q, rr = np.linalg.qr(z)
            q = q @ np.diag(np.diag(rr)/np.abs(np.diag(rr)))
            gauge.append(q)
        gauge = np.array(gauge)
        norm_error = float(np.max(np.abs(gauge.conj().transpose(0,2,1)@gauge-np.eye(4))))
        _, changed = links_and_flux(n, indices, lookup, selected, gauge)
        flux_error = float(np.max(np.abs(np.angle(np.exp(1j*(changed-flux))))))
        chern_error = max(abs(np.sum(changed[indices[:,2]==s]-flux[indices[:,2]==s])/(2*np.pi)) for s in range(n))
        assert norm_error < 1e-12 and flux_error < 1e-12 and chern_error < 1e-12
        gauge_rows.append(dict(grid=n,trial=trial,seed=seed,unitary_error=norm_error,max_flux_difference_rad=flux_error,max_chern_difference=float(chern_error)))
    slice_rows=[]
    for s in range(n):
        f = flux[indices[:,2]==s]
        chern = float(np.sum(f)/(2*np.pi))
        integer = int(np.rint(chern))
        assert abs(chern-integer) < 1e-10
        slice_rows.append(dict(grid=n,k3_index=s,k3_fraction=s/n,plaquettes=n*n,chern_raw=chern,chern_integer=integer,max_abs_phase_rad=float(np.max(np.abs(f))),plaquette_area_invA2=area))
    write_csv(f"k{n}-links.csv", rows)
    write_csv(f"k{n}-gauge-check.csv", gauge_rows)
    write_csv(f"k{n}-plaquettes.csv", [dict(grid=n,k_index=i+1,k1_index=int(c[0]),k2_index=int(c[1]),k3_index=int(c[2]),k1_fraction=float(points[i,0]),k2_fraction=float(points[i,1]),k3_fraction=float(points[i,2]),phase_rad=float(flux[i]),phase_per_area_A2=float(flux[i]/area)) for i,c in enumerate(indices)])
    summary=dict(grid=n,occupied_bands=4,kpoints=n**3,mmn_neighbors=8,selected_links=len(selected),boundary_links=sum(any(x['G'+str(i)] for i in [1,2,3]) for x in rows),min_link_singular_value=minsv,max_link_singular_value=maxsv,min_abs_determinant=min(x['abs_determinant'] for x in rows),reciprocal_duality_error=reciprocal_error,reverse_link_max_error=reverse_error,normalized_link_norm_error=link_norm_error,max_abs_phase_rad=float(np.max(np.abs(flux))),branch_margin_rad=float(np.pi-np.max(np.abs(flux))),random_gauge_trials=12,max_gauge_flux_difference_rad=max(x['max_flux_difference_rad'] for x in gauge_rows),max_gauge_chern_difference=max(x['max_chern_difference'] for x in gauge_rows),slices=slice_rows,wall_seconds=time.perf_counter()-start)
    print(f"GRID {n}x{n}x{n}: {n**3} k points, 4 occupied bands, {len(selected)} directed links")
    print(f"  singular values: min={minsv:.12f} max={maxsv:.12f}; min|det M|={summary['min_abs_determinant']:.12f}")
    print(f"  reverse overlap residual={reverse_error:.3e}; max plaquette phase={summary['max_abs_phase_rad']:.6e} rad")
    print(f"  12 random U(4) gauges: max phase difference={summary['max_gauge_flux_difference_rad']:.3e} rad")
    for row in slice_rows:
        print(f"  k3={row['k3_fraction']:.9f}: C={row['chern_raw']:+.12e}, integer={row['chern_integer']}, max|phase|={row['max_abs_phase_rad']:.6e}")
    return summary, slice_rows

summaries=[]
slices=[]
for n in [4,6]:
    result, rows = run(n)
    summaries.append(result)
    slices.extend(rows)
write_csv("slices.csv", slices)
record=dict(method="Fukui-Hatsugai-Suzuki determinant links of four occupied native QE/pw2wannier90 bands",phase_convention="Arg(U1(k) U2(k+e1) conj(U1(k+e2)) conj(U2(k)))",surface="fixed fractional k3, oriented reciprocal b1,b2 torus",spin="nonmagnetic scalar calculation: one equivalent spin channel; four spatial bands, eight electrons",claim="Discrete slice Chern calculation and internal numerical checks only; no full-zone insulating-gap or Z2 validation",numpy_version=np.__version__,cases=summaries)
(OUT/"summary.json").write_text(json.dumps(record,indent=2)+"\n")
hashes={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'source').rglob('*')) if f.is_file()}
(OUT/'source-sha256.json').write_text(json.dumps(hashes,indent=2)+"\n")
print("POSTPROCESS_CHECKS_PASSED; full-zone gap and material topological classification not established.")
```

</details>

<details>
<summary>verify.py 的完整源码</summary>

```python
"""Independent polar-matrix loop check, plus a nonzero synthetic link test."""
from pathlib import Path
import csv, hashlib, json
import numpy as np
root=Path(__file__).resolve().parent
hashes=json.loads((root/'results/source-sha256.json').read_text())
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in hashes.items())
receipts=[]
for n in [4,6]:
    raw=(root/f'source/k{n}/silicon.mmn').read_text().splitlines()
    nb,nk,nn=map(int,raw[1].split())
    matrices={}
    for at in range(2,len(raw),nb*nb+1):
        header=tuple(map(int,raw[at].split()))
        z=np.array([complex(*map(float,line.split())) for line in raw[at+1:at+1+nb*nb]]).reshape(nb,nb,order='F')
        u,sv,vh=np.linalg.svd(z)
        matrices[header]=u@vh
    rows=list(csv.DictReader((root/f'results/k{n}-links.csv').open()))
    links={(int(x['k_index'])-1,int(x['axis'])-1):(int(x['neighbor_index'])-1,matrices[(int(x['k_index']),int(x['neighbor_index']),int(x['G1']),int(x['G2']),int(x['G3']))]) for x in rows}
    phases={}
    for k in range(nk):
        k1,m1=links[k,0];k2,m2=links[k,1]
        k12,m12=links[k1,1];k21,m21=links[k2,0]
        assert k12==k21
        phases[k]=float(np.angle(np.linalg.det(m1@m12@m21.conj().T@m2.conj().T)))
    saved=list(csv.DictReader((root/f'results/k{n}-plaquettes.csv').open()))
    error=max(abs(np.angle(np.exp(1j*(phases[int(x['k_index'])-1]-float(x['phase_rad']))))) for x in saved)
    assert error<1e-12
    receipts.append(dict(grid=n,independent_polar_loop_max_phase_error_rad=error,raw_mmn_sha256=hashlib.sha256((root/f'source/k{n}/silicon.mmn').read_bytes()).hexdigest()))
    print(f'k{n}: independent SVD polar-matrix loop phase difference = {error:.3e} rad')
# Periodic link field with a known +1 total flux; not a material calculation.
n=7
u1=np.array([[np.exp(-2j*np.pi*j/(n*n)) for j in range(n)] for i in range(n)])
u2=np.ones((n,n),complex)
for i in range(n):u2[i,-1]=np.exp(2j*np.pi*i/n)
phase=np.empty((n,n))
for i in range(n):
    for j in range(n):phase[i,j]=np.angle(u1[i,j]*u2[(i+1)%n,j]*np.conj(u1[i,(j+1)%n])*np.conj(u2[i,j]))
synthetic=float(phase.sum()/(2*np.pi))
assert abs(synthetic-1)<1e-12
print(f'Synthetic periodic link field: C = {synthetic:.12f} (expected +1; algebra check only)')
assert all(hashlib.sha256((root/n).read_bytes()).hexdigest()==h for n,h in hashes.items())
receipt=dict(source_files_unchanged=len(hashes),polar_loop_checks=receipts,synthetic_link_chern=synthetic,synthetic_scope='Algorithm orientation and periodic-boundary check, not a Si/QE result')
(root/'results/independent-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('INDEPENDENT_CHECKS_PASSED')
```

</details>

完整包还包含逐链接表、随机规范检查表、30 份输入文件的 <code>source-sha256.json</code> 和运行日志。<code>SHA256SUMS</code> 校验下载包内保存的文件；重新执行后处理会重写结果及日志，摘要中的运行时间也会变化，应在重跑前检查保存文件。

## 运行后处理，读取保存的核对输出

上面的完整包包含两套 QE 输入、输出和 XML、原生 Wannier90 文件及运行日志。先核对包内保存文件的哈希，再执行后处理；以下是对应命令：

~~~console
tar -xzf topo_berry_si_files.tar.gz
cd topo_berry_si
sha256sum --check SHA256SUMS
python3 -B analyse.py > analyse.out 2> analyse.err
python3 -B verify.py > verify.out 2> verify.err
cat verify.out
~~~

依赖是 Python 3 与 NumPy；保存结果使用 Python 3.12.3、NumPy 2.4.6，版本写在 <code>requirements.txt</code> 中。<code>analyse.py</code> 生成 <code>results/</code> 下的表和摘要，随后 <code>verify.py</code> 读取这些结果做独立回路核对。程序用 <code>assert</code> 检查输入及数值条件，运行时须保留断言，不能加 <code>-O</code> 或 <code>-OO</code>。输入不满足条件时程序终止，具体断言位置见 stderr；应先检查该位置对应的文件和条件。

保存的独立核对输出为：

~~~text
k4: independent SVD polar-matrix loop phase difference = 1.681e-15 rad
k6: independent SVD polar-matrix loop phase difference = 1.587e-15 rad
Synthetic periodic link field: C = 1.000000000000 (expected +1; algebra check only)
INDEPENDENT_CHECKS_PASSED
~~~

主分析的逐切片输出保存在 <code>analyse.out</code>，其中的 k₃、C 和 integer 对应前面的切片表。上面显示的是 <code>verify.out</code>：它比较两种回路实现，并用合成周期链接场的 C=+1 检查绕行方向与周期索引。

在解压后的同一目录中，也可以对照前文的矩阵文件头：

~~~console
head -n 7 source/k4/silicon.mmn
~~~

<span id="从矩阵回路到-wcc-和-z₂" class="legacy-anchor" aria-hidden="true"></span>
<span id="从矩阵回路到-wcc-和-z2" class="legacy-anchor" aria-hidden="true"></span>
## 从矩阵回路到 WCC 和 Z₂

前面每条链接取 `det(M)/abs(det(M))`，用于一个闭合二维面的总陈数。Z₂ 要研究自旋子占据子空间内本征相位的流动，取完行列式就丢失了这些单独的相位。可以先用同一份真实 Si 矩阵看看这个区别。

可以把重叠矩阵理解为“相邻两点占据态之间的连接”，而不是给每一条带贴一个局部 Berry 相位标签。若在两个点分别重选占据子空间的正交基，链接的左右两端都随之变换；沿周期回路连乘时，中间点的变换相消，闭合后的矩阵只在起点发生相似变换。因此单条链接的矩阵元依赖规范，回路的本征相位集合却不依赖这种换基。下文的随机 U(4) 检查正是在真实 MMN 上验证这件事：改变局域基底，不改变四个圆周相位。

取行列式保留本征相位的总和，适合前面的占据子空间总陈数；保留矩阵谱则能看到各混合电荷中心如何随横向动量演化。C=0 只规定闭合面的总通量，不要求每个 Wilson 回路都等于单位阵，也不要求所有中心为零。上表的 Si 相位与后面的 BHZ 谱流可以从同一回路操作获得，但它们的带空间与对称性不同：四条无 SOC 空间带不能因数目为偶数就被称为四条自旋子占据带。

下面沿 +b₁ 穿过整个倒空间周期。在每个固定 $(k_2,k_3)$ 上，把重叠矩阵作 SVD：$M=U\Sigma V^\dagger$，取幺正部分 $Q=UV^\dagger$，按点序构造 $W=Q_0Q_1\cdots Q_{n-1}$，最后一项包含跨边界的 G。对 W 的四个本征值取 $-\frac{\operatorname{Arg}(\lambda)}{2\pi}$ 并折回 $[0,1)$，得到本约定下四个无量纲混合 WCC。[Soluyanov–Vanderbilt 原文 Sec. II.2](https://doi.org/10.1103/PhysRevB.83.235401)的 SVD 平行输运解释了矩阵回路与一维局域电荷中心的关系；Sec. III 与 Fig. 1 再讨论横向演化及周期分支。

实际计算包括 4³ 网格上的 16 个矩阵回路和 6³ 上的 36 个回路。取 k₃=0 的两处读数如下；四个相位只在每个回路内部排序，列号没有跨 k₂ 的分支追踪含义。

| 网格 | 分数 k₂ | WCC₁ mod 1 | WCC₂ mod 1 | WCC₃ mod 1 | WCC₄ mod 1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 4³ | 0 | 0.375000126 | 0.874999416 | 0.875000620 | 0.875000992 |
| 4³ | 0.5 | 0.374999476 | 0.810104862 | 0.874999891 | 0.939894585 |
| 6³ | 0 | 0.374999955 | 0.874999426 | 0.875000151 | 0.875000309 |
| 6³ | 0.5 | 0.375000228 | 0.812206405 | 0.874999841 | 0.937793627 |

这四个相位不全相同，而相位和 modulo 1 接近周期端点。`0.9999998` 与 `0.0000001` 在这个圆周坐标上很接近，不能把跨过 0/1 的数值直接相减或按排序连成物理分支。矩阵回路保留了行列式总相位中看不见的内部结构。

[Soluyanov–Vanderbilt Fig. 1(a,b)](https://arxiv.org/pdf/1102.5600#page=4)（PDF 第 4 页）把同一 WCC 周期坐标画成左侧圆周和右侧展开的圆柱：纵坐标是模 1 的电荷中心，横坐标 t 从 0 到半个绝热泵浦周期。蓝、绿曲线表示两个中心，红菱形标出每个位置的最大间隙中心；a 示意奇数绕行及伙伴交换，b 示意偶数情形。b 中穿过 0/1 的分支在展开图上看似跳跃，正好说明为什么逐列排序再连线会产生错误。这里 t 表示参数演化，并非本页计算的实际时间。

本页 Si CSV 保存的是四条无 SOC 空间带的逐回路相位，因此画图时先用原始横向分数坐标与 WCC mod 1 作散点，保留 0/1 的圆周等价；没有完成分支追踪就不连成伙伴交换图。后面的 BHZ 自检才有两个占据自旋子带、半布里渊区和相应奇偶判定，可用同一种圆周读法检查其输出；原文的示意分类不赋给 Si。

完整源码：[wilson_loop.py](/Atlas/examples/soc-topology-si-wilson/wilson_loop.py)。[52 个回路的 CSV](/Atlas/examples/soc-topology-si-wilson/si-wilson-loops.csv)保存每个回路的四个相位及残差，[摘要](/Atlas/examples/soc-topology-si-wilson/si-wilson-summary.json)记录子空间与相位约定。程序只需 Python 3 和 NumPy；先解压前面的 `topo_berry_si_files.tar.gz`，将脚本放在解压目录旁，运行：

```bash
python3 wilson_loop.py --data topo_berry_si --output si-wilson-results
```

实际运行输出：

```text
4^3: 16 closed matrix loops; 4 links/loop; four spatial-band phases
  unitarity=3.109e-15; determinant phase=4.441e-16 rad; gauge spectrum=2.220e-16
6^3: 36 closed matrix loops; 6 links/loop; four spatial-band phases
  unitarity=6.439e-15; determinant phase=6.661e-16 rad; gauge spectrum=2.220e-16
WILSON_MATRIX_CHECKS_PASSED; no Z2 or material topology assigned
```

`unitarity` 检查 $W^\dagger W$ 与单位阵的差；`determinant phase` 比较矩阵乘积的行列式与逐链接行列式乘积；`gauge spectrum` 在各点随机 U(4) 换基后，以圆周距离匹配四个相位。它们检验回路代数。本例没有自旋子 Kramers 对，没有导带能隙验证，也没有执行横向相位连接或 Z₂ 奇偶判定。

### 将同一处理逻辑写成代码

```text
使用 Python 3 和 NumPy，从原包 source/k4、source/k6 的 win、nnkp、mmn 和 NSCF XML 读取数据。固定四条占据空间带、八个电子、无 SOC。逐项核对网格点序、矩阵头、占据及自旋设置；MMN 用列优先顺序读取。按 k[j]+G−k[i] 识别 +b1 链接，检查反向共轭和最小奇异值。
对每个固定 k2、k3，SVD 取幺正链接并按 +b1 顺序闭合相乘。四个本征值以 −Arg(λ)/(2π) modulo 1 输出，仅逐回路排序，不跨横向位置连接。保存原始分数坐标和各回路幺正残差；核对行列式相位及随机局域 U(4) 换基后的圆周本征相位谱。输出 CSV、JSON、运行记录和完整源码，不输出 Z2 或材料分类。
```

<details>
<summary>wilson_loop.py 的完整源码</summary>

```python
"""Matrix Wilson loops of the archived scalar Si occupied subspace; no Z2 inference."""
from pathlib import Path
import argparse, csv, itertools, json, re
import xml.etree.ElementTree as ET
import numpy as np

def block(text, name):
    found = re.search(r"begin\s+" + name + r"\s*\n(.*?)end\s+" + name, text, re.S | re.I)
    if found is None:
        raise ValueError("Missing block: " + name)
    return found.group(1).strip().splitlines()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def circle_error(a, b):
    return min(max(abs(((a[i]-b[j]+0.5) % 1)-0.5) for i,j in enumerate(p))
               for p in itertools.permutations(range(len(a))))

def load(data, n):
    folder = data / "source" / f"k{n}"
    points = np.array([list(map(float, x.split())) for x in block((folder/"silicon.win").read_text(), "kpoints")])
    index = np.rint(points*n).astype(int)
    require(points.shape == (n**3, 3) and np.max(abs(points*n-index)) < 1e-8, "Grid mismatch")
    lookup = {tuple(k):i for i,k in enumerate(index)}
    require(len(lookup) == n**3, "Duplicate grid points")
    nnkp = (folder/"silicon.nnkp").read_text()
    nnpoints = block(nnkp, "kpoints")
    require(int(nnpoints[0]) == n**3 and np.allclose(points, np.array([list(map(float,x.split())) for x in nnpoints[1:]]), atol=1e-8, rtol=0), "NNKP order mismatch")
    declared = {tuple(map(int,x.split())) for x in block(nnkp, "nnkpts")[1:]}
    xml = ET.parse(folder/"nscf.data-file-schema.xml").getroot()
    vals = lambda tag: [e.text.strip() for e in xml.iter() if e.tag.split("}")[-1] == tag]
    require(set(vals("nbnd")) == {"4"} and set(vals("nks")) == {str(n**3)}, "XML dimension mismatch")
    require(all(float(x)==8 for x in vals("nelec")), "Not the eight-electron Si case")
    for tag in ["lsda", "noncolin", "spinorbit"]:
        require(set(vals(tag)) == {"false"}, "Not the archived scalar case")
    occupied = [x for x in vals("occupations") if x != "fixed"]
    require(len(occupied)==n**3 and all(np.array_equal(np.fromstring(x, sep=" "), np.ones(4)) for x in occupied), "Occupation mismatch")
    matrices = {}
    with (folder/"silicon.mmn").open() as f:
        f.readline()
        nb,nk,nn = map(int,f.readline().split())
        require((nb,nk,nn)==(4,n**3,8), "MMN dimension mismatch")
        for _ in range(nk*nn):
            h=tuple(map(int,f.readline().split()))
            require(len(h)==5 and h not in matrices, "Duplicate or invalid MMN header")
            matrices[h]=np.array([complex(*map(float,f.readline().split())) for _ in range(nb*nb)]).reshape(nb,nb,order="F")
        require(not f.read().strip(), "Extra MMN records")
    require(set(matrices)==declared, "MMN/NNKP headers mismatch")
    links={}; minsv=1.; reverse=0.
    for h,m in matrices.items():
        i,j,*g=h; step=(points[j-1]+g-points[i-1])*n
        if np.allclose(step,[1,0,0],atol=1e-8,rtol=0):
            require(i-1 not in links and j-1==lookup[tuple((index[i-1]+[1,0,0]) % n)], "Bad periodic link")
            back=(j,i,*[-x for x in g]); require(back in matrices, "Missing reverse link")
            reverse=max(reverse,float(np.max(abs(m-matrices[back].conj().T))))
            u,s,vh=np.linalg.svd(m); minsv=min(minsv,float(s[-1]))
            links[i-1]=(j-1,u@vh)
    require(len(links)==n**3 and minsv>1e-8 and reverse<1e-9, "Singular or inconsistent links")
    return index, lookup, links, minsv, reverse

def run(data,n):
    index,lookup,links,minsv,reverse=load(data,n)
    rng=np.random.default_rng(2026100200+n)
    gauges=[]
    for _ in range(n**3):
        q,r=np.linalg.qr(rng.normal(size=(4,4))+1j*rng.normal(size=(4,4)))
        gauges.append(q)
    rows=[]; maxunit=0.; maxdet=0.; maxgauge=0.
    for k3 in range(n):
        for k2 in range(n):
            w=np.eye(4,dtype=complex); rotated=np.eye(4,dtype=complex); detprod=1.+0j
            for k1 in range(n):
                i=lookup[(k1,k2,k3)]; j,q=links[i]
                w=w@q; rotated=rotated@(gauges[i].conj().T@q@gauges[j]); detprod*=np.linalg.det(q)
            centres=np.sort((-np.angle(np.linalg.eigvals(w))/(2*np.pi)) % 1)
            changed=np.sort((-np.angle(np.linalg.eigvals(rotated))/(2*np.pi)) % 1)
            unit=float(np.max(abs(w.conj().T@w-np.eye(4))))
            deterror=float(abs(np.angle(np.linalg.det(w)/detprod)))
            gauge=circle_error(centres,changed)
            maxunit=max(maxunit,unit); maxdet=max(maxdet,deterror); maxgauge=max(maxgauge,gauge)
            rows.append(dict(grid=n,k2_fraction=k2/n,k3_fraction=k3/n,**{f"wcc{i+1}_mod1":float(x) for i,x in enumerate(centres)},sum_wcc_mod1=float(sum(centres)%1),unitarity_error=unit,det_phase_error_rad=deterror,gauge_spectrum_error_mod1=gauge))
    require(maxunit<1e-12 and maxdet<1e-12 and maxgauge<1e-12, "Wilson loop check failed")
    summary=dict(grid=n,loop_direction="+b1 including periodic G",loops=n*n,loop_points=n,spatial_bands=4,min_link_singular_value=minsv,reverse_overlap_error=reverse,max_unitarity_error=maxunit,max_determinant_phase_error_rad=maxdet,max_random_gauge_spectrum_error_mod1=maxgauge,random_seed=2026100200+n)
    print(f"{n}^3: {n*n} closed matrix loops; {n} links/loop; four spatial-band phases")
    print(f"  unitarity={maxunit:.3e}; determinant phase={maxdet:.3e} rad; gauge spectrum={maxgauge:.3e}")
    return rows,summary

if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--data",type=Path,required=True); parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    rows=[]; summaries=[]
    for n in [4,6]:
        r,s=run(args.data,n); rows.extend(r); summaries.append(s)
    with (args.output/"si-wilson-loops.csv").open("w") as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    record=dict(quantity="-Arg(eigenvalue of product of polar MMN links)/(2*pi), modulo one",subspace="Four occupied spatial bands of eight-electron nonmagnetic scalar Si, no SOC",connection="Closed +b1 loops at each sampled fractional k2,k3",interpretation="Matrix phase extraction only; no spinful Kramers partner tracking, Z2, edge spectrum or gap validation",numpy_version=np.__version__,cases=summaries)
    (args.output/"si-wilson-summary.json").write_text(json.dumps(record,indent=2)+"\n")
    print("WILSON_MATRIX_CHECKS_PASSED; no Z2 or material topology assigned")
```

</details>

### 用 BHZ 原例自检 WCC 与边界谱接口

在接入 DFT 的 SOC 自旋子 Wannier 模型前，可以先用已知的四带模型核对程序接口。[BHZ 原论文](https://doi.org/10.1126/science.1133734)式 (2)–(3) 将模型写成两个时间反演相关的块，并讨论量子自旋 Hall 边界态。这里实际运行的是 [WannierTools 官方 BHZ case1](https://github.com/quanshengwu/wannier_tools/tree/v2.7.2/examples/BHZ-model)：M=2、B=1、A=1、Δ₀=0，单位为模型 eV，四条自旋子带取两条占据带。它没有来自 HgTe 或本研究异质结的 DFT 拟合，输入中的 C、s、pz 是形式上的模型标签。[原件、输入和真实输出包](/Atlas/examples/soc-topology-bhz-check-files.tar.gz)保留原生成器与 `wt.in-normal`；本次使用无 Zeeman 的模型，没有采用磁场示例。

运行程序取源码 tag v2.6.2（日志内置版本标签仍为 2.6.1），GNU 构建只给未使用的 MKL 稀疏分支加显式保护，完整 [差异和构建命令](/Atlas/examples/soc-topology-bhz-check/README.txt)随包保存。所用 dense WCC 自适应积分与边界格林函数代码未改。输入让回路沿完整 b₁ 积分，横向扫描半个 b₂；边界保留 x 周期、沿 y 切开，同一 HR 不增加边界势。

<details>
<summary>完整的 wt.in、原模型生成器和读取核验源码</summary>

输入 `Nk1=Nk2=81` 如下；另一组只把这两个参数改成 41，两个实际输入都在下载包中。WCC 实际回路积分点数由内部自适应算法确定。

```text
&TB_FILE
 Hrfile = 'BHZ_hr.dat'
/
&CONTROL
 BulkBand_calc = T
 WannierCenter_calc = T
 SlabSS_calc = T
/
&SYSTEM
 SOC = 1
 NumOccupied = 2
 E_FERMI = 0.0
/
&PARAMETERS
 Np = 2
 Nk1 = 81
 Nk2 = 81
 Nk3 = 1
 OmegaMin = -2.5
 OmegaMax = 2.5
 OmegaNum = 401
/
LATTICE
Angstrom
3 0 0
0 3 0
0 0 10
ATOM_POSITIONS
1
Direct
C 0 0 0
PROJECTORS
2
C s pz
SURFACE
0 0 1
1 0 0
0 1 0
KPATH_SLAB
1
-X 0 -0.5 X 0 0.5
KPATH_BULK
2
X 0.5 0 0 G 0 0 0
G 0 0 0 Y 0 0.5 0
KPLANE_BULK
0 0 0
1 0 0
0 0.5 0
```

官方生成器原文：

```python
#!/bin/python3
import numpy as np
import cmath

# The Hamiltonian is 
#     ( M-Bk^2    Delta_0+A*k+  ) 
#     ( Delta_0+A*k_    -M+Bk^2 )
# where k^2=kx^2+ky^2

# Case I, QSHE with band inversion and no trivial hybridization
# Delta_0=0, M*B>0, |A|>0

# Case I, QSHE with band inversion and with trivial and nontrivial hybridization
# Delta_0=0.5, M*B>0, |A|>0


# from the kp to TB we use sustitution
# k->sin(k)
# k^2->2(1-cos(k))

# Constants
dp = np.float64
pi = np.arctan(1) * 4
zi = 1j

# Lattice constants
M = 2.0
B = 1.0
A = 1.0
Delta_0=  0.0
             

# Number of Wannier functions and R points
num_wann = 4
nrpts = 7

# R coordinates
Irvec = np.zeros((3, nrpts), dtype=int)

# Hamiltonian m,n are band indexes
HmnR = np.zeros((num_wann, num_wann, nrpts), dtype=complex)

# No of degeneracy of R point
ndegen = np.ones(nrpts, dtype=int)

# Initialization of matrices
Irvec[:, :] = 0
HmnR[:, :, :] = 0.0

# 0 0 0
ir = 0
Irvec[:, ir] = [0, 0, 0]
HmnR[0, 0, ir] = M - 4 * B
HmnR[1, 1, ir] = -M + 4 * B
HmnR[2, 2, ir] = M - 4 * B
HmnR[3, 3, ir] = -M + 4 * B
HmnR[0, 1, ir] = Delta_0
HmnR[1, 0, ir] = Delta_0
HmnR[2, 3, ir] = Delta_0
HmnR[3, 2, ir] = Delta_0

# 1 0
ir = 1
Irvec[:, ir] = [1, 0, 0]
HmnR[0, 0, ir] = B
HmnR[1, 1, ir] = -B
HmnR[2, 2, ir] = B
HmnR[3, 3, ir] = -B
HmnR[0, 1, ir] =-0.5*zi*A
HmnR[1, 0, ir] =-0.5*zi*A
HmnR[2, 3, ir] = 0.5*zi*A
HmnR[3, 2, ir] = 0.5*zi*A

# 0 1
ir = 2
Irvec[:, ir] = [0, 1, 0]
HmnR[0, 0, ir] = B
HmnR[1, 1, ir] = -B
HmnR[2, 2, ir] = B
HmnR[3, 3, ir] = -B
HmnR[0, 1, ir]=  -A/2
HmnR[1, 0, ir]=   A/2
HmnR[2, 3, ir]=  -A/2
HmnR[3, 2, ir]=   A/2


# -1 0
ir = 3
Irvec[:, ir] = [-1, 0, 0]
HmnR[0, 0, ir] = B
HmnR[1, 1, ir] = -B
HmnR[2, 2, ir] = B
HmnR[3, 3, ir] = -B
HmnR[0, 1, ir]= 0.5*zi*A
HmnR[1, 0, ir]= 0.5*zi*A
HmnR[2, 3, ir]=-0.5*zi*A
HmnR[3, 2, ir]=-0.5*zi*A


# 0 -1
ir = 4
Irvec[:, ir] = [0, -1, 0]
HmnR[0, 0, ir] = B
HmnR[1, 1, ir] = -B
HmnR[2, 2, ir] = B
HmnR[3, 3, ir] = -B
HmnR[0, 1, ir]=   A/2
HmnR[1, 0, ir]=  -A/2
HmnR[2, 3, ir]=   A/2
HmnR[3, 2, ir]=  -A/2

nrpts= ir+1
# Writing to a file
with open('BHZ_hr.dat', 'w') as file:
    file.write('4-band of BHZ model\n')
    file.write('4 !num_wann \n')
    file.write(f'{nrpts} ! nrpts\n')
    file.write(' '.join(f'{x:5d}' for x in ndegen) + '\n')
    for ir in range(nrpts):
        for i in range(4):
            for j in range(4):
                file.write(f"{Irvec[0, ir]:5d}{Irvec[1, ir]:5d}{Irvec[2, ir]:5d}{i+1:5d}{j+1:5d} {HmnR[i, j, ir].real:16.8f} {HmnR[i, j, ir].imag:16.8f}\n")
```

核验程序读 HR、WCC、左边界和体谱保存列，并读取日志中的自适应积分记录。它检查 Hermiticity、时间反演、反演和有限网格直接隙，再读占据 Kramers 对的四个 TRIM 宇称，按 [Fu–Kane 式 (1.1)–(1.2)](https://doi.org/10.1103/PhysRevB.76.045302)计算奇偶，与两个 WCC 判定比较。这个宇称核对依赖模型的反演对称性；不要求异质结也具有该对称性。

```python
#!/usr/bin/env python3
"""Read the official BHZ HR and WT outputs; NumPy only; no DFT."""
from pathlib import Path
import itertools, json, re
import numpy as np
root = Path(__file__).resolve().parent
lines = (root / "BHZ_hr.dat").read_text().splitlines()
nw, nr = int(lines[1].split()[0]), int(lines[2].split()[0])
assert (nw, nr) == (4, 5)
# Official generator prints seven unit degeneracies; WT reads five from this line.
deg = np.array([float(x) for x in lines[3].split()][:nr])
raw = np.array([[float(x) for x in s.split()] for s in lines[4:]])
assert raw.shape == (nr*nw*nw, 7) and np.all(deg == 1)
rvec, hr = [], []
for block in raw.reshape(nr, nw*nw, 7):
    assert np.all(block[:, :3] == block[0, :3])
    h = np.zeros((nw,nw), complex)
    for row in block:
        h[int(row[3])-1,int(row[4])-1] = row[5] + 1j*row[6]
    rvec.append(block[0,:3]); hr.append(h)
rvec, hr = np.array(rvec), np.array(hr)
def H(k):
    return np.einsum("r,rij->ij", np.exp(2j*np.pi*(rvec@k))/deg, hr)
T = np.block([[np.zeros((2,2)),np.eye(2)],[-np.eye(2),np.zeros((2,2))]])
P = np.diag([1,-1,1,-1])
gap, herm, tr, inv = float("inf"), 0.0, 0.0, 0.0
for x,y in itertools.product(np.linspace(0,1,101,endpoint=False), repeat=2):
    k = np.array([x,y,0]); h = H(k)
    herm = max(herm, float(np.max(abs(h-h.conj().T))))
    tr = max(tr, float(np.max(abs(T@h.conj()@T.conj().T-H(-k)))))
    inv = max(inv, float(np.max(abs(P@h@P-H(-k)))))
    e = np.linalg.eigvalsh(h); gap = min(gap, float(e[2]-e[1]))
assert herm < 1e-12 and tr < 1e-12 and inv < 1e-12 and gap > 0
parities = []
for k in [[0,0,0],[.5,0,0],[0,.5,0],[.5,.5,0]]:
    e,v = np.linalg.eigh(H(k)); occ = v[:,:2]
    p = np.linalg.eigvalsh(occ.conj().T@P@occ)
    assert np.max(abs(abs(p)-1)) < 1e-12 and abs(p[0]-p[1]) < 1e-12
    parities.append(int(round(p[0])))
z2_parity = int((1-np.prod(parities))//2)
checks = []
for n in [41,81]:
    run = root/f"n{n}-final"; out = (run/"WT.out").read_text()
    assert "ERROR" not in out+(run/"run.out").read_text()
    z2 = int(re.findall(r"Z2 for the plane you choose:\s*(\d+)", out)[-1])
    w = np.loadtxt(run/"wcc.dat")
    assert w.shape == (n,5) and np.isfinite(w).all()
    assert abs(w[0,0]) < 1e-8 and abs(w[-1,0]-.5) < 1e-8
    ends = [float(abs((a[3]-a[4]+.5)%1-.5)) for a in w[[0,-1]]]
    assert max(ends) < 1e-8 and z2 == z2_parity == 1
    l = np.loadtxt(run/"dos.dat_l"); bulk = np.loadtxt(run/"dos.dat_bulk")
    assert l.shape == (n*401,4) and bulk.shape == (n*401,3)
    assert np.isfinite(l).all() and np.isfinite(bulk).all()
    assert np.max(abs(l[:,:2]-bulk[:,:2])) < 1e-10
    # k is an accumulated path length. Middle record corresponds to kx=0.
    center = l.reshape(n,401,4)[n//2]
    j = int(np.argmin(abs(center[:,1])))
    log_l = float(center[j,2]); log_bulk = float(bulk.reshape(n,401,3)[n//2,j,2])
    records = re.findall(r"Wcc integration max_diff, Nk_adaptive\s+([-+0-9.Ee]+)\s+(\d+)", out)
    assert len(records) == n and set(int(x[1]) for x in records) == {64,128}
    counts = {str(k): sum(int(x[1]) == k for x in records) for k in [64,128]}
    tol = float(re.findall(r"wcc_calc_tol\s+([-+0-9.Ee]+)", out)[-1])
    neighbour = float(re.findall(r"wcc_neighbour_tol\s+([-+0-9.Ee]+)", out)[-1])
    max_change = max(float(x[0]) for x in records)
    assert max_change <= tol and tol == .08 and neighbour == .30
    checks.append(dict(mesh=n,input_Nk1=n,input_Nk2=n,
                       wcc_algorithm="dense adaptive integration; initial transverse Nk2 sampling",
                       loop_points_final_counts=counts,loop_max_recorded_change=max_change,
                       wcc_calc_tol=tol,wcc_neighbour_tol=neighbour,
                       z2=z2,wcc_rows=len(w),kramers_endpoint_circular_difference=ends,
                       near_zero_energy_eV=float(center[j,1]),ln_left_ldos=log_l,
                       ln_bulk_ldos=log_bulk,left_over_bulk_ldos=float(np.exp(log_l-log_bulk))))
summary = dict(scope="Official lattice BHZ software check, not a material DFT/Wannier result",
               parameters_model_eV=dict(M=2,B=1,A=1,Delta0=0),occupied_spinor_bands=2,
               full_grid_gap_min_eV=gap,gap_grid="101x101, not a material convergence test",
               hermiticity_max=herm,time_reversal_max=tr,inversion_max=inv,occupied_pair_TRIM_parities=parities,
               z2_inversion_parity=z2_parity,surface_eta_eV=15/401,
               weight_comparison_scope="exp(log-left minus log-bulk) only; projections have different trace dimensions, no equal absolute normalization",
               surface_columns="ln LDOS as written by surfstat.f90; no absolute DOS normalization inferred",
               runs=checks)
(root/"checks.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2))
```

</details>

解包后在 `soc-topology-bhz-check` 根目录执行；`WT` 填入按包内说明构建的可执行文件绝对路径。两套目录已经保存对应 HR。

```bash
WT=/absolute/path/to/wt262/bin/wt.x
(cd n41-final && OPENBLAS_NUM_THREADS=1 "$WT" > run.out)
(cd n81-final && OPENBLAS_NUM_THREADS=1 "$WT" > run.out)
python3 verify_bhz.py
gnuplot plot_bhz.gnu
```

两套实际 `WT.out` 均打印：

```text
Z2 for the plane you choose:            1
```

读回结果为：

| 核对量 | 实际结果 |
|---|---:|
| 输入 Nk1=Nk2=41 / 81 的 Z₂ | 1 / 1 |
| 占据 Kramers 对在 Γ、X、Y、M 的宇称 | −1、+1、+1、+1 |
| 101×101 模型采样的最小直接隙 | 2.000725445 eV |
| 时间反演 / 反演矩阵最大差 | 0 / 3.14×10⁻¹⁶ |
| 41 / 81 条 WCC 的两端配对圆周差 | 0 / 0 |

本版本 `WannierCenter_calc` 实际调用 `wannier_center3D_plane_adaptive`。横向以 Nk2 开始采样，本次没有追加横向点，最终为 41、81 行；每条回路从 32 点开始倍增，实际结束于 64 或 128 点。两次日志分别记录 39/79 条 64 点回路及各 2 条 128 点回路。默认 `wcc_calc_tol=0.08`、`wcc_neighbour_tol=0.30`，最大记录变化分别为 0.0503207641、0.0257763349。输入 Nk1=41/81 不能解释成固定回路链接数；当前相位与宇称相符用于接口自检，没有完成高精度积分容差的收敛研究。

最小隙是该模型有限采样的检查值。WCC 数值和反演宇称都给出同一个奇偶；这检查了所选占据子空间与接口。[完整 JSON](/Atlas/examples/soc-topology-bhz-check/checks.json)及[读取输出](/Atlas/examples/soc-topology-bhz-check/checks.out)保存具体误差。

可以在图前先认清 `wcc.dat` 的列。解压后，在同一包根目录读取 81 行结果的起点、中点和终点：

```bash
awk 'NR==1 || NR==2 || NR==42 || NR==82' n81-final/wcc.dat
```

保存文件的原文为：

```text
        #      k      largestgap  sum(wcc(:,ik))      wcc(i, ik)(i=1, NumberofSelectedOccupiedBands)
      0.00000000      0.00000000      0.00000000      0.50000000      0.50000000
      0.25000000      0.50000000      0.00000000      0.08947700      0.91052300
      0.50000000      0.50000000      0.00000000      0.00000000      0.00000000
```

第一列是横向分数坐标；两条 WCC 在 0 处同为 0.5，在 0.5 处同为 0，在中间分开。第三列的相位和已经模 1，三处均为零，但本模型判定为 Z₂=1，因此相位和不能替代单条 WCC 的谱流。第二列是两条中心之间最大间隙的中心，不是一条额外的占据带；程序通过横向演化计算奇偶，端点成对本身还不足以分类。换一套模型时先核对 `NumOccupied` 和实际列数，再读谱流，不把图中线条数量当作电子数。

![官方 BHZ 模型的 WCC 网格对照与半无限边界谱](/Atlas/examples/soc-topology-bhz-check/bhz-wcc-edge.png)

左图用散点叠加 Nk2=41、81 两套横向输出；图例标的是横向采样点数，回路内部均采用上述自适应积分。横向是分数 kᵧ，纵向是 WCC mod 1。两个端点成对，0 与 1 的圆周等价需要保持；本图没有人为连接逐点排序的分支。右图是同一模型半无限 y 边界的真实谱，横向为守恒的分数 kₓ。能隙内谱支在 kₓ=0 附近交叉并接向体带，因而与正常态 Z₂ 对应；[体谱原始输出](/Atlas/examples/soc-topology-bhz-check/n81-final/dos.dat_bulk)也保留在包中。

颜色读自此版本 `dos.dat_l` 第三列的 **自然对数 LDOS**，不是未经处理的 DOS；源代码在写文件前取 log。`SlabSS_calc` 实际展宽由能窗与能量点数确定，为 3×5/401=0.0374065 eV，图中保留这一值；最靠近零的能量点为 −0.006234414 eV。边界增强不能单靠亮线判读，还要结合体投影和同一模型的 WCC。

这张边界图的强度来自推迟格林函数：能量写成 $E+i\eta$，边界投影上的负虚部给出展宽后的谱权重。这里 η 约为 37.4 meV，会把理想谱线展成有宽度的亮带；颜色高不等于能隙更大。所用 [WannierTools v2.6.2 的 SlabSS_calc](https://github.com/quanshengwu/wannier_tools/blob/v2.6.2/src/surfstat.f90#L84-L239)先累加边界格林函数对角元的负虚部，再取自然对数，没有在这里除以 π。`dos.dat_bulk` 的体投影与边界投影还具有不同的迹空间，两个文件不能直接当成同一绝对归一化下的态密度相除。

复现现有图时保持同一能量窗、展宽和色标，先在体投影中定位能隙，再沿守恒 kₓ 看边界谱支如何接入两侧体带。更改终止方式可以改变边界色散或附加普通表面态；与同一体模型的 WCC 对照，才能区分贯穿能隙的连接和孤立的边界亮线。上述模型在 y 方向切开、x 方向周期，当前输入没有边界势，也没有表面电荷或结构的自洽重排；材料表面发生重构时要重新说明边界模型。

[Li 等 Fig. 4(a,b,d,e)](https://doi.org/10.1103/PhysRevB.108.125302)（原文 PDF 第 4 页）在同一异质双层模型中并列 WCC 与半无限边缘谱。a、d 的横轴 k₂ 从 0 到 π，是横向半个倒空间周期；纵轴 WCC(θ/2π) 从 0 到 1，表示相位模 1。b、e 的横轴为边缘守恒动量 X̄–Γ̄–X̄，纵轴为能量 / eV；正文说明边缘谱由 MLWF 哈密顿量经迭代半无限格林函数得到。两幅谱的能量窗口不同，原图也未给数值色条，不能从同样的红色直接比较两构型的谱权重。

对照的重点是 WCC 奇偶与谱支连接：非平庸构型的 b 中有贯穿 SOC 能隙、连接体价带和导带的边缘支；另一构型的 e 虽有能隙内亮线，却没有这种连接。本站 BHZ 图对应的是同一 HR 的 WCC 与 y 开放边界，横轴改用明确的分数 kᵧ、kₓ，并按实际 WT 输出标出自然对数 LDOS 和展宽。复现材料图时，应保存切边与终止方式，用同一 HR 叠查体投影、边界谱和 WCC；完整的 gnuplot 代码已经展示坐标映射与原始列读取。这个分析关系可用于材料验收，文献的构型分类不赋给本页 Si 或 BHZ 参数。

<details>
<summary>完整 gnuplot 源码</summary>

gnuplot 直接读取实际 WCC 与边界输出；把单段累计路径长度线性映射回输入的 kₓ=−0.5…0.5，保存物理坐标而不依赖原文件的长度单位表题。

本例 `KPATH_SLAB` 只有这一条直线段，第一列从零累计到 `pathmax`，所以代码中的 `$1/pathmax-0.5` 恢复了分数 kₓ；多段路径或曲线不能沿用这个全局缩放。WCC 使用第四、五列的模 1 相位作散点，不补造跨点分支；谱图则把第二列 eV 能量与第三列对数权重直接送入 gnuplot `pm3d`，保留实际采样点、展宽和固定色标。

```gnuplot
# Nk2 labels transverse outputs; dense loop integration is adaptive (64/128 final points).
# WT output columns and periodic path; no recomputation or smoothing.
set encoding utf8
set terminal pngcairo enhanced font "DejaVu Sans,12" size 1400,480
set output 'bhz-wcc-edge.png'
set multiplot layout 1,2 margins 0.08,0.88,0.14,0.91 spacing 0.12
set title 'BHZ model | two occupied spinor bands'
set xlabel 'Transverse k_y (fractional)'
set ylabel 'WCC (mod 1)'
set xrange [0:0.5]
set yrange [0:1]
set xtics 0.1
set ytics 0.25
set key top right
plot 'n81-final/wcc.dat' using 1:4 with points pt 7 ps 0.45 lc rgb '#0072b2' title 'Nk2=81', \
 'n81-final/wcc.dat' using 1:5 with points pt 7 ps 0.45 lc rgb '#0072b2' notitle, \
 'n41-final/wcc.dat' using 1:4 with points pt 6 ps 0.7 lc rgb '#d55e00' title 'Nk2=41', \
 'n41-final/wcc.dat' using 1:5 with points pt 6 ps 0.7 lc rgb '#d55e00' notitle
set title 'Semi-infinite y boundary | eta = 0.0374 eV'
unset key
set xlabel 'Conserved k_x (fractional)'
set ylabel 'Energy (eV)'
set xrange [-0.5:0.5]
set yrange [-2.5:2.5]
set xtics 0.25
set ytics 1
set view map
set palette defined (-5 '#194eff', 0 'white', 5 '#d73027')
set cbrange [-5:5]
set cblabel 'ln LDOS (WT output)'
set pm3d map
stats 'n81-final/dos.dat_l' using 1 nooutput
pathmax = STATS_max
splot 'n81-final/dos.dat_l' using ($1/pathmax-0.5):2:3 with pm3d
unset multiplot
```

</details>

该自检说明“同一 HR → 占据子空间 WCC → 正常态 Z₂ → 同一切边谱”能够实际运行。进入材料计算时，仍须先完成下面的 SOC DFT/Wannier 模型验收；模型自检不能代替目标能区、能隙、自旋算符和结构的材料检查。

### 异质结的 Z₂ 与边界态如何接续

对于时间反演对称的二维 SOC 体系，先确认准备分类的占据子空间在整个区域上保持固定维数、与其他能带分离。费米能穿带时，不宜把随 k 改变的瞬时占据数直接放进绝缘体 Z₂ 程序。若存在可分离的低能带子空间，应明确它的定义、直接隙及实际费米占据，分别解释能带子空间拓扑与材料是否绝缘。

从 [经验证的 SOC Wannier 模型](/Atlas/m/wannier90/qe/#把模型扩展到-soc-自旋子与边界态)或原始自旋子重叠出发，沿一个完整倒格周期积分，在横向的半布里渊区追踪 WCC。时间反演端点的 Kramers 配对与途中跨越周期边界的连接需要保持一致；加密积分和横向网格，核对判定的奇偶是否稳定。Si 的 C=0 没有保存这样的配对信息，不能用 `C mod 2` 替代 Z₂。

[WannierTools 的 WCC 接口](https://wannier-tools.readthedocs.io/en/latest/features.html#wannier-charge-center-wilson-loop-calculation)中，`WannierCenter_calc` 指定矩阵回路，`KPLANE_BULK` 的第一向量定义完整周期、第二向量定义横向半周期。`NumOccupied` 是所选模型中占据带的数量，不能填入总电子数。`wcc.dat` 第一列为横向位置，第二列为最大 WCC 间隙的中心，第三列为相位和，第四列起为各条 WCC；相位和与单条谱流的用途不同。

正常态 Z₂、自旋锁定和超导配对各需要自己的输入。前两者分别接到占据子空间和 [费米面自旋投影](/Atlas/m/spin-texture/vasp/)；讨论拓扑超导则还需配对矩阵与 BdG 能隙及不变量。本页材料数据止于 Si 的离散陈数和矩阵回路相位；BHZ 配套只核对正常态拓扑程序接口。
