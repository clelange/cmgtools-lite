#!/bin/bash
for i in `ls combined*.txt`; do
  ws="${i%.*}.root"
  text2workspace.py $i -o $ws
done
