#!/usr/bin/env python
# -*- coding: utf_8 -*-

#==============================================================================
#
#   E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (www.iee-einstein.org)
#
#------------------------------------------------------------------------------
#
#   EINSTEIN Main
#
#------------------------------------------------------------------------------
#
#   GUI Main routines
#
#==============================================================================
#
#   EINSTEIN Version No.: 1.0
#   Created by: 	Hans Schweiger, Heiko Henning, Tom Sobota, Stoyan Danov
#                       01/02/2008 - 25/09/2008
#
#   Update No. 002
#
#   Since Version 1.0 revised by:
#               
#   01/04/2009  HS  MySQL encoding set fixed to utf-8 (avoids problems with
#                   erroneous configuration files)
#   21/07/2009  HS  Several minor changes since update 001: storage of language settings,
#                   clean-up, ...
#
#------------------------------------------------------------------------------
#   (C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008,2009
#   www.energyxperts.net / info@energyxperts.net
#
#   This program is free software: you can redistribute it or modify it under
#   the terms of the GNU general public license v3 as published by the Free
#   Software Foundation (www.gnu.org).
#
#==============================================================================

#-----  Imports

from einstein.modules.energystreams.CurveCalculation import CurveCalculation
from einstein.modules.energystreams.StreamGeneration import *
import sys

import os
import time
import gettext
import locale   #HS2008-10-09 added
import exceptions
import wx
import wx.grid
import pSQL, MySQLdb
#TS20080429 dynamical setting of pythonpath
# fix pythonpath for this run
# before loading Einstein modules
sys.path.append(os.path.abspath('../..'))
#TS20080505 install a default language, so the importing of 'constants'
#           will recognize the gettext alias _(...)
gettext.install("einstein", "locale", unicode=False)
language = gettext.translation("einstein", "locale", languages=['%s' % ('en',)], fallback=True)
language.install()

import HelperClass
from einstein.modules.interfaces import Interfaces
from einstein.modules.modules import Modules
from einstein.modules.constants import *

#--- popup frames
from einstein.modules.project import Project #functions for handling of PId/ANo

#--- popup frames
import DBEditFrame
from PreferencesFrame import *
from dialogPOManageDB import DialogPOManageDB

#--- Module Panels
from panelCC import *
from panelA import *
from panelPO import *
from panelHR import *
from panelHC import *
from panelST import *
from panelHP import *
from panelBB import *
from panelCHP import *
from panelEnergy import *
#TS20080406 the new panels Q*
from einstein.GUI.panelQ0 import PanelQ0
from einstein.GUI.panelQ1 import PanelQ1
from einstein.GUI.panelQ2 import PanelQ2
from einstein.GUI.panelQ3 import PanelQ3
from einstein.GUI.panelQ4 import PanelQ4
from einstein.GUI.panelQ5 import PanelQ5
from einstein.GUI.panelQ6 import PanelQ6
from einstein.GUI.panelQ7 import PanelQ7
from einstein.GUI.panelQ8 import PanelQ8
from einstein.GUI.panelQ9 import PanelQ9

#TS2008-03-23 panelEA1-EA6, EM1 added
from panelEA1 import *
from panelEA2 import *
from panelEA3 import *
from panelEA4a import *
from panelEA4b import *
from panelEA4c import *
from panelEA5 import *
from panelEM1 import *
from panelEM2 import *
#from panelEH1 import *
#from panelEH2 import *
from panelCS1 import *
from panelCS2 import *
from panelCS3 import *
from panelCS4 import *
from panelCS5 import *
from panelCS6 import *
from panelCS7 import *
from panelBM1 import *
from panelBM2 import *
from panelBM3 import *

from panelTCA import *
from panelTCAInvestment import *
from panelTCAEnergy import *
from panelTCACont import *
from panelTCANon import *

#TS2008-04-15 panelInfo added
from panelInfo import *

#TS2008-04-15 help frame added
from userHelp import *
#TS2008-04-22 language selection dialog added
from dialogLanguage import *
#TS2008-05-01 report generation
from panelReport import *
#TS2008-05-16 export data
from einstein.modules.xmlIO import *
#TS2008-06-18 fonts management
from fonts import FontProperties
#TS2008-06-30 database management
from dialogDatabase import DlgDatabase
from dialogImport import DialogImport

from einstein.GUI.status import Status #processing status of the tool

#from einstein.modules.energystreams.ProcessBatch import ProcessBatch
#from einstein.modules.energystreams.EquipmentStreamSet import *
from einstein.modules.energystreams.Stream import *
from einstein.modules.energystreams.HXCalculation import *
from einstein.modules.energystreams.HXProposal import *

def _U(text):
    try:
        return unicode(_(text),"utf-8")
    except:
        return _(text)
    
def U(text):
    try:
        return unicode((text),"utf-8")
    except:
        return (text)
    
#----- Constants
qPageSize = (800, 600)
KFramesize = (1024, 740)

        
#------------------------------------------------------------------------------
class EinsteinFrame(wx.Frame):
#------------------------------------------------------------------------------
#   Main frame structure:
#
#   EinsteinFrame -------- menubar
#                      |
#                      |-- panelinfo
#                      |
#                      |-- splitter --x-- treepanel ----- tree
#                      |              |
#                      |              |-- splitter2 --x-- leftpanel2
#                      |                              |
#                      |                              |
#                      |                              |-- message
#                      |
#                      |-- statusbar
#------------------------------------------------------------------------------
    def __init__(self, parent, id, title):
        #----- Initialise the Frame
        wx.Frame.__init__(self, parent, id, title, size=KFramesize, pos=(0,0))

        self.treePermissions = {}
        self.prnt = parent


    def connectToDB(self):
        ############################################
        #
        # Database connexion
        #
        ############################################

        self.DBHost = self.conf.get('DB', 'DBHost')
        self.DBUser = self.conf.get('DB', 'DBUser')
        self.DBPass = self.conf.get('DB', 'DBPass')
        self.DBName = self.conf.get('DB', 'DBName')
        #TS20080730 read character encoding
#        try:
#            self.MySQLEncoding = self.conf.get('DB', 'ENCODING')
#        except:
#            # default encoding for MySQL
#            self.MySQLEncoding = 'Latin1'
        self.MySQLEncoding = 'utf8'

        #----- Connect to the Database
        conn = MySQLdb.connect(host=self.DBHost, user=self.DBUser, passwd=self.DBPass, db=self.DBName)
        if conn:
            # set mysql encoding translation
            try:
                cursor = conn.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SET NAMES '%s'" % self.MySQLEncoding)
#                self.doLog.LogThis('EinsteinMain: Encoding %s' % self.MySQLEncoding)
            except MySQLdb.Error, e:
                self.doLog.LogThis('Could not set encoding %s: %s' % (self.MySQLEncoding,str(e)))

        return conn
                                   
    def setLanguage(self):
        #TS20080528 Took this out of createUI, so it can be called before creating the UI
        LANGUAGE = Status.DB.stool.STool_ID[1][0].LanguageTool
#        print "Main(setLanguage): language set to ",LANGUAGE

        if LANGUAGE not in LANGUAGES:
            LANGUAGE = self.conf.get('GUI', 'LANGUAGE')

        if LANGUAGE not in LANGUAGES:
            LANGUAGE = 'en' #default -> set to English

        Status.LanguageTool = LANGUAGE
        Status.DB.stool.STool_ID[1][0].LanguageTool = LANGUAGE
                    
#        self.doLog.LogThis('Reading config done')

        #----- I18N
        #TS20080120 Installed runtime text translation infrastructure
        #Read the LANGUAGE parameter from einstein.ini
        #TS20080120 added fallback to avoid errors on inexistent translations
        #
        gettext.install("einstein", "locale", unicode=False)

        if LANGUAGE == "cz":
            language = gettext.translation("einstein", "locale", languages=['cs_CZ'], fallback=True)
        else:
            language = gettext.translation("einstein", "locale", languages=['%s' % (LANGUAGE,)], fallback=True)
        language.install()

        Status.TRANS = updateConstants()

#HS2008-10-09 added (see http://wiki.wxpython.org/Internationalization#head-45277e6d8f10a94d0f9dadaa64a7e8527f59f948)
#        self.prnt.locale = wx.Locale(wx.wxLANGUAGE_ITALIAN)
#        locale.setlocale(locale.LC_ALL, 'IT')
        
    def createUI(self):
        self.activeQid = 0

        ############################################
        #
        # UI generation
        #
        ############################################

        #----- add statusbar
        self.CreateStatusBar()

        #----- create splitters
        self.splitter = wx.SplitterWindow(self,style=wx.CLIP_CHILDREN|wx.SP_LIVE_UPDATE|wx.SP_3D|wx.SP_3DSASH)

        self.splitter2 = wx.SplitterWindow(self.splitter,-1,
                                           style=wx.CLIP_CHILDREN|wx.SP_LIVE_UPDATE|wx.SP_3D|wx.SP_3DSASH)
        self.splitter2.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE))

        self.treepanel = wx.Panel(self.splitter, -1)

        ####---- Upper info panel
