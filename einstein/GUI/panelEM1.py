#Boa:Frame:PanelEM1
#==============================================================================
#
#	E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (www.iee-einstein.org)
#
#------------------------------------------------------------------------------
#
#	PanelEM1- GUI component for: Energy performance - Monthly data
#			
#==============================================================================
#
#	Version No.: 0.01
#	Created by: 	    Tom Sobota	16/03/2008
#       Revised by:         Tom Sobota  29/03/2008
#       Revised by:         Tom Sobota  28/04/2008
#                           Stoyan Danov            18/06/2008
#                           Stoyan Danov    03/07/2008
#                           Stoyan Danov    04/07/2008
#                           Stoyan Danov    07/07/2008
#                           Stoyan Danov    09/07/2008
#                           Stoyan Danov    13/10/2008
#
#       Changes to previous version:
#       29/03/08:           mod. to use external graphics module
#       28/04/2008          created method display
#       18/06/2008 SD: change to translatable text _(...)
#       03/07/2008 SD: activate eventhandlers Fwd >>> and Back <<<, esthetics & security features
#       04/07/2008 SD: changed min No columns, col width,
#       07/07/2008 SD: data split: totals eliminated from data to plot, colours, columnwidth, Totals line highlited
#       09/07/2008 SD: set initially emptu labels to columns and fixed columnwidth to first 5 col
#       13/10/2008: SD  change _() to _U()
#
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

from status import Status
from einstein.modules.energyStats.moduleEM1 import *
import einstein.modules.matPanel as Mp
from GUITools import *
from einstein.GUI.graphics import drawStackedBarPlot
from numCtrl import *
from displayClasses import ChoiceEntry

[wxID_PANELEM1, wxID_PANELEM1BTNBACK, wxID_PANELEM1BTNFORWARD, 
 wxID_PANELEM1BTNOK, wxID_PANELEM1GRID1, wxID_PANELEM1PANELGRAPHMPHD, 
] = [wx.NewId() for _init_ctrls in range(6)]

#
# constants
#

ORANGE = '#FF6000'
LIGHTGREY = '#F8F8F8'
WHITE = '#FFFFFF'
DARKGREY = '#000060'
LIGHTGREEN = '#F0FFFF'

GRID_LETTER_SIZE = 8               # points
GRID_LABEL_SIZE = 9                # points
MINROWS = 12
COLNO1 = 5 # minimum number of columns-for the case that only ONE process exists
GRID_LETTER_COLOR = DARKGREY      # specified as hex #RRGGBB
GRID_BACKGROUND_COLOR = LIGHTGREY  # idem
GRAPH_BACKGROUND_COLOR = WHITE # idem
TITLE_COLOR = ORANGE

def _U(text):
    return unicode(_(text),"utf-8")

