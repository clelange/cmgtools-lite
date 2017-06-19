#!/usr/bin/env python
import ROOT
from array import array
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log
import os, sys, re, optparse,pickle,shutil,json
import json
from CMGTools.VVResonances.plotting.tdrstyle import *
setTDRStyle()
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter

parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="Output",default='')
parser.add_option("-s","--samples",dest="samples",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for yield in gen sample",default='')
parser.add_option("-C","--genCut",dest="genCut",help="Cut to apply for yield",default='')
parser.add_option("-d","--isData",dest="data",type=int,help="isData",default=1)
parser.add_option("-v","--var",dest="var",help="variable for gen",default='')
parser.add_option("-b","--bins",dest="bins",type=int,help="bins",default=20)
parser.add_option("-m","--min",dest="mini",type=float,help="minimum ",default=0.0)
parser.add_option("-M","--max",dest="maxi",type=float,help="maximum ",default=0.0)
parser.add_option("-g","--genVar",dest="genvar",help="variable for gen",default='')
parser.add_option("-q","--systMean",dest="systMean",default="mean",help="mean syst variation ")
parser.add_option("-w","--systSigma",dest="systSigma",default="sigma",help="sigma syst variation")


(options,args) = parser.parse_args()

def returnHisto(name,w,options):
    histo=w.pdf("model").createHistogram(options.var,w.var(options.var).getBins())
    histo.SetName(name)
    histo.Scale(1.0/histo.Integral())
    return histo


sampleTypes=options.samples.split(',')

dataPlotters=[]

for filename in os.listdir(args[0]):
    for sampleType in sampleTypes:
        if filename.find(sampleType)!=-1:
            fnameParts=filename.split('.')
            fname=fnameParts[0]
            ext=fnameParts[1]
            if ext.find("root") ==-1:
                continue
            dataPlotters.append(TreePlotter(args[0]+'/'+fname+'.root','tree'))
            if options.data==0 or options.data==2:
                dataPlotters[-1].setupFromFile(args[0]+'/'+fname+'.pck')
                dataPlotters[-1].addCorrectionFactor('xsec','tree')
                dataPlotters[-1].addCorrectionFactor('genWeight','tree')
                dataPlotters[-1].addCorrectionFactor('puWeight','tree')
if options.data==2:
    sigmas=[]
    for d in dataPlotters:
        sigmas.append(d.tree.GetMaximum("xsec")/d.weightinv)
    sigmaW=max(sigmas)
    for p in dataPlotters:
        p.addCorrectionFactor(1.0/sigmaW,'flat')
parameterization={}



data=MergedPlotter(dataPlotters)
dataset = data.makeDataSet(options.genvar,options.genCut,-1)
histo=data.drawTH1(options.var,options.cut,"1",options.bins,options.mini,options.maxi)
fitter=Fitter([options.var])
fitter.importBinnedData(histo,[options.var],'data')
fitter.gaussianSum('model',options.var,dataset,options.genvar)
fitter.fit('model','data',[ROOT.RooFit.SumW2Error(1)])
chi=fitter.projection("model","data",options.var,"debugPlot_"+options.output+".root",'x')
print 'Chi2',chi

print 'make systematics'
meanDefault=fitter.w.var("scale").getVal()
sigmaDefault=fitter.w.var("sigma").getVal()



f2=ROOT.TFile(options.output,"RECREATE")
f2.cd()
histo=returnHisto("histo",fitter.w,options)
histo.Write()

systs= options.systMean.split(':')
syst=systs[0]
val = float(systs[1])

fitter.w.var("scale").setVal(meanDefault+3*val)
histo=returnHisto("histo_"+syst+"Up",fitter.w,options)
histo.Write()

fitter.w.var("scale").setVal(meanDefault-3*val)
histo=returnHisto("histo_"+syst+"Down",fitter.w,options)
histo.Write()


fitter.w.var("scale").setVal(meanDefault)


systs= options.systSigma.split(':')
syst=systs[0]
val = float(systs[1])

fitter.w.var("sigma").setVal(sigmaDefault+3*val)
histo=returnHisto("histo_"+syst+"Up",fitter.w,options)
histo.Write()

fitter.w.var("sigma").setVal(sigmaDefault-3*val)
histo=returnHisto("histo_"+syst+"Down",fitter.w,options)
histo.Write()

fitter.w.var("sigma").setVal(sigmaDefault)
f2.Close()


