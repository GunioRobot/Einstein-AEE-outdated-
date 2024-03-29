#Boa:Frame:PanelEA4a
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
#	PanelEA4a - GUI component for: Process heat by temperature - Yearly data
#			
#==============================================================================
#
#	Version No.: 0.05
#	Created by: 	    Tom Sobota      21/03/2008
#       Revised by:         Tom Sobota      29/03/2008
#       Revised by:         Tom Sobota      28/04/2008
#                           Stoyan Danov    18/06/2008
#                           Hans Schweiger  19/06/2008
#                           Stoyan Danov    20/06/2008
#                           Stoyan Danov    01/07/2008
#                           Stoyan Danov    02/07/2008
#                           Stoyan Danov    03/07/2008
#                           Hans Schweiger  06/07/2008
#                           Stoyan Danov    13/10/2008
#
#       Changes to previous version:
#       29/03/08:       mod. to use external graphics module
#       28/04/2008      created method display
#       18/06/2008: SD  change to translatable text _(...)
#       19/06/2008: HS  some security features added
#       20/06/2008: SD  change esthetics - continue: layout, security features
#                       grid1 decimals control, changes of position and size of objects
#       01/07/2008: SD  adappted as panelEAa - heat demand by temperature, new columns added
#       02/07/2008: SD  changed to orange colour (staticBox)
#       03/07/2008 SD: activate eventhandlers Fwd >>> and Back <<<
#       06/07/2008: HS  made it work again. finish layout
#       13/10/2008: SD  change _() to _U()
#	
#------------------------------------------------------------------------------		
#	(C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008
#	www.energyxperts.net / info@energyxperts.net
#
#	This program is free software: you can redistribute it or modify it under
#	the terms of the GNU general public license as published by the Free
#	Software Foundation (www.gnu.org).
#
#============================================================================== 

import wx
from einstein.GUI.graphics import drawPiePlot
from numCtrl import *

from status import Status
from einstein.modules.energyStats.moduleEA4 import *
import einstein.modules.matPanel as Mp
from GUITools import *
from displayClasses import ChoiceEntry

[wxID_PANELEA4, wxID_PANELEA4GRID1, wxID_PANELEA4GRID2,
 wxID_PANELEA4PANELGRAPHUPH, wxID_PANELEA4PANELGRAPHHD,
 wxID_PANELEA4STATICTEXT1, wxID_PANELEA4STATICTEXT2,
 wxID_PANELEA4STATICTEXT3,
] = [wx.NewId() for _init_ctrls in range(8)]
#
# constants
#

COLNO1 = 8
MAXROWS = 20

def _U(text):
    try:
        return unicode(_(text), "utf-8")
    except:
        return _(text)

#============================================================================== 
#============================================================================== 
class PanelEA4a(wx.Panel):
#============================================================================== 
#============================================================================== 

