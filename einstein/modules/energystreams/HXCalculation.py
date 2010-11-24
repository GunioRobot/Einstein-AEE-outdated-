#from einstein.GUI.status import Status
import math


__author__="Andre Rattinger"
__date__ ="$02.08.2010 09:28:43$"

from einstein.modules.dataHR import *
from einstein.GUI.status import *
from einstein.modules.energystreams.Stream import *
from einstein.modules.energystreams.StreamGeneration import loadStreamData
#from einstein.modules.energystreams.StreamGeneration import *

def avg(List):
    return float(sum(List)) / len(List)

class HXCombination():
    def __init__(self):
        pass




    def combineAllStreams(self):
        for elem in Status.int.HXPinchConnection:
            if len(elem.sinkstreams) < 1:
                return -1
            if len(elem.sourcestreams) < 1:
                return -1
            print elem.HXID, elem.Name
            print "--------------------SINKSTREAMS TO COMBINE----------------------"
            for el in elem.sinkstreams:
                el.stream.printStream()
            print "--------------------END SINKSTREAMS-----------------------------"
            print "--------------------SOURCESTREAMS TO COMBINE--------------------"
            for el in elem.sourcestreams:
                el.stream.printStream()
            print "--------------------END SOURCESTREAMS---------------------------"
            """
            SINKS
            """
            elem.combinedSink = pinchTemp()
            self.combineStream(elem.combinedSink, elem.sinkstreams)
            pT = elem.combinedSink
            pT.outletTemp = self.combineSinkTempOut(elem.sinkstreams)
            pT.inletTemp = self.combineTempSink(elem.sinkstreams,pT.outletTemp, pT.stream.EnthalpyVector,\
                                                   pT.stream.MassFlowVector, pT.stream.SpecHeatCap)

            pT.stream.OperatingHours = self.combineOperatingHours(elem.sinkstreams)
            pT.stream.MassFlowAvg = self.combineMassFlowNom(elem.sinkstreams)


#            print "PercentHeatFlow: " + str(type(elem.sinkstreams[0].percentHeatFlow))
            if len(elem.sinkstreams)==1:
                pT.percentHeatFlow = elem.sinkstreams[0].percentHeatFlow
            elif len(elem.sinkstreams)>1:
                pT.percentHeatFlow = 100

#            try:
#                print "InletTemp: " + str(pT.inletTemp[0:100])
#                print "OutletTemp: " + str(pT.outletTemp)
#            except:
#                print "InletTemp: " + str(pT.inletTemp)
#                print "OutletTemp: " + str(pT.outletTemp)

            elem.combinedSink.stream.printStream()
            """
            SOURCES
            """
            elem.combinedSource = pinchTemp()
            self.combineStream(elem.combinedSource, elem.sourcestreams)
            pT = elem.combinedSource
            pT.inletTemp = self.combineTempIn(elem.sourcestreams)
            pT.outletTemp = self.combineTempSource(pT.inletTemp, pT.stream.EnthalpyVector, \
                                                 pT.stream.MassFlowVector, pT.stream.SpecHeatCap)

            pT.stream.OperatingHours = self.combineOperatingHours(elem.sourcestreams)
            pT.stream.MassFlowAvg = self.combineMassFlowNom(elem.sourcestreams)

            if len(elem.sourcestreams)==1:
                pT.percentHeatFlow = elem.sourcestreams[0].percentHeatFlow
            elif len(elem.sourcestreams)>1:
                pT.percentHeatFlow = 100

#            try:
#                print "InletTemp: " + str(pT.inletTemp[0:100])
#                print "OutletTemp: " + str(pT.outletTemp)
#            except:
#                print "InletTemp: " + str(pT.inletTemp)
#                print "OutletTemp: " + str(pT.outletTemp)
            elem.combinedSource.stream.printStream()

#            print "MassFlowVectorSink: ", str(pT.stream.MassFlowVector[0:200])
        return 0

    def combineMassFlowNom(self, sstreams):
        massflow = 0
        for elem in sstreams:
            print elem.stream.name
            if elem.stream.MassFlowAvg != None:
                massflow += elem.stream.MassFlowAvg
        if len(sstreams) != 0:
            massflow /= len(sstreams)
        return massflow

    def combineOperatingHours(self, sstreams):
        OperatingHours = 0
        for elem in sstreams:
#            print elem.stream.name
            if elem.stream.OperatingHours != None:
                OperatingHours += elem.stream.OperatingHours
        if len(sstreams) != 0:
            OperatingHours /= len(sstreams)
        return OperatingHours

#self.combineStream(elem.combinedSink, elem.sinkstreams)
    def combineStream(self, comb, sstream):
            comb.stream = Stream()
            comb.stream.name = "CombinedStream"
            self.loadVector(sstream)
            comb.stream.EnthalpyVector = self.combineEnthalpy(sstream)
            for el in sstream:
                el.stream.printStream()

            comb.stream.MassFlowVector = self.combineMassFlow(sstream)
            comb.stream.SpecHeatCap = self.combineSpecificHeatCap(sstream)

    def loadVector(self, sstream):
        for elem in sstream:
            loadStreamData(elem.stream)


    def combineEnthalpy(self, pinchstreams):
        combH = []
        if pinchstreams == None or len(pinchstreams) == 0:
            print "No Pinchstream in Enthalpy"
            return combH

        if pinchstreams[0].stream == None:
            print "No Stream in pinchstream in Enthalpy"
            return combH

        if pinchstreams[0].stream.EnthalpyVector == None:
            print "No EnthalpyVector exists: " + str(pinchstreams[0].stream.name)
            print "Vector: " + str(pinchstreams[0].stream.EnthalpyVector)
            return combH
        
#        print "Len of Elements Pinchstream CombEnthalpy: ", str(len(pinchstreams))
        
        if len(pinchstreams)==1:
            
            for i in xrange(Status.Nt):
                combH.append(pinchstreams[0].stream.EnthalpyVector[i] * pinchstreams[0].percentHeatFlow/100)
            
