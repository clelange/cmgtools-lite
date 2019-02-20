from bisect import bisect
from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from PhysicsTools.Heppy.physicsobjects.Jet import *
from PhysicsTools.Heppy.physicsutils.JetReCalibrator import JetReCalibrator
from PhysicsTools.Heppy.analyzers.objects.JetAnalyzer import shiftJERfactor
from PhysicsTools.HeppyCore.utils.deltar import matchObjectCollection2
# import itertools
import ROOT
import os
import math

class jetBuilder(Analyzer):

    def __init__(self, cfg_ana, cfg_comp, looperName):
        super(jetBuilder, self).__init__(cfg_ana, cfg_comp, looperName)

        mcGT   = cfg_ana.mcGT   if hasattr(cfg_ana, 'mcGT')   else "Fall17_17Nov2017_V6_MC"
        dataGT = cfg_ana.dataGT if hasattr(cfg_ana, 'dataGT') else [(297020,"Fall17_17Nov2017B_V6_DATA"), (299337,"Fall17_17Nov2017C_V6_DATA"), (302030,"Fall17_17Nov2017D_V6_DATA"), (303435,"Fall17_17Nov2017E_V6_DATA"), (304911,"Fall17_17Nov2017F_V6_DATA")]
        GTs = getattr(cfg_comp, 'jecGT', mcGT if self.cfg_comp.isMC else dataGT)
        if type(GTs) == str: GTs = [ (-1, GTs) ]

        self.jecPath = getattr(self.cfg_ana, 'jecPath', "${CMSSW_BASE}/src/CMGTools/RootTools/data/jec/")
        self.rho = getattr(self.cfg_ana, 'rho', ('fixedGridRhoFastjetAll','',''))

        self.shiftJEC = self.cfg_ana.shiftJEC if hasattr(self.cfg_ana, 'shiftJEC') else 0
        self.recalibrateJets = getattr(self.cfg_ana, 'recalibrateJets', True)
        self.addJECShifts = getattr(self.cfg_ana, 'addJECShifts', True)
        self.doJEC = self.recalibrateJets or (self.shiftJEC != 0) or self.addJECShifts
        if self.doJEC:
          doResidual = getattr(cfg_ana, 'applyL2L3Residual', 'Data')
          if   doResidual == "MC":   doResidual = self.cfg_comp.isMC
          elif doResidual == "Data": doResidual = not self.cfg_comp.isMC
          elif doResidual not in [True, False]: raise RuntimeError, "If specified, applyL2L3Residual must be any of { True, False, 'MC', 'Data'(default)}"

        self.smearing = ROOT.TRandom(10101982)

        self.shiftJER = self.cfg_ana.shiftJER if hasattr(self.cfg_ana, 'shiftJER') else 0
        self.addJERShifts = self.cfg_ana.addJERShifts if hasattr(self.cfg_ana, 'addJERShifts') else 0
        self.matchJetsWithThreshold = getattr(self.cfg_ana, 'matchJetsWithThreshold', False)

        self.jetReCalibrators = []
        self.runsGT=[]
        for (run, GT) in GTs:
              self.jetReCalibrators.append(JetReCalibrator(GT, cfg_ana.recalibrationType, doResidual, self.jecPath))
              self.runsGT.append(run)

    def declareHandles(self):
        super(jetBuilder, self).declareHandles()
        self.handles['packed'] = AutoHandle(
            'packedPFCandidates', 'std::vector<pat::PackedCandidate>')
        if self.cfg_comp.isMC:
            self.handles['packedGen'] = AutoHandle(
                'packedGenParticles', 'std::vector<pat::PackedGenParticle>')
        self.handles['rho'] = AutoHandle( self.cfg_ana.rho, 'double' )
        self.handles['genJet'] = AutoHandle( self.cfg_ana.genJetCol, 'vector<reco::GenJet>' )
        self.handles['primaryVertices'] = AutoHandle('offlineSlimmedPrimaryVertices',"vector<reco::Vertex>")


    def matchJets(self, event, jets):
        match = matchObjectCollection2(jets,
                                       event.genbquarks + event.genwzquarks,
                                       deltaRMax = 0.3)
        for jet in jets:
            gen = match[jet]
            jet.mcParton    = gen
            jet.mcMatchId   = (gen.sourceId     if gen != None else 0)
            jet.mcMatchFlav = (abs(gen.pdgId()) if gen != None else 0)

        match = matchObjectCollection2(jets,
                                       self.genJets,
                                       deltaRMax = 0.3)
        for jet in jets:
            jet.mcJet = match[jet]


    def smearJets(self, event, jets):
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/TWikiTopRefSyst#Jet_energy_resolution
       for jet in jets:
            gen = jet.mcJet
            if gen != None:
               genpt, jetpt, aeta = gen.pt(), jet.pt(), abs(jet.eta())
               # from https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
               factor = shiftJERfactor(self.shiftJER, aeta)
               ptscale = max(0.0, (jetpt + (factor-1)*(jetpt-genpt))/jetpt)
               #print "get with pt %.1f (gen pt %.1f, ptscale = %.3f)" % (jetpt,genpt,ptscale)
               jet.deltaMetFromJetSmearing = [ -(ptscale-1)*jet.rawFactor()*jet.px(), -(ptscale-1)*jet.rawFactor()*jet.py() ]
               if ptscale != 0:
                  jet.setP4(jet.p4()*ptscale)
                  # leave the uncorrected unchanged for sync
                  jet.setRawFactor(jet.rawFactor()/ptscale)
            #else: print "jet with pt %.1d, eta %.2f is unmatched" % (jet.pt(), jet.eta())
               if (self.shiftJER==0) and (self.addJERShifts):
                   setattr(jet, "corrJER", ptscale )
                   factorJERUp= shiftJERfactor(1, aeta)
                   ptscaleJERUp = max(0.0, (jetpt + (factorJERUp-1)*(jetpt-genpt))/jetpt)
                   setattr(jet, "corrJERUp", ptscaleJERUp)
                   factorJERDown= shiftJERfactor(-1, aeta)
                   ptscaleJERDown = max(0.0, (jetpt + (factorJERDown-1)*(jetpt-genpt))/jetpt)
                   setattr(jet, "corrJERDown", ptscaleJERDown)


    def process(self, event):
        self.readCollections(event.input)
        # get primary vertices
        pVertices = self.handles['primaryVertices'].product()
        # load packed candidatyes
        cands = self.handles['packed'].product()
        packedCandidatesCHS = ROOT.std.vector("math::XYZTLorentzVector")()
        for c in cands:
            if c.pt() > 13000 or c.pt() == float('Inf'):
                continue
            if c.fromPV(0) > 0:
                packedCandidatesCHS.push_back(c.p4())
        interface = ROOT.cmg.FastJetInterface(
            packedCandidatesCHS, -1.0, 0.8, 1, 0.01, 5.0, 4.4)
        interface.makeInclusiveJets(150.0)
        ak8CHS4Vector = interface.get(True)
        jetCollection = []
        for i, fourVec in enumerate(ak8CHS4Vector):
            reco_jet = ROOT.reco.Jet(fourVec, pVertices[0].position())
            pat_jet = ROOT.pat.Jet(reco_jet)
            jet = Jet(pat_jet)
            jet.jecFactor = lambda x: 1.
            jetCollection.append(jet)
        self.ak8JetsCHS = jetCollection

        # JECs
        rho  = float(self.handles['rho'].product()[0])
        self.rho = rho
        run = event.input.eventAuxiliary().id().run()
        if self.doJEC:
            runBin = bisect(self.runsGT, run) - 1
            if runBin == -1:
                raise RuntimeError, "ERROR: run range not covered by the Jet recalibrator (jetAnalyzer), check the JECs"

        ## Read jets, if necessary recalibrate and shift MET
        allJets = copy.deepcopy(self.ak8JetsCHS)
        # allJets = map(JetWithArea, self.ak8JetsCHS)

        #set dummy MC flavour for all jets in case we want to ntuplize discarded jets later
        for jet in allJets:
            jet.mcFlavour = 0

        self.deltaMetFromJEC = [0.,0.]
        self.type1METCorr    = [0.,0.,0.]
        self.jetReCalibrators[runBin].correctAll(allJets, rho, delta=self.shiftJEC,
                                                 addCorr=True, addShifts=self.addJECShifts,
                                                 metShift=self.deltaMetFromJEC, type1METCorr=self.type1METCorr )

        # JET Smearing
        if self.cfg_comp.isMC:
            self.genJets = [ x for x in self.handles['genJet'].product() ]
            if self.cfg_ana.do_mc_match:
                for igj, gj in enumerate(self.genJets):
                    gj.index = igj
                if self.matchJetsWithThreshold and not getattr(self.cfg_ana, 'smearJets', False):
                    self.matchJets(event, [ j for j in allJets if j.pt()>self.cfg_ana.jetPt ]) # To match only jets above chosen threshold
                else:
                    self.matchJets(event, allJets)
            if getattr(self.cfg_ana, 'smearJets', False):
                self.smearJets(event, allJets)

        # add the jets to the event
        setattr(event, 'CustomJets' + self.cfg_ana.suffix, allJets)
