[Nelson–Kosterlitz 的普适跃变](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.39.1201) · [经典二维 XY 模型的有限尺寸研究](https://arxiv.org/abs/cond-mat/0502556) · [NumPy 随机数生成器](https://numpy.org/doc/stable/reference/random/generator.html)

把一个小箭头放在每个格点上，相邻箭头越平行，能量越低。升高温度后，局部方向会波动；绕某个小方格走一圈，方向还可能完整转过一周。这一页实际运行这样的二维 XY 模型，看自旋构型、涡旋和相位刚度怎样随温度与尺寸变化。

这是使用 Python 与 NumPy 运行的方格经典 XY 模型。以 J 作为能量单位、J/kB 作为温度单位；程序令 J=kB=1，因此输入 0.92 表示 kB·T/J=0.92。下文和原始输出中的 T/J 是这一约定下的简写，不能直接标为 K。一次 Monte Carlo sweep 是抽样操作，不是飞秒、皮秒或真实自旋动力学时间。

[下载完整算例](/Atlas/examples/xy-bkt-files.tar.gz)后，可以查看全部随机种子、热化记录、抽样序列和末态构型。[mc.py](/Atlas/examples/xy-bkt/mc.py) 是完整计算输入，[analyse.py](/Atlas/examples/xy-bkt/analyse.py) 提取相位刚度与误差，[verify.py](/Atlas/examples/xy-bkt/verify.py) 核对保存数据，[plot.py](/Atlas/examples/xy-bkt/plot.py)（同时下载同目录的 [atlas_plot_style.py](/Atlas/examples/xy-bkt/atlas_plot_style.py)） 重新作图。

<details>
<summary>plot.py 的完整源码</summary>

```python
"""Read actual Monte Carlo CSVs and render figures; no generated fit data."""

from atlas_plot_style import install as install_atlas_style
install_atlas_style()
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;O=R/'figures';O.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
rows=list(csv.DictReader((R/'results/helicity.csv').open()))
fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
for n,color in [(8,'#326ca8'),(16,'#bf6635'),(24,'#39816d')]:
    selected=[r for r in rows if int(r['L'])==n]
    temp=np.array([float(r['temperature_J']) for r in selected])
    axs[0].errorbar(temp,[float(r['Y_J']) for r in selected],yerr=[float(r['display_error_J']) for r in selected],fmt='o-',capsize=3,color=color,label=f'L={n}, two seeds')
    axs[1].plot(temp,[float(r['vortex_abs_density']) for r in selected],'o-',color=color,label=f'L={n}')
t=np.linspace(.68,1.12,100);axs[0].plot(t,2*t/np.pi,'--',color='.25',label='2T / pi reference')
axs[0].set(xlabel='T / J  (kB=1)',ylabel='Helicity modulus Y / J',title='Finite square lattices; no TBKT extrapolation')
axs[1].set(xlabel='T / J',ylabel='Mean absolute plaquette vorticity',title='Defect density, not an unbinding test')
for ax in axs:ax.legend(fontsize=8)
fig.savefig(O/'xy-helicity.png',dpi=200);fig.savefig(O/'xy-helicity.pdf');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,5),layout='constrained')
for ax,temp in zip(axs,[.70,1.10]):
    run=sorted((R/'base').glob(f'L24-T{temp:.2f}-s*'))[0]
    angle=np.loadtxt(run/'final-angles.csv',delimiter=',');vort=np.loadtxt(run/'final-vortices.csv',delimiter=',')
    n=angle.shape[0];x,y=np.indices(angle.shape)
    ax.quiver(x,y,np.cos(angle),np.sin(angle),angle,cmap='twilight',clim=(-np.pi,np.pi),pivot='mid',scale=32,width=.0025)
    for charge,color,marker in [(1,'#d02525','o'),(-1,'#18449e','s')]:
        px,py=np.where(vort==charge)
        ax.scatter((px+.5)%n,(py+.5)%n,s=45,facecolors='none',edgecolors=color,marker=marker,label=f'vorticity {charge:+d}')
    meta=json.loads((run/'run.json').read_text())
    ax.set(xlim=(-.7,n+.2),ylim=(-.7,n+.2),aspect='equal',xlabel='lattice x',ylabel='lattice y',title=f'L=24, T/J={temp:.2f}, seed={meta["seed"]}')
    ax.legend(fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.13),ncol=2)
fig.suptitle('Actual final Monte Carlo configurations; periodic square lattice',fontsize=12)
fig.savefig(O/'xy-configurations.png',dpi=200);fig.savefig(O/'xy-configurations.pdf');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
cases=[r for r in csv.DictReader((R/'results/extension-comparison.csv').open()) if int(r['L'])==24]
for i,r in enumerate(cases):
    label=f'T={r["temperature_J"]}, {r["initialization"]}'
    axs[0].errorbar([20000,40000],[float(r['Y_base_J']),float(r['Y_extended_J'])],yerr=[float(r['base_error_J']),float(r['extended_error_J'])],fmt='o-',capsize=3,label=label)
for d in sorted((R/'extended').glob('L24-T0.92-*')):
    a=np.loadtxt(d/'series.csv',delimiter=',',skiprows=1);meta=json.loads((d/'run.json').read_text())
    means=a.reshape(80,100,10).mean(axis=1)
    axs[1].plot(means[:,0],means[:,1],label=meta['initialization'])
axs[0].set(xlabel='Production sweeps',ylabel='Helicity modulus Y / J',title='Nested continuation of the same chains')
axs[1].set(xlabel='Production sweep',ylabel='Block-mean energy / (N J)',title='L=24, T/J=0.92; blocks of 500 sweeps')
axs[0].set_xticks([20000,40000])
axs[1].set_xticks([0,10000,20000,30000,40000])
for ax in axs:ax.legend(fontsize=7)
fig.savefig(O/'xy-sampling.png',dpi=200);fig.savefig(O/'xy-sampling.pdf');plt.close(fig)
print('Saved xy-helicity, xy-configurations, xy-sampling as PNG and PDF')
```

</details>

## 模型、周期边界和一次更新

方格有 L×L 个格点，两个方向都周期连接。每个格点保存一个角 θ，哈密顿量为

```text
H/J = −Σ cos(θ[i+1,j] − θ[i,j]) − Σ cos(θ[i,j+1] − θ[i,j])
```

两个求和都遍历全格点，下标按 L 取模。每条最近邻键只计一次；所有角都相同时，H/(NJ)=−2，其中 N=L²。这给程序提供了一个容易核对的零温构型。

本次取 L=8、16、24。温度依次为 0.70、0.80、0.88、0.92、1.00、1.10；每种尺寸和温度有两个独立种子，一个从全同向角开始，另一个从 [−π,π) 的随机角开始，共 36 条基础轨迹。改变初态，是为了检查短热化是否仍留下可见影响。

更新采用固定幅度的 Metropolis 提议：给某个角加一个均匀分布在 [−π/2,π/2] 的扰动，计算它与四个邻居之间的能量变化 ΔH，再以 `min(1, exp(−ΔH/T))` 的概率接受。没有在正式采样中继续调整提议幅度。

程序把格点分为棋盘上的黑白两组。同一组中没有最近邻键，可以同时更新；先更新一组，再更新另一组，构成一次 sweep，每个自旋被尝试一次。本例的 L 都是偶数，因此跨周期边界后仍保持这项分组性质。不能原样把这个更新方式用到奇数边长的周期方格。

## 先计时，再提交这一批短轨迹

这次在 Talos 的独立普通目录运行，NumPy 版本为 2.4.6。两个工作进程分别做不同参数的轨迹，每个进程限定一个线程。

```console
talos@talos-MS-7D54:~/xy-bkt$ export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
talos@talos-MS-7D54:~/xy-bkt$ python3 -B mc.py --benchmark > benchmark.out 2> benchmark.err; echo "exit=$?"
exit=0
talos@talos-MS-7D54:~/xy-bkt$ cat benchmark.out
SELF_CHECK {"ordered_energy_per_spin": -2.0, "random_local_delta_energy_max_error": 1.5543122344752192e-15, "periodic_net_vorticity": 0, "numpy": "2.4.6"}
BENCHMARK L24 1000 sweeps = 0.176617 s; 36 base + 8 extension cases at 2 workers estimated < 93.6 s plus I/O
```

第一行先核对全同向构型的能量，又对随机构型做了 25 次单自旋变化，将局部公式的 ΔH 与整个体系重新求和的能量差对照，最大差为 1.55×10⁻¹⁵。它检查更新公式，不代表热化或采样已经充分。

正式基础批次的命令是：

```console
talos@talos-MS-7D54:~/xy-bkt$ python3 -B mc.py --base > base.out 2> base.err; echo "exit=$?"
exit=0
talos@talos-MS-7D54:~/xy-bkt$ tail -4 base.out
FINISHED base/L24-T1.00-s2026094609 samples=4000 acceptance=0.5436 wall=5.27s
FINISHED base/L24-T1.10-s2026094610 samples=4000 acceptance=0.5832 wall=5.35s
FINISHED base/L24-T1.10-s2026094611 samples=4000 acceptance=0.5836 wall=5.32s
MONTE_CARLO_FINISHED 36 cases wall=75.38s
```

每条轨迹先丢弃 5000 sweep 作为热化段，再进行 20000 sweep 的正式抽样，每隔五次记录一次，因此留下 4000 行。热化序列单独保存在 `warmup.csv`，没有与正式序列混在一起平均。运行中可以用 `tail -f base.out` 看哪些参数已完成，用 `tail -f base.err` 看异常；末尾没有出现的参数仍可能在运行，不能据已有几行就认定全批次结束。

目录名中的 s 后面就是随机种子。以 L=24、T/J=0.92 的全同向起态为例，`run.json` 记录 seed=2026094606、5000 次热化、20000 次正式 sweep、4000 次测量，正式接受率为 0.5171571181。同组随机起态用另一个种子 2026094607，两条轨迹并非把同一段序列复制两次。

## 原始序列里存了什么

```console
talos@talos-MS-7D54:~/xy-bkt$ head -4 base/L24-T0.92-s2026094606/series.csv
sweep,energy_per_spin,M2,cos_x,cos_y,current_x,current_y,current_x2,current_y2,vortex_abs_density
5.000000000000000000e+00,-1.387290803993360022e+00,2.337981439126416983e-01,4.012807560977712455e+02,3.977987470024040704e+02,1.025602657115940275e+01,6.943740528079212382e+00,1.051860810283276919e+02,4.821553252128978073e+01,2.083333333333333218e-02
1.000000000000000000e+01,-1.335394938149527366e+00,2.501137036302885641e-01,3.785037986647218986e+02,3.906836857094058360e+02,5.871106822454554397e+00,5.510315311576374775e+00,3.446989532067241413e+01,3.036357483299304150e+01,1.736111111111111188e-02
1.500000000000000000e+01,-1.426929403562417376e+00,3.185028587959647939e-01,4.126565016448240044e+02,4.092548348071283044e+02,8.377220335896305770e+00,1.037883624951718353e+01,7.017782055615461445e+01,1.077202418942919167e+02,2.083333333333333218e-02
```

`energy_per_spin` 是 H/(NJ)。`M2` 是单位自旋平均矢量的模平方，有限小格子的非零值不能直接当成热力学极限的长程磁序。`cos_x` 与 `cos_y` 是两个方向全部键余弦的和；两者之和取负、除以 N，应该还原该行能量。

`current_x` 与 `current_y` 分别保存相邻角差正弦的总和，后两列是它们各自的平方。这里的 current 是计算扭转响应所需的模型量，不是安培单位的电流。把这些一阶、二阶矩分别存下来，才能重算涨落项，不能先对每一步随意定义一个“瞬时刚度”再忽略相关性。

最后一列是每个小方格涡旋电荷绝对值的平均。沿小方格四条边，把每个角差回卷到 [−π,π)，总和除以 2π并核对整数，得到电荷 q。一个周期方格的全部电荷和应为零；这一点在每次测量中都检查过。

## 刚度要连着误差一起读

在本页 J=1 的约定下，两个方向平均的 helicity modulus 为

```text
Y = { <Cx+Cy> − [Var(Ix)+Var(Iy)]/T } / (2N)
```

这里 Y 的单位是 J，方差保留 `<I²>−<I>²`。有些文章定义的是 Y/T；那种无量纲量对应的参考值是 2/π。本页画的是 Y/J，因此参考线是 2T/π，不能混用这两个约定。

连续测量会相关，4000 行并不等于 4000 个独立样本。本次把每条轨迹分成 16 个连续块，做删一块 jackknife，重新计算整个含方差的 Y；另外保留 8 块和 32 块的误差结果。基础轨迹每块覆盖 1250 sweep，加长后的每块覆盖 2500 sweep。 分块数改变时误差仍有波动：全部轨迹的 8/16 与 32/16 块误差比范围为 0.300–1.384，其中一条 L=8、T/J=0.80 轨迹的 8 块、16 块误差分别为 0.000515、0.001718。因此本页不把这些诊断误差写成已形成稳定平台的误差估计。

能量及电流平方的自相关时间也随原始序列估计。这次诊断值约为 2.89–52.20 sweep，最短的分块仍约为较大自相关估计的 23.9 倍。这是有限序列上的相关性检查，尤其不能证明局部 Metropolis 已充分访问所有绕行扇区。

合并两个种子时，中心值取两条轨迹估计的平均。图中的误差取“轨迹内分块误差合并值”和“两种子结果差的一半”中较大者。这是明确给出构造方法的诊断误差条，不是已校准的置信区间。每条种子的结果也保留在 [cases.csv](/Atlas/examples/xy-bkt/results/cases.csv)，没有只留下合并曲线。

## 将八条轨迹加长到 40000 sweep

L=16、24 在 T/J=0.88、0.92 的两个种子都继续到 40000 正式 sweep，共八条加长轨迹。程序从各自末态角度和 RNG 状态继续，不再重新热化；原 20000 sweep 数据保持在 `base/`，加长记录单独保存在 `extended/`。

```console
talos@talos-MS-7D54:~/xy-bkt$ python3 -B mc.py --extended > extended.out 2> extended.err; echo "exit=$?"
exit=0
talos@talos-MS-7D54:~/xy-bkt$ tail -4 extended.out
FINISHED extended/L24-T0.88-s2026094605 samples=8000 acceptance=0.5046 wall=4.36s
FINISHED extended/L24-T0.92-s2026094606 samples=8000 acceptance=0.5167 wall=4.28s
FINISHED extended/L24-T0.92-s2026094607 samples=8000 acceptance=0.5173 wall=4.42s
MONTE_CARLO_FINISHED 8 cases wall=15.59s
```

加长不保证每个数都静止。例如 L=16、T/J=0.92 的全同向起态，Y 从 0.623675±0.006564 变为 0.613795±0.004536；L=24 同温度的随机起态从 0.612411±0.005743 变为 0.604368±0.008524。这些变化和误差一起保留在 [extension-comparison.csv](/Atlas/examples/xy-bkt/results/extension-comparison.csv)。前后两份估计包含重叠样本，不能把它们当成两次独立实验做显著性检验。

![加长抽样前后的刚度与能量分块记录](/Atlas/examples/xy-bkt/figures/xy-sampling.png)

本次所检查的起态差异、前后半段差异没有越过脚本设置的三倍组合分块误差提示线。这个结果只说明这批检查没有检出那一级差异，不是充分热化的证明，更不是“再加长也不会变”。

## 有限尺寸曲线与 2T/π 相遇在哪里

### 交给代码助手的任务：分析已有 XY 轨迹

> 读取保存的 base/、extended/ 轨迹参数与抽样序列，按 L、temperature_J、随机种子和初态分组。J=kB=1，温度按无量纲 kBT/J 解释；sweep 是抽样次数。按原 analyse.py 的公式计算能量、涡旋密度和 helicity modulus，保留逐链热化/样本长度、分块误差与两种子差异。汇总误差使用既有 display_error_J 定义，不能再除以样本数。用各 L 的 Y−2T/π 在相邻温度点的符号变化输出 crossing_brackets；本数据只给出0.92–1.00交叉温区，不拟合热力学极限温度。保存链级和温度级 CSV、诊断 JSON 及完整源码，报告缺失/非有限记录；只分析已有44条轨迹，不运行 Monte Carlo 或材料计算，不把无量纲温区改标为 K。

[完整分析源码 analyse.py](/Atlas/examples/xy-bkt/analyse.py) · [保存数据核对源码 verify.py](/Atlas/examples/xy-bkt/verify.py) · [原抽样源码 mc.py](/Atlas/examples/xy-bkt/mc.py)。

<details>
<summary>mc.py 的完整源码</summary>

```python
"""Nearest-neighbour classical XY Monte Carlo on even periodic square lattices.

J=k_B=1. Checkerboard Metropolis, fixed symmetric angle proposal.
One sweep attempts every spin once. NumPy only; no DFT/material parameters.
"""
from pathlib import Path
import argparse
import csv
import json
import time
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

ROOT=Path(__file__).resolve().parent

def energy(theta):
    return -float(np.sum(np.cos(np.roll(theta,-1,axis=0)-theta)+np.cos(np.roll(theta,-1,axis=1)-theta)))

def sweep(theta,rng,temperature,masks):
    accepted=0
    for mask in masks:
        c=np.cos(theta);s=np.sin(theta)
        hc=np.roll(c,1,0)+np.roll(c,-1,0)+np.roll(c,1,1)+np.roll(c,-1,1)
        hs=np.roll(s,1,0)+np.roll(s,-1,0)+np.roll(s,1,1)+np.roll(s,-1,1)
        proposal=theta+rng.uniform(-np.pi/2,np.pi/2,theta.shape)
        delta=-(np.cos(proposal)-c)*hc-(np.sin(proposal)-s)*hs
        take=mask&(rng.random(theta.shape)<np.exp(-np.maximum(delta,0)/temperature))
        theta[take]=(proposal[take]+np.pi)%(2*np.pi)-np.pi
        accepted+=int(np.count_nonzero(take))
    return accepted/theta.size

def observe(theta):
    dx=np.roll(theta,-1,axis=0)-theta
    dy=np.roll(theta,-1,axis=1)-theta
    cx=float(np.cos(dx).sum());cy=float(np.cos(dy).sum())
    ix=float(np.sin(dx).sum());iy=float(np.sin(dy).sum())
    magnetization=abs(np.exp(1j*theta).mean())**2
    wrap=lambda x:(x+np.pi)%(2*np.pi)-np.pi
    vortex=np.rint((wrap(dx)+np.roll(wrap(dy),-1,axis=0)-np.roll(wrap(dx),-1,axis=1)-wrap(dy))/(2*np.pi)).astype(int)
    assert int(vortex.sum())==0
    return [-(cx+cy)/theta.size,float(magnetization),cx,cy,ix,iy,ix*ix,iy*iy,float(np.abs(vortex).mean())],vortex

def self_check():
    n=8;theta=np.zeros((n,n));assert energy(theta)==-2*n*n
    rng=np.random.default_rng(9135701);theta=rng.uniform(-np.pi,np.pi,(n,n))
    errors=[]
    for _ in range(25):
        i,j=map(int,rng.integers(0,n,size=2));old=theta[i,j];new=rng.uniform(-np.pi,np.pi)
        neighbours=[theta[(i+1)%n,j],theta[(i-1)%n,j],theta[i,(j+1)%n],theta[i,(j-1)%n]]
        local=-sum(np.cos(new-v)-np.cos(old-v) for v in neighbours)
        before=energy(theta);theta[i,j]=new;actual=energy(theta)-before
        errors.append(abs(local-actual))
    assert max(errors)<1e-12
    values,vort=observe(theta)
    assert abs(values[0]*n*n-energy(theta))<1e-12
    result={'ordered_energy_per_spin':-2.0,'random_local_delta_energy_max_error':max(errors),'periodic_net_vorticity':int(vort.sum()),'numpy':np.__version__}
    print('SELF_CHECK',json.dumps(result),flush=True)
    return result

def run_case(spec):
    length,temperature,seed,initial,extend=spec
    name=f'L{length}-T{temperature:.2f}-s{seed}'
    base=ROOT/'base'/name;target=(ROOT/'extended'/name) if extend else base
    target.mkdir(parents=True,exist_ok=False)
    rng=np.random.default_rng(seed)
    parity=np.indices((length,length)).sum(axis=0)%2
    masks=[parity==0,parity==1]
    started=time.perf_counter()
    if extend:
        theta=np.load(base/'final-angles.npy')
        rng.bit_generator.state=json.loads((base/'rng-state.json').read_text())
        previous=np.loadtxt(base/'series.csv',delimiter=',',skiprows=1)
        warmup=0
    else:
        theta=np.zeros((length,length)) if initial=='ordered' else rng.uniform(-np.pi,np.pi,(length,length))
        previous=None;warmup=5000
    initial_energy=energy(theta)/theta.size
    initial_angles=theta.copy()
    warm_records=[]
    warm_accept=0
    for step in range(1,warmup+1):
        warm_accept+=sweep(theta,rng,temperature,masks)
        if step%50==0:
            obs,_=observe(theta);warm_records.append([step,*obs])
    rows=[];acceptance=0
    for step in range(1,20001):
        acceptance+=sweep(theta,rng,temperature,masks)
        if step%5==0:
            obs,_=observe(theta);rows.append([step+(20000 if extend else 0),*obs])
    data=np.array(rows)
    if previous is not None:data=np.vstack([previous,data])
    header='sweep,energy_per_spin,M2,cos_x,cos_y,current_x,current_y,current_x2,current_y2,vortex_abs_density'
    np.savetxt(target/'series.csv',data,delimiter=',',header=header,comments='')
    if warm_records:np.savetxt(target/'warmup.csv',np.array(warm_records),delimiter=',',header=header,comments='')
    obs,vort=observe(theta)
    np.save(target/'initial-angles.npy',initial_angles);np.save(target/'final-angles.npy',theta)
    np.savetxt(target/'final-angles.csv',theta,delimiter=',')
    np.savetxt(target/'final-vortices.csv',vort,delimiter=',',fmt='%d')
    (target/'rng-state.json').write_text(json.dumps(rng.bit_generator.state,indent=2)+'\n')
    receipt=dict(L=length,temperature_J=temperature,J=1,kB=1,seed=seed,initialization=initial,extension_from_base=extend,initial_energy_per_spin=initial_energy,warmup_sweeps=warmup,production_sweeps=40000 if extend else 20000,additional_production_sweeps=20000,measurement_every_sweeps=5,measurements=len(data),proposal_half_width_rad=float(np.pi/2),sweep_definition='two checkerboard sublattice updates, each spin attempted once',warmup_acceptance=warm_accept/warmup if warmup else None,production_acceptance=acceptance/20000,periodic_net_vorticity=int(vort.sum()),wall_seconds=time.perf_counter()-started,numpy_version=np.__version__)
    (target/'run.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('FINISHED',str(target.relative_to(ROOT)),f"samples={len(data)} acceptance={receipt['production_acceptance']:.4f} wall={receipt['wall_seconds']:.2f}s",flush=True)
    return receipt

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--benchmark',action='store_true');parser.add_argument('--base',action='store_true');parser.add_argument('--extended',action='store_true');args=parser.parse_args()
    check=self_check()
    if args.benchmark:
        theta=np.zeros((24,24));rng=np.random.default_rng(20260922);parity=np.indices(theta.shape).sum(0)%2;masks=[parity==0,parity==1]
        start=time.perf_counter()
        for i in range(1000):sweep(theta,rng,.92,masks)
        duration=time.perf_counter()-start
        print(f'BENCHMARK L24 1000 sweeps = {duration:.6f} s; 36 base + 8 extension cases at 2 workers estimated < {duration*1060/2:.1f} s plus I/O',flush=True)
        return
    temps=[.70,.80,.88,.92,1.00,1.10]
    specifications=[]
    for length in [8,16,24]:
        for ti,temp in enumerate(temps):
            for replica,initial in [(0,'ordered'),(1,'random')]:
                if args.extended and not(length in [16,24] and temp in [.88,.92]):continue
                seed=2026092200+length*100+ti*2+replica
                specifications.append((length,temp,seed,initial,args.extended))
    assert args.base or args.extended
    start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=2) as pool:
        result=[f.result() for f in as_completed([pool.submit(run_case,s) for s in specifications])]
    record=dict(hamiltonian='H/J=-sum_nearest_neighbour_once cos(theta_i-theta_j)',boundary='periodic square',software='Python/NumPy, two workers, one thread each',cases=result,total_wall_seconds=time.perf_counter()-start,self_check=check,interpretation='finite size and finite sampling model demonstration; no material J or thermodynamic-limit transition estimate')
    (ROOT/('extended-summary.json' if args.extended else 'base-summary.json')).write_text(json.dumps(record,indent=2)+'\n')
    print('MONTE_CARLO_FINISHED',len(result),'cases',f"wall={record['total_wall_seconds']:.2f}s",flush=True)

if __name__=='__main__':main()
```

</details>

<details>
<summary>analyse.py 的完整源码</summary>

```python
"""Block jackknife of helicity modulus; preserve finite-sampling limitations."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
R=Path(__file__).resolve().parent;O=R/'results';O.mkdir(exist_ok=True)

def write(name,rows):
    with (O/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)

def helicity(mean,n,temp):
    # mean refers to the columns in series.csv, including sweep at index 0.
    return .5*(mean[3]+mean[4]-(mean[7]-mean[5]**2+mean[8]-mean[6]**2)/temp)/(n*n)

def jackknife(data,n,temp,blocks=16):
    length=len(data)//blocks
    assert length>=10
    a=data[:length*blocks].reshape(blocks,length,-1).mean(axis=1)
    mean=a.mean(axis=0)
    raw=helicity(mean,n,temp)
    leave=np.array([helicity((blocks*mean-b)/(blocks-1),n,temp) for b in a])
    corrected=blocks*raw-(blocks-1)*leave.mean()
    error=np.sqrt((blocks-1)/blocks*np.sum((leave-leave.mean())**2))
    return float(corrected),float(error),float(raw),length

def tau_positive_window(values):
    a=values-values.mean();n=len(a)
    if np.dot(a,a)==0:return .5
    size=1<<(2*n-1).bit_length()
    f=np.fft.rfft(a,n=size)
    cov=np.fft.irfft(f*np.conj(f),n=size)[:n]/np.arange(n,0,-1)
    ac=cov/cov[0];tau=.5
    for k in range(1,n//4):
        if ac[k]<=0:break
        tau+=ac[k]
        if k>=6*tau:break
    return float(tau)

cases=[]
for family in ['base','extended']:
    for d in sorted((R/family).glob('L*')):
        if not (d/'run.json').exists():continue
        run=json.loads((d/'run.json').read_text());n=run['L'];temp=run['temperature_J']
        data=np.loadtxt(d/'series.csv',delimiter=',',skiprows=1)
        assert len(data)==run['measurements'] and np.isfinite(data).all()
        assert np.array_equal(data[:,0],np.arange(1,len(data)+1)*5)
        assert np.all((-2<=data[:,1])&(data[:,1]<=2)) and np.all((0<=data[:,2])&(data[:,2]<=1+1e-12))
        assert np.allclose(data[:,1],-(data[:,3]+data[:,4])/(n*n),rtol=0,atol=1e-12)
        assert np.allclose(data[:,7],data[:,5]**2,atol=1e-10) and np.allclose(data[:,8],data[:,6]**2,atol=1e-10)
        y,error,raw,blocklength=jackknife(data,n,temp)
        y8,e8,_,_=jackknife(data,n,temp,8);y32,e32,_,_=jackknife(data,n,temp,32)
        tauE=tau_positive_window(data[:,1]);tauI=tau_positive_window(data[:,7]+data[:,8]);tau=max(tauE,tauI)
        half=len(data)//2;first=jackknife(data[:half],n,temp,8);last=jackknife(data[half:],n,temp,8)
        case=dict(family=family,case=d.name,L=n,temperature_J=temp,seed=run['seed'],initialization=run['initialization'],production_sweeps=run['production_sweeps'],measurements=len(data),energy_per_spin=float(data[:,1].mean()),M2=float(data[:,2].mean()),vortex_abs_density=float(data[:,9].mean()),Y_J=y,Y_block_stderr_J=error,Y_raw_J=raw,Y_error_8_blocks_J=e8,Y_error_32_blocks_J=e32,block_sweeps=blocklength*5,tau_energy_sweeps=tauE*5,tau_current_squared_sweeps=tauI*5,block_over_max_tau=blocklength/tau,effective_samples_diagnostic=len(data)/(2*tau),first_half_Y_J=first[0],second_half_Y_J=last[0],half_shift_J=last[0]-first[0],half_shift_over_combined_block_error=abs(last[0]-first[0])/max(np.hypot(first[1],last[1]),1e-15),acceptance=run['production_acceptance'])
        cases.append(case)
write('cases.csv',cases)
groups=[]
for n in [8,16,24]:
    for temp in [.70,.80,.88,.92,1.00,1.10]:
        family='extended' if n in [16,24] and temp in [.88,.92] else 'base'
        rows=[c for c in cases if c['L']==n and c['temperature_J']==temp and c['family']==family]
        assert len(rows)==2
        y=np.array([c['Y_J'] for c in rows]);e=np.array([c['Y_block_stderr_J'] for c in rows])
        within=float(np.linalg.norm(e)/2);between=float(abs(y[0]-y[1])/2)
        groups.append(dict(L=n,temperature_J=temp,family=family,independent_seeds=2,Y_J=float(y.mean()),within_chain_stderr_J=within,between_seed_stderr_J=between,display_error_J=max(within,between),seed_difference_J=float(abs(y[0]-y[1])),seed_difference_over_combined_block_error=float(abs(y[0]-y[1])/max(np.linalg.norm(e),1e-15)),reference_2T_over_pi=float(2*temp/np.pi),min_block_over_tau=min(c['block_over_max_tau'] for c in rows),max_half_shift_over_combined_error=max(c['half_shift_over_combined_block_error'] for c in rows),vortex_abs_density=float(np.mean([c['vortex_abs_density'] for c in rows]))))
write('helicity.csv',groups)
extensions=[]
for c in cases:
    if c['family']!='extended':continue
    b=next(x for x in cases if x['family']=='base' and x['case']==c['case'])
    extensions.append(dict(L=c['L'],temperature_J=c['temperature_J'],seed=c['seed'],initialization=c['initialization'],base_sweeps=b['production_sweeps'],extended_sweeps=c['production_sweeps'],Y_base_J=b['Y_J'],base_error_J=b['Y_block_stderr_J'],Y_extended_J=c['Y_J'],extended_error_J=c['Y_block_stderr_J'],shift_J=c['Y_J']-b['Y_J'],note='nested same-chain extension, not an independent second estimate'))
write('extension-comparison.csv',extensions)
brackets=[]
for n in [8,16,24]:
    rows=sorted([g for g in groups if g['L']==n],key=lambda g:g['temperature_J'])
    for a,b in zip(rows,rows[1:]):
        if (a['Y_J']-a['reference_2T_over_pi'])*(b['Y_J']-b['reference_2T_over_pi'])<0:
            brackets.append(dict(L=n,lower_sampled_T=a['temperature_J'],upper_sampled_T=b['temperature_J'],meaning='finite-size mean-curve crossing bracket only; no extrapolation to thermodynamic limit'))
flags=[{'case':c['family']+'/'+c['case'],'block_over_tau':c['block_over_max_tau'],'half_shift_over_error':c['half_shift_over_combined_block_error']} for c in cases if c['block_over_max_tau']<10 or c['half_shift_over_combined_block_error']>3]
seed_flags=[g for g in groups if g['seed_difference_over_combined_block_error']>3]
summary=dict(model='periodic nearest-neighbour square-lattice classical XY; J=kB=1',helicity_definition='Y=(<Cx+Cy>-[Var(Ix)+Var(Iy)]/T)/(2 L^2)',uncertainty='16-block delete-one jackknife per chain; plotted error=max(within-chain combined error, half the two-seed difference); diagnostic error, not a calibrated confidence interval',autocorrelation='positive autocorrelation window capped at six tau; diagnostic only',case_count=len(cases),base_cases=sum(c['family']=='base' for c in cases),extended_cases=sum(c['family']=='extended' for c in cases),crossing_brackets=brackets,sampling_flags=flags,seed_disagreement_flags=seed_flags,conclusion='finite-size Monte Carlo workflow completed; thermodynamic-limit TBKT and material temperatures not estimated')
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('L  T/J    Y/J      display_error   seed_delta/error  minimum_block/tau')
for g in groups:print(f"{g['L']:2d} {g['temperature_J']:.2f}  {g['Y_J']:+.6f}   {g['display_error_J']:.6f}          {g['seed_difference_over_combined_block_error']:.2f}             {g['min_block_over_tau']:.1f}")
print('Mean-curve crossing brackets:',brackets)
print('Sampling flags:',len(flags),'seed disagreement flags:',len(seed_flags))
print('No thermodynamic-limit TBKT, no material J, no material superconducting temperature.')
```

</details>

<details>
<summary>verify.py 的完整源码</summary>

```python
"""Verify saved Monte Carlo snapshots and continuations without a new campaign."""
from pathlib import Path
import csv,json,math
import numpy as np
R=Path(__file__).resolve().parent
errors=[];vortex_errors=[];extensions=0;current_z=[]
for family in ['base','extended']:
    for d in sorted((R/family).glob('L*')):
        a=np.loadtxt(d/'final-angles.csv',delimiter=',');q=np.loadtxt(d/'final-vortices.csv',delimiter=',',dtype=int)
        n=len(a);energy=0;charge=np.zeros((n,n),int)
        wrap=lambda x:(x+math.pi)%(2*math.pi)-math.pi
        for i in range(n):
            for j in range(n):
                energy-=math.cos(a[(i+1)%n,j]-a[i,j])+math.cos(a[i,(j+1)%n]-a[i,j])
                edges=[a[(i+1)%n,j]-a[i,j],a[(i+1)%n,(j+1)%n]-a[(i+1)%n,j],a[i,(j+1)%n]-a[(i+1)%n,(j+1)%n],a[i,j]-a[i,(j+1)%n]]
                charge[i,j]=round(sum(wrap(x) for x in edges)/(2*math.pi))
        data=np.loadtxt(d/'series.csv',delimiter=',',skiprows=1)
        errors.append(abs(energy/(n*n)-data[-1,1]));vortex_errors.append(int(np.max(np.abs(charge-q))))
        assert charge.sum()==0
        blocks=data.reshape(16,len(data)//16,10).mean(axis=1)
        for k in [5,6]:
            se=np.std(blocks[:,k],ddof=1)/4
            current_z.append(abs(blocks[:,k].mean())/max(se,1e-15))
        if family=='extended':
            base=R/'base'/d.name;b=np.loadtxt(base/'series.csv',delimiter=',',skiprows=1)
            assert np.array_equal(data[:len(b)],b)
            assert np.array_equal(np.load(d/'initial-angles.npy'),np.load(base/'final-angles.npy'))
            extensions+=1
assert max(errors)<1e-12 and max(vortex_errors)==0 and extensions==8
# Seed reproducibility check of the saved first 100 warmup sweeps.
from mc import sweep,observe
d=R/'base/L8-T0.70-s2026093001'
meta=json.loads((d/'run.json').read_text());n=meta['L'];rng=np.random.default_rng(meta['seed'])
theta=rng.uniform(-np.pi,np.pi,(n,n));parity=np.indices((n,n)).sum(0)%2;masks=[parity==0,parity==1]
saved=np.loadtxt(d/'warmup.csv',delimiter=',',skiprows=1);prefix=[]
for step in range(1,101):
    sweep(theta,rng,meta['temperature_J'],masks)
    if step%50==0:obs,_=observe(theta);prefix.append([step,*obs])
replay_error=float(np.max(np.abs(np.array(prefix)-saved[:2])))
# Short replay only: permit floating-point reductions across BLAS/libm/CPU variants.
# Stored base/extension sample equality above remains exact.
assert np.allclose(np.array(prefix),saved[:2],rtol=1e-13,atol=1e-13), f'Short seed replay differs by {replay_error}'
receipt=dict(checked_snapshots=len(errors),max_snapshot_energy_error_per_spin=max(errors),max_snapshot_vorticity_error=max(vortex_errors),continuations_with_identical_original_samples=extensions,seed_warmup_replay_max_error=replay_error,max_current_mean_over_block_error=max(current_z),current_mean_note='zero-current symmetry check is a finite-sampling diagnostic, not a proof of winding-sector ergodicity')
(R/'results/independent-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
print('SAVED_DATA_CHECKS_PASSED; sampling and thermodynamic-limit convergence remain separate.')
```

</details>

```console
talos@talos-MS-7D54:~/xy-bkt$ python3 -B analyse.py > analyse.out 2> analyse.err; echo "exit=$?"
exit=0
talos@talos-MS-7D54:~/xy-bkt$ head -19 analyse.out
L  T/J    Y/J      display_error   seed_delta/error  minimum_block/tau
 8 0.70  +0.785049   0.001336          1.97             314.4
 8 0.80  +0.734276   0.001520          1.13             252.9
 8 0.88  +0.681421   0.003004          0.54             222.7
 8 0.92  +0.652275   0.003858          0.15             169.8
 8 1.00  +0.570432   0.010481          2.25             136.4
 8 1.10  +0.443103   0.014112          1.73             102.1
16 0.70  +0.778496   0.000443          0.74             279.3
16 0.80  +0.721847   0.001557          1.15             128.8
16 0.88  +0.663836   0.002284          0.44             235.9
16 0.92  +0.614160   0.003609          0.10             117.9
16 1.00  +0.490403   0.011392          1.06             51.9
16 1.10  +0.256825   0.020686          1.43             34.3
24 0.70  +0.778040   0.000581          0.07             236.0
24 0.80  +0.720485   0.001789          0.94             44.6
24 0.88  +0.651180   0.003518          1.12             80.7
24 0.92  +0.610133   0.005765          1.20             66.3
24 1.00  +0.455445   0.022363          1.57             30.7
24 1.10  +0.163436   0.023722          0.88             23.9
```

![三个有限尺寸的相位刚度、参考线与涡旋密度](/Atlas/examples/xy-bkt/figures/xy-helicity.png)

三个尺寸的平均曲线都在采样温度 0.92 与 1.00 之间越过 2T/π。这里没有把两点连线的交点报成 T_BKT：温度间隔还很粗，体系也只有 8²、16²、24²。三个尺寸落在同一温度区间，不能说明尺寸效应已经消失。

右图的涡旋密度随温度增加。它能帮助理解局部角度缺陷如何出现，但仅有密度还没有区分束缚对与自由涡旋，也没有建立热力学极限的 BKT 标度。要研究极限温度，应在更大尺寸上结合对数有限尺寸修正、相关性和更充分的抽样，不能把三个小系统的曲线硬拟合成一个精确数字。

## 把涡旋放在实际构型上看

![实际抽样得到的二维XY构型与涡旋位置](/Atlas/examples/xy-bkt/figures/xy-configurations.png)

箭头来自保存的末态角度，圆圈与方框标记 q=+1 与 q=−1 的小格子中心。它们是某一次构型的快照，不能代替系综平均；周期边缘的箭头和缺陷也需要与另一侧连接起来阅读。图片中的种子写在标题上，可以回到相应目录的 `final-angles.csv` 和 `final-vortices.csv` 核对。

保存数据另做了一次独立检查：用普通循环重新计算全部 44 份末态的能量与涡旋，最大每自旋能量差 2.66×10⁻¹⁵，涡旋电荷逐格一致。八份加长序列的前 4000 行与原数据完全相同；从记录的随机种子重放前 100 次热化，在原 Talos 环境中也精确复现了两次已保存测量。Mac（NumPy 2.3.4）重算这两行时最大差为 7.11×10⁻¹⁵，来自浮点求值与归约的微小差别；下载脚本对这项短重放采用 `rtol=1e-13, atol=1e-13` 的检查。加长序列与原序列的已保存前缀仍要求逐项完全相同，涡旋整数也严格核对。不同 NumPy 版本或硬件上的长随机轨迹不承诺逐位相同；一次接受分支的微小变化就可能使后续路径分开。

```console
talos@talos-MS-7D54:~/xy-bkt$ python3 -B verify.py > verify.out 2> verify.err; echo "exit=$?"
exit=0
```

[检查记录](/Atlas/examples/xy-bkt/results/independent-check.json)和[完整输出](/Atlas/examples/xy-bkt/verify.out)随包保存。基础抽样、加长抽样、分析与独立检查的最终错误文件均为空；程序结束与统计收敛仍是两项不同判断。

## 下载后继续使用这些数据

已有结果可以直接出图，不必重新抽样。在解压后的 `xy-bkt` 目录，以有 NumPy、Matplotlib 的 Python 运行：

```bash
python3 plot.py
```

它读取原始 CSV 和末态构型，输出 `figures/xy-helicity.png`、`xy-configurations.png`、`xy-sampling.png` 及对应 PDF。图中连线连接实际计算的六个温度点。

相位刚度图读取 `results/helicity.csv` 的 18 行汇总，即 3 个尺寸各 6 个温度。横轴来自 `temperature_J`，纵轴来自 `Y_J`，误差棒使用 `display_error_J`：它取链内分块误差与两个种子之间误差估计的较大者。重画时不要误选单个种子的标准差，也不要把这列再除以样本数。`reference_2T_over_pi` 保存了同一温度的参考值；曲线交点仍只属于这些有限尺寸与离散温度的比较。

加长抽样图读取 `results/extension-comparison.csv`，能量分块记录则来自 `extended/` 中对应两条 L=24、T/J=0.92 链的 `series.csv`。快照读取按名称排序后选定的 L=24 低温与高温目录，并从其中的 `run.json` 取种子。要换一份快照，应同时换它的 `final-angles.csv`、`final-vortices.csv` 与标题中的种子，不能只换箭头图而留下另一条链的缺陷标记。

论文图使用 [Nature 要求的可编辑矢量输出](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/)时，在创建画布前选择已安装的 Arial/Helvetica 并设置 `pdf.fonttype=42`；保留现有 PDF 保存步骤即可，字体与布局需重新导出。网页图使用适合屏幕的字号，论文副本再按最终版面检查 5—7 pt 正文与 8 pt 面板号。文字、图例和坐标保持黑色，尺寸 L 用不同标记或线型辅助区分颜色。

快照里箭头方向已经表示角度；若继续用颜色编码角度，应补上带弧度单位的色标，否则可使用单色箭头。q=+1 和 q=−1 继续用圆圈与方框区分，不能只剩红蓝颜色。坐标表示格点位置，可标为 `x / a`、`y / a`，其中 a 是方格间距；这不是材料的 Å 坐标。`2T/π` 参考线、误差棒和周期边界附近的涡旋都保留，不能在整理画面时删掉。

若要重新运行，把四份 Python 脚本复制到一个新的空目录，先做 `--benchmark`，再按 `--base → --extended → analyse.py → verify.py` 的顺序执行。`mc.py` 会拒绝覆盖已有 case 目录；这使原始抽样记录可以保留下来比较。已有包中的 `base/` 与 `extended/` 是结果，不要在原处重跑后覆盖。

下一步可对照[有限尺寸研究中的对数修正](https://arxiv.org/abs/cond-mat/0502556)，设计更大 L、更密温度点和更充分的抽样。本页完成的是无量纲二维模型的数值教案；若要谈真实二维材料，需要另外建立材料参数与有效模型之间的对应关系。

```text
H、J=kB=1、周期边界
  → 两种起态与独立种子
  → 热化记录 → 正式抽样序列
  → 能量 / 涡旋 / helicity modulus
  → 分块误差、相关性、加长抽样
  → 有限尺寸曲线与2T/π对照
  → 更大尺寸与标度检查后，才讨论热力学极限
```
