# -*- coding: utf-8 -*-
#============================================================================== 				
#
#	E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (www.iee-einstein.org)
#
#------------------------------------------------------------------------------
#
#	CCheck (Consistency Check)
#			
#------------------------------------------------------------------------------
#			
#	Short description:
#	
#	Functions for consistency checking of data
#
#==============================================================================
#
#   EINSTEIN Version No.: 1.0
#   Created by: 	Claudia Vannoni, Hans Schweiger
#                       08/03/2008 - 03/09/2008
#
#   Update No. 004
#
#   Since Version 1.0 revised by:
#
#                       Hans Schweiger  06/04/2009
#                       Hans Schweiger  20/07/2009
#               
#   06/04/2009  HS  Clean-up: elimination of prints
#   20/07/2009  HS  Bug-fix: fluid properties in outgoing medium
#   15/01/2010  HS  Adaptation for new parameters (EINSTEIN-AT):
#                   - VInFlowCycle
#                   - mInFlowNom
#                   - VOutFlowCycle
#                   - mOutFlowNom
#                   - HPerDayInFlow
#                   - HPerDayOutFlow
#                   - NCyclesPerYear (= NBatch * NDaysProc)
#   26/01/2010  HS  PartLoad - Factor and HPerDayOp, and VIn/OutFlowCycleEff added
#
#------------------------------------------------------------------------------		
#	(C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008,2009
#	www.energyxperts.net / info@energyxperts.net
#
#	This program is free software: you can redistribute it or modify it under
#	the terms of the GNU general public license as published by the Free
#	Software Foundation (www.gnu.org).
#
#============================================================================== 				

EPSILON = 1.e-3     # required accuracy for function "isequal"
INFINITE = 1.e99    # numerical value assigned to "infinite"

from math import *
from ccheckFunctions import *
from einstein.modules.fluids import *
from einstein.modules.streams import *

#libraries necessary for SQL access:
from einstein.GUI.status import *
import einstein.GUI.pSQL as pSQL, MySQLdb

#------------------------------------------------------------------------------
class CheckProc():
#------------------------------------------------------------------------------
#   Carries out consistency checking for process k
#------------------------------------------------------------------------------

#QHXProc: recovered heat as input to the process k (source= matrix of ducts/processes). Not calculated yet
#UPHtotQ: total UPH from different sources = UPHProc+ QHXProc (the definition as to redefined into the questionnaire).
# Pay attention: both values used here per process k comes from matrix . At present assigned here.


    def __init__(self,k):     #function that is called at the beginning when object is created


# assign a variable to all intermediate/calculated values needed
        
        self.PTOutFlowRec = [CCPar("PTOutFlowRec",parType="T")] # specific to multiple streams
        self.PTFinal = [CCPar("PTFinal",parType = "T")] # specific to multiple streams
        self.HOutFlowRec = CCPar("HOutFlowRec")
        self.HFinal = CCPar("HFinal")
        self.dHOutFlow = CCPar("dHOutFlow")
        self.dHFinal = CCPar("dHFinal")
        self.PTInFlow3 = CCPar("PTInFlow3")
        self.PTInFlow4 = CCPar("PTInFlow4")
        self.dhFinal2 = CCPar("dhFinal2")

        self.XOutFlow = [CCPar("XOutFlow",parType = "X")] # specific to multiple streams
        self.XOutFlowRec = CCPar("XOutFlowRec",parType = "X")
        self.XFinal = CCPar("XFinal",parType = "X")

        self.HPerYearProc = CCPar("HPerYearProc",priority=2)
        self.HPerYearProc.valMax = 8760

        self.VInFlowCycleEff = [CCPar("VInFlowCycleEff")] # specific to multiple streams
        self.VOutFlowCycleEff = [CCPar("VOutFlowCycleEff")] # specific to multiple streams

        self.NBatch1 = CCPar("NBatch1")
        self.PartLoad1 = CCPar("PartLoad1")
        self.PartLoad2 = CCPar("PartLoad2")
        self.PartLoad3 = CCPar("PartLoad3")
        
        self.VInFlowCycle1 = CCPar("VInFlowCycle1") 
        self.VInFlowCycleEff = CCPar("VInFlowCycleEff") 
        self.VInFlowCycleEff1 = CCPar("VInFlowCycleEff1") 
        self.VInFlowCycleEff2 = CCPar("VInFlowCycleEff2") 
        self.VInFlowCycleEff3 = CCPar("VInFlowCycleEff3") 
        self.VInFlowCycleEff4 = CCPar("VInFlowCycleEff4")
        
        self.VOutFlowCycle1 = CCPar("VOutFlowCycle1")
        self.VOutFlowCycleEff = CCPar("VOutFlowCycleEff")
        self.VOutFlowCycleEff1 = CCPar("VOutFlowCycleEff1")
        self.VOutFlowCycleEff2 = CCPar("VOutFlowCycleEff2")
        self.VOutFlowCycleEff3 = CCPar("VOutFlowCycleEff3")
        self.VOutFlowCycleEff4 = CCPar("VOutFlowCycleEff4")

        self.VolProcMed1 = CCPar("VolProcMed1")
        self.DTLoss=CCPar("DTLoss")
        self.QLoss = CCPar("QLoss")
        self.UPHm = CCPar("UPHm")
        self.DTUPHcGross2 = CCPar("DTUPHcGross2")
        self.DTUPHcGross3 = CCPar("DTUPHcGross3")
        self.DTUPHcGross = CCPar("DTUPHcGross",parType="DT")
        self.UPHcdotGross = [CCPar("UPHcdotGross")]
        self.UPHcdotGross2 = CCPar("UPHcdotGross2")#For convention UPH and UPHc are net!
        self.DTQHXIn = CCPar("DTQHXIn",parType="DT")
        self.DTQHXOut = CCPar("DTQHXOut",parType="DT")
        self.DTCrossHXLT = CCPar("DTCrossHXLT",parType="DT")
        self.DTCrossHXLT.valMin = 5.0   #engineering lower limit
        self.DTCrossHXHT = CCPar("DTCrossHXHT",parType="DT")
        self.DTCrossHXHT.valMin = 5.0   #engineering lower limit
        self.DTOutFlow = CCPar("DTOutFlow",parType="DT")
        self.QHXdotProcInt = CCPar("QHXdotProcInt")
        self.NCyclesPerYear = CCPar("NCyclesPerYear")
        self.NCyclesPerYear = CCPar("NCyclesPerYear")
        self.DTUPHcNet3 = CCPar("DTUPHcNet2")
        self.DTUPHcNet2 = CCPar("DTUPHcNet2")
        self.DTUPHcNet = CCPar("DTUPHcNet",parType="DT")
        self.UPHcdot = CCPar("UPHcdot")
        self.UPHc2 = CCPar("UPHc2")
        self.UPHc = CCPar("UPHc")
        self.DTUPHs = CCPar("DTUPHs",parType="DT")
        self.UPHsdot = CCPar("UPHsdot")
        self.UPHs = CCPar("UPHs")
        self.UPH = CCPar("UPH")
        self.UPHw = CCPar("UPHw")# It is the waste heat of the outflow. In general it is QWHProc but if we have a vessel it does not
        self.UPHw2 = CCPar("UPHw2")
        self.UPHw_dot = CCPar("UPHw_dot")
        self.UPHProc = CCPar("UPHProc") 
        self.UAProc = CCPar("UAProc")
        self.QEvapProc = CCPar("QEvapProc")
        self.UPHcGross = CCPar("UPHcGross")
        self.QHXProcInt = CCPar("QHXProcInt")
        self.QHXProc = CCPar("QHXProc")# It comes from the matrix
        self.QWHProc = CCPar("QWHProc")# It comes from the matrix. In theory it is the sum UPHw and UPHmass (not existing yet)

        self.mInFlowYear = CCPar("mInFlowYear")
        self.mOutFlowYear = CCPar("mOutFlowYear")

        self.mInFlowNom1 = CCPar("mInFlowNom1")
        self.mInFlowNom2 = CCPar("mInFlowNom2")

        self.mOutFlowYear = CCPar("mOutFlowYear")
        self.mOutFlowYear1 = CCPar("mOutFlowYear1")
        self.mOutFlowYear2 = CCPar("mOutFlowYear2")
        self.mOutFlowNom1 = CCPar("mOutFlowNom1")
        self.mOutFlowNom2 = CCPar("mOutFlowNom2")

        self.importData(k)

        if DEBUG in ["ALL","BASIC","MAIN"]:
            self.showAllUPH()
            
    def importStreamsData(self, dataName, streams):
        data = getattr(self, dataName).pop() # assume singleton template variable
        for i in range(len(streams)):
            data.name = '%s %d (%n)' % (dataName, i, streams[i].name)
            data.setValue(getattr(streams[i], dataName))
            getattr(self,dataName).append(data)
            
