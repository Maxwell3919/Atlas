参考：

- QE 官方文档 INPUT_PH：<https://www.quantum-espresso.org/Doc/INPUT_PH.html>
- QE 官方文档 INPUT_Q2R：<https://www.quantum-espresso.org/Doc/INPUT_Q2R.html>
- QE 官方文档 INPUT_MATDYN：<https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html>
- PHonon 用户指南：<https://www.quantum-espresso.org/Doc/user_guide/>

## 本页目标

结构弛豫收敛后，用 DFPT 算完整声子谱：在 8×8×1 q 网格上逐 q 解析求动力常数，q2r.x 合并成力常数文件，matdyn.x 沿高对称路径内插色散。读完本页你能：分批准备并提交 ph.x、接上 q2r 与 matdyn、对每一步的产物与验收标志逐项核对。

## 前置

- vc-relax 已收敛，弛豫后结构与赝势就位；
- scf 已跑通（普通 32×32×1 网格即可；EPC 场景要换成 la2F 的密 k 自洽，见电声耦合页）。

## ph.x 输入（q=1 单独一批）

ph.x 输入只有 `&inputph` 一个 namelist——它从 scf 的输出目录读波函数与电荷，质量用 amass 单独给，不需要再写结构卡片：

```fortran
&inputph
  tr2_ph = 1.0d-16        ! 声子自洽收敛阈值，取得严一些
  nmix_ph = 12            ! 声子自洽混合步数
  verbosity = 'high'
  prefix = '<prefix>'     ! 与 scf 完全一致，否则读不到波函数
  fildvscf = 'zrclsccdv'  ! 自洽变势文件前缀（EPC 链要用）
  amass(1) = 91.224       ! Zr，单位 amu，与 ATOMIC_SPECIES 一致
  amass(2) = 35.450       ! Cl
  amass(3) = 44.956       ! Sc
  amass(4) = 12.011       ! C
  outdir = './out/'
  fildyn = 'zrclscc.dyn'  ! 动力学矩阵输出前缀
  trans = .true.          ! 计算声子（含介电张量/Born 电荷，绝缘体自动给）
  ldisp = .true.          ! 用 nq1×nq2×nq3 网格自动铺 q 点
  start_q = 1
  last_q = 1              ! 本批只算 q=1（Γ 点）
  nq1 = 8
  nq2 = 8
  nq3 = 1
/
```

纯声子谱页不需要 `electron_phonon`/`el_ph_sigma`/`el_ph_nsigma` 三个键；要接电声链就照上面电声耦合页的写法加上。

## q 分批与提交

8×8×1 网格共有 10 个不等价 q 点。ph.x 按 `start_q/last_q` 切批，每批一个输入文件、各自 sbatch 并行：

| 文件 | start_q | last_q | 说明 |
|---|---|---|---|
| phx.in | 1 | 1 | Γ 点单独一批 |
| phx1.in | 2 | 4 | |
| phx2.in | 5 | 7 | |
| input_tmp.in | 8 | 10 | |

除 `start_q/last_q` 外四份文件逐字节相同（diff 核验过）。作业脚本就是常规写法：

```bash
#!/bin/bash
#SBATCH --job-name=phx1
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=<np>
#SBATCH --time=<时长>
mpirun -np <np> ph.x -i phx1.in > phx1.out
```

```bash
sbatch phx1.slurm
```

提交后 `squeue -u <user>` 确认排队。ph.x 是整条 DFPT 链里最耗时的环节，把 q 拆成四批并行是常规做法；批间无依赖，全部跑完才进 q2r。

## 验收与产物对号

每批跑完先查完成标志：

```bash
grep -l "JOB DONE" phx*.out
```

四份输出都应有命中。产物按前缀对号：

| 产物 | 来自 | 用途 |
|---|---|---|
| zrclscc.dyn0 | ph.x | q 点清单 |
| zrclscc.dyn1 … dyn10 | ph.x 各 q | 动力学矩阵 |
| zrclscc.fc | q2r.x | 合并后的力常数 |
| zrclscc.freq / .freq.gp | matdyn.x | 色散频率 |
| matdyn.modes | matdyn.x | 各 q 各支本矢 |

## q2r.x：合并力常数

所有 q 批 JOB DONE 之后：

```fortran
&input
  zasr = 'crystal'        ! 声学求和规则；消除 Γ 点小残差
  fildyn = 'zrclscc.dyn'
  flfrc = 'zrclscc.fc'
  la2F = .true.           ! 只在接电声链时保留
/
```

```bash
q2r.x -i q2rx.in > q2rx.out
```

成功标志：输出出现 `fft-check success`，并生成 `zrclscc.fc`。

## matdyn.x：沿路径内插色散

```fortran
&input
  asr = 'crystal'
  amass(1) = 91.224
  amass(2) = 35.450
  amass(3) = 44.956
  amass(4) = 12.011
  flfrc = 'zrclscc.fc'
  flfrq = 'zrclscc.freq'
  la2F = .true.
  dos = .false.              ! 不算声子态密度
  q_in_band_form = .true.    ! q 列表按高对称路径给
  q_in_cryst_coord = .true.  ! q 用晶体坐标
/
4
0.0000000000   0.0000000000   0.0000000000 50    !G
0.5000000000   0.0000000000   0.0000000000 50    !M
0.3333333333   0.3333333333   0.0000000000 50    !K
0.0000000000   0.0000000000   0.0000000000  1    !G
/
```

```bash
matdyn.x -i matdynxline.in > matdynxline.out
```

六方体系的 G-M-K-G 路径每段 50 个点；`q_in_band_form` 让 matdyn 沿路径连点出 `.freq.gp`（画图用）与 `.modes`。

## 思考

- 为什么 Γ 点（q=1）值得单独一批？它与声学求和规则、非解析项处理有什么关系？
- `zasr`/`asr` 取 'crystal' 时，q2r 与 matdyn 各自做了什么？若换成 'simple' 结果差在哪？
- 四批 q 中有一批没跑完就先执行 q2r，会发生什么？
