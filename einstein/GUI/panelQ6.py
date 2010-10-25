
# -*- coding: iso-8859-15 -*-
#==============================================================================
#
#	E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (<a href="http://www.iee-einstein.org/" target="_blank">www.iee-einstein.org</a>)
#
#------------------------------------------------------------------------------
#
#	PanelQ6: Heat exchangers
#
#==============================================================================
#
#   EINSTEIN Version No.: 1.0
#   Created by: 	Heiko Henning, Tom Sobota, Hans Schweiger, Stoyan Danov
#                       04/05/2008 - 13/10/2008
#
#   Update No. 002
#
#   Since Version 1.0 revised by:
#                       Hans Schweiger      01/04/2009
#                       Hans Schweiger      06/07/2009
#
#       Changes to previous version:
#       01/04/2009: HS  impossibility to save entries with empty name field
#       06/07/2009: HS  small bug-fix: storage of WHEEMedium was not possible
#
#------------------------------------------------------------------------------
#	(C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008,2009
#	http://www.energyxperts.net/
#
#	This program is free software: you can redistribute it or modify it under
#	the terms of the GNU general public license as published by the Free
#	Software Foundation (www.gnu.org).
#
#==============================================================================


import copy

from einstein.modules.energystreams.StreamGeneration import loadStreamData
import wx
import pSQL
from status import Status
from units import *
from displayClasses import *
#from einstein.modules.constants import HXTYPES
from GUITools import *
from fonts import *
from einstein.modules.energystreams.StreamGeneration import *
from einstein.modules.energystreams.Stream import *

ENCODING = "latin-1"

# constants that control the default sizes
# 1. font sizes
TYPE_SIZE_LEFT    =   9
TYPE_SIZE_MIDDLE  =   9
TYPE_SIZE_RIGHT   =   9
TYPE_SIZE_TITLES  =  10

# 2. field sizes
HEIGHT               =  32
HEIGHT_RIGHT         =  32

LABEL_WIDTH_LEFT     = 300
LABEL_WIDTH_RIGHT    = 300

DATA_ENTRY_WIDTH     = 100
DATA_ENTRY_WIDTH_LEFT= 100

UNITS_WIDTH          =  90

# 3. vertical separation between fields
VSEP_LEFT            =   2
VSEP_RIGHT           =   2


ORANGE = '#FF6000'
TITLE_COLOR = ORANGE

class SinkSourcePanel(wx.Panel):
    def __init__(self, parent, main):
	self.main = main
        self._init_ctrls(parent)
        self.__do_layout()
        self.disabledALL = True
        self.disabledTempEntry = True

    def _init_ctrls(self, parent):

        #self.txtStreamType = wx.StaticText(parent, -1, _U("Stream Type"))
        self.txtStream = wx.StaticText(parent, -1, _U("Stream"))
        self.cbStreamType = wx.ComboBox(parent, -1, choices=['Processes', 'Distribution Lines', 'Equipments', 'WHEE'], style=wx.CB_READONLY)
        self.cbStream = wx.ComboBox(parent, -1, choices=[], style=wx.CB_READONLY)

        self.buttonAdd = wx.Button(parent,-1,label="Add")
        self.buttonDelete = wx.Button(parent, -1, label = "Delete")
        self.listBox= wx.ListBox(parent,-1,
                            choices=[])
    
        self.rbInletTemp = wx.RadioButton(parent, wx.ID_ANY, "Inlet Temperature",style=wx.RB_GROUP)
        self.rbInletHX = wx.RadioButton(parent, wx.ID_ANY, "Outlet of HX")

        self.inletTemp = wx.TextCtrl(parent, -1)
        #self.inletTemp.Disable()
        self.outletHXChoice = wx.ComboBox(parent, -1, choices=[], style=wx.CB_READONLY)

        self.rbOutletTemp = wx.RadioButton(parent, wx.ID_ANY, "Outlet Temperature",style=wx.RB_GROUP)
        self.rbOutletHX = wx.RadioButton(parent, wx.ID_ANY, "Inlet of HX")
        self.outletTemp = wx.TextCtrl(parent, -1)

        self.inletHXChoice = wx.ComboBox(parent, -1, choices=[],style=wx.CB_READONLY)

        self.txtPercentHeatFlow = wx.StaticText(parent, -1, 'Percentage of Heat in HX')

        self.tbPercentHeatFlow = wx.TextCtrl(parent, -1)
        #self.slider = wx.Slider(parent, -1)

        self.frame_inlet = wx.StaticBox(parent, -1, _U("Inlet"))
        self.frame_inlet.SetForegroundColour(TITLE_COLOR)
        self.frame_inlet.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.frame_outlet = wx.StaticBox(parent, -1, _U("Outlet"))
        self.frame_outlet.SetForegroundColour(TITLE_COLOR)
        self.frame_outlet.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.frame_heatflow = wx.StaticBox(parent, -1, _U("Heat Flow"))
        self.frame_heatflow.SetForegroundColour(TITLE_COLOR)
        self.frame_heatflow.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.frame_temp = wx.StaticBox(parent, -1, _U(""))
        self.frame_temp.SetForegroundColour(TITLE_COLOR)
        self.frame_temp.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

#        self.disableAll()
        self.disableTempEntry()

    def disableAll(self):
        self.cbStreamType.Disable()
        self.cbStream.Disable()
        self.listBox.Disable()
        self.buttonAdd.Disable()
        self.rbInletTemp.Disable()
        self.rbInletHX.Disable()
        self.inletTemp.Disable()
        self.outletHXChoice.Disable()
        self.rbOutletTemp.Disable()
        self.rbOutletHX.Disable()
        self.outletTemp.Disable()
        self.inletHXChoice.Disable()
        self.tbPercentHeatFlow.Disable()

    def enableAll(self):
        self.cbStreamType.Enable()
        self.cbStream.Enable()
        self.listBox.Enable()
        self.buttonAdd.Enable()
        self.rbInletTemp.Enable()
        self.rbInletHX.Enable()
        self.inletTemp.Enable()
#        self.outletHXChoice.Enable()
        self.rbOutletTemp.Enable()
        self.rbOutletHX.Enable()
        self.outletTemp.Enable()
#        self.inletHXChoice.Enable()
        self.tbPercentHeatFlow.Enable()

    def disableTempEntry(self):
        self.rbInletTemp.Disable()
        self.rbInletHX.Disable()
        self.inletTemp.Disable()
        self.outletHXChoice.Disable()
        self.rbOutletTemp.Disable()
        self.rbOutletHX.Disable()
        self.outletTemp.Disable()
        self.inletHXChoice.Disable()
        self.tbPercentHeatFlow.Disable()

    def enableTempEntry(self):
        self.rbInletTemp.Enable()
        self.rbInletHX.Enable()
#        self.inletTemp.Enable()
        self.rbOutletTemp.Enable()
        self.rbOutletHX.Enable()
#        self.outletTemp.Enable()
        self.tbPercentHeatFlow.Enable()


    def __do_layout(self):
        pass

def _U(text):
    return unicode(_(text),"utf-8")



