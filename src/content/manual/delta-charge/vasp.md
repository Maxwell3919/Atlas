参考：

- [VASP：CHGCAR 的结构与网格](https://vasp.at/wiki/CHGCAR)
- [VASPKIT：两个片段的差分电荷](https://vaspkit.com/tutorials.html#charge-density-difference)
- [VESTA 官方手册：VASP 体数据与等值面](https://jp-minerals.org/vesta/archives/VESTA_Manual.pdf)

## 把两层放在一起，电子密度在哪里改变了？

这里比较同一构型的三份电子密度：完整异质结 AB、只保留上面一层的 A、只保留下面一层的 B。计算的是

```text
Δn(r) = n_AB(r) − n_A(r) − n_B(r)
```

Δn 为正表示这个位置的电子密度增加，为负表示减少。它描述相对于两个冻结片段的空间重排；仅凭正负等值面的形状，还不能读出某一层净转移了多少电子。

本例是 Sc₂C/ZrCl₂，原子顺序为 `Zr C Cl Sc`，个数为 `1 1 2 2`。A 取 ZrCl₂，B 取 Sc₂C。三份计算必须保留相同晶胞、相同坐标原点，以及片段在 AB 中原本的位置。删掉另一层之后，不再移动剩下的原子，否则减出来的密度还会混入几何变化。

### 先读晶胞和网格，再拆结构

保存的母体 SCF 读取记录是：

```text
[bcgong@localhost cod]$ grep -n "dimension x,y,z" ../scf/OUTCAR
515:   dimension x,y,z NGX =    28 NGY =   28 NGZ =  294
516:   dimension x,y,z NGXF=    56 NGYF=   56 NGZF=  588
```

这是两套 FFT 网格。`NGX/NGY/NGZ` 是粗网格；CHGCAR 中写出的电子密度使用 `NGXF/NGYF/NGZF` 的细网格。本例三份 CHGCAR 的密度网格都应当是 **56×56×588**，共有 **1,843,968** 个网格值。不能将 28×28×294 和 56×56×588 当作两种都能接受的 CHGCAR 尺寸。

母体结构头部留下了另一条重要信息：

```text
[bcgong@localhost cod]$ head -n 10 ../scf/CONTCAR
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

标题虽然写着 `Sc2C`，元素行却明确包含 Zr、C、Cl、Sc，因此不能靠第一行标题识别材料。这里没有 `Selective dynamics` 行，坐标从第 9 行开始；这份文件的原子编号与拆分方式为：

| AB 中的原子编号 | 元素 | 保留在哪个片段 |
|---|---|---|
| 1 | Zr | A |
| 2 | C | B |
| 3、4 | Cl | A |
| 5、6 | Sc | B |

整理自己的文件时，先复制再在 `vi` 中删掉另一组原子的坐标，保留晶胞和剩余坐标原值。下面是这种手动整理的命令写法，保存后用 `cat` 逐行核对：

```bash
mkdir -p AB part_A part_B
cp ../scf/CONTCAR AB/POSCAR
cp AB/POSCAR part_A/POSCAR
cp AB/POSCAR part_B/POSCAR
vi part_A/POSCAR
cat part_A/POSCAR
vi part_B/POSCAR
cat part_B/POSCAR
```

A 的元素与个数应改成 `Zr Cl`、`1 2`，只留 Zr 和两个 Cl 的三行坐标；B 改成 `C Sc`、`1 2`，只留 C 和两个 Sc。晶胞仍是原来的三条矢量。换成有选择性约束、速度块或不同原子顺序的 POSCAR 时，坐标行号会变，不能照着旧行号剪切。

### POTCAR 要跟着元素顺序一起拆

原记录中曾直接寻找普通 `Zr` 目录，得到文件不存在的错误。继续读取母体 POTCAR 的标识，才确认实际使用的是半芯态版本：

```text
[bcgong@localhost cod]$ grep "TITEL" ../scf/POTCAR
    TITEL  = PAW_PBE Zr_sv 04Jan2005
    TITEL  = PAW_PBE C 08Apr2002
    TITEL  = PAW_PBE Cl 06Sep2000
    TITEL  = PAW_PBE Sc_sv 07Sep2000
```

因此 AB 可以复制母体 POTCAR；A 要按 `Zr_sv → Cl` 拼接，B 按 `C → Sc_sv` 拼接。原子个数不会决定 POTCAR 中重复多少份势，**原子类型的顺序**才决定各数据集怎样匹配 POSCAR。

```bash
cp ../scf/POTCAR AB/POTCAR
POT_DIR="<赝势库路径>"
cat "$POT_DIR/Zr_sv/POTCAR" "$POT_DIR/Cl/POTCAR" > part_A/POTCAR
cat "$POT_DIR/C/POTCAR" "$POT_DIR/Sc_sv/POTCAR" > part_B/POTCAR
grep TITEL part_A/POTCAR
grep TITEL part_B/POTCAR
```

最后两条命令应分别核对到 `Zr_sv、Cl` 和 `C、Sc_sv`。这里只展示技术标识，不公开 POTCAR 数据本体。若计算中手动设过 `NELECT`，拆分后还要核对片段的电荷状态；不能把完整体系的 `NELECT` 原样留在少了原子的片段里。

### 固定几何，分别得到三份自洽密度

本例保存的 [INCAR 记录](/Atlas/examples/sc2c-zrcl2-charge/INCAR.record.txt) 中，关键设置如下：

```ini
IBRION = -1
NSW = 0
ENCUT = 520
EDIFF = 1E-6
NELM = 160
LCHARG = .TRUE.
LWAVE = .FALSE.
LREAL = A
LASPH = .TRUE.
PREC = Accurate
ISMEAR = 0
SIGMA = 0.05
NGX = 28
NGY = 28
NGZ = 294
NGXF = 56
NGYF = 56
NGZF = 588
```

`IBRION=-1` 与 `NSW=0` 固定原子位置；`LCHARG` 写出 CHGCAR；这份输入关闭了 WAVECAR 输出，因此结束后没有 WAVECAR 本身不是异常。三份计算沿用相同的截断能、k 点网格、泛函、展宽和对应元素的赝势。显式固定 FFT 尺寸是为了让减法在同一空间网格上进行，仍需从输出核对实际使用的网格。

准备输入时可以逐个目录复制并查看：

```bash
cp INCAR AB/INCAR
cp INCAR part_A/INCAR
cp INCAR part_B/INCAR
cp ../scf/KPOINTS AB/KPOINTS
cp ../scf/KPOINTS part_A/KPOINTS
cp ../scf/KPOINTS part_B/KPOINTS
cat AB/INCAR
cat AB/KPOINTS
```

提交脚本沿用已在该主机核验的 `script_std`。保存的资料没有脚本全文和这三次任务的完成摘要，所以这里不列新的任务号，也不把排队命令当作计算已经通过。实际提交后，在对应目录用 `tail -f OSZICAR` 观察电子迭代，用 `tail -n 40 OUTCAR` 查看最新结果，再检查调度器日志。

一次静态 VASP 计算的文件可以这样读：

| 文件 | 在这个步骤看什么 |
|---|---|
| `OUTCAR` | 开头的实际输入、元素与电子数、FFT 网格；中间的电子迭代、能量、力；末尾的运行与计时信息 |
| `OSZICAR` | 电子步能量变化的摘要，查看是否因达到 `NELM` 上限而停下 |
| `CHGCAR` | 结构头、细 FFT 网格和密度数据，是下一步相减的输入 |
| `CONTCAR` | 本次输出结构；静态任务中出现它并不能证明做过结构优化 |
| `WAVECAR` | 波函数重启文件；本例 `LWAVE=.FALSE.` 不要求生成它 |

可以从这些位置开始查，A、B、AB 分别检查：

```bash
head -n 80 OUTCAR
grep -E 'NELECT|NGXF|NGYF|NGZF' OUTCAR
tail -n 20 OSZICAR
tail -n 40 OUTCAR
```

末尾有计时信息说明程序走到了结束段，电子步也必须满足本次的收敛条件。对于这里定义的中性冻结片段，还应有 `NELECT(AB) = NELECT(A) + NELECT(B)`。这保证三份密度的总电子数彼此配平；随后 Δn 在全晶胞的积分应接近零，而不是靠更换等值面把不平衡掩盖掉。

### 在 CHGCAR 里找到真正要相减的数据块

先用 `head -n 20 AB/CHGCAR` 和两个片段的同类命令查看文件开头。不同原子数会让网格行落在不同行，不能固定抓同一个行号。文件布局可以按下面的顺序辨认：

```text
POSCAR 格式的晶胞、元素、个数与原子坐标
    ↓ 空行
NGXF  NGYF  NGZF
    ↓
第一块：NGXF×NGYF×NGZF 个总电子密度网格值
    ↓
PAW augmentation occupancies
```

这里三份文件的网格行都应是 `56 56 588`。密度数据一行可以有多个数，直到第一块的 1,843,968 个值读完；它们之后的 PAW 信息不是新的空间网格。自旋极化计算还可能有后续磁化密度块，不能把它们与第一块总电子密度混在一起。

同时看晶胞矢量是否一致。仅仅有相同的 `56 56 588` 不够：若晶胞尺寸或原点不同，同一个数组下标对应的实空间位置就不同，逐点相减没有意义。

### 用 VASPKIT 相减，然后在 VESTA 中保留单位

三份 SCF 与网格核对完成后运行：

```bash
vaspkit -task 314
```

按当前 VASPKIT 官方教程，出现文件名输入提示时，把三个文件名放在**同一行，以空格分隔**：

```text
AB/CHGCAR part_A/CHGCAR part_B/CHGCAR
```

顺序表示 `AB − A − B`，结果文件名为 `CHGDIFF.vasp`。以上是命令与输入方式；现有记录没有收录本例的 VASPKIT 完整结束输出、密度积分或最终 VESTA 工程，因而这里不附一张无法核对来源的等值面图。

在本机打开 `CHGDIFF.vasp` 后，先核对晶胞和两层原子的相对位置，再进入 `Properties → Isosurfaces`，建立数值绝对值相同的一正一负两层等值面。给两者使用不同颜色，并在图注写明哪一色代表电子增加、哪一色代表电子减少。侧视界面时保持两层都在显示范围内；只看一个剪裁很窄的区域，容易把层内重排看成层间转移。

**等值面数值必须带上实际单位。** VESTA 手册说明，直接读取 VASP CHG/CHGCAR 类文件时，会用以 bohr³ 计的晶胞体积归一化，密度单位为 bohr⁻³。若想表达 `0.005 e/Å³`，换成相应数值约为 `0.000741 bohr⁻³`；不能在界面里输入 0.005 后直接把图注写成 e/Å³。处理过的 `.vasp` 文件也应核对其写出约定和导入方式。

保存图片的同时保存 `.vesta` 工程，留下输入文件、正负等值面数值、单位、颜色与视角。以后更换体系时，先比较这些设置，再比较等值面大小。

下一步：需要原子或层的净电子转移，进入[Bader 电荷](/Atlas/m/bader/vasp/)；希望结合局域成键特征理解同一界面，继续看[ELF](/Atlas/m/elf/vasp/)。

```text
同一 AB 几何 → 保持晶胞与原位坐标，拆成 A / B
                     ↓
            三份 SCF → 电子数、收敛与细网格检查
                     ↓
            AB − A − B → 密度积分与 VESTA 单位检查
                     ↓
                等值面图 → Bader / ELF
```
