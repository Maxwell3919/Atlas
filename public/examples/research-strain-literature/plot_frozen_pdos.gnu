# Read the published CSV directly; all energies are already relative to each EF.
# Run: gnuplot plot_frozen_pdos.gnu
# Optional: gnuplot -e "energy_window=0.5" plot_frozen_pdos.gnu
if (!exists("datafile")) datafile="frozen_pdos_long.csv"
if (!exists("output_path")) output_path="frozen-pdos-gnuplot.png"
if (!exists("energy_window")) energy_window=2.0
set encoding utf8
set datafile separator comma
# Shared y range from every plotted Sc2C/ZrCl2 trace within the chosen window.
stats datafile using (abs($4)<=energy_window ? $5 : 1/0) nooutput
shared_max=STATS_max
stats datafile using (abs($4)<=energy_window ? $6 : 1/0) nooutput
shared_max=1.08*(shared_max>STATS_max ? shared_max : STATS_max)
set terminal pngcairo enhanced font "DejaVu Sans,12" size 1500,620
set output output_path
set multiplot layout 1,2 margins 0.075,0.97,0.18,0.78 spacing 0.06
set xrange [-energy_window:energy_window]
set yrange [0:shared_max]
set xlabel "Energy relative to each Fermi level (eV)"
set ylabel "Projected DOS (states / eV / simulation cell)"
set grid ytics lc rgb "#dddddd"
set border 3
set tics nomirror
set key top right font ",10"
set arrow 1 from 0,graph 0 to 0,graph 1 nohead dt 2 lc rgb "#777777"
set title "(a) 0% strain | frozen geometry"
plot datafile using 4:(stringcolumn(1) eq "Heterostructure 0%" ? $5 : 1/0) with lines lw 2 lc rgb "#0072b2" title "Sc2C layer", \
 datafile using 4:(stringcolumn(1) eq "Isolated Sc2C 0%" ? $5 : 1/0) with lines lw 2 dt 2 lc rgb "#0072b2" title "matched isolated Sc2C", \
 datafile using 4:(stringcolumn(1) eq "Heterostructure 0%" ? $6 : 1/0) with lines lw 2 lc rgb "#d55e00" title "ZrCl2 layer"
set title "(b) +1.5% strain | frozen geometry"
unset ylabel
plot datafile using 4:(stringcolumn(1) eq "Heterostructure +1.5%" ? $5 : 1/0) with lines lw 2 lc rgb "#0072b2" title "Sc2C layer", \
 datafile using 4:(stringcolumn(1) eq "Isolated Sc2C +1.5%" ? $5 : 1/0) with lines lw 2 dt 2 lc rgb "#0072b2" title "matched isolated Sc2C", \
 datafile using 4:(stringcolumn(1) eq "Heterostructure +1.5%" ? $6 : 1/0) with lines lw 2 lc rgb "#d55e00" title "ZrCl2 layer"
unset multiplot
print sprintf("Read column4 and layer columns5/6 without resampling; |E-EF|<=%.2f eV; shared_ymax=%.8f", energy_window,shared_max)
