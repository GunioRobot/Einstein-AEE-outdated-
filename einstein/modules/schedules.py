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
#	SCHEDULES
#			
#------------------------------------------------------------------------------
#			
#	Functions for management of time schedules
#
#==============================================================================
#
#	Version No.: 0.04
#	Created by: 	    Hans Schweiger	07/05/2008
#	Revised by:         Hans Schweiger      02/09/2008
#                           Hans Schweiger      08/07/2009
#                           Hans Schweiger      10/09/2009
#
#       Changes in last update:
#
#       02/09/08: HS    Security feature added -> avoid zero division in function
#                       normalize
#       08/07/09: HS    Bug-fix in fav: schedules with very short start,stop intervals
#                       didn't work well.
#       10/09/09: HS    Clean-up in schedules. now controlled by NBatch, HBatch and
#                       HPerDayInd only
#	
#------------------------------------------------------------------------------		
#	(C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008,2009,2010
#	www.energyxperts.net / info@energyxperts.net
#
#	This program is free software: you can redistribute it or modify it under
#	the terms of the GNU general public license as published by the Free
#	Software Foundation (www.gnu.org).
#
#==============================================================================

"""
:mod:`einstein.modules.schedules` -- Detailed schedules of periodic operation
=============================================================================

   :synopsis: Periodic yearly load profiles of process operation
   :author:   Hans Schweiger <hans.schweiger@energyxperts.net>
   :author:   David Baehrens <david.baehrens@energyxperts.net>
"""

from datetime import *
from math import *
from numpy import *
from random import *
from einstein.auxiliary.auxiliary import *
from einstein.GUI.status import Status
from einstein.modules.constants import *
from einstein.modules.messageLogger import *
from einstein.modules.processes import originalProcessId
from einstein.GUI.dialogGauge import DialogGauge

### Constants
periodReference = date(2007, 1, 1) # year 2007 starts and ends on Monday
DEFAULTSCHEDULES = ["operation", "batchCharge", "batchDischarge"]
DEFAULTCHARGETIME = 0.2 #20% of batch duration
TOLERANCE_GAP = 0.5
"""Minimum time between consecutive cycles after random tolerance shift (hours)"""

### Errors
class ScheduleNoProfilesError(Exception):
    """No weekly profiles selected for period schedule."""
    pass

class ScheduleNotFoundError(Exception):
    """No detailed schedule for process found in DB."""
    pass

class ProcessDataNotFoundError(Exception):
    """No data on process found in DB (table qprocessdata)."""
    pass

class InconsistentDataBaseError(Exception):
    """BUG: Data base structure is inconsistent."""
    pass

#------------------------------------------------------------------------------		
class Schedule():
#------------------------------------------------------------------------------		
#   class that defines the standard EINSTEIN format for schedules
#------------------------------------------------------------------------------		

    def __init__(self, name):     #by default assigns a constant profile throughout the year
        self.daily = [[(0.0, 24.0)]]
        self.weekly = [(0.0, 120.0)]
        self.monthly = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        self.holidays = [(365, 365)]
        self.NHolidays = 1
        self.NDays = 260
        self.HPerDay = 24.      #operating period for the present schedule
        self.NBatch = 1
        self.HBatch = 24.
        self.PartLoad = 1.0     # for effective hour scaling in detailed schedules
        self.ScheduleType = "operation"
        self.name = name
        self.HPerYear = self.NDays * self.HPerDay
        self.hop = 1.0          #yearly operation hours from normalisation calculations
                                #should be finally identical with self.HPerYear

        self.fav = None         #fav is stored as a vector, as calculation seems
                                #quite time-consuming (-> calc_fav) 
                                
#------------------------------------------------------------------------------		
    def setPars(self, ScheduleType, NDays, HPerDay, NBatch, HBatch):
#------------------------------------------------------------------------------		
#   sets the global parameters of this schedule
#------------------------------------------------------------------------------		
        if ScheduleType in DEFAULTSCHEDULES: self.ScheduleType = ScheduleType
        else: ScheduleType = DEFAULTSCHEDULES[0]
        
        self.NDays = int(checkLimits(NDays, 0, 365, default=260))
        self.NBatch = int(checkLimits(NBatch, 1, 100, default=1))
        self.HBatch = checkLimits(HBatch, 0.0, 24.0 / self.NBatch, default=Status.HPerDayInd / self.NBatch)
        # self.HPerDay and self.HPerYear are calculated in setDefault

        self.setDefault(ScheduleType)
        self.build_fav()
        
#------------------------------------------------------------------------------		
    def f(self, time):
#------------------------------------------------------------------------------		
#   calculates the instantaneous value of the schedule at time 
#------------------------------------------------------------------------------		
        if time < 0.0 or time > YEAR: return 0.
        day = int(floor(time / DAY)) + 1

        if self.isHoliday(day):return 0.

        weekTime = time % WEEK
        fweek = 0.0
        for period in self.weekly:
            start, stop = period
            if weekTime >= start and weekTime <= stop:
                fweek = 1.
                break
            
        month = findFirstGE(day, MONTHSTARTDAY)
        fmonth = self.monthly[month - 1]
        
        return fweek * fmonth

#------------------------------------------------------------------------------		
    def calc_fav(self, time):
#------------------------------------------------------------------------------		
#   calculates the average value within the interval [time,time+Dt] 
#------------------------------------------------------------------------------		
        if time < 0.0 or time >= YEAR: return 0.
        day = int(floor(time / DAY)) + 1

        if self.isHoliday(day):return 0.

        weekTime = time % WEEK
        fweek = 0.0

        for period in self.weekly:
            start, stop = period
            if weekTime < stop:
                weekTime1 = weekTime + Status.TimeStep
                if weekTime1 > start:
                    if weekTime >= start and weekTime1 <= stop:     #time interval fully within period
                        fweek += 1.
                        break
                    elif weekTime >= start and weekTime1 > stop:    #time interval starts within period, but ends afterwards
                        fweek += (stop - weekTime) / Status.TimeStep
                    elif weekTime < start and weekTime1 <= stop:    #time interval starts before period, but ends within
                        fweek += (weekTime1 - start) / Status.TimeStep
                    elif weekTime < start and weekTime1 > stop:
                        fweek += (stop - start) / Status.TimeStep
                else:
                    break
            
        month = findFirstGE(day, MONTHSTARTDAY)
        fmonth = self.monthly[month - 1]

        return fweek * fmonth
        
#------------------------------------------------------------------------------		
    def isHoliday(self, day):
#------------------------------------------------------------------------------		
        for period in self.holidays:
            start, stop = period
            if day <= stop and day >= start: return True
            
        return False

#------------------------------------------------------------------------------		
    def normalize(self):
#------------------------------------------------------------------------------		
        fsum = 0.0
        ftot = 0.0
        for it in range(Status.Nt):
            fsum += self.fav[it]
            ftot += Status.TimeStep

        fsum *= YEAR / ftot
        self.hop = fsum

        if fsum > 0:
            for it in range(Status.Nt):
                self.fav[it] /= fsum
        else:
            logDebug("Schedule (normalize): WARNING - schedule is 0 in all time steps")

        if fabs(self.hop - self.HPerYear) > 1.0:
            logDebug("Schedule (normalize): WARNING - normalized operating hours (%s) different from specified in HPerYear (%s)"\
                     % (self.hop, self.HPerYear))

        return fsum

        
#------------------------------------------------------------------------------		
    def build_fav(self):
#------------------------------------------------------------------------------		
#   calculates the vector with average values for all timesteps
#------------------------------------------------------------------------------		
        self.fav = []
        for it in range(Status.Nt):
            time = Status.TimeStep * it
            self.fav.append(self.calc_fav(time))
        self.favTemp = self.fav[:]
        self.normalize()


#------------------------------------------------------------------------------		
    def setDefault(self, scheduleType):
#------------------------------------------------------------------------------		
#   based on the basic schedule parameters (basic Q) assigns a detailed
#   default schedule
#------------------------------------------------------------------------------		

        if scheduleType == "operation":

            if self.NBatch > 0 and self.HBatch * self.NBatch <= Status.HPerDayInd:
                TPeriod = Status.HPerDayInd / self.NBatch
                tStartDay = 12.0 - 0.5 * Status.HPerDayInd
            else:
                TPeriod = 24. / self.NBatch
                tStartDay = 0
                logWarning("WARNING: batch duration larger than industry operating time")


            self.daily = [[]]
            for i in range(self.NBatch):
                start = tStartDay + TPeriod * i
                stop = start + self.HBatch
                self.daily[0].append((start, stop))

            self.HPerDay = self.NBatch * self.HBatch
        
