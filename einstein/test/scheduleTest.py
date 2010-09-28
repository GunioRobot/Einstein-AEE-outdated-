'''
Created on 18.11.2009

@author: david
'''

import gettext
gettext.install("einstein", "../GUI/locale", unicode=False)
language = gettext.translation("einstein", "../GUI/locale", languages=['en'])
language.install()

import unittest
import MySQLdb
import einstein.GUI.pSQL
import einstein.modules.profiles  as profiles
import einstein.modules.schedules as schedules
from einstein.GUI.status        import Status
from math                       import *
from random                     import *
from datetime                   import *
from einstein.modules.constants import *

dbHost = "localhost"
dbUser = "root"
dbPass = "root"
dbBase = "einstein"

class TestScheduleProfiles(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass


    def testAddConstantPeriodProfile(self):
        """Schedule unit load during complete year"""
        constantWeeklyProfile = profiles.WeeklyProfile("constantWeeklyProfile")
        constantWeeklyProfile.addInterval(time(0, 0), time(0, 0), 100)
        constantWeeklyProfile.setMonday(True)
        constantWeeklyProfile.setTuesday(True)
        constantWeeklyProfile.setWednesday(True)
        constantWeeklyProfile.setThursday(True)
        constantWeeklyProfile.setFriday(True)
        constantWeeklyProfile.setSaturday(True)
        constantWeeklyProfile.setSunday(True)
        periodSchedule = schedules.PeriodSchedule("testConstantSchedule")
        periodSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=constantWeeklyProfile)
        constantSchedule = periodSchedule.getYearlyProfile()
        for h in range(int(YEAR)):
            self.failUnlessEqual(1., constantSchedule[h])
    
    def testAddScaledConstantPeriodProfile(self):
        """Schedule scaled load during complete year"""
        weeklyLoad = 50
        periodLoad = 25
        constantWeeklyProfile = profiles.WeeklyProfile("constantWeeklyProfile")
        constantWeeklyProfile.addInterval(time(0, 0), time(0, 0), weeklyLoad)
        constantWeeklyProfile.setMonday(True)
        constantWeeklyProfile.setTuesday(True)
        constantWeeklyProfile.setWednesday(True)
        constantWeeklyProfile.setThursday(True)
        constantWeeklyProfile.setFriday(True)
        constantWeeklyProfile.setSaturday(True)
        constantWeeklyProfile.setSunday(True)
        periodSchedule = schedules.PeriodSchedule("testConstantSchedule")
        periodSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=periodLoad, profile=constantWeeklyProfile)
        constantSchedule = periodSchedule.getYearlyProfile()
        for h in range(int(YEAR)):
            self.failUnlessEqual((weeklyLoad * .01) * (periodLoad * .01), constantSchedule[h])
            
    def testAddScaledConstantHolidayPeriodProfile(self):
        """Schedule scaled load during complete year except holidays"""
        weeklyLoad = 50
        periodLoad = 25
        constantWeeklyProfile = profiles.WeeklyProfile("constantWeeklyProfile")
        constantWeeklyProfile.addInterval(time(0, 0), time(0, 0), weeklyLoad)
        constantWeeklyProfile.setMonday(True)
        constantWeeklyProfile.setTuesday(True)
        constantWeeklyProfile.setWednesday(True)
        constantWeeklyProfile.setThursday(True)
        constantWeeklyProfile.setFriday(True)
        constantWeeklyProfile.setSaturday(True)
        constantWeeklyProfile.setSunday(True)
        periodSchedule = schedules.PeriodSchedule("testConstantSchedule", holidayScale=0.)
        periodSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=periodLoad, profile=constantWeeklyProfile)
        periodSchedule.addHolidays(date(2009, 2, 1), date(2009, 2, 28))
        constantSchedule = periodSchedule.getYearlyProfile(withHolidays=True)
        holidayStartHour = 744
        holidayStopHour  = 1415
        for h in range(int(YEAR)):
            if holidayStartHour <= h and h <= holidayStopHour:
                self.failUnlessEqual(0., constantSchedule[h])
            else:
                self.failUnlessEqual((weeklyLoad * .01) * (periodLoad * .01), constantSchedule[h])    
            
    def testSteppedConstantPeriodProfile(self):
        """Schedule unit load every second day during the year"""
        constantWeeklyProfile = profiles.WeeklyProfile('constantWeeklyProfile')
        constantWeeklyProfile.addInterval(time(0, 0), time(0, 0), 100)
        constantWeeklyProfile.setMonday(True)
        constantWeeklyProfile.setTuesday(True)
        constantWeeklyProfile.setWednesday(True)
        constantWeeklyProfile.setThursday(True)
        constantWeeklyProfile.setFriday(True)
        constantWeeklyProfile.setSaturday(True)
        constantWeeklyProfile.setSunday(True)
        periodSchedule = schedules.PeriodSchedule("testConstantSchedule")
        periodSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=2, scale=100, profile=constantWeeklyProfile)
        constantSchedule = periodSchedule.getYearlyProfile()
        dayHours = 1     # count hour of day from 1 to 24
        runOnDay = True  # always run on first day
        for h in range(int(YEAR)):
            if runOnDay:
                self.failUnlessEqual(1., constantSchedule[h])
            else:
                self.failUnlessEqual(0., constantSchedule[h])
            if dayHours < 24:
                dayHours += 1
            else:
                dayHours  = 1
                runOnDay  = not runOnDay
                
    def testEmptyProfileIntervals(self):
        """Empty schedule has no profile intervals"""
        emptySchedule = schedules.PeriodSchedule("emptySchedule")
        self.failUnlessEqual([], emptySchedule.getYearlyProfileIntervals())
    
    def testConstantProfileIntervals(self):
        """Constant schedule during complete year has one profile interval"""
        constantSchedule = schedules.PeriodSchedule("constantSchedule", schedule=([1.] * int(YEAR)))
        self.failUnlessEqual([(0, 8759, 1.)], constantSchedule.getYearlyProfileIntervals())
        
    def testBatchProfileIntervals(self):
        """Batch schedule with one cycle per day has 365 intervals per year"""
        batchProfile  = profiles.WeeklyProfile("BatchWeeklyProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        batchProfile.addInterval(time(9,0), time(0,0), 100)
        batchSchedule = schedules.PeriodSchedule("batchSchedule")
        batchSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=batchProfile)
        self.failUnlessEqual(365, len(batchSchedule.getYearlyProfileIntervals()))
        
    def testProfileIntervalHoursInclusive(self):
        """Interval start and stop hours are inclusive"""
        batchProfile  = profiles.WeeklyProfile("BatchWeeklyProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        batchProfile.addInterval(time(9,0), time(0,0), 100)
        batchSchedule = schedules.PeriodSchedule("batchSchedule")
        batchSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=batchProfile)
        inclusiveStartDayHour = 9
        inclusiveStopDayHour  = 23
        for (start, stop, scale) in batchSchedule.getYearlyProfileIntervals():
            self.failUnlessEqual(inclusiveStartDayHour, start % 24)
            self.failUnlessEqual(inclusiveStopDayHour,  stop  % 24)
            self.failUnlessEqual(1., scale)
            
    def testProfileOnOffMeanIntervals(self):
        """On/off interval profile with mean load"""
        stepUpProfile = profiles.WeeklyProfile("stepUpProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        stepUpProfile.addInterval(time(10,0), time(12,0),  50)
        stepUpProfile.addInterval(time(12,0), time(14,0), 100)
        stepUpSchedule = schedules.PeriodSchedule("stepUpSchedule")
        stepUpSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=stepUpProfile)
        inclusiveOnDayHour  = 10
        inclusiveOffDayHour = 13
        for (start, stop, scale) in stepUpSchedule.getYearlyProfileOnOffMeanIntervals():
            self.failUnlessEqual(inclusiveOnDayHour,  start % 24)
            self.failUnlessEqual(inclusiveOffDayHour, stop  % 24)
            self.failUnlessEqual(0.75, scale)
            
    def testProfileOnOffUnitIntervals(self):
        """On/off interval profile with unit load"""
        stepUpProfile = profiles.WeeklyProfile("stepUpProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        stepUpProfile.addInterval(time(10,0), time(12,0),  50)
        stepUpProfile.addInterval(time(12,0), time(14,0), 100)
        stepUpSchedule = schedules.PeriodSchedule("stepUpSchedule")
        stepUpSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=stepUpProfile)
        inclusiveOnDayHour  = 10
        inclusiveOffDayHour = 13
        for (start, stop, scale) in stepUpSchedule.getYearlyProfileOnOffUnitIntervals():
            self.failUnlessEqual(inclusiveOnDayHour,  start % 24)
            self.failUnlessEqual(inclusiveOffDayHour, stop  % 24)
            self.failUnlessEqual(1., scale)
            
    def testWeeklyPeriodProfile(self):
        """Weekly profile of period contains 168 hours"""
        constantSchedule = schedules.PeriodSchedule("constantSchedule", schedule=([1.] * int(YEAR)))
        self.failUnlessEqual(168, len(constantSchedule.getWeeklyProfile(date(2010,1,28))))
    
    def testDefaultStartupProfile(self):
        """Startup profile defaults to fractional time of operation profile"""
        batchProfile  = profiles.WeeklyProfile("BatchWeeklyProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        batchProfile.addInterval(time(9,0), time(11,0), 100)
        batchSchedule = schedules.PeriodSchedule("batchSchedule")
        batchSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=batchProfile)
        startupProfile = batchSchedule.getYearlyStartupProfile()
        for day in range(365):
            self.failUnlessEqual(2*schedules.DEFAULTCHARGETIME, startupProfile[int(DAY)*day + 9])
        
    def testDefaultInflowProfile(self):
        """Inflow profile defaults to fractional time of operation profile"""
        batchProfile  = profiles.WeeklyProfile("BatchWeeklyProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        batchProfile.addInterval(time(9,0), time(11,0), 100)
        batchSchedule = schedules.PeriodSchedule("batchSchedule")
        batchSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=batchProfile)
        inflowProfile = batchSchedule.getYearlyInflowProfile()
        for day in range(365):
            self.failUnlessEqual(2*schedules.DEFAULTCHARGETIME, inflowProfile[int(DAY)*day + 9])

    def testDefaultOutflowProfile(self):
        """Outflow profile defaults to fractional time of operation profile"""
        batchProfile  = profiles.WeeklyProfile("BatchWeeklyProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        batchProfile.addInterval(time(9,0), time(11,0), 100)
        batchSchedule = schedules.PeriodSchedule("batchSchedule")
        batchSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=batchProfile)
        outflowProfile = batchSchedule.getYearlyOutflowProfile()
        for day in range(365):
            self.failUnlessEqual(2*schedules.DEFAULTCHARGETIME, outflowProfile[int(DAY)*day + 11])
            
    def testContinuousStartupProfile(self):
        """Startup profile of continuous process has unit load"""
        stepUpProfile = profiles.WeeklyProfile("stepUpProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        stepUpProfile.addInterval(time(10,0), time(12,0),  50)
        stepUpProfile.addInterval(time(12,0), time(14,0), 100)
        stepUpSchedule = schedules.PeriodSchedule("stepUpSchedule", startup=1.7)
        stepUpSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=stepUpProfile)
        inclusiveOnDayHour  = 10
        unitLoad = 1. / (stepUpSchedule.startup * 365.)
        fracLoad = (1. * fmod(stepUpSchedule.startup, 1) ) / (stepUpSchedule.startup * 365.)
        for (hour, scale) in enumerate(stepUpSchedule.getYearlyContinuousStartupProfile()):
            if   inclusiveOnDayHour <= (hour % 24) and (hour % 24) < inclusiveOnDayHour + int(stepUpSchedule.startup):
                self.failUnlessAlmostEqual(unitLoad, scale)
            elif (hour % 24) == inclusiveOnDayHour + int(stepUpSchedule.startup):
                self.failUnlessAlmostEqual(fracLoad, scale) 
            else:
                self.failUnlessEqual(0., scale)
    
    def testContinuousInflowProfile(self):
        """Inflow profile of continuous process equals operation profile"""
        stepUpProfile = profiles.WeeklyProfile("stepUpProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        stepUpProfile.addInterval(time(10,0), time(12,0),  50)
        stepUpProfile.addInterval(time(12,0), time(14,0), 100)
        stepUpSchedule = schedules.PeriodSchedule("stepUpSchedule", inflow=1.7)
        stepUpSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=stepUpProfile)
        self.failUnlessEqual(stepUpSchedule.getYearlyContinuousOperationProfile(), stepUpSchedule.getYearlyContinuousInflowProfile())

    def testContinuousOutflowProfile(self):
        """Outflow profile of continuous process equals operation profile"""
        stepUpProfile = profiles.WeeklyProfile("stepUpProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        stepUpProfile.addInterval(time(10,0), time(12,0),  50)
        stepUpProfile.addInterval(time(12,0), time(14,0), 100)
        stepUpSchedule = schedules.PeriodSchedule("stepUpSchedule", outflow=1.7)
        stepUpSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=stepUpProfile)
        self.failUnlessEqual(stepUpSchedule.getYearlyContinuousOperationProfile(), stepUpSchedule.getYearlyContinuousOutflowProfile())

    def testBatchOperationProfile(self):
        """Operation profiles of continuous and batch processes are the same"""
        stepUpProfile = profiles.WeeklyProfile("stepUpProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        stepUpProfile.addInterval(time(10,0), time(12,0),  50)
        stepUpProfile.addInterval(time(12,0), time(14,0), 100)
        stepUpSchedule = schedules.PeriodSchedule("stepUpSchedule")
        stepUpSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=stepUpProfile)
        self.failUnlessEqual(stepUpSchedule.getYearlyContinuousOperationProfile(), stepUpSchedule.getYearlyBatchOperationProfile())

    def testBatchStartupProfile(self):
        """Startup profile of batch process has unit load"""
        stepUpProfile = profiles.WeeklyProfile("stepUpProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        stepUpProfile.addInterval(time(10,0), time(12,0),  50)
        stepUpProfile.addInterval(time(12,0), time(14,0), 100)
        stepUpSchedule = schedules.PeriodSchedule("stepUpSchedule", startup=1.7)
        stepUpSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=stepUpProfile)
        inclusiveOnDayHour  = 10
        unitLoad = 1. / (stepUpSchedule.startup * 365.)
        fracLoad = (1. * fmod(stepUpSchedule.startup, 1)) / (stepUpSchedule.startup * 365.)
        for (hour, scale) in enumerate(stepUpSchedule.getYearlyBatchStartupProfile()):
            if   inclusiveOnDayHour <= (hour % 24) and (hour % 24) < inclusiveOnDayHour + int(stepUpSchedule.startup):
                self.failUnlessAlmostEqual(unitLoad, scale)
            elif (hour % 24) == inclusiveOnDayHour + int(stepUpSchedule.startup):
                self.failUnlessAlmostEqual(fracLoad, scale) 
            else:
                self.failUnlessEqual(0., scale)

    def testBatchInflowProfile(self):
        """Inflow profile of batch process has mean load"""
        stepUpProfile = profiles.WeeklyProfile("stepUpProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        stepUpProfile.addInterval(time(10,0), time(12,0),  50)
        stepUpProfile.addInterval(time(12,0), time(14,0), 100)
        stepUpSchedule = schedules.PeriodSchedule("stepUpSchedule", inflow=1.7)
        stepUpSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=stepUpProfile)
        inclusiveOnDayHour  = 10
        # for normalized inflow profile meanLoad == unitLoad
        meanLoad = 0.75 / (0.75 * stepUpSchedule.inflow * 365.)
        fracLoad = (0.75 * fmod(stepUpSchedule.inflow, 1)) / (0.75 * stepUpSchedule.inflow * 365.)
        for (hour, scale) in enumerate(stepUpSchedule.getYearlyBatchInflowProfile()):
            if   inclusiveOnDayHour <= (hour % 24) and (hour % 24) < inclusiveOnDayHour + int(stepUpSchedule.inflow):
                self.failUnlessAlmostEqual(meanLoad, scale)
            elif (hour % 24) == inclusiveOnDayHour + int(stepUpSchedule.inflow):
                self.failUnlessAlmostEqual(fracLoad, scale) 
            else:
                self.failUnlessEqual(0., scale)
    
    def testBatchOutflowProfile(self):
        """Outflow profile of batch process has mean load"""
        stepUpProfile = profiles.WeeklyProfile("stepUpProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        stepUpProfile.addInterval(time(10,0), time(12,0),  50)
        stepUpProfile.addInterval(time(12,0), time(14,0), 100)
        stepUpSchedule = schedules.PeriodSchedule("stepUpSchedule", outflow=1.7)
        stepUpSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=stepUpProfile)
        inclusiveOffDayHour  = 13
        # for normalized outflow profile meanLoad == unitLoad
        meanLoad = 0.75 / (0.75 * stepUpSchedule.outflow * 365.)
        fracLoad = (0.75 * fmod(stepUpSchedule.outflow, 1)) / (0.75 * stepUpSchedule.outflow * 365.)
        for (hour, scale) in enumerate(stepUpSchedule.getYearlyBatchOutflowProfile()):
            if   inclusiveOffDayHour + 1 <= (hour % 24) and (hour % 24) < inclusiveOffDayHour + 1 + int(stepUpSchedule.outflow):
                self.failUnlessAlmostEqual(meanLoad, scale)
            elif (hour % 24) == inclusiveOffDayHour + 1 + int(stepUpSchedule.outflow):
                self.failUnlessAlmostEqual(fracLoad, scale) 
            else:
                self.failUnlessEqual(0., scale)
                
    def testDurationHoursPerBatch(self):
        """Duration hours per batch do not scale"""
        stepUpProfile = profiles.WeeklyProfile("stepUpProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        stepUpProfile.addInterval(time(10,0), time(12,0),  50)
        stepUpProfile.addInterval(time(12,0), time(14,0), 100)
        stepUpSchedule = schedules.PeriodSchedule("stepUpSchedule")
        stepUpSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=stepUpProfile)
        self.failUnlessEqual(4., stepUpSchedule.getDurationHoursPerBatch())
        
    def testPartLoadFactor(self):
        """Part load factor contains daily scaling"""
        batchProfile = profiles.WeeklyProfile("batchProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        batchProfile.addInterval(time(10,0), time(12,0), 100)
        batchProfile.addInterval(time(13,0), time(16,0), 100)
        batchSchedule = schedules.PeriodSchedule("batchSchedule")
        batchSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=50, profile=batchProfile)
        self.failUnlessEqual(0.5, batchSchedule.getDailyPartLoad())
        
    def testToleranceYearlyProfile(self):
        """Random tolerance shift is applied to each cycle"""
        batchProfile = profiles.WeeklyProfile("batchProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        batchProfile.addInterval(time(10,0), time(12,0), 100)
        batchSchedule = schedules.PeriodSchedule("batchSchedule", tolerance=0.2)
        batchSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=50, profile=batchProfile)
        batchSchedule.updateToleranceOffset()
        toleranceProfile = batchSchedule.getYearlyProfile(withTolerance=True)
        for day in range(365):
            if batchSchedule.toleranceOffset[day] > 0: # shift right
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 9] , 0.)
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 10], 0.5 * (1. - batchSchedule.toleranceOffset[day]))
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 11], 0.5)
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 12], 0.5 * batchSchedule.toleranceOffset[day])
            elif batchSchedule.toleranceOffset[day] < 0: # shift left
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 9] , 0.5 * abs(batchSchedule.toleranceOffset[day]))
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 10], 0.5)
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 11], 0.5 * (1. - abs(batchSchedule.toleranceOffset[day])))
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 12], 0.)
            else: # no shift
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 9] , 0.)
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 10], 0.5)
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 11], 0.5)
                self.failUnlessEqual(toleranceProfile[int(DAY)*day + 12], 0.)
                
    def testToleranceNoOverlap(self):
        """No overlap is introduced by random tolerance shift of cycles"""
        batchProfile = profiles.WeeklyProfile("batchProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        batchProfile.addInterval(time(10,0), time(12,0), 100)
        batchProfile.addInterval(time(13,0), time(14,0), 100)
        batchSchedule = schedules.PeriodSchedule("batchSchedule", tolerance=2.0)
        batchSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=batchProfile)
        toleranceOffset = []
        for cycle in range(2*365):
            toleranceOffset.append(pow(-1, cycle % 2))
        batchSchedule.updateToleranceOffset(toleranceOffset)
        toleranceProfile = batchSchedule.getYearlyProfile(withTolerance=True)
        for day in range(365):
            self.failUnlessEqual(0.0, toleranceProfile[int(DAY)*day + 10])
            self.failUnlessEqual(1.0, toleranceProfile[int(DAY)*day + 11])
            self.failUnlessEqual(1.0, toleranceProfile[int(DAY)*day + 12])
            self.failUnlessEqual(0.5, toleranceProfile[int(DAY)*day + 13])
            self.failUnlessEqual(0.5, toleranceProfile[int(DAY)*day + 14])
            
    def testToleranceYearWrap(self):
        """Random tolerance shift wraps around year bounds"""
        batchProfile = profiles.WeeklyProfile("batchProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        batchProfile.addInterval(time(1,0), time(0,0), 100)
        batchSchedule = schedules.PeriodSchedule("batchSchedule", tolerance=1.0)
        batchSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=batchProfile)
        batchSchedule.updateToleranceOffset([1] * 365)
        toleranceProfile = batchSchedule.getYearlyProfile(withTolerance=True)
        for day in range(365):
            self.failUnlessEqual(1.0, toleranceProfile[int(DAY)*day])
            
    def testToleranceZero(self):
        """Zero tolerance equals original profile"""
        batchProfile = profiles.WeeklyProfile("batchProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        batchProfile.addInterval(time(1,0), time(0,0), 100)
        batchSchedule = schedules.PeriodSchedule("batchSchedule", tolerance=0.0)
        batchSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=batchProfile)
        batchSchedule.updateToleranceOffset()
        toleranceProfile = batchSchedule.getYearlyProfile(withTolerance=True)
        originalProfile  = batchSchedule.getYearlyProfile(withTolerance=False)
        for hour in range(int(YEAR)):
            self.failUnlessEqual(toleranceProfile[hour], originalProfile[hour])
            
    def testToleranceNumberOfBatchesPerYear(self):
        """Tolerance shift keeps number of batches constant"""
        batchProfile = profiles.WeeklyProfile("batchProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        batchProfile.addInterval(time(10,0), time(12,0), 100)
        batchSchedule = schedules.PeriodSchedule("batchSchedule", tolerance=2.0)
        batchSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=batchProfile)
        batchSchedule.updateToleranceOffset()
        self.failUnlessEqual(365., batchSchedule.getNumberOfBatchesPerYear(withTolerance=True))
                        
