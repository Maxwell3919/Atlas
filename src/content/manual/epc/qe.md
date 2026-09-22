参考：

- [PHonon：interpolated 电声流程](https://www.quantum-espresso.org/Doc/ph_user_guide/node10.html)
- [pw.x 输入](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
- [ph.x 输入](https://www.quantum-espresso.org/Doc/INPUT_PH.html)

## 先把两套电子网格接对

继续使用 Sc₂C/ZrCl₂ 主算例的 `ph64`（QE 7.1，2026 年 6 月输出）。这里的两次 SCF 各有用途：密网格为费米面求和保存数据，粗网格衔接声子响应。下面是 2026-09-22 对留存输入和输出的读取，不是新提交记录。

```text
[<user>@<cluster> 2]$ grep -A1 K_POINTS ph64/pwx.in ph64/pwxall.in ph96/pwxall.in; grep -E 'nq[123]' ph64/phx.in ph96/phx.in
ph64/pwx.in:K_POINTS automatic
ph64/pwx.in-  16 16 1 0 0 0
--
ph64/pwxall.in:K_POINTS automatic
ph64/pwxall.in-  64 64 1 0 0 0
--
ph96/pwxall.in:K_POINTS automatic
ph96/pwxall.in-  96 96 1 0 0 0
ph64/phx.in:  nq1=8
ph64/phx.in:  nq2=8
ph64/phx.in:  nq3=1
ph96/phx.in:  nq1=8
ph96/phx.in:  nq2=8
ph96/phx.in:  nq3=1
[<user>@<cluster> 2]$
```

更正（2026-09-22）：原文把 `pwx` 写成 32×32×1，并称密网格 SCF 必须紧挨 ph.x、之后不能运行粗网格 SCF。这与本目录输入和运行次序不符。该 `interpolated` 路线先准备密网格数据，再做粗网格 SCF 和声子；不能把它与另一种电声流程混写。

## 读取密网格输入与执行脚本

```text
[<user>@<cluster> ph64]$ cat pwxall.in
&CONTROL
  calculation = 'scf'
  outdir = './out/'
  prefix = 'zrclscc'
  pseudo_dir = '<赝势库路径>'
! tprnfor = .true.
! tstress = .true.
  verbosity = 'high'
/
&SYSTEM
  ibrav = 0,
  nat = 6,
  ntyp = 4,
  ecutwfc = 100,
  ecutrho = 800,
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
Zr  91.224  Zr.pbe-spn-kjpaw_psl.1.0.0.UPF
Cl  35.450  Cl.pbe-n-kjpaw_psl.1.0.0.UPF
Sc  44.956  Sc.pbe-spn-kjpaw_psl.1.0.0.UPF
C   12.011  C.pbe-n-kjpaw_psl.1.0.0.UPF
CELL_PARAMETERS (angstrom)
   3.308844553  -0.000000000   0.000000000
  -1.654422277   2.865543440   0.000000000
   0.000000000   0.000000000  40.000000000
ATOMIC_POSITIONS (crystal)
Zr            0.6666666667        0.3333333333        0.5694323199
C             0.0000000000        0.0000000000        0.4417100192
Cl            0.3333333333        0.6666666667        0.6133689415
Cl            0.3333333333        0.6666666667        0.5201529798
Sc            0.3333333333        0.6666666667        0.4128299130
Sc            0.6666666667        0.3333333333        0.4719057887
K_POINTS automatic
  64 64 1 0 0 0
[<user>@<cluster> ph64]$
```

完整脚本如下。这里实用 32 个 MPI 进程；HfCl₂/PbO₂ 页面里的 56 属于另一台集群的另一份作业，不能为了统一排版改成同一个数。

```text
[<user>@<cluster> ph64]$ cat pwxall.slurm
#!/bin/bash

#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

#unlimit memory
ulimit -s unlimited
ulimit -l unlimited

# load path
source /data/intel/oneapi/setvars.sh

cd $SLURM_SUBMIT_DIR

mpirun -np 32 <qe_bin>/pw.x<pwxall.in>pwxall.out
#rm -r _*.log
[<user>@<cluster> ph64]$
```

同一脚本中的输入、输出文件名是一对。复制脚本后先 `tail -n 5 pwxall.slurm` 逐字检查；`bash -n` 只能查 shell 语法，像 `pw.xpwxall.out` 这样的错误文件名仍可能通过语法检查。

## 按输出时间核对先后

本目录三份输出的开头分别为：

```text
Program PWSCF v.7.1 starts on 19Jun2026 at  1: 2:52   # pwxall.out
Program PWSCF v.7.1 starts on 19Jun2026 at  2:52:53   # pwx.out
Program PHONON v.7.1 starts on 19Jun2026 at  3: 1:20  # phx.out
```

这与密网格 → 粗网格 → ph.x 的次序相符。时间顺序本身不能证明所有保存文件完整；重新运行前还要检查密网格保存产物、粗网格目录及 prefix 的对应关系，不应覆盖一套仍需使用的数据。

密网格这次留下的 SCF 摘录：

```text
[<user>@<cluster> ph64]$ grep -E 'Program PWSCF|number of k points|convergence has been achieved|^!|JOB DONE' pwxall.out
     Program PWSCF v.7.1 starts on 19Jun2026 at  1: 2:52
     number of k points=   374  Gaussian smearing, width (Ry)=  0.0037
!    total energy              =    -793.68227867 Ry
     convergence has been achieved in  44 iterations
   JOB DONE.
[<user>@<cluster> ph64]$
```

![密电子网格 SCF 的误差随迭代变化](/Atlas/figures/scf-accuracy.svg)

这里可以看到电子迭代误差如何下降到输入阈值附近。这是一次固定输入的 SCF 过程，不能替代 k 网格、q 网格或展宽的收敛测试。

## 电声文件是一 q 一份

声子页列出的四批 q 范围对应十个不可约 q 点。接着检查 lambda.x 要读取的文件：

```text
[<user>@<cluster> ph64]$ find elph_dir -maxdepth 1 -name 'elph.inp_lambda.*' -type f | sort -V; head -n 5 elph_dir/elph.inp_lambda.1; head -n 4 lambda.dat; tail -n 3 lambda.dat
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
[<user>@<cluster> ph64]$
```

第一行末尾的 20 与 18 分别对应本文件的展宽数和模数，后面会出现各档 Gaussian Broadening 数据。这里是十个 q 文件，每个文件内部有二十档展宽；原文的“十个 q × 二十档、各一份文件”会让人误找二百份文件，已更正。

文件存在只是起点：逐 q 编号、坐标、模数与每档展宽都应相互对应。q2r 的实际警告保留在[声子页](/Atlas/m/phonon-dfpt/qe/)，不能只挑成功行进入下一步。

## 下一步

读取[谱函数与 λ 表](/Atlas/m/eliashberg-a2f/qe/)，先观察它们随展宽如何变化。

```text
密 k SCF（la2F）→ 粗 k SCF → ph.x（q 网格 + EPC）
                                      ↓
                       逐 q 文件核对 → lambda.x
                                      ↓
                         展宽 / k / q 收敛分别检查
```
