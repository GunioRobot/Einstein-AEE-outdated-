# -*- coding: utf-8 -*-
#==============================================================================
#
#	E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (www.iee-einstein.org)
#
#------------------------------------------------------------------------------
#
#	Panel Chillers
#			
#------------------------------------------------------------------------------
#			
#	Short description:
#	
#	Panel for CH design assistant
#
#==============================================================================
#
#	Version No.: 0.01
#	Created by: 	    Jan Ries                    September 2010
#	Last revised by:
#
#------------------------------------------------------------------------------		
#	(C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2010
#	www.energyxperts.net / info@energyxperts.net
#
#	This program is free software: you can redistribute it or modify it under
#	the terms of the GNU general public license as published by the Free
#	Software Foundation (www.gnu.org).
#
#============================================================================== 
"""
This module contains only the PanelCH class.
"""
import wx
from wx import grid
from einstein.GUI.status import Status 
from einstein.GUI.addEquipment_popup import AddEquipment, ManualAddDialog 
import einstein.modules.matPanel as Mp
from einstein.GUI.dialogOK import DialogOK

from einstein.modules.interfaces import Interfaces 
import einstein.modules.constants as const
from einstein.modules.messageLogger import *
from GUITools import *
from numCtrl import *
import matplotlib.font_manager as font
from matplotlib.ticker import FuncFormatter

[wxID_PANELCH, wxID_PANELCHCHCALCULATE, wxID_PANELCHBUTTONPAGECHADD,
 wxID_PANELCHBUTTONPAGECHBACK, wxID_PANELCHBUTTONPAGECHCANCEL,
 wxID_PANELCHBUTTONPAGECHFWD, wxID_PANELCHBUTTONPAGECHOK,
 wxID_PANELCHCBCONFIG1, wxID_PANELCHCBCONFIG3, wxID_PANELCHCHOICECONFIG4,
 wxID_PANELCHGRID, wxID_PANELCHPANELFIG, wxID_PANELCHST12PAGECH,
 wxID_PANELCHST1PAGECH, wxID_PANELCHST2PAGECH, wxID_PANELCHST3PAGECH,
 wxID_PANELCHST4PAGECH, wxID_PANELCHSTATICTEXT1, wxID_PANELCHSTINFO2_T3,
 wxID_PANELCHSTCONFIG3, wxID_PANELCHSTCONFIG4, wxID_PANELCHSTCONFIG5,
 wxID_PANELCHSTCONFIG6, wxID_PANELCHSTCONFIG7, wxID_PANELCHSTINFO1,
 wxID_PANELCHSTINFO1VALUE, wxID_PANELCHSTINFO2, wxID_PANELCHSTINFO2VALUE, wxID_PANELCHSTINFO2_P1, ####E.F. 01/08
 wxID_PANELCHSTINFO2_P2, wxID_PANELCHSTINFO2_P3, wxID_PANELCHSTINFO2_T1,
 wxID_PANELCHSTINFO2_T2, wxID_PANELCHSTINFO2A, wxID_PANELCHTCCONFIG2,
 wxID_PANELCHTCCONFIG5, wxID_PANELCHTCCONFIG6, wxID_PANELCHTCCONFIG7,
] = [wx.NewId() for _init_ctrls in range(38)]

# constants
#
axeslabel_fontsize = 10
axesticks_fontsize = 8
legend_fontsize = 10
spacing_left = 0.2
spacing_right = 0.9
spacing_bottom = 0.2
spacing_top = 0.85

MAXROWS = 50
TABLECOLS = 6

def _U(text):
    try:
        return unicode(_(text), "utf-8")
    except:
        return _(text)

TYPELIST = const.CHTYPES
FUELLIST = [_U("Natural Gas"), \
            _U("Biomass"), \
            _U("Fuel oil")]

