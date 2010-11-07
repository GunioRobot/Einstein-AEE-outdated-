from einstein.modules.energystreams.Stream import *
from einstein.GUI.status import *
from einstein.modules.energystreams.StreamConstants import *

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
            self.streams = Status.int.StreamGen.getAllStreams()
        except:
            self.streams = []
            
    def start(self):
        self.__splitAboveBelowPinch()
        self.sortStreams()
        self.printToSplit()
        self.matchStreamsAbovePinch()
        self.matchStreamsBelowPinch()
        self.printSplits()
        self.convertMatchesToHX()
    
    def sortStreams(self):
        self.streams_above_pinch_cold = self.sortStreamWithMCP(self.streams_above_pinch_cold)
        self.streams_above_pinch_hot  = self.sortStreamWithMCP(self.streams_above_pinch_hot)
        self.streams_below_pinch_cold = self.sortStreamWithMCP(self.streams_below_pinch_cold)
        self.streams_below_pinch_hot  = self.sortStreamWithMCP(self.streams_below_pinch_hot)
        
    def sortStreamWithMCP(self, streamlist):
        return sorted(streamlist, key=lambda stream: stream.MassFlowAvg*stream.SpecHeatCap*stream.percent/100)
        
    
#        self.matchStreams(self.streams_above_pinch_cold, self.streams_above_pinch_hot, self.match_above_cold, self.match_above_hot)

    def matchStreamsAbovePinch(self):
        """
        match Streams
        """
        print "MATCH STREAMS:"
        # ABOVE PINCH
        MAXRUN = len(self.streams_above_pinch_hot)*2
        run = 0
        print "Above Pinch cold_8"
        for elem in self.streams_above_pinch_cold:
            print elem
        print "Above Pinch Hot_8"
        for elem in self.streams_above_pinch_hot:
            print elem    
        while len(self.streams_above_pinch_cold) > 0 and len(self.streams_above_pinch_hot) > 0:
            if run >= MAXRUN:
                break
            run +=1
            
            print "Above Pinch cold_9"
            for elem in self.streams_above_pinch_cold:
                print elem
            print "Above Pinch Hot_9"
            for elem in self.streams_above_pinch_hot:
                print elem    
            # Select Hot Stream with maximal m*cp
            hs = self.streams_above_pinch_hot[-1]
            mcp_hot = hs.MassFlowAvg * hs.SpecHeatCap * hs.percent/100
            # Find cold stream with closest m*cp value
            index = -1
            diff = 1e10 
            print "Above Pinch cold_9.5"
            for elem in self.streams_above_pinch_cold:
                print elem
            print "Above Pinch Hot_9.5"
            for elem in self.streams_above_pinch_hot:
                print elem    
            
            for i in xrange(len(self.streams_above_pinch_cold)):
                stream = self.streams_above_pinch_cold[i]
                mcp_cold = stream.MassFlowAvg * stream.SpecHeatCap * stream.percent/100
                if abs(mcp_hot - mcp_cold) < diff:
                    diff = abs(mcp_hot-mcp_cold)
                    index = i

            print "Above Pinch cold_10"
            for elem in self.streams_above_pinch_cold:
                print elem        
            print "Above Pinch Hot_10"
            for elem in self.streams_above_pinch_hot:
                print elem    
            stream = self.streams_above_pinch_cold[index]
            mcp_cold = stream.MassFlowAvg * stream.SpecHeatCap * stream.percent/100 
            
            print "Above Pinch cold_11"
            for elem in self.streams_above_pinch_cold:
                print elem
            print "Above Pinch Hot_11"
            for elem in self.streams_above_pinch_hot:
                print elem    
            # Check: mcp_hot < mcp_cold
            print mcp_hot, mcp_cold
            
            if mcp_hot <= mcp_cold:
                # match
                self.match_above_cold.append(self.streams_above_pinch_cold[index])
                self.match_above_hot.append(self.streams_above_pinch_hot[-1])
                del self.streams_above_pinch_cold[index]
                del self.streams_above_pinch_hot[-1]
            else:
                hs1 = self.streams_above_pinch_hot[-1]
                hs2 = Stream()
                hs2.copyStream(self.streams_above_pinch_hot[-1])
                cs1 = self.streams_above_pinch_cold[index]
                
                percent = hs1.percent
                if (cs1.MassFlowAvg*cs1.SpecHeatCap* cs1.percent) == 0:
                    del self.streams_above_pinch_cold[index]
                    print "Call: delete Stream before split"
                    continue
                print self.streams_above_pinch_hot[-1]
                print hs2
                print cs1
                self.streams_above_pinch_hot[-1].percent = ((percent/100) * (cs1.MassFlowAvg * cs1.SpecHeatCap * cs1.percent/100\
                                                                          / (hs1.MassFlowAvg * hs1.SpecHeatCap * hs1.percent/100)))*100
                hs2.percent = percent - hs1.percent
                
                print self.streams_above_pinch_hot[-1]
                print hs2
                self.streams_above_pinch_hot.append(hs2)
                self.sortStreamWithMCP(self.streams_above_pinch_hot)
        
           
    def matchStreamsBelowPinch(self):
        # BELOW PINCH
        MAXRUN = len(self.streams_below_pinch_hot)*2
        run = 0
        while len(self.streams_below_pinch_cold) > 0 and len(self.streams_below_pinch_hot) > 0:
            if run >= MAXRUN:
                break
            run +=1
            # Select Hot Stream with maximal m*cp
            hs = self.streams_below_pinch_hot[-1]
            mcp_hot = hs.MassFlowAvg * hs.SpecHeatCap
            # Find cold stream with closest m*cp value
            index = -1
            diff = 1e10 
            for i in xrange(len(self.streams_below_pinch_cold)):
                mcp_cold = self.streams_below_pinch_cold[i].MassFlowAvg * self.streams_below_pinch_cold[i].SpecHeatCap 
                if abs(mcp_hot - mcp_cold) < diff:
                    diff = abs(mcp_hot-mcp_cold)
                    index = i
        
            mcp_cold = self.streams_below_pinch_cold[index].MassFlowAvg * self.streams_below_pinch_cold[index].SpecHeatCap 
            
            # Check: mcp_hot < mcp_cold
            if mcp_hot >= mcp_cold:
                # match
                self.match_below_cold.append(self.streams_below_pinch_cold[index])
                self.match_below_hot.append(self.streams_below_pinch_hot[-1])
                del self.streams_below_pinch_cold[index]
                del self.streams_below_pinch_hot[-1]
            else:
                cs1 = self.streams_below_pinch_cold[index]
                cs2 = Stream()
                cs2.copyStream(self.streams_below_pinch_cold[index])
                hs1 = self.streams_below_pinch_hot[-1]
                
                percent = cs1.percent
                if (hs1.MassFlowAvg*hs1.SpecHeatCap) == 0:
                    del self.streams_below_pinch_hot[-1]
                    continue
                
                self.streams_below_pinch_cold[index].percent = ((percent/100) *(cs1.MassFlowAvg * cs1.SpecHeatCap * cs1.percent/100\
                                                                              /(hs1.MassFlowAvg * hs1.SpecHeatCap * hs1.percent/100)))*100
                cs2.percent = percent - cs1.percent

                self.streams_below_pinch_cold.append(cs2)
                self.sortStreamWithMCP(self.streams_below_pinch_cold)
                

    def convertMatchesToHX(self):
        
        for i in xrange(len(self.match_above_cold)):
            HXID = self.createNewHX("HX_AbovePinch_" +  str(i))
            hxpinch = HXPinchConnection(HXID, "HX_AbovePinch_" +  str(i))
            hconn = pinchTemp()
            cconn = pinchTemp()
            hconn.percentHeatFlow = self.match_above_hot[i].percent
            cconn.percentHeatFlow = self.match_above_cold[i].percent
            hconn.inletTemp = self.match_above_hot[i].StartTemp.getAvg()
            hconn.outletTemp = self.match_above_cold[i].EndTemp.getAvg()

            cconn.inletTemp = self.match_above_hot[i].StartTemp.getAvg()
            cconn.outletTemp = self.match_above_cold[i].EndTemp.getAvg()
            
            hconn.stream = self.match_above_hot[i]
            cconn.stream = self.match_above_cold[i]
            
            hconn = self.setStreamData(hconn)
            cconn = self.setStreamData(cconn)
            
            hxpinch.sinkstreams.append(cconn)
            hxpinch.sourcestreams.append(hconn)
            
            hxpinch.writeToDB()
            
            Status.int.HXPinchConnection.append(hxpinch)
            
        
        for i in xrange(len(self.match_below_cold)):
            HXID = self.createNewHX("HX_BelowPinch_" +  str(i))
            hxpinch = HXPinchConnection(HXID, "HX_BelowPinch_" +  str(i))
            hconn = pinchTemp()
            cconn = pinchTemp()
            hconn.percentHeatFlow = self.match_below_hot[i].percent
            cconn.percentHeatFlow = self.match_below_cold[i].percent
            hconn.inletTemp = self.match_below_hot[i].StartTemp.getAvg()
            hconn.outletTemp = self.match_below_cold[i].EndTemp.getAvg()

            cconn.inletTemp = self.match_below_hot[i].StartTemp.getAvg()
            cconn.outletTemp = self.match_below_cold[i].EndTemp.getAvg()
                        
            hconn.stream = self.match_below_hot[i]
            cconn.stream = self.match_below_cold[i]
            
            hconn = self.setStreamData(hconn)
            cconn = self.setStreamData(cconn)
       
            hxpinch.sinkstreams.append(cconn)
            hxpinch.sourcestreams.append(hconn)            
            
            hxpinch.writeToDB()
            
            Status.int.HXPinchConnection.append(hxpinch)
        
    def setStreamData(self, conn):