class PanelQ6(wx.Panel):
    def __init__(self, parent, main):
        self.main = main
        self._init_ctrls(parent)
        self.__do_layout()

        self.HXID = None
        self.WHEEID = None

        self.HXNo = None
        self.WHEENo = None

        self.HXName = None
        self.WHEEName = None

        if Status.int.NameGen == None:
            Status.int.NameGen = NameGeneration()
            Status.int.NameGen.loadDataFromDB()

        self.HXPinch = None
        self.selectedSStream = None
        self.temperatureIsChanged = False
        self._init_HXPinch()

        self.fillPage()

    def _init_HXPinch(self):
        DB = Status.DB
        HXIDList = Status.prj.getHXList("QHeatExchanger_ID")
        HXNames = Status.prj.getHXList("HXName")
        Status.int.HXPinchConnection = []
        for i in xrange(len(HXIDList)):
            HXPinch = HXPinchConnection(HXIDList[i], HXNames[i])
            HXPinch.loadFromDB()
            Status.int.HXPinchConnection.append(HXPinch)


    def _init_ctrls(self, parent):

#------------------------------------------------------------------------------
#--- UI setup
#------------------------------------------------------------------------------		

        wx.Panel.__init__(self, id=-1, name='PanelQ6', parent=parent,
              pos=wx.Point(0, 0), size=wx.Size(780, 580), style=0)
        self.Hide()

        # access to font properties object
        fp = FontProperties()

        self.notebook = wx.Notebook(self, -1, style=0)
        self.notebook.SetFont(fp.getFont())

        self.page0 = wx.Panel(self.notebook)
        self.notebook.AddPage(self.page0, _U('Heat recovery from thermal equipment'))

        self.page1 = wx.Panel(self.notebook)
        self.notebook.AddPage(self.page1, _U('Heat recovery from electrical equipment'))


        self.notebookSinkSource = wx.Notebook(self.page0, -1, style=0)
        self.notebookSinkSource.SetFont(fp.getFont())
#        self.frame_nbSinkSource = wx.StaticBox(self.notebookSinkSource, -1, _U('Sink/Source'))
        self.pageSink = wx.Panel(self.notebookSinkSource)
        self.notebookSinkSource.AddPage(self.pageSink, _U('Sink'))
#        self.pageSource = wx.Panel(self.notebookSinkSource)
        self.pageSource = wx.Panel(self.notebookSinkSource)
        self.notebookSinkSource.AddPage(self.pageSource, _U('Source'))
        self.SinkActive = True
#        self.frame_sink = wx.StaticBox(self.pageSink, -1, _U('Sink'))
#        self.frame_source = wx.StaticBox(self.pageSource, -1, _U('Source'))
        self.Sink = SinkSourcePanel(self.pageSink, self)
        self.Source = SinkSourcePanel(self.pageSource, self)

        self.frame_exchangers_list = wx.StaticBox(self.page0, -1, _U("Heat exchangers list"))
        self.frame_exchangers_list.SetForegroundColour(TITLE_COLOR)
        self.frame_exchangers_list.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.frame_exchanger_data = wx.StaticBox(self.page0, -1, _U("Heat exchanger data"))
        self.frame_exchanger_data.SetForegroundColour(TITLE_COLOR)
        self.frame_exchanger_data.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))


        self.frame_source_sink = wx.StaticBox(self.page0, -1, _U("Heat source / sink"))
        self.frame_source_sink.SetForegroundColour(TITLE_COLOR)
        self.frame_source_sink.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        

        self.frame_electrical_equipment_list = wx.StaticBox(self.page1, -1, _U("Electrical equipment list"))
        self.frame_electrical_equipment_list.SetForegroundColour(TITLE_COLOR)
        self.frame_electrical_equipment_list.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))


        self.frame_equipment_data = wx.StaticBox(self.page1, -1, _U("Equipment data"))
        self.frame_equipment_data.SetForegroundColour(TITLE_COLOR)
        self.frame_equipment_data.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))


        self.frame_schedule = wx.StaticBox(self.page1, -1, _U("Schedule"))
        self.frame_schedule.SetForegroundColour(TITLE_COLOR)
        self.frame_schedule.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))


        # set font for titles
        # 1. save actual font parameters on the stack
        fp.pushFont()
        # 2. change size and weight
        fp.changeFont(size=TYPE_SIZE_TITLES, weight=wx.BOLD)
        self.frame_exchangers_list.SetFont(fp.getFont())
        self.frame_exchanger_data.SetFont(fp.getFont())
        self.frame_source_sink.SetFont(fp.getFont())
        self.frame_electrical_equipment_list.SetFont(fp.getFont())
        self.frame_schedule.SetFont(fp.getFont())
        self.frame_equipment_data.SetFont(fp.getFont())
        # 3. recover previous font state
        fp.popFont()
      
        fs = FieldSizes(wHeight=HEIGHT,wLabel=LABEL_WIDTH_LEFT,
                       wData=DATA_ENTRY_WIDTH_LEFT,wUnits=UNITS_WIDTH)

        #
        # left tab controls
        # tab 0 - Heat recovery from thermal equipment
        #
        fp.pushFont()
        fp.changeFont(size=TYPE_SIZE_LEFT)

        # left static box: List of heat exchangers

        self.listBoxHX = wx.ListBox(self.page0,-1,
                                    choices=[])
        self.Bind(wx.EVT_LISTBOX, self.OnListBoxHXListboxClick, self.listBoxHX)




        # right top static box: Heat exchanger data	

        self.tc1 = TextEntry(self.page0,maxchars=255,value='',
                             label=_U("Short name of heat exchanger"),
                             tip=_U("Give a short name of the equipment"))

        self.tc2 = ChoiceEntry(self.page0,
                               values=[],
                               label=_U("Heat exchanger type"),
                               tip=_U("Specify the type of heat exchanger, e.g. shell-and-tube, plate, fin-and-tube, ..."))

        
        self.tc3 = FloatEntry(self.page0,
                              decimals=1, minval=0., maxval=1.e+12, value=0.,
                              unitdict='POWER',
                              label=_U("Heat transfer rate"),
                              tip=_U("Heat transfer rate for the specific working conditions"))

        self.tc4 = FloatEntry(self.page0,
                              decimals=1, minval=0., maxval=999., value=0.,
                              unitdict='TEMPERATURE',
                              label=_U("Log. Mean Temperature Diff. (LMTD)"),
                              tip=_U("Between the fluids in the heat exchanger"))

        self.tc5 = FloatEntry(self.page0,
                              decimals=1, minval=0., maxval=1.e+12, value=0.,
                              unitdict='ENERGY',
                              label=_U("Total heat transfered"),
                              tip=_U("Total heat transferred per year"))
    
        self.tcUA = FloatEntry(self.page0,
                              decimals=1, minval=0., maxval=1.e+12, value=0.,
                              unitdict='HEATTRANSFERCOEF',
                              label=_U("UA value of HX"),
                              tip=_U(""))


        # right bottom staticbox Heat source / sink

