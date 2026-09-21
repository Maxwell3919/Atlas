## 需要 / 产出

需要：弛豫好的结构与收敛参数结论（来自 relax / convergence 步）；电声目录下两套 SCF 输入——`pwx.in`（16×16 普通网格 SCF，可选）与 `pwxall.in`（密 k 网格 + `la2F=.true.`，必需）。两个 SCF 写同一个 `./out/`、同一个 `prefix='scc'`。

产出（沿用真实算例的文件命名）：

| 文件 | 内容 |
|---|---|
| `pwxall.out` / `pwx.out` | 密 k + la2F 与普通网格两次 SCF 的输出 |
| `phx.out`、`phx1/2/3.out` | ph.x 按 q 段的电声与动力学矩阵输出 |
| `elph.gamma.<n>` | ph.x 电声中间文件 |
| `scc.dyn*`、`scc.fc`、`scc.freq` | 动力学矩阵、力常数、频率 |
| `elph_dir/elph.inp_lambda.<iq>` | lambda.x 的逐 q 点输入（w2 与 λ(q,ν)） |
| `dyna2F`、`alpha2F.dat` | α²F(ω) 谱 |
| `lambdax.out` | λ–degauss 扫描表与 λ / ω_log / Tc 汇总 |
| `matdyn.modes`、`gam.lines`、`lambda.dat` | 频散模式、Γ 线数据、λ 数据 |

本算例网格：pwxall 密 k `64 64 1`（对比套件另有 `96 96 1`），ph q 网格 `8 8 1`（10 个不可约 q 点），`el_ph_sigma=0.0002`（早期目录为 `0.002`，两套目录以 `.1` 后缀区分）。

## 本步与相邻步骤不同之处

- 普通声子步骤（DFPT / 有限位移）只算力常数；本步在此基础上让 ph.x 输出逐模电声系数 λ(q,ν)，并额外要求一次 `la2F=.true.` 的密 k SCF。
- SCF 有两套输入：`pwx.in`（16×16）为声子准备 outdir；`pwxall.in` 用密 k（64×64×1 或 96×96×1）加 `la2F=.true.`。两者的分工与先后由提交链固定（见「命令与输出」）。
- 后处理走 QE 自带 lambda.x 的 McMillan 路线；与 Wannier90 插值路线（本手册另一方法）相比，这里不做最大局域化变换，直接从 `elph_dir/elph.inp_lambda.*` 读 w2 与 λ(q,ν)。
- 本步不改结构：`phx*.in`、`q2rx.in`、`lambdax.in` 都不读晶胞，换应变目录时无需改动。

## 参数（只列本步）

pwxall.in 的 k 网格（两套对比）：

```text
K_POINTS automatic
  64 64 1 0 0 0
```

```text
K_POINTS automatic
  96 96 1 0 0 0
```

q 网格写在 `scc.dyn0` 头两行（q 网格与不可约 q 点数）：

```text
   8   8   1
 10
```

phx*.in 中的电子展宽（与 pwxall 的 smearing 配套，`.1` 目录为细展宽版）：

```text
el_ph_sigma=0.0002
```

晶胞与原子坐标片段（拉伸 1% 算例，真空层 c = 40 Å；完整 &CONTROL/&SYSTEM 输入模板：待填充）：

```text
CELL_PARAMETERS (angstrom)
   3.346026565   0.000000000   0.000000000
  -1.673013283   2.897744007   0.000000000
   0.000000000   0.000000000  40.000000000
ATOMIC_POSITIONS (crystal)
Sc            0.3333333333        0.6666666667        0.4700343471
Sc            0.6666666667        0.3333333333        0.5299656529
C             0.0000000000        0.0000000000        0.5000000000
K_POINTS automatic
```

lambdax.in（lambda.x 输入）：首行三个数是 `emax(THz) degaussq(THz) ngaussq`，末行为 μ*（mustar）。算例终值：`emax=18`（须盖住最高声子支，本体系 ≈465 cm⁻¹ ≈ 13.9 THz）、`degaussq=0.12`、`ngaussq=1`、μ*=0.10，并复算 μ*=0.13 对比。

```text
18  0.12  1    ! emax THz > 13.9, degaussq THz, ngaussq
```

## 命令与输出

电声目录的提交链：pwxall → pwx → phx（q=1）→ phx1/2/3（q=2–4 / 5–7 / 8–10，依赖同一个 phx 任务，可并行；共用 `./out/` 与 `scc.dyn*` 时串行更稳）→ 之后人工依次交 q2rx → matdynxline → lambdax。`--parsable` + `--dependency=afterok` 把整条链挂到队列上：

