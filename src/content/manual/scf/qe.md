## 固定结构，求后续分析使用的电子密度

研究界面电荷转移、电子态与声子，先要给每个结构建立一份匹配的自洽密度和有效势。SCF 固定晶胞与原子位置，反复求本征态、更新密度，直到输入的电子停止条件满足。[Giannozzi 等](https://doi.org/10.1088/0953-8984/21/39/395502)附录 A.1 式 (A.1)把这一步写成密度或有效势的固定点问题；下面 OUT 中的估计误差与停止行对应这个求解过程。

密度决定电子所感受到的 Hartree 势和交换关联势，而这些势又决定轨道和占据。SCF 每轮用当前密度求电子态，再由已占据态形成新的密度并混合，逐步使两者相容；本例的超软赝势还包含增广电荷，不能只把波函数平方相加就当作完整密度。固定晶胞时，8³ 网格参与的是这一次密度的布里渊区积分。后面把本征态采样加密到 24³，是在已有有效势上换位置求解，父密度本身仍来自这次 8³ 自洽。

本例用 Preston 上的 QE 7.5 计算两个原子的金刚石 Si 原胞，常规立方晶格参数为 10.20 bohr，采用公开的 PBE 超软赝势。这个小体系让输入、电子数、迭代、力、压力和保存目录都能逐项读清。它提供固定结构 Si 的电子计算记录，后续 [NSCF](/Atlas/m/nscf/qe/)和 [Γ 点声子](/Atlas/m/imaginary-phonon/qe/)沿用相应父数据。

自己的结构若来自优化，先在[离子弛豫](/Atlas/m/relax/qe/)或[晶胞弛豫](/Atlas/m/vc-relax/qe/)核对末态。以下输入的截断和网格是这份 Si 记录的设置；[收敛测试](/Atlas/m/convergence/qe/)给出它们对总能量的实际影响。[QE 7.5 输入定义](https://github.com/QEF/q-e/blob/qe-7.5/PW/Doc/INPUT_PW.def)用于查本版本参数。

[完整算例包](/Atlas/examples/si-pbe-lesson-files.tar.gz)含输入、OUT、XML 与已生成的数据，未打包 `tmp/si.save` 中的密度和波函数。可直接阅读输出与 XML；重新计算须按[官方来源](https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF)准备赝势，从这份输入生成自己的保存目录。

## 读完这份小输入，再提交

在 `si-pbe` 下，`pseudo` 放赝势，`scf` 放本次输入与输出。输入使用相对路径 `../pseudo`，所以提交时要先进入 `scf`。本次文件内容如下：

```text
[preston@preston-System-Product-Name scf]$ cat scf.in
&CONTROL
  calculation = 'scf'
  prefix = 'si'
  outdir = './tmp'
  pseudo_dir = '../pseudo'
  tprnfor = .true.
  tstress = .true.
/
&SYSTEM
  ibrav = 2
  A = 5.397607551
  nat = 2
  ntyp = 1
  ecutwfc = 60
  ecutrho = 640
  occupations = 'fixed'
/
&ELECTRONS
  conv_thr = 1.0d-10
/
ATOMIC_SPECIES
Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS alat
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25
K_POINTS automatic
8 8 8 0 0 0
```
`ibrav=2` 定义 fcc 原胞，`A` 是常规立方晶格参数，单位 Å。`ATOMIC_POSITIONS alat` 中的坐标按这个晶格参数缩放，不是分数坐标卡片 `crystal`。两种坐标表示不能只换卡片名而不换数值。

`calculation='scf'` 固定晶胞和原子位置。`tprnfor`、`tstress` 让它仍然打印力和应力，供我们判断这个固定结构处在什么状态。8 个价电子在这份非磁性计算中占据 4 条带，所以 `occupations='fixed'` 可用于这个半导体例子；金属的占据处理另见[Al 声子前的 SCF](/Atlas/m/phonon-dfpt/qe/)。

`ecutwfc=60 Ry` 限制波函数的平面波基组，`ecutrho=640 Ry` 控制电荷密度与势使用的截断；超软赝势的增广电荷也需要足够细的表示。两个数的作用不同，比例不能直接搬给另一种赝势。本例的[独立对照](/Atlas/m/convergence/qe/)中，60→80 Ry 的总能变化约 0.138 meV/atom；但 `8³` 与 `14³` 网格仍相差约 1.95 meV/atom。这些参数用于认识 SCF 的计算过程；研究具体性质时，还应检查该性质对网格和截断能的敏感性。最后三个零表示不施加半格位移；之后再增加 NSCF 的 k 点，也不会反过来更新这份 SCF 密度。

下面是实际运行的四进程脚本。`ulimit`、线程数和工作目录一起保留；QE 路径按本机安装位置填写。Preston 的这套程序使用 GCC/OpenMPI，启动命令应与本机程序链接的 MPI 实现和调度环境匹配。

```text
[preston@preston-System-Product-Name scf]$ cat run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
ulimit -s unlimited
ulimit -c 0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to core -np 4 <qe_bin>/pw.x -in scf.in > scf.out 2> scf.err
```
用 `vi scf.in` 检查并保存输入后，提交与查看的命令是：

```bash
sbatch run.sh
squeue -j 765
tail -f scf.out
```
这次作业号是 765，实际 WALL 时间为 13.73 s；重新提交会得到新的号码。`tail -f` 只跟随输出，Ctrl-C 结束的是查看进程。输出一段时间没有新增时，先同时看队列和错误文件，不要立即往同一目录再次提交。

## OUT 的前半段是在告诉你：程序实际读到了什么

`scf.out` 开头记录程序版本、进程数和输入文件。继续往下，会出现结构、电子数、截断能与交换关联设置：

```text
     bravais-lattice index     =            2
     lattice parameter (alat)  =      10.2000  a.u.
     unit-cell volume          =     265.3020 (a.u.)^3
     number of atoms/cell      =            2
     number of atomic types    =            1
     number of electrons       =         8.00
     number of Kohn-Sham states=            4
     kinetic-energy cutoff     =      60.0000  Ry
     charge density cutoff     =     640.0000  Ry
     scf convergence threshold =      1.0E-10
     mixing beta               =       0.7000
     number of iterations used =            8  plain     mixing
     Exchange-correlation= PBE
                           (   1   4   3   4   0   0   0)
```
这里的 `alat=10.2000 a.u.` 与输入中的 Å 单位不同；它们描述的是同一个长度。`number of electrons=8.00` 来自两个 Si、每个 4 个价电子。`number of Kohn-Sham states=4` 也解释了为什么这份 SCF 输出没有可供我们研究导带的空带：空带会在后面的 NSCF 或路径计算中明确增加。

下一段是晶格轴、赝势来源、对称性和原子位置。赝势段可以直接核对文件名、类型与价电子数：

```text
     PseudoPot. # 1 for Si read from file:
     ../pseudo/Si.pbe-n-rrkjus_psl.1.0.0.UPF
     MD5 check sum: fa25574f73a70a4139f2adfbefec430c
     Pseudo is Ultrasoft + core correction, Zval =  4.0
```
再往下是 k 点列表。输入写了 8×8×8，输出却只有 29 个点，这里先不要改输入：程序利用当前晶体的对称性只保留不可约点，同时写出权重。29 不代表输入变成了 29×29×29。

```text
     number of k points=    29
                       cart. coord. in units 2pi/alat
        k(    1) = (   0.0000000   0.0000000   0.0000000), wk =   0.0039062
        k(    2) = (  -0.1250000   0.1250000  -0.1250000), wk =   0.0312500
        k(    3) = (  -0.2500000   0.2500000  -0.2500000), wk =   0.0312500
        k(    4) = (  -0.3750000   0.3750000  -0.3750000), wk =   0.0312500
        k(    5) = (   0.5000000  -0.5000000   0.5000000), wk =   0.0156250
```
头部的这些内容应该在计算刚开始时就检查。若元素、原子数、k 点或赝势与预期不同，即使后面得到一个收敛能量，也是在解另一份输入。

## 迭代段要连着看能量和估计误差

第一次电子迭代从初始密度出发。下面保留两轮连续的输出，可以看清每个循环的排列：

```text
     iteration #  1     ecut=    60.00 Ry     beta= 0.70
     Davidson diagonalization with overlap
     ethr =  1.00E-02,  avg # of iterations =  2.0

     Threshold (ethr) on eigenvalues was too large:
     Diagonalizing with lowered threshold

     Davidson diagonalization with overlap
     ethr =  6.40E-04,  avg # of iterations =  1.5

     total cpu time spent up to now is        1.2 secs

     total energy              =     -22.83581101 Ry
     estimated scf accuracy    <       0.05540955 Ry

     iteration #  2     ecut=    60.00 Ry     beta= 0.70
     Davidson diagonalization with overlap
     ethr =  6.93E-04,  avg # of iterations =  1.0

     total cpu time spent up to now is        1.5 secs

     total energy              =     -22.83770169 Ry
     estimated scf accuracy    <       0.00288592 Ry
```
`total energy` 是当前轮的总能；`estimated scf accuracy` 是程序对电子自洽误差的估计，单位 Ry；`ethr` 属于本征值求解器的内部阈值。三者不是同一个量。能量两轮之间看起来变化很小，仍要继续核对 SCF 的停止条件。

从这一排列可以分清两种迭代：Davidson 在当前有效势下求本征态，随后密度混合为下一轮 SCF 更新有效势。`ethr` 先随电子循环收紧，是为了在早期尚未稳定的势上节省对角化成本；真正接近自洽时，才用更精细的本征态支撑小残差。判断电子停止看末轮 `estimated scf accuracy` 与 `conv_thr`，[QE 7.5 定义](https://github.com/QEF/q-e/blob/qe-7.5/PW/Doc/INPUT_PW.def)明确它估计的是整胞自洽能量误差。把它和相邻两轮总能差混作一列，会失去这一判据的含义。

这次第 9 轮结束后，输出先列能带本征值，再打印最高占据态、带感叹号的总能和自洽收敛信息：

```text
     highest occupied level (ev):     6.3971

!    total energy              =     -22.83859230 Ry
     estimated scf accuracy    <          4.3E-11 Ry

     The total energy is the sum of the following terms:
     one-electron contribution =       5.30781076 Ry
     hartree contribution      =       1.08523150 Ry
     xc contribution           =     -12.33187599 Ry
     ewald contribution        =     -16.89975857 Ry

     convergence has been achieved in   9 iterations
```
`4.3E-11 Ry` 小于输入的 `conv_thr=1.0d-10`，并有明确的 9 轮收敛行。这个阈值对应整胞的估计自洽能量误差，不能解释为每个原子的误差，更不包含基组、k 网格和泛函的误差。这里的最高占据态是 6.3971 eV；求带隙还需要导带底以及它所在的 k 点。比较异质结和孤立层的能级时，也要先选共同的能量参照，例如真空平台；分别把每幅图的费米能设为零，不能直接读出绝对带边的移动。具体能级对齐见[带边对齐](/Atlas/m/band-alignment/)。

## 力为零、压力不为零，两件事可以同时发生

```text
     Forces acting on atoms (cartesian axes, Ry/au):

     atom    1 type  1   force =    -0.00000000   -0.00000000   -0.00000000
     atom    2 type  1   force =     0.00000000    0.00000000    0.00000000

     Total force =     0.000000     Total SCF correction =     0.000000


     Computing stress (Cartesian axis) and pressure

          total   stress  (Ry/bohr**3)                   (kbar)     P=       38.45
   0.00026138   0.00000000   0.00000000           38.45        0.00        0.00
   0.00000000   0.00026138  -0.00000000            0.00       38.45       -0.00
   0.00000000  -0.00000000   0.00026138            0.00       -0.00       38.45
```
两个 Si 的力在打印精度内为零，而压力是 **38.45 kbar**。高对称结构可以使原子力为零；这并不保证晶胞体积已经优化。因此这份结果可用于演示“固定结构电子自洽”，不能据此宣布得到零压平衡晶格。若问题要求平衡晶胞，应回到 `vc-relax`，而不是不断收紧同一固定晶胞的电子阈值。

程序随后写出保存数据，末尾给出分项计时和退出标记：

```text
     Writing all to output data dir ./tmp/si.save/ :
     XML data file, charge density, pseudopotentials, collected wavefunctions
```

```text
     Parallel routines

     PWSCF        :      9.22s CPU     13.73s WALL


   This run was terminated on:  21:32:37  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
保存行说明程序执行了写盘，后续还要检查对应文件确实完整。把它与电子收敛行和结束段一起读，才能把结果与这轮计算对应起来。完整的 [scf.out](/Atlas/examples/si-pbe/scf/scf.out.txt) 和 [scf.err](/Atlas/examples/si-pbe/scf/scf.err.txt)可以下载；运行日志不能只保留 `JOB DONE.` 一行。这里的 `scf.err` 有 780 字节，包含重复的 `Authorization required, but no authorization protocol specified` 环境提示；本次电子循环和程序结束记录完整。

## 下一步要带走保存目录，不只是一份 OUT

`scf.out` 便于人阅读，`tmp/si.save` 才保存后续程序读取的电子态。这个目录里的 `data-file-schema.xml` 记录结构和计算信息，`charge-density.dat` 保存电子密度，`wfc*.dat` 保存波函数；文件分布还会随 QE 版本和并行方式变化。

XML 可以单独保留，用于核对结构、参数和能级；它不是电荷密度的替代文件。实际运行后，先在该计算目录检查 `tmp/si.save` 内的文件，再按 `prefix` 与 `outdir` 找到父数据。下载包只有 OUT/XML 时，能做的是读取存档和重绘已有数值；要重跑子计算，须先生成自己的匹配保存目录。

准备新的分支时，先新建目录并复制这份父数据，避免后续 NSCF 改写 SCF 原件。下面用 `nscf` 演示分支命名；[下一页](/Atlas/m/nscf/qe/)保留的实际复算目录叫 `gap24-cg`，跟那份算例时按它的目录名接续。

```bash
mkdir ../nscf
cp -r tmp ../nscf/
cp scf.in ../nscf/nscf.in
cd ../nscf
vi nscf.in
```
这里的 `nscf.in` 还需要按[NSCF 页](/Atlas/m/nscf/qe/)修改计算类型、网格与空带；复制只建立文件关系，没有自动完成那些设置。`prefix` 和 `outdir` 必须指向刚复制的 Si 数据。如果改变了结构、元素、赝势或上游物理设置，应重新建立对应 SCF。

本例共 9 轮电子迭代，末轮 `estimated scf accuracy` 为 4.3×10⁻¹¹ Ry；[完整迭代表](/Atlas/examples/basics-si-convergence/results/scf-history.csv)由上述 OUT 逐轮提取。原子力在打印精度内为零，固定晶胞的压力为 38.45 kbar。电子收敛与晶胞是否达到目标压力应分别看这两项输出。

下一步按所需结果选择：[均匀网格 NSCF](/Atlas/m/nscf/qe/)通向 DOS 与布里渊区采样；[路径能带](/Atlas/m/bands/qe/)沿指定高对称线求本征值；[Γ 点声子及虚频对照](/Atlas/m/imaginary-phonon/qe/)读取本例的密度与波函数求响应。

这里的两条电子态分支从同一 SCF 出发，各自复制父数据，并按不同用途采样：

| 想读出的量 | 本例实际分支 | 本征态在哪些位置求解 | 怎样使用结果 |
| --- | --- | --- | --- |
| 全区带边、DOS | `gap24-cg`，`calculation='nscf'` | 24³ 均匀网格，约化后 413 点 | 带权重积分或遍历所有已采样本征值 |
| 高对称方向的色散 | `bands-cg`，`calculation='bands'` | Γ–X–W–K–Γ–L–X，121 个路径点 | 按路径距离连接同一带的能级 |

路径点覆盖的是线而不是整个布里渊区，不能拿这 121 点代替 DOS 的均匀积分；均匀点也没有自动给出高对称路径顺序。两条分支都把带数从四条增到八条，以覆盖本例要读的空带，却不重新混合父密度。[官方 PWscf 手册第 3.3.0.2 节](https://www.quantum-espresso.org/Doc/pw_user_guide/node10.html)说明这两种非自洽用途，并提醒原子位置默认从父数据读取；只修改子输入中的坐标，可能仍读到旧结构。换结构时，应从那份结构建立新的 SCF。

### 用存档核对两条分支的身份

先读取三份 XML 的 `calculation`、`nks`、`nbnd` 和 `nelec`，再检查每个 k 点的本征值数目与有限性；结构、赝势名称、泛函、自旋设置和截断也一起比较。OUT 另查正常结束与本征值警告，这样才能分清“文件计数一致”和“求解是否留下警告”。这次核对只读现有存档，不提交计算。保存目录是否在包内另列出来，避免把 XML 的存在理解为完整父密度已经可用。

可将下述具体需求交给编程助手：

> 用 Python 标准库读取 si-pbe 下 scf、gap24-cg、bands-cg 的 OUT 与 data-file-schema.xml。核对输出 k 点数、能带数和每点有限本征值；比较原子/晶胞、赝势文件名、PBE、自旋开关和截断。按实际 calculation 区分三份记录，统计 c_bands 未收敛行、JOB DONE 和 XML exit_status。单列 scf/tmp/si.save 是否存在，不把这些检查解释成目标物理量或密度身份已经验证。打印逐分支记录，并可选输出 JSON；资料缺失时明确报错。

[完整源码 audit_si_branches.py](/Atlas/examples/enrichment-20261003/basics/audit_si_branches.py)如下：

<details>
<summary>读取现有 OUT/XML 的完整核对程序</summary>

```python
#!/usr/bin/env python3
"""Read this Si archive's OUT/XML; do not submit jobs or inspect remote save data."""
import argparse
import json
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET

CASES = [('scf', 'scf.out'), ('gap24-cg', 'nscf.out'), ('bands-cg', 'bands.out')]

def numbers(text):
    values = [float(x) for x in text.split()]
    if not all(math.isfinite(x) for x in values):
        raise ValueError('Non-finite XML numbers')
    return tuple(round(x, 11) for x in values)

def read_case(root, name, outname):
    x = ET.parse(root / name / 'data-file-schema.xml').getroot()
    b = x.find('output/band_structure')
    ks = b.findall('ks_energies')
    nbnd, nks = int(b.findtext('nbnd')), int(b.findtext('nks'))
    if len(ks) != nks or any(len(numbers(k.findtext('eigenvalues'))) != nbnd for k in ks):
        raise ValueError(f'{name}: XML counts/eigenvalues disagree')
    g = x.find('output/atomic_structure')
    species = [(s.attrib['name'], s.findtext('pseudo_file'))
               for s in x.findall('input/atomic_species/species')]
    model = [x.findtext('input/dft/functional'), species,
             [x.findtext('input/spin/' + tag) for tag in ('lsda', 'noncolin', 'spinorbit')],
             [x.findtext('input/basis/' + tag) for tag in ('ecutwfc', 'ecutrho')],
             [(q.tag, numbers(q.text)) for q in g.find('cell')],
             [(q.attrib['name'], numbers(q.text)) for q in g.find('atomic_positions')]]
    out = (root / name / outname).read_text()
    report = dict(calculation=x.findtext('input/control_variables/calculation'),
                  nks=nks, nbnd=nbnd, nelec=float(b.findtext('nelec')),
                  xml_exit_status=int(x.findtext('exit_status')),
                  job_done='JOB DONE.' in out,
                  eigenvalue_warning_lines=len(re.findall(r'c_bands:.*not converged', out)))
    return report, model

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path, help='the extracted si-pbe directory')
    p.add_argument('--json', type=Path, help='optional report destination')
    args = p.parse_args()
    rows, models = {}, []
    for name, outname in CASES:
        rows[name], model = read_case(args.root, name, outname)
        models.append(model)
        q = rows[name]
        print(f"{name}: calculation={q['calculation']} nks={q['nks']} nbnd={q['nbnd']} "
              f"nelec={q['nelec']:g} xml_exit={q['xml_exit_status']} "
              f"JOB_DONE={q['job_done']} eigenvalue_warning_lines={q['eigenvalue_warning_lines']}")
    same = all(m == models[0] for m in models[1:])
    saved = (args.root / 'scf/tmp/si.save').is_dir()
    print(f'same_geometry_and_model={same}; scf_save_directory_in_archive={saved}')
    result = dict(cases=rows, same_geometry_and_model=same,
                  scf_save_directory_in_archive=saved,
                  boundary='XML/OUT consistency only; no proof of saved density identity or target convergence')
    if args.json:
        args.json.write_text(json.dumps(result, indent=2) + '\n')
    if not same:
        raise ValueError('Geometry or selected physical-model fields differ')

if __name__ == '__main__':
    main()
```

</details>

下载程序，在解包后的共同上级运行 `python3 audit_si_branches.py si-pbe --json si-branch-audit.json`。下面是读取本站实际 `si-pbe` 存档得到的输出：

```text
scf: calculation=scf nks=29 nbnd=4 nelec=8 xml_exit=0 JOB_DONE=True eigenvalue_warning_lines=0
gap24-cg: calculation=nscf nks=413 nbnd=8 nelec=8 xml_exit=0 JOB_DONE=True eigenvalue_warning_lines=0
bands-cg: calculation=bands nks=121 nbnd=8 nelec=8 xml_exit=0 JOB_DONE=True eigenvalue_warning_lines=0
same_geometry_and_model=True; scf_save_directory_in_archive=False
```

程序核对了三组记录的模型、结构和本征态计数；最后的 `False` 对应包内未保存 SCF 保存目录。它支持按这些字段识别存档，不建立密度文件之间的逐字节身份关系。更密子网格能否满足带隙、DOS 或其他目标，由相应分析页的对照决定。[本次 JSON](/Atlas/examples/enrichment-20261003/basics/si-branch-audit.json)与[实际输出](/Atlas/examples/enrichment-20261003/basics/si-branch-audit.txt)一起保留。


## 密度差必须来自匹配的父计算

界面差分密度要把异质结和两个冻结组分放在相同晶胞、相同原子位置参照和兼容 FFT 网格上，再按[差分电荷](/Atlas/m/delta-charge/)的定义相减。单独把两个自由层优化到不同晶格，所得密度不能直接逐格相减。若要分辨界面杂化与形变的作用，可以另外计算各自由层；那是另一个参照问题。

<figure>
<img src="/Atlas/figures/literature/qiu2022-ba2n-fig2bd.png" alt="Ba2N论文Fig.2(b,d)原图：DOS及ELF俯视侧视图" />
<figcaption>Qiu 等，Phys. Rev. B 105, 165101 (2022)，原文第 3 页 Fig. 2(b,d)：单层 Ba₂N 的总及投影 DOS，以及 ELF=0.5 的俯视和侧视等值面。虚线圈标出空球 X 的位置。<a href="https://doi.org/10.1103/PhysRevB.105.165101">论文原文</a>。</figcaption>
</figure>

自洽密度也为 [ELF](/Atlas/m/elf/)与[静电势](/Atlas/m/electrostatic-potential/)提供起点。[Ba₂N 原文 Fig. 2(d)，第 165101-3 页](https://doi.org/10.1103/PhysRevB.105.165101)用 ELF=0.5 的俯视和侧视等值面，把表面电子区域与 Ba–N–Ba 原子面对应；同页 Fig. 2(b)再比较总 DOS、Ba-d、N-p 与空球 X 投影。侧视图先定位区域，投影曲线再检查它参与哪些能量附近的态；ELF 的等值面体积本身不是电子数。要接续这种图法，先从自己的匹配 SCF 用 `pp.x` 导出所需标量网格，再用 VESTA 统一晶胞、视向和阈值检查；[ELF 页](/Atlas/m/elf/vasp/)已有另一份 Fe 网格的实际 VESTA 展示，可以参照操作。这里的 Si OUT 尚未提供 ELF 图，公开包也没有父密度与波函数，不能从总能和电子数画出那片等值面。进入 [DFPT](/Atlas/m/phonon-dfpt/qe/)时，密度和波函数同样必须对应待求响应的最终结构。