#------------------------------------------------------------------------------
    def importData(self,k):  
#------------------------------------------------------------------------------
#   imports data from SQL tables (from AlternativeProposalNo = -1)
#------------------------------------------------------------------------------

        self.ProcNo = k+1
        ANo = -1
        
#..............................................................................
# assign empty CCPar to all questionnaire parameters

        
        self.PTInFlow = [CCPar("PTInFlow", parType="T")] # specific to multiple streams
        self.PT = CCPar("PT",priority=2)
        self.PTOutFlow = [CCPar("PTOutFlow", parType="T")] # specific to multiple steams
        self.PTInFlowRec = [CCPar("PTInFlowRec",parType="T")] # specific to multiple streams
        self.PTStartUp = CCPar("PTStartUp",parType="T")
        self.VInFlowCycle = [CCPar("VInFlowCycle")] # specific to multiple streams
        self.mInFlowNom = [CCPar("mInFlowNom")] # specific to multiple streams
        self.VOutFlowCycle = [CCPar("VOutFlowCycle")] # specific to multiple streams
        self.mOutFlowNom = [CCPar("mOutFlowNom")] # specific to multiple streams
        self.HOutFlow = [CCPar("HOutFlow")] # specific to multiple streams
        self.VolProcMed = CCPar("VolProcMed")
        self.NDaysProc = CCPar("NDaysProc")
        self.NDaysProc.valMax = 365
        self.HPerDayProc = CCPar("HPerDayProc")
        self.HPerDayProc.valMax = 24
        self.HPerYearInFlow = CCPar("HPerYearInFlow")
        self.HPerYearOutFlow = CCPar("HPerYearOutFlow")
        self.PartLoad = CCPar("PartLoad",parType="X")
        self.HBatch = CCPar("HBatch")
        self.NBatch = CCPar("NBatch")
        self.TEnvProc = CCPar("TEnvProc",parType="T")# Now cannot be entered by questionnaire
        self.QOpProc = CCPar("QOpProc")
        self.UPH = CCPar("UPH") # Useful process heat asked into the questionnaire is UPH not UPHproc
        
        
#..............................................................................
# reading data from table "qprocessdata"
        qprocessdataTable = Status.DB.qprocessdata.Questionnaire_id[Status.PId].AlternativeProposalNo[ANo].ProcNo[self.ProcNo]
        
#        print "CheckProc (importData): lengh %s ProcNo = %s"%(len(qprocessdataTable),self.ProcNo)
        if len(qprocessdataTable) > 0:
            qprocessdata = qprocessdataTable[0]
            
            # get all in-flowing and out-flowing streams
            self.inflowingStreams = []
            for name in getInflowingStreamNamesFromDB(qprocessdata.QProcessData_ID):
                stream = InflowingStream(name)
                stream.loadFromDB(qprocessdata.QProcessData_ID)
                self.inflowingStreams.append(stream)
            self.nInflowingStreams = len(self.inflowingStreams)
            self.outflowingStreams = []
            for name in getOutflowingStreamNamesFromDB(qprocessdata.QProcessData_ID):
                stream = OutflowingStream(name)
                stream.loadFromDB(qprocessdata.QProcessData_ID)
                self.outflowingStreams.append(stream)
            self.nOutflowingStreams = len(self.outflowingStreams)

            self.FluidCp      = [None] * self.nInflowingStreams
            self.FluidDensity = [None] * self.nInflowingStreams
            self.FluidRhoCp   = [None] * self.nInflowingStreams
            for i in range(self.nInflowingStreams):
                stream_fluid = Fluid(findKey(Status.prj.getFluidDict(), self.inflowingStreams[i].Medium))   #IMPORT from the FluidDB
                self.FluidCp[i]      = stream_fluid.cp
                self.FluidDensity[i] = stream_fluid.rho
                self.FluidRhoCp[i]   = self.FluidCp * self.FluidDensity[i]

            self.importStreamsData('PTInFlow', self.inflowingStreams)
            self.PT.setValue(qprocessdata.PT,err=0.0)   # if specified, take as fixed
            self.importStreamsData('PTOutFlow', self.outflowingStreams)

