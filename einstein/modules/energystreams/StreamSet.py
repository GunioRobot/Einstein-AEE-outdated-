# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="Andre Rattinger"
__date__ ="$04.08.2010 11:34:15$"

class StreamSet():
    """
    holds Streams that occur together and provides basic functionality for stream generation
    """

    FluidCp = None
    FluidCpMaintainance = None
    heatTransferMaintainance = None
    PT = None
    PTStartUp = None
    VolProcMed = None
    FluidDensity = None
    VaporCp = None
    PTInflowRec = None
    PTInflow = None
    VInflowCycle = None
    VOutflowCycle = None
    Hbatch = None
    Qdot = None

    def __init__(self, periodSchedule):
        self.periodSchedule = periodSchedule


    def autoinitProcessing(self):
        #self.processes = Status.prj.getProcesses()
        #self.fluids = Status.prj.getFluidDict()
        #self.fluids = Status.DB.dbfluid.sql_select()
        #"FluidName"+"='"+str(Q3[17])+"'"
        #ProcMedDBFluid_id
        #self.periodSchedule = PeriodSchedule(self.processes[0]['Process'])
        #self.periodSchedule.loadFromDB(4666)

        self.Holiday = True
        self.Tolerance = True
        #self.initValues()

    def initValues(self):
        """
        Just for Testing. Code will be replaced when the method  for real value initialisation is known.
        (Database, from Classes etc.)
        """
        if 1==1:
            return

        self.FluidCp = 4.19
        self.FluidCpMaintainance = 20.05 # Steam
        self.heatTransferMaintainance = 5000
        self.PT = 21
        self.PTStartUp = 12
        self.VolProcMed = 203663.3
        self.FluidDensity = 1000
        self.VaporCp = 5.98
        self.PTInflowRec = 37
        self.PTInflow = 35
        self.VInflowCycle = 400
        self.Hbatch = 10
        self.Qdot = 10 # Use QdotProc_c, _m, _s, _w ?
        self.mInflowNom = None
        self.VInflowDay = None
        self.HperDay = None
        self.PTOutflow = 1
        # CONSTANTS
        self.Tcond = 54.125

        #getFromDB
        self.DistribCircFlow = 100
        self.PercentRecirc = 5
        self.OffGasDensity = 0.5
        self.OffGasHeatCap = 1
        self.LatentHeatWater = 20
        self.LatentHeat = 15
        self.TExhaustGas = 40

        self.mOutFlowNom = 10
        self.VOutflowCycle = 10

    def getStreamType(self, StartTemp, EndTemp):
        """
	    Get Type of Stream

        :param StartTemp: Data base value of Start Temperature
        :type  StartTemp: Double
        :param EndTemp: Data base value of End Temperature
        :type  EndTemp: Double

        :returns: Type of Stream i.e. latent or sensible
        :rtype: String
        """
        if(StartTemp == EndTemp):
            return "latent"
        else:
            return "sensible"


    def getProcessStreamType(self, StartTemp, EndTemp):
        if StartTemp == EndTemp + 0.1 or StartTemp == EndTemp - 0.1:
            return 'latent'
        else:
            return 'sensible'

    def getHeatCapacity(self, massFlowMax, SpecHeatCap):
        """
	    Calculates Heat Capacity

        :param massFlow: Calculated Mass Flow values
        :type  massFlow: List of Double values
        :param SpecHeatCap: Specific Heat Capacity
        :type  SpecHeatCap: Double

        :returns: List of Float values
        """
#        heatCapacity = []
#        for elem in massFlow:
#            heatCapacity.append(elem*SpecHeatCap)
#        return heatCapacity
        return massFlowMax*SpecHeatCap


    def getHotCold(self, stream):
        """
	    Query if Medium is hot or cold

        :param stream: stream with calculated Temperature values
        :type  stream: class stream

        :returns: String i.e. Hot, Cold
        """


        if stream.StartTemp.getAvg() < stream.EndTemp.getAvg():
            return "Cold"
        else:
            return "Hot"


    def getSpecificEnthalpy(self, EndTemp, StartTemp, SpecHeatCap):
        """
	Calculates Specific Enthalpy

        :param StartTemp: Data base value of Start Temperature
        :type  StartTemp: Double
        :param EndTemp: Data base value of End Temperature
        :type  EndTemp: Double
        :param SpecHeatCap: Specific Heat Capacity
        :type  SpecHeatCap: Double

        :returns: Double
        """
        #print EndTemp, StartTemp, SpecHeatCap
        return abs(EndTemp-StartTemp)*SpecHeatCap


#    def getMassFlowOp(self, Enthalpy, SpecHeatCap):
#        m_vector = []
#        for elem in Enthalpy:
#            m_vector.append(elem/SpecHeatCap)
#        m_average = max(m_vector)
#        return m_average, m_vector

    def getEnthalpy(self, EndTemp, StartTemp, SpecHeatCap, massFlowVector, massFlowNom):
        """
	Calculates Enthalpy

        :param StartTemp: Data base value of Start Temperature
        :type  StartTemp: Double
        :param EndTemp: Data base value of End Temperature
        :type  EndTemp: Double
        :param SpecHeatCap: Specific Heat Capacity
        :type  SpecHeatCap: Double
        :param massFlow: Calculated List of Mass Flow values
        :type  massFlow: List of Double values

        :returns: List of Double values
        """
        enthalpy_nom = abs(EndTemp-StartTemp)*SpecHeatCap*massFlowNom
        enthalpy_v = []

        for elem in massFlowVector:
            enthalpy_v.append(abs(EndTemp-StartTemp)*SpecHeatCap*elem)
        return enthalpy_nom, enthalpy_v

    def getMassFlowVector(self, EnthalpyVector, SpecHeatCap, EndTemp, StartTemp):

        massFlowVector = []
        for elem in EnthalpyVector:
            if EndTemp.getAvg()== StartTemp.getAvg():
                massFlowVector.append(0)
            else:
                massFlowVector.append(elem/(SpecHeatCap*abs((EndTemp.getAvg()-StartTemp.getAvg()))))
        return massFlowVector


    def getEnthalpyNom(self, EndTemp, StartTemp, SpecHeatCap, massFlowNom):
        enthalpy_nom = abs(EndTemp-StartTemp)*SpecHeatCap*massFlowNom
        return enthalpy_nom

    def getMassVectorFromEnthalpy(self):
        pass

    def getHeatTransferCoefficient(self, FluidDensity):
        """
	    Get Heat Transfer Coefficient

        :param FluidDensity: Fluid Density
        :type  FluidDensity: Double

        :returns: Integer
        """
        if FluidDensity > 5:
            return 5000
        else:
            return 100

#    def getOperatingHours(self):
#        return self.periodSchedule.startup * self.periodSchedule.getNumberOfBatchesPerYear(self.Holiday, self.Tolerance)





if __name__ == "__main__":
    print "Hello World";
