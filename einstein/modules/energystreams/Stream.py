

#
#__author__="Andre Rattinger"
#__date__ ="$08.07.2010 12:01:24$"

"""
:mod:`einstein.modules.Stream` -- Automatic Stream Generation
=============================================================================

   :synopsis: Automatic generation of energystreams and sets of energystreams
   :author:   Andre Rattinger <Andre.Rattinger@student.TUGraz.at>
"""

"""
TODO:

- rename m_average to m_nom
x Make PT, PTStartup etc. Temperature Type
x Delete autoinitprocessing from the StreamSets and create Dataload class (from DB or at runtime from Program -> Status)
x Fill in operating Hours
x Change Initialisation of MassFlowCalc in StreamFactory
x Delete Holidays from MassFlowCalc Initialisation
"""


from einstein.GUI.status import *
from GUITools import *

import gettext
gettext.install("einstein", "../GUI/locale", unicode=False)
from einstein.modules.constants import *

#from einstein.GUI.status import *
#from einstein.modules.schedules import *
#from einstein.modules.schedules import Schedules, PeriodSchedule
import uuid
from StreamSet import StreamSet
from StreamConstants import *





class Stream():
    """
    Saves a single erneergystream.
    Currently the energystream is only saved at runtime.
    Functions for writing into DB or into a File can be introduced later.
    """
    ProcessID = None
    MediumID = None
    StartTemp = None
    EndTemp = None
    Type = None
    HeatCap = None
    HotOrCold = None
    MassFlowAvg = None
    MassFlowVector = None
    SpecHeatCap = None
    SpecEnthalpy = None
    EnthalpyVector = None
    EnthalpyNom = None
    HeatTransferCoeff = None
    FluidDensity = None
    OperatingHours = None
    id = None
    name = ""
    Source = None
    BaseValues = None
    DBID = None
    DBType = None
    activ = True
    HXSource = None
        
    def __init__(self, MediumID=None, StartTemp=None, EndTemp=None):
        self.ProcessID = None
        self.MediumID = None
        self.StartTemp = Temperature()
        self.EndTemp = Temperature()
        self.Type = None
        self.HeatCap = None
        self.HotOrCold = None
        self.MassFlowAvg = None
        self.MassFlowVector = None
        self.SpecHeatCap = None
        self.SpecEnthalpy = None
        self.EnthalpyVector = None
        self.EnthalpyNom = None
        self.HeatTransferCoeff = None
        self.FluidDensity = None
        self.OperatingHours = None
        self.id = uuid.uuid4()
        self.name = ""
        self.Source = None
        self.BaseValues = None
        self.DBID = None
        self.DBType = None
        self.activ = True
        self.HXSource = None
#        self.percentHeatFlow = None

        # HeatExchanger : SplitFactor
        self.HeatExchangerConnection = {}


    def writeToDB(self):
        pass

    def loadFromDB(self):
        pass

    def printStream(self):

#        hEList = []
#        for i in range(100):
#            hEList.append(self.EnthalpyVector[i])


        print "Name: ", self.name
        print "StartTemp: ", str(self.StartTemp.getAvg())
        print "EndTemp: ", str(self.EndTemp.getAvg())
        print "selfType: ", str(self.Type)
        print "Heat Capacity: ", str(self.HeatCap)
        print "Hot/Cold: ", self.HotOrCold
        print "Enthalpy Nominal: ", self.EnthalpyNom
        print "Enthalpy Vector: ", str(self.EnthalpyVector)
        print "MassFlow Avg: ", self.MassFlowAvg
        print "MassFlow Vector: ", str(self.MassFlowVector)
        print "Specific Heat Capacity: ", self.SpecHeatCap
        print "Specific Enthalpy: ", self.SpecEnthalpy
        print "Heat Transfer Coefficient: ", self.HeatTransferCoeff
        print "Fluid Density", self.FluidDensity
        print "ID: ", self.id
        print "Operating Hours: ", self.OperatingHours
        print

