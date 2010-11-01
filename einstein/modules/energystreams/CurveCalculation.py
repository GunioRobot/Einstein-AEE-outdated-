from einstein.GUI.status import *
from einstein.modules.dataHR import *
from einstein.modules.schedules import intervalsOnOffUnit
from sets import Set
__author__="Andre Rattinger"
__date__ ="$25.09.2010 01:03:40$"


class CurveCalculation():

    dTmin = None
    streams = []
    sort_for_section = None
    sections_only_hot = None
    sections_only_cold = None
    sections_hot = None
    sections_cold = None
    hot_cp_section = None
    cold_cp_section = None
    only_hot_cp_section = None
    only_cold_cp_section = None
    difference = None
    pre_heat_input = None
    pre_heat_output = None
    heat_input = None
    heat_output = None
    gcc_arrows = None
    ccc_arrows = None
    hcc_arrows = None


    def __init__(self):
        self.dTmin = 5
        self.sort_for_section = SortedList()
        self.sections_only_hot = SortedList()
        self.sections_only_cold = SortedList()
        self.sections_hot = []
        self.sections_cold = []
        self.hot_cp_section = []
        self.cold_cp_section = []
        self.only_hot_cp_section = []
        self.only_cold_cp_section = []
        self.difference = []
        self.pre_heat_input = []
        self.pre_heat_output = []
        self.heat_input = []
        self.heat_output = []
        self.gcc_arrows = []
        self.ccc_arrows = []
        self.hcc_arrows = []
        self.signal_pinch_temp = True
        self.pinch_temperature = -999
#        self.__getStreams()

    def __getStreams(self):
        try:
            self.streams = Status.int.NameGen.getAllStreams()
        except:
            self.streams = []
        
    def calc(self):
        self.__calculateIntervals()
        
    def __calculateIntervals(self):
        self.ColdIntervals = []
        self.HotIntervals = []
        self.seperateHotColdStreams(self.streams)
        
        self.ColdIntervals = self.getTemperatureLevels(self.ColdStreams)
        self.HotIntervals = self.getTemperatureLevels(self.HotStreams)

        print "HotIntervals: ", str(self.HotIntervals)
        print "ColdIntervals: ", str(self.ColdIntervals)
        
        self.fillTemperatureLevelsCS(self.ColdIntervals, self.ColdStreams)
        self.fillTemperatureLevelsHS(self.HotIntervals, self.HotStreams)
        
        self.calculateVectors(self.ColdIntervals)
        self.calculateVectors(self.HotIntervals)
        
        self.CCC = self.setColdCurves(self.ColdIntervals)
        self.HCC = self.setHotCurves(self.HotIntervals)
        self.GCC = Curve("HCC")
        if Status.int.hrdata == None:
            Status.int.hrdata = HRData(Status.PId,Status.ANo)
        
        Status.int.hrdata.curves = [self.CCC, self.HCC, self.GCC]
        
    def setHotCurves(self, Intervals):
        curve = Curve("HCC")
        curve.X.append(0)
        curve.Y.append(0)
        
#        print "Hot Curves"
        for interval in Intervals:
            curve.X.append(curve.X[-1]+interval.H)
            curve.Y.append(curve.Y[-1]+abs(interval.StartTemp-interval.EndTemp))
#            print "X: ", str(curve.X[-1]), "Interval: ", str(interval.CP)
#            print "Y: ", str(curve.Y[-1]), "diffTemp: ", str(abs(interval.StartTemp-interval.EndTemp))

        return curve
#        Status.int.hrdata.curves[1] = curve
        
    def setColdCurves(self, Intervals):
        curve = Curve("CCC")
        
        curve.X.append(0)
        curve.Y.append(0)
        
#        print "Cold Curves"
        for interval in Intervals:
            curve.X.append(curve.X[-1]+interval.H)
            curve.Y.append(curve.Y[-1]+abs(interval.StartTemp-interval.EndTemp))
#            print "X: ", str(curve.X[-1]), "Interval: ", str(interval.CP)
#            print "Y: ", str(curve.Y[-1]), "diffTemp: ", str(abs(interval.StartTemp-interval.EndTemp))

        return curve
