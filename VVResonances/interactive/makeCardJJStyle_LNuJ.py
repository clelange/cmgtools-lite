import ROOT
import os
import sys
from CMGTools.VVResonances.statistics.DataCardMaker import DataCardMaker
from CMGTools.VVResonances.plotting.categories_VV_2016 import findCut, categories
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")

useConstraints = False
constraintsFactor = 5

finalState = "LNUJ"
channels = ["XWW", "XWZ"]

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

minMVV = 800
maxMVV = 4500.0

binsMJJ = 60
binsMVV = 200

fTestResults = {}
fTestResults["mu_HP_WW_nob"] = 2
fTestResults["mu_HP_WZ_nob"] = 3
fTestResults["mu_LP_WW_nob"] = 2
fTestResults["mu_LP_WZ_nob"] = 2
fTestResults["e_HP_WW_nob"] = 2
fTestResults["e_HP_WZ_nob"] = 3
fTestResults["e_LP_WW_nob"] = 2
fTestResults["e_LP_WZ_nob"] = 3


def makePrefit(sampleTypes, cuts, catName, resonanceMassString, templateDir, degree):
    assert type(degree) is int, "degree is not an integer: %r" % id
    assert(degree >= 2), "Need at least 2 parameters"
    assert(degree < 5), "Currently support at most 4 parameters"
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
    # for debugging the fit it helps to write out the histo and fit it interactively
    # outFile = ROOT.TFile("%s_datahist.root" % catName, "recreate")
    # outFile.cd()
    # histo.Write()
    # outFile.Write()
    # outFile.Close()

    """
    qcfFunc1 = TF1("qcdFunc2", "[1]*TMath::Power( x/13000., [0])", 1000, 4500)
    qcfFunc2 = TF1("qcdFunc3", "[2]*TMath::Power(1-x/13000., [0])/TMath::Power(x/13000., [1])", 1000, 4500)
    qcfFunc3 = TF1("qcdFunc4", "[3]*TMath::Power(1-x/13000., [0])/TMath::Power(x/13000., [1]+[2]*TMath::Log(x/13000.))", 1000, 4500)
    TH1D* myHist = (TH1D*)_file0->Get("tmpTH1")
    myHist->Fit("qcdFunc2")
    myHist->Fit("qcdFunc3")
    myHist->Fit("qcdFunc4")
    """

    #    if options.zeroNegative:
    #        for i in range(0,int(pbins[0])+2):
    #            if histo.GetBinContent(i)<0:
    #                histo.SetBinContent(i,0.0)
    sqrt_s = 13000
    xRange = [minMVV, maxMVV]
    qcdFunc = None
    if (degree == 2):
        qcdFunc = ROOT.TF1("qcdFunc", "[0]*TMath::Power( x/{sqrt_s}, [1])".format(sqrt_s=sqrt_s), xRange[0], xRange[1])
        qcdFunc.SetParameter(0, 1e-06)
        qcdFunc.SetParameter(1, -6)
    if (degree == 3):
        qcdFunc = ROOT.TF1("qcdFunc", "[0]*TMath::Power(1-x/{sqrt_s}, [1])/TMath::Power(x/{sqrt_s}, [2])".format(sqrt_s=sqrt_s), xRange[0], xRange[1])
    if (degree == 4):
        qcdFunc = ROOT.TF1("qcdFunc", "TMath::Power(1-x/{sqrt_s}, [2])/TMath::Power(x/{sqrt_s}, [2]+[3]*TMath::Log(x/{sqrt_s}))".format(sqrt_s=sqrt_s), xRange[0], xRange[1])

    if (degree >= 3):
        qcdFunc.SetParameter(0, 1e-03)
        qcdFunc.SetParameter(1, 7)
        qcdFunc.SetParameter(2, 5)
        if (degree >= 4):
            qcdFunc.SetParameter(4, 1e-04)

    canvas = ROOT.TCanvas("c1", "c1", 800, 600)
    canvas.Draw()
    histo.Fit(qcdFunc)
    fitResult = histo.GetFunction("qcdFunc")
    print "chi2", fitResult.GetChisquare()
    # print "p0", fitResult.GetParameter(0), "+/-", fitResult.GetParError(0)
    # print "p1", fitResult.GetParameter(1), "+/-", fitResult.GetParError(1)
    # print "p2", fitResult.GetParameter(2), "+/-", fitResult.GetParError(2)
    parDict = {}
    # shift the parameter by one since RooFit doesn't use normalisation
    for par in range(degree-1):
        parDict["p%d" % par] = fitResult.GetParameter(par+1)
        parDict["e%d" % par] = fitResult.GetParError(par+1)
    # qcdFunc.Draw()
    events = histo.Integral()
    print "Yield:", events
    parDict["yield"] = events
    canvas.SaveAs("prefit_%s.png" % (catName))
    return parDict


def main():

    templateDir = "samples"
    if len(sys.argv) > 1:
        templateDir = sys.argv[1]

    commands = []

    for channel in channels:
        print "-------"*5
        cmd = 'combineCards.py '
        cmd += getCommand(templateDir, channel)
        cmd += " > combined_%s.txt" % channel
        commands.append(cmd)

    for cmd in commands:
        print "-------"*5
        print cmd


