#!/bin/bash
echo "combining cards"
combineCards.py  mu_HP_WW_nob_13TeV=datacard_LNUJ_XWW_mu_HP_WW_nob_13TeV.txt mu_HP_WZ_nob_13TeV=datacard_LNUJ_XWW_mu_HP_WZ_nob_13TeV.txt mu_LP_WW_nob_13TeV=datacard_LNUJ_XWW_mu_LP_WW_nob_13TeV.txt mu_LP_WZ_nob_13TeV=datacard_LNUJ_XWW_mu_LP_WZ_nob_13TeV.txt e_HP_WW_nob_13TeV=datacard_LNUJ_XWW_e_HP_WW_nob_13TeV.txt e_HP_WZ_nob_13TeV=datacard_LNUJ_XWW_e_HP_WZ_nob_13TeV.txt e_LP_WW_nob_13TeV=datacard_LNUJ_XWW_e_LP_WW_nob_13TeV.txt e_LP_WZ_nob_13TeV=datacard_LNUJ_XWW_e_LP_WZ_nob_13TeV.txt > combined_XWW.txt

combineCards.py  mu_HP_WW_nob_13TeV=datacard_LNUJ_XWZ_mu_HP_WW_nob_13TeV.txt mu_HP_WZ_nob_13TeV=datacard_LNUJ_XWZ_mu_HP_WZ_nob_13TeV.txt mu_LP_WW_nob_13TeV=datacard_LNUJ_XWZ_mu_LP_WW_nob_13TeV.txt mu_LP_WZ_nob_13TeV=datacard_LNUJ_XWZ_mu_LP_WZ_nob_13TeV.txt e_HP_WW_nob_13TeV=datacard_LNUJ_XWZ_e_HP_WW_nob_13TeV.txt e_HP_WZ_nob_13TeV=datacard_LNUJ_XWZ_e_HP_WZ_nob_13TeV.txt e_LP_WW_nob_13TeV=datacard_LNUJ_XWZ_e_LP_WW_nob_13TeV.txt e_LP_WZ_nob_13TeV=datacard_LNUJ_XWZ_e_LP_WZ_nob_13TeV.txt > combined_XWZ.txt

for i in `ls combined*.txt`; do
  ws="${i%.*}.root"
  text2workspace.py $i -o $ws
done
