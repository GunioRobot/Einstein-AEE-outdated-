# -*- coding: utf-8 -*-
#==============================================================================                 
#
#    E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (www.iee-einstein.org)
#
#------------------------------------------------------------------------------
#
#    CCheck (Consistency Check)
#            
#------------------------------------------------------------------------------
#            
#    Short description:
#    
#    Functions for consistency checking of data
#
#==============================================================================
#
#   EINSTEIN Version No.: 1.0
#   Created by:     Claudia Vannoni, Hans Schweiger
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
#    (C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008,2009
#    www.energyxperts.net / info@energyxperts.net
#
#    This program is free software: you can redistribute it or modify it under
#    the terms of the GNU general public license as published by the Free
#    Software Foundation (www.gnu.org).
#
#==============================================================================                 
from ccheckFunctions import *
from einstein.modules.fluids import Fluid
from einstein.modules.streams import getStreams
from einstein.GUI.status import Status
from einstein.GUI.GUITools import check
from einstein.modules.constants import findKey

EPSILON = 1.e-3     # required accuracy for function "isequal"
INFINITE = 1.e99    # numerical value assigned to "infinite"
global DEBUG

class CheckProc():
    """Carry out a consistency check on given data."""
#QHXProc: recovered heat as input to the process k (source= matrix of ducts/processes). Not calculated yet
#UPHtotQ: total UPH from different sources = UPHProc+ QHXProc (the definition as to redefined into the questionnaire).
# Pay attention: both values used here per process k comes from matrix . At present assigned here.
    def __init__(self, k):
        """Setup the check with the data for process nr. k"""
        # assign a variable to all intermediate/calculated values needed
        self.ProcNo = k + 1
        
        self.PTOutFlowRec = [CCPar("PTOutFlowRec", parType="T")]  # specific to individual out-flowing stream
        self.PTFinal = [CCPar("PTFinal", parType="T")]     # specific to individual out-flowing stream
        self.HOutFlowRec = [CCPar("HOutFlowRec")]               # specific to individual out-flowing stream
        self.HFinal = [CCPar("HFinal")]                    # specific to individual out-flowing stream
        self.dHOutFlow = [CCPar("dHOutFlow")]                 # specific to individual out-flowing stream
        self.dHFinal = [CCPar("dHFinal")]                   # specific to individual out-flowing stream

        self.XOutFlow = [CCPar("XOutFlow", parType="X")]    # specific to individual out-flowing stream
        self.XOutFlowRec = [CCPar("XOutFlowRec", parType="X")] # specific to individual out-flowing stream
        self.XFinal = [CCPar("XFinal", parType="X")]      # specific to individual out-flowing stream

        self.HPerYearProc = CCPar("HPerYearProc", priority=2)
        self.HPerYearProc1 = CCPar("HPerYearProc1")
        self.HPerYearProc.valMax = 8760

        self.HPerYearInFlow1 = CCPar("HPerYearInFlow1")
        self.HPerYearOutFlow1 = CCPar("HPerYearOutFlow1")

        self.VInFlowCycleEff = [CCPar("VInFlowCycleEff Stream:??")] # specific to individual in-flowing stream      
        self.VOutFlowCycleEff = [CCPar("VOutFlowCycleEff Stream:??")] # specific to individual in-flowing stream
        
        self.FluidCp_c = CCPar("") # specific to individual in-flowing stream 
        self.FluidDensity_c = CCPar("") # specific to individual in-flowing stream 
        self.FluidRhoCp_c = CCPar("") # specific to individual in-flowing stream 

        self.NBatch1 = CCPar("NBatch1")
        self.DTLoss = CCPar("DTLoss")
        self.QLoss = CCPar("QLoss")
        self.UPHm = CCPar("UPHm")
        self.DTUPHcGross = [CCPar("DTUPHcGross", parType="DT")] # specific to individual in-flowing stream
        self.UPHcdotGross = [CCPar("UPHcdotGross")]             # specific to individual in-flowing stream
        
        self.DTQHXIn = [CCPar("DTQHXIn", parType="DT")]     # specific to individual in-flowing stream
        self.DTQHXOut = [CCPar("DTQHXOut", parType="DT")]    # specific to individual out-flowing stream
    
        self.DTCrossHXLT = CCPar("DTCrossHXLT", parType="DT")   # only for single in-flowing and single out-flowing stream
        self.DTCrossHXLT.valMin = 5.0   #engineering lower limit
        self.DTCrossHXHT = CCPar("DTCrossHXHT", parType="DT")
        self.DTCrossHXHT.valMin = 5.0   #engineering lower limit
        
        self.DTOutFlow = [CCPar("DTOutFlow", parType="DT")]   # specific to individual out-flowing stream
        self.QHXdotProcIntIn = []        # specific to individual in-flowing stream
        self.QHXdotProcIntOut = []       # specific to individual out-flowing stream
        self.QHXdotProcInt = CCPar("QHXdotProcInt") # the sum of the stream QHX
        
        self.NCyclesPerYear = CCPar("NCyclesPerYear")
        
        self.DTUPHcNet = [CCPar("DTUPHcNet", parType="DT")]   # specific to individual in-flowing stream
        self.UPHcdot = [CCPar("UPHcdot")]                  # specific to individual in-flowing stream
        self.UPHc = [CCPar("UPHc")]                 # specific to individual in-flowing stream 
        self.UPHcOfProcess = CCPar("UPHcOfProcess") # individual in-flowing streams are summed
        
        self.DTUPHs = CCPar("DTUPHs", parType="DT")
        self.UPHsdot = CCPar("UPHsdot")
        self.UPHs = CCPar("UPHs")
        
        self.UPH = CCPar("UPH")

        self.UPHwOfProcess = CCPar("UPHwOfProcess")                      # individual out-flowing streams are summed. It is the waste heat of the outflow. In general it is QWHProc but if we have a vessel it does not
        self.UPHw_dot = [CCPar("UPHw_dot")]                # specific to individual out-flowing stream
        self.UPHw = [CCPar("UPHw")]                # specific to individual out-flowing stream

        self.UPHProc = CCPar("UPHProc") 
        self.UAProc = CCPar("UAProc")
        self.QEvapProc = CCPar("QEvapProc")
        
        self.UPHcGrossProd = [CCPar("UPHcGrossProd")]           # specific to individual in-flowing stream
        self.UPHcGross = CCPar("UPHcGross")                 # individual in-flowing streams are summed
        
        self.QHXProcInt = [CCPar("QHXProcInt")]              # specific to individual in-flowing stream
        self.QHXProc = CCPar("QHXProc")                   # It comes from the matrix
        self.QWHProc = CCPar("QWHProc")                   # specific to individual out-flowing stream. It comes from the matrix. In theory it is the sum UPHwOfProcess and UPHmass (not existing yet)

        self.mInFlowYear = [CCPar("mInFlowYear")]             # specific to individual in-flowing stream
        self.mOutFlowYear = [CCPar("mOutFlowYear")]            # specific to individual out-flowing stream

        self.mInFlowNom1 = CCPar("mInFlowNom1")
        self.mInFlowNom2 = CCPar("mInFlowNom2")

        self.mOutFlowYear1 = CCPar("mOutFlowYear1")
        self.mOutFlowYear2 = CCPar("mOutFlowYear2")
        self.mOutFlowNom1 = CCPar("mOutFlowNom1")
        self.mOutFlowNom2 = CCPar("mOutFlowNom2")

        self.importData()

        if DEBUG in ["ALL", "BASIC", "MAIN"]:
            self.showAllUPH()
            
    def importStreamsData(self, dataName, streams):
        """
        Import the content of the attribute dataName of each element of
        streams into a list as the attribute dataName of self.
        
        :param dataName: the name of the attribute to import
        :param streams: the list of streams
        """
        # TODO: can this first element be more than a placeholder?
        data = getattr(self, dataName).pop() # assume singleton template variable
        for i in range(len(streams)):
            newitem = CCPar('%s %d (%s)' % (dataName, i, streams[i].Name),
                            data.parType)
            newitem.setValue(getattr(streams[i], dataName)) 
            getattr(self, dataName).append(newitem)
            
    def exportStreamsData(self, dataName, streams):
        for i in range(len(streams)):
            setattr(streams[i], dataName, check(getattr(self, dataName)[i].val))
            
    def importData(self): 
        """
        Import process data from SQL tables 
        (from AlternativeProposalNo = -1)
        """
        ANo = -1
        
        # assign empty CCPar to all questionnaire parameters
        self.PTInFlow = [CCPar("PTInFlow", parType="T")]    # specific to individual in-flowing stream
        self.PT = CCPar("PT", priority=2)
        self.PTOutFlow = [CCPar("PTOutFlow", parType="T")]   # specific to individual out-flowing stream
        self.PTInFlowRec = [CCPar("PTInFlowRec", parType="T")]  # specific to individual in-flowing stream
        self.PTStartUp = CCPar("PTStartUp", parType="T")
        self.VInFlowCycle = [CCPar("VInFlowCycle")]             # specific to individual in-flowing stream
        self.mInFlowNom = [CCPar("mInFlowNom")]               # specific to individual in-flowing stream
        self.VOutFlowCycle = [CCPar("VOutFlowCycle")]            # specific to individual out-flowing stream
        self.mOutFlowNom = [CCPar("mOutFlowNom")]              # specific to individual out-flowing stream
        self.HOutFlow = [CCPar("HOutFlow")]                 # specific to individual out-flowing stream
        self.VolProcMed = CCPar("VolProcMed")
        self.ThermalMass = CCPar("ThermalMass")
        self.NDaysProc = CCPar("NDaysProc")
        self.NDaysProc.valMax = 365
        self.HPerDayProc = CCPar("HPerDayProc")
        self.HPerDayProc.valMax = 24
        self.HPerYearInFlow = CCPar("HPerYearInFlow")             # independent of streams, assigned from single process schedule
        self.HPerYearOutFlow = CCPar("HPerYearOutFlow")            # independent of streams, assigned from single process schedule
        self.PartLoad = CCPar("PartLoad", parType="X")
        self.HBatch = CCPar("HBatch")
        self.NBatch = CCPar("NBatch")
        self.TEnvProc = CCPar("TEnvProc", parType="T")       # Now cannot be entered by questionnaire
        self.QOpProc = CCPar("QOpProc")
        self.UPH = CCPar("UPH")                        # Useful process heat asked into the questionnaire is UPH not UPHproc
        
        # read in data from table "qprocessdata"
        qprocessdataTable = Status.DB.qprocessdata.Questionnaire_id[Status.PId].AlternativeProposalNo[ANo].ProcNo[self.ProcNo]
        if len(qprocessdataTable) > 0:
            qprocessdata = qprocessdataTable[0]
            # get all in-flowing and out-flowing streams
            (self.inflowingStreams, self.outflowingStreams) = getStreams(qprocessdata.QProcessData_ID)
            self.nInflowingStreams = len(self.inflowingStreams)
            self.nOutflowingStreams = len(self.outflowingStreams)
            # import global Fluid data
            if qprocessdata.ProcMedDBFluid_id is not None:
                global_fluid = Fluid(qprocessdata.ProcMedDBFluid_id)
                self.FluidCp = global_fluid.cp
                self.FluidDensity = global_fluid.rho
                try:
                    self.FluidRhoCp = global_fluid.cp * global_fluid.rho
                except TypeError: # at least one of the operands is None
                    self.FluidRhoCp = None
            else:
                self.FluidCp = None
                self.FluidDensity = None
                self.FluidRhoCp = None
            self.FluidCp_c = [None] * self.nInflowingStreams
            self.FluidDensity_c = [None] * self.nInflowingStreams
            self.FluidRhoCp_c = [None] * self.nInflowingStreams
            self.VInFlowCycleEff = [None] * self.nInflowingStreams
            self.mInFlowYear = [None] * self.nInflowingStreams
            self.UPHcGrossProd = [None] * self.nInflowingStreams
            self.UPHcdotGross = [None] * self.nInflowingStreams
            self.DTUPHcGross = [None] * self.nInflowingStreams 
            self.DTQHXIn = [None] * self.nInflowingStreams
            self.UPHcdot = [None] * self.nInflowingStreams
            self.DTUPHcNet = [None] * self.nInflowingStreams
            for i in range(self.nInflowingStreams):
                stream = self.inflowingStreams[i]
                stream_fluid = Fluid(findKey(Status.prj.getFluidDict(), stream.Medium))   #IMPORT from the FluidDB
                self.FluidCp_c[i] = stream_fluid.cp
                self.FluidDensity_c[i] = stream_fluid.rho
                self.FluidRhoCp_c[i] = self.FluidCp_c[i] * self.FluidDensity_c[i]
                self.VInFlowCycleEff[i] = CCPar("VInFlowCycleEff Stream: %s" % (stream.Name,))
                self.mInFlowYear[i] = CCPar("mInFlowYear Stream: %s" % (stream.Name,))
                self.UPHcGrossProd[i] = CCPar("UPHcGrossProd Stream: %s" % (stream.Name,))
                self.UPHcdotGross[i] = CCPar("DTUPHcdotGross") 
                self.DTUPHcGross[i] = CCPar("DTUPHcGross", parType="DT") 
                self.DTQHXIn[i] = CCPar("DTQHXIn Stream: %s" % (stream.Name,), parType="DT")
                self.UPHcdot[i] = CCPar("UPHcdot Stream: %s" % (stream.Name,))
                self.DTUPHcNet[i] = CCPar("DTUPHcNet Stream: %s" % (stream.Name,), parType="DT")
            self.importStreamsData('PTInFlow', self.inflowingStreams)
            self.PT.setValue(qprocessdata.PT, err=0.0)   # if specified, take as fixed
            self.importStreamsData('PTOutFlow', self.outflowingStreams)
            # if no temperature or enthalpy for Outflow is specified, 
            # start with PT as initial estimate
            # but leave error range from 0 to infinite !!!!
            self.importStreamsData('PTOutFlowRec', self.outflowingStreams)
            self.VOutFlowCycleEff = [None] * self.nOutflowingStreams
            self.dHOutFlow = [None] * self.nOutflowingStreams
            self.dHOutFlowRec = [None] * self.nOutflowingStreams
            self.HOutFlowRec = [None] * self.nOutflowingStreams
            self.HFinal = [None] * self.nOutflowingStreams
            self.dHFinal = [None] * self.nOutflowingStreams
            self.UPHw_dot = [None] * self.nOutflowingStreams
            self.mOutFlowYear = [None] * self.nOutflowingStreams
            self.XOutFlowRec = [None] * self.nOutflowingStreams
            self.XFinal = [None] * self.nOutflowingStreams
            for i in range(self.nOutflowingStreams):
                stream = self.outflowingStreams[i]
                if stream.PTOutFlow is None and stream.HOutFlow is None:
                    self.PTOutFlow[i].val = self.PT.val
                    self.PTOutFlowRec[i].val = self.PT.val
                if stream.HeatRecExist != True: # could be None, which means No
                    self.PTOutFlowRec[i].update(self.PTOutFlow[i])
                self.VOutFlowCycleEff[i] = CCPar("VOutFlowCycleEff Stream: %s" 
                                                 % (stream.Name,))
                self.dHOutFlow[i] = CCPar("dHOutFlow Stream: %s" 
                                          % (stream.Name,))
                self.HOutFlowRec[i] = CCPar("HOutFlowRec Stream: %s"
                                             % (stream.Name,))
                self.dHOutFlowRec[i] = CCPar("dHOutFlowRec Stream: %s" 
                                             % (stream.Name,))
                self.HFinal[i] = CCPar("HFinal Stream: %s" % (stream.Name,))
                self.dHFinal[i] = CCPar("dHFinal Stream: %s" % (stream.Name,))
                self.UPHw_dot[i] = CCPar("UPHw_dot Stream: %s" 
                                         % (stream.Name,)) 
                self.mOutFlowYear[i] = CCPar("mOutFlowYear Stream: %s"
                                             % (stream.Name,)) 
                self.XOutFlowRec[i] = CCPar("XOutFlowRec Stream: %s"
                                            % (stream.Name,)) 
                self.XFinal[i] = CCPar("XFinal Stream: %s" % (stream.Name,),
                                       parType="X")   
            self.importStreamsData('HOutFlow', self.outflowingStreams)
            self.importStreamsData('XOutFlow', self.outflowingStreams)
            self.importStreamsData('PTInFlowRec', self.inflowingStreams)
            self.importStreamsData('mInFlowNom', self.inflowingStreams)
            self.importStreamsData('VInFlowCycle', self.inflowingStreams)
            self.importStreamsData('mOutFlowNom', self.outflowingStreams)
            self.importStreamsData('VOutFlowCycle', self.outflowingStreams)
            self.importStreamsData('UPHc', self.inflowingStreams)
            self.importStreamsData('UPHw', self.outflowingStreams)             
            
            self.PTStartUp.setValue(qprocessdata.PTStartUp)
            self.VolProcMed.setValue(qprocessdata.VolProcMed) 
            self.ThermalMass.setValue(qprocessdata.ThermalMass)
            self.NDaysProc.setValue(qprocessdata.NDaysProc, err=0.0) # number -> exact value
            self.HPerDayProc.setValue(qprocessdata.HPerDayProc)
            self.HPerYearInFlow.setValue(qprocessdata.HPerYearInFlow)
            self.HPerYearOutFlow.setValue(qprocessdata.HPerYearOutFlow)

            if qprocessdata.PartLoad is None:   # should be always set from GUI, but for being sure!
                self.PartLoad.setValue(1.0, err=0.0)
            else:
                self.PartLoad.setValue(qprocessdata.PartLoad)

            # if 24.0 hours are specified, suppose that this value is exact.
            if self.HPerDayProc.val > 23.99:
                self.HPerDayProc.setValue(24.0, err=0.0)
                
            if qprocessdata.NBatch is None:
                self.NBatch.setValue(1.0, err=0.0)   # if no number is specified, suppose 1!
            else:
                self.NBatch.setValue(qprocessdata.NBatch, err=0.0) #number -> exact value

            self.HBatch.setValue(qprocessdata.HBatch)

            self.importStreamsData('PTFinal', self.outflowingStreams)
            self.HeatRecOK = [None] * self.nOutflowingStreams
            for i in range(self.nOutflowingStreams):
                if self.outflowingStreams[i].HeatRecOK is None:
                    logWarning(_("Possibility of heat recovery for process no. %s (%s) stream %d (%s) is not specified.\nYES is assumed." % (self.ProcNo, qprocessdata.Process, i, self.outflowingStreams[i].Name)))
                    self.HeatRecOK[i] = True
                else:
                    self.HeatRecOK[i] = self.outflowingStreams[i].HeatRecOK
                if self.HeatRecOK[i] and self.outflowingStreams[i].PTFinal is None: #read in PT final only if heat recovery is possible!
                        logMessage(_("No limit specified for cooling of outgoing stream %d (%s). 0 °C is assumed" % (i, self.outflowingStreams[i].Name)))
                        self.PTFinal[i].setValue(0.0)
                
            if qprocessdata.TEnvProc is None:
                self.TEnvProc.setValue(18.0)
            else:
                self.TEnvProc.setValue(qprocessdata.TEnvProc)
            self.QOpProc.setValue(qprocessdata.QOpProc) 
            self.UPH.setValue(qprocessdata.UPH, err=0.0) # if specified, take exact value 

            self.internalHR = [None] * self.nInflowingStreams
            self.FluidCp_w = [None] * self.nOutflowingStreams
            self.FluidDensity_w = [None] * self.nOutflowingStreams
            self.FluidRhoCp_w = [None] * self.nOutflowingStreams
            self.Fluid_hL_w = [None] * self.nOutflowingStreams
            self.FluidTCond_w = [None] * self.nOutflowingStreams
            for i in range(self.nInflowingStreams):
                self.internalHR[i] = not (isequal(self.PTInFlow[i].val, self.PTInFlowRec[i].val) 
                                          or (self.PTInFlowRec[i].val is None) 
                                          or (self.PT.val < self.PTInFlow[i].val + 5.0)  # TODO: cooling needs different sign or similar
                                          )
            for i in xrange(self.nOutflowingStreams):
                if self.HeatRecOK[i] or any(self.internalHR):   # fluid pars only needed in this case
                    stream_fluid_w = Fluid(findKey(Status.prj.getFluidDict(), self.outflowingStreams[i].Medium))   #IMPORT from the FluidDB
                    self.FluidCp_w[i] = stream_fluid_w.cp
                    self.FluidDensity_w[i] = stream_fluid_w.rho
                    self.FluidRhoCp_w[i] = self.FluidCp_w[i] * self.FluidDensity_w[i]
                    self.Fluid_hL_w[i] = stream_fluid_w.hL
                    self.FluidTCond_w[i] = stream_fluid_w.TCond
            

    def exportData(self):  
        """
        Store corrected data in SQL (under AlternativeProposalNo = 0)
        """
        ANo = 0
        # write data into table "qprocessdata", "streams_in" and "streams_out"
        qprocessdataTable = Status.DB.qprocessdata.Questionnaire_id[Status.PId].AlternativeProposalNo[ANo].ProcNo[self.ProcNo]
        if len(qprocessdataTable) > 0:
            qprocessdata = qprocessdataTable[0]
            procId = qprocessdata.QProcessData_ID
            self.exportStreamsData("PTInFlow", self.inflowingStreams)
            qprocessdata.PT = check(self.PT.val)
            self.exportStreamsData("PTOutFlow", self.outflowingStreams)
            self.exportStreamsData("PTOutFlowRec", self.outflowingStreams)
            self.exportStreamsData("HOutFlow", self.outflowingStreams)
            self.exportStreamsData("PTInFlow", self.inflowingStreams)
            self.exportStreamsData("PTInFlowRec", self.inflowingStreams)
            qprocessdata.PTStartUp = check(self.PTStartUp.val)
            self.exportStreamsData("PTFinal", self.outflowingStreams)
            self.exportStreamsData("VInFlowCycle", self.inflowingStreams)
            self.exportStreamsData("mInFlowNom", self.inflowingStreams)
            self.exportStreamsData("VOutFlowCycle", self.outflowingStreams)
            self.exportStreamsData("mOutFlowNom", self.outflowingStreams)
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
            qprocessdata.QHXProcInt = check(calcRowSum("QHXProcInt", self.QHXProcInt).val)
            qprocessdata.UPHm = check(self.UPHm.val)
            qprocessdata.UPHs = check(self.UPHs.val)
            self.exportStreamsData("UPHc", self.inflowingStreams)
            qprocessdata.UPH = check(self.UPH.val)
            qprocessdata.UPHc = check(self.UPHcOfProcess.val)
            qprocessdata.UPHw = check(self.UPHwOfProcess.val)
            self.exportStreamsData("UPHw", self.outflowingStreams)
            qprocessdata.QWHProc = check(self.QWHProc.val)
            qprocessdata.QHXProc = check(self.QHXProc.val)
            for i in range(self.nOutflowingStreams):
                self.outflowingStreams[i].HeatRecOK = self.HeatRecOK[i]
            for stream in self.inflowingStreams:
                stream.saveToDB(procId, ANo)
            for stream in self.outflowingStreams:
                stream.saveToDB(procId, ANo)
            Status.SQL.commit()
        else:
            print "CheckProc (exportData): error writing data to qprocessdata"

    def showAllUPH(self):
        print "====================="
        for item in (
        self.UPH,
        self.UPHm,
        self.UPHs,
        self.UPHwOfProcess,
        self.UPHsdot,
        self.UPHProc,
        self.QHXProc,
        self.UPHcOfProcess,
        self.UPHcdot,
        self.UPHcdotGross, # For convention UPH and UPHcOfProcess are net!
        self.UPHcGross,
        self.UPHw_dot,
        self.QHXProcInt,
        self.DTUPHcGross,
        self.QOpProc,
        self.VolProcMed,
        self.HPerYearProc,
        self.HPerDayProc,
        self.NDaysProc,
        self.VInFlowCycleEff,
        self.VOutFlowCycle,
        self.PTInFlow,
        self.PT,
        self.PTInFlowRec,
        self.PTOutFlow,
        self.HOutFlow,
        self.PTStartUp,
        self.PTFinal,
        self.HFinal,
        self.PTOutFlowRec,
        self.HOutFlowRec,
        self.NBatch,
        self.UAProc,
        self.QEvapProc,
        self.TEnvProc,
        self.DTLoss,
        self.QLoss,
        self.DTUPHcGross,
        self.DTQHXIn,
        self.DTQHXOut,
        self.NCyclesPerYear,
        self.DTUPHcNet,
        self.DTUPHs,
        self.QWHProc,
        self.QHXProc):
            item.show()
        print "HeatRecOK: ", self.HeatRecOK
        print "====================="

    def screen(self):  
        """screen all variables in the block"""
        # Change of priority for parameters not needed
        for i in range(self.nInflowingStreams):
            if iszero(self.VInFlowCycle[i]):
                self.PTInFlow[i].priority = 99
                self.PTInFlowRec[i].priority = 99
        for i in range(self.nOutflowingStreams):
            if iszero(self.VOutFlowCycle[i]) or (self.HeatRecOK[i] == False):
                self.PTOutFlow[i].priority = 99
                self.PTOutFlowRec[i].priority = 99
        if iszero(self.VolProcMed):
            self.PTStartUp.priority = 99
        if iszero(self.QOpProc):
            self.TEnvProc.priority = 99
            self.UAProc.priority = 99

        self.UPH.screen()
        self.UPHcOfProcess.screen()
        self.UPHm.screen()
        self.UPHs.screen()
        self.UPHwOfProcess.screen()
        # self.QWHProc.screen() Now it coincides with UPHwOfProcess
        self.UPHProc.screen()
        self.QHXProc.screen()
        self.UPHcGross.screen()
        for i in xrange(self.nInflowingStreams):
            self.QHXProcInt[i].screen()
        self.PT.screen()
        for i in range(self.nInflowingStreams):
            self.PTInFlow[i].screen()
            self.PTInFlowRec[i].screen()
        for i in range(self.nOutflowingStreams):
            self.PTOutFlow[i].screen()
            self.PTOutFlowRec[i].screen() 
        self.PTStartUp.screen()
        for i in range(self.nInflowingStreams):
            self.VInFlowCycle[i].screen()
            self.mInFlowNom[i].screen()
        for i in range(self.nOutflowingStreams):
            self.VOutFlowCycle[i].screen()
            self.mOutFlowNom[i].screen()
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
        
    def definePriority(self, mainProcess):
        """
        Change the priority in function of the importance of the process
        @param mainProcess:
        """
        if mainProcess == True:
            
            self.UPH.priority = 1
            self.UPHProc.priority = 1
            self.UPHs.priority = 1
            self.UPHcOfProcess.priority = 1
            self.UPHm.priority = 1
            self.UPHwOfProcess.priority = 1 
            self.PT.priority = 1
            self.QOpProc.priority = 1

            for i in range(self.nInflowingStreams):
                if self.PTInFlow[i].priority < 99: self.PTInFlow[i].priority = 1
                if self.PTInFlowRec[i].priority < 99: self.PTInFlowRec[i].priority = 1
            if self.PTStartUp.priority < 99: self.PTStartUp.priority = 1

            # here some verifications are redundant but they do not affect the results
            for i in range(self.nOutflowingStreams):
                if self.PTOutFlow[i].priority < 99: self.PTOutFlow[i].priority = 2
                if self.PTOutFlowRec[i].priority < 99: self.PTOutFlowRec[i].priority = 2
                if self.VOutFlowCycle[i].priority < 99: self.VOutFlowCycle[i].priority = 2
            for i in range(self.nInflowingStreams):
                if self.VInFlowCycle[i].priority < 99: self.VInFlowCycle[i].priority = 2

            if self.VolProcMed.priority < 99: self.VolProcMed.priority = 2
            if self.QHXProc.priority < 99: self.QHXProc.priority = 2
            #if self.QWHProc.priority < 99: self.QWHProc.priority = 2 Now it coincides with UPHwOfProcess. Assigned priority 2 coherent with the QHX
            if self.HPerYearProc.priority < 99: self.HPerYearProc.priority = 2
            
            if self.NBatch.priority < 99: self.NBatch.priority = 3
            if self.NDaysProc.priority < 99: self.NDaysProc.priority = 3
            if self.HPerDayProc.priority < 99: self.HPerDayProc.priority = 3
            if self.UPHcGross.priority < 99: self.UPHcGross.priority = 3
            for i in xrange(self.nInflowingStreams):
                if self.QHXProcInt[i].priority < 99: self.QHXProcInt[i].priority = 3
            if self.TEnvProc.priority < 99: self.TEnvProc.priority = 3
            if self.UAProc.priority < 99: self.UAProc.priority = 3
            if self.QEvapProc.priority < 99: self.QEvapProc.priority = 3
            
            # sense of the if: -> if the value is not needed, because massflow = 0, then priority should remain 99 = not needed

        else:
            
            self.UPH.priority = 2
            self.UPHProc.priority = 2
            self.UPHs.priority = 2
            self.UPHcOfProcess.priority = 2
            self.UPHm.priority = 2 
            self.UPHwOfProcess.priority = 2 
            self.PT.priority = 2
            self.QOpProc.priority = 2

            for i in range(self.nInflowingStreams):
                if self.PTInFlow[i].priority < 99: self.PTInFlow[i].priority = 2
                if self.PTInFlowRec[i].priority < 99: self.PTInFlowRec[i].priority = 2
            if self.PTStartUp.priority < 99: self.PTStartUp.priority = 2

            # here some verifications are redundant but they do not affect the results
            for i in range(self.nOutflowingStreams):
                if self.PTOutFlow[i].priority < 99: self.PTOutFlow[i].priority = 3
                if self.PTOutFlowRec[i].priority < 99: self.PTOutFlowRec[i].priority = 3
                if self.VOutFlowCycle[i].priority < 99: self.VOutFlowCycle[i].priority = 3
            for i in range(self.nInflowingStreams):
                if self.VInFlowCycle[i].priority < 99: self.VInFlowCycle[i].priority = 3
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
            for i in range(self.nInflowingStreams):
                if self.UPHcGross[i].priority < 99: self.UPHcGross[i].priority = 3
                if self.QHXProcInt[i].priority < 99: self.QHXProcInt[i].priority = 3

    def check(self):     #function that is called at the beginning when object is created
        """main function, carry out the check of the block"""
        if DEBUG in ["ALL"]:
            print "-------------------------------------------------"
            print " Process checking"
            print "-------------------------------------------------"
        # check/create basic consistency assumptions
        for i in xrange(self.nInflowingStreams):
            if self.inflowingStreams[i].HeatRecExist == False:
                # no HR means the temperatures have to be equal
                self.PTInFlowRec[i].update(self.PTInFlow[i]) 
        
        for n in range(1):
            cycle.initCheckBalance()
            if DEBUG in ["ALL", "MAIN"]:
                print "-------------------------------------------------"
                print "Cycle %s" % n
                print "-------------------------------------------------"
            # Step 1: Call all calculation routines in a given sequence
            if DEBUG in ["ALL", "MAIN"]:
                print "-------------------------------------------------"
                print "Step 1: calculating from left to right (CALC)"
                print "-------------------------------------------------"
            self.HPerYearProc.push(calcProd("HPerYearProc", self.NDaysProc, self.HPerDayProc))
            self.HPerDayOp = calcProd("HPerDayOp", self.HBatch, self.NBatch)
            self.HPerDayProc.push(calcProd("HPerDayProc", self.PartLoad, self.HPerDayOp))
            for i in range(self.nInflowingStreams):
                self.VInFlowCycleEff[i].push(calcProd("VInFlowCycleEff", self.PartLoad, self.VInFlowCycle[i]))
            for i in range(self.nOutflowingStreams):
                self.VOutFlowCycleEff[i].push(calcProd("VOutFlowCycleEff", self.PartLoad, self.VOutFlowCycle[i]))