# if no temperature or enthalpy for Outflow is specified, start with PT as initial estimate
# but leave error range from 0 to infinite !!!!

            self.importStreamsData('PTOutFlowRec', self.outflowingStreams)
            for i in range(len(self.outflowingStream)):
                if self.outflowingStream[i].PTOutFlow is None and self.outflowingStream[i].HOutFlow is None:
                    self.PTOutFlow[i].val    = self.PT.val
                    self.PTOutFlowRec[i].val = self.PT.val
                    
            self.importStreamsData('HOutFlow', self.outflowingStreams)
            self.importStreamsData('XOutFlow', self.outflowingStreams)
                
            self.importStreamsData('PTInFlowRec', self.inflowingStreams)
            self.importStreamsData('mInFlowNom', self.inflowingStreams)
            self.importStreamsData('VInFlowCycle', self.inflowingStreams)
            # multiply VInFlowCycleEff
            self.VInFlowCycleEff *= self.nInflowingStreams 
    
            self.importStreamsData('mOutFlowNom', self.outflowingStreams)
            self.importStreamsData('VOutFlowCycle', self.outflowingStreams)
            # multiply VOutFlowCycleEff
            self.VOutFlowCycleEff *= self.nOutflowingStreams
            
             
            self.PTStartUp.setValue(qprocessdata.PTStartUp)
            self.VolProcMed.setValue(qprocessdata.VolProcMed) 
            self.NDaysProc.setValue(qprocessdata.NDaysProc,err=0.0) #number -> exact value
            self.HPerDayProc.setValue(qprocessdata.HPerDayProc)
            self.HPerYearInFlow.setValue(qprocessdata.HPerYearInFlow)
            self.HPerYearOutFlow.setValue(qprocessdata.HPerYearOutFlow)

            if qprocessdata.PartLoad is None:   #should be always set from GUI, but for being sure !!!
                self.PartLoad.setValue(1.0,err=0.0)
            else:
                self.PartLoad.setValue(qprocessdata.PartLoad)

#if 24.0 hours are specified, suppose that this value is exact.
            if self.HPerDayProc.val > 23.99:
                self.HPerDayProc.setValue(24.0,err=0.0)
                
            if qprocessdata.NBatch is None:
                self.NBatch.setValue(1.0,err=0.0)   # if no number is specified, suppose 1 !!!
            else:
                self.NBatch.setValue(qprocessdata.NBatch,err=0.0) #number -> exact value

            self.HBatch.setValue(qprocessdata.HBatch)

            self.importStreamsData('PTFinal', self.outflowingStreams)
            self.HeatRecOk = [None] * self.nOutflowingStreams
            for i in range(self.nOutflowingStreams):
                if self.outflowingStreams.HeatRecOK is None:
                    logWarning(_("Possibility of heat recovery for process no. %s (%s) stream %d (%s) is not specified.\nYES is assumed." % (self.ProcNo,qprocessdata.Process, i, self.outflowingStreams[i].name)))
                    self.HeatRecOK[i] = True
                else:
                    self.HeatRecOk[i] = self.outflowingStreams[i].HeatRecOk
                if self.HeatRecOk[i] and self.outflowingStreams[i].PTFinal is None: #reads in PT final only if heat recovery is possible !!!
                        logMessage(_("No limit specified for cooling of outgoing stream %d (%s). 0 °C is assumed" % (i, self.outflowingStreams[i].name)))
                        self.PTFinal[i].setValue(0.0)
                
            if qprocessdata.TEnvProc is None:
                self.TEnvProc.setValue(18.0)
            else:
                self.TEnvProc.setValue(qprocessdata.TEnvProc)
            self.QOpProc.setValue(qprocessdata.QOpProc) 
            self.UPH.setValue(qprocessdata.UPH,err=0.0) #if specified, take exact value 

            self.internalHR = [None] * self.nInflowingStreams
            
            self.FluidCp_w      = [None] * self.nOutflowingStreams
            self.FluidDensity_w = [None] * self.nOutflowingStreams
            self.FluidRhoCp_w   = [None] * self.nOutflowingStreams
            self.Fluid_hL_w     = [None] * self.nOutflowingStreams
            self.FluidTCond_w   = [None] * self.nOutflowingStreams
            for i in range(self.nInflowingStreams):
                self.internalHR[i] = not ( \
                                          isequal(self.PTInFlow[i].val,self.PTInFlowRec[i].val) \
                                          or (self.PTInFlowRec[i].val is None) \
                                          or (self.PT.val < self.PTInFlow[i].val + 5.0) \
                                          )

                if self.HeatRecOK[i] or self.internalHR: # global internalHR = any(internalHR[i])   # fluid pars only needed in this case
                    stream_fluid_w = Fluid(findKey(Status.prj.getFluidDict(), self.outflowingStreams[i].Medium))   #IMPORT from the FluidDB
                    
                    self.FluidCp_w[i]      = stream_fluid_w.cp
                    self.FluidDensity_w[i] = stream_fluid_w.rho
                    self.FluidRhoCp_w[i]   = self.FluidCp_w * self.FluidDensity_w[i]
                    self.Fluid_hL_w[i]     = stream_fluid_w.hL
                    self.FluidTCond_w[i]   = stream_fluid_w.TCond
                    
            # multiply
            self.UPHcdotGross *= self.nInflowingStreams

               
#------------------------------------------------------------------------------
    def exportData(self):  
#------------------------------------------------------------------------------
#   stores corrected data in SQL (under AlternativeProposalNo = 0)
#------------------------------------------------------------------------------

        ANo = 0
        
#..............................................................................
# writing data into table " qprocessdata"
#        try:
        if ANo == 0:
            qprocessdataTable = Status.DB.qprocessdata.Questionnaire_id[Status.PId].AlternativeProposalNo[ANo].ProcNo[self.ProcNo]
            if len(qprocessdataTable) > 0:
