from einstein.modules.energystreams.Stream import *

__author__="Andre Rattinger"
__date__ ="$01.08.2010 11:43:11$"

class HXProposal():
    streams = []
    streams_below_pinch_cold = []
    streams_below_pinch_hot = []
    streams_above_pinch_cold = []
    streams_above_pinch_hot = []
    
    # Matches
    match_below_cold = []
    match_below_hot = []
    match_above_cold = []
    match_above_hot = []
    
    consider_existing_hx = False
    pinch_temperature = -999
    pinch_temperature_lower = -994
    pinch_temperature_upper = -999
    dT = 5
    
    def __init__(self, pinch_temperature_upper, pinch_temperature_lower, consider_existing_hx = False, dT=5 ):
        self.streams_below_pinch_cold = []
        self.streams_below_pinch_hot = []
        self.streams_above_pinch_cold = []
        self.streams_above_pinch_hot = []
        self.pinch_temperature_upper = pinch_temperature_upper
        self.pinch_temperature_lower = pinch_temperature_lower
        self.consider_existing_hx = consider_existing_hx
        self.dT = dT
        self.__getStreams()
        
    def __getStreams(self):
        try:
            self.streams = Status.int.NameGen.getAllStreams()
        except:
            self.streams = []
            
    def start(self):
        self.__splitAboveBelowPinch()
        self.sortStreamsPerMCP()
        self.matchStreams()
    
    def sortStreams(self):
        self.streams_above_pinch_cold = self.sortStreamWithMCP(self.streams_above_pinch_cold)
        self.streams_above_pinch_hot  = self.sortStreamWithMCP(self.streams_above_pinch_hot)
        self.streams_below_pinch_cold = self.sortStreamWithMCP(self.streams_below_pinch_cold)
        self.streams_below_pinch_hot  = self.sortStreamWithMCP(self.streams_below_pinch_hot)
        
    def sortStreamWithMCP(self, streamlist):
        return sorted(streamlist, key=lambda stream: stream.MassFlowAvg*stream.SpecHeatCap)
        
    
    def matchStreams(self):
        
        MAXRUN = len(self.streams_above_pinch_hot)*2
        run = 0
        while len(self.streams_above_pinch_cold) > 0 and len(self.streams_above_pinch_hot) > 0:
            if run >= MAXRUN:
                break
            run +=1
            # Select Hot Stream with maximal m*cp
            hs = self.streams_above_pinch_hot[-1]
            mcp_hot = hs.MassFlowAvg * hs.SpecHeatCap
            # Find cold stream with closest m*cp value
            index = -1
            diff = 1e10 
            for i in xrange(len(self.streams_above_pinch_cold)):
                mcp_cold = self.streams_above_pinch_cold[i].MassFlowAvg * self.streams_above_pinch_cold[i].SpecHeatCap 
                if abs(mcp_hot - mcp_cold) < diff:
                    diff = abs(mcp_hot-mcp_cold)
                    index = i
        
            mcp_cold = self.streams_above_pinch_cold[index].MassFlowAvg * self.streams_above_pinch_cold[index].SpecHeatCap 
            
            # Check: mcp_hot < mcp_cold
            if mcp_hot <= mcp_cold:
                # match
                self.match_above_cold.append(self.streams_above_pinch_cold[i])
                self.match_above_hot.append(self.streams_above_pinch_hot[-1])
                del self.streams_above_pinch_cold[i]
                del self.streams_above_pinch_hot[-1]
            else:
                pass
        
    
    def printSplittedStreams(self):
        
        print "----------Streams Above Pinch----------"
        for stream in self.streams_above_pinch:
            stream.printStream()
        print "----------End Stream Above Pinch-------"
        print "----------Streams Below Pinch----------"
        for stream in self.streams_below_pinch:
            stream.printStream()
        print "----------End Stream Below Pinch-------"            
            
        
    
#        def __init__(self, MediumID=None, StartTemp=None, EndTemp=None, HeatCap=None, 
#                 HotColdType=None, MassFlowAvg=None, SpecHeatCap=None, SpecEnthalpy=None,
#                 EnthalpyNom=None, HeatTransferCoeff=None, FluidDensity=None, OperatingHours=None,
#                 id=None, name=None, Source=None, BaseValues=None, DBID=None, DBType=None):

    def __splitAboveBelowPinch(self):
        if self.consider_existing_hx == False:
            for stream in self.streams:
                if stream.HotColdType == "Cold" or stream.HotColdType == "Sink":
                    
                    if stream.EndTemp.getAvg() < self.pinch_temperature_lower:
                        print "Call Cold Below", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        bp = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=stream.EndTemp.getAvg(), 
                                    name=stream.name)
                        bp.copyStreamAttributes(stream)
                        self.streams_below_pinch_cold.append(bp)
                    elif stream.StartTemp.getAvg() > self.pinch_temperature_lower:
                        print "Call Cold Above", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        ap = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=stream.EndTemp.getAvg(), 
                                    name=stream.name)
                        ap.copyStreamAttributes(stream)
                        self.streams_above_pinch_cold.append(ap)
                    else:
                        print "Call Cold Both", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        bp = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=self.pinch_temperature_lower, 
                                    name="Splitted Sink Stream Below Pinch")
                        bp.copyStreamAttributes(stream)
                        self.streams_below_pinch_cold.append(bp)
                        ap = Stream(StartTemp=self.pinch_temperature_lower, EndTemp=stream.EndTemp.getAvg(), 
                                    name="Splitted Sink Stream Above Pinch")
                        ap.copyStreamAttributes(stream)
                        self.streams_above_pinch_cold.append(ap)
                    
                    
                elif stream.HotColdType == "Hot" or stream.HotColdType == "Source":
                    if stream.EndTemp.getAvg() > self.pinch_temperature_upper:
                        print "Call Hot Above", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        ap = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp = stream.EndTemp.getAvg(), name=stream.name)
                        ap.copyStreamAttributes(stream)
                        self.streams_above_pinch_hot.append(ap)
                    elif stream.StartTemp.getAvg() < self.pinch_temperature_upper:
                        print "Call Hot Below", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        bp = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=stream.EndTemp.getAvg(), name=stream.name)
                        bp.copyStreamAttributes(stream)
                        self.streams_below_pinch_hot.append(bp)
                    else:    
                        print "Call Hot Both", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        bp = Stream(StartTemp=self.pinch_temperature_upper, EndTemp=stream.EndTemp.getAvg(), 
                                    name="Splitted Souce Stream Below Pinch")
                        bp.copyStreamAttributes(stream)
                        self.streams_below_pinch_hot.append(bp)
                        ap = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=self.pinch_temperature_upper, 
                                    name="Splitted Source Stream Above Pinch")
                        ap.copyStreamAttributes(stream)
                        self.streams_above_pinch_hot.append(ap)
                
        else:
            # Consider Existing HX
            pass
    
    
if __name__ == "__main__":
    print "HX Proposal Module";