class PanelEM1(wx.Panel):
    def __init__(self, parent):
        self._init_ctrls(parent)
        self.keys = ['EM1_Table','EM1_Plot'] 
        # Whether to show heating or cooling processes
        self._showHeating = True
        self.mod = ModuleEM1(self.keys, self._showHeating)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PANELEM1, name=u'PanelEM1', parent=prnt,
              pos=wx.Point(0, 0), size=wx.Size(800, 600), style=0)

        #....box1....................................................................
        self.box1 = wx.StaticBox(self, -1, unicode(""),
                                 pos = (10,10),size=(780,210))

        self.box1.SetForegroundColour(TITLE_COLOR)
        self.box1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        hcModeChooser = ChoiceEntry(self, values=HEATING_COOLING,
                                         value=_('heating'), label=_('heating/cooling'),
                                         tip=_('Show only heating or cooling processes.'))
        hcModeChooser.Bind(wx.EVT_CHOICE, self.OnModeChooser)
        self.sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_1.Add(hcModeChooser, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=2)
        self.sizer_1.SetDimension(x=20, y=30, width=760, height=160)

        #....box2.....................................................................
        self.box2 = wx.StaticBox(self, -1, unicode(""),
                                 pos = (10,240),size=(780,310))

        self.box2.SetForegroundColour(TITLE_COLOR)
        self.box2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.panelGraphMPHD = wx.Panel(id=wxID_PANELEM1PANELGRAPHMPHD,
              name=u'panelGraphMPHD', parent=self, pos=wx.Point(20, 260),
              size=wx.Size(760, 280), style=wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
        self.panelGraphMPHD.SetBackgroundColour(wx.Colour(127, 127, 127))
        
        #..............................................................................
        #   default buttons
        #..............................................................................
        self.btnBack = wx.Button(id=wx.ID_BACKWARD, label=u'<<<',
              name=u'btnBack', parent=self, pos=wx.Point(500, 560),
              size=wx.Size(80, 20), style=0)
        self.btnBack.Bind(wx.EVT_BUTTON, self.OnBtnBackButton,
              id=-1)

        self.btnOK = wx.Button(id=wx.ID_OK, label=_U('OK'), name=u'btnOK',
              parent=self, pos=wx.Point(600, 560), size=wx.Size(80, 20),
              style=0)
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOKButton,
              id=-1)

        self.btnForward = wx.Button(id=wx.ID_FORWARD, label=u'>>>',
              name=u'btnForward', parent=self, pos=wx.Point(700, 560),
              size=wx.Size(80, 20), style=0)
        self.btnForward.Bind(wx.EVT_BUTTON, self.OnBtnForwardButton,
              id=-1)

    #------------------------------------------------------------------------------		
    #   Event handlers for default buttons
    #------------------------------------------------------------------------------		
    def OnBtnOKButton(self, event):
        event.Skip()

    def OnBtnBackButton(self, event):
        self.Hide()
        Status.main.tree.SelectItem(Status.main.qEA5, select=True)
        print "Button exitModuleBack: now I should show another window"

    def OnBtnForwardButton(self, event):
        self.Hide()
        Status.main.tree.SelectItem(Status.main.qEM2, select=True)
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
        """Initiate all the necessary calculations and then show the panel."""
        if self._showHeating:
            self.box1.SetLabel(_U('Monthly useful process heat'))
            self.box2.SetLabel(_U('Distribution of useful process heat per months'))
            plottitle = _U('Monthly process heat demand')
        else:
            self.box1.SetLabel(_U('Monthly useful process cooling'))
            self.box2.SetLabel(_U('Distribution of useful process cooling per months'))
            plottitle = _U('Monthly process cooling demand')
        # warning: this grid has a variable nr. of cols
        # so the 1st.row has the column headings
        data = Status.int.GData[self.keys[0]]
        # Security feature against non existing GData entry
        try: (rows,cols) = data.shape
        except: (rows,cols) = (0,COLNO1)
        # remap drawing methods to the wx widgets.
        paramList={'labels'      : 0,                            # labels column
                   'data'        : 3,                            # data column for this graph ##SD: nothing happens if number changes, error if this line commented
                   'key'         : self.keys[1],                      # key for Interface ##SD this points the data
                   'title'       : plottitle, # title of the graph
                   'ylabel'      :_U('UPH (MWh)'),                   # y axis label
                   'backcolor'   :GRAPH_BACKGROUND_COLOR,        # graph background color
                   'tickfontsize': 8,                            # tick label fontsize
                   'ignoredrows' :[0,1]}                        # rows that should not be plotted
        Mp.MatPanel(self.panelGraphMPHD,wx.Panel,drawStackedBarPlot,
                            paramList)
        # grid setup
        try:
            self.grid1.Destroy()
        except AttributeError:
            # There was no self.grid to delete in the first place
            pass
        self.grid1 = wx.grid.Grid(id=wxID_PANELEM1GRID1, name='grid1',
              parent=self, size=wx.Size(760, 150), style=0)
        self.grid1.CreateGrid(max(rows - 1, MINROWS), max(COLNO1, cols))
        self.grid1.EnableGridLines(True)
        self.grid1.SetDefaultRowSize(20)
        self.grid1.SetRowLabelSize(30)
        self.grid1.EnableEditing(False)
        self.grid1.SetColLabelValue(0, _U(" ")) #set initially empty column labels
        self.grid1.SetColLabelValue(1, _U(" "))
        self.grid1.SetColLabelValue(2, _U(" "))
        self.grid1.SetColLabelValue(3, _U(" "))
        self.grid1.SetColLabelValue(4, _U(" "))
        headings = data[0] # extract the array of headings
        self.grid1.SetLabelFont(wx.Font(9, wx.ROMAN, wx.ITALIC, wx.BOLD))
        for col in range(len(headings)):
            self.grid1.SetColSize(col, 141)
            self.grid1.SetColLabelValue(col, headings[col])
        for row in range(1, max(rows - 1 , MINROWS)):
            self.grid1.SetRowLabelValue(row, unicode(row))
        self.grid1.SetRowLabelValue(0, "")
        self.grid1.SetColSize(0, 141)
        self.grid1.SetColSize(1, 141)
        self.grid1.SetColSize(2, 141)
        self.grid1.SetColSize(3, 141)
        self.grid1.SetColSize(4, 141)
        self.sizer_1.Add(self.grid1)
        self.sizer_1.SetDimension(x=20, y=30, width=760, height=160)
        # data cell attributes
        attr = wx.grid.GridCellAttr()
        attr.SetTextColour(GRID_LETTER_COLOR)
        attr.SetBackgroundColour(GRID_BACKGROUND_COLOR)
        attr.SetFont(wx.Font(GRID_LETTER_SIZE, wx.SWISS, wx.NORMAL, wx.BOLD))

        attr2 = wx.grid.GridCellAttr()
        attr2.SetTextColour(GRID_LETTER_COLOR_HIGHLIGHT)
        attr2.SetBackgroundColour(GRID_BACKGROUND_COLOR_HIGHLIGHT)
        attr2.SetFont(wx.Font(GRID_LETTER_SIZE, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        # copy values from dictionary to grid
        # ignore the 1st. row, the column headings, which has been already
        # processed
        labels_column = 0
        # number of decimal digits for each column according to numbers
        # of columns (variable)
        decimals = [-1] + [ 1 for dummy in range(cols-1)] 
        for r in range(rows-1):
            if r == 0:
                self.grid1.SetRowAttr(r, attr2) #SD: set Totals highlited                
            else:
                self.grid1.SetRowAttr(r, attr)
                
            for c in range(cols):
                try:
                    if decimals[c] >= 0: # -1 indicates text
                        self.grid1.SetCellValue(r, c, \
                            convertDoubleToString(float(data[r+1][c]),nDecimals = decimals[c]))
                    else:
                        self.grid1.SetCellValue(r, c, data[r+1][c])
                except: 
                    logError("PanelEM1: error writing data[%s][%s]: " % (r, c))
                if c == labels_column:
                    self.grid1.SetCellAlignment(r, c, wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
                else:
                    self.grid1.SetCellAlignment(r, c, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.grid1.SetGridCursor(0, 0)
        self.panelGraphMPHD.draw()
        self.Refresh()
        self.Show()

