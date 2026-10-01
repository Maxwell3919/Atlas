# Run beside al-sigma010-spectrum.csv: gnuplot plot_al_spectrum.gnuplot
# Actual run: gnuplot 6.0 patchlevel 0; input is prepared by prepare_al_spectrum.py from saved raw spectra.
set datafile separator comma
set encoding utf8
if (!exists("export_format")) export_format="svg"
if (export_format eq "png") {
    set terminal pngcairo size 1200,866 font "Liberation Sans,17" enhanced
    set output "al-sigma010-spectrum.png"
} else {
    set terminal svg size 900,650 font "Liberation Sans,14" enhanced
    set output "al-sigma010-spectrum.svg"
}
set multiplot layout 2,1 margins 0.12,0.96,0.11,0.92 spacing 0.0,0.075
set xrange [0:14]
set grid ytics lc rgb '#dddddd'
set border 3
set tics nomirror
set key top left opaque
unset xlabel
set format x ''
set ylabel 'α²F (native QE convention)'
set yrange [0:*]
set label 1 '(a) Saved Al spectra, σ = 0.010 Ry' at graph 0.50,1.08 center
plot 'al-sigma010-spectrum.csv' every ::1 using 1:2 with lines lw 2 lc rgb '#1a1a1a' title 'dense k 32³', \
     '' every ::1 using 1:3 with lines lw 2 lc rgb '#0072b2' title 'dense k 48³'
unset label 1
set format x '%g'
set xlabel 'Frequency (THz)'
set ylabel 'Cumulative λ'
set label 1 '(b) Cumulative coupling on the same frequency axis' at graph 0.50,1.08 center
plot 'al-sigma010-spectrum.csv' every ::1 using 1:4 with lines lw 2 lc rgb '#1a1a1a' title 'dense k 32³', \
     '' every ::1 using 1:5 with lines lw 2 lc rgb '#0072b2' title 'dense k 48³'
unset label 1
unset multiplot
unset output
