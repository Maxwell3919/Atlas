能带图给出电子的能量，却没有直接告诉我们占据态沿布里渊区变化时积累了怎样的几何相位。陈数把一个闭合二维周期面上的 Berry 曲率通量汇总成整数，用来刻画该面上占据子空间的整体拓扑性质；要理解非零陈数与霍尔响应的联系，还要结合相应体系的能隙和占据。这里先用金刚石 Si 建立可逐项核对的零整数算例：相邻 k 点的原生重叠矩阵经过周期闭合、回路求和之后，是否给出一致的切片陈数，并且不随占据态的换基改变？

本例读取 QE 7.5 导出的完整 4×4×4 与 6×6×6 网格，在固定分数坐标 k₃ 的平面内沿倒格方向 b₁、b₂ 构造 FHS 回路。十个实际采样切片均得到离散整数 C=0。下面的链接、跨界处理和规范检查共同说明这个整数怎样从文件中算出；这些 Si 数据回答的是周期切片的计算问题。

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

倒格基矢来自 .nnkp。程序核对 aᵢ·bⱼ=2πδᵢⱼ，实际最大残差为 2.15×10⁻⁷，并由 b₁、b₂ 求小格面积。

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

## 从切片整数到材料解释

局部曲率与全周期面的陈数回答不同的问题。[Shi et al. 对 LaH₂ 单层的研究](https://doi.org/10.1088/1361-648X/ac96bb)在 §3.4 的式 (16)、(17) 给出占据加权的 Ωz 及其 Kubo 表达式，Fig. 4(a) 显示两个谷附近符号相反的曲率峰，再通过式 (18) 的反常速度讨论掺空穴后的谷霍尔响应。论文采用磁性单层和 Wannier 函数得到曲率分布；本页的 Si 切片积分为零，并不要求每个小格相位都为零，也没有计算谷分辨输运。

[Zhong et al. 对 TbCl 的研究](https://doi.org/10.1038/s41524-025-01732-0)在 Fig. 2(b) 用 Wannier 电荷中心流得到体材料 k_z=0、π 两个平面的 C=−1，并在 Fig. 4 将单层的含 SOC 能隙、占据带曲率积分、量子化反常霍尔电导平台和手性边缘谱联系起来。这给出了把陈数用于材料判断的具体例子：整数需要与同一模型的能隙、占据及响应相互对应。论文研究铁磁 TbCl，采用 DFT+U 或 HSE06、SOC 和 Wannier 后处理；这里计算的是无 SOC、非磁 Si 的倒格分数坐标切片，模型、曲面和方法实现均有区别。

这里的 C=0 来自四条占据空间带在十个周期切片上的离散计算。它检验了这些数据的链接与回路处理，并不单独证明整个材料拓扑平庸，也没有给出 ℤ₂ 不变量。作材料判断前，应先确认目标占据子空间与其余能带分离，再针对所研究的不变量检查完整布里渊区和网格收敛。