# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Andre Rattinger"
__date__ ="$13.08.2010 09:27:36$"


from einstein.modules.processes import Processes
from Stream import *
from StreamSet import *
from ProcessStreamSet import *
from EquipmentStreamSet import *


import einstein.modules.schedules as schedules
import einstein.modules.profiles  as profiles
from datetime import *
from StreamConstants import *


DEBUG = 0
DETAILEDOUTPUT = 0

def calcProcessStream(stream):
    process = ProcessStreams()
    process.streams.append(stream)
    process.calcStreams()

    if DETAILEDOUTPUT == 1:
        print "Stream After Process Calculation: "
        stream.printStream()

def calcDistLineStream(stream):
    distline = DistLineStreams()
    distline.streams.append(stream)
    distline.calcStreams()

    if DETAILEDOUTPUT == 1:
        print "Stream After DistLine Calculation"
        stream.printStream()

def calcWHEEStream(stream):
    whee = WHEEStreams()
    whee.streams.append(stream)
    whee.calcStreams()

    if DETAILEDOUTPUT == 1:
        print "Stream After WHEE Calculation"
        stream.printStream()

def calcEquipmentStream(stream):
    equipment = EquipmentStreams()
    equipment.streams.append(stream)
    equipment.calcStreams()

    if DETAILEDOUTPUT == 1:
        print "Stream After Equipment Calculation"
        stream.printStream()

def setCalcMethod(StreamGeneration, stream):
    if stream.Source == STREAMSOURCE[0]:
        StreamGeneration.setBatchCalc()
    elif stream.Source == STREAMSOURCE[1]:
        StreamGeneration.setContinuousCalc()

        
def loadStreamData(stream):
    if stream.DBType == STREAMTYPE[0]:
        pStreams = ProcessStreams()
        pStreams.streams.append(stream)
        setCalcMethod(pStreams, stream)
        pStreams.getEnthalpyVectorStUp(stream)
        stream.MassFlowVector = pStreams.getMassFlowVectorStUp(stream)
        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[1]:
        pStreams = ProcessStreams()
        setCalcMethod(pStreams, stream)
        pStreams.streams.append(stream)
        pStreams.getEnthalpyVectorCirc(stream)
        pStreams.getMassFlowVectorCirc(stream)
        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[2]:
        pStreams = ProcessStreams()
        setCalcMethod(pStreams, stream)
        pStreams.streams.append(stream)
        pStreams.getEnthalpyVectorMaintain(stream)
        pStreams.getMassFlowVectorMaintain(stream)
        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[3]:
        pStreams = ProcessStreams()
        setCalcMethod(pStreams, stream)
        pStreams.streams.append(stream)
        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[4]:
        pStreams = ProcessStreams()
        setCalcMethod(pStreams, stream)
        pStreams.streams.append(stream)
        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[5]:
        pStreams = ProcessStreams()
        setCalcMethod(pStreams, stream)
        pStreams.streams.append(stream)

        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[6]:
        pStreams = EquipmentStreams()
        pStreams.streams.append(stream)
        pStreams.getEnthalpyVectorExGas(stream)
        pStreams.getMassFlowVectorExGas(stream)
        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[7]:
        pStreams = EquipmentStreams()
        pStreams.streams.append(stream)
        pStreams.getEnthalpyVectorExGasCond(stream)
        pStreams.getMassFlowVectorExGasCond(stream)
        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[8]:
        pStreams = EquipmentStreams()
        pStreams.streams.append(stream)
        pStreams.getEnthalpyVectorComAir(stream)
        pStreams.getMassFlowVectorCombAir(stream)
        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[9]:
        pStreams = EquipmentStreams()
        pStreams.streams.append(stream)
        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[10]:
        pStreams = DistLineStreams()
        pStreams.streams.append(stream)
        stream.EnthalpyVector = pStreams.getEnthalpyVectorCondRec(stream)
        pStreams.getMassFlowVectorCondRec(stream)
        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[11]:
        pStreams = WHEEStreams()
        pStreams.streams.append(stream)
        pStreams.getVectorSensHeat(stream)
        return pStreams.streams[0]

    elif stream.DBType == STREAMTYPE[12]:
        pStreams = ProcessStreams()
        pStreams.streams.append(stream)
        return pStreams.streams[0]


def getProcess(DBID):
    PId = Status.PId
    ANo = Status.ANo
    DB = Status.DB
    process = None
    processquery = "Questionnaire_id = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
    processes = DB.qprocessdata.sql_select(processquery)
    for proc in processes:
        if DBID == proc.QProcessData_ID:
            process = proc
    return process


def getEquipment(DBID):
    PId = Status.PId
    ANo = Status.ANo
    DB = Status.DB
    equipment = None
    equipquery = "Questionnaire_id = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
    equipments = DB.qgenerationhc.sql_select(equipquery)
    
    for equip in equipments:
        if DBID == equip.QGenerationHC_ID:
            equipment = equip
    return equipment

def getDistLine(DBID):
    PId = Status.PId
    ANo = Status.ANo
    DB = Status.DB
    distquery = "Questionnaire_id = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
    lines = DB.qdistributionhc.sql_select(distquery)
    line = None
    for line in lines:
        if DBID == line.QDistributionHC_ID:
            ln = line
    return ln

def getWHEE(DBID):
    PId = Status.PId
    ANo = Status.ANo
    DB = Status.DB
    wh = None
    wheequery =  "ProjectID = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
    whees = DB.qwasteheatelequip.sql_select(wheequery)
    for whee in whees:
        if DBID == whee.QWasteHeatElEquip_ID:
            wh = whee

    return wh

def getMultipleProcessStreams(ProcID):
    DB = Status.DB
    streamquery = "qprocessdata_QProcessData_id = '"+ str(ProcID) + "'"
    streams_in = DB.process_streams_in.sql_select(streamquery)
    streams_out = DB.process_streams_out.sql_select(streamquery)
    if len(streams_in) > 0:
        streamInQuery = "id = '" + str(streams_in[0]['streams_in_id']) + "'"
        streams_in = DB.streams_in.sql_select(streamInQuery)
    else:
        streams_in = []

    if len(streams_out) > 0:
        streamOutQuery = "id = '" + str(streams_out[0]['streams_out_id']) + "'"
        streams_out = DB.streams_out.sql_select(streamOutQuery)
    else:
        streams_out = []

    return streams_in, streams_out

def initStream(stream):
    if stream.DBType == STREAMTYPE[0]:
        pStreams = ProcessStreams()
        process = getProcess(stream.DBID)
#        mps = getMultipleProcessStreams(process.QProcessData_ID)
        pStreams.loadValues(stream, process, None)
        return stream

    elif stream.DBType == STREAMTYPE[1]:
        pStreams = ProcessStreams()
        process = getProcess(stream.DBID)
        pStreams.loadValues(stream, process, None)
        return stream

    elif stream.DBType == STREAMTYPE[2]:
        pStreams = ProcessStreams()
        process = getProcess(stream.DBID)
        pStreams.loadValues(stream, process, None)
        return stream

    elif stream.DBType == STREAMTYPE[3]:
        pStreams = ProcessStreams()
        process = getProcess(stream.DBID)
        pStreams.loadValues(stream, process, None)
        return stream

    elif stream.DBType == STREAMTYPE[4]:
        pStreams = ProcessStreams()
        process = getProcess(stream.DBID)
        pStreams.loadValues(stream, process, None)
        return stream

    elif stream.DBType == STREAMTYPE[5]:
        pStreams = ProcessStreams()
        process = getProcess(stream.DBID)
        pStreams.loadValues(stream, process, None)
        return stream

    elif stream.DBType == STREAMTYPE[6]:
        pStreams = EquipmentStreams()
        equipment = getEquipment(stream.DBID)
        pStreams.loadValues(stream, equipment, Status.DB)
        return stream

    elif stream.DBType == STREAMTYPE[7]:
        pStreams = EquipmentStreams()
        equipment = getEquipment(stream.DBID)
        pStreams.loadValues(stream, equipment, Status.DB)
        return stream

    elif stream.DBType == STREAMTYPE[8]:
        pStreams = EquipmentStreams()
        equipment = getEquipment(stream.DBID)
        pStreams.loadValues(stream, equipment, Status.DB)
        return stream

    elif stream.DBType == STREAMTYPE[9]:
        pStreams = EquipmentStreams()
        equipment = getEquipment(stream.DBID)
        pStreams.loadValues(stream, equipment, Status.DB)
        return stream

    elif stream.DBType == STREAMTYPE[10]:
        pStreams = DistLineStreams()
        line = getDistLine(stream.DBID)
        pStreams.loadValues(stream, line, Status.DB)
        return stream

    elif stream.DBType == STREAMTYPE[11]:
        pStreams = WHEEStreams()
        whee = getWHEE(stream.DBID)
        pStreams.loadValues(stream, whee, Status.DB)
        return stream

    
    elif stream.DBType == STREAMTYPE[12]:
        pStreams = ProcessStreams()
        process = getProcess(stream.DBID)
        pStreams.loadValues(stream, process, None)
        return stream



