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
#	ModuleCH
#			
#------------------------------------------------------------------------------
#			
#	Module for calculation of chillers
#
#==============================================================================
#
#   EINSTEIN Version No.: 2.0
#   Created by:      Jan Ries                 September 2010
#
#   Since Version 2.0 revised by:
#                        
#------------------------------------------------------------------------------		
#	(C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008, 2009
#	www.energyxperts.net / info@energyxperts.net
#
#	This program is free software: you can redistribute it or modify it under
#	the terms of the GNU general public license v3 as published by the Free
#	Software Foundation (www.gnu.org).
#
#============================================================================== 
"""
This Module only contains the class ModuleCH for preparation and calculation of
data for the design assistant window for chillers.
"""
import numpy as np
import copy

from einstein.modules.constants import *
from einstein.auxiliary.auxiliary import *
from einstein.GUI.status import Status
from einstein.modules.messageLogger import *
from einstein.GUI.dialogGauge import DialogGauge

class ModuleCH(object):

    def __init__(self, keys):
        self.keys = keys
        # up to which cascade level do we know of chillers 
        self.cascadeIndex = 0

    def initPanel(self):
        logTrack("ModuleChiller (initPanel)")

    def updatePanel(self):
        """
        Carry out any calculations necessary previous to displaying the CH
        design assistant window
        """
        # get list of chillers in the system
        # and update the energetic calculation up to the level needed for representation
        (CHList, CHTableDataList) = self.screenEquipments()

        if Status.int.cascadeUpdateLevel < self.cascadeIndex:
            Status.mod.moduleEnergy.runSimulation(self.cascadeIndex)

        # 1. List of equipments
        matrix = []
        for row in CHTableDataList:
            matrix.append(row)
        data = np.array(matrix)
        assert(np.all(data == np.array(CHTableDataList)))

        Status.int.setGraphicsData('CH Table', data)

        # 2. Preparing data
        PowerSumTmax = 0
        
        for i in CHList:
            PowerSumTmax += i["equipePnom"] 

        if len(CHList) == 0:
            # assures that index >= 0
            # even if there's NO equipment at all
            index = max(len(Status.prj.getEquipments()) + 1, 1)    
        else:
            chs = Status.DB.qgenerationhc.QGenerationHC_ID[CHList[0]["equipeID"]]
            if len(chs) > 0:
                ch = chs[0]
                index = ch.CascadeIndex

        QD80C = copy.deepcopy(Status.int.QD_Tt_mod[index - 1][int(80 / Status.TemperatureInterval + 0.5)])
        QD80C.sort(reverse=True)

        QD140C = copy.deepcopy(Status.int.QD_Tt_mod[index - 1][int(140 / Status.TemperatureInterval)])
        QD140C.sort(reverse=True)

        # 2. XY Plot
        TimeIntervals = [(Status.TimeStep * (it + 1) * Status.EXTRAPOLATE_TO_YEAR) 
                         for it in xrange(Status.Nt + 1)]
        try:

            Status.int.setGraphicsData('CH Plot', [TimeIntervals,
                                                            QD80C])
        except:
            logDebug("ModuleCH (updatePanel): problems sending data for CH Plot")

        # 3. Configuration design assistant