#                print "exporting data to qprocessdata"
                qprocessdata = qprocessdataTable[0]

        
                qprocessdata.PTInFlow = check(self.PTInFlow.val)
                qprocessdata.PT = check(self.PT.val)
                qprocessdata.PTOutFlow = check(self.PTOutFlow.val)
                qprocessdata.PTOutFlowRec = check(self.PTOutFlowRec.val)
                qprocessdata.HOutFlow = check(self.HOutFlow.val)
                qprocessdata.PTInFlowRec = check(self.PTInFlowRec.val)
                qprocessdata.PTStartUp = check(self.PTStartUp.val)
                qprocessdata.PTFinal = check(self.PTFinal.val)
                qprocessdata.VInFlowCycle = check(self.VInFlowCycle.val)
                qprocessdata.mInFlowNom = check(self.mInFlowNom.val)
                qprocessdata.VOutFlowCycle = check(self.VOutFlowCycle.val)
                qprocessdata.mOutFlowNom = check(self.mOutFlowNom.val)
                qprocessdata.VolProcMed = check(self.VolProcMed.val)
                qprocessdata.NDaysProc = check(self.NDaysProc.val)
                qprocessdata.HPerDayProc = check(self.HPerDayProc.val)
                qprocessdata.NBatch = check(self.NBatch.val)
                qprocessdata.HBatch = check(self.HBatch.val)
                qprocessdata.TEnvProc = check(self.TEnvProc.val)
                qprocessdata.QOpProc = check(self.QOpProc.val)
                qprocessdata.UPHProc = check(self.UPHProc.val)
                qprocessdata.HPerYearProc = check(self.HPerYearProc.val)
                qprocessdata.HPerYearInFlow = check(self.HPerYearInFlow.val)
                qprocessdata.HPerYearOutFlow = check(self.HPerYearOutFlow.val)
                qprocessdata.PartLoad = check(self.PartLoad.val)
                qprocessdata.UAProc = check(self.UAProc.val)
                qprocessdata.QEvapProc = check(self.QEvapProc.val)
                qprocessdata.UPHcGross = check(self.UPHcGross.val)
                qprocessdata.QHXProcInt = check(self.QHXProcInt.val)
                qprocessdata.UPHm = check(self.UPHm.val)
                qprocessdata.UPHs = check(self.UPHs.val)
                qprocessdata.UPHc = check(self.UPHc.val)
                qprocessdata.UPH = check(self.UPH.val)
                qprocessdata.UPHw = check(self.UPHw.val)
                qprocessdata.QWHProc = check(self.QWHProc.val)
                qprocessdata.QHXProc = check(self.QHXProc.val)

                if self.HeatRecOK == True:
                    qprocessdata.HeatRecOK = "yes"
                else:
                    qprocessdata.HeatRecOK = "no"

                Status.SQL.commit()
                
            else:
                print "CheckProc (exportData): error writing data to qprocessdata"
            pass




    def showAllUPH(self):
        print "====================="

        self.UPH.show()
        self.UPH1.show()
        self.UPH2.show()
        self.UPHm.show()
        self.UPHm1.show()
        self.UPHs.show()
        self.UPHw.show()
        self.UPHw1.show()
        self.UPHs1.show()
        self.UPHsdot.show()
        self.UPHsdot1.show()
        self.UPHProc.show()
        self.UPHProc1.show()
        self.QHXProc.show()
        self.QHXProc1.show()
        self.UPHc.show()
        self.UPHc1.show()
        self.UPHcdot.show()
        self.UPHcdot1.show()
        self.UPHcdot2.show()
        self.UPHcdotGross.show()
        self.UPHcdotGross1.show()#For convention UPH and UPHc are net!
        self.UPHcGross.show()
        self.UPHw_dot.show()
        self.UPHw_dot1.show()
        self.QHXProcInt.show()
        self.DTUPHcGross.show()
        self.QOpProc.show()
        self.QOpProc1.show()
        self.VolProcMed.show()
        self.HPerYearProc.show()
        #self.HPerYearProc1.show()
        self.HPerDayProc.show()
        self.NDaysProc.show()
        self.NDaysProc1.show()
        self.VInFlowCycleEff.show()
        self.VInFlowCycleEff1.show()
        self.VInFlowCycleEff2.show()
        self.VOutFlowCycle.show()
        self.VOutFlowCycle1.show()
        self.PTInFlow.show()
        self.PTInFlow1.show()
        self.PT.show()
        self.PT1.show()
        self.PT2.show()
        self.PT3.show()
        self.PTInFlowRec.show()
        self.PTInFlowRec1.show()
        self.PTOutFlow.show()
        self.HOutFlow.show
        self.PTStartUp.show()
        self.PTFinal.show()
        self.HFinal.show()
        self.PTOutFlowRec.show()
        self.HOutFlowRec.show
        self.NBatch.show()
        self.UAProc.show()
        self.QEvapProc.show()
        self.TEnvProc.show()  
        self.DTLoss1.show()
        self.DTLoss.show()
        self.QLoss.show()
        self.QLoss1.show()
        self.DTUPHcGross1.show()
        self.DTUPHcGross.show()
        self.DTQHXIn.show()
        self.DTQHXOut.show()
        self.QHXdotProcInt1.show()
        self.QHXdotProcInt2.show()
        self.QHXdotProcInt.show()
        self.NCyclesPerYear1.show()
        self.NCyclesPerYear2.show()
        self.NCyclesPerYear.show()
        self.DTUPHcNet1.show()
        self.DTUPHcNet.show()
        self.DTUPHs1.show()
        self.DTUPHs.show()
        self.QWHProc.show()
        self.QHXProc.show()
        print "HeatRecOK: ",self.HeatRecOK
        

        print "====================="
#-----------------------------------------------------------------------------
    def screen(self):  
#------------------------------------------------------------------------------
#   screens all variables in the block
#------------------------------------------------------------------------------

########## Change of priority for parameters not needed

        if iszero(self.VInFlowCycle):
            self.PTInFlow.priority = 99
            self.PTInFlowRec.priority = 99
        if iszero(self.VOutFlowCycle) or (self.HeatRecOK == False):
            self.PTOutFlow.priority = 99
            self.PTOutFlowRec.priority = 99
        if iszero(self.VolProcMed):
            self.PTStartUp.priority = 99
        if iszero(self.QOpProc):
            self.TEnvProc.priority = 99
            self.UAProc.priority = 99
#................................................................................
        self.UPH.screen()
        self.UPHc.screen()
        self.UPHm.screen()
        self.UPHs.screen()
        self.UPHw.screen()
        # self.QWHProc.screen() Now it coincides with UPHw

        self.UPHProc.screen()
        self.QHXProc.screen()

        self.UPHcGross.screen()
        self.QHXProcInt.screen()

        self.PT.screen()
        self.PTInFlow.screen()
        self.PTOutFlow.screen()
        self.PTInFlowRec.screen()
        self.PTOutFlowRec.screen() 
        self.PTStartUp.screen()

        self.VInFlowCycle.screen()
        self.mInFlowNom.screen()
        self.VOutFlowCycle.screen()
        self.mOutFlowNom.screen()
        self.VolProcMed.screen()

        self.HPerYearProc.screen()
        self.HPerYearInFlow.screen()
        self.HPerYearOutFlow.screen()
        self.NDaysProc.screen()
        self.HPerDayProc.screen()
        self.NBatch.screen()

        self.TEnvProc.screen()
        self.QOpProc.screen()
        self.UAProc.screen()
        self.QEvapProc.screen()
        
#------------------------------------------------------------------------------
    def definePriority(self,mainProcess):