class HXPinchConnection():

    sinkstreams = []
    sourcestreams = []
    HXID = None
    combinedSink = None
    combinedSource = None
    StorageSize = None

    def __init__(self, HXID):
        self.HXID = HXID
        self.sinkstreams = []
        self.sourcestreams = []
        self.combinedSink = None
        self.combinedSource = None
        self.StorageSize = 0

    def writeToDB(self):

        # Got to delete all entrys for the heatexchanger first

        for elem in self.sinkstreams:
            self.__writeDBEntry(elem)

        for elem in self.sourcestreams:
            self.__writeDBEntry(elem)

    def __writeDBEntry(self, sstream):
        elem = sstream
        stream = {}
        hxpinch = {}

        

        stream['name'] = check(elem.stream.name)
        stream['Hot_Cold'] = check(elem.stream.HotOrCold)
        stream['Type'] = check(elem.stream.Type)

        stream['source_id'] = check(elem.stream.DBID)
        stream['source_type'] = check(elem.stream.Source)

        stream['medium_id'] = check(elem.stream.MediumID)
        stream['StartTemp'] = check(elem.stream.StartTemp.getAvg())
        stream['EndTemp'] = check(elem.stream.EndTemp.getAvg())
        stream['StreamType'] = check(elem.stream.DBType)
        stream['HeatCapacity'] = check(elem.stream.HeatCap)
        stream['MassFlowNom'] = check(elem.stream.MassFlowAvg)
        stream['SpecHeatCapacity'] = check(elem.stream.SpecHeatCap)
        stream['SpecEnthalpy'] = check(elem.stream.SpecEnthalpy)
        stream['EnthalpyNom'] = check(elem.stream.EnthalpyNom)
        stream['HeatTransferCoeff'] = check(elem.stream.HeatTransferCoeff)

        DB = Status.DB
        pinch_id = DB.pinchstream.insert(stream)

        hxpinch['qheatexchanger_QHeatExchanger_Id'] = check(self.HXID)
        hxpinch['pinchstream_id'] = check(pinch_id)

        hxpinch['inletTemp'] = check(elem.inletTemp)
        hxpinch['outletTemp'] = check(elem.outletTemp)
        hxpinch['outletOfHX_id'] = check(elem.outletHX)
        hxpinch['inletOfHX_id'] = check(elem.inletHX)
        hxpinch['HeatFlowPercent'] = check(elem.percentHeatFlow)

#        if elem.InTempActive:
#            hxpinch['inletTemp'] = check(elem.inletTemp)
#            hxpinch['outletOfHX_id'] = check(None)
#        elif not elem.InTempActive:
#            hxpinch['inletTemp'] = check(None)
#            hxpinch['outletOfHX_id'] = check(elem.outletHX)
#
#        if elem.OutTempActive:
#            hxpinch['outletTemp'] = check(elem.outletTemp)
#            hxpinch['inletOfHX_id'] = check(None)
#        elif not elem.OutTempActive:
#            hxpinch['outletTemp'] = check(None)
#            hxpinch['inletOfHX_id'] = check(elem.inletHX)

        hx_id = DB.heatexchanger_pinchstream.insert(hxpinch)

    def deleteFromDB(self):
        DB = Status.DB

        if self.HXID == None: return
        query = "qheatexchanger_QHeatExchanger_Id = '"+str(self.HXID)+"'"
        result = DB.heatexchanger_pinchstream.sql_select(query)
        for elem in result:
            query = "DELETE FROM pinchstream WHERE id = %s"
            query = query % elem['pinchstream_id']
            Status.DB.sql_query(query)

        query = "DELETE FROM heatexchanger_pinchstream WHERE qheatexchanger_QHeatExchanger_Id = %s"
        query = query % str(self.HXID)
        Status.DB.sql_query(query)


    def loadFromDB(self):
        self.sinkstreams = []
        self.sourcestreams = []
        DB = Status.DB
        query = "qheatexchanger_QHeatExchanger_Id = '" + str(self.HXID) +"'"
        connections = DB.heatexchanger_pinchstream.sql_select(query)

#        print self.HXID, connections
        for connection in connections:
            pinch_id = connection['pinchstream_id']
            query = "id = '" + str(pinch_id) +"'"
            pinchstreams = DB.pinchstream.sql_select(query)
            pinch = pinchTemp()
            
            pinch.outletTemp = connection['outletTemp']
            pinch.inletHX = connection['inletOfHX_id']
            pinch.inletTemp = connection['inletTemp']
            pinch.outletHX = connection['outletOfHX_id']
            pinch.percentHeatFlow = connection['HeatFlowPercent']

            if pinch.inletTemp == None:
                pinch.InTempActive = False
            if pinch.outletTemp == None:
                pinch.OutTempActive = False

            for pstream in pinchstreams:
                
                stream = Stream()
                stream.name = pstream['name']
                stream.HotOrCold = pstream['Hot_Cold']
                stream.Type = pstream['Type']
                stream.HeatCap = pstream['HeatCapacity']
                stream.MassFlowAvg = pstream['MassFlowNom']
                stream.SpecHeatCap = pstream['SpecHeatCapacity']
                stream.SpecEnthalpy = pstream['SpecEnthalpy']
                stream.EnthalpyNom = pstream['EnthalpyNom']
                stream.HeatTransferCoeff = pstream['HeatTransferCoeff']
                stream.HXSource = self.HXID
                stream.StartTemp.setAvgTemp(pstream['StartTemp'])
                stream.EndTemp.setAvgTemp(pstream['EndTemp'])
                stream.MediumID = pstream['medium_id']
                stream.DBID = pstream['source_id']
                stream.Source = pstream['source_type']
                stream.DBType = pstream['StreamType']
                pinch.stream = stream

                if pinch.stream.HotOrCold == 'Cold' or pinch.stream.HotOrCold == 'Sink':
                    self.sinkstreams.append(pinch)
                elif pinch.stream.HotOrCold == 'Hot' or pinch.stream.HotOrCold == 'Source':
                    self.sourcestreams.append(pinch)