#            for i in xrange(Status.Nt):
#                st = pinchstreams[0].stream
#                ps = pinchstreams[0]
#                combH.append(0)
#                if st.HotColdType == "Sink" or st.HotColdType == "Cold":
#                    if ps.outletTemp != None and ps.outletTemp <= st.EndTemp.getAvg():
#                        pinchstreams[0].stream.EnthalpyVector[i] = (st.EnthalpyVector[i]/(st.EndTemp.getAvg()-st.StartTemp.getAvg()))\
#                        *(ps.outletTemp-st.StartTemp.getAvg())
#                elif st.HotColdType == "Source" or st.HotColdType == "Hot":
#                    if st.MassFlowVector[i]!=0:
#                        pinchstreams[0].outletTemp = ps.inletTemp-st.EnthalpyVector[i]/(st.MassFlowVector[i]*st.SpecHeatCap)
#                    #else:
#                        #pinchstreams[0].outletTemp = pinchstreams[0].inletTemp
#                    if ps.outletTemp != None and ps.outletTemp < st.EndTemp.getAvg() and st.StartTemp.getAvg()!=st.EndTemp.getAvg():
#                        pinchstreams[0].stream.EnthalpyVector[i] = (st.EnthalpyVector[i]/(st.StartTemp.getAvg()-st.EndTemp.getAvg()))\
#                        *(ps.inletTemp-st.EndTemp.getAvg())
##                        print pinchstreams[0].outletTemp, pinchstreams[0].inletTemp
#                combH[i] += st.EnthalpyVector[i]*(ps.percentHeatFlow/100)
        else:

            for i in xrange(Status.Nt):
                combH.append(0)
                for elem in pinchstreams:
                    stream = elem.stream
                    if elem.stream.HotColdType == "Sink" or elem.stream.HotColdType == "Cold":
                        if elem.outletTemp != None and elem.outletTemp <= elem.stream.EndTemp.getAvg():
                            stream.EnthalpyVector[i] = (stream.EnthalpyVector[i]/(elem.stream.EndTemp.getAvg()-elem.stream.StartTemp.getAvg()))\
                            *(elem.outletTemp-elem.stream.StartTemp.getAvg())
                        if elem.outletTemp != None and elem.inletTemp >= elem.stream.StartTemp.getAvg():
                            stream.EnthalpyVector[i] = (stream.EnthalpyVector[i]/(elem.stream.EndTemp.getAvg()-elem.stream.StartTemp.getAvg()))\
                            *(elem.stream.EndTemp.getAvg()-elem.inletTemp)
                    elif elem.stream.HotColdType == "Source" or elem.stream.HotColdType == "Hot":
                        if elem.stream.MassFlowVector[i]!=0:
                            elem.outletTemp = elem.inletTemp-stream.EnthalpyVector[i]/(elem.stream.MassFlowVector[i]*elem.stream.SpecHeatCap)
                        #else:
                            #elem.outletTemp = elem.inletTemp
                        if elem.outletTemp != None and elem.outletTemp < elem.stream.EndTemp.getAvg() and elem.stream.StartTemp.getAvg()!=elem.stream.EndTemp.getAvg():
                            stream.EnthalpyVector[i] = (stream.EnthalpyVector[i]/(elem.stream.StartTemp.getAvg()-elem.stream.EndTemp.getAvg()))\
                            *(elem.inletTemp-elem.stream.EndTemp.getAvg())
                        if elem.outletTemp != None and elem.outletTemp < elem.stream.EndTemp.getAvg() and elem.stream.StartTemp.getAvg()!=elem.stream.EndTemp.getAvg():
                            stream.EnthalpyVector[i] = (stream.EnthalpyVector[i]/(elem.stream.StartTemp.getAvg()-elem.stream.EndTemp.getAvg()))\
                            *(elem.stream.StartTemp.getAvg()-elem.outletTemp)
    #                        print elem.outletTemp, elem.inletTemp
                    combH[i] += stream.EnthalpyVector[i]*(float(elem.percentHeatFlow)/100)
        
        print "Combined H: ", str(sum(combH))
        return combH


    def combineTempIn(self, pinchstreams):
        """
        for Sources
        """
        TIn = 0
        div = 0
        for elem in pinchstreams:

            if elem.InTempActive:
                inTemp = elem.inletTemp
                #check if temperature is in possible range
                if inTemp > elem.stream.StartTemp.getAvg():
                    inTemp=elem.stream.StartTemp.getAvg()
            
            else:
                inTemp = 0
                """
                GET OUTLET OF HX
                elem.outletHX
                """
            TIn += inTemp*elem.stream.MassFlowAvg
            div +=elem.stream.MassFlowAvg
        if div == 0:
            return 0
        return TIn/div


#            pT.inletTemp = self.combineTemp(pT.outletTemp, pT.stream.EnthalpyVector,\
#                                                   pT.stream.MassFlowVector, pT.stream.SpecHeatCap)
    def combineTempSource(self, T, Hcomb, mcomb, cpcomb):
        Treturn = []
        for i in xrange(Status.Nt):
            Treturn.append(0)
            if mcomb[i] == 0 or cpcomb == 0:
                Treturn[i] = T

            else: Treturn[i] = T - Hcomb[i]/(mcomb[i]*cpcomb)
            
        return Treturn

    def combineTempSink(self, pinchstreams, T, Hcomb, mcomb, cpcomb):
        Treturn = []

        mw = self.combineTempIn(pinchstreams)
        
        for i in xrange(Status.Nt):
            Treturn.append(0)
            if mcomb[i] == 0 or cpcomb == 0:
                Treturn[i] = mw

            else: Treturn[i] = T - Hcomb[i]/(mcomb[i]*cpcomb)
            
        
        return Treturn


#    def combineTemp(self, TOut, Hcomb, mcomb, cpcomb):
#        pass

    def combineSinkTempOut(self, pinchstreams):
        """
        for SINKS
        """
        try:
            if pinchstreams[0].OutTempActive:
                TOut = pinchstreams[0].outletTemp
            else:
                TOut = 0
                """
                GET INLET OF HX
                elem.inletHX
                """
        except:
            return 0

        for elem in pinchstreams:
            if elem.OutTempActive:
                outTemp = elem.outletTemp
                #check if temperature is in possible range
                if outTemp > elem.stream.EndTemp.getAvg():
                    outTemp=elem.stream.EndTemp.getAvg()
            else:
                outTemp = 0
                """
                GET OUTLET OF HX
                elem.outletHX
                """
            if outTemp > TOut:
                TOut = outTemp
        return TOut

    def combineMassFlow(self, pinchstreams):

        if pinchstreams == None or len(pinchstreams) == 0:
            print "No Pinchstream in Massflow"
            return
        if pinchstreams[0].stream == None:
            return
            print "No Stream in pinchstream in Massflow"
        if pinchstreams[0].stream.EnthalpyVector == None:
            print "No MassFlowVector exists: " + str(pinchstreams[0].stream.name)
            print "Vector: " + str(pinchstreams[0].stream.EnthalpyVector)
            return

        if len(pinchstreams) == 1:
            combM = [x*pinchstreams[0].percentHeatFlow/100 for x in pinchstreams[0].stream.MassFlowVector]
            
        else:
            for elem in pinchstreams:
                print "MassFlow in Combination: ", str(elem.stream.MassFlowVector[0:100])
                print "percentHeatFlow in Combination: ", str(elem.percentHeatFlow)
                
            combM = [0]*Status.Nt
            for i in xrange(Status.Nt):
                for elem in pinchstreams:
                    combM[i] += (elem.stream.MassFlowVector[i]*(float(elem.percentHeatFlow)/100))
                    if i < 200:
                        print "MassFlow: " , elem.stream.MassFlowVector[i]
                        print "PercentHeatFlow: ", float(elem.percentHeatFlow/100)
                        print "combM: ", str(combM[i])
                        print 
            
            
#            combM = [None]*Status.Nt
#            
#            for i in xrange(Status.Nt):
#    #            combM.append(0)
#                MassFlow = 0
#                for elem in pinchstreams:
##                    print "MassFlowVector: ", str(elem.stream.MassFlowVector[i]), str(elem.percentHeatFlow), str(MassFlow)
#                    MassFlow = MassFlow + elem.stream.MassFlowVector[i]*(elem.percentHeatFlow/100)
#                
#                combM[i] = MassFlow 
    
        return combM


    def combineSpecificHeatCap(self, pinchstreams):
        cp = 0
        m = 0
        for elem in pinchstreams:
            stream = elem.stream
            cp += stream.MassFlowAvg * stream.SpecHeatCap
            m += stream.MassFlowAvg

        if m == 0:
            return 0
        return cp/m


class HXSimulation():

    Thsin = None
    Tcsin = None
    Q = None
    Energy = None
    Thsout = None
    Tcsout = None
    UA = None
    hxPinchCon= None


    def __init__(self, Thsin, Tcsin, Q=None, Energy=None, Thsout=None, Tcsout=None, UA=10000, hxPinchCon = None):
        self.Thsin = self.toList(Thsin, Status.Nt)
        self.Tcsin = self.toList(Tcsin, Status.Nt)
