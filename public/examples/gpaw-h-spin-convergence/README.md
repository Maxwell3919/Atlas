# 能量稳定，为什么 SCF 仍未收敛？

直接打开 index.html 即可查看：它自带80步数据，无远程请求或服务器依赖。方向键/Home/End选择步数，按钮和表中步号也可鼠标/触摸选择。SVG图在小屏可水平平移，打开原图后可放大；CSV与SVG链接下载保存文件。

本页只重放已保存的一个失败尝试：GPAW26.7.0旧计算器、ASE3.29.0/Python3.12.3/libxc5.2.3；中性H，PBE，周期6Å立方盒、Γ、PW340eV、2能带、零展宽、固定1μB双重态、symmetry off。原生日志显示80步后KohnShamConvergenceError/exit1，分数自旋参考没有执行。没有成功返回的能量/占据/最终密度/磁矩，不能形成配对能差或物理精度结论。这里不提供新的科学计算运行入口，不把重绘称作重现成功SCF。

scf-raw-lines.txt 逐字复制原 gpaw.txt 第209–288行；它是完整80步表的摘录，不是完整原生日志，也未包含末尾错误块。原完整日志SHA-256为 ab6999d81a6e7eb889284cf3fa9dcb20230a316790490ab7f3f9d531f901f929。scf-iterations.csv 保留行号、原行、打印token和原生c标记；第1步密度空白不是0。原始能量是外推总能量/eV，不是残差。log10残差仅两位小数，10^x近似不能恢复内部精确残差。能量/密度c从7/11步持续出现；本征态无c，最后−2.50约3.16e−3 eV²/价电子，目标1e−8；密度目标1e−6电子/价电子。

使用已安装Python/Matplotlib，重绘保存数据：

```sh
cd gpaw-h-spin-convergence
python3 plot.py
```

输入 scf-iterations.csv，输出 residual.svg。脚本只绘图，不导入GPAW/ASE，不运行SCF。两面板保留各自单位和阈值，不把总能量画成残差；连线不意味着步间采样。

GPAW来源与许可证：[官方源26.7.0](https://gitlab.com/gpaw/gpaw/-/tree/26.7.0)，GPL-3.0-or-later；PAW H数据来源与原始哈希保持既有公开H数据身份。本包不再分发PAW数据、原计算输入或GPAW程序。ASE为LGPL-2.1-or-later，本包不再分发ASE。此处新编写的页面、脚本与重绘图采用GPL-3.0-or-later，许可证文本见 https://www.gnu.org/licenses/gpl-3.0.html 。SCF摘录是保存运行的事实记录；没有第三方论文图或内部框架记录。

列含义对应同版本 scf.py/write_iteration 和 convergence_criteria.py/Energy,Density,Eigenstates；其官方缓存源码与已核版本绑定。受约束打印+1.0000μB只表示约束下的打印量。没有逐带/逐自旋残差，不能确定哪一轨道主导失败，也不能据通用提示认定空带、混合或内部求解次数为根因。