#        conn.stream.Source = STREAMSOURCE[5]
#        conn.stream.DBType = STREAMTYPE[13]
        conn.stream.MassFlowVector = [conn.stream.MassFlowAvg]*Status.Nt
        return conn
        
    def insertStream(self, stream):
        
        stream['name'] = check(stream.name)
        stream['Hot_Cold'] = check(stream.HotColdType)
        stream['Type'] = check(stream.Type)

        stream['source_id'] = check(stream.DBID)
        stream['source_type'] = check(stream.Source)

        stream['medium_id'] = check(stream.MediumID)
        stream['StartTemp'] = check(stream.StartTemp.getAvg())
        stream['EndTemp'] = check(stream.EndTemp.getAvg())
        stream['StreamType'] = check(stream.DBType)
        stream['HeatCapacity'] = check(stream.HeatCap)
        stream['MassFlowNom'] = check(stream.MassFlowAvg)
        stream['SpecHeatCapacity'] = check(stream.SpecHeatCap)
        stream['SpecEnthalpy'] = check(stream.SpecEnthalpy)
        stream['EnthalpyNom'] = check(stream.EnthalpyNom)
        stream['HeatTransferCoeff'] = check(stream.HeatTransferCoeff)
        
    def createNewHX(self, name):
        tmphx = {"ProjectID":Status.PId,
               "AlternativeProposalNo":Status.ANo,
               "HXName":check(str(name))
               }
        
        qhxTable = Status.DB.qheatexchanger
        HXID = qhxTable.insert(tmphx)
        
        return HXID
        
    def printToSplit(self):
        print "--------------------- STREAMS TO SPLIT -------------------"
        print "Above pinch cold"
        for elem in self.streams_above_pinch_cold:
            print elem
        print "Above pinch hot"
        for elem in self.streams_above_pinch_hot:
            print elem
        print "Below pinch cold"
        for elem in self.streams_below_pinch_cold:
            print elem
        print "Below pinch hot"
        for elem in self.streams_below_pinch_hot:
            print elem
        
        print "----------------------------------------------------------"
        
    def printSplits(self):
        print "------------------Split finished-----------------------"
        print "Above pinch cold"
        for elem in self.streams_above_pinch_cold:
            print elem
        print "Above pinch hot"
        for elem in self.streams_above_pinch_hot:
            print elem
        print "Below pinch cold"
        for elem in self.streams_below_pinch_cold:
            print elem
        print "Below pinch hot"
        for elem in self.streams_below_pinch_hot:
            print elem
        print "------------Matches--------------"
        print "Above: "
        print "Cold:"
        for elem in self.match_above_cold:
            print elem
        print "Hot:"
        for elem in self.match_above_hot:
            print elem
        print "Below:"
        print "Cold:"
        for elem in self.match_below_cold:
            print elem
        print "Hot:"
        for elem in self.match_below_hot:
            print elem
        print "-------------------------------------------------------"
        
        
    def printSplittedStreams(self):
        pass