#------------------------------------------------------------------------------
#   changes the priority in function of the importance of the process
#------------------------------------------------------------------------------

        if mainProcess == True:
            
            self.UPH.priority = 1
            self.UPHProc.priority = 1
            self.UPHs.priority = 1
            self.UPHc.priority = 1
            self.UPHm.priority = 1 
            self.UPHw.priority = 1 
            self.PT.priority = 1
            self.QOpProc.priority = 1

            if self.PTInFlow.priority < 99: self.PTInFlow.priority = 1
            if self.PTInFlowRec.priority < 99: self.PTInFlowRec.priority = 1
            if self.PTStartUp.priority < 99: self.PTStartUp.priority = 1

########## here some verifications are redundant but they do not affect the results
            
            if self.PTOutFlow.priority < 99: self.PTOutFlow.priority = 2
            if self.PTOutFlowRec.priority < 99: self.PTOutFlowRec.priority = 2
            if self.VInFlowCycle.priority < 99: self.VInFlowCycle.priority = 2
            if self.VOutFlowCycle.priority < 99: self.VOutFlowCycle.priority = 2
            if self.VolProcMed.priority < 99: self.VolProcMed.priority = 2
            if self.QHXProc.priority < 99: self.QHXProc.priority = 2
            #if self.QWHProc.priority < 99: self.QWHProc.priority = 2 Now it coincides with UPHw. Assigned priority 2 coherent with the QHX
            if self.HPerYearProc.priority < 99: self.HPerYearProc.priority = 2
            
            if self.NBatch.priority < 99: self.NBatch.priority = 3
            if self.NDaysProc.priority < 99: self.NDaysProc.priority = 3
            if self.HPerDayProc.priority < 99: self.HPerDayProc.priority = 3
            if self.UPHcGross.priority < 99: self.UPHcGross.priority = 3
            if self.QHXProcInt.priority < 99: self.QHXProcInt.priority = 3
            if self.TEnvProc.priority < 99: self.TEnvProc.priority = 3
            if self.UAProc.priority < 99: self.UAProc.priority = 3
            if self.QEvapProc.priority < 99: self.QEvapProc.priority = 3
            
#### sense of the if: -> if the value is not needed, because massflow = 0, then priority should remain 99 = not needed

        else:
            
            self.UPH.priority = 2
            self.UPHProc.priority = 2
            self.UPHs.priority = 2
            self.UPHc.priority = 2
            self.UPHm.priority = 2 
            self.UPHw.priority = 2 
            self.PT.priority = 2
            self.QOpProc.priority = 2

            if self.PTInFlow.priority < 99: self.PTInFlow.priority = 2
            if self.PTInFlowRec.priority < 99: self.PTInFlowRec.priority = 2
            if self.PTStartUp.priority < 99: self.PTStartUp.priority = 2

########## here some verifications are redundant but they do not affect the results
            
            if self.PTOutFlow.priority < 99: self.PTOutFlow.priority = 3
            if self.PTOutFlowRec.priority < 99: self.PTOutFlowRec.priority = 3
            if self.VInFlowCycle.priority < 99: self.VInFlowCycle.priority = 3
            if self.VOutFlowCycle.priority < 99: self.VOutFlowCycle.priority = 3
            if self.VolProcMed.priority < 99: self.VolProcMed.priority = 3
            if self.TEnvProc.priority < 99: self.TEnvProc.priority = 3
            if self.UAProc.priority < 99: self.UAProc.priority = 3
            if self.QEvapProc.priority < 99: self.QEvapProc.priority = 3
            if self.QHXProc.priority < 99: self.QHXProc.priority = 3
            #if self.QWHProc.priority < 99: self.QWHProc.priority = 3
            if self.HPerYearProc.priority < 99: self.HPerYearProc.priority = 3
            if self.NBatch.priority < 99: self.NBatch.priority = 3
            if self.NDaysProc.priority < 99: self.NDaysProc.priority = 3
            if self.HPerDayProc.priority < 99: self.HPerDayProc.priority = 3
            if self.UPHcGross.priority < 99: self.UPHcGross.priority = 3
            if self.QHXProcInt.priority < 99: self.QHXProcInt.priority = 3

          
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
    def check(self):     #function that is called at the beginning when object is created
#------------------------------------------------------------------------------
#   main function carrying out the check of the block
#------------------------------------------------------------------------------

        if DEBUG in ["ALL"]:
            print "-------------------------------------------------"
            print " Process checking"
            print "-------------------------------------------------"

        for n in range(1):

            cycle.initCheckBalance()

            if DEBUG in ["ALL","MAIN"]:
                print "-------------------------------------------------"
                print "Cycle %s"%n
                print "-------------------------------------------------"
        
# Step 1: Call all calculation routines in a given sequence

            if DEBUG in ["ALL","MAIN"]:
                print "-------------------------------------------------"
                print "Step 1: calculating from left to right (CALC)"
                print "-------------------------------------------------"
                
            #self.HPerYearProc1 = calcProd("HPerYearProc1",self.NDaysProc,self.HPerDayProc)
            self.HPerYearProc.push(calcProd("HPerYearProc",self.NDaysProc,self.HPerDayProc))

            self.HPerDayOp = calcProd("HPerDayOp",self.HBatch,self.NBatch)
            self.HPerDayProc.push(calcProd("HPerDayProc",self.PartLoad,self.HPerDayOp))
                          
            for i in range(self.nInflowingStreams):
                self.VInFlowCycleEff[i].push(calcProd("VInFlowCycleEff",self.PartLoad,self.VInFlowCycle[i]))
            for i in range(self.nOutflowingStreams):
                self.VOutFlowCycleEff[i].push(calcProd("VOutFlowCycleEff",self.PartLoad,self.VOutFlowCycle[i]))
            
            self.DTLoss.push(calcDiff("DTLoss1",self.PT,self.TEnvProc))
######            calcProd_SYM(self.QLoss,self.UAProc,self.DTLoss)
            self.QLoss.push(calcProd("QLoss",self.UAProc,self.DTLoss))

