# Read the accepted CSV; no fit, interpolation, or new energy points.
if (!exists("data_root")) data_root = "."
if (!exists("out_root")) out_root = "."
data = data_root."/exfoliation.csv"
set encoding utf8
set datafile separator ","
set datafile columnheaders
set border 3
set tics out nomirror
set key off
do for [ext in "svg png pdf"] {
    if (ext eq "svg") { set terminal svg size 900,360 enhanced font "DejaVu Sans,11" }
    if (ext eq "png") { set terminal pngcairo size 900,360 enhanced font "DejaVu Sans,11" }
    if (ext eq "pdf") { set terminal pdfcairo size 9,3.6 enhanced font "DejaVu Sans,11" }
    set output out_root."/hfi2-separation-gnuplot.".ext
    set size 1,1
    set origin 0,0
    unset title
    set multiplot layout 1,2 margins 0.08,0.98,0.18,0.83 spacing 0.12,0.05 title "HfI2 | frozen six-layer separation"
    set title "(a) Accepted separation points"
    set xlabel "Top-layer displacement d (Å)"
    set ylabel "[E(d)-E(0)]/A (meV Å^{-2})"
    set xrange [-0.4:20.4]
    set yrange [-0.5:25]
    plot data using 2:6 with linespoints pt 7 ps 0.55 lw 1 lc rgb "#0072B2"
    set title "(b) Large-distance detail"
    set ylabel "E(d)-E(0) (meV/cell)"
    set xrange [11.6:20.4]
    set yrange [*:*]
    plot data using 2:($2>=12 ? $5 : 1/0) with linespoints pt 5 ps 0.55 lw 1 dt 2 lc rgb "#D55E00"
    unset multiplot
    unset output
}
print "Read 20 accepted points; wrote hfi2-separation-gnuplot.svg/.png/.pdf"