class StreamUtils():
    def getStreams(self):
        pass

    def loadFromDB(self):
        pass

    def generateNames(self):
        pass

    def calcStreams(self):
        pass
    
    def detailPrint(self):
        for elem in self.streams:
            self.printStream(elem)

    def printStream(self, stream):

        hEList = []
        if stream.EnthalpyVector == None:
            hEList = []
        elif len(stream.EnthalpyVector) == 0:
            hEList = []
        else:
            for i in range(100):
                hEList.append(stream.EnthalpyVector[i])

        print "Name: ", stream.name
        print "StartTemp: ", str(stream.StartTemp.getAvg())
        print "EndTemp: ", str(stream.EndTemp.getAvg())
        print "StreamType: ", str(stream.Type)
        print "Heat Capacity: ", str(stream.HeatCap)
        print "Hot/Cold: ", stream.HotColdType
        print "Enthalpy Nominal: ", stream.EnthalpyNom
        print "Enthalpy Vector: ", hEList
        print "MassFlow Avg", stream.MassFlowAvg
        if stream.MassFlowVector != None:
            if len(stream.MassFlowVector)>0:
                print "MF Avg Vector: ", sum(stream.MassFlowVector)/len(stream.MassFlowVector)
                print "MF max Vector: ", max(stream.MassFlowVector)
        print "Specific Heat Capacity: ", stream.SpecHeatCap
        print "Specific Enthalpy: ", stream.SpecEnthalpy
        print "Heat Transfer Coefficient: ", stream.HeatTransferCoeff
        print "Fluid Density", stream.FluidDensity
        print "ID: ", stream.id
#        print "Operating Hours: ", self.OperatingHours
        print

class ProcessValues():
    FluidDensityWater = 1000
    FluidID = None
    FluidDensity = None
    FluidCp = None
    VaporCp = None
    TCond = None
    LatentHeat = None
    PTInFlow = None
    PTOutFlow = None
    PTOutFlowRec = None
    VInflowCycle = None
    VOutFlowCycle = None
    mOutFlowNom = None
    mInFlowNom = None
    XOutFlow = None
    PT = None
    PTStartUp = None
    PTFinal = None
    VolProcMed = None
    PTInFlowRec = None
    VInflowDay = None
    HperDay = None
    Qdot_m = None


