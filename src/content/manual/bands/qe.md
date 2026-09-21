参考：

- QE 官方文档 INPUT_PW：<https://www.quantum-espresso.org/Doc/INPUT_PW.html>
- QE 官方文档 INPUT_BANDS：<https://www.quantum-espresso.org/Doc/INPUT_BANDS.html>

## 能带：pw.x bands + bands.x

能带计算分两步：`pw.x` 以 `calculation = 'bands'` 沿高对称路径解本征值（非自洽，复用 static SCF 的电荷密度），再用后处理程序 `bands.x` 把本征值整理成可直接画图的数据文件。本例做无 SOC 的 Γ-M-K-Γ 能带。

### 路径怎么定

六方二维晶格的高对称点（倒格子分数坐标）：

```text
Γ = (0,   0,   0)
M = (1/2, 0,   0)
K = (1/3, 1/3, 0)
Γ = (0,   0,   0)
```

### 建目录与 nbnd 的选取理由

和 DOS-NSCF 一样复制 static SCF 数据：

```bash
[<user>@<cluster> QE]$ cd <工作目录>/QE

[<user>@<cluster> QE]$ mkdir -p 08_bands
[<user>@<cluster> QE]$ cd 08_bands

[<user>@<cluster> 08_bands]$ mkdir -p out

[<user>@<cluster> 08_bands]$ cp -a ../06_static/out/HfCl2_PbO2.save out/
```

写输入文件（K_POINTS 换成 crystal_b 路径卡；每行末尾整数是该段插值点数，最后一段回到 Γ 只给 1 个点）：

```bash
[<user>@<cluster> 08_bands]$ cat > bands.in <<'EOF'
&CONTROL
  calculation = 'bands'
  outdir = './out/'
  prefix = 'HfCl2_PbO2'
  pseudo_dir = '<赝势库路径>'
  verbosity = 'high'
/

&SYSTEM
  ibrav = 0
  nat = 6
  ntyp = 4
  ecutwfc = 90
  ecutrho = 720
  input_dft = 'vdw-DF3-opt1'
  force_symmorphic = .true.
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 3.7d-3
  nbnd = 40
/

&ELECTRONS
  conv_thr = 1.0000000000d-08
  electron_maxstep = 200
  mixing_beta = 7.0000000000d-01
/

ATOMIC_SPECIES
Hf  178.49   Hf.pbe-spn-kjpaw_psl.1.0.0.UPF
Cl   35.45   Cl.pbe-n-kjpaw_psl.1.0.0.UPF
Pb  207.20   Pb.pbe-dn-kjpaw_psl.1.0.0.UPF
O    15.999  O.pbe-n-kjpaw_psl.1.0.0.UPF

CELL_PARAMETERS (angstrom)
! 此处放入结构优化输出的三行晶胞矢量（本例 3.356510437 …，c = 30 Å）

ATOMIC_POSITIONS (crystal)
! 此处放入结构优化输出的六行原子坐标

K_POINTS crystal_b
4
0.0000000000  0.0000000000  0.0000000000  50
0.5000000000  0.0000000000  0.0000000000  50
0.3333333333  0.3333333333  0.0000000000  50
0.0000000000  0.0000000000  0.0000000000   1
EOF
```

这里显式设了 `nbnd = 40`，理由来自 NSCF 的实测：自动只有 31 条 Kohn-Sham bands，而体系有 52 个电子，即无自旋极化下约 26 条占据带，只剩约 5 条空带。40 条给费米能级以上留出更合理的观察窗口。注意这个值用于画电子能带，并不是一个新的物理收敛参数。

### Slurm 脚本与提交

```bash
[<user>@<cluster> 08_bands]$ cp ../05_relax/rx.slurm bands.slurm

[<user>@<cluster> 08_bands]$ sed -i \
> 's#pw.x<rx.in>rx.out#pw.x -in bands.in > bands.out#' \
> bands.slurm

[<user>@<cluster> 08_bands]$ cat bands.slurm

[<user>@<cluster> 08_bands]$ sbatch bands.slurm
```

### 验收

```bash
[<user>@<cluster> 08_bands]$ grep "JOB DONE" bands.out
   JOB DONE.
[<user>@<cluster> 08_bands]$
[<user>@<cluster> 08_bands]$ grep -E \
> "number of electrons|number of Kohn-Sham states|number of k points" \
> bands.out
     number of electrons       =        52.00
     number of Kohn-Sham states=           40
     number of k points=   151  Gaussian smearing, width (Ry)=  0.0037
[<user>@<cluster> 08_bands]$
[<user>@<cluster> 08_bands]$ grep -iE "error|warning" bands.out | tail -n 30
[<user>@<cluster> 08_bands]$
```