###CHECK: cooling - reverse sign. DTLoss should be allowed both negative and positive values !!!            
            self.DTLoss.push(calcDiff("DTLoss1", self.PT, self.TEnvProc))
######            calcProd_SYM(self.QLoss,self.UAProc,self.DTLoss)
            self.QLoss.push(calcProd("QLoss", self.UAProc, self.DTLoss))

            self.HPerDayOp = calcProd("HPerDayOp", self.HBatch, self.NBatch)
            self.HPerDayProc1 = calcProd("HPerDayProc1", self.PartLoad, self.HPerDayOp)
            # UA: add suggestion how to calculate
            self.QOpProc.push(calcSum("QOpProc", self.QLoss, self.QEvapProc))
            self.UPHm.push(calcProd("UPHm", self.QOpProc, self.HPerYearProc))
            for i in range(self.nInflowingStreams):
###CHECK cooling: reverse order of PT and PTInFlow
                self.UPHcdotGross[i].push(calcFlow("UPHcdotGross", self.FluidRhoCp_c[i], self.VInFlowCycleEff[i],
                                          self.PT, self.PTInFlow[i],
                                          self.DTUPHcGross[i], self.DTUPHcGross[i]))
            if any(self.internalHR):
#                self.QHXdotProcInt1 = calcFlow("QHXdotProcInt1",self.FluidRhoCp_w,self.VOutFlowCycle,
#                                               self.PTOutFlowRec,self.PTOutFlow,
#                                                   self.DTQHXOut,self.DTQHXOut1)
                self.QHXdotProcIntIn = [CCPar("QHXdotProcIntIn, stream: %s" % (stream.Name)) 
                                         for stream in self.inflowingStreams] 
                self.QHXdotProcIntOut = [CCPar("QHXdotProcIntOut, stream: %s" % (stream.Name)) 
                                         for stream in self.outflowingStreams]
                for i in range(self.nOutflowingStreams):