class ProcessStreams(StreamUtils, StreamSet):
    def __init__(self):
        self.streams = []
        self.processes = None

        self.periodSchedule = self.createTestSchedule()
        self.batchCalc = BatchMassFlow(self.periodSchedule)
        self.continuousCalc = ContinuousMassFlow(self.periodSchedule)
        self.massFlow = None

    def createTestSchedule(self):
        stepUpProfile = profiles.WeeklyProfile("stepUpProfile", weekday=dict(zip(profiles.weekdays, len(profiles.weekdays)*[True])))
        stepUpProfile.addInterval(time(10,0), time(12,0),  50)
        stepUpProfile.addInterval(time(12,0), time(14,0), 100)
        stepUpSchedule = schedules.PeriodSchedule("stepUpSchedule", startup=1.7, inflow=1.7,  outflow=1.7)

        stepUpSchedule.addPeriodProfile(start=date(2009, 1, 1), stop=date(2009,12,31), step=1, scale=100, profile=stepUpProfile)
        return stepUpSchedule


    def getStreams(self):
        pass

    def setBatchCalc(self):
        self.massFlow = self.batchCalc

    def setContinuousCalc(self):
        self.massFlow = self.continuousCalc

    def loadFromDB(self, ProjectID, AlternativeProposalNo, DBConnection):
        PId = ProjectID
        ANo = AlternativeProposalNo
        DB = DBConnection
        # ProcessNames
        processquery = "Questionnaire_id = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
        self.processes = DB.qprocessdata.sql_select(processquery)

        for process in self.processes:
            ProcType = str(process['ProcType'])
            ProcID = process['QProcessData_ID']
            name = process['Process']

            # get id from Connection Table
            streamquery = "qprocessdata_QProcessData_id = '"+ str(ProcID) + "'"
            streams_in = DB.process_streams_in.sql_select(streamquery)
            streams_out = DB.process_streams_out.sql_select(streamquery)
            
            if len(streams_in) > 0:
                streamInQuery = "id = '" + str(streams_in[0]['streams_in_id']) + "'"
                streams_in = DB.streams_in.sql_select(streamInQuery)
            else:
                streams_in = []

            if len(streams_out) > 0:
                streamOutQuery = "id = '" + str(streams_out[0]['streams_out_id']) + "'"
                streams_out = DB.streams_out.sql_select(streamOutQuery)
            else:
                streams_out = []
                
            streamNr = 1

            if ProcType == 'batch':
                source = STREAMSOURCE[0]
            elif ProcType == 'continuous':
                source = STREAMSOURCE[1]
            else: return

            if len(streams_in)+len(streams_out)>0:
                fluidId = process['ProcMedDBFluid_id']
                stream = self.__createBasicStream(name+'_StartUp', ProcID, source, fluidId)
                stream.DBType = STREAMTYPE[0]
                stream.HotColdType = 'Sink'
                self.loadValues(stream, process, None)
                self.streams.append(stream)
                for instream in streams_in:
                    fluidId = instream['dbfluid_id']
                    stream = self.__createBasicStream(name+str(streamNr)+'_Circulation', ProcID, source, fluidId)
                    stream.DBType = STREAMTYPE[1]
                    stream.HotColdType = 'Sink'
                    self.loadValues(stream, process, instream, 'in')
                    self.streams.append(stream)
                    streamNr+=1
                for outstream in streams_out:
                    XOutFlow = outstream['XOutFlow']
                    PTFinal = outstream['PTFinal']
                    FluidID = process['ProcMedDBFluid_id']
                    fluid = DB.dbfluid.sql_select("DBFluid_ID = '" + str(FluidID) + "'")
                    TCond = fluid[0]['TCond']
                    if XOutFlow > 0 or PTFinal < TCond:
                        streamAC = self.__createBasicStream(name+'_WasteHeat_AboveCond', ProcID, source, FluidID)
                        streamAC.DBType = STREAMTYPE[3]
                        streamAC.HotColdType = 'Source'
                        self.loadValues(streamAC, process, outstream, 'out')
                        streamBC = self.__createBasicStream(name+'_WasteHeat_BelowCond', ProcID, source, FluidID)
                        streamBC.DBType = STREAMTYPE[5]
                        streamBC.HotColdType = 'Source'
                        self.loadValues(streamBC, process, outstream, 'out')
                        streamC = self.__createBasicStream(name+'_WasteHeat_Cond', ProcID, source, FluidID)
                        streamC.DBType = STREAMTYPE[4]
                        streamC.HotColdType = 'Source'
                        self.loadValues(streamC, process, outstream, 'out')
                        for elem in [streamAC, streamC, streamBC]:
                            self.streams.append(elem)
                    else:
                        streamWH = self.__createBasicStream(name+'_WasteHeat', ProcID, source, FluidID)
                        streamWH.DBType = STREAMTYPE[12]
                        streamWH.HotColdType = 'Source'
                        self.loadValues(streamWH, process, outstream, 'out')
                        self.streams.append(streamWH)

                stream = self.__createBasicStream(name+'_Maintainance', ProcID, source, fluidId)
                stream.DBType = STREAMTYPE[2]
                stream.HotColdType = 'Sink'
                self.loadValues(stream, process, None)
                self.streams.append(stream)
            else:
                fluidId = process['ProcMedDBFluid_id']
                streamStUp = self.__createBasicStream(name+'_StartUp', ProcID, source, fluidId)
                streamStUp.DBType = STREAMTYPE[0]
                streamStUp.HotColdType = 'Sink'
                self.loadValues(streamStUp, process, None)
                streamCirc = self.__createBasicStream(name+'_Circulation', ProcID, source, fluidId)
                streamCirc.DBType = STREAMTYPE[1]
                streamCirc.HotColdType = 'Sink'
                self.loadValues(streamCirc, process, None)
                streamMain = self.__createBasicStream(name+'_Maintainance', ProcID, source, fluidId)
                streamMain.DBType = STREAMTYPE[2]
                streamMain.HotColdType = 'Sink'
                self.loadValues(streamMain, process, None)

                XOutFlow = process['XOutFlow']
                PTFinal = process['PTFinal']
                fluid = DB.dbfluid.sql_select("DBFluid_ID = '" + str(fluidId) + "'")
                TCond = fluid[0]['TCond']
                if XOutFlow > 0 or PTFinal < TCond:
                    streamAC = self.__createBasicStream(name+ '_WasteHeat_AboveCond', ProcID, source, fluidId)
                    streamAC.DBType = STREAMTYPE[3]
                    streamAC.HotColdType = 'Source'
                    self.loadValues(streamAC, process, None)
                    streamBC = self.__createBasicStream(name+ '_WasteHeat_BelowCond', ProcID, source, fluidId)
                    streamBC.DBType = STREAMTYPE[5]
                    streamBC.HotColdType = 'Source'
                    self.loadValues(streamBC, process, None)
                    streamC = self.__createBasicStream(name+ '_WasteHeat_Cond', ProcID, source, fluidId)
                    streamC.DBType = STREAMTYPE[4]
                    streamC.HotColdType = 'Source'
                    self.loadValues(streamC, process, None)

                    for elem in [streamStUp, streamCirc, streamMain, streamAC, streamC, streamBC]:
                        self.streams.append(elem)

                else:
                    streamWH = self.__createBasicStream(name+'_WasteHeat', ProcID, source, fluidId)
                    streamWH.DBType = STREAMTYPE[12]
                    streamWH.HotColdType = 'Source'
                    self.loadValues(streamWH, process, None)

                    for elem in [streamStUp, streamCirc, streamMain, streamWH]:
                        self.streams.append(elem)

        if DEBUG == 1:
            self.calcStreams()
        if DETAILEDOUTPUT == 1:
            for elem in self.streams:
                for el in elem:
                    self.printStream(el)

    def __createBasicStream(self, name, dbid, source, mediumid):
        stream = Stream()
        stream.name = name
        stream.MediumID = mediumid
        stream.DBID = dbid
        stream.Source = source
        return stream

    def loadValues(self, stream, process, medium = None, mediumType = None):
        """
        mediumType = "in"/"out"
        """
        DB = Status.DB
        proval = ProcessValues()
        
        if medium != None:
            if mediumType == 'in':
                proval.PTInFlow = medium['PTInFlow']
                proval.PTInFlowRec = medium['PTInFlowRec']
                proval.mInFlowNom = medium['mInFlowNom']
                proval.VInFlowCycle = medium['VInFlowCycle']
                proval.FluidID = medium['dbfluid_id']
            if mediumType == 'out':
                proval.PTOutFlow = medium['PTOutFlow']
                proval.PTOutFlowRec = medium['PTOutFlowRec']
                proval.PTFinal = medium['PTFinal']
                proval.VOutFlowCycle = medium['VOutFlowCycle']
                proval.mOutFlowNom = medium['mOutFlowNom']
                proval.XOutFlow = medium['XOutFlow']
                proval.FluidID = medium['dbfluid_id']

        else:
            proval.PTInFlow = process['PTInFlow']
            proval.PTInFlowRec = process['PTInFlowRec']
            proval.mInFlowNom = process['mInFlowNom']
            proval.VInFlowCycle = process['VInFlowCycle']
            proval.FluidID = process['ProcMedDBFluid_id']
            proval.PTOutFlow = process['PTOutFlow']
            proval.PTFinal = process['PTFinal']
            proval.VOutFlowCycle = process['VOutFlowCycle']
            proval.mOutFlowNom = process['mOutFlowNom']
            proval.XOutFlow = process['XOutFlow']

        fluid = DB.dbfluid.sql_select("DBFluid_ID = '" + str(proval.FluidID) + "'")
        if len(fluid)>0:
            proval.FluidDensity = fluid[0]['FluidDensity']
            proval.FluidCp = fluid[0]['FluidCp']
            proval.VaporCp = fluid[0]['VaporCp']
            proval.TCond = fluid[0]['TCond']
            proval.LatentHeat = fluid[0]['LatentHeat']
        
        proval.PT = process['PT']
        proval.PTStartUp = process['PTStartUp']
        proval.VolProcMed = process['VolProcMed']
        proval.VInFlowDay = process['VInFlowDay']
        proval.HperDay = process['HPerDayProc']
        proval.Qdot_m = process['QOpProc']

        if DETAILEDOUTPUT == 1:
            print "---LOADVALUE CALL---"
            print "FluidDensityWater: " + str(proval.FluidDensityWater)
            print "FluidID: " + str(proval.FluidID)
            print "FluidDensity: " + str(proval.FluidDensity)
            print "FluidCp: " + str(proval.FluidCp)
            print "VaporCp: " + str(proval.VaporCp)
            print "TCond: " + str(proval.TCond)
            print "LatentHeat: " + str(proval.LatentHeat)
            print "PTInflow: " + str(proval.PTInFlow)
            print "PTOutflow: " + str(proval.PTOutFlow)
            print "PTOutflowRec: " + str(proval.PTOutFlowRec)
            print "VInFlowCycle: " + str(proval.VInflowCycle)
            print "VOutFlwoCycle: " + str(proval.VOutFlowCycle)
            print "mOutFlowNom: " + str(proval.mOutFlowNom)
            print "mInflowNom: " + str(proval.mInFlowNom)
            print "XOutFlow: " + str(proval.XOutFlow)
            print "PT: " + str(proval.PT)
            print "PTStartUp: " + str(proval.PTStartUp)
            print "PTFinal: " + str(proval.PTFinal)
            print "VolProcMed: " + str(proval.VolProcMed)
            print "PTInFlowRec: " + str(proval.PTInFlowRec)
            print "VInflowDay: " + str(proval.VInflowDay)
            print "HperDay: " + str(proval.HperDay)
            print "Qdot_m: " + str(proval.Qdot_m)
            print

        stream.BaseValues = proval


    def calcStreams(self):
        for stream in self.streams:
            if stream.Source == STREAMSOURCE[0]:
                self.setBatchCalc()
            elif stream.Source == STREAMSOURCE[1]:
                self.setContinuousCalc()

            if stream.DBType == STREAMTYPE[0]:
                self.generateStUpStream(stream)
            elif stream.DBType == STREAMTYPE[1]:
                self.generateCircStream(stream)
            elif stream.DBType == STREAMTYPE[2]:
                self.generateMaintainanceStream(stream)
            elif stream.DBType == STREAMTYPE[3]:
                base = stream.BaseValues
                self.generateWHAboveCondStream(stream, base.VaporCp, 1)
            elif stream.DBType == STREAMTYPE[4]:
                self.generateWHCondStream(stream)
            elif stream.DBType == STREAMTYPE[5]:
                self.generateWHBelowCondStream(stream)
            elif stream.DBType == STREAMTYPE[12]:
                base = stream.BaseValues
                self.generateWHAboveCondStream(stream, base.FluidCp, None)



    def generateStUpStream(self, stream):
        val = stream.BaseValues
        #self.massFlow.periodSchedule.loadFromDB(stream.DBID)
        stream.FluidDensity = val.FluidDensity
        stream.StartTemp.setAverageTemperature(val.PTStartUp)
        stream.EndTemp.setAverageTemperature(val.PT)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = val.FluidCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
#        stream.MassFlowAvg = self.massFlow.getMassFlowStUpNom(val.VolProcMed, val.FluidDensity)
#        stream.EnthalpyNom = self.getEnthalpyNom(stream.EndTemp, stream.StartTemp, stream.SpecHeatCap, stream.MassFlowAvg)
#        try:
#        ProcessID = self.getProcessNr(stream)
        stream.EnthalpyVector = []