#------------------------------------------------------------------------------		
def drawFigure(self):
#------------------------------------------------------------------------------
#   defines the figures to be plotted
#------------------------------------------------------------------------------		
    if hasattr(self, 'subplot'):
        del self.subplot
    self.subplot = self.figure.add_subplot(1, 1, 1)
    self.figure.subplots_adjust(left=spacing_left, right=spacing_right, bottom=spacing_bottom, top=spacing_top)

    self.subplot.plot(Interfaces.GData['CH Plot'][0],
                      Interfaces.GData['CH Plot'][1],
                      '--', color=MIDDLEGREY, label=u'QD [80ºC]')
    self.subplot.plot(Interfaces.GData['CH Plot'][0],
                      Interfaces.GData['CH Plot'][2],
                      ':', color=DARKGREY, label=u'QD [140ºC]')
    self.subplot.plot(Interfaces.GData['CH Plot'][0],
                      Interfaces.GData['CH Plot'][3],
                      '-', color=ORANGE, label='QD [Tmax]', linewidth=2)
#    self.subplot.axis([0, 100, 0, 3e+7])
    self.subplot.legend()

    major_formatter = FuncFormatter(format_int_wrapper)
    self.subplot.axes.xaxis.set_major_formatter(major_formatter)
    self.subplot.axes.yaxis.set_major_formatter(major_formatter)
    fp = font.FontProperties(size=axeslabel_fontsize)
    self.subplot.axes.set_ylabel(_U('Heat demand [kW]'), fontproperties=fp)
    self.subplot.axes.set_xlabel(_U('Cumulative hours [h]'), fontproperties=fp)
    
    for label in self.subplot.axes.get_yticklabels():
        label.set_fontsize(axesticks_fontsize)
    for label in self.subplot.axes.get_xticklabels():
        label.set_fontsize(axesticks_fontsize)

    self.subplot.legend(loc='best')
    try:
        lg = self.subplot.get_legend()
        ltext = lg.get_texts()             # all the text.Text instance in the legend
        for txt in ltext:
            txt.set_fontsize(legend_fontsize)  # the legend text fontsize
        # legend line thickness
        llines = lg.get_lines()             # all the lines.Line2D instance in the legend
        for lli in llines:
            lli.set_linewidth(1.5)          # the legend linewidth
        # color of the legend frame
        # this only works when the frame is painted (see below draw_frame)
        frame = lg.get_frame()             # the patch.Rectangle instance surrounding the legend
        frame.set_facecolor('#F0F0F0')      # set the frame face color to light gray
        # should the legend frame be painted
        lg.draw_frame(False)
    except:
        # no legend
        pass