###CHECK cooling: reverse order of HOutFlowRec and HOutFlow
                    self.dHOutFlow[i].push(calcDiff("dHOutFlow", self.HOutFlowRec[i], self.HOutFlow[i]))
                    self.QHXdotProcIntOut[i].push(calcProdC("QHXdotProcInt", self.FluidDensity_w[i],
                                                self.dHOutFlow[i], self.VOutFlowCycleEff[i]))
                for i in range(self.nInflowingStreams):
###CHECK cooling: reverse order of PT's
                    self.QHXdotProcIntIn[i].push(calcFlow("QHXdotProcInt", self.FluidRhoCp_c[i], self.VInFlowCycleEff[i],
                                               self.PTInFlowRec[i], self.PTInFlow[i],
                                               self.DTQHXIn[i], self.DTQHXIn[i]))
                self.QHXdotProcInt.push(calcRowSum("QHXdotProcInt", self.QHXdotProcIntIn))
                self.QHXdotProcInt.push(calcRowSum("QHXdotProcInt", self.QHXdotProcIntOut))
                
            else:
                self.QHXdotProcIntIn = [CCPar("QHXdotProcIntIn, stream: %s" % (stream.Name)) 
                                         for stream in self.inflowingStreams] 
                self.QHXdotProcIntOut = [CCPar("QHXdotProcIntOut, stream: %s" % (stream.Name)) 
                                         for stream in self.outflowingStreams]
                self.QHXdotProcIntIn = [par.value(0) for par in self.QHXdotProcIntIn]
                self.QHXdotProcIntOut = [par.value(0) for par in self.QHXdotProcIntOut]
            for i in range(self.nInflowingStreams):
                self.UPHcdot[i].push(calcDiff("UPHcdot", self.UPHcdotGross[i], self.QHXdotProcIntIn[i]))
