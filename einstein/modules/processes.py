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
#    PROCESSES
#            
#------------------------------------------------------------------------------
#            
#    Functions for calculation and temperature decomposition of
#       process heat demands
#
#==============================================================================
#
#    Version No.: 0.01
#    Created by:         Hans Schweiger    07/05/2008
#    Revised by:         ---
#
#       Changes in last update:
#    
#------------------------------------------------------------------------------        
#    (C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008
#    www.energyxperts.net / info@energyxperts.net
#
#    This program is free software: you can redistribute it or modify it under
#    the terms of the GNU general public license as published by the Free
#    Software Foundation (www.gnu.org).
#
#==============================================================================

import numpy as np
from einstein.auxiliary.auxiliary import *
from einstein.modules.constants import *
from einstein.GUI.status import Status
from einstein.modules.messageLogger import *
from einstein.modules.fluids import *
from einstein.GUI.dialogGauge import DialogGauge
import copy


def originalProcessId(processId):
    """Get process id of process in original state"""
    questionnaireId = Status.DB.qprocessdata.QProcessData_ID[processId].Questionnaire_id.column()[0]
    procNo = Status.DB.qprocessdata.QProcessData_ID[processId].ProcNo.column()[0]
    return Status.DB.qprocessdata.Questionnaire_id[questionnaireId].ProcNo[procNo].AlternativeProposalNo[-1].QProcessData_ID.column()[0]