#HS2008-04-18: argument list shortened. new function update in infopanel directly linked to status
        self.panelinfo = PanelInfo(self,self)

        ####---- panel containing qPages
        self.leftpanel2 = wx.Panel(self.splitter2, -1, style=wx.WANTS_CHARS)

        #----- add menu
        self.CreateMenu()
        self.changeAssistantMainMenu(ASSISTANTLIST.index(Status.UserInteractionLevel))

        #----- create tree control and close branches that conditionally cannot be yet activated


#HS2008-05-29: CANCELLED OUT -> sobreescribe treePermissions que ya se han definido antes.
        #self.treePermissions = {}
        self.CreateTree()
        root = self.tree.GetRootItem()
        #self.getNodeNames(root)
        #TS20080515 implemented a simpler method for allowing/disallowing tree branches expansion
        #self.treePermissions is a dictionary that has:
        # 1. a key. It is the tree element label
        # 2. a value. It is a tuple containing 3 elements:
        #    a. allow. A boolean. When false, disallows branch expansion
        #    b. level. The level of this branch in the tree. Root=0, main branches=1, ...
        #    c. a message that is presented to the user when attempting to activate a disallowed branch
        #
        # The method self.treeChangeConditionalNode can be used to change the value of
        # a branch.

#HS2008-05-29: CANCELLED OUT -> sobreescribe treePermissions que ya se han definido antes.
#        for key in self.treePermissions.keys():
#            (allow,level,message) = self.treePermissions[key]
#            # only top level branches
#            if level == 1:
#                if key == _("Edit Industry Data"):
#                    self.treeChangeConditionalNode(key, True)
#                else:
#                    self.treeChangeConditionalNode(key, False)

        #----- error log window
        self.message = wx.ListCtrl(id=-1,
                   name='message',
                   parent=self.splitter2,
                   style= wx.RAISED_BORDER | wx.LC_REPORT | wx.LC_NO_HEADER)
        self.message.InsertColumn(0, _U("Message log"))
        self.message.SetBackgroundColour('white')
        # show/hide is a main menu action
        # ini. state is hidden
        self.message.Show()

        #----- configure sizers and splitters
        self.DoLayout ()

        #----- set binding events
        self.BindEvents()

        #----- create title page
        self.CreateTitlePage()

        #----- initial message
        self.logMessage(_U("einstein started"))
        #self.logWarning('an example of a warning')
        #self.logError('an example of an error')


    def changeUI(self):
        #----- add statusbar
#        self.CreateStatusBar()

        self.panelinfo.Destroy()
        self.panelinfo = PanelInfo(self,self)

        self.CreateMenu()
        self.changeAssistantMainMenu(ASSISTANTLIST.index(Status.UserInteractionLevel))

        self.tree.Destroy()
        self.CreateTree()
        root = self.tree.GetRootItem()

        self.DoLayout()

        #----- set binding events
        self.BindEvents()

#------------------------------------------------------------------------------
    def _log(self,fcolor,bcolor,text):
#        tl = time.localtime()
#        now = '%s-%s-%s %s:%s:%s  ' % (tl[0],tl[1],tl[2],tl[3],tl[4],tl[5])
        now = ""
        item = wx.ListItem()
        try:
            item.SetText(now + text.encode("latin-1","replace"))  
        except:
            try:
                item.SetText(now + unicode(text,"utf-8").encode("latin-1","replace"))
            except:
                item.SetText(now + "---")

        item.SetTextColour(fcolor)
        item.SetBackgroundColour(bcolor)
        item.SetColumn(0)
        f = item.GetFont()
        f.SetPointSize(8)
        item.SetFont(f)
        try:
            self.message.InsertItem(item)
        except:
            pass

    def logMessage(self,text):
        self._log('#00A000','#FFFFFF',text)
        self.doLog.LogThis('Message:'+text)

    def logWarning(self,text):
        self._log('#0000FF','#FFFF80',text)
        self.doLog.LogThis('Warning:'+text)

    def logError(self,text):
        self._log('#FFFFFF','#FF0000',text)
        self.doLog.LogThis('Error:'+text)

    def showError(self, text):
        self.logError(text)
        if Status.UserInteractionLevel <> "automatic":
            dlg = wx.MessageDialog(None, U(text), _U("Error"), wx.OK | wx.ICON_ERROR)
            ret = dlg.ShowModal()
            dlg.Destroy()
        self.doLog.LogThis('Error: '+ text)

    def showWarning(self, text):
        self.logWarning(text)

        if Status.UserInteractionLevel <> "automatic":
            dlg = wx.MessageDialog(None, U(text), _U("Warning"), wx.OK | wx.ICON_EXCLAMATION)
            ret = dlg.ShowModal()
        #dlg.Destroy()
        self.doLog.LogThis('Warning: '+text)

    def showInfo(self, text):
        self.logMessage(text)
        if Status.UserInteractionLevel <> "automatic":
            dlg = wx.MessageDialog(None, U(text), _U("Info"), wx.OK | wx.ICON_INFORMATION)
            ret = dlg.ShowModal()
            dlg.Destroy()
        self.doLog.LogThis('Info: '+text)

    def askConfirmation(self, text):
        self.logMessage(text)
        if Status.UserInteractionLevel <> "automatic":
            dlg = wx.MessageDialog(None, U(text), _U("Confirm"), wx.YES_NO | wx.ICON_QUESTION)
            ret = dlg.ShowModal()
            dlg.Destroy()
            self.doLog.LogThis('Confirm: '+text+'. Answer='+str(ret))
        else:
            ret = wx.ID_OK
        return ret

#------------------------------------------------------------------------------
    def DoLayout(self):
#------------------------------------------------------------------------------
#       Layout of main frame and panels
#------------------------------------------------------------------------------

        # set sizers

        # this sizer allows the horiz.expansion of the tree
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.tree, 1, wx.EXPAND)
        self.treepanel.SetSizer(sizer1)

        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(self.leftpanel2, 1, wx.EXPAND, 0)
        self.splitter2.SetSizer(sizer2)

        panelsizer = wx.BoxSizer(wx.VERTICAL)
        #panelsizer.Add(self.panelinfo, 0, wx.FIXED_MINSIZE, 0)
        panelsizer.Add(self.panelinfo, 0, wx.EXPAND)
        panelsizer.Add(self.splitter, 1, wx.EXPAND, 0)

        infobar = self.FindWindowByName("PanelInfo")
        infobar.SetMinSize((0,26))

        self.SetSizer(panelsizer)

        self.Layout()

        # set splitters
        self.splitter.SplitVertically(self.treepanel, self.splitter2, 200)
        self.splitter2.SplitHorizontally(self.leftpanel2, self.message, -50) # initially open
        self.splitter.SetSashPosition(222)

        # find the width of message panel
        w = self.splitter2.GetWindow1()
        (width,height) = w.GetClientSizeTuple()
        self.message.SetColumnWidth(0, width-10)

######################################################################################

    def CreateTitlePage(self):
        ####----PAGE Title
        self.pageTitle = wx.Panel(id=-1, name='pageTitle', parent=self.leftpanel2, pos=wx.Point(0, 0), size=wx.Size(800, 600), style=0)
        self.pageTitle.Show()
#..............................................................................
# grid for displaying alternatives

       # self.box1 = wx.StaticBox(self.pageTitle, -1, _("Welcome to the Magic World of ..."),
       # self.box1 = wx.StaticBox(self.pageTitle, -1, _("EINSTEIN - the tool that never fails ..."),
       # self.box1 = wx.StaticBox(self.pageTitle, -1, _("EINSTEIN - summer special edition ..."),
        self.box1 = wx.StaticBox(self.pageTitle, -1, _U("Welcome to ..."),
                                 pos = (10,10),size=(780,580))
        
#        self.box1.SetForegroundColour(wx.Colour(255, 128, 0))
        ORANGE = '#FF6000'
        self.box1.SetForegroundColour(ORANGE)
        self.box1.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.staticBitmap1 = wx.StaticBitmap(bitmap=wx.Bitmap(os.path.join(sys.path[0],'img','brochureTitlePage.jpg'),
                                             wx.BITMAP_TYPE_JPEG),
                                             id=-1,#TS 2008-3-26 changed from id=wxID_PANELCCPIC1,
                                             parent=self.pageTitle,
                                             pos=wx.Point(60, 100),
                                             size=wx.Size(700, 480),
                                             style=wx.SUNKEN_BORDER)
        self.staticBitmap2 = wx.StaticBitmap(bitmap=wx.Bitmap(os.path.join(sys.path[0], 'img','einstein_logo_small.jpg'),
                                             wx.BITMAP_TYPE_JPEG),
                                             id=-1,#TS 2008-3-26 changed from id=wxID_PANELCCPIC1,
                                             parent=self.pageTitle,
                                             pos=wx.Point(280, 0),
                                             size=wx.Size(478, 130),
                                             style=0)


#==============================================================================
#--- Eventhandlers Application
#==============================================================================

