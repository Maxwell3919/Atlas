set style data dots
set nokey
set xrange [0: 3.57734]
set yrange [ -6.69922 :  7.38604]
set arrow from  1.16407,  -6.69922 to  1.16407,   7.38604 nohead
set arrow from  1.74610,  -6.69922 to  1.74610,   7.38604 nohead
set arrow from  2.56922,  -6.69922 to  2.56922,   7.38604 nohead
set xtics ("G"  0.00000,"X"  1.16407,"W"  1.74610,"L"  2.56922,"G"  3.57734)
 plot "silicon_band.dat"
