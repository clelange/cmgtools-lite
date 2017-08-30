#!/bin/bash
for i in `ls combined*.root`; do
  dir="run_${i%.*}"
  echo "Creating limit plots for dir ${dir}"
  cd $dir || exit
  vvMakeLimitPlot.py limits.root -x 800 -X 4500 --period 2016
  cd ..
done