#------------------------------------------------------------------------------
#--- Eventhandlers Menu
#------------------------------------------------------------------------------

    def OnMenuNewProject(self,event):
        #TS20080421 Add project on main menu Opens panel Q1
        self.activeQid = 0
        self.hidePages()
        #TS20080428 Modified for loading on demand
        self.Page0 = PanelQ0(self.leftpanel2, self)
        self.Page0.fillPage()
        self.Page0.Show()
        self.Page0.NewProject()

    def OnMenuOpenProject(self, event):
        self.hidePages()
        #TS20080428 Modified for loading on demand
        self.Page0 = PanelQ0(self.leftpanel2, self)
        self.Page0.fillPage()
        self.Page0.Show()

    def OnMenuExit(self, event):
        #TS20080421 Ask before exiting
        if self.askConfirmation(_U("Do you really want to exit?")) == wx.ID_YES:
            wx.Exit()

    def OnMenuExportAll(self, event):
        ex = ExportDB("all")

    def OnMenuExportDBBenchmark(self, event):
        ex = ExportDB("dbbenchmark")
        
    def OnMenuExportDBNaceCode(self, event):
        ex = ExportDB("dbnacecode")
        
    def OnMenuExportDBUnitOperation(self, event):
        ex = ExportDB("dbunitoperation")
        
    def OnMenuExportAllEquipments(self, event):
        ex = ExportDB("all equipments")
        
    def OnMenuExportDBCHP(self, event):
        ex = ExportDB("dbchp")
        
    def OnMenuExportDBHeatPump(self, event):
        ex = ExportDB("dbheatpump")
        
    def OnMenuExportDBFluid(self, event):
        ex = ExportDB("dbfluid")
        
    def OnMenuExportDBFuel(self, event):
        ex = ExportDB("dbfuel")
        
    def OnMenuExportDBElectricityMix(self, event):
        ex = ExportDB("dbelectricitymix")
        
    def OnMenuExportDBBoiler(self, event):
        ex = ExportDB("dbboiler")
        
    def OnMenuExportDBSolarThermal(self, event):
        ex = ExportDB("dbsolarthermal")
        
    def OnMenuExportDBChiller(self, event):
        ex = ExportDB("dbchiller")
        

    def OnMenuImportData(self, event):
        im = ImportDB()

    def OnMenuExportProject(self, event):
#        print 'PId='+repr(Status.PId)
#        ex = ExportProject(pid=Status.PId)

# DO CURVE CALCULATION
        if Status.processData.outOfDate == True:
            Status.processData.createAggregateDemand()
        Status.int.StreamGen.calcStreams()
#        curvecalc = CurveCalculation()
#        curvecalc.calculate()
#        curvecalc.printResults()
#        Status.mod.moduleHR.doHXPostProcessing()
        hxp = HXProposal(20, False, 5)
        hxp.start()
        hxp.printSplittedStreams()
        


    def OnMenuImportProject(self, event):
        ex = ImportProject()
        pids = ex.getPid()
        oldPId,newPId = pids
        self.showInfo('Project with pid=%s has been imported. New pid set to %s' % pids)
		
    def calcStream(self, stream):
        initStream(stream)
        if stream.Source == STREAMSOURCE[0]:
            calcProcessStream(stream)
        elif stream.Source == STREAMSOURCE[1]:
            calcProcessStream(stream)
        elif stream.Source == STREAMSOURCE[2]:
            calcEquipmentStream(stream)
        elif stream.Source == STREAMSOURCE[3]:
            calcWHEEStream(stream)
        elif stream.Source == STREAMSOURCE[4]:
            calcDistLineStream(stream)


    def OnMenuImportQ(self, event):

#        for elem in Status.int.HXPinchConnection:
#            for el in elem.sinkstreams:
#                initStream(el.stream)

        if Status.processData.outOfDate == True:
            Status.processData.createAggregateDemand()
        print "-------------------CALCULATE STREAMS--------------------"
#        Status.int.StreamGen.initStreams()
        for i in xrange(len(Status.int.HXPinchConnection)):
            for j in xrange(len(Status.int.HXPinchConnection[i].sinkstreams)):
                stream = Status.int.HXPinchConnection[i].sinkstreams[j].stream
                self.calcStream(stream)
                stream.printStream()

            for j in xrange(len(Status.int.HXPinchConnection[i].sourcestreams)):
                stream = Status.int.HXPinchConnection[i].sourcestreams[j].stream
                self.calcStream(stream)
                stream.printStream()


        Status.int.StreamGen.calcStreams()

        print "--------STREAM CURVE CALCULATION--------"

        curvecalc = CurveCalculation()
        curvecalc.calculate()
        curvecalc.printResults()
        print "---------------------PRINT STREAMS----------------------"
#        Status.int.StreamGen.printStreams()

        hxcomb = HXCombination()
        hxcomb.combineAllStreams()
        print "--------------------COMBINED STREAMS--------------------"
#        for elem in Status.int.HXPinchConnection:
#            elem.combinedSink.stream.printStream()
#            elem.combinedSource.stream.printStream()
        print "--------------------SIMULATION--------------------------"

        #hxlist =  createHXList()
        for hx in Status.int.HXPinchConnection:
            hxes = Status.DB.qheatexchanger.\
               QHeatExchanger_ID[hx.HXID]
            hxsim = HXSimulation(hx.combinedSource.inletTemp,\
                                    hx.combinedSink.inletTemp,\
                                    hxes[0].QdotHX,\
                                    hxes[0].QHX,\
                                    hx.combinedSource.outletTemp,\
                                    hx.combinedSink.outletTemp,\
                                    hxes[0].UA,\
                                    hx
                                    )
            hxsim.startSimulation()
            


    def printMatrix(self, matrix):
        for elem in matrix:
            print elem[0:100]

#..............................................................................
# Scroll-up menu "VIEW"

#TS20080421 Dynamic alternatives menu
    def OnMenuPresentState(self, event):
        i = event.GetId()- self.rangeId[0]
        al = Status.prj.getAlternativeList()
        apNo = al[i][0]
        #print 'OnMenuPresentState',i,apNo
        Status.prj.setActiveAlternative(apNo)
        self.panelinfo.update()

#..............................................................................
    def OnMenuEditDBAdmin(self, event):
        dlgdb = DlgDatabase(parent=None,id=-1)
        rsp = dlgdb.ShowModal()
        if dlgdb.getChanges():
            self.showWarning(_U('Any changes will be in effect next time you restart Einstein'))
            
    def OnMenuEditDBBenchmark(self, event):
        frameEditDBBenchmark = DBEditFrame(self, "Edit DBBenchmark", 'dbbenchmark', 0, True)
        frameEditDBBenchmark.ShowModal()

    def OnMenuEditDBBAT(self, event):
        dlg = DialogPOManageDB(self)
        dlg.ShowModal()
        event.Skip()

    def OnMenuEditDBNaceCode(self, event):
        frameEditDBNaceCode = DBEditFrame(None, "Edit DBNaceCode", 'dbnacecode', 0, True)
        frameEditDBNaceCode.ShowModal()
    def OnMenuEditDBUnitOperation(self, event):
        frameEditDBUnitOperation = DBEditFrame(None, "Edit DBUnitOperation", 'dbunitoperation', 0, True)
        frameEditDBUnitOperation.ShowModal()
    def OnMenuEditDBCHP(self, event):
        frameEditDBCHP = DBEditFrame(None, "Edit DBCHP", 'dbchp', 0, True)
        frameEditDBCHP.ShowModal()
    def OnMenuEditDBHeatPump(self, event):
        frameEditDBHeatPump = DBEditFrame(self, "Edit DBHeatPump", 'dbheatpump', 0, True)
        frameEditDBHeatPump.ShowModal()
    def OnMenuEditDBFluid(self, event):
        frameEditDBFluid = DBEditFrame(None, "Edit DBFluid", 'dbfluid', 0, True)
        frameEditDBFluid.ShowModal()
    def OnMenuEditDBFuel(self, event):
        frameEditDBFuel = DBEditFrame(None, "Edit DBFuel", 'dbfuel', 0, True)
        frameEditDBFuel.ShowModal()
    def OnMenuEditDBBoiler(self, event):
        frameEditDBBoiler = DBEditFrame(None, "Edit DBBoiler", 'dbboiler', 0, True)
        frameEditDBBoiler.ShowModal()
    def OnMenuEditDBSolarThermal(self, event):
        frameEditDBSolarThermal = DBEditFrame(None, "Edit DBSolarThermal", 'dbsolarthermal', 0, True)
        frameEditDBSolarThermal.ShowModal()
    def OnMenuEditDBChiller(self, event):
        frameEditDBChiller = DBEditFrame(None, "Edit DBChiller", 'dbchiller', 0, True)
        frameEditDBChiller.ShowModal()
    def OnMenuEditDBElectricityMix(self, event):
        frameEditDBElectricityMix = DBEditFrame(None, "Edit DBElectricityMix", 'dbelectricitymix', 0, True)
        frameEditDBElectricityMix.ShowModal()