class Processes(object):
    """Module that handles all project schedules"""
    def __init__(self):
        self.outOfDate = True
        self.outOfDateYearly = True
       
    def createYearlyDemand(self):
        """
        Is created automatically in an alternative after cchecking or
        after selecting a new alternative that is already cchecked.
        
        """
        logTrack("Processes (createYearlyDemand): starting")
        (projectData, generalData) = Status.prj.getProjectData()
        processes = Status.prj.getProcesses()

        UPH_T = []
        UPHs_T = []
        UPHm_T = []
        UPHc_T = []
        UPHw_T = []
        UPHTotal_T = Status.int.createQ_T()
        UPHwTotal_T = Status.int.createQ_T()
        UPCTotal_T = Status.int.createQ_T()
        UPCwTotal_T = Status.int.createQ_T()
        NT = Status.NT
        
        for process in processes:
            (inStreams, outStreams) = Status.prj.getStreams(process.QProcessData_ID) 
            
            UPH_T.append(Status.int.createQ_T())
            UPHc_T.append(Status.int.createQ_T())
            UPHc_per_stream_T = np.zeros((len(inStreams), NT + 2), "f")
            UPHm_T.append(Status.int.createQ_T())
            UPHs_T.append(Status.int.createQ_T())
            UPHw_T.append(Status.int.createQ_T())
            UPHw_per_stream_T = np.zeros((len(outStreams), NT + 2), "f")
            k = process.ProcNo - 1

            UPHc = checkLimits(process.UPHc, 0.0, INFINITE, 0.0)
            if inStreams == []: # no inStreams
                UPHc_per_stream = np.zeros((1, 1), "f")
                distInStreams = np.zeros((1, NT + 2), "f")
            else:
                UPHc_per_stream = np.array([checkLimits(stream.UPHc, 0.0, INFINITE, 0.0) 
                                        for stream in inStreams])
                distInStreams = np.array([self._createTempDist(stream.PTInFlow, T0=stream.PTInFlowRec,
                                                              mode=process.heating_cooling)
                                                              for stream in inStreams])
            UPHm = checkLimits(process.UPHm, 0.0, INFINITE, 0.0)
            distUPHm = self._createTempDist(process.PT, mode=process.heating_cooling)

            UPHs = checkLimits(process.UPHs, 0.0, INFINITE, 0.0)
            distUPHs = self._createTempDist(process.PT, T0=process.PTStartUp,
                                           mode=process.heating_cooling)

            UPHw = checkLimits(process.UPHw, 0.0, INFINITE, 0.0) 
            UPHw_per_stream = np.array([checkLimits(stream.UPHw, 0.0, INFINITE, 0.0) 
                                        for stream in outStreams])
            distOutStreams = [] 
            for index in xrange(len(outStreams)):
                if UPHw_per_stream[index] <= 0:
                    distOutStreams.append(Status.int.createQ_T())
                else:
                    stream = outStreams[index]
                    distOutStreams.append(self.createInvTempDistLat(stream.PTOutFlow,
                                                                    stream.HOutFlow,
                                                                    stream.dbfluid_id,
                                                                    T0=stream.PTFinal,
                                                                    mode=process.heating_cooling))
                        
            distOutStreams = np.array(distOutStreams)
            if np.all(distOutStreams == []): # no outStreams
                UPHw_per_stream = np.zeros((1, 1), "f")
                distOutStreams = np.zeros((1, Status.NT + 2), "f")
         
            UPHc_per_stream_T = (UPHc_per_stream * distInStreams.transpose()).transpose()
            UPHw_per_stream_T = (UPHw_per_stream * distOutStreams.transpose()).transpose()
            UPHc_T[k] = UPHc_per_stream_T.sum(0).tolist()
            UPHw_T[k] = UPHw_per_stream_T.sum(0).tolist()
            UPHs_T[k] = (UPHs * distUPHs).tolist()
            UPHm_T[k] = (UPHm * distUPHm).tolist()
            # actually: UPH_T[k] = UPHc_T[k] + UPHm_T[k] + UPHs_T[k] but no arrays :-(
            UPH_T[k] = (UPHc_per_stream_T.sum(0) + (UPHm * distUPHm) 
                        + (UPHs * distUPHs)).tolist()
            if process.heating_cooling == "heating":
                UPXTotal_T = UPHTotal_T
                UPXwTotal_T = UPHwTotal_T
            else:
                UPXTotal_T = UPCTotal_T
                UPXwTotal_T = UPCwTotal_T
            for iT in xrange(NT + 2): #NT + 2 -> additional value for T > Tmax
                UPXTotal_T[iT] += UPH_T[k][iT]
                UPXwTotal_T[iT] += UPHw_T[k][iT]
        Status.int.UPH_T = UPH_T   
        Status.int.UPHc_T = UPHc_T   
        Status.int.UPHm_T = UPHm_T   
        Status.int.UPHs_T = UPHs_T   
        Status.int.UPHw_T = UPHw_T
        Status.int.UPHTotal_T = UPHTotal_T
        Status.int.UPHwTotal_T = UPHwTotal_T
        Status.int.UPCTotal_T = UPCTotal_T
        Status.int.UPCwTotal_T = UPCwTotal_T
        logTrack("Processes (createYearlyDemand): yearly heat demand = %s yearly waste heat availability = %s" % \
              (Status.int.UPHTotal_T[NT + 1], Status.int.UPHwTotal_T[0]))

        self.outOfDateYearly = False

    def createAggregateDemand(self):
        logTrack("Processes (createAggregateDemand): Creating time and temperature dependent heat demand")
        dlg = DialogGauge(Status.main, _("Time dependent aggregate heat demand"), _("generate demand profile"))
        
        (projectData, generalData) = Status.prj.getProjectData()
        Status.HPerDayInd = projectData.HPerDayInd

        if Status.processData.outOfDate == False:
            logTrack("Processes (createAggregateDemand): WARNING - someone wants to create demand profile which is already up to date")

        if Status.processData.outOfDateYearly == True:
            logTrack("Processes (createAggregateDemand): creating yearly demand UPHk(T)")
            self.createYearlyDemand()

        if Status.schedules.outOfDate == True:
            logTrack("Processes (createAggregateDemand): creating process schedules")
            Status.schedules.create()

        processes = Status.prj.getProcesses()

        UPH_Tt = []
        UPHw_Tt = []

        UPHTotal_Tt = Status.int.createQ_Tt()
        UPHwTotal_Tt = Status.int.createQ_Tt()
        UPCTotal_Tt = Status.int.createQ_Tt()
        UPCwTotal_Tt = Status.int.createQ_Tt()

        NK = len (processes)
        i = 0

        for process in processes:
            k = process.ProcNo - 1

            UPH_Tt.append(Status.int.createQ_Tt())
            UPHw_Tt.append(Status.int.createQ_Tt())
            
            scheduleC = Status.schedules.procInFlowSchedules[k]
            scheduleM = Status.schedules.procOpSchedules[k]
            scheduleS = Status.schedules.procStartUpSchedules[k]
            scheduleW = Status.schedules.procOutFlowSchedules[k]
            
            NT = Status.NT
            Nt = Status.Nt

            if process.heating_cooling == "heating":
                UPXTotal_Tt = UPHTotal_Tt
                UPXwTotal_Tt = UPHwTotal_Tt
            else:
                UPXTotal_Tt = UPCTotal_Tt
                UPXwTotal_Tt = UPCwTotal_Tt
            for it in xrange(Nt):
                fC = scheduleC.fav[it]
                fM = scheduleM.fav[it]
                fS = scheduleS.fav[it]
                fW = scheduleW.fav[it]

                for iT in range(NT+2): #NT + 1 + 1 -> additional value for T > Tmax
                    UPH_Tt[k][iT][it] = Status.int.UPHc_T[k][iT]*fC +\
                                        Status.int.UPHm_T[k][iT]*fM +\
                                        Status.int.UPHs_T[k][iT]*fS
                    UPHw_Tt[k][iT][it] = Status.int.UPHw_T[k][iT]*fW

                    UPXTotal_Tt[iT][it] += UPH_Tt[k][iT][it]
                    UPXwTotal_Tt[iT][it] += UPHw_Tt[k][iT][it]

            self.createHeatFlow_tDict(process.UPHm, scheduleM.favTemp, Status.int.UPH_m_t, process.QProcessData_ID)
            self.createHeatFlow_tDict(process.UPHs, scheduleS.favTemp, Status.int.UPH_s_t, process.QProcessData_ID)
            self.createHeatFlow_tDict(process.UPHc, scheduleC.favTemp, Status.int.UPH_c_t, process.QProcessData_ID)
            self.createHeatFlow_tDict(process.UPHw, scheduleW.favTemp, Status.int.UPH_w_t, process.QProcessData_ID)

            i += 1
            dlg.update(90.0*i/NK)

            print "process.UPHs: "  + str(process.UPHs) + "process.id: " + str(process.QProcessData_ID)
            print "scheduleS.fav: " + str(scheduleS.fav)

        Status.int.UPH_Tt = UPH_Tt    
        Status.int.UPHw_Tt = UPHw_Tt

        Status.int.UPHTotal_Tt = UPHTotal_Tt    
        Status.int.UPHwTotal_Tt = UPHwTotal_Tt
        Status.int.UPCTotal_Tt = UPCTotal_Tt
        Status.int.UPCwTotal_Tt = UPCwTotal_Tt
        
                           
        # set status-flag (required BEFORE call to runHRModule !!!)
        Status.int.cascadeUpdateLevel = 0 #indicates that demand profile is created !!!
        Status.processData.outOfDate = False
        
        #   estimate equipment waste heat from annual QWHj and equipment schedules
        equipments = Status.prj.getEquipments()

        Status.int.QWHEqTotal_Tt = Status.int.createQ_Tt()
        Status.int.QWHEqTotal_T = Status.int.createQ_T()
        Status.int.QWHEqTotal_t = Status.int.createQ_t()
        Status.int.QWHEqTotal = 0
        
        NT = Status.NT
        Nt = Status.Nt
        for equipe in equipments:
            j = equipe.EqNo - 1
            schedule = Status.schedules.equipmentSchedules[j]
            # temperature distribution of waste heat. assumed as fix
            TExhaustGas = equipe.TExhaustGas
            if TExhaustGas == None:
                logDebug("Processes: Equipment exhaust gas temperature not specified. 200 Â°C assumed")
                TExhaustGas = 200
            if equipe.DBFuel_id is None:
                TMinOffGas = 0
                dTtot = 1.e-10
            else:
                fuel = Fuel(equipe.DBFuel_id)
                TMinOffGas = max(fuel.TCondOffGas(), 0)
                dTtot = max(TExhaustGas - TMinOffGas, 1.e-10)
            
            QWHj = equipe.QWHEq
            if QWHj is None:
                QWHj = 0.0
            Status.int.QWHEqTotal += QWHj

            QWHj_T = Status.int.createQ_T()
            for iT in range(Status.NT + 2):
                temp = Status.int.T[iT]
                dT = max(temp - TMinOffGas, 0.)
                QWHj_T[iT] = QWHj * max(0.0, 1.0 - dT / dTtot)
                Status.int.QWHEqTotal_T[iT] += QWHj_T[iT]
                

            QWHj_Tt = Status.int.createQ_Tt()
            for it in range(Nt):
                time = Status.TimeStep * it
                f = schedule.fav[it]
                for iT in range(NT + 2): #NT + 2 -> additional value for T > Tmax
                    QWHj_Tt[iT][it] = QWHj_T[iT] * f

                    Status.int.QWHEqTotal_Tt[iT][it] += QWHj_Tt[iT][it]
            self.createHeatFlow_t(equipe.QWHEq, schedule.fav, Status.int.QWHEq_t)
