[q2r.x 输入](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html) · [matdyn.x 输入](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html) · [QE 7.5 lambda.x 源码](https://github.com/QEF/q-e/blob/qe-7.5/PHonon/PH/lambda.f90) · [电子声子谱定义](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html)

α²F(ω) 把声子频率与电子–声子耦合权重放在同一条谱上；对 `2α²F/ω` 积分得到 λ，对它做对数频率平均得到 ωlog。本页从 [Al EPC](/Atlas/m/epc/qe/) 的八份逐 q 文件接到这两个积分，并分别追踪 `matdyn` 与 `lambda.x` 的输出来源。

下面展开 32³ 致密、16³ 响应、4³ q 网格这一完整分支。原件与脚本在 [Al 输入输出包](/Atlas/examples/al-lesson-files.tar.gz)，新增表位于 `al/tc-route/`。48³ 分支的独立计算及两条 Tc 曲线求交见 [Tc 对照](/Atlas/m/allen-dynes/qe/#tc-two-dense-grids)；两分支原件在 [双分支下载包](/Atlas/examples/supercon-al-tc-files.tar.gz)。

## q2r / matdyn 与 lambda.x 分别留下什么

脚本先执行 `q2r.x`，把完整 q 网格的力常数和 EPC 数据一起变换到实空间，再交给 `matdyn.x`。两份输入如下。

```console
maxwell@maxwell:~/al/epc-q4$ cat q2r.in
&INPUT
 fildyn='al.dyn'
 flfrc='al.fc'
 zasr='simple'
 la2F=.true.
/
```

```console
maxwell@maxwell:~/al/epc-q4$ cat matdyn-dos.in
&INPUT
 flfrc='al.fc'
 asr='simple'
 amass(1)=26.9815385
 la2F=.true.
 dos=.true.
 nk1=24
 nk2=24
 nk3=24
 ndos=400
 fldos='al.phdos.dat'
/
```

`matdyn.x` 的 24³ 是对已有实空间数据的积分网格，并没有增加真实计算的 DFPT q 点。它生成 `a2F.dos1` 到 `a2F.dos10`，编号依次对应十组电子展宽；同目录的 `lambda` 文件记录该路线的 λ 和对数平均频率。

这里 `nk1/nk2/nk3` 虽然名字带 k，在 `matdyn.x` 中却是声子 DOS 积分使用的 q 网格。增加它们可以检查后处理积分的离散误差，但无法补回原先 4³ DFPT 网格没有提供的力常数范围。`asr='simple'` 处理平移声学求和规则，也不会自动修复电子声子矩阵元或证明材料没有虚频。

同样的 `la2F` 出现在不同程序里，要跟着程序名读：`pw.x` 负责保存致密电子本征值，`q2r.x` 处理配套 EPC 实空间数据，`matdyn.x` 才在这条插值路线中输出谱函数。仅在普通声子后处理中打开最后一个开关，并不能产生前面从未计算的耦合。三份程序输入与逐 q 文件必须属于同一次完整计算链。

```console
maxwell@maxwell:~/al/epc-q4$ head -8 a2F.dos4
 
 # Eliashberg function a2F (per both spin)
 #  frequencies in Rydberg  
 # DOS normalized to E in Rydberg: a2F_total, a2F(mode) 
 
       0.378477E-05    0.138515E-09    0.613987E-10    0.351279E-10    0.419882E-10
       0.113543E-04    0.373996E-08    0.165777E-08    0.948475E-09    0.113372E-08
       0.189239E-04    0.173147E-07    0.767484E-08    0.439111E-08    0.524872E-08
```

文件头直接写着 `frequencies in Rydberg`。第一列是 Ry，第二列是总谱函数，后面三列按模式编号分解；单原子原胞有三个模式，因此数据区共五列。文件最后还有 `lambda = ... Delta = ...` 一行，它不是数值数据行，读表时不能直接把整份文件强行当成五列数组。

```console
maxwell@maxwell:~/al/epc-q4$ tail -3 a2F.dos4
       0.301648E-02    0.281188E-02    0.000000E+00    0.000000E+00    0.281188E-02
       0.302405E-02    0.000000E+00    0.000000E+00    0.000000E+00    0.000000E+00
  lambda =  0.374096616223644         Delta =   7.569579561024077E-006
```


## 输入之后，程序实际留下了什么

原作业按顺序执行这两条命令。先读齐同一 q 网格及其电声数据，再让 matdyn 读新写出的实空间文件；第一步失败时不能继续拿旧的 `al.fc` 画图。

```bash
<qe_bin>/q2r.x -in q2r.in > q2r.out 2> q2r.err
<qe_bin>/matdyn.x -in matdyn-dos.in > matdyn-dos.out 2> matdyn-dos.err
```

```console
maxwell@maxwell:~/al/epc-q4$ tail -18 q2r.out
 Broadening =      0.045
      q-space grid ok, #points =   64

      fft-check success (sum of imaginary terms < 10^-12)
 
 Broadening =      0.050
      q-space grid ok, #points =   64

      fft-check success (sum of imaginary terms < 10^-12)
 
     Q2R          :      0.01s CPU      0.01s WALL

 
   This run was terminated on:  22:14:11  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```
```console
maxwell@maxwell:~/al/epc-q4$ cat matdyn-dos.out
MPI startup(): PMI server not found. Please set I_MPI_PMI_LIBRARY variable if it is not a singleton case.

     Program MATDYN v.7.5 starts on 22Sep2026 at 22:14:11 

     This program is part of the open-source Quantum ESPRESSO suite
     for quantum simulation of materials; please cite
         "P. Giannozzi et al., J. Phys.:Condens. Matter 21 395502 (2009);
         "P. Giannozzi et al., J. Phys.:Condens. Matter 29 465901 (2017);
         "P. Giannozzi et al., J. Chem. Phys. 152 154105 (2020);
          URL http://www.quantum-espresso.org", 
     in publications or presentations arising from this work. More details at
     http://www.quantum-espresso.org/quote

     Parallel version (MPI), running on     1 processors

     MPI processes distributed on     1 nodes
     1755 MiB available memory on the printing compute node when the environment starts
 
     Message from routine matdyn:
     Z* not found in file al.fc, TO-LO splitting at q=0 will be absent!
 
     MATDYN       :     26.00s CPU     26.11s WALL

 
   This run was terminated on:  22:14:38  22Sep2026            

=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
```

本例 `q2r` 输入写有 `zasr='simple'`，它针对 Born 有效电荷；这份金属 Al 计算没有求 Born 电荷。对插值力常数施加平移声学求和规则的是 `matdyn` 中的 `asr='simple'`。24³ 是插值积分网格，`ndos=400` 是输出频率采样，二者都不会新增上游的 DFPT 响应信息。[q2r 的 zasr 定义](https://www.quantum-espresso.org/Doc/INPUT_Q2R.html#zasr) · [matdyn 的 asr 定义](https://www.quantum-espresso.org/Doc/INPUT_MATDYN.html#asr)

| 读到的字段 | 本例单位 | 在哪里使用 |
|---|---|---|
| `alpha2F.dat` 第一列 | THz，普通频率 ν | 直接求和谱的 λ 与频率矩 |
| `a2F.dos*` 第一列 | Ry 对应的频率能量 | matdyn 插值谱；先确认单位再比较横轴 |
| `lambda.dat` 的 log w | K | 可直接代入 Tc 公式 |
| `el_ph_sigma` 与谱列标题 | Ry | 电子双 δ 积分的展宽 |
| `lambda.in` 的 0.12 | THz | 频率轴 Gaussian 参数宽度 |
| `lambda.in` 末行 0.10 | 无量纲 | Tc 采用的 μ* 假设 |

普通频率 ν 与角频率 ω 的单位转换分别写成 hν/kB 与 ħω/kB，两者相等，不能再多乘一次 2π。`lambda.f90` 固定使用 47.9924 K/THz；已经打印成 K 的 ωlog 不需要重复转换。它从逐 q 文件的有限小数频率平方重建最高模式约为 9.936533 THz，ph.x 原文打印为 9.936574 THz，差别是文本精度与常数使用造成的，不能强行当作同一全精度读数。

另一条路线是 `lambda.x`：直接读取这 8 个 q 点的 `elph.inp_lambda.*`，按星权重求和并在频率轴做 Gaussian 展宽。本页主图使用这条路线，文件名是 `alpha2F.dat`，频率单位为 THz。两个文件名很相似，单位和积分方式却不同，应分别保存与标注。

```console
maxwell@maxwell:~/al/epc-q4$ cat lambda.in
14.0 0.12 0
8
0.000000000 0.000000000 0.000000000 1.0
-0.176776700 0.176776700 -0.176776700 8.0
0.353553400 -0.353553400 0.353553400 4.0
0.000000000 0.353553400 0.000000000 6.0
0.530330100 -0.176776700 0.530330100 24.0
0.353553400 0.000000000 0.353553400 12.0
0.000000000 -0.707106800 0.000000000 3.0
-0.353553400 -0.707106800 0.000000000 6.0
elph_dir/elph.inp_lambda.1
elph_dir/elph.inp_lambda.2
elph_dir/elph.inp_lambda.3
elph_dir/elph.inp_lambda.4
elph_dir/elph.inp_lambda.5
elph_dir/elph.inp_lambda.6
elph_dir/elph.inp_lambda.7
elph_dir/elph.inp_lambda.8
0.10
```

第一行依次是频率上限 14 THz、频率展宽 0.12 THz 和 Gaussian 类型 0。第二行是不可约 q 点数；随后八行是 q 坐标及其星权重。坐标沿用 ph.x 输出的笛卡尔坐标、单位为 2π/alat；权重之和为 64，程序会归一化，不能给八个点都填 1。再往下的八行对应这八个点的文件，最后一行的 0.10 是用于公式估计 Tc 的 μ* 假设。

本次直接计算的最高模式为 9.936574 THz。14 THz 的上限还为频率展宽的尾部留出了空间。换材料时应先检查真实最高频率与高频尾部；沿用一个过小的上限，会使谱函数积分漏掉贡献，即使程序正常退出也不能接受。

```console
maxwell@maxwell:~/al/epc-q4$ <qe_bin>/lambda.x < lambda.in > lambda.out 2> lambda.err

```

```console
maxwell@maxwell:~/al/epc-q4$ cat lambda.dat
# degauss   lambda    int alpha2F  <log w>     N(Ef)
  0.005    0.430378    0.430442   355.877    2.518161
  0.010    0.371061    0.371121   344.606    2.624685
  0.015    0.370295    0.370356   343.420    2.647439
  0.020    0.374486    0.374547   343.741    2.646097
  0.025    0.374613    0.374674   343.537    2.643523
  0.030    0.373773    0.373835   342.831    2.643829
  0.035    0.373581    0.373643   342.006    2.645823
  0.040    0.374086    0.374148   341.243    2.648339
  0.045    0.375022    0.375085   340.631    2.650827
  0.050    0.376041    0.376104   340.145    2.653067
```

从左到右是电子展宽（Ry）、逐 q 点求和的 λ、对程序内部谱函数积分得到的 λ、ω_log（K），以及单自旋 DOS(EF)，后者单位是 states/spin/Ry/cell。0.020 Ry 这一行的前两种 λ 分别为 0.374486 和 0.374547，差约 0.000061；频率展宽与数值积分会造成小差别。

## 把图积分回输出里的 λ

```console
maxwell@maxwell:~/al/epc-q4$ head -5 alpha2F.dat
# E(THz)     0.005     0.010     0.015     0.020     0.025     0.030     0.035     0.040     0.045     0.050
  0.0000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0070   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0140   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0210   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
```

第一列后的十列依次对应文件头十组电子展宽。不要取第二列画图，却拿 0.020 Ry 那一行的 λ 做标题。下面的提取脚本检查 q 坐标、模式数、权重和十组展宽，然后用谱函数独立计算 `2∫α²F(ν)/ν dν`。零频点不参加除法，也没有对负数取绝对值。

### 交给代码助手的任务：解析谱与累计耦合

> 从保存的 lambda.in、alpha2F.dat、lambda.out 和逐 q elph 文件编写独立谱分析程序。按文件实际表头读取频率轴与十档电子展宽，保留 THz；验证轴单调、点数、有限数值和谱上限。计算累计 λ(ω)=2∫α²F(ω′)/ω′dω′、最终谱积分 λ 和对数频率矩；ω=0 且谱为零时明确处理该点，记录积分规则和打印精度。将谱积分 λ 与输出括号内值核对，逐 q 加权 λ 与括号外值核对；使用对应版本源码常数把 ωlog 换为 K。分别保留 lambda.x 谱和 matdyn 谱的来源、频率网格与展宽，不把两个谱文件强行当成同一数据。输出逐频率累计积分 CSV、各 σ 摘要 JSON 和完整源码。只做后处理，不补生成缺失的18 THz计算记录或新 DFT。

[完整谱与公式核对源码 verify_tc_chain.py](/Atlas/examples/al/tc-route/scripts/verify_tc_chain.py) · [谱解析源码 analyse_epc.py](/Atlas/examples/al/epc-q4/analyse_epc.py) · [双网格谱差源码 compare_spectral_grids.py](/Atlas/examples/supercon-al-tc/compare_spectral_grids.py)。

<details>
<summary>verify_tc_chain.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Read the completed Al lesson; check lineage, units and Tc formulas.
Standard library only. No QE execution and no edits to source calculations.
Source formulas: QE 7.5 lambda.f90; Allen & Dynes, PRB 12, 905 (1975).
"""
from pathlib import Path
import argparse, csv, hashlib, json, math, re, statistics

QE_RY_THZ=3289.828
QE_THZ_K=47.9924
SI_THZ_K=6.62607015e-34*1e12/1.380649e-23
SI_RY_K=(4.3597447222071e-18/2)/1.380649e-23
SI_RY_THZ=(4.3597447222071e-18/2)/6.62607015e-34/1e12

def table(path):
    return [[float(x) for x in s.split()] for s in path.read_text().splitlines()
            if s.strip() and re.match(r'^\s*[-+]?\d',s)]

def trap(x,y):
    return sum((b-a)*(v+u)/2 for a,b,u,v in zip(x,x[1:],y,y[1:]))

def cumulative(x,y):
    out=[0.]
    for a,b,u,v in zip(x,x[1:],y,y[1:]):
        out.append(out[-1]+(b-a)*(u+v)/2)
    return out

def moments(x,y,to_K):
    if any(v<0 for v in y):
        raise ValueError("A negative spectrum is not silently clipped for Tc moments.")
    pairs=[(a,b) for a,b in zip(x,y) if a>0]
    a,b=map(list,zip(*pairs))
    lam=2*trap(a,[v/u for u,v in pairs])
    if lam<=0:raise ValueError("Non-positive spectral lambda")
    logw=math.exp(2*trap(a,[v*math.log(u)/u for u,v in pairs])/lam)
    w2=math.sqrt(2*trap(a,[v*u for u,v in pairs])/lam)
    return lam,logw*to_K,w2*to_K

def formula(lam,wlog_K,w2_K,mu):
    den=lam-mu*(1+.62*lam)
    if lam<=0 or wlog_K<=0 or den<=0:
        raise ValueError("Outside this empirical formula's admissible denominator.")
    simple=wlog_K/1.2*math.exp(-1.04*(1+lam)/den)
    ratio=w2_K/wlog_K
    L1=2.46*(1+3.8*mu);L2=1.82*(1+6.3*mu)*ratio
    f1=(1+(lam/L1)**1.5)**(1/3)
    f2=1+(ratio-1)*lam*lam/(lam*lam+L2*L2)
    return dict(denominator=den,Tc_simple_K=simple,f1=f1,f2=f2,Tc_full_AD_K=f1*f2*simple)

def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=Path('data'))
    a=ap.parse_args();r=a.source.resolve();o=a.output.resolve();o.mkdir(parents=True,exist_ok=True)
    source_names=['lambda.in','lambda.dat','lambda.out','alpha2F.dat','al.elph.out','q2r.out','matdyn-dos.out',
                  'al.dense.in','al.scf.in','al.elph.in','q2r.in','matdyn-dos.in','q-weight-source.json']
    inp=[x.strip() for x in (r/'lambda.in').read_text().splitlines() if x.strip()]
    emax,width,kind=map(float,inp[0].split());nq=int(inp[1])
    assert int(kind)==0 and width>0
    qrows=[list(map(float,x.split())) for x in inp[2:2+nq]]
    files=inp[2+nq:2+2*nq];mu=float(inp[2+2*nq])
    wsum=sum(q[3] for q in qrows);assert wsum==64 and nq==8
    ph=(r/'al.elph.out').read_text()
    qblocks=re.split(r'Calculation of q\s*=',ph)[1:];assert len(qblocks)==nq
    modes=[];negative_w2=[];native_ph_frequencies=[]
    for iq,(q,name,block) in enumerate(zip(qrows,files,qblocks),1):
        p=r/name;source_names.append(name);text=p.read_text();lines=text.splitlines()
        h=lines[0].split();ns,nm=map(int,h[3:]);assert ns==10 and nm==3
        assert all(abs(float(h[j])-q[j])<1e-6 for j in range(3))
        native_ph_frequencies.extend(float(v) for v in re.findall(r'freq\s*\(\s*\d+\)\s*=\s*([-\d.]+)\s*\[THz\]',block))
        stars=list(map(int,re.findall(r'Number of q in the star\s*=\s*(\d+)',block)))
        assert stars and set(stars)=={int(q[3])}
        w2=list(map(float,lines[1].split()));assert len(w2)==nm
        for j,v in enumerate(w2):
            if v<=0:negative_w2.append([iq,j+1,v])
        if negative_w2:raise ValueError("Nonpositive direct squared frequencies: "+str(negative_w2))
        chunks=re.split(r'Gaussian Broadening:',text)[1:];assert len(chunks)==ns
        for chunk in chunks:
            sigma=float(re.match(r'\s*([.\d]+)',chunk)[1])
            vals=re.findall(r'lambda\(\s*(\d+)\)=\s*([-\d.]+)\s+gamma=\s*([-\d.]+)\s+GHz',chunk)
            assert len(vals)==nm
            for mode,lam,gamma in vals:
                j=int(mode)-1;freq=math.sqrt(w2[j])*QE_RY_THZ
                row=dict(q_index=iq,mode=j+1,sigma_Ry=sigma,star_weight=int(q[3]),
                         weight=q[3]/wsum,frequency_THz=freq,lambda_mode=float(lam),gamma_GHz=float(gamma))
                modes.append(row)
    direct=table(r/'lambda.dat');af=table(r/'alpha2F.dat')
    assert len(direct)==10 and len(af)==2000 and len(af[0])==11
    assert all(math.isfinite(x) for row in af for x in row) and min(min(row[1:]) for row in af)>=0
    printed_x=[row[0] for row in af]
    exact_x=[i*emax/1999 for i in range(2000)]
    native_tc=table_from_output=(r/'lambda.out').read_text().split('lambda        omega_log          T_c')[-1]
    native_tc=[[float(x) for x in s.split()] for s in native_tc.strip().splitlines()]
    assert len(native_tc)==10
    scans=[];spectrum=[];matdyn=[];pairs=[]
    for j,(sigma,lam_print,li_print,wl_print,dosef) in enumerate(direct):
        selected=[m for m in modes if abs(m['sigma_Ry']-sigma)<1e-9]
        qsum=sum(m['weight']*m['lambda_mode'] for m in selected)
        recon=[]
        for nu in exact_x:
            recon.append(sum(m['weight']*m['lambda_mode']*m['frequency_THz']/2
                             *math.exp(-((nu-m['frequency_THz'])/width)**2)/(math.sqrt(math.pi)*width)
                             for m in selected))
        step=emax/1999
        li_exact=2*step*sum(v/x for x,v in zip(exact_x[1:],recon[1:]))
        log_exact=math.exp(2*step*sum(v*math.log(x)/x for x,v in zip(exact_x[1:],recon[1:]))/li_exact)*QE_THZ_K
        assert abs(qsum-lam_print)<5.1e-7
        assert abs(li_exact-li_print)<5.1e-7 and abs(log_exact-wl_print)<.00051
        y=[row[j+1] for row in af];lam_s,log_s,w2_s=moments(printed_x,y,QE_THZ_K)
        assert abs(lam_s-li_print)<2e-5 and abs(log_s-wl_print)<.02
        f=formula(lam_s,log_s,w2_s,mu)
        native_formula=formula(qsum,log_exact,w2_s,mu)['Tc_simple_K']
        assert abs(native_formula-native_tc[j][2])<.00051
        row=dict(sigma_Ry=sigma,lambda_qsum=qsum,lambda_native_printed=lam_print,
                 lambda_spectrum_internal=li_exact,lambda_spectrum_printed_trapezoid=lam_s,
                 omega_log_native_replay_K=log_exact,omega_log_printed_K=wl_print,
                 omega_log_spectrum_K=log_s,omega2_spectrum_K=w2_s,
                 mu_star=mu,Tc_native_printed_K=native_tc[j][2],Tc_QE_replay_K=native_formula,
                 Tc_spectrum_simple_K=f['Tc_simple_K'],f1=f['f1'],f2=f['f2'],Tc_spectrum_full_AD_K=f['Tc_full_AD_K'])
        scans.append(row)
        cy=cumulative(printed_x,[0 if x==0 else 2*v/x for x,v in zip(printed_x,y)])
        if j in [0,3]:
            for x,v,z in zip(printed_x,y,cy):spectrum.append(dict(route='lambda.x',sigma_Ry=sigma,frequency_THz=x,a2F=v,cumulative_lambda=z))
        apath=r/f'a2F.dos{j+1}';source_names.append(apath.name);atxt=apath.read_text();arr=table(apath)
        assert len(arr)==400 and all(len(v)==5 for v in arr)
        ry=[v[0] for v in arr];ay=[v[1] for v in arr]
        footer=float(re.search(r'lambda\s*=\s*([-\d.Ee+]+)',atxt)[1])
        neg=sum(v<0 for v in ay)
        md=dict(sigma_Ry=sigma,negative_rows=neg,min_a2F=min(ay),lambda_footer=footer,
                lambda_trapezoid=2*trap(ry,[v/x for x,v in zip(ry,ay)]),frequency_unit='Ry',
                moment_status='rejected_negative_spectrum' if neg else 'nonnegative_for_arithmetic')
        if neg==0:
            ml,mw,m2=moments(ry,ay,SI_RY_K);md.update(lambda_spectrum=ml,omega_log_K=mw,omega2_K=m2)
        matdyn.append(md)
        if j in [0,3]:
            cx=[x*SI_RY_THZ for x in ry];cy=cumulative(ry,[2*v/x for x,v in zip(ry,ay)])
            for x,v,z in zip(cx,ay,cy):spectrum.append(dict(route='matdyn.x',sigma_Ry=sigma,frequency_THz=x,a2F=v,cumulative_lambda=z))
    chosen=scans[3];mu_rows=[]
    for i in range(8,17):
        m=i/100;f=formula(chosen['lambda_spectrum_printed_trapezoid'],chosen['omega_log_spectrum_K'],chosen['omega2_spectrum_K'],m)
        simple=formula(chosen['lambda_native_printed'],chosen['omega_log_printed_K'],chosen['omega2_spectrum_K'],m)['Tc_simple_K']
        mu_rows.append(dict(mu_star=m,Tc_QE_rounded_input_K=simple,Tc_spectrum_simple_K=f['Tc_simple_K'],Tc_spectrum_full_AD_K=f['Tc_full_AD_K']))
    write_csv(o/'tc-formula-scan.csv',scans);write_csv(o/'mu-star-scan.csv',mu_rows)
    write_csv(o/'spectra-and-integrals.csv',spectrum);write_csv(o/'mode-check.csv',modes)
    # Rejecting negative spectra is recorded; raw values are always preserved in plots/data.
    (o/'matdyn-spectrum-checks.json').write_text(json.dumps(matdyn,indent=2)+'\n')
    density_hash=hashlib.sha256((r/'tmp/al.a2Fsave').read_bytes()).hexdigest()
    assert density_hash==hashlib.sha256((r/'al.a2Fsave.k32').read_bytes()).hexdigest()
    minfreq=min(m['frequency_THz'] for m in modes);maxfreq=max(m['frequency_THz'] for m in modes)
    for name in ['al.dense','al.scf','al.elph','q2r','matdyn-dos']:
        out=(r/f'{name}.out').read_text();assert 'JOB DONE.' in out and 'convergence NOT achieved' not in out
        assert (r/f'{name}.err').stat().st_size==0
    assert (r/'lambda.err').stat().st_size==0
    report=dict(case='completed fcc Al lesson, QE7.5',q_irreducible=nq,q_star_sum=wsum,nmodes=3,
                electronic_widths_Ry=[row[0] for row in direct],frequency_min_direct_THz=minfreq,
                frequency_max_direct_THz=max(native_ph_frequencies),frequency_max_reconstructed_from_printed_w2_THz=maxfreq,frequency_upper_limit_THz=emax,gaussian_parameter_THz=width,
                direct_negative_squared_frequencies=negative_w2,dense_a2Fsave_sha256=density_hash,
                low_frequency_mode_lambda_cutoff_cm1=20,
                cutoff_source='QE7.5 PHonon/PH/elphon.f90 epsw and elphsum; raw gamma still exists',
                constants=dict(lambda_x_Ry_to_THz=QE_RY_THZ,lambda_x_THz_to_K=QE_THZ_K,
                               SI_THz_to_K=SI_THZ_K,SI_Ry_to_K=SI_RY_K,SI_Ry_to_THz=SI_RY_THZ),
                source_sha256={name:hashlib.sha256((r/name).read_bytes()).hexdigest() for name in source_names},
                formula_versions=['QE omega_log modified McMillan/Allen-Dynes with f1=f2=1',
                                  'spectral-moment Allen-Dynes with both f1 and f2'],
                numerical_crosscheck='qsum, source-algorithm replay, printed-spectrum quadrature and native Tc agree within printing/integration tolerances',
                scientific_status='teaching formula results only; k/q/cutoff convergence not established; mu_star assumed; no material Tc accepted',
                selected_sigma_Ry_0p020=chosen)
    (o/'tc-chain-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'q points={nq}; weights={wsum:g}; modes=3; widths=10; mode records={len(modes)}')
    print(f'printed-omega^2 reconstruction={minfreq:.6f}..{maxfreq:.6f} THz; negative omega^2=0')
    print(f'ph.x printed maximum={max(native_ph_frequencies):.6f} THz; frequency difference comes from printed w2 precision')
    print(f'lambda.x grid=2000 points, 0..{emax:g} THz; Gaussian parameter={width:g} THz')
    print('sigma_Ry lambda_qsum lambda_spectrum omega_log_K omega2_K Tc_QE_K Tc_full_AD_K')
    for s in scans:
        print(f"{s['sigma_Ry']:.3f} {s['lambda_qsum']:.8f} {s['lambda_spectrum_printed_trapezoid']:.8f} {s['omega_log_spectrum_K']:.5f} {s['omega2_spectrum_K']:.5f} {s['Tc_QE_replay_K']:.6f} {s['Tc_spectrum_full_AD_K']:.6f}")
    print('sigma=0.020: f1={:.8f}; f2={:.8f}; spectral simple Tc={:.6f} K'.format(chosen['f1'],chosen['f2'],chosen['Tc_spectrum_simple_K']))
    print('matdyn negative rows by width: '+', '.join(str(m['negative_rows']) for m in matdyn))
    print('Cross-check completed. Material Tc convergence is not established.')

if __name__=='__main__':main()
```

</details>

<details>
<summary>analyse_epc.py 的完整源码</summary>

```python
from pathlib import Path
import csv,json,re,hashlib
import numpy as np
r=Path(__file__).resolve().parent
qs=json.loads((r/'q-weight-source.json').read_text())['qpoints']
ph=(r/'al.elph.out').read_text()
blocks=re.split(r'Calculation of q\s*=',ph)[1:]
assert len(blocks)==len(qs)==8
rows=[]
for iq,(q,b) in enumerate(zip(qs,blocks),1):
    f=r/'elph_dir'/f'elph.inp_lambda.{iq}'
    lines=f.read_text().splitlines()
    h=lines[0].split(); ns,nm=map(int,h[3:]); assert ns==10 and nm==3
    assert np.allclose(list(map(float,h[:3])),q['q_cart_2pi_alat'],atol=1e-6,rtol=0)
    freq=re.findall(r'freq\s*\(\s*(\d+)\)\s*=\s*([-\d.]+)\s*\[THz\]\s*=\s*([-\d.]+)\s*\[cm-1\]',b)
    assert len(freq)==3
    w2=np.array(list(map(float,lines[1].split())))
    assert np.all(w2>0)
    assert np.allclose(np.sqrt(w2)*3289.828,[float(x[1]) for x in freq],atol=1e-4,rtol=0)
    chunks=re.split(r'Gaussian Broadening:',f.read_text())[1:]; assert len(chunks)==ns
    for ch in chunks:
        sigma=float(re.search(r'^\s*([.\d]+)\s+Ry',ch).group(1))
        dosef,ef=map(float,re.search(r'DOS\s*=\s*([.\d]+).*?Ef=\s*([.\d]+)',ch).groups())
        modes=re.findall(r'lambda\(\s*(\d+)\)=\s*([-\d.]+)\s+gamma=\s*([-\d.]+)\s+GHz',ch)
        assert len(modes)==nm
        for mode,lam,gamma in modes:
            j=int(mode)-1
            rows.append(dict(q_index=iq,qx=q['q_cart_2pi_alat'][0],qy=q['q_cart_2pi_alat'][1],qz=q['q_cart_2pi_alat'][2],star_weight=q['star_weight'],sigma_Ry=sigma,mode=int(mode),frequency_THz=float(freq[j][1]),frequency_cm1=float(freq[j][2]),lambda_mode=float(lam),gamma_GHz=float(gamma),DOS_EF_states_spin_Ry_cell=dosef,EF_eV=ef))
assert sum(x['star_weight'] for x in qs)==64 and len(rows)==240
with (r/'linewidth.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
dat=np.loadtxt(r/'lambda.dat'); af=np.loadtxt(r/'alpha2F.dat'); assert dat.shape==(10,5) and af.shape[1]==11
assert np.all(np.isfinite(dat)) and np.all(np.isfinite(af)) and np.min(af[:,1:])>=0
native_tc=np.array([list(map(float,x.split())) for x in (r/'lambda.out').read_text().split('lambda        omega_log          T_c')[-1].strip().splitlines()])
assert native_tc.shape==(10,3)
mp=[]
for line in (r/'lambda').read_text().splitlines():
    m=re.search(r'Broadening\s+([.\d]+)\s+lambda\s+([.\d]+).*?omega_ln \[K\]\s+([.\d]+)',line)
    if m:mp.append(list(map(float,m.groups())))
assert len(mp)==10
scan=[]
for j,(sigma,lam,li,wlog,dosef) in enumerate(dat):
    weighted=sum(v['star_weight']/64*v['lambda_mode'] for v in rows if abs(v['sigma_Ry']-sigma)<1e-10)
    integ=2*(np.trapezoid if hasattr(np, "trapezoid") else np.trapz)(af[1:,j+1]/af[1:,0],af[1:,0])
    assert abs(weighted-lam)<1e-6 and abs(integ-li)<2e-5
    denom=lam-.1*(1+.62*lam); assert denom>0
    tc=wlog/1.2*np.exp(-1.04*(1+lam)/denom)
    assert abs(tc-native_tc[j,2])<.001
    a2text=(r/f'a2F.dos{j+1}').read_text()
    a2=np.array([list(map(float,line.split())) for line in a2text.splitlines() if re.match(r'^\s*[-+]?\d',line)]); assert a2.shape==(400,5)
    footer_lambda=float(re.search(r'lambda\s*=\s*([-+.\dEe]+)',a2text).group(1))
    scan.append(dict(sigma_Ry=sigma,lambda_qsum=lam,lambda_qsum_from_mode_text=weighted,lambda_native_integral=li,lambda_printed_spectrum_integral=integ,omega_log_K=wlog,mu_star=.1,Tc_formula_K=tc,Tc_native_K=native_tc[j,2],DOS_EF_states_spin_Ry_cell=dosef,lambda_matdyn=mp[j][1],lambda_matdyn_spectrum_footer=footer_lambda,omega_log_matdyn_K=mp[j][2],a2F_matdyn_min=float(np.min(a2[:,1])),a2F_matdyn_negative_rows=int(np.sum(a2[:,1]<0))))
with (r/'tc-scan.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=scan[0].keys());w.writeheader();w.writerows(scan)
mu=np.arange(.08,.161,.01)
chosen=dat[3]; denom=chosen[1]-mu*(1+.62*chosen[1]); assert np.all(denom>0)
np.savetxt(r/'mu-sensitivity.csv',np.column_stack([mu,chosen[3]/1.2*np.exp(-1.04*(1+chosen[1])/denom)]),delimiter=',',header='mu_star,Tc_K',comments='')
summary=dict(low_frequency_lambda_cutoff_cm1=20.0,low_frequency_lambda_cutoff_source='QE7.5 PHonon/PH/elphon.f90:743-744 and 1087-1093, interpolated elphsum',low_frequency_cutoff_scope='lamb is set to zero below 20 cm^-1; gamma is still printed. Three Gamma residual modes fall below it; this does not establish a physical zero coupling.',material='fcc Al, one-atom primitive cell',nmodes=3,dense_k=[32]*3,coarse_k=[16]*3,q_mesh=[4]*3,q_irreducible=8,q_star_weight_sum=64,q_elph_files=len(list((r/'elph_dir').glob('elph.inp_lambda.*'))),q2r_elph_files=len(list((r/'elph_dir').glob('a2Fq2r.*'))),matdyn_elph_files=len(list((r/'elph_dir').glob('a2Fmatdyn.*'))),spectral_rows=af.shape[0],spectral_frequency_unit='THz',matdyn_spectral_frequency_unit='Ry',spectrum_max_THz=float(af[-1,0]),largest_computed_mode_THz=max(x['frequency_THz'] for x in rows),gaussian_spectrum_width_THz=.12,mode_records=len(rows),min_spectrum=float(np.min(af[:,1:])),spectrum_last_nonzero_THz=float(af[np.any(af[:,1:]!=0,axis=1),0][-1]),frequency_upper_margin_in_gaussian_widths=(14-max(x['frequency_THz'] for x in rows))/.12,a2Fsave_unchanged=hashlib.sha256((r/'tmp/al.a2Fsave').read_bytes()).hexdigest()==hashlib.sha256((r/'al.a2Fsave.k32').read_bytes()).hexdigest(),scan=scan,assessment='native complete; q/k/cutoff/smearing convergence not established; mu_star is assumed; no accepted material Tc')
assert summary['q2r_elph_files']==80 and summary['matdyn_elph_files']==10 and summary['a2Fsave_unchanged']
for n in ['al.dense','al.scf','al.elph','q2r','matdyn-dos']:
    assert 'JOB DONE.' in (r/(n+'.out')).read_text()
    assert (r/(n+'.err')).stat().st_size==0
    assert 'convergence NOT achieved' not in (r/(n+'.out')).read_text()
assert (r/'lambda.err').stat().st_size==0
(r/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('8 irreducible q points; star weights sum to 64; 3 modes; 10 electronic widths; 240 mode records')
print('80 q2r el-ph inputs; 10 real-space el-ph files; dense a2Fsave hash preserved')
print(f"Maximum computed mode = {summary['largest_computed_mode_THz']:.6f} THz; spectrum end = {af[-1,0]:.3f} THz")
print('sigma_Ry  lambda_qsum  lambda_integral  omega_log_K  Tc_mu0.10_K')
for s in scan: print(f"{s['sigma_Ry']:.3f}     {s['lambda_qsum']:.6f}      {s['lambda_printed_spectrum_integral']:.6f}       {s['omega_log_K']:.3f}      {s['Tc_formula_K']:.6f}")
print('Native calculation completed; scientific convergence not established.')
```

</details>

<details>
<summary>compare_spectral_grids.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Quantify Al k32/k48 Eliashberg spectral and moment differences; no plotting."""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def read_a2f(path: Path):
    lines = path.read_text().splitlines()
    header = next((line.split() for line in lines if line.strip()), None)
    if not header or len(header) < 3:
        raise ValueError(f"{path}: missing frequency/sigma header")
    sigmas = [float(x) for x in header[2:]]
    groups = {sigma: [] for sigma in sigmas}
    for line in lines[1:]:
        parts = line.split()
        if not parts or parts[0].startswith("#"):
            continue
        values = [float(x) for x in parts]
        if len(values) != len(sigmas) + 1 or any(not math.isfinite(x) for x in values):
            raise ValueError(f"{path}: malformed/non-finite alpha2F row")
        for sigma, a2f in zip(sigmas, values[1:]):
            groups[sigma].append((values[0], a2f))
    for sigma, rows in groups.items():
        xs = [r[0] for r in rows]
        if len(rows) < 2 or any(b <= a for a, b in zip(xs, xs[1:])):
            raise ValueError(f"{path}: invalid frequency axis at sigma={sigma}")
    return groups

def trapezoid(xs, ys):
    return sum((xs[i] - xs[i - 1]) * (ys[i] + ys[i - 1]) / 2 for i in range(1, len(xs)))

def read_pairs(path: Path):
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    return {float(r["sigma_Ry"]): r for r in rows}

def signed_summary(values):
    return {"min": min(values), "max": max(values), "max_abs": max(abs(v) for v in values)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True, help="supercon-al-tc package root")
    p.add_argument("--outdir", type=Path, required=True)
    a = p.parse_args()
    root, outdir = a.root, a.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    path32, path48 = root / "k32/alpha2F.dat", root / "k48/alpha2F.dat"
    s32, s48 = read_a2f(path32), read_a2f(path48)
    paired_path = root / "comparison-k32-k48/paired-tc.csv"
    paired = read_pairs(paired_path)
    sigmas = sorted(set(s32) & set(s48) & set(paired))
    if len(sigmas) != 10 or set(sigmas) != set(s32) or set(sigmas) != set(s48) or set(sigmas) != set(paired):
        raise ValueError("Expected exactly ten common sigma samples in both alpha2F files and paired Tc table")
    result_rows = []
    max_rounded_spectrum_lambda_mismatch = 0.0
    for sigma in sigmas:
        left, right = s32[sigma], s48[sigma]
        if [x[0] for x in left] != [x[0] for x in right]:
            raise ValueError(f"Frequency grids differ at sigma={sigma}")
        row = paired[sigma]
        xs = [r[0] for r in left]
        diff_integrand = [0.0 if x == 0.0 else 2.0 * abs(l[1] - r[1]) / x for x, l, r in zip(xs, left, right)]
        l1 = trapezoid(xs, diff_integrand)
        max_idx = max(range(len(xs)), key=lambda i: abs(left[i][1] - right[i][1]))
        # The native alpha2F.dat prints five decimals; this integral diagnoses spectral-shape
        # differences from that saved output and is not substituted for lambda.x's full-precision moments.
        lam_a2f_32 = trapezoid(xs, [0.0 if x == 0.0 else 2.0 * r[1] / x for x, r in zip(xs, left)])
        lam_a2f_48 = trapezoid(xs, [0.0 if x == 0.0 else 2.0 * r[1] / x for x, r in zip(xs, right)])
        max_rounded_spectrum_lambda_mismatch = max(
            max_rounded_spectrum_lambda_mismatch,
            abs(lam_a2f_32 - float(row["lambda_spectrum_rebuilt_A"])),
            abs(lam_a2f_48 - float(row["lambda_spectrum_rebuilt_B"])),
        )
        record = {
            "sigma_Ry": sigma,
            "lambda_qsum_32": float(row["lambda_qsum_rebuilt_A"]),
            "lambda_qsum_48": float(row["lambda_qsum_rebuilt_B"]),
            "delta_lambda_qsum_32_minus_48": float(row["lambda_qsum_rebuilt_A"]) - float(row["lambda_qsum_rebuilt_B"]),
            "lambda_spectrum_32": float(row["lambda_spectrum_rebuilt_A"]),
            "lambda_spectrum_48": float(row["lambda_spectrum_rebuilt_B"]),
            "delta_lambda_spectrum_32_minus_48": float(row["lambda_spectrum_rebuilt_A"]) - float(row["lambda_spectrum_rebuilt_B"]),
            "weighted_L1_spectral_difference_lambda_from_saved_a2F": l1,
            "weighted_L1_relative_to_mean_lambda_percent": 100.0 * l1 / ((float(row["lambda_spectrum_rebuilt_A"]) + float(row["lambda_spectrum_rebuilt_B"])) / 2.0),
            "max_abs_delta_a2F_from_saved_files": abs(left[max_idx][1] - right[max_idx][1]),
            "frequency_at_max_abs_delta_a2F_THz": xs[max_idx],
            "omega_log_32_K": float(row["omega_log_rebuilt_K_A"]),
            "omega_log_48_K": float(row["omega_log_rebuilt_K_B"]),
            "delta_omega_log_32_minus_48_K": float(row["omega_log_rebuilt_K_A"]) - float(row["omega_log_rebuilt_K_B"]),
            "Tc_32_K": float(row["Tc_rebuilt_K_A"]),
            "Tc_48_K": float(row["Tc_rebuilt_K_B"]),
            "delta_Tc_32_minus_48_K": float(row["Tc_rebuilt_K_A"]) - float(row["Tc_rebuilt_K_B"]),
        }
        result_rows.append(record)
    fields = list(result_rows[0])
    with (outdir / "spectral-grid-differences.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(result_rows)
    summary = {
        "method": "For each native sigma, compare the paired saved alpha2F.dat arrays pointwise on their common 0-14 THz grid. Weighted L1 spectral difference is integral 2*abs(alpha2F_32-alpha2F_48)/nu dnu. The source alpha2F.dat values are printed to five decimals; lambda, omega_log and Tc are reconstructed independently from the exact printed elph.inp_lambda records.",
        "source_files": {
            "k32_alpha2F_sha256": sha256(path32),
            "k48_alpha2F_sha256": sha256(path48),
            "paired_tc_sha256": sha256(paired_path),
        },
        "sigma_count": len(result_rows),
        "frequency_bins_per_sigma": len(s32[sigmas[0]]),
        "frequency_range_THz": [s32[sigmas[0]][0][0], s32[sigmas[0]][-1][0]],
        "max_abs_lambda_integral_difference_from_five_decimal_alpha2F_vs_rebuilt_source": max_rounded_spectrum_lambda_mismatch,
        "delta_lambda_qsum_32_minus_48": signed_summary([r["delta_lambda_qsum_32_minus_48"] for r in result_rows]),
        "delta_lambda_spectrum_32_minus_48": signed_summary([r["delta_lambda_spectrum_32_minus_48"] for r in result_rows]),
        "weighted_L1_relative_to_mean_lambda_percent": {
            "min": min(r["weighted_L1_relative_to_mean_lambda_percent"] for r in result_rows),
            "max": max(r["weighted_L1_relative_to_mean_lambda_percent"] for r in result_rows),
            "max_at_sigma_Ry": max(result_rows, key=lambda r: r["weighted_L1_relative_to_mean_lambda_percent"])["sigma_Ry"],
        },
        "delta_omega_log_32_minus_48_K": signed_summary([r["delta_omega_log_32_minus_48_K"] for r in result_rows]),
        "delta_Tc_32_minus_48_K": signed_summary([r["delta_Tc_32_minus_48_K"] for r in result_rows]),
        "tc_curve_crossings": 0 if all(r["delta_Tc_32_minus_48_K"] > 0.0 for r in result_rows) else "review required",
        "interpretation": "This is a dense-k comparison at fixed 16^3 response k, 4^3 q, and common smearing values. It supplies spectral and moment evidence for those two branches, but the smearing scan is not by itself a k/q convergence proof.",
    }
    (outdir / "spectral-grid-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("sigma lambda_q32 lambda_q48 delta_lambda_q L1_spectrum_pct d_omega_log_K delta_Tc_K")
    for r in result_rows:
        print(f"{r['sigma_Ry']:.3f} {r['lambda_qsum_32']:.9f} {r['lambda_qsum_48']:.9f} "
              f"{r['delta_lambda_qsum_32_minus_48']:+.9f} "
              f"{r['weighted_L1_relative_to_mean_lambda_percent']:.5f} "
              f"{r['delta_omega_log_32_minus_48_K']:+.3f} {r['delta_Tc_32_minus_48_K']:+.9f}")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
```

</details>

```console
maxwell@maxwell:~/al/epc-q4$ ../.venv/bin/python analyse_epc.py > analysis.out
maxwell@maxwell:~/al/epc-q4$ cat analysis.out
8 irreducible q points; star weights sum to 64; 3 modes; 10 electronic widths; 240 mode records
80 q2r el-ph inputs; 10 real-space el-ph files; dense a2Fsave hash preserved
Maximum computed mode = 9.936574 THz; spectrum end = 14.000 THz
sigma_Ry  lambda_qsum  lambda_integral  omega_log_K  Tc_mu0.10_K
0.005     0.430378      0.430437       355.877      2.212103
0.010     0.371061      0.371118       344.606      0.915531
0.015     0.370295      0.370354       343.420      0.900166
0.020     0.374486      0.374545       343.741      0.969046
0.025     0.374613      0.374671       343.537      0.970575
0.030     0.373773      0.373833       342.831      0.954739
0.035     0.373581      0.373641       342.006      0.949300
0.040     0.374086      0.374146       341.243      0.955437
0.045     0.375022      0.375083       340.631      0.969102
0.050     0.376041      0.376101       340.145      0.984595
Native calculation completed; scientific convergence not established.
```

打印后的 α²F 只保留有限小数，0.020 Ry 一列独立积分得到 0.374545，与程序内部积分 0.374547 的差别很小。这个交叉核对用于发现列号、单位或截断范围错误，不能代替 k/q 网格收敛。

![fcc Al 的 α²F 及累计 λ](/Atlas/examples/al/figures/eliashberg-a2f.png)

上图能看到谱权重集中在哪些频率；下面的累计积分则直接显示这些频段对 λ 的贡献。由于被积函数带有 1/ν，相同的谱函数面积放在不同频率，对 λ 的影响也不一样。

![电子展宽下的 λ 与对数平均频率](/Atlas/examples/al/figures/epc-smearing.png)

0.005 Ry 的结果明显偏离更宽的几组。后面几组接近，只能说明在当前网格上对这一段展宽不太敏感；没有更密电子网格和真实 q 网格对照，不能据此宣布 λ 已收敛。图中也保留了 matdyn 路线的结果。这次 matdyn 在 0.005 Ry 的谱中还有 146 行负值，最小值为 −0.00554175；0.010 Ry 有 9 行微小负值。原文件保留这些数值，不取绝对值或截零；这些列需要继续检查实空间插值与 q 网格，不能作为已接受的非负谱使用。两条路线的数值积分与插值不同，尤其在较大展宽时差别可见，不能从其中各挑一个数拼成一组结果。


## 从同一份谱同时提取 λ、ωlog 与二阶矩

普通频率 ν 采用同一固定单位时，三个积分分别为：

**λspec = 2∫ α²F(ν)/ν dν**

**νlog = exp{(2/λspec)∫ [α²F(ν)/ν] ln(ν) dν}**

**ν̄₂ = {(2/λspec)∫ α²F(ν)ν dν}<sup>1/2</sup>**

对数可理解为先对 `ν/(1 THz)` 取对数，最终恢复 THz。计算频率矩的归一化 λ 要由同一份谱得到；不能把另一条插值路线的 λ 填进分母。零频点不直接做除法或取对数。本例零频谱为零，可以从正频点积分；这不是允许在其他材料中删掉异常低频峰或实质性虚频。

新增脚本从八份电声原件重建 QE 7.5 的 2000 点 Gaussian 谱，复现程序的内部积分，再对已打印的谱做梯形积分，区分打印舍入与错列、错单位。对负谱不取绝对值、不裁零，也不为它生成可接受的频率矩。

```console
maxwell@maxwell:~/al/tc-route$ mkdir -p evidence
maxwell@maxwell:~/al/tc-route$ python3 scripts/verify_tc_chain.py --source <工作目录>/al/epc-q4 --output data > evidence/verify.out
```
```console
maxwell@maxwell:~/al/tc-route$ cat evidence/verify.out
q points=8; weights=64; modes=3; widths=10; mode records=240
printed-omega^2 reconstruction=0.087851..9.936533 THz; negative omega^2=0
ph.x printed maximum=9.936574 THz; frequency difference comes from printed w2 precision
lambda.x grid=2000 points, 0..14 THz; Gaussian parameter=0.12 THz
sigma_Ry lambda_qsum lambda_spectrum omega_log_K omega2_K Tc_QE_K Tc_full_AD_K
0.005 0.43037813 0.43043738 355.87701 370.56657 2.212105 2.248232
0.010 0.37106094 0.37111797 344.60678 363.11888 0.915532 0.928052
0.015 0.37029531 0.37035355 343.41976 362.60101 0.900170 0.912494
0.020 0.37448594 0.37454456 343.74087 363.33106 0.969044 0.982511
0.025 0.37461250 0.37467149 343.53737 363.44354 0.970568 0.984079
0.030 0.37377344 0.37383269 342.83124 363.00639 0.954746 0.968016
0.035 0.37358125 0.37364098 342.00604 362.39378 0.949304 0.962508
0.040 0.37408594 0.37414604 341.24361 361.79075 0.955437 0.968761
0.045 0.37502188 0.37508257 340.63107 361.29676 0.969100 0.982670
0.050 0.37604063 0.37610138 340.14505 360.89644 0.984588 0.998426
sigma=0.020: f1=1.01206929; f2=1.00080168; spectral simple Tc=0.970016 K
matdyn negative rows by width: 146, 9, 0, 0, 0, 0, 0, 0, 0, 0
Cross-check completed. Material Tc convergence is not established.
```

`Tc_full_AD_K` 是脚本从同一非负谱求得的含 f₁、f₂ 结果，不是 QE 原生打印值。具体公式与 μ* 接着到 [Tc 页](/Atlas/m/allen-dynes/qe/)逐项代入。

![同一电子展宽下，两条谱函数路线及累计 λ](/Atlas/examples/al/tc-route/figures/a2f-route-check.png)

图中固定 0.020 Ry，将 Ry 横轴换成 THz 后比较原值。两条离散处理接近不等于真实 q 网格已收敛。

![matdyn 原生负值与零附近放大](/Atlas/examples/al/tc-route/figures/a2f-negative-values.png)

右幅只改变查看范围，没有修改数据。0.005 Ry 的 146 行负值和 0.010 Ry 的 9 行微小负值需要继续排查；直接求和谱非负，不会自动消除这条插值路线的问题。

在公开包内运行提取与绘图：

在解包后的 `al` 目录中执行：

```bash
cd tc-route
python3 scripts/verify_tc_chain.py --source ../epc-q4 --output data
python3 scripts/plot_tc_chain.py --data data --output figures
```

提取只需 Python 标准库，绘图使用 NumPy、Matplotlib。脚本保留原始符号，不再乘自旋因子；网页 PNG 用大字号，PDF 用 7 pt 正文、8 pt 黑色粗体面板标记和可编辑字体，不加背景网格。

新增下载：[提取与交叉计算](/Atlas/examples/al/tc-route/scripts/verify_tc_chain.py) · [绘图脚本](/Atlas/examples/al/tc-route/scripts/plot_tc_chain.py) · [λ、频率矩与公式表](/Atlas/examples/al/tc-route/data/tc-formula-scan.csv) · [两条谱及累计积分](/Atlas/examples/al/tc-route/data/spectra-and-integrals.csv) · [源文件与单位核验](/Atlas/examples/al/tc-route/data/tc-chain-checks.json)。

<details>
<summary>plot_tc_chain.py 的完整源码</summary>

```python
#!/usr/bin/env python3
"""Render verified Al EPC data; run on the visualization machine.
Requires NumPy and Matplotlib. This script never runs QE.
Default: web PNG plus publication PDF, with separate font scales.
"""
from pathlib import Path
import argparse,csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BLUE,ORANGE,BLACK='#0072B2','#D55E00','#222222'

def read_rows(path):
    with path.open() as f:return list(csv.DictReader(f))

def number(rows,key):return np.array([float(r[key]) for r in rows])

def style(publication):
    fs=7 if publication else 12
    plt.rcParams.update({'font.family':'sans-serif',
        'font.sans-serif':['Arial','Helvetica','DejaVu Sans'],
        'font.size':fs,'axes.labelsize':fs,'xtick.labelsize':fs,'ytick.labelsize':fs,
        'legend.fontsize':fs,'axes.linewidth':.65,'lines.linewidth':1 if publication else 1.5,
        'xtick.major.width':.65,'ytick.major.width':.65,'xtick.major.size':2.5,'ytick.major.size':2.5,
        'axes.spines.top':False,'axes.spines.right':False,'axes.grid':False,
        'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white',
        'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'})
    return fs

def panel(ax,label,publication):
    ax.text(-.15,1.035,label,transform=ax.transAxes,fontweight='bold',
            fontsize=8 if publication else 14,color='black',va='bottom')
    ax.tick_params(direction='out')

def save(fig,out,name,publication):
    fig.savefig(out/(name+('.pdf' if publication else '.png')),
                dpi=240,bbox_inches=None if publication else 'tight',pad_inches=.12)
    plt.close(fig)

def draw(data,out,publication):
    style(publication)
    width,height=(183/25.4,3.35) if publication else (9,4.3)
    spec=read_rows(data/'spectra-and-integrals.csv')
    scan=read_rows(data/'tc-formula-scan.csv');mu=read_rows(data/'mu-star-scan.csv')
    report=json.loads((data/'tc-chain-checks.json').read_text())
    fig,ax=plt.subplots(1,2,figsize=(width,height),layout='constrained')
    for route,color,line,label in [('lambda.x',BLUE,'-','Direct q sum + Gaussian'),
                                  ('matdyn.x',ORANGE,'--','q2r / matdyn interpolation')]:
        rows=[r for r in spec if r['route']==route and abs(float(r['sigma_Ry'])-.02)<1e-9]
        x=number(rows,'frequency_THz')
        ax[0].plot(x,number(rows,'a2F'),color=color,linestyle=line,label=label)
        ax[1].plot(x,number(rows,'cumulative_lambda'),color=color,linestyle=line,label=label)
    ax[0].set(xlabel='Frequency (THz)',ylabel=r'$\alpha^2F$')
    ax[1].set(xlabel='Frequency (THz)',ylabel=r'Cumulative $\lambda$')
    for i,a in enumerate(ax):a.set_xlim(0,14);panel(a,chr(97+i),publication)
    ax[1].legend(frameon=False,loc='lower right')
    save(fig,out,'a2f-route-check',publication)

    fig,ax=plt.subplots(1,2,figsize=(width,height),layout='constrained')
    x=number(scan,'sigma_Ry')
    ax[0].plot(x,number(scan,'Tc_QE_replay_K'),'o-',color=BLACK,markersize=3,label='QE simplified')
    ax[0].plot(x,number(scan,'Tc_spectrum_simple_K'),'--',color=BLUE,label='Spectrum simplified')
    ax[0].plot(x,number(scan,'Tc_spectrum_full_AD_K'),'s:',color=ORANGE,markersize=3,label=r'Spectrum with $f_1f_2$')
    ax[0].set(xlabel='Electronic broadening (Ry)',ylabel=r'Formula $T_c$ (K)')
    x=number(mu,'mu_star')
    ax[1].plot(x,number(mu,'Tc_QE_rounded_input_K'),'o-',color=BLACK,markersize=3,label='QE rounded inputs')
    ax[1].plot(x,number(mu,'Tc_spectrum_simple_K'),'--',color=BLUE,label='Spectrum simplified')
    ax[1].plot(x,number(mu,'Tc_spectrum_full_AD_K'),'s:',color=ORANGE,markersize=3,label=r'Spectrum with $f_1f_2$')
    ax[1].set(xlabel=r'Assumed $\mu^*$',ylabel=r'Formula $T_c$ (K)')
    for i,a in enumerate(ax):a.set_ylim(bottom=0);panel(a,chr(97+i),publication)
    ax[0].legend(frameon=False)
    save(fig,out,'tc-formulas',publication)

    fig,ax=plt.subplots(1,2,figsize=(width,height),layout='constrained')
    for sigma,color,line in [(.005,ORANGE,'--'),(.020,BLUE,'-')]:
        rows=[r for r in spec if r['route']=='matdyn.x' and abs(float(r['sigma_Ry'])-sigma)<1e-9]
        x=number(rows,'frequency_THz');y=number(rows,'a2F')
        ax[0].plot(x,y,color=color,linestyle=line,label=f'{sigma:.3f} Ry')
        # Same raw values; only the viewing limits change for the right panel.
        ax[1].plot(x,y,color=color,linestyle=line)
    ax[0].axhline(0,color=BLACK,linewidth=.6);ax[1].axhline(0,color=BLACK,linewidth=.6)
    ax[0].set(xlabel='Frequency (THz)',ylabel=r'Raw interpolated $\alpha^2F$')
    ax[1].set(xlabel='Frequency (THz)',ylabel=r'Raw $\alpha^2F$ near zero',ylim=(-.007,.015))
    for i,a in enumerate(ax):panel(a,chr(97+i),publication)
    ax[0].legend(frameon=False)
    save(fig,out,'a2f-negative-values',publication)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=Path('data'))
    p.add_argument('--output',type=Path,default=Path('figures'))
    p.add_argument('--mode',choices=['both','web','publication'],default='both')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    for pub in ([False,True] if a.mode=='both' else [a.mode=='publication']):
        draw(a.data,a.output,pub)
    print('Raw values retained; no clipping, absolute-value repair, or extra spin factor.')
    print('Publication PDF: 7 pt text, 8 pt bold black panel labels, embedded type-42 fonts.')
    print('Scientific status: formula demonstration; material Tc convergence not established.')

if __name__=='__main__':main()
```

</details>

原始输入、程序输出和独立检查脚本可以逐个查看：[al.dense.in](/Atlas/examples/al/epc-q4/al.dense.in), [al.dense.out](/Atlas/examples/al/epc-q4/al.dense.out), [al.scf.in](/Atlas/examples/al/epc-q4/al.scf.in), [al.scf.out](/Atlas/examples/al/epc-q4/al.scf.out), [al.elph.in](/Atlas/examples/al/epc-q4/al.elph.in), [al.elph.out](/Atlas/examples/al/epc-q4/al.elph.out), [continue.slurm](/Atlas/examples/al/epc-q4/continue.slurm), [q2r.in](/Atlas/examples/al/epc-q4/q2r.in), [q2r.out](/Atlas/examples/al/epc-q4/q2r.out), [matdyn-dos.in](/Atlas/examples/al/epc-q4/matdyn-dos.in), [matdyn-dos.out](/Atlas/examples/al/epc-q4/matdyn-dos.out), [lambda.in](/Atlas/examples/al/epc-q4/lambda.in), [lambda.out](/Atlas/examples/al/epc-q4/lambda.out), [lambda.dat](/Atlas/examples/al/epc-q4/lambda.dat), [alpha2F.dat](/Atlas/examples/al/epc-q4/alpha2F.dat), [analyse_epc.py](/Atlas/examples/al/epc-q4/analyse_epc.py), [tc-scan.csv](/Atlas/examples/al/epc-q4/tc-scan.csv)。绘图代码为 [plot_epc.py](/Atlas/examples/al/plot_epc.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/al/atlas_plot_style.py)）。

<details>
<summary>plot_epc.py 的完整源码</summary>

```python
"""Run from the downloaded Al bundle root: python plot_epc.py.
Inputs stay in epc-q4/. Figures are written to figures/.
"""

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent;d=r/'epc-q4';out=r/'figures';out.mkdir(exist_ok=True)
a=np.loadtxt(d/'alpha2F.dat')
s=np.genfromtxt(d/'tc-scan.csv',delimiter=',',names=True)
colors=['#009e73','#d55e00','#cc79a7']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
def save(fig,name):
    fig.savefig(out/(name+'.png'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(2,1,figsize=(7.2,6),sharex=True)
for j,c in zip([0,3,9],colors):
    ax[0].plot(a[:,0],a[:,j+1],color=c,label=f"Electronic width {s['sigma_Ry'][j]:.3f} Ry")
    integ=np.zeros(len(a));f=np.zeros(len(a));f[1:]=2*a[1:,j+1]/a[1:,0]
    integ[1:]=np.cumsum(.5*(f[1:]+f[:-1])*np.diff(a[:,0]))
    ax[1].plot(a[:,0],integ,color=c)
ax[0].set(ylabel=r'$\alpha^2 F$');ax[0].legend(frameon=False)
ax[1].set(xlabel='Phonon frequency (THz)',ylabel=r'Cumulative $\lambda(\nu)$',xlim=(0,14))
fig.suptitle('fcc Al | 32³ electron grid, 4³ phonon grid\nUnconverged teaching calculation; Gaussian frequency width 0.12 THz',fontsize=11)
fig.tight_layout();save(fig,'eliashberg-a2f')
fig,ax=plt.subplots(1,2,figsize=(9,3.9))
ax[0].plot(s['sigma_Ry'],s['lambda_qsum'],'o-',color=colors[0],label='q-point sum')
ax[0].plot(s['sigma_Ry'],s['lambda_printed_spectrum_integral'],'x--',color=colors[1],label='Spectrum integral')
ax[0].plot(s['sigma_Ry'],s['lambda_matdyn'],'s:',color=colors[2],label='matdyn real-space interpolation')
ax[0].set(xlabel='Electronic double-delta width (Ry)',ylabel=r'$\lambda$');ax[0].legend(frameon=False,fontsize=8)
ax[1].plot(s['sigma_Ry'],s['omega_log_K'],'o-',color=colors[0]);ax[1].set(xlabel='Electronic double-delta width (Ry)',ylabel=r'$\omega_{\log}$ (K)')
fig.suptitle('Changing electronic width does not establish k/q convergence',fontsize=11);fig.tight_layout();save(fig,'epc-smearing')
mu=np.genfromtxt(d/'mu-sensitivity.csv',delimiter=',',names=True)
fig,ax=plt.subplots(1,2,figsize=(9,3.8))
ax[0].plot(s['sigma_Ry'],s['Tc_formula_K'],'o-',color=colors[0]);ax[0].set(xlabel='Electronic double-delta width (Ry)',ylabel=r'Formula $T_c$ (K)',title=r'Assumed $\mu^*=0.10$')
ax[1].plot(mu['mu_star'],mu['Tc_K'],'o-',color=colors[1]);ax[1].set(xlabel=r'Assumed $\mu^*$',ylabel=r'Formula $T_c$ (K)',title='Electronic width 0.020 Ry')
fig.suptitle('Simplified Allen–Dynes expression (f₁=f₂=1); not a converged Al prediction',fontsize=11);fig.tight_layout();save(fig,'allen-dynes')
rows=list(csv.DictReader((d/'linewidth.csv').open()))
fig,ax=plt.subplots(2,1,figsize=(7.5,6),sharex=True)
for m,c in zip([1,2,3],colors):
    sel=[x for x in rows if int(x['mode'])==m and abs(float(x['sigma_Ry'])-.020)<1e-8]
    q=np.array([int(x['q_index']) for x in sel]);x=q+(m-2)*.22
    ax[0].bar(x,[float(v['gamma_GHz']) for v in sel],.20,color=c,label=f'Mode {m}')
    ax[1].bar(x,[float(v['lambda_mode']) for v in sel],.20,color=c)
ax[0].set(ylabel=r'QE linewidth $\gamma$ (GHz)');ax[0].legend(frameon=False,ncol=3)
ax[1].set(ylabel=r'Mode $\lambda_{q\nu}$',xlabel='Irreducible q-point index (file order; not a band path)',xticks=range(1,9))
fig.suptitle('fcc Al | electronic width 0.020 Ry\nRaw ph.x values; Γ acoustic residual is not an optical mode',fontsize=11)
fig.tight_layout();save(fig,'phonon-linewidth')
print('Wrote eliashberg-a2f, epc-smearing, allen-dynes, phonon-linewidth as PNG and PDF')
```

</details>

## 二维异质结 ZrCl₂/Sc₂C：含声子带隙体系的 α²F(ω) 谱积分上限核验与共享频率轴三联图

在单质金属 Al 中，3 条声子支连续分布在 `0–9.94 THz`，`lambda.in` 设 `emax = 14 THz` 即可覆盖全谱。而在同时包含重过渡金属（Zr、Sc、Cl）与轻元素（C 或 N）的层状异质结中，声子谱往往存在宽达数 THz 的**声子带隙（Phononic Gap）**，高频轻原子光学支容易超出 `emax = 10 THz` 的积分上限。

在 **`ZrCl₂/Sc₂C`**（[完整双网格计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中：
- 重原子 `Zr/Sc/Cl` 的 15 条声学与中低频光学支分布在 `0–10.11 THz`（直接 DFPT 网格为 `0–10.02 THz`）；
- 轻原子 C 原子位移主导的 3 条高频光学支（ν=16–18）跨越 10.11–12.49 THz 的声子带隙，分布在 12.49–17.11 THz（原始 DFPT 网格为 12.38–17.11 THz；σ=0.003 Ry 下，Γ 点第 16 支面外模与第 17、18 支简并面内模的线宽在 ph64 中为 260.01–318.58 GHz，在 ph96 中为 297.74–322.13 GHz）。C-2p 是电子轨道投影标签，不是原子振动模式标签。


匹配的 10 THz 输入首行是 10 0.12 1（Methfessel–Paxton）。在 σ=0.003 Ry 下，直接 q 加权 λ 为 ph64=2.459034、ph96=2.451080；谱积分分别为 2.427435 和 2.418456。QE 7.1 lambda.f90 限定 α²F 频率网格与 ωlog 的计算范围，高于 emax 的模式仍可能通过展宽尾部贡献较低频率。18 THz 保存表在 σ=0.003 Ry 的积分值为 ph64=2.458955、ph96=2.451001；全表直接 λ 与积分的最大绝对差为 0.000102。可是 18 THz 表尚未与生成输入、运行命令或 QE 可执行文件绑定，ph64.1/ph96.1 的 18 0.12 1 输入只是候选文件，不能证明输出来源，也不能将变化归因于只提高 emax。参见 <a href="https://raw.githubusercontent.com/QEF/q-e/qe-7.1/PHonon/PH/lambda.f90">QE 7.1 lambda.f90 源码</a>。

下图采用共享频率纵轴（0–18 THz）的三联图版式。为保持输入来源可追溯，右侧谱曲线来自有匹配 10 THz 输入记录的 alpha2F.dat；18 THz 保存输出来源仍待核实。

<figure><img src="/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-phonon-epc.png" alt="ZrCl₂/Sc₂C 的声子色散、原子分辨 PHDOS 与有匹配 10 THz 输入的 α²F 表" loading="lazy"/><figcaption>ZrCl₂/Sc₂C 三联图：（左）声子色散与模式耦合，红虚线标出 10 THz 频率网格上限；（中）原子分辨 PHDOS，C 的高频光学模由原子位移识别；（右）来自匹配 10 THz 输入的保存 α²F 表。18 THz 输出表的生成来源尚未闭合。</figcaption></figure>

保存文件（18 THz 输出来源待核）：[ph96 alpha2F.emax18.dat](/Atlas/examples/zrcl2-sc2c/ph96/alpha2F.emax18.dat) · [ph96 lambdax.emax18.out](/Atlas/examples/zrcl2-sc2c/ph96/lambdax.emax18.out) · [zrclscc.phdos](/Atlas/examples/zrcl2-sc2c/ph64/zrclscc.phdos) · [绘图脚本 plot_zrcl2_sc2c.py](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py)。

<details>
<summary>plot_zrcl2_sc2c.py 的完整源码</summary>

```python
#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import numpy as np

ZR_DIR = Path(__file__).resolve().parent
for candidate in (ZR_DIR, ZR_DIR.parent, ZR_DIR.parents[1] / 'scripts'):
    if (candidate / 'atlas_plot_style.py').exists():
        sys.path.insert(0, str(candidate))
        break

import atlas_plot_style

sys.path.insert(0, str(ZR_DIR))
from tc_table_audit import piecewise_linear_crossings, write_report

PALETTE = {
    'Ink': '#162232',
    'Slate': '#324255',
    'Muted': '#5a6b80',
    'Navy': '#0072b2',
    'Blue': '#2968a8',
    'SoftBlue': '#d6e6f4',
    'Teal': '#009e73',
    'SoftTeal': '#d7ece8',
    'Amber': '#e69f00',
    'Rust': '#d55e00',
    'Coral': '#cc79a7',
    'WarmTint': '#f4efe6',
}

CM1_TO_THZ = 1.0 / 33.3564095198152
FIG_OUT_DIR = (
    ZR_DIR.parents[1] / 'figures' / 'zrcl2-sc2c'
    if (ZR_DIR.parents[1] / 'figures').exists()
    else ZR_DIR / 'figures'
)


def apply_atlas_style() -> None:
    atlas_plot_style.install()


def style_axis(ax) -> None:
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def save_figure(fig, stem_name: str) -> None:
    FIG_OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_OUT_DIR / f'{stem_name}.png')
    plt.close(fig)


def parse_zrcl2_fatbands() -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133  # eV from scf/pwx.out
    data_dir = ZR_DIR / 'scf'
    gnu_path = data_dir / 'bands.dat.gnu'
    proj_path = data_dir / 'fatbands.projwfc_up'
    proj_lines = [line for line in proj_path.read_text().splitlines() if line.strip()]
    header_rows = [
        idx for idx, line in enumerate(proj_lines[:30])
        if len(line.split()) == 3 and all(part.isdigit() for part in line.split())
    ]
    if len(header_rows) != 1:
        raise ValueError(f'Expected one projection header; found {len(header_rows)}.')
    header_idx = header_rows[0]
    natomwfc, nk, nbnd = map(int, proj_lines[header_idx].split())
    if header_idx + 2 >= len(proj_lines):
        raise ValueError('Projection header is missing its spin flags or first state.')
    spin_flags = proj_lines[header_idx + 1].split()
    if len(spin_flags) != 2 or any(flag not in {'T', 'F'} for flag in spin_flags):
        raise ValueError(f'Unexpected projection spin flags: {spin_flags}')
    ptr = header_idx + 2

    raw = np.loadtxt(gnu_path)
    if raw.shape != (nbnd * nk, 2) or not np.isfinite(raw).all():
        raise ValueError(f'Unexpected bands.dat.gnu shape or nonfinite values: {raw.shape}')
    band_blocks = raw.reshape(nbnd, nk, 2)
    k_blocks = band_blocks[:, :, 0]
    if not np.allclose(k_blocks, k_blocks[0:1], rtol=0.0, atol=1e-8):
        raise ValueError('The k-distance sequence differs between band blocks.')
    k_dist = k_blocks[0]
    if not np.isclose(k_dist[0], 0.0, rtol=0.0, atol=1e-8):
        raise ValueError(f'Band path does not start at zero: {k_dist[0]}')
    if np.any(np.diff(k_dist) < -1e-8) or k_dist[-1] <= k_dist[0]:
        raise ValueError('Band path distances are not a forward, nonzero path.')
    bands_e = band_blocks[:, :, 1] - ef

    atom_elements = {1: 'Zr', 2: 'C', 3: 'Cl', 4: 'Cl', 5: 'Sc', 6: 'Sc'}
    group_by_site_orbital = {
        (1, 'D'): 'Zr-4d',
        (5, 'D'): 'Sc-3d',
        (6, 'D'): 'Sc-3d',
        (2, 'P'): 'C-2p',
        (3, 'P'): 'Cl-3p',
        (4, 'P'): 'Cl-3p',
    }
    expected_state_counts = {'Zr-4d': 5, 'Sc-3d': 10, 'C-2p': 3, 'Cl-3p': 6}
    grouped = {key: np.zeros((nbnd, nk)) for key in expected_state_counts}
    state_counts = {key: 0 for key in expected_state_counts}
    expected_ik = np.repeat(np.arange(1, nk + 1), nbnd)
    expected_ib = np.tile(np.arange(1, nbnd + 1), nk)
    block_len = nk * nbnd
    seen_state_ids = set()

    for expected_state in range(1, natomwfc + 1):
        if ptr >= len(proj_lines):
            raise ValueError(f'Projection file ended before state {expected_state}.')
        hdr = proj_lines[ptr].split()
        if len(hdr) < 4:
            raise ValueError(f'Malformed state header at line {ptr + 1}: {hdr}')
        state_id, atom_id = int(hdr[0]), int(hdr[1])
        element, orbital = hdr[2], hdr[3].upper()
        if state_id != expected_state or state_id in seen_state_ids:
            raise ValueError(f'Unexpected or duplicate state id {state_id}; expected {expected_state}.')
        seen_state_ids.add(state_id)
        if atom_id not in atom_elements or element != atom_elements[atom_id]:
            raise ValueError(f'State {state_id} has atom/element mismatch: #{atom_id} {element}.')
        angular_parts = [char for char in orbital if char in 'SPDF']
        if len(angular_parts) != 1:
            raise ValueError(f'State {state_id} has unrecognized orbital label {orbital}.')
        key = group_by_site_orbital.get((atom_id, angular_parts[0]))
        ptr += 1
        rows = []
        for row_index in range(block_len):
            if ptr >= len(proj_lines):
                raise ValueError(f'State {state_id} ended at projection row {row_index}.')
            fields = proj_lines[ptr].split()
            if len(fields) != 3:
                raise ValueError(f'Malformed projection row at line {ptr + 1}: {fields}')
            rows.append((int(fields[0]), int(fields[1]), float(fields[2])))
            ptr += 1
        state_data = np.asarray(rows, dtype=float)
        if not np.array_equal(state_data[:, 0].astype(int), expected_ik):
            raise ValueError(f'State {state_id} has an unexpected k-index sequence.')
        if not np.array_equal(state_data[:, 1].astype(int), expected_ib):
            raise ValueError(f'State {state_id} has an unexpected band-index sequence.')
        state_weights = state_data[:, 2]
        if not np.isfinite(state_weights).all():
            raise ValueError(f'State {state_id} contains nonfinite projection weights.')
        if key is not None:
            grouped[key] += state_weights.reshape(nk, nbnd).T
            state_counts[key] += 1

    if ptr != len(proj_lines) or len(seen_state_ids) != natomwfc:
        raise ValueError(f'Projection records do not close cleanly: consumed {ptr}/{len(proj_lines)} lines.')
    if state_counts != expected_state_counts:
        raise ValueError(f'Unexpected selected state counts: {state_counts}')
    if any(not np.isfinite(curve).all() for curve in grouped.values()):
        raise ValueError('Grouped projection weights contain nonfinite values.')
    return k_dist, bands_e, grouped

def parse_zrcl2_pdos() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    ef = 0.3133
    pdos_dir = ZR_DIR / 'pdos'

    def read_ldos(filename: str) -> tuple[np.ndarray, np.ndarray]:
        arr = np.loadtxt(pdos_dir / filename, comments='#')
        return arr[:, 0] - ef, arr[:, 1]

    e_grid, zr_4d = read_ldos('zrclscc.pdos_atm#1(Zr)_wfc#5(d)')
    _, c_2p = read_ldos('zrclscc.pdos_atm#2(C)_wfc#2(p)')
    _, cl1_3p = read_ldos('zrclscc.pdos_atm#3(Cl)_wfc#2(p)')
    _, cl2_3p = read_ldos('zrclscc.pdos_atm#4(Cl)_wfc#2(p)')
    _, sc1_3d = read_ldos('zrclscc.pdos_atm#5(Sc)_wfc#4(d)')
    _, sc2_3d = read_ldos('zrclscc.pdos_atm#6(Sc)_wfc#4(d)')
    tot_arr = np.loadtxt(pdos_dir / 'zrclscc.pdos_tot', comments='#')

    return e_grid, {
        'Total': tot_arr[:, 1],
        'Zr-4d': zr_4d,
        'Sc-3d': sc1_3d + sc2_3d,
        'C-2p': c_2p,
        'Cl-3p': cl1_3p + cl2_3p,
    }


def parse_zrcl2_bxsf() -> tuple[float, np.ndarray, np.ndarray, dict[int, np.ndarray]]:
    bxsf_path = ZR_DIR / 'FS' / 'zrclscc_fs.bxsf'
    lines = [l.strip() for l in bxsf_path.read_text().splitlines() if l.strip()]
    ef = 0.3154
    for l in lines[:20]:
        if 'Fermi Energy:' in l:
            ef = float(l.split(':')[1].strip())
            break

    b_idx = [i for i, l in enumerate(lines) if l.startswith('BEGIN_BANDGRID_3D')][0]
    nx, ny, nz = [int(x) for x in lines[b_idx + 2].split()]
    b1 = np.array([float(x) for x in lines[b_idx + 4].split()[:2]])
    b2 = np.array([float(x) for x in lines[b_idx + 5].split()[:2]])

    bands: dict[int, np.ndarray] = {}
    ptr = b_idx + 7
    while ptr < len(lines):
        line = lines[ptr]
        if line.startswith('BAND:'):
            b_num = int(line.split(':')[1].strip())
            ptr += 1
            vals: list[float] = []
            while ptr < len(lines) and not lines[ptr].startswith('BAND:') and not lines[ptr].startswith('END_BANDGRID_3D'):
                vals.extend([float(x) for x in lines[ptr].split()])
                ptr += 1
            arr3d = np.array(vals).reshape((nx, ny, nz))
            bands[b_num] = arr3d[:, :, 0] - ef
        else:
            ptr += 1

    return ef, b1, b2, bands


def render_zrcl2_sc2c_electronic() -> None:
    apply_atlas_style()
    k_dist, bands_e, grouped_w = parse_zrcl2_fatbands()
    e_dos, pdos = parse_zrcl2_pdos()
    _, b1, b2, fs_bands = parse_zrcl2_bxsf()

    fig = plt.figure(figsize=(10.2, 4.35))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.985, bottom=0.17, top=0.85,
        width_ratios=[1.35, 0.72, 1.15], wspace=0.22
    )
    ax_band = fig.add_subplot(gs[0, 0])
    ax_dos = fig.add_subplot(gs[0, 1], sharey=ax_band)
    ax_fs = fig.add_subplot(gs[0, 2])

    for ax in (ax_band, ax_dos, ax_fs):
        style_axis(ax)

    k_ticks = [k_dist[0], k_dist[50], k_dist[100], k_dist[150]]
    for x in k_ticks[1:-1]:
        ax_band.axvline(x, color='#ced8e3', lw=0.85, zorder=1)
    ax_band.axhline(0.0, color=PALETTE['Muted'], ls='--', lw=0.95, zorder=2)
    ax_band.axhspan(-0.16, 0.16, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)

    for ib in range(bands_e.shape[0]):
        e_curve = bands_e[ib]
        if e_curve.max() < -2.7 or e_curve.min() > 2.2:
            continue
        ax_band.plot(k_dist, e_curve, color='#7d8b9d', lw=0.85, alpha=0.75, zorder=2)

    orb_specs = [
        ('Cl-3p', PALETTE['Amber'], 72.0),
        ('C-2p', PALETTE['Rust'], 85.0),
        ('Sc-3d', PALETTE['Teal'], 92.0),
        ('Zr-4d', PALETTE['Navy'], 96.0),
    ]
    for label, color, scale in orb_specs:
        w_mat = grouped_w[label]
        for ib in range(bands_e.shape[0]):
            e_curve = bands_e[ib]
            if e_curve.max() < -2.6 or e_curve.min() > 2.1:
                continue
            w = w_mat[ib]
            mask = w > 0.04
            if np.any(mask):
                ax_band.scatter(
                    k_dist[mask],
                    e_curve[mask],
                    s=w[mask] * scale,
                    facecolors='none',
                    edgecolors=color,
                    linewidths=0.95,
                    alpha=0.88,
                    zorder=4,
                )

    ax_band.set_xlim(k_ticks[0], k_ticks[-1])
    ax_band.set_ylim(-2.5, 2.0)
    ax_band.set_xticks(k_ticks, [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$'])
    ax_band.set_ylabel(r'Energy $E - E_F$ (eV)')
    ax_band.set_title('Orbital fatbands', pad=8)

    legend_handles = [
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Navy'], markeredgewidth=1.3, markersize=5.2, label=r'Zr-$4d$ [#1]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Teal'], markeredgewidth=1.3, markersize=5.2, label=r'Sc-$3d$ [#5+#6]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Rust'], markeredgewidth=1.3, markersize=5.2, label=r'C-$2p$ [#2]'),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='none', markeredgecolor=PALETTE['Amber'], markeredgewidth=1.3, markersize=5.2, label=r'Cl-$3p$ [#3+#4]'),
    ]
    ax_band.legend(handles=legend_handles, loc='lower left', ncol=2, fontsize=8.0)

    ax_band.annotate(
        'Bands 26, 27\n(Zr-$4d$ [#1] / Sc-$3d$ [#5+#6])',
        xy=(k_dist[24], 0.04),
        xytext=(k_dist[8], 0.92),
        fontsize=8.0, zorder=10,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.8),
    )

    mask_dos = (e_dos >= -2.6) & (e_dos <= 2.1)
    ed = e_dos[mask_dos]
    ax_dos.axhline(0.0, color=PALETTE['Muted'], ls='--', lw=0.95, zorder=2)
    ax_dos.axhspan(-0.16, 0.16, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)

    ax_dos.fill_betweenx(ed, 0, pdos['Total'][mask_dos], color='#dfe6ef', alpha=0.55)
    ax_dos.plot(pdos['Total'][mask_dos], ed, color=PALETTE['Ink'], lw=1.05, label='Total')
    ax_dos.plot(pdos['Zr-4d'][mask_dos], ed, color=PALETTE['Navy'], lw=1.1, label=r'Zr-$4d$ [#1]')
    ax_dos.plot(pdos['Sc-3d'][mask_dos], ed, color=PALETTE['Teal'], lw=1.1, label=r'Sc-$3d$ [#5+#6]')
    ax_dos.plot(pdos['C-2p'][mask_dos], ed, color=PALETTE['Rust'], lw=1.05, label=r'C-$2p$ [#2]')
    ax_dos.plot(pdos['Cl-3p'][mask_dos], ed, color=PALETTE['Amber'], lw=0.95, label=r'Cl-$3p$ [#3+#4]')

    ax_dos.set_xlim(0, 6.8)
    ax_dos.set_xticks([0, 3, 6])
    ax_dos.set_xlabel('PDOS (eV$^{-1}$)')
    ax_dos.set_title('PDOS', pad=8)
    ax_dos.tick_params(labelleft=False)

    B = np.column_stack([b1, b2])
    B_inv = np.linalg.inv(B)
    angles = np.deg2rad(np.arange(0, 360, 60))
    R_k = 2.0 / 3.0
    bz_verts = np.column_stack([R_k * np.cos(angles), R_k * np.sin(angles)])

    nx = 220
    kx_lin = np.linspace(-0.75, 0.75, nx)
    ky_lin = np.linspace(-0.75, 0.75, nx)
    KX, KY = np.meshgrid(kx_lin, ky_lin)
    uv = B_inv @ np.vstack([KX.ravel(), KY.ravel()])
    u_mod = np.mod(uv[0], 1.0) * 64.0
    v_mod = np.mod(uv[1], 1.0) * 64.0

    def interp_periodic(grid65: np.ndarray) -> np.ndarray:
        i0 = np.floor(u_mod).astype(int) % 64
        j0 = np.floor(v_mod).astype(int) % 64
        i1 = (i0 + 1) % 64
        j1 = (j0 + 1) % 64
        du = u_mod - np.floor(u_mod)
        dv = v_mod - np.floor(v_mod)
        val = (
            (1 - du) * (1 - dv) * grid65[i0, j0]
            + du * (1 - dv) * grid65[i1, j0]
            + (1 - du) * dv * grid65[i0, j1]
            + du * dv * grid65[i1, j1]
        )
        return val.reshape(KX.shape)

    E26 = interp_periodic(fs_bands[26])
    E27 = interp_periodic(fs_bands[27])

    m_angles = np.deg2rad([30.0, 90.0, 150.0])
    inside_bz = np.ones_like(KX, dtype=bool)
    for ang in m_angles:
        inside_bz &= np.abs(KX * np.cos(ang) + KY * np.sin(ang)) <= (1.0 / np.sqrt(3.0) + 0.004)

    E26_masked = np.where(inside_bz, E26, np.nan)
    E27_masked = np.where(inside_bz, E27, np.nan)

    ax_fs.contourf(
        KX, KY, E26_masked,
        levels=np.linspace(-0.6, 0.4, 22),
        cmap='Blues_r', alpha=0.25, zorder=1,
    )
    ax_fs.contour(KX, KY, E26_masked, levels=[0.0], colors=[PALETTE['Navy']], linewidths=1.85, zorder=4)
    ax_fs.contour(KX, KY, E27_masked, levels=[0.0], colors=[PALETTE['Rust']], linewidths=1.85, zorder=5)

    bz_poly = Polygon(bz_verts, closed=True, fill=False, edgecolor=PALETTE['Ink'], lw=1.2, zorder=6)
    ax_fs.add_patch(bz_poly)

    gamma_pt = np.array([0.0, 0.0])
    m_pt = np.array([0.5, 1.0 / (2.0 * np.sqrt(3.0))])
    k_pt = np.array([1.0 / 3.0, 1.0 / np.sqrt(3.0)])
    path_pts = np.vstack([gamma_pt, m_pt, k_pt, gamma_pt])
    ax_fs.plot(path_pts[:, 0], path_pts[:, 1], color=PALETTE['Slate'], ls='--', lw=0.95, zorder=6)
    ax_fs.scatter([gamma_pt[0], m_pt[0], k_pt[0]], [gamma_pt[1], m_pt[1], k_pt[1]], color=PALETTE['Ink'], s=16, zorder=7)
    ax_fs.text(-0.07, -0.08, r'$\Gamma$', fontsize=8.5, fontweight='bold')
    ax_fs.text(m_pt[0] + 0.03, m_pt[1] - 0.02, r'$M$', fontsize=8.5, fontweight='bold')
    ax_fs.text(k_pt[0] + 0.02, k_pt[1] + 0.03, r'$K$', fontsize=8.5, fontweight='bold')

    fs_handles = [
        Line2D([0], [0], color=PALETTE['Navy'], lw=1.8, label='Band 26'),
        Line2D([0], [0], color=PALETTE['Rust'], lw=1.8, label='Band 27'),
    ]
    ax_fs.legend(handles=fs_handles, loc='lower center', ncol=2, fontsize=8.0)
    ax_fs.set_aspect('equal')
    ax_fs.set_xlim(-0.74, 0.74)
    ax_fs.set_ylim(-0.74, 0.74)
    ax_fs.set_xticks([-0.5, 0.0, 0.5])
    ax_fs.set_yticks([-0.5, 0.0, 0.5])
    ax_fs.set_xlabel(r'$k_x$ ($2\pi/a$)')
    ax_fs.set_ylabel(r'$k_y$ ($2\pi/a$)')
    ax_fs.set_title('2D Fermi surface', pad=8)

    save_figure(fig, 'zrcl2-sc2c-electronic')


def parse_gam_lines(filepath: Path, target_broadening: float = 0.0030) -> np.ndarray:
    text = filepath.read_text()
    blocks = re.split(r'Broadening\s+([\d.]+)', text)[1:]
    for i in range(0, len(blocks), 2):
        bval = float(blocks[i])
        if abs(bval - target_broadening) < 1e-5:
            lines = [l.strip() for l in blocks[i + 1].strip().splitlines() if l.strip()]
            gam = np.zeros((151, 18))
            ptr = 0
            for iq in range(151):
                ptr += 1
                vals = []
                while len(vals) < 18 and ptr < len(lines):
                    vals.extend([float(x) for x in lines[ptr].split()])
                    ptr += 1
                gam[iq] = np.maximum(0.0, np.array(vals[:18]) * 1000.0)
            return gam
    raise ValueError(f'Broadening {target_broadening} not found in {filepath}')


def render_zrcl2_sc2c_phonon_epc() -> None:
    apply_atlas_style()
    ph96_dir = ZR_DIR / 'ph96'
    freq_arr = np.loadtxt(ph96_dir / 'zrclscc.freq.gp')
    q_dist = freq_arr[:, 0]
    freqs_thz = freq_arr[:, 1:] * CM1_TO_THZ

    gam_qv = parse_gam_lines(ph96_dir / 'gam.lines', target_broadening=0.0030)
    ry_to_thz = 3289.84196
    nef_003 = 30.772452
    w_ry = np.maximum(freqs_thz, 0.25) / ry_to_thz
    g_ry = (gam_qv / 1000.0) / ry_to_thz
    lam_qv = np.where(freqs_thz > 0.25, g_ry / (np.pi * nef_003 * (w_ry ** 2)), 0.0)

    phdos_arr = np.loadtxt(ph96_dir / 'zrclscc.phdos', comments='#')
    w_dos_thz = phdos_arr[:, 0] * CM1_TO_THZ
    dos_scale = 33.3564095
    phdos_tot = phdos_arr[:, 1] * dos_scale
    phdos_zr = phdos_arr[:, 2] * dos_scale
    phdos_c = phdos_arr[:, 3] * dos_scale
    phdos_cl = (phdos_arr[:, 4] + phdos_arr[:, 5]) * dos_scale
    phdos_sc = (phdos_arr[:, 6] + phdos_arr[:, 7]) * dos_scale

    a2f_lines = (ph96_dir / 'alpha2F.dat').read_text().splitlines()[2:]
    e_a2f, a2f_003, a2f_001 = [], [], []
    for idx in range(0, len(a2f_lines), 2):
        r1 = [float(x) for x in a2f_lines[idx].split()]
        e_a2f.append(r1[0])
        a2f_001.append(max(0.0, r1[1]))
        a2f_003.append(max(0.0, r1[3]))
    e_a2f = np.array(e_a2f)
    a2f_003 = np.array(a2f_003)
    a2f_001 = np.array(a2f_001)

    de = e_a2f[1] - e_a2f[0]
    cum_lam_003 = np.zeros_like(e_a2f)
    cum_lam_003[1:] = np.cumsum(2.0 * a2f_003[1:] / e_a2f[1:] * de)

    fig = plt.figure(figsize=(10.2, 4.45))
    gs = GridSpec(
        1, 3, figure=fig,
        left=0.075, right=0.98, bottom=0.17, top=0.84,
        width_ratios=[1.42, 0.76, 1.02], wspace=0.12
    )
    ax_ph = fig.add_subplot(gs[0, 0])
    ax_pdos = fig.add_subplot(gs[0, 1], sharey=ax_ph)
    ax_a2f = fig.add_subplot(gs[0, 2], sharey=ax_ph)

    for ax in (ax_ph, ax_pdos, ax_a2f):
        style_axis(ax)
        ax.axhline(10.0, color=PALETTE['Coral'], ls='--', lw=1.05, zorder=3)
        ax.axhspan(12.2, 17.3, color=PALETTE['WarmTint'], alpha=0.55, zorder=0)

    q_ticks = [q_dist[0], q_dist[50], q_dist[100], q_dist[150]]
    for x in q_ticks[1:-1]:
        ax_ph.axvline(x, color='#ced8e3', lw=0.85, zorder=1)

    for nu in range(18):
        ax_ph.plot(q_dist, freqs_thz[:, nu], color='#4a5a70', lw=0.9, alpha=0.85, zorder=2)
        g_vals = gam_qv[:, nu]
        l_vals = lam_qv[:, nu]
        idx_sub = np.arange(0, 151, 3)
        sizes = np.clip(l_vals[idx_sub] * 26.0 + g_vals[idx_sub] * 0.14, 4.0, 95.0)
        ax_ph.scatter(
            q_dist[idx_sub],
            freqs_thz[idx_sub, nu],
            s=sizes,
            c=np.clip(g_vals[idx_sub], 0.0, 340.0),
            cmap='YlOrRd',
            vmin=0.0,
            vmax=330.0,
            edgecolors='#2b3a4d',
            linewidths=0.3,
            alpha=0.84,
            zorder=4,
        )

    ax_ph.set_xlim(q_ticks[0], q_ticks[-1])
    ax_ph.set_ylim(0.0, 18.0)
    ax_ph.set_xticks(q_ticks, [r'$\Gamma$', r'$M$', r'$K$', r'$\Gamma$'])
    ax_ph.set_ylabel(r'Frequency $\omega$ (THz)')
    ax_ph.set_title(r'Fat-phonon $\gamma_{\mathbf{q}\nu}$ & $\lambda_{\mathbf{q}\nu}$', pad=8)

    ax_ph.annotate(
        r'C-atom optical modes ($\nu=16\text{–}18$): $\gamma_{\Gamma,17\text{–}18}\approx 322\ \mathrm{GHz}$',
        xy=(q_dist[8], 15.45),
        xytext=(q_dist[10], 11.20),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.95),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Rust'], lw=0.85),
    )
    ax_ph.text(
        q_dist[54], 9.05,
        'Saved input emax = 10 THz',
        fontsize=7.5,
        color=PALETTE['Coral'],
        fontweight='bold',
    )

    ax_pdos.fill_betweenx(w_dos_thz, 0, phdos_tot, color='#dfe6ef', alpha=0.55)
    ax_pdos.plot(phdos_tot, w_dos_thz, color=PALETTE['Ink'], lw=1.0, label='Total')
    ax_pdos.plot(phdos_zr, w_dos_thz, color=PALETTE['Navy'], lw=1.1, label='Zr')
    ax_pdos.plot(phdos_sc, w_dos_thz, color=PALETTE['Teal'], lw=1.1, label='Sc')
    ax_pdos.plot(phdos_cl, w_dos_thz, color=PALETTE['Amber'], lw=1.0, label='Cl')
    ax_pdos.plot(phdos_c, w_dos_thz, color=PALETTE['Rust'], lw=1.2, label='C')

    ax_pdos.set_xlim(0, 3.8)
    ax_pdos.set_xticks([0, 1.5, 3.0])
    ax_pdos.set_xlabel('PHDOS (THz$^{-1}$)')
    ax_pdos.set_title('PHDOS', pad=8)
    ax_pdos.tick_params(labelleft=False)
    ax_pdos.legend(loc='center right', fontsize=7.8)

    ax_a2f.fill_betweenx(e_a2f, 0, a2f_003, color=PALETTE['SoftBlue'], alpha=0.72)
    ax_a2f.plot(a2f_003, e_a2f, color=PALETTE['Navy'], lw=1.35, label=r'$\alpha^2F$ ($\sigma=0.003$)')
    ax_a2f.plot(a2f_001, e_a2f, color=PALETTE['Blue'], lw=0.85, ls=':', alpha=0.85, label=r'$\alpha^2F$ ($\sigma=0.001$)')
    lam_scale = 0.36
    ax_a2f.plot(cum_lam_003 * lam_scale, e_a2f, color=PALETTE['Rust'], lw=1.65, label=r'$0.36\times \lambda(\omega)$')

    ax_a2f.set_xlim(0, 1.05)
    ax_a2f.set_xticks([0.0, 0.4, 0.8])
    ax_a2f.set_xlabel(r'$\alpha^2F(\omega)$ & scaled $\lambda(\omega)$')
    ax_a2f.set_title(r'Saved $\alpha^2F(\omega)$ (emax = 10 THz)', pad=8)
    ax_a2f.tick_params(labelleft=False)

    ax_a2f.text(
        0.22, 13.3,
        'Input: 10 0.12 1\n18-THz output provenance open',
        fontsize=7.8,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
    )
    ax_a2f.legend(loc='center right', bbox_to_anchor=(1.0, 0.36), fontsize=7.6)

    save_figure(fig, 'zrcl2-sc2c-phonon-epc')


def load_zrcl2_lambda_series(tag: str, suffix: str = '') -> dict[str, np.ndarray]:
    base = ZR_DIR / tag
    dat_file = base / (f'lambda{suffix}.dat')
    out_file = base / (f'lambdax{suffix}.out')
    arr = np.loadtxt(dat_file, comments='#')
    lines = out_file.read_text().splitlines()
    tc_idx = [i for i, l in enumerate(lines) if 'omega_log' in l and 'T_c' in l][0] + 1
    tc_vals = [float(lines[tc_idx + i].split()[2]) for i in range(arr.shape[0])]
    return {
        'sigma': arr[:, 0],
        'lambda': arr[:, 1],
        'int_a2f': arr[:, 2],
        'wlog': arr[:, 3],
        'nef': arr[:, 4],
        'tc': np.array(tc_vals),
    }


def render_zrcl2_sc2c_k64_k96_tc() -> None:
    apply_atlas_style()
    p64_10 = load_zrcl2_lambda_series('ph64', '')
    p96_10 = load_zrcl2_lambda_series('ph96', '')
    p64_18 = load_zrcl2_lambda_series('ph64', '.emax18')
    p96_18 = load_zrcl2_lambda_series('ph96', '.emax18')
    sigma = p64_10['sigma']
    write_report(ZR_DIR)
    roots10 = piecewise_linear_crossings(sigma, p64_10['tc'], p96_10['tc'])
    roots18 = piecewise_linear_crossings(sigma, p64_18['tc'], p96_18['tc'])

    fig, (ax_tc, ax_diff) = plt.subplots(1, 2, figsize=(10.0, 4.35))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.18, top=0.85, wspace=0.28)
    style_axis(ax_tc)
    style_axis(ax_diff)

    for ax in (ax_tc, ax_diff):
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.72, zorder=0)
        ax.set_xticks([0.005, 0.010, 0.015, 0.020])

    ax_tc.plot(sigma, p64_18['tc'], color=PALETTE['Navy'], marker='o', ms=3.8, lw=1.6, label=r'$64^2$ stored 18-THz table (source open)')
    ax_tc.plot(sigma, p96_18['tc'], color=PALETTE['Rust'], marker='s', ms=3.6, lw=1.6, label=r'$96^2$ stored 18-THz table (source open)')
    ax_tc.plot(sigma, p64_10['tc'], color=PALETTE['Navy'], ls='--', lw=1.05, alpha=0.7, label=r'$64^2$ matched 10-THz input')
    ax_tc.plot(sigma, p96_10['tc'], color=PALETTE['Rust'], ls='--', lw=1.05, alpha=0.7, label=r'$96^2$ matched 10-THz input')

    for i, root in enumerate(roots10):
        ax_tc.scatter([root['sigma_ry']], [root['tc_k']], marker='^', s=42, color=PALETTE['Amber'], zorder=6, label='10-THz table roots' if i == 0 else None)
    for i, root in enumerate(roots18):
        ax_tc.scatter([root['sigma_ry']], [root['tc_k']], s=58, facecolors='none', edgecolors=PALETTE['Teal'], linewidths=1.8, zorder=7, label='18-THz stored-table root (source open)' if i == 0 else None)
    if roots18:
        root = roots18[0]
        ax_tc.annotate(
            f"Stored 18-THz table\n$\\sigma={root['sigma_ry']:.6f}$ Ry, $T_c={root['tc_k']:.3f}$ K\ninput/run record unlinked",
            xy=(root['sigma_ry'], root['tc_k']),
            xytext=(0.0062, 11.6),
            fontsize=7.7,
            bbox=dict(boxstyle='round,pad=0.22', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.94),
            arrowprops=dict(arrowstyle='->', color=PALETTE['Teal'], lw=0.95),
        )

    ax_tc.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_tc.set_ylabel(r'Stored Allen–Dynes $T_c(\sigma)$ (K)')
    ax_tc.set_title(r'Stored $T_c$ tables and interpolated roots', pad=8)
    ax_tc.legend(loc='upper right', fontsize=7.4)

    dtc_18 = p64_18['tc'] - p96_18['tc']
    dtc_10 = p64_10['tc'] - p96_10['tc']
    ax_diff.axhline(0.0, color=PALETTE['Ink'], ls='-', lw=0.95, zorder=2)
    ax_diff.plot(sigma, dtc_18, color=PALETTE['Teal'], marker='o', ms=3.8, lw=1.6, label=r'$\Delta T_c$ (18-THz stored tables)')
    ax_diff.plot(sigma, dtc_10, color=PALETTE['Amber'], marker='^', ms=3.6, lw=1.35, ls='--', label=r'$\Delta T_c$ (matched 10-THz inputs)')
    for root in roots10:
        ax_diff.scatter([root['sigma_ry']], [0.0], marker='^', color=PALETTE['Amber'], s=42, zorder=6)
    for root in roots18:
        ax_diff.scatter([root['sigma_ry']], [0.0], color=PALETTE['Teal'], s=48, zorder=7)
    ax_diff.text(
        0.035, 0.055,
        'Prepared ph64.1/ph96.1\nrefinement has no complete Tc pair',
        transform=ax_diff.transAxes,
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
    )

    ax_diff.set_xlabel(r'Electronic broadening $\sigma$ (Ry)')
    ax_diff.set_ylabel(r'$\Delta T_c(\sigma) = T_{c,64} - T_{c,96}$ (K)')
    ax_diff.set_title(r'Linear-interpolation roots of $\Delta T_c=0$', pad=8)
    ax_diff.set_ylim(-0.135, 0.155)
    ax_diff.legend(loc='upper right', fontsize=7.4)

    save_figure(fig, 'zrcl2-sc2c-k64-k96-tc')


def render_zrcl2_sc2c_k64_k96_moments() -> None:
    apply_atlas_style()
    p64 = load_zrcl2_lambda_series('ph64', '')
    p96 = load_zrcl2_lambda_series('ph96', '')
    sigma = p64['sigma']

    fig, (ax_nef, ax_lam, ax_wlog) = plt.subplots(1, 3, figsize=(10.4, 4.15))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.18, top=0.85, wspace=0.31)
    for ax in (ax_nef, ax_lam, ax_wlog):
        style_axis(ax)
        ax.axvspan(0.001, 0.0045, color=PALETTE['WarmTint'], alpha=0.65, zorder=0)
        ax.set_xticks([0.005, 0.012, 0.020])

    ax_nef.plot(sigma, p64['nef'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64\times 64\times 1$')
    ax_nef.plot(sigma, p96['nef'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96\times 96\times 1$')
    ax_nef.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_nef.set_ylabel(r'$N_\sigma(E_F)$ (states/spin/Ry)')
    ax_nef.set_title(r'$N_\sigma(E_F)$ from stored tables', pad=8)
    ax_nef.legend(loc='upper right', fontsize=7.6)
    ax_nef.annotate(
        'Close for $\\sigma\\geq0.004$ Ry\n(two grids; no convergence proof)',
        xy=(0.004, p64['nef'][3]),
        xytext=(0.0075, 28.5),
        fontsize=7.5,
        bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#d7dfeb', alpha=0.92),
        arrowprops=dict(arrowstyle='->', color=PALETTE['Navy'], lw=0.85),
    )

    ax_lam.plot(sigma, p64['lambda'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ direct $\lambda$')
    ax_lam.plot(sigma, p96['lambda'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ direct $\lambda$')
    ax_lam.plot(sigma, p64['int_a2f'], color=PALETTE['Navy'], ls='--', lw=1.1, alpha=0.75, label=r'$64^2$ $\int\alpha^2F$ (10 THz)')
    ax_lam.plot(sigma, p96['int_a2f'], color=PALETTE['Rust'], ls='--', lw=1.1, alpha=0.75, label=r'$96^2$ $\int\alpha^2F$ (10 THz)')
    ax_lam.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_lam.set_ylabel(r'Coupling $\lambda(\sigma)$')
    ax_lam.set_title(r'10-THz input: $\lambda$ and $\int\alpha^2F$', pad=8)
    ax_lam.legend(loc='upper right', fontsize=7.2)

    ax_wlog.plot(sigma, p64['wlog'], color=PALETTE['Navy'], marker='o', ms=3.5, lw=1.5, label=r'$64^2$ (10-THz input)')
    ax_wlog.plot(sigma, p96['wlog'], color=PALETTE['Rust'], marker='s', ms=3.3, lw=1.5, label=r'$96^2$ (10-THz input)')
    ax_wlog.set_xlabel(r'Broadening $\sigma$ (Ry)')
    ax_wlog.set_ylabel(r'$\omega_{\log}(\sigma)$ (K)')
    ax_wlog.set_title(r'Stored $\omega_{\log}$ (10-THz input)', pad=8)
    ax_wlog.legend(loc='upper left', fontsize=7.2)
    ax_wlog.text(
        0.04, 0.04,
        'Frequency grid ends at 10 THz',
        transform=ax_wlog.transAxes,
        fontsize=7.3,
        color=PALETTE['Muted'],
    )

    save_figure(fig, 'zrcl2-sc2c-k64-k96-moments')


if __name__ == '__main__':
    render_zrcl2_sc2c_electronic()
    render_zrcl2_sc2c_phonon_epc()
    render_zrcl2_sc2c_k64_k96_tc()
    render_zrcl2_sc2c_k64_k96_moments()
```

</details>

## 文献中的 Eliashberg 谱函数与累计耦合图例（附 DOI 溯源）

在展示 `α²F(ω)` 与累计 `λ(ω)` 时，文献常通过**标出主峰对应的实空间声子振动模式**或**与声子色散及 PHDOS 共用频率纵轴**，将谱峰归因到具体的原子振动。下面结合两幅文献原图说明其构图方式：

### 1. α²F(ω) / 累计 λ(ω) 双轴叠绘与主峰声子振动本征矢对照

<figure class="research-figure"><img src="/Atlas/figures/literature/M6_Eliashberg_a2F_Modes_MoW_Bekaert2020_Fig4.jpg" alt="四种二维过渡金属碳氮化物的 Eliashberg 谱函数 α²F(ω)、累计 λ(ω) 及底部对应的三维声子振动模式示意图" loading="lazy"/><figcaption>子面板 (a)–(d) 分别展示 Mo<sub>2</sub>C、Mo<sub>2</sub>N、W<sub>2</sub>C 与应变 W<sub>2</sub>N 的 Eliashberg 谱函数 α<sup>2</sup>F(ω)（蓝色曲线，左轴）与累计耦合函数 λ(ω)（红色曲线，右轴），并在特征峰处标注罗马数字 I、II、III；底部子面板 (e) 集中展示峰 I、II、III 对应的三维晶体结构与实空间原子振动位移箭头。图片来源：Bekaert et al., <em>Nanoscale</em> <strong>12</strong>, 17354 (2020)，<a href="https://doi.org/10.1039/D0NR03875J" target="_blank" rel="noopener noreferrer">DOI: 10.1039/D0NR03875J</a>。</figcaption></figure>

- **数据组织要点**：由于被积函数含有 `2 α²F(ω) / ω` 权重，子图 (a)–(d) 中特征峰 `I`（低频过渡金属声学/光学模）对右轴红色累计曲线 `λ(ω)` 的台阶拉升显著大于高频区的特征峰 `III`（轻元素 C/N 光学模）。在底部子图 (e) 中列出 `I、II、III` 对应的三维原子位移方向，能够清楚交代每个 `λ(ω)` 台阶的微观振动起源。

### 2. 声子色散、模式耦合强度、分波 PHDOS 与 α²F(ω)/λ(ω) 共享频率纵轴五面板图

<figure class="research-figure"><img src="/Atlas/figures/literature/M6_5Panel_FatPhonon_PHDOS_a2F_BZ_hAlH2_Jiang_Fig3.jpg" alt="二维金属氢化物 h-AlH₂ 的声子色散、模式耦合 λ_qν、原子投影 PHDOS、Eliashberg 谱函数 α²F(ω) 与二维布里渊区耦合分布图" loading="lazy"/><figcaption>将频率 ω 统一设为纵轴，从左至右依次排列 (a) 振动方向与原子投影声子色散、(b) 模式电声耦合强度 λ<sub>qν</sub>、(c) Al/H 元素分辨 PHDOS、(d) α<sup>2</sup>F(ω) 与累计 λ(ω)，并在右上角附 (e) 二维布里渊区中的 λ(q) 热力分布。图片来源：Jiang et al., <em>Phys. Status Solidi RRL</em> <strong>18</strong>, 2300417 (2024)，<a href="https://doi.org/10.1002/pssr.202300417" target="_blank" rel="noopener noreferrer">DOI: 10.1002/pssr.202300417</a>。</figcaption></figure>

- **数据组织要点**：当体系同时含有重金属与轻元素（如 H、C、N）时，把频率轴竖置并将色散、模式 `λ_qν`、元素 PHDOS 与 `α²F(ω)` 水平并排，可以直观对比重原子低频支与轻原子高频支各自贡献的 `Δλ` 台阶。

## 把完整谱函数交给 Tc 求解

走到这里得到的是 α²F。若需要快速比较同一组数据的 μ* 敏感性，可以进入 [Allen–Dynes / McMillan 估算](/Atlas/m/allen-dynes/qe/)；若需要实际求解能隙方程，则进入 [EPW / Eliashberg Tc](/Atlas/m/epw-eliashberg/qe/)。后一页使用原始频率列和谱函数列，核对单位转换后的积分，再把整条曲线交给 EPW。只保留 λ 和 ωlog 两个数，已经不足以重建方程需要的频率依赖。

EPW 的各向同性入口可以读取已有谱函数；各向异性求解还需要保留带、k 点和散射之间的分辨信息。因此，本页由 QE 双网格产生的谱可以接各向同性方程，但不能仅凭这个平均谱恢复各向异性能隙。具体文件要求见 [EPW 的 eliashberg 输入说明](https://docs.epw-code.org/Inputs/Inputs.html#eliashberg)。

```text
pwxall / dense-k → pwx / response-k → 完整逐 q EPC
                                      ↓
                       q2r + matdyn 或 lambda.x
                                      ↓
                             同一展宽的 α²F
                        ┌─────────────┴─────────────┐
                        ↓                           ↓
                   λ、ωlog、频率矩               完整频率与谱列
                        ↓                           ↓
                 Allen–Dynes Tc 估算       EPW 各向同性 Eliashberg 方程
```

下一步：[Tc 公式估算](/Atlas/m/allen-dynes/qe/) · [EPW 方程求解](/Atlas/m/epw-eliashberg/qe/)；需要定位单 q、单模贡献时，转到 [声子线宽](/Atlas/m/phonon-linewidth/qe/)。

```text
同结构致密 SCF + 响应 SCF → 完整 q 网格 EPC → 逐 q、逐模 λ/γ
                                             ├─ q2r → matdyn → a2F.dos*（Ry）
                                             └─ lambda.x → alpha2F.dat（THz）→ λ / ω_log
```