#..............................................................................
# Scroll-up menu "USER SELECT LEVEL 1 - 3"

    def OnMenuUserSelectLevel1(self, event):
        self.panelinfo.changeAssistant(0)
        Status.prj.setUserInteractionLevel(1)
    def OnMenuUserSelectLevel2(self, event):
        self.panelinfo.changeAssistant(1)
        Status.prj.setUserInteractionLevel(2)
    def OnMenuUserSelectLevel3(self, event):
        self.panelinfo.changeAssistant(2)
        Status.prj.setUserInteractionLevel(3)

#..............................................................................



    def OnMenuSettingsPreferences(self, event):
#        print "EinsteinMain (OnMenuSettingsPreferences): HRTool received as ",Status.HRTool
        framePreferences = PreferencesFrame(self)
        x = framePreferences.ShowModal()
#        print "EinsteinMain (OnMenuSettingsPreferences): HRTool set to ",Status.HRTool

    def OnMenuSettingsLanguage(self,event):
        dialogLang = DialogLanguage(self)
        if dialogLang.ShowModal() == wx.ID_OK:
            newlang = dialogLang.GetLanguage()
            language = gettext.translation("einstein", "locale",
                                           languages=['%s' % (newlang,)], fallback=True)
            language.install()

        dialogLang.Destroy()
        Status.TRANS = updateConstants()
        self.changeUI()

    def OnMenuSettingsViewMessages(self,event):
        if self.menuBar.IsChecked(event.GetId()):
            self.splitter2.SetSashPosition(-50)
            self.message.Show()
        else:
            self.splitter2.SetSashPosition(-1)
            self.message.Hide()

    def OnMenuSettingsManageFonts(self,event):
        fp = FontProperties()
        fp.chooseFont()
        
#..............................................................................
# Scroll-up menu "HELP" and "About ..."
    def OnMenuHelpUserManual(self, event):
        frameUserManual = FrameHelpUserManual(self, '../docs/sphinx/_build/html/users/guide.html')
        frameUserManual.Show()

    def OnMenuHelpSupport(self, event):
        frameSupport = FrameHelpSupport(self)
        frameSupport.Show()

    def OnMenuHelpAbout(self, event):
        frameAbout = FrameHelpAbout(self)
        frameAbout.Show()

#------------------------------------------------------------------------------
#--- Eventhandlers Tree
#------------------------------------------------------------------------------

    def _interceptActivation(self, event):
        item = event.GetItem()
        label = self.tree.GetItemText(item)
        if self.treePermissions.has_key(label):
            (allow,level,message) = self.treePermissions[label]
            if not allow:
                event.Veto()
                if not message:
                    message = _U('Cannot open this action')
                self.showWarning(message)
                
    def OnTreeItemExpanding(self, event):
        self._interceptActivation(event)

    def OnTreeSelChanging(self, event):
        self._interceptActivation(event)

    def OnTreeSelChanged(self, event):
        #
        #TS20080428 Most items below were modified for loading on demand
        #
        self.item = event.GetItem()
        select = self.tree.GetItemText(self.item)

        #PageTitle
        if select == _U("Einstein"):
            self.hidePages()
            self.activePanel = "MAIN" ####HS 20090613 - was an attempt. uncompleted !!!
                                        #function required that associates translated text with code or english text
            self.pageTitle.Show()
        #Page0
        elif select == _U('Edit Industry Data'): #Edit Industry Data
            self.hidePages()
            self.activePanel = "Q0"
            self.Page0 = PanelQ0(self.leftpanel2, self)
            self.Page0.fillPage()
            self.Page0.Show()
        #Page1
        elif select == _U('General data'): #General data
            self.hidePages()
            self.activePanel = "Q1"
            self.Page1 = PanelQ1(self.leftpanel2, self)
            self.Page1.display()
##            self.Page1.clear()
##            self.Page1.fillChoiceOfNaceCode()
##            self.Page1.fillPage()
##            self.Page1.Show()
            
        #Page2
        elif select == _U("Energy consumption"): #Energy consumption
            self.hidePages()
            self.activePanel = "Q2"
            self.Page2 = PanelQ2(self.leftpanel2, self)
            self.Page2.display()
##            self.Page2.clear()
##            self.Page2.fillChoiceOfDBFuelType()
##            self.Page2.fillPage()
##            self.Page2.Show()
            
        #Page3
        elif select == _U("Processes data"): #Processes data
            self.hidePages()
            self.activePanel = "Q3"
            self.Page3 = PanelQ3(self.leftpanel2, self)
            self.Page3.display()

        #Page4
        elif select == _U("Generation of heat and cold"): #Generation of heat and cold
            self.hidePages()
            self.activePanel = "Q4"
            #HS2008-04-13 None as argument added.
            self.Page4 = PanelQ4(self.leftpanel2, self, None)
            self.Page4.display()
        #Page5
        elif select == _U("Distribution of heat and cold"): #Distribution of heat and cold
            self.hidePages()
            self.activePanel = "Q5"
            self.Page5 = PanelQ5(self.leftpanel2, self)
            self.Page5.display()

        #Page6 (Heat Recovery Missing)
        elif select == _U("Heat recovery"): #Heat recovery
            self.hidePages()
            self.activePanel = "Q6"
            self.Page6 = PanelQ6(self.leftpanel2, self)
            self.Page6.display()
##            self.Page6.clear()
##            self.Page6.fillPage()
##            self.Page6.Show()

        #Page7
        elif select == _U("Renewable energies"): # Renewable energies
            self.hidePages()
            self.activePanel = "Q7"
            self.Page7 = PanelQ7(self.leftpanel2, self)
            self.logMessage(_U("city / country"))
            self.Page7.display()
##            self.Page7.clear()
##            self.Page7.fillPage()
##            self.Page7.Show()
            
        #Page8
        elif select == _U("Buildings"): #Buildings
            self.hidePages()
            self.activePanel = "Q8"
            self.Page8 = PanelQ8(self.leftpanel2, self)
            self.Page8.display()
##            self.Page8.clear()
##            self.Page8.fillPage()
##            self.Page8.Show()
            
        #Page9
        elif select == _U("Economic parameters"): #Economic parameters
            self.hidePages()
            self.activePanel = "Q9"
            self.Page9 = PanelQ9(self.leftpanel2, self)
            self.Page9.display()
##            self.Page9.clear()
##            self.Page9.fillPage()
##            self.Page9.Show()
            
        #qDataCheck
        elif select == _U("Consistency Check"):
            self.hidePages()
            self.activePanel = "CC"
            self.panelCC = PanelCC(id=-1, name='panelCC',
                                   parent=self.leftpanel2, main=self,
                                   pos=wx.Point(0, 0), size=wx.Size(800, 600))
            self.panelCC.display()
        #qStatistics
        elif select == _U("Energy statistics"):
            #TS 2008-3-26 No action here
            #self.hidePages()
            #self.pageStatistics.Show()
            self.activePanel = "EA"
            pass
        #qEA1 'Primary energy - Yearly'
        elif select == _U("Primary energy"):
            self.hidePages()
            self.panelEA1 = PanelEA1(parent=self.leftpanel2)
            self.panelEA1.display()

        #qEA2 'Final energy by fuels - Yearly'
        elif select == _U("Final energy by fuels"):
            self.hidePages()
            self.panelEA2 = PanelEA2(parent=self.leftpanel2)
            self.panelEA2.display()
        #qEA3 'Final energy by equipment - Yearly'
        elif select == _U("Final energy by equipment"):
            self.hidePages()
            self.panelEA3 = PanelEA3(parent=self.leftpanel2)
            self.panelEA3.display()
        #qEA4a 'Process heat 1 - Yearly'   #SD2008-07-01
        elif select == _U("Heat demand (proc.)"):
            self.hidePages()
            self.panelEA4a = PanelEA4a(parent=self.leftpanel2)
            self.panelEA4a.display()
        #qEA4b 'Process heat 2 - Yearly'   #SD2008-07-01
        elif select == _U("Heat demand (temp.)"):
            self.hidePages()
            self.panelEA4b = PanelEA4b(parent=self.leftpanel2)
            self.panelEA4b.display()
        #qEA4c 'Process heat 3 - Yearly'   #SD2008-07-01
        elif select == _U("Heat demand (time)"):
            self.hidePages()
            self.panelEA4c = PanelEA4c(parent=self.leftpanel2)
            self.panelEA4c.display()
        #qEA5 'Energy intensity - Yearly'
        elif select == _U("Energy intensity"):
            self.hidePages()
            self.panelEA5 = PanelEA5(parent=self.leftpanel2)
            self.panelEA5.display()
        #qEM1 'Energy performance - Monthly'
        elif select == _U('Monthly demand'):
            self.hidePages()
            self.panelEM1 = PanelEM1(parent=self.leftpanel2)
            self.panelEM1.display()
        #qEM2 'Heat supply - Monthly'
        elif select == _U('Monthly supply'):
            if Status.ANo <= 0:
                self.showWarning(_("Sorry. This function is not available for the present state."))
                return
            self.hidePages()
            self.panelEM2 = PanelEM2(parent=self.leftpanel2)
            self.panelEM2.display()
        #qEH1 'Energy performance - Hourly'
        elif select == _U('Hourly demand'):
            self.logWarning(_("Sorry. This function is not yet available. Coming soon !"))
            return
            self.hidePages()
            #self.panelEH1 = PanelEH1(parent=self.leftpanel2)
            #self.panelEH1.Show()
        #qEH2 'Heat supply - Hourly'
        elif select == _U('Hourly supply'):
            self.logWarning(_("Sorry. This function is not yet available. Coming soon !"))
            return
            self.hidePages()
            #self.panelEH2 = PanelEH2(parent=self.leftpanel2)
            #self.panelEH2.Show()
        #
        #
        #qBenchmarkCheck
        elif select == _U("Benchmark check"):
            #TS 2008-3-26 No action here
            #self.hidePages()
            #self.pageBenchmarkCheck = wx.Panel(id=-1, name='pageBenchmarkCheck',
            #                                   parent=self.leftpanel2, pos=wx.Point(0, 0),
            #                                   size=wx.Size(800, 600), style=0)
            #self.pageBenchmarkCheck.Show()
            pass