判读：Kohn-Sham states 从 31 提到 40，符合 nbnd 设置；151 个 k 点来自路径卡的 50+50+50+1 插值；无 error/warning。pw.x 部分完成，接着用 bands.x 把本征值整理成适合直接画 Γ-M-K-Γ 能带的数据文件。

### bands.x 后处理

```bash
[<user>@<cluster> 08_bands]$ cat > bands_pp.in <<'EOF'
&BANDS
  prefix = 'HfCl2_PbO2'
  outdir = './out/'
  filband = 'HfCl2_PbO2.bands'
/
EOF

[<user>@<cluster> 08_bands]$ cat > bands_pp.slurm <<'EOF'
#!/bin/bash
#SBATCH -o _out_bands.%j.log
#SBATCH -e _err_bands.%j.log

ulimit -s unlimited
ulimit -l unlimited

source /data/intel/oneapi/setvars.sh

cd $SLURM_SUBMIT_DIR

mpirun -np 56 <qe_bin>/bands.x \
  -in bands_pp.in > bands_pp.out
EOF

[<user>@<cluster> 08_bands]$ sbatch bands_pp.slurm
```

完成后检查：

```bash
[<user>@<cluster> 08_bands]$ grep "JOB DONE" bands_pp.out
   JOB DONE.
[<user>@<cluster> 08_bands]$
[<user>@<cluster> 08_bands]$ grep -iE "error|warning" bands_pp.out | tail -n 30
[<user>@<cluster> 08_bands]$
[<user>@<cluster> 08_bands]$ ls -lh HfCl2_PbO2.bands*
-rw-rw-r-- 1 <user> <user>  60K Sep  5 14:44 HfCl2_PbO2.bands
-rw-rw-r-- 1 <user> <user> 124K Sep  5 14:44 HfCl2_PbO2.bands.gnu
-rw-rw-r-- 1 <user> <user>  55K Sep  5 14:45 HfCl2_PbO2.bands.rap
[<user>@<cluster> 08_bands]$
```

三个产物各司其职：`.bands` 是原始本征值，`.gnu` 是 gnuplot 可直接画的网格数据，`.rap` 是重排后的辅助文件。`.gnu` 生成成功后再看头部：

```bash
[<user>@<cluster> 08_bands]$ head -n 20 HfCl2_PbO2.bands.gnu
    0.0000  -62.5594
    0.0115  -62.5594
    0.0231  -62.5594
    0.0346  -62.5593
    0.0462  -62.5591
    0.0577  -62.5590
    0.0693  -62.5587
    0.0808  -62.5585
    0.0924  -62.5582
    0.1039  -62.5579
    0.1155  -62.5576
    0.1270  -62.5572
    0.1386  -62.5568
    0.1501  -62.5563
    0.1617  -62.5559
    0.1732  -62.5554
    0.1848  -62.5549
    0.1963  -62.5544
    0.2078  -62.5538
    0.2194  -62.5532
[<user>@<cluster> 08_bands]$
```

两列分别是路径累计坐标和本征值（Ry 单位，画图时换算 Ry→eV）。同时把高对称路径坐标抓出来：

```bash
[<user>@<cluster> 08_bands]$ grep "high-symmetry point" bands_pp.out
     high-symmetry point:  0.0000 0.0000 0.0000   x coordinate   0.0000
     high-symmetry point:  0.5000 0.2887 0.0000   x coordinate   0.5774
     high-symmetry point:  0.3333 0.5774 0.0000   x coordinate   0.9107
     high-symmetry point:  0.0000 0.0000 0.0000   x coordinate   1.5774
[<user>@<cluster> 08_bands]$
```

这个输出给出 Γ、M、K、Γ 在横坐标上的累计距离：

```text
Γ : 0.0000
M : 0.5774
K : 0.9107
Γ : 1.5774
```

画图时直接拿来做竖线和横轴刻度。

### 记下费米能级

```bash
[<user>@<cluster> 08_bands]$ echo "0.0500" > Ef.dat
[<user>@<cluster> 08_bands]$ cat Ef.dat
0.0500
[<user>@<cluster> 08_bands]$
```

后面画能带统一做 E − E_F，把费米能级平移到 0 eV。

### 下一步

`.bands.gnu`、`.bands.rap` 都已生成，无 SOC 能带后处理判定完成。下一步需要额外补充 SOC，而不是先做普通能带图收尾：这个体系含 Hf 和 Pb，都是较重元素，SOC 很可能显著改变费米能级附近的能带劈裂和交叉，真正用于后续讨论的电子结构应以 SOC 结果为主。

```text
static SCF
    ↓
bands（本页，nbnd=40，151 k 点）→ bands.x → .gnu/.rap + 高对称点坐标
    ↓
SOC 补算（fully relativistic 赝势）
```
