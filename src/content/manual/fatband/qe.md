参考：

- QE 官方文档 INPUT_PROJWFC：<https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html>

## 先分清 PDOS 和胖带的数据

这里保留已有的能量分辨 PDOS 操作。它还不是一份完成的胖带教程：胖带需要沿能带路径、逐 k 点逐能带的投影权重；把 DOS 的 pdos_atm 文件按能量求和，不能恢复这些信息。

DOS 主流程（projwfc.x）跑完后，费米能级附近「电子到底是谁的」这个问题就靠 PDOS 文件回答。计算本身在 DOS 页已完成（同一套 projwfc.in：`filpdos='HfCl2_PbO2'`、degauss=0.0037 与 SCF/NSCF 一致），本页讲怎么组织文件、怎么归并出有解释力的轨道证据。

### 数据源：pdos_atm 文件与 state 通道

projwfc.x 的产物按「原子#(元素)_波函数#(轨道)」命名，本例（HfCl2/PbO2，6 原子）：

```text
HfCl2_PbO2.pdos_atm#1(Hf)_wfc#1(s)  … #4(d)
HfCl2_PbO2.pdos_atm#2(Cl)_wfc#1(s)  … #2(p)
HfCl2_PbO2.pdos_atm#3(Cl)_wfc#1(s)  … #2(p)
HfCl2_PbO2.pdos_atm#4(Pb)_wfc#1(s)  … #3(d)
HfCl2_PbO2.pdos_atm#5(O)_wfc#1(s)   … #2(p)
HfCl2_PbO2.pdos_atm#6(O)_wfc#1(s)   … #2(p)
HfCl2_PbO2.pdos_tot
```

先确认投影通道齐全（state 通道清单是轨道归纳的依据）：

```bash
[hzw@localhost pdos]$ grep "state #" projwfc.out
     state #   1: atom   1 (Hf ), wfc  1 (l=0 m= 1)
     ...
     state #   6: atom   1 (Hf ), wfc  4 (l=2 m= 1)
     ...
     state #  11: atom   2 (Cl ), wfc  1 (l=0 m= 1)
     ...
     state #  19: atom   4 (Pb ), wfc  1 (l=0 m= 1)
     ...
     state #  28: atom   5 (O  ), wfc  1 (l=0 m= 1)
     ...
[hzw@localhost pdos]$
```

（本例共 35 条 state，完整清单见 projwfc.out。）归纳成元素×轨道：

```text
Hf : s + p + d
Cl : s + p
Pb : s + p + d
O  : s + p
```

### 怎么归并：同元素同轨道求和

画轨道分辨图时，把同一元素同一 l 的各 m 分量（即同名 `pdos_atm#N(元素)_wfc#M(l)` 系列文件）求和。本例最值得关注的四组：

```text
Hf-d
Pb-p
O-p
Cl-p
```

理由：如果费米能级附近存在有限 DOS，这几组通常最有解释价值——Hf-d/Pb-p 是金属阳离子的主导价道，O-p/Cl-p 是阴离子配位道，实际权重需从文件读出；轨道权重本身不能直接给出电声耦合强度。

### 判读：E_F 附近的投影数值

总 DOS 与总投影的对照取 pdos_tot 在 E_F 最近的点：

```bash
[hzw@localhost pdos]$ awk '
> BEGIN { EF=0.050; best=1e9 }
> $1 !~ /^#/ {
>     d=$1-EF
>     if(d<0)d=-d
>     if(d<best){ best=d; line=$0 }
> }
> END { print line }
> ' HfCl2_PbO2.pdos_tot
   0.050  0.189E+01  0.184E+01
[hzw@localhost pdos]$
```

第三列就是投影求和后的 pdos(E)。本例两列应读作 1.89 与 1.84；两者在这个能量点相差约 3%，但不证明整个能量窗口内的投影完备。具体到每个元素/轨道在 E_F 附近的占比，把上面对应 pdos_atm 文件在 E=0.050 行的第二列读出来相加即可（本例文件齐全，逐文件读数过程不再展开）。

### 三条对齐纪律

1. **能量零点**：统一 E − E_F = 0（本例 E_F = 0.050 eV，与 dos.x 头部标注一致）；
2. **展宽固定**：所有 pdos 文件来自同一 projwfc.in（degauss=0.0037 Ry），跨计算对比时展宽必须一致；
3. **wfc 编号不跨体系硬对齐**：`wfc#M` 与 `l` 的对应关系以本体系 `grep "state #"` 输出为准，换赝势或换体系后编号会变。

### 下一步

轨道分辨的 PDOS 证据与能带放在一起才完整： bands → bands.x 出色散后，把轨道权重按元素叠加到能带图上；这一步还需要路径上逐 k、逐带的投影数据。本页已有的能量分辨 PDOS 不能充当这些权重：

```text
均匀网格 NSCF → projwfc.x → 能量分辨 PDOS（本页）
路径 bands → 路径上的逐带投影 → 胖带（另需数据）
```
