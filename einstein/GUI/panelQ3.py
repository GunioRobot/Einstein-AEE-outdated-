# -*- coding: utf-8 -*-
#==============================================================================
#
#	E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (<a href="http://www.iee-einstein.org/" target="_blank">www.iee-einstein.org</a>)
#
#------------------------------------------------------------------------------
#
#	PanelQ3: Process data
#
#==============================================================================
#
#   EINSTEIN Version No.: 1.0
#   Created by: 	Heiko Henning, Tom Sobota, Hans Schweiger, Stoyan Danov
#                       February 2008 - 13/10/2008
#
#   Update No. 001
#
#   Since Version 1.0 revised by:
#                       Hans Schweiger      01/04/2009
#                       David Baehrens      20/04/2010
#
#       Changes to previous version:
#       01/04/2009: HS  impossibility to save entries with empty name field
#       20/04/2010: DB  Detailed schedules
#
#------------------------------------------------------------------------------
#	(C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008,2009,2010
#	http://www.energyxperts.net/
#
#	This program is free software: you can redistribute it or modify it under
#	the terms of the GNU general public license as published by the Free
#	Software Foundation (www.gnu.org).
#
#==============================================================================
import wx
import wx.xrc
import os
import pSQL
from datetime import *
from status import Status
from GUITools import *
from units import *
from displayClasses import *
from fonts import *
from matplotlib.mlab import linspace
from einstein.modules.messageLogger import *
from einstein.modules.processes import originalProcessId
from einstein.modules.profiles import *
from einstein.modules.schedules import *
from einstein.modules.streams import *
from einstein.modules.matPanel import MatPanel

# constants that control the default sizes
# 1. font sizes
TYPE_SIZE_LEFT    =   9
TYPE_SIZE_RIGHT   =   9
TYPE_SIZE_TITLES  =  10

# 2. field sizes
HEIGHT_LEFT        =  29
LABEL_WIDTH_LEFT   = 260
HEIGHT_RIGHT       =  26
LABEL_WIDTH_RIGHT  = 400
DATA_ENTRY_WIDTH   = 100
UNITS_WIDTH        = 100

ENCODING = "latin-1"
def _U(text):
    return unicode(_(text), "utf-8")

def GetSelectedItems(listCtrl):
    selectedItemIndex = []
    index = listCtrl.GetFirstSelected()
    while index != -1:
        selectedItemIndex.append(index)
        index = listCtrl.GetNextSelected(index)
    return selectedItemIndex

#------------------------------------------------------------------------------        
def drawFigure(self):
#------------------------------------------------------------------------------
#   defines the figures to be plotted
#------------------------------------------------------------------------------        

    #AXIS_FONT = {'fontsize'  : 6}
    resolution = 10

    if hasattr(self, 'subplot'):
        del self.subplot
    self.subplot = self.figure.add_subplot(1, 1, 1)
    self.subplot.plot(linspace(0, int(WEEK), resolution * int(WEEK)), graphSquareFromSaw(resolution, Status.int.GData['SchedulePeriodWeeklyProfile']), 'b-')
    #self.subplot.plot(Status.int.GData['EA4b_Plot'][0],
    #                  Status.int.GData['EA4b_Plot'][2],
    #                  color = ORANGE, label='UPH proc', linewidth=3)
    #self.subplot.plot(Status.int.GData['EA4b_Plot'][0],
    #                  Status.int.GData['EA4b_Plot'][3],
    #                  'r:',  label='USH', linewidth=3)

    self.subplot.axis([0, int(WEEK), 0, 1.2])
    #self.subplot.legend(loc = 2)
    self.subplot.axes.set_ylabel(_U('Load'), fontsize=8)
    self.subplot.axes.set_xlabel(_U('Hour of week'), fontsize=8)
    
    for label in self.subplot.axes.get_yticklabels():
        #label.set_color(self.params['ytickscolor'])
        label.set_fontsize(6)
        #label.set_rotation(self.params['yticksangle'])
    #
    # properties of labels on the x axis
    #
    for label in self.subplot.axes.get_xticklabels():
        #label.set_color(self.params['xtickscolor'])
        label.set_fontsize(6)
        #label.set_rotation(self.params['xticksangle'])

    try:
        lg = self.subplot.get_legend()
        ltext  = lg.get_texts()             # all the text.Text instance in the legend
        for txt in ltext:
            txt.set_fontsize(6)  # the legend text fontsize
        # legend line thickness
        llines = lg.get_lines()             # all the lines.Line2D instance in the legend
        for lli in llines:
            lli.set_linewidth(1.5)          # the legend linewidth
        # color of the legend frame
        # this only works when the frame is painted (see below draw_frame)
        frame  = lg.get_frame()             # the patch.Rectangle instance surrounding the legend
        frame.set_facecolor('#F0F0F0')      # set the frame face color to light gray
        # should the legend frame be painted
        lg.draw_frame(False)
    except:
        # no legend
        pass

class PanelQ3(wx.Panel):
    def __init__(self, parent, main):
        self.main = main
        self._init_ctrls(parent)
        self.__do_layout()
        self.selectedProcessName = None

    def _init_ctrls(self, parent):

