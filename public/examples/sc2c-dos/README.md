# 给定三原子 Sc₂C 几何的近费米 DOS

这是 QE 7.5 产生的一份非磁、无 SOC、固定几何的电子 DOS 数据。晶胞 a=3.358477221 Å、c=40 Å，Sc–C–Sc 三原子中性胞有 26 个 PAW 价电子；C 到两侧 Sc 平面的高度为 1.121277504 Å 和 1.204184232 Å。本分支没有重新弛豫。实际设置为 vdW-DF3-opt1、100/800 Ry、16×16×1，SCF 与 DOS 的 Gaussian 参数均为 0.0037 Ry。

`case/` 保留完整输入、SCF/DOS stdout、DOS stderr、原生三列 DOS 和 SCF XML。公开副本将 prefix 统一写作 sc2c，并把原 DOS 读取目录映射为 ./out/；日志中相应目录也作了同一映射。软件版本、运行记录、结构、能量、力、应力、k 点、本征值和 DOS 数值没有改动。这些是已有运行的公开派生副本，映射后的路径不是一次另行运行的回执。

SCF stdout 记录 52 次迭代后收敛并正常结束；DOS stdout 写出 Gaussian 参数并正常结束。DOS stderr 保留显示授权提示及 IEEE underflow/denormal 信息，stdout 的 negative rho 为 8.592E−05；原始诊断随完整输出保留。

`pseudos/` 为实际采用的命名 Sc/C PAW 文件，原文件说明随文件保留。PAW 以 PBE 构造，而实际计算的交换关联为 vdW-DF3-opt1；两者名称不能互相替换。`data/` 中 DOS 表有 101 行，本征值表有 510 行。DOS 与累计列原样保留；前四列分别给出原生 F8.3 打印能量/相对费米能和由输入重建的精确网格/相对费米能。零点使用 XML 的自身费米能 −2.124738461037 eV，不把打印到三位小数的能量当成精确网格。

在此目录实际可用的静态导出命令为：

```bash
python3 source/process_native_dos.py --xml case/data-file-schema.xml --dos-input case/dos.in --dos-data case/dos_preview.dat --output-dir data
```

程序只用 Python 标准库，核对非自旋 XML、30 个不可约 k 点、17 条带、带自旋因子的权重和 2，以及加权占据电子数。它按原 DOS 输入重建 0.01 eV 网格；不重算 DOS、不平滑曲线、不变更归一化。该命令重新导出的两个 CSV 与随包 CSV 全列相同。

作图使用 GNUplot 6.0。完整程序在 `source/plot_dos.gp`：

```bash
gnuplot source/plot_dos.gp
```

它把 CSV 第五列 DOS 放横轴，第四列 E−Ef 放纵轴，将全部 101 点直接连线，输出 `figures/sc2c-dos.svg` 和 `figures/sc2c-dos.pdf`。费米能处的点为 5.433 states/(eV·cell)，已经包括两自旋；不再乘 2，也不除以三原子数。原生累计列从窗口下限开始，每个点先加上 DOS(E)×0.01 eV，再写出累计值。起点、费米点和上界依次为 0.007598、1.862、4.172 states/cell；第一点已含一个矩形项，上界也包含费米能以上的态。保留这列的原生累加定义，不能换成梯形积分，也不能用窗口末值核验 26 个电子。

本征值表为 30 个不可约 k 点×17 条带。k 坐标是 Cartesian 2π/alat 单位，不是晶格分数坐标；点编号顺序也不是 M–Γ–K–M 路径。

包内没有电荷密度或完整波函数/save。上述静态导出和作图直接读取随包数据；如果从头计算，应在 `case/` 用匹配版本的 pw.x 运行完整 `scf.in` 生成 `out/sc2c.save` 后，再用 dos.x 读取 `dos.in`。SCF 设置和各字段可联读 Atlas 的 SCF/QE 页。现有 XML 单独搬到新目录启动 dos.x 尚未实际接受。

这份近费米 DOS 和已有采样中的 13/14 带穿越支持本输入的金属态特征。k 网格、展宽、几何弛豫和 SOC 影响需要各自的对照；把 DOS 的能量聚集连到完整 k 空间口袋需要相应能带/费米面数据。