###CHECK cooling: reverse order of PT's
                self.UPHcdot[i].push(calcFlow("UPHcdot", self.FluidRhoCp_c[i], self.VInFlowCycleEff[i],
                                     self.PT, self.PTInFlowRec[i],
                                     self.DTUPHcNet[i], self.DTUPHcNet[i]))
                self.UPHc[i].push(calcProdC("UPHcProd_%d" % i, self.FluidCp_c[i], self.mInFlowYear[i], self.DTUPHcNet[i]))
            
            self.UPHcOfProcess.push(calcRowSum("UPHcOfProcess", self.UPHc))

            sumUPHcdot = calcRowSum('UPHc_streamSum', self.UPHcdot)
            self.UPHcOfProcess.push(calcProd("UPHcOfProcess", sumUPHcdot, self.NCyclesPerYear))
            UPHcStreams = [None] * self.nInflowingStreams
            for i in xrange(self.nInflowingStreams):
                stream = self.inflowingStreams[i]
                UPHcStreams[i] = calcProdC("UPHcOfProcess of stream: %s" % (stream.Name,),
                                        self.FluidCp_c[i], self.mInFlowYear[i],
                                        self.DTUPHcNet[i])
            self.UPHcOfProcess.push(calcRowSum("UPHcOfProcess", UPHcStreams))
            
            if self.FluidRhoCp is not None:

###CHECK cooling: reverse order of PT's, allow negative values for DT's
                self.UPHsdot.push(calcFlow("UPHsdot", self.FluidRhoCp, self.VolProcMed,
                                           self.PT, self.PTStartUp,
                                           self.DTUPHs, self.DTUPHs))
###CHECK: the following equations for DTUPHs and UPHsdot should already be included in the calcFLow function above -> revise if the corresponding push()-commands are included
### -> if necessary create a function calcFlow_stack
            self.DTUPHs.push(calcDiff("DTUPHs", self.PT, self.PTStartUp))
            self.UPHsdot.push(calcProd("UPHsdot", self.ThermalMass, self.DTUPHs))
            if self.FluidRhoCp is not None:
                self.UPHsdot.push(calcProdC("UPHsdot", self.FluidRhoCp, self.VolProcMed, self.DTUPHs))
            self.NCyclesPerYear.push(calcProd("NCyclesPerYear", self.NDaysProc, self.NBatch))
            self.UPHs.push(calcProd("UPHs", self.UPHsdot, self.NCyclesPerYear))
            self.UPH.push(calcSum3("UPH", self.UPHm, self.UPHcOfProcess, self.UPHs))
            self.UPH.push(calcSum("UPH", self.UPHProc, self.QHXProc))

            # only if single in-flowing and single out-flowing stream, else skip, see also adjust
            if (self.nInflowingStreams == self.nOutflowingStreams == 1) and any(self.internalHR):

