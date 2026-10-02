# Run beside al-sigma010-compensation.csv; gnuplot 6.0, no Python plotting.
# export_format="svg" (default), "png", or "pdf".
set datafile separator comma
set encoding utf8
if (!exists("export_format")) export_format="svg"
if (export_format eq "png") {
    set terminal pngcairo size 1300,760 font "Liberation Sans,19" enhanced
    set output "al-sigma010-compensation.png"
} else {
    if (export_format eq "pdf") {
        set terminal pdfcairo size 18.3cm,10.7cm font "Liberation Sans,11" enhanced
        set output "al-sigma010-compensation.pdf"
    } else {
        set terminal svg size 1000,585 font "Liberation Sans,16" enhanced
        set output "al-sigma010-compensation.svg"
    }
}
set lmargin at screen 0.13
set rmargin at screen 0.97
set bmargin at screen 0.14
set tmargin at screen 0.92
set xrange [0:14]
set yrange [-0.025:0.036]
set xlabel 'Frequency (THz)'
set ylabel 'Accumulated coupling difference'
set border 3
set tics nomirror
set grid ytics lc rgb '#dddddd'
set key top left opaque font ',15' spacing 1.2
set label 1 'Al: dense k 32³ vs 48³, σ = 0.010 Ry' at screen 0.55,0.966 center
set arrow 1 from graph 0,first 0 to graph 1,first 0 nohead dt 3 lw 1 lc rgb '#777777'
plot 'al-sigma010-compensation.csv' every ::1 using 1:5 with lines lw 2.4 lc rgb '#1a1a1a' title 'P: cumulative positive part', \
     '' every ::1 using 1:6 with lines dt 2 lw 2.4 lc rgb '#0072b2' title 'N: cumulative negative magnitude', \
     '' every ::1 using 1:7 with lines lw 2.8 lc rgb '#d55e00' title 'P − N: signed Δλ (32³ − 48³)'
unset output
