
__author__="Andre Rattinger"
__date__ ="$04.08.2010 11:44:42$"

from StreamSet import StreamSet
from Stream import *



class ProcessStreamSet(StreamSet):
    """
    Process Stream Set
    """
    StUpStream = []
    CircStream = []
    MaintainanceStream = []
    WasteHeatAC = []
    WasteHeatC = []
    WasteHeatBC = []
    def __init__(self, massFlowCalculation, periodSchedule):
        """
        massFlowCalculation can be the classes BatchMassFlow or ContinuousMassFlow
        """

        StreamSet.__init__(self, periodSchedule)
        self.massFlow = massFlowCalculation
        self.VInflowCycle = None
        self.mInflowNom = None
        self.VInflowDay = None
        self.Process = 0
        self.HperDay = None
        self.StUpStream = []
        self.CircStream = []
        self.MaintainanceStream = []
        self.WasteHeatAC = []
        self.WasteHeatC = []
        self.WasteHeatBC = []

        #self.initvalues()

    def getStUpStream(self):
        return self.StUpStream
    
    def getCircStream(self):
        return self.CircStream

    def getMaintainanceStream(self):
        return self.MaintainanceStream

    def getWHAboveCondStream(self):
        return self.WasteHeatAC

    def getWHCondStream(self):
        return self.WasteHeatC

    def getWHBelowCondStream(self):
        return self.WasteHeatBC

    def generateStreams(self):
        self.generateStUpStream()
        self.generateCircStream()
        self.generateMaintainanceStream()
        self.generateWHAboveCondStream()
        self.generateWHCondStream()
        self.generateWHBelowCondStream()


    def initvalues(self):
        self.FluidDensity = 10
        self.Tcond = 10
        self.PTStartUp = 10
        self.PT = 10
        self.FluidCp = 10
        self.VolProcMed = 10
        self.PTInflowRec = 10
        self.PTInflow = 10
        self.VInflowCycle = 10
        self.mInflowNom = 10
        self.VInflowDay = 10
        self.HperDay = 10
        self.Qdot = 10
        self.PTOutflow = 10
        self.VaporCp = 10
        self.VOutflowCycle = 10
        self.mOutFlowNom = 10
        self.LatentHeat = 10
        self.XOutFlow = 10
        self.PTFinal = 10
        self.Process = 0

    def generateStUpStream(self):
        stream = Stream()
        stream.FluidDensity = self.FluidDensity
        stream.StartTemp.setAverageTemperature(self.PTStartUp)
        stream.EndTemp.setAverageTemperature(self.PT)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = self.FluidCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
        stream.MassFlowAvg = self.massFlow.getMassFlowStUpNom(self.VolProcMed, self.FluidDensity)
        stream.EnthalpyNom = self.getEnthalpyNom(stream.EndTemp, stream.StartTemp, stream.SpecHeatCap, stream.MassFlowAvg)
        stream.EnthalpyVector = Status.int.UPH_s_t[self.Process]
        stream.MassFlowVector = self.getMassFlowVector(stream.EnthalpyVector, stream.SpecHeatCap, stream.EndTemp, stream.StartTemp)
        #stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        #stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowStUp(self.VolProcMed, self.FluidDensity, stream.EnthalpyVector, stream.EnthalpyNom)

        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(self.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream.EnthalpyNom)
        stream.OperatingHours = self.massFlow.getStUpOperatingHours()
        self.StUpStream.append(stream)