class TestScheduleParameters(unittest.TestCase):
    def setUp(self):
        random = Random()
        random.seed()
        randomSchedule = []
        for h in range(int(YEAR)): # gaussian random schedule
            randomSchedule.append(random.uniform(0., 1.5))
        for day in range(365): # do not run in first and last two hours of each day
            randomSchedule[int(DAY) * day]      = 0.
            randomSchedule[int(DAY) * day + 1]  = 0.
            randomSchedule[int(DAY) * day + 22] = 0.
            randomSchedule[int(DAY) * day + 23] = 0.
        self.periodSchedule = schedules.PeriodSchedule('testScheduleParameters',
                                                       tolerance=0.,
                                                       holidayScale=0.,
                                                       holidays=[],
                                                       schedule=randomSchedule)
        self.toleranceSchedule = schedules.PeriodSchedule('testToleranceScheduleParameters',
                                                          tolerance=0.5,
                                                          holidayScale=0.,
                                                          holidays=[],
                                                          schedule=randomSchedule)
        self.toleranceSchedule.updateToleranceOffset()
        self.UPHDotNominal       = 5.
        self.timeStep            = .5
        self.f                   = self.periodSchedule.getYearlyProfile()
        self.fav                 = self.periodSchedule.getYearlyContinuousOperationProfile()
        self.fTolerance          = self.toleranceSchedule.getYearlyProfile(withTolerance=True)
        self.favTolerance        = self.toleranceSchedule.getYearlyContinuousOperationProfile(withTolerance=True)
        self.fInt                = sum(self.f)   * self.timeStep
        self.fIntTolerance       = sum(self.fTolerance)   * self.timeStep
        self.favInt              = sum(self.fav) * self.timeStep
        self.favIntTolerance     = sum(self.favTolerance) * self.timeStep
        self.UPHDotReal          = [self.f[h] * self.UPHDotNominal for h in range(int(YEAR))]
        self.UPHDotRealTolerance = [self.fTolerance[h] * self.UPHDotNominal for h in range(int(YEAR))]
        self.UPHReal             = sum(self.UPHDotReal) * self.timeStep
        self.UPHRealTolerance    = sum(self.UPHDotRealTolerance) * self.timeStep
        
    def testPartLoad(self):
        """h_{day} = PartLoad * h_{cycle} * n_{cycle,day}"""
        self.failUnlessAlmostEqual(self.periodSchedule.getOperationHoursPerBatch(), self.periodSchedule.getDailyPartLoad() * self.periodSchedule.getDurationHoursPerBatch())
        
    def testPartLoadTolerance(self):
        """h_{day} = PartLoad * h_{cycle} * n_{cycle,day} after tolerance shift"""
        self.failUnlessAlmostEqual(self.toleranceSchedule.getOperationHoursPerBatch(withTolerance=True), self.toleranceSchedule.getDailyPartLoad(withTolerance=True) * self.toleranceSchedule.getDurationHoursPerBatch(withTolerance=True))
        
    def testPartLoadToleranceInvariant(self):
        """PartLoad is NOT invariant over tolerance shift"""
        self.failUnlessEqual(self.toleranceSchedule.getDailyPartLoad(withTolerance=False), self.periodSchedule.getDailyPartLoad(withTolerance=True))

    def testNBatch(self):
        """n_{cycle} = n_{cycle,day} \\times n_{days}"""
        self.failUnlessEqual(self.periodSchedule.getNumberOfBatchesPerYear(), self.periodSchedule.getNumberOfBatchesPerDay()*self.periodSchedule.getNumberOfOperationDays())
    
    def testNBatchTolerance(self):
        """n_{cycle} = n_{cycle,day} \\times n_{days} after tolerance shift"""
        self.failUnlessEqual(self.toleranceSchedule.getNumberOfBatchesPerYear(withTolerance=True), self.toleranceSchedule.getNumberOfBatchesPerDay(withTolerance=True)*self.toleranceSchedule.getNumberOfOperationDays(withTolerance=True))    

    def testNBatchToleranceInvariant(self):
        """n_{cycle} is invariant over tolerance shift"""
        self.failUnlessEqual(self.toleranceSchedule.getNumberOfBatchesPerYear(withTolerance=True), self.periodSchedule.getNumberOfBatchesPerYear(withTolerance=True))    
    
    def testHBatch(self):
        """h_{cycle} = \\frac{h_{year}}{n_{cycles}}"""
        self.failUnlessEqual(self.periodSchedule.getOperationHoursPerBatch(), self.periodSchedule.getOperationHoursPerYear()/self.periodSchedule.getNumberOfBatchesPerYear())
        
    def testHBatchTolerance(self):
        """h_{cycle} = \\frac{h_{year}}{n_{cycles}} after tolerance shift"""
        self.failUnlessEqual(self.toleranceSchedule.getOperationHoursPerBatch(withTolerance=True), self.toleranceSchedule.getOperationHoursPerYear(withTolerance=True)/self.toleranceSchedule.getNumberOfBatchesPerYear(withTolerance=True))

    def testHBatchToleranceInvariant(self):
        """h_{cycle} is invariant over tolerance shift"""
        self.failUnlessAlmostEqual(self.toleranceSchedule.getOperationHoursPerBatch(withTolerance=True), self.periodSchedule.getOperationHoursPerBatch(withTolerance=True))

    def testHPerDay(self):
        """h_{day} = \\frac{h_{year}}{n_{days}}"""
        self.failUnlessEqual(self.periodSchedule.getOperationHoursPerDay(), self.periodSchedule.getOperationHoursPerYear()/self.periodSchedule.getNumberOfOperationDays())

    def testHPerDayTolerance(self):
        """h_{day} = \\frac{h_{year}}{n_{days}} after tolerance shift"""
        self.failUnlessEqual(self.toleranceSchedule.getOperationHoursPerDay(withTolerance=True), self.toleranceSchedule.getOperationHoursPerYear(withTolerance=True)/self.toleranceSchedule.getNumberOfOperationDays(withTolerance=True))

    def testHPerDayToleranceInvariant(self):
        """h_{day} is invariant over tolerance shift"""
        self.failUnlessAlmostEqual(self.toleranceSchedule.getOperationHoursPerDay(withTolerance=True), self.periodSchedule.getOperationHoursPerDay(withTolerance=True))
        
    def testHPerYearFint(self):
        """h_{year} \\times \Delta t = \\int f(t)dt"""
        self.failUnlessEqual(self.fInt, self.timeStep * self.periodSchedule.getOperationHoursPerYear())

    def testHPerYearFintTolerance(self):
        """h_{year} \\times \Delta t = \\int f(t)dt after tolerance shift"""
        self.failUnlessEqual(self.fIntTolerance, self.timeStep * self.toleranceSchedule.getOperationHoursPerYear(withTolerance=True))
        
    def testHPerYearFintToleranceInvariant(self):
        """\\int f(t)dt is invariant over tolerance shift"""
        self.failUnlessAlmostEqual(self.fIntTolerance, self.fInt)        
        
    def testFUPH(self):
        """f(t) \\times UPH_{dot}^{nom}(t) = UPH_{dot}(t)"""
        for t in range(int(YEAR)):
            self.failUnlessEqual(self.UPHDotReal[t], self.f[t] * self.UPHDotNominal)
            
    def testFUPHTolerance(self):
        """f(t) \\times UPH_{dot}^{nom}(t) = UPH_{dot}(t) after tolerance shift"""
        for t in range(int(YEAR)):
            self.failUnlessEqual(self.UPHDotRealTolerance[t], self.fTolerance[t] * self.UPHDotNominal)

    def testFIntUPH(self):
        """\\int f(t)dt = \\frac{\\int UPH_{dot}^{real}(t)dt}{UPH_{dot}^{nom}}"""
        self.failUnlessAlmostEqual(self.UPHReal/self.UPHDotNominal, self.fInt)
    
    def testFIntUPHTolerance(self):
        """\\int f(t)dt = \\frac{\\int UPH_{dot}^{real}(t)dt}{UPH_{dot}^{nom}} after tolerance shift"""
        self.failUnlessAlmostEqual(self.UPHRealTolerance/self.UPHDotNominal, self.fIntTolerance)

    def testFIntUPHToleranceInvariant(self):
        """\\int UPH_{dot}^{real}(t)dt is invariant over tolerance shift"""
        self.failUnlessAlmostEqual(self.UPHRealTolerance, self.UPHReal)
        
    def testHPerYearUPH(self):
        """h_{year} = \\frac{\\int UPH_{dot}^{real}(t)dt}{UPH_{dot}^{nom}}"""
        self.failUnlessAlmostEqual(self.UPHReal/self.UPHDotNominal, self.timeStep * self.periodSchedule.getOperationHoursPerYear())

    def testHPerYearUPHTolerance(self):
        """h_{year} = \\frac{\\int UPH_{dot}^{real}(t)dt}{UPH_{dot}^{nom}} after tolerance shift"""
        self.failUnlessAlmostEqual(self.UPHRealTolerance/self.UPHDotNominal, self.timeStep * self.toleranceSchedule.getOperationHoursPerYear(withTolerance=True))
        
    def testFavNormal(self):
        """\\sum_{t=0}^{8769} fav(t) = 1"""
        self.failUnlessAlmostEqual(1, sum(self.fav))

    def testFavNormalTolerance(self):
        """\\sum_{t=0}^{8769} fav(t) = 1 after tolerance shift"""
        self.failUnlessAlmostEqual(1, sum(self.favTolerance))
        
    def testFavUPH(self):
        """fav(t) \\times \\frac{\\int UPH_{dot}^{real}(t)dt}{\Delta t} = UPH_{dot}^{nom}(t)"""
        for t in range(int(YEAR)):
            self.failUnlessAlmostEqual(self.UPHDotReal[t], self.fav[t] * (self.UPHReal / self.timeStep))

    def testFavUPHTolerance(self):
        """fav(t) \\times \\frac{\\int UPH_{dot}^{real}(t)dt}{\Delta t} = UPH_{dot}^{nom}(t) after tolerance shift"""
        for t in range(int(YEAR)):
            self.failUnlessAlmostEqual(self.UPHDotRealTolerance[t], self.favTolerance[t] * (self.UPHRealTolerance / self.timeStep))
        
    def testFIntUPHFavIntUPH(self):
        """UPH_{dot}^{nom} \\times \\int f(t)dt = \\frac{\\int UPH_{dot}^{real}(t)dt}{\Delta t} \\times \\int fav(t)dt"""
        self.failUnlessAlmostEqual(self.UPHDotNominal * self.fInt, (self.UPHReal/self.timeStep) * self.favInt)

    def testFIntUPHFavIntUPHTolerance(self):
        """UPH_{dot}^{nom} \\times \\int f(t)dt = \\frac{\\int UPH_{dot}^{real}(t)dt}{\Delta t} \\times \\int fav(t)dt after tolerance shift"""
        self.failUnlessAlmostEqual(self.UPHDotNominal * self.fIntTolerance, (self.UPHRealTolerance/self.timeStep) * self.favIntTolerance)
        
class TestScheduleDB(unittest.TestCase):
    def setUp(self):
        connection = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbBase)
        cursor     = connection.cursor(MySQLdb.cursors.DictCursor)
        status     = Status("testing")
        Status.DB  = einstein.GUI.pSQL.pSQL(connection, 'einstein')
        
    def testExportWeeklyProfilesFromDB(self):
        print profiles.exportWeeklyProfilesFromDB()
        
    def testExportProcessPeriodsFromDB(self):
        print schedules.exportProcessPeriodsFromDB(4630)
        
    def testSaveToDB(self):
        self.fail("not tested")
        
    def testLoadFromDB(self):
        self.fail("not tested")
        
    def testDeletePeriodsFromDB(self):
        self.fail("not tested")
        
    def testDeleteScheduleFromDB(self):
        self.fail("not tested")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()