###CHECK cooling: reverse order of PT's
                self.DTCrossHXLT.push(calcDiff("DTCrossHXLT", self.PTOutFlow[0], self.PTInFlow[0]))
###CHECK cooling: reverse order of PT's
                self.DTCrossHXHT.push(calcDiff("DTCrossHXHT", self.PTOutFlowRec[0], self.PTInFlowRec[0]))
            
            for i in range(self.nOutflowingStreams):
                if self.HeatRecOK[i]:
#                   self.UPHw_dot1 = calcFlow("UPHw_dot1",self.FluidRhoCp_w,self.VOutFlowCycle,
#                                          self.PTOutFlow,self.PTFinal,
#                                          self.DTOutFlow,self.DTOutFlow1)
###CHECK cooling: reverse order of H's
                    self.dHFinal[i].push(calcDiff("dHFinal", self.HOutFlow[i], self.HFinal[i]))
                    self.UPHw_dot[i].push(calcProdC("UPHw_dot", self.FluidDensity_w[i],
                                                 self.dHFinal[i], self.VOutFlowCycleEff[i]))
###CHECK: nomenclature, see above
                    self.UPHw[i].push(calcProd("UPHwProd_%d" % i, self.mOutFlowYear[i], self.dHFinal[i]))
                    self.HOutFlowRec[i].push(calcH("HOutFlow", self.FluidCp_w[i],
                                                   self.FluidCp_w[i],
                                                   self.Fluid_hL_w[i],
                                                   self.FluidTCond_w[i],
                                                   self.PTOutFlowRec[i], self.XOutFlowRec[i]))
                    self.HOutFlow[i].push(calcH("HOutFlow", self.FluidCp_w[i],
                                                self.FluidCp_w[i],
                                                self.Fluid_hL_w[i],
                                                self.FluidTCond_w[i],
                                                self.PTOutFlow[i], self.XOutFlow[i]))
                    self.HFinal[i].push(calcH("HFinal", self.FluidCp_w[i],
                                              self.FluidCp_w[i],
                                              self.Fluid_hL_w[i],
                                              self.FluidTCond_w[i],
                                              self.PTFinal[i], self.XFinal[i]))
                    self.mOutFlowYear[i].push(calcProd("mOutFlowYear", self.mOutFlowNom[i], self.HPerYearOutFlow))
                    self.mOutFlowYear[i].push(calcProdC("mOutFlowYear", self.FluidDensity_w[i], self.VOutFlowCycleEff[i], self.NCyclesPerYear))
###CHECK: sum of massflows should be added
                else:
                    self.UPHw_dot[i].setValue(0.0)
                    self.UPHw_dot[i].push()
                    self.UPHwOfProcess.setValue(0.0)
                    self.UPHwOfProcess.push()
                
            UPHw_streamSum = calcRowSum('UPHw_streamSum', self.UPHw_dot)
            self.UPHwOfProcess.push(calcProd("UPHwOfProcess", UPHw_streamSum, self.NCyclesPerYear))

            for i in range(self.nInflowingStreams):
                self.mInFlowYear[i].push(calcProd("mInFlowYear", self.mInFlowNom[i], self.HPerYearInFlow))
                self.mInFlowYear[i].push(calcProdC("mInFlowYear", self.FluidDensity_c[i], self.VInFlowCycleEff[i], self.NCyclesPerYear))

###CHECK: sum of massflows should be added

            if DEBUG in ["ALL", "MAIN"]:
                self.showAllUPH()

# Step 2: Cross check the variables

                print "-------------------------------------------------"
                print "Step 2: cross checking"
                print "-------------------------------------------------"
                
            self.ccheckAll()            

            # Step 3: Adjust the variables (inverse of calculation routines)
            if DEBUG in ["ALL", "MAIN"]:
                self.showAllUPH()
                print "-------------------------------------------------"
                print "Step 3: calculating from right to left (ADJUST)"
                print "-------------------------------------------------"
            # check/create basic consistency assumptions
            for i in xrange(self.nInflowingStreams):
                if self.inflowingStreams[i].HeatRecExist == False:
                    # no HR means the temperatures have to be equal
                    self.PTInFlowRec[i].update(self.PTInFlow[i]) 
            
            for i in range(self.nInflowingStreams):
                adjustProd_stack(self.mInFlowYear[i], self.mInFlowNom[i], self.HPerYearInFlow)
                adjustProdC_stack(self.mInFlowYear[i], self.FluidDensity_c[i], self.VInFlowCycleEff[i], self.NCyclesPerYear)

            for i in range(self.nOutflowingStreams):
                if self.HeatRecOK[i]:
                    #                adjustFlow(self.UPHw_dot1,self.FluidRhoCp_w,self.VOutFlowCycleEff2,
