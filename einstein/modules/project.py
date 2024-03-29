#==============================================================================
#
#	E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (www.iee-einstein.org)
#
#------------------------------------------------------------------------------
#
#	PROJECT
#			
#------------------------------------------------------------------------------
#			
#	Definition of objects defining and handling a project (industry)
#       - projects (create, delete, ...)
#       - alternatives (create, delete, ...)
#       - access to SQL data tables (fuels, equipments, pipes, processes, ...)
#
#==============================================================================
#
#   EINSTEIN Version No.: 1.0
#   Created by: 	Hans Schweiger, Stoyan Danov
#                       02/04/2008 - 01/08/2008
#
#   Update No. 003
#
#   Since Version 1.0 revised by:
#
#                       Hans Schweiger  01/04/2009
#                       Hans Schweiger  06/04/2009
#                       Hans Schweiger  10/06/2009
#                       Hans Schweiger  26/07/2009
#               
#   01/04/2009  HS  Security features added for dealing with corrupt entries
#                   in db: Equipments w/o name etc.
#                   -> cleanUpProject called when opening project
#                   -> cleanUpSQLRows checks mainField
#   06/04/2009  HS  Clean-up: elimination of prints
#   10/06/2009  HS  bug-fix. empty project description field led to errors in
#                   setActiveProject
#   26/07/2009  HS  change in deleteEquipment -> elimination of connected HX
#		
#------------------------------------------------------------------------------		
#	(C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008,2009
#	www.energyxperts.net / info@energyxperts.net
#
#	This program is free software: you can redistribute it or modify it under
#	the terms of the GNU general public license as published by the Free
#	Software Foundation (www.gnu.org).
#
#==============================================================================

from einstein.GUI.status import Status
from messageLogger import *
from constants import *
from schedules import Schedules
from processes import Processes
from messageLogger import *
from einstein.GUI.GUITools import check

def _U(text):
    return unicode(_(text), "utf-8")

#------------------------------------------------------------------------------		
def copySQLRows(table, query, keyID, keyPar=None, valPar=None):
    """
    auxiliary function for copying full rows in SQL Tables
    
    :param table: name of the table
    :param query: the part after the WHERE in the SQL clause
    :param keyID: name of the primary key in the table
    :param keyPar: name of a column with entries that are to be changed in the
    copy
    :param valPar: new value for column keyPar
    :returns: A dict with oldId: newID pairs
    """
    rows = table.sql_select(query)

    IDDict = {}
    newID = None
        
    for row in rows:

#..............................................................................
# translates the pSQL - object into a dictionary

        mydict = {}
        mydict.update(row)

#..............................................................................
# eliminates the main key of the table, that has to be unique

        oldID = mydict[keyID]
        mydict.pop(keyID)
        
#..............................................................................
# changes one parameter within the row (usually AlternativeNo or ProjectID

        if valPar is not None:
            mydict.update([(keyPar, valPar)])

#..............................................................................
# eliminates the None's from the dictionary (would otherwise be substituted by
# 0 in SQL

        noneKeys = []
        for key in mydict:
            if mydict[key] is None:
                noneKeys.append(key)
        for key in noneKeys:
            mydict.pop(key)
                
#..............................................................................
# now inserts the new row into the SQL Table

        newID = table.insert(mydict)

        IDDict.update({oldID:newID})

    return IDDict
#------------------------------------------------------------------------------		
def deleteSQLRows(table, query):
#------------------------------------------------------------------------------		
#       auxiliary function for copying full rows in SQL Tables
#------------------------------------------------------------------------------		

    rows = table.sql_select(query)
    n = len(rows)

    for i in range(n):
        rows[0].delete()
        Status.SQL.commit()
        rows = table.sql_select(query)
           

#------------------------------------------------------------------------------		
def cleanUpSQLRows(table, query, maxANo=None, mainField=None):
#------------------------------------------------------------------------------		
#       auxiliary function for copying full rows in SQL Tables
#       eliminates rows with erroneous ANO
#------------------------------------------------------------------------------		

    checked = False
    ctr = 0
    rows = table.sql_select(query)
    maxCtr = len(rows)
        

    while (checked == False and ctr < maxCtr):
        ctr += 1
        
        checked = True
        
        rows = table.sql_select(query)
        
        n = len(rows)
        for i in range(n):

# check here if there are rows with an AlternativeProposalNo out of range [-1:maxANo]
            if maxANo is not None:
                if rows[i].AlternativeProposalNo > maxANo or rows[i].AlternativeProposalNo < -1:
                    logDebug(_("Project (cleanUpSQLRows): entry with ANo %s > maxANo %s deleted -> \n%s") % \
                             (rows[i].AlternativeProposalNo, maxANo, rows[i]))
                    rows[i].delete()    #delete from 0 and update rows -> strange solution. see comment in deleteSQLRows
                    checked = False
                    Status.SQL.commit()
                    break
                
# check here if the mandatory main entry field of the row is defined (avoid crashes due to nones in name-fields, etc.)

            if mainField is not None:

                if rows[i][mainField] is None:
                
                    logDebug(_("Project (cleanUpSQLRows): corrupt entry with ANo %s deleted\n%s") % \
                             (rows[i].AlternativeProposalNo, rows[i]))
                    rows[i].delete()    #delete from 0 and update rows -> strange solution. see comment in deleteSQLRows
                    checked = False
                    Status.SQL.commit()
                    break                    

#------------------------------------------------------------------------------		
def shiftANoInSQLRows(table, query, shift):
#------------------------------------------------------------------------------		
#       auxiliary function for changing a value in rows
#------------------------------------------------------------------------------		
    rows = table.sql_select(query)

    for row in rows:
        newval = row.AlternativeProposalNo + shift
        row.AlternativeProposalNo = newval
                
#==============================================================================
#       PROJECT CLASS
#==============================================================================

class Project(object):

#------------------------------------------------------------------------------		
    def __init__(self):
#------------------------------------------------------------------------------		
# initialisation. does the initialisation of basic parameters in Status
#------------------------------------------------------------------------------		

        Status.prj = self
        
#..............................................................................
# get last tool settings from table STOOLS (last project opened, etc.)

        self.getLastToolSettings()

#..............................................................................
# create instance of Schedules and Processes (does no calculations)

        Status.schedules = Schedules()
        Status.processData = Processes()

#..............................................................................
# set active project to the last one opened

        self.setActiveProject(Status.PId)

#------------------------------------------------------------------------------		
        
#------------------------------------------------------------------------------		
# HANDLING OF ALTERNATIVE PROPOSALS (= REPEATED PART OF A PROJECT)
#------------------------------------------------------------------------------		

#------------------------------------------------------------------------------
    def createNewAlternative(self, originalANo, shortName, description):
#------------------------------------------------------------------------------
#   creates a new alternative copying all entries for the original ANo
#------------------------------------------------------------------------------

        if Status.PId < 0: return
        
        DB = Status.DB

        Status.NoOfAlternatives += 1
        ANo = Status.NoOfAlternatives

        sproject = Status.DB.sproject.ProjectID[Status.PId][0]
        sproject.NoOfAlternatives = Status.NoOfAlternatives

        logTrack("Project (createNewAlternative) - project %s, copying from %s %s" % (Status.PId, originalANo, ANo))

#..............................................................................
# copying Q- and corresponding C-Tables

        sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, originalANo)

        #additional query necessary for old tables who still have Questionnaire_id instead of ProjectID
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, originalANo)

        copySQLRows(DB.salternatives, sqlQuery, "SAlternative_ID", "AlternativeProposalNo", ANo)
        copySQLRows(DB.cgeneraldata, sqlQueryQ, "CGeneralData_ID", "AlternativeProposalNo", ANo)

        copySQLRows(DB.qbuildings, sqlQueryQ, "QBuildings_ID", "AlternativeProposalNo", ANo)
        copyPipeDict = copySQLRows(DB.qdistributionhc, sqlQueryQ, "QDistributionHC_ID", "AlternativeProposalNo", ANo)
        copySQLRows(DB.qelectricity, sqlQueryQ, "QElectricity_ID", "AlternativeProposalNo", ANo)
        copySQLRows(DB.qfuel, sqlQueryQ, "QFuel_ID", "AlternativeProposalNo", ANo)
        copyEqDict = copySQLRows(DB.qgenerationhc, sqlQueryQ, "QGenerationHC_ID", "AlternativeProposalNo", ANo)
        copySQLRows(DB.qheatexchanger, sqlQuery, "QHeatExchanger_ID", "AlternativeProposalNo", ANo)
        copyProcessesDict = copySQLRows(DB.qprocessdata, sqlQueryQ, "QProcessData_ID", "AlternativeProposalNo", ANo)
        copySQLRows(DB.qproduct, sqlQueryQ, "QProduct_ID", "AlternativeProposalNo", ANo)
#        copySQLRows(DB.qrenewables,sqlQueryQ,"QRenewables_ID","AlternativeProposalNo",ANo)
        copySQLRows(DB.qwasteheatelequip, sqlQuery, "QWasteHeatElEquip_ID", "AlternativeProposalNo", ANo)
        copySQLRows(DB.uheatpump, sqlQueryQ, "UHeatPump_ID", "AlternativeProposalNo", ANo)
        inStreamIds = self._getStreamsForProcesses(DB.process_streams_in,
                                                   copyProcessesDict.keys(),
                                                   "streams_in_id")
        self._copyStreams(inStreamIds, copyProcessesDict,
                                             DB.process_streams_in,
                                             "streams_in_id",
                                             DB.streams_in, ANo)
        outStreamIds = self._getStreamsForProcesses(DB.process_streams_out,
                                                    copyProcessesDict.keys(),
                                                    "streams_out_id")
        self._copyStreams(outStreamIds, copyProcessesDict,
                                              DB.process_streams_out,
                                              "streams_out_id",
                                              DB.streams_out, ANo)
        
#..............................................................................
# re-establish links

        self.reconnectEquipesToPipes(copyEqDict, copyPipeDict)
        
#..............................................................................
# rename alternative

        sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, ANo)
        aa = DB.salternatives.sql_select(sqlQuery)
        if len(aa) > 0:
            a = aa[0]
            a.ShortName = check(shortName)
            if description is None:
                description = "---"
            a.Description = check(description)

            Status.SQL.commit()
            self.setActiveAlternative(ANo)
        else:
            logError(_("ERROR: possibly corrupt project data\n cannot copy alternative (PId: %s ANo: %s)") % (Status.PId, ANo))
                        
#------------------------------------------------------------------------------
        
#------------------------------------------------------------------------------
    def deleteAlternative(self, ANo):
#------------------------------------------------------------------------------
#   deletes all entries for the original ANo
#------------------------------------------------------------------------------

        if ANo > Status.NoOfAlternatives or ANo == -1:
            
            logWarning(_("Project (deleteAlternative) - project %s, cannot delete alternative %s") % (Status.PId, ANo))
            return - 1
        
        finalAlternative = Status.FinalAlternative
        if finalAlternative is not None:
            if finalAlternative > ANo:
                finalAlternative -= 1
            elif finalAlternative == ANo:
                finalAlternative = None
        self.setFinalAlternative(finalAlternative)
        
        logTrack("Project (deleteAlternative) - project %s, deleting alternative %s" % (Status.PId, ANo))

#..............................................................................
# deleting Q- and corresponding C-Tables

        DB = Status.DB
        sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, ANo)

        #additional query necessary for old tables who still have Questionnaire_id instead of ProjectID
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, ANo)
        
        processes = DB.qprocessdata.sql_select(sqlQueryQ)
        processes = [p.QProcessData_ID for p in processes]
        for pId in processes:
            self.deleteProcess(pId)
        deleteSQLRows(DB.salternatives, sqlQuery)
        deleteSQLRows(DB.cgeneraldata, sqlQueryQ)

        deleteSQLRows(DB.qbuildings, sqlQueryQ)
        deleteSQLRows(DB.qdistributionhc, sqlQueryQ)
        deleteSQLRows(DB.qelectricity, sqlQueryQ)
        deleteSQLRows(DB.qfuel, sqlQueryQ)
        deleteSQLRows(DB.qgenerationhc, sqlQueryQ)
        deleteSQLRows(DB.qheatexchanger, sqlQuery)
        deleteSQLRows(DB.qprocessdata, sqlQueryQ)
        deleteSQLRows(DB.streams_in, sqlQuery)
        deleteSQLRows(DB.streams_out, sqlQuery)
        deleteSQLRows(DB.process_streams_in, sqlQuery)
        deleteSQLRows(DB.process_streams_out, sqlQuery)
        deleteSQLRows(DB.qproduct, sqlQueryQ)
