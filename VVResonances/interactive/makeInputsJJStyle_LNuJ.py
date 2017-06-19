"""Dijet style cards for significance testing."""
# import ROOT
import os
from CMGTools.VVResonances.plotting.categories_VV_2016 import *


class SignalTemplate:
    """primitive signal template class."""

    def __init__(self, shortName, templateName, branchingFraction):
        """initialise with all that's needed."""
        self.shortName = shortName
        self.templateName = templateName
        self.branchingFraction = branchingFraction

cuts = {}

cuts['common'] = [lnujj_inc_basic]

leptons = ['mu', 'e']
purities = ['HP', 'LP']
bCategories = ['nob']
bosons = ['WW', 'WZ']  # this should cut on the jet mass

jetMassString = 'lnujj_l2_softDrop_mass'
resonanceMassString = 'lnujj_LV_mass'

WWTemplate = SignalTemplate("XWW", "BulkGravToWWToWlepWhad_narrow", 2. * 0.327 * 0.6760)

WZTemplate = SignalTemplate("XWZ", "WprimeToWZToWlepZhad_narrow", 0.327 * 0.6991)

WHTemplate = SignalTemplate("XWH", "WprimeToWhToWlephbb", 0.577 * 0.327)

dataTemplate = "SingleMuon,SingleElectron,MET"

topTemplate = "TTJets."
WJetsTemplate = "WJetsToLNu_HT"
SMWWTemplate = 'WWTo1L1Nu2Q'
SMWZTemplate = 'WZTo1L1Nu2Q'

minMJJ = 40.0
maxMJJ = 160.0

minMVV = 800.0
maxMVV = 4500.0

binsMJJ = 60
binsMVV = 200


def makeSignalShapes(filename, template):
    """assuming here that the signal shapes are independent of channel and cuts."""
    cut = '&&'.join(cuts['common'])
    rootFile = filename + ".root"
    # cmd = 'vvMakeSignalMJJShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -V "{resonanceMassString}" -m {minMJJ} -M {maxMJJ} -e 0  samples'.format(
    #     template=template, cut=cut, rootFile=rootFile, resonanceMassString=resonanceMassString, jetMassString=jetMassString, minMJJ=minMJJ, maxMJJ=maxMJJ)
    cmd = 'vvMakeSignalMVVShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -V "{resonanceMassString}" samples'.format(
        template=template, cut=cut, rootFile=rootFile, resonanceMassString=resonanceMassString, jetMassString=jetMassString)
    print cmd
    os.system(cmd)
    jsonFile = filename + ".json"
    cmd = 'vvMakeJSON.py  -o "{jsonFile}" -g "MEAN:pol1,SIGMA:pol2,ALPHA1:pol3,N1:pol0,ALPHA2:pol4,N2:pol0"  -m 800 -M 5000 {rootFile}  '.format(
        jsonFile=jsonFile, rootFile=rootFile)
    print cmd
    os.system(cmd)


def makeSignalYields(filename, template, branchingFraction):
    """for each final state and overall category, make yields."""
    for lepton in leptons:
        for purity in purities:
            for bosonMass in bosons:
                for bCat in bCategories:
                    # cut = "&&".join([cuts['common'], cuts[lepton], cuts[purity], cuts[bosonMass], cuts[bCat]])
                    cut = findCut(categories, cat="lnujj", lep=lepton, tau21=purity, mJ=bosonMass[-1], reg=bCat)
                    # Signal yields
                    yieldFile = "{filename}_{lepton}_{purity}_{bosonMass}_{bCat}_yield".format(filename=filename, lepton=lepton, purity=purity, bosonMass=bosonMass, bCat=bCat)
                    cmd = 'vvMakeSignalYields.py -s {template} -c "{cut}" -o {output} -V "{resonanceMassString}" -m {minMVV} -M {maxMVV} -f "pol3" -b {BR} -x 1000.0 samples'.format(
                        template=template, cut=cut, output=yieldFile, resonanceMassString=resonanceMassString, minMVV=minMVV, maxMVV=maxMVV, BR=branchingFraction)
                    os.system(cmd)


def makeNormalizations(name, filename, template, data=0, addCut='', factor=1):
    """Data normalisation for each final state and overall category."""
    for lepton in leptons:
        for purity in purities:
            for bosonMass in bosons:
                for bCat in bCategories:
                    rootFile = "{filename}_{lepton}_{purity}_{bosonMass}_{bCat}.root".format(filename=filename, lepton=lepton, purity=purity, bosonMass=bosonMass, bCat=bCat)
                    if addCut == '':
                        # cut = "&&".join([cuts['common'], cuts[lepton], cuts[purity], cuts[bosonMass], cuts[bCat]])
                        cut = findCut(categories, cat="lnujj", lep=lepton, tau21=purity, mJ=bosonMass[-1], reg=bCat)
                    else:
                        cut = "&&".join([findCut(categories, cat="lnujj", lep=lepton, tau21=purity, mJ=bosonMass[-1], reg=bCat), addCut])
                    cmd = 'vvMakeData.py -s "{samples}" -d {data} -c "{cut}"  -o "{rootFile}" -v "{resonanceMassString}" -b "{BINS}" -m "{MINI}" -M "{MAXI}" -f {factor} -n "{name}"  samples'.format(
                        samples=template, cut=cut, rootFile=rootFile, resonanceMassString=resonanceMassString, BINS=binsMVV, MINI=minMVV, MAXI=maxMVV, factor=factor, name=name, data=data)
                    os.system(cmd)


makeSignalShapes("LNUJ_%s" % WWTemplate.shortName, WWTemplate.templateName)
makeSignalYields("LNUJ_%s" % WWTemplate.shortName, WWTemplate.templateName, WWTemplate.branchingFraction)
makeNormalizations("data", "LNUJ", dataTemplate, 1)