#                                     self.PTOutFlow,self.PTFinal,self.DTOutFlow,self.DTOutFlow1)
                    adjustH_stack(self.HOutFlowRec[i], self.FluidCp_w[i],
                                  self.FluidCp_w[i],
                                  self.Fluid_hL_w[i],
                                  self.FluidTCond_w[i],
                                  self.PTOutFlowRec[i], self.XOutFlowRec[i])
                    adjustH_stack(self.HOutFlow[i], self.FluidCp_w[i],
                                  self.FluidCp_w[i],
                                  self.Fluid_hL_w[i],
                                  self.FluidTCond_w[i],
                                  self.PTOutFlow[i], self.XOutFlow[i])
                    adjustH_stack(self.HFinal[i], self.FluidCp_w[i],
                              self.FluidCp_w[i],
                              self.Fluid_hL_w[i],
                              self.FluidTCond_w[i],
                              self.PTFinal[i], self.XFinal[i])
                    adjustDiff_stack(self.dHFinal[i], self.HOutFlow[i], 
                                     self.HFinal[i])
                    adjustProdC_stack(self.UPHw_dot[i], self.FluidDensity_w[i], 
                                      self.dHFinal[i], self.VOutFlowCycleEff[i])
                    adjustProd_stack(self.UPHw[i], self.mOutFlowYear[i], 
                                     self.dHFinal[i])
                    adjustProd_stack(self.mOutFlowYear[i], self.mOutFlowNom[i],
                                     self.HPerYearOutFlow)  
                    adjustProdC_stack(self.mOutFlowYear[i], 
                                      self.FluidDensity_w[i],
                                      self.VOutFlowCycleEff[i], 
                                      self.NCyclesPerYear)
                    adjustProd_stack(self.mOutFlowYear[i], self.mOutFlowNom[i], self.HPerYearOutFlow)
                    adjustProdC_stack(self.mOutFlowYear[i], self.FluidDensity_w[i], self.VOutFlowCycleEff[i], self.NCyclesPerYear)
    
                else:
                    self.PTFinal[i].update(self.PTOutFlow[i]) #for security (link with HR module): -> zero UPHwOfProcess !!!
                    self.PTFinal[i].push()
                    
            adjustSumOfProds_stack(self.UPHwOfProcess, self.UPHw_dot, 
                                   (self.NCyclesPerYear,) * self.nOutflowingStreams)

            adjRowSum_stack(self.QHXdotProcInt, self.QHXdotProcIntIn, self.nInflowingStreams)
            adjRowSum_stack(self.QHXdotProcInt, self.QHXdotProcIntOut, self.nOutflowingStreams)
            # TODO: Why only single in/out, why no generic loop? 
            if (self.nInflowingStreams == self.nOutflowingStreams == 1) and any(self.internalHR):
                adjustDiff_stack(self.DTCrossHXHT, self.PTOutFlowRec[0], self.PTInFlowRec[0])
                adjustDiff_stack(self.DTCrossHXLT, self.PTOutFlow[0], self.PTInFlow[0])
                adjustFlow_stack(self.QHXdotProcIntIn[0], self.FluidRhoCp_c[0], self.VInFlowCycleEff[0],
                                 self.PTInFlowRec[0], self.PTInFlow[0], self.DTQHXIn[0], self.DTQHXIn[0])
                adjustProdC_stack(self.QHXdotProcIntIn[0], self.FluidDensity_w[0], self.dHOutFlow[0], self.VOutFlowCycleEff[0])
            for i in range(self.nOutflowingStreams):
                adjustDiff_stack(self.dHOutFlow[i], self.HOutFlowRec[i], self.HOutFlow[i])
                 
            adjustSum_stack(self.UPH, self.UPHProc, self.QHXProc)
            adjustSum3_stack(self.UPH, self.UPHm, self.UPHcOfProcess, self.UPHs)
            
            adjustProd_stack(self.UPHs, self.UPHsdot, self.NCyclesPerYear)
            adjustProd_stack(self.NCyclesPerYear, self.NDaysProc, self.NBatch)

            if self.FluidRhoCp is not None:
                adjustFlow_stack(self.UPHsdot, self.FluidRhoCp, self.VolProcMed,
                                 self.PT, self.PTStartUp, self.DTUPHs, self.DTUPHs)
            adjustSumOfProdsC_stack(self.UPHcOfProcess, self.FluidCp_c,
                                   self.mInFlowYear, self.DTUPHcNet)
            adjustSumOfProds_stack(self.UPHcOfProcess, self.UPHcdot, 
                                  (self.NCyclesPerYear, ) * self.nInflowingStreams)
            adjustFlow_stack(self.UPHcdot, 
                             self.FluidRhoCp_c, 
                             self.VInFlowCycleEff, 
                             (self.PT,) * self.nInflowingStreams, 
                             self.PTInFlowRec, 
                             self.DTUPHcNet, 
                             self.DTUPHcNet)
            adjustDiff_stack(self.UPHcdot, self.UPHcdotGross, self.QHXdotProcIntIn)
            adjustFlow_stack(self.UPHcdotGross, 
                             self.FluidRhoCp_c, 
                             self.VInFlowCycleEff,
                             (self.PT, )* self.nInflowingStreams, 
                             self.PTInFlow, 
                             self.DTUPHcGross, 
                             self.DTUPHcGross)
            
            adjustProd_stack(self.UPHm, self.QOpProc, self.HPerYearProc)

            # FIXME: delete self.QLoss.push()
            adjustSum_stack(self.QOpProc, self.QLoss, self.QEvapProc)
#            adjustProd(self.QLoss1,self.UAProc,self.DTLoss)
            adjustDiff_stack(self.DTLoss, self.PT, self.TEnvProc)
            
            for i in range(self.nInflowingStreams):
                adjustProd_stack(self.VInFlowCycleEff[i], self.PartLoad, self.VInFlowCycle[i])
            for i in range(self.nOutflowingStreams):
                adjustProd_stack(self.VOutFlowCycleEff[i], self.PartLoad, self.VOutFlowCycle[i])

            adjustProd_stack(self.HPerDayOp, self.HBatch, self.NBatch)
            adjustProd_stack(self.HPerDayProc, self.PartLoad, self.HPerDayOp)
                        
            adjustProd_stack(self.HPerYearProc, self.NDaysProc, self.HPerDayProc)
            
            adjustProd_stack(self.VInFlowCycleEff,
                             (self.PartLoad,) * self.nInflowingStreams,
                             self.VInFlowCycle)
            adjustProd_stack(self.VOutFlowCycleEff,
                             (self.PartLoad,) * self.nOutflowingStreams,
                             self.VOutFlowCycle)

            adjustProd_stack(self.HPerDayOp, self.HBatch, self.NBatch)
            adjustProd_stack(self.HPerDayProc, self.PartLoad, self.HPerDayOp)
                        
            adjustProd_stack(self.HPerYearProc, self.NDaysProc, self.HPerDayProc)
            

            if DEBUG in ["ALL", "MAIN"]:
                self.showAllUPH()
           