#        deleteSQLRows(DB.qrenewables,sqlQueryQ)
        deleteSQLRows(DB.qwasteheatelequip, sqlQuery)
        deleteSQLRows(DB.uheatpump, sqlQueryQ)


#..............................................................................
# changing ANos in all rows with ANo higher than the deleted one

        for i in range(ANo + 1, Status.NoOfAlternatives + 1):
            sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, i)

        #additional query necessary for old tables who still have Questionnaire_id instead of ProjectID
            sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, i)

            shiftANoInSQLRows(DB.salternatives, sqlQuery, -1)
            shiftANoInSQLRows(DB.cgeneraldata, sqlQueryQ, -1)

            shiftANoInSQLRows(DB.qbuildings, sqlQueryQ, -1)
            shiftANoInSQLRows(DB.qdistributionhc, sqlQueryQ, -1)
            shiftANoInSQLRows(DB.qelectricity, sqlQueryQ, -1)
            shiftANoInSQLRows(DB.qfuel, sqlQueryQ, -1)
            shiftANoInSQLRows(DB.qgenerationhc, sqlQueryQ, -1)
            shiftANoInSQLRows(DB.qheatexchanger, sqlQuery, -1)
            shiftANoInSQLRows(DB.qprocessdata, sqlQueryQ, -1)
            shiftANoInSQLRows(DB.qproduct, sqlQueryQ, -1)
#            shiftANoInSQLRows(DB.qrenewables,sqlQueryQ,-1)
            shiftANoInSQLRows(DB.qwasteheatelequip, sqlQuery, -1)
            shiftANoInSQLRows(DB.uheatpump, sqlQueryQ, -1)


#..............................................................................
# book-keeping: reduce number of alernatives in the system

        Status.NoOfAlternatives -= 1
        ANo = Status.NoOfAlternatives
        self.setActiveAlternative(ANo)

        sproject = Status.DB.sproject.ProjectID[Status.PId][0]
        sproject.NoOfAlternatives = Status.NoOfAlternatives


        Status.SQL.commit()

#------------------------------------------------------------------------------
    def getAlternativeList(self):
#------------------------------------------------------------------------------

        defaultList = [[-1, _("Present State (original)"),
                            _("original data as delivered in questionnaire"),
                            "-", "---", "---", "---"],
                            [0, _("Present State (checked)"),
                            _("complete data set for present state after\ncross-checking and data estimation"),
                            "-", "---", "---", "---"]]

        alternativeList = []
        if Status.PId is None or Status.PId <= 0:
            return alternativeList
        
        for ANo in range(-1, Status.NoOfAlternatives + 1):
            aa = Status.DB.salternatives.ProjectID[Status.PId].AlternativeProposalNo[ANo]
            if len(aa) > 0:
                a = aa[0]
                
                if a.StatusA == 0:
                    stat = "-"
                elif a.StatusA == 1:
                    stat = "ok"
                else:
                    stat = "?"

#..............................................................................
# get main energy data if available

                if a.StatusEnergy > 0:
                    cc = Status.DB.cgeneraldata.Questionnaire_id[Status.PId].AlternativeProposalNo[ANo]
                    if len(cc) > 0:
                        cgeneraldata = cc[0]
                        try: PEC = float(cgeneraldata.PEC) / 1000.0   #conversion to MWh
                        except:
                            logTrack("Project (getAlternativeList): no PEC available")
                            PEC = 0.0

                        try: EnergyCost = float(cgeneraldata.EnergyCost)
                        except:
                            logTrack("Project (getAlternativeList): no EnergyCost available")
                            EnergyCost = 0.0
                        
                        if a.Description is None: a.Description = "---"
                        alternativeList.append([a.AlternativeProposalNo,
                                                unicode(a.ShortName, "utf-8"),
                                                unicode(a.Description, "utf-8"),
                                                stat, PEC, EnergyCost])
                    else:
                        logError(_("Corrupt data in data base. no entry in cgeneraldata for ANo = %s") % ANo)
                        if ANo in [-1, 0]:
                            alternativeList.append(defaultList[ANo + 1])
                else:
                    if a.Description is None: a.Description = "---"
                    alternativeList.append([a.AlternativeProposalNo,
                                            unicode(a.ShortName, "utf-8"),
                                            unicode(a.Description, "utf-8"),
                                            stat, '---', '---'])
            else:
                logError(_("Corrupt data in data base. no entry in salternative for ANo = %s") % ANo)
                if ANo in [-1, 0]:
                    alternativeList.append(defaultList[ANo + 1])

        return alternativeList
            
#------------------------------------------------------------------------------
    def setActiveAlternative(self, n, checked=False):
#------------------------------------------------------------------------------

        if (n >= -1) and n <= Status.NoOfAlternatives:

            sprojects = Status.DB.sproject.ProjectID[Status.PId]
            if len(sprojects) > 0:
                Status.DB.sproject.ProjectID[Status.PId][0].ActiveAlternative = n
                Status.SQL.commit()
                Status.ANo = n
            else:
                logTrack("Project (setActiveAlternative): error writing active alternative no. to project table PId %s" % \
                         Status.PId)

            salternatives = Status.DB.salternatives.ProjectID[Status.PId].AlternativeProposalNo[n]
            if len(salternatives) > 0:
                Status.ActiveAlternativeName = unicode(salternatives[0].ShortName, "utf-8")
                self.getStatus()
                logTrack("Project (setActiveAlternative): PId = %s ANo = %s StatusCC = %s" % \
                  (Status.PId, Status.ANo, Status.StatusCC))

                if checked == True:
                    Status.prj.setStatus("CC")

                if Status.StatusCC > 0:
                    Status.processData.createYearlyDemand()
                
                Status.schedules.outOfDate = True
                Status.processData.outOfDate = True
                Status.int.changeInCascade(0)

                try:
                    Status.main.panelinfo.update()
                except:
                    logDebug("problems updating panelinfo")

                try:
                    Status.main.showMainMenuAlternatives()
                except:
                    logDebug("problems updating main menu alternatives")
            else:
                logTrack("Project (setActiveAlternative): error trying to set alternative to %s" % n)
                Status.StatusCC = None
                Status.StatusQ = None

        else:
            logTrack("Project (setActiveAlternative): alternative number out of range [%s,%s]" % (-1, Status.NoOfAlternatives))
            
#------------------------------------------------------------------------------
    def copyQuestionnaire(self):
#------------------------------------------------------------------------------
#   Creates a 1:1 copy from alternative -1 to alternative 0
#------------------------------------------------------------------------------

#first remove everything with ANo > -1

        self.cleanUpProject(Status.PId) #use the opportunity to clean-up erroneous entries with ANo > NoOfAlternatives
        
        n = Status.NoOfAlternatives
        for ANo in range(n, -1, -1):
            self.deleteAlternative(ANo)
        self.createNewAlternative(-1, _U("Present State (checked)"), \
                                _U("complete data set for present state after\n cross-checking and data estimation"))
        self.setActiveAlternative(-1)
        self.setStatus("Q")
        self.setStatus("CC", 0)

#------------------------------------------------------------------------------		
#------------------------------------------------------------------------------
    def setFinalAlternative(self, ANo):
#------------------------------------------------------------------------------
        finalANo = ANo
        if finalANo is None:
            self.setStatus("CS", 0)
            Status.FinalAlternativeName = "---"
        else:
            if ANo < 0:
                finalANo = 0     
            elif finalANo > Status.NoOfAlternatives:
                logDebug("Project (setFinalAlternative): error in no. of selected alternative [%s]" % finalANo)
                return

            Status.FinalAlternativeName = "---"

            self.setStatus("CS")
            aa = Status.DB.salternatives.ProjectID[Status.PId].\
                 AlternativeProposalNo[finalANo]
            if len(aa) > 0:
                name = aa[0].ShortName
                if name is not None:
                    Status.FinalAlternativeName = unicode(name, "utf-8")
                else:
                    logDebug("Project (setFinalAlternative): no name specified for alternative no. [%s]" % finalANo)
                    Status.FinalAlternativeName = "---"
            else:
                logDebug("Project (setFinalAlternative): no entry in table salternative for ANo [%s]" % finalANo)
                Status.FinalAlternativeName = "---"

        sprojects = Status.DB.sproject.ProjectID[Status.PId]
        if len(sprojects) > 0:
            sproject = sprojects[0]
            sproject.FinalAlternative = check(finalANo)
            Status.SQL.commit()
            
        Status.FinalAlternative = finalANo
            
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------		
# HANDLING OF PROJECTS (CREATE,COPY,DELETE,INIT ...)
#------------------------------------------------------------------------------		

#------------------------------------------------------------------------------
    def getProjectList(self):
#------------------------------------------------------------------------------
#   returns a list with the names of the projects. used in panelQ0
#------------------------------------------------------------------------------
        projectList = []
        for n in Status.DB.questionnaire.Name["%"]:
            projectList.append(unicode(n.Name, "utf-8"))
        return projectList

#------------------------------------------------------------------------------
    def getProjectData(self):
#------------------------------------------------------------------------------
#   returns the data in tables questionnaire and cgenerationhc
#   for given ANo and PId
#------------------------------------------------------------------------------
        # TODO: check whether this self.projectData and self.generalData serves 
        # any global initialisation and should be documented/changed or can be dropped. 
        sqlQuery = "Questionnaire_id = '%s'" % (Status.PId)
        projects = Status.DB.questionnaire.sql_select(sqlQuery)
        if len(projects) > 0: self.projectData = projects[0]
        else: self.projectData = None

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        generaldatasets = Status.DB.cgeneraldata.sql_select(sqlQuery)
        if len(generaldatasets) > 0:self.generalData = generaldatasets[0]
        else: self.generalData = None

        return (self.projectData, self.generalData)


#------------------------------------------------------------------------------
    def getProjectID(self, name):
#------------------------------------------------------------------------------
#   returns the ID of a project as a function of the name
#------------------------------------------------------------------------------

        projects = Status.DB.questionnaire.Name[check(name)]
        
        if len(projects) > 0:
            return projects[0].Questionnaire_ID
        
        else:
            logTrack("Project (getProjectID): project name %s unknown" % name)
            return None

#------------------------------------------------------------------------------
    def setActiveProject(self, PId, name=None):
