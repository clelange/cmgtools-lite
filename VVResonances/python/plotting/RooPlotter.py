import ROOT
import copy

class RooPlotter(object):
    def __init__(self,filename):
        self.fIN=ROOT.TFile(filename)
        self.w=self.fIN.Get("w")
        self.contributions=[]
        self.fitResult=None

    def fix(self,var,val):
        self.w.var(var).setVal(val)
        self.w.var(var).setConstant(1)

    def prefit(self,model="s",minos=0,weighted=False,verbose=0):
        self.fitResult = self.w.pdf("model_"+model).fitTo(self.w.data("data_obs"),ROOT.RooFit.NumCPU(8),ROOT.RooFit.SumW2Error(weighted),ROOT.RooFit.Minos(minos),ROOT.RooFit.Verbose(verbose),ROOT.RooFit.Save(1))


    def addContribution(self,contrib,signal,description,linewidth,lineStyle,lineColor,fillStyle,fillColor,suffix=""):
        self.contributions.append({'name':contrib,'signal':signal,'description':description,'linewidth':linewidth,'linestyle':lineStyle,'linecolor':lineColor,'fillstyle':fillStyle,'fillcolor':fillColor,'suffix':suffix})


    def draw(self,var,varDesc,cat,blinded=[],doUncBand = False,log=False):
        self.canvas=ROOT.TCanvas("c")
        self.canvas.cd()
        varMax=self.w.var(var).getMax()
        varMin=self.w.var(var).getMin()
        varBins=self.w.var(var).getBins()
        #make frame
        self.frame=self.w.var(var).frame()

        if log:
            self.frame.GetYaxis().SetRangeUser(1e-2,1e+5)

        dataset=self.w.data("data_obs").reduce("CMS_channel==CMS_channel::"+cat)
        dataset.plotOn(self.frame,ROOT.RooFit.Name("datapoints"),ROOT.RooFit.Invisible())
        visError=False

        #make special binning for fats drawing


        #OK now stack for each curve add all the others
        for i in range(0,len(self.contributions)):
            data = self.contributions[i]
            print 'Plotting ',data['name']
            names=[]
            hasSignal=False
            for j in range(i,len(self.contributions)):
                if self.contributions[j]['signal']:
                    names.append('shapeSig_'+self.contributions[j]['name']+"_"+cat+self.contributions[j]['suffix'])
                    hasSignal=True
                else:
                    names.append('shapeBkg_'+self.contributions[j]['name']+"_"+cat+self.contributions[j]['suffix'])


            if (not visError) and (self.fitResult != None) and (not hasSignal) and doUncBand:
                self.w.pdf("model_s").getPdf(cat).plotOn(self.frame,ROOT.RooFit.Components(",".join(names)),ROOT.RooFit.Name('bkgError'),ROOT.RooFit.Invisible(),ROOT.RooFit.Normalization(1.0,ROOT.RooAbsReal.RelativeExpected),ROOT.RooFit.VisualizeError(self.fitResult))

                visError=True
                errorCurve=self.frame.getCurve('bkgError')
                errorCurve.SetLineColor(ROOT.kBlack)
                errorCurve.SetLineWidth(1)
                errorCurve.SetLineStyle(1)
                errorCurve.SetFillColor(ROOT.kBlack)
                errorCurve.SetFillStyle(3003)



            self.w.pdf("model_s").getPdf(cat).plotOn(self.frame,ROOT.RooFit.Components(",".join(names)),ROOT.RooFit.Name(data['name']),ROOT.RooFit.Invisible(),ROOT.RooFit.Normalization(1.0,ROOT.RooAbsReal.RelativeExpected))

            curve=self.frame.getCurve(data['name'])
            curve.SetLineColor(data['linecolor'])
            curve.SetLineWidth(data['linewidth'])
            curve.SetLineStyle(data['linestyle'])
            curve.SetFillColor(data['fillcolor'])
            curve.SetFillStyle(data['fillstyle'])


        self.frame.SetXTitle(varDesc)
        self.frame.SetYTitle("Events")

        #legend
        self.legend = ROOT.TLegend(0.62,0.6,0.92,0.90,"","brNDC")
	self.legend.SetBorderSize(0)
	self.legend.SetLineColor(1)
	self.legend.SetLineStyle(1)
	self.legend.SetLineWidth(1)
	self.legend.SetFillColor(0)
	self.legend.SetFillStyle(0)
	self.legend.SetTextFont(42)

        for c in self.contributions:
            name=c['name']
            desc=c['description']
            curve=self.frame.getCurve(name)
            self.legend.AddEntry(curve,desc,"f")



        self.frame.SetTitle("")
        self.frame.SetLabelSize(0.04,"X")
        self.frame.SetLabelSize(0.04,"Y")
        self.frame.SetTitleSize(0.05,"X")
        self.frame.SetTitleSize(0.05,"Y")
        self.frame.SetTitleOffset(0.90,"X")
        self.frame.SetTitleOffset(0.93,"Y")

        self.frame.Draw()
        for c in self.contributions:
            name=c['name']
            curve=self.frame.getCurve(name)
            curve.Draw("Fsame")
            curve.Draw("Lsame")

        if visError:
            curve=self.frame.getCurve('bkgError')
            curve.Draw("Fsame")



        hist=self.frame.getHist("datapoints")

        if len(blinded)==0:
            hist.Draw("Psame")
        elif len(blinded)==2:
            x=ROOT.Double(0.0)
            y=ROOT.Double(0.0)
            graph = hist.Clone()
            graph.SetName('tmpGRAPH')
            while hist.GetN()>0:
                hist.RemovePoint(0)
            N=0
            for i in range(0,graph.GetN()):
                graph.GetPoint(i,x,y)
                if x>blinded[0] and x< blinded[1]:
                    continue
                hist.SetPoint(N,x,y)
                hist.SetPointError(N,graph.GetErrorXlow(i),graph.GetErrorXhigh(i),graph.GetErrorYlow(i),graph.GetErrorYhigh(i))
                N=N+1
            hist.Draw("Psame")
        self.legend.Draw()
        if log:
            self.canvas.SetLogy(1)
        self.canvas.RedrawAxis()
        self.canvas.Update()








    def drawBinned(self,var,varDesc,cat,blinded=[],doUncBand = False,log=False,rangeStr=""):
        self.canvas=ROOT.TCanvas("c","",700,750)
        self.canvas.cd()
        self.pad1 = ROOT.TPad("pad1","",0.0,0.2,1.0,1.0,0)
        self.pad2 = ROOT.TPad("pad2","",0.0,0.0,1.0,0.2,0)
        self.pad1.Draw()
        self.pad2.Draw()
        self.pad1.cd()


        # varMax=self.w.var(var).getMax()
        varMax = 2500
        varMin=self.w.var(var).getMin()
        varBins=self.w.var(var).getBins()


        #make frame
        self.frame=self.w.var(var).frame()
        cutStr="CMS_channel==CMS_channel::"+cat
        dataset=self.w.data("data_obs").reduce(cutStr)

        projRange=[]
        if rangeStr!="":
            ranges=rangeStr.split(',')
            for r in ranges:
                rdata=r.split(':')
                self.w.var(rdata[0]).setRange(rdata[1],float(rdata[2]),float(rdata[3]))
                projRange.append(rdata[1])
                dataset=dataset.reduce("{var}>{mini}&&{var}<{maxi}".format(var=rdata[0],mini=rdata[2],maxi=rdata[3]))

        dataset.plotOn(self.frame,ROOT.RooFit.Name("datapoints"),ROOT.RooFit.Invisible())


        visError=False

        #make special binning for fats drawing
        binArray = self.w.var(var).getBinning().array()
        nBins = self.w.var(var).getBinning().numBins()
        axis = ROOT.TAxis(nBins,binArray)

        self.histoSum = ROOT.TH1D("histoSum","histo",nBins,binArray)
        self.bkgUncRatio=ROOT.TH1D(self.histoSum)

        #OK now stack for each curve add all the others
        backgrounds=[]
        for i in range(0,len(self.contributions)):
            data = self.contributions[i]
            print 'Plotting ',data['name']
            hasSignal=False
            if self.contributions[i]['signal']:
                name=('shapeSig_'+self.contributions[i]['name']+"_"+cat+self.contributions[i]['suffix'])
                hasSignal=True
            else:
                name=('shapeBkg_'+self.contributions[i]['name']+"_"+cat+self.contributions[i]['suffix'])
                backgrounds.append(name)



            if rangeStr=="":
                self.w.pdf("model_s").getPdf(cat).plotOn(self.frame,ROOT.RooFit.Components(name),ROOT.RooFit.Name(data['name']),ROOT.RooFit.Invisible(),ROOT.RooFit.Normalization(1.0,ROOT.RooAbsReal.RelativeExpected))
            else:
                self.w.pdf("model_s").getPdf(cat).plotOn(self.frame,ROOT.RooFit.Components(name),ROOT.RooFit.Name(data['name']),ROOT.RooFit.Invisible(),ROOT.RooFit.Normalization(1.0,ROOT.RooAbsReal.RelativeExpected),ROOT.RooFit.ProjectionRange(','.join(projRange)))


            curve=self.frame.getCurve(data['name'])
            histo = ROOT.TH1D("histo_"+name,"histo",nBins,binArray)
            histo.SetLineColor(data['linecolor'])
            histo.SetLineWidth(data['linewidth'])
            histo.SetLineStyle(data['linestyle'])
            histo.SetFillColor(data['fillcolor'])
            histo.SetFillStyle(data['fillstyle'])
            for j in range(1,histo.GetNbinsX()+1):
                x=histo.GetXaxis().GetBinCenter(j)
                histo.SetBinContent(j,curve.Eval(x))
            if not data['signal']:
                self.histoSum.Add(histo)
            self.contributions[i]['histo']=histo

        if (not visError) and (self.fitResult != None)  and doUncBand:
            if rangeStr=="":
                self.w.pdf("model_s").getPdf(cat).plotOn(self.frame,ROOT.RooFit.Components(",".join(backgrounds)),ROOT.RooFit.Name('bkgError'),ROOT.RooFit.Invisible(),ROOT.RooFit.Normalization(1.0,ROOT.RooAbsReal.RelativeExpected),ROOT.RooFit.VisualizeError(self.fitResult))
            else:
                self.w.pdf("model_s").getPdf(cat).plotOn(self.frame,ROOT.RooFit.Components(",".join(backgrounds)),ROOT.RooFit.Name('bkgError'),ROOT.RooFit.Invisible(),ROOT.RooFit.Normalization(1.0,ROOT.RooAbsReal.RelativeExpected),ROOT.RooFit.VisualizeError(self.fitResult),ROOT.RooFit.ProjectionRange(','.join(projRange)))


            visError=True
            errorCurve=self.frame.getCurve('bkgError')
            #create histo like error curve
            for i in range(1,self.histoSum.GetNbinsX()+1):
                x=self.histoSum.GetXaxis().GetBinCenter(i)
                bkg=self.histoSum.GetBinContent(i)
                self.histoSum.SetBinError(i,errorCurve.Eval(x)-self.histoSum.GetBinContent(i))
                self.bkgUncRatio.SetBinContent(i,1.0)
                self.bkgUncRatio.SetBinError(i,self.histoSum.GetBinError(i)/bkg)


            self.histoSum.SetFillColor(ROOT.kBlack)
            self.histoSum.SetFillStyle(3001)
            self.histoSum.SetLineColor(ROOT.kBlack)

            self.bkgUncRatio.SetFillColor(ROOT.kBlack)
            self.bkgUncRatio.SetFillStyle(3001)
            self.bkgUncRatio.SetLineColor(ROOT.kBlack)

        self.stack = ROOT.THStack("stack","")





        self.frame.SetXTitle(varDesc)
        self.frame.SetYTitle("Events")

        #legend
        self.legend = ROOT.TLegend(0.58,0.6,0.92,0.90,"","brNDC")
	self.legend.SetBorderSize(0)
	self.legend.SetLineColor(1)
	self.legend.SetLineStyle(1)
	self.legend.SetLineWidth(1)
	self.legend.SetFillColor(0)
	self.legend.SetFillStyle(0)
	self.legend.SetTextFont(42)

        self.legend.AddEntry(self.frame.getHist("datapoints"),"Data","P")
        if visError:
            self.legend.AddEntry(self.histoSum,"bkg. uncertainty","F")

        for i in range(len(self.contributions)-1,-1,-1):
            c=self.contributions[i]
            hist=c['histo']
            self.stack.Add(hist)
        for c in self.contributions:
            hist=c['histo']
            desc=c['description']
            self.legend.AddEntry(hist,desc,"LF")


        self.frame.SetTitle("")
        self.frame.SetLabelSize(0.04,"X")
        self.frame.SetLabelSize(0.04,"Y")
        self.frame.SetTitleSize(0.05,"X")
        self.frame.SetTitleSize(0.05,"Y")