#..............................................................................		
# Charge of batch process: first DEFAULTCHARGETIME % of process duration

        elif scheduleType == "batchCharge":
            if self.NBatch > 0 and self.HBatch * self.NBatch <= Status.HPerDayInd:
                TPeriod = Status.HPerDayInd / self.NBatch
                tStartDay = 12.0 - 0.5 * Status.HPerDayInd
            else:
                TPeriod = 24. / self.NBatch
                tStartDay = 0
                logWarning("WARNING: batch duration larger than industry operating time")

            self.daily = [[]]
            for i in range(self.NBatch):
                start = tStartDay + TPeriod * i
                stop = start + DEFAULTCHARGETIME * self.HBatch
                self.daily[0].append((start, stop))

            self.HPerDay = self.NBatch * self.HBatch * DEFAULTCHARGETIME

#..............................................................................		
# Charge of batch process: first DEFAULTCHARGETIME % of process duration after process stop

        elif scheduleType == "batchDischarge":
            if self.NBatch > 0 and self.HBatch * self.NBatch <= Status.HPerDayInd:
                TPeriod = Status.HPerDayInd / self.NBatch
                tStartDay = 12.0 - 0.5 * Status.HPerDayInd
            else:
                TPeriod = 24. / self.NBatch
                tStartDay = 0
                logWarning("WARNING: batch duration larger than industry operating time")

            self.daily = [[]]
            for i in range(self.NBatch):
                start = (tStartDay + TPeriod * i + self.HBatch) % DAY
                stop = (start + DEFAULTCHARGETIME * self.HBatch) % DAY

#### take care: the %DAY controls to avoid that processes discharge AFTER 24:00 h of a day
#### this works well only for 7 days operation without holidays
#### as this is a quite strange special case, should not give problems for the moment
#### but should be improved !!!
                
                self.daily[0].append((start, stop))

            self.HPerDay = self.NBatch * self.HBatch * DEFAULTCHARGETIME

#..............................................................................		
# Now extend daily to weekly profile

        self.NDaysPerWeek = (self.NDays + self.NHolidays - 1.0) / 52.0
        self.HPerYear = self.HPerDay * self.NDays

        self.weekly = []
        for i in range(7):
            tmax = self.NDaysPerWeek * 24.0
            
            for dayinterval in self.daily[0]:
                (start, stop) = dayinterval
                start += 24.0 * i
                stop += 24.0 * i
                if start < tmax:
                    stop = min(stop, tmax)
                    self.weekly.append((start, stop))
                else:
                    break

        logTrack("Schedule (setDefault): weekly profile created: %s" % self.weekly)
        
#------------------------------------------------------------------------------		
class Schedules(object):
#------------------------------------------------------------------------------		
#   Module that handles all project schedules
#------------------------------------------------------------------------------		
    
#------------------------------------------------------------------------------		
    def __init__(self):
#------------------------------------------------------------------------------		
        self.outOfDate = True
       
#------------------------------------------------------------------------------		
#------------------------------------------------------------------------------		
    def create(self):
#------------------------------------------------------------------------------		

        (projectData, generalData) = Status.prj.getProjectData()
        Status.HPerDayInd = projectData.HPerDayInd
        if Status.HPerDayInd is None:
            logWarning(_("Industry operating hours are not defined !\n12 hours per day assumed"))
            Status.HPerDayInd = 12.0

        dlg = DialogGauge(Status.main, _("Schedules of operation"), _("generating schedules"))

        self.calculateProcessSchedules()
        dlg.update(40)
        
        self.calculateEquipmentSchedules()
        dlg.update(80)
        
        self.calculateWHEESchedules()
        dlg.Destroy()

        self.outOfDate = False
       
#------------------------------------------------------------------------------		
#------------------------------------------------------------------------------		
    def calculateProcessSchedules(self):
#------------------------------------------------------------------------------		
#   calculates the Schedules of the processes
#------------------------------------------------------------------------------		

        logTrack("Schedules (calcProcS): running")
        
        processes = Status.prj.getProcesses()

        self.procOpSchedules = []
        self.procStartUpSchedules = []
        self.procInFlowSchedules = []
        self.procOutFlowSchedules = []
        
        for process in processes:
            try:
                periodSchedule = PeriodSchedule(process.Process)
                periodSchedule.loadFromDB(originalProcessId(process.QProcessData_ID))
            except ScheduleNotFoundError:
                pass
            else: # wrap detailed schedule into old simple schedule class interface
                #daily   = [[(0.0,24.0)]]
                monthly = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                #holidays = [(365,365)]
                #NHolidays = 1
                NDays = periodSchedule.getNumberOfOperationDays()
                HPerDay = periodSchedule.getOperationHoursPerDay()
                NBatch = periodSchedule.getNumberOfBatchesPerDay()
                HBatch = periodSchedule.getDurationHoursPerBatch()
                PartLoad = periodSchedule.getDailyPartLoad()
                HPerYear = Status.TimeStep * periodSchedule.getOperationHoursPerYear()
                hop = HPerYear
                operationSchedule = Schedule("Process No.%s (%s): Detailed Operation" % (process.ProcNo, process.Process))
                startupSchedule = Schedule("Process No.%s (%s): Detailed Start-Up" % (process.ProcNo, process.Process))
                inflowSchedule = Schedule("Process No.%s (%s): Detailed InFlow 1" % (process.ProcNo, process.Process))
                outflowSchedule = Schedule("Process No.%s (%s): Detailed OutFlow 1" % (process.ProcNo, process.Process))
                periodSchedule.dbId = process.QProcessData_ID
                operationSchedule.detailedSchedule = startupSchedule.detailedSchedule = inflowSchedule.detailedSchedule = outflowSchedule.detailedSchedule = periodSchedule    
                operationSchedule.NDays = startupSchedule.NDays = inflowSchedule.NDays = outflowSchedule.NDays = NDays
                operationSchedule.HPerDay = startupSchedule.HPerDay = inflowSchedule.HPerDay = outflowSchedule.HPerDay = HPerDay
                operationSchedule.NBatch = startupSchedule.NBatch = inflowSchedule.NBatch = outflowSchedule.NBatch = NBatch
                operationSchedule.HBatch = startupSchedule.HBatch = inflowSchedule.HBatch = outflowSchedule.HBatch = HBatch
                operationSchedule.PartLoad = startupSchedule.PartLoad = inflowSchedule.PartLoad = outflowSchedule.PartLoad = PartLoad
                operationSchedule.HPerYear = startupSchedule.HPerYear = inflowSchedule.HPerYear = outflowSchedule.HPerYear = HPerYear
                operationSchedule.hop = startupSchedule.hop = inflowSchedule.hop = outflowSchedule.hop = hop
                operationSchedule.NDays = startupSchedule.NDays = inflowSchedule.NDays = outflowSchedule.NDays = NDays
                operationSchedule.monthly = startupSchedule.monthly = inflowSchedule.monthly = outflowSchedule.monthly = monthly
                if process.ProcType == "batch":
                    operationSchedule.ScheduleType = "operation"
                    operationSchedule.fav = periodSchedule.getYearlyBatchOperationProfile(withHolidays=True, withTolerance=True)
                    operationSchedule.weekly = periodSchedule.getMeanWeeklyBatchOperationTimePeriods()
                    startupSchedule.ScheduleType = "batchCharge"
                    startupSchedule.fav = periodSchedule.getYearlyBatchStartupProfile(withHolidays=True, withTolerance=True)
                    startupSchedule.weekly = periodSchedule.getMeanWeeklyBatchStartupTimePeriods() 
                    inflowSchedule.ScheduleType = "batchCharge"
                    inflowSchedule.fav = periodSchedule.getYearlyBatchInflowProfile(withHolidays=True, withTolerance=True)
                    inflowSchedule.weekly = periodSchedule.getMeanWeeklyBatchInflowTimePeriods()
                    outflowSchedule.ScheduleType = "batchDischarge"
                    outflowSchedule.fav = periodSchedule.getYearlyBatchOutflowProfile(withHolidays=True, withTolerance=True)
                    outflowSchedule.weekly = periodSchedule.getMeanWeeklyBatchOutflowTimePeriods() 
                else: # assume continuous process
                    operationSchedule.ScheduleType = "operation"
                    operationSchedule.fav = periodSchedule.getYearlyContinuousOperationProfile(withHolidays=True, withTolerance=True)
                    operationSchedule.weekly = periodSchedule.getMeanWeeklyContinuousOperationTimePeriods()
                    startupSchedule.ScheduleType = "batchCharge"
                    startupSchedule.fav = periodSchedule.getYearlyContinuousStartupProfile(withHolidays=True, withTolerance=True)
                    startupSchedule.weekly = periodSchedule.getMeanWeeklyContinuousStartupTimePeriods() 
                    inflowSchedule.ScheduleType = "operation"
                    inflowSchedule.fav = periodSchedule.getYearlyContinuousInflowProfile(withHolidays=True, withTolerance=True)
                    inflowSchedule.weekly = periodSchedule.getMeanWeeklyContinuousInflowTimePeriods()
                    inflowSchedule.hop = inflowSchedule.HPerYear
                    outflowSchedule.ScheduleType = "operation"
                    outflowSchedule.fav = periodSchedule.getYearlyContinuousOutflowProfile(withHolidays=True, withTolerance=True)
                    outflowSchedule.weekly = periodSchedule.getMeanWeeklyContinuousOutflowTimePeriods() 
                    outflowSchedule.HPerYear = Status.TimeStep * periodSchedule.getOperationHoursPerYear(withHolidays=True, withTolerance=True)
                    outflowSchedule.hop = outflowSchedule.HPerYear 
                self.procOpSchedules.append(operationSchedule)
                self.procStartUpSchedules.append(startupSchedule)
                self.procInFlowSchedules.append(inflowSchedule)
                self.procOutFlowSchedules.append(outflowSchedule)
                return             