#------------------------------------------------------------------------------
    def generateCircStream(self):
        stream = Stream()

        if self.PTInflowRec != None:
            stream.StartTemp.setAverageTemperature(self.PTInflowRec)
        else:
            stream.StartTemp.setAverageTemperature(self.PTInflow)

        stream.FluidDensity = self.FluidDensity
        stream.EndTemp.setAverageTemperature(self.PT)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = self.FluidCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
        stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowCirc(stream.FluidDensity, self.VInflowCycle, self.mInflowNom, self.VInflowDay, self.HperDay)
        stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        stream.HeatTransferCoeff = self.getHeatTransferCoefficient(self.FluidDensity)
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream.EnthalpyNom)
        operatingHours = self.periodSchedule.getInflowHoursPerYear()
        self.CircStream.append(stream)


    def generateMaintainanceStream(self):

        stream = Stream()
        stream.StartTemp.setAverageTemperature(self.PT)
        stream.EndTemp.setAverageTemperature(self.PT+0.1)
        stream.FluidDensity = self.FluidDensity
        stream.Type = self.getProcessStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = 3600
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
        stream.Enthalpy = []
        for elem in self.periodSchedule.getYearlyBatchOperationProfile():
            stream.Enthalpy.append(elem*self.Qdot)

        stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowOp(stream.Enthalpy, stream.SpecHeatCap)
        stream.HeatTransferCoeff = 5000
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream.EnthalpyNom)
        stream.OperatingHours = self.periodSchedule.getOperationHoursPerYear()
        self.MaintainanceStream.append(stream)


    def generateWHAboveCondStream(self):
        """
        Generate Waste Heat Above Cond Stream
        TODO Correct to Waste Heat
        """
        stream = Stream()
        stream.FluidDensity = self.FluidDensity
        stream.StartTemp.setAverageTemperature(self.PTOutflow)
        stream.EndTemp.setAverageTemperature(self.Tcond)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = self.VaporCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
        if self.VOutflowCycle != None:
            stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowWH(stream.FluidDensity, VOutflowCycle = self.VOutflowCycle)
        elif self.mOutflowNom != None:
            stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowWH(stream.FluidDensity, mOutflowNom = self.mOutFlowNom)
        stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        stream.HeatTransferCoeff = 100
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream.EnthalpyNom)
        stream.OperatingHours = self.periodSchedule.getOutflowHoursPerYear()
        self.WasteHeatAC.append(stream)

    def generateWHCondStream(self):
        """
        Generate Waste Heat Cond Stream
        TODO Correct to Waste Heat
        """
        stream = Stream()
        stream.FluidDensity = 1000
        stream.StartTemp.setAverageTemperature(self.Tcond)
        stream.EndTemp.setAverageTemperature(self.Tcond-0.1)
        stream.Type = self.getProcessStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())

        stream.SpecEnthalpy = self.LatentHeat
        stream.SpecHeatCap = stream.SpecEnthalpy*10
        stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowWHCond(VOutflowCycle = self.VOutflowCycle, FluidDensity = stream.FluidDensity, XOutFlow = self.XOutFlow, mOutflowNom = self.mOutFlowNom)
        stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        stream.HeatTransferCoeff = 10000
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream.EnthalpyNom)
        stream.OperatingHours = self.periodSchedule.getOutflowHoursPerYear()
        self.WasteHeatC.append(stream)

    def generateWHBelowCondStream(self):
        """
        Generate Waste heat below Cond Stream
        TODO Correct to Waste Heat
        """
        stream = Stream()
        stream.FluidDensity = self.FluidDensity
        stream.StartTemp.setAverageTemperature(self.Tcond)
        stream.EndTemp.setAverageTemperature(self.PTFinal)
        stream.Type = self.getStreamType(stream.StartTemp.getAvg(), stream.EndTemp.getAvg())
        stream.SpecHeatCap = self.FluidCp
        stream.SpecEnthalpy = self.getSpecificEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap)
        if self.VOutflowCycle != None:
            stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowWH(stream.FluidDensity, VOutflowCycle = self.VOutflowCycle)
        elif self.mOutflowNom != None:
            stream.MassFlowAvg, stream.MassFlowVector = self.massFlow.getMassFlowWH(stream.FluidDensity, mOutflowNom = self.mOutFlowNom)
        stream.EnthalpyNom, stream.EnthalpyVector = self.getEnthalpy(stream.EndTemp.getAvg(), stream.StartTemp.getAvg(), stream.SpecHeatCap, stream.MassFlowVector, stream.MassFlowAvg)
        stream.HeatTransferCoeff = 5000
        stream.HeatCap = self.getHeatCapacity(stream.MassFlowAvg, stream.SpecHeatCap)
        stream.HotColdType = self.getHotCold(stream.EnthalpyNom)
        stream.OperatingHours = self.periodSchedule.getOutflowHoursPerYear()
        self.WasteHeatBC.append(stream)

    def getAllStreams(self):
        #streamlist = [self.StUpStream, self.CircStream, self.MaintainanceStream]
        return self.StUpStream, self.CircStreamrc, self.MaintainanceStream