#------------------------------------------------------------------------------		
    def __init__(self, parent):
        self._init_ctrls(parent)
        # Whether to show heating or cooling processes
        self._showHeating = True
        self.keys = ['EA4a_Table', 'EA4a_Plot']
        self.mod = ModuleEA4(self.keys)
        self.mod.updatePanel(self._showHeating)
        # Build-up table
        self.grid1.CreateGrid(MAXROWS, COLNO1)
        self.grid1.EnableGridLines(True)
        self.grid1.SetDefaultRowSize(20)
        self.grid1.SetRowLabelSize(30)
        self.grid1.SetDefaultColSize(80)
        self.grid1.SetColSize(0, 145)
        self.grid1.EnableEditing(False)
        self.grid1.SetLabelFont(wx.Font(9, wx.ROMAN, wx.ITALIC, wx.BOLD))
        self.grid1.SetColLabelValue(0, _U("Process"))
        # the label for col 1 is set dynamic in self.display() 
        self.grid1.SetColLabelValue(2, _U("Share\n[%]"))
        self.grid1.SetColLabelValue(3, _U("Circulation\n[MWh]"))
        self.grid1.SetColLabelValue(4, _U("Maintenance\n[MWh]"))
        self.grid1.SetColLabelValue(5, _U("Start-Up\n[MWh]"))
        self.grid1.SetColLabelValue(6, _U("Process\nTemp. [°C]"))
        self.grid1.SetColLabelValue(7, _U("Process Supply\nTemp. [°C]"))

    def _init_ctrls(self, prnt):
        """basic lay-out"""        
        wx.Panel.__init__(self, id=wxID_PANELEA4, name=u'PanelEA4a', parent=prnt,
              pos=wx.Point(0, 0), size=wx.Size(800, 600))

        self.box1 = wx.StaticBox(self, -1, unicode(""),
                                 pos=(10, 10), size=(780, 200))

        self.box1.SetForegroundColour(TITLE_COLOR)
        self.box1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.grid1 = wx.grid.Grid(id=wxID_PANELEA4GRID1, name='grid1', #SD
                                  parent=self, size=wx.Size(760, 150), style=0)

        self.box2 = wx.StaticBox(self, -1, unicode(""),
                                 pos=(10, 230), size=(780, 320))

        self.box2.SetForegroundColour(TITLE_COLOR)
        self.box2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.panelGraphUPH = wx.Panel(id=wxID_PANELEA4PANELGRAPHUPH,
              name=u'panelGraphUPH', parent=self, pos=wx.Point(200, 260),
              size=wx.Size(400, 280), style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        self.panelGraphUPH.SetBackgroundColour(wx.Colour(127, 127, 127))
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.hcModeChooser = ChoiceEntry(self, values=HEATING_COOLING,
                                         value=_U('heating'), label=_U('heating/cooling'),
                                         tip=_U('Show only heating or cooling processes.'))
        self.hcModeChooser.Bind(wx.EVT_CHOICE, self.OnModeChooser)
        sizer_1.Add(self.hcModeChooser, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=2)
        sizer_1.Add(self.grid1, flag=wx.EXPAND)
        sizer_1.SetDimension(x=20, y=20, width=760, height=180)
#..............................................................................
#   default buttons
#..............................................................................
        self.btnBack = wx.Button(id=wx.ID_BACKWARD, label=u'<<<',
              name=u'btnBack', parent=self, pos=wx.Point(500, 560),
              size=wx.Size(80, 20), style=0)
        self.btnBack.Bind(wx.EVT_BUTTON, self.OnBtnBackButton,
              id= -1)

        self.btnOK = wx.Button(id=wx.ID_OK, label=_U('OK'), name=u'btnOK',
              parent=self, pos=wx.Point(600, 560), size=wx.Size(80, 20),
              style=0)
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOKButton,
              id= -1)

        self.btnForward = wx.Button(id=wx.ID_FORWARD, label=u'>>>',
              name=u'btnForward', parent=self, pos=wx.Point(700, 560),
              size=wx.Size(80, 20), style=0)
        self.btnForward.Bind(wx.EVT_BUTTON, self.OnBtnForwardButton,
              id= -1)

