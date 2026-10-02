# Run beside the two .dat files written by prepare_snse2_panels.py.
# gnuplot 6.0; existing CSV values, no fitting or additional smoothing.
# Default: SVG. Use gnuplot -e "raster=1" or -e "pdf=1" for other exports.
if (!exists("raster")) raster=0
if (!exists("pdf")) pdf=0
if (pdf) {set terminal pdfcairo enhanced color size 10.8in,5.85in font "DejaVu Sans,14"; set output "snse2-edge-panels.pdf"} else {if (raster) {set terminal pngcairo size 1440,780 font "DejaVu Sans,18"; set output "snse2-edge-panels.png"} else {set terminal svg size 1080,585 font "DejaVu Sans,14"; set output "snse2-edge-panels.svg"}}
set encoding utf8
set multiplot
set border linewidth 1.2
set tics out nomirror
set yrange [-1:1.5]
set ytics -1,0.5,1.5
set lmargin at screen 0.085
set rmargin at screen 0.68
set bmargin at screen 0.15
set tmargin at screen 0.90
set xrange [0:2.574194239014428]
set xtics ("Γ" 0, "M" 0.9422205454845932, "K" 1.486211776671035, "Γ" 2.574194239014428)
set ylabel "E − E_F (eV)"
set xlabel "Γ–M–K–Γ; cumulative distance (Å^{-1})"
unset key
set title "(a) Frozen PBE SnSe₂: path band edges" offset 0,0.5
set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead dt 2 lc rgb "#666666"
set arrow 2 from first 0.9422205454845932, graph 0 to first 0.9422205454845932, graph 1 nohead lc rgb "#dddddd"
set arrow 3 from first 1.486211776671035, graph 0 to first 1.486211776671035, graph 1 nohead lc rgb "#dddddd"
set label 1 "VBM" at 0.23074792714808598,-0.30606177 point pt 7 ps 0.65 offset 1,-0.8
set label 2 "CBM" at 0.9422205454845932,0.45813323 point pt 7 ps 0.65 offset 1,0.8
plot for [n=1:20] "snse2-bands.dat" using 1:(column(n+1)) with lines lw 1.5 lc rgb "#303438"
unset label
unset arrow 2
unset arrow 3
set lmargin at screen 0.735
set rmargin at screen 0.965
unset ylabel
set format y ""
set xrange [0:8]
set xtics 0,2,8
set xlabel "DOS (states/eV/cell)"
set title "(b) Uniform 18×18×1" offset 0,0.5
set key at graph 0.98,0.97 right top font ",11" spacing 0.8 samplen 1.3 opaque
plot "snse2-pdos.dat" using 1:4 with linespoints pt 7 ps 0.22 lw 1.5 lc rgb "#6c737b" title "TDOS", \
     "snse2-pdos.dat" using 2:4 with linespoints pt 7 ps 0.22 lw 1.5 lc rgb "#b83f47" title "Sn-s", \
     "snse2-pdos.dat" using 3:4 with linespoints pt 7 ps 0.22 lw 1.5 lc rgb "#7654a7" title "Se-p (2 atoms)"
unset multiplot
unset output
