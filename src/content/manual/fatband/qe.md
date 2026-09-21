# QE 轨道分辨（胖带数据源）：把 pdos_atm 文件用起来

**参考**：[INPUT_PROJWFC 文档](https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html)

本页目标：dos 链跑完后，`pdos/` 目录里按原子×轨道拆开的投影文件就是「哪条带来自哪个原子哪个轨道」的数据源。本页讲怎么组织这些文件、怎么保证跨应变可比。案例体系 ZrCl2/Sc2C（nat=6），计算与 dos 页完全相同（同一 pdos.in），区别只在后处理。

## 数据源：文件名即归属

```text
zrclscc.pdos_atm#1(Zr)_wfc#5(d)   # Zr 4d
zrclscc.pdos_atm#2(C)_wfc#2(p)    # C 2p
zrclscc.pdos_atm#3(Cl)_wfc#2(p)   # Cl 3p
zrclscc.pdos_atm#4(Cl)_wfc#2(p)   # Cl 3p
zrclscc.pdos_atm#5(Sc)_wfc#4(d)   # Sc 3d
zrclscc.pdos_atm#6(Sc)_wfc#4(d)   # Sc 3d
```

每个文件是能量格点上的分轨道 ldos 列，读法与 pdos_tot 一致。界面电荷转移或能带归属问题的标准做法：同一元素（或同一层）的文件按轨道求和，叠加到能带/总 DOS 图上，费米面附近的成分占比一目了然。

## 判读三件套

```bash
ls $d/pdos/zrclscc.pdos_atm#* | wc -l
```

判据一：文件数覆盖 6 个原子的全部价道（Zr 5 道、C 2 道、Cl 各 2 道、Sc 各 4 道）。判据二：`grep -H "JOB DONE" $d/pdos/pwx.out $d/pdos/pdos.out` 两处都在——projwfc 半途而废时部分文件会缺，数一下就知道。判据三：E_F 从同目录 scf 输出取：

```bash
grep "the Fermi energy is" $d/pdos/pwx.out | tail -1
```

## 三条对齐纪律

轨道分辨对比最容易失真的是不对齐，守住三条即可比：

1. **能量零点**：统一 E − E_F = 0，E_F 取自本目录 scf（本例约 −0.34 eV 量级，以各自输出为准）；
2. **展宽与能量窗固定**：degauss 统一（本例 2.2d-3 Ry），跨应变只变结构不变参数；
3. **wfc 编号不跨体系硬对齐**：`wfc#` 编号跟随赝势的价道排列，换赝势后编号会变；`lsym=.true.` 下低对称体系投影可能按对称性合并，严格逐原子拆分时先核对 `pdos.out` 里的投影计数是否与 nat 一致。

## 产物与判读落点

本页交付一套轨道分辨证据：对每个应变给出「费米面附近 Zr 4d / Sc 3d / C 2p / Cl 3p 各占多少」。判读结论直接决定后续讨论的落点——费米面贡献集中在金属阳离子 d 道（电声与超导的主战场）还是阴离子 p 道（配位/共价主导）。

尚未覆盖：把权重画到 k 点上、逐能带宽窄变化的 k 分辨投影能带（fatband）作图待填充——本页的 pdos_atm 文件是它的数据基础。

## 思考

1. 为什么「同一元素按轨道求和」之前必须先确认投影计数与 nat 一致？
2. `lsym=.true.` 在什么情形下会把哪些投影合并起来？对界面低对称体系意味着什么？
3. 若两个应变的 degauss 一个是 2.2d-3 另一个是 2.2d-2，画在同一张图上会怎样？