#        self.tc6 = ChoiceEntry(self.pageSink,
#                               values=[],
#                               label=_U("Heat source (process [+outflow no.],\nequipment, ...)"),
#                               tip=_U("Indicate: Process, Equipment, Distribution line, Compressor, Electric motor, together with its number"))
#
#	self.tc6_1 = ChoiceEntry(self.pageSink,
#                               values=[],
#                               label=_U("Source stream"),
#                               tip=_U(""))
#
#        self.tc7 = FloatEntry(self.pageSink,
#                              decimals=1, minval=0., maxval=999., value=0.,
#                              unitdict='TEMPERATURE',
#                              label=_U("Inlet temperature (source)"),
#                              tip=_U("Inlet temperature of the hot fluid"))
#
#        self.tc8 = FloatEntry(self.pageSink,
#                              decimals=4, minval=0., maxval=99999., value=0.,
#                              unitdict='SPECIFICENTHALPY',
#                              label=_U("Inlet specific enthalpy (source)"),
#                              tip=_U("Inlet enthalpy of the hot fluid"))
#
#        self.tc9 = FloatEntry(self.pageSink,
#                              decimals=1, minval=0., maxval=999., value=0.,
#                              unitdict='TEMPERATURE',
#                              label=_U("Outlet temperature (source)"),
#                              tip=_U("Outlet temperature of hot fluid"))
#
#        self.tc10 = FloatEntry(self.pageSink,
#                              decimals=4, minval=0., maxval=99999., value=0.,
#                              unitdict='SPECIFICENTHALPY',
#                              label=_U("Outlet specific enthalpy (source)"),
#                              tip=_U("Outlet enthalpy of the hot fluid"))
#
#
#        self.tc11 = ChoiceEntry(self.pageSink,
#                               values=[],
#                               label=_U("Heat sink (process, pipe/duct)"),
#                               tip=_U("Indicate: Process or Distribution line and number. If heat exchange is via storage, it should be defined in the distribution line"))
#
#
#        self.tc12 = FloatEntry(self.pageSink,
#                               decimals=1, minval=0., maxval=999., value=0.,
#                               unitdict='TEMPERATURE',
#                               label=_U("Inlet temperature (sink)"),
#                               tip=_U("Inlet temperature of the cold fluid"))
#
#        self.tc13 = FloatEntry(self.pageSink,
#                               decimals=1, minval=0., maxval=999., value=0.,
#                               unitdict='TEMPERATURE',
#                               label=_U("Outlet temperature (sink)"),
#                               tip=_U("Inlet enthalpy of the cold fluid"))



        
        #
        # right tab controls
        # tab 1 - Heat recovery from electrical equipment
        #
        fp.changeFont(size=TYPE_SIZE_RIGHT)
        f = FieldSizes(wHeight=HEIGHT_RIGHT,wLabel=LABEL_WIDTH_RIGHT)


        # left static box: List of electrical equipment


        self.listBoxWHEE = wx.ListBox(self.page1,-1,choices=[])
        self.Bind(wx.EVT_LISTBOX, self.OnListBoxWHEEListboxClick, self.listBoxWHEE)


        # right upper static box: Equipment data

        self.tc101 = TextEntry(self.page1,maxchars=255,value='',
                               label=_U("Short name of electrical equipment"),
                               tip=_U("Give a short name of the equipment"))

        self.tc102 = ChoiceEntry(self.page1,
                                 values=TRANSWHEEEQTYPES.values(),
                                 label=_U("Equipment type"),
                                 tip=_U("specify type of equipment, e.g. compressor, electric motor,..."))

        self.tc103 = ChoiceEntry(self.page1,
                                 values=TRANSWHEEWASTEHEATTYPES.values(),
                                 label=_U("Waste heat type"),
                                 tip=_U("Specify type of waste heat (e.g. Recooling of compressed air, cooling water of motor/compressor, ...)"))
        
        self.tc104 = FloatEntry(self.page1,
                                decimals=1, minval=0., maxval=1.e+12, value=0.,
                                unitdict='POWER',
                                label=_U("Available waste heat"),
                                tip=_U("Estimated quantity"))

        self.tc105 = ChoiceEntry(self.page1,
                                 values=[],
                                 label=_U("Medium"),
                                 tip=_U("Waste heat carrying medium (fluid)"))

        self.tc106 = FloatEntry(self.page1,
                                decimals=1, minval=0., maxval=1.e+12, value=0.,
                                unitdict='MASSORVOLUMEFLOW',
                                label=_U("Flow rate"),
                                tip=_U("Specify the flow rate of the waste heat carrying medium"))

        self.tc107 = FloatEntry(self.page1,
                                decimals=1, minval=0., maxval=999., value=0.,
                                unitdict='TEMPERATURE',
                                label=_U("Waste heat temperature"),
                                tip=_U("Specify the temperature of the waste heat medium at the outlet"))


        self.tc108 = ChoiceEntry(self.page1,
                                 values=TRANSYESNO.values(),
                                 label=_U("Present use of waste heat"),
                                 tip=_U("If yes, specify distribution pipe / duct or heat exchanger where waste heat is used at present"))

        # right lower static box Schedule

        self.tc110 = FloatEntry(self.page1,
                                decimals=1, minval=0., maxval=999., value=0.,
                                unitdict='TIME',
                                label=_U("Hours of  operation per day"),
                                tip=_U(" "))

        self.tc111 = FloatEntry(self.page1,
                                decimals=1, minval=0., maxval=99., value=0.,
                                label=_U("Number of batches per day"),
                                tip=_U(" "))

        self.tc112 = FloatEntry(self.page1,
                                decimals=1, minval=0., maxval=24., value=0.,
                                unitdict='TIME',
                                label=_U("Duration of 1 batch"),
                                tip=_U(" "))

        self.tc113 = FloatEntry(self.page1,
                                decimals=1, minval=0., maxval=365., value=0.,
                                label=_U("Days of operation per year"),
                                tip=_U(" "))

        #
        # buttons
        #
        self.buttonHXDelete = wx.Button(self.page0,-1,label="delete HX")
        self.Bind(wx.EVT_BUTTON, self.OnButtonHXDelete, self.buttonHXDelete)
        self.buttonHXDelete.SetMinSize((136, 32))
        self.buttonHXDelete.SetFont(fp.getFont())

        self.buttonHXAdd = wx.Button(self.page0,-1, label="add HX")
        self.Bind(wx.EVT_BUTTON, self.OnButtonHXAdd, self.buttonHXAdd)
        self.buttonHXAdd.SetMinSize((136, 32))
        self.buttonHXAdd.SetFont(fp.getFont())

        self.buttonWHEEDelete = wx.Button(self.page1,-1,label="delete WHEE")
        self.Bind(wx.EVT_BUTTON, self.OnButtonWHEEDelete, self.buttonWHEEDelete)
        self.buttonWHEEDelete.SetMinSize((136, 32))
        self.buttonWHEEDelete.SetFont(fp.getFont())

        self.buttonWHEEAdd = wx.Button(self.page1,-1,label="add WHEE")
        self.Bind(wx.EVT_BUTTON, self.OnButtonWHEEAdd, self.buttonWHEEAdd)
        self.buttonWHEEAdd.SetMinSize((136, 32))
        self.buttonWHEEAdd.SetFont(fp.getFont())

        self.buttonOK = wx.Button(self,wx.ID_OK,"")
        self.Bind(wx.EVT_BUTTON, self.OnButtonOK, self.buttonOK)
        self.buttonOK.SetDefault()

        self.buttonCancel = wx.Button(self,wx.ID_CANCEL, "")
        self.Bind(wx.EVT_BUTTON, self.OnButtonCancel, self.buttonCancel)

        # recover previous font parameters from the stack
        fp.popFont()



    def __do_layout(self):
        flagText = wx.ALIGN_CENTER_VERTICAL|wx.TOP

        # global sizer for panel. Contains notebook w/two tabs + buttons Cancel and Ok
        sizerGlobal = wx.BoxSizer(wx.VERTICAL)
        
        # sizer for left tab
        # tab 0, Heat recovery from thermal equipment
        sizerPage0 = wx.BoxSizer(wx.HORIZONTAL)
        # left part: listbox
        sizerP0Left= wx.StaticBoxSizer(self.frame_exchangers_list, wx.VERTICAL)
        sizerP0Left.Add(self.listBoxHX, 1, wx.EXPAND, 0)
        sizerP0Left.Add(self.buttonHXAdd, 0, wx.ALIGN_RIGHT, 0)
        sizerP0Left.Add(self.buttonHXDelete, 0, wx.ALIGN_RIGHT, 0)
        sizerPage0.Add(sizerP0Left,2,wx.EXPAND|wx.TOP,10)

        # right part: data entries
        sizerP0Right= wx.BoxSizer(wx.VERTICAL)
        sizerP0RightTop= wx.StaticBoxSizer(self.frame_exchanger_data, wx.VERTICAL)
        sizerP0RightTop.Add(self.tc1, 0, flagText, VSEP_RIGHT)
        sizerP0RightTop.Add(self.tc2, 0, flagText, VSEP_RIGHT)
        sizerP0RightTop.Add(self.tc3, 0, flagText, VSEP_RIGHT)
        sizerP0RightTop.Add(self.tc4, 0, flagText, VSEP_RIGHT)
        sizerP0RightTop.Add(self.tc5, 0, flagText, VSEP_RIGHT)
        sizerP0RightTop.Add(self.tcUA, 0, flagText, VSEP_RIGHT)
        sizerP0Right.Add(sizerP0RightTop,0,wx.EXPAND,0)
        
        sizerP0RightBottom= wx.StaticBoxSizer(self.frame_source_sink, wx.VERTICAL)
        sizerP0RightBottom.Add(self.notebookSinkSource, 0, wx.EXPAND, VSEP_RIGHT)

        self.SinkSourceLayOut(self.pageSink, self.Sink)
        self.SinkSourceLayOut(self.pageSource, self.Source)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNBSinkSourceChange, self.notebookSinkSource)
