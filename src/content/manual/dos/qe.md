# QE 投影态密度（projwfc.x）：从稠密网格到原子分辨

**参考**：[INPUT_PROJWFC 文档](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html) · [INPUT_DOS 文档](https://www.quantum-espresso.org/Doc/INPUT_DOS.html)

本页目标：在独立 `pdos/` 目录里跑 scf + projwfc.x，得到总态密度和逐原子逐轨道的投影文件。与能带链分目录维护是有意为之：bands 走高对称路径，dos 要稠密 k 网格，K_POINTS 诉求不同。案例体系仍是 ZrCl2/Sc2C（nat=6）。

## 输入文件：pdos.in

真实主例全文：

```fortran
&PROJWFC
  outdir = '<outdir>'
  prefix = '<prefix>'
  ngauss=0,                      ! 高斯展宽
  degauss = 2.2d-3               ! Ry；与 scf 的 smearing 配套
  DeltaE=0.005                   ! Ry；输出能量格点步长
  lsym=.true.
  filpdos='<prefix>',            ! 产物文件前缀
  filproj='<prefix>',
/
```

参数逐条读：`degauss` 决定投影展宽，跨应变必须一致，否则 pdos_tot 之间没有可比性；`DeltaE` 定能量网格分辨率；`filpdos` 定产物文件名前缀（本例 zrclscc，故产物叫 zrclscc.pdos_tot 等）。

配套的 scf 步（pdos/pwx.in）结构块与主 scf 一致、k 网格按需求加密——稠密网格是态密度质量的关键，判据仍是 `JOB DONE`。

## 命令主线

```bash
pw.x < pwx.in > pwx.out 2>&1
projwfc.x < pdos.in > pdos.out 2>&1
```

## 判读三件套

```bash
grep "JOB DONE" pdos.out
```

```text
   JOB DONE.
```

```bash
ls *pdos* | head -4
```

```text
zrclscc.pdos_tot
zrclscc.pdos_atm#1(Zr)_wfc#1(s)
zrclscc.pdos_atm#1(Zr)_wfc#5(d)
zrclscc.pdos_atm#2(C)_wfc#2(p)
```

判据：`pdos.out` 含 `JOB DONE.`（projwfc.x 没跑完的数据一律不可用）；`pdos_tot` 与全部 `pdos_atm#N_wfc#M` 文件生成且非空。

## 产物：两层文件体系

- `zrclscc.pdos_tot`：总态密度（能量、DOS、投影 DOS 三列）；
- `zrclscc.pdos_atm#N(元素)_wfc#M(轨道)`：逐原子逐轨道，文件名自带归属（本例 Zr 4d 在 `wfc#5(d)`、C 2p 在 `wfc#2(p)`、Sc 3d 在 `wfc#4(d)`）。

## 判读：E−E_F 零点纪律与 N(E_F)

```bash
grep "the Fermi energy is" pwx.out | tail -1 | awk '{print $(NF-1)}'
```

PDOS 图横轴必须以 E − E_F = 0 为零点，E_F 取同目录 scf 输出最后一次出现的值。N(E_F) 的读法：在 `pdos_tot` 里取 E ≈ E_F 行的 DOS 列。这个量对超导和磁性讨论都有直接意义——金属体系 N(E_F) 越高，电声耦合起点越高；磁性体系 N(E_F) 的自旋分辨差决定 Stoner 倾向。引用时注明所用展宽（degauss），不同展宽下的 N(E_F) 不可直接比。

## 分工说明：dos.x（&DOS）是更轻的替代

只需要总 DOS、不需要投影时，可用 dos.x，输入更短（另一个体系的真实例子）：

```fortran
&DOS
  prefix='<prefix>'
  outdir='<outdir>'
  fildos='dos.ptte2.dat'         ! 输出 dos.ptte2.dat
/
```

projwfc.x 与 dos.x 的分工：前者给原子/轨道分辨（胖带与 N(E_F) 分析的基础），后者只出总 DOS——要做轨道归属就别省 projwfc 这一步。

## 思考

1. 为什么 `degauss` 要与 scf 的 smearing 取同一套值？
2. `pdos.out` 没有 `JOB DONE` 但 pdos 文件已生成，能不能直接用？
3. 换了赝势之后，`wfc#` 编号会变吗？对跨体系对比意味着什么？