#        self.frame.SetTitleOffset(0.90,"X")
        self.frame.SetTitleOffset(3,"X")
        self.frame.SetLabelOffset(3,"X")
        self.frame.SetTitleOffset(1.35,"Y")




        self.frame.Draw("AH")
#        self.frame.Draw("")

        self.stack.Draw("A,HIST,SAME")
        self.frame.GetXaxis().SetRangeUser(varMin, varMax)
        if log:
            self.frame.GetYaxis().SetRangeUser(0.3,1e+6)

        if visError:
            self.histoSum.Draw("E2,same")



        hist=self.frame.getHist("datapoints")
        hist.SetMarkerStyle(20)
        hist.SetLineWidth(2)
        if len(blinded)==0:
            hist.Draw("Psame")
        elif len(blinded)==2:
            x=ROOT.Double(0.0)
            y=ROOT.Double(0.0)
            graph = hist.Clone()
            graph.SetName('tmpGRAPH')
            while hist.GetN()>0:
                hist.RemovePoint(0)
            N=0
            for i in range(0,graph.GetN()):
                graph.GetPoint(i,x,y)
                if x>blinded[0] and x< blinded[1]:
                    continue
                hist.SetPoint(N,x,y)
                hist.SetPointError(N,graph.GetErrorXlow(i),graph.GetErrorXhigh(i),graph.GetErrorYlow(i),graph.GetErrorYhigh(i))
                N=N+1
            hist.Draw("Psame")

        self.legend.Draw()
        self.pad1.SetBottomMargin(0.012)
        self.pad1.SetLeftMargin(0.13)

        if log:
            self.pad1.SetLogy(1)
        self.pad1.RedrawAxis()
        self.pad1.Update()

        self.pad2.cd()
        #mke the ratio data/MC
        self.frame2=self.w.var(var).frame()
        self.frame2.SetTitle("")
        self.frame2.SetLabelSize(0.15,"X")
        self.frame2.SetLabelSize(0.15,"Y")
        self.frame2.SetTitleSize(0.18,"X")
        self.frame2.SetTitleSize(0.18,"Y")
        self.frame2.SetTitleOffset(0.90,"X")
        self.frame2.SetTitleOffset(0.3,"Y")

        self.frame2.Draw()
        self.frame2.GetYaxis().SetRangeUser(0.5,1.5)
        self.frame2.SetXTitle(varDesc)
        self.frame2.SetYTitle("Data/MC")
        self.frame2.GetYaxis().SetNdivisions(5+100*10)


        self.ratioGraph = ROOT.TGraphAsymmErrors(hist)

        x=ROOT.Double(0.)
        y=ROOT.Double(0.)
        for i in range(0,hist.GetN()):
            hist.GetPoint(i,x,y)
            bkgBin=self.histoSum.GetXaxis().FindBin(x)
            bkg=self.histoSum.GetBinContent(bkgBin)
            if y==0.0:
                continue
            self.ratioGraph.SetPoint(i,x,y/bkg)
            self.ratioGraph.SetPointError(i,0,0,hist.GetErrorYlow(i)/bkg,hist.GetErrorYhigh(i)/bkg)
        self.line=ROOT.TLine(varMin,1.0,varMax,1)
        self.line.SetLineWidth(2)
        self.line.Draw()
        if visError:
            self.bkgUncRatio.Draw("E2,same")
        self.ratioGraph.Draw("Psame")

        self.pad2.SetTopMargin(0.04)
        self.pad2.SetBottomMargin(0.5)
        self.pad2.SetLeftMargin(0.13)
        self.frame2.GetXaxis().SetRangeUser(varMin, varMax)

        self.pad2.RedrawAxis()
        self.pad2.Update()
