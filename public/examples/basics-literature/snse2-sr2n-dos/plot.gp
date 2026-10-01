# Existing total DOS of the six-atom SnSe2/Sr2N cell, ISPIN=1.
# Column 2 already subtracts this calculation's EF; never subtract EF again.
set datafile separator ','
set encoding utf8
set border linewidth 1
set tics out nomirror
set xlabel 'Energy E-E_F (eV)'
set ylabel 'Total DOS (states/eV/cell)'
set xrange [-2:2]
set yrange [0:*]
set style line 1 lc rgb '#205493' lw 1.6 pt 7 ps 0.65
set arrow 1 from 0,graph 0 to 0,graph 1 nohead lc rgb '#777777' dt 2
set label 1 'E_F' at 0.06,graph 0.93 textcolor rgb '#555555'
unset title
set key top right
unset label 2
do for [fmt in 'svg png pdf'] {
 if (fmt eq 'svg') { set terminal svg size 940,460 enhanced font 'Arial,13' }
 if (fmt eq 'png') { set terminal pngcairo size 940,460 enhanced font 'DejaVu Sans,13' }
 if (fmt eq 'pdf') { set terminal pdfcairo size 9.4in,4.6in enhanced font 'DejaVu Sans,13' }
 set output 'total-dos.'.fmt
 plot 'total-dos.csv' using 2:3 with linespoints ls 1 title 'SnSe_{2}/Sr_{2}N'
 unset output
}
