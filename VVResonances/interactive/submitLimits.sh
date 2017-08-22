#!/bin/bash
STEPSIZE=50
bjobs || exit
for i in `ls combined*.root`; do
  dir="run_${i%.*}"
  cd $dir || exit
  vvSubmitLimits.py combined.root -s $STEPSIZE -q 8nh -m 1000 -M 4500 -o "-M Asymptotic --rAbsAcc=0.00001"
  cd ..
done
