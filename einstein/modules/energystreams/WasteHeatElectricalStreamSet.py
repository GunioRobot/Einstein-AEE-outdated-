
__author__="Andre Rattinger"
__date__ ="$04.08.2010 11:43:11$"

from StreamSet import StreamSet
from Stream import *

class WasteHeatElectricalStreamSet(StreamSet):
    def __init__(self, periodSchedule):
        StreamSet.__init__(self, periodSchedule)
        #self.initvalues()
        self.sensHeatStream = []
        self.condHeatStream = []

    def getCondHeatStream(self):
        return self.condHeatStream

    def getSensHeatStream(self):
        return self.sensHeatStream

    def generateStreams(self):
        self.generateSensibleHeatStream()
        self.generateCondensationHeatStream()

    def initvalues(self):
        self.WHEEOutlet = 10
        self.SensibleHeat = 10
        self.QWHEE = 10
        self.SpecificMassFlow = 10
        self.FluidDensity = 10
        self.Tcond = 11
        self.LatentHeat = 10
        self.FluidCp = 10



    def generateSensibleHeatStream(self):
        stream = Stream()
        stream.FluidDensity = self.FluidDensity
        stream.StartTemp.setAverageTemperature(self.WHEEOutlet)
        stream.EndTemp.setAverageTemperature(self.Tcond)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecEnthalpy = self.SensibleHeat
        #stream.MassFlowAvg, stream.MassFlowVector = self.getMediumFlow(self.QWHEE, self.SpecificMassFlow, stream)

        stream.EnthalpyNom = self.QWHEE*(self.SensibleHeat/(self.SensibleHeat+self.LatentHeat))
        stream.MassFlowAvg = stream.EnthalpyNom/self.SensibleHeat
        stream.EnthalpyVector = []
        stream.MassFlowVector = []
        for elem in Status.int.WHEEEq_t:
            enth = elem*(self.SensibleHeat/(self.SensibleHeat+self.LatentHeat))
            stream.EnthalpyVector.append(enth)
            stream.MassFlowVector.append(enth/self.SensibleHeat)


#        stream.Enthalpy = []
#        for elem in stream.MassFlowVector:
#            stream.Enthalpy.append(elem*stream.SpecEnthalpy)
        #stream.Enthalpy = stream.MassFlowAvg * stream.SpecEnthalpy
        

        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(stream.FluidDensity)
        stream.SpecHeatCap = self.getWasteHeatSpecificCapacity(stream)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotOrCold = self.getHotCold(stream.EnthalpyNom)
        #stream.OperatingHours = whee.HPerDayWHEE*whee.NDaysWHEE from processess.py (get Data from DB)
        self.sensHeatStream.append(stream)

    def getWasteHeatSpecificCapacity(self, stream):
        """
        Get the Specific Heat Capacity for the sensible Heat Stream
        """
        if(stream.StartTemp.getAvg()-stream.EndTemp.getAvg()==0):
            return 0

        Enthalpy = max(stream.Enthalpy)
        SpecHeatCap = Enthalpy/(stream.MassFlowAvg*(stream.StartTemp.getAvg()-stream.EndTemp.getAvg()))
#        SpecHeatCap = []
#        for elem in stream.MassFlowVector:
#            SpecHeatCap.append(stream.Enthalpy/(elem*(stream.StartTemp.getAvg()-stream.EndTemp.getAvg())))
        return SpecHeatCap


    def generateCondensationHeatStream(self):
        stream = Stream()
        stream.FluidDensity = self.FluidDensity
        stream.StartTemp.setAverageTemperature(self.Tcond)
        stream.EndTemp.setAverageTemperature(self.Tcond-0.1)
        stream.Type = self.getProcessStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecEnthalpy = self.LatentHeat

        stream.EnthalpyNom = self.QWHEE*(self.LatentHeat/(self.SensibleHeat+self.LatentHeat))
        stream.MassFlowAvg = stream.EnthalpyNom/self.LatentHeat
        stream.EnthalpyVector = []
        stream.MassFlowVector = []
        for elem in Status.int.WHEEEq_t:
            enth = elem*(self.LatentHeat/(self.SensibleHeat+self.LatentHeat))
            stream.EnthalpyVector.append(enth)
            stream.MassFlowVector.append(enth/self.LatentHeat)

        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(stream.FluidDensity)
        stream.SpecHeatCap = self.getWasteHeatSpecificCapacity(stream)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotOrCold = self.getHotCold(stream.EnthalpyNom)
        #stream.OperatingHours = whee.HPerDayWHEE*whee.NDaysWHEE from processess.py (get Data from DB)
        self.condHeatStream.append(stream)

    def getMediumFlow(self, QWHEE, SpecificMassFlow, stream):
        """
        Create return Vector
        """
        m_max = QWHEE * SpecificMassFlow
        m_vector = []
        for i in xrange(len(self.periodSchedule.getYearlyBatchInflowProfile())):
            m_vector.append(m_max)
        return m_max, m_vector



if __name__ == "__main__":
    print "Hello World";