#------------------------------------------------------------------------------
#   sets the presently active project no.
#   If PId <= 0 and no name is given, then all projects are deselected
#------------------------------------------------------------------------------
        
        if name is not None:    #if a name is given, overwrite ID
            PId = self.getProjectID(name)

        if (PId <= 0 or (PId is None)):
            Status.PId = -1
            Status.ActiveProjectName = u'---'
            Status.ActiveProjectDescription = u'---'
            self.setFinalAlternative(None)
            Status.NoOfAlternatives = -1
            
            logTrack("Project (setActiveProject): no project selected")

        else:

            try:
                Status.ActiveProjectName = unicode(Status.DB.questionnaire.Questionnaire_ID[PId][0].Name, "utf-8")

                if Status.DB.questionnaire.Questionnaire_ID[PId][0].DescripIndustry is not None:
                    Status.ActiveProjectDescription = unicode(Status.DB.questionnaire.Questionnaire_ID[PId][0].\
                                                              DescripIndustry, "utf-8")
                else:
                    Status.ActiveProjectDescription = ""

                self.cleanUpProject(PId)

 
            except:
                Status.ActiveProjectName = u'unknown'
                Status.ActiveProjectDescription = u'unknown'
                logTrack("Project (setActiveProject): error in table questionnaire")
                
            try:
                sproject = Status.DB.sproject.ProjectID[PId][0]
                Status.NoOfAlternatives = sproject.NoOfAlternatives
                Status.ANo = sproject.ActiveAlternative
                Status.FinalAlternative = sproject.FinalAlternative
                
                logTrack("Project (setActiveProject): number of alternatives in the project %s" % Status.NoOfAlternatives)
                logTrack("Project (setActiveProject): active alternative %s" % Status.ANo)
            except:
                Status.NoOfAlternatives = -1
                Status.ANo = -1
                Status.FinalAlternative = None
                logTrack("Project (setActiveProject): could not open project no. %s" % PId)
                
            Status.PId = PId


            try:
                Status.DB.stool.STool_ID[1][0].ActiveProject = PId
                logTrack("Project (setActiveProject): active project set to %s" % PId)
            except:
                logTrack("Project (setActiveProject): error writing new active project ID to stool")                

            self.setActiveAlternative(Status.ANo)
            self.setFinalAlternative(Status.FinalAlternative)

        Status.SQL.commit()

        try:                                #try, because at start-up there's not yet a moduleST
            Status.mod.moduleST.resetST()   #resets the calculator of surface areas
        except:
            pass

#------------------------------------------------------------------------------
    def createNewProject(self, originalPId, shortName, description, originalName=None):
#------------------------------------------------------------------------------

        DB = Status.DB
        questionnaires = Status.DB.questionnaire
        sprojects = Status.DB.sproject
        salternatives = Status.DB.salternatives
        cgeneraldata = Status.DB.cgeneraldata
        qelectricity = Status.DB.qelectricity
        uheatpump = Status.DB.uheatpump
        
        if (originalPId <= 0) and (originalName is None):

            isNewProject = True
#..............................................................................
# start a new project from scratch (creates basic project tables)

            newProject = {"Name": check(shortName), "DescripIndustry":check(description)}

            newID = questionnaires.insert(newProject)
            logTrack("Project (createNewProject): new project inserted with ID %s " % newID)

            newSProject = {"ProjectID":newID,
                           "NoOfAlternatives":-1,
                           "ActiveAlternative":-1,
                           "WriteProtected":0,
                           "StatusQ":EINSTEIN_NOTOK,
                           "StatusCC":EINSTEIN_NOTOK,
                           "StatusCA":EINSTEIN_NOTOK,
                           "StatusR":EINSTEIN_NOTOK,
                           "LanguageReport":Status.LanguageTool,
                           "UnitsReport":Status.UnitsTool}
            sprojects.insert(newSProject)

            newAlternative = {"ProjectID":newID,
                              "AlternativeProposalNo":-1,
                              "ShortName":_U("present state (original)"),
                              "Description":_U("original data as submitted by industry")}
            salternatives.insert(newAlternative)
            
            newGeneralData = {"Questionnaire_id":newID,
                              "AlternativeProposalNo":-1,
                              "NFuels":0,
                              "NEquipe":0,
                              "NPipeDuct":0,
                              "NThProc":0,
                              "NProducts":0,
                              "NHX":0,
                              "NWHEE":0}
            cgeneraldata.insert(newGeneralData)

            newElectricity = {"Questionnaire_id":newID,
                              "AlternativeProposalNo":-1}
            qelectricity.insert(newElectricity)

            newUHeatPump =  {"Questionnaire_id":newID,
                             "AlternativeProposalNo":-1,
                             "CHPMaintain":1,
                             "CHPType":"CHP Engine",
                             "CHPFuelType":"Natural Gas",
                             "CHPHOp":2000.0,
                             "CHPEff":0.55,
                             "UHPMaintain":1,
                             "UHPType":"compression",
                             "UHPMinHop":1500.0,
                             "UHPDTMax":60.0,
                             "UHPTgenIn":100.0,
                             "UHPmaxT":100.0,
                             "UHPminT":-10.0,
                             "BBMaintain":0,
                             "BBSafety":10.0,
                             "BBRedundancy":1,
                             "BBFuelType":"Natural Gas",
                             "BBHOp":1000.0,
                             "BBPmin":500,
                             "BBEff":0.85,
                             "STSolFra":0.5,
                             "STCollType":"any",
                             "STMinYield":300.0}

### fill default values for design assistants ...
            
            uheatpump.insert(newUHeatPump)

            Status.NoOfAlternatives = -1
                        
        else:

            isNewProject = False

            if originalName is not None:    #if a name is given, overwrite ID
                originalPId = self.getProjectID(originalName)
                self.cleanUpProject(originalPId)

            logTrack("Project (createNewProject): copying from %s [%r]" % (originalPId, originalName))

#..............................................................................
# copy a project
# 1. create a copy of the entry in the main table (questionnaire) with different ID and get the new ID

            sqlQuery = "ProjectID = '%s'" % originalPId
            #additional query necessary for old tables who still have Questionnaire_id instead of ProjectID
            sqlQueryQ = "Questionnaire_id = '%s'" % originalPId
            sqlQueryQ_ID = "Questionnaire_ID = '%s'" % originalPId

            Status.SQL.commit()
            
            newIDdict = copySQLRows(DB.questionnaire, sqlQueryQ_ID, "Questionnaire_ID", None, None)
            newID = newIDdict[originalPId]
#..............................................................................
# copying project data tables

            copySQLRows(DB.sproject, sqlQuery, "SProject_ID", "ProjectID", newID)
            copySQLRows(DB.salternatives, sqlQuery, "SAlternative_ID", "ProjectID", newID)
            
            copySQLRows(DB.cgeneraldata, sqlQueryQ, "CGeneralData_ID", "Questionnaire_id", newID)
            copySQLRows(DB.qelectricity, sqlQueryQ, "QElectricity_ID", "Questionnaire_id", newID)

            copySQLRows(DB.qbuildings, sqlQueryQ, "QBuildings_ID", "Questionnaire_id", newID)
            copyPipeDict = copySQLRows(DB.qdistributionhc, sqlQueryQ, "QDistributionHC_ID", "Questionnaire_id", newID)
            copySQLRows(DB.qfuel, sqlQueryQ, "QFuel_ID", "Questionnaire_id", newID)
            copyEqDict = copySQLRows(DB.qgenerationhc, sqlQueryQ, "QGenerationHC_ID", "Questionnaire_id", newID)
            copySQLRows(DB.qheatexchanger, sqlQuery, "QHeatExchanger_ID", "ProjectID", newID)
            copyProcessesDict = copySQLRows(DB.qprocessdata, sqlQueryQ, "QProcessData_ID", "Questionnaire_id", newID)
            copySQLRows(DB.qproduct, sqlQueryQ, "QProduct_ID", "Questionnaire_id", newID)
            copySQLRows(DB.qrenewables, sqlQueryQ, "QRenewables_ID", "Questionnaire_id", newID)
            copySQLRows(DB.qsurfarea, sqlQuery, "id", "ProjectID", newID)
            copySQLRows(DB.qwasteheatelequip, sqlQuery, "QWasteHeatElEquip_ID", "ProjectID", newID)
            copySQLRows(DB.uheatpump, sqlQueryQ, "UHeatPump_ID", "Questionnaire_id", newID)
            newProcessIds = copyProcessesDict.keys()
            sqlQuery = ("qprocessdata_QProcessData_Id in (" + 
                        ", ".join([str(item) for item in newProcessIds]) + ")")
            inStreamIds = self._getStreamsForProcesses(DB.process_streams_in,
                                                   copyProcessesDict.keys(),
                                                   "streams_in_id")
            self._copyStreams(inStreamIds, copyProcessesDict,
                              DB.process_streams_in, "streams_in_id",
                              DB.streams_in)
            outStreamIds = self._getStreamsForProcesses(DB.process_streams_out,
                                                    copyProcessesDict.keys(),
                                                    "streams_out_id")
            self._copyStreams(outStreamIds, copyProcessesDict,
                              DB.process_streams_out, "streams_out_id",
                              DB.streams_out)
        
#..............................................................................
# copying project detailed schedule tables
            for (oldQProcessdataId, newQProcessdataId) in copyProcessesDict.items():
                copiedProcessPeriods = copySQLRows(DB.process_periods, "qprocessdata_QProcessData_ID = %d" % oldQProcessdataId, "id", "qprocessdata_QProcessData_ID", newQProcessdataId)
                for (oldProcessPeriodsId, newProcessPeriodsId) in copiedProcessPeriods.items():
                    copySQLRows(DB.process_period_profiles, "process_periods_id = %d" % oldProcessPeriodsId, "id", "process_periods_id", newProcessPeriodsId)
                copySQLRows(DB.process_schedules, "qprocessdata_QProcessData_ID = %d" % oldQProcessdataId, "id", "qprocessdata_QProcessData_ID", newQProcessdataId)
                copySQLRows(DB.process_schedules_tolerance_offsets, "qprocessdata_QProcessData_ID = %d" % oldQProcessdataId, "id", "qprocessdata_QProcessData_ID", newQProcessdataId)

#..............................................................................
# re-establish links

            self.reconnectEquipesToPipes(copyEqDict, copyPipeDict)
            
#..............................................................................
# rename project

            q = DB.questionnaire.Questionnaire_ID[newID][0]
            q.Name = check(shortName)
            q.DescripIndustry = check(description)


        Status.SQL.commit()

        self.setActiveProject(newID)

        if isNewProject == True:
            self.setStatus("Q", 0)
            self.getDefaultSetUp()

    def _copyStreams(self, streamIds, processIDsDict, connectionTable,
                     streamIdColumn, streamTable, ANo=None):
        """
        Copy all streams in streamTable that are referred to by Ids in 
        streamIDs. Create a corresponding entry in connectionTable.
        
        :param streamIds: a dict of IDs of streams: process IDs.
        :param processIDsDict: a dict with oldid: newid of copied processdata.
        :param connectionTable: usually process_streams_in or ...out.
        :param streamIdColumn: a String that is the name of the column that holds
        the stream IDs to set. 
        :param streamTable: the source and target table for the stream copies.
        :param ANo: the number of the target alternative proposal if a new
        alternative is created
        :returns: a dict with oldid: newid of the copied rows
        """
        result = {}
        for sId, pId in streamIds.items():
            streamIdsDict = copySQLRows(streamTable, "id = %s" % (sId,) , "id")
            oldId, newId = streamIdsDict.items()[0]
            stream = streamTable.id[newId][0]
            if ANo is None:
                ANo = stream.AlternativeProposalNo
            newEntry = {"qprocessdata_QProcessData_Id"  : processIDsDict[pId],
                        streamIdColumn                  : newId,
                        "ProjectID"                     : stream.ProjectID,
                        "AlternativeProposalNo"         : ANo 
                        }
            connectionTable.insert(newEntry)
            result[oldId] = newId
        return result
            
    def _getStreamsForProcesses(self, connectiontable, processIds, keycolumn):
        """Return a dict of IDs of streams that belong to the processesIds 
        :param connectiontable: usually process_streams_in or ...out.
        :param processIds: a list of IDs of processes.
        :param keycolumn: a String that is the name of the column that holds
        the stream IDs that are searched for.
        :returns: a dict of stream IDs: process IDs.
        """
        result = {}
        for pId in processIds:
            streams = connectiontable.qprocessdata_QProcessData_Id[pId]
            sIds = [stream[keycolumn] for stream in streams]
            for sId in sIds:
                result[sId] = pId
        return result
#------------------------------------------------------------------------------
    def cleanUpProject(self, PId):
#------------------------------------------------------------------------------
#   deletes all tables for a given project with AlternativeProposalNo different
#   than ActiveAlternatives in sproject
#------------------------------------------------------------------------------

        logTrack("Project (cleanUpProject): cleaning project no. %s" % PId)