class PanelCH(wx.Panel):
    """Panel for the chiller design assistant"""

    def __init__(self, parent, main, id, pos, size, style, name):
        self.parent = parent
        self.main = main
        self._init_ctrls(parent)

        self.keys = ['CH Table']
        self.mod = Status.mod.moduleCH
        self.mod.initPanel()
        
        # graphic: Cumulative heat demand by hours
        labels_column = 0
        ignoredrows = []
        paramList = {'labels'      : labels_column, # labels column
                   'data'        : 3, # data column for this graph
                   'key'         : self.keys[0], # key for Interface
                   'title'       : 'Some title', # title of the graph
                   'backcolor'   : GRAPH_BACKGROUND_COLOR, # graph background color
                   'ignoredrows' : ignoredrows}            # rows that should not be plotted

        Mp.MatPanel(self.panelFig, wx.Panel, drawFigure, paramList)
        
        # additional widgets setup
        # data cell attributes
        attr = wx.grid.GridCellAttr()
        attr.SetTextColour(GRID_LETTER_COLOR)
        attr.SetBackgroundColour(GRID_BACKGROUND_COLOR)
        attr.SetFont(wx.Font(GRID_LETTER_SIZE, wx.SWISS, wx.NORMAL, wx.NORMAL))

        (rows, cols) = (MAXROWS, TABLECOLS)
        self.grid.CreateGrid(MAXROWS, cols)
        self.grid.EnableGridLines(True)
        self.grid.SetSelectionMode(wx.grid.Grid.wxGridSelectRows)
        self.grid.SetDefaultRowSize(20)
        self.grid.SetRowLabelSize(30)
        self.grid.SetColSize(0, 115)
        self.grid.SetColSize(2, 60)
        self.grid.EnableEditing(False)
        self.grid.SetLabelFont(wx.Font(9, wx.ROMAN, wx.ITALIC, wx.BOLD))
        self.grid.SetColLabelValue(0, _U("Short name"))
        self.grid.SetColLabelValue(1, _U("Nom. power"))
        self.grid.SetColLabelValue(2, _U("COP"))
        self.grid.SetColLabelValue(3, _U("Type"))
        self.grid.SetColLabelValue(4, _U("Operating\nhours"))
        self.grid.SetColLabelValue(5, _U("Year manufact."))
        
        # copy values from dictionary to grid
        for r in range(rows):
            self.grid.SetRowAttr(r, attr)
            for c in range(cols):
                self.grid.SetCellValue(r, c, "")
                if c == labels_column:
                    self.grid.SetCellAlignment(r, c, wx.ALIGN_LEFT, wx.ALIGN_CENTRE);
                else:
                    self.grid.SetCellAlignment(r, c, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE);
        self.grid.SetGridCursor(0, 0)

    def _init_ctrls(self, parent):
        """
        Complete the GUI setup.
        
        :param parent: wxwidget parent of this widget
        """
        wx.Panel.__init__(self, id=wxID_PANELCH, name='PanelCH', parent=parent,
              pos=wx.Point(0, 0), size=wx.Size(800, 600), style=0)

        # box1: table
        self.box1 = wx.StaticBox(self, -1, _U("Chillers in the HC Supply System"),
                                 pos=(10, 10), size=(420, 220))
        self.box1.SetForegroundColour(TITLE_COLOR)
        self.box1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.grid = wx.grid.Grid(id=wxID_PANELCHGRID, name='gridpageCH',
              parent=self, pos=wx.Point(40, 48), size=wx.Size(376, 168),
              style=0)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK,
              self.OnGridPageCHGridCellLeftDclick, id=wxID_PANELCHGRID)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK,
              self.OnGridPageCHGridCellRightClick, id=wxID_PANELCHGRID)

        # box2: figure
        self.box2 = wx.StaticBox(self, -1, _U("Cumulative cooling demand to be covered by chillers"),
                                 pos=(440, 10), size=(350, 270))
        self.box2.SetForegroundColour(TITLE_COLOR)
        self.box2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.panelFig = wx.Panel(id=wxID_PANELCHPANELFIG, name='panelFig', parent=self,
              pos=wx.Point(450, 40), size=wx.Size(320, 220),
              style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)

        #   action buttons
        self.CHCalculate = wx.Button(id=wxID_PANELCHCHCALCULATE,
              label=_U('run design assistant'), name='CH_Calculate', parent=self,
              pos=wx.Point(232, 240), size=wx.Size(184, 24), style=0)
#        self.CHCalculate.Bind(wx.EVT_BUTTON, self.OnCHCalculateButton,
#              id=wxID_PANELCHCHCALCULATE)

        self.buttonpageCHAdd = wx.Button(id=wxID_PANELCHBUTTONPAGECHADD,
              label=_U('add boiler / burner'), name='buttonpageCHAdd', parent=self,
              pos=wx.Point(32, 240), size=wx.Size(184, 24), style=0)
        self.buttonpageCHAdd.Bind(wx.EVT_BUTTON, self.OnButtonpageCHAddButton,
              id=wxID_PANELCHBUTTONPAGECHADD)

        # box 3     Configuration design assistant
        self.box3 = wx.StaticBox(self, -1, _U("Design assistant options:"),
                                 pos=(10, 270), size=(420, 300))
        self.box3.SetForegroundColour(TITLE_COLOR)
        self.box3.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        # 1. Maintain existing equipment ?
        self.st3pageCH = wx.StaticText(id= -1,
              label=_U('Maintain existing equipment ?'), name='st3pageCH',
              parent=self, pos=wx.Point(40, 304), style=0)
        self.cbConfig1 = wx.CheckBox(id=wxID_PANELCHCBCONFIG1, label='',
              name='cbConfig1', parent=self, pos=wx.Point(288, 304),
              size=wx.Size(16, 16), style=0)
