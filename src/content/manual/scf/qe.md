## 需要 / 产出

- 前置：应变/形变目录结构已就绪，各目录配有 scf 输入（本例 pw.x 输入为 pwx.in）。
- 产出：各目录自洽结果与能量表——最终迭代总能量（`! total energy` 行）、费米能级 E_F、以及跨应变的能量-应变对照表。
- 参考体系：nat = 6（Sc2C 单层），`K_POINTS automatic` 网格。

## 本步与相邻步骤不同之处

- scf 是一切后处理（bands、dos、pdos）的地基：后续链都以「scf 输出有 `JOB DONE` 且 `!` 总能量行存在」为验收门槛。
- 应变扫描中 scf 输入完全相同，仅结构（CELL/坐标）随弛豫输出更新；因此验收脚本可以跨目录复用。

## 参数（只列本步）

- 输入文件片段（ELECTRONS 段）：`conv_thr = 1.0000000000d-12`、`mixing_beta = 4.0000000000d-01`。
- 体系片段：`ibrav = 0, nat = 6, ntyp = 4, ecutwfc = 100, ecutrho = 800`，vdw-DF3-opt1。
- 完整的 `&CONTROL`/`&SYSTEM` pw.x 输入模板待填充（教程只给出片段，禁止凭空补全）。

## 命令与输出

批量验收：逐目录判 DONE/WAIT 并抽能量行（命令与输出原样）：

```bash
for d in tensile/001 tensile/002 compress/001 compress/002 compress/003; do
  f="$d/pwx.out"
  if grep -q "JOB DONE" "$f" 2>/dev/null; then st=DONE; else st=WAIT; fi
  echo "[$st] $f"
  grep -E "total energy|highest occupied|JOB DONE" "$f" | tail -n 5
done
```

输出节选（`!` 开头即自洽最终能量）：

```text
[DONE] tensile/001/pwx.out
     total energy              =    -208.22938097 Ry
!    total energy              =    -208.22938097 Ry
   JOB DONE.
[DONE] tensile/002/pwx.out
!    total energy              =    -208.22814362 Ry
[DONE] compress/001/pwx.out
!    total energy              =    -208.22929538 Ry
```

全目录作业状态盘点（DONE / ERROR / RUNNING 三分类）：

```bash
find . -name '*.out' | while read -r f; do
  if grep -q "JOB DONE" "$f" 2>/dev/null; then
    st="DONE"
  elif grep -qiE "Error|CRASH|stopped" "$f" 2>/dev/null; then
    st="ERROR"
  else
    st="RUNNING/INCOMPLETE"
  fi
  calc=$(grep -m1 -E "calculation\s*=" "$f" 2>/dev/null | head -1)
  echo "[$st] $f $calc"
done
```

## 后处理

- 能量-应变表：直接汇总各目录 `!` 行总能量（Ry），如上例 tensile/001 −208.22938097、tensile/002 −208.22814362、compress/001 −208.22929538，用于比较形变能量代价。
- 费米能级提取（作图零点）：

```bash
for d in compress/00{3,2,1} tensile/00{1,0015,2,3}; do
  ef=$(grep "the Fermi energy is" $d/scf/pwx.out | tail -n 1 | awk '{print $(NF-1)}')
  echo -e "$d\t E_F = $ef eV"
done
```

## 失败与假阳性

- 只有 `total energy`（不带 `!`）而最后没有 `! total energy` 行：说明自洽尚未收敛到判据，数据不能进能量表。
- `convergence NOT achieved` 关键字出现在输出中即 FAIL（验收 grep 应包含它）。
- 状态分类里 `RUNNING/INCOMPLETE` 不等于崩溃：可能是排队中被杀或仍在写，先看作业状态再决定重投。

## 可选脚本 + 检查清单

能量行快速汇总：

```bash
grep -E "total energy|highest occupied|JOB DONE" $d/pwx.out | tail -n 5
```

检查清单：
- [ ] 每个目录 `pwx.out` 含 `JOB DONE.`。
- [ ] 每个目录有 `!` 前缀的最终总能量行。
- [ ] 输出无 `convergence NOT achieved`。
- [ ] E_F 已批量提取并登记（后续 DOS/能带零点）。
- [ ] 能量-应变表注明统一收敛判据（conv_thr）与 k 网格。
