#==============================================================================
#
#	E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (www.iee-einstein.org)
#
#------------------------------------------------------------------------------
#
#	ModuleEM2- Heat supply - Monthly data
#			
#==============================================================================
#
#	Version No.: 0.05
#	Created by: 	    Tom Sobota	28/03/2008
#                       Stoyan Danov    04/07/2008
#                       Stoyan Danov    07/07/2008
#                       Stoyan Danov    09/07/2008
#                       Hans Schweiger  15/01/2010
#
#       Changes to previous version:
#       04/07/08:   SD changes
#       07/07/08:   SD data1 added for plot
#       09/07/08:   SD calculation of monthly from hourly data
#       15/01/10:   HS  introduction of function update (+ call to this function
#                       in initModule
#	
#------------------------------------------------------------------------------		
#	(C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008
#	www.energyxperts.net / info@energyxperts.net
#
#	This program is free software: you can redistribute it or modify it under
#	the terms of the GNU general public license as published by the Free
#	Software Foundation (www.gnu.org).
#
#============================================================================== 

from sys import *
from math import *
from numpy import *
import wx

from einstein.modules.constants import *
from einstein.GUI.status import Status
from einstein.auxiliary.auxiliary import *
from einstein.GUI.status import *
from einstein.modules.interfaces import *
import einstein.modules.matPanel as mP
import copy

def _U(text):
    return unicode(_(text),"utf-8")

class ModuleEM2(object):

    def __init__(self, keys, showHeating):
        self.keys = keys
        self._showHeating = showHeating
        self.interface = Interfaces()
        self.initModule()

#------------------------------------------------------------------------------
    def update(self):
#------------------------------------------------------------------------------
#       calls energy simulations, if not up to date
#------------------------------------------------------------------------------
        Status.prj.getEquipments()  # make sure that Status.NEquipe is up to date
                                    # maybe can deleted later on, once all functions
                                    # that modify the equipment list do this automatically

        if Status.StatusEnergy == 0 or Status.int.cascadeUpdateLevel < Status.NEquipe:
            logTrack("ModuleEM2 (update): StatusEnergy %s"%Status.StatusEnergy)
            if Status.StatusCC > 0:
                Status.processData.createYearlyDemand()
            
            if Status.ANo > 0:
                logMessage(_("EINSTEIN running system simulation for updating energy balances"))
                logMessage(_("This may take a while. please be patient ..."))
                wx.SafeYield()
                Status.mod.moduleEnergy.runSimulation()
            logMessage(_("EINSTEIN now updating annual energy balances"))
            Status.mod.moduleEA.calculateEquipmentEnergyBalances()

    def initModule(self):
        """
        module initialization
        """
        allequipments = Status.prj.getEquipments()
        if self._showHeating:
            equipments = [e for e in allequipments if isHeatingEquipment(e.EquipType)]
        else:
            equipments = [e for e in allequipments if not isHeatingEquipment(e.EquipType)]
        # filling the label row
        # for the graphic data array
        LabelRow1 =['Process heat\nsupply']
        for equip in equipments:
            LabelRow1.append(unicode(equip.Equipment,"utf-8") +'\n[MWh]')

        # for the table data array
        LabelRow = copy.deepcopy(LabelRow1)
        LabelRow.append(_U('TOTAL\n[MWh]'))

        # taking the USH values from interfaces
        self.update()       # makes sure, that USH arrays are up to date
        
        USH_Tt = Status.int.USHj_Tt
        
        # calculating the monthly data start
        USHMonthly = [] #USH all equipments (matrix)
        labelColumn = [_U('Total')]
        labelColumn.extend(MONTHS)
        USHMonthly.append(labelColumn)
        # start of calculation loop
        if self._showHeating:
            maximumPoint = Status.NT + 1
        else:
            maximumPoint = 0
        for localJ in xrange(len(equipments)):
            USHMonthlyEquip = [0.0] * 13 #USH single equipment
            #Annual simulation. Hours month assumed = 730 (8760/12)
            month = 1
            j = allequipments.index(equipments[localJ])
            for it in range(Status.Nt):
                time = Status.TimeStep * it * Status.EXTRAPOLATE_TO_YEAR
                if time >= 24.0 * MONTHSTARTDAY[month]:
                    month += 1
                USHMonthlyEquip[month] += USH_Tt[j][maximumPoint][it] / 1000 #converted to [MWh]
            #calculating the total for process: USHMonthlyEquip[0]
            USHMonthlyEquip[0] = sum(USHMonthlyEquip[1:13])
            USHMonthly.append(USHMonthlyEquip)
            
        # transposing the matrix: order as shown in table
        USHMonthly = transpose(USHMonthly)
       
        # creating the data array for the graph
        GraphUSHMonthly = copy.deepcopy(USHMonthly)
        GraphUSHMonthly.insert(0,LabelRow1)
        # don't plot the yearly total 
        graphdata = [GraphUSHMonthly[0]] + GraphUSHMonthly[2:]
        data1 = array(graphdata)

        # calculating monthly totals
        for i in range(len(USHMonthly)):
            USHMonthlyTotal = sum(USHMonthly[i][1:])
            USHMonthly[i].append(USHMonthlyTotal)

        # creating the data array for the table
        TableUSHMonthly = copy.deepcopy(USHMonthly)
        TableUSHMonthly.insert(0,LabelRow)
        tabledata = TableUSHMonthly
        data = array(tabledata)

        # writing the arrays in interfaces
        self.interface.setGraphicsData(self.keys[0], data)
        self.interface.setGraphicsData(self.keys[1], data1)
        return "ok"
    
    def updatePanel(self, showHeating):
        """Update the cached data according to showHeating"""
        self._showHeating = showHeating
        self.initModule()

    def exitModule(self,exit_option):
        """
        Carry out any calculations necessary previous to displaying the HP
        design assistant window.
        """
        if exit_option == "save":
            logDebug("exitModule: here I should save the current configuration")
        elif exit_option == "cancel":
            logDebug("exitModule: here I should retrieve the previous configuration")
        else:
            logDebug("exitModule: function not yet defined")
        return "ok"