#        Status.int.hrdata.curves[0] = curve

    def calculateVectors(self, Intervals):
        for i in xrange(len(Intervals)):
            Intervals[i].calculateCP()

    def fillTemperatureLevelsCS(self, Intervals, streams):
        
        for interval in Intervals:
            for stream in streams:
                if stream.StartTemp.getAvg() <= interval.StartTemp and \
                    stream.EndTemp.getAvg() >= interval.EndTemp:
                    interval.Streams.append(stream)

    def fillTemperatureLevelsHS(self, Intervals, streams):
        
        for interval in Intervals:
            for stream in streams:
                if stream.StartTemp.getAvg() >= interval.StartTemp and \
                    stream.EndTemp.getAvg() <= interval.EndTemp:
                    interval.Streams.append(stream)
                

    def seperateHotColdStreams(self, streams):
        self.HotStreams = []
        self.ColdStreams = []
        for stream in streams:
            if stream.HotColdType == "Hot" or stream.HotColdType == "Source":
                self.HotStreams.append(stream)
            elif stream.HotColdType == "Cold" or stream.HotColdType == "Sink":
                self.ColdStreams.append(stream)
            else:
                print "Cant find Stream hot or Cold Type"
        
    def getTemperatureLevels(self, streams):
        lvl = []
        for stream in streams:        
            lvl.append(stream.StartTemp.getAvg())
            lvl.append(stream.EndTemp.getAvg())
            
        lvl = list(Set(lvl))
        lvl.sort()
        Intervals = []
        for i in xrange(len(lvl)-1):
            Intervals.append(Interval(lvl[i], lvl[i+1]))
        
        return Intervals
    
    def shiftCurve(self, x_curve, y_curve, x_shift, y_shift):
        for i in xrange(len(x_curve)):
            x_curve[i] += x_shift
        for i in xrange(len(y_curve)):
            y_curve[i] += y_shift
    
    
    def shift(self, x_static, y_static, x_shift, y_shift, dT):
        pinchtemp = -999
        index = -1
        for i in xrange(len(x_shift)-0): #-0
            shift, index = self.shiftPointToVector(x_static, y_static, x_shift[i], y_shift[i], dT)
            #print "Shift:", str(shift), "on x = ", str(x_shift[i]), "and y = ", str(y_shift[i])
            if shift > 0:
                self.shiftCurve(x_shift, y_shift, shift, 0)
            shift, index = self.shiftPointToVector(x_static, y_static, x_shift[i], y_shift[i], dT)
            if shift > 0:
                self.shiftCurve(x_shift, y_shift, shift, 0)
            if shift !=0:
                pinchtemp = y_shift[i]
                index = i
            #print x_shift, y_shift        
        #print pinchtemp
        return pinchtemp
    
    def shiftPointToVector(self, x_vector, y_vector, x_point, y_point, dT):

        #print
        index = self.findCorrespondingLineIndexForX(x_point, x_vector)
        #print "index:", str(index)
        #print "from:", "(", str(x_vector[index]), "/", str(y_vector[index]), ")", "to:", "(", str(x_vector[index+1]), "/", str(y_vector[index+1]), ")"
        #print "x_point/y_point:", "(", str(x_point), "/", str(y_point), ")"
    
        if index == -1:
            return 0, 0
    
        if x_point == x_vector[index] and y_point == y_vector[index]:
            return 0, 0
    
        # Calculate Vector
        xv = x_vector[index+1] - x_vector[index]
        yv = y_vector[index+1] - y_vector[index]
    
        #print "index:", str(index)
        #print "xv/yv:", "(", str(xv), "/", str(yv), ")"
        
        # Get coordinates relativ to zero (zero is the starting point of the vector)
        xpn = x_point - x_vector[index]
        ypn = y_point - y_vector[index]
    
        #print "xpn/ypn:", "(", str(xpn), "/", str(ypn), ")"
    
        # Shorten vector to length xp-xn
        xk = abs(xv-xpn)
        yk = xk*yv/xv
    
        #print "xk/yk:", "(", str(xk), "/", str(yk), ")"
    
        # Move point to xpn = xv
        xz = xpn-xk
        yz = ypn-yk
    
        #print "xz/yz:", "(", str(xz), "/", str(yz), ")"
    
        if yz >= ypn:
            # do move to pinch temp
            
            return 0, -1
        else:
            xe = ypn*xv/yv
            ye = ypn
            #print "xe/ye:", "(", str(xe), "/", str(ye), ")"
            return x_vector[index]+xe-x_point, 0
    
    def findCorrespondingLineIndexForX(self, x_point, x_vector):
        index = -1
        for i in xrange(len(x_vector)-1):
            if x_point < x_vector[i+1]:
                index=i
                break
        return index
    
    def shiftTemperatures(self, x_hcc, y_hcc, x_ccc, y_ccc, dT):
        self.shiftCurve(x_hcc, y_hcc, 0, dT/2)
        self.shiftCurve(x_ccc, y_ccc, 0, -dT/2)
    
    def shiftToPinch(self, dT):
        xh = self.HCC.X
        yh = self.HCC.Y
        xc = self.CCC.X
        yc = self.CCC.Y
        
        self.shiftCurve(xc, yc, -xc[0], 0)
        self.pinch_temperature = self.shift(xh, yh, xc, yc, dT)
        self.pinchupper = self.pinch_temperature + dT/2
        self.pinchlower = self.pinch_temperature - dT/2
        self.shiftTemperatures(xh, yh, xc, yc, dT)
    
    
    def calculate(self):
        self.__getStreams()

        self.__collectTemperaturesFromStreamForCalculation()
        self.__seperateToCorrectSectionByTemperature()
        self.__calculateMCPforHCC()
        self.__calculateMCPforCCC()
        self.__calculateStreamDataEntryTable()
        self.__calculatePreHeatInputOutput()
        self.__calculatePinchTemperature()
        self.__calculateGCCArrows()
        self.__calculateHCCArrows()
        self.__calculateCCCArrows()
        self.__calculateGCCResults()
        self.__calculateHCCResults()
        self.__calculateCCCResults()
        
        self.setDataCurves()
        self.calc()
        
    def printResults(self):
        print "Sort Section", str(self.sort_for_section)
        print "Sections only hot", str(self.sections_only_hot)
        print "Sections only cold", str(self.sections_only_cold)
        print "Sections Hot" , str(self.sections_hot)
        print "Sections Cold" , str(self.sections_cold)
        print "Hot cp Section" , str(self.hot_cp_section)
        print "Cold cp Section" , str(self.cold_cp_section)
        print "only hot cp" , str(self.only_hot_cp_section)
        print "only cold cp" , str(self.only_cold_cp_section)
        print "diff" , str(self.difference)
        print "pre heat input" , str(self.pre_heat_input)
        print "pre heat output" , str(self.pre_heat_output)
        print "heat input" , str(self.heat_input)
        print "heat output" , str(self.heat_output)
        
        print "GCC Arrows: "
        for elem in self.gcc_arrows:
            print elem.MCP, elem.StartTemp, elem.EndTemp, elem.Direction, elem.StartMcpPoint, elem.kw

        print "CCC Arrows: "
        for elem in self.ccc_arrows:
            print elem.MCP, elem.StartTemp, elem.EndTemp, elem.kw
        print "HCC Arrows"
        for elem in self.hcc_arrows:
            print elem.MCP, elem.StartTemp, elem.EndTemp, elem.kw
     

    def __collectTemperaturesFromStreamForCalculation(self):
        current_pos = 0
        
        for stream in self.streams:
            self.__classifyStreamForHotColdSideByTemperature(stream, current_pos)
            self.__classifyStreamForTotalSectionByTemperature(stream, current_pos)
            current_pos+=1


    def __classifyStreamForTotalSectionByTemperature(self, stream, current_pos):
        startTemp = stream.StartTemp.getAvg()
        endTemp = stream.EndTemp.getAvg()

        print stream.name, startTemp, endTemp, stream.HeatCap, stream.HotColdType
        if(not self.sort_for_section.containsKey(startTemp)):
            self.sort_for_section.append(startTemp, current_pos)

        if(not self.sort_for_section.containsKey(endTemp)):
            self.sort_for_section.append(endTemp, current_pos)

    def __classifyStreamForHotColdSideByTemperature(self, stream, current_pos):
        startTemp = stream.StartTemp.getAvg()
        endTemp = stream.EndTemp.getAvg()

        if stream.HotColdType == "Hot" or stream.HotColdType == "Source":
            if not self.sections_only_hot.containsKey(endTemp):
                self.sections_only_hot.append(endTemp, current_pos)

            if not self.sections_only_hot.containsKey(startTemp):
                self.sections_only_hot.append(startTemp, current_pos)
        else:
            if not self.sections_only_cold.containsKey(endTemp):
                self.sections_only_cold.append(endTemp, current_pos)

            if not self.sections_only_cold.containsKey(startTemp):
                self.sections_only_cold.append(startTemp, current_pos)



    def __seperateToCorrectSectionByTemperature(self):
        old_temp = -10000

        for i in xrange(self.sort_for_section.count):
            if self.sort_for_section.Keys(i) != old_temp:
                if self.streams[self.sort_for_section.Values(i)].HotColdType == "Cold" or \
                    self.streams[self.sort_for_section.Values(i)].HotColdType == "Sink":
                    self.sections_cold.append(self.sort_for_section.Keys(i))
                    self.sections_hot.append(self.sort_for_section.Keys(i) + self.dTmin)
                else:
                    self.sections_cold.append(self.sort_for_section.Keys(i) - self.dTmin)
                    self.sections_hot.append(self.sort_for_section.Keys(i))
            old_temp = self.sort_for_section.Keys(i)


        self.sections_cold.sort()
        self.sections_hot.sort()


    def __calculateMCPforHCC(self):

        for i in xrange(self.sections_only_hot.count):
            cp_hot = 0

            for j in xrange(len(self.streams)):
                if self.streams[j].HotColdType == "Hot" or self.streams[j].HotColdType == "Source":
                    if self.streams[j].StartTemp.getAvg() > self.sections_only_hot.Keys(i-1) and \
                        self.streams[j].EndTemp.getAvg() < self.sections_only_hot.Keys(i):
                        cp_hot += self.streams[j].HeatCap

            self.only_hot_cp_section.append(cp_hot)

    def __calculateMCPforCCC(self):

        for i in xrange(self.sections_only_cold.count):
            cp_cold = 0

            for j in xrange(len(self.streams)):
                if self.streams[j].HotColdType == "Cold" or self.streams[j].HotColdType == "Sink":
                    if self.streams[j].EndTemp.getAvg() > self.sections_only_cold.Keys(i-1) and \
                        self.streams[j].StartTemp.getAvg() < self.sections_only_cold.Keys(i):
                        cp_cold += self.streams[j].HeatCap

            self.only_cold_cp_section.append(cp_cold)

    def __calculateStreamDataEntryTable(self):

        for i in xrange(len(self.sections_cold)-1, 1, -1):
            dT = self.sections_cold[i] - self.sections_cold[i-1]
            cp_hot = 0
            cp_cold = 0

            for j in xrange(len(self.streams)):
                if self.streams[j].HotColdType == "Cold" or self.streams[j].HotColdType == "Sink":
                    if self.streams[j].EndTemp.getAvg() > self.sections_cold[i-1] and \
                        self.streams[j].StartTemp.getAvg() < self.sections_cold[i]:
                        cp_cold += self.streams[j].HeatCap
                else:
                    if self.streams[j].EndTemp.getAvg() > self.sections_hot[i-1] and \
                        self.streams[j].StartTemp.getAvg() < self.sections_hot[i]:
                        cp_hot += self.streams[j].HeatCap

            self.cold_cp_section.append(cp_cold)
            self.hot_cp_section.append(cp_hot)
            self.difference.append(dT * (cp_cold - cp_hot))

    def __calculatePreHeatInputOutput(self):
        if len(self.difference) > 0:
            self.pre_heat_input.append(0)
            self.pre_heat_output.append(self.difference[0] * -1)

        for i in xrange(len(self.difference)):
            self.pre_heat_input.append(self.pre_heat_output[i-1])
            self.pre_heat_output.append(self.pre_heat_input[i] - self.difference[i])

        minimum_heat_input = min(self.pre_heat_input) *-1

        for i in xrange(len(self.pre_heat_input)):
            self.heat_input.append(self.pre_heat_input[i] + minimum_heat_input)
            self.heat_output.append(self.pre_heat_output[i] + minimum_heat_input)

    def __calculatePinchTemperature(self):
        print self.heat_input
        print self.heat_output
        for i in xrange(len(self.heat_output)):
            if i+1 < len(self.heat_input):
                if self.heat_output[i]==0 and self.heat_input[i+1] == 0:
                    index = len(self.sections_hot) - 1 - (i+1)
                    self.pinch_temperature = (self.sections_hot[index] + self.sections_cold[index]) / 2

                    if self.signal_pinch_temp:
                        pass
        print "Pinch Temperature: ", str(self.pinch_temperature)

    def __calculateGCCArrows(self):
        temperature_index = len(self.sections_hot) - 1

        sum_mcp = 0
        if len(self.heat_input) > 0:
            sum_mcp = self.heat_input[0]

        for i in xrange(len(self.heat_input)):
            mcp = self.heat_output[i] - self.heat_input[i]

            arrow_gcc = ArrowGCC(abs(mcp), sum_mcp)

            if mcp < 0:
                arrow_gcc.setMinusDirection()
                sum_mcp -= arrow_gcc.MCP
            else:
                arrow_gcc.setPlusDirection()
                sum_mcp += arrow_gcc.MCP

            arrow_gcc.StartTemp = (self.sections_hot[temperature_index] \
                                + self.sections_cold[temperature_index])/2
            arrow_gcc.EndTemp = (self.sections_hot[temperature_index-1] \
                                + self.sections_cold[temperature_index-1])/2
            self.gcc_arrows.append(arrow_gcc)
            temperature_index-=1


    def __calculateHCCArrows(self):
        temperature_index = self.sections_only_hot.count-1

