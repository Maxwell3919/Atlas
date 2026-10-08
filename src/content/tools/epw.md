# EPW：把电子模型接到位移响应与谱

电子能量的 Wannier 插值没有提供电子–声子矩阵元。EPW 需要匹配的电子父态、DFPT 位移势响应和 Wannier 子空间，才能在细电子/声子网格上读取耦合。先区分“生成谱”和“把保存的谱交给方程”两条接口，避免把一张谱误当成完整计算父链。

## 软件取得和实际版本

本站公开 Al 输出标明 EPW 6.0，源码核对固定在 [QE 7.5 的 EPW 树](https://github.com/QEF/q-e/tree/qe-7.5/EPW)。树内 README 仍写 v5.9，因此运行身份以原生输出头为依据，不能把 README 标签覆盖到输出。[同标签 Makefile](https://github.com/QEF/q-e/blob/qe-7.5/Makefile)包含 `epw` 目标及其 PH、Wannier 和接口依赖；读者应在已经配置 Fortran/数学库的匹配 QE 源树构建 `make -j2 epw`，并检查实际输出版本。本轮未安装、编译或启动 `epw.x`。

## 两种输入不应混用

| 路线 | 必须匹配的输入 | 可检查的输出 |
|---|---|---|
| 粗矩阵 → Wannier 插值 → 谱 | SCF/NSCF 父态、dvscf、粗电子/声子网格、结构与窗口 | `source/epw2.in/out`、`source/al.a2f` |
| 保存谱 → 各向同性方程 | `fila2f`、谱的列与单位、μ*、温区和截断 | `linear-*/epw.in/out/err`、低温虚轴解 |

[公开 Al 原生谱包](/Atlas/examples/al-epw-wannier-tc-files.tar.gz)解开后顶层为 `al-epw-wannier-tc/`。它保存历史输入、原生输出、谱与提取脚本，省略完整粗矩阵和 dvscf/save。`source/epw2.out` 头为 EPW 6.0；`linear-refine/epw.in` 设置 `fila2f='../source/al.a2f'`、`nqstep=500`、`wscut=0.10` eV。文件路径存在不证明粗矩阵父链也存在。

同版本 [io/io_supercond.f90 的 read_a2f](https://github.com/QEF/q-e/blob/qe-7.5/EPW/src/io/io_supercond.f90#L1281-L1339)读取 `fila2f`：跳过首行，再读取 `nqstep` 行，将第一列频率从 meV 转为 eV；[supercond_driver.f90 的 eliashberg_eqs](https://github.com/QEF/q-e/blob/qe-7.5/EPW/src/supercond_driver.f90#L45-L71)选择读谱及求解分支；`supercond.f90` 中的 [eliashberg_init](https://github.com/QEF/q-e/blob/qe-7.5/EPW/src/supercond.f90#L22)和 [eliashberg_grid](https://github.com/QEF/q-e/blob/qe-7.5/EPW/src/supercond.f90#L279-L358)分别处理初始化与频率网格、截断逻辑。遇到找不到谱、读列失败、温度表缺行或迭代未收敛，要分别检查相对路径、单位/样本数、stderr 与原生结束标记；不能仅从生成了 CSV 就接受方程或材料 Tc。不同谱来源的温度差也不是求解器精度比较。

## 从保存输出提取表，而不重解方程

在新目录解开包后，复制最小输入到一个不存在的检查目录。以下脚本只需 Python 3 标准库，按自身位置读写，不接受输出目录参数：

```bash
mkdir new-epw
cp al-epw-wannier-tc/analyse_tc.py new-epw/
cp -R al-epw-wannier-tc/linear-coarse al-epw-wannier-tc/linear-refine al-epw-wannier-tc/nonlinear-T0.25 new-epw/
mkdir new-epw/source
cp al-epw-wannier-tc/source/al.a2f new-epw/source/
python3 new-epw/analyse_tc.py
```

这组命令的保存数据提取已在本站案例集成时实跑；本轮没有重复执行。检查 `linear.csv` 15 行、`gap.csv` 一行、`source-spectrum.csv` 500 行，以及 `solver-status.json`、`tc-brackets.json` 与包内保存参考的逐字比较。脚本的 `SHA256.json` 先于后两项输出生成，不是完整最终清单。0.84–0.85 K 是保存的固定各向同性模型交叉区间，没有材料精度或联合收敛保证。

完整物理解释见 [EPW/Eliashberg 教程](/Atlas/m/epw-eliashberg/qe/)和[从电荷到模式的公开案例](/Atlas/cases/charge-to-epc/)。[Phonopy](/Atlas/tools/phonopy/)处理另一条力常数接口，不能用其力常数文件替代 EPW 的电子–声子矩阵元。