#XXXHS2008-04-08
        elif select == _U("Global energy intensity"):
            self.hidePages()
            self.panelBM1 = PanelBM1(parent=self.leftpanel2)
            self.panelBM1.display()

        elif select == _U("SEC by product"):
            self.hidePages()
            self.panelBM2 = PanelBM2(parent=self.leftpanel2)
            self.panelBM2.display()

        elif select == _U("SEC by process"):
            self.hidePages()
            self.panelBM3 = PanelBM3(parent=self.leftpanel2)
            self.panelBM3.display()

        #qA
        elif select == _U("Alternative proposals"):        #generation of alternatives
            self.hidePages()
            self.panelA = PanelA(parent=self.leftpanel2,main=self)
            self.panelA.display()

        #panelPO
        elif select == _U("Process optimisation"):
            self.hidePages()
            self.panelPO = PanelPO(id=-1, name='panelPO', parent=self.leftpanel2, main = self,
                                   pos=wx.Point(0, 0), size=wx.Size(800, 600), style=wx.TAB_TRAVERSAL)
            self.panelPO.display()

        #panelCHP
        elif select == _U("CHP"):
#            self.logWarning(_("Sorry. This function is not yet available. Coming soon !"))
#            return
            self.hidePages()
            self.panelCHP = PanelCHP(id=-1, name='panelCHP', parent=self.leftpanel2,
                                   main=self,pos=wx.Point(0, 0), size=wx.Size(800, 600),
                                   style=wx.TAB_TRAVERSAL)
            self.panelCHP.display()
        #panelST
        elif select == _U("Solar Thermal"):
            self.hidePages()
            self.panelST = PanelST(id=-1, name='panelST', parent=self.leftpanel2,main=self)
            self.panelST.display()
            
        #panelHP
        elif select == _U("Heat Pumps"):
            self.hidePages()
            self.panelHP = PanelHP(id=-1, name='panelHP', parent=self.leftpanel2,
                                   main=self, pos=wx.Point(0, 0), size=wx.Size(800, 600),
                                   style=wx.TAB_TRAVERSAL)
            self.panelHP.display()

        #pageBoilers
        elif select == _U("Boilers & burners"):
            self.hidePages()
            self.panelBB = PanelBB(id=-1, name='panelBB', parent=self.leftpanel2,
                                   main=self,pos=wx.Point(0, 0), size=wx.Size(800, 600),
                                   style=wx.TAB_TRAVERSAL)
            self.panelBB.display()
        #panelEnergy
        elif select == _U("Energy performance"):
            ###TS2008-03-11 Boiler Page activated
            self.hidePages()
            self.panelEnergy = PanelEnergy(id=-1, name='panelEnergy',
                                           parent=self.leftpanel2, main=self,
                                           pos=wx.Point(0, 0), size=wx.Size(800, 600),
                                           style=wx.TAB_TRAVERSAL)
            self.panelEnergy.display()

        #panelHR
        elif select == _U("HX network"):
            self.hidePages()
            self.panelHR = PanelHR(id=-1, name='panelHR', parent=self.leftpanel2, main = self,
                                   pos=wx.Point(0, 0), size=wx.Size(800, 600), style=wx.TAB_TRAVERSAL)
            self.panelHR.display()

        #panelHC
        elif select == _U("H&C Supply"):
            self.hidePages()
            self.panelHC = PanelHC(id=-1, name='panelHC', parent=self.leftpanel2, main = self,
                                   pos=wx.Point(0, 0), size=wx.Size(800, 600), style=wx.TAB_TRAVERSAL)
            self.panelHC.display()


  	elif select ==  _U("Total Cost Assessment"):
            self.hidePages()
            self.panelTCA = PanelTCA(id=-1, name='panelTCA', parent=self.leftpanel2, main = self,
                                   pos=wx.Point(0, 0), size=wx.Size(800, 600), style=wx.TAB_TRAVERSAL)
            self.panelTCA.display()
        
        elif select ==  _U("Investment"):
            self.hidePages()
            self.panelTCAInvestment = PanelTCAInvestment(id=-1, name='panelTCAInvestment', parent=self.leftpanel2, main = self,
                                   pos=wx.Point(0, 0), size=wx.Size(800, 600), style=wx.TAB_TRAVERSAL)
            self.panelTCAInvestment.display()
            
        elif select ==  _U("Energy and operating costs"):
            self.hidePages()
            self.panelTCAEnergy = PanelTCAEnergy(id=-1, name='panelTCAEnergy', parent=self.leftpanel2, main = self,
                                   pos=wx.Point(0, 0), size=wx.Size(800, 600), style=wx.TAB_TRAVERSAL)
            self.panelTCAEnergy.display()
        
        elif select ==  _U("Contingencies"):
            self.hidePages()
            self.panelTCACont = PanelTCAContingencies(id=-1, name='panelTCAEnergy', parent=self.leftpanel2, main = self,
                                   pos=wx.Point(0, 0), size=wx.Size(800, 600), style=wx.TAB_TRAVERSAL)
            self.panelTCACont.display()
        
        elif select ==  _U("Non reocurring costs"):
            self.hidePages()
            self.panelTCANon = PanelTCANon(id=-1, name='panelTCAEnergy', parent=self.leftpanel2, main = self,
                                   pos=wx.Point(0, 0), size=wx.Size(800, 600), style=wx.TAB_TRAVERSAL)
            self.panelTCANon.display()
        #qCS1 'Primary energy - Yearly'   #SD2008-07-01
        elif select == _U("Comp.study: Primary energy"):
            self.hidePages()
            self.panelCS1 = PanelCS1(parent=self.leftpanel2)
            self.panelCS1.display()
        #qCS2 'Process & supply heat - Yearly'   #SD2008-07-01
        elif select == _U("Comp.study: Process & supply heat"):
            self.hidePages()
            self.panelCS2 = PanelCS2(parent=self.leftpanel2)
            self.panelCS2.display()
        #qCS3 'Environmental  impact - Yearly'   #SD2008-07-01
        elif select == _U("Comp.study: Environmental  impact"):
            self.hidePages()
            self.panelCS3 = PanelCS3(parent=self.leftpanel2)
            self.panelCS3.display()
        #qCS4 'Investment cost - Yearly'   #SD2008-07-10
        elif select == _U("Comp.study: Investment cost"):
            self.hidePages()
            self.panelCS4 = PanelCS4(parent=self.leftpanel2)
            self.panelCS4.display()
        #qCS5 'Annual cost - Yearly'   #SD2008-07-10
        elif select == _U("Comp.study: Annual cost"):
            self.hidePages()
            self.panelCS5 = PanelCS5(parent=self.leftpanel2)
            self.panelCS5.display()
        #qCS6 'Additional cost per saved energy - Yearly'   #SD2008-07-10
        elif select == _U("Comp.study: Additional cost per saved energy"):
            self.hidePages()
            self.panelCS6 = PanelCS6(parent=self.leftpanel2)
            self.panelCS6.display()
        #qCS7 'Internal rate of return - Yearly'   #SD2008-07-10
        elif select == _U("Comp.study: Internal rate of return"):
            self.hidePages()
            self.panelCS7 = PanelCS7(parent=self.leftpanel2)
            self.panelCS7.display()
        elif select == _U("Report"):
            self.hidePages()
            self.panelReport = PanelReport(parent=self.leftpanel2, main=self)
            self.panelReport.Show()


#------------------------------------------------------------------------------
#--- Eventhandlers DataCheck
#------------------------------------------------------------------------------
    def OnButtonDataCheck(self, event):
        if self.activeQid <> 0:
            #ret = self.ModBridge.FunctionOneDataCheck(Status.SQL, DB, self.activeQid)
            #self.showInfo("Return of FunctionOneDataCheck %s" %(ret))
            pass
        else:
            self.showError("Select Questionnaire first!")