#        for i in xrange(self.sections_only_hot.count):
#            print i, ":", self.sections_only_hot.Keys(i)

        for i in xrange(len(self.only_hot_cp_section)):
#            print  "length", self.sections_only_hot.count, "temp_index", temperature_index
#            print "sections_only_hot", type(self.sections_only_hot.Keys[temperature_index])
            arrow_hcc = ArrowCCCHCC(self.only_hot_cp_section[i], \
                        self.sections_only_hot.Keys(temperature_index), \
                        self.sections_only_hot.Keys(temperature_index-1))
            self.hcc_arrows.append(arrow_hcc)
            temperature_index-=1



    def __calculateCCCArrows(self):
        temperature_index = 0
        print "only cold cp: ", str(self.only_cold_cp_section)
        for i in xrange(len(self.only_cold_cp_section)-1, 0, -1):
            arrow_ccc = ArrowCCCHCC(self.only_cold_cp_section[i], \
                        self.sections_only_cold.Keys(temperature_index), \
                        self.sections_only_cold.Keys(temperature_index+1))
            self.ccc_arrows.append(arrow_ccc)

            temperature_index+=1


    def __calculateGCCResults(self):
        for elem in self.gcc_arrows:
            elem.kw = elem.MCP * self.dTmin

    def __calculateHCCResults(self):
        for elem in self.hcc_arrows:
            elem.kw = elem.MCP * self.dTmin

    def __calculateCCCResults(self):
        for elem in self.ccc_arrows:
            elem.kw = elem.MCP * self.dTmin
            
            
    def setDataCurves(self):
        if Status.int.hrdata == None:
            Status.int.hrdata = HRData(Status.PId,Status.ANo)
            
        data = Status.int.hrdata
        
        ccc = self.appendCurve(self.ccc_arrows, "CCC")
