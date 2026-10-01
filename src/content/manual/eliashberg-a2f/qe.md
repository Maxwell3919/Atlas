[EPC与双网格输入](/Atlas/m/epc/qe/) · [声子态密度](/Atlas/m/phdos/qe/) · [QE谱函数定义](https://www.quantum-espresso.org/Doc/ph_user_guide/node19.html)

## 把各个模式的耦合放到频率轴上

声子态密度F(ω)告诉我们哪些频率有多少振动态。α²F(ω)进一步按费米面电子与这些振动的耦合加权，因此PHDOS高峰不一定对应α²F高峰，同一总λ也可能来自不同振动频段。识别异质结或应变的配对变化，需要同时看色散上的q与模式、元素/方向投影、α²F谱峰和累计λ，而不是从一个总数直接推断机制。

[Ba₂N研究](https://doi.org/10.1103/PhysRevB.105.165101)的图3(b,c)正是这种比较：低频主要是Ba振动，高频N峰也在耦合谱中可见。图6(b,c)保持同样轴和投影，比较4%应变下的谱重分布。它们展示的是文献材料；下面的数值来自真实Al双网格链。Al用于认清文件、单位和积分，多原子模式的分析再接到后面的异质结记录。

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


<span id="h-输入之后-程序实际留下了什么"></span>

## 逐 q 求和谱与实空间插值谱分开保存

q2r/matdyn产生a2F.dos*，其第一列为Ry；lambda.x直接按逐q电声文件和星权重形成alpha2F.dat，其第一列为THz。本例主谱采用后者。matdyn的asr处理力常数，并不会把低频修正自动写回lambda.x读取的原始elph文件。

lambda.x输入将8个不可约q、各自的星权重及文件顺序放在一起：

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

第一行14.0、0.12、0分别为14 THz频率上限、0.12 THz谱频率高斯宽度和普通Gaussian。八个星权重1、8、4、6、24、12、3、6合计64，程序归一化后求和。末行0.10为Tc公式的μ*，不参与生成α²F。最高直接模式9.936574 THz落在谱窗内，谱窗还要容纳展宽尾部。

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

lambda.dat第二列是逐q加权λqsum，第三列是内部展宽谱积分λspec，第四列ωlog已经是K；最后的DOS保留states/spin/Ry/cell。0.020 Ry一行的两种λ为0.374486和0.374547。这两列对应同一父链的不同离散汇总。复现QE原生Tc时遵循它的定义：指数使用λqsum，ωlog按内部λspec归一化；另做同一谱的完整Allen–Dynes对照时，λspec、ωlog与二阶矩都从该谱提取，结果单列。不要跨分支、σ或matdyn/lambda路线挑选输入；[三种公式代入对照](/Atlas/m/allen-dynes/qe/#same-spectrum-formulas)保留了这一区别。

普通频率ν的温度尺度用hν/kB，角频率ω用ħω/kB，两者一致。QE7.5使用47.9924 K/THz；已经打印成K的ωlog不要再次换算。

## α²F的峰怎样进入累计 λ

```console
maxwell@maxwell:~/al/epc-q4$ head -5 alpha2F.dat
# E(THz)     0.005     0.010     0.015     0.020     0.025     0.030     0.035     0.040     0.045     0.050
  0.0000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0070   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0140   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
  0.0210   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000   0.00000
```

表头后十列对应σ=0.005–0.050 Ry的电子双δ积分展宽，0.020 Ry位于整个数值表第5列。它们是十种电子积分设置，频率轴都相同。先选定同一σ，再计算：

**λ(Ω)=2∫₀^Ω α²F(ν)/ν dν**

累计曲线在谱峰所在频段抬升，到最高频率后趋于总λ。某频段[a,b]的贡献为λ(b)−λ(a)，所以按同一频率范围比较两个体系的Δλ，比单看峰高更直接。1/ν使低频谱权重对λ更敏感；尖但很窄的高频峰不一定贡献最大的台阶。区间边界应来自实际模式和PHDOS归属，不能任意按元素质量替所有模式分类。

![Al实际α²F与累计λ](/Atlas/examples/al/figures/eliashberg-a2f.png)

这张图来自Al32³/16³/q4³原件。读峰位时先对照[逐模频率与线宽](/Atlas/m/phonon-linewidth/qe/)，再由累计曲线判断该频段占总λ的多少。PHDOS仅作振动成分参照，不能替代电子配对权重。

## 从同一谱得到 ωlog 和二阶矩

**νlog=exp{(2/λspec)∫[α²F(ν)/ν]ln(ν)dν}**

**ν̄₂={(2/λspec)∫α²F(ν)νdν}¹ᐟ²**

λspec、νlog和ν̄₂都由同一非负谱积分。对数可理解为ln[ν/(1 THz)]，最后恢复THz；ωlog是νlog换成K后的表示。低频权重增加通常同时提高λ、拉低对数频率尺度，这两种变化进入Tc公式后会竞争。二阶矩还保留对高频权重的敏感性，用于完整Allen–Dynes的谱形修正。

原表零频点为(0,0)，不在这里直接除零或取对数。程序保留正频原值，分别重建内部谱和积分已打印谱，检查五位小数带来的舍入。实质性虚频先回到[声子稳定性](/Atlas/m/imaginary-phonon/qe/)解释，不能取绝对值生成配对谱。

<span id="spectral-reproduction"></span>

## 用真实文件复算这些积分

数据格式是lambda.in的q与权重、elph文件的模式/σ块、alpha2F.dat的2000行频率谱和lambda.out的两种λ。处理顺序为核对身份与列号、逐q加权求和、重建版本对应的谱、逐频率累计梯形积分、求频率矩，最后对照原生打印精度。单位和谱窗始终随输出保存。

> 读取同一分支的lambda.in/out、alpha2F.dat及所有elph.inp_lambda文件。验证q坐标、权重和σ列；逐σ计算累计λ、最终λspec、ωlog和ν̄₂，将ν单位由THz按QE7.5常数换成K。保留内部谱算法与打印谱积分的差别、低频规则和负谱状态，输出逐频率CSV、谱矩CSV、检查JSON及完整Python源码。只读取存档，不补生成新的响应或谱。

[完整verify_tc_chain.py](/Atlas/examples/al/tc-route/scripts/verify_tc_chain.py)用于这一复算，标准库即可运行；[analyse_epc.py](/Atlas/examples/al/epc-q4/analyse_epc.py)还提供逐模表。解包[Al完整包](/Atlas/examples/al-lesson-files.tar.gz)，进入al/tc-route：

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

在0.020 Ry列，打印谱积分λspec=0.37454456、ωlog=343.74087 K、ν̄₂对应363.33106 K；它们在同一归一化下形成一组谱矩。原生Tc和脚本完整公式温度分列保存，具体代入见[Allen–Dynes](/Atlas/m/allen-dynes/qe/)。

matdyn在32³链的0.005、0.010 Ry谱分别有146和9行负值，48³链的前三档为145、88和5行。原件保留符号；这些插值谱需要排查实空间变换与网格，不能裁零后当成接受谱。用于本段频率矩的lambda.x谱非负，其来源独立。

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

下载[谱与累计积分CSV](/Atlas/examples/al/tc-route/data/spectra-and-integrals.csv)、[谱矩与公式表](/Atlas/examples/al/tc-route/data/tc-formula-scan.csv)、[单位及检查记录](/Atlas/examples/al/tc-route/data/tc-chain-checks.json)。两条致密网格的逐频谱差见[Tc页](/Atlas/m/allen-dynes/qe/#spectral-grid-comparison)。

<span id="spectral-window"></span>

## 异质结高频模式与谱积分上限

在单质金属 Al 中，3 条声子支连续分布在 `0–9.94 THz`，`lambda.in` 设 `emax = 14 THz` 即可覆盖全谱。而在同时包含较重元素（Zr、Sc、Cl）与轻元素（C 或 N）的层状异质结中，声子谱可能分为间隔较大的频段，具体范围需要从力常数和模式频率中确认，高频轻原子光学支容易超出 `emax = 10 THz` 的积分上限。

在 **`ZrCl₂/Sc₂C`**（[完整双网格计算记录](/Atlas/m/epc/qe/#zrcl2-sc2c-k64-k96-record)）中：
- 15 条声学与中低频光学支分布在 `0–10.11 THz`（直接 DFPT 网格为 `0–10.02 THz`）；
- 逐原子PHDOS中C投影占优的高频段包含3条光学支（ν=16–18）跨越 10.11–12.49 THz 的声子带隙，分布在 12.49–17.11 THz（原始 DFPT 网格为 12.38–17.11 THz；σ=0.003 Ry 下，Γ 点第16支高频光学模与第17、18支高频简并组的线宽在 ph64 中为 260.01–318.58 GHz，在 ph96 中为 297.74–322.13 GHz）。


匹配的 10 THz 输入首行是 10 0.12 1（Methfessel–Paxton）。在 σ=0.003 Ry 下，直接 q 加权 λ 为 ph64=2.459034、ph96=2.451080；谱积分分别为 2.427435 和 2.418456。QE 7.1 lambda.f90 限定 α²F 频率网格与 ωlog 的计算范围，高于 emax 的模式仍可能通过展宽尾部贡献较低频率。18 THz 保存表在 σ=0.003 Ry 的积分值为 ph64=2.458955、ph96=2.451001；全表直接 λ 与积分的最大绝对差为 0.000102。可是 18 THz 表尚未与生成输入、运行命令或 QE 可执行文件绑定，ph64.1/ph96.1 的 18 0.12 1 输入只是候选文件，不能证明输出来源，也不能将变化归因于只提高 emax。参见 <a href="https://raw.githubusercontent.com/QEF/q-e/qe-7.1/PHonon/PH/lambda.f90">QE 7.1 lambda.f90 源码</a>。

对照同链的[原始PHDOS](/Atlas/examples/zrcl2-sc2c/ph64/zrclscc.phdos)、[Γ逐模EPC文件](/Atlas/examples/zrcl2-sc2c/ph64/elph_dir/elph.inp_lambda.1)和[模式γ/λ表](/Atlas/m/phonon-linewidth/qe/#heterostructure-modes)，高频模式的线宽和λ非零，而匹配输入的alpha2F.dat只写到10 THz。旧附件没有该链模式向量，因此这里不按频率简并指定C的面内/面外方向。

<details>
<summary>旧三联图下载与编码说明</summary>

[下载原三联图PNG](/Atlas/figures/zrcl2-sc2c/zrcl2-sc2c-phonon-epc.png)。它使用0–18 THz共享纵轴，右侧是匹配10 THz输入的保存谱；左侧散点面积按clip(26λ+0.14γ,4,95)混合两量，颜色为γ，右侧累计λ乘0.36共用横轴。点面积不能定量读成单独λ或γ，缩放线也不能按另一坐标直接读取；独立量值使用原始文件和上面的模式表。18 THz保存表生成来源仍未闭合。

</details>

保存文件（18 THz 输出来源待核）：[ph96 alpha2F.emax18.dat](/Atlas/examples/zrcl2-sc2c/ph96/alpha2F.emax18.dat) · [ph96 lambdax.emax18.out](/Atlas/examples/zrcl2-sc2c/ph96/lambdax.emax18.out) · [zrclscc.phdos](/Atlas/examples/zrcl2-sc2c/ph64/zrclscc.phdos) · [绘图脚本 plot_zrcl2_sc2c.py](/Atlas/examples/zrcl2-sc2c/plot_zrcl2_sc2c.py)。


从频率与PHDOS确认12.49–17.11 THz高频段，再对照匹配输入的保存谱止于10 THz：没有显示这一段并不意味着它不耦合。原生高频模式的γ、λ确实非零，见[线宽页](/Atlas/m/phonon-linewidth/qe/#heterostructure-modes)。原始10 THz记录与来源未闭合的18 THz保存表分别保留，当前不能把后者作为已验证的完整材料谱。

## Ba₂N的应变比较怎样读

Ba₂N图3和图6保持色散、PHDOS和α²F的对应关系。未应变Γ附近约55 cm⁻¹的Ba面内反向光学模，在4%拉伸后移至约49 cm⁻¹；K声学模软化后，在图6(c)出现约24 cm⁻¹峰。72、92、105 cm⁻¹附近的谱变化还要与Ba/N投影混合及对应模式一起解释。低频峰对累计λ的影响由1/ν积分权重决定，不能只按α²F最高峰归因。

原文图3(c)只画α²F；图6(c)同时画蓝色α²F和红色累计λ(ω)，红线读右侧坐标轴。累计曲线在低频峰附近陡升，随后趋向总λ=1.49；应把红线的台阶、蓝线的频段和图6(a,b)中的模式对应起来，而不是从峰高直接判断贡献。用于自己的界面，应保持单层与异质结的应变、结构参考和数值协议一致，才比较频段贡献。

由完整谱进入[经验Tc公式](/Atlas/m/allen-dynes/qe/)时使用谱矩；进入[等方Eliashberg求解](/Atlas/m/epw-eliashberg/qe/)时保留整条谱。材料各向异性还要保留(n,k)与散射矩阵信息，平均α²F无法恢复费米面能隙分布。
