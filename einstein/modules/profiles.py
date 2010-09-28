"""
:mod:`einstein.modules.profiles` -- Operation time of processes
===============================================================

   :synopsis: Running time profiles for processes
   :author:   David Baehrens <david.baehrens@energyxperts.net>
"""

from datetime                   import datetime, date, time
from einstein.modules.constants import DAY
from einstein.GUI.status        import Status

### Constants

weekdays = (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
            )
"""Weekday names in order."""

### Errors

class ProfileNotFoundError(Exception):
    """No profile found with given name."""
    pass

class ProfileWithoutIntervalsError(Exception):
    """Profile has no running time intervals."""
    pass


### Functions

def getProfileIndexByName(name, profiles):
    """Retrieve index of profile in instance list by profile name.
    
    :param name:     Name of the profile to look for
    :type  name:     String
    :param profiles: Profiles to choose from
    :type  profiles: List of profile instances
    :returns:        Index of profile with name in list
    :rtype:          Integer
    """
    try:
        return [i for i,p in enumerate(profiles) if p.id == name][0]
    except IndexError:
        raise ProfileNotFoundError
    
def getProfileNamesFromDB():
    """Retrieve known profile names from data base.
    
    :returns: All profile names stored in data base.
    :rtype:   List of strings
    """
    return Status.DB.profiles.name['%'].column()

def exportWeeklyProfilesFromDB():
    """Export all stored weekly profiles from data base in fractional weekly hour format.
    
    :returns: {"name" : name of weekly profile, "intervals" : [{"start" : start hour point in week, "stop" : stop hour point in week, "scale" : load [0,1]}]}
    :rtype: Dictionary
    """
    profiles = []
    for profile in Status.DB.profiles.get_table():
        intervals = []
        for intervalId in Status.DB.profile_intervals.profiles_id[profile.id].intervals_id.column():
            startHour = Status.DB.intervals.id[intervalId][0].start.seconds / 3600.
            stopHour  = Status.DB.intervals.id[intervalId][0].stop.seconds / 3600.
            scale     = float(Status.DB.intervals.id[intervalId][0].scale) * .01
            for weekdayIndex in range(len(weekdays)):
                if getattr(profile, weekdays[weekdayIndex]) != 0: 
                    intervals.append({"start" :  (weekdayIndex * DAY) + startHour,
                                      "stop"  :  (weekdayIndex * DAY) + stopHour,
                                      "scale" :  scale})
        intervals.sort(key=lambda x: x["start"])
        profiles.append({"name"      : profile.name,
                         "intervals" : intervals})
    return profiles
            

### Classes

