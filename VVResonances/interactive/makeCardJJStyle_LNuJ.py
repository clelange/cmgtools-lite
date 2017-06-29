import ROOT
import os
import sys
from CMGTools.VVResonances.statistics.DataCardMaker import DataCardMaker
from CMGTools.VVResonances.plotting.categories_VV_2016 import findCut, categories
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")

finalState = "LNUJ"
channel = "XWW"

lumi = 35900
leptons = ['mu', 'e']
purities = ['HP', 'LP']
b_categories = ['nob']
bosons = ['WW', 'WZ']


leptons = ['mu', 'e']
purities = ['HP', 'LP']
bCategories = ['nob']
bosons = ['WW', 'WZ']  # this should cut on the jet mass

jetMassString = 'lnujj_l2_softDrop_mass'
resonanceMassString = 'lnujj_LV_mass'

dataTemplate = "SingleMuon,SingleElectron,MET"

minMJJ = 40.0
maxMJJ = 160.0

minMVV = 1000.0
maxMVV = 4500.0

binsMJJ = 60
binsMVV = 200


def makePrefit(sampleTypes, cuts, catName, resonanceMassString, templateDir, logTerm=False):
    sampleTypes = sampleTypes.split(',')
    dataPlotters = []
    for filename in os.listdir(templateDir):
        for sampleType in sampleTypes:
            # print "filename", filename, "sampleType", sampleType
            # return
            if filename.find(sampleType) != -1:
                fnameParts = filename.split('.')
                fname = fnameParts[0]
                ext = fnameParts[1]
                if ext.find("root") == -1:
                    continue
                dataPlotters.append(TreePlotter(templateDir + '/' + fname + '.root', 'tree'))

    data = MergedPlotter(dataPlotters)

    histo = data.drawTH1(resonanceMassString, cuts, "1", binsMVV, minMVV, maxMVV)
    #    if options.zeroNegative:
    #        for i in range(0,int(pbins[0])+2):
    #            if histo.GetBinContent(i)<0:
    #                histo.SetBinContent(i,0.0)
    sqrt_s = 13000
    xRange = [800, 5000]
    nPar = 2
    if logTerm:
        qcdFunc = ROOT.TF1("qcdFunc", "TMath::Power(1-x/{sqrt_s}, [0])/TMath::Power(x/{sqrt_s}, [1]+[2]*TMath::Log(x/{sqrt_s}))".format(sqrt_s=sqrt_s), xRange[0], xRange[1])
        nPar = 3
    else:
        qcdFunc = ROOT.TF1("qcdFunc", "TMath::Power(1-x/{sqrt_s}, [0])/TMath::Power(x/{sqrt_s}, [1])".format(sqrt_s=sqrt_s), xRange[0], xRange[1])
    qcdFunc.SetParameter(0, 4.48531e-07)
    qcdFunc.SetParameter(1, -7.96655e-01)
    if logTerm:
        qcdFunc.SetParameter(2, 7.43952e+00)

    canvas = ROOT.TCanvas("c1", "c1", 800, 600)
    canvas.Draw()
    histo.Fit(qcdFunc)
    fitResult = histo.GetFunction("qcdFunc")
    print "chi2", fitResult.GetChisquare()
    # print "p0", fitResult.GetParameter(0), "+/-", fitResult.GetParError(0)
    # print "p1", fitResult.GetParameter(1), "+/-", fitResult.GetParError(1)
    # print "p2", fitResult.GetParameter(2), "+/-", fitResult.GetParError(2)
    parDict = {}
    for par in range(nPar):
        parDict["p%d" % par] = fitResult.GetParameter(par)
        parDict["e%d" % par] = fitResult.GetParError(par)
    # qcdFunc.Draw()
    canvas.SaveAs("prefit_%s.png" % (catName))
    return parDict