#..............................................................................
        DB = Status.DB

        sqlQuery = "ProjectID = '%s'" % PId
        sqlQueryQ = "Questionnaire_id = '%s'" % PId

        sprojects = Status.DB.sproject.sql_select(sqlQuery)
        if len(sprojects) > 0:
            sproject = sprojects[0]
            maxANo = sproject.NoOfAlternatives

#..............................................................................
# cleanUp of project data tables: checks ANo and Nones in main entry field (name)

            cleanUpSQLRows(DB.salternatives, sqlQuery, maxANo, "ShortName")
        
            cleanUpSQLRows(DB.cgeneraldata, sqlQueryQ, maxANo)

            cleanUpSQLRows(DB.qbuildings, sqlQueryQ, maxANo, "BuildName")
            cleanUpSQLRows(DB.qdistributionhc, sqlQueryQ, maxANo, "Pipeduct")
            cleanUpSQLRows(DB.qelectricity, sqlQueryQ, maxANo)
            cleanUpSQLRows(DB.qfuel, sqlQueryQ, maxANo, "FuelNo")
            cleanUpSQLRows(DB.qgenerationhc, sqlQueryQ, maxANo, "Equipment")
            cleanUpSQLRows(DB.qheatexchanger, sqlQuery, maxANo, "HXName")
            cleanUpSQLRows(DB.qprocessdata, sqlQueryQ, maxANo, "Process")
            cleanUpSQLRows(DB.qproduct, sqlQueryQ, maxANo, "Product")
#            cleanUpSQLRows(DB.qrenewables,sqlQueryQ,maxANo)
            cleanUpSQLRows(DB.qsurfarea, sqlQuery, mainField="SurfAreaName")  #surface areas have no ANo. fixed for the project !!!!
            cleanUpSQLRows(DB.qwasteheatelequip, sqlQuery, maxANo, "WHEEName")
            cleanUpSQLRows(DB.uheatpump, sqlQueryQ, maxANo)


#------------------------------------------------------------------------------
    def getDefaultSetUp(self):
#------------------------------------------------------------------------------
#   charges the default set-up parameters for a NEW project
#------------------------------------------------------------------------------

        (projectData, generalData) = self.getProjectData()
        setups = Status.DB.psetupdata.PSetUpData_ID['%']
        if (len(setups) > 0):
            setup = setups[0]
            eMixID = setup.ElectricityMix

        else:
            logTrack("Project (getDefaultSetUp): no setup table found in DB. Default mix ID = 1")
            setups.insert({"ElectricityMix": 1})
            eMixID = 1

        emixes = Status.DB.dbelectricitymix.id[eMixID]
        if (len(emixes) > 0):
            emix = emixes[0]
            
            generalData.PEConvEl = emix.PE2ConvEl
            generalData.CO2ConvEl = emix.CO2ConvEl
            generalData.NoNukesConvEl = emix.NoNukesConvEl

        else:
            generalData.PEConvEl = 1. / 0.34
            generalData.CO2ConvEl = 0.5
            generalData.NoNukesConvEl = 99.99
            logTrack("Project (getDefaultSetUp) Electricity Mix %s specified in Set-Up was not found" % eMixID)
           
                     
#------------------------------------------------------------------------------
    def deleteProject(self, PId, name=None):
#------------------------------------------------------------------------------
#   deletes all entries for a given project
#------------------------------------------------------------------------------

        if name is not None:    #if a name is given, overwrite ID
            PId = self.getProjectID(name)

        logMessage(_("Project (deleteProject) -deleting project %r (%r)") % (PId, name))

#..............................................................................
# deleting Q- and corresponding C-Tables

        DB = Status.DB
        sqlQuery = "ProjectID = '%s'" % PId

        #additional query necessary for old tables who still have Questionnaire_id instead of ProjectID
        sqlQueryQ = "Questionnaire_id = '%s'" % PId

        deleteSQLRows(DB.questionnaire, sqlQueryQ)
        deleteSQLRows(DB.sproject, sqlQuery)
        deleteSQLRows(DB.salternatives, sqlQuery)
                   
        deleteSQLRows(DB.cgeneraldata, sqlQueryQ)

        deleteSQLRows(DB.qbuildings, sqlQueryQ)
        deleteSQLRows(DB.qdistributionhc, sqlQueryQ)
        deleteSQLRows(DB.qelectricity, sqlQueryQ)
        deleteSQLRows(DB.qfuel, sqlQueryQ)
        deleteSQLRows(DB.qgenerationhc, sqlQueryQ)
        deleteSQLRows(DB.qheatexchanger, sqlQuery)
        deleteSQLRows(DB.qprocessdata, sqlQueryQ)
        deleteSQLRows(DB.streams_in, sqlQuery)
        deleteSQLRows(DB.streams_out, sqlQuery)
        deleteSQLRows(DB.process_streams_in, sqlQuery)
        deleteSQLRows(DB.process_streams_out, sqlQuery)
        deleteSQLRows(DB.qproduct, sqlQueryQ)
        deleteSQLRows(DB.qrenewables, sqlQueryQ)
        deleteSQLRows(DB.qsurfarea, sqlQuery)
        deleteSQLRows(DB.qwasteheatelequip, sqlQuery)
        deleteSQLRows(DB.uheatpump, sqlQueryQ)

#..............................................................................
# book-keeping: reduce number of alernatives in the system

        self.setActiveProject(-1)

        Status.SQL.commit()


#------------------------------------------------------------------------------		

#------------------------------------------------------------------------------		
# RE-ESTABLISH LINKS AFTER COPYING PROJECTS OR ALTERNATIVES
#------------------------------------------------------------------------------		

#------------------------------------------------------------------------------
    def reconnectEquipesToPipes(self, equipeIDDict, pipeIDDict):
#------------------------------------------------------------------------------

        for equipeID in equipeIDDict.values():
            equipes = Status.DB.qgenerationhc.QGenerationHC_ID[equipeID]
            if len(equipes) > 0:
                equipe = equipes[0]
                pipeLink = equipe["PipeDuctEquip"]
                oldPipeLink = pipeLink
#                print "Project (reconnectEquipesToPipes): equipe ",equipe.Equipment,pipeLink
                pipeIDs = []
                if pipeLink is not None:
                    pipeLinkSplit = pipeLink.split(';')
                    for i in range(len(pipeLinkSplit)):
                        try:
                            pipeIDs.append(long(pipeLinkSplit[i]))
                        except:
                            pass
#                print "Project (reconnectEquipesToPipes): pipeIDs ",pipeIDs
       
                newPipeIDs = []
                for pipeID in pipeIDs:
                    if pipeID in pipeIDDict:
                        newPipeIDs.append("%d" % pipeIDDict[pipeID])
                    else:
                        logDebug(_("Project (reconnect equipes): pipe ID %s was not in old pipe table") % pipeID)
#                print "Project (reconnectEquipesToPipes): pipeIDs ",newPipeIDs
       
                pipeLink = ';'.join(newPipeIDs)
#                print "Project (reconnectEquipesToPipes): new pipeLink ",pipeLink
                equipe["PipeDuctEquip"] = pipeLink
                logTrack("Project (reconnect...): link of equipe %s updated from %s to %s" % (equipeID, oldPipeLink, pipeLink))
                
        Status.SQL.commit()
                                    
#------------------------------------------------------------------------------		
# OTHER SET-UP FUNCTIONS
#------------------------------------------------------------------------------		

#------------------------------------------------------------------------------
    def getLastToolSettings(self):
#------------------------------------------------------------------------------

        stool = Status.DB.stool.STool_ID[1][0]
        Status.PId = stool.ActiveProject
        logTrack(_("New session of tool starting with ProjectID %s") % Status.PId)

        Status.UserType = stool.UserType
        Status.Auditor_ID = stool.Auditor_ID
        Status.UserInteractionLevel = stool.UserInteractionLevel
        Status.LanguageTool = stool.LanguageTool
        Status.UnitsTool = stool.UnitsTool
        
#------------------------------------------------------------------------------
    def setUserInteractionLevel(self, level):
#------------------------------------------------------------------------------
        
        if level in INTERACTIONLEVELS:
            Status.UserInteractionLevel = level
            Status.DB.stool.STool_ID[1][0].UserInteractionLevel = level
            logTrack("Project (setUserInteractionLevel): %s" % level)
        else:
            logDebug("Project (setUserInteractionLevel): ERROR in level %s" % level)

#------------------------------------------------------------------------------
    def setStatus(self, key, value=1):
#------------------------------------------------------------------------------
#   sets a status flag
#------------------------------------------------------------------------------

        sqlQuery = "ProjectID = '%s'" % (Status.PId)
        sprojects = Status.DB.sproject.sql_select(sqlQuery)

        sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        salternatives = Status.DB.salternatives.sql_select(sqlQuery)

        if key == "Q":
            Status.StatusQ = value
            if len(sprojects) > 0: sprojects[0].StatusQ = value
        elif key == "CC":
            Status.StatusCC = value
            if len(sprojects) > 0: sprojects[0].StatusCC = value
        elif key == "CS":
            Status.StatusCS = value
#XXXXXXXX here name confusion between CA and CS -> to be unified to CS once SQL is changed !!!
            if len(sprojects) > 0: sprojects[0].StatusCA = value
        elif key == "Energy":
            Status.StatusEnergy = value
            if len(salternatives) > 0: salternatives[0].StatusEnergy = value
        else:
            logDebug("Project (setStatus): status key %s unknown" % key)

        self.setTreePermissions()

#------------------------------------------------------------------------------
    def setTreePermissions(self):
#------------------------------------------------------------------------------
#   sets the tree permissions ...
#------------------------------------------------------------------------------

        tmp = {}
        allow = (True, 0, "")
        
        tmp.update({_("Edit Industry Data"):allow})   #access to this window is always allowed

#..............................................................................
# StatusPId: actions allowed once an industry is selected

        if (Status.PId > 0):
            if (Status.ANo <= 0 and Status.StatusCC > 0):
                permit = (False, 0, _("Data have already been confirmed as consistent. First unblock before modifying"))
            else:
                permit = allow           
        else:
            permit = (False, 0, _("Cannot access this function. First select a project"))

        tmp.update({_("General data"):permit})
        
#..............................................................................
# StatusQ: actions allowed once general data of the industry have been set and
#   and confirmed

# 1. manipulation of questionnaire

        if (Status.StatusQ > 0):
            if (Status.ANo <= 0 and Status.StatusCC > 0):
                permit = (False, 0, _("Data have already been confirmed as consistent. First unblock before modifying data of present state"))
            else:
                permit = allow           
        else:
            permit = (False, 0, _("Cannot access this function. First open or define a new project and enter general data"))

        tmp.update({_("Energy consumption"):permit})
        tmp.update({_("Processes data"):permit})
        tmp.update({_("Generation of heat and cold"):permit})
        tmp.update({_("Distribution of heat and cold"):permit})
        tmp.update({_("Heat recovery"):permit})
        tmp.update({_("Renewable energies"):permit})
        tmp.update({_("Buildings"):permit})
        tmp.update({_("Economic parameters"):permit})

# 2. access to consistency check window

        if (Status.StatusQ > 0):
            permit = allow
        else:
            permit = (False, 0, _("Cannot access this function. First open or define a new project"))

        tmp.update({_("Consistency Check"):permit})
        
#..............................................................................
# StatusCC: actions allowed once consistency check is concluded

        if (Status.StatusCC > 0):
            if Status.ANo > -1:
                permit = allow
            else:
                permit = (False, 0, _("Cannot display statistics for raw data. change view to checked version"))
        else:
            permit = (False, 0, _("Cannot access this function. First check the data for consistency"))
                                      
        tmp.update({_("Energy statistics"):permit})
        tmp.update({_("Annual data"):permit})
        tmp.update({_("Monthly data"):permit})
        tmp.update({_("Hourly performance\ndata"):permit})
                
        tmp.update({_("Primary energy"):permit})
        tmp.update({_("Final energy by fuels"):permit})
        tmp.update({_("Final energy by equipment"):permit})
        tmp.update({_("Process heat"):permit})
        tmp.update({_("Energy intensity"):permit})
        tmp.update({_("Environmental Impact"):permit})

        tmp.update({_("Monthly demand"):permit})
        tmp.update({_("Monthly supply"):permit})
                   
        tmp.update({_("Hourly demand"):permit})
        tmp.update({_("Hourly supply"):permit})


        tmp.update({_("Benchmark check"):permit})
        tmp.update({_("Global energy intensity"):permit})
        tmp.update({_("SEC by product"):permit})
        tmp.update({_("SEC by process"):permit})
        
        tmp.update({_("Alternative proposals"):permit})

