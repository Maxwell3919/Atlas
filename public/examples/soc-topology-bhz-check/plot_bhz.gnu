# Nk2 labels transverse outputs; dense loop integration is adaptive (64/128 final points).
# WT output columns and periodic path; no recomputation or smoothing.
set encoding utf8
set terminal pngcairo enhanced font "DejaVu Sans,12" size 1400,480
set output 'bhz-wcc-edge.png'
set multiplot layout 1,2 margins 0.08,0.88,0.14,0.91 spacing 0.12
set title 'BHZ model | two occupied spinor bands'
set xlabel 'Transverse k_y (fractional)'
set ylabel 'WCC (mod 1)'
set xrange [0:0.5]
set yrange [0:1]
set xtics 0.1
set ytics 0.25
set key top right
plot 'n81-final/wcc.dat' using 1:4 with points pt 7 ps 0.45 lc rgb '#0072b2' title 'Nk2=81', \
 'n81-final/wcc.dat' using 1:5 with points pt 7 ps 0.45 lc rgb '#0072b2' notitle, \
 'n41-final/wcc.dat' using 1:4 with points pt 6 ps 0.7 lc rgb '#d55e00' title 'Nk2=41', \
 'n41-final/wcc.dat' using 1:5 with points pt 6 ps 0.7 lc rgb '#d55e00' notitle
set title 'Semi-infinite y boundary | eta = 0.0374 eV'
unset key
set xlabel 'Conserved k_x (fractional)'
set ylabel 'Energy (eV)'
set xrange [-0.5:0.5]
set yrange [-2.5:2.5]
set xtics 0.25
set ytics 1
set view map
set palette defined (-5 '#194eff', 0 'white', 5 '#d73027')
set cbrange [-5:5]
set cblabel 'ln LDOS (WT output)'
set pm3d map
stats 'n81-final/dos.dat_l' using 1 nooutput
pathmax = STATS_max
splot 'n81-final/dos.dat_l' using ($1/pathmax-0.5):2:3 with pm3d
unset multiplot