#        sizerSource = wx.BoxSizer(wx.VERTICAL)
#        self.pageSource.SetSizer(sizerSource)
#
#        sizerSource.Add(self.Source.StreamType, 0, flagText, VSEP_RIGHT)
##	self.Bind(wx.EVT_CHOICE, self.OnHeatSourceChoice, self.tc6.entry)
#	sizerSource.Add(self.Source.Stream, 0, flagText, VSEP_RIGHT)
#        sizerSource.Add(self.Source.buttonAdd, 0, flagText, VSEP_RIGHT)
#        sizerSource.Add(self.Source.listBox, 0, flagText, VSEP_RIGHT)
#        sizerSource.Add(self.Source.InletText, 0, flagText, VSEP_RIGHT)
#        sizerSource.Add(self.Source.OutletText, 0, flagText, VSEP_RIGHT)

        sizerP0Right.Add(sizerP0RightBottom,7,wx.EXPAND| wx.ALL,0)
        sizerPage0.Add(sizerP0Right,5,wx.EXPAND|wx.TOP,10)
        self.page0.SetSizer(sizerPage0)

        # sizer for right tab
        # tab 1, Heat recovery from electrical equipment
        sizerPage1 = wx.BoxSizer(wx.HORIZONTAL)
        # left part: listbox
        sizerP1Left= wx.StaticBoxSizer(self.frame_electrical_equipment_list, wx.VERTICAL)
        sizerP1Left.Add(self.listBoxWHEE, 1, wx.EXPAND, 0)
        sizerP1Left.Add(self.buttonWHEEAdd, 0, wx.ALIGN_RIGHT, 0)
        sizerP1Left.Add(self.buttonWHEEDelete, 0, wx.ALIGN_RIGHT, 0)
        sizerPage1.Add(sizerP1Left,2,wx.EXPAND|wx.TOP,10)

        # right part: data entry
        sizerP1Right= wx.BoxSizer(wx.VERTICAL)
        sizerP1RightTop= wx.StaticBoxSizer(self.frame_equipment_data, wx.VERTICAL)
        sizerP1RightTop.Add(self.tc101, 0, flagText, VSEP_RIGHT)
        sizerP1RightTop.Add(self.tc102, 0, flagText, VSEP_RIGHT)
        sizerP1RightTop.Add(self.tc103, 0, flagText, VSEP_RIGHT)
        sizerP1RightTop.Add(self.tc104, 0, flagText, VSEP_RIGHT)
        sizerP1RightTop.Add(self.tc105, 0, flagText, VSEP_RIGHT)
        sizerP1RightTop.Add(self.tc106, 0, flagText, VSEP_RIGHT)
        sizerP1RightTop.Add(self.tc107, 0, flagText, VSEP_RIGHT)
        sizerP1RightTop.Add(self.tc108, 0, flagText, VSEP_RIGHT)
        sizerP1Right.Add(sizerP1RightTop,8,wx.EXPAND|wx.TOP,0)
        
        sizerP1RightBottom= wx.StaticBoxSizer(self.frame_schedule, wx.VERTICAL)
        sizerP1RightBottom.Add(self.tc110, 0, flagText, VSEP_RIGHT)
        sizerP1RightBottom.Add(self.tc111, 0, flagText, VSEP_RIGHT)
        sizerP1RightBottom.Add(self.tc112, 0, flagText, VSEP_RIGHT)
        sizerP1RightBottom.Add(self.tc113, 0, flagText, VSEP_RIGHT)
        sizerP1Right.Add(sizerP1RightBottom,4,wx.EXPAND|wx.TOP,0)
        sizerPage1.Add(sizerP1Right,5,wx.EXPAND|wx.TOP,10)

        self.page1.SetSizer(sizerPage1)

        sizerOKCancel = wx.BoxSizer(wx.HORIZONTAL)
        sizerOKCancel.Add(self.buttonCancel, 0, wx.ALL|wx.EXPAND, 2)
        sizerOKCancel.Add(self.buttonOK, 0, wx.ALL|wx.EXPAND, 2)

        sizerGlobal.Add(self.notebook, 3, wx.EXPAND, 0)
        sizerGlobal.Add(sizerOKCancel, 0, wx.TOP|wx.ALIGN_RIGHT, 0)
        self.SetSizer(sizerGlobal)
        self.Layout()

    def SinkSourceLayOut(self, page, target):
        sizer = wx.BoxSizer(wx.VERTICAL)
        page.SetSizer(sizer)

        sizerStream = wx.FlexGridSizer(1, 5, 3, 5)
        sizerStream.AddMany( [(target.txtStream, 2, wx.EXPAND),
            (target.cbStreamType, 2, wx.EXPAND),
            (target.cbStream, 3, wx.EXPAND),
            (target.buttonAdd, 1, wx.EXPAND),
            (target.buttonDelete, 1, wx.EXPAND) ])

        target.tbPercentHeatFlow.SetValue("100")

        self.Bind(wx.EVT_BUTTON, self.OnButtonAdd, target.buttonAdd)
        self.Bind(wx.EVT_BUTTON, self.OnButtonDelete, target.buttonDelete)
        self.Bind(wx.EVT_COMBOBOX, self.OnCBStreamTypeChange, target.cbStreamType)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRBInletChoiceChange, target.rbInletTemp)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRBInletChoiceChange, target.rbInletHX)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRBOutletChoiceChange, target.rbOutletTemp)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRBOutletChoiceChange, target.rbOutletHX)
        self.Bind(wx.EVT_LISTBOX, self.OnListBoxSinkSourceClick, target.listBox)
        self.Bind(wx.EVT_TEXT, self.OnTempInletChange, target.inletTemp)
        self.Bind(wx.EVT_TEXT, self.OnTempOutletChange, target.outletTemp)
        self.Bind(wx.EVT_TEXT, self.OnPercentHeatFlowChange, target.tbPercentHeatFlow)
        self.Bind(wx.EVT_COMBOBOX, self.OnCBHXOutletChange, target.outletHXChoice)
        self.Bind(wx.EVT_COMBOBOX, self.OnCBHXInletChange, target.inletHXChoice)

        sizerBoxTemp = wx.StaticBoxSizer(target.frame_temp, wx.HORIZONTAL)
        sizerBoxInlet= wx.StaticBoxSizer(target.frame_inlet, wx.VERTICAL)
        sizerBoxOutlet= wx.StaticBoxSizer(target.frame_outlet, wx.VERTICAL)
        sizerBoxHeatFlow = wx.StaticBoxSizer(target.frame_heatflow, wx.VERTICAL)

        sizerGridInlet = wx.GridSizer(2,2,2,2)
        sizerGridOutlet = wx.GridSizer(2,2,2,2)
        sizerGridHeatFlow = wx.GridSizer(1,2,2,2)

        sizerGridInlet.AddMany( [(target.rbInletTemp, 0, wx.EXPAND),
            (target.inletTemp, 0, wx.EXPAND),
            (target.rbInletHX, 0, wx.EXPAND),
            (target.outletHXChoice, 0, wx.EXPAND)])

        sizerGridOutlet.AddMany( [(target.rbOutletTemp, 0, wx.EXPAND),
            (target.outletTemp, 0, wx.EXPAND),
            (target.rbOutletHX, 0, wx.EXPAND),
            (target.inletHXChoice, 0, wx.EXPAND)])

        # Basis deactivate
        target.outletHXChoice.Disable()
        target.inletHXChoice.Disable()

        sizerGridHeatFlow.AddMany([(target.txtPercentHeatFlow, 0, wx.EXPAND),
            (target.tbPercentHeatFlow, 0, wx.EXPAND)])

        sizerBoxInlet.Add(sizerGridInlet, 0)
        sizerBoxOutlet.Add(sizerGridOutlet, 0)
        sizerBoxHeatFlow.Add(sizerGridHeatFlow, 0, wx.EXPAND)

        sizerTemp = wx.BoxSizer(wx.HORIZONTAL)
        sizerRB = wx.BoxSizer(wx.VERTICAL)
        sizerRB.Add(sizerBoxInlet, 0)
        sizerRB.Add(sizerBoxOutlet, 0)
        sizerRB.Add(sizerBoxHeatFlow, 0, wx.EXPAND)

        sizerTemp.Add(target.listBox, 1, wx.EXPAND|wx.ALL, VSEP_RIGHT)
        sizerTemp.Add(sizerRB, 0, wx.ALL, VSEP_RIGHT)

        sizer.Add(sizerStream, 0, wx.EXPAND|wx.ALL|wx.ALIGN_RIGHT, VSEP_RIGHT)
        sizer.Add(sizerTemp, 0, wx.EXPAND)



