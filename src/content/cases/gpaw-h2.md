# GPAW H₂：固定设置下的能量、优化与力一致性

H₂ 的势能梯度能否驱动优化？同一个 Cartesian 力分量能否与中心能量差分对应？这个小例使用 GPAW 26.7.0/PBE/PW 的真实本地原生输出回答这两个接口问题。先看安装与输入解释。计算已在本地执行并经过独立数值核验；网页候选仍待独立科学与读者复核。同一输入在 Preston 的固定设置结果也已独立接受，保存证据与资源边界另列如下。

## 固定模型与复现入口

模型为 6 Å 立方周期盒中的非自旋极化 H₂，PBE、PW 340 eV、2 bands、Γ 点、零电荷和零宽度占据。`symmetry='off'` 允许原子移动后不再满足初始点群；它关闭点群及时间反演 k 点约化，不表示物理时间反演破缺，Γ 权重仍为 1。基组/盒长/k 点、PAW 可迁移性及步长敏感性未检验。不能拿另一个 10 Å 教程的绝对能量作为本模型 oracle。

下载[完整精确输入](/Atlas/examples/gpaw-h2/inputs/h2.py)与[H 数据](/Atlas/examples/gpaw-h2/data/H.PBE.gz)，在新目录中按以下布局保存；输入哈希 `bbcf810022eea28f1102eba9a8a3cc2c85723d260fcc4404731023a232e657e1`，数据哈希 `e16130c5eb16325a4404f46be86182a4b0f468038ae5c8ab9ffc777a2993fd1d`。直接打开输入可见完整参数与判断，没有用压缩包索引替代正文。

```text
gpaw-h2/
  inputs/h2.py
  data/H.PBE.gz
```

