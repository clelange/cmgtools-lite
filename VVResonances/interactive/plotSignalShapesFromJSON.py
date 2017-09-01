#!/bin/env python
import ROOT
import json
import math
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")

inFileName = "LNUJ_XWW.json"
massPoints = [800, 1000, 1200, 1500, 2000, 2500, 3000, 4000]

def DoubleCrystalBall(x, par):
    """
    mean: par[0]
    sigma: par[1]
    alpha1: par[2]
    alpha2: par[3]
    n1: par[4]
    n2: par[5]
    """
    t = (x[0] - par[0])/par[1]
    if (t > -par[2]) and (t < par[3]):
        return math.exp(-0.5*t*t)
    elif (t < -par[2]):
        A1 = pow(par[4]/abs(par[2]), par[4])*math.exp(-par[2]*par[2]/2)
        B1 = par[4]/abs(par[2])-abs(par[2])
        return A1*pow(B1-t, -par[4])
    elif (t > par[3]):
        A2 = pow(par[5]/abs(par[3]), par[5])*math.exp(-par[3]*par[3]/2)
        B2 = par[5] / abs(par[3]) - abs(par[3])
        return A2*pow(B2+t, -par[5])
    else:
        print "ERROR evaluating range..."
        return 99


def main():
    with open(inFileName) as jsonFile:
        j = json.load(jsonFile)

    c1 = ROOT.TCanvas("c1", "c1", 800, 600)
    c1.Draw()
    firstPoint = True
    graphs = []
    leg = ROOT.TLegend(0.8, 0.2, 0.95, 0.8)

    for i, MH in enumerate(massPoints):  # mind that MH is evaluated below
        # if not firstPoint:
        #     continue
        pdfName = "signal_%d" % MH
        mean = eval(j['MEAN'])
        sigma = eval(j['SIGMA'])
        alpha1 = eval(j['ALPHA1'])
        alpha2 = eval(j['ALPHA2'])
        n1 = eval(j['N1'])
        n2 = eval(j['N2'])
        doubleCB = ROOT.TF1(pdfName, DoubleCrystalBall,  0,  7000, 6)
        doubleCB.SetParameters(mean, sigma, alpha1, alpha2, n1, n2)
        doubleCB.SetLineColor(i+1)
        leg.AddEntry(doubleCB, "%d GeV" % MH, "L")
        if firstPoint:
            doubleCB.Draw()
            firstPoint = False
            doubleCB.GetXaxis().SetTitle("m_{X} (GeV)")
            doubleCB.GetYaxis().SetTitle("arbitrary units")
        else:
            doubleCB.Draw("SAME")
        graphs.append(doubleCB)
    leg.Draw()
    c1.SaveAs("signalShapes_%s.png" % inFileName.rsplit(".", 1)[0])


if __name__ == '__main__':
    main()
