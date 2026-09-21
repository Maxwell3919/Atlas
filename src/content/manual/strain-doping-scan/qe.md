## 需要 / 产出

目标：扫面内应变 ±1–3%（tensile/compress 各 001–003），每个应变重复"弛豫 → SCF → 能带 → 电声"全链。起点只有一个无应变弛豫胞，其余目录全部由它复制改造。

## 本步与相邻步骤不同之处

本步的独特操作是"造目录"：整套复制既有目录，再 sed 替换晶胞数字。形变体系弛豫用 relax（锁胞，只动原子内坐标），不用 vc-relax；只有无应变参考体系才用 vc-relax。真空方向 c=40 永远不动。

## 参数（只列本步）

无应变面内格矢（vc-relax 后实录）：

```
3.312897589 0.000000000 0.000000000
-1.656448795 2.869053472 0.000000000
0.000000000 0.000000000 40.000000000
```

拉伸 3% 即面内矢量乘 1.030000（3.412284517 / 3.312897589 = 1.030000）；压缩 3% 乘 0.97：

```
3.213510661 0.000000000 0.000000000
-1.606755331 2.782981868 0.000000000
0.000000000 0.000000000 40.000000000
```

原子起步用无应变分数坐标；rx 收敛后再把新 z 写回后续 pwx/bands/ph* 输入。

## 命令与输出

建压缩 3% 目录（整套复制输入与 slurm，再只改晶胞三个数；替换串只含面内数字，c=40 不会被误改）：

```bash
mkdir -p compress
rm -rf compress/003
cp -a tensile/003 compress/003
find compress/003 -name '*.in' -exec grep -l '3.412284517' {} \; | while read f; do
  sed -i \
    -e 's/3.412284517/3.213510661/g' \
    -e 's/-1.706142258/-1.606755331/g' \
    -e 's/2.955125076/2.782981868/g' \
    "$f"
done
```

五套 SCF 的应变–能量表（32×32，取 `! total energy` 行）：

```
compress/003   -208.225061 Ry
compress/002   -208.227747 Ry
compress/001   -208.229295 Ry
tensile/001    -208.229381 Ry
tensile/002    -208.228144 Ry
```

±1% 最低、压到 −3% 上升最明显——能量随应变的形状合理。

## 后处理

每个应变目录先验收 rx → pwx → bands → bandspp，再进电声目录重跑整套 `pwx → pwxall → phx 四段 → q2r → matdyn → lambdax`（脚本见下）。一次只推一个应变目录；能量表先确认应变方向单调合理，再进入跨应变的 Tc 对比。

## 失败与假阳性

- 批量 sed 改 .slurm 核数时会吃掉重定向：`mpirun -np <np> <qe_bin>/pw.x<pwxall.in>pwxall.out` 变成 `<qe_bin>/pw.xpwxall.out`，pw.x 拿不到输入直接跑错。用 `cat -A` 看 `<>` 是否还在；统一修回 `pw.x<pwxall.in>pwxall.out` 形态后再提交，改完 `grep mpirun` 复核。
- 别在 tensile/003 里原地改来改去：压缩等新应变一律新建目录，保住原始 tensile/003。
- sed 前先 `grep -l` 确认命中文件，防止对不含该数字的文件空跑或误伤。

## 可选脚本 + 检查清单

```bash
# 批量改核数（数值按机器填，phx1+phx2+phx3 之和≈满配核数，三个可并行）
fix_np() {
  d="$1"
  setnp() { # $1=file $2=np
    f="$d/$1"; [ -f "$f" ] || return
    sed -i -E \
      -e "s/mpirun[[:space:]]+-np[[:space:]]+[0-9]+/mpirun -np $2/" \
      -e "s/^(#SBATCH[[:space:]]+-n[[:space:]]+)[0-9]+/\1$2/" \
      -e "s/^(#SBATCH[[:space:]]+--ntasks=)[0-9]+/\1$2/" \
      "$f"
    echo -n "$f "; grep -E 'mpirun -np|#SBATCH -n' "$f"
  }
  setnp pwxall.slurm <np>; setnp pwx.slurm <np>; setnp phx.slurm <np>
  setnp phx1.slurm <np_s>; setnp phx2.slurm <np_s>; setnp phx3.slurm <np_m>
}

# 按依赖链提交某电声目录全流程（一次只交一个目录）
sub_epc() {
  d="$1"; cd "$d" || return
  j1=$(sbatch --parsable pwxall.slurm)
  j2=$(sbatch --parsable --dependency=afterok:$j1 pwx.slurm)
  j3=$(sbatch --parsable --dependency=afterok:$j2 phx.slurm)
  j4=$(sbatch --parsable --dependency=afterok:$j3 phx1.slurm)
  j5=$(sbatch --parsable --dependency=afterok:$j3 phx2.slurm)
  j6=$(sbatch --parsable --dependency=afterok:$j3 phx3.slurm)
  echo "$d: pwxall $j1, pwx $j2, phx $j3, phx1/2/3 $j4/$j5/$j6"
  cd - >/dev/null
}
```

清单：

- [ ] 每个应变目录由 `cp -a` 整套复制而来，原始 tensile/003 未被动过
- [ ] 晶胞三个数替换后已 grep 复核，c=40 未变
- [ ] 形变目录 rx 用 relax 锁胞，无应变才 vc-relax
- [ ] 每套 SCF 能量已收表，应变–能量形状单调合理
- [ ] `grep mpirun` 确认重定向 `<...in>...out` 完整后再提交
- [ ] 一次只 sub_epc 一个目录，q2r 之后三步在六段全 DONE 后再交
