# Existing Al coordinate frames; the pair interval is a geometric range, not uncertainty.
if (!exists("data_root")) data_root = "structure-observations"
if (!exists("out_root")) out_root = data_root
coarse = data_root."/nve-dt20-nosym-structure.csv"
fine = data_root."/nve-dt10-nosym-structure.csv"
set encoding utf8
set datafile separator ","
set datafile columnheaders
stats fine using ($1==0 ? $5 : 1/0) nooutput
r0 = STATS_mean
set border 3
set tics out nomirror
do for [ext in "svg png pdf"] {
    if (ext eq "svg") { set terminal svg size 1100,430 enhanced font "DejaVu Sans,11" }
    if (ext eq "png") { set terminal pngcairo size 1100,430 enhanced font "DejaVu Sans,11" }
    if (ext eq "pdf") { set terminal pdfcairo size 11,4.3 enhanced font "DejaVu Sans,11" }
    set output out_root."/al-nve-structure.".ext
    set size 1,1
    set origin 0,0
    unset title
    set multiplot layout 1,2 margins 0.09,0.98,0.18,0.83 spacing 0.14,0.05 title "8-atom Al | recorded positions, fixed cell"
    set title "(a) Motion from the shared initial frame"
    set xlabel "Coordinate time (fs)"
    set ylabel "RMS displacement (Å)"
    set xrange [0:48.37768653]
    set yrange [0:0.11]
    set key top left
    plot coarse using 1:2 with lines lw 1.5 lc rgb "#D55E00" title "dt = 0.967554 fs", fine using 1:2 with lines dt 2 lw 1.5 lc rgb "#CC79A7" title "dt = 0.483777 fs"
    set title "(b) Initial neighbor pairs, fine step"
    set ylabel "Al-Al pair length (Å)"
    set yrange [*:*]
    set key top left
    set style fill transparent solid 0.2 noborder
    plot fine using 1:3:4 with filledcurves lc rgb "#009E73" title "min-max of 48 pairs", fine using 1:5 with lines lw 1.5 lc rgb "#009E73" title "mean", r0 with lines dt 3 lc rgb "#777777" title "initial distance"
    unset multiplot
    unset output
}
print "Wrote al-nve-structure.svg/.png/.pdf from all recorded coordinate frames"
