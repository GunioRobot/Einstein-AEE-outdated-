
__author__="Andre Rattinger"
__date__ ="$01.08.2010 11:43:11$"

class HXProposal():
    streams = []
    streams_below_pinch = []
    streams_above_pinch = []
    consider_existing_hx = False
    pinch_temperature = -999
    
    def __init__(self, pinch_temperature, consider_existing_hx = False):
        self.streams_below_pinch = []
        self.streams_above_pinch = []
        self.pinch_temperature = pinch_temperature
        self.consider_existing_hx = consider_existing_hx
        self.__getStreams()
        
    def __getStreams(self):
        try:
            self.streams = Status.int.NameGen.getAllStreams()
        except:
            self.streams = []
            
    def start(self, PinchTemperature):
        self.__splitAboveBelowPinch()
    
    
    def __splitAboveBelowPinch(self):
        if self.consider_existing_hx:
            for stream in self.streams:
                if stream.HotColdType == "Cold" or stream.HotColdType == "Sink":
                    pass
                elif stream.HotColdType == "Hot" or stream.HotColdType == "Source":
                    pass
            
        else:
            pass
    
    
if __name__ == "__main__":
    print "HX Proposal Module";