def getCommand(templateDir, channel):

    cmd = ''
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
                    card.addMVVSignalParametricShape(channel, "MVV", "{finalState}_{channel}.json".format(finalState=finalState, channel=channel), {
                                                     'CMS_scale_j': 1, 'CMS_scale_MET': 1.0}, {'CMS_res_j': 1.0, 'CMS_res_MET': 1.0})
                    # card.addMVVSignalParametricShape(channel, "MVV", "{finalState}_{channel}.json".format(finalState=finalState, channel=channel), {})
                    card.addParametricYield(channel, 0, "{finalState}_{channel}_{catName}_yield.json".format(
                        finalState=finalState, channel=channel, catName=catName))

                    # QCD function
                    # card.addMVVBackgroundShapeQCD("QCD", "MVV", logTerm=False)
                    cuts = findCut(categories, cat="lnujj", lep=lepton, tau21=purity, mJ=boson[-1], reg=categ)
                    parDict = makePrefit(dataTemplate, cuts, catName, resonanceMassString, templateDir, fTestResults[catName])
                    preconstraints = {}
                    boundaries = {}
                    for i in range(fTestResults[catName]-1):
                        preconstraints['p%s' % i] = {}
                        boundaries['p%s' % i] = {}
                        # use prefit value as starting point
                        preconstraints['p%s' % i]['val'] = parDict['p%s' % i]
                        bounds = []
                        bounds.append(parDict['p%s' % i] + 1000*parDict['e%s' % i])
                        bounds.append(parDict['p%s' % i] - 1000*parDict['e%s' % i])
                        boundaries['p%s' % i] = [min(bounds), max(bounds)]
                        if useConstraints:
                            preconstraints['p%s' % i]['err'] = parDict['e%s' % i]*constraintsFactor
                    # preconstraints['p0']['val'] = -0.05
                    # preconstraints['p0']['err'] = 0.05/2.
                    # preconstraints['p1']['val'] = 1000
                    # preconstraints['p1']['err'] = 1000/2.
                    # preconstraints['p2']['val'] = 400
                    # preconstraints['p2']['err'] = 400/2.
                    events = parDict["yield"]

                    # card.addMVVBackgroundShapeErfPow("QCD", "MVV", preconstraints=preconstraints)
                    # card.addMVVBackgroundShapeErfPow("QCD", "MVV")
                    card.addMVVBackgroundShapeQCDJJStyle("QCD", "MVV", degree=fTestResults[catName], boundaries=boundaries, preconstraints=preconstraints)
                    # card.addMVVBackgroundShapeExp("QCD", "MVV")
                    # card.addFloatingYield("QCD", 1, 1000, mini=0.5*yield, maxi=1e+9)  # commented out 30 Aug
                    card.addFixedYieldWithEvents("QCD", 1, events)
                    card.importBinnedData("{finalState}_{catName}.root".format(
                        finalState=finalState, catName=catName), "data", ["MVV"])

                    #####
                    # SYSTEMATICS

                    # luminosity
                    card.addSystematic("CMS_lumi", "lnN", {'XWW': 1.026, 'XWZ': 1.026})
                    card.addSystematic("CMS_background", "lnN", {'QCD': 1.5})

                    # kPDF uncertainty for the signal
                    card.addSystematic("CMS_pdf", "lnN", {'XWW': 1.01, 'XWZ': 1.01})

                    # lepton efficiency
                    card.addSystematic("CMS_eff_" + lepton, "lnN", {'XWW': 1.1, 'XWZ': 1.1})

                    #W+jets cross section in acceptance-dominated by pruned mass
                    # card.addSystematic("CMS_VV_LNuJ_nonRes_norm_"+lepton+"_"+purity+"_"+category,"lnN",{'nonRes':1.5})
                    # card.addSystematic("CMS_VV_LNuJ_resW_norm_"+lepton+"_"+purity+"_"+category,"lnN",{'resW':1.20})


                    # tau21
                    if purity == 'HP':
                        card.addSystematic("CMS_VV_LNuJ_tau21_eff", "lnN", {'XWW': 1 + 0.14, 'XWZ': 1 + 0.14})

                    if purity == 'LP':
                        card.addSystematic("CMS_VV_LNuJ_tau21_eff", "lnN", {'XWW': 1 - 0.33, 'XWZ': 1 - 0.33})

                    card.addSystematic("CMS_btag_fake", "lnN", {'XWW': 1 + 0.02, 'XWZ': 1 + 0.02})

                    # pruned mass scale
                    card.addSystematic("CMS_scale_j","param",[0.0,0.02])
                    card.addSystematic("CMS_res_j","param",[0.0,0.05])
                    # card.addSystematic("CMS_scale_prunedj","param",[0.0,0.0094])
                    # card.addSystematic("CMS_res_prunedj","param",[0.0,0.2])
                    # card.addSystematic('CMS_VV_topPt_0_'+lepton+"_"+purity+"_"+category,"param",[0.0,0.2])
                    # card.addSystematic('CMS_VV_topPt_1_'+lepton+"_"+purity+"_"+category,"param",[0.0,25000.0])

                    card.addSystematic("CMS_scale_MET","param",[0.0,0.02])
                    card.addSystematic("CMS_res_MET","param",[0.0,0.01])
                    # card.addSystematic("CMS_VV_LNuJ_nonRes_PTX_"+qcdTag,"param",[0.0,0.333])
                    # card.addSystematic("CMS_VV_LNuJ_nonRes_OPTX_"+qcdTag,"param",[0.0,0.333])

                    # card.addSystematic("CMS_VV_LNuJ_nonRes_PTY_"+qcdTag,"param",[0.0,333])
                    # card.addSystematic("CMS_VV_LNuJ_nonRes_OPTY_"+qcdTag,"param",[0.0,0.6])


                    # card.addSystematic("CMS_VV_LNuJ_resW_PT_"+resWTag,"param",[0.0,0.333])
                    # card.addSystematic("CMS_VV_LNuJ_resW_OPT_"+resWTag,"param",[0.0,0.333])

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
    return cmd


if __name__ == '__main__':
    main()
