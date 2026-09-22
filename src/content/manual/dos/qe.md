参考：

- QE 官方文档 INPUT_DOS：<https://www.quantum-espresso.org/Doc/INPUT_DOS.html>
- QE 官方文档 INPUT_PROJWFC：<https://www.quantum-espresso.org/Doc/INPUT_PROJWFC.html>

## TDOS 与 PDOS：dos.x 和 projwfc.x

DOS 描述「某个特定能量位置上有多少个可供电子占据的量子态」，横坐标能量、纵坐标状态数。上一页的 DOS-NSCF（k 36×36×1）跑完后，TDOS 与 PDOS 都直接读取 `07_dos/nscf/out/HfCl2_PbO2.save`，不需要再复制波函数目录。两者分工：`dos.x` 出总态密度（TDOS），`projwfc.x` 出逐原子逐轨道投影（PDOS）。

### TDOS：dos.in 与提交

```bash
[<user>@<cluster> QE]$ cd <工作目录>/QE

[<user>@<cluster> QE]$ mkdir -p 07_dos/tdos
[<user>@<cluster> QE]$ cd 07_dos/tdos

[<user>@<cluster> tdos]$ cat > dos.in <<'EOF'
&DOS
  prefix = 'HfCl2_PbO2'
  outdir = '../nscf/out/'
  fildos = 'HfCl2_PbO2.dos'
  Emin = -10.0
  Emax = 10.0
  DeltaE = 0.01
  ngauss = 0
  degauss = 0.0037
/
EOF
```

`degauss = 0.0037 Ry` 与前面的 SCF/NSCF 保持一致；比较时应标出各自展宽，另做展宽与 k 采样检查，不把一致的输入自动当成收敛。能量窗 −10 到 10 eV、步长 0.01 eV，覆盖费米能级上下足够远。

```bash
[<user>@<cluster> tdos]$ cat > dos.slurm <<'EOF'
#!/bin/bash
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

ulimit -s unlimited
ulimit -l unlimited

source /data/intel/oneapi/setvars.sh

cd $SLURM_SUBMIT_DIR

mpirun -np 56 <qe_bin>/dos.x \
  -in dos.in > dos.out
EOF

[<user>@<cluster> tdos]$ sbatch dos.slurm
```

### TDOS 验收

```bash
[<user>@<cluster> tdos]$ grep "JOB DONE" dos.out
   JOB DONE.
[<user>@<cluster> tdos]$ cat _err.*.log
[<user>@<cluster> tdos]$
[<user>@<cluster> tdos]$ ls -lh HfCl2_PbO2.dos
-rw-rw-r-- 1 <user> <user> 65K Sep  5 14:22 HfCl2_PbO2.dos
[<user>@<cluster> tdos]$ head HfCl2_PbO2.dos
#  E (eV)   dos(E)     Int dos(E) EFermi =    0.050 eV
 -10.000  0.9616E-84  0.9616E-86
  -9.990  0.9616E-84  0.1923E-85
  -9.980  0.9616E-84  0.2885E-85
  -9.970  0.9616E-84  0.3846E-85
  -9.960  0.9616E-84  0.4808E-85
  -9.950  0.9616E-84  0.5770E-85
  -9.940  0.9616E-84  0.6731E-85
  -9.930  0.9616E-84  0.7693E-85
  -9.920  0.9616E-84  0.8654E-85
[<user>@<cluster> tdos]$
```

判读：JOB DONE、err 日志为空、.dos 文件生成；文件头直接给出本次用的费米能级 `EFermi = 0.050 eV`。深能级处 dos(E) 是 10⁻⁸⁴ 量级——不是零但完全可忽略，说明展宽下限正常。

### PDOS：projwfc.in 与提交

```bash
[<user>@<cluster> QE]$ mkdir -p 07_dos/pdos
[<user>@<cluster> QE]$ cd 07_dos/pdos

[<user>@<cluster> pdos]$ cat > projwfc.in <<'EOF'
&PROJWFC
  prefix = 'HfCl2_PbO2'
  outdir = '../nscf/out/'
  filpdos = 'HfCl2_PbO2'
  Emin = -10.0
  Emax = 10.0
  DeltaE = 0.01
  ngauss = 0
  degauss = 0.0037
/
EOF

[<user>@<cluster> pdos]$ cat > pdos.slurm <<'EOF'
#!/bin/bash
#SBATCH -o _out.%j.log
#SBATCH -e _err.%j.log

ulimit -s unlimited
ulimit -l unlimited

source /data/intel/oneapi/setvars.sh

cd $SLURM_SUBMIT_DIR

mpirun -np 56 <qe_bin>/projwfc.x \
  -in projwfc.in > projwfc.out
EOF

[<user>@<cluster> pdos]$ sbatch pdos.slurm
```

### PDOS 验收：文件体系与轨道通道