#                StreamGeneration.loadStreamData(stream)

class pinchTemp():
    stream = None
    InTempActive = True
    inletTemp = None
    inletHX = None
    OutTempActive = True
    outletTemp = None
    outletHX = None
    percentHeatFlow = None

    def __init__(self):
        self.stream = None
        self.inletHX = None
        self.inletTemp = None
        self.outletHX = None
        self.outletTemp = None
        self.percentHeatFlow = None
#        self.InTempActive = True
#        self.OutTempActive = True


class StreamFactory():
    """
    StreamFactory creates the different kinds of stream based on the Streamname.
    param: periodSchedule needed to initialise the Streamsets

    """
    def __init__(self, periodSchedule):
        """
        periodSchedule needed to initialise StreamSets
        """
        self.periodSchedule = periodSchedule

    def setPeriodSchedule(self, periodSchedule):
        self.periodSchedule = periodSchedule

    def getStreamSet(self, StreamType):
        """
	Get a StreamSet based on an String
        Possible values:
        Boiler
        ProcessBatch
        ProcessContinuous
        WasteHeatElectrical
        DistributionLine

        :param StreamType: String thats used to create a new StreamSet
        :type  StreamType: String

        :returns: complete StreamSet 
        :rtype: einstein.modules.energystreams.StreamSet
        """
        if StreamType == 'Equipment':
            return self.getEquipmentStreamSet()
        elif StreamType == 'ProcessBatch':
            return self.getProcessBatchStreamSet()
        elif StreamType == 'ProcessContinuous':
            return self.getProcessContStreamSet()
        elif StreamType == 'WasteHeatElectrical':
            return self.getWasteHeatElectricalStreamSet()
        elif StreamType == 'DistributionLine':
            return self.getDistributionLineStreamSet()
        else:
            print "Not found"
            return None

    def getEquipmentStreamSet(self):
        stream_set = EquipmentStreamSet(self.periodSchedule)
        stream_set.generateStreams()
        return stream_set

    def getProcessBatchStreamSet(self):
        massFlowCalc = BatchMassFlow(self.periodSchedule)
        stream_set = ProcessStreamSet(massFlowCalc, self.periodSchedule)
        """
        do stream initialising
        """
        
        return stream_set


    def getProcessContStreamSet(self):
        massFlowCalc = ContinuousMassFlow(self.periodSchedule)
        stream_set = ProcessStreamSet(massFlowCalc, self.periodSchedule)
        return stream_set

    def getWasteHeatElectricalStreamSet(self):
        stream_set = WasteHeatElectricalStreamSet(self.periodSchedule)
        return stream_set

    def getDistributionLineStreamSet(self):
        stream_set = DistributionLineStreamSet(self.periodSchedule)
        return stream_set

class Temperature():

    def __init__(self, AverageTemp = None, VectorTemp = None):
        self.__avg_temp = AverageTemp
        self.__v_temp = VectorTemp

    def setAverageTemperature(self, AverageTemperature):
        self.__avg_temp = AverageTemperature

    def setAvgTemp(self, AverageTemperature):
        self.__avg_temp = AverageTemperature

    def setTemperaturVector(self, VectorTemp):
        self.__v_temp = VectorTemp

    def setVectorTemp(self, VectorTemperature):
        self.__v_temp = VectorTemperature
        
    def getAverageTemperatur(self):
        return self.__avg_temp

    def getAvg(self):
        return self.__avg_temp

    def getVector(self):
        return self.__v_temp

    def getTemperaturVector(self):
        return self.__v_temp




if __name__ == "__main__":
#    stream = Stream()
#    stream.Temperature.setAverageTemperature(10)
#    print stream.Temperature.getAverageTemperatur()

    Factory = StreamFactory()

    stream_set = Factory.getStreamSet('ProcessBatch')
    stream_set.StUpStream.Temperature.setAverageTemperature(10)
    print stream_set.StUpStream.Temperature.getAverageTemperatur()






