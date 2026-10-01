有效质量取决于带边附近的局部曲率。Si 的导带谷位于 Γ–X 之间，先由[带隙计算](/Atlas/m/band-gap/qe/)定位其附近区域，再沿谷的纵向和两个横向加密采样。拟合范围应围绕同一个极值点，不能用整条 Γ–X 能带的一条抛物线代替局部曲率。

`mass` 使用 Si 的 `12³` 父 SCF 密度，`ecutwfc/ecutrho=60/640 Ry`，固定晶胞、PBE、无 SOC。父密度来自独立完成的 `k12/tmp/si.save`。复制后，精细采样在自己的目录中读写；`k12` 保留原样。

[pw.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_PW.html) · [PWscf 用户手册](https://www.quantum-espresso.org/Doc/pw_user_guide/) · [bands.x 输入说明](https://www.quantum-espresso.org/Doc/INPUT_BANDS.html)

[下载 Si 算例](/Atlas/examples/si-pbe-electronic-files.tar.gz)后保留目录结构，在 `si-pbe` 中运行绘图脚本。本页图读取 `mass/longitudinal.csv` 和 `mass/mass-fits.json`；横向与父密度复核结果另存于 `mass/mass-checks.csv`。包内输入、输出和 XML 可供复核，但不含可接续计算的 `tmp/si.save`，重新求能级前需重建下文对应的父 SCF 密度。

## 围绕已定位的导带谷加密采样

重新计算这条链时，先取用收敛算例的真实 [k12/scf.in](/Atlas/examples/basics-si-convergence/si-pbe/k12/scf.in)，在独立 `k12` 目录中准备相同赝势并完成 SCF；运行方法见 [Si SCF](/Atlas/m/scf/qe/)。这份输入保持同一晶胞与 `60/640 Ry`，末尾网格为 `12 12 12 0 0 0`，运行后生成 `k12/tmp/si.save`。SCF 入门页的 `8³` 密度属于另一套父网格，重建时须使用这里的 `12³` 输入，才能与本文有效质量数值配对。

完整电子下载包已提供 `mass/mass.in`。下面 `cp scf/scf.in` 与 `vi` 是作者从起始 SCF 输入编辑质量采样输入的历史记录；跟算时直接核对包内完整 `mass/mass.in`，再把已重建的 `k12/tmp` 复制到 `mass`。质量输入的 101 个点、计算类型和空带数与父 SCF 输入各有用途。

```text
[preston@preston-System-Product-Name si-pbe]$ cp -a k12/tmp mass/
[preston@preston-System-Product-Name si-pbe]$ cp scf/scf.in mass/mass.in
[preston@preston-System-Product-Name si-pbe]$ vi mass/mass.in
```

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 38 mass/mass.in
&CONTROL
  calculation = 'bands'
  verbosity = 'high'
  prefix = 'si'
  outdir = './tmp'
  pseudo_dir = '../pseudo'
  tprnfor = .true.
  tstress = .true.
/
&SYSTEM
  ibrav = 2
  A = 5.397607551
  nbnd = 8
  nat = 2
  ntyp = 1
  ecutwfc = 60
  ecutrho = 640
  occupations = 'fixed'
/
&ELECTRONS
  conv_thr = 1.0d-12
/
ATOMIC_SPECIES
Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS alat
Si 0.00 0.00 0.00
Si 0.25 0.25 0.25
K_POINTS tpiba
101
0.70000000 0.00000000 0.00000000 1.0
0.70250000 0.00000000 0.00000000 1.0
0.70500000 0.00000000 0.00000000 1.0
0.70750000 0.00000000 0.00000000 1.0
0.71000000 0.00000000 0.00000000 1.0
0.71250000 0.00000000 0.00000000 1.0
0.71500000 0.00000000 0.00000000 1.0
0.71750000 0.00000000 0.00000000 1.0
0.72000000 0.00000000 0.00000000 1.0
[preston@preston-System-Product-Name si-pbe]$
```

这里用 `calculation='bands'` 读取已经得到的密度，并计算明确指定的 k 点。保留 8 条能带，Si 原胞有 8 个价电子，当前非自旋极化模型中前 4 条占据，第 5 条是要跟踪的最低导带。这里保持密度固定，`conv_thr=1.0d-12` 不表示又做了一轮密度自洽；在未另设 `diago_thr_init` 的非自洽计算中，它参与确定默认的本征值求解阈值。收紧这个输入仍不能代替检查每个本征值是否正常求出。

`K_POINTS tpiba` 后的 `101` 是点数。x 从 0.70 取到 0.95，步长 0.0025，y、z 为零；这些坐标的单位是 `2π/a`。文件最后几行如下，实际计算确实覆盖了谷的两侧，而不是只从极小值向一边取点。

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 6 mass/mass.in
0.93750000 0.00000000 0.00000000 1.0
0.94000000 0.00000000 0.00000000 1.0
0.94250000 0.00000000 0.00000000 1.0
0.94500000 0.00000000 0.00000000 1.0
0.94750000 0.00000000 0.00000000 1.0
0.95000000 0.00000000 0.00000000 1.0
[preston@preston-System-Product-Name si-pbe]$
```

完整输入可下载为[mass.in](/Atlas/examples/si-pbe-electronic/mass/mass.in)。这份输入比普通能带路径密，是因为最后的曲率来自局部能量差；若只有两三个很远的点，图上像抛物线也不足以保证拟合可靠。

```text
[preston@preston-System-Product-Name si-pbe]$ cat mass/run.sh
#!/bin/bash
#SBATCH --job-name=atlas-si-mass
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=_out.%j.log
#SBATCH --error=_err.%j.log
unset DISPLAY XAUTHORITY
ulimit -s unlimited
ulimit -c 0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
/usr/bin/mpirun --bind-to none -np 4 <qe_bin>/pw.x -in mass.in > mass.out 2> mass.err
[preston@preston-System-Product-Name si-pbe]$
```

```text
[preston@preston-System-Product-Name si-pbe]$ cd mass
[preston@preston-System-Product-Name mass]$ sbatch run.sh
Submitted batch job 785
[preston@preston-System-Product-Name mass]$ cd ..
```

运行的头部确认了实际版本和 MPI 进程数。中间是每个 k 点的本征值，末尾给出程序计时与结束标志。这里的 `mass.out`、横向采样输出和 `14³` 父密度复核输出均没有 `eigenvalues not converged` 提示。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 33 mass/mass.out

     Program PWSCF v.7.5 starts on 22Sep2026 at 21:40:13

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org",
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on     4 processors

     MPI processes distributed on     1 nodes
     8001 MiB available memory on the printing compute node when the environment starts

     Reading input from mass.in

     Current dimensions of program PWSCF are:
     Max number of different atomic species (ntypx) = 10
     Max number of k-points (npk) =  40000
     Max angular momentum in pseudopotentials (lmaxx) =  4

     Atomic positions and unit cell read from directory:
     ./tmp/si.save/


     R & G space division:  proc/nbgrp/npool/nimage =       4
     Subspace diagonalization in iterative solution of the eigenvalue problem:
     a serial algorithm will be used


[preston@preston-System-Product-Name si-pbe]$
```

```text
[preston@preston-System-Product-Name si-pbe]$ tail -n 12 mass/mass.out
     davcio       :      0.01s CPU      0.01s WALL (     202 calls)

     Parallel routines

     PWSCF        :     18.61s CPU     19.43s WALL


   This run was terminated on:  21:40:32  22Sep2026

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
[preston@preston-System-Product-Name si-pbe]$
```

本次纵向采样原生用时约 19 秒。[完整 mass.out](/Atlas/examples/si-pbe-electronic/mass/mass.out)适合人工查看；数值提取读取同一次计算的[data-file-schema.xml](/Atlas/examples/si-pbe-electronic/mass/data-file-schema.xml)，避免从只打印有限小数的屏幕表中做二阶差分。这个 XML 的本征值以 Hartree 给出，脚本先换算成 eV。k 坐标则用本例实际的 `alat` 转为 Å⁻¹。

```text
[preston@preston-System-Product-Name si-pbe]$ head -n 7 mass/longitudinal.csv
kx_tpiba,kx_inv_A,band5_eV
0.7,0.8148479995013461,7.043633109580449
0.7025,0.8177581709281366,7.039997615730428
0.705,0.8206683423549271,7.036421417077702
0.7075,0.8235785137817176,7.032904654922736
0.71,0.8264886852085082,7.029447505916328
0.7125,0.8293988566352989,7.026050133682778
[preston@preston-System-Product-Name si-pbe]$
```

`kx_tpiba` 和 `kx_inv_A` 两列同时保留。换算为

```text
k [Å⁻¹] = k [2π/a] × 2π / a [Å]
E [eV]  = E [Hartree] × 27.211386245988
```

## 用局部曲率求方向有效质量

先在采样点中找第 5 条能带的最低值，再以它为中心取对称窗口。拟合的是 `E=Aq²+Bq+C`，其中 `q=kₓ−k_center` 是相对采样最低点的波矢偏移，以 Å⁻¹ 计。`B` 允许真实谷底稍微偏离这个采样点；拟合后的偏移为 `q₀=−B/(2A)`，绝对位置为 `kₓ=k_center+q₀`。这次 `±0.02 Å⁻¹` 的纵向窗口得到谷底 `kx≈0.84430088×2π/a`。

有效质量由能量对波矢的二阶导数决定。对这个二次式，`d²E/dk²=2A`，因此

```text
m*/mₑ = [ℏ²/(2mₑ)] / A
       = 3.80998211615486 [eV·Å²] / A [eV·Å²]
```

拟合前需将波矢转换为 Å⁻¹。把第几个 k 点作为横轴、或直接把 `tpiba` 数字塞进该式，都会改变曲率的尺度。

随后固定拟合出的 x 坐标，分别沿 y 和 z 方向取 33 个点。横向输入和输出保存在[mass-transverse/mass.in](/Atlas/examples/si-pbe-electronic/mass-transverse/mass.in)、[mass-transverse/mass.out](/Atlas/examples/si-pbe-electronic/mass-transverse/mass.out)。另一个独立目录 `mass-k14` 保持同样的 101 个纵向 k 点，只把父 SCF 密度由 `12³` 改为 `14³`。它用于区分“拟合窗口造成的变化”和“父密度采样造成的变化”。

| 方向 / 父 SCF | 拟合半窗 / Å⁻¹ | 点数 | m*/mₑ | 残差 RMS / meV |
| --- | ---: | ---: | ---: | ---: |
| 纵向 x / 12³ | 0.01 | 7 | 0.956455 | 0.000212 |
| 纵向 x / 12³ | 0.02 | 13 | 0.955904 | 0.000866 |
| 纵向 x / 12³ | 0.03 | 21 | 0.955577 | 0.003613 |
| 纵向 x / 14³ | 0.01 | 7 | 0.956454 | 0.000212 |
| 纵向 x / 14³ | 0.02 | 13 | 0.955903 | 0.000866 |
| 纵向 x / 14³ | 0.03 | 21 | 0.955576 | 0.003613 |
| 横向 y / 12³ | 0.01 | 7 | 0.191769 | 0.000070 |
| 横向 y / 12³ | 0.02 | 13 | 0.191935 | 0.000712 |
| 横向 y / 12³ | 0.03 | 21 | 0.192320 | 0.005181 |
| 横向 z / 12³ | 0.01 | 7 | 0.191769 | 0.000070 |
| 横向 z / 12³ | 0.02 | 13 | 0.191935 | 0.000712 |
| 横向 z / 12³ | 0.03 | 21 | 0.192320 | 0.005181 |

对 `±0.02 Å⁻¹` 窗口，本例纵向质量约 **0.955904 mₑ**，两个横向质量都约 **0.191936 mₑ**。y、z 结果相同，与这个 Si 谷的对称性相容。窗口从 0.01 增到 0.03 Å⁻¹ 时，纵向质量约改变 0.09%，横向约改变 0.29%；更宽的窗口还带来更大的二次拟合残差，因此局部二次近似的窗口应由残差与质量变化共同选择。父密度从 `12³` 改到 `14³` 后，纵向结果的变化约为 `10⁻⁶ mₑ`，比本次窗口变化小。

这些是给定 PBE、赝势、晶胞和无 SOC 模型下的方向曲率质量。输运分析还需散射时间；处理带边简并、非抛物线或 SOC 混合时，须核对分支与拟合窗口。

<span id="把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
<span id="h-把后处理要求写成提示词" class="legacy-anchor" aria-hidden="true"></span>
## 曲率拟合的输入与检查

拟合程序需要使用笛卡尔波矢、统一能量单位，并分别报告各窗口的曲率。下面给出输入约定和应保留的中间量。

```text
编写 Si 导带谷曲率分析程序，使用 Python 3、NumPy 和 Matplotlib。
输入：mass/longitudinal.csv、mass-fits.json、mass-checks.csv，以及 mass-transverse、mass-k14 的 XML。能量 eV，拟合 k 为 Å⁻¹，同时保留 tpiba。
方法：围绕采样谷底取 ±0.01/0.02/0.03 Å⁻¹，拟合 E=Aq²+Bq+C，顶点 −B/(2A)，m*/me=3.80998211615486/A；分别处理纵向、横向和 12³/14³ 父密度。
检查：点数、有限值、正曲率、残差；±0.02 Å⁻¹ 纵向约 0.955904 me、横向约 0.191936 me。
输出：源码、依赖、命令、拟合表、PNG/SVG/PDF，结果标为 PBE 无 SOC 模型的方向曲率质量。
```

## 后处理源码与运行

完整源码：[analyse_electronic.py](/Atlas/examples/si-pbe-electronic/analyse_electronic.py) · [analyse_mass_checks.py](/Atlas/examples/si-pbe-electronic/analyse_mass_checks.py) · [plot_si.py](/Atlas/examples/si-pbe-electronic/plot_si.py) · [atlas_plot_style.py](/Atlas/examples/si-pbe-electronic/atlas_plot_style.py)。Python 3 依赖：NumPy、Matplotlib。

<details>
<summary>analyse_electronic.py 的完整源码</summary>

```python
from pathlib import Path
import csv, json, re, hashlib, xml.etree.ElementTree as ET
import numpy as np
ROOT=Path(__file__).resolve().parent
RY_EV=13.605693122994
HA_EV=2*RY_EV
BOHR_ANG=0.529177210903
HBAR2_OVER_2ME=3.80998211615486 # eV Angstrom^2

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def table(path,header,rows):
    with path.open('w') as f:
        w=csv.writer(f);w.writerow(header);w.writerows(rows)
def read_xml(directory):
    x=ET.parse(ROOT/directory/'data-file-schema.xml').getroot()
    output=x.find('output')
    states=output.find('band_structure').findall('ks_energies')
    k=np.array([[float(v) for v in s.find('k_point').text.split()] for s in states])
    e=np.array([[float(v)*HA_EV for v in s.find('eigenvalues').text.split()] for s in states])
    alat=float(output.find('atomic_structure').attrib['alat'])*BOHR_ANG
    return k,e,alat

# Gap on uniform meshes; a local line refinement is a separate piece of evidence.
gaps=[]
for name in ['gap12','gap18-cg','gap24-cg','gap24-k12-cg']:
    if not (ROOT/name/'data-file-schema.xml').exists():continue
    k,e,a=read_xml(name)
    v=e[:,3]; c=e[:,4];iv=int(v.argmax());ic=int(c.argmin())
    row={'directory':name,'nks':len(k),'vbm_eV':float(v[iv]),'cbm_eV':float(c[ic]),'gap_eV':float(c[ic]-v[iv]),'minimum_direct_gap_eV':float((c-v).min()),'vbm_k_tpiba':k[iv].tolist(),'cbm_k_tpiba':k[ic].tolist()}
    gaps.append(row)
    table(ROOT/name/'edges.csv',['kx_tpiba','ky_tpiba','kz_tpiba','vbm_band4_eV','cbm_band5_eV'],np.c_[k,v,c])
(ROOT/'gap-results.json').write_text(json.dumps(gaps,indent=2)+'\n')

# Fits use physical k in inverse Angstrom, not a path-point index.
k,e,a=read_xml('mass'); kcart=k*2*np.pi/a
imin=int(e[:,4].argmin());center=kcart[imin,0]
fits=[]
for window in [.010,.020,.030]:
    take=np.abs(kcart[:,0]-center)<=window+1e-12
    coeff=np.polyfit(kcart[take,0]-center,e[take,4],2)
    fit=np.polyval(coeff,kcart[take,0]-center)
    x0=center-coeff[1]/(2*coeff[0]);e0=coeff[2]-coeff[1]**2/(4*coeff[0])
    fits.append({'half_window_inv_A':window,'npoints':int(take.sum()),'quadratic_A_eVA2':float(coeff[0]),'minimum_k_inv_A':float(x0),'minimum_k_tpiba':float(x0*a/(2*np.pi)),'minimum_energy_eV':float(e0),'mass_over_me':float(HBAR2_OVER_2ME/coeff[0]),'rms_residual_meV':float(np.sqrt(np.mean((fit-e[take,4])**2))*1000)})
(ROOT/'mass/mass-fits.json').write_text(json.dumps(fits,indent=2)+'\n')
table(ROOT/'mass/longitudinal.csv',['kx_tpiba','kx_inv_A','band5_eV'],np.c_[k[:,0],kcart[:,0],e[:,4]])

# Actual 3D local cube: retain every point, not only a plotted 2D slice.
if (ROOT/'band3d/data-file-schema.xml').exists():
    k,e,a=read_xml('band3d')
    assert len(k)==891
    table(ROOT/'band3d/cube.csv',['kx_tpiba','ky_tpiba','kz_tpiba','kx_inv_A','ky_inv_A','kz_inv_A','band5_eV'],np.c_[k,k*2*np.pi/a,e[:,4]])

# Fatband weights are squared complex projection amplitudes. Take energies
# from PW QEXSD (Hartree); the independent atomic_proj E values use Ry.
k,e,a=read_xml('bands-cg')
pr=ET.parse(ROOT/'bands-cg/atomic_proj.xml').getroot().find('EIGENSTATES')
projs=pr.findall('PROJS'); pk=pr.findall('K-POINT');pe=pr.findall('E')
assert len(projs)==len(k)
rows=[];distance=np.r_[0,np.cumsum(np.linalg.norm(np.diff(k,axis=0),axis=1))]
for ik,proj in enumerate(projs):
    kp=np.array([float(v) for v in pk[ik].text.split()])
    ep=np.array([float(v)*RY_EV for v in pe[ik].text.split()])
    assert np.max(np.abs(kp-k[ik]))<1e-9 and np.max(np.abs(ep-e[ik]))<1e-6
    weights=[]
    for orbital in proj.findall('ATOMIC_WFC'):
        z=np.array([float(v) for v in orbital.text.split()]).reshape(-1,2)
        weights.append((z*z).sum(axis=1))
    weights=np.array(weights)
    assert weights.shape==(8,8)
    for ib in range(8):
        sw=weights[[0,4],ib].sum();pw=weights[[1,2,3,5,6,7],ib].sum()
        rows.append([ik+1,ib+1,distance[ik],*k[ik],e[ik,ib],sw,pw,sw+pw])
table(ROOT/'bands-cg/fatband.csv',['ik','iband','path_distance_tpiba','kx_tpiba','ky_tpiba','kz_tpiba','energy_eV','Si_s_weight','Si_p_weight','projection_norm'],rows)

print('gaps:',len(gaps),'fits:',len(fits),'fatband rows:',len(rows))
```

</details>

`analyse_electronic.py` 是完整电子下载包的共用提取器：一次运行读取带隙网格 XML，并同时读取 `mass/data-file-schema.xml`、`bands-cg/data-file-schema.xml` 和 `bands-cg/atomic_proj.xml`，生成带隙、纵向质量及胖带数据；包内的局部三维 XML 存在时也会提取该网格。因此运行它时保留整包目录及这些跨页面数据。上面的提示词描述本页性质的分析逻辑，复用现有共用脚本时还需满足这组文件依赖。只重画已有 CSV/JSON 时，直接执行 `python3 plot_si.py mass`。

解压本页示例包后，在 `si-pbe` 根目录执行：

```bash
python3 -m pip install numpy matplotlib
python3 analyse_electronic.py
python3 analyse_mass_checks.py
python3 plot_si.py mass
```

本例保存的提取运行记录如下：

```text
[preston@preston-System-Product-Name si-pbe]$ python3 analyse_mass_checks.py
longitudinal       window=0.01  n= 7  m/me=0.95645509  RMS=0.000212 meV
longitudinal       window=0.02  n=13  m/me=0.95590414  RMS=0.000866 meV
longitudinal       window=0.03  n=21  m/me=0.95557656  RMS=0.003613 meV
longitudinal-k14   window=0.01  n= 7  m/me=0.95645402  RMS=0.000212 meV
longitudinal-k14   window=0.02  n=13  m/me=0.95590308  RMS=0.000866 meV
longitudinal-k14   window=0.03  n=21  m/me=0.95557550  RMS=0.003613 meV
transverse-y       window=0.01  n= 7  m/me=0.19176939  RMS=0.000070 meV
transverse-y       window=0.02  n=13  m/me=0.19193550  RMS=0.000712 meV
transverse-y       window=0.03  n=21  m/me=0.19232024  RMS=0.005181 meV
transverse-z       window=0.01  n= 7  m/me=0.19176939  RMS=0.000070 meV
transverse-z       window=0.02  n=13  m/me=0.19193550  RMS=0.000712 meV
transverse-z       window=0.03  n=21  m/me=0.19232024  RMS=0.005181 meV
[preston@preston-System-Product-Name si-pbe]$
```

[纵向原始数据](/Atlas/examples/si-pbe-electronic/mass/longitudinal.csv)、[窗口和父密度对照表](/Atlas/examples/si-pbe-electronic/mass/mass-checks.csv)、[质量复核脚本](/Atlas/examples/si-pbe-electronic/analyse_mass_checks.py)都可以下载。画下面这张图只需[绘图脚本](/Atlas/examples/si-pbe-electronic/plot_si.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/si-pbe-electronic/atlas_plot_style.py)）和对应 CSV/JSON：

<details>
<summary>analyse_mass_checks.py 的完整源码</summary>

```python
from pathlib import Path
import json,csv,xml.etree.ElementTree as ET
import numpy as np
R=Path(__file__).resolve().parent
BOHR_ANG=0.529177210903
HA_EV=27.211386245988
C=3.80998211615486

def read(d):
    x=ET.parse(R/d/'data-file-schema.xml').getroot().find('output');a=float(x.find('atomic_structure').attrib['alat'])*BOHR_ANG
    states=x.find('band_structure').findall('ks_energies')
    k=np.array([[float(v) for v in s.find('k_point').text.split()] for s in states])*2*np.pi/a
    e=np.array([[float(v)*HA_EV for v in s.find('eigenvalues').text.split()] for s in states])
    return k,e

rows=[]
for d,direction,part,col in [('mass','longitudinal',slice(None),0),('mass-k14','longitudinal-k14',slice(None),0),('mass-transverse','transverse-y',slice(0,33),1),('mass-transverse','transverse-z',slice(33,66),2)]:
    k,e=read(d);q=k[part,col];ec=e[part,4];q0=q[ec.argmin()]
    for window in [.01,.02,.03]:
        mask=np.abs(q-q0)<=window+1e-12
        a,b,c=np.polyfit(q[mask]-q0,ec[mask],2)
        residual=np.polyval([a,b,c],q[mask]-q0)-ec[mask]
        rows.append({'directory':d,'direction':direction,'window_inv_A':window,'points':int(mask.sum()),'mass_over_me':float(C/a),'curvature_eVA2':float(2*a),'minimum_k_inv_A':float(q0-b/(2*a)),'rms_residual_meV':float(np.sqrt(np.mean(residual**2))*1000)})
(R/'mass/mass-checks.json').write_text(json.dumps(rows,indent=2)+'\n')
with (R/'mass/mass-checks.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for row in rows:
    print(f"{row['direction']:18s} window={row['window_inv_A']:.2f}  n={row['points']:2d}  m/me={row['mass_over_me']:.8f}  RMS={row['rms_residual_meV']:.6f} meV")
```

</details>

<details>
<summary>plot_si.py 的完整源码</summary>

```python

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import argparse,csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'plots';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':130,'savefig.dpi':300,'axes.titleweight':'bold'})
BLUE='#0072b2';ORANGE='#e69f00';GRAY='#667080'

def read(name):return np.genfromtxt(ROOT/name,delimiter=',',names=True,encoding='utf-8')
def save(fig,name):
    fig.savefig(OUT/(name+'.png'),bbox_inches='tight');fig.savefig(OUT/(name+'.svg'),bbox_inches='tight');plt.close(fig);print(OUT/(name+'.png'))
def clean(ax):ax.grid(alpha=.18);ax.set_axisbelow(True)
def convergence():
    rows=list(csv.DictReader((ROOT/'convergence.csv').open()))
    fig,axes=plt.subplots(1,3,figsize=(12,3.6),layout='constrained')
    for ax,param,label in zip(axes,['ecutwfc','ecutrho','kmesh'],['Wavefunction cutoff (Ry)','Charge-density cutoff (Ry)','Uniform mesh n × n × n']):
        r=[x for x in rows if x['parameter']==param];x=[float(v['setting']) for v in r];y=[float(v['delta_meV_per_atom_vs_last']) for v in r]
        ax.plot(x,y,'o-',color=BLUE);ax.set_xlabel(label);ax.set_ylabel('ΔE vs last point (meV/atom)');clean(ax)
        if param=='kmesh':ax.set_yscale('symlog',linthresh=.1);ax.axhline(1,color=ORANGE,ls='--',label='Example comparison: 1 meV/atom');ax.legend(fontsize=8)
        ax.set_title({'ecutwfc':'Fixed 640 Ry, 8³ mesh','ecutrho':'Fixed 60 Ry, 8³ mesh','kmesh':'Fixed 60 / 640 Ry'}[param],fontsize=11)
    save(fig,'convergence')
def relax():
    r=read('relax/relaxation.csv')
    fig,axes=plt.subplots(1,2,figsize=(9.6,3.6),layout='constrained')
    e_diff = (r['energy_Ry'] - r['energy_Ry'][-1]) * 13605.693122994
    axes[0].plot(r['scf_cycle'], e_diff, 'o-', color=BLUE, lw=1.5, ms=5, zorder=3)
    axes[0].fill_between(r['scf_cycle'], 0, e_diff, color=BLUE, alpha=0.12, zorder=1)
    axes[0].set_ylabel('Energy above final geometry (meV/cell)')
    axes[0].set_title('Si: Monotonic Energy Descent', fontweight='bold', fontsize=10.5)
    for cycle, de in zip(r['scf_cycle'][:-1], e_diff[:-1]):
        axes[0].annotate(f"{de:.1f} meV", xy=(cycle, de), xytext=(0, 6),
                         textcoords='offset points', ha='center', fontsize=7.5, color=BLUE)
    axes[0].annotate("Final E₀ = -22.838592 Ry", xy=(r['scf_cycle'][-1], 0), xytext=(-55, 18),
                     textcoords='offset points', fontsize=7.5, color='#162232',
                     arrowprops=dict(arrowstyle='->', color='#718096', lw=0.6))
    
    # Total force plot with log-scale threshold lines
    f_vals = np.array(r['total_force_Ry_per_Bohr'])
    # For display of the 0.0 final step, set a small visual floor for the arrow
    f_disp = np.maximum(f_vals, 1e-5)
    axes[1].plot(r['scf_cycle'][:-1], f_vals[:-1], 's-', color=ORANGE, lw=1.5, ms=5, label='Total Force', zorder=3)
    axes[1].plot([r['scf_cycle'][-2], r['scf_cycle'][-1]], [f_vals[-2], f_disp[-1]], 's--', color=ORANGE, lw=1.0, zorder=2)
    axes[1].scatter([r['scf_cycle'][-1]], [f_disp[-1]], marker='o', facecolors='white', edgecolors=ORANGE, s=40, zorder=4)
    axes[1].axhline(1e-3, color='#c0392b', ls='--', lw=0.9, label=r'QE Default $10^{-3}$ Ry/Bohr', zorder=1)
    axes[1].axhline(1e-4, color='#27ae60', ls=':', lw=0.9, label=r'Stringent $10^{-4}$ Ry/Bohr', zorder=1)
    axes[1].set_yscale('log')
    axes[1].set_ylim(5e-6, 1.2e-1)
    axes[1].set_ylabel('Total Force (Ry/Bohr, log scale)')
    axes[1].set_title('Si: BFGS Force Convergence', fontweight='bold', fontsize=10.5)
    axes[1].annotate('Printed as 0.000000\n(Force strictly zero by symmetry)',
                     xy=(r['scf_cycle'][-1], f_disp[-1]), xytext=(-120, 28),
                     textcoords='offset points', fontsize=7.5, color='#8c3b00',
                     arrowprops=dict(arrowstyle='->', color=ORANGE, lw=0.7))
    axes[1].legend(frameon=True, facecolor='#f8fafc', edgecolor='#e2e8f0', fontsize=7.5, loc='upper right')
    
    for label, ax in zip('ab', axes):
        ax.set_xlabel('BFGS Step / SCF Cycle')
        ax.set_xticks(r['scf_cycle'])
        clean(ax)
        ax.text(-0.14, 1.05, label, transform=ax.transAxes, fontweight='bold', fontsize=10)
    save(fig, 'relax')

def gap():
    r=json.loads((ROOT/'gap-results.json').read_text());base=[x for x in r if x['directory'] in ['gap12','gap18-cg','gap24-cg']]
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),layout='constrained')
    axes[0].plot([12,18,24],[x['gap_eV'] for x in base],'o-',color=BLUE);axes[0].set_xticks([12,18,24]);axes[0].set_xlabel('Uniform NSCF mesh n × n × n');axes[0].set_ylabel('Sampled indirect gap (eV)');axes[0].set_title('The sampled minimum need not vary monotonically',fontsize=10)
    for n,x in zip([12,18,24],base):axes[0].annotate(f"{max(x['cbm_k_tpiba']):.4f} × 2π/a",(n,x['gap_eV']),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
    m=read('mass/longitudinal.csv');fit=json.loads((ROOT/'mass/mass-fits.json').read_text())[1]
    dense=next(x for x in r if x['directory']=='gap24-k12-cg');axes[1].plot(m['kx_tpiba'],m['band5_eV']-dense['vbm_eV'],color=BLUE)
    axes[1].scatter([fit['minimum_k_tpiba']],[fit['minimum_energy_eV']-dense['vbm_eV']],color=ORANGE,zorder=4)
    axes[0].margins(y=.20)
    axes[1].set_xlabel('kx (2π/a), ky = kz = 0');axes[1].set_ylabel('Conduction energy − VBM (eV)');axes[1].set_title('Local Γ–X valley refinement; 12³ parent density',fontsize=10)
    for ax in axes:clean(ax)
    save(fig,'band-gap')
def mass():
    r=read('mass/longitudinal.csv');fits=json.loads((ROOT/'mass/mass-fits.json').read_text());fit=fits[1]
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),layout='constrained')
    dk=r['kx_inv_A']-fit['minimum_k_inv_A'];take=np.abs(dk)<.04
    axes[0].scatter(dk[take],(r['band5_eV'][take]-fit['minimum_energy_eV'])*1000,s=24,color=BLUE,label='Actual QE eigenvalues')
    q=np.linspace(-.035,.035,101);axes[0].plot(q,fit['quadratic_A_eVA2']*q*q*1000,color=ORANGE,label='Quadratic fit, ±0.02 Å⁻¹')
    axes[0].set_xlabel('kx − valley minimum (Å⁻¹)');axes[0].set_ylabel('Energy above minimum (meV)');axes[0].legend(fontsize=8)
    axes[1].plot([f['half_window_inv_A'] for f in fits],[f['mass_over_me'] for f in fits],'o-',color=BLUE)
    axes[1].set_xlabel('Fit half-window (Å⁻¹)');axes[1].set_ylabel('Longitudinal electron mass / me');axes[1].set_xticks([.01,.02,.03]);axes[1].ticklabel_format(useOffset=False,axis='y')
    for ax in axes:clean(ax)
    save(fig,'effective-mass')
