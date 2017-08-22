#!/bin/bash
for i in `ls combined*.root`; do
  dir="run_${i%.*}"
  mkdir $dir
  cd $dir || exit
  ln -s ../$i combined.root
  cd ..
done