class WeeklyProfile(object):
    """Daily intervals of running time during one week on selected weekdays.
    
    :param id: Unique name used for identification
    :type  id: String
    :param profile: Initial daily intervals, default: empty
    :type  profile: List of 3-tuples (start time, stop time, scale integer)
    :param weekday: Initial selection of weekdays, default: all False
    :type  weekday: Dictionary {<names from :data:`einstein.modules.profiles.weekdays`> : <Booleans>}
    :returns:       Weekly profile instance
    :rtype:         einstein.modules.profiles.WeeklyProfile
    """
    
    def __init__(self, id, profile=None, weekday=None):
        self.id      = id
        if profile:
            self.profile = profile
        else:
            self.profile = []
        if weekday:
            self.weekday = weekday
        else:
            self.weekday = dict(zip(weekdays, len(weekdays)*[False]))
            
    def loadFromDB(self):
        """Retrieve daily intervals and selected weekdays from data base.

        To load a weekly profile from the data base by name construct an
        empty instance with the name as id first, then call this method on
        it. To get the names of all profiles available in the data base use
        :func:`einstein.modules.profiles.getProfileNamesFromDB()`.  
    
        :returns: nothing
        :exception einstein.modules.profiles.ProfileNotFoundError:         No profile with name of id found in data base.
        :exception einstein.modules.profiles.ProfileWithoutIntervalsError: Profile with name of id has no intervals in data base.
        """
        # table profiles
        dbProfile = Status.DB.profiles.name[self.id]
        try:
            self.weekday = dict(zip(weekdays, [dbProfile[0][w] != 0 for w in weekdays]))
        except IndexError:
            raise ProfileNotFoundError
        
        try:
            for intervalId in Status.DB.profile_intervals.profiles_id[dbProfile[0].id].intervals_id.column():
                interval = Status.DB.intervals.id[intervalId].pop()
                # work around python limitation to not allow arithmetic with time and timedelta types directly
                # cf. http://bugs.python.org/issue1487389
                dummyDateTime = datetime.combine(datetime.today(), time(0))
                self.addInterval((dummyDateTime + interval['start']).time(), (dummyDateTime + interval['stop']).time(), interval['scale'])
        except LookupError:
            raise ProfileWithoutIntervalsError
            
    def saveToDB(self):
        """Store profile to data base.
        
        :returns: nothing
        """
        # table profiles
        profileRow = { 'name' : self.id }
        profileRow.update(dict([ (k,v and 1 or 0) for k,v in self.weekday.iteritems()]))
        dbProfile = Status.DB.profiles.name[self.id]
        try:
            dbProfile[0].update(profileRow)
            profileRowId = dbProfile[0].id
        except IndexError:
            profileRowId = Status.DB.profiles.insert(profileRow)
        
        # wipe profile_intervals for this profile
        profileIntervalRows = Status.DB.profile_intervals.profiles_id[profileRowId]
        for profileInterval in profileIntervalRows:
            profileInterval.delete()
            
        for interval in self.profile:
            # table intervals
            dbInterval  = Status.DB.intervals.start[interval[0]].stop[interval[1]].scale[interval[2]]
            try:
                intervalRowId = dbInterval[0].id
            except IndexError:
                intervalRow   = dict(zip(('start', 'stop', 'scale'), interval))
                intervalRowId = Status.DB.intervals.insert(intervalRow)
            # table profile_intervals
            Status.DB.profile_intervals.insert({'profiles_id':profileRowId,'intervals_id':intervalRowId})
            
    def deleteFromDB(self):
        """Remove profile from data base.
        
        :returns: nothing
        :exception einstein.modules.profiles.ProfileNotFoundError: No profile with name of id found in data base.
        """
        # table profiles
        dbProfile = Status.DB.profiles.name[self.id]
        try:
            dbProfileRowId = dbProfile[0].id
            dbProfile[0].delete()
        except IndexError:
            raise ProfileNotFoundError
        
        # wipe profile_intervals for this profile
        profileIntervalRows = Status.DB.profile_intervals.profiles_id[dbProfileRowId]
        while True:
            try:
                profileInterval = profileIntervalRows.pop()
                profileInterval.delete()
            except IndexError:
                break
           
    def addInterval(self, start, stop, scale):
        """Add an running time interval to profile instance.
                
        :param start: start time (inclusive)
        :type  start: time
        :param stop:  stop time (inclusive)
        :type  stop:  time
        :param scale: percentage of operation relative to nominal load
        :type  scale: Integer
        :returns:     nothing
        """

        firstLaterStart = 0
        while firstLaterStart < len(self.profile):
            if start < self.profile[firstLaterStart][0]:
                break
            else:
                firstLaterStart += 1
        self.profile.insert(firstLaterStart, (start, stop, scale))
        
    def setMonday(self, value):
        """Specify whether to run on Monday.
        :param value: Run on Monday?
        :type  value: Boolean
        """
        self.weekday['monday'] = value

    def setTuesday(self, value):
        """Specify whether to run on Tuesday.
        :param value: Run on Tuesday?
        :type  value: Boolean
        """
        self.weekday['tuesday'] = value
        
    def setWednesday(self, value):
        """Specify whether to run on Wednesday.
        :param value: Run on Wednesday?
        :type  value: Boolean
        """
        self.weekday['wednesday'] = value
        
    def setThursday(self, value):
        """Specify whether to run on Thursday.
        :param value: Run on Thursday?
        :type  value: Boolean
        """
        self.weekday['thursday'] = value
        
    def setFriday(self, value):
        """Specify whether to run on Friday.
        
        :param value: Run on Friday?
        :type  value: Boolean
        """
        self.weekday['friday'] = value
        
    def setSaturday(self, value):
        """Specify whether to run on Saturday.
        
        :param value: Run on Saturday?
        :type  value: Boolean
        """
        self.weekday['saturday'] = value
        
    def setSunday(self, value):
        """Specify whether to run on Sunday.
        
        :param value: Run on Sunday?
        :type  value: Boolean
        """
        self.weekday['sunday'] = value
        
    def getProfile(self):
        """Retrieve the running time intervals of profile instance.
        
        :returns: Running time intervals ordered by ascending start time.
        :rtype:   List of 3-tuples (start time, stop time, scale integer)
        """
        return self.profile
    
    def getWeekdays(self):
        """Retrieve the weekdays of operation.
        
        :returns: Weekdays of operation ordered as in `einstein.modules.profiles.weekdays`
        :rtype:   List of Boolean
        """
        return [self.weekday[w] for w in weekdays]