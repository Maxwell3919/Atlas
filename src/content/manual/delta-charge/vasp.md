参考：

- vaspkit 项目主页：<https://github.com/vaspkit/vaspkit>
- VESTA 官网：<https://jp-minerals.org/vesta/>

## 差分电荷密度

差分电荷密度 Δρ = ρ(AB) − ρ(A) − ρ(B) 回答"形成异质结后电荷在空间里怎么重新分布"：正等值面是电荷积累，负等值面是电荷耗散。前提是三个体系必须在同一晶胞盒子、同一 FFT 网格上算——密度是逐点相减的，网格不一致就没法减。这决定了本页的全部操作顺序：先从母体 SCF 读出网格写死，再切片造单体、重组赝势，最后相减。

记录体系：Sc2C/ZrCl2 异质结（6 原子：Zr C Cl Sc，1 1 2 2），A = ZrCl2，B = Sc2C。

### 从母体 SCF 固定网格

```bash
[<user>@<cluster> vasp]$ cd <工作目录>/vasp/cod

[<user>@<cluster> cod]$ grep -n "dimension x,y,z" ../scf/OUTCAR
515:   dimension x,y,z NGX =    28 NGY =   28 NGZ =  294
516:   dimension x,y,z NGXF=    56 NGYF=   56 NGZF=  588

[<user>@<cluster> cod]$ mkdir -p AB part_A part_B

[<user>@<cluster> cod]$ ls
AB  part_A  part_B
```

判读：把 NGX/NGY/NGZ = 28 28 294 与 NGXF/NGYF/NGZF = 56 56 588 显式写进 INCAR，三个体系才会用同一网格。PREC = Accurate 时 VASP 默认按 ENCUT 自动定网格，删掉部分原子后网格可能改变——这正是要写死它的原因。

### INCAR 写死网格

```bash
[<user>@<cluster> cod]$ cat > INCAR <<'EOF'
SYSTEM = sc2c_zrcl2_cod
########## about parallelation ###########
   LPLANE = .TRUE.
   NPAR = 4
   NSIM = 4
##########################################
############### about I/O ################
   ISTART = 0
##########################################
########### about switch control ##########
   LWAVE = .FALSE.
   LCHARG = .TRUE.
   LCORR = .TRUE.
   LREAL = A
   LASPH = .TRUE.
   LORBIT = 11
###########################################
############# about ionic relax ############
   ISIF = 2
   IBRION = -1
   NSW = 0
###########################################
########### about electron scf ############
   ENCUT = 520
   GGA = PE
   VOSKOWN = 1
   EDIFF = 1E-6
   NELMIN = 4
   NELM = 160
##############################################
############### about mixer ###############
   AMIX = 0.1
   BMIX = 0.0001
   AMIX_MAG = 0.4
   BMIX_MAG = 0.0001
   MAXMIX = 80
   LMAXMIX = 4
   IVDW = 11
###########################################
############### other important parameter ###############
   ALGO = N
   PREC = Accurate
   ISMEAR = 0
   SIGMA = 0.05
########################################################
################## fixed FFT-grid #################
   NGX = 28
   NGY = 28
   NGZ = 294
   NGXF = 56
   NGYF = 56
   NGZF = 588
###################################################
EOF
[<user>@<cluster> cod]$ for dir in AB part_A part_B; do cp INCAR $dir/; cp ../scf/KPOINTS $dir/; cp ../scf/script_std $dir/; done

[<user>@<cluster> cod]$ cp ../scf/CONTCAR AB/POSCAR

[<user>@<cluster> cod]$ cp ../scf/POTCAR AB/
```

AB（复合体系）直接继承母体的 CONTCAR 与 POTCAR——它就是母体几何的重算。

### CONTCAR 切片造单体

```bash
[<user>@<cluster> cod]$ head -n 10 ../scf/CONTCAR
Sc2C
    1.00000000000000
      3.3268753886372542   -0.0000000000982961    0.0000000000000000
     -1.6634376949064786    2.8811586017376438    0.0000000000000000
      0.0000000000000001   -0.0000000000000005   39.5675948821758965
    Zr   C    Cl   Sc
      1     1     2     2
 Direct
   0.6666666667000030  0.3333333332999970  0.5707895733199777
   0.0000000000000000  0.0000000000000000  0.4406509079136001
```

判读：行号地图——1–5 行是标题、缩放与晶胞（a ≈ 3.3269 Å，c ≈ 39.5676 Å），6–7 行元素与数目，第 8 行 Direct，第 9–14 行坐标（9 = Zr、10 = C、11–12 = Cl、13–14 = Sc）。切片规则：晶胞五行原样保留，原子绝对位置不动，只按行号抽取——删原子不等于让剩余原子弛豫回"平衡"，否则三者的密度就不在同一构型上了。

