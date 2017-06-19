#!/usr/bin/env python

import ROOT
from array import array
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log
import os, sys, re, optparse,pickle,shutil,json
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
import copy



parser = optparse.OptionParser()
parser.add_option("-s","--samples",dest="samples",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for yield",default='')
parser.add_option("-o","--output",dest="output",help="Output ROOT",default='')
parser.add_option("-v","--varx",dest="varx",help="variablex",default='lnujj_LV_mass')
parser.add_option("-b","--binsx",dest="binsx",type=int,help="bins in x",default=1000)
parser.add_option("-x","--minx",dest="minx",type=float,help="minimum x",default=600)
parser.add_option("-X","--maxx",dest="maxx",type=float, help="maximum x",default=5000)
parser.add_option("-V","--vary",dest="vary",help="variablex",default='lnujj_l2_pruned_mass')
parser.add_option("-l","--lumi",dest="lumi",type=float, help="lumi",default="1")
parser.add_option("-e","--doExp",dest="doExp",type=int, help="Do exponential",default=0)
parser.add_option("-j","--json",dest="json", help="InputJSON",default=0)

(options,args) = parser.parse_args()

def returnString(func,options):
    varName="MH"
    if func.GetName().find("pol")!=-1:
        st='0'
        for i in range(0,func.GetNpar()):
            st=st+"+("+str(func.GetParameter(i))+")"+(("*"+varName)*i)
        return st    
    elif func.GetName().find("log")!=-1:
        return str(func.GetParameter(0))+"+("+str(func.GetParameter(1))+")*log("+varName+")"
    else:
        return ""



def runFits(data,options):
    jsonFile=open(options.json)
    info=json.load(jsonFile)

    meanF = ROOT.TFormula("meanF",info['mean'].replace('MH','x'))
    sigmaF = ROOT.TFormula("sigmaF",info['sigma'].replace('MH','x'))
    alphaF = ROOT.TFormula("alphaF",info['alpha'].replace('MH','x'))
    nF = ROOT.TFormula("nF",info['n'].replace('MH','x'))
    alpha2F = ROOT.TFormula("alpha2F",info['alpha2'].replace('MH','x'))
    n2F = ROOT.TFormula("n2F",info['n2'].replace('MH','x'))
    slopeF = ROOT.TFormula("slopeF",info['slope'].replace('MH','x'))
    fF = ROOT.TFormula("fF",info['f'].replace('MH','x'))



#    axis=ROOT.TAxis(10,array('d',[600,800,900,1000,1250,1500,2000,2500,3000,3500,4000]))
    axis=ROOT.TAxis(10,array('d',[600,650,700,750,800,900,1000,1250,1500,2000,2500]))

    graphs={'mean':ROOT.TGraphErrors(),'sigma':ROOT.TGraphErrors(),'alpha':ROOT.TGraphErrors(),'n':ROOT.TGraphErrors(),'alpha2':ROOT.TGraphErrors(),'n2':ROOT.TGraphErrors(),'f':ROOT.TGraphErrors(),'slope':ROOT.TGraphErrors()}

    for i in range(1,axis.GetNbins()+1):
    
        center=axis.GetBinCenter(i)
        h = data.drawTH1(options.varx,options.cut+"*({vary}>{mini}&&{vary}<{maxi})".format(vary=options.vary,mini=axis.GetBinLowEdge(i),maxi=axis.GetBinUpEdge(i)),str(options.lumi),options.binsx,options.minx,options.maxx) 

        histo=copy.deepcopy(h)
        fitter=Fitter(['M'])
        fitter.w.var("M").setVal((options.maxx-options.minx)/2.0)
        fitter.w.var("M").setMax(options.maxx)
        fitter.w.var("M").setMin(options.minx)
        if options.doExp>=0: ##MICHALIS CHANGED IT
            fitter.jetResonance('model','M')
            fitter.w.var("slope").setVal(slopeF.Eval(center))
            fitter.w.var("slope").setMin(-2)
            fitter.w.var("slope").setMax(2)
            fitter.w.var("slope").setConstant(0)
            fitter.w.var("f").setVal(fF.Eval(center))
            fitter.w.var("f").setMin(0)
            fitter.w.var("f").setMax(1.)
            fitter.w.var("f").setConstant(0)


        else:    
            fitter.jetResonanceNOEXP('model','M')

        fitter.w.var("mean").setVal(meanF.Eval(center))
        fitter.w.var("mean").setMin(meanF.Eval(center)*0.9)
        fitter.w.var("mean").setMax(meanF.Eval(center)*1.1)
        fitter.w.var("sigma").setVal(sigmaF.Eval(center))
        fitter.w.var("sigma").setMin(sigmaF.Eval(center)*0.5)
        fitter.w.var("sigma").setMax(sigmaF.Eval(center)*2)
#        fitter.w.var("alpha").setVal(alphaF.Eval(center))
        fitter.w.var("alpha").setVal(1.59049)
        fitter.w.var("alpha").setConstant(1)

        fitter.w.var("alpha2").setVal(1.3)
        fitter.w.var("alpha2").setConstant(1)


#        fitter.w.var("alpha2").setConstant(1)



        fitter.importBinnedData(histo,['M'],'data')   
        fitter.fit('model','data',[ROOT.RooFit.SumW2Error(1),ROOT.RooFit.Minos(0)])
        fitter.fit('model','data',[ROOT.RooFit.SumW2Error(1),ROOT.RooFit.Minos(1)])
        chi=fitter.projection("model","data","M","debugfitMJJTop_"+options.output+"_"+str(i)+".png")
    
        for var,graph in graphs.iteritems():
            value,error=fitter.fetch(var)
            graph.SetPoint(i-1,center,value)
            graph.SetPointError(i-1,0.0,error)

    F=ROOT.TFile(options.output+".root","RECREATE")
    F.cd()
    for name,graph in graphs.iteritems():
        graph.Write(name)
    F.Close()



#Initialize plotters


samples={}



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
            dataPlotters[-1].setupFromFile(args[0]+'/'+fname+'.pck')
            dataPlotters[-1].addCorrectionFactor('xsec','tree')
            dataPlotters[-1].addCorrectionFactor('genWeight','tree')
            dataPlotters[-1].addCorrectionFactor('puWeight','tree')
    
sigmas=[]
for d in dataPlotters:
    sigmas.append(d.tree.GetMaximum("xsec")/d.weightinv)
sigmaW=max(sigmas)
for p in dataPlotters:
    p.addCorrectionFactor(1.0/sigmaW,'flat')



data=MergedPlotter(dataPlotters)






graphs=runFits(data,options)
    
    
    