#        print "init Tcsin: " + str(self.Tcsin)
        self.Q = Q
        self.Energy = Energy
        self.Thsout = self.toList(Thsout, Status.Nt)
        self.Tcsout = self.toList(Tcsout, Status.Nt)
        self.UA = 10000
        self.hxPinchCon = hxPinchCon
        if hxPinchCon.combinedSource.percentHeatFlow != None:
            self.bhxhs = self.toList(hxPinchCon.combinedSource.percentHeatFlow, Status.Nt)
        else: self.bhxhs = self.toList(1, Status.Nt)
        if hxPinchCon.combinedSink.percentHeatFlow != None:
            self.bhxcs = self.toList(hxPinchCon.combinedSink.percentHeatFlow, Status.Nt)
        else: self.bhxcs = self.toList(1, Status.Nt)
        self.dTmin = 5
        self.QHX1hs = None
        self.QHX1cs = None
        self.StorageSize=0

        self.data = HRData(Status.PId,Status.ANo)
        self.mod = Status.mod.moduleHR


    def toList(self, value, length):
        if type(value) == type([]): return value
        if type(value) == type({}): return value
        list = [value]*length

        return list



    def setValues(self, Thsin, Tcsin, Q=None, Energy=None, Thsout=None, Tcsout=None, UA=10000, hxPinchCon = None):
        self.Thsin = Thsin
        self.Tcsin = Tcsin
        self.Q = Q
        self.Energy = Energy
        self.Thsout = Thsout
        self.Tcsout = Tcsout
        self.UA = UA

        # Values to get:
#        self.QHXVector = None
        self.dTmin = 5
        self.dThs = None
        self.dTcs = None
        self.QStorage = None
        self.StorageSize=0

    def startSimulation(self):
#        self.getStartQHXVector()
        self.printCombinedHX()
        self.__checkStartValues()
        self.__doBasicCalculation()
        
    def printCombinedHX(self):
        Sink = self.hxPinchCon.combinedSink
        Source = self.hxPinchCon.combinedSource
        self.printHXPinch(Sink)
        self.printHXPinch(Source)
        
    def printHXPinch(self, st):
        print "InletTemp: ", st.inletTemp
        print "OutletTemp: ", st.outletTemp
        print "PercentHeatFlow:", st.percentHeatFlow
        print "MassFlowVector:", str(st.stream.MassFlowVector[0:100])
        print "SpecHeatCap:", str(st.stream.SpecHeatCap)
        
        
    def __doBasicCalculation(self):
        if (self.Thsout != None and self.Tcsout != None) or (self.bhxcs == None and self.bhxhs == None):
            
            print "CheckThsoutVector"
            self.checkThsoutVector()
            self.printBasicValues()
            print "CheckTcsoutVector"
            self.checkTcsoutVector()
            self.printBasicValues()
            print "CalculateHXoverHS"
            self.calculateHXoverHS()
            self.printBasicValues()
            print "CalculateHXoverCS"
            self.calculateHXoverCS()
            self.printBasicValues()
            print "CheckQHX"
            self.checkQHX()
            self.printBasicValues()
            print "QHXcs Sum:", str(sum(self.QHX1cs))
            print "QHXhs Sum:", str(sum(self.QHX1hs))
            self.dThs = self.calculateDThs()
            print "CalculateQStorage"
            self.calculateQStorage()
            self.printBasicValues()
            print "CalculateTcsoutOverHXStorage"
            self.calculateTcsoutOverHXStorage()
            self.printBasicValues()
            print "adaptTcsout"
            self.adaptTcsout()
            self.printBasicValues()
            print "QHXcs Sum:", str(sum(self.QHX1cs))
            print "QHXhs Sum:", str(sum(self.QHX1hs))
            print "calculateThsoutOverHX"
            self.calculateThsoutOverHX()
            self.printBasicValues()
            print "adaptThsout"
            self.adaptThsout()
            self.printBasicValues()
            print "calculateHXOverUA"
            self.calculateHXoverUA()
            self.printBasicValues()
            print "CheckQ"
            self.checkQ()
#            print "Q: " + str(self.Q)
            
            print "Finished Basic Calculation"
            print "QHXcs Sum:", str(sum(self.QHX1cs))
            print "QHXhs Sum:", str(sum(self.QHX1hs))
            
            self.doPostProcess()
            
            Tcsin = avg(self.Tcsin)
            Tcsout = avg(self.Tcsout)
            Thsin = avg(self.Thsin)
            Thsout = avg(self.Thsout)

            
#            self.startPostProcess()
            Status.int.hrdata.storeHXData(self.hxPinchCon, self.QHX1cs, self.UA, max(self.Tloghx), Tcsin, Tcsout, 
                                          Thsin, Thsout, self.inletTSink, self.outletTSink, self.HeatFlowPercentSink, self.inletTSource,
                                          self.outletTSource, self.HeatFlowPercentSource, round(self.StorageSize,2))
            
            
            QHXSinkProc, QHXSinkEq, QHXSinkWh, QHXSinkDist = self.getQHX(self.hxPinchCon.sinkstreams, self.Tcsin, self.Tcsout, self.bhxcs)
            QHXSourceProc, QHXSourceEq, QHXSourceWh, QHXSourceDist = self.getQHX(self.hxPinchCon.sourcestreams, self.Thsin, self.Thsout, self.bhxhs)
            
            print "QHXcs Sum:", str(sum(self.QHX1cs))
            print "QHXhs Sum:", str(sum(self.QHX1hs))
            print "QHXSinkProc: ", str(QHXSinkProc[0:200])
            print "QHXSinkProc Sum: ", str(sum(QHXSinkProc))
            print "QHXSinkEq: ", str(QHXSinkEq[0:200])
            print "QHXSinkEq Sum: ", str(sum(QHXSinkEq))
            print "QHXSinkWh: ", str(QHXSinkWh[0:200])
            print "QHXSinkWh Sum: ", str(sum(QHXSinkWh))
            print "QHXSinkDist: ", str(QHXSinkDist[0:200])
            print "QHXSinkDist Sum: ", str(sum(QHXSinkDist))
            
            print "QHXSourceProc: ", str(QHXSourceProc[0:200])
            print "QHXSourceProc Sum: ", str(sum(QHXSourceProc))
            print "QHXSourceEq: ", str(QHXSourceEq[0:200])
            print "QHXSourceEq Sum: ", str(sum(QHXSourceEq))
            print "QHXSourceWh: ", str(QHXSourceWh[0:200])
            print "QHXSourceWh Sum: ", str(sum(QHXSourceWh))
            print "QHXSourceDist: ", str(QHXSourceDist[0:200])
            print "QHXSourceDist Sum: ", str(sum(QHXSourceDist))
            
            