#        print "Status.int.UPH: " + str(Status.int.UPH_s_t)
        stream.EnthalpyVector = Status.int.UPH_s_t[stream.DBID]
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)
        stream.MassFlowAvg=max(stream.MassFlowVector)
        stream.EnthalpyNom=max(stream.EnthalpyVector)
        #stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        #stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowStUp(self.VolProcMed, self.FluidDensity, stream.EnthalpyVector, stream.EnthalpyNom)
#        except:
#            stream.EnthalpyVector = []
#            stream.MassFlowVector = []
            
        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(stream.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
        if max(stream.EnthalpyVector)==0:
            stream.OperatingHours=0
        else:
            stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)

        self.test_stream(stream)

    def getEnthalpyVectorStUp(self, stream):
#        ProcessID = self.getProcessNr(stream)
#        stream.EnthalpyVector = []
        print "DBID: " + str(stream.DBID)
        print "UPH_s_t: " + str(Status.int.UPH_s_t)
        stream.EnthalpyVector = Status.int.UPH_s_t[stream.DBID]

    def getMassFlowVectorStUp(self, stream):
        return self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)

    def test_stream(self, stream):
        if stream.OperatingHours == None:
            print stream.name + ": Warning! Operating Hours couldnt be calculated!"

    def getProcessNr(self, stream):
        PId = Status.PId
        ANo = Status.ANo
        DB = Status.DB
        processquery = "Questionnaire_id = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
        self.processes = DB.qprocessdata.sql_select(processquery)
        id = 0
        for process in self.processes:
            if stream.DBID == process['QProcessData_ID']:
                return id
            id+=1
        return None

        
    def generateCircStream(self, stream):
        val = stream.BaseValues
        
        if val.PTInFlowRec != None:
            stream.StartTemp.setAverageTemperature(val.PTInFlowRec)
        else:
            stream.StartTemp.setAverageTemperature(val.PTInFlow)
#        print stream.name, stream.DBID, val.PTInFlowRec, val.PTInFlow, val.PT
        stream.FluidDensity = val.FluidDensity
        stream.EndTemp.setAverageTemperature(val.PT)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = val.FluidCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)

#        stream.MassFlowAvg = self.massFlow.getMassFlowCircNom(val.FluidDensity, val.VInFlowCycle, val.mInFlowNom, val.VInFlowDay, val.HperDay)
#        stream.EnthalpyNom = self.getEnthalpyNom(stream.EndTemp, stream.StartTemp, stream.SpecHeatCap, stream.MassFlowAvg)

#        try:
#        ProcessID = self.getProcessNr(stream)
        stream.EnthalpyVector = Status.int.UPH_c_t[stream.DBID]
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)
        stream.MassFlowAvg=max(stream.MassFlowVector)
        stream.EnthalpyNom=max(stream.EnthalpyVector)
#        except:
#            stream.EnthalpyVector = []
#            stream.MassFlowVector = []

        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(val.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
        
#        stream.OperatingHours = self.massFlow.periodSchedule.getInflowHoursPerYear()
        if max(stream.EnthalpyVector)==0:
            stream.OperatingHours=0
        else:
            stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)

    def getEnthalpyVectorCirc(self, stream):
#        ProcessID = self.getProcessNr(stream)
        stream.EnthalpyVector = Status.int.UPH_c_t[stream.DBID]

    def getMassFlowVectorCirc(self, stream):
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)


    def generateMaintainanceStream(self, stream):
#        print stream.name
        val = stream.BaseValues
        stream.StartTemp.setAverageTemperature(val.PT)
        stream.EndTemp.setAverageTemperature(val.PT+0.1)
        stream.FluidDensity = val.FluidDensityWater
        stream.Type = self.getProcessStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = 3600
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)

#        stream.EnthalpyNom = val.Qdot_m
#        stream.MassFlowAvg = self.massFlow.getMassFlowOpNom(stream.EnthalpyNom, stream.SpecHeatCap, stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
#        try:
        ProcessID = self.getProcessNr(stream)
        stream.EnthalpyVector = Status.int.UPH_m_t[stream.DBID]
        stream.MassFlowVector = self.massFlow.getMassFlowOpVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.MassFlowAvg=max(stream.MassFlowVector)
        stream.EnthalpyNom=max(stream.EnthalpyVector)
#        except:
#            pass

#        stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowOp(stream.Enthalpy, stream.SpecHeatCap)
        stream.HeatTransferCoeff = 5000
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
#        stream.OperatingHours = self.periodSchedule.getOperationHoursPerYear()
        if max(stream.EnthalpyVector)==0:
            stream.OperatingHours=0
        else:
            stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)

    def getEnthalpyVectorMaintain(self, stream):
#        ProcessID = self.getProcessNr(stream)
        stream.EnthalpyVector = Status.int.UPH_m_t[stream.DBID]

    def getMassFlowVectorMaintain(self, stream):
        stream.MassFlowVector = self.massFlow.getMassFlowOpVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.StartTemp.getAvg(), stream.EndTemp.getAvg())


    def generateWHAboveCondStream(self, stream, SpecHeatCap, HeatTransferCoeff = None):
        """
        Generate Waste Heat Above Cond Stream
        TODO Correct to Waste Heat
        """
        val = stream.BaseValues
#        print stream.name, val.VaporCp
        stream.FluidDensity = val.FluidDensity
        if val.PTOutFlow > val.TCond:
            stream.StartTemp.setAverageTemperature(val.PTOutFlow)
            if val.TCond < val.PTFinal:
                stream.EndTemp.setAverageTemperature(val.TCond)
            else:
                stream.EndTemp.setAverageTemperature(val.PTFinal) 
        else:
            #in this case there is no WasteHeatAbovCond Stream
            stream.StartTemp.setAverageTemperature(val.PTOutFlow)
            stream.EndTemp.setAverageTemperature(val.PTFinal)

       
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = SpecHeatCap
#        print "name: " + str(stream.name)
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
        if val.VOutFlowCycle != None:
            stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowWH(stream.FluidDensity, VOutflowCycle = val.VOutFlowCycle)
        elif val.mOutFlowNom != None:
            stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowWH(stream.FluidDensity, mOutflowNom = val.mOutFlowNom)
        else:
            stream.MassFlowAvg = 0
            stream.MassFlowVector = []
            
#       stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)

        ProcessID = self.getProcessNr(stream)
        if val.TCond > val.PTOutFlow:
                #no superheating stream exists
            #stream.EnthalpyVector=[0]*Status.Nt
            #ACHTUNG!!! ZU AENDERN
            stream.EnthalpyVector = Status.int.UPH_w_t[stream.DBID]
        else:        
            if val.TCond < val.PTFinal:
                #in this case desuperheating is definitely  the only waste heat stream:
                stream.EnthalpyVector = Status.int.UPH_w_t[stream.DBID]
            else:
#                stream.EnthalpyVector = Status.int.UPH_w_t[stream.DBID] 
            #waste heat vector must be corrected
                if val.XOutFlow != None:
                    for i in xrange (Status.Nt):
                        stream.EnthalpyVector[i]=(Status.int.UPH_w_t[stream.DBID][i]-(stream.MassFlowVector[i]*val.FluidCp*(val.TCond-val.PTFinal)))                
                else:
                    for i in xrange (Status.Nt):      
                        stream.EnthalpyVector[i]=(Status.int.UPH_w_t[stream.DBID][i]-(stream.MassFlowVector[i]*val.XOutFlow*val.LatentHeat)-(stream.MassFlowVector[i]*val.FluidCp*(val.TCond-val.PTFinal)))
           
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)
        stream.MassFlowAvg=max(stream.MassFlowVector)
        stream.EnthalpyNom=max(stream.EnthalpyVector)
        if HeatTransferCoeff == None:
            stream.HeatTransferCoeff = self.getHeatTransferCoefficient(stream.FluidDensity)
        else:
            stream.HeatTransferCoeff = 100
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
#        stream.OperatingHours = self.periodSchedule.getOutflowHoursPerYear()
        if max(stream.EnthalpyVector)==0:
            stream.OperatingHours=0
        else:
            stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)
            
    def generateWHCondStream(self, stream):
        """
        Generate Waste Heat Cond Stream
        TODO Correct to Waste Heat
        """
        val = stream.BaseValues
        stream.FluidDensity = 1000
        if val.PTOutFlow >= val.TCond and val.TCond > val.PTFinal:
            stream.StartTemp.setAverageTemperature(val.TCond)
            stream.EndTemp.setAverageTemperature(val.TCond-0.1)
        else:
            #in this case there is no Cond Stream
            stream.StartTemp.setAverageTemperature(val.TCond)
            stream.EndTemp.setAverageTemperature(val.TCond)
            
        stream.Type = self.getProcessStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())

        stream.SpecEnthalpy = val.LatentHeat
        stream.SpecHeatCap = stream.SpecEnthalpy*10
        stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowWHCond(VOutflowCycle = val.VOutFlowCycle, FluidDensity = stream.FluidDensity, XOutFlow = val.XOutFlow, mOutflowNom = val.mOutFlowNom)
        stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        ProcessID = self.getProcessNr(stream)
        if val.PTOutFlow < val.TCond or val.TCond <= val.PTFinal:
            #condensation is relevant
            stream.EnthalpyVector = [0]*Status.Nt