#        print "----------Streams Above Pinch----------"
#        for stream in self.streams_above_pinch:
#            stream.printStream()
#        print "----------End Stream Above Pinch-------"
#        print "----------Streams Below Pinch----------"
#        for stream in self.streams_below_pinch:
#            stream.printStream()
#        print "----------End Stream Below Pinch-------"            
            
        
    
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
                        bp.percent = 100
                        self.streams_below_pinch_cold.append(bp)
                    elif stream.StartTemp.getAvg() > self.pinch_temperature_lower:
                        print "Call Cold Above", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        ap = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=stream.EndTemp.getAvg(), 
                                    name=stream.name)
                        ap.copyStreamAttributes(stream)
                        ap.percent = 100
                        self.streams_above_pinch_cold.append(ap)
                    else:
                        print "Call Cold Both", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        bp = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=self.pinch_temperature_lower, 
                                    name="Splitted Sink Stream Below Pinch")
                        bp.copyStreamAttributes(stream)
                        bp.percent = 100
                        self.streams_below_pinch_cold.append(bp)
                        ap = Stream(StartTemp=self.pinch_temperature_lower, EndTemp=stream.EndTemp.getAvg(), 
                                    name="Splitted Sink Stream Above Pinch")
                        ap.copyStreamAttributes(stream)
                        ap.percent = 100
                        self.streams_above_pinch_cold.append(ap)
                    
                    
                elif stream.HotColdType == "Hot" or stream.HotColdType == "Source":
                    if stream.EndTemp.getAvg() > self.pinch_temperature_upper:
                        print "Call Hot Above", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        ap = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp = stream.EndTemp.getAvg(), name=stream.name)
                        ap.copyStreamAttributes(stream)
                        ap.percent = 100
                        self.streams_above_pinch_hot.append(ap)
                    elif stream.StartTemp.getAvg() < self.pinch_temperature_upper:
                        print "Call Hot Below", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        bp = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=stream.EndTemp.getAvg(), name=stream.name)
                        bp.copyStreamAttributes(stream)
                        bp.percent = 100
                        self.streams_below_pinch_hot.append(bp)
                    else:    
                        print "Call Hot Both", str(stream.StartTemp.getAvg()), str(stream.EndTemp.getAvg())
                        bp = Stream(StartTemp=self.pinch_temperature_upper, EndTemp=stream.EndTemp.getAvg(), 
                                    name="Splitted Souce Stream Below Pinch")
                        bp.copyStreamAttributes(stream)
                        bp.percent = 100
                        self.streams_below_pinch_hot.append(bp)
                        ap = Stream(StartTemp=stream.StartTemp.getAvg(), EndTemp=self.pinch_temperature_upper, 
                                    name="Splitted Source Stream Above Pinch")
                        ap.copyStreamAttributes(stream)
                        ap.percent = 100
                        self.streams_above_pinch_hot.append(ap)
                
        else:
            # Consider Existing HX
            pass
    
    
if __name__ == "__main__":
    print "HX Proposal Module";
