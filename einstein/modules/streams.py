"""
:mod:`einstein.modules.streams` -- In- and out-flowing streams
==============================================================

   :synopsis: Multiple streams of process input and output
   :author:   David Baehrens <david.baehrens@energyxperts.net>
"""

from einstein.GUI.status        import Status
from einstein.GUI.GUITools      import check
from einstein.modules.constants import findKey
from _mysql_exceptions import ProgrammingError

class ProcessStreamsNotFoundError(Exception):
    """No streams for process with given id found in DB."""
    pass

class StreamNotFoundError(Exception):
    """No stream with given name for process found in DB."""
    pass

class FluidNotFoundError(Exception):
    """No fluid with given id found in DB."""

class InconsistentDataBaseError(Exception):
    """BUG: Data base structure is inconsistent."""
    pass

def getInflowingStreamNamesFromDB(processId):
    """Retrieve all known in-flowing stream names for given processId from data base.
    
    :param processId: Id of process with in-flowing streams to look for.
    :type  processId: Integer

    :returns: All in-flowing stream names stored in data base for processId.
    :rtype:   List of strings
    """
    try:
        streamsInIds = Status.DB.process_streams_in.qprocessdata_QProcessData_Id[processId].streams_in_id.column()
    except LookupError:
        return []
    try:
        return Status.DB.streams_in.sql_select('id IN (%s) ORDER BY Name' % ', '.join(str(id) for id in streamsInIds)).Name.column()
    except ProgrammingError:
        raise InconsistentDataBaseError

def getOutflowingStreamNamesFromDB(processId):
    """Retrieve all known out-flowing stream names for given processId from data base.
    
    :param processId: Id of process with out-flowing streams to look for.
    :type  processId: Integer

    :returns: All out-flowing stream names stored in data base for processId.
    :rtype:   List of strings
    """
    try:
        streamsOutIds = Status.DB.process_streams_out.qprocessdata_QProcessData_Id[processId].streams_out_id.column()
    except LookupError:
        return []
    try:
        return Status.DB.streams_out.sql_select('id IN (%s) ORDER BY Name' % ', '.join(str(id) for id in streamsOutIds)).Name.column()
    except ProgrammingError:
        raise InconsistentDataBaseError

def getStreams(processId):
    """
    Retrieve all streams associated with the given processId form the
    data base.
    
    :param processId: Id of the process whose streams are to retrieved.
    :type processId: Integer
    
    :returns: A 2-Tuple of lists of InflowingStream and 
    OutflowingStream objects, (inflowing, outflowing). 
    """
    result = ([],[])
    (instreams, outstreams) = Status.prj.getStreams(processId)
    for streams, generator, target in ((instreams, InflowingStream, result[0]), 
                                       (outstreams, OutflowingStream, result[1])):
        for stream in streams:
            newstream = generator(stream.Name)
            newstream.loadFromDB(processId)
            target.append(newstream)
    return result
    
