## 从电子自洽读到同一结构的能量与力

密度网格加密后，总能量只变几 meV，原子力是否也已足够稳定？这个问题会直接影响后面的结构优化与有限位移声子。本页用 CP2K 2026.2 的一个周期水分子，把固定几何的电子迭代、解析力、两套密度网格和一个中心有限差分接起来。四份真实计算均完成 29 步 SCF；同一份输出中的能量与力仍要分别比较。

下载[输入、完整 OUT、官方数据与全部 Python 源码](/Atlas/examples/cp2k-water-files.tar.gz)，解包得到 `cp2k-water/`。原水分子的相对坐标来自 [CP2K v2026.2 官方 H2O-fixed 示例](https://github.com/cp2k/cp2k/blob/v2026.2/tests/QS/regtest-gpw-1/H2O-fixed.inp)。这里将三个原子统一平移 (4,4,4) Å，采用 8 Å 的 XYZ 周期立方胞、PBE/GPW 和固定离子；官方原例的胞、泛函与优化流程不同，其原输入随包保存。当前能量属于这个含周期镜像的有限模型。

## 高斯轨道基组与密度网格分别设置

GPW 用高斯基组展开轨道，将密度等高斯乘积表示在实空间网格上。O/H 使用 `DZVP-MOLOPT-SR-GTH-q6/q1` 与 `GTH-PBE-q6/q1`，一共 8 个价电子、闭壳层。基组和赝势全文来自同版本官方 `BASIS_MOLOPT` 与 `GTH_POTENTIALS`，通过输入中的相对路径加载。

[`MGRID` 的 `CUTOFF`](https://manual.cp2k.org/cp2k-2026_2-branch/CP2K_INPUT/FORCE_EVAL/DFT/MGRID.html#CUTOFF)规定最细网格，`REL_CUTOFF`影响高斯乘积分配到哪一级网格。提高前者并不会扩大高斯轨道基组；这两个数也不能直接对应 QE 的 `ecutwfc/ecutrho`。本次两个网格参数同时提高，只能读出这组联动变化，不能单独归因于其中一个参数。

| 算例 | CUTOFF / REL_CUTOFF（Ry） | 第二个原子 H1 的 y 坐标改动 |
| --- | --- | --- |
| baseline | 600 / 60 | 0 |
| grid_control | 800 / 80 | 0 |
| H1_y_plus | 600 / 60 | +0.005 Å |
| H1_y_minus | 600 / 60 | −0.005 Å |

四份输入的其余设置相同，`NGRIDS=4`、`EPS_SCF=1e-10`、`EPS_DEFAULT=1e-12`，OT 采用 DIIS 与 FULL_SINGLE_INVERSE。`ENERGY_FORCE`在固定坐标求电子解及受力，不执行离子优化。下面是基线的完整便携输入；两条数据路径改为 `../../data/`，这些路径派生副本没有再次运行。实际 OUT 保留完整科学数值、警告与计时，主机身份和路径已简写。

```text
&GLOBAL
 PROJECT baseline
 RUN_TYPE ENERGY_FORCE
 PRINT_LEVEL MEDIUM
&END GLOBAL
&FORCE_EVAL
 METHOD QS
 &DFT
  BASIS_SET_FILE_NAME ../../data/BASIS_MOLOPT
  POTENTIAL_FILE_NAME ../../data/GTH_POTENTIALS
  CHARGE 0
  MULTIPLICITY 1
  &QS
   METHOD GPW
   EPS_DEFAULT 1.0E-12
  &END QS
  &MGRID
   CUTOFF 600
   REL_CUTOFF 60
   NGRIDS 4
  &END MGRID
  &SCF
   SCF_GUESS ATOMIC
   EPS_SCF 1.0E-10
   MAX_SCF 100
   &OT
    MINIMIZER DIIS
    PRECONDITIONER FULL_SINGLE_INVERSE
   &END OT
  &END SCF
  &XC
   &XC_FUNCTIONAL PBE
   &END XC_FUNCTIONAL
  &END XC
 &END DFT
 &SUBSYS
  &CELL
   ABC 8.0 8.0 8.0
   PERIODIC XYZ
  &END CELL
  &COORD
   O 4.000000000000 4.000000000000 3.934413000000
   H 4.000000000000 3.242864000000 4.520545000000
   H 4.000000000000 4.757136000000 4.520545000000
  &END COORD
  &KIND O
   BASIS_SET DZVP-MOLOPT-SR-GTH-q6
   POTENTIAL GTH-PBE-q6
  &END KIND
  &KIND H
   BASIS_SET DZVP-MOLOPT-SR-GTH-q1
   POTENTIAL GTH-PBE-q1
  &END KIND
 &END SUBSYS
 &PRINT
  &FORCES ON
   FORCE_UNIT hartree/bohr
   NDIGITS 12
  &END FORCES
 &END PRINT
&END FORCE_EVAL
```

## 在完整 OUT 中定位电子结束、能量和三行力

四份输出都含 `SCF run converged in 29 steps` 与末尾 `PROGRAM ENDED AT`，stderr 为空。实际启动使用 32 MPI ranks、每 rank OMP 1；下面给出程序调用的可读表示，实际绝对 launcher/binary 路径写成程序名：

```bash
mpirun --map-by hwthread --bind-to hwthread -np 32 cp2k.psmp -i input.inp > cp2k.out 2> cp2k.err
```

未来使用便携输入时，从各自 `cases/` 子目录启动，以正确解析 `../../data/`；MPI/OMP 要匹配所用程序和计算资源。已有四份 OUT 都保留“non-square number of MPI ranks”的性能警告。另一次 `--version` 调用打印版本后在格式输出处发生 Fortran 错误，退出码 2，记录在 `version_observation/`；它没有替代下面四份正常 ENERGY_FORCE 的状态。

[基线完整 OUT](/Atlas/examples/cp2k-water/cases/baseline/cp2k.out)先读电子迭代，再定位下面这段原生输出。CP2K 2026.2 这里的 `FORCES|` 表按输入的 O/H/H 原子顺序给 x、y、z 与范数，单位为 Hartree/Bohr；范数不能当第四个笛卡尔分量。

```text
 ENERGY| Total FORCE_EVAL ( QS ) energy [hartree]            -17.219592377082307

 FORCES| Atomic forces [hartree/bohr]
 FORCES|   Atom     x                   y                   z                   |f|
 FORCES|      1  2.820077149308E-13  9.499540043478E-12 -1.531714580670E-02   1.531714580670E-02
 FORCES|      2  5.735346078415E-12 -9.859539145479E-03  7.516648287748E-03   1.239800442180E-02
 FORCES|      3 -4.147357452745E-12  9.859539137423E-03  7.516648285454E-03   1.239800441400E-02
 FORCES| Sum     1.869996340601E-12  1.442873598378E-12 -2.838492334990E-04
 FORCES| Total atomic force                                                   2.838492334990E-04

```

总能为整胞 `ENERGY|`，单位 Hartree。换算力时同时转换能量与长度：

$$
F_{\mathrm{eV/\AA}}=F_{\mathrm{Ha/Bohr}}\frac{27.211386245988}{0.529177210903}.
$$

H1 的 y 分量 −0.009859539145479 Ha/Bohr 对应 −0.5069978872242975 eV/Å。O 的 z 力约 −0.7876393052 eV/Å，两个 H 的 z 力各约 +0.3865215954 eV/Å；固定几何并未达到小原子力的结构。`EPS_SCF`给的是本次电子停止设置，不是每个力分量的误差界。

## 提取程序：从原生表到物理 CSV

下面提示词给出本例的实际格式、列和算术，便于检查生成的程序。

> 编写 Python 3 标准库命令行后处理。case 子命令读取一个算例的 cp2k.out，核对 CP2K 2026.2、明确 SCF 收敛与程序结束，读取最后一个 ENERGY| 的 Hartree 总能和最后一个 FORCES| Atomic forces [hartree/bohr] 表。要求原子序号恰为 1/2/3，按该输入的 O/H/H 顺序读取 xyz 三分量，拒绝缺行与非有限数。保留 Ha/Bohr，用 1 Ha=27.211386245988 eV、1 Bohr=0.529177210903 Å 换算 eV/Å，并求三分量总力。compare 子命令读取 baseline/grid_control/H1_y_plus/H1_y_minus 的提取结果，计算加密网格的能量差和最大力分量差；H1-y 中心差分步长 h=0.005 Å，计算 −(Eplus−Eminus)/(2h)，与基线第二个原子的 y 解析力比较。另给完整 CSV 导出器，每行一个算例中的原子，固定列序 case、energy_Ha、atom_index、element、Fx/Fy/Fz_Ha_Bohr、Fx/Fy/Fz_eV_A。原始 OUT 只读，不能调整数值来消除总力残差或有限差分差异。

[完整解析与比较程序](/Atlas/examples/cp2k-water/source/postprocess.py)与[CSV 导出器](/Atlas/examples/cp2k-water/source/export_csv.py)只用 Python 标准库。程序间的数值中间文件自动产生；核对时直接对照原 OUT 和[12 行原生力 CSV](/Atlas/examples/cp2k-water/native_energy_forces.csv)。同一算例的 `energy_Ha`在三行重复，表示同一整胞能量，不能再次求和成三倍能量。

<details><summary>完整 postprocess.py</summary>

```python
"""Read CP2K 2026.2 ENERGY_FORCE output and compare density grids and one finite difference."""
from pathlib import Path
import hashlib,json,math,re,sys
HA_EV=27.211386245988;BOHR_A=.529177210903
def case(p):
    t=(p/'cp2k.out').read_text()
    assert 'CP2K version 2026.2' in t and 'PROGRAM ENDED AT' in t
    assert re.search(r'SCF run converged in\s+\d+\s+steps',t) and 'SCF run NOT converged' not in t
    energies=re.findall(r'ENERGY\|\s+Total FORCE_EVAL.*?energy\s*\[hartree\]\s*:?\s*([-+\d.Ee]+)',t);assert energies
    en=float(energies[-1]);assert math.isfinite(en)
    # CP2K2026.2 force_env_utils.F uses FORCES|, atom index and xyz/norm,
    # rather than the older ATOMIC FORCES/Kind/Element table.
    header='FORCES| Atomic forces [hartree/bohr]';assert header in t
    b=t.rsplit(header,1)[1]
    rows=re.findall(r'^\s*FORCES\|\s*(\d+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+)\s+([-+\d.Ee]+)\s*$',b,re.M)[:3]
    assert [int(x[0]) for x in rows]==[1,2,3]
    f=[[float(v) for v in x[1:4]] for x in rows];assert all(math.isfinite(v) for row in f for v in row)
    rec={'status':'NATIVE_ENERGY_FORCE_PARSER_PASS','energy_Ha':en,'forces_Ha_Bohr':f,'forces_eV_A':[[x*HA_EV/BOHR_A for x in row] for row in f],'sum_force_Ha_Bohr':[sum(row[j] for row in f) for j in range(3)],'nonzero_force_above_print_halfunit':max(abs(x) for row in f for x in row)>5e-13,'scientific_acceptance':False,'limits':'Parser/numericalreceipt only; no convergence acceptance or cross-pseudopotential absoluteenergy comparison'}
    (p/'postprocessing.json').write_text(json.dumps(rec,indent=2)+'\n');return rec
def compare(p):
    r={x:json.loads((p/x/'postprocessing.json').read_text()) for x in ['baseline','grid_control','H1_y_plus','H1_y_minus']}
    fd=-(r['H1_y_plus']['energy_Ha']-r['H1_y_minus']['energy_Ha'])/.01*BOHR_A
    f=r['baseline']['forces_Ha_Bohr'][1][1]
    d={'status':'BASELINE_MINIMAL_CONTROL_DIAGNOSTIC_COMPLETE','cases':r,'H1_y_FD_Ha_Bohr':fd,'H1_y_analytic_Ha_Bohr':f,'FD_minus_analytic_Ha_Bohr':fd-f,'grid_delta_energy_Ha':r['grid_control']['energy_Ha']-r['baseline']['energy_Ha'],'grid_force_component_max_delta_Ha_Bohr':max(abs(x-y) for a,b in zip(r['grid_control']['forces_Ha_Bohr'],r['baseline']['forces_Ha_Bohr']) for x,y in zip(a,b)),'scientific_acceptance':False,'limits':['SamePBE/basis/GTH/cell energy differences only.','OneFDstep tests energy-force consistency, noth->0 convergence.','Two density grids do not converge Gaussianbasis orperiodiccell.','SCFcriterion is notrigorous force/energy error bar.','NoPhonopy calculation authorized bythisreceipt.']}
    (p/'energy_force_comparison.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
if __name__=='__main__':
    mode,path=sys.argv[1:];{'case':case,'compare':compare}[mode](Path(path))
```

</details>

<details><summary>完整 export_csv.py</summary>

```python
from pathlib import Path
import csv,json,sys
p=Path(sys.argv[1]);rows=[]
for case in ['baseline','grid_control','H1_y_plus','H1_y_minus']:
 r=json.loads((p/'cases'/case/'postprocessing.json').read_text())
 for i,(native,ev) in enumerate(zip(r['forces_Ha_Bohr'],r['forces_eV_A']),1):rows.append([case,r['energy_Ha'],i,['O','H','H'][i-1],*native,*ev])
with (p/'native_energy_forces.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['case','energy_Ha','atom_index','element','Fx_Ha_Bohr','Fy_Ha_Bohr','Fz_Ha_Bohr','Fx_eV_A','Fy_eV_A','Fz_eV_A']);w.writerows(rows)
print('Exported12actualatomrows; nativeHa/HaBohr and converted eV/A')
```

</details>

解包后在 `cp2k-water/`运行以下后处理。本次已对四份真实 OUT 执行这些相同解析/导出步骤；它们不调用 CP2K。

```bash
python3 source/postprocess.py case cases/baseline
python3 source/postprocess.py case cases/grid_control
python3 source/postprocess.py case cases/H1_y_plus
python3 source/postprocess.py case cases/H1_y_minus
python3 source/postprocess.py compare cases
python3 source/export_csv.py .
```

CSV 中的四组能量来自各自实际 OUT：

| 算例 | 整胞能量（Ha） |
| --- | --- |
| baseline | −17.219592377082307 |
| grid_control | −17.219517870609640 |
| H1_y_plus | −17.219482112231460 |
| H1_y_minus | −17.219668655138822 |

## 能量差小，不代表力分量也稳定

把 baseline 与 grid_control 的同一几何、PBE、基组和赝势成对比较，能量变化为 +2.0274244 meV/cell，最大力分量变化为 0.0287235083 eV/Å。后者出现在 O 的 z 分量；不能将前者这个几 meV 的数直接换成力精度。本次同时改变两个 MGRID 参数，没有区分它们各自的贡献。

三原子总力的 z 分量，基线为 −0.0145961144 eV/Å、加密网格为 +0.0146234856 eV/Å。内部各原子力相加有残差，且两网格改变后翻转符号；这与单个原子的未优化受力是两类读数。这两套网格没有单独分离误差来源，不能据此确认具体机制。它提醒后续力敏感任务还要检查网格表示、电子精度与坐标采样，不能通过减掉平均力把原始结果“校正”为零。

## 用同一能量的中心差分检查解析力

H1-y 两次位移仍用 600/60 Ry 网格。因输入位移以 Å 给出，先计算 eV/Å 的导数，或将 Hartree/Å 的导数乘 Bohr 的 Å 长度，得到 Ha/Bohr：

$$
F_y^{\mathrm{FD}}=-\frac{E(y+h)-E(y-h)}{2h},\qquad h=0.005\,\mathrm{\AA}.
$$

用上表真实能量与转换常数，可得 −0.5076091103652093 eV/Å，与基线解析力 −0.5069978872242975 eV/Å 的差为 −0.0006112231409118 eV/Å。`minus`侧能量更低，负力方向与降低能量的方向相符；差分负号、原子序号和单位都在这里得到具体核对。

这组差值来自一个 h 和两套密度网格。若进入优化或声子任务，需按目标力精度继续分开检查网格、电子阈值、基组、周期胞和 h 的敏感性；当前数据没有给出 h→0 极限，也没有力常数或 Phonopy 输出。已有的[参数收敛方法](/Atlas/m/convergence/)解释怎样保持其它设置不变地比较；[原子弛豫](/Atlas/m/relax/)与[有限位移声子](/Atlas/m/phonon-finite-disp/qe/)分别把力接到坐标更新与匹配位移受力。

参数与原生单位的详细定义见 [CP2K 2026.2 MGRID](https://manual.cp2k.org/cp2k-2026_2-branch/CP2K_INPUT/FORCE_EVAL/DFT/MGRID.html)、[SCF](https://manual.cp2k.org/cp2k-2026_2-branch/CP2K_INPUT/FORCE_EVAL/DFT/SCF.html) 和 [FORCES](https://manual.cp2k.org/cp2k-2026_2-branch/CP2K_INPUT/FORCE_EVAL/PRINT/FORCES.html)。