def band3d():
    r=read('band3d/cube.csv');emin=r['band5_eV'].min();fig=plt.figure(figsize=(11,4.4),layout='constrained')
    for i,(key,value,xkey,ykey,title) in enumerate([('kz_tpiba',0.,'kx_tpiba','ky_tpiba','kz = 0 plane'),('kx_tpiba',.85,'ky_tpiba','kz_tpiba','kx = 0.85 × 2π/a plane')]):
        d=r[np.isclose(r[key],value)];xs=np.unique(d[xkey]);ys=np.unique(d[ykey]);X,Y=np.meshgrid(xs,ys,indexing='ij');Z=np.empty_like(X)
        for u,x in enumerate(xs):
            for v,y in enumerate(ys):Z[u,v]=(d['band5_eV'][np.isclose(d[xkey],x)&np.isclose(d[ykey],y)][0]-emin)*1000
        ax=fig.add_subplot(1,2,i+1,projection='3d');ax.plot_surface(X,Y,Z,cmap='viridis',linewidth=.2,edgecolor=(0,0,0,.15),antialiased=True)
        ax.set_xlabel(xkey.replace('_tpiba','')+' (2π/a)');ax.set_ylabel(ykey.replace('_tpiba','')+' (2π/a)');ax.set_zlabel('');ax.text2D(0.02, 0.91, 'E − sampled minimum (meV)', transform=ax.transAxes, fontsize=9);ax.set_title(title);ax.view_init(elev=25,azim=-125);ax.xaxis.set_major_locator(plt.MaxNLocator(4));ax.yaxis.set_major_locator(plt.MaxNLocator(4));ax.zaxis.set_major_locator(plt.MaxNLocator(4))
    fig.suptitle('Two cuts through an actual 11 × 9 × 9 local k-point cube',fontsize=12)
    save(fig,'band-3d')
