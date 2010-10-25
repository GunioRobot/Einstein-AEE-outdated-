
__author__="Andre Rattinger"
__date__ ="$04.08.2010 11:48:08$"

from StreamSet import StreamSet
from Stream import *

class DistributionLineStreamSet(StreamSet):
    """
    Generates the Streams for a Distributionline
    """

    def __init__(self, periodSchedule):
        StreamSet.__init__(self, periodSchedule)
        # VALUES FROM DB OR PROGRAM

        #self.initvalues()
        self.CondRecoveryStream = []

    def getCondRecoveryStream(self):
        return self.CondRecoveryStream

    def generateStreams(self):
        self.generateCondensateRecoveryStream()



    def initvalues(self):
        self.Tfeedup = 10
        self.ToutDistrib = 10
        self.TreturnDistrib = 10
        self.FluidDensity = 10
        self.TreturnDistrib = 10
        self.Tfeedup = 10
        self.FluidCp = 10
        self.DistribCircFlow = 10
        self.PercentRecirc = 10


    def generateBoilerFeedWaterStream(self):
        pass

    def generateCondensateRecoveryStream(self):
        """
	Generates Stream for Condensate Recovery

        :returns: Stream
        """
        stream = Stream()
        stream.FluidDensity = self.FluidDensity
        stream.StartTemp.setAverageTemperature(self.TreturnDistrib)
        stream.EndTemp.setAverageTemperature(self.Tfeedup)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = self.FluidCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
        stream.MassFlowAvg, stream.MassFlowVector = self.getCondrecMassFlow(self.DistribCircFlow, self.PercentRecirc)
        stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(stream.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream.EnthalpyNom)
        #stream.OperatingHours = self.getOperatingHours()
        self.CondRecoveryStream.append(stream)

    def getBFWMassFlow(self):
        pass

    def getCondrecMassFlow(self, DistribCircFlow, PercentRecirc):
        m_average = DistribCircFlow *PercentRecirc/3600
        m_vector = []
        #getVector USHj_t
        USHj_t = []
        for elem in USHj_t:
            m_vector.append(m_average*elem)

        return m_average, m_vector


if __name__ == "__main__":
    print "Hello World";
