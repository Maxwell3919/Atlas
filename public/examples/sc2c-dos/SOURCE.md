# 数据和读图出处

数据来自固定三原子 Sc₂C 的既有 QE 7.5 SCF 与 DOS 运行；本包沿用这些原生文件和已有 CSV，未新增 DFT。输入与输出的物理字段保持，路径/prefix 的公开映射见 README。两个 PAW 名称为 Sc.pbe-spn-kjpaw_psl.1.0.0.UPF 与 C.pbe-n-kjpaw_psl.1.0.0.UPF，文件原说明完整保留。

公开读图依据 Bekaert、Sevik 与 Milošević，2020，First-principles exploration of superconductivity in MXenes，Nanoscale，DOI：[10.1039/D0NR03875J](https://doi.org/10.1039/D0NR03875J)。采用[大学机构库的 RSC accepted manuscript](https://repository.uantwerpen.be/docman/irua/e6d66b/171988.pdf)的 Fig. 5(b,d) 图号：b 为 Sc₂C 路径能带和右侧电子 DOS，d 为费米速度着色的费米面；a/c 为 Ta₂N。图中的 DOS 横轴 e/eV·uc，能量轴相对费米能，路径 M–Γ–K–M；图注的蓝实线含 SOC、红虚线不含 SOC。d 色标为 v(10⁶ m/s)，刻度 0–0.7，蓝色低、红色高；此处红蓝表示速度，与能带的 SOC 红蓝线型含义不同。电子 DOS、声子 DOS 与 Eliashberg 谱是不同对象，Fig. 6 的数据不属于本包。

本包图沿用 DOS 横向、能量纵向的读法，范围为实际计算的 −0.5～0.5 eV、每晶胞两自旋求和；没有数字化原文曲线。原文能带/口袋以及其 EPC、Tc 属于原作者计算，本文给定不对称固定几何数据是另一份计算示例。

软件参数定义：[QE 7.5 INPUT_DOS.def](https://github.com/QEF/q-e/blob/qe-7.5/PP/Doc/INPUT_DOS.def)。Emin/Emax/DeltaE 为 eV，degauss 为 Ry；ngauss=0 是 Gaussian。静态导出使用 XML 的 Ha→eV 和已有带自旋权重，完整实现随包给出。

累计列按[QE 7.5 dos.f90](https://github.com/QEF/q-e/blob/qe-7.5/PP/src/dos.f90#L197)的 Gaussian 分支逐点矩形相加。源码先将 DOSint 初始化为零，每个能量点累加后写出，原能量字段按 F8.3 打印。随包 CSV 同时保留打印网格与由输入生成的逻辑网格，没有替换原生累计列。
