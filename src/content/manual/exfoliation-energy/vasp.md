参考：

- VASP wiki INCAR 标签总表：<https://www.vasp.at/wiki/index.php/Category:All_INCAR_Tags>

## 剥离能 E(d)

把多层 slab 的顶层逐次整体抬高、只做固定结构的单点 SCF，得到能量随层间距 d 的曲线 E(d)；曲线在高 d 处进入渐近平台，平台值减去平衡能量就是剥离能。本方案的核心纪律：scf_eq 与 scf_d1…d20 共享同一份 INCAR，只改 POSCAR 里的层间距——任何参数差异都会直接污染能量差。

记录体系：HfI2 slab（12 I + 6 Hf = 18 原子，6 个 I-Hf-I 层），a ≈ 3.8018 Å，c ≈ 86.6518 Å。全套算例：relax + scf_eq + scf_d1…d20 + submit_all_scf.sh + submitted_jobs.tsv。

### E(d) 方案与结构来源

relax 目录先做结构优化（IBRION = 2、NSW = 200，ISIF = 2 固定晶胞只弛豫原子），得到层间平衡几何；scf_eq 是平衡态单点；scf_dN 把顶层（第 6 层 I-Hf-I）整体上移 N×1.00 Å，其余 17 个原子坐标不动。真空约 40 Å，足够容纳 +20 Å 的位移而不与周期镜像相互作用。

### relax INCAR

```bash
[<user>@<cluster> exf]$ cat relax/INCAR
SYSTEM = HfI2_relax
   LREAL = A
   LASPH = T
   LCORR = T
   LORBIT = 11
   LWAVE = F
   LCHARG = T
   ISIF = 2
   IBRION = 2
   NSW = 200
   EDIFFG = -0.01
   ENCUT = 520
   GGA = PE
   VOSKOWN = 1
   EDIFF = 1E-6
   NELMIN = 4
   NELM = 60
   AMIX = 0.1
   BMIX = 0.0001
   AMIX_MAG = 0.4
   BMIX_MAG = 0.0001
   MAXMIX = 80
   LMAXMIX = 4
   IVDW = 11
   ALGO = Fast
   PREC = Normal
   ISMEAR = 0
   SIGMA = 0.05
```

### scf 系列 INCAR（21 个作业同一份）

```bash
[<user>@<cluster> exf]$ cat scf_eq/INCAR
SYSTEM = SnS2
   LPLANE = .TRUE.
   NPAR = 4
   NSIM = 4
   ISTART = 0
   LWAVE = F
   LCHARG = T
   LCORR = T
   LREAL = A
   LASPH = T
   LORBIT = 11
   ISIF = 2
   IBRION = -1
   ENCUT = 400
   GGA = PE
   VOSKOWN = 1
   EDIFF = 1E-6
   NELMIN = 4
   NELM = 160
   AMIX = 0.1
   BMIX = 0.0001
   AMIX_MAG = 0.4
   BMIX_MAG = 0.0001
   MAXMIX = 80
   LMAXMIX = 4
   IVDW = 11
   ALGO = N
   PREC = Accurate
   ISMEAR = 0
   SIGMA = 0.05
```

（真实文件是带全套注释的模板；此处给出等价的去注释版。）

两处模板陷阱判读：一是 SYSTEM = SnS2——从别的体系复制模板时忘了改标题；SYSTEM 不进物理，但归档检索会把 HfI2 认成 SnS2，复制模板要改 SYSTEM。二是 ENCUT = 400 与 relax 的 520 不一致（PREC 也从 Normal 变 Accurate）：21 个 E(d) 作业内部参数完全一致，能量**差**可用；但若把 E_eq 直接与其它 ENCUT = 520 的计算相减，截断能差异会引入系统误差——跨计算比较能量前先统一参数。

### 同 INCAR 核验与坐标核验

scf 系列逐字节一致性（diff 无输出即相同）：

```bash
[<user>@<cluster> exf]$ for n in 1 8 15 20; do diff scf_eq/INCAR scf_d$n/INCAR > /dev/null && echo "scf_d$n: INCAR identical"; done
scf_d1: INCAR identical
scf_d8: INCAR identical
scf_d15: INCAR identical
scf_d20: INCAR identical
```

顶层位移核对——POSCAR 第 19 行是顶层内侧 I 的 z 分数坐标：