#------------------------------------------------------------------------------		
#   Event handlers for default buttons
#------------------------------------------------------------------------------		
    def OnBtnOKButton(self, event):
        event.Skip()

    def OnBtnBackButton(self, event):
        self.Hide()
        Status.main.tree.SelectItem(Status.main.qEA3, select=True)
        print "Button exitModuleBack: now I should show another window"

    def OnBtnForwardButton(self, event):
        self.Hide()
        Status.main.tree.SelectItem(Status.main.qEA4b, select=True)
        print "Button exitModuleFwd: now I should show another window"

    def OnModeChooser(self, event):
        """
        Eventhandler to set whether cooling or heating processes 
        should be displayed.
        """
        if event.GetClientData().GetStringSelection() == _('heating'):
            self._showHeating = True
        else:
            self._showHeating = False
        self.mod.updatePanel(self._showHeating)
        self.display()

    def display(self):
        """Update the representation in the panel."""
        if self._showHeating:
            self.box1.SetLabel(_U('Useful heat demand by process (UPH)'))
            self.box2.SetLabel(_U('Distribution of process heat demand (UPH Total) by processes'))
            plottitle = _U('UPH by process')
            self.grid1.SetColLabelValue(1, _U("UPH Total\n[MWh]"))

        else:
            self.box1.SetLabel(_U('Useful cooling demand by process (UPC)'))
            self.box2.SetLabel(_U('Distribution of process cooling demand (UPC Total) by processes'))
            plottitle = _U('UPC by process')
            self.grid1.SetColLabelValue(1, _U("UPC Total\n[MWh]"))
        try:
            data = Interfaces.GData[self.keys[0]]
            (rows, cols) = data.shape
        except:
            logDebug("PanelEA4a: received corrupt data set [%s]" % self.keys[0])
            (rows, cols) = (0, COLNO1)
        # pie-plot
        self.labels_column = 0
        # remaps drawing methods to the wx widgets.
        #
        # upper graphic: UPH demand by process
        #
        ignoredrows = [rows - 1]
        paramList = {'labels'      : self.labels_column, # labels column
                   'data'        : 2, # data column for this graph
                   'key'         : self.keys[0], # key for Interface
                   'title'       : plottitle, # title of the graph
                   'backcolor'   : GRAPH_BACKGROUND_COLOR, # graph background color
                   'ignoredrows' : ignoredrows}            # rows that should not be plotted
        
        Mp.MatPanel(self.panelGraphUPH, wx.Panel, drawPiePlot, paramList)
        # data cell attributes
                
        decimals = [-1, 2, 2, 2, 2, 2, 2, 2]   #number of decimal digits for each colum
        self.grid1.ClearGrid()
        for r in range(MAXROWS):
            # sometimes the attr object gets changed by the SetRowAttr call
            # that causes a wxwidget crash, these in-loop reinstanciatings
            # are a workaround (wx ver. <=2.8.11)
            attr = wx.grid.GridCellAttr()
            attr.SetTextColour(GRID_LETTER_COLOR)
            attr.SetBackgroundColour(GRID_BACKGROUND_COLOR)
            attr.SetFont(wx.Font(GRID_LETTER_SIZE, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.grid1.SetRowAttr(r, attr)
        for r in range(rows):
            if r < rows - 1:
                attr = wx.grid.GridCellAttr()
                attr.SetTextColour(GRID_LETTER_COLOR)
                attr.SetBackgroundColour(GRID_BACKGROUND_COLOR)
                attr.SetFont(wx.Font(GRID_LETTER_SIZE, wx.SWISS, wx.NORMAL, wx.NORMAL))
                self.grid1.SetRowAttr(r, attr)
            else:
                attr2 = wx.grid.GridCellAttr()
                attr2.SetTextColour(GRID_LETTER_COLOR_HIGHLIGHT)
                attr2.SetBackgroundColour(GRID_BACKGROUND_COLOR_HIGHLIGHT)
                attr2.SetFont(wx.Font(GRID_LETTER_SIZE, wx.SWISS, wx.NORMAL, wx.BOLD))
                self.grid1.SetRowAttr(r, attr2)  #highlight totals row
                
            for c in range(cols):
                try:
                    if decimals[c] >= 0: # -1 indicates text
                        self.grid1.SetCellValue(r, c, 
                            convertDoubleToString(float(data[r][c]), nDecimals=decimals[c]))
                    else:
                        self.grid1.SetCellValue(r, c, data[r][c])
                except:
                    logDebug("PanelEA4a: error writing data[%s][%s]: " % (r, c))
                    
                if c == self.labels_column:
                    self.grid1.SetCellAlignment(r, c, wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
                else:
                    self.grid1.SetCellAlignment(r, c, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.panelGraphUPH.draw()
        self.Refresh()
