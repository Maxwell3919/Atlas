本页用 QE 7.5 导出的金刚石 Si 占据态重叠矩阵，计算固定分数坐标 k₃ 的周期二维切片陈数。先读取完整 4×4×4 与 6×6×6 网格，再构造沿倒格方向 b₁、b₂ 的 FHS 回路。十个实际采样切片均得到离散整数 C=0。

准备这类文件的前置步骤见 [QE–Wannier90 接口](/Atlas/m/wannier90/qe/)。重叠矩阵格式见 [Wannier90 的后处理文件说明](https://wannier90.readthedocs.io/en/latest/user_guide/wannier90/postproc/)，接口参数见 [pw2wannier90.x 文档](https://www.quantum-espresso.org/Doc/INPUT_pw2wannier90.html)。

## 下载并运行占据态后处理

[下载完整示例包](/Atlas/examples/topo_berry_si_files.tar.gz)。包中含两套 QE 输入、输出和 XML，原生 Wannier90 文件，完整源码、结果表及运行日志。下载后在终端解压，先检查保存文件，再运行：

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

合成周期链接场的 C=+1 用来检查绕行方向与周期索引；Si 的结果来自下面的真实重叠矩阵。

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

查看 4³ 网格的矩阵文件开头：

~~~console
head -n 7 source/k4/silicon.mmn
~~~

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

这里的函数记号说明各链接所在的 k 点，完整索引实现见 <code>analyse.py</code>。<code>angle</code> 取弧度主值。绕行方向决定陈数符号；对每个固定 k₃ 的周期面，将 N×N 个小格相位相加。占据态在每个 k 点作任意 U(4) 换基时，闭合回路相位保持不变。这是 [Fukui–Hatsugai–Suzuki 离散陈数方法](https://doi.org/10.1143/JPSJ.74.1674) 在多占据带子空间中的行列式链接形式。

| 输出字段 | 单位及位置 |
| --- | --- |
| <code>phase_rad</code> | 弧度；逐 plaquette CSV |
| <code>phase_per_area_A2</code> | Å²；相位除以真实倒空间小格面积，逐 plaquette CSV |
| <code>plaquette_area_invA2</code> | Å⁻²；保存在 slices.csv 和 summary.json 的切片条目 |
| <code>chern_raw</code>、<code>chern_integer</code> | 无量纲；逐切片表 |
| 奇异值、行列式模长 | 无量纲；逐链接 CSV 和摘要 |

<code>phase_per_area_A2</code> 是有限小格的面积平均量。解释连续 Berry 曲率分布还需检查局部量随网格加密的变化；两个网格得到相同整数本身不证明局部曲率收敛。

## 十个实际采样切片

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

## 源码与结果

| 文件 | 下载及用途 |
| --- | --- |
| 主分析器 | [analyse.py](/Atlas/examples/topo_berry_si/analyse.py) |
| 极分解回路与合成场核对 | [verify.py](/Atlas/examples/topo_berry_si/verify.py) |
| 十个切片的原始和、整数及小格面积 | [slices.csv](/Atlas/examples/topo_berry_si/slices.csv) |
| 逐小格相位 | [4³ CSV](/Atlas/examples/topo_berry_si/k4-plaquettes.csv) · [6³ CSV](/Atlas/examples/topo_berry_si/k6-plaquettes.csv) |
| 数值条件与逐切片摘要 | [summary.json](/Atlas/examples/topo_berry_si/summary.json) |
| 独立核对结果 | [independent-check.json](/Atlas/examples/topo_berry_si/independent-check.json) |

完整包还包含逐链接表、随机规范检查表、30 份输入文件的 <code>source-sha256.json</code> 和运行日志。<code>SHA256SUMS</code> 校验下载包内保存的文件；重新执行后处理会重写结果及日志，摘要中的运行时间也会变化，应在重跑前检查保存文件。

## 编写同类后处理的提示词

以下是独立的代码生成任务说明。它描述本例当前输入和输出约定，适用于编写可对照现有脚本的程序；更换网格、占据子空间或自旋设置时，需要相应修改并核对输入条件。

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

## 从切片整数到材料解释

LaH₂ 的研究用 Fukui 方法计算二维六角布里渊区的 Berry 曲率，Fig. 4(a) 显示带符号 Ωz 分布，随后结合谷附近的曲率讨论反常谷霍尔响应。这说明局部几何量如何参与物理响应的分析。[Shi et al., J. Phys.: Condens. Matter 34, 475303 (2022)](https://doi.org/10.1088/1361-648X/ac96bb)。

TbCl 的研究在 Fig. 2(b) 比较 k_z=0、π 平面的 Wannier 电荷中心流，并在 Fig. 4 将含 SOC 能隙、反常霍尔电导及手性边缘谱联系起来。平面不变量、能隙和边界响应各回答材料解释中的一个问题。[Zhong et al., npj Comput. Mater. 11, 236 (2025)](https://doi.org/10.1038/s41524-025-01732-0)。

Si 示例把计算链的起点具体化：读取原生占据态重叠，识别周期链接，检验规范不变性，再列出实际切片整数。进一步研究材料时，应按目标物理量补齐能带与相应的响应计算。