```bash
# part_A (ZrCl2)：保留 Zr 与 Cl
[<user>@<cluster> cod]$ sed -n '1,5p' ../scf/CONTCAR > part_A/POSCAR
[<user>@<cluster> cod]$ echo "   Zr   Cl" >> part_A/POSCAR
[<user>@<cluster> cod]$ echo "     1     2" >> part_A/POSCAR
[<user>@<cluster> cod]$ echo "Direct" >> part_A/POSCAR
[<user>@<cluster> cod]$ sed -n '9p' ../scf/CONTCAR >> part_A/POSCAR     # Zr (1个)
[<user>@<cluster> cod]$ sed -n '11,12p' ../scf/CONTCAR >> part_A/POSCAR # Cl (2个)
# part_B (Sc2C)：保留 C 与 Sc
[<user>@<cluster> cod]$ sed -n '1,5p' ../scf/CONTCAR > part_B/POSCAR
[<user>@<cluster> cod]$ echo "   C    Sc" >> part_B/POSCAR
[<user>@<cluster> cod]$ echo "     1     2" >> part_B/POSCAR
[<user>@<cluster> cod]$ echo "Direct" >> part_B/POSCAR
[<user>@<cluster> cod]$ sed -n '10p' ../scf/CONTCAR >> part_B/POSCAR    # C (1个)
[<user>@<cluster> cod]$ sed -n '13,14p' ../scf/CONTCAR >> part_B/POSCAR # Sc (2个)
```

核对：`cat part_A/POSCAR`、`cat part_B/POSCAR`——两个文件都应为 11 行（头部 5 行 + 元素/数目 2 行 + Direct + 3 行坐标），part_A 为 1 Zr + 2 Cl，part_B 为 1 C + 2 Sc。

### POTCAR 按片段重组

第一反应往往是复制母体 POTCAR、或者直接用普通元素名拼，两个都会撞墙：

```bash
[<user>@<cluster> cod]$ POT_DIR="<赝势库路径>"

[<user>@<cluster> cod]$ cat $POT_DIR/Zr/POTCAR $POT_DIR/Cl/POTCAR > part_A/POTCAR
cat: <赝势库路径>/Zr/POTCAR: No such file or directory

[<user>@<cluster> cod]$ grep "TITEL" ../scf/POTCAR
    TITEL  = PAW_PBE Zr_sv 04Jan2005
    TITEL  = PAW_PBE C 08Apr2002
    TITEL  = PAW_PBE Cl 06Sep2000
    TITEL  = PAW_PBE Sc_sv 07Sep2000
```

判读：母体用的是半芯态版本 Zr_sv 与 Sc_sv，普通 Zr/Sc 目录不存在——这就是 No such file or directory 的来源。更重要的是 POTCAR 不能整份复制：VASP 按原子类型的顺序与数量从前往后匹配，part_A 只有 Zr 和 Cl，沿用 4 元素的母体 POTCAR 时第 2 种元素会被识别成 C，价电子数与类型全错；part_B 同理。按片段重组，顺序必须与 POSCAR 一致：

```bash
[<user>@<cluster> cod]$ cat $POT_DIR/Zr_sv/POTCAR $POT_DIR/Cl/POTCAR > part_A/POTCAR

[<user>@<cluster> cod]$ cat $POT_DIR/C/POTCAR $POT_DIR/Sc_sv/POTCAR > part_B/POTCAR

[<user>@<cluster> cod]$ echo "=== part_A POTCAR ==="; grep "TITEL" part_A/POTCAR
[<user>@<cluster> cod]$ echo "=== part_B POTCAR ==="; grep "TITEL" part_B/POTCAR
```

（判据：part_A 应显示 Zr_sv、Cl 两行，part_B 应显示 C、Sc_sv 两行，顺序与各自 POSCAR 一致。）

### 批量提交三个体系

```bash
[<user>@<cluster> cod]$ for dir in AB part_A part_B; do cd $dir; sbatch script_std; cd ..; done

[<user>@<cluster> cod]$ squeue -u <user>
```

三个任务都应处于排队/运行状态。跑完后先验网格再相减：

```bash
[<user>@<cluster> cod]$ head -n 20 AB/CHGCAR

[<user>@<cluster> cod]$ head -n 20 part_A/CHGCAR

[<user>@<cluster> cod]$ head -n 20 part_B/CHGCAR
```

（判据：三份 CHGCAR 结构信息下方的网格行必须同为 28 28 294 / 56 56 588；出现任何不一致，回查 INCAR 的 fixed FFT-grid 段。）

### vaspkit 相减与 VESTA 出图

```bash
[<user>@<cluster> cod]$ vaspkit -task 314
```

按提示依次输入复合体系 AB/CHGCAR、单体 part_A/CHGCAR、单体 part_B/CHGCAR，生成 CHGDIFF.vasp。下载到本地用 VESTA 打开：Properties → Isosurfaces 新建等值面，正值（电荷积累）与负值（电荷耗散）各画一层；先切过界面原子的竖直面看层间转移方向，再切水平面看面内重构。等值面数值从 0.005 e/Å³ 量级起步按体系调（经验值，非本记录实测）。

### 下一步

```text
SCF：AB / part_A / part_B（同盒子同网格）
    ↓
vaspkit -task 314 → CHGDIFF.vasp
    ↓
VESTA 等值面/切面      ← 本页
    ↓
Bader 电荷（原子分配视角，与本页互为定量/定性）
    ↓
ELF（键合定域性视角）
```

一个提醒：Δρ 只在"同构型、同网格、同赝势"下有效。三个体系任一参数漂移（ENCUT、LREAL、赝势版本），图形会出错但往往不像崩溃那样明显——按上面两个判据逐项核对再出图。
