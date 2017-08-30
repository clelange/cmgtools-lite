#!/bin/bash
for i in `ls combined*.root`; do
  dir="run_${i%.*}"
  echo "Merging for dir ${dir}"
  cd $dir || exit
  find higgsCombineTest.Asymptotic.* -size +1500c |xargs hadd -f limits.root
  cd ..
done
