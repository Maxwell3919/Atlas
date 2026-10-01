- [Nature：图件与导出要求](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)
- [Nature：面板排列、尺寸与配色](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)

画一张图之前，先决定它要解释什么。界面是否改变了费米能附近的电子态，要把孤立层和异质结放在相同的几何与能量参考下比较；某一段声子对耦合贡献大不大，要同时看频率、模式和累计 λ。数据之间的关系决定面板怎么排，字体和颜色随后再处理。

## 先从文献里看分析怎样展开

Qiu 等关于单层 Ba₂N 的研究中，Fig. 2 将能带、DOS、费米面和 ELF 放在一起；Fig. 3 接上声子色散、线宽、投影声子态密度和 α²F；Fig. 4 比较应变下的近费米态，Fig. 6 再看声子与耦合怎样变化。这几组图提供了一条具体的分析路线：先辨认参与低能过程的电子态，再寻找与它们耦合的振动。[原文与图件](https://doi.org/10.1103/PhysRevB.105.165101)

<figure class="research-figure"><img src="/Atlas/figures/literature/M6_FatPhonon_Linewidth_Ba2N_Qiu2022_Fig3a.jpg" alt="Qiu 等 Ba₂N 论文 Fig. 3(a) 的声子色散与模式线宽" loading="lazy" /><figcaption>Qiu 等，Phys. Rev. B 105, 165101 (2022)，Fig. 3(a) 摘图。红色色带的宽度编码模式电声线宽，黑线给出频率。沿同一声子支追踪宽度，再与原文同图的 PHDOS 和 α²F 比较，可以找到值得检查的频率区间。<a href="https://doi.org/10.1103/PhysRevB.105.165101">论文来源</a>。</figcaption></figure>

线宽大和对总 λ 的贡献大，需要分别核对。λ 含频率权重与布里渊区积分；α²F 的一个峰也可能来自多个 q 点和模式。逐模文件的编号必须先与实际波矢、本征频率配对，再去读位移方向。具体文件格式与提取见[声子线宽](/Atlas/m/phonon-linewidth/qe/)和[谱函数](/Atlas/m/eliashberg-a2f/qe/)。

## 电子态的图先统一参考

能带与 DOS 来自两类采样。高对称路径展示色散和轨道来源，均匀网格对整个布里渊区积分。路径上某一支较平，只能提示相关能区；要解释 DOS 峰，还需检查它在其他 k 点的分布。界面前后对照时，先列出结构、晶胞、赝势、SOC 与电子数，再决定零点取各自 EF、共同真空参考还是电势参考。

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-electronic.png" alt="ZrCl₂/Sc₂C 保存记录的投影能带、PDOS 与二维费米等能轮廓" loading="lazy" /><figcaption>ZrCl₂/Sc₂C 的一组历史电子结构图。路径胖带与 PDOS 使用保存的 0.3133 eV 参考，BXSF 使用自身的 0.3154 eV；数值配对时要保留各文件的零点。页面中的原始表与源码分别见<a href="/Atlas/m/fatband/qe/">投影能带</a>、<a href="/Atlas/m/dos/qe/">DOS</a>和<a href="/Atlas/m/fermi-surface/qe/">费米面</a>。</figcaption></figure>

图中相同颜色应一直表示相同元素、层或轨道。PDOS 的轴标要给出 states/eV/cell 或其他实际归一化；按原子求和时写清原子集合。选能窗积分得到的是该投影内的谱重，它与 Bader 电荷、差分密度积分属于不同定义。若要辨认间隙电子，还要看对应能带或能窗的实空间密度，不能只凭一个原子 PDOS 峰作判断。[Ba₂N 的能窗密度对照，Fig. 4](https://doi.org/10.1103/PhysRevB.105.165101)

## 空间分布保留坐标、单位和阈值

VESTA 的等值面适合看三维位置，切片适合看层间连通与密度分布；平面平均及累计积分用于定量比较。先给出晶轴、法向、原子层的位置，再写等值面的数值与单位。ELF 是无量纲量；电子密度和差分密度要保留各自单位。两个结构作对照时，视向、阈值和色标范围应一致。

正负差分密度可以用以零为中心的发散色标，ELF 可用顺序色标。坐标、切面和连续色标缺少时，图仍可展示空间轮廓，但数值判断要回到完整网格。差分密度的参照应为同晶胞、同网格、同冻结几何的孤立层；累计积分前写出符号约定、面积和电子数归一化。操作与源码见[差分电荷](/Atlas/m/delta-charge/vasp/)、[ELF](/Atlas/m/elf/vasp/)和[平面平均电势](/Atlas/m/electrostatic-potential/vasp/)。

Ca₂N 的电化合物研究把层间实空间电子分布与电子结构联系起来。读它的 Fig. 3 时，要同时辨认离子层和间隙区域；这套分析可用于设计自己的密度图，但材料是否具有相同电子态还需检查本模型。[Ca₂N 原文](https://doi.org/10.1038/nature11812)

## Tc 曲线保留产生它的完整设置

两条 Tc(σ) 曲线只在相同电子展宽下比较。每条曲线应来自独立完整的 pwxall → pwx → ph.x → q2r.x → matdyn.x → lambda.x 链，记录致密 k 网格、主 k 网格、q 网格、积分范围、μ* 与使用的公式。读到交点后，再查看相同展宽下的 λ、ωlog 和网格差值。

![两条实际 Al 网格分支的 Tc 与逐点差值](/Atlas/examples/supercon-al-tc/figures/supercon-al-k32-k48-tc-delta.png)

这组 Al 的 32³ 与 48³ 曲线在实际采样范围内没有交点；下方 ΔTc 展示的是两条计算的差。不能把没有交点的曲线外推成一个答案。提取表、线性求交源码与运行记录见[Tc 的计算与提取](/Atlas/m/allen-dynes/qe/)。

各向异性 Eliashberg 分析还要保留 Δ(k,T) 在费米面上的分布，以及能隙如何随温度消失。单条各向同性 Δ(T) 或 Allen–Dynes 数值不提供这部分信息。Ba₂N 原文 Fig. 7 展示了各向异性能隙的温度变化；本站已有方程求解入口见[EPW](/Atlas/m/epw-eliashberg/qe/)，数据覆盖到哪一类方程，以该页的实际输入输出为准。[Ba₂N Fig. 7](https://doi.org/10.1103/PhysRevB.105.165101)

## 后处理代码从数据定义写起

需要让 AI 帮忙写程序时，把原始文件的一段、各列意义、单位和预期结果一并交给它。比如提取 Tc 的请求，可以写成：

> 我要比较两次独立 QE EPC 计算的 lambda.x 输出。两份文件都按电子展宽列出了 λ、ωlog 和 Tc。请先识别实际表头，按相同 σ 配对；输出原始数值、两网格的 ΔTc，并在相邻点出现变号时作逐段线性求交。没有变号时报告当前区间没有交点，不外推。脚本应打印使用的文件、列和单位，保留完整源码，并附读取真实输出的运行命令。

之后先核对提取表，再看图。不同软件版本的列顺序、密度单位和投影定义可能不同，不能仅凭列号套用旧脚本。各算例提供完整源码和可下载数据；运行提取程序时，把报错和原文件一起检查。若计算表没有新采样点，绘图程序也不应增加貌似计算所得的点。

## 导出时再安排字体与面板

网页预览与论文图分别导出。论文 PDF 中保留矢量线条和可编辑文字，网页使用适合屏幕阅读的 PNG 或 SVG。Nature 的面板规范列出单栏 89 mm、双栏 183 mm，普通文字 5–7 pt，面板字母 8 pt；这些是该期刊的印刷要求，本站网页图可用更大的字号。[Nature 尺寸规范](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)

使用 Arial、Helvetica 或实际安装的标准字体，检查中文与希腊字母。曲线颜色由图例线段表示，图例文字保持深色；不同数据同时用线型或标记区分。去掉背景网格后，保留 EF、频率零线、高对称路径分隔线等有物理含义的参考线。Nature 的要求也强调轴标与单位、可辨认配色和可编辑矢量文字。[Nature 图件要求](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)

现有绘图程序可下载[样式辅助源码](/Atlas/examples/atlas_plot_style.py)。它负责字体和导出格式，数据范围、归一化、色标及物理参考仍需在具体脚本里设定。每幅图同时保留原始输出、提取表、完整脚本、矢量 PDF 和网页预览；修改图时从数据与源码重画，最后打开实际导出文件检查文字和面板。