#        self.appendEndCurve(ccc, self.ccc_arrows)
        self.hcc_arrows.reverse()
        hcc = self.appendCurve(self.hcc_arrows, "HCC")
#        hcc.Y[-1] = 0
#        self.appendEndCurve(hcc, self.hcc_arrows)
        gcc = self.appendCurve(self.gcc_arrows, "GCC")
#        self.appendEndCurve(gcc, self.gcc_arrows)
        
        data.curves = [ccc, hcc, gcc]
        Status.int.hrdata = data
        
    
        
    def appendCurve(self, curve_arrows, Name):
        
        curve = Curve(Name)
        curve.X.append(0)
        curve.Y.append(curve_arrows[0].StartTemp)
        
        for arrow in curve_arrows:
            curve.X.append(curve.X[-1]+arrow.MCP)
            curve.Y.append(arrow.StartTemp)


        return curve
    
#        curve.X.append(0)
#        curve.Y.append(0)
#        
##        print "Cold Curves"
#        for interval in Intervals:
#            curve.X.append(curve.X[-1]+interval.H)
#            curve.Y.append(curve.Y[-1]+abs(interval.StartTemp-interval.EndTemp))

    def appendStartCurve(self, curve, curve_arrows):
        for elem in curve_arrows:
            curve.X.append(elem.MCP)
            curve.Y.append(abs(elem.StartTemp-elem.EndTemp))
            
    def appendEndCurve(self, curve, curve_arrows):
        for elem in curve_arrows:
            curve.X.append(elem.MCP)
            curve.Y.append(elem.EndTemp)

