## 需要 / 产出

- 前置：应变目录结构已就绪（与能带链同一套形变子目录）。
- 产出：各应变 `pdos/` 目录下自洽 + 投影态密度：总态密度 `zrclscc.pdos_tot` 与分原子分轨道文件 `zrclscc.pdos_atm#N(元素)_wfc#M(轨道)`。
- 参考体系：nat = 6, ntyp = 4（Zr, Cl, Sc, C），prefix = 'zrclscc'，outdir = './out/'。

## 本步与相邻步骤不同之处

- dos 链在独立的 `pdos/` 目录执行：`pw.x < pwx.in`（自洽或加密 k 网格非自洽）→ `projwfc.x < pdos.in`（提取 PDOS/LDOS），与能带链（`scf/` 目录 scf→bands→bands.x）分开维护。
- 与 bands 步的差别：bands 沿高对称路径解本征值；dos 用稠密 k 网格 + projwfc.x 投影，输出能量网格上的态密度。
- 关键纪律：不同形变下所有输入参数（截断、泛函、赝势、smearing、k 网格、PROJWFC 设置）完全保持不变，唯一更新的是对应形变弛豫后的 `CELL_PARAMETERS` 与 `ATOMIC_POSITIONS`。

## 参数（只列本步）

`head -n 25 pdos.in` 原样内容：

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

- `degauss = 2.2d-3`（Ry）与 scf 的 smearing 取同一套展宽；`DeltaE=0.005` 控制输出能量格点步长。

## 命令与输出

每目录两步，`JOB DONE` 门控（批处理节选）：

```bash
$PW_CMD < pwx.in > pwx.out 2>&1
if grep -q "JOB DONE" pwx.out; then
    echo "[ ${d} ] 2/2: Running projwfc.x..."
    $PROJ_CMD < pdos.in > pdos.out 2>&1
    echo "[ ${d} ] 态密度计算全部完成！"
fi
```

本例（nat=6）生成的分波文件清单（节选）：

```text
zrclscc.pdos_atm#1(Zr)_wfc#1(s) ... wfc#5(d)
zrclscc.pdos_atm#2(C)_wfc#1(s)  ... wfc#2(p)
zrclscc.pdos_atm#3(Cl)_wfc#1(s) ... wfc#2(p)
zrclscc.pdos_atm#5(Sc)_wfc#1(s) ... wfc#4(d)
```

## 后处理

- PDOS 作图必须以费米能为零点（E − E_F = 0 eV），E_F 取自 scf 输出：

```bash
ef=$(grep "the Fermi energy is" $d/pdos/pwx.out | tail -n 1 | awk '{print $(NF-1)}')
```

- N(E_F)：从 `zrclscc.pdos_tot` 中取 E ≈ E_F 行的 DOS 列读数，用于对比各应变费米面附近态密度变化。
- 完整性检查（两目录五个输出都要有 `JOB DONE`）：

```bash
for d in compress/00{1,2,3} tensile/00{1,0015,2,3}; do
  echo "=== 检查 $d ==="
  grep -H "JOB DONE" $d/pdos/pwx.out $d/pdos/pdos.out 2>/dev/null
done
```

## 失败与假阳性

- `pdos.out` 无 `JOB DONE`：projwfc.x 未完成或中途崩溃，数据不可用于作图，先查错误再重投。
- E_F 取错文件：能带零点必须取同体系同参数 scf 输出的费米能级，混用不同应变的 E_F 会造成态密度整体错位。
- 各应变的 degauss/DeltaE 若不一致，pdos_tot 之间的对比失去意义——属于假阳性差异。

## 可选脚本 + 检查清单

批量 N(E_F) 零点表（配合 E_F 提取循环使用）：

```bash
for d in compress/00{3,2,1} tensile/00{1,0015,2,3}; do
  ef=$(grep "the Fermi energy is" $d/pdos/pwx.out | tail -n 1 | awk '{print $(NF-1)}')
  echo -e "$d\t E_F = $ef eV"
done
```

检查清单：
- [ ] `pdos/pwx.out` 与 `pdos/pdos.out` 均含 `JOB DONE`。
- [ ] `zrclscc.pdos_tot` 与全部 `pdos_atm#N_wfc#M` 文件已生成且非空。
- [ ] 各应变 PROJWFC 参数（degauss、DeltaE、lsym）逐项一致。
- [ ] 已记录各应变 E_F，作图统一以 E − E_F = 0 为零点。
- [ ] N(E_F) 读数来自 E ≈ E_F 行，并注明所用展宽。