#        else:
            #condensation is not relevant, Enthalpy vector stays as calculated

                
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)
        stream.MassFlowAvg=max(stream.MassFlowVector)
        stream.EnthalpyNom=max(stream.EnthalpyVector)
        stream.HeatTransferCoeff = 10000
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
#        stream.OperatingHours = self.periodSchedule.getOutflowHoursPerYear()
        if max(stream.EnthalpyVector)==0:
            stream.OperatingHours=0
        else:
            stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)


    def generateWHBelowCondStream(self, stream):
        """
        Generate Waste heat below Cond Stream
        TODO Correct to Waste Heat
        """
        stream.CalculationMethod = "WasteHeatBelowCond"
        val = stream.BaseValues
        stream.FluidDensity = val.FluidDensity
        if val.TCond < val.PTOutFlow:
            stream.StartTemp.setAverageTemperature(val.TCond)
        else:
            stream.StartTemp.setAverageTemperature(val.PTOutFlow)        
        stream.EndTemp.setAverageTemperature(val.PTFinal)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = val.FluidCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
        if val.VOutFlowCycle != None:
            stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowWH(stream.FluidDensity, VOutflowCycle = val.VOutFlowCycle)
        elif val.mOutFlowNom != None:
            stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowWH(stream.FluidDensity, mOutflowNom = val.mOutFlowNom)
#        stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        ProcessID = self.getProcessNr(stream)
        
        if val.TCond > val.PTOutFlow:
            #only subcooling exists, waste heat vector can be taken 1:1
            stream.EnthalpyVector = Status.int.UPH_w_t[stream.DBID]      
             
        else:        
            if val.TCond < val.PTFinal:
            #no subcooling stream exists
                stream.EnthalpyVector=[0]*Status.Nt
            else:
            #waste heat vector must be corrected
                if val.XOutFlow != None:
                    for i in xrange (Status.Nt):
                        stream.EnthalpyVector[i]=(Status.int.UPH_w_t[stream.DBID][i]-(stream.MassFlowVector[i]*val.VaporCp*(val.PTOutFlow-val.TCond)))            
                else:
                    for i in xrange (Status.Nt):      
                        stream.EnthalpyVector[i]=(Status.int.UPH_w_t[stream.DBID][i]-(stream.MassFlowVector[i]*val.XOutFlow*val.LatentHeat)-(stream.MassFlowVector[i]*val.VaporCp*(val.PTOutFlow-val.TCond)))

        

        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)
        stream.MassFlowAvg=max(stream.MassFlowVector)
        stream.EnthalpyNom=max(stream.EnthalpyVector)
        stream.HeatTransferCoeff = 5000
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
#        stream.OperatingHours = self.periodSchedule.getOutflowHoursPerYear()
        if max(stream.EnthalpyVector)==0:
            stream.OperatingHours=0
        else:
            stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)

class DistLineValues():
    FluidCp = None
    FluidDensity = None
    FluidID = None
    DistribCircFlow = None
    PercentRecirc = None
    TreturnDistrib = None
    Tfeedup = None
    ToutDistrib = None


class DistLineStreams(StreamUtils, StreamSet):
    def __init__(self):
        self.streams = []
        self.lines = None

    def loadFromDB(self, ProcessID, AlternativeProposalNo, DBConnection):
        PId = ProcessID
        ANo = AlternativeProposalNo
        DB = DBConnection

        distquery = "Questionnaire_id = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
        self.lines = DB.qdistributionhc.sql_select(distquery)

        for line in self.lines:
            fluidID = line['HeatDistMedium']
            name = str(line['Pipeduct'])
            DistID = line['QDistributionHC_ID']
#            streamBFW = self.__createBasicDistStream(name+'_BoilerFeedWater', DistID, fluidID)
#            streamBFW.HotColdType = 'Sink'
#            streamBFW.DBType = STREAMTYPE[9]
#            self.loadValues(streamBFW, line, DB)
            streamCR = self.__createBasicDistStream(name+'_CondensateRecovery', DistID, fluidID)
            streamCR.HotColdType = 'Source'
            streamCR.DBType = STREAMTYPE[10]
            self.loadValues(streamCR, line, DB)
#            for elem in [streamBFW, streamCR]:
            for elem in [streamCR]:
                self.streams.append(elem)
        
        if DEBUG == 1:
            self.calcStreams()
        if DETAILEDOUTPUT == 1:
            for elem in self.streams:
                for el in elem:
                    self.printStream(el)
        

    def loadValues(self, stream, line, DBConnection):
        distval = DistLineValues()
        FluidCp = FluidDensity = None
        DB = DBConnection
        distval.FluidID = line['HeatDistMedium']
        fluid = DB.dbfluid.sql_select("DBFluid_ID = '" + str(distval.FluidID) + "'")
        if len(fluid)>0:
            distval.FluidCp = fluid[0]['FluidCp']
            distval.FluidDensity = fluid[0]['FluidDensity']
        distval.DistribCircFlow = line['DistribCircFlow']
        distval.PercentRecirc = line['PercentRecirc']
        distval.TreturnDistrib = line['TreturnDistrib']
        distval.Tfeedup = line['Tfeedup']
        distval.ToutDistrib = line['ToutDistrib']
        stream.BaseValues = distval
#        line['QDistributionHC_ID']
#        print FluidID, FluidCp, FluidDensity
#        print DistribCircFlow, PercentRecirc
#        print TreturnDistrib, Tfeedup, ToutDistrib



    def calcStreams(self):
        for stream in self.streams:
            if stream.DBType == STREAMTYPE[10]:
#                print "--CONDENSATE RECOVERY--"
                self.generateCondensateRecoveryStream(stream)
            elif stream.DBType == STREAMTYPE[9]:
                print "--BOILERFEEDWATER-"


    def generateCondensateRecoveryStream(self, stream):
        """
	Generates Stream for Condensate Recovery

        :returns: nothing
        """
        val = stream.BaseValues
        stream.FluidDensity = val.FluidDensity
        stream.StartTemp.setAverageTemperature(val.TreturnDistrib)
        stream.EndTemp.setAverageTemperature(val.Tfeedup)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = val.FluidCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)

        
        stream.MassFlowAvg  = self.getCondrecMassFlow(val.DistribCircFlow, val.PercentRecirc)
        stream.EnthalpyNom = self.getEnthalpyNom(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowAvg)
        stream.EnthalpyVector = self.getEnthalpyVectorCondRec(stream)
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)

        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(stream.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
#        stream.OperatingHours = self.getOperatingHours()
        if max(stream.EnthalpyVector)==0:
            stream.OperatingHours=0
        else:
            stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)
        #self.CondRecoveryStream.append(stream)

    def getOperatingHours(self):
        return None

    def getEnthalpyVectorCondRec(self, stream):
        equip = getEquipListperLine(stream.DBID)

