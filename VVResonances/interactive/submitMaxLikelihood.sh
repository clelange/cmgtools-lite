#!/bin/bash
STEPSIZE=50
bjobs || exit
for i in `ls combined*.root`; do
  dir="run_${i%.*}"
  echo "Submitting for dir ${dir}"
  cd $dir || exit
  vvSubmitLimits.py combined.root -s $STEPSIZE -q 8nh -m 800 -M 4500 -o "-M MaxLikelihoodFit"
  cd ..
done