def main():

    templateDir = "samples"
    if len(sys.argv) > 1:
        templateDir = sys.argv[1]
    cmd = 'combineCards.py '

    for lepton in leptons:
        for purity in purities:
            for boson in bosons:
                for categ in b_categories:
                    catName = '_'.join([lepton, purity, boson, categ])
                    card = DataCardMaker(channel, catName, '13TeV', lumi, finalState)
                    cat = '_'.join([catName, '13TeV'])
                    cmd = cmd + " " + cat + '=datacard_{finalState}_{channel}_{cat}.txt'.format(
                        finalState=finalState, channel=channel, cat=cat)

                    # WW signal-MVV
                    # card.addMVVSignalParametricShape(channel, "MVV", "{finalState}_{channel}.json".format(finalState=finalState, channel=channel), {
                    #                                  'CMS_scale_j': 1, 'CMS_scale_MET': 1.0}, {'CMS_res_j': 1.0, 'CMS_res_MET': 1.0})
                    card.addMVVSignalParametricShape(channel, "MVV", "{finalState}_{channel}.json".format(finalState=finalState, channel=channel), {})
                    card.addParametricYield(channel, 0, "{finalState}_{channel}_{catName}_yield.json".format(
                        finalState=finalState, channel=channel, catName=catName))

                    # QCD function
                    # card.addMVVBackgroundShapeQCD("QCD", "MVV", logTerm=False)
                    cuts = findCut(categories, cat="lnujj", lep=lepton, tau21=purity, mJ=boson[-1], reg=categ)
                    logTerm = False
                    parDict = makePrefit(dataTemplate, cuts, catName, resonanceMassString, templateDir, logTerm)
                    preconstraints = {}
                    nPar = 2
                    if logTerm:
                        nPar = 3
                    for i in range(nPar):
                        preconstraints['p%s' % i] = {}
                        preconstraints['p%s' % i]['val'] = parDict['p%s' % i]
                        preconstraints['p%s' % i]['err'] = parDict['e%s' % i]*5
                    # preconstraints['p0']['val'] = -0.05
                    # preconstraints['p0']['err'] = 0.05/2.
                    # preconstraints['p1']['val'] = 1000
                    # preconstraints['p1']['err'] = 1000/2.
                    # preconstraints['p2']['val'] = 400
                    # preconstraints['p2']['err'] = 400/2.

                    # card.addMVVBackgroundShapeErfPow("QCD", "MVV", preconstrains=preconstraints)
                    # card.addMVVBackgroundShapeErfPow("QCD", "MVV")
                    card.addMVVBackgroundShapeQCD("QCD", "MVV", logTerm=logTerm, preconstrains=preconstraints)
                    # card.addMVVBackgroundShapeExp("QCD", "MVV")
                    card.addFloatingYield("QCD", 1, 1000, mini=0, maxi=1e+9)
                    card.importBinnedData("{finalState}_{catName}.root".format(
                        finalState=finalState, catName=catName), "data", ["MVV"])

                    #####
                    # SYSTEMATICS

                    # luminosity
                    card.addSystematic("CMS_lumi", "lnN", {'XWW': 1.026, 'XWZ': 1.026})

                    # kPDF uncertainty for the signal
                    card.addSystematic("CMS_pdf", "lnN", {'XWW': 1.01, 'XWZ': 1.01})

                    # lepton efficiency
                    card.addSystematic("CMS_eff_" + lepton, "lnN", {'XWW': 1.1, 'XWZ': 1.1})

                    # tau21
                    if purity == 'HP':
                        card.addSystematic("CMS_VV_LNuJ_tau21_eff", "lnN", {'XWW': 1 + 0.14, 'XWZ': 1 + 0.14})

                    if purity == 'LP':
                        card.addSystematic("CMS_VV_LNuJ_tau21_eff", "lnN", {'XWW': 1 - 0.33, 'XWZ': 1 - 0.33})

                    card.addSystematic("CMS_btag_fake", "lnN", {'XWW': 1 + 0.02, 'XWZ': 1 + 0.02})

                    # pruned mass scale
                    card.addSystematic("CMS_scale_j", "param", [0.0, 0.02])
                    card.addSystematic("CMS_res_j", "param", [0.0, 0.05])
                    card.addSystematic("CMS_scale_prunedj", "param", [0.0, 0.0094])
                    card.addSystematic("CMS_res_prunedj", "param", [0.0, 0.2])

                    card.addSystematic("CMS_scale_MET", "param", [0.0, 0.02])
                    card.addSystematic("CMS_res_MET", "param", [0.0, 0.01])

                    # # Tagging efficiency correlated between signal and top in each purity
                    # if purity == 'HP':
                    #     card.addSystematic("CMS_tau21", "lnN", {finalState: 0.5})
                    # else:
                    #     card.addSystematic("CMS_tau21", "lnN", {finalState: 1.5})
                    #
                    # # parametric systs
                    #
                    # card.addSystematic("CMS_scale_j", "param", [0.0, 0.02])
                    # card.addSystematic("CMS_res_j", "param", [0.0, 0.05])
                    # card.addSystematic("CMS_scale_MET", "param", [0.0, 0.02])
                    # card.addSystematic("CMS_res_MET", "param", [0.0, 0.01])

                    card.makeCard()

    # make combined cards
    print cmd


if __name__ == '__main__':
    main()