#------------------------------------------------------------------------------
# GUI actions - 0. OK/Cancel buttons
#------------------------------------------------------------------------------		

    def OnButtonCancel(self, event):
        if self.notebook.GetSelection()==0:
            self.clearHX()
        else:
            self.clearWHEE()
            
    def OnButtonOK(self, event):
        if self.notebook.GetSelection()==0:
            self.OnButtonHXOK(event)
        else:
            self.OnButtonWHEEOK(event)

        for elem in Status.int.HXPinchConnection:
            if elem.HXID == self.HXID:
                pass

        stype = self.getActiveTab()
        sstream = self.getActiveStreamType()

        if sstream == None:
            return 

        id = self.selectedSStream
        if id != None and id != -1 and id <= stype.listBox.GetCount()-1:
            if stype.rbInletTemp.GetValue():
                sstream[self.selectedSStream].InTempActive = True
            else: sstream[self.selectedSStream].InTempActive = False

            if stype.rbOutletTemp.GetValue():
                sstream[self.selectedSStream].OutTempActive = True
            else: sstream[self.selectedSStream].OutTempActive = False
            
#        for elem in Status.int.HXPinchConnection:
#            for el in elem.sinkstreams:
#                loadStreamData(el.stream)
#            for el in elem.sourcestreams:
#                loadStreamData(el.stream)

        for elem in Status.int.HXPinchConnection:
            elem.deleteFromDB()
            
#        Status.int.NameGen.calcStreams()
#        Status.int.NameGen.printStreams()

        for elem in Status.int.HXPinchConnection:
            elem.writeToDB()




#------------------------------------------------------------------------------
# GUI actions - 1. Heat exchanger page
#------------------------------------------------------------------------------		
    def OnNBSinkSourceChange(self, event):
        if self.SinkActive:
            self.SinkActive = False
        else:
            self.SinkActive = True

    def OnRBInletChoiceChange(self, event):

        stype = self.getActiveTab()

        if stype.rbInletTemp.GetValue():
            stype.inletTemp.Enable()
            stype.outletHXChoice.Disable()
#            stype.outletHXChoice.SetValue('')
        elif stype.rbInletHX.GetValue():
            stype.inletTemp.Disable()
#            stype.inletTemp.SetValue('')
            stype.outletHXChoice.Enable()

    def getActiveTab(self):
        if self.SinkActive:
            return self.Sink
        else:
            return self.Source


    def OnRBOutletChoiceChange(self, event):
        stype = self.getActiveTab()

        if stype.rbOutletTemp.GetValue():
            stype.outletTemp.Enable()
            stype.inletHXChoice.Disable()
#            stype.inletHXChoice.SetValue('')
        elif stype.rbOutletHX.GetValue():
            stype.outletTemp.Disable()