#            for elem in Status.int.HXPinchConnection: 
#                elem.combinedSink.inletTemp = max(elem.combinedSink.inletTemp)
#                elem.combinedSource.outletTemp = max(elem.combinedSource.outletTemp)
                
            self.mod.doHXPostProcessing(QHXSinkProc, QHXSinkEq, QHXSinkWh, QHXSinkDist,
                                        QHXSourceProc, QHXSourceEq, QHXSourceWh, QHXSourceDist)



        elif (self.Thsout == None and self.Tcsout == None) or (self.bhxcs != None and self.bhxhs != None):
            self.calculateThsoutOverTcsin()
            self.calculateTcsoutOverThsin()
            self.calculateHXoverHS()
            self.calculateHXoverCS()
            self.adaptQHX()
            self.calculateHXoverHS()
            self.calculateHXoverCS()
            self.calculateQStorage()

            #Recalculate:
    
    
    
    def doPostProcess(self):
        self.postProcessSink()
        self.postProcessSource()
    
    def postProcessSource(self):      
        bhxhs = round(self.getNonZeroMax(self.bhxhs, self.QHX1hs),2)
        bhxcs = round(self.getNonZeroMax(self.bhxcs, self.QHX1cs),2)
        if len(self.hxPinchCon.sourcestreams)>1:
            self.outletTSource = []
            QHX_total = max(self.QHX1hs)
            combined = self.hxPinchCon.combinedSink
            self.HeatFlowPercentSource = []
            self.inletTSource = []
            for elem in self.hxPinchCon.sourcestreams:
                self.inletTSource.append(elem.inletTemp)
                
                QHXperStream = 0
                combinedMassFlowAvg=0
                combinedMassFlowAvg = round(self.getNonZeroAverage(combined.stream.MassFlowVector, self.QHX1hs),2)
    
                if (combinedMassFlowAvg*combined.stream.SpecHeatCap) == 0:
                    QHXperStream = 0
                else:    
                    QHXperStream = QHX_total*elem.stream.SpecHeatCap\
                                        *elem.stream.MassFlowAvg*(bhxhs/100)/(combinedMassFlowAvg\
                                        *combined.stream.SpecHeatCap)
                if (elem.stream.MassFlowAvg*elem.stream.SpecHeatCap) == 0:
                    elem.outletTemp = 0
                else:
                    if (elem.stream.MassFlowAvg*(bhxcs/100)*elem.stream.SpecHeatCap) != 0:
                        elem.outletTemp = elem.inletTemp - \
                            QHXperStream/(elem.stream.MassFlowAvg*(bhxhs/100)*elem.stream.SpecHeatCap)
                    else: elem.outletTemp = 0
                    self.outletTSource.append(elem.outletTemp)
                    self.HeatFlowPercentSource.append(bhxhs)
                                        
        elif len(self.hxPinchCon.sourcestreams)==1:
            thsin = round(self.getNonZeroAverage(self.Thsin, self.QHX1hs),2)
            thsout = round(self.getNonZeroAverage(self.Thsout, self.QHX1hs),2)
            self.inletTSource = [thsin]
            self.outletTSource = [thsout]
            # auf max setzen
            self.HeatFlowPercentSource = [round(max(self.bhxhs),2)]
#                self.HeatFlowPercentSource = [sum(self.bhxhs)/len(self.bhxhs)]
        else:
            self.inletTSource = [0]
            self.outletTSource = [0]
            self.HeatFlowPercentSource = [0]
                
                
    def postProcessSink(self):
        bhxhs = round(self.getNonZeroMax(self.bhxhs, self.QHX1hs),2)
        bhxcs = round(self.getNonZeroMax(self.bhxcs, self.QHX1cs),2)

        if len(self.hxPinchCon.sinkstreams)>1:
            # Insert List of new inlet/outletTemp in the right order
            # inletTSink = [sinktemp1, sinktemp2, ...]
            self.inletTSink = []
            QHX_total = max(self.QHX1hs)
            combined = self.hxPinchCon.combinedSink
            self.outletTSink = []
            self.HeatFlowPercentSink = []
            for elem in self.hxPinchCon.sinkstreams:
                self.inletTSink.append(elem.inletTemp)
                
                QHXperStream = 0
                combinedMassFlowAvg=0
                combinedMassFlowAvg = round(self.getNonZeroAverage(combined.stream.MassFlowVector, self.QHX1cs),2)
                
                if (combinedMassFlowAvg*combined.stream.SpecHeatCap) == 0:
                    QHXperStream = 0
                else:    
                    QHXperStream = QHX_total*elem.stream.SpecHeatCap\
                                        *elem.stream.MassFlowAvg*(bhxcs/100)/(combinedMassFlowAvg\
                                        *combined.stream.SpecHeatCap)
                if (elem.stream.MassFlowAvg*elem.stream.SpecHeatCap) == 0:
                    elem.outletTemp = 0
                else:
                    if (elem.stream.MassFlowAvg*(bhxcs/100)*elem.stream.SpecHeatCap) != 0:
                        elem.outletTemp = elem.inletTemp + \
                            QHXperStream/(elem.stream.MassFlowAvg*(bhxcs/100)*elem.stream.SpecHeatCap)
                    else: elem.outletTemp = 0
                    self.outletTSink.append(elem.outletTemp)
                    self.HeatFlowPercentSink.append(bhxcs)
                
                
        elif len(self.hxPinchCon.sinkstreams)==1:
            tcsin = round(self.getNonZeroAverage(self.Tcsin, self.QHX1cs),2)
            tcsout = round(self.getNonZeroAverage(self.Tcsout, self.QHX1cs),2)
            self.inletTSink = [tcsin]
            self.outletTSink = [tcsout]
            self.HeatFlowPercentSink = [round(max(self.bhxcs),2)]
#                self.HeatFlowPercentSink = [sum(self.bhxcs)/len(self.bhxcs)]
        else:
            self.inletTSink = [0]
            self.outletTSink = [0]
            self.HeatFlowPercentSink = [0]
    
    
    def getQHX(self, type, Tin, Tout, bhx):
        QHXProc =[0]*Status.Nt
        QHXEq = [0]*Status.Nt
        QHXWh = [0]*Status.Nt
        QHXDist = [0]*Status.Nt
        for el in type:
            if el.stream.Source == STREAMSOURCE[0] or el.stream.Source == STREAMSOURCE[1]:
                for i in xrange(len(QHXProc)):
                    """
                    temperature difference from heat exchanger is taken, this is in line when sink=1 stream
                    when sink includes several streams, temperatures per stream are recalculated above
                    temperature difference still remains the same
                    """
                    QHXProc[i] += el.stream.MassFlowVector[i]*el.stream.SpecHeatCap*bhx[i]/100*\
                                    abs(Tin[i]-Tout[i])
                                    
            elif el.stream.Source == STREAMSOURCE[2]:
                for i in xrange(len(QHXEq)):
                    QHXEq[i] += el.stream.MassFlowVector[i]*el.stream.SpecHeatCap*bhx[i]/100*\
                                    abs(Tin[i]-Tout[i])
                    
            elif el.stream.Source == STREAMSOURCE[3]:
                for i in xrange(len(QHXWh)):
                    QHXWh[i] += el.stream.MassFlowVector[i]*el.stream.SpecHeatCap*bhx[i]/100*\
                                    abs(Tin[i]-Tout[i])
            elif el.stream.Source == STREAMSOURCE[4]:
                for i in xrange(len(QHXDist)):
                    QHXDist[i] += el.stream.MassFlowVector[i]*el.stream.SpecHeatCap*bhx[i]/100*\
                                    abs(Tin[i]-Tout[i])
        return QHXProc, QHXEq, QHXWh, QHXDist

    def startPostProcess(self):
        # Split Stream results
        
 #       bhxhs = sum(self.bhxhs)/len(self.bhxhs)
 #       bhxcs = sum(self.bhxcs)/len(self.bhxcs)
        
        bhxhs = round(self.getNonZeroMax(self.bhxhs, self.QHX1hs),2)
        bhxcs = round(self.getNonZeroMax(self.bhxcs, self.QHX1cs),2)
        
        for i in xrange(len(Status.int.HXPinchConnection)):
            if len(Status.int.HXPinchConnection[i].sourcestreams)>1:
                for j in xrange(len(Status.int.HXPinchConnection[i].sourcestreams)):
                    source = Status.int.HXPinchConnection[i].sourcestreams[j]
                    self.splitStreamResults(Status.int.HXPinchConnection[i].combinedSource, source, bhxcs)
            else: Status.int.HXPinchConnection[i].sourcestreams[0].PercentHeatFlow = bhxhs
            if len(Status.int.HXPinchConnection[i].sinkstreams)>1:
                for j in xrange(len(Status.int.HXPinchConnection[i].sinkstreams)):
                    sink = Status.int.HXPinchConnection[i].sinkstreams[j]
                    self.splitStreamResults(Status.int.HXPinchConnection[i].combinedSink, sink, bhxhs)
            else: Status.int.HXPinchConnection[i].sinkstreams[0].PercentHeatFlow = bhxcs    
        
        for elem in Status.int.HXPinchConnection:
            elem.deleteFromDB()
            elem.writeToDB()

        
    def splitStreamResults(self, combined, hxstream, bhx):
        
        #hxstream.stream.MassFlowAvg *= bhx/100
        QHX_total = max(self.QHX1hs)
        
        QHXperStream = 0
        
        combinedMassFlowAvg=0
        combinedMassFlowAvg = round(self.getNonZeroAverage(combined.stream.MassFlowVector, self.QHX1cs),2)
        
        QHXperStream = QHX_total*hxstream.stream.SpecHeatCap\
                *hxstream.stream.MassFlowAvg/(combinedMassFlowAvg\
                *combined.stream.SpecHeatCap)
        if (hxstream.stream.MassFlowAvg*hxstream.stream.SpecHeatCap) == 0:
            hxstream.outletTemp = 0
        else:
            if hxstream.stream.HotColdType == "Cold" or hxstream.stream.HotColdType == "Sink":
                hxstream.outletTemp = hxstream.inletTemp + \
                QHXperStream/(hxstream.stream.MassFlowAvg*hxstream.stream.SpecHeatCap)
            else:
                hxstream.outletTemp = hxstream.inletTemp - \
                QHXperStream/(hxstream.stream.MassFlowAvg*hxstream.stream.SpecHeatCap)
    


    def printBasicValues(self):
        if self.QHX1hs != None:
            print "QHX1hs: " + str(self.QHX1hs[0:200])
        if self.QHX1cs != None:
            print "QHX1cs: " + str(self.QHX1cs[0:200])
        print "Tcsout: " + str(self.Tcsout[0:200])
        print "Thsout: " + str(self.Thsout[0:200])
        print "bhxcs: " + str(self.bhxcs[0:200])
        print "bhxhs: " + str(self.bhxhs[0:200])
