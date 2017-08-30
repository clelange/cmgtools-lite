import sys
from CMGTools.VVResonances.plotting.RooPlotter import RooPlotter
from CMGTools.VVResonances.plotting.CMS_lumi import cmslabel_prelim

import ROOT
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")

mass = 1350
if len(sys.argv) > 1:
    mass = int(sys.argv[1])

channel = "XWW"

plotter = RooPlotter("combined_%s.root" % channel)
plotter.fix("MH", mass)
# plotter.fix("r",0.0)
plotter.prefit()
plotter.addContribution("XWW", True, "X #rightarrow WW", 3, 1, ROOT.kOrange + 10, 0, ROOT.kWhite)
plotter.addContribution("QCD", False, " QCD", 2, 1, ROOT.kBlack, 1001, ROOT.kAzure - 9)

leptons = ['mu', 'e']
purities = ['HP', 'LP']
b_categories = ['nob']
bosons = ['WW', 'WZ']


for lepton in leptons:
    for purity in purities:
        for boson in bosons:
            for categ in b_categories:
                catName = '_'.join([lepton, purity, boson, categ, "13TeV"])
                plotter.drawBinned("MVV", "m_{WV} (GeV)", catName, [], 0)
                cmslabel_prelim(plotter.pad1, '2016', 11)
                # plotter.canvas.SaveAs("postFitMJJ_{}_m{}.root".format(catName, mass))
                plotter.canvas.SaveAs("postFitMJJ_{}_m{}.pdf".format(catName, mass))
                plotter.canvas.SaveAs("postFitMJJ_{}_m{}.png".format(catName, mass))
                plotter.drawBinned("MVV", "m_{WV} (GeV)", catName, [], 0, True, "")
                cmslabel_prelim(plotter.pad1, '2016', 11)
                plotter.canvas.SaveAs("postFitMJJ_{}_m{}_log.pdf".format(catName, mass))
                plotter.canvas.SaveAs("postFitMJJ_{}_m{}_log.png".format(catName, mass))
