参考：

- QE 官方文档 INPUT_PW（la2F 键）：<https://www.quantum-espresso.org/Doc/INPUT_PW.html>
- QE 官方文档 INPUT_PH（electron_phonon / el_ph_sigma）：<https://www.quantum-espresso.org/Doc/INPUT_PH.html>
- PHonon 用户指南（EPC 与 lambda.x 章节）：<https://www.quantum-espresso.org/Doc/user_guide/>

## 电声耦合（EPC）

电声耦合矩阵元是超导 Tc 预测的原料：DFPT 求出每个 q 点上电子密度对原子位移的响应，与 phonon 一起组装成 λ.x 可消费的 elph 数据。这一页走通从结构到 elph 文件齐备的完整链路。

## 先分清两套 SCF

体系里通常并存两套自洽，别混用：

| SCF | k 网格 | 作用 |
|---|---|---|
| 普通 scf（pwx.in） | 32×32×1 | 供能带、DOS、费米面等电子结构 |
| EPC 自洽（pwxall.in） | 64×64×1 + `la2F=.true.` | 专供电声链：算费米面平均量并落盘密网格波函数 |

**紧挨着 ph.x 的那次自洽必须是 pwxall**——密网格波函数是电声插值的数据源；若在 pwxall 之后再跑一次普通 scf，波函数被低密度版本覆盖，后面电声结果整个失真。真实工作流里 pwx（普通）与 pwxall（EPC）放在不同目录，互不覆盖。

## 第一步：pwxall（EPC 自洽）

相对普通 scf 只多两处：`la2F=.true.` 和更密的 k 网格。

```bash
[<user>@<cluster> ph64]$ cat > pwxall.in <<'EOF'
&CONTROL
  calculation = 'scf'
  outdir = './out/'
  prefix = '<prefix>'
  pseudo_dir = '<赝势库路径>'
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

CELL_PARAMETERS (angstrom)
! 此处放入你的结构块：三行晶胞矢量

ATOMIC_POSITIONS (crystal)
! 此处放入你的结构块：原子坐标行

K_POINTS automatic
  64 64 1 0 0 0
EOF
```

```bash
pw.x -i pwxall.in > pwxall.out
```

## 第二步：ph.x（EPC 开关 + q 分批）

EPC 版 phx.in 与纯声子版的差别只有三个键：

```bash
[<user>@<cluster> ph64]$ cat > phx.in <<'EOF'
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
EOF
```

同样按 start_q/last_q 切四批（q=1；2–4；5–7；8–10）各自 sbatch 并行。每批跑完在对应 q 的输出目录里生成 `elph_dir/elph.inp_lambda.<q>`——这就是给 lambda.x 的原料，20 个展宽各一份文件。

## 事故：批量 sed 之后丢了重定向

一次批量改写提交脚本时，`pw.x < pwxall.in > pwxall.out` 被写成了 `pw.xpwxall.out`（少个空格、输入重定向整个丢失），作业秒退且没有任何 pw.x 输出。定位用 `cat -A` 看脚本末尾的不可见字符：

```bash
[<user>@<cluster> ph64]$ cat -A pwxall.slurm | tail -n 5
mpirun -np 56 <qe_bin>/pw.xpwxall.out$
[<user>@<cluster> ph64]$
```

把执行行改回完整重定向再提交即可。教训：批量 sed 改脚本后，提交前先 `cat -A` 或 `bash -n` 过一遍。

## 第三步：q2r（带 la2F）

```bash
[<user>@<cluster> ph64]$ cat > q2rx.in <<'EOF'
&input
zasr = 'crystal'
fildyn = 'zrclscc.dyn'
flfrc = 'zrclscc.fc'
la2F = .true.                ! 必须带，否则 elph 数据链断裂
/
EOF
```

四批 q 全部 JOB DONE 后再执行；成功标志 `fft-check success`。

## 第四步：清点 elph 数据

lambda.x 需要的原料应齐备：

```bash
[<user>@<cluster> ph64]$ ls elph_dir/ | head
elph.inp_lambda.1
elph.inp_lambda.2
...
[<user>@<cluster> ph64]$
```

10 个 q × 20 档展宽各一份。之后交给 lambda.x——输入文件与判读见 λ(ω) 谱函数页。

## 下一步

```text
DFPT 声子 + la2F 自洽（本页）
    ↓ elph.inp_lambda.N 齐备
λ(ω) 谱函数（lambda.x）
    ↓
Allen–Dynes Tc
```
