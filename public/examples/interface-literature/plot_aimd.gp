# Use energy_sample_time_fs, not position_time_fs.
if (!exists("data_root")) data_root = "."
if (!exists("out_root")) out_root = "."
coarse = data_root."/aimd/nve-dt20-nosym/thermo.csv"
fine = data_root."/aimd/nve-dt10-nosym/thermo.csv"
set encoding utf8
set datafile separator ","
set datafile columnheaders
stats fine using ($1==1 ? $5 : 1/0) nooutput
p0 = STATS_mean
stats fine using ($1==1 ? $6 : 1/0) nooutput
k0 = STATS_mean
conv = 13.605693122994*1000/8
set border 3
set tics out nomirror
set key top left
do for [ext in "svg png pdf"] {
    if (ext eq "svg") { set terminal svg size 1000,400 enhanced font "DejaVu Sans,11" }
    if (ext eq "png") { set terminal pngcairo size 1000,400 enhanced font "DejaVu Sans,11" }
    if (ext eq "pdf") { set terminal pdfcairo size 10,4 enhanced font "DejaVu Sans,11" }
    set output out_root."/al-nve-gnuplot.".ext
    set size 1,1
    set origin 0,0
    unset title
    set multiplot layout 1,2 margins 0.11,0.98,0.18,0.82 spacing 0.14,0.05 title "8-atom Al | existing short NVE records"
    set title "(a) 50 matched energy times"
    set xlabel "Energy sample time (fs)"
    set ylabel "Change of total energy (meV/atom)"
    set xrange [0:47.4101328]
    set yrange [-0.002:0.022]
    plot coarse using 2:11 with linespoints pt 7 ps 0.3 lw 1 lc rgb "#D55E00" title "dt = 0.967554 fs", fine every 2 using 2:11 with linespoints pt 5 ps 0.3 lw 1 lc rgb "#CC79A7" title "dt = 0.483777 fs"
    set title "(b) Energy exchange, fine step"
    set ylabel "Change from first sample (meV/atom)"
    set xrange [0:47.8939097]
    set yrange [*:*]
    plot fine using 2:(($5-p0)*conv) with lines lw 1 lc rgb "#009E73" title "Potential", fine using 2:(($6-k0)*conv) with lines lw 1 lc rgb "#D55E00" title "Kinetic"
    unset multiplot
    unset output
}
print "Wrote al-nve-gnuplot.svg/.png/.pdf; panel (a) uses 50 shared energy times"