###############################

            self.HPerDayOp = calcProd("HPerDayOp",self.HBatch,self.NBatch)
            self.HPerDayProc1 = calcProd("HPerDayProc1",self.PartLoad,self.HPerDayOp)
                          
            self.VInFlowCycleEff1 = calcProd("VInFlowCycleEff1",self.PartLoad,self.VInFlowCycle)
            self.VOutFlowCycleEff1 = calcProd("VOutFlowCycleEff1",self.PartLoad,self.VOutFlowCycle)
            
            # UA: add suggestion how to calculate
            self.QOpProc.push(calcSum("QOpProc",self.QLoss,self.QEvapProc))
            self.UPHm.push(calcProd("UPHm",self.QOpProc,self.HPerYearProc))
            
            for i in range(self.nInflowingStreams):
                self.UPHcdotGross[i].push(calcFlow("UPHcdotGross",self.FluidRhoCp[i],self.VInFlowCycleEff[i],
                                          self.PT,self.PTInFlow[i],
                                          self.DTUPHcGross,self.DTUPHcGross))
            #self.UPHcdotGross2 = calcFlow("UPHcdotGross2",self.FluidCp,self.mInFlowNom,
            #                              self.PT,self.PTInFlow,
            #                              self.DTUPHcGross2,self.DTUPHcGross3)
            if self.internalHR == True:
#                self.QHXdotProcInt1 = calcFlow("QHXdotProcInt1",self.FluidRhoCp_w,self.VOutFlowCycle,
#                                               self.PTOutFlowRec,self.PTOutFlow,
#                                               self.DTQHXOut,self.DTQHXOut1)

                self.dHOutFlow.push(calcDiff("dHOutFlow",self.HOutFlowRec,self.HOutFlow))
                self.QHXdotProcInt[i].push(calcProdC("QHXdotProcInt",self.FluidDensity_w,
                                                self.dHOutFlow,self.VOutFlowCycleEff))
                #self.QHXdotProcIntSumInFlow = sum(self.QHXdotProcInt)
                self.QHXdotProcInt.push(calcFlow("QHXdotProcInt",self.FluidRhoCp,self.VInFlowCycleEff.stack[1],
                                               self.PTInFlowRec,self.PTInFlow,
                                               self.DTQHXIn,self.DTQHXIn))
                 #self.QHXdotProcIntSumOutFlow = sum(self.QHXdotProcInt)
                 # elf.QHXdotProcIntSumInFlow == self.QHXdotProcIntSumOutFlow
                

            self.UPHc1 = calcProd("UPHc1",self.UPHcdot,self.NCyclesPerYear)
            self.UPHc2 = calcProdC("UPHc2",self.FluidCp,self.mInFlowYear,self.DTUPHcNet)
                
            self.UPHcdot.push(calcDiff("UPHcdot",self.UPHcdotGross,self.QHXdotProcInt))
            self.UPHcdot.push(calcFlow("UPHcdot",self.FluidRhoCp,self.VInFlowCycleEff,
                                     self.PT,self.PTInFlowRec,
                                     self.DTUPHcNet,self.DTUPHcNet))
#changed for EINSTEIN-AT            self.UPHc1 = calcProd("UPHc1",self.UPHcdot,self.NDaysProc1)
            self.UPHc.push(calcProd("UPHc",self.UPHcdot,self.NCyclesPerYear))
            self.UPHc.push(calcProdC("UPHc",self.FluidCp,self.mInFlowYear,self.DTUPHcNet))
            
            self.UPHsdot.push(calcFlow("UPHsdot",self.FluidRhoCp,self.VolProcMed,
                                     self.PT,self.PTStartUp,
                                     self.DTUPHs,self.DTUPHs))
            self.NCyclesPerYear.push(calcProd("NCyclesPerYear",self.NDaysProc,self.NBatch))
            self.UPHs.push(calcProd("UPHs",self.UPHsdot,self.NCyclesPerYear))
            
            self.UPH.push(calcSum3("UPH",self.UPHm,self.UPHc,self.UPHs))
            self.UPH.push(calcSum("UPH",self.UPHProc,self.QHXProc))

            # only if 1:1, else skip, see also adjust
            if self.internalHR == True:
                self.DTCrossHXLT.push(calcDiff("DTCrossHXLT",self.PTOutFlow,self.PTInFlow))
                self.DTCrossHXHT.push(calcDiff("DTCrossHXHT",self.PTOutFlowRec,self.PTInFlowRec))

            if self.HeatRecOK == True:
#                self.UPHw_dot1 = calcFlow("UPHw_dot1",self.FluidRhoCp_w,self.VOutFlowCycle,
#                                          self.PTOutFlow,self.PTFinal,
#                                          self.DTOutFlow,self.DTOutFlow1)

                self.dHFinal.push(calcDiff("dHFinal",self.HOutFlow,self.HFinal))
                self.UPHw_dot.push(calcProdC("UPHw_dot",self.FluidDensity_w,
                                                self.dHFinal,self.VOutFlowCycleEff))
                self.UPHw.push(calcProd("UPHw",self.mOutFlowYear,self.dHFinal))

                self.HOutFlowRec.push(calcH("HOutFlow",self.FluidCp_w,
                          self.FluidCp_w,
                          self.Fluid_hL_w,
                          self.FluidTCond_w,
                          self.PTOutFlowRec,self.XOutFlowRec))

                self.HOutFlow.push(calcH("HOutFlow",self.FluidCp_w,
                          self.FluidCp_w,
                          self.Fluid_hL_w,
                          self.FluidTCond_w,
                          self.PTOutFlow,self.XOutFlow))

                self.HFinal.push(calcH("HFinal",self.FluidCp_w,
                          self.FluidCp_w,
                          self.Fluid_hL_w,
                          self.FluidTCond_w,
                          self.PTFinal,self.XFinal))
                
                self.mOutFlowYear.push(calcProd("mOutFlowYear",self.mOutFlowNom,self.HPerYearOutFlow))
                self.mOutFlowYear.push(calcProdC("mOutFlowYear",self.FluidDensity_w,self.VOutFlowCycleEff,self.NCyclesPerYear))

            else:
                # FIXME eliminate direct stack access
                self.UPHw_dot.stack[0].setValue(0.0)
                self.UPHw.stack[1].setValue(0.0)
                
            self.UPHw.push(calcProd("UPHw",self.UPHw_dot,self.NCyclesPerYear))

            self.mInFlowYear.push(calcProd("mInFlowYear",self.mInFlowNom,self.HPerYearInFlow))
            self.mInFlowYear.push(calcProdC("mInFlowYear",self.FluidDensity,self.VInFlowCycleEff,self.NCyclesPerYear))

            if DEBUG in ["ALL","MAIN"]:
                self.showAllUPH()

# Step 2: Cross check the variables

                print "-------------------------------------------------"
                print "Step 2: cross checking"
                print "-------------------------------------------------"
                
            self.ccheckAll()            

            if DEBUG in ["ALL","MAIN"]:
                self.showAllUPH()