#        self.cbConfig1.Bind(wx.EVT_CHECKBOX, self.OnCbConfig1Checkbox,
#              id=wxID_PANELCHCBCONFIG1)

        # 2. Safety factor
        self.st4pageCH = wx.StaticText(id= -1, label=_U('Safety factor [%]'),
              name='st4pageCH', parent=self, pos=wx.Point(40, 344), style=0)
        self.tcConfig2 = wx.TextCtrl(id=wxID_PANELCHTCCONFIG2, name='tcConfig2',
              parent=self, pos=wx.Point(288, 336), size=wx.Size(128, 24),
              style=0, value='')
#        self.tcConfig2.Bind(wx.EVT_KILL_FOCUS, self.OnTcConfig2TextEnter,
#              id=wxID_PANELCHTCCONFIG2)

        # 3. Redundancy necessary ?
        self.stConfig3 = wx.StaticText(id= -1, label=_U('Is redundancy necessary ?'),
              name='stConfig3', parent=self, pos=wx.Point(40, 384), style=0)
        self.cbConfig3 = wx.CheckBox(id=wxID_PANELCHCBCONFIG3, label='',
              name='cbConfig3', parent=self, pos=wx.Point(288, 388),
              size=wx.Size(24, 13), style=0)
#        self.cbConfig3.Bind(wx.EVT_CHECKBOX, self.OnCbConfig3Checkbox,
#              id=wxID_PANELCHCBCONFIG3)

        # 4. choose fuel
        self.stConfig4 = wx.StaticText(id= -1, label=_U('Fuel Type'),
              name='stConfig4', parent=self, pos=wx.Point(40, 424), style=0)
        self.choiceConfig4 = wx.Choice(choices=FUELLIST,
              id=wxID_PANELCHCHOICECONFIG4, name='choiceConfig4', parent=self,
              pos=wx.Point(288, 416), size=wx.Size(128, 21), style=0)
#        self.choiceConfig4.Bind(wx.EVT_CHOICE, self.OnChoiceConfig4Choice,
#              id=wxID_PANELCHCHOICECONFIG4)

        # 5. minimum operation hours
        self.stConfig5 = wx.StaticText(id= -1,
              label=_U('Minimum operating hours (baseload chiller)'),
              name='stConfig5', parent=self, pos=wx.Point(40, 464), style=0)
        self.tcConfig5 = wx.TextCtrl(id=wxID_PANELCHTCCONFIG5, name='tcConfig5', parent=self,
              pos=wx.Point(288, 456), size=wx.Size(128, 24), style=0, value='')
#        self.tcConfig5.Bind(wx.EVT_KILL_FOCUS, self.OnTcConfig5TextEnter,
#              id=wxID_PANELCHTCCONFIG5)

        # 5. minimum boiler power
        self.stConfig6 = wx.StaticText(id= -1, label=_U('Minimum chiller power [kW]'),
              name='stConfig6', parent=self, pos=wx.Point(40, 504), style=0)
        self.tcConfig6 = wx.TextCtrl(id=wxID_PANELCHTCCONFIG6, name='tcConfig6',
              parent=self, pos=wx.Point(288, 496), size=wx.Size(128, 24),
              style=0, value='')
#        self.tcConfig6.Bind(wx.EVT_KILL_FOCUS, self.OnTcConfig6TextEnter,
#              id=wxID_PANELCHTCCONFIG6)

        # 5. minimum efficiency
        self.stConfig7 = wx.StaticText(id= -1,
              label=_U('Minimum effiency allowed [%]'), name='stConfig7',
              parent=self, pos=wx.Point(40, 544), style=0)
        self.tcConfig7 = wx.TextCtrl(id=wxID_PANELCHTCCONFIG7, name='tcConfig7',
              parent=self, pos=wx.Point(288, 544), size=wx.Size(128, 21),
              style=0, value='')