#            stype.outletTemp.SetValue('')
            stype.inletHXChoice.Enable()



    def OnCBStreamTypeChange(self, event):

        stype = self.getActiveTab()

        self.Sink.cbStream.Clear()
        self.Source.cbStream.Clear()

        streamType = stype.cbStreamType.GetValue()

        if streamType == 'Processes':
            self.appendStreamNames(Status.int.NameGen.process.streams, stype)
            #self.appendStreamNames(Status.int.NameGen.process.processContStreams)
        elif streamType == 'Distribution Lines':
            self.appendStreamNames(Status.int.NameGen.distline.streams, stype)
        elif streamType == 'WHEE':
            self.appendStreamNames(Status.int.NameGen.whee.streams, stype)
        elif streamType == 'Equipments':
            self.appendStreamNames(Status.int.NameGen.equipment.streams, stype)

    def appendStreamNames(self, streamList, stype):
        for el in streamList:
            if el.HotColdType == 'Cold' or el.HotColdType == 'Sink':
                self.Sink.cbStream.Append(el.name, self.Sink)
            elif el.HotColdType == 'Hot' or el.HotColdType == 'Source':
                self.Source.cbStream.Append(el.name, self.Source)


    def OnButtonAdd(self, event):
        if self.HXPinch == None:
            return
        stype = self.getActiveTab()

        selectedType = stype.cbStreamType.GetStringSelection()
        selectedStream = stype.cbStream.GetStringSelection()

        streamList = Status.int.NameGen.process.streams + \
                     Status.int.NameGen.distline.streams + \
                     Status.int.NameGen.equipment.streams + \
                     Status.int.NameGen.whee.streams
        pinch = pinchTemp()
        for elem in streamList:
            if elem.name == selectedStream:
                pinch.stream = elem
                if elem.HotColdType == 'Cold' or elem.HotColdType == 'Sink':
                    self.HXPinch.sinkstreams.append(pinch)
                elif elem.HotColdType == 'Hot' or elem.HotColdType == 'Source':
                    self.HXPinch.sourcestreams.append(pinch)
                stype.listBox.Append(elem.name)

    def OnButtonDelete(self, event):
        if self.HXPinch == None:
            return
        stype = self.getActiveTab()
        sstream = self.getActiveStreamType()

        if stype.listBox.GetSelection() < 0:
            return

        del sstream[stype.listBox.GetSelection()]
        stype.listBox.Delete(stype.listBox.GetSelection())
        self.setStreamChoiceEmpty(stype)

    def setStreamChoiceEmpty(self, stype):
        stype.inletTemp.SetValue('')
        stype.outletTemp.SetValue('')
        stype.inletHXChoice.SetSelection(-1)
        stype.outletHXChoice.SetSelection(-1)

    def getActiveStreamType(self):
        if self.HXPinch == None:
            return None
        if self.SinkActive:
            return self.HXPinch.sinkstreams
        else:
            return self.HXPinch.sourcestreams

    def printSinkSourceChange(self):
        list = []
        for elem in Status.int.HXPinchConnection:
             list.append(["HXID:", elem.HXID, "inTSink:", elem.sinkstreams[0].inletTemp, "outTSink:", elem.sinkstreams[0].outletTemp])
             list.append(["inTSink:", elem.sourcestreams[0].inletTemp, "outTSink:", elem.sourcestreams[0].outletTemp])
        print list
             
    def OnListBoxSinkSourceClick(self, event):

        stype = self.getActiveTab()
        sstream = self.getActiveStreamType()
        self.selectedSStream = ids = stype.listBox.GetSelection()
        if ids != None and ids != -1 and ids <= stype.listBox.GetCount()-1:
            if stype.rbInletTemp.GetValue():
                sstream[self.selectedSStream].InTempActive = True
            else: sstream[self.selectedSStream].InTempActive = False

            if stype.rbOutletTemp.GetValue():
                sstream[self.selectedSStream].OutTempActive = True
            else: sstream[self.selectedSStream].OutTempActive = False

        id = stype.listBox.GetSelection()

        if sstream[id].InTempActive:
            stype.inletTemp.Enable()
            stype.outletHXChoice.Disable()
        elif not sstream[id].InTempActive:
            stype.inletTemp.Disable()
            stype.outletHXChoice.Enable()
        else:
            stype.inletTemp.Enable()
            stype.outletHXChoice.Disable()

        if sstream[id].OutTempActive:
            stype.outletTemp.Enable()
            stype.inletHXChoice.Disable()
        elif not sstream[id].OutTempActive:
            stype.outletTemp.Disable()
            stype.inletHXChoice.Enable()
        else:
            stype.outletTemp.Enable()
            stype.inletHXChoice.Disable()
            
        stype.enableTempEntry()


        if sstream[id].inletTemp == None:
            stype.inletTemp.SetValue('')
        else: stype.inletTemp.SetValue(str(sstream[id].inletTemp))

        if sstream[id].outletTemp == None:
            stype.outletTemp.SetValue('')
        else: stype.outletTemp.SetValue(str(sstream[id].outletTemp))

        if sstream[id].percentHeatFlow == None:
            stype.tbPercentHeatFlow.SetValue('100')
        else: stype.tbPercentHeatFlow.SetValue(str(sstream[id].percentHeatFlow))

        if sstream[id].inletHX == None:
            stype.inletHXChoice.SetSelection(-1)
#            print sstream[id].inletHX
        else:
            stype.inletHXChoice.SetStringSelection(self.getHXName(sstream[id].inletHX))
#            print sstream[id].inletHX

        if sstream[id].outletHX == None:
            stype.outletHXChoice.SetSelection(-1)
#            print sstream[id].outletHX
        else:
            stype.outletHXChoice.SetStringSelection(self.getHXName(sstream[id].outletHX))
#            print sstream[id].outletHX


    def setTempValues(self, stype, sstream):
        pass

    def activateSinkSource(self):
        pass

    def activateTempEntry(self, stype):
        pass

    def OnListBoxHXListboxClick(self, event):

        self.HXName = self.listBoxHX.GetStringSelection()
        if self.HXName in self.HXList:
            self.HXNo = self.HXList.index(self.HXName)+1
        else:
            self.HXNo = None

        self.display()

        self.HXPinch = None
        for elem in Status.int.HXPinchConnection:
            if self.HXID == elem.HXID:
                self.HXPinch = elem
                break

        if self.HXPinch == None:
            self.HXPinch = HXPinchConnection(self.HXID)
            Status.int.HXPinchConnection.append(self.HXPinch)

        self.Sink.outletHXChoice.Clear()
        self.Sink.inletHXChoice.Clear()
        self.Source.outletHXChoice.Clear()
        self.Source.inletHXChoice.Clear()

        try:
            HXPinchList = copy.deepcopy(self.HXList)
            HXPinchList.remove(self.HXName)

            for elem in HXPinchList:
                self.Sink.outletHXChoice.Append(elem)
                self.Sink.inletHXChoice.Append(elem)
                self.Source.outletHXChoice.Append(elem)
                self.Source.inletHXChoice.Append(elem)
        except:
            #HXPinchList = self.HXList
            pass
        self.loadOnHXChange(self.Sink, self.HXPinch.sinkstreams)
        self.loadOnHXChange(self.Source, self.HXPinch.sourcestreams)


    def loadOnHXChange(self, stype, sstream):
        stype.disableTempEntry()
        stype.disabledTempEntry = True
        stype.listBox.Clear()
        stype.cbStream.Clear()
        stype.cbStreamType.SetSelection(-1)
        self.temperatureIsChanged = True
        stype.inletTemp.SetValue('')
        stype.outletTemp.SetValue('')
        self.temperatureIsChanged = False
        stype.tbPercentHeatFlow.SetValue('')
        stype.outletHXChoice.SetSelection(-1)
        stype.inletHXChoice.SetSelection(-1)
        for elem in sstream:
            stype.listBox.Append(elem.stream.name)

    def OnTempInletChange(self, event):
        if not self.temperatureIsChanged:
            stype = self.getActiveTab()
            sstream = self.getActiveStreamType()
            id = stype.listBox.GetSelection()
            if id != -1:
                if stype.inletTemp.GetValue() != '':
                    sstream[id].inletTemp = float(stype.inletTemp.GetValue())
                else:
                    sstream[id].inletTemp = stype.inletTemp.GetValue()
    #                sstream[id].outletHX = self.getHXID(stype.outletHXChoice.GetStringSelection())
            
    def OnTempOutletChange(self, event):
        if not self.temperatureIsChanged:
            stype = self.getActiveTab()
            sstream = self.getActiveStreamType()
            id = stype.listBox.GetSelection()
            if id != -1:
                if stype.outletTemp.GetValue() != '':
                    sstream[id].outletTemp = float(stype.outletTemp.GetValue())
                else:
                    sstream[id].outletTemp = stype.outletTemp.GetValue()
