色散定位哪一支在什么 q 变软，声子态密度则统计整个布里渊区中某一频段的模式数。给每个模式加上原子或层权重，就能继续回答这个频段主要由哪一层、哪种元素参与。界面和应变分析需要把这两种读法对应起来：色散上的高频支与 PHDOS 中的元素峰属于同一套力常数，但高对称路径上的点数不能当作布里渊区积分权重。

先接着 [Al DFPT](/Atlas/m/phonon-dfpt/qe/)完成从力常数到 DOS 的操作。单原子 fcc Al 用 QE 7.5、LDA-PZ `Al.pz-vbc.UPF` 和完整 4³ 原始 q 网格，下面比较 24³ 与 32³ 后处理网格。它的原胞总共三个振动自由度，适合直接核对积分与列含义；多元素界面分析放在后半段。

输入、输出、数据与完整脚本可[一起下载](/Atlas/examples/al-lesson-files.tar.gz)。解包后进入 `al` 运行绘图命令。[Ba₂N 论文 Fig. 3(b) 与 Fig. 6(b)](https://doi.org/10.1103/PhysRevB.105.165101)展示原子 PHDOS 如何与应变色散及 α²F 配对；下面采用的是这种按频段与原子组成对读的分析。

## 先看手上的动力学矩阵

```console
maxwell@maxwell:~/al/dfpt$ ls al.dyn*
al.dyn0
al.dyn1
al.dyn2
al.dyn3
al.dyn4
al.dyn5
al.dyn6
al.dyn7
al.dyn8
```
`al.dyn0` 是 q 网格的索引，后面的编号文件才存放各个不可约 q 点的动力学矩阵。8 个不可约点不等于只计算了 8 个任意 q 点；它们借助晶体对称性覆盖这里的完整 64 点网格。

```console
maxwell@maxwell:~/al/dfpt$ cat al.dyn0
   4   4   4
   8
   0.000000000000000E+00   0.000000000000000E+00   0.000000000000000E+00
  -0.176776695296637E+00   0.176776695296637E+00  -0.176776695296637E+00
   0.353553390593273E+00  -0.353553390593273E+00   0.353553390593273E+00
   0.000000000000000E+00   0.353553390593273E+00   0.000000000000000E+00
   0.530330085889910E+00  -0.176776695296637E+00   0.530330085889910E+00
   0.353553390593273E+00   0.000000000000000E+00   0.353553390593273E+00
   0.000000000000000E+00  -0.707106781186547E+00   0.000000000000000E+00
  -0.353553390593273E+00  -0.707106781186547E+00   0.000000000000000E+00
```
先核对网格，再看程序是否真的走到末尾。一个文件刚出现时，程序还可能在写它。这里末尾的运行时间和 `JOB DONE.` 是程序结束证据；SCF 和各个响应分量的收敛还要在前面的输出中逐项检查。

```console
maxwell@maxwell:~/al/dfpt$ tail -12 al.ph.out
     h_psi:calbec :      5.55s CPU      6.68s WALL (  859163 calls)
     s_psi_bgrp   :      1.70s CPU      2.04s WALL ( 1409957 calls)
 
 
     PHONON       :   2m40.10s CPU   3m11.61s WALL

 
   This run was terminated on:  21:38:17  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
## 从 q 空间回到实空间力常数

动力学矩阵按 q 点存放，`q2r.x` 把这一整套相容的网格变成实空间力常数。原来的 `al.dyn*` 留在原处，转换结果另写成 `al.fc`。

```console
maxwell@maxwell:~/al/dfpt$ cat q2r.in
&INPUT
 fildyn='al.dyn'
 flfrc='al.fc'
 zasr='simple'
/
```
这里 `fildyn` 对应文件名前缀，`flfrc` 是即将写出的力常数文件。`q2r.x` 的 `zasr` 针对 Born 有效电荷的和规则；这份金属 Al 数据没有 Born 有效电荷，不能把 `zasr='simple'` 当作已经修正声学支的依据。下面 `matdyn.x` 的 `asr='crystal'` 才对力常数施加三条平移和规则。它约束整体平移的恢复力，不能消除原始 q 网格或电子参数造成的误差。不要从另一份结构的目录借几个编号文件来凑齐网格。

```console
maxwell@maxwell:~/al/dfpt$ <qe_bin>/q2r.x -in q2r.in > q2r.out 2> q2r.err

```
```console
maxwell@maxwell:~/al/dfpt$ tail -12 q2r.out
      q-space grid ok, #points =   64

      fft-check success (sum of imaginary terms < 10^-12)
 
     Q2R          :      0.00s CPU      0.00s WALL

 
   This run was terminated on:  21:38:19  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
这里的 `#points = 64` 与 4×4×4 相符，`fft-check success` 说明这一轮读入的数据通过了程序的 Fourier 一致性检查。它不回答 q 网格是否足够密；那个问题要增加真正的 DFPT q 采样，再比较目标频率或 DOS。

## 用均匀网格积分，而不是沿高对称线计数

```console
maxwell@maxwell:~/al/dfpt$ cat matdyn-dos.in
&INPUT
 flfrc='al.fc'
 asr='crystal'
 dos=.true.
 nk1=24
 nk2=24
 nk3=24
 deltaE=1.0
 fldos='al.phdos.dat'
/
```
`dos=.true.` 让 `matdyn.x` 在均匀 q 网格上用四面体方法计算 DOS。`nk1`、`nk2`、`nk3` 是声子积分网格，不是 SCF 的电子 k 网格，也不是重新调用 `ph.x` 计算响应。这里从 4×4×4 的力常数插值到 24×24×24 点；`deltaE=1.0` 指定输出频率轴的步长为 1 cm⁻¹，不是 Gaussian 展宽，输出文件名为 `al.phdos.dat`。减小这个步长只会把频率轴取样写得更细，不会补充原始 DFPT 响应点。

```console
maxwell@maxwell:~/al/dfpt$ <qe_bin>/matdyn.x -in matdyn-dos.in > matdyn-dos.out 2> matdyn-dos.err

```
```console
maxwell@maxwell:~/al/dfpt$ tail -12 matdyn-dos.out

     Message from routine matdyn:
     Z* not found in file al.fc, TO-LO splitting at q=0 will be absent!
 
     MATDYN       :      5.32s CPU      5.32s WALL

 
   This run was terminated on:  21:38:25  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
这份输出写着 `Z* not found`。本例是金属 Al，没有在这条路线中计算绝缘体的 Born 有效电荷和非解析项；所以不能把这句话解释成已经处理了极性材料的 LO–TO 分裂。若换成极性绝缘体，应回到 DFPT 计算相应的电场响应，保持同一套结构与参数。

```console
maxwell@maxwell:~/al/dfpt$ head -8 al.phdos.dat
 # Frequency[cm^-1] DOS PDOS
 -2.9127447802E-06  0.0000000000E+00  0.0000E+00
  9.9999708726E-01  6.8963092060E-08  6.8963E-08
  1.9999970873E+00  2.7585269581E-07  2.7585E-07
  2.9999970873E+00  6.2066881126E-07  6.2067E-07
  3.9999970873E+00  1.1034114384E-06  1.1034E-06
  4.9999970873E+00  1.7240805772E-06  1.7241E-06
  5.9999970873E+00  2.4826762278E-06  2.4827E-06
```
第一列是频率，单位 cm⁻¹；第二列是总 DOS；第三列是这里唯一一个原子的投影贡献。单原子原胞只有 3 条声子支，所以对总 DOS 积分应接近 3，而不是电子 DOS 中常见的电子态数。文件开头的约 −0.000003 cm⁻¹ 在这个计算中对应数值零，不能据此画出一个有物理意义的负频峰。

换 32³ 的过程只改变后处理积分网格，保留原输出：

```console
maxwell@maxwell:~/al/dfpt$ cp matdyn-dos.in matdyn-dos32.in
maxwell@maxwell:~/al/dfpt$ vi matdyn-dos32.in
maxwell@maxwell:~/al/dfpt$ cat matdyn-dos32.in
&INPUT
 flfrc='al.fc'
 asr='crystal'
 dos=.true.
 nk1=32
 nk2=32
 nk3=32
 deltaE=1.0
 fldos='al.phdos32.dat'
/
```
保存后仍在 `al/dfpt` 目录运行第二份输入，再检查它自己的输出与错误文件：

```bash
<qe_bin>/matdyn.x -in matdyn-dos32.in > matdyn-dos32.out 2> matdyn-dos32.err
tail -n 14 matdyn-dos32.out
cat matdyn-dos32.err
```

本次保存的 [matdyn-dos32.out](/Atlas/examples/al/dfpt/matdyn-dos32.out) 记录了 22.21 s WALL 与 `JOB DONE.`，[matdyn-dos32.err](/Atlas/examples/al/dfpt/matdyn-dos32.err) 为空。`fldos` 使用新的文件名，因此两份 `al.phdos*.dat` 都会保留。先完成这一步，再运行同时读取两份数据的绘图脚本。

## 把积分数和图放在一起检查

解包本页开头的 Al 算例并保留目录结构，在 `al` 目录运行[绘图脚本](/Atlas/examples/al/plot_phdos.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)）。脚本从 `dfpt/al.phdos.dat` 和 `dfpt/al.phdos32.dat` 读取 24³、32³ 两份数据；[单独下载的原始 DOS 数据](/Atlas/examples/al/dfpt/al.phdos.dat)也应放回对应的 `dfpt` 子目录。它先输出积分再画曲线，这样能发现列读错、单位弄错或数据截断的问题。


绘图脚本读取两份总 DOS，先按频率列积分并与单原子原胞的 3 个振动自由度比较，再叠画 24³ 与 32³ 积分网格的结果。下面的需求对应这一步：

```text
编写 plot_phdos.py，从 Al 根目录读取 dfpt/al.phdos.dat 与 dfpt/al.phdos32.dat，比较 24³ 和 32³ 后处理积分网格。第一列频率单位 cm⁻¹，第二列总 DOS 单位 states/(cm⁻¹)；用梯形积分打印原始积分，与单原子原胞的 3 个模式比较，不强制归一化。以真实频率列画 DOS 曲线、标单位和网格，输出 figures/phdos.png 与 PDF，复用 atlas_plot_style.py。
```

<details>
<summary>plot_phdos.py 完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
fig,ax=plt.subplots(figsize=(6.8,4.3),layout="constrained")
for n,file in [(24,"al.phdos.dat"),(32,"al.phdos32.dat")]:
    d=np.loadtxt(root/"dfpt"/file)
    print(f"mesh={n} integral={np.trapezoid(d[:,1],d[:,0]):.8f}")
    ax.plot(d[:,0],d[:,1],label=f"{n}³ integration mesh",lw=1.8)
ax.set(xlabel="Frequency (cm⁻¹)",ylabel="Phonon DOS (states / cm⁻¹)",xlim=(0,None))
ax.legend(frameon=False);ax.grid(alpha=.18)
(root/"figures").mkdir(exist_ok=True)
fig.savefig(root/"figures/phdos.png",dpi=220)
fig.savefig(root/"figures/phdos.pdf")
```

</details>

```bash
python3 plot_phdos.py
```

本次 24³ 网格的积分是 **2.99953038**；32³ 网格为 **2.99931874**。完整频率范围是约 0—332 cm⁻¹。两次积分都应与 3 对照，而不是强行归一化后再宣布通过。

<figure><img src="/Atlas/examples/al/figures/phdos.png" alt="Al 声子态密度，24与32网格积分比较" loading="lazy"/><figcaption>同一份 4×4×4 DFPT 力常数上的两种积分网格。曲线是实际输出的 DOS，没有手工平滑或补点。</figcaption></figure>

两种积分网格的总模式数都接近 3，且图中的主要峰形相近。这个对照检验同一组力常数上的布里渊区积分；要看力常数本身怎样随原始 DFPT q 网格变化，需要另一组响应计算。

## 原子 PHDOS 用的是什么向量

用归一化动力学矩阵本征矢 e 定义某原子 I 的模态权重 `W_I(qν)=Σ_α|e_Iα(qν)|²`，原子谱可写成

$$
g_I(\omega)=\sum_{\mathbf q\nu}w_{\mathbf q}W_I(\mathbf q\nu)\,\delta(\omega-\omega_{\mathbf q\nu}),\qquad
\sum_I g_I(\omega)=g(\omega).
$$

w_q 是布里渊区积分权重。总谱在完整频段的积分对应 `3N_at` 个自由度。[QE 7.2 matdyn 源码](https://github.com/QEF/q-e/blob/qe-7.2/PHonon/PH/matdyn.f90#L689-L695)的 `dynq` 由对角化得到的位移乘回质量因子，形成本征矢平方投影；7.5 使用相同定义。因此 `.phdos` 的原子峰是质量加权模态组成，不是原子的实际振幅平方。若要画归一化位移的方向权重，应另读 `.modes`，并在图例注明向量定义。

多原子文件每行依次给出频率、总 DOS 和按输入原子顺序排列的 N_at 个投影列。把频率从 cm⁻¹ 换为 THz 时，横轴除以 `33.3564095198152`，谱密度乘以同一个因子，积分保持不变。只改横轴单位会把模式数也改掉。

## 按真实原子顺序合成元素与层投影

ZrCl₂/Sc₂C 的[结构输入](/Atlas/examples/zrcl2-sc2c/ph64/pwx.in)中，顺序为 `1 Zr、2 C、3 Cl、4 Cl、5 Sc、6 Sc`。Cl 合并第 3、4 个原子列，Sc 合并第 5、6 个原子列；ZrCl₂ 层合并第 1、3、4 个原子列，Sc₂C 层合并第 2、5、6 个原子列。这里的层分组由结构中的原子归属决定，与元素类型编号不同。

SnSe₂/Sr₂N 的[结构输入](/Atlas/examples/snse2-sr2n/ph64/pwxall.in)顺序为 `Sr、Sr、Sn、Se、Se、N`。Sr₂N 层对应第 1、2、6 个原子，SnSe₂ 层对应第 3、4、5 个原子。两份文件都是六原子体系，但不能共用同一套列号。

当前界面 DOS 的[ZrCl₂/Sc₂C 运行输出](/Atlas/examples/zrcl2-sc2c/ph64/matdyn_dos.out)和[SnSe₂/Sr₂N 输出](/Atlas/examples/snse2-sr2n/ph64/matdyn_dos.out)记录的是 QE 7.2，区别于上面的 Al 7.5。两份存档输入均采用 `asr='simple'`、`nk1=nk2=48`、`nk3=1`、`ndos=400`，并从已有 `.fc` 读取质量；这次复核只读取现存 `.phdos` 和结构，没有重新计算力常数。

[完整投影脚本](/Atlas/examples/phonons-interface-projections/analyse_phdos.py)读结构确定原子顺序，再从真实数据合成元素和层谱。它不平滑、不强制归一化，也不由色散图反推谱线。数据格式、单位变换与编程需求如下：

```text
编写 analyse_phdos.py，参数 --public-root 指向解包后的 public 数据根目录，--output 指定结果目录。读取 examples/zrcl2-sc2c/ph64/zrclscc.phdos 与 pwx.in，及 examples/snse2-sr2n/ph64/srnsnse.phdos 与 pwxall.in。每份数据应有频率、总DOS和六列原子投影；从 ATOMIC_POSITIONS 核对原子顺序。频率除以 33.3564095198152，所有谱密度乘以同一因子。按正文的真实原子号合成元素与层谱，保存 CSV；打印原始总积分与18的比较，记录逐原子、逐层积分及投影和相对峰值的偏差。负频符号保留，不修改原始文件、不自动归一化、不画示意数据。
```

<details>
<summary>analyse_phdos.py 完整源码</summary>

```python
#!/usr/bin/env python3
"""Group existing QE 7.2 atomic PHDOS; do not recompute force constants."""
from pathlib import Path
import argparse, csv, json, re
import numpy as np

CM_PER_THZ = 33.3564095198152
CASES = {
    "zrcl2-sc2c": {
        "dos": "zrclscc.phdos", "input": "pwx.in",
        "symbols": ["Zr", "C", "Cl", "Cl", "Sc", "Sc"],
        "layers": {"ZrCl2": [0, 2, 3], "Sc2C": [1, 4, 5]},
    },
    "snse2-sr2n": {
        "dos": "srnsnse.phdos", "input": "pwxall.in",
        "symbols": ["Sr", "Sr", "Sn", "Se", "Se", "N"],
        "layers": {"Sr2N": [0, 1, 5], "SnSe2": [2, 3, 4]},
    },
}

def analyse(public_root, output):
    output.mkdir(parents=True, exist_ok=True)
    report = {"numpy_version": np.__version__,
              "projection": "QE 7.2 matdyn dynq: squared dynamical-matrix eigenvector",
              "density_unit": "states/THz", "frequency_unit": "THz", "cases": {}}
    for name, case in CASES.items():
        directory = public_root / "examples" / name / "ph64"
        text = (directory / case["input"]).read_text()
        tail = re.split(r"ATOMIC_POSITIONS[^\n]*\n", text, flags=re.I)[1]
        symbols = [line.split()[0] for line in tail.splitlines()[:6]]
        assert symbols == case["symbols"], (name, symbols)
        data = np.loadtxt(directory / case["dos"])
        assert data.shape[1] == len(symbols) + 2
        assert np.all(np.isfinite(data)) and np.all(np.diff(data[:, 0]) > 0)
        frequency = data[:, 0] / CM_PER_THZ
        total = data[:, 1] * CM_PER_THZ
        atoms = data[:, 2:] * CM_PER_THZ
        elements = {s: np.flatnonzero(np.array(symbols) == s).tolist()
                    for s in dict.fromkeys(symbols)}
        groups = {**elements, **case["layers"]}
        grouped = {g: atoms[:, ids].sum(axis=1) for g, ids in groups.items()}
        with (output / (name + "-grouped.csv")).open("w") as handle:
            writer = csv.writer(handle)
            writer.writerow(["frequency_THz", "total_states_per_THz", *groups])
            writer.writerows(zip(frequency, total, *grouped.values()))
        integral = lambda y: float(np.trapezoid(y, frequency))
        peak = float(np.max(np.abs(total)))
        result = {"sources": ["examples/" + name + "/ph64/" + case[k]
                              for k in ["dos", "input"]],
                  "atom_order": symbols, "layer_site_indices_1based": {
                      g: [i + 1 for i in ids] for g, ids in case["layers"].items()},
                  "rows": len(data), "frequency_range_THz": [float(frequency[0]), float(frequency[-1])],
                  "total_integral": integral(total), "expected_modes": 3 * len(symbols),
                  "atom_integrals": [integral(atoms[:, i]) for i in range(len(symbols))],
                  "group_integrals": {g: integral(y) for g, y in grouped.items()},
                  "max_projection_sum_error_relative_to_peak":
                      float(np.max(np.abs(atoms.sum(axis=1) - total)) / peak)}
        report["cases"][name] = result
        print(f"{name}: rows={len(data)} modes={result['total_integral']:.8f} / 18 "
              f"sum_error/peak={result['max_projection_sum_error_relative_to_peak']:.3e}")
        print("  atom order:", ", ".join(f"{i+1}:{s}" for i, s in enumerate(symbols)))
        print("  layer integrals:", ", ".join(f"{g}={result['group_integrals'][g]:.8f}"
                                               for g in case["layers"]))
    (output / "projection-checks.json").write_text(json.dumps(report, indent=2) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("projection-results"))
    arguments = parser.parse_args()
    analyse(arguments.public_root, arguments.output)
```

</details>

[界面 PHDOS 轻量复算包](/Atlas/examples/phonons-interface-projections-files.tar.gz)包含完整脚本和下面四份原始输入；需要 Python 3 与 NumPy 2.0 或更新版本。也可分别下载 [ZrCl₂/Sc₂C 原始 PHDOS](/Atlas/examples/zrcl2-sc2c/ph64/zrclscc.phdos)、[对应结构输入 pwx.in](/Atlas/examples/zrcl2-sc2c/ph64/pwx.in)、[SnSe₂/Sr₂N 原始 PHDOS](/Atlas/examples/snse2-sr2n/ph64/srnsnse.phdos)和[对应结构输入 pwxall.in](/Atlas/examples/snse2-sr2n/ph64/pwxall.in)，按以下目录放置。这里的 public 是这四份文件的数据根目录，不需要另下载整站或页首的 Al 包。

```text
phonons-interface-projections/
├── analyse_phdos.py
└── public/
    └── examples/
        ├── zrcl2-sc2c/
        │   └── ph64/
        │       ├── zrclscc.phdos
        │       └── pwx.in
        └── snse2-sr2n/
            └── ph64/
                ├── srnsnse.phdos
                └── pwxall.in
```

下载轻量包后，在保存它的目录解压，进入上面的顶层目录，再运行同一条分组命令：

```bash
tar -xzf phonons-interface-projections-files.tar.gz
cd phonons-interface-projections
python3 analyse_phdos.py --public-root ./public --output ./projection-results
```

这次在 Talos 的 NumPy 2.4.6 中实际得到：

```text
zrcl2-sc2c: rows=400 modes=18.52393348 / 18 sum_error/peak=9.400e-06
  atom order: 1:Zr, 2:C, 3:Cl, 4:Cl, 5:Sc, 6:Sc
  layer integrals: ZrCl2=9.55101188, Sc2C=8.97291708
snse2-sr2n: rows=400 modes=18.74245521 / 18 sum_error/peak=4.769e-06
  atom order: 1:Sr, 2:Sr, 3:Sn, 4:Se, 5:Se, 6:N
  layer integrals: Sr2N=9.34211754, SnSe2=9.40032494
```

两份谱在每个频率处的原子投影和与总 DOS 相符到打印精度，但对当前 400 行数据作梯形积分分别得到 18.52393348 和 18.74245521，比六原子的 18 个模式多约 2.91% 和 4.12%。这说明“投影列加起来等于总列”与“频率积分正确”是两项不同的数值关系。当前分组可复现存档中的元素谱形，但这组积分不适合用于定量比较层间振动自由度或计算精细热力学量。QE 的该 DOS 实现还注明四面体法在非立方材料中可能不适用；要查清偏差，需要从同一力常数比较频率轴密度和适合二维积分的处理，而不是把输出统一缩放到 18。

可直接下载[ZrCl₂/Sc₂C 分组谱](/Atlas/examples/phonons-interface-projections/zrcl2-sc2c-grouped.csv)、[SnSe₂/Sr₂N 分组谱](/Atlas/examples/phonons-interface-projections/snse2-sr2n-grouped.csv)和[积分记录](/Atlas/examples/phonons-interface-projections/projection-checks.json)。这些层谱由原子权重求和得到，并不保留两层之间运动的相位；剪切或呼吸模仍需回到[本征位移](/Atlas/m/phonon-dfpt/qe/#h-将频率-本征矢和原子位移连起来)。

## 将频段组成与应变机制对应起来

ZrCl₂/Sc₂C 的现存路径色散在 0–10.11 THz 有 15 条中低频支，12.49–17.11 THz 有三条高频支。对照原子谱可见高频段以 C 的本征矢权重为主。它回答高频振动主要落在哪种元素上，尚不区分 C 的面内和面外运动。频段之间的间隔也不能只用轻重原子质量解释，恢复力与模式混合共同决定频率。

[Ba₂N Fig. 3(b)](https://doi.org/10.1103/PhysRevB.105.165101)中，低于约 130 cm⁻¹ 的谱主要来自 Ba，160–220 cm⁻¹ 主要来自 N；到 4% 拉伸的 Fig. 6(b)，N 频段降到约 120–172 cm⁻¹，部分 Ba 与 N 贡献发生混合。Fig. 6(a) 的 K 软模、Fig. 6(c) 的低频 α²F 峰和 Fig. 6(e) 的位移图进一步说明，谱峰移动发生在怎样的原子运动中。这个论证包含频率、投影、运动与耦合四项信息，不能只按 PHDOS 峰高排序“哪种元素贡献最大”。

界面或应变前后比较时，先统一原胞模式数、频率单位、ASR 与积分约定，再按同一原子/层分组读谱。若要解释超导变化，则接到[α²F](/Atlas/m/eliashberg-a2f/qe/)：PHDOS 统计声子模态，α²F 另含电子散射和耦合矩阵元。相同频率处两者都有峰，不意味着每个声子对耦合的权重相同。

## 参考资料

[matdyn 输入与单位](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html) · [QE 7.2 原子投影源码](https://github.com/QEF/q-e/blob/qe-7.2/PHonon/PH/matdyn.f90#L689-L695) · [Ba₂N Fig. 3、6](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.105.165101)