```bash
[<user>@<cluster> exf]$ for d in scf_eq scf_d1 scf_d10 scf_d20; do echo "== $d =="; sed -n '19p' $d/POSCAR; done
== scf_eq ==
  0.6666666670000012  0.3333333329999988  0.4915434728751257
== scf_d1 ==
  0.6666666670000012  0.3333333329999988  0.5030839150891475
== scf_d10 ==
  0.6666666670000012  0.3333333329999988  0.6069478950153439
== scf_d20 ==
  0.6666666670000012  0.3333333329999988  0.7223523171555620
```

判读：z×86.6518 Å = 42.587 → 43.587 → 52.587 → 62.587 Å，即每个 scf_dN 把顶层再上移 N×1.000 Å（d1/d10/d20 三个检查点验证）；scf_eq 的顶层间隙 = 0.491543 − 0.450334 = 0.041209 分数 ≈ 3.57 Å（平衡 vdW 间隙）。

### 批量提交

```bash
[<user>@<cluster> exf]$ head -5 submitted_jobs.tsv
dir	jobid	dependency
scf_eq	16554	none
scf_d1	16555	none
scf_d2	16556	none
scf_d3	16557	none
```

submit_all_scf.sh 一次排队 scf_eq 与 d1…d20 共 21 个作业，TSV 记录 jobid 对账。

### 能量提取与 E(d) 表

```bash
[<user>@<cluster> exf]$ grep "energy  without entropy" scf_eq/OUTCAR | tail -1
  energy  without entropy=     -111.23310238  energy(sigma->0) =     -111.23310238
```

隔步取 11 点（每目录取 OUTCAR 最后一行 energy without entropy，单位 eV）：

| 目录 | 顶层位移 Δd (Å) | E (eV) | E − E_eq (meV) |
|------|----------------|--------|----------------|
| scf_eq  | 0  | −111.23310238 | 0     |
| scf_d2  | 2  | −111.07191478 | 161.19 |
| scf_d4  | 4  | −111.01334680 | 219.76 |
| scf_d6  | 6  | −110.99687336 | 236.23 |
| scf_d8  | 8  | −110.99053976 | 242.56 |
| scf_d10 | 10 | −110.98760066 | 245.50 |
| scf_d12 | 12 | −110.98601295 | 247.09 |
| scf_d14 | 14 | −110.98508993 | 248.01 |
| scf_d16 | 16 | −110.98458118 | 248.52 |
| scf_d18 | 18 | −110.98427886 | 248.82 |
| scf_d20 | 20 | −110.98414608 | 248.96 |

判据与结果：d15 → d20 能量变化 E(d20) − E(d15) = −110.98414608 − (−110.98481305) = 0.000667 eV ≈ 0.67 meV，曲线已进入渐近平台，取 d20 作渐近值；剥离能 E_exf = E(d20) − E(scf_eq) = 0.24896 eV ≈ 0.249 eV，除以 18 原子得 ≈ 13.8 meV/atom。对照文献量级：石墨层间结合能约 70 meV/atom 量级——HfI2 层间以 vdW 为主、明显更弱，数值上自洽。

### 参考体系配对

E(d) 渐近方案不需要额外参考体系：d→∞ 的平台就是"两片分离"参考态，且与结合态共用同一 INCAR 与网格，系统误差相消。若改用"单层 − 体相"式结合能，则需要单层与体相两个参考算例，配对逻辑要经得起推敲：记录中 HfCl2 一侧的参考算例，单层用 c ≈ 30 Å 并配 QE 的 assume_isolated = '2D' 二维库仑截断，4 层 slab 用 c ≈ 100 Å；而标记为 bulk 的目录实际只含 3 个原子（一个化学式单位）——对层状 vdW 晶体这不是可用的体相参考，参考目录的真实意图需与执行者核对后再用。

### 下一步

```text
vc-relax（relax/，IBRION = 2，层间平衡）
    ↓
E(d) 扫描：scf_eq + scf_d1…scf_d20     ← 本页
    ↓
E_exf ≈ 0.249 eV（≈ 13.8 meV/atom）
    ↓
层间耦合的电荷视角 → 差分电荷/Bader
    ↓
层间滑移与堆垛 → 声子与稳定性分析
```

一个提醒：E(d) 曲线在 d 增大初期变化很快，末段 10 Å 才挪 1 meV——判据看末两点的绝对增量（<1 meV），而不是看曲线"看起来平了"。
