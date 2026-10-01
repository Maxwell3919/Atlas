# Native gnuplot replay of the existing H2 plane-average/integration table.
# CSV: z_A,delta_n_e_A3,linear_e_A,cumulative_e. No smoothing or fitting.
# Put this script in public/examples/charge-literature and run gnuplot.
if (!exists("datafile")) datafile = "../charge-planar/h2-half-spaces/planar.csv"
if (!exists("prefix")) prefix = "h2-planar-and-cumulative"
set datafile separator comma
set encoding utf8
set border 3 back lc rgb "#555555" lw 1
set tics nomirror out scale 0.55
set style fill solid 0.35 noborder
set xrange [0:10]
set key at graph 0.98,0.95 right top horizontal font ",10"
set grid ytics lc rgb "#dddddd" lw 0.5
set format y "%.2f"
set arrow 1 from 4.63, graph 0 to 4.63, graph 1 nohead dt 3 lw 1 lc rgb "#777777" back
set arrow 2 from 5.37, graph 0 to 5.37, graph 1 nohead dt 3 lw 1 lc rgb "#777777" back
set arrow 3 from 5.0, graph 0 to 5.0, graph 1 nohead dt 2 lw 1 lc rgb "#444444" back
set arrow 4 from graph 0, first 0 to graph 1, first 0 nohead lw 0.8 lc rgb "#333333" back
# Three exports use the same measured table and plotting settings.
do for [export_index=1:3] {
 if (export_index==1) { set terminal svg size 1000,700 font "Liberation Sans,15"; set output prefix.".svg" }
 if (export_index==2) { set terminal pdfcairo enhanced color size 7.0in,4.9in font "Liberation Sans,10.5"; set output prefix.".pdf" }
 if (export_index==3) { set terminal pngcairo size 1000,700 font "Liberation Sans,15"; set output prefix.".png" }
 set multiplot layout 2,1 margins 0.13,0.97,0.12,0.86 spacing 0.10 title "Frozen H₂: planar redistribution and cumulative integral" font ",17"
 set ylabel "Area-integrated Δn (e/Å)" offset 0.4,0
 set format x ""
 set xlabel ""
 set label 1 "(a) S × plane-average Δn" at graph 0.02,0.90 front font ",11"
 plot datafile every ::1 using 1:3 with filledcurves above y1=0 lc rgb "#d8a126" title "electron gain", \
      datafile every ::1 using 1:3 with filledcurves below y1=0 lc rgb "#31a9bd" title "electron depletion", \
      datafile every ::1 using 1:3 with lines lw 1.8 lc rgb "#333333" notitle
 unset label 1
 set key off
 set format x "%g"
 set xlabel "z (Å); dotted: H at 4.63 / 5.37 Å, dashed: half-cell boundary at 5 Å"
 set ylabel "T(z) (e)" offset 0.4,0
 set label 2 "(b) Integral from cell origin to z" at graph 0.02,0.90 front font ",11"
 plot datafile every ::1 using 1:4 with lines lw 2 lc rgb "#205a83" notitle
 unset label 2
 unset multiplot
 unset output
 set key at graph 0.98,0.95 right top horizontal font ",10"
}