#..............................................................................
# ActiveAlternative: actions allowed only for ANo > 0

        if (Status.ANo > 0):
            permit = allow
        else:
            permit = (False, 0, _("Cannot access this function for the present state of the industry.\nFirst define a new alternative !"))
                          
        tmp.update({_("Design"):permit})

        tmp.update({_("Process optimisation"):permit})
        tmp.update({_("Process optimisation interface 1"):permit})
        tmp.update({_("Process optimisation interface 2"):permit})

        tmp.update({_("Pinch analysis"):permit})
        tmp.update({_("Pinch interface 1"):permit})
        tmp.update({_("Pinch interface 2"):permit})
               
        tmp.update({_("HX network"):permit})
        tmp.update({_("H&C Supply"):permit})
        tmp.update({_("H&C Storage"):permit})
        tmp.update({_("CHP"):permit})
        tmp.update({_("Solar Thermal"):permit})
        tmp.update({_("Heat Pumps"):permit})
        tmp.update({_("Biomass"):permit})
        tmp.update({_("Chillers"):permit})
        tmp.update({_("Boilers & burners"):permit})

        tmp.update({_("H&C Distribution"):permit})

        tmp.update({_("Energy performance"):permit})
        tmp.update({_("Economic analysis"):permit})
        tmp.update({_("Economics 1"):permit})
        tmp.update({_("Economics 2"):permit})

#..............................................................................
# StatusCC: actions allowed once consistency check is concluded

        if (Status.StatusCC > 0):
            permit = allow
        else:
            permit = (False, 0, _("Cannot access this function. First check the data for consistency"))
            
        tmp.update({_("Comparative study"):permit})

        tmp.update({_("Report"):permit})
        tmp.update({_("Report generation"):permit})

        Status.main.treePermissions = tmp
        
#------------------------------------------------------------------------------
    def getStatus(self):
#------------------------------------------------------------------------------
#   sets a status flag
#------------------------------------------------------------------------------

        sqlQuery = "ProjectID = '%s'" % (Status.PId)
        sprojects = Status.DB.sproject.sql_select(sqlQuery)

        if len(sprojects) > 0:
            sproject = sprojects[0]
            if sproject.StatusQ is not None: Status.StatusQ = sproject.StatusQ
            else:
                sproject.StatusQ = EINSTEIN_NOTOK
                Status.StatusQ = EINSTEIN_NOTOK

            if sproject.StatusCC is not None: Status.StatusCC = sproject.StatusCC
            else:
                sproject.StatusCC = EINSTEIN_NOTOK
                Status.StatusCC = EINSTEIN_NOTOK

            if sproject.HRTool is not None: Status.HRTool = sproject.HRTool
            else: Status.HRTool = "PE2"
            
        else:
            logTrack("Project (getStatus): could not find project table of last opened project")
#XXX -> getStatus is called BEFORE GUI is built -> logError not yet available !!!
            Status.StatusCC = EINSTEIN_NOTOK
            Status.StatusQ = EINSTEIN_NOTOK


        sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        salternatives = Status.DB.salternatives.sql_select(sqlQuery)

        if len(salternatives) > 0:
            a = salternatives[0]
            if a.StatusEnergy is not None: Status.StatusEnergy = a.StatusEnergy
            else:
                a.StatusEnergy = EINSTEIN_NOTOK
                Status.StatusEnergy = EINSTEIN_NOTOK

        self.setTreePermissions()

#------------------------------------------------------------------------------
    def deleteProduct(self, productName):
#------------------------------------------------------------------------------
#   deletes all entries for the original ANo
#------------------------------------------------------------------------------

        logTrack("Project (deleteProduct) - project %s, alternative %s, deleting product %s " % \
                 (Status.PId, Status.ANo, productName))

#..............................................................................
# deleting Q- and corresponding C-Tables

        DB = Status.DB
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' AND Product = '%s'"\
                    % (Status.PId, Status.ANo, check(productName))

        deleteSQLRows(DB.qproduct, sqlQueryQ)

#------------------------------------------------------------------------------
    def getProducts(self, PId=None):
#------------------------------------------------------------------------------
#   returns a table of existing equipment
#------------------------------------------------------------------------------

        if PId is None:
            sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        else:
            sqlQuery = "Questionnaire_id = '%s'" % (PId)
            
        products = Status.DB.qproduct.sql_select(sqlQuery)
        
        return products

#------------------------------------------------------------------------------
    def getProductList(self, key, PId=None):
#------------------------------------------------------------------------------
#   returns a table of existing equipment
#------------------------------------------------------------------------------

        products = self.getProducts(PId)
        
        productList = []
        for product in products:
            if isinstance(product[key], str) or isinstance(product[key], unicode):
                productList.append(unicode(product[key], "utf-8"))
            else:
                productList.append(product[key])

        return productList

#------------------------------------------------------------------------------
    def addEquipmentDummy(self):
#------------------------------------------------------------------------------
#   enters a dummy of a new equiment
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        equipments = Status.DB.qgenerationhc.sql_select(sqlQuery)
        NEquipe = len(equipments)
        tmp = {
            "Questionnaire_id":Status.PId,
            "AlternativeProposalNo":Status.ANo,
            "EqNo": NEquipe + 1,
            "CascadeIndex": NEquipe + 1,
            "Equipment":"dummy"
            }          
        newID = Status.DB.qgenerationhc.insert(tmp)
        newEquipe = Status.DB.qgenerationhc.QGenerationHC_ID[newID][0]

        NEquipe += 1

        generaldata = Status.DB.cgeneraldata.sql_select(sqlQuery)
        generaldata[0].NEquipe = NEquipe
        Status.NEquipe = NEquipe

        Status.SQL.commit()

        Status.int.changeInCascade(NEquipe)     # updates Status-flags
        
        return newEquipe

#------------------------------------------------------------------------------
    def deleteEquipment(self, eqID):
#------------------------------------------------------------------------------
#   deletes all entries for a given equipment
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        print "Project (deleteEquipment)", eqID
        
        DB = Status.DB
        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' AND QGenerationHC_ID = '%s'"\
                    % (Status.PId, Status.ANo, eqID)  #query is redundant, but maintained as is for security

        equipes = Status.DB.qgenerationhc.sql_select(sqlQuery)
        if len(equipes) > 0:
            equipmentName = equipes[0].Equipment
            deletedIndex = equipes[0].CascadeIndex
            deleteSQLRows(DB.qgenerationhc, sqlQuery)
        else:
            equipmentName = None
            logDebug("Project (deleteEquipment): cannont delete equipment with ID %s. No corresponding entry in database" % eqID)
            return

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY EqNo ASC" % (Status.PId, Status.ANo)
        equipes = Status.DB.qgenerationhc.sql_select(sqlQuery)

        for i in range(len(equipes)): #assign new EqNo in QGenerationHC table
            equipes[i].EqNo = i + 1

        Status.SQL.commit()

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY CascadeIndex ASC" % (Status.PId, Status.ANo)
        equipes = Status.DB.qgenerationhc.sql_select(sqlQuery)

        for i in range(len(equipes)): #assign new Cascade Index in QGenerationHC table
            equipes[i].CascadeIndex = i + 1

        Status.int.cascadeUpdateLevel = min(Status.int.cascadeUpdateLevel, deletedIndex - 1)
        
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)  
        cgeneraldata = Status.DB.cgeneraldata.sql_select(sqlQueryQ)
        cgeneraldata[0].NEquipe = len(equipes)
        Status.NEquipe = len(equipes)

        Status.SQL.commit()

#..............................................................................
# delete heat exchangers connected to the deleted equipment
        
        sourceName_h = Status.prj.getHXList("HXSource")
        sourceID_h = Status.prj.getHXList("QHeatExchanger_ID")
        sinkName_h = Status.prj.getHXList("HXSink")
        sinkID_h = Status.prj.getHXList("QHeatExchanger_ID")

        blackList = []
        for h in range(len(sourceName_h)):
            if sourceName_h[h] == equipmentName and sourceID_h[h] not in blackList:
                    blackList.append(sourceID_h[h])
        for h in range(len(sinkName_h)):
            if sinkName_h[h] == equipmentName and sinkID_h[h] not in blackList:
                blackList.append(sinkID_h[h])
                
        for i in blackList:
            self.deleteHX(i)

#------------------------------------------------------------------------------
    def getEquipments(self, PId=None, cascade=False):
        """
        Return a pSQL.Result of all equipment used in the current industry.
        
        If the PId is given all equipment of all alternative proposals is
        returned, otherwise only of the current one.
        @param PId: Which Questinonnaire_id is requested if not the current one
        which is the default.
        @param cascade: FIXME: what is that for?
        
        """
        if PId is None:
            if cascade == False:
                sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY EqNo ASC" % (Status.PId, Status.ANo)
            else:
                sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY CascadeIndex ASC" % (Status.PId, Status.ANo)
        else:
            if cascade == False:
                sqlQuery = "Questionnaire_id = '%s' ORDER BY EqNo ASC" % (PId)
            else:
                sqlQuery = "Questionnaire_id = '%s' ORDER BY CascadeIndex ASC" % (PId)
                

        equipments = Status.DB.qgenerationhc.sql_select(sqlQuery)

        if PId is None:
            Status.NEquipe = len(equipments)
        
        return equipments

#------------------------------------------------------------------------------
    def getEquipe(self, id):
#------------------------------------------------------------------------------
#   returns the equipment with id 
#------------------------------------------------------------------------------

        equipes = Status.DB.qgenerationhc.QGenerationHC_ID[id]
        if len(equipes) > 0:
            return equipes[0]
        else:
            return None
        
#------------------------------------------------------------------------------
    def getEquipmentList(self, key, PId=None, cascade=False):
#------------------------------------------------------------------------------
#   returns a list of existing equipment
#------------------------------------------------------------------------------

        eqs = self.getEquipments(PId, cascade)
        
        eqList = []
        for eq in eqs:
            if isinstance(eq[key], str) or isinstance(eq[key], unicode):
                eqList.append(unicode(eq[key], "utf-8"))
            else:
                eqList.append(eq[key])

        return eqList

    def getStreams(self, qProcessData_ID):
        """
        Return a 2-tuple of all streams associated with the given 
        qProcessData_ID.
        
        :param qProcessData_ID: Numeric database ID of the process for which
        the streams are requested
        :returns: A tuple of lists (inStreams, outStreams).
        """
        sqlQuery = "qprocessdata_QProcessData_ID= '%s' " % (qProcessData_ID,)
        inStreamsTable = Status.DB.process_streams_in
        inStreamsTable.x_ref(Status.DB.streams_in, "streams_in_id", "id")
        outStreamsTable = Status.DB.process_streams_out
        outStreamsTable.x_ref(Status.DB.streams_out, "streams_out_id", "id")
        inStreams = inStreamsTable.sql_select(sqlQuery)
        outStreams = outStreamsTable.sql_select(sqlQuery)
        inStreams = [stream.streams_in for stream in inStreams]
        outStreams = [stream.streams_out for stream in outStreams]
        return (inStreams, outStreams)
        
#------------------------------------------------------------------------------
    def addFuelDummy(self):
#------------------------------------------------------------------------------
#   deletes all entries for the original ANo
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        fuels = Status.DB.qfuel.sql_select(sqlQuery)
        NFuels = len(fuels)
        tmp = {
            "Questionnaire_id":Status.PId,
            "AlternativeProposalNo":Status.ANo,
            "FuelNo": NFuels + 1
            }          
        newID = Status.DB.qfuel.insert(tmp)

        NFuels += 1

        generaldata = Status.DB.cgeneraldata.sql_select(sqlQuery)
        generaldata[0].NFuels = NFuels

        Status.SQL.commit()

        return newID