#        config = self.getUserDefinedPars()
        config = [1, 10, 0, "Natural Gas", 100, 500, 80]
        Status.int.setGraphicsData('CH Config', config)
        
        # 4. additional information (Info field right side of panel)
        info = []
        info.append(max(0, QD80C[0]))
        info.append(max(0, (QD140C[0] - QD80C[0])))

        Status.int.setGraphicsData('CH Info', info)

    def screenEquipments(self, setIndex=True):
        """Return already existing chillers in the industry and their data."""
        equipments = Status.prj.getEquipments()
        Status.int.getEquipmentCascade()
        NEquipe = len(equipments)
        CHList = []
        maxIndex = NEquipe
        index = 0
        for row in Status.int.cascade:
            index += 1
            if getEquipmentClass(row["equipeType"]) == "CH":
                CHList.append(row)
                maxIndex = index
        
        if setIndex == True:
            self.cascadeIndex = maxIndex

        CHTableDataList = []
        for row in Status.int.EquipTableDataList:
            if getEquipmentClass(row[3]) == "CH":
                CHTableDataList.append(row)

        #screen list and substitute None with "not available"
        for i in range(len(CHTableDataList)):
            for j in range(len(CHTableDataList[i])):
                if CHTableDataList[i][j] == None:
                    CHTableDataList[i][j] = "not available"        
        return (CHList, CHTableDataList)
        
    def calculateEnergyFlows(self, equipe, cascadeIndex):
        """
        Update the cascade by calculating of energy flows in the chillers.
        @param equipe: The equipment to calculate
        @param cascadeIndex: The cascade index of the equipment
        """
        Status.int.extendCascadeArrays(cascadeIndex)

        PNom = equipe.HCGPnom
        if PNom is None:
            logTrack("ModuleChiller (cEF-dummy): no equipment capacity specified")
            PNom = 0

        COPc_nom = equipe.HCGTEfficiency
        if COPc_nom is None:
            logTrack("ModuleChiller (cEF-dummy): no equipment COP specified")
            COPc_nom = 3.0
        
        NT = Status.NT
        DT = Status.TemperatureInterval
        Nt = Status.Nt
        Dt = Status.TimeStep
        
        # get demand data for CascadeIndex/EquipmentNo from Interfaces
        # and create arrays for storing heat flow in equipment
        QD_Tt = copy.deepcopy(Status.int.QD_Tt_mod[cascadeIndex - 1])
        QDc_Tt = copy.deepcopy(Status.int.QDc_Tt_mod[cascadeIndex - 1])
        QA_Tt = copy.deepcopy(Status.int.QA_Tt_mod[cascadeIndex - 1])
        
        USCj_Tt = Status.int.createQ_Tt()
        USCj_t = Status.int.createQ_t()
        USCj_T = Status.int.createQ_T()

        QWHj_Tt = Status.int.createQ_Tt()
        QWHj_t = Status.int.createQ_t()
        QWHj_T = Status.int.createQ_T()

        # start simulation
        USHj = 0
        QWHj = 0

        HPerYear = 0

        # outer iterative cycle: over all time steps
        for it in xrange(Nt):   
            # inner iterative cycle: temperature intervals
            for iT in xrange(NT + 2):   #+1 = the > 100 �C case
                USCj_Tt[iT][it] = min(QDc_Tt[iT][it], PNom * Dt) #just max(demand,nom.power) 
                QWHj_Tt[iT][it] = 0
            
            if USCj_Tt[NT + 1][it] > 0:
                HPerYear += Dt
        
        USHj += sum(USCj_Tt[NT + 1])
        QWHj += sum(QWHj_Tt[NT + 1])
        # end simulation. 

        # storing results in Interfaces
        # remaining heat/cooling demand and availability for next equipment in cascade
        Status.int.QD_Tt_mod[cascadeIndex] = QD_Tt
        Status.int.QD_T_mod[cascadeIndex] = Status.int.calcQ_T(QD_Tt)
        Status.int.QDc_Tt_mod[cascadeIndex] = QDc_Tt
        Status.int.QDc_T_mod[cascadeIndex] = Status.int.calcQ_T(QDc_Tt)
        Status.int.QA_Tt_mod[cascadeIndex] = QA_Tt
        Status.int.QA_T_mod[cascadeIndex] = Status.int.calcQ_T(QA_Tt)

        # cooling delivered by present equipment                            
        Status.int.USHj_Tt[cascadeIndex - 1] = USCj_Tt
        Status.int.USHj_T[cascadeIndex - 1] = Status.int.calcQ_T(USCj_Tt)
        Status.int.USHj_t[cascadeIndex - 1] = copy.deepcopy(USCj_Tt[Status.NT + 1])

        # waste heat produced by present equipment
        Status.int.QWHj_Tt[cascadeIndex - 1] = QWHj_Tt
        Status.int.QWHj_T[cascadeIndex - 1] = Status.int.calcQ_T(QWHj_Tt)
        Status.int.QWHj_t[cascadeIndex - 1] = copy.deepcopy(QWHj_Tt[Status.NT + 1])

        Status.int.cascadeUpdateLevel = cascadeIndex

        # Global results (annual energy flows)
        Status.int.USHj[cascadeIndex - 1] = USHj * Status.EXTRAPOLATE_TO_YEAR
        Status.int.QWHj[cascadeIndex - 1] = QWHj * Status.EXTRAPOLATE_TO_YEAR
        # no change for heat exchangers
        Status.int.QHXj[cascadeIndex - 1] = Status.int.QHXj[cascadeIndex - 2] 

        if COPc_nom > 0:
            FETFuel_j = USHj / COPc_nom
        else:
            FETFuel_j = 0.0
            showWarning("Strange chiller with COP = 0.0")
        FETel_j = 0.0
        
        Status.int.FETFuel_j[cascadeIndex - 1] = FETFuel_j
        Status.int.FETel_j[cascadeIndex - 1] = 0.0
        Status.int.HPerYearEq[cascadeIndex - 1] = HPerYear * Status.EXTRAPOLATE_TO_YEAR

        logMessage("Dummy: eq.no.:%s USH: %s FETFuel: %s FETel: %s HPerYear: %s [MWh]" % \
                   (equipe.EqNo, \
                    USHj * Status.EXTRAPOLATE_TO_YEAR / 1000.0, \
                    0.0, \
                    FETel_j * Status.EXTRAPOLATE_TO_YEAR / 1000.0, \
                    HPerYear * Status.EXTRAPOLATE_TO_YEAR / 1000.0))

        self.calculateOM(equipe, USHj * Status.EXTRAPOLATE_TO_YEAR)
        
    def calculateOM(self, equipe, USH):
        OMFix = equipe.OandMfix
        OMVar = equipe.OandMvar
        try:
            OM = OMFix + OMVar * USH
        except:
            logWarning(_("OM costs for equipment %s could not be calculated") % equipe.Equipment)
            OM = 0.0
        equipe.OandM = OM
        Status.SQL.commit()
        
    def getEquipmentTotals(self):
        # estimate equipment waste heat from annual QWHj and equipment schedules
        Status.int.QWHEqTotal_Tt = Status.int.createQ_Tt()
        equipments = Status.prj.getEquipments()
        for equipe in equipments:
            j = equipe.EqNo - 1
            for iT in range(Status.NT + 2):
                for it in range(Status.Nt):
                    Status.int.QWHEqTotal_Tt[iT][it] += Status.int.QWHj_Tt[j][iT][it]

        Status.int.QWHEqTotal_t = copy.deepcopy(Status.int.QWHEqTotal_Tt[0])
        Status.int.QWHEqTotal_T = Status.int.calcQ_T(Status.int.QWHEqTotal_Tt)
        Status.int.QWHEqTotal = Status.int.QWHEqTotal_T[0]        
