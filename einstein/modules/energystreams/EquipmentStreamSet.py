
__author__="Andre Rattinger"
__date__ ="$04.08.2010 11:39:46$"

from StreamSet import StreamSet
from Stream import *
from einstein.GUI.status import Status

def getEquipListperLine(LineID):
    equipments = []

    for equip in Status.prj.getEquipments():
        list = str(equip.PipeDuctEquip).split(';')
        for i in xrange(len(list)):
            try:
                list[i]=int(list[i])
            except:
                pass

        if LineID in list and equip.AlternativeProposalNo == Status.ANo:
            equipments.append(equip.QGenerationHC_ID)
    return equipments






class EquipmentStreamSet(StreamSet):
    def __init__(self, periodSchedule):
        StreamSet.__init__(self, periodSchedule)

        self.withCond = False
        self.FuelConsum = None
        self.PartLoad = None
        self.Offgas = None
        # TExhaustGas: Default Value for Waste Heat Temperature
        self.TExhaustGas = 200
        self.FeedWaterStream = []
        self.ExhaustGasStream = []
        self.ExhaustGasCondStream = []
        self.CombustionAirStream = []

    def getFeedWaterStream(self):
        return self.FeedWaterStream

    def getExhaustGasStream(self):
        return self.ExhaustGasStream

    def getExhaustGasCondStream(self):
        return self.ExhaustGasCondStream

    def getCombustionAirStream(self):
        return self.CombustionAirStream

    def generateStreams(self):
        self.generateFeedWaterStream()
        self.generateExhaustGasStream()
        self.generateExhaustGasCondStream()
        self.generateCombustionAirStream()

    def initvalues(self):

        self.Offgas = 10
        self.FuelConsum = 10
        self.PartLoad = 10
        self.CombAir = 10
        self.FluidDensity = 10
        self.FluidCp = 10
        self.OffGasDensity = 10
        self.TExhaustGas = 10
        self.Tcond = 10
        self.OffGasHeatCap = 10
        self.LatentHeatWater = 10
        self.SpecHeatCap = 10
        self.DistribCircFlow = 10 #Change Functioncall
        self.PercentRecirc = 10 #Change Functioncall
        self.PartLoad = 10



    def generateFeedWaterStream(self):
	"""
	Generates Stream for BoilerFeedWater

        :returns: Stream
        """
        stream = Stream()
        stream.FluidDensity = self.FluidDensity
        stream.StartTemp.setAverageTemperature(10) # Calculate from Climate Data
        stream.EndTemp.setAverageTemperature(102) # Calculate from Climate Data
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = self.FluidCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)

        stream.MassFlowAvg, stream.MassFlowVector = self.getMassFlowBFW(self.DistribCircFlow, self.PercentRecirc)
        stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)

        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(self.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream.EnthalpyNom)
        stream.OperatingHours = self.getOperatingHours()
        self.FeedWaterStream.append(stream)


    def generateExhaustGasStream(self):
        """
	Generates Stream for Exhaust Gas

        :returns: Stream
        """
        stream = Stream()
        stream.FluidDensity = self.OffGasDensity
        stream.StartTemp.setAverageTemperature(self.TExhaustGas)
        stream.EndTemp.setAverageTemperature(self.Tcond)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = self.OffGasHeatCap
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
        stream.MassFlowAvg = self.getOffGasFlow(self.FuelConsum, self.PartLoad, self.Offgas)
        stream.EnthalpyNom = self.getEnthalpyNom(stream.EndTemp, stream.StartTemp, stream.SpecHeatCap, stream.MassFlowAvg)
        stream.EnthalpyVector = self.QWHEq_t # get Vector not matrix
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, steam.StartTemp)

        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(self.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream.EnthalpyNom)
        #stream.OperatingHours = #ccheckEq.py - self.HPerYearEq1
        self.ExhaustGasStream.append(stream)

        if self.withCond:
            self.__generateExhaustGasCondStream(stream.EnthalpyNom)


    def __generateExhaustGasCondStream(self, EnthalpyNom):
        """
	Generates Stream for Exhaust Gas Cond

        :returns: Stream
        """
        stream = Stream()
        stream.FluidDensity = self.FluidDensity
        stream.StartTemp.setAverageTemperature(self.Tcond)
        stream.EndTemp.setAverageTemperature(self.Tcond)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = self.LatentHeatWater/0.1
        stream.SpecEnthalpy = self.LatentHeatWater
        stream.MassFlowAvg = self.getH20Air(self.FuelConsum, self.CombAir, self.PartLoad)
        stream.EnthalpyNom = self.getEnthalpyNom(stream.EndTemp, stream.StartTemp, stream.SpecHeatCap, stream.MassFlowAvg)
        scheduleEGC = self.calcScheduleEGC(EnthalpyNom, self.QWHEq_t)
        stream.MassFlowVector = []
        for elem in scheduleEGC:
            stream.MassFlowVector.append(elem*stream.EnthalpyNom)

        #stream.MassFlowAvg, stream.MassFlowVector = self.getH20Air(self.FuelConsum, self.CombAir, self.PartLoad)
        #stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(self.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream.EnthalpyNom)
        #stream.OperatingHours = self.getOperatingHours() ccheckEq.py - self.HPerYearEq1
        self.ExhaustGasCondStream.append(stream)

    def calcScheduleEGC(self, EnthalpyNom, QWHEq_t):
        schedule = []
        for elem in QWHEq_t:
            schedule.append((elem/Status.TimeStep)/(EnthalpyNom))
        return Schedule

    def generateCombustionAirStream(self):
        """
	Generates Stream for Combustion Air

        :returns: Stream
        """
        stream = Stream()
        stream.FluidDensity = self.FluidDensity
        stream.StartTemp.setAverageTemperature(25) # Calculate from Climate Data
        stream.EndTemp.setAverageTemperature(self.TExhaustGas) # Calculate from Climate Data
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = self.FluidCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
        stream.MassFlowAvg, stream.MassFlowVector = self.getCombustionAirMassFlow(self.FuelConsum, self.CombAir, self.PartLoad)
        stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(stream.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream.EnthalpyNom)
        #stream.OperatingHours = #from ccheckEq.py - self.HPerYearEq1
        self.CombustionAirStream.append(stream)

    def getMassFlowBFW(self, DistribCircFlow, PercentRecirc):

        m_average = DistribCircFlow*PercentRecirc/3600
        m_vector = []
        yearlyGHCProfile = self.getYearlyGHCProfile()
        for elem in yearlyGHCProfile:
            m_vector.append(m_average*elem)
#        for i in xrange(len(yearlyGHCProfile)):
#            m_vector.append(m_average*yearlyGHCProfile[i])
        return m_average, m_vector

    def getYearlyGHCProfile(self):
        # Still needs to be defined
        # !!! getYearlyGHCProfile needs to be calculated!!  =MAX(aller profiles)*PartLoad
        return self.periodSchedule.getYearlyContinuousOutflowProfile()


    def getOffGasFlow(self, FuelConsum, PartLoad, Offgas):
        FuelAmount = FuelConsum * PartLoad
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
        CombustionAir = PartLoad * FuelConsum * CombAir
        m_vector = []
        for i in xrange(8760):
            m_vector.append(CombustionAir)
        return CombustionAir, m_vector

    def getOperatingHours(self):
        return None




if __name__ == "__main__":
    print "Hello World";