#------------------------------------------------------------------------------
    def deleteFuel(self, DBFuel_id):
#------------------------------------------------------------------------------
#   deletes all entries for a given fuel type
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        DB = Status.DB
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' AND DBFuel_id = '%s'"\
                    % (Status.PId, Status.ANo, DBFuel_id)

        deleteSQLRows(DB.qfuel, sqlQueryQ)

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY FuelNo ASC" % (Status.PId, Status.ANo)
        fuels = Status.DB.qfuel.sql_select(sqlQuery)

        for i in range(len(fuels)): #assign new EqNo in QGenerationHC table
            fuels[i].FuelNo = i + 1

        
        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        generaldata = Status.DB.cgeneraldata.sql_select(sqlQuery)
        generaldata[0].NFuels = len(fuels)

        Status.SQL.commit()

#------------------------------------------------------------------------------
    def addProcessDummy(self):
#------------------------------------------------------------------------------
#   deletes all entries for the original ANo
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)

        processes = Status.DB.qprocessdata.sql_select(sqlQuery)
        NThProc = len(processes)
        tmp = {
            "Questionnaire_id":Status.PId,
            "AlternativeProposalNo":Status.ANo,
            "ProcNo": NThProc + 1
            }          
        newID = Status.DB.qprocessdata.insert(tmp)
        newProcess = Status.DB.qprocessdata.QProcessData_ID[newID][0]

        NThProc += 1

        generaldata = Status.DB.cgeneraldata.sql_select(sqlQuery)
        generaldata[0].NThProc = NThProc

        Status.SQL.commit()

        return newProcess

#------------------------------------------------------------------------------
    def deleteProcess(self, processID):
#------------------------------------------------------------------------------
#   deletes all entries for a given fuel type
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        DB = Status.DB
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' AND QProcessData_ID = '%s'"\
                    % (Status.PId, Status.ANo, processID)  #query is redundant, but maintained as is for security
        deleteSQLRows(DB.qprocessdata, sqlQueryQ)

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY ProcNo ASC" % (Status.PId, Status.ANo)
        processes = Status.DB.qprocessdata.sql_select(sqlQuery)

        for i in range(len(processes)): #assign new EqNo in QGenerationHC table
            processes[i].ProcNo = i + 1

        
        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        generaldata = Status.DB.cgeneraldata.sql_select(sqlQuery)
        generaldata[0].NThProc = len(processes)
        
        inStreamIds = self._getStreamsForProcesses(DB.process_streams_in,
                                                   [processID],
                                                   "streams_in_id")
        outStreamIds = self._getStreamsForProcesses(DB.process_streams_out,
                                                   [processID],
                                                   "streams_out_id")
        for id in inStreamIds:
            self.deleteStream(id, Status.DB.streams_in,
                              Status.DB.process_streams_in, "streams_in_id")
        for id in outStreamIds:
            self.deleteStream(id, Status.DB.streams_out,
                              Status.DB.process_streams_out, "streams_out_id")
        
        Status.SQL.commit()

    def deleteStream(self, id, streamTable, connectionTable, referenceColumn):
        """
        Delete the stream with ID id from table streamTable, and remove the
        corresponding entry from the connectionTable.
        :param id: stream id in streamTable
        :param streamTable: usually streams_in or ...out.
        :param connectionTable: usually process_streams_in or ...out. 
        :param referenceColumn: a String, usually "streams_in_id" or 
        "streams_out_id"
        """
        sqlQueryQ = "id = '%s' " % (id,)
        deleteSQLRows(streamTable, sqlQueryQ)
        sqlQueryQ = "%s = '%s' " % (referenceColumn, id)
        deleteSQLRows(connectionTable, sqlQueryQ)

#------------------------------------------------------------------------------
    def addPipeDummy(self):
#------------------------------------------------------------------------------
#   adds a new empty pipe field in table qdistributionhc
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        pipes = self.getPipes()
        NPipes = len(pipes)
        tmp = {
            "Questionnaire_id":Status.PId,
            "AlternativeProposalNo":Status.ANo,
            "PipeDuctNo": NPipes + 1
            }          
        newID = Status.DB.qdistributionhc.insert(tmp)
        newPipe = Status.DB.qdistributionhc.QDistributionHC_ID[newID][0]

        NPipes += 1

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        cgeneraldata = Status.DB.cgeneraldata.sql_select(sqlQuery)
        cgeneraldata[0].NPipeDuct = NPipes

        Status.SQL.commit()

        return newPipe

#------------------------------------------------------------------------------
    def deletePipe(self, pipeID):
#------------------------------------------------------------------------------
#   deletes all entries for a given fuel type
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        DB = Status.DB
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' AND QDistributionHC_ID = '%s'"\
                    % (Status.PId, Status.ANo, pipeID)  #query is redundant, but maintained as is for security

        deleteSQLRows(DB.qdistributionhc, sqlQueryQ)

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY PipeDuctNo ASC" % (Status.PId, Status.ANo)
        pipes = Status.DB.qdistributionhc.sql_select(sqlQuery)

        for i in range(len(pipes)): #assign new EqNo in QGenerationHC table
            pipes[i].PipeDuctNo = i + 1
            pass

        
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)  
        cgeneraldata = Status.DB.cgeneraldata.sql_select(sqlQueryQ)
        cgeneraldata[0].NPipeDuct = len(pipes)

        Status.SQL.commit()

#------------------------------------------------------------------------------
    def getPipes(self, PId=None):
#------------------------------------------------------------------------------
#   returns a list of existing heat exchangers
#------------------------------------------------------------------------------

        if PId is None:
            sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY PipeDuctNo ASC" % (Status.PId, Status.ANo)
        else:
            sqlQuery = "Questionnaire_id = '%s' ORDER BY PipeDuctNo ASC" % (PId)
            
        pipes = Status.DB.qdistributionhc.sql_select(sqlQuery)
        
        return pipes
#------------------------------------------------------------------------------
    def getPipeList(self, key, PId=None):
#------------------------------------------------------------------------------
#   returns a list of existing heat exchangers
#------------------------------------------------------------------------------

        pipes = self.getPipes(PId)
        
        pipeList = []
        for pipe in pipes:
            if isinstance(pipe[key], str) or isinstance(pipe[key], unicode):
                pipeList.append(unicode(pipe[key], "utf-8"))
            else:
                pipeList.append(pipe[key])

        return pipeList
    
#------------------------------------------------------------------------------
    def getPipeDict(self):
#------------------------------------------------------------------------------
#   returns a list of fuels in DB
#------------------------------------------------------------------------------

        pipes = self.getPipes()     
        pipeDict = {}
        for pipe in pipes:
            pipeName = unicode(pipe["Pipeduct"], "utf-8")
            pipeID = pipe["QDistributionHC_ID"]
            pipeDict.update({pipeID:pipeName})

        return pipeDict

#==============================================================================
#------------------------------------------------------------------------------
    def addBuildingDummy(self):
#------------------------------------------------------------------------------
#   deletes all entries for the original ANo
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)

        buildings = Status.DB.qbuildings.sql_select(sqlQuery)
        NBuildings = len(buildings)
        tmp = {
            "Questionnaire_id":Status.PId,
            "AlternativeProposalNo":Status.ANo,
#            "BuildingNo": NBuildings+1
            }          
        newID = Status.DB.qbuildings.insert(tmp)

        NBuildings += 1

        sqlQuery = "Questionnaire_id = '%s'" % (Status.PId)
        questionnaire = Status.DB.questionnaire.sql_select(sqlQuery)
        questionnaire[0].NBuild = NBuildings

        Status.SQL.commit()

        return newID

#------------------------------------------------------------------------------
    def deleteBuilding(self, buildingID):
#------------------------------------------------------------------------------
#   deletes all entries for a given fuel type
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        DB = Status.DB
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' AND QBuildings_ID = '%s'"\
                    % (Status.PId, Status.ANo, buildingID)  #query is redundant, but maintained as is for security

#        print "Project (deleteBuilding): query"
#        print sqlQueryQ
        
        deleteSQLRows(DB.qbuildings, sqlQueryQ)

#        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY BuildingNo ASC"%(Status.PId,Status.ANo)
        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        buildings = Status.DB.qbuildings.sql_select(sqlQuery)

        for i in range(len(buildings)): #assign new EqNo in QGenerationHC table
#            buildings[i].BuildingNo = i+1
            pass

        
        sqlQuery = "Questionnaire_id = '%s'" % (Status.PId)
        questionnaire = Status.DB.questionnaire.sql_select(sqlQuery)
        questionnaire[0].NBuild = len(buildings)

        Status.SQL.commit()

#------------------------------------------------------------------------------
    def addHXDummy(self):
#------------------------------------------------------------------------------
#   adds a new empty HX field in table qgenerationhc
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)

        hxes = Status.DB.qheatexchanger.sql_select(sqlQuery)
        NHX = len(hxes)
        tmp = {
            "ProjectID":Status.PId,
            "AlternativeProposalNo":Status.ANo,
            "HXNo": NHX + 1
            }          
        newID = Status.DB.qheatexchanger.insert(tmp)
        newhx = Status.DB.qheatexchanger.QHeatExchanger_ID[newID][0]

        NHX += 1

        cgeneraldata = Status.DB.cgeneraldata.sql_select(sqlQueryQ)
        cgeneraldata[0].NHX = NHX

        Status.SQL.commit()

        return newhx

#------------------------------------------------------------------------------
    def deleteHX(self, HXID):
#------------------------------------------------------------------------------
#   deletes all entries for a given heat exchanger
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        DB = Status.DB
        sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s' AND QHeatExchanger_ID = '%s'"\
                    % (Status.PId, Status.ANo, HXID)  #query is redundant, but maintained as is for security

        deleteSQLRows(DB.qheatexchanger, sqlQuery)

        sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s' ORDER BY HXNo ASC" % (Status.PId, Status.ANo)
        hxes = Status.DB.qheatexchanger.sql_select(sqlQuery)

        for i in range(len(hxes)): #assign new EqNo in QGenerationHC table
            hxes[i].HXNo = i + 1
            pass

        
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)  
        cgeneraldata = Status.DB.cgeneraldata.sql_select(sqlQueryQ)
        cgeneraldata[0].NHX = len(hxes)

        Status.SQL.commit()

#------------------------------------------------------------------------------
    def getHXes(self):
#------------------------------------------------------------------------------
#   returns a list of existing heat exchangers
#------------------------------------------------------------------------------

        sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s' ORDER BY HXNo ASC" % (Status.PId, Status.ANo)
        hxes = Status.DB.qheatexchanger.sql_select(sqlQuery)
        
        return hxes

#------------------------------------------------------------------------------
    def getHXList(self, key):
#------------------------------------------------------------------------------
#   returns a list of existing heat exchangers
#------------------------------------------------------------------------------

        hxes = self.getHXes()
        
        HXList = []
        for hx in hxes:
            
            if isinstance(hx[key], str) or isinstance(hx[key], unicode):
                HXList.append(unicode(hx[key], "utf-8"))
            else:
                HXList.append(hx[key])

        return HXList

#------------------------------------------------------------------------------
    def addWHEEDummy(self):
#------------------------------------------------------------------------------
#   adds a new empty WHEE field in table qwasteheatelequip
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        whees = self.getWHEEs()
        NWHEE = len(whees)
        tmp = {
            "ProjectID":Status.PId,
            "AlternativeProposalNo":Status.ANo,
            "WHEENo": NWHEE + 1
            }          
        newID = Status.DB.qwasteheatelequip.insert(tmp)
        newwhee = Status.DB.qwasteheatelequip.QWasteHeatElEquip_ID[newID][0]

        NWHEE += 1

        sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        cgeneraldata = Status.DB.cgeneraldata.sql_select(sqlQuery)
        cgeneraldata[0].NWHEE = NWHEE

        Status.SQL.commit()

        return newwhee

