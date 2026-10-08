# 从静态电荷到模式耦合：H₂、Si 与 Al 的公开方法实例

成键或接触改变电子分布以后，哪些电子态参与散射，哪一种原子运动与它们耦合，最后又怎样进入频率谱？这些问题彼此相关，却需要不同的可观察量。差分密度给出固定几何下的空间重排，能带与投影描述所选电子态，DFPT 提供位移势响应及振动模式，电子–声子矩阵元才把电子态与运动联系起来。下面用 H₂ 学习静态密度的参考，用 Si 学习电子子空间的独立检查，再用 fcc Al 读取模式、谱与条件温度。这是跨材料的方法示范；H₂ 的密度和 Si 的插值结果不是 Al 的计算输入，也不构成界面临界温度预测。

## 键区出现积累，为什么还不能说发生了净转移

H₂ 存档把分子放在 10 Å 立方胞中，两颗 H 的 z 坐标为 4.63、5.37 Å。`h2-delta-charge/AB` 是完整分子，`A`、`B` 分别删除另一颗 H 而保留原位置；三份 `INCAR`、`POSCAR`、`KPOINTS` 与 VASP 5.4.4 原生 `OUTCAR` 保存了实际参考。它们采用相同的 400 eV 截断、Γ 点采样和 144³ 精细电荷网格，片段分别自旋极化。这样比较的是冻结几何的电子重排，没有把片段各自松弛的几何变化混进差分。

