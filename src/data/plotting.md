- [Nature：图件、文字和导出规范](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)
- [Nature：尺寸、面板排列与配色](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)
- [Matplotlib：PDF 与 SVG 中的字体](https://matplotlib.org/stable/users/explain/text/fonts.html)

画图前，先写清楚准备比较哪两个量。能带要交代能量零点和 k 路径，DOS 要交代每个原胞还是每个原子的归一化，声子要保留虚频，Tc 要同时留下产生它的 λ、ωlog、μ* 和公式。只调整颜色与字体，解决不了这些定义上的歧义。

本站的图从可下载的原始输出或提取表重画。输入、输出、后处理脚本和图片沿用同一组目录；计算没有完成时，不用平滑曲线把空缺接上。先运行相应页面的提取脚本，再画图，才能把图上的点追溯到具体输出行。

本次本机重绘使用 Python 3.14.0、NumPy 2.3.4 和 Matplotlib 3.10.7。提取程序所需的其他软件在各页单独注明；只改颜色、字号和导出格式，不需要重新提交 DFT。字体优先使用本机已有的 Arial，缺少时回退到 DejaVu Sans，并检查实际导出的文字。

## 先把一条曲线的含义说完整

以 [Si DOS](/Atlas/m/dos/qe/) 为例，`si.dos.dat` 的第一列是程序的绝对能量，第二列是总态密度，第三列是从低能端累计的态数。这里画的是两原子原胞的态密度；若要换成每原子单位，应把第二列除以 2，并同步修改轴标。第三列本身不能不加占据条件就叫作电子数。

零点来自同一组 `gap24-cg` 的价带顶。不要从另一组 SCF 随手复制一个 Fermi energy，也不要把每张图各自平移到“看起来一致”。下载 [Si 算例](/Atlas/examples/si-pbe-lesson-files.tar.gz) 后，进入解压得到的 `si-pbe` 目录运行：

```bash
python3 plot_si.py dos
```

图的横坐标在脚本中由以下实际数据定义：

```python
data = np.loadtxt(ROOT / 'dos-cg/si.dos.dat')
gaps = json.loads((ROOT / 'gap-results.json').read_text())
vbm = next(row['vbm_eV'] for row in gaps
           if row['directory'] == 'gap24-cg')
energy = data[:, 0] - vbm
dos = data[:, 1]
```

这里没有移动峰的位置，也没有增加采样点。Gaussian 展宽 `0.01 Ry` 属于原先 `dos.x` 的后处理设置；把曲线线宽改细，不会提高计算分辨率。若要判断峰是否稳定，需回到 NSCF 网格和展宽对照，见 [DOS](/Atlas/m/dos/qe/)。

下面两幅图使用相同数据与能量参考。第一幅保留此前网页的样式，第二幅是目前的导出样式；比较的是排版，不是新的计算结果。

![此前的 Si DOS 图，保留用于比较排版](/Atlas/figures/style-example-before.png)

![相同 Si DOS 数据的当前科研绘图样式](/Atlas/examples/si-pbe/plots/dos.png)

[当前图的矢量 PDF](/Atlas/examples/si-pbe/plots/dos.pdf) · [完整绘图脚本](/Atlas/examples/si-pbe/plot_si.py)

## 让图例、刻度和曲线各自做一件事

先定横纵轴、范围和单位，再放图例。DOS 使用 `Energy − VBM (eV)` 与 `DOS (states/eV/cell)`；声子路径的横轴用真实高对称点，不把不可约 q 点编号装作高对称路径。二维电荷切片还要给出切片方向、位置、密度单位和色标范围。

同一物理量的不同网格可以用实线、虚线和空心点区分；不同物理量可以再加颜色。图例文字保持黑色，让色块或线段承担颜色辨认。蓝、橙、绿、紫可作为分类起点，但连续场应根据数值含义选色标：只有大小的 ELF 用顺序色标，正负都有的差分电荷用以零为中心的发散色标。两幅要直接比较的密度图必须固定同一色标范围。

背景网格通常可以去掉，物理参考线应保留。例如 `E−EF=0`、虚频的零线、能带高对称路径的分隔线，以及事先规定的数值容差，各自回答一个明确的问题。误差棒来自重复样本或明确的误差估计；相邻 k 网格之间的差不能换一个名字就当作统计误差棒。

多面板图尽量共享可比较的范围。若一张图用绝对值、另一张图放大差值，在轴标和图注里直接说明。下面的 [COHP 算例](/Atlas/m/cohp/qe/) 左图保留原生占据态积分，右图比较相邻设置的最大逐键变化；右图的对数坐标使三个不同量级的差都能读出。

![金刚石真实 ICOHP 的绝对值和逐键参数对照](/Atlas/figures/cohp-diamond/cohp-comparison.png)

[这张图的矢量 PDF](/Atlas/figures/cohp-diamond/cohp-comparison.pdf) · [绘图脚本](/Atlas/examples/diamond-cohp/plot_cohp.py)

连线只帮助追踪左图的网格序列，不代表插值得到的中间计算。右图的 `0.02 eV/bond` 是这次算例事先选择的比较线；它不是一种材料的实验误差。坐标范围、连线和容差线都应有这样的具体解释。

## 同时留网页预览和可编辑矢量图

Nature 给出的印刷宽度是单栏 89 mm 或双栏 183 mm，普通文字 5–7 pt，面板字母 8 pt。本站参考这些尺寸另存论文用 PDF，同时让网页 PNG/SVG 使用较大的阅读字号。论文尺寸不应直接套在网页上。[尺寸与文字规范](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/)

曲线、刻度和文字保存在矢量 PDF 中，PNG 供网页预览。仅把 PNG 改成 600 dpi，不能恢复已经丢失的细节。需要在 Illustrator 或 Inkscape 中排版时，优先打开 PDF；检查文字仍可编辑，避免把整个坐标图作为一张位图再次截屏。[Nature 导出规范](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)

单张新图可以从下面的设置开始，再根据实际标注长度安排面板：

```python
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams.update({
    'font.family': 'Arial',
    'font.size': 7,
    'axes.labelsize': 7,
    'axes.linewidth': 0.65,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'axes.grid': False,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'svg.fonttype': 'none',
})
fig, ax = plt.subplots(figsize=(89/25.4, 65/25.4),
                       layout='constrained')
ax.plot(energy, dos, color='#0072b2', linewidth=0.9)
ax.set(xlabel='Energy − VBM (eV)',
       ylabel='DOS (states/eV/cell)', xlim=(-13, 8))
fig.savefig('dos-paper.pdf')
```

`pdf.fonttype=42` 使 PDF 使用嵌入的 TrueType 字体；`svg.fonttype='none'` 保留 SVG 的文字。Arial 不在机器上时，应选择已有字体并检查替代结果，不能只看脚本写了什么。[Matplotlib 字体说明](https://matplotlib.org/stable/users/explain/text/fonts.html)

本站下载包中的 [atlas_plot_style.py](/Atlas/examples/atlas_plot_style.py) 对既有绘图程序集中处理字体、背景网格和双格式导出。单独下载绘图脚本时，也把这个辅助文件放到同一目录。它不修改曲线数值、坐标范围、密度归一化、色标上下限和误差棒。可在自己的脚本开头加载，也可以从中取出需要的普通 Matplotlib 设置：

```python
from atlas_plot_style import install
install()
```

一次保存会生成同名 PNG、保留文字的 SVG 和独立排版的 PDF。COHP 的 `plot_cohp.py` 已在文件内部直接实现两种版式，不依赖这个辅助文件。重画之后仍需亲自检查字体是否缺字、图例是否挡住数据、零线是否清晰；统一设置不能代替逐图检查。

## 从图回到计算记录

图注应写材料或模型、关键数值设置、能量零点或归一化、曲线各自含义，以及支撑的结论。COHP 的投影质量、虚频的声学残差、Tc 对电子展宽的变化，都应该在对应图后解释。参数表与完整输出通过算例包提供，避免把长日志塞进图中。

最终保留原始输入输出、提取后的 CSV 或 NPZ、可执行绘图脚本、矢量 PDF 和网页预览。若需要改图，回到数据和脚本修改；不要在图片上挪动数据点、删除不顺眼的负频，或把图上的文字数值改成希望得到的答案。

继续阅读：[能带](/Atlas/m/bands/qe/)、[DOS](/Atlas/m/dos/qe/)、[虚频](/Atlas/m/imaginary-phonon/qe/)、[α²F](/Atlas/m/eliashberg-a2f/qe/)、[Tc 的完整提取](/Atlas/m/allen-dynes/qe/)、[差分电荷](/Atlas/m/delta-charge/vasp/)。
