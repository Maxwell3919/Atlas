参考：

- QE 官方文档 INPUT_PW（la2F 键）：<https://www.quantum-espresso.org/Doc/INPUT_PW.html>
- QE 官方文档 INPUT_PH（electron_phonon / el_ph_sigma）：<https://www.quantum-espresso.org/Doc/INPUT_PH.html>
- PHonon 用户指南（EPC 与 lambda.x 章节）：<https://www.quantum-espresso.org/Doc/user_guide/>

## 本页目标

从弛豫结构出发跑通完整电声耦合链，产出 λ.x 所需的全部输入数据。读完本页你能：理解两套 SCF 的分工、按 q 分批提交 EPC 计算、把 elph 输出喂给 lambda.x。

## 前置与两套 SCF 的分工

体系里通常并存两套自洽，别混用：

| SCF | k 网格 | 作用 |
|---|---|---|
| 普通 scf（pwx.in） | 32×32×1 | 供能带、DOS、费米面等电子结构 |
| EPC 自洽（pwxall.in） | 64×64×1 + `la2F=.true.` | 专供电声链：算费米面平均量并落盘密网格波函数 |

**紧挨着 ph.x 的那次自洽必须是 pwxall**——密网格波函数是电声插值的数据源；若在 pwxall 之后再跑一次普通 scf，波函数被低密度版本覆盖，后面电声结果整个失真。真实工作流里 pwx（普通）与 pwxall（EPC）放在不同目录，互不覆盖。

## pwxall.in（相对普通 scf 只多两处）

```fortran
&CONTROL
  calculation = 'scf'
  outdir = './out/'
  prefix = '<prefix>'
  pseudo_dir = '<赝势库路径，与 ATOMIC_SPECIES 匹配>'
  verbosity = 'high'
/
&SYSTEM
  ibrav = 0, nat = 6, ntyp = 4,
  ecutwfc = 100, ecutrho = 800,
  input_dft = 'vdw-DF3-opt1'
  la2F = .true.              ! 关键：打开 Eliashberg 谱函数计算
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 3.7d-3
/
&ELECTRONS
  conv_thr = 1.0000000000d-12
  mixing_beta = 4.0000000000d-01
/
ATOMIC_SPECIES
（与 scf 相同，略）
（替换为你的结构块：CELL_PARAMETERS / ATOMIC_POSITIONS）
K_POINTS automatic
  64 64 1 0 0 0              ! 比 scf 的 32×32×1 密一倍
```

```bash
pw.x -i pwxall.in > pwxall.out
```

## ph.x（EPC 开关 + q 分批）

EPC 版 phx.in 与纯声子版的差别只是三个键：

```fortran
&inputph
  tr2_ph = 1.0d-16
  nmix_ph = 12
  verbosity = 'high'
  prefix = '<prefix>'
  fildvscf = 'zrclsccdv'
  amass(1) = 91.224
  amass(2) = 35.450
  amass(3) = 44.956
  amass(4) = 12.011
  outdir = './out/'
  fildyn = 'zrclscc.dyn'
  electron_phonon = 'interpolated'   ! EPC 模式：逐 q 写出电声矩阵元
  el_ph_sigma = 0.001                ! 展宽起点
  el_ph_nsigma = 20                  ! 生成 20 个展宽文件（0.001→0.020 Ry）
  trans = .true.
  ldisp = .true.
  start_q = 1
  last_q = 1
  nq1 = 8
  nq2 = 8
  nq3 = 1
/
```

同样按 start_q/last_q 切四批（q=1；2–4；5–7；8–10）各自 sbatch 并行。每批跑完在对应 q 的输出目录里生成 `elph_dir/elph.inp_lambda.<q>`——这就是给 lambda.x 的原料，20 个展宽各一份文件。

## q2r.x（带 la2F）

```fortran
&input
zasr = 'crystal'
fildyn = 'zrclscc.dyn'
flfrc = 'zrclscc.fc'
la2F = .true.                ! 必须带，否则 elph 数据链断裂
/
```

## 事故：提交脚本里丢掉的输入重定向

一次批量改写提交脚本时，重定向被吃掉一个字符，实际执行成了：

```text
pw.xpwxall.out          ← 本应是  pw.x < pwxall.in > pwxall.out
```

现象是作业秒退且没有任何 pw.x 输出。定位用 `cat -A` 看脚本末尾不可见字符：

```bash
cat -A pwxall.slurm | tail -n 5
```

把执行行改成带完整重定向的写法后重交即可。教训：批量 sed 改脚本后，提交前先 `cat -A` 或 `bash -n` 过一遍。

## 交接给 lambda.x

四批 q 全部 JOB DONE、q2r 完成 `zrclscc.fc` 后，elph_dir 里应齐备 10 个 q 的 20 套展宽文件。lambda.x 的输入与判读见 λ(ω) 谱函数页。

## 思考

- `la2F` 打开后，scf 与 ph.x 各自多算了什么量？
- 为什么 EPC 自洽要用比普通 scf 更密的 k 网格？密度不够时最先失真的是哪一步？
- el_ph_nsigma 取 20 的意义是什么？判读时挑哪一档展宽？
