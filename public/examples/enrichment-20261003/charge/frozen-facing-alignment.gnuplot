# Actual frozen-layer SCF table; no fitting and no synthetic metal band edges.
# Download band-edges-vacuum-referenced.csv beside this script, then run gnuplot.
if (!exists('datafile')) datafile = 'band-edges-vacuum-referenced.csv'
if (!exists('prefix')) prefix = 'frozen-facing-alignment'
set datafile separator comma
stats datafile using (strcol(1) eq 'snse2' && strcol(2) eq 'lower_z' ? column(7) : 1/0) nooutput
if (STATS_records != 1) { print 'Need exactly one SnSe2 lower-z VBM'; exit error }
vbm = STATS_mean
stats datafile using (strcol(1) eq 'snse2' && strcol(2) eq 'lower_z' ? column(8) : 1/0) nooutput
if (STATS_records != 1) { print 'Need exactly one SnSe2 lower-z CBM'; exit error }
cbm = STATS_mean
stats datafile using (strcol(1) eq 'sr2n' && strcol(2) eq 'upper_z' ? column(6) : 1/0) nooutput
if (STATS_records != 1) { print 'Need exactly one Sr2N upper-z EF'; exit error }
ef = STATS_mean
offset = cbm - ef
set encoding utf8
set border 2 lc rgb '#444444'
set tics nomirror out
set xrange [0.5:2.8]
set yrange [-6.65:0.65]
set ylabel 'Energy relative to the selected vacuum (eV)'
set xtics ('SnSe₂  lower-z' 1, 'Sr₂N  upper-z' 2.2) scale 0
set ytics 1
set key off
set grid ytics lc rgb '#dddddd'
set object 1 rect from 0.75,vbm to 1.25,cbm fc rgb '#e9f0f5' fs solid 1 noborder behind
set arrow 1 from 0.75,vbm to 1.25,vbm nohead lw 3 lc rgb '#205a83'
set arrow 2 from 0.75,cbm to 1.25,cbm nohead lw 3 lc rgb '#205a83'
set arrow 3 from 1.95,ef to 2.45,ef nohead lw 3 lc rgb '#ae542f'
set arrow 4 from 1.60,ef to 1.60,cbm heads size screen 0.012,15 lw 1.3 lc rgb '#555555'
set arrow 5 from 1.27,cbm to 1.60,cbm nohead dt 2 lc rgb '#777777'
set arrow 6 from 1.60,ef to 1.93,ef nohead dt 2 lc rgb '#777777'
set label 1 sprintf('VBM  %.6f',vbm) at 0.78,vbm-0.24 left font ',12'
set label 2 sprintf('CBM  %.6f',cbm) at 0.78,cbm+0.25 left font ',12'
set label 3 sprintf('EF  %.6f',ef) at 2.2,ef+0.25 center font ',12'
set label 4 'CBM − EF' at 1.69,(ef+cbm)/2+0.12 left font ',12'
set label 6 sprintf('= %.6f eV',offset) at 1.69,(ef+cbm)/2-0.18 left font ',12'
set label 5 'Vacuum = 0' at 0.58,0.18 left font ',12'
set title 'Frozen isolated layers before contact' font ',17'
do for [export_index=1:3] {
 if (export_index==1) { set terminal svg size 960,680 font 'Liberation Sans,16'; set output prefix.'.svg' }
 if (export_index==2) { set terminal pdfcairo enhanced color size 7in,5in font 'Liberation Sans,11'; set output prefix.'.pdf' }
 if (export_index==3) { set terminal pngcairo size 960,680 font 'Liberation Sans,16'; set output prefix.'.png' }
 plot 0 with lines lw 1.3 dt 2 lc rgb '#777777' notitle
 unset output
}
print sprintf('VBM=%.9f; CBM=%.9f; Sr2N EF=%.9f; CBM-EF=%.9f eV',vbm,cbm,ef,offset)
