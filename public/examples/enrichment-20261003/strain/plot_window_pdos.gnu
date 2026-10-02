# gnuplot 6.0; direct published CSV, piecewise-linear sample connections.
# Run beside frozen_pdos_long.csv: gnuplot plot_window_pdos.gnu
if (!exists("datafile")) datafile="frozen_pdos_long.csv"
if (!exists("output_base")) output_base="pdos-window"
set encoding utf8
set datafile separator comma
stats datafile using (abs($4)<=0.5 ? $5 : 1/0) nooutput
shared_max=STATS_max
stats datafile using (abs($4)<=0.5 ? $6 : 1/0) nooutput
shared_max=1.08*(shared_max>STATS_max ? shared_max : STATS_max)
do for [format_index=1:2] {
    if (format_index==1) {
        set terminal pngcairo enhanced font "DejaVu Sans,12" size 1500,620
        set output output_base.".png"
    } else {
        set terminal svg enhanced font "DejaVu Sans,12" size 1500,620
        set output output_base.".svg"
    }
    set multiplot layout 1,2 margins 0.075,0.97,0.18,0.78 spacing 0.06
    set xrange [-0.5:0.5]
    set yrange [0:shared_max]
    set xlabel "Energy relative to each Fermi level (eV)"
    set ylabel "Projected DOS (states / eV / simulation cell)"
    set grid ytics lc rgb "#dddddd"
    set border 3
    set tics nomirror
    set key top right font ",10"
    set object 1 rect from -0.1,graph 0 to 0.1,graph 1 behind \
        fc rgb "#777777" fs transparent solid 0.10 noborder
    set arrow 1 from 0,graph 0 to 0,graph 1 nohead dt 2 lc rgb "#777777"
    set arrow 2 from -0.1,graph 0 to -0.1,graph 1 nohead dt 3 lc rgb "#aaaaaa"
    set arrow 3 from 0.1,graph 0 to 0.1,graph 1 nohead dt 3 lc rgb "#aaaaaa"
    set label 1 "integrated window" at 0,graph 0.95 center font ",10" tc rgb "#555555"
    set title "(a) 0% strain | frozen geometry"
    plot datafile using 4:(stringcolumn(1) eq "Heterostructure 0%" ? $5 : 1/0) \
        with lines lw 2 lc rgb "#0072b2" title "Sc2C layer", \
      datafile using 4:(stringcolumn(1) eq "Isolated Sc2C 0%" ? $5 : 1/0) \
        with lines lw 2 dt 2 lc rgb "#0072b2" title "matched isolated Sc2C", \
      datafile using 4:(stringcolumn(1) eq "Heterostructure 0%" ? $6 : 1/0) \
        with lines lw 2 lc rgb "#d55e00" title "ZrCl2 layer"
    set title "(b) +1.5% strain | frozen geometry"
    unset ylabel
    plot datafile using 4:(stringcolumn(1) eq "Heterostructure +1.5%" ? $5 : 1/0) \
        with lines lw 2 lc rgb "#0072b2" title "Sc2C layer", \
      datafile using 4:(stringcolumn(1) eq "Isolated Sc2C +1.5%" ? $5 : 1/0) \
        with lines lw 2 dt 2 lc rgb "#0072b2" title "matched isolated Sc2C", \
      datafile using 4:(stringcolumn(1) eq "Heterostructure +1.5%" ? $6 : 1/0) \
        with lines lw 2 lc rgb "#d55e00" title "ZrCl2 layer"
    unset multiplot
    unset output
}
print sprintf("Original CSV, common y range 0..%.8f; window +/-0.1 eV; PNG/SVG written.",shared_max)