#        self.tcConfig7.Bind(wx.EVT_KILL_FOCUS, self.OnTcConfig7TextEnter,
#              id=wxID_PANELCHTCCONFIG7)

        # box 4     Info field
        self.box4 = wx.StaticBox(self, -1, _U("System Performance Data"),
                                 pos=(440, 320), size=(350, 200))
        self.box4.SetForegroundColour(TITLE_COLOR)
        self.box4.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.stInfo1 = wx.StaticText(id=wxID_PANELCHSTINFO1,
              label=_U('Minimum demand temperature [°C]'), name='stInfo1', parent=self,
              pos=wx.Point(460, 352), style=0)
        self.stInfo1Value = wx.StaticText(id=wxID_PANELCHSTINFO1VALUE,
              label='-', name='stInfo1Value', parent=self, pos=wx.Point(660,
              352), style=0)
        self.stInfo2 = wx.StaticText(id=wxID_PANELCHSTINFO2,
              label=_U('Residual power to be supplied [kW]'), name='stInfo2',
              parent=self, pos=wx.Point(460, 372), style=0)
        self.stInfo2Value = wx.StaticText(id=wxID_PANELCHSTINFO2VALUE,
              label='0', name='stInfo2Value', parent=self, pos=wx.Point(660,
              372), style=0)
        self.stInfo2a = wx.StaticText(id=wxID_PANELCHSTINFO2A,
              label=_U('Temperature [°C]'), name='stInfo3', parent=self,
              pos=wx.Point(504, 416), style=0)
        self.stInfo2b = wx.StaticText(id= -1, label=_U('Peak demand [kW]'),
              name='stInfo2b', parent=self, pos=wx.Point(616, 416), style=0)
        self.stInfo2_T1 = wx.StaticText(id=wxID_PANELCHSTINFO2_T1, label=_U('Up to 80'),
              name='stInfo2_T1', parent=self, pos=wx.Point(504, 440), style=0)
        self.stInfo2_T2 = wx.StaticText(id=wxID_PANELCHSTINFO2_T2, label=_U('80<T<140'),
              name='stInfo2_T2', parent=self, pos=wx.Point(504, 464), style=0)
        self.stInfo2_T3 = wx.StaticText(id=wxID_PANELCHSTINFO2_T3, label=_U('T<Tmax'),
              name='staticText3', parent=self, pos=wx.Point(504, 488), style=0)
        self.stInfo2_P1 = wx.StaticText(id=wxID_PANELCHSTINFO2_P1, label=_U('0'),
              name='stInfo2_P1', parent=self, pos=wx.Point(616, 440), style=0)
        self.stInfo2_P2 = wx.StaticText(id=wxID_PANELCHSTINFO2_P2, label=_U('0'),
              name='stInfo2_P2', parent=self, pos=wx.Point(616, 464), style=0)
        self.stInfo2_P3 = wx.StaticText(id=wxID_PANELCHSTINFO2_P3, label=_U('0'),
              name='stInfo2_P3', parent=self, pos=wx.Point(616, 488), style=0)

        # Default action buttons: FWD / BACK / OK / Cancel
        self.buttonpageCHOk = wx.Button(id=wx.ID_OK, label=_U('OK'),
              name='buttonpageCHOk', parent=self, pos=wx.Point(528, 544),
              size=wx.Size(75, 23), style=0)
#        self.buttonpageCHOk.Bind(wx.EVT_BUTTON, self.OnButtonpageCHOkButton,
#              id=wx.ID_OK)
        self.buttonpageCHCancel = wx.Button(id=wx.ID_CANCEL, label=_U('Cancel'),
              name='buttonpageCHCancel', parent=self, pos=wx.Point(616, 544),
              size=wx.Size(75, 23), style=0)
#        self.buttonpageCHCancel.Bind(wx.EVT_BUTTON,
#              self.OnButtonpageCHCancelButton, id=wx.ID_CANCEL)
        self.buttonpageCHFwd = wx.Button(id=wxID_PANELCHBUTTONPAGECHFWD,
              label='>>>', name='buttonpageCHFwd', parent=self,
              pos=wx.Point(704, 544), size=wx.Size(75, 23), style=0)
#        self.buttonpageCHFwd.Bind(wx.EVT_BUTTON, self.OnButtonpageCHFwdButton,
#              id=wxID_PANELCHBUTTONPAGECHFWD)
        self.buttonpageCHBack = wx.Button(id=wxID_PANELCHBUTTONPAGECHBACK,
              label='<<<', name='buttonpageCHBack', parent=self,
              pos=wx.Point(440, 544), size=wx.Size(75, 23), style=0)
