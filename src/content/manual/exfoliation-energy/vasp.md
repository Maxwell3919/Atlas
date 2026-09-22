参考：

- [VASP：OUTCAR 中记录的内容](https://vasp.at/wiki/OUTCAR)
- [VASP：展宽与能量的选择](https://vasp.at/wiki/Smearing_technique)
- [VASP：EDIFFG 与结构优化停止条件](https://vasp.at/wiki/EDIFFG)
- [Jung 等：剥离能的定义与参考态](https://arxiv.org/abs/1805.04527)

## 把最上面一层抬高，能量还会增加多少？

这份 HfI₂ 算例在一个晶胞里放了六个 I–Hf–I 层，共 18 个原子。保留下面五层，把最上面一层整体向上移动，每次增加 1 Å，分别做固定结构单点计算。这样得到的是一条**冻结原子构型的单层分离能曲线**。

横坐标记作顶层位移 Δd：`scf_eq` 是 Δd=0，`scf_d20` 是相对它上移 20 Å。Δd 不是实际层间隙。原记录中零点的相邻表面 I 原子间隙约为 3.57 Å，因此 Δd=20 Å 时，该间隙约为 23.57 Å。

本次不在每一个位移点重新弛豫内部坐标，也没有把分离层的面内晶格放松。曲线可以给出这一冻结几何协议下的分离能；要与充分弛豫、无限厚基底定义的剥离能比较，还需要检查这些参考条件。

### 先读清楚参考结构用了什么设置

`relax` 使用固定晶胞离子优化，`scf_eq` 和 `scf_d1` 到 `scf_d20` 读取对应结构做单点。原稿保存的有效参数中，有几个差异需要先看见：

| 设置 | relax | scf_eq 与位移序列 |
|---|---|---|
| 原子运动 | `IBRION=2`、`NSW=200`、`ISIF=2` | `IBRION=-1`，固定几何单点 |
| 截断能 | `ENCUT=520` eV | `ENCUT=400` eV |
| FFT 精度设置 | `PREC=Normal` | `PREC=Accurate` |
| 电子精度 | `EDIFF=1E-6` | `EDIFF=1E-6` |
| 离子停止条件 | `EDIFFG=-0.01` eV/Å | 不做离子优化 |
| 展宽 | `ISMEAR=0`、`SIGMA=0.05` eV | 相同 |
| 色散设置 | `IVDW=11` | 相同 |

本页收录的两份[优化参数记录](/Atlas/examples/hfi2-exfoliation/relax-parameters.record.txt)与[单点参数记录](/Atlas/examples/hfi2-exfoliation/scf-parameters.record.txt)保留了原有值。单点记录的 `SYSTEM=SnS2` 是沿用模板时留下的标题；应从 POSCAR 元素、个数与实际赝势识别 HfI₂，不能由这个标题改判材料。

优化与单点采用不同的 `ENCUT/PREC`，因此 `scf_eq` 在这里先作为**位移零点**使用。它的名字本身不保证它是 400 eV 单点协议下经过重新收敛的能量极小点；原记录也没有在这一页给出完整的结构优化接受证据。下面所有能量差都统一减去 `scf_eq` 的单点能量，不减去 `relax` 的最终能量。

### 位移要加在同一层的三个原子上

18 个原子中，被移动的是第 11、12、18 号原子，也就是顶层的两个 I 和一个 Hf。原子层内部的相对坐标不变，其余 15 个原子不动。

晶胞第三方向约为 `c=86.6518 Å`，且这里沿 z 移动，所以 Direct 坐标的改变量为：

```text
Δz_fractional = Δd / c
Δd = 1 Å 时，Δz_fractional ≈ 0.01154044
```

已有读取记录给出了顶层一个 I 原子的分数坐标变化：

```text
[hzw@localhost exf]$ for d in scf_eq scf_d1 scf_d10 scf_d20; do echo "== $d =="; sed -n '19p' $d/POSCAR; done
== scf_eq ==
  0.6666666670000012  0.3333333329999988  0.4915434728751257
== scf_d1 ==
  0.6666666670000012  0.3333333329999988  0.5030839150891475
== scf_d10 ==
  0.6666666670000012  0.3333333329999988  0.6069478950153439
== scf_d20 ==
  0.6666666670000012  0.3333333329999988  0.7223523171555620
```

把 z 分数坐标乘以 c，可以看见相对零点约为 1、10、20 Å 的移动。这个行号属于本例的 POSCAR 排列；换一种元素顺序或增加 `Selective dynamics` 行后，应按原子身份重新找到对应坐标。

手动准备少量检查点时，可以复制完整目录到新名称，再用 `vi POSCAR` 修改同一组三个原子的 z 坐标，保存后用 `cat POSCAR` 逐项核对。不能只改 Hf 而留下两个 I，也不能把原子的绝对 z 坐标直接设成 20 Å。完整晶胞、原子个数、原子次序和其他 15 个原子的坐标都应保留。

### 先核对计算协议，再比较总能量

原记录抽查了四个分离点的 INCAR，保留的比较结果是：

```text
[hzw@localhost exf]$ for n in 1 8 15 20; do diff scf_eq/INCAR scf_d$n/INCAR > /dev/null && echo "scf_d$n: INCAR identical"; done
scf_d1: INCAR identical
scf_d8: INCAR identical
scf_d15: INCAR identical
scf_d20: INCAR identical
```

这四个文件与零点逐字节相同。要接受整个 21 点序列，还应把其余点的 INCAR、KPOINTS、POTCAR 标识与原子位移一并核对，不能把四点抽查写成全系列都已逐项验证。

原有提交记录的开头还保存了这些历史任务号：

```text
[hzw@localhost exf]$ head -5 submitted_jobs.tsv
dir     jobid   dependency
scf_eq  16554   none
scf_d1  16555   none
scf_d2  16556   none
scf_d3  16557   none
```

任务号用于把目录与当时的调度器记录对应起来；它不能证明电子迭代已经收敛。这份曲线所需的产物主要是每个单点的 `OUTCAR`。`OSZICAR` 用于快速观察电子步；本输入的 `LCHARG=T` 还会写 CHGCAR，而 `LWAVE=F` 关闭 WAVECAR 写出。这些密度和波函数文件并不参与下面的能量相减。

读取一个单点时，可以依次看：

```bash
head -n 80 scf_eq/OUTCAR
tail -n 20 scf_eq/OSZICAR
grep "energy  without entropy" scf_eq/OUTCAR | tail -1
tail -n 40 scf_eq/OUTCAR
```

OUTCAR 开头记录实际参数和体系规模，中间保留电子迭代、能量和力等结果，末尾有运行统计。提取最后一个能量之前，应确认它属于最后完成的电子计算，电子步满足设定阈值，输出没有在错误后中断。仅仅能搜到一个能量数字，还不足以把这个点放入收敛曲线。

### 从最后一行能量开始算差值

零点保存的真实能量行为：

```text
[hzw@localhost exf]$ grep "energy  without entropy" scf_eq/OUTCAR | tail -1
  energy  without entropy=     -111.23310238  energy(sigma->0) =     -111.23310238
```

同一行包含两个能量定义。本表沿用原提取记录中的 `energy without entropy`，不是逐个目录选一个更合适的数。这里零点的两列碰巧相同，不能据此保证所有位移点都相同；若改用外推的 `energy(sigma->0)`，应对全部点统一重提取并检查 SIGMA 收敛。有限展宽的 `TOTEN` 自由能也不能与本表混着相减。

已公开的[数据记录](/Atlas/data/teaching-extracts.json)保存了下面 21 点。文件中还留有原提取记录的哈希；这使绘图数据可追溯，但没有代替各 OUTCAR 的完整收敛核验。

| 顶层位移 Δd（Å） | E（eV/cell） | E−E(0)（meV/cell） |
|---:|---:|---:|
| 0 | -111.23310238 | 0.00000 |
| 1 | -111.14522274 | 87.87964 |
| 2 | -111.07191478 | 161.18760 |
| 3 | -111.03283390 | 200.26848 |
| 4 | -111.01334680 | 219.75558 |
| 5 | -111.00295561 | 230.14677 |
| 6 | -110.99687336 | 236.22902 |
| 7 | -110.99307892 | 240.02346 |
| 8 | -110.99053976 | 242.56262 |
| 9 | -110.98879721 | 244.30517 |
| 10 | -110.98760066 | 245.50172 |
| 11 | -110.98662884 | 246.47354 |
| 12 | -110.98601295 | 247.08943 |
| 13 | -110.98548644 | 247.61594 |
| 14 | -110.98508993 | 248.01245 |
| 15 | -110.98481305 | 248.28933 |
| 16 | -110.98458118 | 248.52120 |
| 17 | -110.98441092 | 248.69146 |
| 18 | -110.98427886 | 248.82352 |
| 19 | -110.98420280 | 248.89958 |
| 20 | -110.98414608 | 248.95630 |

能量差统一按 `1000 × [E(Δd) − E(0)]` 转成 meV/cell。这里的 cell 始终指整个 18 原子晶胞，不是单个原子或单个化学式。

### 用同一份数据重新画出整条曲线

[exfoliation.csv](/Atlas/examples/hfi2-exfoliation/exfoliation.csv)只保留位移、原能量和相对零点的能量差三列。它由公开 JSON 中的 `exfoliation` 数组直接导出；[extract_exfoliation.py](/Atlas/examples/hfi2-exfoliation/extract_exfoliation.py)提供转换方法，未平滑或拟合原始点。

将公开 JSON 下载为 `teaching-extracts.json`，与提取脚本放在同一目录，运行：

```bash
python3 extract_exfoliation.py
head -n 5 exfoliation.csv
```

实际导出结果为：

```text
source_sha256 ca529527922c65cfd823df5615eaf8698933b378dc7e64008abaec6349bdca09
points 21
E20_minus_E0_eV_cell 0.24895630
E20_minus_E15_meV_cell 0.66697
E20_minus_E19_meV_cell 0.05672
```

绘图时，将 CSV 与 [plot_exfoliation.py](/Atlas/examples/hfi2-exfoliation/plot_exfoliation.py)放在同一目录，运行 `python3 plot_exfoliation.py`。这份独立脚本只需要 NumPy 和 Matplotlib。关键两步是取 CSV 的位移列作横轴、取相对能量列作纵轴，再将 Δd≥14 Å 的末段单独放大：

```python
x = data["displacement_A"]
y = data["delta_energy_meV_cell"]
axes[0].plot(x, y, "o-")
tail = x >= 14
axes[1].plot(x[tail], y[tail], "o-")
```

![HfI2 冻结构型单层分离曲线及末段放大](/Atlas/examples/hfi2-exfoliation/exfoliation-repro.svg)

左图从零开始画，容易觉得 10 Å 以后已经变成直线；右图缩小纵轴范围之后，还能看到缓慢上升。15→20 Å 的能量变化是 **0.66697 meV/cell**，最后一步 19→20 Å 仍增加 **0.05672 meV/cell**。是否把它作为平台，需要先确定研究所需的能量差精度，再检查更大的分离距离和周期镜像影响。

这个晶胞的 c 保持不变。顶层向上抬高时，它与下面五层的间隙增大，同时与上方周期镜像的间隙减小。因此不能只根据起始 c 很大就认定真空足够；检验时应在更大 c 下同时重算零点与分离点，比较相同定义的能量差。

### 除以什么面积，得到什么数？

Δd=20 Å 的记录给出：

```text
E(20) − E(0) = 0.24895630 eV/cell
```

本模型只从 slab 的一个面移走一个 I–Hf–I 层。用原记录的面内面积 `A≈12.518 Å²` 归一化，得到有限分离点的估计约 **19.89 meV/Å²**。这里计数的是剥离一层的能量，不因出现两个新表面就再机械地除以 2；若改成上下两面同时移走两层，计数方式需要随操作重新定义。

把同一个差值除以全胞 18 原子，会得到约 13.83 meV/atom；除以被移走层的 3 个原子，则约为 82.99 meV/atom。两者分母不同，不能用相同的“每原子剥离能”名称直接比较。文献比较应优先写清剥离几层、参考结构、层内是否弛豫，以及面积归一化的定义。

这 21 点已经支持一条可重画的冻结结构分离曲线。要将末端数值作为材料的剥离能，还要结合 slab 厚度、k 点、截断能、展宽、色散模型及有限真空的收敛检查；目录名 `bulk` 或 `scf_eq` 都不能替代对参考态的实际核对。

下一步：想理解同一界面为什么产生结合，可以接着看[差分电荷](/Atlas/m/delta-charge/vasp/)和[Bader](/Atlas/m/bader/vasp/)；这些页面若使用另一种材料，其数值不能直接移来解释本例 HfI₂。

```text
参考构型 → 固定晶胞、选定顶层三个原子
                        ↓
                 Δd = 0…20 Å 的单点
                        ↓
            OUTCAR 能量 → 同一定义相减 → CSV 与曲线
                        ↓
            末端、镜像与厚度检查 → 面积归一化
```