#..............................................................................
# check if data are correct

            if process.ProcType == "continuous":
                if process.NBatch != 1 or process.HBatch != process.HPerDayProc:
                    logDebug("Schedules (calculate): error in process schedule")
                    process.HBatch = process.HPerDayProc
                    process.NBatch = 1
                    Status.SQL.commit()

            logDebug("Process No.%s (%s):" % (process.ProcNo, process.Process))
#..............................................................................
# schedule for process operation
                    
            newSchedule = Schedule("Process No.%s (%s): Operation" % (process.ProcNo, process.Process))

            if process.ProcType == "continuous":
                scheduleType = "operation"
            else:
                scheduleType = "operation"
            newSchedule.setPars(scheduleType,
                                   process.NDaysProc,
                                   process.HPerDayProc,
                                   process.NBatch,
                                   process.HBatch)
            self.procOpSchedules.append(newSchedule)
            
#..............................................................................
# schedule for process start-up

            newSchedule = Schedule("Process No.%s (%s): Start-Up" % (process.ProcNo, process.Process))
            
            if process.ProcType == "continuous":
                scheduleType = "batchCharge"
            else:
                scheduleType = "batchCharge"
                
            newSchedule.setPars(scheduleType,
                                   process.NDaysProc,
                                   process.HPerDayProc,
                                   process.NBatch,
                                   process.HBatch)
            self.procStartUpSchedules.append(newSchedule)

#..............................................................................
# schedule for process in-flows (for the moment only ONE !!!)

            newSchedule = Schedule("Process No.%s (%s): InFlow 1" % (process.ProcNo, process.Process))
            
            if process.ProcType == "continuous":
                scheduleType = "operation"
            else:
                scheduleType = "batchCharge"
                
            newSchedule.setPars(scheduleType,
                                   process.NDaysProc,
                                   process.HPerDayProc,
                                   process.NBatch,
                                   process.HBatch)
            self.procInFlowSchedules.append(newSchedule)

            newSchedule = Schedule("Process No.%s (%s): OutFlow 1" % (process.ProcNo, process.Process))
            if process.ProcType == "continuous":
                scheduleType = "operation"
            else:
                scheduleType = "batchDischarge"
            newSchedule.setPars(scheduleType,
                                   process.NDaysProc,
                                   process.HPerDayProc,
                                   process.NBatch,
                                   process.HBatch)
            self.procOutFlowSchedules.append(newSchedule)
       
#------------------------------------------------------------------------------		
#------------------------------------------------------------------------------		
    def calculateEquipmentSchedules(self):
#------------------------------------------------------------------------------		
#   calulates the Schedules of the processes
#------------------------------------------------------------------------------		

        logTrack("Schedules (calcEquipeSchedules): running")
        
        equipments = Status.prj.getEquipments()

        self.equipmentSchedules = []
        
        for equipe in equipments:

#..............................................................................
# schedule for equipment operation
                    
            newSchedule = Schedule("Equipe No.%s (%s)" % (equipe.EqNo, equipe.Equipment))

            newSchedule.setPars("operation",
                                equipe.NDaysEq,
                                equipe.HPerDayEq,
                                1,
                                equipe.HPerDayEq)
            self.equipmentSchedules.append(newSchedule)
            
#------------------------------------------------------------------------------		
#------------------------------------------------------------------------------		
    def calculateWHEESchedules(self):
#------------------------------------------------------------------------------		
#   calulates the Schedules of the electrical equipment w. waste heat
#------------------------------------------------------------------------------		

        logTrack("Schedules (calcWHEESchedules): running")
        
        whees = Status.prj.getWHEEs()

        self.WHEESchedules = []
        
        for whee in whees:

#..............................................................................
# schedule for equipment operation
                    
            newSchedule = Schedule("WHEE No.%s (%s)" % (whee.WHEENo, whee.WHEEName))

            newSchedule.setPars("operation",
                                whee.NDaysWHEE,
                                whee.HPerDayWHEE,
                                whee.NBatchWHEE,
                                whee.HBatchWHEE)
            self.WHEESchedules.append(newSchedule)
            
#------------------------------------------------------------------------------		

def dateToFirstYearHourOfDay(d):
    return (date(periodReference.year, d.month, d.day) - periodReference).days * int(DAY)

def dateToLastYearHourOfDay(d):
    return (((date(periodReference.year, d.month , d.day) - periodReference).days + 1) * int(DAY) - 1)

def intervalsOnOffUnit(profile):
        """Retrieve on/off intervals from load profile.
        
        Intervals start and stop when going through zero. The load is the unit load of 1.0.
        
        :returns: Uniform running intervals (load > 0) of inclusive starting hour [0,|profile|-1], inclusive stopping hour [0,|profile|-1], and load 1.0
        :rtype:   List of 3-Tuples
        """
        profileOnOffIntervals = []
        off = True
        start = None
        for (hour, scale) in enumerate(profile):
            if off and (scale > 0.):
                start = hour
                scaleSum = scale
                off = False
            elif not(off) and (scale == 0.):
                profileOnOffIntervals.append((start, hour - 1, 1.0))
                off = True
                start = None
            elif not(off) and scale > 0.:
                scaleSum += scale
        if (start != None) and not(off):
            profileOnOffIntervals.append((start, len(profile) - 1, 1.0))
        return profileOnOffIntervals
    
def weeklyMeanOfYearlyProfile(yearlyProfile):
    """Retrieve a weekly load profile with mean load during the year.
        
    :returns: Load [0,1] for week hour [0,167]
    :rtype:   List of Float
    """
    weeklyProfile = [0.] * int(WEEK)
    for weekHour in xrange(int(WEEK)):
        yearlyWeekHours = yearlyProfile[weekHour:int(YEAR):int(WEEK)]
        weeklyProfile[weekHour] = sum(yearlyWeekHours) / len(yearlyWeekHours)
    return weeklyProfile

def deleteProcessScheduleFromDB(processId):
    """Remove all yearly load profile intervals and tolerance offsets from data base for a given process.
        
    :param processId: Data base ID of process from which to remove the schedule
    :type  processId: Integer
        
    :returns: nothing
    """
    processScheduleRows = Status.DB.process_schedules.qprocessdata_QProcessData_ID[processId]
    while True:
        try:
            processScheduleInterval = processScheduleRows.pop()
            processScheduleInterval.delete()
        except IndexError:
            break

    processScheduleToleranceOffsetRows = Status.DB.process_schedules_tolerance_offsets.qprocessdata_QProcessData_ID[processId]
    while True:
        try:
            processScheduleToleranceOffset = processScheduleToleranceOffsetRows.pop()
            processScheduleToleranceOffset.delete()
        except IndexError:
            break
        
def deleteProcessPeriodsFromDB(processId):
    """Remove all profile periods defined for a given process from data base.
        
    :param processId: Data base ID of process from which to remove the periods
    :type  processId: Integer
        
    :returns: nothing
    """
    processPeriodRows = Status.DB.process_periods.qprocessdata_QProcessData_ID[processId]
    while True:
        try:
            processPeriod = processPeriodRows.pop()
        except IndexError:
            break
        processPeriodProfileRows = Status.DB.process_period_profiles.process_periods_id[processPeriod.id]
        while True:
            try:
                processPeriodProfile = processPeriodProfileRows.pop()
                processPeriodProfile.delete() 
            except IndexError:
                break
        processPeriod.delete()    