#        self.buttonpageCHBack.Bind(wx.EVT_BUTTON, self.OnButtonpageCHBackButton,
#              id=wxID_PANELCHBUTTONPAGECHBACK)

    def display(self):
        """Update the underlying data and refresh and display the panel."""
        self.mod.updatePanel()        # prepares data for plotting
        # empty the grid
        self.grid.ClearGrid()
        # update the equipment table
        try:
            data = Interfaces.GData[self.keys[0]]
            (rows, cols) = data.shape
        except:
            rows = 0
            cols = TABLECOLS
            
        for r in range(rows):
            for c in range(cols):
                self.grid.SetCellValue(r, c, data[r][c])

        # update of design assistant parameters
#        self.config = Interfaces.GData["BB Config"]
        self.config = [1] * 7
        try:
            if self.config[0] == 1:
                self.cbConfig1.SetValue(True)
            elif self.config[0] == 0:
                self.cbConfig1.SetValue(False)
        except:
            logTrack("PanelCH: problem loading config[0] value %s " % self.config[0])

        try: self.tcConfig2.SetValue(str(self.config[1]))
        except:
            logTrack("PanelCH: problem loading config[1] value %s " % self.config[1])

        try:
            if self.config[2] == 1:
                self.cbConfig3.SetValue(True)
            elif self.config[2] == 0:
                self.cbConfig3.SetValue(False)
        except:
            logTrack("PanelCH: problem loading config[2] value %s " % self.config[2])

        try:        #try-except necessary if there comes a string that is not in list.
            self.choiceConfig4.SetSelection(0)
#            self.choiceConfig4.SetSelection(TYPELIST.index(self.config[1]))
        except:
            logError("PanelCH (display): was asked to display an erroneous heat pump type", self.config[1])

        self.tcConfig5.SetValue(str(self.config[4]))
        self.tcConfig6.SetValue(str(self.config[5]))
        self.tcConfig7.SetValue(str(self.config[6]))
        
        # update of info-values
#        self.info = Interfaces.GData["BB Info"]
        self.info = ["dummy string"] * 5
        self.stInfo1Value.SetLabel(convertDoubleToString(self.info[0]))
        self.stInfo2Value.SetLabel(convertDoubleToString(self.info[1]))
        self.stInfo2_P1.SetLabel(convertDoubleToString(self.info[2]))
        self.stInfo2_P2.SetLabel(convertDoubleToString(self.info[3]))
        self.stInfo2_P3.SetLabel(convertDoubleToString(self.info[4]))

        self.Hide()
        try: self.panelFig.draw()
        except: pass
        
        self.Show()
#==============================================================================
#   Event handlers
#==============================================================================

#------------------------------------------------------------------------------		
    def OnCHCalculateButton(self, event):
#------------------------------------------------------------------------------		
#   Button "Run Design Assistant" pressed
#------------------------------------------------------------------------------		
#..............................................................................
# Step 1 design assistant: gets a preselected list of possible heat pumps

        print "PanelCH (run design assistant): calling function DA"
        self.mod.designAssistant()
        
        self.display()

#------------------------------------------------------------------------------		
#------------------------------------------------------------------------------		
    def OnButtonpageCHAddButton(self, event):
#------------------------------------------------------------------------------		
#   adds an equipment to the list
#------------------------------------------------------------------------------		

        self.equipe = self.mod.addEquipmentDummy() #SD change 30/04/2008, delete equipeC
        pu1 = AddEquipment(self, # pointer to this panel
                            self.mod, # pointer to the associated module
                            'Add chiller equipment', # title for the dialogs
                            'dbboiler', # database table
                            0, # column to be returned
                            False)                     # database table can be edited in DBEditFrame?

        if pu1.ShowModal() == wx.ID_OK:

            print 'PanelCH AddEquipment accepted. Id=' + str(pu1.theId)
            print 'PanelCH AddEquipment pu1.theId is', pu1.theId
            if pu1.theId <= 0:
                self.mod.deleteEquipment(None)
            else:
                print 'PanelCH AddEquipment accepted. Id=' + str(pu1.theId)
        else:
            self.mod.deleteEquipment(None)
        self.display()

#------------------------------------------------------------------------------		
#------------------------------------------------------------------------------		
    def OnGridPageCHGridCellLeftDclick(self, event):