# Step 3: Adjust the variables (inverse of calculation routines)
                print "-------------------------------------------------"
                print "Step 3: calculating from right to left (ADJUST)"
                print "-------------------------------------------------"
                
            adjustProd_stack(self.mInFlowYear,self.mInFlowNom,self.HPerYearInFlow)
            adjustProdC_stack(self.mInFlowYear,self.FluidDensity,self.VInFlowCycleEff,self.NCyclesPerYear)


            if self.HeatRecOK == True:
#                adjustFlow(self.UPHw_dot1,self.FluidRhoCp_w,self.VOutFlowCycleEff2,
#                           self.PTOutFlow,self.PTFinal,self.DTOutFlow,self.DTOutFlow1)

                adjustH_stack(self.HOutFlowRec,self.FluidCp_w,
                          self.FluidCp_w,
                          self.Fluid_hL_w,
                          self.FluidTCond_w,
                          self.PTOutFlowRec,self.XOutFlowRec)
                
                adjustH_stack(self.HOutFlow,self.FluidCp_w,
                          self.FluidCp_w,
                          self.Fluid_hL_w,
                          self.FluidTCond_w,
                          self.PTOutFlow,self.XOutFlow)

                adjustH_stack(self.HFinal,self.FluidCp_w,
                          self.FluidCp_w,
                          self.Fluid_hL_w,
                          self.FluidTCond_w,
                          self.PTFinal,self.XFinal)
                
                adjustDiff_stack(self.dHFinal,self.HOutFlow,self.HFinal)
                adjustProdC_stack(self.UPHw_dot,self.FluidDensity_w,self.dHFinal,self.VOutFlowCycleEff)
                adjustProd_stack(self.UPHw,self.mOutFlowYear,self.dHFinal)
                
                adjustProd_stack(self.mOutFlowYear,self.mOutFlowNom,self.HPerYearOutFlow)
                adjustProdC_stack(self.mOutFlowYear,self.FluidDensity_w,self.VOutFlowCycleEff,self.NCyclesPerYear)


            else:
                self.PTFinal.update(self.PTOutFlow) #for security (link with HR module): -> zero UPHw !!!
                # FIXME: delete self.PTFinal.stack[0].update(self.PTOutFlow) #avoid conflicts !!!
                
            adjustProd_stack(self.UPHw,self.UPHw_dot,self.NCyclesPerYear)

            if self.internalHR == True:
                adjustDiff_stack(self.DTCrossHXHT,self.PTOutFlowRec,self.PTInFlowRec)
                adjustDiff_stack(self.DTCrossHXLT,self.PTOutFlow,self.PTInFlow)

                adjustFlow_stack(self.QHXdotProcInt,self.FluidRhoCp,self.VInFlowCycleEff,
                           self.PTInFlowRec,self.PTInFlow,self.DTQHXIn,self.DTQHXIn)
                
                adjustProdC_stack(self.QHXdotProcInt,self.FluidDensity_w,self.dHOutFlow,self.VOutFlowCycleEff)

            adjustDiff_stack(self.dHOutFlow,self.HOutFlowRec,self.HOutFlow)
                 
            adjustSum_stack(self.UPH,self.UPHProc,self.QHXProc)
            adjustSum3_stack(self.UPH,self.UPHm,self.UPHc,self.UPHs)
            
            adjustProd_stack(self.UPHs,self.UPHsdot,self.NCyclesPerYear)
            adjustProd_stack(self.NCyclesPerYear,self.NDaysProc,self.NBatch)

            # FIXME: delete self.PTStartUp.push()
            adjustFlow_stack(self.UPHsdot,self.FluidRhoCp,self.VolProcMed,
                       self.PT,self.PTStartUp,self.DTUPHs,self.DTUPHs)
            
            adjustProdC_stack(self.UPHc,self.FluidCp,self.mInFlowYear,self.DTUPHcNet)
            adjustProd_stack(self.UPHc,self.UPHcdot,self.NCyclesPerYear)
            adjustFlow_stack(self.UPHcdot,self.FluidRhoCp,self.VInFlowCycleEff,
                       self.PT,self.PTInFlowRec,self.DTUPHcNet,self.DTUPHcNet)
            
            adjustDiff_stack(self.UPHcdot,self.UPHcdotGross,self.QHXdotProcInt)
            #                              self.DTUPHcGross2,self.DTUPHcGross3)
            
            adjustFlow(self.UPHcdotGross1,self.FluidRhoCp,self.VInFlowCycleEff3,
                       self.PT1,self.PTInFlow4,self.DTUPHcGross,self.DTUPHcGross1)
            
            #adjustFlow(self.UPHcdotGross2,self.FluidCp,self.mInFlowNom,
            #                              self.PT4,self.PTInFlow3,
            #                              self.DTUPHcGross2,self.DTUPHcGross3)
            
            adjustProd(self.VInFlowCycleEff1,self.PartLoad,self.VInFlowCycle)
            adjustProd(self.VOutFlowCycleEff1,self.PartLoad2,self.VOutFlowCycle)

            adjustProd(self.HPerDayOp1,self.HBatch,self.NBatch)
            adjustProd(self.HPerDayProc1,self.PartLoad3,self.HPerDayOp)
                        
            adjustFlow_stack(self.UPHcdotGross,self.FluidRhoCp,self.VInFlowCycleEff,
                       self.PT,self.PTInFlow,self.DTUPHcGross,self.DTUPHcGross)
            
            adjustProd_stack(self.UPHm,self.QOpProc,self.HPerYearProc)

            # FIXME: delete self.QLoss.push()
            adjustSum_stack(self.QOpProc,self.QLoss,self.QEvapProc)
#            adjustProd(self.QLoss1,self.UAProc,self.DTLoss)
            adjustDiff_stack(self.DTLoss,self.PT,self.TEnvProc)
            
            adjustProd_stack(self.VInFlowCycleEff,self.PartLoad,self.VInFlowCycle)
            adjustProd_stack(self.VOutFlowCycleEff,self.PartLoad,self.VOutFlowCycle)

            adjustProd_stack(self.HPerDayOp,self.HBatch,self.NBatch)
            adjustProd_stack(self.HPerDayProc,self.PartLoad,self.HPerDayOp)
                        
            adjustProd_stack(self.HPerYearProc,self.NDaysProc,self.HPerDayProc)
            

            if DEBUG in ["ALL","MAIN"]:
                self.showAllUPH()
           
# Step 4: Second cross check of the variables

                print "-------------------------------------------------"
                print "Step 4: cross checking"
                print "-------------------------------------------------"
                
            self.ccheckAll()
            
            if DEBUG in ["ALL","MAIN"]:
                self.showAllUPH()