#------------------------------------------------------------------------------
#--- UI setup
#------------------------------------------------------------------------------

        wx.Panel.__init__(self, id= -1, name='PanelQ3', parent=parent,
              pos=wx.Point(0, 0), size=wx.Size(780, 580), style=0)
        self.Hide()

        # access to font properties object
        fp = FontProperties()

        self.notebook = wx.Notebook(self, -1, style=0)
        self.notebook.SetFont(fp.getFont())

        # Process schedule
        self.xrcSchedule = wx.xrc.XmlResource('Schedule.xrc')
        # Input/output streams
        self.xrcStreams  = wx.xrc.XmlResource('Streams.xrc')
        
        self.page0 = wx.Panel(self.notebook)
        self.page1 = self.xrcSchedule.LoadPanel(self.notebook, 'OperationPanel')
        self.page2 = self.xrcSchedule.LoadPanel(self.notebook, 'ProfilePanel')
        self.page3 = self.xrcSchedule.LoadPanel(self.notebook, 'SchedulePanel')
        self.page4 = wx.Panel(self.notebook)
        self.page5 = wx.Panel(self.notebook)
        self.page6 = self.xrcStreams.LoadPanel(self.notebook, 'InputStreamsPanel')
        self.page7 = self.xrcStreams.LoadPanel(self.notebook, 'OutputStreamsPanel')
        self.scheduleNotebookPageIndex = 3
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChanged, self.notebook)
        
        
        self.sizer_5_staticbox = wx.StaticBox(self.page0, -1, _U("Process list"))
        self.sizer_5_staticbox.SetForegroundColour(TITLE_COLOR)
        self.sizer_5_staticbox.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.sizer_7_staticbox = wx.StaticBox(self.page0, -1, _U("Processes description"))
        self.sizer_7_staticbox.SetForegroundColour(TITLE_COLOR)
        self.sizer_7_staticbox.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.sizer_13_staticbox = wx.StaticBox(self.page4, -1,
                                               _U("Data of existing heat (or cold) supply to the process"))
        self.sizer_13_staticbox.SetForegroundColour(TITLE_COLOR)
        self.sizer_13_staticbox.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        # set font for titles
        # 1. save actual font parameters on the stack
        fp.pushFont()
        # 2. change size and weight
        fp.changeFont(size=TYPE_SIZE_TITLES, weight=wx.BOLD)
        self.sizer_5_staticbox.SetFont(fp.getFont())
        self.sizer_7_staticbox.SetFont(fp.getFont())
        self.sizer_13_staticbox.SetFont(fp.getFont())
        # 3. recover previous font state
        fp.popFont()

        # set field sizes for the left tab.
        # Each data entry class has several configurable parameters:
        # 1. The height. This is the same for all the widgets that make the class
        # 2. The width of the label
        # 3. The width of the entry widget
        # 4. The width of the unit chooser.
        #
        fs = FieldSizes(wHeight=HEIGHT_LEFT, wLabel=LABEL_WIDTH_LEFT,
                       wData=DATA_ENTRY_WIDTH, wUnits=UNITS_WIDTH)

        # set font for labels of left tab
        fp.pushFont()
        fp.changeFont(size=TYPE_SIZE_LEFT)

        #
        # left panel controls
        #

        # process list
        self.listBoxProcesses = wx.ListBox(self.page0, -1, choices=[])
        self.listBoxProcesses.SetFont(fp.getFont())
        self.Bind(wx.EVT_LISTBOX, self.OnListBoxProcessesClick, self.listBoxProcesses)

        p1 = wx.StaticBitmap(bitmap=wx.Bitmap(os.path.join('img', 'Q3.png'),
                                             wx.BITMAP_TYPE_PNG),
                                             id= -1,
                                             parent=self.page5,
                                             pos=wx.Point(0, 0),
                                             size=wx.Size(800, 600),
                                             style=wx.SUNKEN_BORDER)
        # Processes description
        #
        self.tc1 = TextEntry(self.page0, maxchars=255, value='',
                             label=_U("Process short name"),
                             tip=_U("Give an organizational diagram of the production process (e.g. the flux of crude milk in chease production or the the flux of car chasis in the automobile industry)"))
        self.tc1_1 = TextEntry(self.page0, maxchars=200, value='',
                             label=_U("Description"),
                             tip=_U("Give a short description of the process"))
        self.tc2 = ChoiceEntry(self.page0,
                               values=TRANSPROCTYPES.values(),
                               label=_U("Process type"),
                               tip=_U("Give a brief description of the process or the unitary operation, and specify if it is continuous or batch"))        
        self.tc3 = ChoiceEntry(self.page0,
                               values=[],
                               label=_U("Unit operation type"),
                               tip=_U("Select from predefined list"))
        self.tcHeating_cooling = ChoiceEntry(self.page0,
                               values=HEATING_COOLING,
                               label=_U("heating/cooling"),
                               tip=_U("Select whether this is a heating or cooling process"))
        self.tc4 = ChoiceEntry(self.page0,
                               values=[],
                               label=_U("Product or process medium"),
                               tip=_U("The medium that is in direct contact with the treated product, e.g. air for drying, lye or water for washing, etc..."))           
        self.tc5 = FloatEntry(self.page0,
                              ipart=4, decimals=1, minval=0., maxval=999., value=0.,
                              unitdict='TEMPERATURE',
                              label=_U("Typical (final) temperature of the  process medium during operation"),
                              tip=_U("Give the temperature of the process medium and not that of the heat supplying medium."))
        self.tc7 = FloatEntry(self.page0,
                              ipart=4, decimals=1, minval=0., maxval=999., value=0.,
                              unitdict='TEMPERATURE',
                              label=_U("Start-up temperature of process medium (after breaks)"),
                              tip=_U("Temperature of the process equipment before heating up when process start-up begins"))
        self.tc9 = FloatEntry(self.page0, ipart=10, decimals=1, minval=0., maxval=1.e+12, value=0.,
                              unitdict='VOLUME',
                              label=_U("Volume of the process medium within the equipment or storage"),
                              tip=_U("e.g. volume of liquid in a bottle for cleaning"))
        self.ThermalMassFloatEntry = FloatEntry(self.page0,
                              ipart=10, decimals=1, minval=0., maxval=1.e+12, value=0.,
                              unitdict='MASS',
                              label=_U("effective thermal mass of the process medium"),
                              tip=_U("effective thermal mass of the process medium"))

        self.tc10 = FloatEntry(self.page0,
                              ipart=6, decimals=1, minval=0., maxval=1.e+12, value=0.,
                              unitdict='POWER',
                              label=_U("Power requirement of the process in operation"),
                              tip=_U("Power requirement during operation at steady state (thermal losses, evapoartion, endogenous chemical recations; without heating of circulating fluid)"))
        self.Bind(wx.EVT_CHOICE, self.OnProcessMediumChoice, self.tc4.entry)
        
        # Right panel controls
        # make width of labels larger for this panel and change fontsize
        fp.changeFont(size=TYPE_SIZE_RIGHT)
        f = FieldSizes(wHeight=HEIGHT_RIGHT, wLabel=LABEL_WIDTH_RIGHT)

        # Data of existing heat ...
        
        self.tc22 = ChoiceEntry(self.page4,
                               values=[],
                               label=_U("Medium supplying heat or cold to the process (water, steam, air)"),
                               tip=_U("Medium supplying heat or cold to the process (up to 3)"))


        self.tc23 = ChoiceEntry(self.page4,
                             values=[],
                             label=_U("Heat or cold supply to the process from distribution line / branch No."),
                             tip=_U("Specify the distribution(supply) line of heat/cold feeding the process, using the nomenclature of the hydraulic scheme"))

        self.tc24 = FloatEntry(self.page4,
                               ipart=4, decimals=1, minval=0., maxval=999., value=0.,
                               unitdict='TEMPERATURE',
                               label=_U("Temperature of the incoming medium supplying heat or cold to the process/heat exchanger"),
                               tip=_U("Temperature of the supplying medium at heat exchangers inlet"),
                               fontsize=TYPE_SIZE_RIGHT - 1)

        self.tc25 = FloatEntry(self.page4,
                               ipart=6, decimals=1, minval=0., maxval=1.e+12, value=0.,
                               unitdict='MASSFLOW',
                               label=_U("Flow rate of the heat supply medium (close to process)"),
                               tip=_U("Mass flow of the heat/cold supplyind medium"))

        self.tc26 = FloatEntry(self.page4,
                               ipart=10, decimals=2, minval=0., maxval=1.e+12, value=0.,
                               unitdict='ENERGY',
                               label=_U("Total yearly process heat consumption"),
                               tip=_U("Only for the process"))

        fp.popFont()
        self.buttonAddProcess = wx.Button(self.page0, -1, _U("Add process"))
        self.buttonAddProcess.SetMinSize((125, 32))
        self.Bind(wx.EVT_BUTTON, self.OnButtonAddProcess, self.buttonAddProcess)
        self.buttonAddProcess.SetFont(fp.getFont())

        self.buttonDeleteProcess = wx.Button(self.page0, -1, _U("Delete process"))
        self.buttonDeleteProcess.SetMinSize((125, 32))
        self.Bind(wx.EVT_BUTTON, self.OnButtonDeleteProcess, self.buttonDeleteProcess)
        self.buttonDeleteProcess.SetFont(fp.getFont())

        self.buttonCancel = wx.Button(self, wx.ID_CANCEL, _U("Cancel"))
        self.Bind(wx.EVT_BUTTON, self.OnButtonCancel, self.buttonCancel)
        self.buttonCancel.SetFont(fp.getFont())

        self.buttonOK = wx.Button(self, wx.ID_OK, _U("OK"))
        self.Bind(wx.EVT_BUTTON, self.OnButtonOK, self.buttonOK)
        self.buttonOK.SetDefault()
        self.buttonOK.SetFont(fp.getFont())
        
        # FIXME: Hack common methods into wx widgets
        wx.ListCtrl.GetSelected = GetSelectedItems

        ### tab "Operation"
        # Simple/Detailed schedule selection
        self.page1.DetailedScheduleCheckBox = wx.xrc.XRCCTRL(self.page1, 'DetailedScheduleCheckBox')
        self.Bind(wx.EVT_CHECKBOX, self.OnDetailedScheduleCheckBox, self.page1.DetailedScheduleCheckBox)
        
        # instantiate custom controls
        self.xrcSchedule.AttachUnknownControl("HPerDayFloatEntry",
                                              FloatEntry(self.page1,
                                                         ipart=2, decimals=1, minval=0., maxval=24., value=0.,
                                                         unitdict='TIME',
                                                         label=_U("Hours of process operation per day"),
                                                         tip=_U("Specify the total duration of process, e.g. 3 cycles/day x 2 hrs/cycle = 6 hrs.")))
        self.xrcSchedule.AttachUnknownControl("NCyclesFloatEntry",
                                              FloatEntry(self.page1,
                                                         ipart=2, decimals=1, minval=0., maxval=99., value=0.,
                                                         label=_U("Number of cycles per day"),
                                                         tip=_U(" ")))
        self.xrcSchedule.AttachUnknownControl("HCycleFloatEntry" ,
                                              FloatEntry(self.page1,
                                                         ipart=4, decimals=1, minval=0., maxval=9999., value=0.,
                                                         unitdict='TIME',
                                                         label=_U("Duration of 1 cycle"),
                                                         tip=_U(" ")))
        self.xrcSchedule.AttachUnknownControl("NDaysFloatEntry"  ,
                                              FloatEntry(self.page1,
                                                         ipart=3, decimals=1, minval=0., maxval=365., value=0.,
                                                         label=_U("Days of process operation per year"),
                                                         tip=_U(" ")))
        self.page1.HPerDayFloatEntry = wx.xrc.XRCCTRL(self.page1, 'HPerDayFloatEntry')
        self.page1.NCyclesFloatEntry = wx.xrc.XRCCTRL(self.page1, 'NCyclesFloatEntry')
        self.page1.HCycleFloatEntry  = wx.xrc.XRCCTRL(self.page1, 'HCycleFloatEntry')
        self.page1.NDaysFloatEntry   = wx.xrc.XRCCTRL(self.page1, 'NDaysFloatEntry')
        self.page1.OperationStaticBoxSizer = wx.xrc.XRCCTRL(self.page1, 'OperationStaticBoxSizer')
        self.page1.OperationStaticBoxSizer.SetForegroundColour(TITLE_COLOR)
        
        ### tab "Profile"
        # Daily Profile
        self.page2.ProfileDailyStaticBoxSizer      = wx.xrc.XRCCTRL(self.page2, 'ProfileDailyStaticBoxSizer')
        self.page2.ProfileDailyStaticBoxSizer.SetForegroundColour(TITLE_COLOR)
        self.page2.ProfileDailyFromHourSpinCtrl    = wx.xrc.XRCCTRL(self.page2, 'ProfileDailyFromHourSpinCtrl')
        self.page2.ProfileDailyFromMinuteSpinCtrl  = wx.xrc.XRCCTRL(self.page2, 'ProfileDailyFromMinuteSpinCtrl')
        self.page2.ProfileDailyUntilHourSpinCtrl   = wx.xrc.XRCCTRL(self.page2, 'ProfileDailyUntilHourSpinCtrl')
        self.page2.ProfileDailyUntilMinuteSpinCtrl = wx.xrc.XRCCTRL(self.page2, 'ProfileDailyUntilMinuteSpinCtrl')
        self.page2.ProfileDailyScaleSpinCtrl       = wx.xrc.XRCCTRL(self.page2, 'ProfileDailyScaleSpinCtrl')
        self.page2.ProfileDailyScaleSlider         = wx.xrc.XRCCTRL(self.page2, 'ProfileDailyScaleSlider')
        self.page2.ProfileDailyAddButton           = wx.xrc.XRCCTRL(self.page2, 'ProfileDailyAddButton')
        self.page2.ProfileDailyChangeButton        = wx.xrc.XRCCTRL(self.page2, 'ProfileDailyChangeButton')
        self.page2.ProfileDailyRemoveButton        = wx.xrc.XRCCTRL(self.page2, 'ProfileDailyRemoveButton')
        self.page2.ProfileDailyListCtrl            = wx.xrc.XRCCTRL(self.page2, 'ProfileDailyListCtrl')
        self.page2.ProfileDailyListCtrlFromColumnIndex  = 0
        self.page2.ProfileDailyListCtrlUntilColumnIndex = 1
        self.page2.ProfileDailyListCtrlScaleColumnIndex = 2
        self.page2.ProfileDailyListCtrl.InsertColumn(self.page2.ProfileDailyListCtrlFromColumnIndex, _U('from'))
        self.page2.ProfileDailyListCtrl.InsertColumn(self.page2.ProfileDailyListCtrlUntilColumnIndex, _U('until'))
        self.page2.ProfileDailyListCtrl.InsertColumn(self.page2.ProfileDailyListCtrlScaleColumnIndex, _U('scale (%)'))
        self.Bind(wx.EVT_SPINCTRL, self.OnProfileDailyScaleSpinCtrlChanged, self.page2.ProfileDailyScaleSpinCtrl)
        self.Bind(wx.EVT_TEXT, self.OnProfileDailyScaleSpinCtrlChanged, self.page2.ProfileDailyScaleSpinCtrl)
        self.Bind(wx.EVT_SCROLL_CHANGED, self.OnProfileDailyScaleSliderChanged, self.page2.ProfileDailyScaleSlider)
        self.Bind(wx.EVT_BUTTON, self.OnProfileDailyAddButtonClicked, self.page2.ProfileDailyAddButton)
        self.Bind(wx.EVT_BUTTON, self.OnProfileDailyChangeButtonClicked, self.page2.ProfileDailyChangeButton)
        self.Bind(wx.EVT_BUTTON, self.OnProfileDailyRemoveButtonClicked, self.page2.ProfileDailyRemoveButton)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnProfileDailyListCtrlItemSelected, self.page2.ProfileDailyListCtrl)
        # Weekly Profile
        self.page2.ProfileWeeklyStaticBoxSizer               = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklyStaticBoxSizer')
        self.page2.ProfileWeeklyStaticBoxSizer.SetForegroundColour(TITLE_COLOR)
        self.page2.ProfileWeeklyMondayCheckBox               = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklyMondayCheckBox')
        self.page2.ProfileWeeklyTuesdayCheckBox              = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklyTuesdayCheckBox')#
        self.page2.ProfileWeeklyWednesdayCheckBox            = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklyWednesdayCheckBox')
        self.page2.ProfileWeeklyThursdayCheckBox             = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklyThursdayCheckBox')
        self.page2.ProfileWeeklyFridayCheckBox               = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklyFridayCheckBox')
        self.page2.ProfileWeeklySaturdayCheckBox             = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklySaturdayCheckBox')
        self.page2.ProfileWeeklySundayCheckBox               = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklySundayCheckBox')
        self.page2.ProfileWeeklyNameTextCtrl                 = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklyNameTextCtrl')
        self.page2.ProfileWeeklyAddButton                    = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklyAddButton')
        self.page2.ProfileWeeklyChangeButton                 = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklyChangeButton')
        self.page2.ProfileWeeklyRemoveButton                 = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklyRemoveButton')
        self.page2.ProfileWeeklyListCtrl                     = wx.xrc.XRCCTRL(self.page2, 'ProfileWeeklyListCtrl')
        self.page2.ProfileWeeklyListCtrlNameColumnIndex  = 0
        self.page2.ProfileWeeklyListCtrlScheduleColumnIndex  = 1
        self.page2.ProfileWeeklyListCtrl.InsertColumn(self.page2.ProfileWeeklyListCtrlNameColumnIndex, _U('name'))
        self.page2.ProfileWeeklyListCtrl.InsertColumn(self.page2.ProfileWeeklyListCtrlScheduleColumnIndex, _U('schedule'))
        self.Bind(wx.EVT_BUTTON, self.OnProfileWeeklyAddButtonClicked, self.page2.ProfileWeeklyAddButton)
        self.Bind(wx.EVT_BUTTON, self.OnProfileWeeklyChangeButtonClicked, self.page2.ProfileWeeklyChangeButton)
        self.Bind(wx.EVT_BUTTON, self.OnProfileWeeklyRemoveButtonClicked, self.page2.ProfileWeeklyRemoveButton)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnProfileWeeklyListCtrlItemSelected, self.page2.ProfileWeeklyListCtrl)
    
        ### tab "Schedule"
        # instantiate custom controls
        self.xrcSchedule.AttachUnknownControl('StartupFloatEntry'  , FloatEntry(self.page3, wLabel=60, wData=60, wUnits=60, label=_U('startup:'), unitdict='TIME', decimals=1, value='' , minval=0., maxval=YEAR))
        self.xrcSchedule.AttachUnknownControl('InflowFloatEntry'   , FloatEntry(self.page3, wLabel=60, wData=60, wUnits=60, label=_U('inflow:') , unitdict='TIME', decimals=1, value='' , minval=0., maxval=YEAR))
        self.xrcSchedule.AttachUnknownControl('OutflowFloatEntry'  , FloatEntry(self.page3, wLabel=60, wData=60, wUnits=60, label=_U('outflow:'), unitdict='TIME', decimals=1, value='' , minval=0., maxval=YEAR))
        self.xrcSchedule.AttachUnknownControl('ToleranceFloatEntry', FloatEntry(self.page3, wLabel=60, wData=60, wUnits=60, label=_U('tolerance +/-:'), unitdict='TIME', decimals=1, value=0.0, minval=0., maxval=12.0))
        
        # Schedule
        self.page3.PeriodStaticBoxSizer       = wx.xrc.XRCCTRL(self.page3, 'PeriodStaticBoxSizer')
        self.page3.ScheduleStaticBoxSizer     = wx.xrc.XRCCTRL(self.page3, 'ScheduleStaticBoxSizer')
        self.page3.SchedulePeriodWeeklyProfileBoxSizer = wx.xrc.XRCCTRL(self.page3, 'SchedulePeriodWeeklyProfileBoxSizer')
        self.page3.PeriodStaticBoxSizer.SetForegroundColour(TITLE_COLOR)
        self.page3.ScheduleStaticBoxSizer.SetForegroundColour(TITLE_COLOR)
        self.page3.SchedulePeriodWeeklyProfileBoxSizer.SetForegroundColour(TITLE_COLOR)
        self.page3.StartupFloatEntry          = wx.xrc.XRCCTRL(self.page3, 'StartupFloatEntry')
        self.page3.InflowFloatEntry           = wx.xrc.XRCCTRL(self.page3, 'InflowFloatEntry')
        self.page3.OutflowFloatEntry          = wx.xrc.XRCCTRL(self.page3, 'OutflowFloatEntry')
        self.page3.ToleranceFloatEntry        = wx.xrc.XRCCTRL(self.page3, 'ToleranceFloatEntry')
        self.page3.PeriodFromDatePicker       = wx.xrc.XRCCTRL(self.page3, 'PeriodFromDatePicker')
        self.page3.PeriodUntilDatePicker      = wx.xrc.XRCCTRL(self.page3, 'PeriodUntilDatePicker')
        self.page3.PeriodStepSpinCtrl         = wx.xrc.XRCCTRL(self.page3, 'PeriodStepSpinCtrl')
        self.page3.PeriodScaleSpinCtrl        = wx.xrc.XRCCTRL(self.page3, 'PeriodScaleSpinCtrl')
        self.page3.PeriodScaleSlider          = wx.xrc.XRCCTRL(self.page3, 'PeriodScaleSlider')
        self.page3.ProfileListCtrl            = wx.xrc.XRCCTRL(self.page3, 'ProfileListCtrl')
        self.page3.HolidaySpinCtrl            = wx.xrc.XRCCTRL(self.page3, 'HolidaySpinCtrl')
        self.page3.HolidaySlider              = wx.xrc.XRCCTRL(self.page3, 'HolidaySlider')
        self.page3.ScheduleAddButton          = wx.xrc.XRCCTRL(self.page3, 'ScheduleAddButton')
        self.page3.ScheduleChangeButton       = wx.xrc.XRCCTRL(self.page3, 'ScheduleChangeButton')
        self.page3.ScheduleRemoveButton       = wx.xrc.XRCCTRL(self.page3, 'ScheduleRemoveButton')
        self.page3.ScheduleListCtrl           = wx.xrc.XRCCTRL(self.page3, 'ScheduleListCtrl')
        self.page3.SchedulePeriodWeeklyProfilePanel = wx.xrc.XRCCTRL(self.page3, 'SchedulePeriodWeeklyProfilePanel')
        self.Bind(wx.EVT_SPINCTRL, self.OnPeriodScaleSpinCtrlChanged, self.page3.PeriodScaleSpinCtrl)
        self.Bind(wx.EVT_TEXT, self.OnPeriodScaleSpinCtrlChanged, self.page3.PeriodScaleSpinCtrl)
        self.Bind(wx.EVT_SCROLL_CHANGED, self.OnPeriodScaleSliderChanged, self.page3.PeriodScaleSlider)
        self.Bind(wx.EVT_SPINCTRL, self.OnHolidaySpinCtrlChanged, self.page3.HolidaySpinCtrl)
        self.Bind(wx.EVT_TEXT, self.OnHolidaySpinCtrlChanged, self.page3.HolidaySpinCtrl)
        self.Bind(wx.EVT_SCROLL_CHANGED, self.OnHolidaySliderChanged, self.page3.HolidaySlider)
        self.Bind(wx.EVT_BUTTON, self.OnScheduleAddButtonClicked, self.page3.ScheduleAddButton)
        self.Bind(wx.EVT_BUTTON, self.OnScheduleChangeButtonClicked, self.page3.ScheduleChangeButton)
        self.Bind(wx.EVT_BUTTON, self.OnScheduleRemoveButtonClicked, self.page3.ScheduleRemoveButton)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnScheduleListCtrlItemSelected, self.page3.ScheduleListCtrl)
        dt = wx.DateTime()
        dt.ParseDate("%d-01-01" % date.today().year)
        self.page3.PeriodFromDatePicker.SetValue(dt)
        dt = wx.DateTime() 
        dt.ParseDate("%d-12-31" % date.today().year)
        self.page3.PeriodUntilDatePicker.SetValue(dt)
        self.page3.ProfileListCtrl.InsertColumn(self.page2.ProfileWeeklyListCtrlNameColumnIndex, _U('name'))
        self.page3.ProfileListCtrl.InsertColumn(self.page2.ProfileWeeklyListCtrlScheduleColumnIndex, _U('schedule'))
        self.page3.ScheduleListCtrlFromColumnIndex  = 0
        self.page3.ScheduleListCtrlUntilColumnIndex = 1
        self.page3.ScheduleListCtrlStepColumnIndex  = 2
        self.page3.ScheduleListCtrlScaleColumnIndex = 3
        self.page3.ScheduleListCtrlProfileColumnIndex = 4
        self.page3.ScheduleListCtrl.InsertColumn(self.page3.ScheduleListCtrlFromColumnIndex, _U('from'))
        self.page3.ScheduleListCtrl.InsertColumn(self.page3.ScheduleListCtrlUntilColumnIndex, _U('until'))
        self.page3.ScheduleListCtrl.InsertColumn(self.page3.ScheduleListCtrlStepColumnIndex, _U('step (d)'))
        self.page3.ScheduleListCtrl.InsertColumn(self.page3.ScheduleListCtrlScaleColumnIndex, _U('scale (%)'))
        self.page3.ScheduleListCtrl.InsertColumn(self.page3.ScheduleListCtrlProfileColumnIndex, _U('profiles'))

        # Profile list
        self.weeklyProfile = []
        for weeklyProfileName in getProfileNamesFromDB():
            weeklyProfile = WeeklyProfile(weeklyProfileName)
            try:
                weeklyProfile.loadFromDB()
            except ProfileNotFoundError:
                logError("Cannot find profile by name. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
                continue
            except ProfileWithoutIntervalsError:
                logError("Skipping DB profile without intervals. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
                continue
            self.weeklyProfile.append(weeklyProfile)
            newProfileWeeklyListCtrlItemIndex = self.page2.ProfileWeeklyListCtrl.InsertStringItem(self.page2.ProfileWeeklyListCtrlNameColumnIndex, weeklyProfile.id)        
            self.page2.ProfileWeeklyListCtrl.SetStringItem(newProfileWeeklyListCtrlItemIndex, self.page2.ProfileWeeklyListCtrlScheduleColumnIndex, "<click to see>")
            
        # Period list
        # load all periods from DB (defaults are in SQL files)
        for periodRow in sorted(Status.DB.periods.get_table(), key=lambda x: x['start'], reverse=True):
            newPeriodItem = self.page3.ScheduleListCtrl.InsertStringItem(self.page3.ScheduleListCtrlProfileColumnIndex, '')
            self.page3.ScheduleListCtrl.SetStringItem(newPeriodItem, self.page3.ScheduleListCtrlFromColumnIndex, periodRow['start'].strftime('%m-%d'))
            self.page3.ScheduleListCtrl.SetStringItem(newPeriodItem, self.page3.ScheduleListCtrlUntilColumnIndex, periodRow['stop'].strftime('%m-%d'))
            self.page3.ScheduleListCtrl.SetStringItem(newPeriodItem, self.page3.ScheduleListCtrlStepColumnIndex, '1')
            self.page3.ScheduleListCtrl.SetStringItem(newPeriodItem, self.page3.ScheduleListCtrlScaleColumnIndex, '100')
            
        # Period Weekly Profile plot panel
        paramList = {'labels'       : 0, # labels column
                   'data'         : 0,                      # data column for this graph
                   'key'         : 'SchedulePeriodWeeklyProfile',                # key for Interface
                   'title'       : _U('Period Weekly Profile'),           # title of the graph
                   'backcolor'   : GRAPH_BACKGROUND_COLOR, # graph background color
                   'ignoredrows' : []}            # rows that should not be plotted
        Status.int.setGraphicsData('SchedulePeriodWeeklyProfile', [0.] * int(WEEK))
        dummy = MatPanel(self.page3.SchedulePeriodWeeklyProfilePanel, wx.Panel, drawFigure, paramList)
        del dummy
        self.page3.SchedulePeriodWeeklyProfilePanel.draw()
        
        # Input streams
        self.InputStreamsProcMedDBFluidChoiceEntry = ChoiceEntry(self.page6,
                                                                 values=[], value=None,
                                                                 label=_U("Product or process medium"),
                                                                 tip=_U("The medium that is in direct contact with the treated product, e.g. air for drying, lye or water for washing, etc..."))
        self.InputStreamsPTInFlowFloatEntry        = FloatEntry(self.page6,
                                                                ipart=4, decimals=1, minval=0., maxval=999., value=None,
                                                                unitdict='TEMPERATURE',
                                                                label=_U("Inlet temperature of the process medium"),
                                                                tip=_U("Inlet temperature of the process medium before heat recovery"))
        self.InputStreamsVInFlowCycleFloatEntry    = FloatEntry(self.page6,
                                                                ipart=10, decimals=1, minval=0., maxval=1.e+12, value=None,
                                                                # FIXME: should be unitdict='VOLUMEORMASS',
                                                                unitdict='VOLUME',
                                                                label=_U("Inflow of process medium per cycle"),
                                                                tip=_U("Continuous process: Fluid flow rate times hours of circulation. Batch process with fluid renewal: volume of renewal."))
        self.InputStreamsMInFlowNomFloatEntry      = FloatEntry(self.page6,
                                                                ipart=10, decimals=1, minval=0., maxval=1.e+12, value=None,
                                                                # FIXME: should be unitdict='MASSORVOLUMEFLOW',
                                                                unitdict='MASSFLOW',
                                                                label=_U("Nominal mass flow rate of inflow of process medium"),
                                                                tip=_U(""))
        self.InputStreamsHeatRecExistChoiceEntry = ChoiceEntry(self.page6,
                                                                 values=[' '] + TRANSYESNO.values(), value=None,
                                                                 label=_U("Exists internal heat recovery for the process?"),
                                                                 tip=_U("If affirmative, specify the inlet temperature after heat recovery"))
        self.InputStreamsPTInFlowRecFloatEntry     = FloatEntry(self.page6,
                                                                ipart=4, decimals=1, minval=0., maxval=999., value=None,
                                                                unitdict='TEMPERATURE',
                                                                label=_U("Inlet temperature of the process medium  (after heat recovery)"),
                                                                tip=_U("Inlet temperature (towards the system) of the process medium after the heat recovery"))
        self.xrcStreams.AttachUnknownControl('InputStreamsProcMedDBFluidChoiceEntry', self.InputStreamsProcMedDBFluidChoiceEntry)
        self.xrcStreams.AttachUnknownControl('InputStreamsPTInFlowFloatEntry'       , self.InputStreamsPTInFlowFloatEntry)
        self.xrcStreams.AttachUnknownControl('InputStreamsVInFlowCycleFloatEntry'   , self.InputStreamsVInFlowCycleFloatEntry)
        self.xrcStreams.AttachUnknownControl('InputStreamsMInFlowNomFloatEntry'     , self.InputStreamsMInFlowNomFloatEntry)
        self.xrcStreams.AttachUnknownControl('InputStreamsHeatRecExistChoiceEntry'  , self.InputStreamsHeatRecExistChoiceEntry)
        self.xrcStreams.AttachUnknownControl('InputStreamsPTInFlowRecFloatEntry'    , self.InputStreamsPTInFlowRecFloatEntry)
        self.InputStreamsListBox      = wx.xrc.XRCCTRL(self.page6, 'InputStreamsListBox')
        self.InputStreamsAddButton    = wx.xrc.XRCCTRL(self.page6, 'InputStreamsAddButton')
        self.InputStreamsChangeButton = wx.xrc.XRCCTRL(self.page6, 'InputStreamsChangeButton')
        self.InputStreamsRemoveButton = wx.xrc.XRCCTRL(self.page6, 'InputStreamsRemoveButton')
        self.InputStreamsNameTextCtrl = wx.xrc.XRCCTRL(self.page6, 'InputStreamsNameTextCtrl')
        self.InputStreamsBeforeHeatRecoveryStaticBoxSizer = wx.xrc.XRCCTRL(self.page6, 'InputStreamsBeforeHeatRecoveryStaticBoxSizer')
        self.InputStreamsAfterHeatRecoveryStaticBoxSizer  = wx.xrc.XRCCTRL(self.page6, 'InputStreamsAfterHeatRecoveryStaticBoxSizer')
        self.InputStreamsBeforeHeatRecoveryStaticBoxSizer.SetForegroundColour(TITLE_COLOR)
        self.InputStreamsAfterHeatRecoveryStaticBoxSizer.SetForegroundColour(TITLE_COLOR)
        self.Bind(wx.EVT_BUTTON, self.OnInputStreamsAddButtonClicked, self.InputStreamsAddButton)
        self.Bind(wx.EVT_BUTTON, self.OnInputStreamsChangeButtonClicked, self.InputStreamsChangeButton)
        self.Bind(wx.EVT_BUTTON, self.OnInputStreamsRemoveButtonClicked, self.InputStreamsRemoveButton)
        self.Bind(wx.EVT_LISTBOX, self.OnInputStreamsListBoxItemSelected, self.InputStreamsListBox)
        self.Bind(wx.EVT_TEXT, self.OnInputStreamsPTInFlowValueChanged, self.InputStreamsPTInFlowFloatEntry.entry)
        self.Bind(wx.EVT_CHOICE, self.OnInputStreamsPTInFlowUnitChanged, self.InputStreamsPTInFlowFloatEntry.units)
        self.Bind(wx.EVT_CHOICE, self.OnInputStreamsHeatRecExistChoice, self.InputStreamsHeatRecExistChoiceEntry.entry)
        
        # Output streams
        self.OutputStreamsHeatRecOkChoiceEntry = ChoiceEntry(self.page7,
                                                                values=[' '] + TRANSYESNO.values(), value=None,
                                                                label=_U("Can heat be recovered from the outflowing medium?"),
                                                                tip=_U("If NO, specify why: e.g. contamination with substances which can affect the heat exchanger,..."))
        self.OutputStreamsProcMedOutChoiceEntry = ChoiceEntry(self.page7,
                                                                values=[], value=None,
                                                                label=_U("Medium of outgoing waste heat flows"),
                                                                tip=_U("Specify media of waste heat flows (up to 3)"))
        self.OutputStreamsPTOutFlowFloatEntry     = FloatEntry(self.page7,
                                                               ipart=4, decimals=1, minval=0., maxval=999., value=None,
                                                               unitdict='TEMPERATURE',
                                                               label=_U("Temperature of outgoing (waste) heat flows"),
                                                               tip=_U("Temperature of the outgoing waste heat flow (e.g. water or hot humid air at the outlet of a drying process)"))
        self.OutputStreamsHOutFlowFloatEntry      = FloatEntry(self.page7,
                                                               ipart=6, decimals=1, minval=0., maxval=999999., value=None,
                                                               unitdict='SPECIFICENTHALPY',
                                                               label=_U("Specific enthalpy of outgoing (waste) heat flows"),
                                                               tip=_U("Enthalpy of the outgoing waste heat flow (e.g. water or hot humid air at the outlet of a drying process)"))
        self.OutputStreamsXOutFlowFloatEntry      = FloatEntry(self.page7,
                                                               ipart=6, decimals=1, minval=0., maxval=999999., value=None,
                                                               unitdict='SPECIFICENTHALPY',
                                                               label=_U("Humidity ratio of outgoing (waste) heat flows"),
                                                               tip=_U("Specify humidity ratio in kg water per kg dry air/gas"))
        self.OutputStreamsPTFinalFloatEntry       = FloatEntry(self.page7,
                                                               ipart=4, decimals=1, minval=0., maxval=999., value=None,
                                                               unitdict='TEMPERATURE',
                                                               label=_U("Final  temperature of outgoing (waste) heat flows"),
                                                               tip=_U("Minimum temperature to which the waste heat flow can be cooled. If there is no limit specify 0"))
        self.OutputStreamsVOutFlowCycleFloatEntry = FloatEntry(self.page7,
                                                               ipart=6, decimals=1, minval=0., maxval=1.e+12, value=None,
                                                               # FIXME: should be VOLUMEORMASS
                                                               unitdict='VOLUME',
                                                               label=_U("Outflow of process medium per cycle"),
                                                               tip=_U("Can be different from the incoming flow if e.g. there is evaporation or some chemical reaction."))
        self.OutputStreamsMOutFlowNomFloatEntry   = FloatEntry(self.page7,
                                                               ipart=10, decimals=1, minval=0., maxval=1.e+12, value=None,
                                                               # FIXME: should be unitdict='MASSORVOLUMEFLOW',
                                                               unitdict='MASSFLOW',
                                                               label=_U("Nominal mass flow rate of outflow of process medium"),
                                                               tip=_U(""))
        self.xrcStreams.AttachUnknownControl('OutputStreamsHeatRecOkChoiceEntry'   , self.OutputStreamsHeatRecOkChoiceEntry)
        self.xrcStreams.AttachUnknownControl('OutputStreamsProcMedOutChoiceEntry'  , self.OutputStreamsProcMedOutChoiceEntry)
        self.xrcStreams.AttachUnknownControl('OutputStreamsPTOutFlowFloatEntry'    , self.OutputStreamsPTOutFlowFloatEntry)
        self.xrcStreams.AttachUnknownControl('OutputStreamsHOutFlowFloatEntry'     , self.OutputStreamsHOutFlowFloatEntry)
        self.xrcStreams.AttachUnknownControl('OutputStreamsXOutFlowFloatEntry'     , self.OutputStreamsXOutFlowFloatEntry)
        self.xrcStreams.AttachUnknownControl('OutputStreamsPTFinalFloatEntry'      , self.OutputStreamsPTFinalFloatEntry)
        self.xrcStreams.AttachUnknownControl('OutputStreamsVOutFlowCycleFloatEntry', self.OutputStreamsVOutFlowCycleFloatEntry)
        self.xrcStreams.AttachUnknownControl('OutputStreamsMOutFlowNomFloatEntry'  , self.OutputStreamsMOutFlowNomFloatEntry)
        self.OutputStreamsListBox      = wx.xrc.XRCCTRL(self.page7, 'OutputStreamsListBox')
        self.OutputStreamsAddButton    = wx.xrc.XRCCTRL(self.page7, 'OutputStreamsAddButton')
        self.OutputStreamsChangeButton = wx.xrc.XRCCTRL(self.page7, 'OutputStreamsChangeButton')
        self.OutputStreamsRemoveButton = wx.xrc.XRCCTRL(self.page7, 'OutputStreamsRemoveButton')
        self.OutputStreamsNameTextCtrl = wx.xrc.XRCCTRL(self.page7, 'OutputStreamsNameTextCtrl')
        self.Bind(wx.EVT_BUTTON, self.OnOutputStreamsAddButtonClicked, self.OutputStreamsAddButton)
        self.Bind(wx.EVT_BUTTON, self.OnOutputStreamsChangeButtonClicked, self.OutputStreamsChangeButton)
        self.Bind(wx.EVT_BUTTON, self.OnOutputStreamsRemoveButtonClicked, self.OutputStreamsRemoveButton)
        self.Bind(wx.EVT_LISTBOX, self.OnOutputStreamsListBoxItemSelected, self.OutputStreamsListBox)
        self.Bind(wx.EVT_CHOICE, self.OnOutputStreamsHeatRecOkChoice, self.OutputStreamsHeatRecOkChoiceEntry.entry)
    
    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        
        sizerOKCancel = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10 = wx.BoxSizer(wx.VERTICAL)
        sizer_13 = wx.StaticBoxSizer(self.sizer_13_staticbox, wx.VERTICAL)
        sizer_25 = wx.BoxSizer(wx.VERTICAL)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_7 = wx.StaticBoxSizer(self.sizer_7_staticbox, wx.VERTICAL)
        sizer_21 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.StaticBoxSizer(self.sizer_5_staticbox, wx.VERTICAL)
        sizer_5.Add(self.listBoxProcesses, 1, wx.EXPAND, 0)
        sizer_5.Add(self.buttonAddProcess, 0, wx.ALIGN_RIGHT, 0)
        sizer_5.Add(self.buttonDeleteProcess, 0, wx.ALIGN_RIGHT, 0)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)

        flagLabel = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM
        flagText = wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM
        # Left tab. Processes description
        sizer_21.Add(self.tc1, 0, flagText, 1)
        sizer_21.Add(self.tc1_1, 0, flagText, 1)
        sizer_21.Add(self.tc2, 0, flagText, 1)
        sizer_21.Add(self.tc3, 0, flagText, 1)
        sizer_21.Add(self.tcHeating_cooling, 0, flagText, 1)
        sizer_21.Add(self.tc4, 0, flagText, 1)
        sizer_21.Add(self.tc5, 0, flagText, 1)
        sizer_21.Add(self.tc7, 0, flagText, 1)
        sizer_21.Add(self.tc9, 0, flagText, 1)
        sizer_21.Add(self.ThermalMassFloatEntry, 0, flagText, 1)
        sizer_21.Add(self.tc10, 0, flagText, 1)

        sizer_7.Add(sizer_21, 1, wx.LEFT | wx.EXPAND, 40)
        sizer_6.Add(sizer_7, 2, wx.EXPAND, 0)

        #sizer_8.Add(sizer_22, 1, wx.LEFT|wx.EXPAND, 40)
        #sizer_6.Add(sizer_8, 0, wx.EXPAND, 0)
        sizer_4.Add(sizer_6, 2, wx.EXPAND, 0)
        self.page0.SetSizer(sizer_4)
        
        # Right tab. Data of existing supply
        sizer_25.Add(self.tc22, 0, flagText, 1)
        sizer_25.Add(self.tc23, 0, flagText, 1)
        sizer_25.Add(self.tc24, 0, flagText, 1)
        sizer_25.Add(self.tc25, 0, flagText, 1)
        sizer_25.Add(self.tc26, 0, flagText, 1)

        sizer_13.Add(sizer_25, 1, wx.LEFT | wx.TOP | wx.EXPAND, 10)
        sizer_10.Add(sizer_13, 0, wx.EXPAND, 0)
        self.page4.SetSizer(sizer_10)
        self.notebook.AddPage(self.page0, _U('Process data'))
        self.notebook.AddPage(self.page1, _U('Operation'))
        self.notebook.AddPage(self.page2, _U('Profile'))
        self.notebook.AddPage(self.page3, _U('Schedule'))
        self.notebook.AddPage(self.page4, _U('Heat supply'))
        self.notebook.AddPage(self.page5, _U('Temperatures and flow rates'))
        self.notebook.AddPage(self.page6, _U('In-flow'))
        self.notebook.AddPage(self.page7, _U('Out-flow'))
        # initially disable detailed schedule tabs
        self.page2.Enable(False)
        self.page3.Enable(False)
        sizer_2.Add(self.notebook, 1, wx.EXPAND, 0)
        sizerOKCancel.Add(self.buttonCancel, 0, wx.ALL | wx.EXPAND, 2)
        sizerOKCancel.Add(self.buttonOK, 0, wx.ALL | wx.EXPAND, 2)
        sizer_2.Add(sizerOKCancel, 0, wx.TOP | wx.ALIGN_RIGHT, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()

#------------------------------------------------------------------------------
#--- UI actions
#------------------------------------------------------------------------------		

    def OnNotebookPageChanged(self, event):
        oldPageIndex = event.GetOldSelection()
        newPageIndex = event.GetSelection()
        
        if newPageIndex == self.scheduleNotebookPageIndex:
            self.page3.ProfileListCtrl.DeleteAllItems()
            for weeklyProfile in self.weeklyProfile:
                i = self.page3.ProfileListCtrl.InsertStringItem(self.page2.ProfileWeeklyListCtrlNameColumnIndex, weeklyProfile.id)
                self.page3.ProfileListCtrl.SetStringItem(i, self.page2.ProfileWeeklyListCtrlScheduleColumnIndex, "<see Profile tab>")
            for periodItemIndex in range(self.page3.ScheduleListCtrl.GetItemCount()):
                self.page3.ScheduleListCtrl.Select(periodItemIndex, False)

    def OnButtonAddProcess(self, event):
        self.clear()
        # for new processes default to detailed schedule
        self.page1.DetailedScheduleCheckBox.SetValue(True)
        self.OnDetailedScheduleCheckBox(None)
        self.selectedProcessName = None

    def OnButtonDeleteProcess(self, event):
        
        if self.checkIfAllowed() == False:
            return
        
        Status.prj.deleteProcess(self.selectedProcessID)
        self.clear()
        self.selectedProcessName = None
        self.display()
        
    def OnProcessMediumChoice(self, event):
        processMedium = self.tc4.GetValue(text=True)
        if processMedium != ' ':
            inputStreamMedium  = self.InputStreamsProcMedDBFluidChoiceEntry.GetValue(text=True)
            if inputStreamMedium == ' ':
                self.InputStreamsProcMedDBFluidChoiceEntry.SetValue(processMedium)
            outputStreamMedium = self.OutputStreamsProcMedOutChoiceEntry.GetValue(text=True)
            if outputStreamMedium == ' ':
                self.OutputStreamsProcMedOutChoiceEntry.SetValue(processMedium)
            

    def OnListBoxProcessesClick(self, event):
        self.selectedProcessName = self.listBoxProcesses.GetStringSelection()
        print "PanelQ3: selected Process Name = %r" % self.selectedProcessName
        self.showProcess()

    def showProcess(self):

        print "PanelQ3 (showProcess): selected Process Name = %r" % self.selectedProcessName
        if self.selectedProcessName is not None:
            processes = Status.DB.qprocessdata.\
                        Questionnaire_id[Status.PId].\
                        AlternativeProposalNo[Status.ANo].\
                        Process[self.selectedProcessName.encode("utf-8")]
        else:
            processes = []
        
        if len(processes) == 0:
            print "PanelQ3 (showProcess): process not found in DB"
            return
        else:
            q = processes[0]
            print "PanelQ3 (showProcess): process found in DB"
        
        self.selectedProcessID = q.QProcessData_ID

        fluidDict = Status.prj.getFluidDict()
        unitOpDict = Status.prj.getUnitOpDict()

        print "PanelQ3 (showProcess): now writing tc1 = %r" % q.Process
        self.tc1.SetValue(q.Process)
        self.tc1_1.SetValue(q.Description)
        if q.ProcType in TRANSPROCTYPES.keys():
            self.tc2.SetValue(TRANSPROCTYPES[q.ProcType])
        else:
            self.tc2.SetValue("None")

        if q.DBUnitOperation_id in unitOpDict.keys():
            unitOp = unitOpDict[q.DBUnitOperation_id]
            self.tc3.SetValue(unitOp)
        else:
            self.tc3.SetValue("None")

        if q.heating_cooling in HEATING_COOLING:
            self.tcHeating_cooling.SetValue(q.heating_cooling)
        else:
            self.tcHeating_cooling.SetValue("None")

        if q.ProcMedDBFluid_id in fluidDict.keys():
            fluidName = fluidDict[q.ProcMedDBFluid_id]
            self.tc4.SetValue(fluidName)
        else:
            self.tc4.SetValue("None")
            
        self.tc5.SetValue(str(q.PT))
        self.InputStreamsPTInFlowFloatEntry.SetValue(str(q.PTInFlow))
        self.tc7.SetValue(str(q.PTStartUp))

        setUnitsFluidDensity(q.ProcMedDBFluid_id)
        self.InputStreamsVInFlowCycleFloatEntry.SetValue(str(q.VInFlowCycle))
        self.InputStreamsMInFlowNomFloatEntry.SetValue(str(q.mInFlowNom))
        
        self.tc9.SetValue(str(q.VolProcMed))
        self.ThermalMassFloatEntry.SetValue(str(q.ThermalMass))
        self.tc10.SetValue(str(q.QOpProc))
        self.page1.HPerDayFloatEntry.SetValue(str(q.HPerDayProc))
        self.page1.NCyclesFloatEntry.SetValue(str(q.NBatch))
        self.page1.HCycleFloatEntry.SetValue(str(q.HBatch))
        self.page1.NDaysFloatEntry.SetValue(str(q.NDaysProc))		
        self.OutputStreamsPTOutFlowFloatEntry.SetValue(str(q.PTOutFlow))

        if q.ProcMedOut in fluidDict.keys():
            fluidName = fluidDict[q.ProcMedOut]
            self.OutputStreamsProcMedOutChoiceEntry.SetValue(fluidName)
        else:
            self.OutputStreamsProcMedOutChoiceEntry.SetValue("None")

        self.OutputStreamsHOutFlowFloatEntry.SetValue(str(q.HOutFlow))
        self.OutputStreamsXOutFlowFloatEntry.SetValue(str(q.XOutFlow))
        self.OutputStreamsPTFinalFloatEntry.SetValue(str(q.PTFinal))
        
        ### Schedule settings
        # default to simple schedule
        try:
            self.periodSchedule = PeriodSchedule(self.selectedProcessName)
            self.periodSchedule.loadFromDB(originalProcessId(self.selectedProcessID))
        except ScheduleNotFoundError:
            self.periodSchedule = None
        else:
            # display process schedule parameters
            self.page3.StartupFloatEntry.SetValue(self.periodSchedule.startup)
            self.page3.InflowFloatEntry.SetValue(self.periodSchedule.inflow)
            self.page3.OutflowFloatEntry.SetValue(self.periodSchedule.outflow)
            self.page3.ToleranceFloatEntry.SetValue(self.periodSchedule.tolerance)
            self.page3.HolidaySpinCtrl.SetValue(self.periodSchedule.holidayScale)
            self.page3.HolidaySlider.SetValue(self.periodSchedule.holidayScale)
            # load process periods and profiles from DB
            self.page3.ScheduleListCtrl.DeleteAllItems()
            for dbPeriod in Status.DB.periods.id['%']:
                # add every period defined in DB including empty ones
                newScheduleListCtrlItemIndex = self.page3.ScheduleListCtrl.InsertStringItem(self.page3.ScheduleListCtrlProfileColumnIndex, '')
                self.page3.ScheduleListCtrl.SetStringItem(newScheduleListCtrlItemIndex, self.page3.ScheduleListCtrlFromColumnIndex, dbPeriod.start.strftime('%m-%d'))
                self.page3.ScheduleListCtrl.SetStringItem(newScheduleListCtrlItemIndex, self.page3.ScheduleListCtrlUntilColumnIndex, dbPeriod.stop.strftime('%m-%d'))
                # find process definition for current period
                dbProcessPeriods = Status.DB.process_periods.qprocessdata_QProcessData_ID[originalProcessId(self.selectedProcessID)].periods_id[dbPeriod.id]
                try:
                    dbProcessPeriod = dbProcessPeriods[0] # use first definition of period only    
                except IndexError: # No definitions for process in current period
                    continue
                # found process period definition -> detailed schedule
                self.page1.DetailedScheduleCheckBox.SetValue(True)
                self.OnDetailedScheduleCheckBox(None)
                self.page3.ScheduleListCtrl.SetStringItem(newScheduleListCtrlItemIndex, self.page3.ScheduleListCtrlStepColumnIndex, str(dbProcessPeriod.step))
                self.page3.ScheduleListCtrl.SetStringItem(newScheduleListCtrlItemIndex, self.page3.ScheduleListCtrlScaleColumnIndex, str(dbProcessPeriod.scale))
                # find profiles for current process period            
                addProfileNames  = []
                for dbProcessPeriodProfileId in Status.DB.process_period_profiles.process_periods_id[dbProcessPeriod.id].profiles_id['%'].column():
                    addProfileNames.append(Status.DB.profiles.id[dbProcessPeriodProfileId][0].name)
                self.page3.ScheduleListCtrl.SetStringItem(newScheduleListCtrlItemIndex, self.page3.ScheduleListCtrlProfileColumnIndex, ', '.join(addProfileNames))
            self.fillSchedule()
        
        self.page1.DetailedScheduleCheckBox.SetValue(self.periodSchedule != None)
        self.OnDetailedScheduleCheckBox(None)
        
        ### Streams settings
        # display process in-flowing streams
        self.InputStreamsListBox.Set(getInflowingStreamNamesFromDB(self.selectedProcessID))  
        # display process out-flowing streams
        self.OutputStreamsListBox.Set(getOutflowingStreamNamesFromDB(self.selectedProcessID))  

###        setUnitsFluidDensity(q.ProcMedOut) works only with One fluid per panel !!!
        self.OutputStreamsVOutFlowCycleFloatEntry.SetValue(str(q.VOutFlowCycle))
        self.OutputStreamsMOutFlowNomFloatEntry.SetValue(str(q.mOutFlowNom))
        
        if q.HeatRecOK is not None and q.HeatRecOK.lower() in TRANSYESNO:
            self.OutputStreamsHeatRecOkChoiceEntry.SetValue(TRANSYESNO[q.HeatRecOK.lower()])
        else:
            self.OutputStreamsHeatRecOkChoiceEntry.SetValue("None")
           
        if q.HeatRecExist is not None and q.HeatRecExist.lower() in TRANSYESNO:
            self.InputStreamsHeatRecExistChoiceEntry.SetValue(TRANSYESNO[q.HeatRecExist.lower()])
        else:
            self.InputStreamsHeatRecExistChoiceEntry.SetValue("None")

#        self.tc20.SetValue(q.SourceWasteHeat)
        if q.HeatRecExist is not None and q.HeatRecExist.lower() in TRANSYESNO:
            if str(q.HeatRecExist.lower()) == TRANSYESNO['yes']:
                self.InputStreamsPTInFlowRecFloatEntry.SetValue(str(q.PTInFlowRec))
            else:
                self.InputStreamsPTInFlowRecFloatEntry.SetValue(str(q.PTInFlow))

        fluidDict = Status.prj.getFluidDict()        
        if q.SupplyMedDBFluid_id in fluidDict.keys():
            fluidName = fluidDict[q.SupplyMedDBFluid_id]
            self.tc22.SetValue(fluidName)
        else:
            self.tc22.SetValue("None")

        self.tc23.SetValue(q.PipeDuctProc)
        self.tc24.SetValue(str(q.TSupply))
        self.tc25.SetValue(str(q.SupplyMedFlow))
        self.tc26.SetValue(str(q.UPH))

    def OnButtonCancel(self, event):
        self.clear()
        self.display()

    def OnButtonOK(self, event):
        if Status.PId == 0:
            return

        if self.checkIfAllowed()==False:
            return
        
        processName = self.tc1.GetValue()
        logTrack("PanelQ3 (ok-button): adding process %r"%processName)

# assure that a name has been entered before continuing
        if len(processName) == 0 or processName is None:
            showWarning(_U("You have to enter a name for the new process before saving"))
            return
        
        processes = Status.DB.qprocessdata.Questionnaire_id[Status.PId].\
                    AlternativeProposalNo[Status.ANo].\
                    Process[check(processName)]

        if len(processes) == 0:
            process = Status.prj.addProcessDummy()
        elif len(processes) == 1:
            process = processes[0]
        else:
            showWarning(_U("PanelQ3 (ButtonOK): Process name has to be a unique value!"))
            return

        unitOpDict = Status.prj.getUnitOpDict()          
        fluidDict = Status.prj.getFluidDict()
            
        setUnitsFluidDensity(findKey(fluidDict,self.tc4.GetValue(text=True)))

###     FIXME: What is this?   setUnitsFluidDensity(findKey(fluidDict,self.OutputStreamsProcMedOut.GetValue(text=True)))
### only one fluid per panel can be changed between mass/volume ...
        
        # load all in-flowing and out-flowing streams
        inputStreams      = []
        outputStreams     = []
        #inputStreamNames  = getInputStreamNamesFromDB(self.selectedProcessID)
        #outputStreamNames = getOutputStreamNamesFromDB(self.selectedProcessID) 
        #for name in inputStreamNames:
        #    stream = InflowingStream(name)
        #    stream.loadFromDB(self.selectedProcessID)
        #    inputStreams.append(stream)
        #for name in outputStreamNames:
        #    stream = OutflowingStream(name)
        #    stream.loadFromDB(self.selectedProcessID)
        #    outputStreams.append(stream)
        tmp = {
            "Questionnaire_id":Status.PId,
            "AlternativeProposalNo":Status.ANo,
            "Process":check(self.tc1.GetValue()),
            "Description":check(self.tc1_1.GetValue()),
            "DBUnitOperation_id":check(findKey(unitOpDict,self.tc3.GetValue(text=True))),
            "ProcType":check(findKey(TRANSPROCTYPES,self.tc2.GetValue(text=True))),             
            "ProcMedDBFluid_id":check(findKey(fluidDict,self.tc4.GetValue(text=True))),
            "PT":check(self.tc5.GetValue()), 
            "PTInFlow":check(None), # now separate for individual streams 
            "PTStartUp":check(self.tc7.GetValue()), 
            "VInFlowCycle":check(None), # now separate for individual streams
            "mInFlowNom":check(sum([s.mInFlowNom is not None and s.mInFlowNom or 0. for s in inputStreams])), # now separate for individual streams
            "VolProcMed":check(self.tc9.GetValue()),
            "ThermalMass":check(self.ThermalMassFloatEntry.GetValue()),
            "QOpProc":check(self.tc10.GetValue()), 
            "HPerDayProc":check(self.page1.HPerDayFloatEntry.GetValue()), 
            "NBatch":check(self.page1.NCyclesFloatEntry.GetValue()), 
            "HBatch":check(self.page1.HCycleFloatEntry.GetValue()), 
            "NDaysProc":check(self.page1.NDaysFloatEntry.GetValue()),
            "PartLoad": 1.0, # PartLoad == 1. for simple schedule
            "ProcMedOut":check(None), # now separate for individual streams
            "PTOutFlow":check(None), # now separate for individual streams
            "HOutFlow":check(None), # now separate for individual streams
            "XOutFlow":check(None), # now separate for individual streams
            "PTFinal":check(None), # now separate for individual streams 
            "VOutFlowCycle":check(None), # now separate for individual streams
            "mOutFlowNom":check(sum([s.mOutFlowNom is not None and s.mOutFlowNom or 0. for s in outputStreams])), # now separate for individual streams
            "HeatRecOK":check(findKey(TRANSYESNO,self.OutputStreamsHeatRecOkChoiceEntry.entry.GetStringSelection())),
            "HeatRecExist":check(findKey(TRANSYESNO,self.InputStreamsHeatRecExistChoiceEntry.entry.GetStringSelection())),
#            "SourceWasteHeat":check(findKey(TRANSYESNO,self.tc20.entry.GetStringSelection())), 	
            "PTInFlowRec":check(None), # now separate for individual streams 
            "SupplyMedDBFluid_id":check(findKey(fluidDict,self.tc22.entry.GetStringSelection())),
            "PipeDuctProc":check(self.tc23.GetValue(text=True)), 
            "TSupply":check(self.tc24.GetValue()), 
            "SupplyMedFlow":check(self.tc25.GetValue()), 
            "UPH":check(self.tc26.GetValue()),
            "heating_cooling":check(self.tcHeating_cooling.GetValue(text=True)),
        }
        process.update(tmp)
        
        try: # set and save detailed schedule parameters
            self.periodSchedule.startup      = self.page3.StartupFloatEntry.GetValue()
            self.periodSchedule.inflow       = self.page3.InflowFloatEntry.GetValue()
            self.periodSchedule.outflow      = self.page3.OutflowFloatEntry.GetValue()
            self.periodSchedule.tolerance    = self.page3.ToleranceFloatEntry.GetValue()
            self.periodSchedule.holidayScale = self.page3.HolidaySpinCtrl.GetValue()
            self.periodSchedule.updateToleranceOffset()
            self.periodSchedule.saveToDB(originalProcessId(process.QProcessData_ID), withHolidays=True)
        except AttributeError: # simple schedule: delete detailed schedule for process
            deleteProcessScheduleFromDB(originalProcessId(process.QProcessData_ID))
            deleteProcessPeriodsFromDB(originalProcessId(process.QProcessData_ID))
            

        print "PanelQ3 (ok-button): process table updated with: ",tmp
        Status.SQL.commit()
        print "PanelQ3 (ok-button): what arrived is this: ",process

        Status.processData.changeInProcess()

        self.selectedProcessName = processName
        self.display()        
    # Schedule type selection
    def OnDetailedScheduleCheckBox(self, event):
        if not self.selectedProcessName:
            logError("No process selected in tab Process data.")
            return
        detailedSchedule = self.page1.DetailedScheduleCheckBox.GetValue()
        self.page1.HPerDayFloatEntry.Enable(not detailedSchedule)
        self.page1.NCyclesFloatEntry.Enable(not detailedSchedule)
        self.page1.HCycleFloatEntry.Enable(not detailedSchedule)
        self.page1.NDaysFloatEntry.Enable(not detailedSchedule)
        self.page2.Enable(detailedSchedule)
        self.page3.Enable(detailedSchedule)
        if detailedSchedule:
            try: # try to load existing detailed schedule for selected process
                self.periodSchedule = PeriodSchedule(self.selectedProcessName)
                self.periodSchedule.loadFromDB(originalProcessId(self.selectedProcessID))
            except AttributeError: # no process selected
                pass
            except ScheduleNotFoundError: # no detailed schedule exists yet
                pass
        else:
            self.periodSchedule = None

    # Profile
    def OnProfileDailyScaleSpinCtrlChanged(self, event):
        self.page2.ProfileDailyScaleSlider.SetValue(self.page2.ProfileDailyScaleSpinCtrl.GetValue())
    
    def OnProfileDailyScaleSliderChanged(self, event):
        self.page2.ProfileDailyScaleSpinCtrl.SetValue(self.page2.ProfileDailyScaleSlider.GetValue())
        
    def OnProfileDailyAddButtonClicked(self, event):
        newProfileDailyFromHour    = self.page2.ProfileDailyFromHourSpinCtrl.GetValue()
        newProfileDailyFromMinute  = self.page2.ProfileDailyFromMinuteSpinCtrl.GetValue()
        newProfileDailyUntilHour   = self.page2.ProfileDailyUntilHourSpinCtrl.GetValue()
        newProfileDailyUntilMinute = self.page2.ProfileDailyUntilMinuteSpinCtrl.GetValue()
        newProfileDailyScale       = self.page2.ProfileDailyScaleSpinCtrl.GetValue()
        
        newProfileDailyListCtrlItemIndex = self.page2.ProfileDailyListCtrl.InsertStringItem(self.page2.ProfileDailyListCtrlFromColumnIndex, "%02d:%02d" % (newProfileDailyFromHour, newProfileDailyFromMinute))        
        self.page2.ProfileDailyListCtrl.SetStringItem(newProfileDailyListCtrlItemIndex, self.page2.ProfileDailyListCtrlUntilColumnIndex,    "%02d:%02d" % (newProfileDailyUntilHour, newProfileDailyUntilMinute))
        self.page2.ProfileDailyListCtrl.SetStringItem(newProfileDailyListCtrlItemIndex, self.page2.ProfileDailyListCtrlScaleColumnIndex, str(newProfileDailyScale))
        
        
    def OnProfileDailyChangeButtonClicked(self, event):
        newProfileDailyFromHour    = self.page2.ProfileDailyFromHourSpinCtrl.GetValue()
        newProfileDailyFromMinute  = self.page2.ProfileDailyFromMinuteSpinCtrl.GetValue()
        newProfileDailyUntilHour   = self.page2.ProfileDailyUntilHourSpinCtrl.GetValue()
        newProfileDailyUntilMinute = self.page2.ProfileDailyUntilMinuteSpinCtrl.GetValue()
        newProfileDailyScale       = self.page2.ProfileDailyScaleSpinCtrl.GetValue()
        
        selectedItemIndex = self.page2.ProfileDailyListCtrl.GetSelected()
        for itemIndex in selectedItemIndex:
            self.page2.ProfileDailyListCtrl.SetStringItem(itemIndex, self.page2.ProfileDailyListCtrlFromColumnIndex,  "%02d:%02d" % (newProfileDailyFromHour, newProfileDailyFromMinute))
            self.page2.ProfileDailyListCtrl.SetStringItem(itemIndex, self.page2.ProfileDailyListCtrlUntilColumnIndex, "%02d:%02d" % (newProfileDailyUntilHour, newProfileDailyUntilMinute))
            self.page2.ProfileDailyListCtrl.SetStringItem(itemIndex, self.page2.ProfileDailyListCtrlScaleColumnIndex, str(newProfileDailyScale))
            
    def OnProfileDailyRemoveButtonClicked(self, event):
        selectedItemIndex = self.page2.ProfileDailyListCtrl.GetSelected()
        selectedItemIndex.reverse()
        for itemIndex in selectedItemIndex:
            self.page2.ProfileDailyListCtrl.DeleteItem(itemIndex)

    def OnProfileDailyListCtrlItemSelected(self, event):
        selectedItemIndex = event.m_itemIndex
        (fromHour, fromMinute)   = self.page2.ProfileDailyListCtrl.GetItem(selectedItemIndex, self.page2.ProfileDailyListCtrlFromColumnIndex).GetText().split(':', 2)
        (untilHour, untilMinute) = self.page2.ProfileDailyListCtrl.GetItem(selectedItemIndex, self.page2.ProfileDailyListCtrlUntilColumnIndex).GetText().split(':', 2)
        scale                    = int(self.page2.ProfileDailyListCtrl.GetItem(selectedItemIndex, self.page2.ProfileDailyListCtrlScaleColumnIndex).GetText())
        self.page2.ProfileDailyFromHourSpinCtrl.SetValue(int(fromHour))
        self.page2.ProfileDailyFromMinuteSpinCtrl.SetValue(int(fromMinute))
        self.page2.ProfileDailyUntilHourSpinCtrl.SetValue(int(untilHour))
        self.page2.ProfileDailyUntilMinuteSpinCtrl.SetValue(int(untilMinute))
        self.page2.ProfileDailyScaleSpinCtrl.SetValue(scale)
        self.page2.ProfileDailyScaleSlider.SetValue(scale)
          
    def OnProfileWeeklyAddButtonClicked(self, event):
        if self.page2.ProfileDailyListCtrl.GetItemCount() < 1:
            logError("No daily profile defined.")
            return
        
        newProfileWeeklyName      = self.page2.ProfileWeeklyNameTextCtrl.GetValue()
        if not newProfileWeeklyName:
            logError("No name given for weekly profile.")
            return

        newProfileWeeklyMonday    = self.page2.ProfileWeeklyMondayCheckBox.GetValue()
        newProfileWeeklyTuesday   = self.page2.ProfileWeeklyTuesdayCheckBox.GetValue()
        newProfileWeeklyWednesday = self.page2.ProfileWeeklyWednesdayCheckBox.GetValue()
        newProfileWeeklyThursday  = self.page2.ProfileWeeklyThursdayCheckBox.GetValue()
        newProfileWeeklyFriday    = self.page2.ProfileWeeklyFridayCheckBox.GetValue()
        newProfileWeeklySaturday  = self.page2.ProfileWeeklySaturdayCheckBox.GetValue()
        newProfileWeeklySunday    = self.page2.ProfileWeeklySundayCheckBox.GetValue()
        
        newWeeklyProfile = WeeklyProfile(newProfileWeeklyName)
        for itemIndex in range(self.page2.ProfileDailyListCtrl.GetItemCount()):
            newProfileDailyFrom  = datetime.strptime(self.page2.ProfileDailyListCtrl.GetItem(itemIndex, self.page2.ProfileDailyListCtrlFromColumnIndex).GetText(), '%H:%M').time()
            newProfileDailyUntil = datetime.strptime(self.page2.ProfileDailyListCtrl.GetItem(itemIndex, self.page2.ProfileDailyListCtrlUntilColumnIndex).GetText(), '%H:%M').time()
            newProfileDailyScale = int(self.page2.ProfileDailyListCtrl.GetItem(itemIndex, self.page2.ProfileDailyListCtrlScaleColumnIndex).GetText())
            newWeeklyProfile.addInterval(newProfileDailyFrom, newProfileDailyUntil, newProfileDailyScale)
        newWeeklyProfile.setMonday(newProfileWeeklyMonday)
        newWeeklyProfile.setTuesday(newProfileWeeklyTuesday)
        newWeeklyProfile.setWednesday(newProfileWeeklyWednesday)
        newWeeklyProfile.setThursday(newProfileWeeklyThursday)
        newWeeklyProfile.setFriday(newProfileWeeklyFriday)
        newWeeklyProfile.setSaturday(newProfileWeeklySaturday)
        newWeeklyProfile.setSunday(newProfileWeeklySunday)
        self.weeklyProfile.append(newWeeklyProfile)
        
        newWeeklyProfile.saveToDB()
            
        newProfileWeeklyListCtrlItemIndex = self.page2.ProfileWeeklyListCtrl.InsertStringItem(self.page2.ProfileWeeklyListCtrlNameColumnIndex, newProfileWeeklyName)        
        self.page2.ProfileWeeklyListCtrl.SetStringItem(newProfileWeeklyListCtrlItemIndex, self.page2.ProfileWeeklyListCtrlScheduleColumnIndex, "<click to see>")
        
        
    def OnProfileWeeklyChangeButtonClicked(self, event):
        if self.page2.ProfileDailyListCtrl.GetItemCount() < 1:
            logError("No daily profile defined.")
            return
        
        newProfileWeeklyName      = self.page2.ProfileWeeklyNameTextCtrl.GetValue()
        if not newProfileWeeklyName:
            logError("No name given for weekly profile.")
            return
        
        newProfileWeeklyMonday    = self.page2.ProfileWeeklyMondayCheckBox.GetValue()
        newProfileWeeklyTuesday   = self.page2.ProfileWeeklyTuesdayCheckBox.GetValue()
        newProfileWeeklyWednesday = self.page2.ProfileWeeklyWednesdayCheckBox.GetValue()
        newProfileWeeklyThursday  = self.page2.ProfileWeeklyThursdayCheckBox.GetValue()
        newProfileWeeklyFriday    = self.page2.ProfileWeeklyFridayCheckBox.GetValue()
        newProfileWeeklySaturday  = self.page2.ProfileWeeklySaturdayCheckBox.GetValue()
        newProfileWeeklySunday    = self.page2.ProfileWeeklySundayCheckBox.GetValue()
        
        newWeeklyProfile = WeeklyProfile(newProfileWeeklyName)
        for itemIndex in range(self.page2.ProfileDailyListCtrl.GetItemCount()):
            newProfileDailyFrom  = datetime.strptime(self.page2.ProfileDailyListCtrl.GetItem(itemIndex, self.page2.ProfileDailyListCtrlFromColumnIndex).GetText(), '%H:%M').time()
            newProfileDailyUntil = datetime.strptime(self.page2.ProfileDailyListCtrl.GetItem(itemIndex, self.page2.ProfileDailyListCtrlUntilColumnIndex).GetText(), '%H:%M').time()
            newProfileDailyScale = int(self.page2.ProfileDailyListCtrl.GetItem(itemIndex, self.page2.ProfileDailyListCtrlScaleColumnIndex).GetText())
            newWeeklyProfile.addInterval(newProfileDailyFrom, newProfileDailyUntil, newProfileDailyScale)
        newWeeklyProfile.setMonday(newProfileWeeklyMonday)
        newWeeklyProfile.setTuesday(newProfileWeeklyTuesday)
        newWeeklyProfile.setWednesday(newProfileWeeklyWednesday)
        newWeeklyProfile.setThursday(newProfileWeeklyThursday)
        newWeeklyProfile.setFriday(newProfileWeeklyFriday)
        newWeeklyProfile.setSaturday(newProfileWeeklySaturday)
        newWeeklyProfile.setSunday(newProfileWeeklySunday)
        newWeeklyProfile.saveToDB()
        
        selectedItemIndex = self.page2.ProfileWeeklyListCtrl.GetSelected()
        for itemIndex in selectedItemIndex:
            oldWeeklyProfileName = self.page2.ProfileWeeklyListCtrl.GetItem(itemIndex, self.page2.ProfileWeeklyListCtrlNameColumnIndex).GetText()
            try:
                changeIndex = getProfileIndexByName(oldWeeklyProfileName, self.weeklyProfile)
            except ProfileNotFoundError:
                    logError("Cannot find profile by name. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
                    return
            self.weeklyProfile[changeIndex].deleteFromDB()
            self.weeklyProfile[changeIndex] = newWeeklyProfile
            self.page2.ProfileWeeklyListCtrl.SetStringItem(itemIndex, self.page2.ProfileWeeklyListCtrlNameColumnIndex, newWeeklyProfile.id)
        
    def OnProfileWeeklyRemoveButtonClicked(self, event):   
        selectedItemIndex = self.page2.ProfileWeeklyListCtrl.GetSelected()
        selectedItemIndex.reverse()
        for itemIndex in selectedItemIndex:
            removeWeeklyProfileName = self.page2.ProfileWeeklyListCtrl.GetItem(itemIndex, self.page2.ProfileWeeklyListCtrlNameColumnIndex).GetText()
            try:
                removeIndex = getProfileIndexByName(removeWeeklyProfileName, self.weeklyProfile)
            except ProfileNotFoundError:
                logError("Cannot find profile by name. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
                return
            self.weeklyProfile[removeIndex].deleteFromDB()
            del self.weeklyProfile[removeIndex]
            self.page2.ProfileWeeklyListCtrl.DeleteItem(itemIndex)
            
    def OnProfileWeeklyListCtrlItemSelected(self, event):
        selectedItemIndex    = event.m_itemIndex
        selectedProfileName  = self.page2.ProfileWeeklyListCtrl.GetItem(selectedItemIndex, self.page2.ProfileWeeklyListCtrlNameColumnIndex).GetText()
        try:
            selectedProfileIndex = getProfileIndexByName(selectedProfileName, self.weeklyProfile)
        except ProfileNotFoundError:
            logError("Cannot find profile by name. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return
        weeklyProfile = self.weeklyProfile[selectedProfileIndex]
        self.page2.ProfileWeeklyNameTextCtrl.SetValue(weeklyProfile.id)
        self.page2.ProfileWeeklyMondayCheckBox.SetValue(weeklyProfile.weekday['monday'])
        self.page2.ProfileWeeklyTuesdayCheckBox.SetValue(weeklyProfile.weekday['tuesday'])
        self.page2.ProfileWeeklyWednesdayCheckBox.SetValue(weeklyProfile.weekday['wednesday'])
        self.page2.ProfileWeeklyThursdayCheckBox.SetValue(weeklyProfile.weekday['thursday'])
        self.page2.ProfileWeeklyFridayCheckBox.SetValue(weeklyProfile.weekday['friday'])
        self.page2.ProfileWeeklySaturdayCheckBox.SetValue(weeklyProfile.weekday['saturday'])
        self.page2.ProfileWeeklySundayCheckBox.SetValue(weeklyProfile.weekday['sunday'])
        self.page2.ProfileDailyListCtrl.DeleteAllItems()
        for (start, stop, scale) in weeklyProfile.getProfile():
            newProfileDailyListCtrlItemIndex = self.page2.ProfileDailyListCtrl.InsertStringItem(self.page2.ProfileDailyListCtrlFromColumnIndex, start.strftime('%H:%M'))        
            self.page2.ProfileDailyListCtrl.SetStringItem(newProfileDailyListCtrlItemIndex, self.page2.ProfileDailyListCtrlUntilColumnIndex,    stop.strftime('%H:%M'))
            self.page2.ProfileDailyListCtrl.SetStringItem(newProfileDailyListCtrlItemIndex, self.page2.ProfileDailyListCtrlScaleColumnIndex, str(scale))
            
    # Schedule
    def OnPeriodScaleSpinCtrlChanged(self, event):
        self.page3.PeriodScaleSlider.SetValue(self.page3.PeriodScaleSpinCtrl.GetValue())
    
    def OnPeriodScaleSliderChanged(self, event):
        self.page3.PeriodScaleSpinCtrl.SetValue(self.page3.PeriodScaleSlider.GetValue())

    def OnHolidaySpinCtrlChanged(self, event):
        self.page3.HolidaySlider.SetValue(self.page3.HolidaySpinCtrl.GetValue())
    
    def OnHolidaySliderChanged(self, event):
        self.page3.HolidaySpinCtrl.SetValue(self.page3.HolidaySlider.GetValue())
        
    def OnScheduleAddButtonClicked(self, event):
        newScheduleListCtrlItemIndex = self.addPeriod()
        self.page3.ScheduleListCtrl.Select(newScheduleListCtrlItemIndex)
        self.fillSchedule()
        addPeriodFromDate  = self.page3.PeriodFromDatePicker.GetValue()
        addPeriodFromDate  = date(addPeriodFromDate.GetYear(), addPeriodFromDate.GetMonth() + 1, addPeriodFromDate.GetDay())
        Status.int.setGraphicsData('SchedulePeriodWeeklyProfile', self.periodSchedule.getWeeklyProfile(addPeriodFromDate))
        paramList = {'labels'       : 0, # labels column
                   'data'         : 0,                      # data column for this graph
                   'key'         : 'SchedulePeriodWeeklyProfile',                # key for Interface
                   'title'       : _U('Period Weekly Profile'),           # title of the graph
                   'backcolor'   : GRAPH_BACKGROUND_COLOR, # graph background color
                   'ignoredrows' : []}            # rows that should not be plotted
        dummy = MatPanel(self.page3.SchedulePeriodWeeklyProfilePanel, wx.Panel, drawFigure, paramList)
        del dummy
        self.page3.SchedulePeriodWeeklyProfilePanel.draw()
        
    def addPeriod(self):
        selectedProfileItemIndex = self.page3.ProfileListCtrl.GetSelected()
        
        if len(selectedProfileItemIndex) < 1:
            logError("No weekly profile selected.")
            raise ScheduleNoProfilesError 
        
        addPeriodFromDate  = self.page3.PeriodFromDatePicker.GetValue()
        addPeriodFromDate  = date(addPeriodFromDate.GetYear(), addPeriodFromDate.GetMonth() + 1, addPeriodFromDate.GetDay())
        addPeriodUntilDate = self.page3.PeriodUntilDatePicker.GetValue()
        addPeriodUntilDate = date(addPeriodUntilDate.GetYear(), addPeriodUntilDate.GetMonth() + 1, addPeriodUntilDate.GetDay())
        addPeriodStep      = self.page3.PeriodStepSpinCtrl.GetValue()
        addPeriodScale     = self.page3.PeriodScaleSpinCtrl.GetValue()
        
        addProfileNames = []
        for profileItemIndex in selectedProfileItemIndex:
            addProfileNames.append(self.page3.ProfileListCtrl.GetItem(profileItemIndex, self.page2.ProfileWeeklyListCtrlNameColumnIndex).GetText())
        newScheduleListCtrlItemIndex = self.page3.ScheduleListCtrl.InsertStringItem(self.page3.ScheduleListCtrlFromColumnIndex, addPeriodFromDate.strftime('%m-%d'))
        self.page3.ScheduleListCtrl.SetStringItem(newScheduleListCtrlItemIndex, self.page3.ScheduleListCtrlUntilColumnIndex, addPeriodUntilDate.strftime('%m-%d'))
        self.page3.ScheduleListCtrl.SetStringItem(newScheduleListCtrlItemIndex, self.page3.ScheduleListCtrlStepColumnIndex, str(addPeriodStep))
        self.page3.ScheduleListCtrl.SetStringItem(newScheduleListCtrlItemIndex, self.page3.ScheduleListCtrlScaleColumnIndex, str(addPeriodScale))
        self.page3.ScheduleListCtrl.SetStringItem(newScheduleListCtrlItemIndex, self.page3.ScheduleListCtrlProfileColumnIndex, ', '.join(addProfileNames))
        
        return newScheduleListCtrlItemIndex
        
    def fillSchedule(self):
        # Remove all process periods and period profiles from DB and schedule, to refill later
        self.periodSchedule.clearSchedule()
        self.periodSchedule.clearHolidays()
        dbProcessPeriodRows = Status.DB.process_periods.qprocessdata_QProcessData_ID[originalProcessId(self.selectedProcessID)]
        while True:
            try:
                dbProcessPeriod = dbProcessPeriodRows.pop()
            except IndexError:
                break
            dbProcessPeriodProfileRows = Status.DB.process_period_profiles.process_periods_id[dbProcessPeriod.id]
            while True:
                try:
                    dbProcessPeriodProfile = dbProcessPeriodProfileRows.pop()
                except IndexError:
                    break
                dbProcessPeriodProfile.delete()
            dbProcessPeriod.delete()
        # Refill process periods and schedule 
        for itemIndex in range(self.page3.ScheduleListCtrl.GetItemCount()):
            addProfileNames    = self.page3.ScheduleListCtrl.GetItem(itemIndex, self.page3.ScheduleListCtrlProfileColumnIndex).GetText()
            if not addProfileNames: continue
            addProfileNames    = addProfileNames.split(', ')
            addPeriodFromDate  = datetime.strptime(self.page3.ScheduleListCtrl.GetItem(itemIndex, self.page3.ScheduleListCtrlFromColumnIndex).GetText(), '%m-%d').date().replace(year=periodReference.year)
            addPeriodUntilDate = datetime.strptime(self.page3.ScheduleListCtrl.GetItem(itemIndex, self.page3.ScheduleListCtrlUntilColumnIndex).GetText(), '%m-%d').date().replace(year=periodReference.year)
            addPeriodStep      = int(self.page3.ScheduleListCtrl.GetItem(itemIndex, self.page3.ScheduleListCtrlStepColumnIndex).GetText())
            addPeriodScale     = int(self.page3.ScheduleListCtrl.GetItem(itemIndex, self.page3.ScheduleListCtrlScaleColumnIndex).GetText())
            # Save period and process period parameters to DB
            try:
                dbPeriodId = Status.DB.periods.start[addPeriodFromDate].stop[addPeriodUntilDate].id.column()[0]
            except LookupError: # Save period to DB if new
                dbPeriodId = Status.DB.periods.insert({'start': addPeriodFromDate, 'stop': addPeriodUntilDate})
            except IndexError:
                logError("Cannot find period id in data base. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
                return
            dbProcessPeriodId = Status.DB.process_periods.insert({'qprocessdata_QProcessData_ID': originalProcessId(self.selectedProcessID), 'periods_id': dbPeriodId, 'step': addPeriodStep, 'scale': addPeriodScale})
    
            for addProfileName in (name for name in addProfileNames if name != ''):
                try:
                    addProfile = self.weeklyProfile[getProfileIndexByName(addProfileName, self.weeklyProfile)]
                except ProfileNotFoundError:
                    logError("Cannot find profile by name. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
                    return
                # Save period profiles to DB
                try:
                    Status.DB.process_period_profiles.insert({'process_periods_id': dbProcessPeriodId, 'profiles_id': Status.DB.profiles.name[addProfileName].id.column()[0]})
                except LookupError:
                    logError("Cannot find profile name in data base. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
                    return
                except IndexError:
                    logError("Profile has no id in data base. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
                    return
                
                self.periodSchedule.addPeriodProfile(addPeriodFromDate, addPeriodUntilDate, addPeriodStep, addPeriodScale, addProfile)
            
        # set global parameters
        self.periodSchedule.startup      = self.page3.StartupFloatEntry.GetValue()
        self.periodSchedule.inflow       = self.page3.InflowFloatEntry.GetValue()
        self.periodSchedule.outflow      = self.page3.OutflowFloatEntry.GetValue()
        self.periodSchedule.tolerance    = self.page3.ToleranceFloatEntry.GetValue()
        self.periodSchedule.holidayScale = self.page3.HolidaySpinCtrl.GetValue()
            
        # add global holiday periods
        try:
            holidayStart = Status.DB.questionnaire.Questionnaire_ID[Status.PId].NoProdStart_1.column().pop()
            holidayStop  = Status.DB.questionnaire.Questionnaire_ID[Status.PId].NoProdStop_1.column().pop()
        except IndexError:
            logError("Data base inconsistency. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return
        if holidayStart and holidayStop:
            self.periodSchedule.addHolidays(holidayStart, holidayStop)
        try:
            holidayStart = Status.DB.questionnaire.Questionnaire_ID[Status.PId].NoProdStart_2.column().pop()
            holidayStop  = Status.DB.questionnaire.Questionnaire_ID[Status.PId].NoProdStop_2.column().pop()
        except IndexError:
            logError("Data base inconsistency. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return
        if holidayStart and holidayStop:
            self.periodSchedule.addHolidays(holidayStart, holidayStop)
        try:
            holidayStart = Status.DB.questionnaire.Questionnaire_ID[Status.PId].NoProdStart_3.column().pop()
            holidayStop  = Status.DB.questionnaire.Questionnaire_ID[Status.PId].NoProdStop_3.column().pop()
        except IndexError:
            logError("Data base inconsistency. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return
        if holidayStart and holidayStop:
            self.periodSchedule.addHolidays(holidayStart, holidayStop)
            
        # save period schedule to DB
        self.periodSchedule.saveToDB(originalProcessId(self.selectedProcessID), withHolidays=True)
        
        # display calculated simple schedule parameters for pick up by OnButtonOk
        self.page1.HPerDayFloatEntry.SetValue(str(self.periodSchedule.getOperationHoursPerDay(withHolidays=True, withTolerance=False)))
        self.page1.NCyclesFloatEntry.SetValue(str(self.periodSchedule.getNumberOfBatchesPerDay(withHolidays=True, withTolerance=False)))
        self.page1.HCycleFloatEntry.SetValue(str(self.periodSchedule.getDurationHoursPerBatch(withHolidays=True, withTolerance=False)))
        self.page1.NDaysFloatEntry.SetValue(str(self.periodSchedule.getNumberOfOperationDays(withHolidays=True, withTolerance=False)))

    def OnScheduleChangeButtonClicked(self, event):
        # add new and remove selected
        # remove first fails for addition errors
        
        if len(self.page3.ScheduleListCtrl.GetSelected()) < 1:
            logError("No period selected to change.")
            return 

        # add new
        try:
            newScheduleListCtrlItemIndex = self.addPeriod()
        except ScheduleNoProfilesError:
            return
        
        # remove selected
        selectedItemIndex = self.page3.ScheduleListCtrl.GetSelected()
        selectedItemIndex.reverse()
        for itemIndex in selectedItemIndex:
            self.page3.ScheduleListCtrl.DeleteItem(itemIndex)
        
        # select changed
        self.page3.ScheduleListCtrl.Select(newScheduleListCtrlItemIndex)
        
        # update schedule
        self.fillSchedule()
        addPeriodFromDate  = self.page3.PeriodFromDatePicker.GetValue()
        addPeriodFromDate  = date(addPeriodFromDate.GetYear(), addPeriodFromDate.GetMonth() + 1, addPeriodFromDate.GetDay())
        Status.int.setGraphicsData('SchedulePeriodWeeklyProfile', self.periodSchedule.getWeeklyProfile(addPeriodFromDate))
        paramList = {'labels'       : 0, # labels column
                   'data'         : 0,                      # data column for this graph
                   'key'         : 'SchedulePeriodWeeklyProfile',                # key for Interface
                   'title'       : _U('Period Weekly Profile'),           # title of the graph
                   'backcolor'   : GRAPH_BACKGROUND_COLOR, # graph background color
                   'ignoredrows' : []}            # rows that should not be plotted
        dummy = MatPanel(self.page3.SchedulePeriodWeeklyProfilePanel, wx.Panel, drawFigure, paramList)
        del dummy
        self.page3.SchedulePeriodWeeklyProfilePanel.draw()
        
    def OnScheduleRemoveButtonClicked(self, event):
        selectedItemIndex = self.page3.ScheduleListCtrl.GetSelected()
        selectedItemIndex.reverse()
        for itemIndex in selectedItemIndex:
            self.page3.ScheduleListCtrl.DeleteItem(itemIndex)
        self.fillSchedule()
        Status.int.setGraphicsData('SchedulePeriodWeeklyProfile', [0] * int(WEEK))
        paramList = {'labels'       : 0, # labels column
                   'data'         : 0,                      # data column for this graph
                   'key'         : 'SchedulePeriodWeeklyProfile',                # key for Interface
                   'title'       : _U('Period Weekly Profile'),           # title of the graph
                   'backcolor'   : GRAPH_BACKGROUND_COLOR, # graph background color
                   'ignoredrows' : []}            # rows that should not be plotted
        dummy = MatPanel(self.page3.SchedulePeriodWeeklyProfilePanel, wx.Panel, drawFigure, paramList)
        del dummy
        self.page3.SchedulePeriodWeeklyProfilePanel.draw()          
    
    def OnScheduleListCtrlItemSelected(self, event):
        if not self.selectedProcessName:
            logError("No process selected in tab Process data.")
            return
        selectedItemIndex    = event.m_itemIndex
        dt = wx.DateTime()
        dt.ParseDate(self.page3.ScheduleListCtrl.GetItem(selectedItemIndex, self.page3.ScheduleListCtrlFromColumnIndex).GetText())
        self.page3.PeriodFromDatePicker.SetValue(dt)
        dt.ParseDate(self.page3.ScheduleListCtrl.GetItem(selectedItemIndex, self.page3.ScheduleListCtrlUntilColumnIndex).GetText())
        self.page3.PeriodUntilDatePicker.SetValue(dt)
        try:
            self.page3.PeriodStepSpinCtrl.SetValue(int(self.page3.ScheduleListCtrl.GetItem(selectedItemIndex, self.page3.ScheduleListCtrlStepColumnIndex).GetText()))
            self.page3.PeriodScaleSpinCtrl.SetValue(int(self.page3.ScheduleListCtrl.GetItem(selectedItemIndex, self.page3.ScheduleListCtrlScaleColumnIndex).GetText()))
            self.page3.PeriodScaleSlider.SetValue(int(self.page3.ScheduleListCtrl.GetItem(selectedItemIndex, self.page3.ScheduleListCtrlScaleColumnIndex).GetText()))
        except ValueError: # Invalid values for step or scale -> empty period, leave controls as already set
            pass
        #self.page3.HolidaySpinCtrl.SetValue(int(self.page3.ScheduleListCtrl.GetItem(selectedItemIndex, self.page3.ScheduleListCtrlHolidayColumnIndex).GetText()))
        #self.page3.HolidaySlider.SetValue(int(self.page3.ScheduleListCtrl.GetItem(selectedItemIndex, self.page3.ScheduleListCtrlHolidayColumnIndex).GetText()))
        selectedProfileNames = self.page3.ScheduleListCtrl.GetItem(selectedItemIndex, self.page3.ScheduleListCtrlProfileColumnIndex).GetText().split(', ')
        for profileItemIndex in range(self.page3.ProfileListCtrl.GetItemCount()):
            self.page3.ProfileListCtrl.Select(profileItemIndex, self.page3.ProfileListCtrl.GetItem(profileItemIndex, self.page2.ProfileWeeklyListCtrlNameColumnIndex).GetText() in selectedProfileNames)
        Status.int.setGraphicsData('SchedulePeriodWeeklyProfile', self.periodSchedule.getWeeklyProfile(datetime.strptime(self.page3.ScheduleListCtrl.GetItem(selectedItemIndex, self.page3.ScheduleListCtrlFromColumnIndex).GetText(), '%m-%d')))
        paramList = {'labels'       : 0, # labels column
                   'data'         : 0,                      # data column for this graph
                   'key'         : 'SchedulePeriodWeeklyProfile',                # key for Interface
                   'title'       : _U('Period Weekly Profile'),           # title of the graph
                   'backcolor'   : GRAPH_BACKGROUND_COLOR, # graph background color
                   'ignoredrows' : []}            # rows that should not be plotted
        dummy = MatPanel(self.page3.SchedulePeriodWeeklyProfilePanel, wx.Panel, drawFigure, paramList)
        del dummy
        self.page3.SchedulePeriodWeeklyProfilePanel.draw()
        
    # Input streams
    def saveInputStream(self, name):
        stream = InflowingStream(name,
                                 PTInFlow=self.InputStreamsPTInFlowFloatEntry.GetValue(),
                                 PTInFlowRec=self.InputStreamsPTInFlowRecFloatEntry.GetValue(),
                                 VInFlowCycle=self.InputStreamsVInFlowCycleFloatEntry.GetValue(),
                                 mInFlowNom=self.InputStreamsMInFlowNomFloatEntry.GetValue())
        if self.InputStreamsProcMedDBFluidChoiceEntry.GetValue() == 0:
            stream.Medium = None
        else:
            stream.Medium = self.InputStreamsProcMedDBFluidChoiceEntry.GetValue(text=True)
        if self.InputStreamsHeatRecExistChoiceEntry.GetValue() == 0:
            stream.HeatRecExist = None
        else:
            stream.HeatRecExist = (TRANSYESNO['yes'] == self.InputStreamsHeatRecExistChoiceEntry.GetValue(text=True))
            if stream.HeatRecExist == False:
                stream.PTInFlowRec = stream.PTInFlow
        try:
            stream.saveToDB(self.selectedProcessID)
        except InconsistentDataBaseError:
            logError("Data base inconsistency. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return None
        return name
    
    def OnInputStreamsAddButtonClicked(self, event):
        if self.checkIfAllowed()==False:
            return
        newInputStreamName = self.InputStreamsNameTextCtrl.GetValue()
        if not newInputStreamName:
            logError("No name given for in-flowing stream.")
            return
        try:
            if newInputStreamName in getInflowingStreamNamesFromDB(self.selectedProcessID):
                logError("Stream '%s' already defined. You may select and change it instead." % newInputStreamName)
                return
            name = self.saveInputStream(newInputStreamName)
        except AttributeError:
            logError("No process selected in tab Process data.")
            return
        if name is not None:
            self.InputStreamsListBox.Append(name)
            self.InputStreamsListBox.SetSelection(-1)
        
    def OnInputStreamsChangeButtonClicked(self, event):
        if self.checkIfAllowed()==False:
            return
        changeInputStreamName = self.InputStreamsNameTextCtrl.GetValue()
        if not changeInputStreamName:
            logError("No name given for in-flowing stream.")
            return
        try:
            name = self.saveInputStream(changeInputStreamName)
        except AttributeError:
            logError("No process selected in tab Process data.")
            return
        if name is not None:
            self.InputStreamsListBox.SetString(self.InputStreamsListBox.GetSelection(), name)
        self.OnInputStreamsListBoxItemSelected(None)
        
        
    def OnInputStreamsRemoveButtonClicked(self, event):
        if self.checkIfAllowed()==False:
            return
        selectedItemIndex = self.InputStreamsListBox.GetSelection()
        if selectedItemIndex == -1: # no selection
            return
        stream = InflowingStream(self.InputStreamsListBox.GetString(selectedItemIndex))
        try:
            stream.deleteFromDB(self.selectedProcessID)
        except AttributeError:
            logError("No process selected in tab Process data.")
            return
        self.InputStreamsListBox.Delete(selectedItemIndex)
    
    def OnInputStreamsListBoxItemSelected(self, event):
        selectedItemIndex = self.InputStreamsListBox.GetSelection()
        if selectedItemIndex == -1: # no selection
            return
        stream = InflowingStream(self.InputStreamsListBox.GetString(selectedItemIndex))
        try:
            stream.loadFromDB(self.selectedProcessID)
        except AttributeError:
            logError("No process selected in tab Process data.")
            return
        except ProcessStreamsNotFoundError, StreamNotFoundError:
            logError("Cannot find stream by name. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return
        except FluidNotFoundError:
            logError("Cannot find fluid medium. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return
        except InconsistentDataBaseError:
            logError("Data base inconsistency. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return
        self.InputStreamsNameTextCtrl.SetValue(stream.Name)
        if stream.Medium is None:
            self.InputStreamsProcMedDBFluidChoiceEntry.SetValue(0)
        else:
            self.InputStreamsProcMedDBFluidChoiceEntry.SetValue(stream.Medium)
        self.InputStreamsPTInFlowFloatEntry.SetValue(stream.PTInFlow)
        self.InputStreamsVInFlowCycleFloatEntry.SetValue(stream.VInFlowCycle)
        self.InputStreamsMInFlowNomFloatEntry.SetValue(stream.mInFlowNom)
        if stream.HeatRecExist is None:
            self.InputStreamsHeatRecExistChoiceEntry.SetValue(0)
        else:
            self.InputStreamsHeatRecExistChoiceEntry.SetValue(stream.HeatRecExist and TRANSYESNO['yes'] or TRANSYESNO['no'])
            self.InputStreamsAfterHeatRecoveryStaticBoxSizer.Enable(stream.HeatRecExist)
            self.InputStreamsPTInFlowRecFloatEntry.Enable(stream.HeatRecExist)
        self.InputStreamsPTInFlowRecFloatEntry.SetValue(stream.PTInFlowRec)
        
    def OnInputStreamsPTInFlowValueChanged(self, event):
        if self.checkIfAllowed()==False:
            return
        try:
            if not self.inputStreamsHeatRec:
                self.InputStreamsPTInFlowRecFloatEntry.SetValue(event.GetString())
        except AttributeError:
            pass
        
    def OnInputStreamsPTInFlowUnitChanged(self, event):
        if self.checkIfAllowed()==False:
            return
        try:
            if not self.inputStreamsHeatRec: 
                self.InputStreamsPTInFlowRecFloatEntry.setUnit(self.InputStreamsPTInFlowFloatEntry.GetUnit(text=False))
                event = wx.CommandEvent(wx.EVT_CHOICE.typeId)
                event.SetString(self.InputStreamsPTInFlowFloatEntry.GetUnit(text=True))
                wx.PostEvent(self.InputStreamsPTInFlowRecFloatEntry.units, event)
        except AttributeError:
            pass
        
    def OnInputStreamsHeatRecExistChoice(self, event):
        if self.checkIfAllowed()==False:
            return
        self.inputStreamsHeatRec = TRANSYESNO['yes'] == event.GetString()
        self.InputStreamsAfterHeatRecoveryStaticBoxSizer.Enable(self.inputStreamsHeatRec)
        self.InputStreamsPTInFlowRecFloatEntry.Enable(self.inputStreamsHeatRec)
        if not self.inputStreamsHeatRec:
            self.InputStreamsPTInFlowRecFloatEntry.setUnit(self.InputStreamsPTInFlowFloatEntry.GetUnit(text=False))
            self.InputStreamsPTInFlowRecFloatEntry.SetValue(self.InputStreamsPTInFlowFloatEntry.GetValue())
    
    # Output streams
    def saveOutputStream(self, name):
        stream = OutflowingStream(name,
                                 PTOutFlow=self.OutputStreamsPTOutFlowFloatEntry.GetValue(),
                                 HOutFlow=self.OutputStreamsHOutFlowFloatEntry.GetValue(),
                                 XOutFlow=self.OutputStreamsXOutFlowFloatEntry.GetValue(),
                                 PTFinal=self.OutputStreamsPTFinalFloatEntry.GetValue(),
                                 VOutFlowCycle=self.OutputStreamsVOutFlowCycleFloatEntry.GetValue(),
                                 mOutFlowNom=self.OutputStreamsMOutFlowNomFloatEntry.GetValue())
        if self.OutputStreamsProcMedOutChoiceEntry.GetValue() == 0:
            stream.Medium = None
        else:
            stream.Medium = self.OutputStreamsProcMedOutChoiceEntry.GetValue(text=True)
        if self.OutputStreamsHeatRecOkChoiceEntry.GetValue() == 0:
            stream.HeatRecOK = None
        else:
            stream.HeatRecOK = (TRANSYESNO['yes'] == self.OutputStreamsHeatRecOkChoiceEntry.GetValue(text=True))
        try:
            stream.saveToDB(self.selectedProcessID)
        except InconsistentDataBaseError:
            logError("Data base inconsistency. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return None
        return name
    
    def OnOutputStreamsAddButtonClicked(self, event):
        if self.checkIfAllowed()==False:
            return
        newOutputStreamName = self.OutputStreamsNameTextCtrl.GetValue()
        if not newOutputStreamName:
            logError("No name given for out-flowing stream.")
            return
        try:
            if newOutputStreamName in getOutflowingStreamNamesFromDB(self.selectedProcessID):
                logError("Stream '%s' already defined. You may select and change it instead." % newOutputStreamName)
                return
            name = self.saveOutputStream(newOutputStreamName)
        except AttributeError:
            logError("No process selected in tab Process data.")
            return
        if name is not None:
            self.OutputStreamsListBox.Append(name)
            self.OutputStreamsListBox.SetSelection(-1)
        
    def OnOutputStreamsChangeButtonClicked(self, event):
        if self.checkIfAllowed()==False:
            return
        changeOutputStreamName = self.OutputStreamsNameTextCtrl.GetValue()
        if not changeOutputStreamName:
            logError("No name given for out-flowing stream.")
            return
        try:
            name = self.saveOutputStream(changeOutputStreamName)
        except AttributeError:
            logError("No process selected in tab Process data.")
            return
        if name is not None:
            self.OutputStreamsListBox.SetString(self.OutputStreamsListBox.GetSelection(), name)
        
    def OnOutputStreamsRemoveButtonClicked(self, event):
        if self.checkIfAllowed()==False:
            return
        selectedItemIndex = self.OutputStreamsListBox.GetSelection()
        if selectedItemIndex == -1: # no selection
            return
        stream = OutflowingStream(self.OutputStreamsListBox.GetString(selectedItemIndex))
        try:
            stream.deleteFromDB(self.selectedProcessID)
        except AttributeError:
            logError("No process selected in tab Process data.")
            return
        self.OutputStreamsListBox.Delete(selectedItemIndex)
    
    def OnOutputStreamsListBoxItemSelected(self, event):
        selectedItemIndex = self.OutputStreamsListBox.GetSelection()
        if selectedItemIndex == -1: # no selection
            return
        stream = OutflowingStream(self.OutputStreamsListBox.GetString(selectedItemIndex))
        try:
            stream.loadFromDB(self.selectedProcessID)
        except AttributeError:
            logError("No process selected in tab Process data.")
            return
        except ProcessStreamsNotFoundError, StreamNotFoundError:
            logError("Cannot find stream by name. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return
        except FluidNotFoundError:
            logError("Cannot find fluid medium. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return
        except InconsistentDataBaseError:
            logError("Data base inconsistency. Please report this as a bug on http://sourceforge.net/tracker/?func=add&group_id=213015&atid=1024025.")
            return
        self.OutputStreamsNameTextCtrl.SetValue(stream.Name)
        if stream.HeatRecOK is None:
            self.OutputStreamsHeatRecOkChoiceEntry.SetValue(0)
        else:
            self.OutputStreamsHeatRecOkChoiceEntry.SetValue(stream.HeatRecOK 
                                                            and TRANSYESNO['yes'] 
                                                            or TRANSYESNO['no'])
        if stream.Medium is None:
            self.OutputStreamsProcMedOutChoiceEntry.SetValue(0)
        else:
            self.OutputStreamsProcMedOutChoiceEntry.SetValue(stream.Medium)
        self.OutputStreamsPTOutFlowFloatEntry.SetValue(stream.PTOutFlow)
        self.OutputStreamsHOutFlowFloatEntry.SetValue(stream.HOutFlow)
        self.OutputStreamsXOutFlowFloatEntry.SetValue(stream.XOutFlow)
        self.OutputStreamsPTFinalFloatEntry.SetValue(stream.PTFinal)
        self.OutputStreamsVOutFlowCycleFloatEntry.SetValue(stream.VOutFlowCycle)
        self.OutputStreamsMOutFlowNomFloatEntry.SetValue(stream.mOutFlowNom)
        
    def OnOutputStreamsHeatRecOkChoice(self, event):
        if self.checkIfAllowed()==False:
            return
        heatRec = TRANSYESNO['yes'] == event.GetString()
        self.OutputStreamsProcMedOutChoiceEntry.Enable(heatRec)
        self.OutputStreamsPTOutFlowFloatEntry.Enable(heatRec)
        self.OutputStreamsHOutFlowFloatEntry.Enable(heatRec)
        self.OutputStreamsXOutFlowFloatEntry.Enable(heatRec)
        self.OutputStreamsPTFinalFloatEntry.Enable(heatRec)
        
#------------------------------------------------------------------------------
#--- Public methods
#------------------------------------------------------------------------------		

    def display(self):
#        print "PanelQ3 (display): filling page"
        self.fillPage()
#        print "PanelQ3 (display): showing process"
        self.showProcess()
        self.Show()

    def fillChoiceOfDBUnitOperation(self): # tc3
        unitOpDict = Status.prj.getUnitOpDict()
        unitOpList = unitOpDict.values()
        unitOpList.sort()
        self.tc3.SetValue(unitOpList)
            
    def fillChoiceOfPMDBFluid(self):
        fluidDict = Status.prj.getFluidDict()
        self.tc4.SetValue(fluidDict.values())

    def fillChoiceOfODBFluid(self):
        fluidDict = Status.prj.getFluidDict()
        self.InputStreamsProcMedDBFluidChoiceEntry.SetValue([None] + fluidDict.values())
        self.OutputStreamsProcMedOutChoiceEntry.SetValue([None] + fluidDict.values())

    def fillChoiceOfSMDBFluid(self):
        fluidDict = Status.prj.getFluidDict()
        self.tc22.SetValue(fluidDict.values())

    def fillChoiceOfPipe(self):
        pipeList = Status.prj.getPipeList("Pipeduct")
#        print "PanelQ3: pipeList = %r"%pipeList
        self.tc23.SetValue(pipeList)

    def fillChoiceOfHX(self):
        hxList = Status.prj.getHXList("HXName")
#        self.tc20.SetValue(hxList)


    def fillPage(self):
        self.clear()
        self.fillChoiceOfDBUnitOperation()
        self.fillChoiceOfPMDBFluid()
        self.fillChoiceOfODBFluid()
        self.fillChoiceOfSMDBFluid()
        self.fillChoiceOfPipe()
        self.fillChoiceOfHX()
        self.tc2.SetValue(TRANSPROCTYPES.values())
        self.OutputStreamsHeatRecOkChoiceEntry.SetValue(TRANSYESNO.values())
        self.InputStreamsHeatRecExistChoiceEntry.SetValue(TRANSYESNO.values())
        self.listBoxProcesses.Clear()
        processList = Status.prj.getProcessList("Process")
        for process in processList:
            self.listBoxProcesses.Append(process)
            print "PanelQ3: adding process %r to list" % process
        try: self.listBoxProcesses.SetStringSelection(self.selectedProcessName)
        except: pass


    def clear(self):
        self.tc1.SetValue('')
#        self.tc2.SetValue('')
#        self.tc3.SetValue('')
#        self.tc4.SetValue('')
        self.tc5.SetValue('')
        self.InputStreamsPTInFlowFloatEntry.SetValue('')
        self.tc7.SetValue('')
        self.InputStreamsVInFlowCycleFloatEntry.SetValue('')
        self.InputStreamsMInFlowNomFloatEntry.SetValue('')
        self.tc9.SetValue('')
        self.ThermalMassFloatEntry.SetValue('')
        self.tc10.SetValue('')
        self.page1.HPerDayFloatEntry.SetValue('')
        self.page1.NCyclesFloatEntry.SetValue('')
        self.page1.HCycleFloatEntry.SetValue('')
        self.page1.NDaysFloatEntry.SetValue('')
        self.OutputStreamsPTOutFlowFloatEntry.SetValue('')
        self.OutputStreamsProcMedOutChoiceEntry.SetValue('')
        self.OutputStreamsHOutFlowFloatEntry.SetValue('')
        self.OutputStreamsXOutFlowFloatEntry.SetValue('')
        self.OutputStreamsPTFinalFloatEntry.SetValue('')
        self.OutputStreamsVOutFlowCycleFloatEntry.SetValue('')
        self.OutputStreamsMOutFlowNomFloatEntry.SetValue('')
        self.OutputStreamsHeatRecOkChoiceEntry.SetValue('')
        self.InputStreamsHeatRecExistChoiceEntry.SetValue('')
#        self.tc20.SetValue('')
        self.InputStreamsPTInFlowRecFloatEntry.SetValue('')
        self.tc22.SetValue('')
        self.tc23.SetValue('')
        self.tc24.SetValue('')
        self.tc25.SetValue('')
        self.tc26.SetValue('')

    def checkIfAllowed(self):
        if Status.ANo >= 0:
            showWarning(_U("In the present version of EINSTEIN it is not allowed to modify\n") + \
                        _U("processes in the checked state or alternative proposals. Go to the original data view\n") + \
                        _U("Workaround for studying process optimisation: create a copy of your project\nand modify on this copy in original state"))
            return False
        else:   
            return True


if __name__ == '__main__':
    class Main(object):
        def __init__(self, qid):
            self.activeQid = qid

    DBName = 'einstein'
    Status.SQL = MySQLdb.connect(host='localhost', user='root', passwd='tom.tom', db=DBName)
    Status.DB =  pSQL.pSQL(Status.SQL, DBName)

    app = wx.PySimpleApp()
    frame = wx.Frame(parent=None, id= -1, size=wx.Size(800, 600), title="Einstein - panelQ3")
    main = Main(1)
    panel = PanelQ3(frame, main)

    frame.Show(True)
    app.MainLoop()
        