def exportProcessPeriodsFromDB(processId):
    """Export all defined process periods from data base.
    
    The periods are sorted by the start hour.
    
    :returns: [{"start" : inclusive start hour of year, "stop" : inclusive stop hour of year, "step": stepping through period in hours, "scale" : load [0,1], "profiles" : [profile names]}]
    :rtype: List of Dictionaries
    """
    processPeriods = []
    for processPeriod in Status.DB.process_periods.qprocessdata_QProcessData_ID[processId]:
        processPeriodProfileNames = []
        for processPeriodProfile in Status.DB.process_period_profiles.process_periods_id[processPeriod.id]:
            processPeriodProfileNames.append(Status.DB.profiles.id[processPeriodProfile.profiles_id].name.column()[0])
        startDate = Status.DB.periods.id[processPeriod.periods_id].start.column()[0]
        startHour = round(dateToFirstYearHourOfDay(startDate), 2)
        stopDate = Status.DB.periods.id[processPeriod.periods_id].stop.column()[0]
        stopHour = round(dateToLastYearHourOfDay(stopDate) + 1, 2) # stopHour is point in time 
        step = float(processPeriod.step) * DAY
        scale = float(processPeriod.scale) * .01
        processPeriods.append({"start"    : startHour,
                               "stop"     : stopHour,
                               "step"     : step,
                               "scale"    : scale,
                               "profiles" : processPeriodProfileNames})
    processPeriods.sort(key=lambda x: x["start"])
    return processPeriods

def exportHolidayIntervalsFromDB(questionnaireId):
    """Export the industry holiday intervals from the data base.
    
    :param questionnaireId: questionnaire.id for SQL data base.
    :type  questionnaireId: Integer
    
    :returns: [{"start" : start hour point in year [0,8760], "stop" : stop hour point in year [0,8760]}]
    :rtype: List of Dictionaries
    """
    industryHolidays = []
    
    # first holiday period
    startDate = Status.DB.questionnaire.Questionnaire_ID[questionnaireId].NoProdStart_1.column().pop()
    stopDate = Status.DB.questionnaire.Questionnaire_ID[questionnaireId].NoProdStop_1.column().pop()
    if startDate and stopDate:
        startHour = dateToFirstYearHourOfDay(startDate)
        stopHour = dateToLastYearHourOfDay(stopDate) + 1 # stopHour is point in time
        industryHolidays.append({"start" : float(startHour), "stop"  : float(stopHour)})
    
    # second holiday period
    startDate = Status.DB.questionnaire.Questionnaire_ID[questionnaireId].NoProdStart_2.column().pop()
    stopDate = Status.DB.questionnaire.Questionnaire_ID[questionnaireId].NoProdStop_2.column().pop()
    if startDate and stopDate:
        startHour = dateToFirstYearHourOfDay(startDate)
        stopHour = dateToLastYearHourOfDay(stopDate) + 1 # stopHour is point in time
        industryHolidays.append({"start" : float(startHour), "stop"  : float(stopHour)})
    
    # third holiday period
    startDate = Status.DB.questionnaire.Questionnaire_ID[questionnaireId].NoProdStart_3.column().pop()
    stopDate = Status.DB.questionnaire.Questionnaire_ID[questionnaireId].NoProdStop_3.column().pop()
    if startDate and stopDate:
        startHour = dateToFirstYearHourOfDay(startDate)
        stopHour = dateToLastYearHourOfDay(stopDate) + 1 # stopHour is point in time
    
    return industryHolidays