class ProcessMassFlow():
    def getMassFlowOpVector(self, EnthalpyVector, SpecHeatCap, StartTemp, EndTemp):
        m_vector = []
        for elem in EnthalpyVector:
            m_vector.append(elem/SpecHeatCap*(EndTemp-StartTemp))
        return m_vector

    def getMassFlowOpNom(self, EnthalpyNom, SpecHeatCap, StartTemp, EndTemp):
        m_average = EnthalpyNom/SpecHeatCap*(EndTemp-StartTemp)
        return m_average

    def getMassFlowStUpNom(self, VolProcMed, FluidDensity):
         m_nom = VolProcMed * FluidDensity/((self.periodSchedule.startup)*3600)
         return m_nom

    def getMassFlowCircNom(self, FluidDensity, VInflowCycle = None, mInflowNom = None, VInflowDay = None, HperDay = None):

        if VInflowCycle != None:
            m_average = VInflowCycle*FluidDensity/(self.periodSchedule.inflow*3600)
        elif mInflowNom != None:
            m_average = mInflowNom/3600
        elif VInflowDay != None and HperDay != None:
            m_average = VInflowDay*FluidDensity/(HperDay*3600)
        else:
            # TODO Throw Exception
            m_average = 0

        return m_average


class ContinuousMassFlow(ProcessMassFlow):

    def __init__(self, periodSchedule = None):
        self.periodSchedule = periodSchedule

    def getMassFlowStUp(self, VolProcMed, FluidDensity):
        m_vector = []
        yearlyContStartUp = self.periodSchedule.getYearlyContinuousStartupProfile()
        m_average = VolProcMed * FluidDensity/((self.periodSchedule.startup)*3600)

        for elem in yearlyContStartUp:
            m_vector.append(m_average*elem)
        return m_average, m_vector


    def getMassFlowCirc(self, FluidDensity, VInflowCycle = None, mInflowNom = None, VInflowDay = None, HperDay = None):

        m_vector = []
        yearlyContinuousInflow = self.periodSchedule.getYearlyContinuousInflowProfile()

        if VInflowCycle != None:
            m_average = VInflowCycle*FluidDensity/(self.periodSchedule.getOperationHoursPerDay()*3600)
        elif mInflowNom != None:
            m_average = mInflowNom/3600
        elif VInflowDay != None and HperDay != None:
            m_average = VInflowDay*FluidDensity/(self.periodSchedule.getOperationHoursPerDay()*3600)
        else:
            # TODO Throw Exception
            m_average = 0

        for elem in yearlyContinuousInflow:
            m_vector.append(m_average*elem)
        return m_average, m_vector



    def getMassFlowWHCond(self, VOutflowCycle, FluidDensity, XOutFlow = None, mOutflowNom = None):
        return self.getMassFlowWH(FluidDensity, VOutflowCycle, mOutflowNom)


    def getMassFlowWH(self, FluidDensity, VOutflowCycle = None, mOutflowNom = None):
        """
	    Calculate Mass Flow WH

        :param VOutflowCycle: Data base value of VOutflowCycle
        :type  VOutflowCycle: Double
        :param mOutflowNom: Data base value of mOutflowNom
        :type  mOutflowNom: Double

        :returns: List of Massflow values
        :rtype: Float List
        """
        
        if VOutflowCycle != None:
            m_average = VOutflowCycle*FluidDensity/(self.periodSchedule.getOperationHoursPerDay()*3600)
        elif mOutflowNom != None:
            m_average = mOutflowNom/3600
        else:
            m_average = 0
            # TODO add exception
        m_vector = []
        yearlyContOutflow = self.periodSchedule.getYearlyContinuousOutflowProfile()
        for elem in yearlyContOutflow:
            m_vector.append(m_average*elem)
        return m_average, m_vector

    def getStUpOperatingHours(self):
        return self.periodSchedule.getNumberOfBatchesPerYear()*self.periodSchedule.startup

