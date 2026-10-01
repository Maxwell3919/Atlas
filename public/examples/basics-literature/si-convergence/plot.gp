# Exact existing CSV; no smoothing, fitting, interpolation or new DFT.
set datafile separator ','
set encoding utf8
set border linewidth 1
set tics out nomirror
set style line 1 lc rgb '#205493' lw 1.6 pt 7 ps 1.0
set style line 2 lc rgb '#ae3b2d' lw 1.5 dt 2
set style line 3 lc rgb '#237747' lw 1.6 pt 6 ps 1.6
unset key
set logscale y
set yrange [0.001:120]
set ylabel '|E-E(ref)| (meV/atom)'
parameters='ecutwfc ecutrho kmesh'
labels='ecutwfc ecutrho k-mesh'
do for [fmt in 'svg png pdf'] {
 if (fmt eq 'svg') { set terminal svg size 1140,430 enhanced font 'Arial,13' }
 if (fmt eq 'png') { set terminal pngcairo size 1140,430 enhanced font 'DejaVu Sans,13' }
 if (fmt eq 'pdf') { set terminal pdfcairo size 11.4in,4.3in enhanced font 'DejaVu Sans,13' }
 set output 'convergence.'.fmt
 set multiplot layout 1,3 margins 0.08,0.985,0.16,0.82 spacing 0.095,0.04 title 'Si: independent scans; highest measured point in each scan is its reference'
 do for [i=1:3] {
  par=word(parameters,i)
  set xlabel (i<3 ? word(labels,i).' (Ry)' : 'Uniform mesh edge N (N x N x N)')
  set title sprintf('(%s) %s',word('a b c',i),word(labels,i))
  if (i==1) { set xrange [40:80]; set xtics 40,10,80; set ylabel "|E-E(ref)| (meV/atom)" }
  if (i==2) { set xrange [320:640]; set xtics 320,160,640; unset ylabel }
  if (i==3) { set xrange [4:14]; set xtics 4,2,14; unset ylabel }
  set key top right font ',10'
  plot 'convergence.csv' using (strcol(1) eq par && $6>0 ? $3 : 1/0):6 with linespoints ls 1 title 'Sampled residual', \
       1 with lines ls 2 title '1 meV/atom', \
       'convergence.csv' using (strcol(1) eq par && strcol(8) eq 'True' && $6>0 ? $3 : 1/0):6 with points ls 3 title 'Selected'
 }
 unset multiplot
 unset output
}