#------------------------------------------------------------------------------
# Auxiliary Functions
#------------------------------------------------------------------------------

    def getNodeNames(self, root, level=0,cookie=0):
        label = self.tree.GetItemText(root)
        if self.treePermissions.has_key(label):
#            print 'Duplicate label in tree:%s. Please change' % (label,)
            sys.exit(1)
        else:
            # initially an empty message
            self.treePermissions[label] = (True,level,"")
        # step in subtree if there are items
        if self.tree.ItemHasChildren(root):
            # process first child
            firstchild, cookie = self.tree.GetFirstChild(root)
            self.getNodeNames(firstchild,level+1,cookie)
            # process rest of children
            child,cookie = self.tree.GetNextChild(root,cookie)
            while child:
                self.getNodeNames(child, level+1,cookie)
                child,cookie = self.tree.GetNextChild(root,cookie)



    def _traverse(self, root, nodename, change, cookie):
        # traverse the tree, opening or closing branches
        label = self.tree.GetItemText(root)
        if label == nodename:
            if change:
                # open this branch and sub-branches
                self.tree.ExpandAllChildren(root)

            else:
                # close this branch and sub-branches
                self.tree.CollapseAllChildren(root)

            if self.treePermissions.has_key(label):
                (allow,level,message) = self.treePermissions[label]
                self.treePermissions[label] = (change,level,message)
            return
        
        # step in subtree if there are items
        if self.tree.ItemHasChildren(root):
            # process first child
            firstchild, cookie = self.tree.GetFirstChild(root)
            self._traverse(firstchild,nodename,change,cookie)
            # process rest of children
            child,cookie = self.tree.GetNextChild(root,cookie)
            while child:
                self._traverse(child, nodename,change,cookie)
                child,cookie = self.tree.GetNextChild(root,cookie)


    def treeChangeConditionalNode(self, nodename, change):
        root = self.tree.GetRootItem()
        self._traverse(root,nodename,change,0)


    def hidePages(self):
        #TS20080428 Modified for loading on demand
        # but pageTitle is not destroyed, just hidden
        self.pageTitle.Hide()

        try:self.Page0.Destroy()
        except:pass
        try:self.Page1.Destroy()
        except:pass
        try:self.Page2.Destroy()
        except:pass
        try:self.Page3.Destroy()
        except:pass
        try:self.Page4.Destroy()
        except:pass
        try:self.Page5.Destroy()
        except:pass
        try:self.Page6.Destroy()
        except:pass
        try:self.Page7.Destroy()
        except:pass
        try:self.Page8.Destroy()
        except:pass
        try:self.Page9.Destroy()
        except:pass

        try:self.panelCC.Destroy()
        except:pass
        
        try:self.panelEA1.Destroy()
        except:pass
        try:self.panelEA2.Destroy()
        except:pass
        try:self.panelEA3.Destroy()
        except:pass
        try:self.panelEA4a.Destroy()
        except:pass
        try:self.panelEA4b.Destroy()
        except:pass
        try:self.panelEA4c.Destroy()
        except:pass
        try:self.panelEA5.Destroy()
        except:pass
        try:self.panelEM1.Destroy()
        except:pass
        try:self.panelEM2.Destroy()
        except:pass

        try:self.panelBM1.Destroy()
        except:pass
        try:self.panelBM2.Destroy()
        except:pass
        try:self.panelBM3.Destroy()
        except:pass

        try:self.panelA.Destroy()
        except:pass
        try:self.panelPO.Destroy()
        except:pass
        try:self.panelHR.Destroy()
        except:pass
        try:self.panelHC.Destroy()
        except:pass
        try:self.panelCHP.Destroy()
        except:pass
        try:self.panelST.Destroy()
        except:pass
        try:self.panelHP.Destroy()
        except:pass
        try:self.panelBB.Destroy()
        except:pass
        try:self.panelEnergy.Destroy()
        except:pass

	try:self.panelTCA.Destroy()        
        except:pass
        try:self.panelTCAInvestment.Destroy()
        except:pass
        try:self.panelTCAEnergy.Destroy()
        except:pass
        try:self.panelTCACont.Destroy()
        except:pass
        try:self.panelTCANon.Destroy()
        except:pass   

        try:self.panelCS1.Destroy()
        except:pass
        try:self.panelCS2.Destroy()
        except:pass
        try:self.panelCS3.Destroy()
        except:pass
        try:self.panelCS4.Destroy()
        except:pass
        try:self.panelCS5.Destroy()
        except:pass
        try:self.panelCS6.Destroy()
        except:pass
        try:self.panelCS7.Destroy()
        except:pass

        try:self.panelReport.Destroy()
        except:pass


    def CreateMenu(self):
        self.menuBar = wx.MenuBar()

        self.menuFile = wx.Menu()
        self.menuDatabase = wx.Menu()
        self.menuSettings = wx.Menu()
        self.menuHelp = wx.Menu()

        self.submenuPrint = wx.Menu()
        self.submenuEditDB = wx.Menu()
        self.submenuExportDB = wx.Menu()

        self.submenuEquipments = wx.Menu()
        self.submenuExportEquipments = wx.Menu()
        self.submenuUserLevel = wx.Menu()
        self.submenuClassification = wx.Menu()


        self.PrintFullReport = self.submenuPrint.Append(-1, _U("full report"))
        self.PrintQuestionnaire = self.submenuPrint.Append(-1, _U("questionnaire"))

        self.NewProject = self.menuFile.Append(-1, _U("&New Project"))
        self.OpenProject = self.menuFile.Append(-1, _U("&Open Project"))
        self.ImportProject = self.menuFile.Append(-1, _U("&Import Project"))
        self.ExportProject = self.menuFile.Append(-1, _U("&Export Project"))
        self.menuFile.AppendSeparator()
        self.ImportQ = self.menuFile.Append(-1, _U("Import &Questionnaire"))
        self.menuFile.AppendSeparator()
        self.ImportData = self.menuFile.Append(-1, _U("Import data"))
        self.ExportData = self.menuFile.AppendMenu(-1, _U("Export data"),self.submenuExportDB)
        self.menuFile.AppendSeparator()
        self.Print = self.menuFile.AppendMenu(-1, _U("&Print"), self.submenuPrint)
        self.menuFile.AppendSeparator()
        self.ExitApp = self.menuFile.Append(-1, _U("E&xit"))

        self.EditDBCHP = self.submenuEquipments.Append(-1, _U("&CHP"))
        self.EditDBHeatPump = self.submenuEquipments.Append(-1, _U("&Heat pumps"))
        self.EditDBChiller = self.submenuEquipments.Append(-1, _U("&Chillers"))
        self.EditDBBoiler = self.submenuEquipments.Append(-1, _U("B&oilers"))
        self.EditDBStorage = self.submenuEquipments.Append(-1, _U("Stora&ge"))
        self.EditDBSolarThermal = self.submenuEquipments.Append(-1, _U("&Solar Collectors"))

        self.EditSubDB = self.menuDatabase.AppendMenu(-1, _U("Equipments"), self.submenuEquipments)
        self.EditDBFuel = self.menuDatabase.Append(-1, _U("Fue&ls"))
        self.EditDBFluid = self.menuDatabase.Append(-1, _U("Flui&ds"))
        self.EditDBElectricityMix = self.menuDatabase.Append(-1, _U("Electricity mix"))
        self.EditDBBenchmark = self.menuDatabase.Append(-1, _U("&Benchmarks"))
        self.EditDBBAT = self.menuDatabase.Append(-1, _U("Best available technologies"))
        self.EditDBAdmin = self.menuDatabase.Append(-1, _U("Database administration"))

        self.EditDBNaceCode = self.submenuClassification.Append(-1, _U("&Nace code"))
        self.EditDBUnitOperation = self.submenuClassification.Append(-1, _U("&Unit operation"))

        self.ExportAll = self.submenuExportDB.Append(-1, _U("all data bases"))
        self.ExportEquipments = self.submenuExportDB.AppendMenu(-1, _U("Equipments"), self.submenuExportEquipments)
        self.ExportDBFuel = self.submenuExportDB.Append(-1, _U("Fue&ls"))
        self.ExportDBFluid = self.submenuExportDB.Append(-1, _U("Flui&ds"))
        self.ExportDBElectricityMix = self.submenuExportDB.Append(-1, _U("Electricity mix"))
        self.ExportDBBenchmark = self.submenuExportDB.Append(-1, _U("&Benchmarks"))
        self.ExportDBBAT = self.submenuExportDB.Append(-1, _U("Best available technologies"))

        self.ExportAllEquipments = self.submenuExportEquipments.Append(-1, _U("all equipment data bases"))
        self.ExportDBCHP = self.submenuExportEquipments.Append(-1, _U("&CHP"))
        self.ExportDBHeatPump = self.submenuExportEquipments.Append(-1, _U("&Heat pumps"))
        self.ExportDBChiller = self.submenuExportEquipments.Append(-1, _U("&Chillers"))
        self.ExportDBBoiler = self.submenuExportEquipments.Append(-1, _U("B&oilers"))
        self.ExportDBStorage = self.submenuExportEquipments.Append(-1, _U("Stora&ge"))
        self.ExportDBSolarThermal = self.submenuExportEquipments.Append(-1, _U("&Solar Collectors"))

        self.interactionLevelList=[]
        i = wx.NewId()
        self.interactionLevelList.append(i)
        self.UserSelectLevel1 = self.submenuUserLevel.AppendRadioItem(i, INTERACTIONLEVELS[0])
        i = wx.NewId()
        self.interactionLevelList.append(i)
        self.UserSelectLevel2 = self.submenuUserLevel.AppendRadioItem(i, INTERACTIONLEVELS[1])
        i = wx.NewId()
        self.interactionLevelList.append(i)
        self.UserSelectLevel3 = self.submenuUserLevel.AppendRadioItem(i, INTERACTIONLEVELS[2])
        self.UserLevel = self.menuSettings.AppendMenu(-1, _U("User interaction &level"), self.submenuUserLevel)
        self.Preferences = self.menuSettings.Append(-1, _U("&Preferences"))
        self.Classification = self.menuSettings.AppendMenu(-1, _U("C&lassification"), self.submenuClassification)
        self.Language = self.menuSettings.Append(-1, _U("Language"))

        i = wx.NewId()
        self.ViewMessages = self.menuSettings.AppendCheckItem(i, _U("View message log"))

        self.ManageFonts = self.menuSettings.Append(-1, _U("Fonts"))

        
        self.HelpUserManual = self.menuHelp.Append(-1, _U("&Documentation"))
        self.menuHelp.AppendSeparator()
        self.HelpSupport = self.menuHelp.Append(-1, _U("&Support"))
        self.menuHelp.AppendSeparator()
        self.HelpAbout = self.menuHelp.Append(-1, _U("&About"))
        
        self.menuBar.Append(self.menuFile, _U("&File"))
        self.showMainMenuAlternatives()

        self.menuBar.Append(self.menuDatabase, _U("Database"))
        self.menuBar.Append(self.menuSettings, _U("&Settings"))
        self.menuBar.Append(self.menuHelp, _U("&Help"))

        self.SetMenuBar(self.menuBar)
        self.menuBar.Check(i,True)

    def showMainMenuAlternatives(self):
        checkedId = None
        self.menuView = wx.Menu()
        id0 = wx.NewId()
        id1 = id0
        for al in Status.prj.getAlternativeList():
            self.menuView.AppendRadioItem(id1, al[1])
            # save the active option id for checking later
            if al[1] == Status.ActiveAlternativeName:
                checkedId = id1
            id1 = wx.NewId()

        self.rangeId = (id0,id1-1)
        self.Bind(wx.EVT_MENU_RANGE, self.OnMenuPresentState, id=self.rangeId[0], id2=self.rangeId[1])
        pos = self.menuBar.FindMenu(_U('View'))
        if pos < 0:
            # the first time just append
            self.menuBar.Append(self.menuView, _U("View"))
        else:
            # first delete existing
            self.menuBar.Remove(pos)
            # then insert new
            self.menuBar.Insert(1,self.menuView, _U("View"))

        if checkedId is not None:
            self.menuBar.Check(checkedId,True)

    def changeAssistantMainMenu(self,level):
        try:
            id = self.interactionLevelList[level]
            self.menuBar.Check(id,True)
        except AttributeError,e:
            pass


    def CreateTree(self):
        # access to font properties object
        fp = FontProperties()
        self.tree = wx.TreeCtrl(self.treepanel, -1, wx.Point(0, 0), wx.Size(200, 740),
                                wx.TR_DEFAULT_STYLE | wx.TR_NO_LINES | \
                                wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_HAS_VARIABLE_ROW_HEIGHT)

        DARKORANGE = '#DD5000'
        DARKGREY = '#0F0F0F'
        self.tree.SetFont(fp.getFont())
        self.tree.SetForegroundColour(DARKGREY)
        
        self.qRoot = self.tree.AddRoot("Einstein")

        self.qPage0 = self.tree.AppendItem (self.qRoot, _U("Edit Industry Data"),0)
        self.qPage1 = self.tree.AppendItem (self.qPage0, _U("General data"),0)
        self.qPage2 = self.tree.AppendItem (self.qPage0, _U("Energy consumption"),0)
        self.qPage3 = self.tree.AppendItem (self.qPage0, _U("Processes data"),0)
        self.qPage4 = self.tree.AppendItem (self.qPage0, _U("Generation of heat and cold"),0)
        self.qPage5 = self.tree.AppendItem (self.qPage0, _U("Distribution of heat and cold"),0)
        self.qPage6 = self.tree.AppendItem (self.qPage0, _U("Heat recovery"),0)
        self.qPage7 = self.tree.AppendItem (self.qPage0, _U("Renewable energies"),0)
        self.qPage8 = self.tree.AppendItem (self.qPage0, _U("Buildings"),0)
        self.qPage9 = self.tree.AppendItem (self.qPage0, _U("Economic parameters"),0)

        self.qCC = self.tree.AppendItem (self.qRoot, _U("Consistency Check"))
        
        #
        # statistics subtree
        #
        self.qStatistics = self.tree.AppendItem (self.qRoot, _U("Energy statistics"))
        self.qEA = self.tree.AppendItem (self.qStatistics, _U("Annual data"))
        self.qEM = self.tree.AppendItem (self.qStatistics, _U("Monthly data"))
        self.qEH = self.tree.AppendItem (self.qStatistics, _U("Hourly performance data"))
        # annual statistics subtree
        self.qEA1 = self.tree.AppendItem (self.qEA, _U("Primary energy"))
        self.qEA2 = self.tree.AppendItem (self.qEA, _U("Final energy by fuels"))
        self.qEA3 = self.tree.AppendItem (self.qEA, _U("Final energy by equipment"))
        self.qEA4a = self.tree.AppendItem (self.qEA, _U("Heat demand (proc.)"))
        self.qEA4b = self.tree.AppendItem (self.qEA, _U("Heat demand (temp.)"))
        self.qEA4c = self.tree.AppendItem (self.qEA, _U("Heat demand (time)"))
        self.qEA5 = self.tree.AppendItem (self.qEA, _U("Energy intensity"))
        # monthly statistics subtree
        self.qEM1 = self.tree.AppendItem (self.qEM, _U("Monthly demand"))
        self.qEM2 = self.tree.AppendItem (self.qEM, _U("Monthly supply"))
        # hourly statistics subtree
        self.qEH1 = self.tree.AppendItem (self.qEH, _U("Hourly demand"))
        self.qEH2 = self.tree.AppendItem (self.qEH, _U("Hourly supply"))


        self.qBM = self.tree.AppendItem (self.qRoot, _U("Benchmark check"))
        self.qBM1 = self.tree.AppendItem (self.qBM, _U("Global energy intensity"))
        self.qBM2 = self.tree.AppendItem (self.qBM, _U("SEC by product"))
        self.qBM3 = self.tree.AppendItem (self.qBM, _U("SEC by process"))
        
        #TS20080419 Example of a conditional tree branch.
        # the argument 'data=' is a list of two members:
        #                      a. a boolean function for testing the condition.
        #                         If the function returns False, the tree branch is not activated
        #                      b. a text. When the tree branch cannot be activated, this text is
        #                         presented as a message to the user.
        # When the tree is first shown, all the branches that have this argument will be shown collapsed.
        # There is a Cond utility function to help loading the data argument.
        #
        #
        self.qA = self.tree.AppendItem (self.qRoot, _U("Alternative proposals"))

        #Design
        self.qDesign = self.tree.AppendItem (self.qA, _U("Design"))
        #Process optimisation
        self.qPO = self.tree.AppendItem (self.qDesign, _U("Process optimisation"))
        #Process optimisation interface 1
        self.qHX = self.tree.AppendItem (self.qDesign, _U("HX network"))
            #H&C Supply
        self.qHC = self.tree.AppendItem (self.qDesign, _U("H&C Supply"))
                #H&C Storage
        self.qStorage = self.tree.AppendItem (self.qHC, _U("H&C Storage"))
                #CHP
        self.qCHP = self.tree.AppendItem (self.qHC, _U("CHP"))
                #Solar Thermal
        self.qST = self.tree.AppendItem (self.qHC, _U("Solar Thermal"))
                #Heat Pumps
        self.qHP = self.tree.AppendItem (self.qHC, _U("Heat Pumps"))
                #Biomass
        self.qBIO = self.tree.AppendItem (self.qHC, _U("Biomass"))
                #Chillers
        self.qCH = self.tree.AppendItem (self.qHC, _U("Chillers"))
                #Boilers & burners
        self.qBB = self.tree.AppendItem (self.qHC, _U("Boilers & burners"))

            #H&C Distribution
        self.qDistribution = self.tree.AppendItem (self.qDesign, _U("H&C Distribution"))

        #Energy performance
        self.qEnergy = self.tree.AppendItem (self.qA, _U("Energy performance"))

        #Total Cost Assessment
        self.qECO  = self.tree.AppendItem (self.qA, _U("Total Cost Assessment"))  
        self.qECO1 = self.tree.AppendItem (self.qECO, _U("Investment"))
        self.qECO2 = self.tree.AppendItem (self.qECO, _U("Energy and operating costs"))
        self.qECO3 = self.tree.AppendItem (self.qECO, _U("Contingencies"))
        self.qECO4 = self.tree.AppendItem (self.qECO, _U("Non reocurring costs"))    


        #Comparative analysis
        self.qCS = self.tree.AppendItem (self.qA, _U("Comparative study"))
            #Comparative study – Detail Info 1
        self.qCS1 = self.tree.AppendItem (self.qCS, _U("Comp.study: Primary energy"))
            #Comparative study – Detail Info 2
        self.qCS2 = self.tree.AppendItem (self.qCS, _U("Comp.study: Process & supply heat"))
            #Comparative study – Detail Info 3
        self.qCS3 = self.tree.AppendItem (self.qCS, _U("Comp.study: Environmental  impact"))
            #Comparative study – Detail Info 4
        self.qCS4 = self.tree.AppendItem (self.qCS, _U("Comp.study: Investment cost"))
            #Comparative study – Detail Info 5
        self.qCS5 = self.tree.AppendItem (self.qCS, _U("Comp.study: Annual cost"))
            #Comparative study – Detail Info 6
        self.qCS6 = self.tree.AppendItem (self.qCS, _U("Comp.study: Additional cost per saved energy"))
            #Comparative study – Detail Info 7
        self.qCS7 = self.tree.AppendItem (self.qCS, _U("Comp.study: Internal rate of return"))

        self.qReport = self.tree.AppendItem (self.qRoot, _U("Report"))
        
        self.tree.Expand(self.qRoot)
        self.tree.Expand(self.qPage0)
        self.tree.Expand(self.qStatistics)
        self.tree.Expand(self.qBM)
        self.tree.Expand(self.qA)
    

    def BindEvents(self):
        #--- binding the menu
        self.Bind(wx.EVT_MENU, self.OnMenuNewProject, self.NewProject)
        self.Bind(wx.EVT_MENU, self.OnMenuOpenProject, self.OpenProject)
        self.Bind(wx.EVT_MENU, self.OnMenuExit, self.ExitApp)
        self.Bind(wx.EVT_MENU, self.OnMenuImportData, self.ImportData)
        self.Bind(wx.EVT_MENU, self.OnMenuImportProject, self.ImportProject)
        self.Bind(wx.EVT_MENU, self.OnMenuExportProject, self.ExportProject)
        self.Bind(wx.EVT_MENU, self.OnMenuImportQ, self.ImportQ)

        self.Bind(wx.EVT_MENU, self.OnMenuEditDBAdmin, self.EditDBAdmin)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBBenchmark, self.EditDBBenchmark)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBBAT, self.EditDBBAT)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBNaceCode, self.EditDBNaceCode)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBUnitOperation, self.EditDBUnitOperation)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBCHP, self.EditDBCHP)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBHeatPump, self.EditDBHeatPump)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBFluid, self.EditDBFluid)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBFuel, self.EditDBFuel)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBElectricityMix, self.EditDBElectricityMix)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBBoiler, self.EditDBBoiler)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBSolarThermal, self.EditDBSolarThermal)
        self.Bind(wx.EVT_MENU, self.OnMenuEditDBChiller, self.EditDBChiller)

        self.Bind(wx.EVT_MENU, self.OnMenuExportAll, self.ExportAll)
        self.Bind(wx.EVT_MENU, self.OnMenuExportDBBenchmark, self.ExportDBBenchmark)
        self.Bind(wx.EVT_MENU, self.OnMenuExportAllEquipments, self.ExportAllEquipments)
        self.Bind(wx.EVT_MENU, self.OnMenuExportDBCHP, self.ExportDBCHP)
        self.Bind(wx.EVT_MENU, self.OnMenuExportDBHeatPump, self.ExportDBHeatPump)
        self.Bind(wx.EVT_MENU, self.OnMenuExportDBFluid, self.ExportDBFluid)
        self.Bind(wx.EVT_MENU, self.OnMenuExportDBFuel, self.ExportDBFuel)
        self.Bind(wx.EVT_MENU, self.OnMenuExportDBElectricityMix, self.ExportDBElectricityMix)
        self.Bind(wx.EVT_MENU, self.OnMenuExportDBBoiler, self.ExportDBBoiler)
        self.Bind(wx.EVT_MENU, self.OnMenuExportDBSolarThermal, self.ExportDBSolarThermal)
        self.Bind(wx.EVT_MENU, self.OnMenuExportDBChiller, self.ExportDBChiller)

        self.Bind(wx.EVT_MENU, self.OnMenuUserSelectLevel1, self.UserSelectLevel1)
        self.Bind(wx.EVT_MENU, self.OnMenuUserSelectLevel2, self.UserSelectLevel2)
        self.Bind(wx.EVT_MENU, self.OnMenuUserSelectLevel3, self.UserSelectLevel3)

        self.Bind(wx.EVT_MENU, self.OnMenuSettingsPreferences, self.Preferences)
        self.Bind(wx.EVT_MENU, self.OnMenuSettingsLanguage, self.Language)
        self.Bind(wx.EVT_MENU, self.OnMenuSettingsViewMessages, self.ViewMessages)
        self.Bind(wx.EVT_MENU, self.OnMenuSettingsManageFonts, self.ManageFonts)

        self.Bind(wx.EVT_MENU, self.OnMenuHelpUserManual, self.HelpUserManual)
        self.Bind(wx.EVT_MENU, self.OnMenuHelpSupport, self.HelpSupport)
        self.Bind(wx.EVT_MENU, self.OnMenuHelpAbout, self.HelpAbout)

        #--- binding the Tree
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged, self.tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.OnTreeSelChanging, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnTreeItemExpanding, self.tree)



