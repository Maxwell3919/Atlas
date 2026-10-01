# Run from the extracted al/ directory: gnuplot plot_nesting.gnu
if (!exists("data_root")) data_root="."
if (!exists("output_path")) output_path="fermi-nesting-gnuplot.png"
set encoding utf8
set datafile separator comma
file(n,s)=sprintf("%s/fermi/k%d-cg/nesting-GX-s%.2f.csv",data_root,n,s)
set terminal pngcairo enhanced font "DejaVu Sans,12" size 1500,600
set output output_path
set multiplot layout 1,2 margins 0.075,0.98,0.17,0.83 spacing 0.10
set xrange [0:0.5]
set yrange [0:*]
set xlabel "q = t(b_1+b_3), Gamma to X"
set grid ytics lc rgb "#dddddd"
set tics nomirror
set key top right font ",10"
set title "(a) Absolute joint weight"
set ylabel "J(q) (eV^{-2})"
plot file(24,0.10) using 1:2 with linespoints lw 1.5 pt 7 ps 0.55 lc rgb "#0072b2" title "24^3, sigma=0.10 eV", \
 file(24,0.20) using 1:2 with linespoints lw 1.5 pt 5 ps 0.55 lc rgb "#d55e00" title "24^3, sigma=0.20 eV", \
 file(32,0.10) using 1:2 with linespoints lw 1.5 pt 9 ps 0.55 lc rgb "#009e73" title "32^3, sigma=0.10 eV", \
 file(32,0.20) using 1:2 with linespoints lw 1.5 pt 11 ps 0.55 lc rgb "#cc79a7" title "32^3, sigma=0.20 eV"
set title "(b) Shape normalized to q=0"
set ylabel "J(q) / J(0)"
plot file(24,0.10) using 1:3 with linespoints lw 1.5 pt 7 ps 0.55 lc rgb "#0072b2" title "24^3, sigma=0.10 eV", \
 file(24,0.20) using 1:3 with linespoints lw 1.5 pt 5 ps 0.55 lc rgb "#d55e00" title "24^3, sigma=0.20 eV", \
 file(32,0.10) using 1:3 with linespoints lw 1.5 pt 9 ps 0.55 lc rgb "#009e73" title "32^3, sigma=0.10 eV", \
 file(32,0.20) using 1:3 with linespoints lw 1.5 pt 11 ps 0.55 lc rgb "#cc79a7" title "32^3, sigma=0.20 eV"
unset multiplot
print "Read the four original CSVs; no interpolation, smoothing or peak normalization beyond stored column3 J/J(0)."