#        massflow = [0]
#        for i in xrange(len(Status.int.QWHEq_t[0])):
#            for elem in equip:
#                massflow[i] += Status.int.QWHEq_t[self.getEquipmentNr(elem)][i]
#            massflow[i] /= len(equip)
#            massflow.append(0)
        schedule=Status.int.QWHEq_t[self.getEquipmentNr(equip[0])]
        QWHEq=max(schedule)
        enthalpy_vector=[]
        if QWHEq == 0:
            enthalpy_vector = [stream.EnthalpyNom]*Status.Nt
        else:
            for elem in schedule:
                enthalpy_vector.append((elem/QWHEq)*stream.EnthalpyNom)
        
#        m_vector = massflow

        return enthalpy_vector

    def getMassFlowVectorCondRec(self, stream):
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)


    def getBFWMassFlow(self):
        pass

    def getEquipmentNr(self, dbid):
        PId = Status.PId
        ANo = Status.ANo
        DB = Status.DB
        query = "Questionnaire_id = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
        self.equipments = DB.qgenerationhc.sql_select(query)
        id = 0
        for equip in self.equipments:
            if dbid == equip['QGenerationHC_ID']:
                return id
            id+=1
        return None

    def getCondrecMassFlow(self, DistribCircFlow, PercentRecirc):
        m_average = DistribCircFlow *PercentRecirc/3600

        return m_average



    def getLineFromStream(self, stream):
        """
        Example Usage:
        distline.getLineFromStream(stream)
        """
        for line in self.lines:
            if line['QDistributionHC_ID'] == stream.DBID:
                print line

    def __createBasicDistStream(self, name, dbid, fluidID):
        stream = Stream()
        stream.Source = STREAMSOURCE[4]
        stream.name = name
        stream.MediumID = fluidID
        stream.DBID = dbid
        return stream

class WHEEValues():
    FluidID = None
    FluidDensity = None
    WHEETOutlet = None
    SensibleHeat = None
    LatentHeat = None
    QWHEE = None
    SpecificMassFlow = None

class WHEEStreams(StreamUtils, StreamSet):
    def __init__(self):
        self.streams = []
        self.whees = None

    def loadFromDB(self, ProcessID, AlternativeProposalNo, DBConnection):
        PId = ProcessID
        ANo = AlternativeProposalNo
        DB = DBConnection

        wheequery =  "ProjectID = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
        self.whees = DB.qwasteheatelequip.sql_select(wheequery)

        for whee in self.whees:
            name = whee['WHEEName']
            fluidID = whee['WHEEMedium']
            wheeID = whee['QWasteHeatElEquip_ID']
            stream = self.__createBasicWHEEStream(name+'_SensibleHeat', wheeID, fluidID)
            stream.HotColdType = 'Source'
            stream.DBType = STREAMTYPE[11]
            self.loadValues(stream, whee, DB)
            self.streams.append(stream)


        if DEBUG == 1:
            self.calcStreams()
        if DETAILEDOUTPUT == 1:
            for elem in self.streams:
                for el in elem:
                    self.printStream(el)


    def loadValues(self, stream, whee, DBConnection):
        DB = DBConnection
        wheeval = WHEEValues()
        wheeval.FluidID = whee['WHEEMedium']
        fluid = DB.dbfluid.sql_select("DBFluid_ID = '" + str(wheeval.FluidID) + "'")
        if len(fluid)>0:
            wheeval.FluidDensity = fluid[0]['FluidDensity']
            wheeval.SensibleHeat = fluid[0]['SensibleHeat']
            wheeval.LatentHeat = fluid[0]['LatentHeat']
            wheeval.SpecificMassFlow = fluid[0]['SpecificMassFlow']
        wheeval.WHEETOutlet = whee['WHEETOutlet']
        wheeval.QWHEE = whee['QWHEE']
        stream.BaseValues = wheeval


    def calcStreams(self):
        for stream in self.streams:
            if stream.DBType == STREAMTYPE[11]:
                self.generateSensibleHeatStream(stream)

    def generateSensibleHeatStream(self, stream):
        val = stream.BaseValues
        stream.FluidDensity = val.FluidDensity
        stream.StartTemp.setAverageTemperature(val.WHEETOutlet)
        stream.EndTemp.setAverageTemperature(val.WHEETOutlet-20)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecEnthalpy = val.SensibleHeat
        #stream.MassFlowAvg, stream.MassFlowVector = self.getMediumFlow(self.QWHEE, self.SpecificMassFlow, stream)

        stream.EnthalpyNom = val.QWHEE*(val.SensibleHeat/(val.SensibleHeat+val.LatentHeat))
        stream.MassFlowAvg = stream.EnthalpyNom/val.SensibleHeat
        stream.EnthalpyVector = []
        stream.MassFlowVector = []

        self.getVectorSensHeat(stream)

        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(stream.FluidDensity)
        stream.SpecHeatCap = self.getWasteHeatSpecificCapacity(stream)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
#        stream.OperatingHours = self.getOperatingHours(stream)
        if max(stream.EnthalpyVector)==0:
            stream.OperatingHours=0
        else:
            stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)
        #stream.OperatingHours = whee.HPerDayWHEE*whee.NDaysWHEE from processess.py (get Data from DB)

    def getOperatingHours(self, stream):
        whees = Status.prj.getWHEEs()
#        whee.HPerDayWHEE*whee.NDaysWHEE from processess.py (get Data from DB)
#        print "----Sensible Heat Operating Hours----"
        for whee in whees:
#            print whee.QWasteHeatElEquip_ID, stream.DBID
            if stream.DBID == whee.QWasteHeatElEquip_ID:
                return whee.HPerDayWHEE*whee.NDaysWHEE
        return None

    def getVectorSensHeat(self, stream):
#        print "Status.int.QWHEEEq_t" + str(Status.int.QWHEEEq_t)
        val = stream.BaseValues
        QWHEEEq_t = Status.int.QWHEEEq_t[self.getWHEEID(stream)]
        for elem in QWHEEEq_t:
#            print "Status.int.QWHEEEq_t" + str(elem)
            enth = elem*(val.SensibleHeat/(val.SensibleHeat+val.LatentHeat))
            stream.EnthalpyVector.append(enth)
            stream.MassFlowVector.append(enth/val.SensibleHeat)

    def getWHEEID(self, stream):
        PId = Status.PId
        ANo = Status.ANo
        DB = Status.DB
        query = "ProjectID = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
        self.whees = DB.qwasteheatelequip.sql_select(query)
        id = 0
        for whee in self.whees:
            if stream.DBID == whee['QWasteHeatElEquip_ID']:
                return id
            id+=1
        return None

    def getWasteHeatSpecificCapacity(self, stream):
        """
        Get the Specific Heat Capacity for the sensible Heat Stream
        """
        if(stream.StartTemp.getAvg()-stream.EndTemp.getAvg()==0):
            return 0

        Enthalpy = stream.EnthalpyNom
        SpecHeatCap = Enthalpy/(stream.MassFlowAvg*(stream.StartTemp.getAvg()-stream.EndTemp.getAvg()))
#        SpecHeatCap = []
#        for elem in stream.MassFlowVector:
#            SpecHeatCap.append(stream.Enthalpy/(elem*(stream.StartTemp.getAvg()-stream.EndTemp.getAvg())))
        return SpecHeatCap

    def getMediumFlow(self, QWHEE, SpecificMassFlow, stream):
        """
        Create return Vector
        """
        m_max = QWHEE * SpecificMassFlow
        m_vector = []
        for i in xrange(len(self.periodSchedule.getYearlyBatchInflowProfile())):
            m_vector.append(m_max)
        return m_max, m_vector


    def __createBasicWHEEStream(self, name, dbid, fluidID):
        stream = Stream()
        stream.Source = STREAMSOURCE[3]
        stream.MediumID = fluidID
        stream.name = name
        stream.DBID = dbid
        return stream


class EquipmentValues():
        FuelID = None
        OffgasHeatCapacity = None
        Offgas = None
        OffgasDensity = None
        CombAir = None
        FuelConsum = None
        TExhaustGas = None
        FluidDensityAir = 1.012
        FluidDensityWater = 1000
        LatentHeatWater = 0
        FluidCpAir = 1.2
        PartLoad = None
        Tcond = 54.125
        HCGPnom = None