class InflowingStream(object):
    '''
    classdocs
    '''


    def __init__(self, Name, Medium=None, PTInFlow=None, PTInFlowRec=None, VInFlowCycle=None, mInFlowNom=None, HeatRecExist=None, HInFlow=None, XInFlow=None, UPHc=None, QdotProc_c=None):
        '''
        Constructor
        '''
        self.Name         = Name
        self.Medium       = Medium
        self.PTInFlow     = PTInFlow
        self.PTInFlowRec  = PTInFlowRec
        self.VInFlowCycle = VInFlowCycle
        self.mInFlowNom   = mInFlowNom
        self.HeatRecExist = HeatRecExist
        self.HInFlow      = HInFlow
        self.XInFlow      = XInFlow
        self.UPHc         = UPHc
        self.QdotProc_c   = QdotProc_c
        self.QProcessData_ID = None
        
    def deleteFromDB(self, processId):
        """Delete all streams with our name associated with given process"""
        processStreamsInRows = Status.DB.process_streams_in.qprocessdata_QProcessData_Id[processId]
        streamsInIds = []
        for processStreamsInRow in processStreamsInRows:
            streamsInRows = Status.DB.streams_in.id[processStreamsInRow['streams_in_id']].Name[self.Name]
            streamsInIds  = streamsInIds + [row['id'] for row in streamsInRows]
            while True:
                try:
                    streamsIn = streamsInRows.pop()
                    streamsIn.delete()
                except IndexError:
                    break
        if not streamsInIds:
            return
        nameProcessStreamsInRows = Status.DB.process_streams_in.sql_select('streams_in_id IN (%s)' % ', '.join([str(id) for id in streamsInIds]))
        while True:
            try:
                nameProcessStreamsInRow = nameProcessStreamsInRows.pop()
                nameProcessStreamsInRow.delete()
            except IndexError:
                break
    
    def saveToDB(self, processId, ANo=None):
        if ANo is None:
            ANo = Status.ANo
        dbFluidId = findKey(Status.prj.getFluidDict(), self.Medium)
        if self.HeatRecExist is None:
            dbHeatRec = None
        else:
            dbHeatRec = self.HeatRecExist and 1 or 0
        dbStream  = {'Name'                 : check(self.Name),
                     'dbfluid_id'           : check(dbFluidId),
                     'PTInFlow'             : check(self.PTInFlow),
                     'PTInFlowRec'          : check(self.PTInFlowRec),
                     'VInFlowCycle'         : check(self.VInFlowCycle),
                     'mInFlowNom'           : check(self.mInFlowNom),
                     'HeatRecExist'         : check(dbHeatRec),
                     'HInFlow'              : check(self.HInFlow),
                     'XInFlow'              : check(self.XInFlow),
                     'UPHc'                 : check(self.UPHc),
                     'QdotProc_c'           : check(self.QdotProc_c),
                     'ProjectID'            : Status.PId,
                     'AlternativeProposalNo': ANo}
        
        try:
            streamsIds = Status.DB.process_streams_in.qprocessdata_QProcessData_Id[processId].streams_in_id.column()
            streamRow  = Status.DB.streams_in.sql_select('id IN (%s) AND Name = "%s"' % (', '.join(str(id) for id in streamsIds), self.Name))[0]
        except ProgrammingError:
            raise InconsistentDataBaseError
        except (LookupError, IndexError): # no input stream with our name found for given processId
            newStreamsInId = Status.DB.streams_in.insert(dbStream)
            Status.DB.process_streams_in.insert({'qprocessdata_QProcessData_Id' : processId,
                                                 'streams_in_id'                : newStreamsInId,
                                                 'ProjectID'                    : Status.PId,
                                                 'AlternativeProposalNo'        : Status.ANo})
        else: # found stream with our name for given processId
            streamRow.update(dbStream)
        
        
    def loadFromDB(self, processId):
        """Load stream with our name associated with given processId"""
        try:
            streamsIds = Status.DB.process_streams_in.qprocessdata_QProcessData_Id[processId].streams_in_id.column()
        except LookupError:
            raise ProcessStreamsNotFoundError
        try:
            streamRow = Status.DB.streams_in.sql_select('id IN (%s) AND Name = "%s"' % (', '.join(str(id) for id in streamsIds), self.Name))[0]
        except IndexError:
            raise StreamNotFoundError
        except ProgrammingError:
            raise InconsistentDataBaseError
        if streamRow['dbfluid_id'] is None:
            self.Medium = None
        else:
            try:
                self.Medium = Status.DB.dbfluid.DBFluid_ID[streamRow['dbfluid_id']][0].FluidName
            except IndexError:
                raise FluidNotFoundError
        self.PTInFlow     = streamRow['PTInFlow']
        self.PTInFlowRec  = streamRow['PTInFlowRec']
        self.VInFlowCycle = streamRow['VInFlowCycle']
        self.mInFlowNom   = streamRow['mInFlowNom']
        if streamRow['HeatRecExist'] is None:
            self.HeatRecExist = None
        else:
            self.HeatRecExist = streamRow['HeatRecExist'] == 1
        self.HInFlow      = streamRow['HInFlow']
        self.XInFlow      = streamRow['XInFlow']
        self.UPHc         = streamRow['UPHc']
        self.QdotProc_c   = streamRow['QdotProc_c']
        self.QProcessData_ID = processId