#            self.createHeatFlow_tDict(equipe.QWHEq, schedule.favTemp, Status.int.QWHEq_t, equipe.QGenerationHC_ID)
        Status.int.QWHEqTotal_t = copy.deepcopy(Status.int.QWHEqTotal_Tt[0])
        
        #   get waste heat from WHEEs
        whees = Status.prj.getWHEEs()

        Status.int.QWHEE_Tt = Status.int.createQ_Tt()
        Status.int.QWHEE_T = Status.int.createQ_T()
        Status.int.QWHEE_t = Status.int.createQ_t()
        Status.int.QWHEE = 0

        for whee in whees:
            n = whee.WHEENo - 1
            schedule = Status.schedules.WHEESchedules[n]
           
            # temperature distribution of waste heat. assumed as fix
            Tout = whee.WHEETOutlet
            if Tout == None:
                logWarning("Processes: WHEE outlet temperature not specified. 70 Â°C assumed")
                Tout = 70
            Tret = max(Tout - 20, 0.0) # by default Delta_T = 20 assumed
            dTtot = max(Tout - Tret, 1.e-10)

            if whee.HPerDayWHEE is None or whee.NDaysWHEE is None or whee.QWHEE is None:
                QWHEE = 0.0
            else:
                QWHEE = whee.QWHEE * whee.HPerDayWHEE * whee.NDaysWHEE
                
            Status.int.QWHEE += QWHEE

            QWHEE_T = Status.int.createQ_T()
            for iT in range(Status.NT + 2):
                temp = Status.int.T[iT]
                dT = max(temp - Tret, 0.)
                QWHEE_T[iT] = QWHEE * max(0.0, 1.0 - dT / dTtot)
                Status.int.QWHEE_T[iT] += QWHj_T[iT]
                

            QWHEE_Tt = Status.int.createQ_Tt()
            for it in range(Nt):
                time = Status.TimeStep * it
                f = schedule.fav[it]
                for iT in range(NT + 2): #NT + 1 + 1 -> additional value for T > Tmax
                    QWHEE_Tt[iT][it] = QWHEE_T[iT] * f

                    Status.int.QWHEE_Tt[iT][it] += QWHEE_Tt[iT][it]
            print "QWHEE:", whee.QWHEE
            self.createHeatFlow_t(whee.QWHEE, schedule.fav, Status.int.QWHEEEq_t)
        Status.int.QWHEE_t = copy.deepcopy(Status.int.QWHEE_Tt[0])

        #   now run HR module for calculating heat recovery and effective demand at pipe entry