取三份 CHGCAR 的第一个总电子密度块，计算 $\Delta n=n_{AB}-n_A-n_B$。这里正值表示电子数密度积累，电荷密度变化的符号则是 $-e\Delta n$。[VASP 的 CHGCAR 格式说明](https://vasp.at/wiki/index.php/CHGCAR)给出全胞电子数的网格归一化；本例转换脚本和 `charge-vesta/h2/summary.json` 将原始网格值除以 1000 Å³ 胞体积，得到 e/Å³。自旋磁化块与 PAW augmentation 块没有作为这张标量图相减。

![H₂ 冻结原子参考的差分电子密度：金黄积累，蓝色耗尽](/Atlas/examples/charge-vesta/figures/h2_delta_3d_zoom.png)

金黄色键区达到 +0.03 e/Å³，轴两端的蓝色区域达到 −0.03 e/Å³。图来自既有 VESTA 场景，显示的是阈值边界；密度积分使用完整网格，不能把可见等值面的体积直接当作电子数。历史摘要中正区积分约 +0.257831 e，负区约 −0.257831 e，全胞差分积分约 $4.36\times10^{-10}$ e。明显的成键重排与几乎为零的全胞净差分可以同时成立；后者只检验这组参考的电子数守恒。要把电子归到某一侧，还须定义分区边界并检查边界敏感性，见[差分电荷的空间积分](/Atlas/m/delta-charge/vasp/)。

实际查看时，从[公开电荷包](/Atlas/examples/charge-vesta-files.tar.gz)解出 `h2/CHGCAR_DELTA` 与 `h2/h2-isosurfaces.vesta`，保持两者相对路径即可打开场景。重新构造差分还需另取[H₂ 的三份密度与输入输出](/Atlas/examples/h2-delta-charge-files.tar.gz)及同名目录的 `CHGCAR.gz`，交给 `scripts/build_delta_chgcar.py`。这一脚本需要 NumPy；这里引用历史差分与既有图，没有重新运行密度构造或 VASP。公开包不提供受许可证约束的 POTCAR，重新做电子计算还需要自己的授权赝势文件。

## 从空间密度转到可以插值的电子子空间

静态密度没有直接给出近费米电子的色散与散射末态。要在更多 k 点上读取这些态，可以构造 Wannier 电子模型，但应先问模型保留了哪些带。Si 的公开实例刻意只保留四条隔离价带：`silicon.win` 中 `num_bands=num_wann=4`，投影位于四个键中心，没有解缠导带。原生输出标明 QE 7.5 与 Wannier90 3.1.0；实际父链是同一 diamond Si 结构的 SCF、完整均匀 NSCF、`pw2wannier90` 接口，再由 `amn/mmn/eig` 完成局域化和能带插值。SCF 使用 10³ 网格，4³、6³ 是两套 NSCF/Wannier 训练网格，不是两套 SCF 网格。

打开[Si 公开包](/Atlas/examples/si-wannier-lesson-files.tar.gz)，先看 `k4/si.scf.in`、两套 `si.nscf.in` 和 `silicon.win`，再把 `silicon_band.dat` 与独立 `k4/validation/si.bands.in` 对应的原生能量比较。后处理 `analyse_wannier.py` 读取 XML、本征值、接口矩阵与 `wout`，核对坐标和文件维度后生成 `direct-bands.csv`、`validation-errors.csv`、两套 `bands.csv` 与 `summary.json`。它需要 NumPy，本例使用保存的分析表，没有重跑该脚本或 Wannier90。

![Si 四价带的直接 DFT 对照与有限路径误差](/Atlas/examples/si-wannier/figures/wannier-bands.png)

图的共同零点是直接 DFT 的 Γ 点价带最高能量，不是各条曲线各自平移到零。13 个路径样本含 12 个唯一 k 点，每点比较四条价带；4³ 模型最大绝对误差约 0.2141 eV，6³ 约 0.08324 eV，对应 RMSE 为 0.08272、0.02695 eV。图说明这组有限路径样本上 6³ 的最大误差与 RMSE 较小，并不说明每个点都改善。它没有导带、完整费米面或速度验证，也不能由局域化停止推断目标量收敛。

进入金属问题时，需重新选择覆盖近费米态的带、投影和解缠窗口。费米口袋几何还不等于近费米态权重：相同窄能窗内，法向色散较慢的区域可能容纳更多态，而实际 DOS 要在整个相应倒空间积分；物理速度还需要正确的倒格基与单位。相应的读法见[近费米态](/Atlas/m/fermi-surface/qe/)和[Wannier 插值](/Atlas/m/wannier90/qe/)。更密的细网格只是更密地采样已有插值函数，不能自动修复目标子空间的误差。

即使电子能量重建良好，`silicon_hr.dat` 仍只提供电子哈密顿量；模式耦合还要原子位移引起的势响应以及它在电子态之间的矩阵元。公开的 [EPW 矩阵元与 Wannier 插值定义](https://docs.epw-code.org/Theory.html#electron-phonon-matrix-elements)说明了这组额外输入及电子、声子两个实空间方向的局域性要求。下一段因此改读 Al 自己的 DFPT 父链，而不是把 Si 的 HR 接到 Al 的谱上。

## 一个 Al 模式怎样进入全局耦合

单原子 fcc Al 有三条声学分支。这里采用 QE 7.5 原生插值 EPC 路线：`al.dense.in` 的 32³ 致密 SCF 保存电子积分数据，`al.scf.in` 的 16³ 响应 SCF 为 `al.elph.in` 提供父态，`ph.x` 在 4³ q 网格的八个不可约点计算响应。它们使用同一结构、Al.pz-vbc.UPF 和 40/160 Ry 截断；致密数据与响应波函数承担不同任务。所选模式的频率、位移与耦合应从这条父链对应的 `al.dyn2`、`al.elph.out`、`elph_dir/elph.inp_lambda.2` 读取，不能把另一份 ASR 处理后的向量按相同分支号直接配过来。

第 2 个 q 的笛卡尔坐标约为 $(-0.1767767,0.1767767,-0.1767767)$，单位为 $2\pi/\mathrm{alat}$。在电子积分展宽 σ=0.020 Ry 下，两条低频模式均为 3.594799 THz，打印 λ 分别为 0.0599、0.0576；第三模为 7.165696 THz，γ=23.94 GHz、λ=0.1845。γ 包含矩阵元平方与双费米窗口中的电子权重，λ 还按频率平方和程序的单自旋 DOS 归一化。因此模式频率、线宽和 λ 回答的是不同问题，最大的线宽也不必对应最大的 λ。[本版 elphsum 源码](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/elphon.f90)明确给出这种关系和打印单位。

![Al 八个不可约 q 点在同一电子展宽下的逐模线宽和 λ](/Atlas/examples/al/figures/phonon-linewidth.png)

横轴是八个文件的顺序，不是连续声子色散路径。第 2 点的三模 λ 合为 0.3020，但它只是全局平均的一项。`lambda.in` 给出该 q 的星权重 8，八点权重总和为 64，因此此点贡献为 $0.3020\times8/64=0.03775$；第三模单独贡献 0.0230625。对其余 q 同样加权，才得到该档全局 λ。模式编号本身也不能标识跨网格运动；前两模的打印同频提示要检查简并子空间与位移约定，不能只追踪一根箭头，具体方法见[逐模线宽](/Atlas/m/phonon-linewidth/qe/)。

为核对单位，本次在检查副本中真实运行了公开标准库脚本 `linewidth_units.py`。它从保存的 `linewidth.csv` 复算第三模 λ=0.184512923，与原生四位小数相符，并对 210 条高于低频阈值的记录保留舍入容差。输入 CSV 是历史 `analyse_epc.py` 由原生输出提取的表，本次没有重新生成它。另 30 条 Γ 声学残差落在 elphsum 的 20 cm⁻¹ 阈值分支，程序直接将 λ 置零；这不证明物理零耦合，γ 仍可非零。σ 是电子积分展宽，也不是晶格温度。

## 谱的来源决定可以怎样读温度

逐模贡献与频率结合后才得到 $\alpha^2F$，而积分得到的 λ 与谱的频率分布共同影响条件温度。先看与上段同路线的[Al 双网格公开包](/Atlas/examples/supercon-al-tc-files.tar.gz)：`k32`、`k48` 保存各自的原生输入输出及八份 elph 记录。五份响应与后处理输入逐字相同，致密 SCF 输入只把 32³ 改为 48³。本次复制最小输入后实际运行 `rebuild_tc.py` 与 `compare_tc.py`，重建 QE 7.5 `lambda.x` 的 2000 点、0–14 THz 简单高斯谱和温度公式，并将结果与原生打印精度核对。[lambda.x 源码](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/lambda.f90)在温度公式中使用逐 q 加权 λ，谱积分 λ 则另作检查，不能擅自互换。

在 σ=0.020 Ry 的 32³ 分支，原生输出为 λqsum=0.374486、λspec=0.374547、ωlog=343.741 K，输入 μ*=0.10 时简式温度打印为 0.969 K。两分支十档 σ=0.005–0.050 Ry 的折线没有交点或重合区间，最小正温差约 0.009221798 K。这只是两份固定响应网格、q 网格及展宽协议的比较，没有认证 Al 的材料临界温度；重建多保留的位数来自保存的 elph 输入运算，也没有恢复 DFPT 未打印精度。

另一个[Al 原生 EPW 谱包](/Atlas/examples/al-epw-wannier-tc-files.tar.gz)演示怎样把已有谱交给各向同性 Eliashberg 方程。它使用 EPW 6.0，谱生成输入 `source/epw2.in` 的粗网格为 k12³/q4³，细网格为 k24³/q12³，电子展宽 0.10 eV、声子展宽 0.5 meV，`crystal` ASR 与 0.1 cm⁻¹ 声学阈值。它不是上段 λx 路线的同一张谱，两套结果不能混合解释为求解器之间的精度比较。

![Al 原生 EPW 谱、累计 λ 与固定模型的线性化本征值](/Atlas/examples/al-epw-wannier-tc/figures/al-native-spectrum-tc.png)

左图直接读取 `source/al.a2f` 的 500 个正频率样本，频率单位为 meV；第三列保存原生累计 λ，末值为 0.3508982，同输出另报的离散求和 λ=0.3507955 应分别保留。右图来自历史 `linear-coarse` 与 `linear-refine/epw.out`：固定 μ*=0.10、请求方程截断 0.10 eV 时，最大本征值在 0.84 K 为 1.0017989，在 0.85 K 为 0.9989208。这里的交叉与上一段的双网格曲线交点是不同定义；前者是固定各向同性模型的线性化本征值达到 1，后者是两条网格结果在相同展宽下相等。

本次只在副本中运行 `analyse_tc.py`，提取了 15 行历史线性解、上述交叉区间和一个低温非线性解。0.25 K 的首个 Matsubara 点 Δ=0.128213 meV，是虚轴自能参数，不能直接称为实轴激发能隙。`fila2f`、`nqstep=500` 与实际 `wscut` 记录说明求解器读了什么；[QE 7.5 随附 EPW 源码](https://github.com/QEF/q-e/blob/qe-7.5/EPW/src/supercond.f90)给出读谱与 Matsubara 截断约定。本次没有重求解方程，更没有以程序完成代替网格、展宽、子空间或截断收敛。

这些公开文本足够重新提取表格和重建指定 λx 运算。重做 H₂/Si 电子计算需要相应软件、赝势与新父态；重做 Al 响应或 EPW 插值还需要匹配的 SCF save、波函数、位移势响应及 Wannier 粗矩阵等大数据。本次最小检查副本不含这些状态，EPW 谱包也不能凭一份 `al.a2f` 重建其完整粗网格父计算。把每项证据保留在它实际回答的问题内，才能从电荷重排走到电子态、运动和谱，而不会把跨材料教学图误拼成一条已接受的科学预测。

## 在新目录核验保存的数据

下面的命令只做保存数据的后处理，不启动电子、声子或 Eliashberg 计算。Python 3 的标准库足够运行 Al 的四项操作；H₂ 密度构造、Si 分析和绘图需要其他依赖，本次未执行。先把上文五个下载包保存到同一目录。实际顶层目录分别是 `charge-vesta/`、`h2-delta-charge/`、`si-wannier/`、`supercon-al-tc/` 和 `al-epw-wannier-tc/`，不是下载文件去掉后缀得到的所有名字。先用 `tar -tzf 包名` 检查成员；本版这五个包没有绝对路径、`..` 路径分量或链接成员。

为保留下载原件与保存的参考结果，在下载目录执行以下命令。`mkdir` 故意不加 `-p`：若检查目录已经存在，应换一个新名字，避免覆盖前次输出。

```bash
mkdir saved-data-check
cd saved-data-check
tar -xzf ../charge-vesta-files.tar.gz
tar -xzf ../h2-delta-charge-files.tar.gz
tar -xzf ../si-wannier-lesson-files.tar.gz
tar -xzf ../supercon-al-tc-files.tar.gz
tar -xzf ../al-epw-wannier-tc-files.tar.gz
python3 supercon-al-tc/rebuild_tc.py supercon-al-tc/k32 supercon-al-tc/k48 --outdir new-supercon-results
python3 supercon-al-tc/compare_tc.py --a supercon-al-tc/k32 --b supercon-al-tc/k48 --out new-supercon-results
```

两个脚本从 `k32/`、`k48/` 各自的 `lambda.in`、`lambda.out` 和八份 `elph_dir/elph.inp_lambda.*` 重建运算，比较还读取 `lambda.dat`。输出写到新建的 `new-supercon-results/`，保留包内 `comparison-k32-k48/` 原参考。检查两份 `k32-rebuild-checks.json`、`k48-rebuild-checks.json` 的打印精度容差记录，并核对两份 `*-rebuilt.csv` 各十行、`paired-tc.csv` 十行以及 `crossings.json` 的无区间内交点/重合记录；`crossings.csv` 此时只有表头。

单位脚本读取自己所在目录的 `linewidth.csv`，没有输出目录参数。另建目录，从[公开 CSV](/Atlas/examples/al/epc-q4/linewidth.csv)与[公开单位脚本](/Atlas/examples/al/epc-q4/linewidth_units.py)保存副本；以下是它的完整调用，脚本没有额外参数：

```bash
mkdir new-linewidth
curl --fail --location https://maxwell3919.github.io/Atlas/examples/al/epc-q4/linewidth.csv --output new-linewidth/linewidth.csv
curl --fail --location https://maxwell3919.github.io/Atlas/examples/al/epc-q4/linewidth_units.py --output new-linewidth/linewidth_units.py
python3 new-linewidth/linewidth_units.py
```

输出 `new-linewidth/linewidth-unit-check.json` 应记录 240 行，其中 210 行参与公式与舍入容差比较、30 行属于 20 cm⁻¹ 低频分支；所选 q2 第三模的复算 λ 约为 0.184512923。这里核验的是历史 CSV 的单位关系，没有重新从 DFPT 输出生成 CSV。

EPW 提取脚本也按自身位置读写。只复制三个历史 solver 目录、谱与脚本到新目录，使包内原表保留：

```bash
mkdir new-epw
cp al-epw-wannier-tc/analyse_tc.py new-epw/
cp -R al-epw-wannier-tc/linear-coarse al-epw-wannier-tc/linear-refine al-epw-wannier-tc/nonlinear-T0.25 new-epw/
mkdir new-epw/source
cp al-epw-wannier-tc/source/al.a2f new-epw/source/
python3 new-epw/analyse_tc.py
```

输入为三个目录的 `epw.in/out/err`、低温目录的 `al.imag_iso_000.25` 和 `source/al.a2f`。输出中 `linear.csv` 应有 15 行、`gap.csv` 一行、`source-spectrum.csv` 500 行；`solver-status.json` 保留历史结束/错误/迭代标记，`tc-brackets.json` 保留固定模型的 0.84–0.85 K 区间。脚本的 `SHA256.json` 在后两项表写出前生成，不能当作完整最终输出清单。这些 CSV/JSON 可以逐字与包内同名参考文件比较；λx 输出可与 `comparison-k32-k48/` 对应文件比较。成功退出表示这些保存数据的运算或提取通过，仍不构成材料临界温度或联合收敛验收。

H₂ 包解开后，差分场与 VESTA 场景位于 `charge-vesta/h2/`。`h2-delta-charge-files.tar.gz` 只含三份输入输出与历史分析，不含大体积 CHGCAR；三个历史密度必须从公开的同名目录单独下载。若另行具备 NumPy，可在上述新目录使用下面的完整下载与历史构造接口；密度构造在本次集成中未运行，输入必须为同胞、同网格的完整总密度：

```bash
curl --fail --location https://maxwell3919.github.io/Atlas/examples/h2-delta-charge/AB/CHGCAR.gz --output h2-delta-charge/AB/CHGCAR.gz
curl --fail --location https://maxwell3919.github.io/Atlas/examples/h2-delta-charge/A/CHGCAR.gz --output h2-delta-charge/A/CHGCAR.gz
curl --fail --location https://maxwell3919.github.io/Atlas/examples/h2-delta-charge/B/CHGCAR.gz --output h2-delta-charge/B/CHGCAR.gz
mkdir new-h2
python3 charge-vesta/scripts/build_delta_chgcar.py --ab h2-delta-charge/AB/CHGCAR.gz --a h2-delta-charge/A/CHGCAR.gz --b h2-delta-charge/B/CHGCAR.gz --output new-h2/CHGCAR_DELTA --summary new-h2/summary.json
```

Si 解包目录是 `si-wannier/`，可查看 `k4/`、`k6/` 与 `k4/validation/` 的历史接口和独立 DFT 检查。这里只读保存的表与图，没有运行 `analyse_wannier.py`。完整分析还需脚本引用的 XML、接口文件和赝势身份输入；接口文本不等于完整 QE save 与波函数。Al 两分支和 EPW 谱包也省略了大体积 save、响应二进制或粗矩阵：上述命令闭合的是保存文本到检查表的路径，不能从这些包恢复完整科学父计算。