# Arrived at the end

        self.UPHcGross = calcProd("UPHcGross",self.UPHcdotGross,self.NCyclesPerYear) # Not adjusted
        self.QHXProcInt = calcProd("QHXProcInt",self.QHXdotProcInt,self.NCyclesPerYear) # Not adjusted 

    #a�adido este �ltimo show all. sino no se ven los ultimos dos resultados ...
        if DEBUG in ["ALL","BASIC"]:
            self.showAllUPH()

        cycle.checkTotalBalance()
        
 
#------------------------------------------------------------------------------
    def ccheckAll(self):    
#------------------------------------------------------------------------------
#   check block
#------------------------------------------------------------------------------

        self.mInFlowYear.check()
        self.mOutFlowYear.check()
        self.mInFlowNom.check()
        self.mOutFlowNom.check()
        
        ccheck5(self.PT,self.PT1,self.PT2,self.PT3,self.PT4,self.PT5)  
        ccheck4(self.PTInFlow,self.PTInFlow1,self.PTInFlow2,self.PTInFlow3,self.PTInFlow4)
        ccheck3(self.PartLoad,self.PartLoad1,self.PartLoad2,self.PartLoad3)
                          
        ccheck4(self.VInFlowCycleEff,self.VInFlowCycleEff1,self.VInFlowCycleEff2,self.VInFlowCycleEff3,self.VInFlowCycleEff4)
        ccheck4(self.VOutFlowCycleEff,self.VOutFlowCycleEff1,self.VOutFlowCycleEff2,self.VOutFlowCycleEff3, self.VOutFlowCycleEff4)

        self.PT.check()
        self.PTInFlow.check()
        self.PTInFlowRec.check()
        self.PTStartUp.check()
        ccheck1(self.HPerDayOp,self.HPerDayOp1)
        ccheck1(self.HBatch,self.HBatch1)
        ccheck1(self.NBatch,self.NBatch1)
                          
        ccheck1(self.NCyclesPerYear4,self.NCyclesPerYear5)
        
        self.VolProcMed.check()
        self.VInFlowCycle.check()
        self.VOutFlowCycle.check()
        self.PartLoad.check()
                          
        self.VInFlowCycleEff.check()
        self.VOutFlowCycleEff.check()
        self.PTOutFlow.check()
        self.PTOutFlowRec.check()
        self.DTCrossHXLT.check()
        self.DTCrossHXHT.check()

        self.DTUPHcNet.check()
        
        self.HPerYearProc.check()
        self.HPerDayProc.check()
        self.HPerDayOp.check()
        self.HBatch.check()
        self.NBatch.check()
                          
        self.DTLoss.check()
        self.QLoss.check()
        self.QOpProc.check()
        self.QEvapProc.check()
        self.UPHm.check()
        self.UPHcdotGross.check()
        self.QHXdotProcInt.check()
        self.UPHcdot.check()
        self.UPHc.check()
        self.UPHsdot.check()
        self.NDaysProc.check()
        self.NCyclesPerYear.check()
        self.UPHs.check()
        self.UPHProc.check()
        self.QHXProc.check()
        self.UPH.check()

        self.UPHw.check()
        self.UPHw_dot.check()
        self.DTOutFlow.check()
        self.PTFinal.check()
        self.UPHw.push(self.QWHProc) #At the moment they are the same. Change it next future when vessel heat recovery will be implemented
        self.QWHProc.push(self.UPHw)
        self.UPHw.check()
        self.QWHProc.check()
        self.UAProc.check()

        self.HOutFlow.check()
        self.HOutFlowRec.check()
        self.HFinal.check()
        self.dHOutFlow.check()
        self.dHFinal.check()
        
        self.XOutFlow.check()
        self.XOutFlowRec.check()
        self.XFinal.check()
        
#------------------------------------------------------------------------------
    def estimate(self):  
#------------------------------------------------------------------------------
#   estimates some of the data that are not sufficiently precise
#   should be a subset of the data that are within screen
#   (not necessarily ALL data have to be estimated)
#------------------------------------------------------------------------------

        if self.QHXdotProcInt.val is None or self.internalHR == False:
            self.PTOutFlowRec.setEstimate(self.PT.val,limits=(self.PT.valMin,self.PT.valMax))
            
        self.VOutFlowCycle.setEstimate(self.VInFlowCycle.val,limits=(self.VInFlowCycle.valMin,self.VInFlowCycle.valMax))
        self.PTInFlow.setEstimate(15.0,limits = (5.0,35.0))

#        if self.internalHR == True:
        if (self.PT.val - self.PTInFlow.val > 5.0):

            self.DTCrossHXHT.setEstimate(10.0,limits = (5.0,999.0))
            self.DTCrossHXLT.setEstimate(10.0,limits = (5.0,999.0))

        else:
            self.PTInFlowRec.update(self.PTInFlow)
            self.internalHR = False


        if self.NBatch.val > 0 and (self.NBatch.val is not None):
            vol1 = self.VInFlowCycle.val / self.NBatch.val
        else:
            vol1 = 0.0
            
        if self.VolProcMed.val is not None:
            vol2 = self.VolProcMed.val
        else:
            vol2 = 0.0
            
        vol = max(vol1,vol2)

        if vol < INFINITE:
        
            surface = 10.0 * pow(vol,2.0/3)
            UAmin = 0.0004 * surface * 0.1  #0.4 W/m2K well insulated vessel
            UA = 0.008 * surface
            UAmax = 0.002 * surface * 1.0   #2.0 W/m2K badly insulated equipment
            
            self.UAProc.setEstimate(UA,limits=(UAmin,UAmax))

            # estimate of Evaporation losses

        QLossMax = UAmax*self.DTLoss.valMax
        
        if self.QOpProc.valMax <= QLossMax:    # maintenance can be fully explained by
                                                # thermal losses
            self.QEvapProc.setEstimate(0.0,limits = (0.0,0.0))
            
# WARNING: this apriori assumption can give problems in cases with evaporation !!!!

        
# limits: optional and fix absolute minimum and maximum values
# sqerr: optional input that fixes the (stochastic) relative square error

#==============================================================================
if __name__ == "__main__":
    
# direct connecting to SQL database w/o GUI. for testing only
    stat = Status("testCheckProc")
    Status.SQL = MySQLdb.connect(user="root", db="einstein")
    Status.DB = pSQL.pSQL(Status.SQL, "einstein")
    Status.PId = 41
    Status.ANo = -1
#..............................................................................
    
    screen = CCScreen()
    
    ccProc = CheckProc(1)       # creates an instance of class CCheck
    ccProc.check()
    ccProc.exportData(1)

    ccProc.screen()
    screen.show()
    
#==============================================================================