#        Status.mod.moduleHR.runHRModule()

        logTrack("Aggregate demand = %s" % str(Status.int.QD_T))
        dlg.Destroy()

#------------------------------------------------------------------------------

    def createHeatFlow_t(self, HeatFlow, schedule, HeatFlow_t):
        """
        HeatFlow can be UPHm, UPHs, QWHEE, QWH
        """

        list = []
        for elem in schedule:
#            try:
            list.append(elem*HeatFlow)
#            except: list.append(-1)
        HeatFlow_t.append(list)

    def createHeatFlow_tDict(self, HeatFlow, schedule, HeatFlow_t, ProcessID):
        """
        HeatFlow can be UPHm, UPHs, QWHEE, QWH
        """
        hours_nominal=0.1
        for elem in schedule:
            hours_nominal += elem
            
        list = []
        sum=0
        for elem in schedule:
#            try:
            list.append(elem*HeatFlow/(hours_nominal))
            sum +=(elem*HeatFlow/(hours_nominal))
#            except: list.append(-1)
        HeatFlow_t[ProcessID] = list
#        HeatFlow_t.append(list)

#------------------------------------------------------------------------------		
    def changeInProcess(self):
#------------------------------------------------------------------------------		
#       function that is called from anywhere in the tool, whenever process data
#       of the present alternative are changed
#------------------------------------------------------------------------------		
        self.outOfDate = True
        self.outOfDateYearly = True
        Status.schedules.outOfDate = True
        Status.int.changeInCascade(0)
        logTrack("Processes (changeInProcess): process data changed")
        
    def _createTempDist(self, PT, T0=None, mode="heating"):
        """
        Create a default temperature distribution for a given temperature PT. 
        
        Create a linear ASCENDING temperature distribution between T0 and T,
        or a step distribution, if T0 = None for heating processes and the
        equivalent DESCENDING temperature distribution for cooling processes.
        
        :param PT: Target temperature 
        :param T0: starting temperature
        :param mode: either "heating" or "cooling"
        :returns: a temperature distribution numpy array with elements as
        formatted in modules.interfaces.Interfaces.T and TC
        
        """
        NT = Status.NT
        dist = []
        if mode == "heating":
            T = Status.int.T
            if T0 == None or T0 >= PT:
                for iT in range(NT + 1):
                    if PT > T[iT]:
                        dist.append(0.0)
                    else:
                        dist.append(1.0)
                dist.append(1.0)    #last entry for T > Tmax
            else:
                for iT in range(NT + 1):
                    dist.append(cutInterval(T[iT], T0, PT))
                dist.append(1.0)    #last entry for T > Tmax
        elif mode == "cooling":
            T = Status.int.TC
            if T0 == None or T0 >= PT:
                for iT in range(NT + 1):
                    if PT > T[iT]:
                        dist.append(1.0)
                    else:
                        dist.append(0.0)
                dist.append(0.0)    #last entry for T > Tmax
            else:
                for iT in range(NT + 1):
                    dist.append(1 - cutInterval(T[iT], T0, PT))
                dist.append(0.0)    #last entry for T > Tmax
        else:
            raise ValueError("Either heating or cooling, please.")
        return np.array(dist)

    def createInvTempDistLat(self, PT, h, fluidID, T0=None, mode="heating"):
        """
        Create a piecewise linear DESCINGING temperature distribution between PT 
        and T0. If the condensation point of the fluid is between T0 and PT
        the distribution makes the sensible jump.
        An equivalent distribution with ASCENDING temperature is created if it is
        not heat that is lost, but the medium is cooled for the process, 'cold 
        loss' so to speak.
           
        @param PT: starting temperature
        @param h: specific enthalpy
        @param fluidID: the id of the used medium
        @param T0: the final temperature after heat/cold loss 
        @param recovering: whether "heating" or "cooling" is lost.
        
        """
        fluid = Fluid(fluidID)
        x = fluid.steamFraction(h, T=PT)
        x0 = fluid.steamFraction(None, T=T0)

        if x is None:
            x = 0

        if x0 is None:
            x0 = x

        if x > x0:
            fX = (x - x0) * fluid.hL
        else:
            fX = 0

        if PT > fluid.TCond:
            fV = fluid.cpV * (PT - fluid.TCond)
        else:
            fV = 0

        if x0 > 0:
            fL = 0
        else:
            if T0 is None:
                fL = 0
            else:
                fL = (min(PT, fluid.TCond) - T0) * fluid.cp

        f = fL + fX + fV
        if f <= 0 or f is None:
            f = 1.0
            fL = 1.0
            logDebug("Processes (createInvTempDistLat): f=0 error with PT %s T0 %s h %s x %s x0 %s" % \
                     (PT, T0, h, x, x0))

        distV = self._createTempDist(PT, T0=fluid.TCond)
        distX = self._createTempDist(fluid.TCond, T0=None)
        distL = self._createTempDist(min(PT, fluid.TCond), T0=T0)
        if mode=="heating":
            dist = (1.0 - (fV * distV + fX * distX + fL * distL) / f).tolist()
        else:
            dist = ((fV * distV + fX * distX + fL * distL) / f).tolist()
        return dist