#------------------------------------------------------------------------------		
#       edits the selected equipment
#------------------------------------------------------------------------------		
        rowNo = event.GetRow() #number of the selected boiler should be detected depending on the selected row
        EqId = self.mod.getEqId(rowNo)
        dialog = ManualAddDialog(self, EqId)

        if (dialog.ShowModal() == wx.ID_OK):
            print "PanelHP (OnGridLeftDclick) - OK"
#            ret = self.mod.calculateCascade()

        self.display()

#------------------------------------------------------------------------------		
    def OnGridPageCHGridCellRightClick(self, event):
#   right double click
#   --> for the moment only DELETE foreseen !!!
#------------------------------------------------------------------------------		
        rowNo = event.GetRow() #number of the selected boiler should be detected depending on the selected row

        ret = "delete"
#..............................................................................
# "delete" selected:

        if (ret == "delete"):
            pu2 = DialogOK(self, _U("delete equipment"), _U("do you really want to delete this equipment ?"))
            if pu2.ShowModal() == wx.ID_OK:
                self.mod.deleteEquipment(rowNo)
                self.display()
                
        elif (ret == _U("edit")):
            OnGridPageCHGridCellLeftDclick(self, event)
        
#------------------------------------------------------------------------------		

#------------------------------------------------------------------------------		
#   Event handlers: parameter change in design assistant
#------------------------------------------------------------------------------		
    def OnCbConfig1Checkbox(self, event):
        val = self.cbConfig1.GetValue()
        if val == True:
            self.config[0] = 1
        elif val == False:
            self.config[0] = 0
        else:
            self.config[0] = None
            
        print "PanelCH: new config[%s] value: " % 0, self.config[0]
        Interfaces.GData["CH Config"] = self.config
        self.mod.setUserDefinedPars()

    def OnTcConfig2TextEnter(self, event):
        self.config[1] = self.tcConfig2.GetValue()
        print "PanelCH: new config[%s] value: " % 1, self.config[1]
        Interfaces.GData["HP Config"] = self.config
        self.mod.setUserDefinedPars()

    def OnCbConfig3Checkbox(self, event):
        val = self.cbConfig3.GetValue()
        if val == True:
            self.config[2] = 1
        elif val == False:
            self.config[2] = 0
        else:
            self.config[2] = None
        print "PanelCH: new config[%s] value: " % 2, self.config[2]
        Interfaces.GData["CH Config"] = self.config
        self.mod.setUserDefinedPars()

    def OnChoiceConfig4Choice(self, event):
        self.config[3] = FUELLIST[self.choiceConfig4.GetSelection()]
        print "PanelCH: new config[%s] value: " % 3, self.config[3]
        Interfaces.GData["HP Config"] = self.config[3]
        self.mod.setUserDefinedPars()

    def OnTcConfig5TextEnter(self, event):
        self.config[4] = self.tcConfig5.GetValue()
        print "PanelCH: new config[%s] value: " % 4, self.config[4]
        Interfaces.GData["HP Config"] = self.config
        self.mod.setUserDefinedPars()

    def OnTcConfig6TextEnter(self, event):
        self.config[5] = self.tcConfig6.GetValue()
        print "PanelCH: new config[%s] value: " % 5, self.config[5]
        Interfaces.GData["HP Config"] = self.config
        self.mod.setUserDefinedPars()

    def OnTcConfig7TextEnter(self, event):
        self.config[6] = self.tcConfig7.GetValue()
        print "PanelCH: new config[%s] value: " % 6, self.config[6]
        Interfaces.GData["HP Config"] = self.config
        self.mod.setUserDefinedPars()


#==============================================================================
#   <<< OK Cancel >>>
#==============================================================================

    def OnButtonpageCHOkButton(self, event):
        self.main.tree.SelectItem(self.main.qHC, select=True)
        self.Hide()

    def OnButtonpageCHCancelButton(self, event):
        print "Button exitModuleCancel: CANCEL Option not yet foreseen"

    def OnButtonpageCHBackButton(self, event):
        self.main.tree.SelectItem(self.main.qHP, select=True)
        self.Hide()

    def OnButtonpageCHFwdButton(self, event):
        self.main.tree.SelectItem(self.main.qEnergy, select=True)
        self.Hide()
