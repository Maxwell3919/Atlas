# Run from sc2c-dos/: gnuplot source/plot_dos.gp
# Col4: exact input energy minus XML EF, eV. Col5: spin-summed DOS, states/eV/cell.
# All 101 rows are plotted as straight segments; no smoothing, rescaling or interpolation.
set datafile separator comma
set encoding utf8
set border 3
set tics nomirror out
set xrange [0:*]
set yrange [-0.5:0.5]
set xlabel "DOS (states / eV / cell, both spins)"
set ylabel "E - E_F (eV)"
set title "Sc_2C: fixed three-atom geometry, NM / no SOC"
set key off
set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead dt 2 lc rgb "#666666"
set label 1 "D(E_F) = 5.433" at first 5.433, first 0 offset 1,1 font ",10"
set terminal svg size 660,700 enhanced font "DejaVu Sans,13"
set output "figures/sc2c-dos.svg"
plot "data/dos_shifted.csv" every ::1 using 5:4 with lines lw 2 lc rgb "#215d96", \
     "data/dos_shifted.csv" every ::1 using (abs($4)<1e-8?$5:1/0):4 with points pt 7 ps 1 lc rgb "#a6422b"
set terminal pdfcairo enhanced color size 5.5in,5.8in font "DejaVu Sans,11"
set output "figures/sc2c-dos.pdf"
replot
unset output