```bash
sub_epc() {
  d="$1"
  cd "$d" || return
  j1=$(sbatch --parsable pwxall.slurm)
  j2=$(sbatch --parsable --dependency=afterok:$j1 pwx.slurm)
  j3=$(sbatch --parsable --dependency=afterok:$j2 phx.slurm)
  j4=$(sbatch --parsable --dependency=afterok:$j3 phx1.slurm)
  j5=$(sbatch --parsable --dependency=afterok:$j3 phx2.slurm)
  j6=$(sbatch --parsable --dependency=afterok:$j3 phx3.slurm)
  echo "$d"
  echo "  pwxall $j1"
  echo "  pwx    $j2  afterok:$j1"
  echo "  phx    $j3  afterok:$j2"
  echo "  phx1   $j4  afterok:$j3"
  echo "  phx2   $j5  afterok:$j3"
  echo "  phx3   $j6  afterok:$j3"
  cd - >/dev/null
}
```

提交后 `squeue -u $USER` 应看到首个任务 R、其余 `PD (Dependency)`。每步的 slurm 脚本形如（重定向写法 `pw.x<pwxall.in>pwxall.out` 是真实脚本的样式，丢失中间尖括号段是常见事故，见「失败与假阳性」）：

```bash
#!/bin/bash
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log
ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
cd $SLURM_SUBMIT_DIR
mpirun -np <n> <qe_bin>/pw.x<pwxall.in>pwxall.out
```

六个 `.out` 全部 `JOB DONE` 后再交 `q2rx.slurm`、`matdynxline.slurm`、`lambdax.slurm`。lambda.x 的输出分两段：随 degauss 扫描的 λ 行，与末尾 λ / ω_log / Tc 汇总表（ω_log 单位 K；下表摘自 μ*=0.10 的真实算例）：

```text
     lambda = 0.312769 (   0.224612 )  =  259.219 K  N(Ef)= 22.787828 at degauss= 0.002
     lambda = 0.287741 (   0.204623 )  =  259.350 K  N(Ef)= 21.586605 at degauss= 0.004
     lambda = 0.282486 (   0.199895 )  =  260.136 K  N(Ef)= 21.964204 at degauss= 0.006

lambda        omega_log          T_c
  0.31277       259.219              0.185
  0.28774       259.350              0.082
  0.28249       260.136              0.067
  0.28955       260.703              0.088
  0.29909       261.154              0.122
```

取值规则：λ 与 N(Ef) 随 degauss 出现平台的档位才可用（算例平台区 λ≈0.31–0.36）；degauss≈0 的首档（该算例中 λ=1.07、N(Ef)=38.4）是未收敛的采样，数值虚高，不能引用。

## 后处理

alpha2F 与汇总表的完整性检查：

```bash
grep -A25 'lambda        omega_log' lambdax.out
head -5 alpha2F.dat
awk 'NR>2 && $2+0==$2 {c++} END{print "numeric a2F rows:", c+0}' alpha2F.dat
```

`alpha2F.dat` 不应再出现整列 NaN；ω_log 应为有限值。Γ 点逐模数据看 `gam.lines` 与 `elph_dir/elph.inp_lambda.1`（每个模一行 `lambda(nu)= … gamma= …`）；频散与模式看 `matdyn.modes`、`matdynxline.out`。

Tc 引用规则：lambda.x 实现的是 Allen–Dynes / McMillan 估计，源码行即公式

```text
Tc = omegalog(i)/1.2 * exp(-1.04*(1+x)/(x-mustar*(1+0.62*x)))
```

报告时并排给出 μ*=0.10 与 0.13 两组（改 lambdax.in 末行即可，无需重跑 ph.x）。更高精度的官方层级是 lambda_tetra + alpha2f.x 或 EPW 各向异性 Eliashberg。

## 失败与假阳性

lambda.x 全表 NaN。症状：λ 值正常但括号内 ω_log 与 Tc 列全为 NaN，`alpha2F.dat` 整表损坏：

```text
     lambda = 1.068245 (        NaN )  =      NaN K  N(Ef)= 38.378850 at degauss= 0.000

lambda        omega_log          T_c
  1.06825           NaN                NaN
```

根因：Γ 点声学支 w2<0（对应 dyn 文件中 −20.9 cm⁻¹ 的虚频模），lambda.x 计算 `omega=sqrt(w2)*3289.828`（Ry^1/2→THz）时开方得 NaN，污染整张 α²F。先扫全部 q 确认负 w2 只在 Γ：

