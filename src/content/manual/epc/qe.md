参考：

- [PHonon：interpolated 电声流程](https://www.quantum-espresso.org/Doc/ph_user_guide/node10.html)
- [pw.x 输入](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
- [ph.x 输入](https://www.quantum-espresso.org/Doc/INPUT_PH.html)
- [matdyn.x 输入](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html)

## 从 SnSe₂/Sr₂N 的计算目录接着做

这次在 bcgong 的 tmux 窗口里准备 EPC 输入。`qe` 下已经建好了两个空目录：`ph64` 和 `ph96`。它们用来比较两套致密电子网格。先看文件从哪里来，再开始复制。

以下保留终端里的真实账号和命令；工作目录、程序路径和赝势库路径作了简写。

```text
[bcgong@localhost qe]$ pwd
<工作目录>/qe
[bcgong@localhost qe]$ grep -n 'bfgs failed' config3/relax/rx.out
49794:     bfgs failed after  43 scf cycles and  40 bfgs steps, convergence not achieved
[bcgong@localhost qe]$
```


这条输出要先读完：程序在 43 次 SCF、40 步 BFGS 后结束，**BFGS 没有收敛，不能判定为结构优化通过**。下面暂时沿用它的末步结构准备输入；开始 EPC 前，要先解决结构验收。如何看力、应力与优化结束信息，见[结构优化](/Atlas/m/vc-relax/qe/)。

还有一处会直接影响声子频率的输入错误：

```text
[bcgong@localhost qe]$ grep amass config3/ph64/phx.in
  amass(1)=87.620
  amass(2)=14.007
  amass(2)=118.71
  amass(4)=78.971
[bcgong@localhost qe]$
```


`amass(2)` 写了两次。对照本材料 `ATOMIC_SPECIES` 的顺序 Sr、N、Sn、Se，118.71 应该属于第三种元素 Sn。新目录中修正这一行，同时检查 `matdynxline.in`；旧结果原样保留，不能把改过质量的输入和旧声子输出拼成一套结果。

## 先复制输入，再用 vi 改

参考 hzw 上 Sc₂C 的步骤：致密网格 SCF → 粗网格 SCF → 声子与 EPC → 后处理。那个算例使用 QE 7.2 和 USPP；这里使用 bcgong 上的 QE 7.1，保留 SnSe₂/Sr₂N 原有的 PAW 赝势、泛函和截断能。借用的是计算步骤，材料参数仍来自本材料。

先只复制输入。新目录里不放旧的 `out/`、动力学矩阵或电声输出。

```text
[bcgong@localhost qe]$ cp config3/ph64/pwx.in config3/ph64/pwxall.in config3/ph64/phx.in config3/ph64/q2rx.in config3/ph64/matdynxline.in ph64/
[bcgong@localhost qe]$ cd ph64
[bcgong@localhost ph64]$
```


用 `vi` 打开输入，按 `i` 编辑，完成后按 `Esc`，输入 `:wq` 保存退出。两份 SCF 输入均打开 `tprnfor` 和 `tstress`，使后续输出包含力和应力；`pwxall.in` 保留 `la2F=.true.` 和 64×64×1 网格。

```text
[bcgong@localhost ph64]$ vi pwxall.in
```


保存后用 `cat` 读回整个文件：

```text
[bcgong@localhost ph64]$ cat pwxall.in
&CONTROL
  calculation = 'scf'
  outdir = './out/'
  prefix = 'srnsnse'
  pseudo_dir = '<赝势库路径>'
  tprnfor = .true.
  tstress = .true.
  verbosity = 'high'
/
&SYSTEM
  ibrav = 0,
  nat = 6,
  ntyp = 4,
  ecutwfc = 120,
  ecutrho = 960,
  input_dft = 'vdw-DF3-opt1'
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 3.7d-3
  la2F=.true.
/
&ELECTRONS
  conv_thr = 1.0000000000d-12
  mixing_beta = 4.0000000000d-01
/
&ions
/
&cell
/
ATOMIC_SPECIES
Sr  87.620  Sr.pbe-spn-kjpaw_psl.1.0.0.UPF
N   14.007  N.pbe-n-kjpaw_psl.1.0.0.UPF
Sn  118.71  Sn.pbe-dn-kjpaw_psl.1.0.0.UPF
Se  78.971  Se.pbe-dn-kjpaw_psl.1.0.0.UPF
CELL_PARAMETERS (angstrom)
   3.915211298  -0.000000000   0.000000000
  -1.957605649   3.390672445   0.000000000
   0.000000000   0.000000000  40.000000000
ATOMIC_POSITIONS (crystal)
Sr            0.3333333333        0.6666666667        0.4858621609
Sr            0.6666666667        0.3333333333        0.4189402327
Sn            0.3333333333        0.6666666667        0.5848669832
Se            0.0000000000        0.0000000000        0.6229981775
Se            0.6666666667        0.3333333333        0.5395777160
N             0.0000000000        0.0000000000        0.4476047279
K_POINTS automatic
  64 64 1 0 0 0
[bcgong@localhost ph64]$
```


文件从上到下依次是控制项、体系设置、电子迭代、元素与赝势、晶胞、原子坐标和 k 网格。`nat=6` 对应六行坐标，`ntyp=4` 对应四种元素；`prefix='srnsnse'` 与 `outdir='./out/'` 后面还要在声子输入中对上。

这里的 120/960 Ry、0.0037 Ry 展宽和电子阈值沿用现有输入，尚不是针对超导温度完成的收敛结论。两套 SCF 的一般操作见[固定结构 SCF](/Atlas/m/scf/qe/)；本页继续看它们与 EPC 相接的地方。

## 声子输入里，质量与 q 网格一起核对

打开 `phx.in`，把 Sn 的质量索引改为 3，并去掉旧文件只计算第一点的 `start_q/last_q` 限制。这次先保留完整 8×8×1 q 网格输入；如果后续需要分批，范围应来自本材料实际列出的不可约 q 点。

```text
[bcgong@localhost ph64]$ vi phx.in
```

```text
[bcgong@localhost ph64]$ cat phx.in
  &inputph
  tr2_ph=1.0d-16
  nmix_ph=12
  verbosity='high'
  prefix='srnsnse'
  fildvscf='srnsnsedv'
  amass(1)=87.620
  amass(2)=14.007
  amass(3)=118.71
  amass(4)=78.971
  outdir='./out/'
  fildyn='srnsnse.dyn'
  electron_phonon='interpolated'
  el_ph_sigma=0.002
  el_ph_nsigma=20
  trans=.true.
  ldisp=.true.
  nq1=8
  nq2=8
  nq3=1
/
[bcgong@localhost ph64]$
```


此处四个 `amass` 与元素表逐一对应。`el_ph_sigma=0.002`、`el_ph_nsigma=20` 也只是当前准备使用的设置，后面要结合实际逐 q 输出检查展宽依赖。Sc₂C 的不可约 q 点数量和分段不能直接照搬过来。

上方官方输入手册目前为 QE 7.5；本机使用 QE 7.1，尚未找到与它匹配的官方输入手册来核实全部精确行为。这套 PAW、泛函与 EPC 的兼容性仍需在本地版本上验证，文件准备完成不等于这些检查已经通过。

## 脚本里的进程数要和申请资源一致

致密网格 SCF 的脚本已在 `vi` 中写入，读回如下：

```text
[bcgong@localhost ph64]$ cat pwxall.slurm
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR" || exit 1

mpirun -np 32 <qe_bin>/pw.x -in pwxall.in > pwxall.out 2> pwxall.err
[bcgong@localhost ph64]$
```


这里申请 32 个任务，`mpirun` 也使用 32 个进程。程序输出写到 `pwxall.out`，标准错误单独写到 `pwxall.err`；Slurm 自身仍保留 `_out.%j.log` 和 `_err.%j.log`。粗网格脚本 `pwx.slurm` 对应 `pwx.in → pwx.out`。

声子脚本使用 16 个 MPI 进程，并设 `OMP_NUM_THREADS=1`：

```text
[bcgong@localhost ph64]$ cat phx.slurm
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR" || exit 1

mpirun -np 16 <qe_bin>/ph.x -in phx.in > phx.out 2> phx.err
[bcgong@localhost ph64]$
```


两个 SCF 与声子步骤需要依次完成并检查，不能一次把三个脚本同时提交。新目录尚未运行这些程序，也没有可供展示的新 SCF 或声子输出。

## 把 ph96 只改成另一套致密网格

输入和脚本在 ph64 核对后，复制到 ph96：

```text
[bcgong@localhost ph64]$ cp *.in *.slurm ../ph96/
[bcgong@localhost ph64]$ cd ../ph96
[bcgong@localhost ph96]$
```

```text
[bcgong@localhost ph96]$ vi pwxall.in
```


在 `vi` 中把最后一行的 `64 64 1 0 0 0` 改成 `96 96 1 0 0 0`。保存后看差异：

```text
[bcgong@localhost ph96]$ diff ../ph64/pwxall.in pwxall.in
47c47
<   64 64 1 0 0 0
---
>   96 96 1 0 0 0
[bcgong@localhost ph96]$ grep -A1 K_POINTS pwx.in pwxall.in
pwx.in:K_POINTS automatic
pwx.in-  16 16 1 0 0 0
--
pwxall.in:K_POINTS automatic
pwxall.in-  96 96 1 0 0 0
[bcgong@localhost ph96]$
```


`diff` 只显示致密网格这一行变化；`pwx.in` 仍为 16×16×1。两目录的声子输入都是 8×8×1 q 网格。这样后续比较时，才知道这两套输入改变的是哪一个量。

再把声子和插值输入中的质量一起读出来：

```text
[bcgong@localhost ph96]$ grep amass phx.in matdynxline.in
phx.in:  amass(1)=87.620
phx.in:  amass(2)=14.007
phx.in:  amass(3)=118.71
phx.in:  amass(4)=78.971
matdynxline.in:  amass(1)=87.620
matdynxline.in:  amass(2)=14.007
matdynxline.in:  amass(3)=118.71
matdynxline.in:  amass(4)=78.971
[bcgong@localhost ph96]$
```


四个索引和四个数值现在一致。ph96 的设置更密，但是否足够，需要比较后续 λ、谱函数及目标物理量；目录名本身不能说明收敛。

## 后处理先把文件关系接好

回到 ph64，`q2rx.in` 把逐 q 动力学矩阵接到力常数文件，`matdynxline.in` 再读取同名力常数：

```text
[bcgong@localhost ph96]$ cd ../ph64
[bcgong@localhost ph64]$ cat q2rx.in
&input
zasr='crystal'
fildyn='srnsnse.dyn'
flfrc='srnsnse.fc'
la2F=.true.
/
[bcgong@localhost ph64]$ cat matdynxline.in
&input
  asr='crystal'
  amass(1)=87.620
  amass(2)=14.007
  amass(3)=118.71
  amass(4)=78.971
  flfrc='srnsnse.fc'
  flfrq='srnsnse.freq'
  la2F=.true.
  dos=.false.
  q_in_band_form = .true.
  q_in_cryst_coord = .true.

/
4
0.0000000000   0.0000000000   0.0000000000 50    !G
0.5000000000   0.0000000000   0.0000000000 50    !M
0.3333333333   0.3333333333   0.0000000000 50    !K
0.0000000000   0.0000000000   0.0000000000  1    !G
/
[bcgong@localhost ph64]$
```


`fildyn='srnsnse.dyn'` 与声子输入相同，`flfrc='srnsnse.fc'` 在两份后处理输入中相同。末尾列的是 Γ–M–K–Γ 路径；它用于画声子色散，完整 q 网格的稳定性仍要另外核对。已有输出的读取方法见[DFPT 声子](/Atlas/m/phonon-dfpt/qe/)。

`lambda.x` 的脚本也准备好了。它从标准输入读取 `lambdax.in`：

```text
[bcgong@localhost ph64]$ cat lambdax.slurm
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

ulimit -s unlimited
ulimit -l unlimited
source /data/intel/oneapi/setvars.sh
export OMP_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR" || exit 1

mpirun -np 1 <qe_bin>/lambda.x < lambdax.in > lambdax.out 2> lambdax.err
[bcgong@localhost ph64]$
```


**当前没有生成 `lambdax.in`。** 它要用本次计算实际得到的不可约 q 点、权重与逐 q 电声文件；频率积分上限也要覆盖实际声子范围。先复制另一材料的 q 列表和频率上限，会让后面的积分失去依据。

最后看一次目录：

```text
[bcgong@localhost ph64]$ ls -1
lambdax.slurm
matdynxline.in
matdynxline.slurm
phx.in
phx.slurm
pwxall.in
pwxall.slurm
pwx.in
pwx.slurm
q2rx.in
q2rx.slurm
README.md
[bcgong@localhost ph64]$
```


每套目录都有五份输入、六份 Slurm 脚本和一份说明。脚本分别做过 `bash -n` 检查，远端文件也已回读；这些检查只验证文件和 shell 语法。本次到这里结束，没有提交计算。

## 已完成算例里的输出长什么样

下面保留原来 **Sc₂C/ZrCl₂** 算例的输出，供对照文件结构。它与上面的 SnSe₂/Sr₂N 新目录是两套材料，数值和计算完成状态不能混用。

<details>
<summary>展开 Sc₂C/ZrCl₂ 的 SCF 与逐 q 电声输出</summary>



本目录三份输出的开头分别为：

```text
Program PWSCF v.7.1 starts on 19Jun2026 at  1: 2:52   # pwxall.out
Program PWSCF v.7.1 starts on 19Jun2026 at  2:52:53   # pwx.out
Program PHONON v.7.1 starts on 19Jun2026 at  3: 1:20  # phx.out
```

这与密网格 → 粗网格 → ph.x 的次序相符。时间顺序本身不能证明所有保存文件完整；重新运行前还要检查密网格保存产物、粗网格目录及 prefix 的对应关系，不应覆盖一套仍需使用的数据。

密网格这次留下的 SCF 摘录：

```text
[bcgong@localhost ph64]$ grep -E 'Program PWSCF|number of k points|convergence has been achieved|^!|JOB DONE' pwxall.out
     Program PWSCF v.7.1 starts on 19Jun2026 at  1: 2:52
     number of k points=   374  Gaussian smearing, width (Ry)=  0.0037
!    total energy              =    -793.68227867 Ry
     convergence has been achieved in  44 iterations
   JOB DONE.
[bcgong@localhost ph64]$
```

![密电子网格 SCF 的误差随迭代变化](/Atlas/figures/scf-accuracy.svg)

这里可以看到电子迭代误差如何下降到输入阈值附近。这是一次固定输入的 SCF 过程，不能替代 k 网格、q 网格或展宽的收敛测试。

### 电声文件是一 q 一份

这个 Sc₂C/ZrCl₂ 算例的四批 q 范围对应十个不可约 q 点。接着检查 lambda.x 要读取的文件：

```text
[bcgong@localhost ph64]$ find elph_dir -maxdepth 1 -name 'elph.inp_lambda.*' -type f | sort -V; head -n 5 elph_dir/elph.inp_lambda.1; head -n 4 lambda.dat; tail -n 3 lambda.dat
elph_dir/elph.inp_lambda.1
elph_dir/elph.inp_lambda.2
elph_dir/elph.inp_lambda.3
elph_dir/elph.inp_lambda.4
elph_dir/elph.inp_lambda.5
elph_dir/elph.inp_lambda.6
elph_dir/elph.inp_lambda.7
elph_dir/elph.inp_lambda.8
elph_dir/elph.inp_lambda.9
elph_dir/elph.inp_lambda.10
           0.000000      0.000000      0.000000    20    18
  0.126180E-06  0.126180E-06  0.242364E-06  0.927933E-06  0.927933E-06  0.177037E-05
  0.248278E-05  0.248278E-05  0.365571E-05  0.407124E-05  0.407124E-05  0.557880E-05
  0.557880E-05  0.794309E-05  0.974618E-05  0.151549E-04  0.228509E-04  0.228509E-04
     Gaussian Broadening:   0.001 Ry, ngauss=   0
# degauss   lambda    int alpha2F  <log w>     N(Ef)
  0.001    2.940003    2.902508    97.625   32.317854
  0.002    2.062339    2.025444   100.907   29.723113
  0.003    1.837986    1.801992   101.797   29.244028
  0.018    0.840009    0.795808   118.455   24.677094
  0.019    0.817430    0.772534   119.438   24.729924
  0.020    0.796142    0.750607   120.400   24.781569
[bcgong@localhost ph64]$
```

第一行末尾的 20 与 18 分别对应本文件的展宽数和模数，后面会出现各档 Gaussian Broadening 数据。这里共有十个 q 文件，每个文件内部有二十档展宽。展宽结果保存在各 q 文件内部，不是每一档各占一个文件。

文件存在只是起点：逐 q 编号、坐标、模数与每档展宽都应相互对应。q2r 的实际警告保留在[声子页](/Atlas/m/phonon-dfpt/qe/)，不能只挑成功行进入下一步。



</details>

## 下一步

本材料先回到[结构优化](/Atlas/m/vc-relax/qe/)解决结构验收，再进行[固定结构 SCF](/Atlas/m/scf/qe/)。得到完整声子和电声输出后，继续读[DFPT 声子](/Atlas/m/phonon-dfpt/qe/)与[谱函数、λ 表](/Atlas/m/eliashberg-a2f/qe/)。这些页面中的已完成算例会标出各自材料，阅读方法可以相接，数值不可混接。

```text
结构验收 → 致密 k SCF（la2F）→ 粗 k SCF → 完整 q 网格声子 + EPC
                                                   ├→ q2r → matdyn → 声子图
                                                   └→ 逐 q 文件、权重、频率范围
                                                        ↓
                                                    lambda.x
                                                        ↓
                                              展宽 / k / q 收敛检查
```