class ArrowCCCHCC():
    MCP = None
    StartTemp = None
    EndTemp = None

    kw = None

    def __init__(self, MCP, StartTemp, EndTemp):
        self.MCP = MCP
        self.StartTemp = StartTemp
        self.EndTemp = EndTemp

class ArrowGCC():
    MCP = None
    StartTemp = None
    EndTemp = None
    Direction = None
    StartMcpPoint = None

    kw = None

    def __init__(self, MCP, StartMcpPoint):
        self.MCP = MCP
        self.StartMcpPoint = StartMcpPoint

    def setPlusDirection(self):
        self.Direction = 1

    def setMinusDirection(self):
        self.Direction = -1

class SortedListElement():
    Key = None
    Value = None

    def __init__(self, Key, Value):
        self.Key = Key
        self.Value = Value

    def __repr__(self):
        return repr((self.Key, self.Value))


class SortedList():
    list = []
    count = 0

    def __init__(self):
        list=[]
        self.count = 0

    def append(self, Key, Value):
        for elem in self.list:
            if Key == elem.Key:
                raise KeyError('Key already in use')

        self.list.append(SortedListElement(Key, Value))
        self.count+=1
        self.sort()

    def sort(self):
        self.list = sorted(self.list, key=lambda SortedListElement: SortedListElement.Key)

    def containsKey(self, Key):
        for elem in self.list:
            if Key == elem.Key:
                return True
        return False

    def Keys(self, i):
        return self.list[i].Key

    def Values(self, i):
        return self.list[i].Value

    def __repr__(self):
        replist=[]
        for elem in self.list:
            replist.append((elem.Key, elem.Value))
        return repr(replist)