#        print "" + str()

    def getNonZeroAverage(self, T, Q):
        t = []
        for i in xrange(Status.Nt):
            if Q[i] != 0:
                t.append(T[i])
        if len(t)==0: return 0
        return sum(t)/len(t)
    
    def getNonZeroMax(self, T, Q):
        """
        T: Split Factor
        """
        t = []
        for i in xrange(Status.Nt):
            if Q[i] != 0:
                t.append(T[i])
        if len(t)==0: return 0
        return max(t)
    

    def adaptQHX(self):
        for i in xrange(Status.Nt):
            if self.QHX1hs[i] > self.QHX1cs[i]:
                if type(self.Thsin)==type([]):
                    self.Thsout[i]=self.Thsin[i]
                else:
                    self.Thsout[i]=self.Thsin
                if type(self.Tcsin)==type([]):
                    Td = self.Tcsin[i]+self.dTmin
                else:
                    Td = self.Tcsin + self.dTmin
                if type(self.Tcsout)==type([]):
                    T = self.Tcsout[i]-Td
                else:
                    T = self.Tcsout-Td
                self.Tcsout[i]=self.Tcsout[i]-(T*self.mcs[i]*self.cpcs*self.bhxcs[i]/100)/(self.mhs[i]*self.cphs*self.bhxhs[i]/100)

            elif self.QHX1hs[i] < self.QHX1cs[i]:
                if type(self.Tcsin)==type([]):
                    self.Tcsout[i]=self.Tcsin[i]
                else:
                    self.Tcsout[i]=self.Tcsin
                if type(self.Thsin)==type([]):
                    Td = self.Thsin[i]+self.dTmin
                else:
                    Td = self.Thsin + self.dTmin
                if type(self.Thsout)==type([]):
                    T = Td-self.Thsout[i]
                else:
                    T = Td-self.Tcsout

                self.Tcsout = self.Tcsout + (T*self.mhs[i]*self.cphs*self.bhxhs[i]/100)/(self.mcs[i]*self.cpcs*self.bhxcs[i]/100)



    def calculateThsoutOverTcsin(self):
        if type(self.Tcsin)==type([]):
            self.Thsout=[]
            for elem in self.Tcsin:
                self.Thsout.append(elem + self.dTmin)
        elif type(self.Tcsin)==type(1):
            self.Thsout = self.Tcsin + self.dTmin

    def calculateTcsoutOverThsin(self):
        if type(self.Thsin)==type([]):
            self.Tcsout=[]
            for elem in self.Thsin:
                self.Tcsout.append(elem - self.dTmin)
        elif type(self.Thsin)==type(1):
            self.Tcsout = self.Thsin - self.dTmin

    def checkQ(self):
        self.UA = [self.UA]*Status.Nt
        for i in xrange(Status.Nt):
            if self.UA[i] * self.Tloghx[i] != self.QHX1cs[i]:
                self.UA[i] = self.QHX1cs[i]/self.Tloghx[i]
        self.UA = max(self.UA)
        
    def checkQHX(self):

        mhs = self.hxPinchCon.combinedSource.stream.MassFlowVector
        cphs = self.hxPinchCon.combinedSource.stream.SpecHeatCap
        mcs = self.hxPinchCon.combinedSink.stream.MassFlowVector
        cpcs = self.hxPinchCon.combinedSink.stream.SpecHeatCap
        dThs = self.calculateDThs()
        dTcs = self.calculateDTcs()

        if type(self.bhxhs) != type([]):
            self.bhxhs = [self.bhxhs]*Status.Nt
        if type(self.bhxcs) != type([]):
            self.bhxcs = [self.bhxcs]*Status.Nt

        self.mhshx1 = [0]*Status.Nt
        self.mcshx1 = [0]*Status.Nt


        for i in xrange(Status.Nt):
            if self.QHX1hs[i] != self.QHX1cs[i]:
                if self.QHX1hs[i] > self.QHX1cs[i]:

                    if type(self.Thsin)==type([]):
                        Thsin = self.Thsin[i]
                    else: Thsin = self.Thsin

                    if type(self.Thsout) == type([]):
                        Thsout = self.Thsout[i]
                    else: Thsout = self.Thsout
                    
                    if Thsin - Thsout == 0:
                        self.bhxhs[i] = 0
                    else:
                        self.bhxhs[i] = self.QHX1cs[i]/(mhs[i]*cphs*(Thsin-Thsout))*100
                    self.mhshx1[i] = mhs[i]*self.bhxhs[i]/100

                    # CalculateHXoverHS -> Single Value
                    self.QHX1hs[i] = mhs[i]*self.bhxhs[i]*cphs*dThs[i]/100
                    # CalculateHXoverCS -> Single Value
                    self.QHX1cs[i] = mcs[i]*self.bhxcs[i]*cpcs*dTcs[i]/100
                elif self.QHX1hs[i] < self.QHX1cs[i]:

                    if type(self.Tcsout)==type([]):
                        Tcsout = self.Tcsout[i]
                    else: Tcsout = self.Tcsout

                    if type(self.Tcsin) == type([]):
                        Tcsin = self.Tcsin[i]
                    else: Tcsin = self.Tcsin

                    if (mcs[i]*cpcs*(Tcsout-Tcsin)) == 0:
                        self.bhxcs[i] = 0
                    else:
                        self.bhxcs[i] = self.QHX1hs[i]/(mcs[i]*cpcs*(Tcsout-Tcsin))*100
                    