class BatchMassFlow(ProcessMassFlow):

    def __init__(self, periodSchedule = None):
        self.periodSchedule = periodSchedule


    def getMassFlowCirc(self, FluidDensity, VInflowCycle = None, mInflowNom = None, VInflowDay = None, HperDay = None):
        # m_average = VInflowCycle*FluidDensity/(Hbatch*3600) or mInflowNom/3600 or VInflowDay*FluidDensity/(HperDay*3600)
        # m_vector = m_average*getYearlyContinuousInflowProfile

        m_vector = []
        yearlyContinuousInflow = self.periodSchedule.getYearlyBatchInflowProfile()

        if VInflowCycle != None:
            m_average = VInflowCycle*FluidDensity/(self.periodSchedule.inflow*3600)
        elif mInflowNom != None:
            m_average = mInflowNom/3600
        elif VInflowDay != None and HperDay != None:
            m_average = VInflowDay*FluidDensity/(HperDay*3600)
        else:
            # TODO Throw Exception
            m_average = 0


        for i in xrange(len(yearlyContinuousInflow)):
            m_vector.append(m_average*yearlyContinuousInflow[i])
        return m_average, m_vector


    def getMassFlowWH(self, FluidDensity, VOutflowCycle = None, mOutflowNom = None):
        """
	Calculate Mass Flow WH

        :param VOutflowCycle: Data base value of VOutflowCycle
        :type  VOutflowCycle: Double
        :param mOutflowNom: Data base value of mOutflowNom
        :type  mOutflowNom: Double

        :returns: List of Massflow values
        :rtype: Float List
        """
        # m_average = Qdot/(FluidCp*((PT+0,1)-PT))
        # m_vector = m_average*getYearlyBatchOutflowProfile
        if VOutflowCycle != None:
            m_average = VOutflowCycle*FluidDensity/(self.periodSchedule.outflow*3600)
        elif mOutflowNom != None:
            m_average = mOutflowNom/3600
        else:
            m_average = 0
            # TODO add exception
        m_vector = []
        yearlyBatchOutflow = self.periodSchedule.getYearlyBatchOutflowProfile()
        for i in xrange(len(yearlyBatchOutflow)):
            m_vector.append(m_average*yearlyBatchOutflow[i])
        return m_average, m_vector


    def getMassFlowWHCond(self, VOutflowCycle, FluidDensity, XOutFlow = None, mOutflowNom = None):
        if XOutFlow > 0:
            m_average =VOutflowCycle * FluidDensity/(self.periodSchedule.outflow*3600)*XOutFlow
        else:
            m_average = VOutflowCycle*FluidDensity/(self.periodSchedule.outflow*3600)
        m_vector = []
        yearlyBatchOutflow = self.periodSchedule.getYearlyBatchOutflowProfile()
        for elem in yearlyBatchOutflow:
            m_vector.append(elem*m_average)
        return m_average, m_vector

    def getStUpOperatingHours(self):
        return self.periodSchedule.getNumberOfBatchesPerYear()*self.periodSchedule.startup






if __name__ == "__main__":
    print "Hello World";