class PeriodSchedule(object):
    """Detailed schedules of process load by hour of year with periodic differences.
    
    :param name: Descriptive name of the schedule
    :type  name: String
    :param startup: Duration of process start up phase in hours
    :type  startup: Float
    :param inflow:  Duration of process charge time in hours
    :type  inflow:  Float
    :param outflow: Duration of process discharge time in hours
    :type  outflow: Float
    :param tolerance: Duration of tolerated back-/forward-shift of schedule times in hours
    :type  tolerance: Float
    :param holidayScale: Global load scale factor [0,100] of process during industry holidays
    :type  holidayScale: Integer
    :param holidays: Starting and stopping hours of holiday periods (hour of year [0,8759], inclusive)
    :type holidays:  List of Integer 2-Tuple
    :param schedule: Load [0,1] during each hour of year [0,8759]
    :type schedule:  List of Float

    :returns: Period schedule instance
    :rtype: einstein.modules.schedules.PeriodSchedule
    """

    def __init__(self, name, startup=None, inflow=None, outflow=None, tolerance=None, holidayScale=None, holidays=None, schedule=None):
        self.name = name
        self.startup = startup
        self.inflow = inflow
        self.outflow = outflow
        if tolerance != None:
            self.tolerance = tolerance
        else:
            self.tolerance = 0.
        if holidayScale != None:
            self.holidayScale = holidayScale
        else:
            self.holidayScale = 0
        if holidays != None:
            self.holidays = holidays
        else:
            self.clearHolidays()
        if schedule != None:
            self.schedule = schedule
        else:
            self.clearSchedule()
        self.updateToleranceOffset()
            
    def updateToleranceOffset(self, toleranceOffset=None):
        """Draw a random tolerance offset for each cycle during the year.
        
        :param toleranceOffset: Offsets for each cycle, default: draw random offsets in interval +/- PeriodSchedule.tolerance 
        :type  toleranceOffset: List of float
        
        :returns: nothing
        """
        if toleranceOffset:
            self.toleranceOffset = toleranceOffset
        else:
            self.toleranceOffset = []
            random = Random()
            random.seed()
            for cylce in range(self.getNumberOfBatchesPerYear(withHolidays=False, withTolerance=False)):
                self.toleranceOffset.append(random.uniform(-self.tolerance, self.tolerance))
    
    def clearHolidays(self):
        """Remove all holiday periods.
        
        :returns: nothing
        """
        self.holidays = []
        
    def addHolidays(self, start, stop):
        """Define a holiday period by two dates.
        
        :param start: starting date (year does not matter, inclusive)
        :type  start: date
        :param  stop: stopping date (year does not matter, inclusive)
        :type   stop: date
        
        :returns: nothing
        """
        holidayStartHour = dateToFirstYearHourOfDay(start)
        holidayStopHour = dateToLastYearHourOfDay(stop)
        self.holidays.append((holidayStartHour, holidayStopHour))
        
    def isHolidays(self, hour):
        """Determine whether a hour of year [0,8759] is during a holiday period.
        
        :param hour: 0-based hour of year [0,8759]
        :type  hour: Integer
        
        :returns: Is hour during holidays?
        :rtype:   Boolean
        """
        for (start, stop) in self.holidays:
            if start <= hour and hour <= stop:
                return True
        return False

    def clearSchedule(self):
        """Define an all-zero yearly profile.
        
        :returns: nothing
        """
        self.schedule = array([0.] * int(YEAR))
    
    def addPeriodProfile(self, start, stop, step, scale, profile):
        """Set an operation time profile in a specific period of the year.
        
        Repeated calls are cumulative. Holiday periods are handled separately by :meth:`einstein.modules.schedules.addHolidays`.
        
        :param start: starting date of period (year does not matter, inclusive)
        :type  start: date
        :param  stop: stopping date of period (year does not matter, inclusive)
        :type   stop: date
        :param  step: daily stepping through the period (1=every day, 2=every second day, etc.)
        :type   step: Integer
        :param scale: Global load scaling [0,100] during the period
        :type  scale: Integer
        :param profile: A weekly profile on selected weekdays during the period.
        :type  profile: einstein.modules.profiles.WeeklyProfile
        
        :returns: nothing
        """
        periodStartHour = dateToFirstYearHourOfDay(start)
        periodStopHour = dateToLastYearHourOfDay(stop)
        profileWeekday = profile.getWeekdays()
        for yearHour in range(periodStartHour, periodStopHour + 1):
            for (intervalStartTime, intervalStopTime, intervalScale) in profile.getProfile():
                intervalStartDayTime = timedelta(hours=intervalStartTime.hour, minutes=intervalStartTime.minute).seconds / 3600.0
                intervalStartDayHour = int(intervalStartDayTime)
                intervalStopDayTime = timedelta(hours=intervalStopTime.hour, minutes=intervalStopTime.minute).seconds / 3600.0
                intervalStopDayHour = int(intervalStopDayTime)
                yearDayHour = yearHour % int(DAY)
                if intervalStartDayHour >= intervalStopDayHour: # wrap around start of next day
                    if not ((intervalStartDayHour <= yearDayHour)  or (yearDayHour <= intervalStopDayHour)): continue
                else:
                    if not ((intervalStartDayHour <= yearDayHour) and (yearDayHour <= intervalStopDayHour)): continue
                if yearDayHour < intervalStartDayHour: # this is the next day
                    if (((yearHour - int(DAY)) / int(DAY)) % step) != 0: break # only run if started the day before
                    yearHourWeekdayIndex = ((yearHour - int(DAY)) / int(DAY)) % len(profile.getWeekdays())
                    if not profileWeekday[yearHourWeekdayIndex]: break # only run if started on the weekday before
                else: # this is the current day
                    if ((yearHour / int(DAY)) % step) != 0: break # only run if started on this day
                    yearHourWeekdayIndex = (yearHour / int(DAY)) % len(profile.getWeekdays())
                    if not profileWeekday[yearHourWeekdayIndex]: break # only run if started on this weekday
                # keep fractions for weighted averaging
                if yearDayHour == intervalStartDayHour:
                    intervalHourFrac = 1. - fmod(intervalStartDayTime, 1)
                elif yearDayHour == intervalStopDayHour:
                    intervalHourFrac = fmod(intervalStopDayTime, 1)
                else:
                    intervalHourFrac = 1.
                # schedule saves floats
                self.schedule[yearHour] = (scale * .01) * ((intervalHourFrac * intervalScale * .01) + ((1. - intervalHourFrac) * self.schedule[yearHour]))
        
                
    def getYearlyProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the yearly load profile optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        :rtype:   List of Float
        """
        if withTolerance:
            schedule = [0.] * int(YEAR)
            lastStop = -TOLERANCE_GAP
            for (cycle, (start, stop, scale)) in enumerate(self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance=False)):
                newStart = (start + self.toleranceOffset[cycle])    # fractional start time point
                if newStart < lastStop + TOLERANCE_GAP: # minimal gap between cycles
                    newStart = lastStop + TOLERANCE_GAP
                    self.toleranceOffset[cycle] = newStart - start
                newStop = (stop + 1 + self.toleranceOffset[cycle]) # fractional stop time point
                lastStop = newStop
                newStartHour = int(ceil(newStart)) # integer inclusive start hour
                newStopHour = int(floor(newStop)) # integer exclusive stop  hour
                for hour in range(newStartHour, newStopHour): # shift hour load to new integer inclusive hours
                    schedule[hour % int(YEAR)] = self.schedule[hour + (start - newStartHour)]
                startFracHour = int(floor(newStart - 1e-10)) # integer hour containing fractional load
                stopFracHour = int(floor(newStop))          # integer hour containing fractional load
                newFrac = fmod(self.toleranceOffset[cycle], 1)
                if newFrac < 0: # shift left
                    schedule[startFracHour % int(YEAR)] += abs(newFrac) * self.schedule[start]
                    schedule[stopFracHour % int(YEAR)] += (1. + newFrac) * self.schedule[stop]
                elif newFrac > 0.: # shift right
                    schedule[startFracHour % int(YEAR)] += (1. - newFrac) * self.schedule[start]
                    schedule[stopFracHour % int(YEAR)] += newFrac * self.schedule[stop]
        else:
            schedule = self.schedule
        if withHolidays:
            return array([(self.isHolidays(hour) and [(scale * self.holidayScale * .01)] or [scale])[0] for (hour, scale) in enumerate(schedule)])
        else:
            return schedule
    
    def getYearlyProfileIntervals(self, withHolidays=True, withTolerance=False):
        """Retrieve the yearly running load intervals optionally with industry holidays.
        
        Consecutive intervals with different load are given for load changes not going through zero.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Uniform running intervals (load > 0) of inclusive starting hour [0,8759], inclusive stopping hour [0,8759], and load (0,1]
        :rtype:   List of 3-Tuples
        """
        yearlyProfileIntervals = []
        lastScale = 0.
        start = None
        for (hour, scale) in enumerate(self.getYearlyProfile(withHolidays, withTolerance)):
            if scale != lastScale:
                if start == None:
                    start = hour
                else:
                    yearlyProfileIntervals.append((start, hour - 1, lastScale))
                if scale > 0.:
                    start = hour
                else:
                    start = None
                lastScale = scale
        if (start != None):
            yearlyProfileIntervals.append((start, int(YEAR) - 1, lastScale))
        return yearlyProfileIntervals
    
    def getYearlyProfileOnOffMeanIntervals(self, withHolidays=True, withTolerance=False):
        """Retrieve the yearly on/off intervals optionally with industry holidays.
        
        Intervals start and stop when going through zero. The load is the mean load during the on/off interval.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Uniform running intervals (load > 0) of inclusive starting hour [0,8759], inclusive stopping hour [0,8759], and load (0,1]
        :rtype:   List of 3-Tuples
        """
        yearlyProfileOnOffIntervals = []
        off = True
        start = None
        for (hour, scale) in enumerate(self.getYearlyProfile(withHolidays, withTolerance)):
            if off and (scale > 0.):
                start = hour
                scaleSum = scale
                off = False
            elif not(off) and (scale == 0.):
                yearlyProfileOnOffIntervals.append((start, hour - 1, scaleSum / (hour - start)))
                off = True
                start = None
            elif not(off) and scale > 0.:
                scaleSum += scale
        if (start != None) and not(off):
            yearlyProfileOnOffIntervals.append((start, int(YEAR) - 1, scaleSum / (int(YEAR) - start))) 
        return yearlyProfileOnOffIntervals
    
    def getYearlyProfileOnOffUnitIntervals(self, withHolidays=True, withTolerance=False):
        """Retrieve the yearly on/off intervals optionally with industry holidays.
        
        Intervals start and stop when going through zero. The load is the unit load of 1.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Uniform running intervals (load > 0) of inclusive starting hour [0,8759], inclusive stopping hour [0,8759], and load 1
        :rtype:   List of 3-Tuples
        """
        return [(start, stop, 1.) for (start, stop, scale) in self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance)]
    
    def getYearlyStartupProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the yearly charge load profile optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        """
        yearlyProfile = [0.] * int(YEAR)
        try:
            startupHours = int(self.startup)
            startupFrac = fmod(self.startup, 1)
        except TypeError: # use DEFAULTCHARGETIME for each cycle
            for (start, stop, scale) in self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance):
                cycleStartup = DEFAULTCHARGETIME * (stop - start + 1) 
                startupHours = int(cycleStartup)
                startupFrac = fmod(cycleStartup, 1)
                yearlyProfile[start:start + startupHours] = [scale] * startupHours
                yearlyProfile[start + startupHours:start + startupHours + 1] = [startupFrac * scale]
        else:
            for (start, stop, scale) in self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance):
                yearlyProfile[start:start + startupHours] = [scale] * startupHours
                yearlyProfile[start + startupHours:start + startupHours + 1] = [startupFrac * scale]
        return yearlyProfile
    
    def getYearlyInflowProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the yearly charge load profile optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        :rtype:   List of Float
        """
        yearlyProfile = [0.] * int(YEAR)
        try:
            inflowHours = int(self.inflow)
            inflowFrac = fmod(self.inflow, 1)
        except TypeError: # use DEFAULTCHARGETIME for each cycle
            for (start, stop, scale) in self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance):
                cycleInflow = DEFAULTCHARGETIME * (stop - start + 1) 
                inflowHours = int(cycleInflow)
                inflowFrac = fmod(cycleInflow, 1)
                yearlyProfile[start:start + inflowHours] = [scale] * inflowHours
                yearlyProfile[start + inflowHours:start + inflowHours + 1] = [inflowFrac * scale]
        else:
            for (start, stop, scale) in self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance):
                yearlyProfile[start:start + inflowHours] = [scale] * inflowHours
                yearlyProfile[start + inflowHours:start + inflowHours + 1] = [inflowFrac * scale]
        return yearlyProfile
    
    def getYearlyOutflowProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the yearly discharge load profile optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        :rtype:   List of Float
        """
        yearlyProfile = [0.] * int(YEAR)
        try:
            outflowHours = int(self.outflow)
            outflowFrac = fmod(self.outflow, 1)
        except TypeError: # use DEFAULTCHARGETIME for each cycle
            for (start, stop, scale) in self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance):
                cycleOutflow = DEFAULTCHARGETIME * (stop - start + 1) 
                outflowHours = int(cycleOutflow)
                outflowFrac = fmod(cycleOutflow, 1)
                yearlyProfile[stop + 1:stop + 1 + outflowHours] = [scale] * outflowHours
                yearlyProfile[stop + 1 + outflowHours:stop + 1 + outflowHours + 1] = [outflowFrac * scale]
        else:
            for (start, stop, scale) in self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance):
                yearlyProfile[stop + 1:stop + 1 + outflowHours] = [scale] * outflowHours
                yearlyProfile[stop + 1 + outflowHours:stop + 1 + outflowHours + 1] = [outflowFrac * scale]
        return yearlyProfile
    
    def getWeeklyProfile(self, start):
        """Retrieve a weekly load profile without industry holidays starting on Monday not before a given start date.
        
        :param start: Date for the weekly profile to start not before (year does not matter)   
        :type  start: date
        
        :returns: Load [0,1] for week hour [0,167]
        :rtype:   List of Float
        """
        start = date(periodReference.year, start.month, start.day)
        if start.weekday() != 0: # start weekly profile on Monday
            start = start + timedelta(days=abs(start.weekday() - 7))
        startYearHour = dateToFirstYearHourOfDay(start)
        return self.schedule[startYearHour:startYearHour + int(WEEK)]
    
    def getYearlyContinuousOperationProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the normalized yearly operation load profile for continuous processes optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        :rtype:   List of Float
        """
        return normalize(self.getYearlyProfile(withHolidays, withTolerance))
        
    def getYearlyContinuousStartupProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the normalized yearly startup load profile for continuous processes optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        :rtype:   List of Float
        """
        return normalize(self.getYearlyStartupProfile(withHolidays, withTolerance))
    
    def getYearlyContinuousInflowProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the normalized yearly charge load profile for continuous processes optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        :rtype:   List of Float
        """
        return self.getYearlyContinuousOperationProfile(withHolidays, withTolerance)
    
    def getYearlyContinuousOutflowProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the normalized yearly discharge load profile for continuous processes optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        :rtype:   List of Float
        """
        return self.getYearlyContinuousOperationProfile(withHolidays, withTolerance)
    
    def getYearlyBatchOperationProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the normalized yearly operation load profile for batch processes optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        :rtype:   List of Float
        """
        return self.getYearlyContinuousOperationProfile(withHolidays, withTolerance)
    
    def getYearlyBatchStartupProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the normalized yearly startup load profile for batch processes optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        :rtype:   List of Float
        """
        return self.getYearlyContinuousStartupProfile(withHolidays, withTolerance)
    
    def getYearlyBatchInflowProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the normalized yearly charge load profile for batch processes optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        :rtype:   List of Float
        """
        return normalize(self.getYearlyInflowProfile(withHolidays, withTolerance))
    
    def getYearlyBatchOutflowProfile(self, withHolidays=True, withTolerance=False):
        """Retrieve the normalized yearly discharge load profile for batch processes optionally with industry holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Load [0,1] for year hour [0,8759]
        :rtype:   List of Float
        """
        return normalize(self.getYearlyOutflowProfile(withHolidays, withTolerance))
    
    def getMeanWeeklyContinuousOperationTimePeriods(self):
        """Retrieve the mean weekly operation time periods for continuous processes.
        
        :returns: Weekly starting and stopping hours
        :rtype:   List of (Float,Float)
        """
        return [(float(start), end + 1.0) for (start, end, load) in intervalsOnOffUnit(weeklyMeanOfYearlyProfile(self.getYearlyProfile(withHolidays=False, withTolerance=False)))]
                                  
    def getMeanWeeklyContinuousStartupTimePeriods(self):
        """Retrieve the mean weekly start-up time periods for continuous processes.
        
        :returns: Weekly starting and stopping hours
        :rtype:   List of (Float,Float)
        """
        return [(float(start), end + 1.0) for (start, end, load) in intervalsOnOffUnit(weeklyMeanOfYearlyProfile(self.getYearlyStartupProfile(withHolidays=False, withTolerance=False)))]

    def getMeanWeeklyContinuousInflowTimePeriods(self):
        """Retrieve the mean weekly in-flow time periods for continuous processes.
        
        :returns: Weekly starting and stopping hours
        :rtype:   List of (Float,Float)
        """
        return self.getMeanWeeklyContinuousOperationTimePeriods()
    
    def getMeanWeeklyContinuousOutflowTimePeriods(self):
        """Retrieve the mean weekly out-flow time periods for continuous processes.
        
        :returns: Weekly starting and stopping hours
        :rtype:   List of (Float,Float)
        """
        return self.getMeanWeeklyContinuousOperationTimePeriods()
    
    def getMeanWeeklyBatchOperationTimePeriods(self):
        """Retrieve the mean weekly operation time periods for batch processes.
        
        :returns: Weekly starting and stopping hours
        :rtype:   List of (Float,Float)
        """
        return self.getMeanWeeklyContinuousOperationTimePeriods()

    def getMeanWeeklyBatchStartupTimePeriods(self):
        """Retrieve the mean weekly start-up time periods for batch processes.
        
        :returns: Weekly starting and stopping hours
        :rtype:   List of (Float,Float)
        """
        return self.getMeanWeeklyContinuousStartupTimePeriods()
    
    def getMeanWeeklyBatchInflowTimePeriods(self):
        """Retrieve the mean weekly in-flow time periods for batch processes.
        
        :returns: Weekly starting and stopping hours
        :rtype:   List of (Float,Float)
        """
        return [(float(start), end + 1.0) for (start, end, load) in intervalsOnOffUnit(weeklyMeanOfYearlyProfile(self.getYearlyInflowProfile(withHolidays=False, withTolerance=False)))]
    
    def getMeanWeeklyBatchOutflowTimePeriods(self):
        """Retrieve the mean weekly out-flow time periods for batch processes.
        
        :returns: Weekly starting and stopping hours
        :rtype:   List of (Float,Float)
        """
        return [(float(start), end + 1.0) for (start, end, float) in intervalsOnOffUnit(weeklyMeanOfYearlyProfile(self.getYearlyOutflowProfile(withHolidays=False, withTolerance=False)))]

    def getNumberOfOperationDays(self, withHolidays=True, withTolerance=False):
        """Calculate the number of days with non-zero load optionally with industry holidays.
        
        :param withHolidays: Ingnore days scaled to zero during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: The number of operation days during the year
        :rtype:   Integer
        """
        nDays = 0
        lastDay = -1
        for (start, stop, scale) in self.getYearlyProfileIntervals(withHolidays, withTolerance):
            startDay = (start / int(DAY))
            stopDay = (stop / int(DAY))
            if startDay > lastDay:
                nDays += stopDay - startDay + 1
                lastDay = stopDay
        return nDays
    
    def getOperationHoursPerDay(self, withHolidays=True, withTolerance=False):
        """Calculate the mean effective hours of operation per day optionally with holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Mean operation hours per day during the year
        :rtype:   Float
        """
        days = self.getNumberOfOperationDays(withHolidays, withTolerance)
        if days == 0:
            return 0.
        else:
            return self.getOperationHoursPerYear(withHolidays, withTolerance) / days

    def getNumberOfBatchesPerYear(self, withHolidays=True, withTolerance=False):
        """Calculate the number of batches per year optionally with holidays.
        
        A batch begins with a change from zero to non-zero and ends with the next change from non-zero to zero.
        If the yearly profile is non-zero for all hours of the year, then the number of batches per year is 0. 
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Number of batches per year
        :rtype:   Integer
        """
        batches = self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance)
        try:
            (start, stop, scale) = batches[0]
        except IndexError:
            return 0
        if start == 0 and stop == int(YEAR) - 1:
            return 0
        else:
            return len(batches)

    def getNumberOfBatchesPerDay(self, withHolidays=True, withTolerance=False):
        """Calculate the mean number of batches per day optionally with holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Mean number of batches per day during the year
        :rtype:   Float
        """
        try:
            return float(len(self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance))) / float(self.getNumberOfOperationDays(withHolidays, withTolerance))
        except ZeroDivisionError:
            return 0.
    
    def getOperationHoursPerYear(self, withHolidays=True, withTolerance=False):
        """Calculate the effective hours of operation per year optionally with holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Total operation hours during the year
        :rtype:   Float
        """
        return sum(self.getYearlyProfile(withHolidays, withTolerance))
    
    def getInflowHoursPerYear(self, withHolidays=True, withTolerance=False):
        """Calculate the effective hours of effective inflow per year optionally with holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Total inflow hours during the year
        :rtype:   Float
        """
        return sum(self.getYearlyInflowProfile(withHolidays, withTolerance))
    
    def getOutflowHoursPerYear(self, withHolidays=True, withTolerance=False):
        """Calculate the effective hours of outflow per year optionally with holidays.
        
        :param withHolidays: Include the scaling during the industry holiday periods?
        :type  withHolidays: Boolean
        
        :returns: Total outflow hours during the year
        :rtype:   Float
        """
        return sum(self.getYearlyOutflowProfile(withHolidays, withTolerance))
    
    def getOperationHoursPerBatch(self, withHolidays=True, withTolerance=False):
        """Calculate the mean effective operation hours of a single batch optionally with holidays.
        
        :returns: Mean operation hours of one batch
        :rtype:   Float
        """
        try:
            return self.getOperationHoursPerYear(withHolidays, withTolerance) / self.getNumberOfBatchesPerYear(withHolidays, withTolerance)
        except ZeroDivisionError:
            return 0.
        
    def getDurationHoursPerBatch(self, withHolidays=True, withTolerance=False):
        """Calulcate the mean nominal duration hours of a single batch optionally with holidays.
        
        :returns: Mean duration hours of one batch
        :rtype:   Float
        """
        yearlyIntervals = self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance)
        yearlyDuration = 0.
        for (start, stop, scale) in yearlyIntervals:
            yearlyDuration += stop - start + 1
        try:
            return yearlyDuration / self.getNumberOfBatchesPerYear(withHolidays, withTolerance)
        except ZeroDivisionError:
            return 0.
    
    def getDailyPartLoad(self, withHolidays=True, withTolerance=False):
        """Calulcate the mean part load factor between nominal and effective hours of a single batch optionally with holidays.
        
        :returns: Mean part load factor
        :rtype:   Float
        """
        return self.getOperationHoursPerBatch(withHolidays, withTolerance) / self.getDurationHoursPerBatch(withHolidays, withTolerance)
            
    def saveToDB(self, processId, withHolidays=True):
        """Store yearly load profile intervals and process schedule parameters (startup, inflow, outflow, tolerance, and holiday scale) to data base for a given process.
        
        Also stores process effective operation hour parameters and tolerance offsets. 
        
        Does not store the holidays, since they are global to the industry.
        
        :param processId: Data base ID of process to store the schedule for
        :type  processId: Integer
        :param withHolidays: Whether holiday periods are honored, only for operation hour parameters. Intervals are always stored ignoring holidays. 
        :type  withHolidays: Boolean
        
        :returns: nothing
        :exception einstein.modules.schedules.ProcessDataNotFoundError: No data on process found in DB (table qprocessdata).
        """
        # store process schedule parameters
        try:
            processDataRow = Status.DB.qprocessdata.QProcessData_ID[processId][0]
        except IndexError:
            raise ProcessDataNotFoundError
        processDataRow.update({"StartUpDuration"   : self.startup != None and self.startup or 'NULL'})
        processDataRow.update({"InFlowDuration"    : self.inflow != None and self.inflow  or 'NULL'})
        processDataRow.update({"OutFlowDuration"   : self.outflow != None and self.outflow or 'NULL'})
        processDataRow.update({"ScheduleTolerance" : self.tolerance})
        processDataRow.update({"HolidayScale"      : self.holidayScale})
        processDataRow.update({"HPerYearInFlow"    : self.getInflowHoursPerYear(withHolidays, withTolerance=False)})
        processDataRow.update({"HPerYearOutFlow"   : self.getOutflowHoursPerYear(withHolidays, withTolerance=False)})
        processDataRow.update({"HPerDayProc"       : self.getOperationHoursPerDay(withHolidays, withTolerance=False)})
        processDataRow.update({"HBatch"            : self.getDurationHoursPerBatch(withHolidays, withTolerance=False)})
        processDataRow.update({"NDaysProc"         : self.getNumberOfOperationDays(withHolidays, withTolerance=False)})
        processDataRow.update({"PartLoad"          : self.getDailyPartLoad(withHolidays, withTolerance=False)})

        # delete previously saved schedule intervals and tolerance offsets for given process
        deleteProcessScheduleFromDB(processId)
                
        # store schedule intervals without holidays and tolerance for given process
        for (start, stop, scale) in self.getYearlyProfileIntervals(withHolidays=False, withTolerance=False):
            Status.DB.process_schedules.insert({'startHour' : start,
                                                'stopHour'  : stop ,
                                                'scale'     : scale,
                                                'qprocessdata_QProcessData_ID' : processId})
            
        # store schedule tolerance offsets for given process
        for (cycle, offset) in enumerate(self.toleranceOffset):
            Status.DB.process_schedules_tolerance_offsets.insert({'qprocessdata_QProcessData_ID' : processId,
                                                                  'cycle'                        : cycle,
                                                                  'offset'                       : offset})
             
    def loadFromDB(self, processId):
        """Retrieve yearly profile, process schedule parameters, tolerance offsets, and industry holidays from data base for a given process.
        
        To load a detailed schedule for a process from the DB, construct an empty period schedule instance first.
        
        :returns: nothing
        :exception einstein.modules.schedules.ProcessDataNotFoundError: No data on process found in DB (table qprocessdata).
        :exception einstein.modules.schedules.InconsistentDataBaseError: Data base structure is inconsistent. This would be a bug.
        :exception einstein.modules.schedules.ScheduleNotFoundError: No detailed schedule for process found in DB.
        """
        # set process schedule parameters
        try:
            processDataRow = Status.DB.qprocessdata.QProcessData_ID[processId][0]
        except IndexError:
            raise ProcessDataNotFoundError
        self.startup = processDataRow.StartUpDuration
        self.inflow = processDataRow.InFlowDuration
        self.outflow = processDataRow.OutFlowDuration
        if processDataRow.ScheduleTolerance != None:
            self.tolerance = processDataRow.ScheduleTolerance
        if processDataRow.HolidayScale != None:
            self.holidayScale = processDataRow.HolidayScale
            
        # set process holidays to industry holidays
        try: # first industry holiday period
            holidayStart = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStart_1.column().pop()
            holidayStop = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStop_1.column().pop()
        except IndexError:
            raise InconsistentDataBaseError
        if holidayStart and holidayStop:
            self.addHolidays(holidayStart, holidayStop)
        try: # second industry holiday period
            holidayStart = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStart_2.column().pop()
            holidayStop = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStop_2.column().pop()
        except IndexError:
            raise InconsistentDataBaseError
        if holidayStart and holidayStop:
            self.addHolidays(holidayStart, holidayStop)
        try: # third industry holiday period
            holidayStart = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStart_3.column().pop()
            holidayStop = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStop_3.column().pop()
        except IndexError:
            raise InconsistentDataBaseError
        if holidayStart and holidayStop:
            self.addHolidays(holidayStart, holidayStop)

        # set schedule 
        self.clearSchedule()
        scheduleIntervalRows = Status.DB.process_schedules.qprocessdata_QProcessData_ID[processId]
        if not scheduleIntervalRows:
            raise ScheduleNotFoundError
        for scheduleInterval in scheduleIntervalRows:
            self.schedule[scheduleInterval['startHour']:scheduleInterval['stopHour'] + 1] = [scheduleInterval['scale']] * (scheduleInterval['stopHour'] - scheduleInterval['startHour'] + 1)

        # set tolerance offsets
        scheduleToleranceOffsetRows = Status.DB.process_schedules_tolerance_offsets.sql_select('qprocessdata_QProcessData_ID = %d ORDER BY cycle' % processId)
        self.updateToleranceOffset([row['offset'] for row in scheduleToleranceOffsetRows])
        
        return sum(self.getYearlyStartupProfile(withHolidays, withTolerance))
    
    def getOperationHoursPerBatch(self, withHolidays=True, withTolerance=False):
        """Calculate the mean effective operation hours of a single batch optionally with holidays.
        
        :returns: Mean operation hours of one batch
        :rtype:   Float
        """
        try:
            result = self.getOperationHoursPerYear(withHolidays, withTolerance) / float(self.getNumberOfBatchesPerYear(withHolidays, withTolerance))
        except ZeroDivisionError:
            return 0.
        if isnan(result) or isinf(result):
            return 0.
        return result
        
    def getOperationHoursPerInterval(self, withHolidays=True):
        """Calculate the mean effective operation hours of a single interval optionally with holidays.
        
        :returns: Mean operation hours of one batch
        :rtype:   Float
        """
        try:
            result = self.getOperationHoursPerYear(withHolidays) / float(self.getNumberOfIntervalsPerYear(withHolidays))
        except ZeroDivisionError:
            return 0.
        if isnan(result) or isinf(result):
            return 0.
        return result

        
    def getDurationHoursPerBatch(self, withHolidays=True, withTolerance=False):
        """Calulcate the mean nominal duration hours of a single batch optionally with holidays.
        
        :returns: Mean duration hours of one batch
        :rtype:   Float
        """
        yearlyIntervals = self.getYearlyProfileOnOffMeanIntervals(withHolidays, withTolerance)
        yearlyDuration = 0.
        for (start, stop, scale) in yearlyIntervals:
            yearlyDuration += stop - start + 1
        try:
            result = yearlyDuration / float(self.getNumberOfBatchesPerYear(withHolidays, withTolerance))
        except ZeroDivisionError:
            return 0.
        if isnan(result) or isinf(result):
            return 0.
        return result        
    
    def getDurationHoursPerInterval(self, withHolidays=True):
        """Calulcate the mean nominal duration hours of a single interval optionally with holidays.
        
        :returns: Mean duration hours of one batch
        :rtype:   Float
        """
        intervals = self.getYearlyIntervals(withHolidays)
        yearlyDuration = 0.
        for day in range(NDAYS):
            for (start, stop, scale) in intervals[day]:
                yearlyDuration += (timedelta(hours=stop.hour, minutes=stop.minute) - timedelta(hours=start.hour, minutes=start.minute)).seconds / 3600.
        try:
            result = yearlyDuration / float(self.getNumberOfIntervalsPerYear(withHolidays))
        except ZeroDivisionError:
            return 0.
        if isnan(result) or isinf(result):
            return 0.
        return result
    
    def getDailyPartLoad(self, withHolidays=True, withTolerance=False):
        """Calulcate the mean part load factor between nominal and effective hours of a single batch optionally with holidays.
        
        :returns: Mean part load factor
        :rtype:   Float
        """
        try:
            result = self.getOperationHoursPerBatch(withHolidays, withTolerance) / self.getDurationHoursPerBatch(withHolidays, withTolerance)
        except ZeroDivisionError:
            return 0.
        if isnan(result) or isinf(result):
            return 0.
        return result
        
    def getDailyIntervalPartLoad(self, withHolidays=True, withTolerance=False):
        """Calulcate the mean part load factor between nominal and effective hours of a single interval optionally with holidays.
        
        :returns: Mean part load factor
        :rtype:   Float
        """
        try:
            result = self.getOperationHoursPerInterval(withHolidays) / self.getDurationHoursPerInterval(withHolidays)
        except ZeroDivisionError:
            return 0.
        if isnan(result) or isinf(result):
            return 0.
        return result
            
    def saveToDB(self, processId, withHolidays=True):
        """Store yearly load profile intervals and process schedule parameters (startup, inflow, outflow, tolerance, and holiday scale) to data base for a given process.
        
        Also stores process effective operation hour parameters and tolerance offsets. 
        
        Does not store the holidays, since they are global to the industry.
        
        :param processId: Data base ID of process to store the schedule for
        :type  processId: Integer
        :param withHolidays: Whether holiday periods are honored, only for operation hour parameters. Intervals are always stored ignoring holidays. 
        :type  withHolidays: Boolean
        
        :returns: nothing
        :exception einstein.modules.schedules.ProcessDataNotFoundError: No data on process found in DB (table qprocessdata).
        """
        # store process schedule parameters
        try:
            processDataRow = Status.DB.qprocessdata.QProcessData_ID[processId][0]
        except IndexError:
            raise ProcessDataNotFoundError
        processDataRow.update({"StartUpDuration"   : self.startup != None and self.startup or 'NULL',
                               "InFlowDuration"    : self.inflow != None and self.inflow  or 'NULL',
                               "OutFlowDuration"   : self.outflow != None and self.outflow or 'NULL',
                               "ScheduleTolerance" : self.tolerance,
                               "HolidayScale"      : self.holidayScale,
                               "HPerYearInFlow"    : processDataRow.ProcType == 'batch' and self.getInflowHoursPerYear(withHolidays)  or self.getOperationHoursPerYear(withHolidays),
                               "HPerYearOutFlow"   : processDataRow.ProcType == 'batch' and self.getOutflowHoursPerYear(withHolidays) or self.getOperationHoursPerYear(withHolidays),
                               "HPerDayProc"       : self.getIntervalOperationHoursPerDay(withHolidays),
                               "HBatch"            : self.getDurationHoursPerInterval(withHolidays),
                               "NDaysProc"         : self.getNumberOfIntervalOperationDays(withHolidays),
                               "PartLoad"          : self.getDailyIntervalPartLoad(withHolidays)})

        # delete previously saved schedule intervals and tolerance offsets for given process
        deleteProcessScheduleFromDB(processId)
                
        # store schedule intervals without holidays and tolerance for given process
        sql = Status.SQL.cursor()
        valueString = ','.join(['(%d, %d, %f, %d)' % (start, stop, scale, processId) for (start, stop, scale) in self.getYearlyProfileIntervals(withHolidays=False, withTolerance=False)])
        if valueString:
            sqlString = 'INSERT DELAYED INTO process_schedules (startHour, stopHour, scale, qprocessdata_QProcessData_ID) VALUES %s' % valueString
            sql.execute(sqlString)
            
        # store schedule tolerance offsets for given process
        valueString = ','.join(['(%d, %d, %f)' % (processId, cycle, offset) for (cycle, offset) in enumerate(self.toleranceOffset)])
        if valueString:
            sqlString = 'INSERT DELAYED INTO process_schedules_tolerance_offsets (qprocessdata_QProcessData_ID, cycle, offset) VALUES %s' % valueString
            sql.execute(sqlString)
        sql.close()
             
    def loadFromDB(self, processId):
        """Retrieve yearly profile, process schedule parameters, tolerance offsets, and industry holidays from data base for a given process.
        
        To load a detailed schedule for a process from the DB, construct an empty period schedule instance first.
        
        :returns: nothing
        :exception einstein.modules.schedules.ProcessDataNotFoundError: No data on process found in DB (table qprocessdata).
        :exception einstein.modules.schedules.InconsistentDataBaseError: Data base structure is inconsistent. This would be a bug.
        :exception einstein.modules.schedules.ScheduleNotFoundError: No detailed schedule for process found in DB.
        """
        # set process schedule parameters
        try:
            processDataRow = Status.DB.qprocessdata.QProcessData_ID[processId][0]
        except IndexError:
            raise ProcessDataNotFoundError
        self.startup = processDataRow.StartUpDuration
        self.inflow = processDataRow.InFlowDuration
        self.outflow = processDataRow.OutFlowDuration
        if processDataRow.ScheduleTolerance != None:
            self.tolerance = processDataRow.ScheduleTolerance
        if processDataRow.HolidayScale != None:
            self.holidayScale = processDataRow.HolidayScale
            
        # set process holidays to industry holidays
        try: # first industry holiday period
            holidayStart = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStart_1.column().pop()
            holidayStop = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStop_1.column().pop()
        except IndexError:
            raise InconsistentDataBaseError
        if holidayStart and holidayStop:
            self.addHolidays(holidayStart, holidayStop)
        try: # second industry holiday period
            holidayStart = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStart_2.column().pop()
            holidayStop = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStop_2.column().pop()
        except IndexError:
            raise InconsistentDataBaseError
        if holidayStart and holidayStop:
            self.addHolidays(holidayStart, holidayStop)
        try: # third industry holiday period
            holidayStart = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStart_3.column().pop()
            holidayStop = Status.DB.questionnaire.Questionnaire_ID[processDataRow.Questionnaire_id].NoProdStop_3.column().pop()
        except IndexError:
            raise InconsistentDataBaseError
        if holidayStart and holidayStop:
            self.addHolidays(holidayStart, holidayStop)

        # set schedule 
        self.clearSchedule()
        scheduleIntervalRows = Status.DB.process_schedules.qprocessdata_QProcessData_ID[processId]
        if not scheduleIntervalRows:
            raise ScheduleNotFoundError
        for scheduleInterval in scheduleIntervalRows:
            self.schedule[scheduleInterval['startHour']:scheduleInterval['stopHour'] + 1] = [scheduleInterval['scale']] * (scheduleInterval['stopHour'] - scheduleInterval['startHour'] + 1)

        # set tolerance offsets
        scheduleToleranceOffsetRows = Status.DB.process_schedules_tolerance_offsets.sql_select('qprocessdata_QProcessData_ID = %d ORDER BY cycle' % processId)
        self.updateToleranceOffset([row['offset'] for row in scheduleToleranceOffsetRows])
        