#==============================================================================
#------------------------------------------------------------------------------
#   Application module
#------------------------------------------------------------------------------
class EinsteinApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)

    def OnInit(self):
        self.Bind(wx.EVT_QUERY_END_SESSION , self._onQueryEndSession )
        self.Bind(wx.EVT_END_SESSION       , self._onEndSession )
        self.frame = EinsteinFrame(parent=None, id=-1, title="Einstein")
        self.SetTopWindow(self.frame)
        # initialize Einstein support
        self.frame.doLog = HelperClass.LogHelper()
        self.frame.conf = HelperClass.ConfigHelper()
        self.frame.doLog.LogThis("\n==================================\n"+\
                                 ("Starting EINSTEIN Version %s"%VERSION)+\
                                 "\n==================================\n")

        # attempt to connect to database
        # if not possible, invoke a database setup dialog, so the user can
        # attempt to change some parameters and fix the problem.
        while True:
            try:
                Status.SQL = self.frame.connectToDB()
                Status.DB =  pSQL.pSQL(Status.SQL, self.frame.DBName)
                self.frame.doLog.LogThis('Connected to database %s@%s' % (self.frame.DBName, self.frame.DBHost))
                break
            except MySQLdb.Error, e:
                self.frame.showWarning('Cannot connect to database. ' +\
                                       'Error is:\n\n%s\n\nPlease verify your database parameters.' % str(e))

                dlgdb = DlgDatabase(parent=None,id=-1)
                rsp = dlgdb.ShowModal()
                if rsp == wx.ID_OK:
                    # read ini file again
                    self.frame.conf = HelperClass.ConfigHelper()
                    continue
                # user has canceled
                sys.exit(1)

        # initialize language
        self.frame.setLanguage()

        #initialize fonts management
        # (needs database connected)
        fp = FontProperties()
        fp.initializeFont()
        
#HS2008-05-28: Status.main has to exist BEFORE instantiating project
            
        Status.main = self.frame
        Status.mod = None
        Status.int = Interfaces()
        Status.prj = Project()
        Status.mod = Modules()

        # create Einstein UI
        self.frame.createUI()
        self.frame.Show()
        self.frame.Bind(wx.EVT_CLOSE, self._onFrameClose)
        self.SetTopWindow(self.frame)
        
        # upgrade to current version if necessary
        from einstein.modules.upgrade import upgradeEINSTEIN
        upgradeEINSTEIN()

        return True;
    #
    #TS20080421 Some testing code that will magically disappear later
    #
    def OnExit(self):
        sys.stdout.flush()

    def OnQueryEndSession(self):
        sys.stdout.flush()

    def _onQueryEndSession(self,event):
        sys.stdout.flush()

    def _onEndSession(self,event):
        sys.stdout.flush()

    def _onFrameClose(self, event):
        sys.stdout.flush()
        self.frame.Destroy()
        wx.Exit()


#------------------------------------------------------------------------------
#   Application start
#------------------------------------------------------------------------------

if __name__ == '__main__':

    app = EinsteinApp()
    app.MainLoop()


#==============================================================================