#                sstream[id].inletHX = self.getHXID(stype.inletHXChoice.GetStringSelection())

    def OnPercentHeatFlowChange(self, event):
        stype = self.getActiveTab()
        sstream = self.getActiveStreamType()
        id = stype.listBox.GetSelection()
        if id != -1:
            if stype.tbPercentHeatFlow.GetValue() != '':
                sstream[id].percentHeatFlow = float(stype.tbPercentHeatFlow.GetValue())
            else:
                sstream[id].percentHeatFlow = stype.tbPercentHeatFlow.GetValue()
                
    def OnCBHXOutletChange(self, event):
        stype = self.getActiveTab()
        sstream = self.getActiveStreamType()
        selectedHX = stype.outletHXChoice.GetStringSelection()
        id = stype.listBox.GetSelection()
        if id != -1:
            sstream[id].outletHX = float(self.getHXID(selectedHX))
#            sstream[id].inletTemp = stype.inletTemp.GetValue()

    def OnCBHXInletChange(self, event):
        stype = self.getActiveTab()
        sstream = self.getActiveStreamType()
        selectedHX = stype.inletHXChoice.GetStringSelection()
        id = stype.listBox.GetSelection()
        if id != -1:
            sstream[id].inletHX = int(self.getHXID(selectedHX))
#            sstream[id].outletTemp = stype.outletTemp.GetValue()

    def getHXID(self, HXName):
        HX = Status.prj.getHXes()
        for hx in HX:
            if HXName == hx['HXName']:
                return hx['QHeatExchanger_ID']

    def getHXName(self, HXID):
        
        if HXID == '': return ''
        if HXID == None: return ''
        HX = Status.prj.getHXes()
        for hx in HX:
            if HXID == hx['QHeatExchanger_ID']:
                return str(hx['HXName'])
        return ''

    def OnHeatSourceChoice(self, event):
        # FIXME: HERE I LEFT
        getProcessIdByName()
        fillChoice(self.tc6_1.entry,getInflowingStreamNamesFromDB(processId))

    def OnButtonHXAdd(self, event):
        self.clearHX()

    def OnButtonHXDelete(self, event):
        Status.prj.deleteHX(self.HXID)
        self.setStreamChoiceEmpty(self.getActiveTab())
        self.getActiveTab().listBox.Clear()
        self.clearHX()
        self.fillPage()
        event.Skip()

    def OnButtonHXOK(self, event):
        hxName = self.tc1.GetValue()

# assure that a name has been entered before continuing
        if len(hxName) == 0 or hxName is None:
            showWarning(_("You have to enter a name for the new heat exchanger before saving"))
            return

        hxes = Status.DB.qheatexchanger.HXName[check(hxName)].ProjectID[Status.PId].AlternativeProposalNo[Status.ANo]
	if len(hxes) == 0:
            hx = Status.prj.addHXDummy()
            self.HXName = hxName
        elif len(hxes) == 1:
            hx = hxes[0]
        else:
	    showError("HX name has to be a uniqe value!")
	    return
        
        tmp = {
            "HXName":check(self.tc1.GetValue()),
            "HXType":check(findKey(Status.TRANS.HXTYPES,self.tc2.GetValue(text=True))),
            "QdotHX":check(self.tc3.GetValue()), 
            "HXLMTD":check(self.tc4.GetValue()), 
            "QHX":check(self.tc5.GetValue()), 
            "UA":check(self.tcUA.GetValue())
#            "HXSource":check(self.tc6.GetValue(text=True)),
#            "HXTSourceInlet":check(self.tc7.GetValue()),
#            "HXhSourceInlet":check(self.tc8.GetValue()),
#            "HXTSourceOutlet":check(self.tc9.GetValue()),
#            "HXhSourceOutlet":check(self.tc10.GetValue()),
#            "HXSink":check(self.tc11.GetValue(text=True)),
#            "HXTSinkInlet":check(self.tc12.GetValue()),
#            "HXTSinkOutlet":check(self.tc13.GetValue()),
            }
        
        hx.update(tmp)
        
        Status.SQL.commit()
        self.display()

                          
#------------------------------------------------------------------------------
# GUI actions - 2. WHEE page
#------------------------------------------------------------------------------		


    def OnListBoxWHEEListboxClick(self, event):
        self.WHEEName = self.listBoxWHEE.GetStringSelection()
        if self.WHEEName in self.WHEEList:
            self.WHEENo = self.WHEEList.index(self.WHEEName)+1
        else:
            self.WHEENo = None

        self.display()
        
    def OnButtonWHEEAdd(self, event):
        self.clearWHEE()

    def OnButtonWHEEDelete(self, event):
        Status.prj.deleteWHEE(self.WHEEID)
        self.clearWHEE()
        self.fillPage()
        event.Skip()

    def OnButtonWHEEOK(self, event):
        wheeName = self.tc101.GetValue()

