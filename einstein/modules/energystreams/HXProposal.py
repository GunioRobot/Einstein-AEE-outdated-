from einstein.modules.energystreams.Stream import *

__author__="Andre Rattinger"
__date__ ="$01.08.2010 11:43:11$"

class HXProposal():
    streams = []
    streams_below_pinch = []
    streams_above_pinch = []
    consider_existing_hx = False
    pinch_temperature = -999
    pinch_temperature_lower = -994
    pinch_temperature_upper = -999
    dT = 5
    
    def __init__(self, pinch_temperature_upper, pinch_temperature_lower, consider_existing_hx = False, dT=5 ):
        self.streams_below_pinch = []
        self.streams_above_pinch = []
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
                    
                    if stream.EndTemp.getAvg() < self.pinch_temperature - self.dT/2:
                        print "Call Cold Below", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        bp = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=stream.EndTemp.getAvg(), 
                                    name=stream.name)
                        bp.copyStreamAttributes(stream)
                        self.streams_below_pinch.append(bp)
                    elif stream.StartTemp.getAvg() > self.pinch_temperature - self.dT/2:
                        print "Call Cold Above", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        ap = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=stream.EndTemp.getAvg(), 
                                    name=stream.name)
                        ap.copyStreamAttributes(stream)
                        self.streams_above_pinch.append(ap)
                    else:
                        print "Call Cold Both", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        bp = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=self.pinch_temperature-self.dT/2, 
                                    name="Splitted Sink Stream Below Pinch")
                        bp.copyStreamAttributes(stream)
                        self.streams_below_pinch.append(bp)
                        ap = Stream(StartTemp=self.pinch_temperature-self.dT/2, EndTemp=stream.EndTemp.getAvg(), 
                                    name="Splitted Sink Stream Above Pinch")
                        ap.copyStreamAttributes(stream)
                        self.streams_above_pinch.append(ap)
                    
                    
                elif stream.HotColdType == "Hot" or stream.HotColdType == "Source":
                    if stream.EndTemp.getAvg() > self.pinch_temperature + self.dT/2:
                        print "Call Hot Above", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        ap = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp = stream.EndTemp.getAvg(), name=stream.name)
                        ap.copyStreamAttributes(stream)
                        self.streams_above_pinch.append(ap)
                    elif stream.StartTemp.getAvg() < self.pinch_temperature + self.dT/2:
                        print "Call Hot Below", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        bp = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=stream.EndTemp.getAvg(), name=stream.name)
                        bp.copyStreamAttributes(stream)
                        self.streams_below_pinch.append(bp)
                    else:    
                        print "Call Hot Both", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        bp = Stream(StartTemp=self.pinch_temperature+self.dT/2, EndTemp=stream.EndTemp.getAvg(), 
                                    name="Splitted Souce Stream Below Pinch")
                        bp.copyStreamAttributes(stream)
                        self.streams_below_pinch.append(bp)
                        ap = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=self.pinch_temperature+self.dT/2, 
                                    name="Splitted Source Stream Above Pinch")
                        ap.copyStreamAttributes(stream)
                        self.streams_above_pinch.append(ap)
                
        else:
            pass
    
    
if __name__ == "__main__":
    print "HX Proposal Module";