#                    if type(mcs)==type([]):
                    self.mcshx1[i] = mcs[i]*self.bhxcs[i]/100

                    # CalculateHXoverHS -> Single Value
                    self.QHX1hs[i] = mhs[i]*self.bhxhs[i]/100*cphs*dThs[i]
                    # CalculateHXoverCS -> Single Value
                    self.QHX1cs[i] = mcs[i]*self.bhxcs[i]/100*cpcs*dTcs[i]

                else:
                    pass
                    # Set default value?        
#        self.checkTcsoutVector()

    def adaptThsout(self):
        mhs = self.hxPinchCon.combinedSource.stream.MassFlowVector
        cphs = self.hxPinchCon.combinedSource.stream.SpecHeatCap
        mcs = self.hxPinchCon.combinedSink.stream.MassFlowVector
        cpcs = self.hxPinchCon.combinedSink.stream.SpecHeatCap
        dThs = self.calculateDThs()
        dTcs = self.calculateDTcs()

        for i in xrange(Status.Nt):
            if type(self.Tcsin) == type([]):
                Tcsin = self.Tcsin[i]
            else: Tcsin = self.Tcsin

            if type(self.hxPinchCon.combinedSource.outletTemp) == type([]):
                outletTemp = self.hxPinchCon.combinedSource.outletTemp[i]
            else: outletTemp = self.hxPinchCon.combinedSource.outletTemp
#            if (mhs[i]*cphs*self.bhxhs[i]/100) != 0:
#                self.Thsout[i] = self.Thsin[i] - self.QHX1hs[i]/(mhs[i]*cphs*self.bhxhs[i]/100)
#            else: 
#                self.Thsout[i] = self.Thsin[i]

            if self.Thsout[i] < outletTemp:
                self.Thsout[i] = outletTemp
                
                self.QHX1hs[i] = mhs[i]*self.bhxhs[i]/100*cphs*(self.Tcsout[i]-Tcsin)
                if (mcs[i]*cpcs*(self.Tcsout[i]-Tcsin))==0:
                    self.bhxcs[i]=0
                else:
                    self.bhxcs[i] = self.QHX1hs[i]/(mcs[i]*cpcs*(self.Tcsout[i]-Tcsin))*100
                self.mcshx1[i] = mcs[i]*self.bhxcs[i]/100
                
            if self.Thsout[i] < Tcsin + self.dTmin:
                self.Thsout[i] = Tcsin + self.dTmin
                self.QHX1hs[i] = mhs[i]*self.bhxhs[i]/100*cphs*(self.Tcsout[i]-Tcsin)
                if (mcs[i]*cpcs*(self.Tcsout[i]-Tcsin))==0:
                    self.bhxcs[i]=0
                else:
                    self.bhxcs[i] = self.QHX1hs[i]/(mcs[i]*cpcs*(self.Tcsout[i]-Tcsin))*100
                self.mcshx1[i] = mcs[i]*self.bhxcs[i]/100

    def adaptTcsout(self):

        mhs = self.hxPinchCon.combinedSource.stream.MassFlowVector
        cphs = self.hxPinchCon.combinedSource.stream.SpecHeatCap
        mcs = self.hxPinchCon.combinedSink.stream.MassFlowVector
        cpcs = self.hxPinchCon.combinedSink.stream.SpecHeatCap
        dThs = self.calculateDThs()
        dTcs = self.calculateDTcs()

        for i in xrange(Status.Nt):

            if type(self.Thsin) == type([]):
                Thsin = self.Thsin[i]
            else: Thsin = self.Thsin
            
            
            if self.Tcsout[i] > self.hxPinchCon.combinedSink.outletTemp:
                self.Tcsout[i] = self.hxPinchCon.combinedSink.outletTemp
                
                self.QHX1cs[i] = mcs[i]*self.bhxcs[i]/100*cpcs*(Thsin-self.Thsout[i])
                if mhs[i]*cphs*(Thsin-self.Thsout[i]) != 0:
                    self.bhxhs[i] = self.QHX1cs[i]/(mhs[i]*cphs*(Thsin-self.Thsout[i]))*100
                else: self.bhxhs[i] = 0

                self.mhshx1[i] = mhs[i]*self.bhxhs[i]/100
                
            if self.Tcsout[i] > Thsin - self.dTmin:
                self.Tcsout[i] = Thsin - self.dTmin
                
                self.QHX1cs[i] = mcs[i]*self.bhxcs[i]/100*cpcs*(Thsin-self.Thsout[i])
                if mhs[i]*cphs*(Thsin-self.Thsout[i]) != 0:
                    self.bhxhs[i] = self.QHX1cs[i]/(mhs[i]*cphs*(Thsin-self.Thsout[i]))*100
                else: self.bhxhs[i] = 0

                self.mhshx1[i] = mhs[i]*self.bhxhs[i]/100

#    def adaptBhxhs(self):
#        self.mhshx1 = []
#        mhs = self.hxPinchCon.combinedSource.stream.MassFlowVector
#        cphs = self.hxPinchCon.combinedSource.stream.SpecHeatCap
#        self.bhxhs = []
#        for i in xrange(len(self.QHX1cs)):
#            self.bhxhs.append(self.QHX1cs[i]/(mhs[i]*cphs*(self.Thsin-self.Tcsout[i])))
#
#    def adaptBhxcs(self):
#        self.mcshx1 = []
#        mcs = self.hxPinchCon.combinedSink.stream.MassFlowVector
#        cpcs = self.hxPinchCon.combinedSink.stream.SpecHeatCap
#
#        self.bhxcs = []
#        for i in xrange(len(self.QHX1hs)):
#            self.bhxcs.append(self.QHX1hs[i]/(mcs[i]*cpcs*(self.Tcsout[i]-self.Tcsin)))

    def calculateHXoverUA(self):

        self.Tloghx = []
        for i in xrange(Status.Nt):
            if type(self.Thsin)==type([]):
                Thsin = self.Thsin[i]
            else: Thsin = self.Thsin

            if type(self.Tcsin)==type([]):
                Tcsin = self.Tcsin[i]
            else: Tcsin = self.Tcsin
            
            if self.QStorage[i] != 0:
                mlog = (Thsin-self.Tcsout[i])/(self.Thsout[i]-Tcsin)
    #            print "mlog: " + str(mlog)
                if mlog==1:
                    self.Tloghx.append(Thsin-self.Tcsout[i])
                else:
                    if mlog < 1:
                        mlog = 1
                    mlog = math.log(mlog)
    #            print "mlog: " + str(mlog)
                    if mlog == 0:
                        self.Tloghx.append(1)
                    else:
                        self.Tloghx.append(((Thsin-self.Tcsout[i])-(self.Thsout[i]-Tcsin))/mlog)
            else:
                self.Tloghx.append(1)
                
                
        self.Q = []
        for elem in self.Tloghx:
            self.Q.append(self.UA*elem)

    def calculateHXoverHS(self):
        self.QHX1hs = []
        mhs = self.hxPinchCon.combinedSource.stream.MassFlowVector
        cphs = self.hxPinchCon.combinedSource.stream.SpecHeatCap
        dThs = self.calculateDThs()
        
        print "mhs: " , str(mhs[0:100])
        print "cphs: ", str(cphs)
        print "dThs: ", str(dThs[0:100])
        print "bhxcs: ", str(self.bhxhs[0:100])
        
        for i in xrange(Status.Nt):
            mhsi = mhs[i]
            dTi = dThs[i]
            self.QHX1hs.append(mhsi*self.bhxhs[i]/100*cphs*dTi)