```bash
for f in elph_dir/elph.inp_lambda.*; do
  echo "==== $f ===="
  # 第2、3行是 9 个 w2（与 nmodes=9 对应）
  awk 'NR==2 || NR==3 {
    for(i=1;i<=NF;i++) if($i+0<0) printf "  neg w2[%d]=%s\n", i, $i
  }' "$f"
done
```

处理：备份后把负 w2 置 0（声学支 λ 本已是 0，几乎只救 ω_log），再把 emax 提到盖住最高声子支（10 → 18 THz），重跑 `sbatch lambdax.slurm`：

```bash
cp -a elph_dir elph_dir.bak_w2

for f in elph_dir/elph.inp_lambda.*; do
  awk 'NR==2 || NR==3 {
    for(i=1;i<=NF;i++) if($i+0<0) $i=sprintf("%.6E", 0.0)
    print
    next
  } { print }' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done

# 确认 Γ 已改掉
awk 'NR<=3{print}' elph_dir/elph.inp_lambda.1
```

Γ 点小负频 ≠ 结构不稳定。Γ 声学支的微量负 w2（算例中 −3.6×10⁻⁷ 量级）来自 ASR 残差与近 Γ 采样噪声，母体算例同样存在；应变后未出现新的成片软模，说明结构仍稳定。真正要警惕的是新出现的、成片的大虚频。另一假阳性：极小展宽下 Γ 光学支 λ 被放大（算例 lambda(7)=3.6、gamma=9215 GHz），这是官方指南对 q→0 光学支贡献发散的已知警告，展宽增大后回落到 0.5 量级，应以收敛档为准。

sed 批量替换弄丢重定向。批量改核数时 `<pwxall.in>` 被误删，命令行变成 `pw.xpwxall.out`（pw.x 直接把 pwxall.out 当参数）。用 `cat -A` 与 `grep mpirun` 检查每个 slurm 脚本，确认重定向段完整：

```bash
grep mpirun pwxall.slurm
cat -A pwxall.slurm | tail -n 5
```

确认已损坏时，先取消队列中的作业再统一修复：

```bash
squeue -u $USER -h -o %i | xargs -r scancel

sed -i \
  -e 's|bin/pw.xpwxall.out|bin/pw.x<pwxall.in>pwxall.out|' \
  -e 's|bin/pw.xpwx.out|bin/pw.x<pwx.in>pwx.out|' \
  -e 's|bin/ph.xphx.out|bin/ph.x<phx.in>phx.out|' \
  -e 's|bin/ph.xphx1.out|bin/ph.x<phx1.in>phx1.out|' \
  -e 's|bin/ph.xphx2.out|bin/ph.x<phx2.in>phx2.out|' \
  -e 's|bin/ph.xphx3.out|bin/ph.x<phx3.in>phx3.out|' \
  ./*.slurm
```

边界提示：lambda.x 没有 asr 关键字，它只读 `elph.inp_lambda.*` 里的 w2 与 λ(q,ν)，不会使用 q2r/matdyn 的 ASR 处理结果；其 Tc 也只是 McMillan 估计，不是各向异性 Eliashberg 结果。

## 可选脚本 + 检查清单

状态巡检函数（六个输出文件逐一判 DONE / ERROR / RUN）：

```bash
chk_epc() {
  d="$1"
  echo "==== $d ===="
  for f in pwxall.out pwx.out phx.out phx1.out phx2.out phx3.out
  do
    p="$d/$f"
    if [ ! -f "$p" ]; then echo "[NO OUT] $f"; continue; fi
    if grep -q "JOB DONE" "$p"; then st=DONE
    elif grep -qiE "Error|CRASH|stopped" "$p"; then st=ERROR
    else st=RUN/INCOMPLETE
    fi
    echo "[$st] $f"
  done
}
```

检查清单：

- 六个 `.out` 全部 `JOB DONE` 后才提交 q2rx → matdynxline → lambdax。
- `alpha2F.dat` 无 NaN 行、`lambdax.out` 的 ω_log / Tc 列为有限值。
- 负 w2 扫描只允许出现在 Γ 附近的声学支；出现成片新软模时先停下判断结构稳定性。
- `emax` 大于最高声子频率（本体系 13.9 THz → 取 18 THz）。
- 引用的 λ / Tc 来自 degauss 平台档，不取 degauss≈0 的首档。
- μ*=0.10 与 0.13 两组结果并排报告；结论注明 lambda.x 为 McMillan 估计。