class EquipmentStreams(StreamUtils, StreamSet):
    def __init__(self):
        self.streams = []
        self.equipments = None
        self.withCond = False

    def loadFromDB(self, ProcessID, AlternativeProposalNo, DBConnection):
        PId = ProcessID
        ANo = AlternativeProposalNo
        DB = DBConnection

        equipquery = "Questionnaire_id = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
        self.equipments = DB.qgenerationhc.sql_select(equipquery)
        equipTypes = TRANSEQUIPTYPE

        for equipment in self.equipments:
            name = equipment['Equipment']
            etype = equipment['EquipType']
            eID = equipment['QGenerationHC_ID']
            if etype == equipTypes["compression heat pump"]: # compression heat pump
                pass
            elif etype == equipTypes["thermal heat pump"]: # thermal heat pump
                pass
            elif etype == equipTypes["steam boiler"]: # steam boiler
                self.appendFullEquip(name, eID, equipment, DB)
            elif etype == equipTypes["condensing boiler"]: # condensing boiler
                self.appendFullEquip(name, eID, equipment, DB)
            elif etype == equipTypes["hot water boiler"]: # hot water boiler
                self.appendFullEquip(name, eID, equipment, DB)
            elif etype == equipTypes["burner (direct heating)"] or etype == equipTypes["burner (indirect heating)"]: # burner
                fID = equipment['DBFuel_id']
                streamCA = self.__createBasicEquipStream(name+'_CombustionAir', eID, fID)
                streamCA.HotColdType = 'Sink'
                streamCA.DBType = STREAMTYPE[8]
                self.loadValues(streamCA, equipment, DB)
                streamEG = self.__createBasicEquipStream(name+'_ExhaustGas', eID, fID)
                streamEG.HotColdType = 'Source'
                streamEG.DBType = STREAMTYPE[6]
                self.loadValues(streamEG, equipment, DB)
                for elem in [streamCA, streamEG]:
                    self.streams.append(elem)
            elif etype == equipTypes["compression chiller"]: # compression chiller
                pass
            elif etype == equipTypes["thermal chiller"]: # thermal chiller
                pass
            elif etype == equipTypes["solar thermal (flat-plate)"] or etype == equipTypes["solar thermal (evacuated tubes)"] or etype == equipTypes["solar thermal (concentrating solar systems)"]: # solar thermal
                pass
            elif etype == equipTypes["CHP engine"]: # CHP engine
                self.appendFullEquip(name, eID, equipment, DB)
            elif etype == equipTypes["CHP steam turbine"]: # CHP steam turbine
                self.appendFullEquip(name, eID, equipment, DB)
            elif etype == equipTypes["CHP gas turbine"]: # CHP gas turbine
                self.appendFullEquip(name, eID, equipment, DB)
            elif etype == equipTypes["CHP fuel cell"]: # CHP fuel cell
                pass

        if DEBUG == 1:
            self.calcStreams()
        if DETAILEDOUTPUT == 1:
            for elem in self.streams:
                for el in elem:
                    self.printStream(el)

    def loadValues(self, stream, equipe, DBConnection):
        DB = DBConnection
        equipval = EquipmentValues()

        equipval.FuelID = equipe['DBFuel_id']
        fuel = DB.dbfuel.sql_select("DBFuel_ID = '" + str(equipval.FuelID) + "'")
        
        if len(fuel)>0:
            equipval.OffgasHeatCapacity = fuel[0]['OffgasHeatCapacity']
            equipval.Offgas = fuel[0]['Offgas']
            equipval.OffgasDensity = fuel[0]['OffgasDensity']
            equipval.CombAir = fuel[0]['CombAir']

        fluid = DB.dbfluid.sql_select("DBFluid_ID = '" + str(1) + "'")
        if len(fluid)>0:
            equipval.FluidDensity = fluid[0]['FluidDensity']
            equipval.FluidCp = fluid[0]['FluidCp']
            equipval.VaporCp = fluid[0]['VaporCp']
            equipval.TCond = fluid[0]['TCond']
            equipval.LatentHeat = fluid[0]['LatentHeat']

        equipval.FuelConsum = equipe['FuelConsum']
        equipval.TExhaustGas = equipe['TExhaustGas']
        equipval.PartLoad = equipe['PartLoad']
        equipval.HCGPnom = equipe['HCGPnom']
        stream.BaseValues = equipval


    def appendFullEquip(self, name, eID, equipe, DB):
        fID = equipe['DBFuel_id']
        streamCA = self.__createBasicEquipStream(name+'_CombustionAir', eID, fID)
        streamCA.HotColdType = 'Sink'
        streamCA.DBType = STREAMTYPE[8]
        self.loadValues(streamCA, equipe, DB)
        streamEG = self.__createBasicEquipStream(name+'_ExhaustGas', eID, fID)
        streamEG.HotColdType = 'Source'
        streamEG.DBType = STREAMTYPE[6]
        self.loadValues(streamEG, equipe, DB)
#        streamBFW = self.__createBasicEquipStream(name+'_BoilerFeedWater', eID, fID)
#        streamBFW.HotColdType = 'Sink'
#        streamBFW.DBType = STREAMTYPE[9]
#        self.loadValues(streamBFW, equipe, DB)
#        for elem in [streamCA, streamEG, streamBFW]:
        for elem in [streamCA, streamEG]:
            self.streams.append(elem)

    def calcStreams(self):
        for stream in self.streams:
            if stream.DBType == STREAMTYPE[6]:
                self.generateExhaustGasStream(stream)
            elif stream.DBType == STREAMTYPE[8]:
                self.generateCombustionAirStream(stream)
            elif stream.DBType == STREAMTYPE[9]:
                pass
#                self.generateFeedWaterStream(stream)

    def __createBasicEquipStream(self, name, dbid, fluidID):
        stream = Stream()
        stream.Source = STREAMSOURCE[2]
        stream.name = name
        stream.MediumID = fluidID
        stream.DBID = dbid
        return stream

    def generateFeedWaterStream(self, stream):
	"""
	Generates Stream for BoilerFeedWater

        :returns: Stream
        """
        val = stream.BaseValues
        stream.FluidDensity = val.FluidDensity
        stream.StartTemp.setAverageTemperature(10) # Calculate from Climate Data
        stream.EndTemp.setAverageTemperature(102) # Calculate from Climate Data
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = val.FluidCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)

        stream.MassFlowAvg, stream.MassFlowVector = self.getMassFlowBFW(val.DistribCircFlow, val.PercentRecirc)
        stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)

        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(val.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
#        stream.OperatingHours = self.getOperatingHours()
        if max(stream.EnthalpyVector)==0:
            stream.OperatingHours=0
        else:
            stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)
        


    def generateExhaustGasStream(self, stream):
        """
	    Generates Stream for Exhaust Gas

        :returns: Stream
        """
        val = stream.BaseValues
        stream.FluidDensity = val.OffgasDensity
        stream.StartTemp.setAverageTemperature(val.TExhaustGas)
        stream.EndTemp.setAverageTemperature(val.Tcond)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = val.OffgasHeatCapacity
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
#        stream.MassFlowAvg = self.getOffGasFlow(val.FuelConsum, val.PartLoad, val.Offgas)
#        stream.EnthalpyNom = self.getEnthalpyNom(stream.EndTemp, stream.StartTemp, stream.SpecHeatCap, stream.MassFlowAvg)
        stream.EnthalpyVector = Status.int.QWHEq_t[self.getEquipmentID(stream)] # get Vector not matrix
