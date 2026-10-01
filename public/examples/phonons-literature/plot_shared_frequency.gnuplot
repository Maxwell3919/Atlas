# Run from the extracted phonons-literature directory with gnuplot 6.
# Only saved data are read; no frequency smoothing or DOS normalization.
if (!exists("public_root")) public_root = "./public"
if (!exists("output_base")) output_base = "./zrcl2-sc2c-shared-frequency"
bands = public_root . "/examples/zrcl2-sc2c/ph64/zrclscc.freq.gp"
dos = public_root . "/examples/phonons-interface-projections/zrcl2-sc2c-grouped.csv"
cm_per_thz = 33.3564095198152
set datafile separator whitespace
stats bands using 1 every ::0::0 nooutput
xg = STATS_min
stats bands using 1 every ::50::50 nooutput
xm = STATS_min
stats bands using 1 every ::100::100 nooutput
xk = STATS_min
stats bands using 1 every ::150::150 nooutput
xend = STATS_min
set datafile separator ","
stats dos using 2 skip 1 nooutput
dosmax = STATS_max
set encoding utf8
set border linewidth 1
set tics out nomirror
set style line 1 linecolor rgb "#202020" linewidth 1.1
set style line 2 linecolor rgb "#0072b2" linewidth 1.8
set style line 3 linecolor rgb "#009e73" linewidth 1.8
set style line 4 linecolor rgb "#d55e00" linewidth 1.5 dashtype 2
do for [fmt in "svg pdf"] {
    if (fmt eq "svg") { set terminal svg size 1000,550 enhanced font "DejaVu Sans,14" }
    if (fmt eq "pdf") { set terminal pdfcairo size 10in,5.5in enhanced font "DejaVu Sans,12" }
    set output output_base . "." . fmt
    set multiplot
    set size 0.64,1
    set origin 0,0
    set lmargin at screen 0.08
    set rmargin at screen 0.61
    set bmargin at screen 0.16
    set tmargin at screen 0.90
    set title "Archived ph64: dispersion"
    set ylabel "Frequency (THz)"
    set xlabel "q path"
    set yrange [-0.25:18]
    set xrange [xg:xend]
    set format y "%g"
    set ytics 0,3,18
    set xtics ("Γ" xg, "M" xm, "K" xk, "Γ" xend)
    set key off
    set arrow 1 from xm,-0.25 to xm,18 nohead linecolor rgb "#cccccc"
    set arrow 2 from xk,-0.25 to xk,18 nohead linecolor rgb "#cccccc"
    set arrow 3 from xg,0 to xend,0 nohead linecolor rgb "#999999" dashtype 2
    set datafile separator whitespace
    plot for [mode=2:19] bands using 1:(column(mode)/cm_per_thz) with lines linestyle 1
    unset arrow
    set size 0.36,1
    set origin 0.64,0
    set lmargin at screen 0.66
    set rmargin at screen 0.98
    set bmargin at screen 0.16
    set tmargin at screen 0.90
    set title "Saved PHDOS projections"
    unset ylabel
    set xlabel "PHDOS (states/THz)"
    set xrange [0:1.08*dosmax]
    set yrange [-0.25:18]
    set xtics autofreq
    set format y ""
    set key top right font ",10"
    set datafile separator ","
    plot dos using 2:1 skip 1 with lines linestyle 1 title "Total", \
         dos using 7:1 skip 1 with lines linestyle 2 title "ZrCl_{2}", \
         dos using 8:1 skip 1 with lines linestyle 3 title "Sc_{2}C", \
         dos using 4:1 skip 1 with lines linestyle 4 title "C inside Sc_{2}C"
    unset multiplot
    unset output
}
print sprintf("q nodes from original rows 0/50/100/150: %.6f %.6f %.6f %.6f", xg,xm,xk,xend)
print "Saved PHDOS integral is 18.52393348 (target 18); data kept unnormalized."
