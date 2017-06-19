import ROOT
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
from CMGTools.VVResonances.statistics.DataCardMaker import DataCardMaker
cmd = 'combineCards.py '

finalState = "LNUJ"
channel = "XWW"

lumi = 35900
leptons = ['mu', 'e']
purities = ['HP', 'LP']
# categories = ['nob', 'b']
categories = ['nob']
bosons = ['WW', 'WZ']

for lepton in leptons:
    for purity in purities:
        for boson in bosons:
            for categ in categories:
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
                preconstraints = {}
                preconstraints['p0'] = {}
                preconstraints['p1'] = {}
                preconstraints['p2'] = {}
                preconstraints['p0']['val'] = 4.48531e-07
                preconstraints['p0']['err'] = 20
                preconstraints['p1']['val'] = -7.96655e-01
                preconstraints['p1']['err'] = 100
                preconstraints['p2']['val'] = 7.43952e+00
                preconstraints['p2']['err'] = 50
                # preconstraints['p0']['val'] = -0.05
                # preconstraints['p0']['err'] = 0.05/2.
                # preconstraints['p1']['val'] = 1000
                # preconstraints['p1']['err'] = 1000/2.
                # preconstraints['p2']['val'] = 400
                # preconstraints['p2']['err'] = 400/2.

                # card.addMVVBackgroundShapeErfPow("QCD", "MVV", preconstrains=preconstraints)
                card.addMVVBackgroundShapeErfPow("QCD", "MVV")
                # card.addMVVBackgroundShapeExp("QCD", "MVV")
                card.addFloatingYield("QCD", 1, 1000, mini=0, maxi=1e+9)
                card.importBinnedData("{finalState}_{catName}.root".format(
                    finalState=finalState, catName=catName), "data", ["MVV"])

                #####
                # SYSTEMATICS

                # luminosity
                card.addSystematic("CMS_lumi", "lnN", {'XWW': 1.04})

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