def population():
    r=read('population-cg/lowdin.csv');fig,ax=plt.subplots(figsize=(6,4),layout='constrained');x=np.arange(len(r))
    ax.bar(x,r['s_electrons'],color=BLUE,label='s');ax.bar(x,r['p_electrons'],bottom=r['s_electrons'],color=ORANGE,label='p')
    for i,q in enumerate(r['total_electrons']):ax.text(i,q+.03,f'{q:.4f}',ha='center')
    ax.axhline(4,color=GRAY,ls='--',lw=1,label='4 valence electrons / Si');ax.set_xticks(x,['Si 1','Si 2']);ax.set_ylabel('Projected electrons');ax.set_ylim(0,4.5);ax.legend(ncol=3,fontsize=9,loc='lower center',bbox_to_anchor=(.5,1.));ax.set_title('Equivalent atoms; spilling = 0.0092',pad=38);save(fig,'population-analysis')
def fatband():
    r=read('bands-cg/fatband.csv');vbm=r['energy_eV'][r['iband']==4].max();fig,axes=plt.subplots(1,2,figsize=(12,4.6),sharey=True,layout='constrained')
    idx=[1,25,37,49,73,97,121];ticks=[r['path_distance_tpiba'][r['ik']==i][0] for i in idx];labels=['Γ','X','W','K','Γ','L','X']
    for ax,weight,color,title in zip(axes,['Si_s_weight','Si_p_weight'],[BLUE,ORANGE],['Si s projection','Si p projection']):
        for ib in range(1,9):
            q=r[r['iband']==ib];ax.plot(q['path_distance_tpiba'],q['energy_eV']-vbm,color='#b6bdc7',lw=.65,zorder=1);ax.scatter(q['path_distance_tpiba'],q['energy_eV']-vbm,s=34*q[weight],color=color,alpha=.75,edgecolors='none',zorder=2)
        for tick in ticks:ax.axvline(tick,color='#e0e3e8',lw=.65,zorder=0)
        ax.axhline(0,color=GRAY,ls='--',lw=.7);ax.set_xticks(ticks,labels);ax.set_xlim(ticks[0],ticks[-1]);ax.set_ylim(-13,7);ax.set_title(title);ax.set_ylabel('Energy − VBM (eV)')
        handles=[ax.scatter([],[],s=34*w,color='#555555',edgecolors='none',label=f'{w:g}') for w in (.25,.5,1.)]
        ax.legend(handles=handles,title='Projection weight (point area)',ncol=3,
                  loc='lower left',bbox_to_anchor=(0,1.015),frameon=False,fontsize=8)
        ax.set_title('',loc='center')
        ax.set_title(title,loc='left',pad=55)
    save(fig,'fatband')
