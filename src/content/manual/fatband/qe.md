## 需要 / 产出

- 前置：已完成 dos 链的 scf + projwfc.x（同 `pdos/` 目录、同 `&PROJWFC` 设置）。
- 产出：分原子分轨道的投影态密度文件（`zrclscc.pdos_atm#N(元素)_wfc#M(轨道)`），作为轨道分辨（fatband 风格）分析的作图数据源。

## 本步与相邻步骤不同之处

- 与总 dos 的差别：dos 步只看 `pdos_tot`；fatband 分析进一步落到 `pdos_atm#N_wfc#M` 级别，按原子（Zr/Sc/C/Cl）与轨道（s/p/d）拆分权重。
- 与 bands 步的差别：bands 给出色散但无轨道信息；projwfc.x 的投影把「哪条带来自哪个原子哪个轨道」定量化，两者叠加即通常所说的 fatband 图。
- 输入与 dos 步完全相同（同一 `pdos.in`），区别只在后处理读哪组文件。

## 参数（只列本步）

与 dos 步共用同一 `&PROJWFC` 输入（节选）：

```fortran
&PROJWFC
 outdir = './out/'
 prefix = 'zrclscc'
 ngauss=0, degauss = 2.2d-3
 DeltaE=0.005
 lsym=.true.
 filpdos='zrclscc',
 filproj='zrclscc',
/
```

## 命令与输出

运行命令与 dos 步相同：scf 完成（`JOB DONE`）后执行 `projwfc.x < pdos.in > pdos.out`。本例（nat=6）投影文件按原子×轨道展开（节选）：

```text
zrclscc.pdos_atm#1(Zr)_wfc#5(d)   # Zr 4d
zrclscc.pdos_atm#2(C)_wfc#2(p)    # C 2p
zrclscc.pdos_atm#3(Cl)_wfc#2(p)   # Cl 3p
zrclscc.pdos_atm#5(Sc)_wfc#4(d)   # Sc 3d
```

每个文件为能量格点上的分轨道 ldos 列，读取方式与 `pdos_tot` 一致。

## 后处理

- 作图以 E − E_F = 0 为零点，E_F 取同目录 scf 输出：

```bash
ef=$(grep "the Fermi energy is" $d/pdos/pwx.out | tail -n 1 | awk '{print $(NF-1)}')
```

- 把同一元素的 `pdos_atm#N` 文件按轨道求和后叠加到能带/总 DOS 图上，即可判断费米面附近的轨道归属。
- 费米面附近轨道成分对比建议固定展宽（degauss）与能量窗，只变应变目录。

## 失败与假阳性

- `lsym=.true.` 且低对称体系下投影可能按对称性合并；若需要逐原子严格拆分，注意核对 `pdos.out` 中的投影计数是否与 nat 一致。
- 投影文件的 wfc 编号与赝势的价道有关，换赝势后编号会变，不能跨体系按编号硬对齐。
- k 加密网格不一致时，不同应变的轨道权重不可直接对比。

## 可选脚本 + 检查清单

轨道分辨数据就位检查：

```bash
ls $d/pdos/zrclscc.pdos_atm#* | wc -l   # 应覆盖 6 个原子的全部价道
grep -H "JOB DONE" $d/pdos/pwx.out $d/pdos/pdos.out
```

检查清单：
- [ ] 全部 `pdos_atm#N(元素)_wfc#M` 文件生成且非空（Zr/Sc/C/Cl 各元素齐全）。
- [ ] E_F 已从同目录 scf 输出提取，作图零点统一。
- [ ] 各应变间 PROJWFC 参数与 k 网格逐项一致。
- [ ] 对比图上注明元素/轨道与所用展宽。
- [ ] 能带分解权重（k 分辨 fatband）作图方法待填充。