class OutflowingStream(object):
    '''
    classdocs
    '''

    def __init__(self, Name, Medium=None, PTOutFlow=None, PTOutFlowRec=None, PTFinal=None, VOutFlowCycle=None, mOutFlowNom=None, HeatRecExist=None, HeatRecOK=None, HOutFlow=None, XOutFlow=None, UPHw=None, QdotProc_w=None):
        '''
        Constructor
        '''
        self.Name          = Name
        self.Medium        = Medium
        self.PTOutFlow     = PTOutFlow
        self.PTOutFlowRec  = PTOutFlowRec
        self.PTFinal       = PTFinal
        self.VOutFlowCycle = VOutFlowCycle
        self.mOutFlowNom   = mOutFlowNom
        self.HeatRecExist  = HeatRecExist
        self.HeatRecOK     = HeatRecOK
        self.HOutFlow      = HOutFlow 
        self.XOutFlow      = XOutFlow
        self.UPHw          = UPHw
        self.QdotProc_w    = QdotProc_w
        self.QProcessData_ID = None
        
    def deleteFromDB(self, processId):
        """Delete all streams with our name associated with given process"""
        processStreamsOutRows = Status.DB.process_streams_out.qprocessdata_QProcessData_Id[processId]
        streamsOutIds = []
        for processStreamsOutRow in processStreamsOutRows:
            streamsOutRows = Status.DB.streams_out.id[processStreamsOutRow['streams_out_id']].Name[self.Name]
            streamsOutIds  = streamsOutIds + [row['id'] for row in streamsOutRows]
            while True:
                try:
                    streamsOut = streamsOutRows.pop()
                    streamsOut.delete()
                except IndexError:
                        break
        if not streamsOutIds:
            return
        nameProcessStreamsOutRows = Status.DB.process_streams_out.sql_select('streams_out_id IN (%s)' % ', '.join([str(id) for id in streamsOutIds]))
        while True:
            try:
                nameProcessStreamsOutRow = nameProcessStreamsOutRows.pop()
                nameProcessStreamsOutRow.delete()
            except IndexError:
                break
    
    def saveToDB(self, processId, ANo=None):
        if ANo is None:
            ANo = Status.ANo
        dbFluidId = findKey(Status.prj.getFluidDict(), self.Medium)
        if self.HeatRecExist is None:
            dbHeatRecExist = None
        else:
            dbHeatRecExist = self.HeatRecExist and 1 or 0
        if self.HeatRecOK is None:
            dbHeatRecOk = None
        else:
            dbHeatRecOk = self.HeatRecOK and 1 or 0
        dbStream  = {'Name'                 : check(self.Name),
                     'dbfluid_id'           : check(dbFluidId),
                     'PTOutFlow'            : check(self.PTOutFlow), 
                     'PTOutFlowRec'         : check(self.PTOutFlowRec), 
                     'PTFinal'              : check(self.PTFinal), 
                     'VOutFlowCycle'        : check(self.VOutFlowCycle),
                     'mOutFlowNom'          : check(self.mOutFlowNom),
                     'HeatRecExist'         : check(dbHeatRecExist), 
                     'HeatRecOk'            : check(dbHeatRecOk), 
                     'HOutFlow'             : check(self.HOutFlow),
                     'XOutFlow'             : check(self.XOutFlow), 
                     'UPHw'                 : check(self.UPHw), 
                     'QdotProc_w'           : check(self.QdotProc_w),
                     'ProjectID'            : Status.PId,
                     'AlternativeProposalNo': ANo} 
        
        try:
            streamsIds = Status.DB.process_streams_out.qprocessdata_QProcessData_Id[processId].streams_out_id.column()
            streamRow  = Status.DB.streams_out.sql_select('id IN (%s) AND Name = "%s"' % (', '.join(str(id) for id in streamsIds), self.Name))[0]
        except ProgrammingError:
            raise InconsistentDataBaseError
        except (LookupError, IndexError): # no input stream with our name found for given processId
            newStreamsOutId = Status.DB.streams_out.insert(dbStream)
            Status.DB.process_streams_out.insert({'qprocessdata_QProcessData_Id' : processId,
                                                 'streams_out_id'                : newStreamsOutId,
                                                 'ProjectID'                     : Status.PId,
                                                 'AlternativeProposalNo'         : Status.ANo})
        else: # found stream with our name for given processId
            streamRow.update(dbStream)        
        
    def loadFromDB(self, processId):
        """Load stream with our name associated with given processId"""
        try:
            streamsIds = Status.DB.process_streams_out.qprocessdata_QProcessData_Id[processId].streams_out_id.column()
        except LookupError:
            raise ProcessStreamsNotFoundError
        try:
            streamRow = Status.DB.streams_out.sql_select('id IN (%s) AND Name = "%s"' % (', '.join(str(id) for id in streamsIds), self.Name))[0]
        except IndexError:
            raise StreamNotFoundError
        except ProgrammingError:
            raise OutconsistentDataBaseError
        if streamRow['dbfluid_id'] is None:
            self.Medium = None
        else:
            try:
                self.Medium = Status.DB.dbfluid.DBFluid_ID[streamRow['dbfluid_id']][0].FluidName
            except IndexError:
                raise FluidNotFoundError
        self.PTOutFlow     = streamRow['PTOutFlow']
        self.PTOutFlowRec  = streamRow['PTOutFlowRec']
        self.PTFinal       = streamRow['PTFinal']
        self.VOutFlowCycle = streamRow['VOutFlowCycle']
        self.mOutFlowNom   = streamRow['mOutFlowNom']
        if streamRow['HeatRecExist'] is None:
            self.HeatRecExist = None
        else:
            self.HeatRecExist = streamRow['HeatRecExist'] == 1
        if streamRow['HeatRecOk'] is None:
            self.HeatRecOK = None
        else:
            self.HeatRecOK = streamRow['HeatRecOk'] == 1
        self.HOutFlow      = streamRow['HOutFlow'] 
        self.XOutFlow      = streamRow['XOutFlow']
        self.UPHw          = streamRow['UPHw']
        self.QdotProc_w    = streamRow['QdotProc_w']
        self.QProcessData_ID = processId