在已经验证原生扩展、GPAW 26.7.0 与 ASE 3.29.0 的环境中，于 `gpaw-h2/` 执行下面完整 argv。它们是供读者重新计算的命令，本次网页编辑没有再运行科学计算。新结果写入 `rerun/`，不覆盖本页的保存结果；任何已有阶段输出目录会报错。

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python inputs/h2.py --stage smoke --setup-dir data --out rerun/smoke
python inputs/h2.py --stage relax --setup-dir data --out rerun/relax
python inputs/h2.py --stage forcecheck --setup-dir data --out rerun/forcecheck
```

IN 为输入、单一 H.PBE.gz 与已验证环境；OUT 每阶段为 `gpaw.txt`、`result.json`、运行时自生成的 `identity.json`，优化另有 `optimizer.log` 和 `trajectory.traj`。保留新运行的身份记录供自己核对，本页不打包作者的运行身份。若原生前提或 SCF 失败，就检查完整错误，不继续宣称成功。

## 九个 SCF 块与三帧优化结果

完整输出：[smoke 原生日志](/Atlas/examples/gpaw-h2/outputs/smoke/gpaw.txt)、[relax 原生日志](/Atlas/examples/gpaw-h2/outputs/relax/gpaw.txt)、[forcecheck 原生日志](/Atlas/examples/gpaw-h2/outputs/forcecheck/gpaw.txt)。仅执行者用户名、进程标识与机器绝对路径作了公共文本定位替换，版本、输入参数、坐标、SCF 表和科学输出保留。精确结果 JSON：[smoke](/Atlas/examples/gpaw-h2/outputs/smoke/result.json)、[relax](/Atlas/examples/gpaw-h2/outputs/relax/result.json)、[forcecheck](/Atlas/examples/gpaw-h2/outputs/forcecheck/result.json)。

实际有 1+5+3=9 个 SCF 块；迭代数依次为 smoke 11，relax 11/11/11/9/9，forcecheck 11/9/10。每块均满足输入的 energy/density/eigenstates 三标准，详细归一化定义见工具页。[SCF CSV](/Atlas/examples/gpaw-h2/scf-ledger.csv)与[阶段汇总 CSV](/Atlas/examples/gpaw-h2/stage-summary.csv)可对照原生日志；五个 relax SCF 包含线搜索试探，不是五个优化步。

smoke 从 0.74 Å 开始，保存总能 −6.659426568123643 eV、有限的能量与力，净力范数约 8.88×10⁻¹⁵ eV/Å，小于 10⁻⁵ 局部标准。这是实现检查，不是绝对总能量准确性接受。

优化从 0.90 Å 开始，用 BFGSLineSearch，`fmax=0.05 eV/Å`、最多 12 步。真实保存的轨迹为：

| 接受的优化步 | 键长 Å | 总能 eV | 最大原子力 eV/Å |
|---|---:|---:|---:|
| 0 | 0.9000000000 | −6.409789624898396 | 3.0765964196 |
| 1 | 0.7773255268 | −6.656849771955055 | 0.6449293169 |
| 2 | 0.7569389496 | −6.663821330295236 | 0.0254523801 |

![固定设置下三帧接受优化轨迹；左为相对末态能量，右为最大力及局部力阈值](/Atlas/examples/gpaw-h2/figures/h2-relax.png)

紧邻图的数据与文件：[图数据 CSV（完整精度）](/Atlas/examples/gpaw-h2/figures/h2-relax.csv) · [PNG](/Atlas/examples/gpaw-h2/figures/h2-relax.png) · [SVG](/Atlas/examples/gpaw-h2/figures/h2-relax.svg) · [优化日志](/Atlas/examples/gpaw-h2/outputs/relax/optimizer.log) · [三帧 ASE 轨迹](/Atlas/examples/gpaw-h2/outputs/relax/trajectory.traj)。图中折线只连接三个实际点，不是拟合。末键长 **0.75693895 Å**、最大力 **0.02545238 eV/Å** 达到本例局部停止标准；末能小于起始值，键长在 0.5–1.2 Å 的防异常区间内。这个范围不是实验精度标准，也没有证明材料或基组/盒长收敛。

## 同一几何的解析力与中心差分

参考键长 0.74 Å，原子 0 固定 (3,3,2.63) Å，原子 1 的 z 从 3.370 Å 分别移动 ±δ；δ=0.005 Å。保存数据见[三个能量 CSV](/Atlas/examples/gpaw-h2/force-energies.csv)与[力对比 CSV](/Atlas/examples/gpaw-h2/force-check-comparison.csv)。

| 几何 | 原子 1 的 z Å | 总能 eV |
|---|---:|---:|
| 参考 | 3.370 | −6.659426568123643 |
| +δ | 3.375 | −6.661754133223602 |
| −δ | 3.365 | −6.656194809498301 |

中心差分使用力的负梯度定义：

$$F_z^{FD}=-\frac{E(z+\delta)-E(z-\delta)}{2\delta}.$$

原生解析力为 **+0.554965936 eV/Å**，用保存精确能量得到差分力 **+0.555932373 eV/Å**，绝对差 **0.000966436 eV/Å**，低于此例 0.02 eV/Å 判断阈值。它检验同一个固定模型中的实现一致性；未证明 δ 足够小、SCF 误差可忽略或截断/盒长达到物理精度。不要把一次差分通过称为步长准确性。


## Preston：同输入验证与跨主机观察

Preston 作业 **932** 在已独立核验的原生 GPAW 26.7.0 / ASE 3.29.0 / LibXC 5.2.3 环境执行；请求 1 task、2 CPU、4G、10 分钟。三个阶段仍用上面的同一完整输入及 H 数据，参数、SCF 标准和接受阈值没有改变。这里不提供主机访问、SSH 或提交脚本。原资源记录中的 srun 客户端 RSS（smoke/relax 7396 KiB、forcecheck 7604 KiB）不是科学进程峰值；科学进程实际内存/CPU 使用及 cgroup 限制执行情况未知，请求资源也不是实耗。

三阶段共九个实际 SCF，迭代数仍为 11；11/11/11/9/9；11/9/10。优化有两次接受更新、三帧，不是九步。原标准分别达到 SCF 三阈值、smoke 净力 <10⁻⁵ eV/Å、末最大力 <0.05 eV/Å 与中心差分误差 ≤0.02 eV/Å。基组、盒长、步长和材料准确性的未验范围保持不变。

| 观察量 | Talos 保存值 | Preston 保存值 | Preston − Talos |
|---|---:|---:|---:|
| 优化末总能 eV | −6.663821330295236 | −6.6638213304200535 | −1.24817489677298×10⁻¹⁰ |
| 末键长 Å | 0.7569389495758476 | 0.7569389446946269 | −4.8812207609216784×10⁻⁹ |
| 末最大力 eV/Å | 0.02545238010997284 | 0.0254525825871726 | 2.024771997601038×10⁻⁷ |
| 差分力 eV/Å | 0.5559323725301546 | 0.5559323725646159 | 3.446132268436486×10⁻¹¹ |
| 力差分误差 eV/Å | 0.0009664363578032464 | 0.0009664363923405084 | 3.453726193924922×10⁻¹¹ |

完整[跨主机观察 CSV](/Atlas/examples/gpaw-h2/preston/talos-preston-observation.csv)保留更多量及精度。差异是已观察的浮点结果，不是逐位相同的 oracle，也不是新的容差或材料准确性证据。不同原生构建/数值库可能影响归约及线搜索，但这里没有做误差来源归因实验。

![Preston 固定设置下三帧接受优化轨迹；能量 eV、最大力 eV/Å 与局部 0.05 阈值](/Atlas/examples/gpaw-h2/preston/figures/h2-relax.png)

图旁数据：[Preston 图数据 CSV](/Atlas/examples/gpaw-h2/preston/figures/h2-relax.csv) · [原 PNG](/Atlas/examples/gpaw-h2/preston/figures/h2-relax.png) · [SVG](/Atlas/examples/gpaw-h2/preston/figures/h2-relax.svg)。保留实际三点和原图，不重画或拟合。完整原生日志：[smoke](/Atlas/examples/gpaw-h2/preston/outputs/smoke/gpaw.txt)、[relax](/Atlas/examples/gpaw-h2/preston/outputs/relax/gpaw.txt)、[forcecheck](/Atlas/examples/gpaw-h2/preston/outputs/forcecheck/gpaw.txt)；仅执行身份和私有路径作公开定位替换，所有科学数值行保留。

精确结果：[smoke JSON](/Atlas/examples/gpaw-h2/preston/outputs/smoke/result.json) · [relax JSON](/Atlas/examples/gpaw-h2/preston/outputs/relax/result.json) · [forcecheck JSON](/Atlas/examples/gpaw-h2/preston/outputs/forcecheck/result.json)；配套[优化日志](/Atlas/examples/gpaw-h2/preston/outputs/relax/optimizer.log)、[三帧轨迹](/Atlas/examples/gpaw-h2/preston/outputs/relax/trajectory.traj)、[SCF CSV](/Atlas/examples/gpaw-h2/preston/scf-ledger.csv)、[阶段 CSV](/Atlas/examples/gpaw-h2/preston/stage-summary.csv)、[差分能量 CSV](/Atlas/examples/gpaw-h2/preston/force-energies.csv)、[力对比 CSV](/Atlas/examples/gpaw-h2/preston/force-check-comparison.csv)与[保存数据后处理源](/Atlas/examples/gpaw-h2/preston/derive-artifacts.py)。后处理源不启动 DFT；它是原执行者的精确源，完整运行还需它引用的阶段日志文件，本页选定下载集不提供这些过程日志，不声称仅此下载集即可重跑全部后处理。计算输入和 H 数据复用上文共享文件，无重复副本。GPAW/数据 GPL3+、ASE LGPL2.1+ 许可及公开原件沿用工具页。

## 检查输出而非退出码

新复现应逐块核 SCF 表的三个收敛标记、`Converged`、实际参数、坐标与有限能量/力；优化另查最大力、接受步数和保存轨迹，差分另查 ±δ 几何和负梯度符号。达到局部标准与科学量收敛分开判断。本文未主张 atomization energy、实验键长、远程性能或材料结论。

公开原件：[GPAW 26.7.0 发行版](https://pypi.org/project/gpaw/26.7.0/)、[GPAW H₂ 优化教程](https://gpaw.readthedocs.io/tutorialsexercises/structureoptimization/optimization/optimization.html)、[同版本收敛实现](https://gitlab.com/gpaw/gpaw/-/blob/26.7.0/gpaw/convergence_criteria.py#L122)。安装、许可证与数据来源保留 GPL3+ GPAW/输入/数据及 LGPL2.1+ ASE 的范围。
