## 需要 / 产出

前置：`ph.x` 已带电声开关跑完，电声目录里有 `elph_dir/elph.inp_lambda.1`–`.10` 与 `elph.gamma.1`–`.10`，`q2r` 已产出力常数。本步只跑后处理程序 `lambda.x`：输入 `lambdax.in`，产出 `lambdax.out`（逐展宽档一行 λ、ω_log、T_c）与 `alpha2F.dat`（α²F(ω) 谱数据）。

## 本步与相邻步骤不同之处

声子与电声矩阵由 `ph.x` 写出（见 DFPT 声子一章），本步不重跑任何 `pw.x`/`ph.x`，只消费 `elph_dir/`。改 μ* 或展宽只需改 `lambdax.in` 再重提 `lambdax.slurm`，分钟级完成。若 α²F 全是 NaN，根因多半在 Γ 点负 w²，诊断与修复见"虚频诊断"一章，本章只管重跑后的读数。

## 参数（只列本步）

`lambdax.in` 第一行三列：emax（THz，必须高于最高声子频率）、degaussq（THz）、ngaussq。本体系最高支约 465 cm⁻¹ ≈ 13.9 THz，所以 emax 从 10 提到 18。中间是 q 点与权重（`kpoints.x` 生成），随后是与 q 点顺序一一对应的 elph 文件名，最后一行是 μ*，本例 0.1。注意目录名后缀 `.1`（如 ph64.1）不是应变，而是 `el_ph_sigma` 0.002 → 0.0002 的另一套参数。

## 命令与输出

`lambdax.in` 全文（中间省略 8 行同名文件）：

```
10 0.12 1 ! emax (something more than highest phonon mode in THz), degauss, smearing method
10 ! Number of q-points for which EPC is calculated,
0.00000000 0.00000000 0.00000000 1.00 ! the first q-point, use kpoints.x program to calculate
0.00000000 0.14433757 0.00000000 6.00 ! q-points and their weight
...
0.25000000 0.57735027 0.00000000 6.00 ! the last q-point
elph_dir/elph.inp_lambda.1 ! elph output file names,
...                        ! in the same order as the q-points before
elph_dir/elph.inp_lambda.10
0.1 ! \mu the Coloumb coefficient in the modified
    ! Allen-Dynes formula for T_c (via \omega_log)
```

置零负 w² 重跑后的结果表：

```
lambda omega_log T_c
1.06825 327.576 25.148
0.60974 330.310 7.928
0.49961 337.772 4.093
...
0.32075 327.181 0.292
0.31590 327.102 0.256
0.31152 327.218 0.226
```

## 后处理

读表三原则：

1. 不要用 degauss≈0 的第一档（λ=1.07、N(Ef)=38），那是未收敛的 δ 函数采样。
2. 取 λ 与 N(Ef) 随 degauss 变平的档，本体系稳定在 λ≈0.31–0.36。
3. μ* 只改最后一行，0.10 与 0.13 并排报告，不必重跑 ph。

α²F 在 `alpha2F.dat`：首行是各展宽档，之后每行 `E(THz)` + 各档谱值，直接可画。逐模分解看 `lambdax.out` 里的 `lambda(N)=… gamma=…GHz` 块（Γ 光学支在极小展宽下虚高，见失败节）。

## 失败与假阳性

- α²F 全 NaN：Γ 点 −20.9 cm⁻¹ 的 ASR 残余使 `elph.inp_lambda.1` 里 w² 为负，`sqrt(w²)` 得 NaN 污染整张表；λ 列却照常打印（`lambda = 1.068245 ( NaN ) = NaN K`），"λ 有数"≠结果健康。修法：备份 `elph_dir` 后把负 w² 置零重跑。
- `lambda.x` 不写 JOB DONE，盘点脚本会长期把它标成 RUNNING/INCOMPLETE——末尾有 λ/ω_log/Tc 三列表即已完成，属假阳性。
- q→0 光学支发散：极小展宽下 lambda(7)=3.6、gamma=9215 GHz，这是 QE 用户指南明确警告的行为；展宽增大后降到 0.5 左右，以收敛档为准。

## 可选脚本 + 检查清单

```bash
# 1) 扫全部 q，确认负 w² 只在 Γ
for f in elph_dir/elph.inp_lambda.*; do
  echo "==== $f ===="
  awk 'NR==2 || NR==3 {
    for(i=1;i<=NF;i++) if($i+0<0) printf " neg w2[%d]=%s\n", i, $i
  }' "$f"
done

# 2) 备份后把第 2、3 行的负 w² 置零，重跑 lambda.x
cp -a elph_dir elph_dir.bak_w2
for f in elph_dir/elph.inp_lambda.*; do
  awk 'NR==2 || NR==3 {
    for(i=1;i<=NF;i++) if($i+0<0) $i=sprintf("%.6E", 0.0)
    print; next
  } { print }' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done
sbatch lambdax.slurm

# 3) 验收：不再有 NaN，ω_log 是有限 K
grep -A25 'lambda omega_log' lambdax.out
awk 'NR>2 && $2+0==$2 {c++} END{print "numeric a2F rows:", c+0}' alpha2F.dat
```

清单：

- [ ] `elph.inp_lambda.N` 文件数与 q 点数一致（本例 10）
- [ ] emax 大于最高声子频率（≈13.9 THz，取 18）
- [ ] α²F 无 NaN，ω_log 为有限值
- [ ] T_c 取自 λ、N(Ef) 变平的展宽档，弃第一档
- [ ] 负 w² 只出现在 Γ，其余 q 干净
- [ ] μ*=0.10/0.13 两档并排报告