class Interval():
    
    StartTemp = None
    EndTemp = None
    Streams = []
    H = None
    
    def __init__(self, StartTemp, EndTemp):
        self.StartTemp = StartTemp
        self.EndTemp = EndTemp
        self.Streams = []

    def calculateCP(self):
        self.H = 0
        dT = 0
        for stream in self.Streams:
#            self.H+=stream.EnthalpyNom
#            dT+= abs(stream.StartTemp.getAvg()-stream.EndTemp.getAvg())
#        self.H = (self.H * abs(self.StartTemp-self.EndTemp))/dT
        
#            self.H += stream.EnthalpyNom
            if abs(stream.StartTemp.getAvg()-stream.EndTemp.getAvg()) != 0:
                self.H += (stream.EnthalpyNom * abs(self.StartTemp-self.EndTemp))/abs(stream.StartTemp.getAvg()-stream.EndTemp.getAvg())
                
            
#            if abs(stream.StartTemp.getAvg()-stream.EndTemp.getAvg()) != 0:
#                self.H += stream.EnthalpyNom / abs(stream.StartTemp.getAvg()-stream.EndTemp.getAvg()) * abs(self.StartTemp-self.EndTemp)
            
#            print "H: " , str(stream.EnthalpyNom)

if __name__ == "__main__":
    print "Hello World";