#------------------------------------------------------------------------------
    def deleteWHEE(self, WHEEID):
#------------------------------------------------------------------------------
#   deletes all entries for a given heat exchanger
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        DB = Status.DB
        sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s' AND QWasteHeatElEquip_ID = '%s'"\
                    % (Status.PId, Status.ANo, WHEEID)  #query is redundant, but maintained as is for security

        deleteSQLRows(DB.qwasteheatelequip, sqlQuery)

        sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s' ORDER BY WHEENo ASC" % (Status.PId, Status.ANo)
        whees = Status.DB.qwasteheatelequip.sql_select(sqlQuery)

        for i in range(len(whees)): #assign new EqNo in QGenerationHC table
            whees[i].WHEENo = i + 1
            pass

        
        sqlQueryQ = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)  
        cgeneraldata = Status.DB.cgeneraldata.sql_select(sqlQueryQ)
        cgeneraldata[0].NWHEE = len(whees)

        Status.SQL.commit()

#------------------------------------------------------------------------------
    def getWHEEs(self, PId=None):
#------------------------------------------------------------------------------
#   returns a list of existing heat exchangers
#------------------------------------------------------------------------------

        if PId is None:
            sqlQuery = "ProjectID = '%s' AND AlternativeProposalNo = '%s' ORDER BY WHEENo ASC" % (Status.PId, Status.ANo)
        else:
            sqlQuery = "ProjectID = '%s' ORDER BY WHEENo ASC" % (PId)
            
        whees = Status.DB.qwasteheatelequip.sql_select(sqlQuery)
        
        return whees

#------------------------------------------------------------------------------
    def getWHEEList(self, key, PId=None):
#------------------------------------------------------------------------------
#   returns a list of existing heat exchangers
#------------------------------------------------------------------------------

        whees = self.getWHEEs(PId)
        
        WHEEList = []
        for whee in whees:
            if isinstance(whee[key], str) or isinstance(whee[key], unicode):
                WHEEList.append(unicode(whee[key], "utf-8"))
            else:
                WHEEList.append(whee[key])

        return WHEEList

#------------------------------------------------------------------------------
    def addSurfaceDummy(self):
#------------------------------------------------------------------------------
#   adds a new empty Surface to qsurfarea
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        surfaces = self.getSurfaces()
        NSurfaces = len(surfaces)
        tmp = {
            "ProjectID":Status.PId,
            "SurfAreaNo":(NSurfaces + 1),
            "SurfAreaName":"dummy"
            }          
        newID = Status.DB.qsurfarea.insert(tmp)
        newSurface = Status.DB.qsurfarea.id[newID][0]

        Status.SQL.commit()

        return newSurface

#------------------------------------------------------------------------------
    def deleteSurface(self, surfaceID):
#------------------------------------------------------------------------------
#   deletes all entries for a given heat exchanger
#------------------------------------------------------------------------------

#..............................................................................
# deleting Q- and corresponding C-Tables

        DB = Status.DB
        sqlQuery = "ProjectID = '%s' AND id = '%s'"\
                    % (Status.PId, surfaceID)  #query is redundant, but maintained as is for security

        deleteSQLRows(DB.qsurfarea, sqlQuery)

        surfaces = self.getSurfaces()

        for i in range(len(surfaces)): #assign new EqNo in QGenerationHC table
            surfaces[i].SurfAreaNo = i + 1

        Status.SQL.commit()

#------------------------------------------------------------------------------
    def getSurfaces(self, PId=None):
#------------------------------------------------------------------------------
#   returns a list of existing heat exchangers
#------------------------------------------------------------------------------

        if PId is None:
            sqlQuery = "ProjectID = '%s' ORDER BY SurfAreaNo ASC" % (Status.PId)
        else:
            sqlQuery = "ProjectID = '%s' ORDER BY SurfAreaNo ASC" % (PId)
            
        surfaces = Status.DB.qsurfarea.sql_select(sqlQuery)
        if PId is None:
            self.surfaces = surfaces
        
        return surfaces

#------------------------------------------------------------------------------
    def getSurfaceList(self, key, PId=None):
#------------------------------------------------------------------------------
#   returns a list of existing heat exchangers
#------------------------------------------------------------------------------

        surfaces = self.getSurfaces(PId)
        
        surfaceList = []
        for surface in surfaces:
            if isinstance(surface[key], str) or isinstance(surface[key], unicode):
                surfaceList.append(unicode(surface[key], "utf-8"))
            else:
                surfaceList.append(surface[key])

        return surfaceList

#------------------------------------------------------------------------------
    def getFuels(self, PId=None):
#------------------------------------------------------------------------------
#   returns a table of existing equipment
#------------------------------------------------------------------------------

        if PId is None:
            sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY FuelNo ASC" % (Status.PId, Status.ANo)
        else:
            sqlQuery = "Questionnaire_id = '%s' ORDER BY FuelNo ASC" % (PId)
        fuels = Status.DB.qfuel.sql_select(sqlQuery)
        
        return fuels

#------------------------------------------------------------------------------
    def getFuelList(self, key, PId=None):
#------------------------------------------------------------------------------
#   returns a table of existing equipment
#------------------------------------------------------------------------------

        fuels = self.getFuels(PId)
        
        fuelList = []
        for fuel in fuels:
            if isinstance(fuel[key], str) or isinstance(fuel[key], unicode):
                fuelList.append(unicode(fuel[key], "utf-8"))
            else:
                fuelList.append(fuel[key])

        return fuelList

#------------------------------------------------------------------------------
    def getProcesses(self, PId=None):
        """
        Return a pSQL.result list of all processes for the current alternative
        proposal.
        
        :param PId: If the Questionaire_id is given explicitly, all processes
        of all proposals are returned.
        :returns: A list of pSQL.result objects for all processes of the current
        alternative proposal.
        """
        if PId is None:
            sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY ProcNo ASC" % (Status.PId, Status.ANo)
        else:
            sqlQuery = "Questionnaire_id = '%s' ORDER BY ProcNo ASC" % (PId)

        self.processes = Status.DB.qprocessdata.sql_select(sqlQuery)
        
        return self.processes

#------------------------------------------------------------------------------
    def getProcessList(self, key, PId=None):
#------------------------------------------------------------------------------
#   returns a list of existing heat exchangers
#------------------------------------------------------------------------------

        processes = self.getProcesses(PId)
        
        processList = []
        for process in processes:
            if isinstance(process[key], str) or isinstance(process[key], unicode):
                processList.append(unicode(process[key], "utf-8"))
            else:
                processList.append(process[key])

        return processList

#------------------------------------------------------------------------------
    def getQFuels(self, PId=None):
#------------------------------------------------------------------------------
#   returns a list of fluids used in the project
#------------------------------------------------------------------------------

        if PId is None:
            sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s' ORDER BY FuelNo ASC" % (Status.PId, Status.ANo)
        else:
            sqlQuery = "Questionnaire_id = '%s' ORDER BY FuelNo ASC" % (PId)
            
        self.qfuel = Status.DB.qfuel.sql_select(sqlQuery)
        
        return self.qfuel

#------------------------------------------------------------------------------
    def getElectricity(self, PId=None):
#------------------------------------------------------------------------------
#   returns a list of fluids used in the project
#------------------------------------------------------------------------------

        if PId is None:
            sqlQuery = "Questionnaire_id = '%s' AND AlternativeProposalNo = '%s'" % (Status.PId, Status.ANo)
        else:
            sqlQuery = "Questionnaire_id = '%s'" % (PId)
            
        self.qelectricity = Status.DB.qelectricity.sql_select(sqlQuery)
        
        return self.qelectricity

#------------------------------------------------------------------------------
    def getQFuelList(self, key, PId=None):
#------------------------------------------------------------------------------
#   returns a list of existing heat exchangers
#------------------------------------------------------------------------------

        fuels = self.getQFuels(PId)
        
        fuelList = []
        for fuel in fuels:
            if isinstance(fuel[key], str) or isinstance(fuel[key], unicode):
                fuelList.append(unicode(fuel[key], "utf-8"))
            else:
                fuelList.append(fuel[key])

        return fuelList

#------------------------------------------------------------------------------
    def getFluidDict(self):
#------------------------------------------------------------------------------
#   returns a list of existing heat exchangers
#------------------------------------------------------------------------------

        sqlQuery = "% ORDER BY FluidName ASC"
#        fluids = Status.DB.dbfluid.sql_select(sqlQuery)
        fluids = Status.DB.dbfluid.FluidName["%"]       
        fluidDict = {}
        for fluid in fluids:
            fluidName = unicode(fluid["FluidName"], "utf-8")
            fluidID = fluid["DBFluid_ID"]
            fluidDict.update({fluidID:fluidName})

        return fluidDict

#------------------------------------------------------------------------------
    def getFuelDict(self):
#------------------------------------------------------------------------------
#   returns a list of fuels in DB
#------------------------------------------------------------------------------

        sqlQuery = "% ORDER BY FuelName ASC"
#        fluids = Status.DB.dbfuel.sql_select(sqlQuery)
        fuels = Status.DB.dbfuel.FuelName["%"]       
        fuelDict = {}
        for fuel in fuels:
            fuelName = unicode(fuel["FuelName"], "utf-8")
            fuelID = fuel["DBFuel_ID"]
            fuelDict.update({fuelID:fuelName})

        return fuelDict

#------------------------------------------------------------------------------
    def getUnitOpDict(self):
#------------------------------------------------------------------------------
#   returns a list of unit operations in DB
#------------------------------------------------------------------------------

        sqlQuery = "% ORDER BY UnitOperation ASC"
#        fluids = Status.DB.dbfuel.sql_select(sqlQuery)
        unitOperations = Status.DB.dbunitoperation.UnitOperation["%"]       
        unitOpDict = {}
        for unitOperation in unitOperations:
            unitOperationName = unicode(unitOperation["UnitOperation"], "utf-8")
            unitOperationID = unitOperation["DBUnitOperation_ID"]
            unitOpDict.update({unitOperationID:unitOperationName})

        return unitOpDict

#------------------------------------------------------------------------------
    def getNACEDict(self, branch=None):
#------------------------------------------------------------------------------
#   returns a list of unit operations in DB
#------------------------------------------------------------------------------

        naceTable = Status.DB.dbnacecode.DBNaceCode_ID['%']       
        naceDict = {}
        naceSubDict = {}
        for entry in naceTable:
            naceCode = entry.CodeNACE
            naceSubCode = naceCode + "." + entry.CodeNACEsub
            naceName = unicode(entry.NameNACE, "utf-8")
            naceSubName = unicode(entry.NameNACEsub, "utf-8")
            naceDict.update({naceCode:naceName})
            if branch == naceName:
                naceSubDict.update({naceSubCode:naceSubName})

#        print "Project (getNACEDict): branch = ",branch
#        print "---"
#        print "naceDict = ",naceDict
#        print "---"
#        print "naceSubDict = ",naceSubDict
#        print "------------------------------------------------"
            
        return (naceDict, naceSubDict)

#------------------------------------------------------------------------------
    def getFluidAndFuelList(self, PId=None):
#------------------------------------------------------------------------------
#   returns a list of all fluids and fuels used in a project
#   if PId = None: returns for some alternative in the active project
#   if PId specified: returns for the total project (all alternatives)
#------------------------------------------------------------------------------

        fuelList = Status.prj.getQFuelList("DBFuel_id", PId)
        fuelIDs = []
        for fuelID in fuelList:
            if fuelID is not None:
                newID = int(fuelID)
                if newID not in fuelIDs:    #avoid double counting !!!
                    fuelIDs.append(newID)

        fluidList = []
        fluidList.extend(Status.prj.getEquipmentList("Refrigerant", PId))
        fluidList.extend(Status.prj.getPipeList("HeatDistMedium", PId))
        fluidList.extend(Status.prj.getProcessList("ProcMedDBFluid_id", PId))
        fluidList.extend(Status.prj.getProcessList("ProcMedOut", PId))
        fluidList.extend(Status.prj.getProcessList("SupplyMedDBFluid_id", PId))
        fluidList.extend(Status.prj.getWHEEList("WHEEMedium", PId))
        
        fluidIDs = []
        for fluidID in fluidList:
            if fluidID is not None:
                newID = int(fluidID)
                if newID not in fluidIDs:    #avoid double counting !!!
                    fluidIDs.append(newID)
           
        return (fluidIDs, fuelIDs)