```bash
[<user>@<cluster> pdos]$ grep "JOB DONE" projwfc.out
   JOB DONE.
[<user>@<cluster> pdos]$
[<user>@<cluster> pdos]$ grep -iE "error|warning" projwfc.out | tail -n 30
[<user>@<cluster> pdos]$
[<user>@<cluster> pdos]$ ls -lh HfCl2_PbO2*
-rw-rw-r-- 1 <user> <user>  46K Sep  5 14:24 HfCl2_PbO2.pdos_atm#1(Hf)_wfc#1(s)
-rw-rw-r-- 1 <user> <user>  46K Sep  5 14:24 HfCl2_PbO2.pdos_atm#1(Hf)_wfc#2(s)
-rw-rw-r-- 1 <user> <user>  77K Sep  5 14:24 HfCl2_PbO2.pdos_atm#1(Hf)_wfc#3(p)
-rw-rw-r-- 1 <user> <user> 109K Sep  5 14:24 HfCl2_PbO2.pdos_atm#1(Hf)_wfc#4(d)
-rw-rw-r-- 1 <user> <user>  46K Sep  5 14:24 HfCl2_PbO2.pdos_atm#2(Cl)_wfc#1(s)
-rw-rw-r-- 1 <user> <user>  77K Sep  5 14:24 HfCl2_PbO2.pdos_atm#2(Cl)_wfc#2(p)
-rw-rw-r-- 1 <user> <user>  46K Sep  5 14:24 HfCl2_PbO2.pdos_atm#3(Cl)_wfc#1(s)
-rw-rw-r-- 1 <user> <user>  77K Sep  5 14:24 HfCl2_PbO2.pdos_atm#3(Cl)_wfc#2(p)
-rw-rw-r-- 1 <user> <user>  46K Sep  5 14:24 HfCl2_PbO2.pdos_atm#4(Pb)_wfc#1(s)
-rw-rw-r-- 1 <user> <user>  77K Sep  5 14:24 HfCl2_PbO2.pdos_atm#4(Pb)_wfc#2(p)
-rw-rw-r-- 1 <user> <user> 109K Sep  5 14:24 HfCl2_PbO2.pdos_atm#4(Pb)_wfc#3(d)
-rw-rw-r-- 1 <user> <user>  46K Sep  5 14:24 HfCl2_PbO2.pdos_atm#5(O)_wfc#1(s)
-rw-rw-r-- 1 <user> <user>  77K Sep  5 14:24 HfCl2_PbO2.pdos_atm#5(O)_wfc#2(p)
-rw-rw-r-- 1 <user> <user>  46K Sep  5 14:24 HfCl2_PbO2.pdos_atm#6(O)_wfc#1(s)
-rw-rw-r-- 1 <user> <user>  77K Sep  5 14:24 HfCl2_PbO2.pdos_atm#6(O)_wfc#2(p)
-rw-rw-r-- 1 <user> <user>  46K Sep  5 14:24 HfCl2_PbO2.pdos_tot
[<user>@<cluster> pdos]$
```

再抓一下投影通道清单，它告诉你每个原子有哪些 s/p/d 投影轨道（`grep "state #" projwfc.out`，本例 35 条 state：Hf s+p+d、Cl 各 s+p、Pb s+p+d、O 各 s+p，完整清单见 projwfc.out）。归纳成：

```text
Hf : s + p + d
Cl : s + p
Pb : s + p + d
O  : s + p
```

TDOS 和 PDOS 都正常完成、无 warning/error，DOS 流程可以判定完成。

### 定量判读：DOS(EF) 与金属判定

先把 E_F 附近的 DOS 定量取出来。dos.x 给出的费米能级是 0.050 eV：

```bash
[<user>@<cluster> tdos]$ awk '
> BEGIN { EF=0.050; best=1e9 }
> $1 !~ /^#/ {
>     d=$1-EF
>     if(d<0)d=-d
>     if(d<best){
>         best=d
>         E=$1
>         DOS=$2
>         INT=$3
>     }
> }
> END {
>     print "E nearest EF =",E,"eV"
>     print "DOS(EF)      =",DOS,"states/eV/cell"
>     print "Int DOS      =",INT
> }
> ' HfCl2_PbO2.dos
E nearest EF = 0.050 eV
DOS(EF)      = 0.1893E+01 states/eV/cell
Int DOS      = 0.2601E+02
```

再看费米能级前后 ±0.1 eV 的逐点形状：

```bash
[<user>@<cluster> tdos]$ awk '
> $1 !~ /^#/ && $1>=-0.05 && $1<=0.15 {
>     print
> }
> ' HfCl2_PbO2.dos
  -0.050  0.5132E+00  0.2588E+02
  -0.040  0.5509E+00  0.2589E+02
   ...
   0.040  0.1911E+01  0.2599E+02
   0.050  0.1893E+01  0.2601E+02
   0.060  0.1785E+01  0.2603E+02
   ...
   0.150  0.8934E+00  0.2613E+02
```

DOS 在 E_F 两侧连续、没有落零的缺口。再看 pdos_tot 在 E_F 最近一点的值：

```bash
[<user>@<cluster> pdos]$ awk '
> BEGIN { EF=0.050; best=1e9 }
> $1 !~ /^#/ {
>     d=$1-EF
>     if(d<0)d=-d
>     if(d<best){ best=d; line=$0 }
> }
> END { print line }
> ' HfCl2_PbO2.pdos_tot
   0.050  0.189E+01  0.184E+01
[<user>@<cluster> pdos]$
```

在 E_F 附近，dos.x 给出 1.893 states/eV/cell，pdos_tot 的两列为 1.89 和 1.84。更正（2026-09-22）：原文漏读了 `E+01`，把后两数写成了 0.189、0.184。这个点上投影和与总 DOS 接近，但不能由单点比例宣布投影基组完备。有限展宽下的非零 DOS 也应结合能带交叉和采样检查来判断。

### 把总 DOS 与投影和放在一起

![同一候选结构的总 DOS 与总投影 DOS 对照](/Atlas/figures/dos.svg)

图中能量统一减去 0.050 eV，虚线为 projwfc.x 的投影和。两者并非每处都完全相同。比较应在所讨论的能量窗口进行，记录 k 网格、展宽和投影定义，而不是只算费米能级一个点的比值。

## 下一步

DOS 主流程完成，进入能带计算（bands → bands.x），轨道分辨的深入分析（按元素×轨道拆 PDOS 权重）见胖带数据页：

```text
static SCF → DOS-NSCF（上一页）
    ↓
dos.x → TDOS       ← 本页
projwfc.x → PDOS   ← 本页
    ↓
bands → bands.x
```