# assure that a name has been entered before continuing
        if len(wheeName) == 0 or wheeName is None:
            showWarning(_("You have to enter a name for the new equipment before saving"))
            return

        whees = Status.DB.qwasteheatelequip.WHEEName[check(wheeName)].ProjectID[Status.PId].AlternativeProposalNo[Status.ANo]
	if len(whees) == 0:
            whee = Status.prj.addWHEEDummy()
            self.WHEEName = wheeName
        elif len(whees) == 1:
            whee = whees[0]
        else:
	    showError("Name has to be a uniqe value!")
	    return
	
        fluidDict = Status.prj.getFluidDict()
                        
        tmp = {
            "WHEEName":check(self.tc101.GetValue()),
            "WHEEEqType":check(findKey(TRANSWHEEEQTYPES,self.tc102.GetValue(text=True))),
            "WHEEWasteHeatType":check(findKey(TRANSWHEEWASTEHEATTYPES,self.tc103.GetValue(text=True))),
            "QWHEE":check(self.tc104.GetValue()), 
            "WHEEMedium":check(findKey(fluidDict,self.tc105.GetValue(text=True))),
            "WHEEFlow":check(self.tc106.GetValue()), 
            "WHEETOutlet":check(self.tc107.GetValue()),
            
            "WHEEPresentUse":check(findKey(TRANSYESNO,self.tc108.GetValue(text=True))),
            
            "HPerDayWHEE":check(self.tc110.GetValue()), 
            "NBatchWHEE":check(self.tc111.GetValue()), 
            "HBatchWHEE":check(self.tc112.GetValue()), 
            "NDaysWHEE":check(self.tc113.GetValue()), 
            }
        
        whee.update(tmp)
        
        Status.SQL.commit()
        self.display()

#------------------------------------------------------------------------------
    def fillPage(self):
#------------------------------------------------------------------------------
#   screens the SQL tables and fills the lists of HX's and WHEE's
#------------------------------------------------------------------------------
        self.HXList = Status.prj.getHXList("HXName")

        self.listBoxHX.Clear()
        for hx in self.HXList:
            self.listBoxHX.Append(hx)

        if self.HXName is not None:
            self.listBoxHX.SetStringSelection(self.HXName)

        self.WHEEList = Status.prj.getWHEEList("WHEEName")

        self.listBoxWHEE.Clear()
        for whee in self.WHEEList:
            self.listBoxWHEE.Append(whee)

        if self.WHEEName is not None: self.listBoxWHEE.SetStringSelection(self.WHEEName)

        fillChoice(self.tc2.entry,Status.TRANS.HXTYPES.values())

        self.sourceList = Status.prj.getEquipmentList("Equipment")
        self.sourceList.extend(Status.prj.getPipeList("Pipeduct"))
        self.sourceList.extend(Status.prj.getProcessList("Process"))
        self.sourceList.extend(Status.prj.getWHEEList("WHEEName"))
        
#        fillChoice(self.tc6.entry,self.sourceList)

        self.sinkList = Status.prj.getEquipmentList("Equipment")
        self.sinkList.extend(Status.prj.getPipeList("Pipeduct"))
        self.sinkList.extend(Status.prj.getProcessList("Process"))
        
#        fillChoice(self.tc11.entry,self.sinkList)

        fluidDict = Status.prj.getFluidDict()
        self.tc105.SetValue(fluidDict.values())


#.............................................................................
# heat exchanger data
        hxes = Status.DB.qheatexchanger.\
               ProjectID[Status.PId].\
               AlternativeProposalNo[Status.ANo].\
               HXName[check(self.HXName)]

        if len(hxes) <>0:
            q = hxes[0]
            self.HXID = q.QHeatExchanger_ID
            
            self.tc1.SetValue(q.HXName)

            if str(q.HXType) in Status.TRANS.HXTYPES.keys():
                self.tc2.SetValue(TRANSHXTYPES[str(q.HXType)])
                
            self.tc3.SetValue(str(q.QdotHX))
            self.tc4.SetValue(str(q.HXLMTD))
            self.tc5.SetValue(str(q.QHX))
            self.tcUA.SetValue(str(q.UA))
            if q.HXSource is not None:
                hxsource = unicode(q.HXSource,"utf-8")
#                if hxsource in self.sourceList: self.tc6.SetValue(hxsource)
#
#            self.tc7.SetValue(str(q.HXTSourceInlet))
#            self.tc8.SetValue(str(q.HXhSourceInlet))
#            self.tc9.SetValue(str(q.HXTSourceOutlet))
#            self.tc10.SetValue(str(q.HXhSourceOutlet))
#
#            if q.HXSink is not None:
#                hxsink = unicode(q.HXSink,"utf-8")
#                if hxsink in self.sinkList: self.tc11.SetValue(hxsink)
#
#            self.tc12.SetValue(str(q.HXTSinkInlet))
#            self.tc13.SetValue(str(q.HXTSinkOutlet))


#.............................................................................
# WHEE data

        whees = Status.DB.qwasteheatelequip.\
                ProjectID[Status.PId].\
                AlternativeProposalNo[Status.ANo].\
                WHEEName[check(self.WHEEName)]

        if len(whees) <>0:
            q = whees[0]
            self.WHEEID = q.QWasteHeatElEquip_ID
        
            self.tc101.SetValue(q.WHEEName)
            
            if str(q.WHEEEqType) in TRANSWHEEEQTYPES.keys():
                self.tc102.SetValue(TRANSWHEEEQTYPES[q.WHEEEqType])
                
            if str(q.WHEEWasteHeatType) in TRANSWHEEWASTEHEATTYPES.keys():
                self.tc103.SetValue(TRANSWHEEWASTEHEATTYPES[str(q.WHEEWasteHeatType)])
                
            self.tc104.SetValue(str(q.QWHEE))
            
            fluidDict = Status.prj.getFluidDict()

            if q.WHEEMedium is not None:
                WHEEMediumID = int(q.WHEEMedium)
            else:
                WHEEMediumID = None
                
            if WHEEMediumID in fluidDict.keys():
                fluidName = fluidDict[WHEEMediumID]
                self.tc105.SetValue(fluidName)
            else:
                self.tc105.SetValue("None")
                
            setUnitsFluidDensity(q.WHEEMedium)
                
            self.tc106.SetValue(str(q.WHEEFlow))
            self.tc107.SetValue(str(q.WHEETOutlet))
            
            if str(q.WHEEPresentUse) in TRANSYESNO.keys():
                self.tc108.SetValue(TRANSYESNO[str(q.WHEEPresentUse)])

            self.tc110.SetValue(str(q.HPerDayWHEE))
            self.tc111.SetValue(str(q.NBatchWHEE))
            self.tc112.SetValue(str(q.HBatchWHEE))
            self.tc113.SetValue(str(q.NDaysWHEE))
        
#------------------------------------------------------------------------------

    def display(self):
        self.clear()
        self.fillPage()
        self.Show()

    def clear(self):
        self.clearHX()
        self.clearWHEE()

    def clearHX(self):
        self.tc1.SetValue('')
#        self.tc2.SetValue('')
        self.tc3.SetValue('')
        self.tc4.SetValue('')
        self.tc5.SetValue('')
        self.tcUA.SetValue('')
#        self.tc6.SetValue('')
#        self.tc7.SetValue('')
#        self.tc8.SetValue('')
#        self.tc9.SetValue('')
#        self.tc10.SetValue('')
##        self.tc11.SetValue('')
#        self.tc12.SetValue('')
#        self.tc13.SetValue('')

    def clearWHEE(self):
        self.tc101.SetValue('')
#        self.tc102.SetValue('')
#        self.tc103.SetValue('')
        self.tc104.SetValue('')
#        self.tc105.SetValue('')
        self.tc106.SetValue('')
        self.tc107.SetValue('')
#        self.tc108.SetValue('')

        self.tc110.SetValue('')
        self.tc111.SetValue('')
        self.tc112.SetValue('')
        self.tc113.SetValue('')

        
#==============================================================================

        