#            self.QHX1hs.append(mhs[i]*self.bhxhs*cphs*dThs[i])

# Check einfuehren, ob Thsout richtig, wenn Enthapiy = 0
        for i in xrange(Status.Nt):
            if self.QHX1hs[i]==0:
                self.Thsout[i]=self.Thsin[i]

    def calculateHXoverCS(self):
        self.QHX1cs = []
        mcs = self.hxPinchCon.combinedSink.stream.MassFlowVector
        cpcs = self.hxPinchCon.combinedSink.stream.SpecHeatCap
        dTcs = self.calculateDTcs()
        for i in xrange(Status.Nt):
            self.QHX1cs.append(mcs[i]*self.bhxcs[i]/100*cpcs*dTcs[i])

# Check einfuehren, ob Thsout richtig, wenn Enthapiy = 0
        for i in xrange(Status.Nt):
            if self.QHX1cs[i]==0:
                self.Tcsout[i]=min(self.Tcsin)

    def calculateDThs(self):
        dThs = []
#        print "Thsout: " + str(self.Thsout)
        for i in xrange(Status.Nt):
            dThs.append(self.Thsin[i]-self.Thsout[i])
#        print dThs
        return dThs

    def calculateDTcs(self):
        dTcs = []
        if type(self.Tcsout) == type([]) and type(self.Tcsin) == type([]):
            for i in xrange(len(self.Tcsout)):
                dTcs.append(self.Tcsout[i]-self.Tcsin[i])
        elif type(self.Tcsout) == type([]) and type(self.Tcsin) != type([]):
            for i in xrange(len(self.Tcsout)):
                dTcs.append(self.Tcsout[i]-self.Tcsin)
        elif type(self.Tcsout) != type([]) and type(self.Tcsin) == type([]):
            for i in xrange(len(self.Tcsout)):
                dTcs.append(self.Tcsout-self.Tcsin[i])
        else:
            for i in xrange(len(self.Tcsout)):
                dTcs.append(self.Tcsout-self.Tcsin)
        return dTcs

    def checkThsoutVector(self):
        if type(self.Thsout) != type([]):
                if type(self.Tcsin) == type([]):
                    for i in xrange(Status.Nt):
                        if self.Thsout < self.Tcsin[i] + self.dTmin:
                            self.Thsout = self.Tcsin[i] + self.dTmin
                else:
                    if self.Thsout < self.Tcsin + self.dTmin:
                        self.Thsout = self.Tcsin + self.dTmin
        else:
            for i in xrange(Status.Nt):
                if type(self.Tcsin) == type([]):
                    Tcsinv = self.Tcsin[i]
                else: Tcsinv = self.Tcsin

                if self.Thsout[i] < Tcsinv + self.dTmin:
                    self.Thsout[i] = Tcsinv + self.dTmin

    def checkTcsoutVector(self):

        if type(self.Tcsout) != type([]):
            if type(self.Thsin) == type([]):
                for i in xrange(Status.Nt):
                    if self.Tcsout > self.Thsin[i] - self.dTmin:
                        self.Tcsout = self.Thsin[i] - self.dTmin
            else: 
                if self.Tcsout > self.Thsin - self.dTmin:
                    self.Tcsout = self.Thsin - self.dTmin
        else:
            for i in xrange(Status.Nt):
                if type(self.Thsin) == type([]):
                    Thsinv = self.Thsin[i]
                else: Thsinv = self.Thsin

                if self.Tcsout[i] > Thsinv - self.dTmin:
                    self.Tcsout[i] = Thsinv - self.dTmin

    def calculateTcsoutOverHXStorage(self):
#        self.Tcsout = []
        mcs = self.hxPinchCon.combinedSink.stream.MassFlowVector
        cpcs = self.hxPinchCon.combinedSink.stream.SpecHeatCap

        for i in xrange(Status.Nt):
            if type(self.Tcsin) == type([]):
                Tcsin = self.Tcsin[i]
            else: Tcsin = self.Tcsin
            if (mcs[i]*cpcs*self.bhxcs[i]) != 0:
                self.Tcsout[i] = Tcsin + self.QStorage[i]/(mcs[i]*cpcs*self.bhxcs[i]/100)
            else:
                self.Tcsout[i] = Tcsin
                
    def calculateTcsoutOverHX(self):
        self.Tcsout = []
        mcs = self.hxPinchCon.combinedSink.stream.MassFlowVector
        cpcs = self.hxPinchCon.combinedSink.stream.SpecHeatCap
        for i in xrange(Status.Nt):
            self.Tcsout.append(self.Tcsin + self.QHX1hs[i]/(mcs[i]*cpcs*self.bhxcs[i]/100))

    def calculateThsoutOverHX(self):
        self.Thsout = []
        mhs = self.hxPinchCon.combinedSource.stream.MassFlowVector
        mhs1 = self.mhsAfterStorage
        cphs = self.hxPinchCon.combinedSource.stream.SpecHeatCap

        for i in xrange(Status.Nt):
            if type(self.Thsin) == type([]):
                Thsin = self.Thsin[i]
            else: Thsin = self.Thsin


            if (mhs[i]*cphs*self.bhxhs[i]/100) != 0:
                self.Thsout.append(Thsin - self.QHX1hs[i]/(mhs[i]*cphs*self.bhxhs[i]/100))
            else:
                self.Thsout.append(Thsin)
                
#            if (mhs1[i]*cphs*self.bhxhs[i]/100) != 0:
#                self.Thsout.append(Thsin - self.QStorage[i]/(mhs1[i]*cphs))
#            else:
#                self.Thsout.append(Thsin) 
                
                
#    def getStartQHXVector(self):
#        self.QHX1V = []

    def __checkStartValues(self):