def bands():
    r=read('bands-cg/fatband.csv');vbm=r['energy_eV'][r['iband']==4].max();fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained');idx=[1,25,37,49,73,97,121];ticks=[r['path_distance_tpiba'][r['ik']==i][0] for i in idx]
    for ib in range(1,9):
        q=r[r['iband']==ib];ax.plot(q['path_distance_tpiba'],q['energy_eV']-vbm,color=BLUE,lw=1)
    for tick in ticks:ax.axvline(tick,color='#dce1e8',lw=.7)
    ax.axhline(0,color=GRAY,ls='--',lw=.7);ax.set_xticks(ticks,['Γ','X','W','K','Γ','L','X']);ax.set_xlim(ticks[0],ticks[-1]);ax.set_ylim(-13,7);ax.set_ylabel('Energy − VBM (eV)');ax.set_title('Si, PBE, fixed example cell; no SOC');save(fig,'bands')
def dos():
    r=np.loadtxt(ROOT/'dos-cg/si.dos.dat');g=json.loads((ROOT/'gap-results.json').read_text());vbm=next(x['vbm_eV'] for x in g if x['directory']=='gap24-cg')
    fig,ax=plt.subplots(figsize=(7.5,3.7),layout='constrained');ax.plot(r[:,0]-vbm,r[:,1],color=BLUE);ax.fill_between(r[:,0]-vbm,r[:,1],alpha=.15,color=BLUE);ax.axvline(0,color=GRAY,ls='--');ax.set_xlim(-13,8);ax.set_xlabel('Energy − VBM (eV)');ax.set_ylabel('DOS (states/eV/cell)');ax.set_title('24³ NSCF mesh; Gaussian broadening 0.01 Ry');clean(ax);save(fig,'dos')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('figure',choices=['convergence','relax','gap','mass','band3d','population','fatband','bands','dos','all']);args=parser.parse_args()
    funcs={'convergence':convergence,'relax':relax,'gap':gap,'mass':mass,'band3d':band3d,'population':population,'fatband':fatband,'bands':bands,'dos':dos}
    for name,fun in funcs.items():
        if args.figure in [name,'all']:fun()
