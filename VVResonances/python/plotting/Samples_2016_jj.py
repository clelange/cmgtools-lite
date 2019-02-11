import os
import ROOT
from ROOT import gSystem

from CMGTools.H2TauTau.proto.plotter.PlotConfigs import SampleCfg
from CMGTools.VVResonances.plotting.HistCreator import setSumWeights


from CMGTools.RootTools.samples.samples_13TeV_RunIIFall17MiniAOD import QCDHT, QCDPt, VJetsQQHT, TTHad_pow
from CMGTools.RootTools.samples.samples_13TeV_DATA2017 import *
from CMGTools.VVResonances.samples.signal_13TeV_94X_Fall17 import signalSamples
from CMGTools.VVResonances.samples.signal_13TeV_94X_Fall17_private import signalSamples_private


def createSampleLists(analysis_dir='samples/',
                      channel='VV', weight='', signalSample='',
                      vJetsKFac=1., qcdKFac=1.,
                      useQCDPt=False):

    # explicit list of samples:
    wjetsSampleNames = ["WJetsToQQ_HT600toInf"]
    dyjetsSampleNames = ['ZJetsToQQ_HT600toInf']
    ttjetsSampleNames = []
    # ttjetsSampleNames = ["TTHad_pow"]
    qcdSampleNames = ['QCD_HT100to200', 'QCD_HT200to300', 'QCD_HT300to500', 'QCD_HT500to700', 'QCD_HT700to1000', 'QCD_HT1000to1500', 'QCD_HT1500to2000', 'QCD_HT2000toInf']

    jj_SampleNames = qcdSampleNames + wjetsSampleNames + dyjetsSampleNames + ttjetsSampleNames

    tree_prod_name = ''

    # if (channel == "WV"):
    #     channelSampleNames = lnujj_SampleNames
    # else:
    channelSampleNames = jj_SampleNames
    samples_essential = []

    # if "/sVJetsReweighting_cc.so" not in gSystem.GetLibraries():
    #     ROOT.gROOT.ProcessLine(".L %s/src/CMGTools/VVResonances/python/plotting/VJetsReweighting.cc+" % os.environ['CMSSW_BASE'])
    # from ROOT import getDYWeight, getWWeight

    # add samples
    for sample in QCDHT + QCDPt + VJetsQQHT + [TTHad_pow]:
        vJetsWeight = "1."  # str(vJetsKFac)
        if sample.name in channelSampleNames:
            if sample.name in qcdSampleNames:
                vJetsWeight = str(qcdKFac)
            if sample.name in (wjetsSampleNames + dyjetsSampleNames):
                vJetsWeight = str(1.0)
            # if (sample in DYJetsM50HT) and reweightVJets:
            #     vJetsWeight = '{} * {}'.format(vJetsKFac, dyJetsQCDCorrections[sample.name])
            # elif (sample in WJetsToLNuHT) and reweightVJets:
            #     vJetsWeight = '{} * {}'.format(vJetsKFac, wJetsQCDCorrections[sample.name])
            # if (sample in DYJetsM50HT) and reweightVJets2015:
            #     vJetsWeight = 'getDYWeight(truth_genBoson_pt) * {} * {}'.format(vJetsKFac, dyJetsQCDCorrections2015[sample.name])
            # elif (sample in WJetsToLNuHT) and reweightVJets2015:
            #     vJetsWeight = 'getWWeight(truth_genBoson_pt) * {} * {}'.format(vJetsKFac, wJetsQCDCorrections2015[sample.name])
            samples_essential.append(
                SampleCfg(name=sample.name, dir_name=sample.name, ana_dir=analysis_dir, tree_prod_name=tree_prod_name,
                    xsec=sample.xSection, sumweights=sample.nGenEvents, weight_expr=('*'.join([weight, vJetsWeight]))))

    # # TTJets sample
    # for sample in topSamples:
    #     if sample.name in channelSampleNames:
    #         # print "Adding", sample.name, sample.xSection, sample.nGenEvents, weight
    #         samples_essential.append(
    #             SampleCfg(name=sample.name+'_W', dir_name=sample.name, ana_dir=analysis_dir, tree_prod_name=tree_prod_name,
    #                 xsec=sample.xSection, sumweights=sample.nGenEvents, weight_expr=('*'.join([weight, ttjetsWCut]))))
    #         samples_essential.append(
    #             SampleCfg(name=sample.name+'_nonW', dir_name=sample.name, ana_dir=analysis_dir, tree_prod_name=tree_prod_name,
    #                 xsec=sample.xSection, sumweights=sample.nGenEvents, weight_expr=('*'.join([weight, ttjetsNonWCut]))))

    # signal sample (set signal xsec to 5 pb)
    samples_signal = []
    if (signalSample):
        for sample in signalSamples:
            if sample.name == signalSample:
                samples_signal.append(
                    SampleCfg(name=sample.name, dir_name=sample.name, ana_dir=analysis_dir, tree_prod_name=tree_prod_name,
                        xsec=5., sumweights=sample.nGenEvents, weight_expr=('*'.join([weight])), is_signal=True))

    samples_data = []
    if channel == 'WV':
        samples_data = [
            SampleCfg(name='data_SingleMuon', dir_name='SingleMuon_Run2016B_03Feb2017_v2', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleMuon', dir_name='SingleMuon_Run2016C_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleMuon', dir_name='SingleMuon_Run2016D_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleMuon', dir_name='SingleMuon_Run2016E_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleMuon', dir_name='SingleMuon_Run2016F_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleMuon', dir_name='SingleMuon_Run2016G_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleMuon', dir_name='SingleMuon_Run2016H_03Feb2017_v2', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleMuon', dir_name='SingleMuon_Run2016H_03Feb2017_v3', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleElectron', dir_name='SingleElectron_Run2016B_03Feb2017_v2', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleElectron', dir_name='SingleElectron_Run2016C_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleElectron', dir_name='SingleElectron_Run2016D_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleElectron', dir_name='SingleElectron_Run2016E_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleElectron', dir_name='SingleElectron_Run2016F_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleElectron', dir_name='SingleElectron_Run2016G_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleElectron', dir_name='SingleElectron_Run2016H_03Feb2017_v2', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_SingleElectron', dir_name='SingleElectron_Run2016H_03Feb2017_v3', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_MET', dir_name='MET_Run2016B_03Feb2017_v2', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_MET', dir_name='MET_Run2016C_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_MET', dir_name='MET_Run2016D_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_MET', dir_name='MET_Run2016E_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_MET', dir_name='MET_Run2016F_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_MET', dir_name='MET_Run2016G_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_MET', dir_name='MET_Run2016H_03Feb2017_v2', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_MET', dir_name='MET_Run2016H_03Feb2017_v3', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
        ]
    else:
        samples_data = [
            SampleCfg(name='data_JetHT', dir_name='JetHT_Run2016B_03Feb2017_v2', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_JetHT', dir_name='JetHT_Run2016C_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_JetHT', dir_name='JetHT_Run2016D_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_JetHT', dir_name='JetHT_Run2016E_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_JetHT', dir_name='JetHT_Run2016F_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_JetHT', dir_name='JetHT_Run2016G_03Feb2017', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_JetHT', dir_name='JetHT_Run2016H_03Feb2017_v2', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
            SampleCfg(name='data_JetHT', dir_name='JetHT_Run2016H_03Feb2017_v3', ana_dir=analysis_dir, tree_prod_name=tree_prod_name, is_data=True),
        ]

    # samples_WH = []
    # mssm_names = ['HiggsSUSYBB80', 'HiggsSUSYBB90', 'HiggsSUSYBB100', 'HiggsSUSYBB110', 'HiggsSUSYBB120', 'HiggsSUSYBB130', 'HiggsSUSYBB140', 'HiggsSUSYBB160', 'HiggsSUSYBB180', 'HiggsSUSYBB200', 'HiggsSUSYBB250', 'HiggsSUSYBB300', 'HiggsSUSYBB350', 'HiggsSUSYBB400', 'HiggsSUSYBB450', 'HiggsSUSYBB500', 'HiggsSUSYBB600', 'HiggsSUSYBB700', 'HiggsSUSYBB900', 'HiggsSUSYBB1000', 'HiggsSUSYBB1200', 'HiggsSUSYBB1500', 'HiggsSUSYBB1600', 'HiggsSUSYBB1800', 'HiggsSUSYBB2000', 'HiggsSUSYBB2300', 'HiggsSUSYBB2600', 'HiggsSUSYBB2900', 'HiggsSUSYBB3200', 'HiggsSUSYGG80', 'HiggsSUSYGG90',
    #               'HiggsSUSYGG100', 'HiggsSUSYGG110', 'HiggsSUSYGG120', 'HiggsSUSYGG130', 'HiggsSUSYGG140', 'HiggsSUSYGG160', 'HiggsSUSYGG180', 'HiggsSUSYGG200', 'HiggsSUSYGG250', 'HiggsSUSYGG300', 'HiggsSUSYGG400', 'HiggsSUSYGG450', 'HiggsSUSYGG500', 'HiggsSUSYGG600', 'HiggsSUSYGG700', 'HiggsSUSYGG800', 'HiggsSUSYGG900', 'HiggsSUSYGG1000', 'HiggsSUSYGG1200', 'HiggsSUSYGG1400', 'HiggsSUSYGG1500', 'HiggsSUSYGG1600', 'HiggsSUSYGG1800', 'HiggsSUSYGG2000', 'HiggsSUSYGG2300', 'HiggsSUSYGG2600', 'HiggsSUSYGG2900', 'HiggsSUSYGG3200']  # HiggsSUSYBB800, HiggsSUSYBB1400, HiggsSUSYGG350
    # for name in mssm_names:
    #     samples_WH.append(SampleCfg(name=name.replace('HiggsSUSYBB', 'bbH').replace('HiggsSUSYGG', 'ggH'), dir_name=name,
    #                                   ana_dir=analysis_dir, tree_prod_name=tree_prod_name, xsec=1., sumweights=1., is_signal=True),)

    samples_mc = samples_essential + samples_signal
    samples = samples_essential + samples_data + samples_signal
    all_samples = samples_mc + samples_data

    # -> Can add cross sections for samples either explicitly, or from file, or from cfg
    #    (currently taken from htt_common)

    weighted_list = []

    for sample in samples_mc:
        if sample.name not in weighted_list:
            setSumWeights(sample)

    # sampleDict = {s.name: s for s in all_samples}
    sampleDict = {}
    for s in all_samples:
        sampleDict[s.name] = s

    return samples_mc, samples_data, samples, all_samples, sampleDict

samples_mc, samples_data, samples, all_samples, sampleDict = createSampleLists()