#        if self.Q == None and self.Energy != None:
#        if self.Energy != None:
##            print self.hxPinchCon.combinedSource.stream.OperatingHours
#            minOphs = self.hxPinchCon.combinedSource.stream.OperatingHours
#            minOpcs = self.hxPinchCon.combinedSink.stream.OperatingHours
#            if minOphs > minOpcs and minOpcs != 0:
#                self.Q = self.Energy/minOpcs
#            elif minOphs != 0:
#                self.Q = self.Energy/minOphs
#            else:
#                self.Q = 0

        mhsAvg = self.hxPinchCon.combinedSource.stream.MassFlowAvg
        mcsAvg = self.hxPinchCon.combinedSink.stream.MassFlowAvg
        cphs = self.hxPinchCon.combinedSource.stream.SpecHeatCap
        cpcs = self.hxPinchCon.combinedSink.stream.SpecHeatCap
        """
        if self.Q != None:
            self.Thsout = []
            try:
                if len(mhsAvg)>1:
                    mhsAvg = mhsAvg[0]
            except:
                pass
            if type(self.Thsin) == type([]):
                for i in xrange(Status.Nt):
                    if (mhsAvg*cphs*self.bhxhs[i]/100) != 0:
                        self.Thsout.append(self.Thsin[i] - self.Q/(mhsAvg*cphs*self.bhxhs[i]/100))
                    else:
                        self.Thsout.append(self.Thsin[i])
            else:
                print "bhxhs: " + str(self.bhxhs)
                print "Q: " + str(self.Q)
                print "mhsAvg: " + str(mhsAvg)
                print "cphs" + str(cphs)
                print "Thsin: " + str(self.Thsin)


                
                self.Thsout.append(self.Thsin - self.Q/(mhsAvg*cphs*self.bhxhs/100))
                self.Thsout = self.Thsout*Status.Nt


            self.Tcsout = []
            try:
                if len(mcsAvg)>1:
                    mcsAvg = mcsAvg[0]
                    print mcsAvg
            except:
                pass
            if type(self.Tcsin) == type([]):
                for i in xrange(Status.Nt):
                    if mcsAvg*cpcs*self.bhxcs[i] != 0:
                        self.Tcsout.append(self.Tcsin[i] + self.Q/(mcsAvg*cpcs*self.bhxcs[i]/100))
                    else:
                        self.Tcsout.append(self.Tcsin[i])
            else:

                self.Tcsout.append(self.Tcsin + self.Q/(mcsAvg*cpcs*self.bhxcs[i]/100))
                self.Tcsout = self.Tcsout*Status.Nt
#            print "Tcsin: " + str(self.Tcsin)
#            print "mcsAvg: " + str(mcsAvg)
#            print "Q: " + str(self.Q)
#            print "cpcs: " + str(cpcs)
#            print "bhxcs: " + str(self.bhxcs)
#            print "Tcsout: " + self.Tcsout
#            self.Tcsout = self.Tcsout*Status.Nt
#            print self.Tcsout
#            self.Thsout = self.calculateThsoutOverHX()
#            self.Tcsout = self.calculateTcsoutOverHX()
        """
        if self.Thsout != None:
            pass
        elif self.Tcsout != None:
            pass
        elif self.LMTD != None:
            # TODO implement
            pass

        # Code for definition of 2nd HX
        # HX Simulation Page 15


    def calculateQStorage(self):

        max_storage = -1

        dE = []
        possibleStorage = []
        for i in xrange(len(self.QHX1hs)):
            dE.append(self.QHX1hs[i]-self.QHX1cs[i])
            # to overcome rounding error, dE >1 instead >0
            if dE[i] > 1:
                possibleStorage.append(dE[i])
            else: possibleStorage.append(0)

        instorage_initial = possibleStorage[i]
        realStorageOut = [0]*len(dE)
        self.realStorage = realStorageOut
        self.QStorage = [0]*len(dE)
        lastrow = len(dE)-1
        i=0


#        for i in xrange(len(self.QHX1cs)):
        while i < lastrow:

            instorage = instorage_initial

            if instorage > max_storage:
                max_storage = instorage

            csdemand = self.QHX1cs[i+1]
            hsdemand = self.QHX1hs[i+1]

            if (csdemand - hsdemand) >= 0 and instorage >= (csdemand - hsdemand):
                realStorageOut[i+1] = csdemand - hsdemand

                startrow = i+1
                instorage = instorage - (csdemand - hsdemand)
                if startrow < lastrow:
                    instoragenext = dE[startrow+1]
                    csdemand = self.QHX1cs[startrow+1]
                    hsdemand = self.QHX1hs[startrow+1]

#Do Until (instorage + instoragenext) < (csdemand - hsdemand) Or startrow > lastrow
                #while instorage + instoragenext > csdemand - hsdemand or startrow < lastrow:
                while instorage + instoragenext > csdemand - hsdemand:
                    if startrow > lastrow:
                        break
                    if csdemand > hsdemand:
                        realStorageOut[startrow+1] = csdemand - hsdemand

                    instorage += instoragenext

                    if instorage > max_storage:
                        max_storage = instorage

                    if startrow +1 < lastrow :

                        csdemand = self.QHX1cs[startrow+2]
                        hsdemand = self.QHX1hs[startrow+2]
                        instoragenext = dE[startrow+2]
                    elif startrow < lastrow:
                        csdemand = self.QHX1cs[startrow+1]
                        hsdemand = self.QHX1hs[startrow+1]
                        instoragenext = dE[startrow+1]

                    startrow+=1

                if instorage + hsdemand < csdemand:
                    if startrow < lastrow:
                        realStorageOut[startrow+1] = instorage
                        instorage_initial = 0 + possibleStorage[startrow + 1]
                else:
                    if startrow < lastrow:
                        realStorageOut[startrow+1] = csdemand - hsdemand
                        if startrow + 1 <= lastrow:
                            instorage_initial = instorage - (csdemand - hsdemand) + possibleStorage[startrow +1]
                        else:
                            instorage_initial = instorage - (csdemand - hsdemand)

                if startrow > i + 1:
                    i = i + (startrow - i) + 1
                else:
                    i = i + 2

            elif (csdemand - hsdemand) >= 0 and instorage < (csdemand - hsdemand):
                realStorageOut[i+1] = instorage
                instorage_initial = 0 + possibleStorage[i+1]
                i+=1

            elif csdemand - hsdemand < 0:
                instorage_initial = instorage - (csdemand - hsdemand)
                i+=1

        for i in xrange(len(self.QHX1hs)):
            if self.QHX1hs[i] + realStorageOut[i] > self.QHX1cs[i]:
                self.QStorage[i] = self.QHX1cs[i]
            else:
                self.QStorage[i] = self.QHX1hs[i] + realStorageOut[i]

        self.mhsAfterStorage = [0]*Status.Nt
        for i in xrange(Status.Nt):
            if self.hxPinchCon.combinedSource.stream.SpecHeatCap*(self.dThs[i]) !=0:
                self.mhsAfterStorage[i] = self.QStorage[i]/ self.hxPinchCon.combinedSource.stream.SpecHeatCap*(self.dThs[i])
        

        # calculate storage size
        
        
        storagesize = []
        for i in xrange(Status.Nt):
            storagesize.append(0)
            if (self.hxPinchCon.combinedSource.stream.MassFlowVector[i]*self.hxPinchCon.combinedSource.stream.SpecHeatCap*(self.dThs[i]))!=0:
                storagesize[i]=self.QStorage[i]/(self.hxPinchCon.combinedSource.stream.MassFlowVector[i]\
                                             *self.hxPinchCon.combinedSource.stream.SpecHeatCap*(self.dThs[i]))
#            if self.dThs[i] != 0:
#                self.hxPinchCon.combinedSource.stream.MassFlowVector[i] = self.QStorage[i]/(self.hxPinchCon.combinedSource.stream.SpecHeatCap*(self.dThs[i]))
        self.StorageSize=max(storagesize)
        
#        self.QHX1hs = self.QStorage
#        self.StorageSize=50
        
#    def calculateTcsoutOverHX(self):
#        Tcsout = []
#        mcs = self.hxPinchCon.combinedSink.stream.MassFlowVector
#        cpcs = self.hxPinchCon.combinedSink.stream.SpecHeatCap
#        for i in xrange(Status.Nt):
#            Tcsout.append(self.Tcsin - self.Q[i]/(mcs[i]*cpcs*self.bhxcs))
#        print "CalculateTcsoutOverHX called"
#        print Tcsout
#        return Tcsout
#
#    def calculateThsoutOverHX(self):
#        Thsout = []
#        mhs = self.hxPinchCon.combinedSource.stream.MassFlowVector
#        cphs = self.hxPinchCon.combinedSource.stream.SpecHeatCap
#        for i in xrange(Status.Nt):
#            Thsout.append(self.Thsin - self.Q[i]/(mhs[i]*cphs*self.bhxhs))
#        print "CalculateThsoutOverHX called"
#        print Thsout
#        return Thsout
        

if __name__ == "__main__":
    pass