```

</details>

```text
[preston@preston-System-Product-Name si-pbe]$ python3 plot_si.py mass
<工作目录>/si-pbe/plots/effective-mass.png
```

![Si 导带谷的真实采样、抛物线拟合和窗口敏感性](/Atlas/examples/si-pbe-electronic/plots/effective-mass.png)

左图以谷底为能量参考显示局部曲率；右图比较三个拟合窗口。残差衡量局部二次近似，窗口与父密度对照给出这组质量的数值敏感性。

## 文献中对能带曲率与费米速度分布的展示方式

二维鞍点不是局部极大值或极小值：沿两个主曲率方向，能量分别向上和向下弯曲。因此电子曲率质量的两个主值符号相反，不能用一个正的标量质量代表整个鞍点。图中可同时展示局部能量曲面和沿主方向的切线；若讨论空穴质量，还需明确相对于价带顶的符号约定。

<figure class="research-figure"><img src="/Atlas/figures/literature/M7_SurfaceStates_3DVHS_ARPES_ZrAs2_Fig4.jpg" alt="二维鞍点附近沿正交动量方向相反符号的能带曲率与有效质量切面" loading="lazy"/><figcaption>ZrAs<sub>2</sub> 表面态二维鞍点附近的三维色散（c）及沿正交动量方向 X̄→Γ̄（正有效质量，开口向上抛物线）与 X̄→S̄（负有效质量，开口向下抛物线）的相反能带曲率切面（e）。引自 <em>Nat. Commun.</em> <strong>16</strong>, 2831 (2025)，Fig. 4c,e，<a href="https://doi.org/10.1038/s41467-025-58024-w" target="_blank" rel="noopener noreferrer">DOI: 10.1038/s41467-025-58024-w</a>。</figcaption></figure>

对于金属，费米面上的局部速度由 v<sub>F</sub>(k) = (1/ℏ)∇<sub>k</sub>E(k) 给出。将速度模长映射到费米面轮廓上，可以辨认不同口袋上的快慢区域。它与带边曲率质量描述的是不同量；讨论输运还需要相应的占据和散射信息。

<figure class="research-figure"><img src="/Atlas/figures/literature/M2_Bands_DOS_FS_MoW_Bekaert2020_Fig2.jpg" alt="二维过渡金属氮化物的低能能带色散、态密度与映射在二维费米面轮廓上的费米速度分布" loading="lazy"/><figcaption>单层二维过渡金属氮化物的低能能带色散、总态密度以及映射在二维费米面轮廓上的费米速度 <em>v</em><sub>F</sub>(<strong>k</strong>) 分布。引自 Bekaert 等人，<em>Nanoscale</em> <strong>12</strong>, 17354 (2020)，Fig. 2，<a href="https://doi.org/10.1039/D0NR03875J" target="_blank" rel="noopener noreferrer">DOI: 10.1039/D0NR03875J</a>。</figcaption></figure>

下一步：可跳到[三维能带采样](/Atlas/m/band-3d/qe/)检查谷的空间形状，或回到[带隙](/Atlas/m/band-gap/qe/)核对带边位置；[载流子迁移率](/Atlas/m/carrier-mobility/qe/)还需要散射模型或电子声子信息。

```text
SCF 密度 → 找到导带谷 → 沿各方向密集 k 点
                           ↓
                  本征值单位与 k 单位转换
                           ↓
                  对称窗口拟合 + 窗口比较
                           ↓
                  方向质量与适用条件
```