#------------------------------------------------------------------------------
    def substituteFluidID(self, PId, oldID, newID):
#------------------------------------------------------------------------------
#   substitutes the links to fluids in import of project tables
#------------------------------------------------------------------------------

        eqs = Status.DB.qgenerationhc.Questionnaire_id[PId].Refrigerant[oldID]
        for eq in eqs:
            eq.Refrigerant = newID
            logTrack("Project (substituteFluidID): table qgenerationhc - FluidID %s substituted by %s in ID %s" % \
                     (oldID, newID, eq.QGenerationHC_ID))
        
        pipes = Status.DB.qdistributionhc.Questionnaire_id[PId].HeatDistMedium[oldID]
        for pipe in pipes:
            pipe.HeatDistMedium = newID
            logTrack("Project (substituteFluidID): table qdistributionhc - FluidID %s substituted by %s in ID %s" % \
                     (oldID, newID, pipe.QDistributionHC_ID))
        
        processes = Status.DB.qprocessdata.Questionnaire_id[PId].ProcMedDBFluid_id[oldID]
        for process in processes:
            process.ProcMedDBFluid_id = newID
            logTrack("Project (substituteFluidID): table qprocessdata - FluidID %s substituted by %s in ID %s for process medium" % \
                     (oldID, newID, process.QProcessData_ID))
        
        processes = Status.DB.qprocessdata.Questionnaire_id[PId].ProcMedOut[oldID]
        for process in processes:
            process.ProcMedOut = newID
            logTrack("Project (substituteFluidID): table qprocessdata - FluidID %s substituted by %s in ID %s for ProcMedOut" % \
                     (oldID, newID, process.QProcessData_ID))
        
        processes = Status.DB.qprocessdata.Questionnaire_id[PId].SupplyMedDBFluid_id[oldID]
        for process in processes:
            process.SupplyMedDBFluid_id = newID
            logTrack("Project (substituteFluidID): table qprocessdata - FluidID %s substituted by %s in ID %s for supply medium" % \
                     (oldID, newID, process.QProcessData_ID))
        
        hxes = Status.DB.qheatexchanger.ProjectID[PId].FluidIDSource[oldID]
        for hx in hxes:
            hx.FluidIDSource = newID
            logTrack("Project (substituteFluidID): table qheatexchanger - FluidID %s substituted by %s in ID %s for source medium" % \
                     (oldID, newID, hx.FluidIDSource))
        
        hxes = Status.DB.qheatexchanger.ProjectID[PId].FluidIDSink[oldID]
        for hx in hxes:
            hx.FluidIDSink = newID
            logTrack("Project (substituteFluidID): table qheatexchanger - FluidID %s substituted by %s in ID %s for sink medium" % \
                     (oldID, newID, hx.FluidIDSink))
        
        whees = Status.DB.qwasteheatelequip.ProjectID[PId].WHEEMedium[oldID]
        for whee in whees:
            whees.WHEEMedium = newID
            logTrack("Project (substituteFluidID): table qwasteheatelequip - FluidID %s substituted by %s in ID %s" % \
                     (oldID, newID, whee.QWasteHeatElEquip_ID))
        
        Status.SQL.commit()

#------------------------------------------------------------------------------
    def substituteFuelID(self, PId, oldID, newID):
#------------------------------------------------------------------------------
#   substitutes the links to fluids in import of project tables
#------------------------------------------------------------------------------

        fuels = Status.DB.qfuel.Questionnaire_id[PId].DBFuel_id[oldID]
        for fuel in fuels:
            fuel.DBFuel_id = newID
            logTrack("Project (substituteFuelID): table qfuel - FuelID %s substituted by %s in ID %s" % \
                     (oldID, newID, fuel.QFuel_ID))
        
        eqs = Status.DB.qgenerationhc.Questionnaire_id[PId].DBFuel_id[oldID]
        for eq in eqs:
            logTrack("Project (substituteFuelID): table qgenerationhc - FuelID %s substituted by %s in ID %s" % \
                     (oldID, newID, eq.QGenerationHC_ID))
            eq.DBFuel_id = newID

        Status.SQL.commit()
        
#------------------------------------------------------------------------------
    def substituteAuditorID(self, PId, oldID, newID):
#------------------------------------------------------------------------------
#   substitutes the links to fluids in import of project tables
#------------------------------------------------------------------------------

        sprojects = Status.DB.sproject.ProjectID[PId].Auditor_ID[oldID]
        for sproject in sprojects:
            sproject.Auditor_ID = newID
            logTrack("Project (substituteAuditorID): table sproject - AuditorID %s substituted by %s in SProject_ID %s" % \
                     (oldID, newID, sproject.SProject_ID))
                              
        Status.SQL.commit()
        
    def substituteStreamID(self, PId, oldID, newID, connectionTable, columnName):
        """
        Substitute the old stream ID in connectionTable with the new one during
        an import.
        
        :param PId: id of the project the connections belong to
        :param oldID: the old id of the stream
        :param newID: the new id of the stream
        :param connectionTable: the table holding the stale connection data
        :param columnName: a String containg the name of the colum holding the
        stale stream ID
        
        """
        connection = connectionTable.ProjectID[PId][columnName][oldID]
        connection[0][columnName] = newID
    
    def substituteProcessID(self, PId, oldID, newID):
        """
        Substitute the old processdata ID in the process_stream_in/out tables
        during an import.
        
        :param PId: id of the project the connections belong to
        :param oldID: the old id of the processdata
        :param newID: the old id of the processdata
        
        """
        DB = Status.DB
        for table in (DB.process_streams_in, DB.process_streams_out):
            connections = table.ProjectID[PId].qprocessdata_QProcessData_Id[oldID]
            for connection in connections:
                connection.qprocessdata_QProcessData_Id = newID 
    
    def substitutePipeID(self, PId, pipeIDdict):
#------------------------------------------------------------------------------
#   substitutes the links to fluids in import of project tables
#------------------------------------------------------------------------------

        eqs = Status.DB.qgenerationhc.Questionnaire_id[PId]
        equipeIDdict = {}
        for eq in eqs:
            newID = eq.QGenerationHC_ID
            equipeIDdict.update({newID:newID})  #only value of pair is used in function "reconnect"
            
        self.reconnectEquipesToPipes(equipeIDdict, pipeIDdict)

    def substituteForeignKey(self, table, primaryKey, primaryKeySelection, foreignKey, foreignKeySubstitutions):
        rows = getattr(Status.DB, table).sql_select('%s IN (%s)' % (primaryKey, ','.join([str(id) for id in primaryKeySelection])))
        for row in rows:
            setattr(row, foreignKey, foreignKeySubstitutions[getattr(row, foreignKey)])
        
    def restoreLinks(self, PId, projectDict):
        """restores the links in an imported project"""
        if u'process_schedules' in projectDict.keys() and u'qprocessdata' in projectDict.keys():
            newProcessSchedulesIDList = [id[1] for id in projectDict[u'process_schedules']]
            self.substituteForeignKey('process_schedules', 'id', newProcessSchedulesIDList, 'qprocessdata_QProcessData_ID', dict(projectDict['qprocessdata']))
            
        if u'process_schedules_tolerance_offsets' in projectDict.keys() and u'qprocessdata' in projectDict.keys():
            newProcessSchedulesToleranceOffsetsIDList = [id[1] for id in projectDict[u'process_schedules_tolerance_offsets']]
            self.substituteForeignKey('process_schedules_tolerance_offsets', 'id', newProcessSchedulesToleranceOffsetsIDList, 'qprocessdata_QProcessData_ID', dict(projectDict['qprocessdata']))
            
        if u'process_periods'         in projectDict.keys() and \
           u'process_period_profiles' in projectDict.keys() and \
           u'periods'                 in projectDict.keys() and \
           u'profiles'                in projectDict.keys() and \
           u'profile_intervals'       in projectDict.keys() and \
           u'intervals'               in projectDict.keys() and \
           u'qprocessdata'            in projectDict.keys():
            qprocessdataSubstitutions   = dict(projectDict['qprocessdata'])
            periodsSubstitutions        = dict(projectDict['periods'])
            processPeriodsSubstitutions = dict(projectDict['process_periods'])
            profilesSubstitutions       = dict(projectDict['profiles'])
            intervalsSubstitutions      = dict(projectDict['intervals'])
            
            newProcessPeriodsIDList = [id[1] for id in projectDict[u'process_periods']]
            self.substituteForeignKey('process_periods', 'id', newProcessPeriodsIDList, 'periods_id', periodsSubstitutions)
            self.substituteForeignKey('process_periods', 'id', newProcessPeriodsIDList, 'qprocessdata_QProcessData_ID', qprocessdataSubstitutions)

            newProcessPeriodProfilesIDList = [id[1] for id in projectDict[u'process_period_profiles']]
            self.substituteForeignKey('process_period_profiles', 'id', newProcessPeriodProfilesIDList, 'process_periods_id', processPeriodsSubstitutions)
            self.substituteForeignKey('process_period_profiles', 'id', newProcessPeriodProfilesIDList, 'profiles_id', profilesSubstitutions)
            
            newProfileIntervalsIDList = [id[1] for id in projectDict[u'profile_intervals']]
            self.substituteForeignKey('profile_intervals', 'id', newProfileIntervalsIDList, 'profiles_id', profilesSubstitutions)
            self.substituteForeignKey('profile_intervals', 'id', newProfileIntervalsIDList, 'intervals_id', intervalsSubstitutions)

        if u'dbfluid' in projectDict.keys():
            fluidIDList = projectDict[u'dbfluid']
            for oldID, newID in fluidIDList:
                self.substituteFluidID(PId, oldID, newID)

        if u'dbfuel' in projectDict.keys():
            fuelIDList = projectDict[u'dbfuel']
            for oldID, newID in fuelIDList:
                self.substituteFuelID(PId, oldID, newID)

        if u'qdistributionhc' in projectDict.keys():
            pipeIDList = projectDict[u'qdistributionhc']
            pipeIDDict = {}
            for oldID, newID in pipeIDList:
                pipeIDDict.update({oldID:newID})
            self.substitutePipeID(PId, pipeIDDict)
            
        if u'auditor' in projectDict.keys():
            auditorIDList = projectDict[u'auditor']
            for oldID, newID in auditorIDList:
                self.substituteAuditorID(PId, oldID, newID)

        if u'streams_in' in projectDict.keys():
            streamsIDs = projectDict[u'streams_in']
            for oldID, newID in streamsIDs:
                self.substituteStreamID(PId, oldID, newID,
                                        Status.DB.process_streams_in,
                                        "streams_in_id")
            
        if u'streams_out' in projectDict.keys():
            streamsIDs = projectDict[u'streams_out']
            for oldID, newID in streamsIDs:
                self.substituteStreamID(PId, oldID, newID,
                                        Status.DB.process_streams_out,
                                        "streams_out_id")
        
        if u'qprocessdata' in projectDict.keys():
            processIDs = projectDict[u'qprocessdata']
            for oldID, newID in processIDs:
                self.substituteProcessID(PId, oldID, newID)
                
    def getAuditorID(self):
#------------------------------------------------------------------------------
#   returns the ID of the responsible auditor for the present project
#------------------------------------------------------------------------------

        projectTable = Status.DB.sproject.ProjectID[Status.PId]
        if len(projectTable) > 0:
            sproject = projectTable[0]
        else:
            logWarning(_("Project (getAuditorID): Corrupt entry for project no. %s: table sproject not found") % Status.PId)

        return sproject.Auditor_ID

#==============================================================================