# Step 4: Second cross check of the variables

                print "-------------------------------------------------"
                print "Step 4: cross checking"
                print "-------------------------------------------------"
                
            self.ccheckAll()
            
            if DEBUG in ["ALL", "MAIN"]:
                self.showAllUPH()

# Arrived at the end

        for i in range(self.nInflowingStreams):
            self.UPHcGrossProd[i] = calcProd("UPHcGrossProd_%s" % (i,), self.UPHcdotGross[i], self.NCyclesPerYear) # Not adjusted
        self.UPHcGross = calcRowSum("UPHcGross", self.UPHcGrossProd)
        self.QHXProcInt = [calcProd("QHXProcInt_%s" % (i,), self.QHXdotProcIntIn[i], self.NCyclesPerYear)
                           for i in xrange(self.nInflowingStreams)] # Not adjusted 

    #adido este ultimo show all. sino no se ven los ultimos dos resultados ...
        if DEBUG in ["ALL", "BASIC"]:
            self.showAllUPH()

        cycle.checkTotalBalance()
        # check/create basic consistency assumptions
        for i in xrange(self.nInflowingStreams):
            if self.inflowingStreams[i].HeatRecExist == False:
                # no HR means the temperatures have to be equal
                self.PTInFlowRec[i].update(self.PTInFlow[i]) 
 
#------------------------------------------------------------------------------
    def ccheckAll(self):    
#------------------------------------------------------------------------------
#   check block
#------------------------------------------------------------------------------

        for i in range(self.nInflowingStreams):
            self.mInFlowYear[i].check()
            self.mInFlowNom[i].check()

###also sum should be checked !!!
            
        for i in range(self.nOutflowingStreams):
            self.mOutFlowYear[i].check()
            self.mOutFlowNom[i].check()

###also sum should be checked !!!
        
        self.PT.check()
        for i in range(self.nInflowingStreams):
            self.PTInFlow[i].check()
            self.PTInFlowRec[i].check()
        self.PTStartUp.check()
        
        self.VolProcMed.check()
        for i in range(self.nInflowingStreams):
            self.VInFlowCycle[i].check()
        for i in range(self.nOutflowingStreams):
            self.VOutFlowCycle[i].check()
        self.PartLoad.check()
        ccheck1(self.NBatch, self.NBatch1)
                          
        for i in range(self.nInflowingStreams):
            self.VInFlowCycleEff[i].check()
        for i in range(self.nOutflowingStreams):
            self.VOutFlowCycleEff[i].check()
            self.PTOutFlow[i].check()
            self.PTOutFlowRec[i].check()
        # only if single in-flowing and single out-flowing stream
        if self.nInflowingStreams == self.nOutflowingStreams == 1:
            self.DTCrossHXLT.check()
            self.DTCrossHXHT.check()

        for i in range(self.nInflowingStreams):
            self.DTUPHcNet[i].check()
        
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
        for item in (self.UPHcdotGross,
                     self.UPHcdot,
                     self.QHXdotProcIntIn, 
                     self.UPHc):
            for streamdata in item:
                streamdata.check() 
        self.UPHcOfProcess.check()
        self.UPHsdot.check()
        self.NDaysProc.check()
        self.NCyclesPerYear.check()
        self.UPHs.check()
        self.UPHProc.check()
        self.QHXProc.check()
        self.UPH.check()
        self.UAProc.check()

        for item in (self.UPHw_dot, 
                     self.DTOutFlow, 
                     self.PTFinal, 
                     self.HOutFlow, 
                     self.HOutFlowRec, 
                     self.HFinal,
                     self.dHOutFlow, 
                     self.dHFinal, 
                     self.XOutFlow,
                     self.XOutFlowRec, 
                     self.XFinal, 
                     self.QHXdotProcIntOut,
                     self.UPHw):
            for streamdata in item:
                streamdata.check() 
            
             
###CHECK: for obtaining real equality AFTER checking it would be better first check both, then push one to the stack of the other, then check again,
### and then do a direct assignment
        self.QHXdotProcInt.check()
        self.UPHwOfProcess.check()
        self.UPHwOfProcess.push(self.QWHProc) #At the moment they are the same. Change it next future when vessel heat recovery will be implemented
        self.QWHProc.push(self.UPHwOfProcess)
        self.UPHwOfProcess.check()
        self.QWHProc.check()
            
    def estimate(self):  
        """
        Estimate some of the data that are not sufficiently precise.
        This should be a subset of the data that are within screen.
        (not necessarily ALL data have to be estimated)
        """
        if (all(self.QHXdotProcIntOut[i].val is None for i in xrange(self.nOutflowingStreams))
               or not any(self.internalHR)):
            for i in range(self.nOutflowingStreams):
                self.PTOutFlowRec[i].setEstimate(self.PT.val, limits=(self.PT.valMin, self.PT.valMax))
            
        if self.nInflowingStreams == self.nOutflowingStreams == 1:
            self.VOutFlowCycle[0].setEstimate(self.VInFlowCycle[0].val, limits=(self.VInFlowCycle[0].valMin, self.VInFlowCycle[0].valMax))
            for i in range(self.nInflowingStreams):
                self.PTInFlow[i].setEstimate(15.0, limits=(5.0, 35.0))

#        if self.internalHR == True:
        if self.nInflowingStreams == self.nOutflowingStreams == 1:
            for i in range(self.nInflowingStreams):
                if (self.PT.val - self.PTInFlow[i].val > 5.0):
        
                    self.DTCrossHXHT.setEstimate(10.0, limits=(5.0, 999.0))
                    self.DTCrossHXLT.setEstimate(10.0, limits=(5.0, 999.0))
        
                else:
                    self.PTInFlowRec[i].update(self.PTInFlow[i])
                    self.internalHR[i] = False
        
        
                if self.NBatch.val > 0 and (self.NBatch.val is not None):
                    vol1 = self.VInFlowCycle[0].val / self.NBatch.val
                else:
                    vol1 = 0.0
            
        if self.VolProcMed.val is not None:
            vol2 = self.VolProcMed.val
        else:
            vol2 = 0.0
            
        vol = max(vol1, vol2)

        if vol < INFINITE:
        
            surface = 10.0 * pow(vol, 2.0 / 3)
            UAmin = 0.0004 * surface * 0.1  #0.4 W/m2K well insulated vessel
            UA = 0.008 * surface
            UAmax = 0.002 * surface * 1.0   #2.0 W/m2K badly insulated equipment
            
            self.UAProc.setEstimate(UA, limits=(UAmin, UAmax))

            # estimate of Evaporation losses

        QLossMax = UAmax * self.DTLoss.valMax
        
        if self.QOpProc.valMax <= QLossMax:    # maintenance can be fully explained by
                                                # thermal losses
            self.QEvapProc.setEstimate(0.0, limits=(0.0, 0.0))
            
# WARNING: this apriori assumption can give problems in cases with evaporation !!!!

        
# limits: optional and fix absolute minimum and maximum values
# sqerr: optional input that fixes the (stochastic) relative square error

#==============================================================================
if __name__ == "__main__":
    import einstein.GUI.pSQL as pSQL, MySQLdb
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
    ccProc.exportData()

    ccProc.screen()
    screen.show()
    
#==============================================================================