#        print "Status.int.QWHEq_t: " + str(stream.EnthalpyVector)
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)
        stream.MassFlowAvg=max(stream.MassFlowVector)
        stream.EnthalpyNom=max(stream.EnthalpyVector)

        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(stream.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
        #stream.OperatingHours = #ccheckEq.py - self.HPerYearEq1
#        print "EnthalpyVector: ", str(stream.EnthalpyVector[0:200])
        if sum(stream.EnthalpyVector)==0 or max(stream.EnthalpyVector) == 0:
            stream.OperatingHours=0
        else:
                stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)
        
    def getOperatingHoursEq(self, stream):
        equipments = Status.prj.getEquipments()
        for equipment in equipments:
            if stream.DBID == equipment.QGenerationHC_ID:
                return equipment.HPerYearEq
        return None
    
    def getEnthalpyVectorExGas(self, stream):
        stream.EnthalpyVector = Status.int.QWHEq_t[self.getEquipmentID(stream)]

    def getMassFlowVectorExGas(self, stream):
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)

    def getEquipmentID(self, stream):
        PId = Status.PId
        ANo = Status.ANo
        DB = Status.DB
        query = "Questionnaire_id = '"+str(PId)+"' AND AlternativeProposalNo ='"+str(ANo)+"'"
        self.equipments = DB.qgenerationhc.sql_select(query)
        id = 0
        for equip in self.equipments:
            if stream.DBID == equip['QGenerationHC_ID']:
                return id
            id+=1
        return None

    def generateExhaustGasCondStream(self, stream):
        """
	    Generates Stream for Exhaust Gas Cond

        :returns: Stream
        """
        val = stream.BaseValues
        stream.FluidDensity = val.FluidDensityWater
        stream.StartTemp.setAverageTemperature(val.Tcond)
        stream.EndTemp.setAverageTemperature(val.Tcond-0.1)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = val.LatentHeatWater/0.1
        stream.SpecEnthalpy = val.LatentHeatWater
        stream.MassFlowAvg = self.getH20Air(val.FuelConsum, val.CombAir, val.PartLoad)
        stream.EnthalpyNom = self.getEnthalpyNom(stream.EndTemp, stream.StartTemp, stream.SpecHeatCap, stream.MassFlowAvg)
        scheduleEGC = self.calcScheduleEGC(stream.EnthalpyNom, Status.int.QWHEq_t[self.getEquipmentID(stream)])
        stream.EnthalpyVector = scheduleEGC
        stream.MassFlowVector = []
        for elem in scheduleEGC:
            stream.MassFlowVector.append(elem/stream.EnthalpyNom*stream.MassFlowAvg)

        #stream.MassFlowAvg, stream.MassFlowVector = self.getH20Air(self.FuelConsum, self.CombAir, self.PartLoad)
        #stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(stream.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
        #stream.OperatingHours = self.getOperatingHours() ccheckEq.py - self.HPerYearEq1
        if max(stream.EnthalpyVector)==0:
            stream.OperatingHours=0
        else:
            stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)

    def getEnthalpyVectorExGasCond(self, stream):
        scheduleEGC = self.calcScheduleEGC(stream.EnthalpyNom, Status.int.QWHEq_t[self.getEquipmentID(stream)])
        stream.EnthalpyVector = scheduleEGC
    
    def getMassFlowVectorExGasCond(self, stream):
        stream.MassFlowVector = []
        for elem in stream.EnthalpyVector:
            stream.MassFlowVector.append(elem*stream.EnthalpyNom)


    def calcScheduleEGC(self, EnthalpyNom, QWHEq_t):
        schedule = []
        QWHEq=max(QWHEq_t)
#calculation based on QWHEq_t--> recalculation to schedule and then multpilied by enthalpy
        for elem in QWHEq_t:
            schedule.append(((elem/Status.TimeStep)/(QWHEq)*EnthalpyNom))
        return schedule

    def generateCombustionAirStream(self, stream):
        """
	Generates Stream for Combustion Air

        :returns: Stream
        """
        val = stream.BaseValues
        stream.FluidDensity = val.FluidDensityAir
        stream.StartTemp.setAverageTemperature(25) # Calculate from Climate Data
        stream.EndTemp.setAverageTemperature(val.TExhaustGas) # Calculate from Climate Data
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = val.FluidCpAir
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)

        stream.MassFlowAvg = self.getCombustionAirMassFlow(val.FuelConsum, val.CombAir, val.PartLoad)
        stream.EnthalpyNom = self.getEnthalpyNom(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowAvg)
        stream.EnthalpyVector = self.getEnthalpyVectorComAir(stream)
#        print "USHj_t: " + str(Status.int.USHj_t)
#        print "USHj: " + str(Status.int.USHj)
#        for elem in Status.int.USHj_t:
#            stream.EnthalpyVector.append((elem/Status.TimeStep)/(val.HCGPnom*val.PartLoad))
        
        # TODO Change back to real Vector
        
#        stream.EnthalpyVector = []
#        for i in xrange(Status.Nt):
#            stream.EnthalpyVector.append(0.1)
        
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)

        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(stream.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream)
        #stream.OperatingHours = #from ccheckEq.py - self.HPerYearEq1
        if max(stream.EnthalpyVector)==0:
            stream.OperatingHours=0
        else:
            stream.OperatingHours = sum(stream.EnthalpyVector)/max(stream.EnthalpyVector)

    def getEnthalpyVectorComAir(self, stream):
        stream.EnthalpyVector = []

        equipquery = "QGenerationHC_ID = '"+str(stream.DBID)+"'"
        equip = Status.DB.qgenerationhc.sql_select(equipquery)

        partload = equip[0]['PartLoad']
        enthalpy_nominal = max(Status.int.QWHEq_t[self.getEquipmentID(stream)])
        
#calculation based on QWHEq_t--> recalculation to schedule and then multpilied by enthalpy
        for elem in Status.int.QWHEq_t[self.getEquipmentID(stream)]:
            if enthalpy_nominal == 0:
                stream.EnthalpyVector.append(0)
            else:    
                stream.EnthalpyVector.append(((elem/Status.TimeStep)/(enthalpy_nominal))*stream.EnthalpyNom)
        return stream.EnthalpyVector

    def getMassFlowVectorCombAir(self, stream):
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)

    def getMassFlowBFW(self, DistribCircFlow, PercentRecirc):

        m_average = DistribCircFlow*PercentRecirc/3600
        m_vector = []
        yearlyGHCProfile = self.getYearlyGHCProfile()
        for elem in yearlyGHCProfile:
            m_vector.append(m_average*elem)
#        for i in xrange(len(yearlyGHCProfile)):
#            m_vector.append(m_average*yearlyGHCProfile[i])
        return m_average, m_vector


    def getOffGasFlow(self, FuelConsum, PartLoad, Offgas):
        FuelAmount = (FuelConsum/3600) * PartLoad
        OffgasFlow = Offgas * FuelAmount
#        m_vector = []
#        for i in xrange(8760):
#            m_vector.append(OffgasFlow)
        return OffgasFlow#, m_vector

    def getH20Air(self, FuelConsum, CombAir, PartLoad):
        m_avg, m_vg = self.getCombustionAirMassFlow(FuelConsum, CombAir, PartLoad)
        H20 = 0.01 * m_avg
#        m_vector = []
#        for i in xrange(8760):
#            m_vector.append(H20)
        return H20#, m_vector

    def getCombustionAirMassFlow(self, FuelConsum, CombAir, PartLoad):
        CombustionAir = PartLoad * (FuelConsum/3600) * CombAir
#        m_vector = []
#        for i in xrange(8760):
#            m_vector.append(CombustionAir)
        return CombustionAir#, m_vector

    def getOperatingHours(self):
        return None




class NameGeneration():
    def __init__(self):

        self.process = ProcessStreams()
        self.distline = DistLineStreams()
        self.equipment = EquipmentStreams()
        self.whee = WHEEStreams()

    def loadDataFromDB(self):
        PId = Status.PId
        ANo = Status.ANo
        DB = Status.DB

        self.process.loadFromDB(PId, ANo, DB)
        self.distline.loadFromDB(PId, ANo, DB)
        self.equipment.loadFromDB(PId, ANo, DB)
        self.whee.loadFromDB(PId, ANo, DB)

    def getAllStreams(self):
        return self.process.streams + self.distline.streams + \
            self.equipment.streams + self.whee.streams

    def calcStreams(self):
        self.process.calcStreams()
        self.distline.calcStreams()
        self.equipment.calcStreams()
        self.whee.calcStreams()
#        self.process.detailPrint()
#        self.distline.detailPrint()
#        self.equipment.detailPrint()
#        self.whee.detailPrint()
        self.printStreams()

    def deleteEmptyStreams(self):
        self.deleteStream(self.process.streams)
        self.deleteStream(self.distline.streams)
        self.deleteStream(self.equipment.streams)
        self.deleteStream(self.whee.streams)
                
            
    def deleteStream(self, streams):
        delCount = 0
        for i in xrange(len(streams)):
            if sum(streams[i-delCount].EnthalpyVector) == 0:
                del streams[i-delCount]
                delCount+=1

    def printStreams(self):
        self.process.detailPrint()
        self.distline.detailPrint()
        self.equipment.detailPrint()
        self.whee.detailPrint()




if __name__ == "__main__":
    print "Hello World"



