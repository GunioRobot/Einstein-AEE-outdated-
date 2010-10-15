#Boa:Frame:PanelEA4c
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
#	PanelEA4c - GUI component for: Process heat by temperature - Yearly data
#			
#==============================================================================
#
#	Version No.: 0.01
#	Created by: 	    Hans Schweiger  06/07/2008
#                           (based on PanelEA4b)
#       Revised by:
#                           Stoyan Danov    13/10/2008
#
#       Changes to previous version:
#       13/10/2008: SD  change _() to _U()
#       15/02/2010 MW: fixed visualization
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
import matplotlib.font_manager as font
from matplotlib.ticker import FuncFormatter

from status import Status
from einstein.modules.energyStats.moduleEA4 import *
from displayClasses import ChoiceEntry
from GUITools import *
import einstein.modules.matPanel as Mp

[wxID_PANELEA4, wxID_PANELEA4GRID1, wxID_PANELEA4GRID2, 
 wxID_PANELEA4PANELGRAPHUPH, wxID_PANELEA4PANELGRAPHHD,
 wxID_PANELEA4STATICTEXT1, wxID_PANELEA4STATICTEXT2,
 wxID_PANELEA4STATICTEXT3
] = [wx.NewId() for _init_ctrls in range(8)]
#
# constants
#

axeslabel_fontsize = 10
axesticks_fontsize = 8
legend_fontsize = 10
spacing_left = 0.2
spacing_right = 0.9
spacing_bottom = 0.2
spacing_top = 0.85

COLNO = 7
MAXROWS = 5

def _U(text):
    try:
        return unicode(_(text),"utf-8")
    except:
        return _(text)

def drawFigure(self):
    """draw with matplotlib the figures to be plotted"""
    if hasattr(self, 'subplot'):
        del self.subplot
    self.subplot = self.figure.add_subplot(1,1,1)
    self.figure.subplots_adjust(left=spacing_left, right=spacing_right,
                                bottom=spacing_bottom, top=spacing_top)
    data = Status.int.GData['EA4c_Plot']
    for i in range(1,len(data)):
        if i == 0:
            linewidth = 3
        else:
            linewidth = 1
        self.subplot.plot(data[0][1:],
                          data[i][1:],
                          LINETYPES[(i-1)%len(LINETYPES)],
                          color=ORANGECASCADE[(i-1)%len(ORANGECASCADE)],
                          label=data[i][0],
                          linewidth=linewidth)
    #self.subplot.axis([0, 100, 0, 3e+7])
    major_formatter = FuncFormatter(format_int_wrapper)
    self.subplot.axes.xaxis.set_major_formatter(major_formatter)
    self.subplot.axes.yaxis.set_major_formatter(major_formatter)
    fp = font.FontProperties(size = axeslabel_fontsize)
    self.subplot.axes.set_ylabel(self.params['ylabel'], fontproperties=fp)
    self.subplot.axes.set_xlabel(self.params['xlabel'], fontproperties=fp)

    for label in self.subplot.axes.get_yticklabels():
#        label.set_color(self.params['ytickscolor'])
        label.set_fontsize(axesticks_fontsize)
#        label.set_rotation(self.params['yticksangle'])
    #
    # properties of labels on the x axis
    #
    for label in self.subplot.axes.get_xticklabels():
#        label.set_color(self.params['xtickscolor'])
        label.set_fontsize(axesticks_fontsize)
#        label.set_rotation(self.params['xticksangle'])
##
    self.subplot.legend(loc = 0)
    try:
        lg = self.subplot.get_legend()
        ltext  = lg.get_texts()             # all the text.Text instance in the legend
        for txt in ltext:
            txt.set_fontsize(legend_fontsize)  # the legend text fontsize
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


class PanelEA4c(wx.Panel):
    def __init__(self, parent):

        self._init_ctrls(parent)
        keys = ['EA4c_Table','EA4c_Plot']
        # Whether to show heating or cooling processes
        self._showHeating = True
        self.mod = ModuleEA4(keys)
        self.mod.updatePanel(self._showHeating)

        # build table
        # set upper grid
        self.grid1.CreateGrid(MAXROWS, COLNO)
        self.grid1.EnableGridLines(True)
        # LAYOUT: here the default row size is fixed
        self.grid1.SetDefaultRowSize(20)
        self.grid1.SetRowLabelSize(30)
        self.grid1.SetColLabelSize(55)
        # LAYOUT: here the column size of the table is fixed (in pixels)
        self.grid1.SetDefaultColSize(100)
        self.grid1.SetColSize(0,115)
        self.grid1.EnableEditing(False)
        self.grid1.SetLabelFont(wx.Font(9, wx.ROMAN, wx.ITALIC, wx.BOLD))
        self.grid1.SetColLabelValue(0, _U("Temperature Levels\n[°C]"))
        self.grid1.SetColLabelValue(1, _U("Base Load\n(power)\n[kW]"))
        self.grid1.SetColLabelValue(2, _U("Base Load\n(energy)\n[MWh]"))
        self.grid1.SetColLabelValue(3, _U("Medium Load\n(power)\n[kW]"))
        self.grid1.SetColLabelValue(4, _U("Medium Load\n(energy)\n[MWh]"))
        self.grid1.SetColLabelValue(5, _U("Peak Load\n(power)\n[kW]"))
        self.grid1.SetColLabelValue(6, _U("Peak Load\n(energy)\n[MWh]"))
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.hcModeChooser = ChoiceEntry(self, values=HEATING_COOLING,
                                         value=_('heating'), label=_('heating/cooling'),
                                         tip=_('Show only heating or cooling processes.'))
        self.hcModeChooser.Bind(wx.EVT_CHOICE, self.OnModeChooser)
        sizer_1.Add(self.hcModeChooser, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=2)
        sizer_1.Add(self.grid1, flag=wx.EXPAND)
        sizer_1.SetDimension(x=20, y=25, width=760, height=160)

    def _init_ctrls(self, prnt):
        wx.Panel.__init__(self, id=wxID_PANELEA4, name=u'PanelEA4c', parent=prnt,
              pos=wx.Point(0, 0), size=wx.Size(800, 600))
        self.box1 = wx.StaticBox(self, -1, unicode(""), pos = (10, 10),
                                 size=(780, 200))
        self.box1.SetForegroundColour(TITLE_COLOR)
        self.box1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.grid1 = wx.grid.Grid(id=wxID_PANELEA4GRID1, name='grid1',#SD
              parent=self, size=wx.Size(760, 145),
              style=0)


        self.box2 = wx.StaticBox(self, -1, unicode(""), pos = (10, 230),
                                 size=(780, 320))
        self.box2.SetForegroundColour(TITLE_COLOR)
        self.box2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.panelEA4cFig = wx.Panel(id=-1, name='panelEA4cFig', parent=self,
              pos=wx.Point(200, 260), size=wx.Size(400, 280), style=wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
        self.panelEA4cFig.SetBackgroundColour(wx.Colour(127, 127, 127))


        #   default buttons
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
        Status.main.tree.SelectItem(Status.main.qEA4b, select=True)

    def OnBtnForwardButton(self, event):
        self.Hide()
        Status.main.tree.SelectItem(Status.main.qEA5, select=True)

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
            self.box1.SetLabel(_U('Useful supply heat demand (USH) - peak and base load'))
            self.box2.SetLabel(_U('Cumulative heat demand (USH)'))
            ylabel = _U('Heat supply load [kW]')
        else:
            self.box1.SetLabel(_U('Useful supply cooling demand (USC) - peak and base load'))
            self.box2.SetLabel(_U('Cumulative cooling demand (USC)'))
            ylabel = _U('Cooling supply load [kW]')
        # build xy-plot
        labels_column = 0
        paramList={'labels'      : labels_column,          # labels column
                   'data'        : 3,                      # data column for this graph
                   'key'         : 'EA4c_Plot',                # key for Interface
                   'title'       : _U('Some title'),           # title of the graph
                   'ylabel'      : ylabel,
                   'xlabel'      : _U('Annual operating hours [h]'),
                   'backcolor'   : GRAPH_BACKGROUND_COLOR, # graph background color
                   'ignoredrows' : []}            # rows that should not be plotted
        Mp.MatPanel(self.panelEA4cFig, wx.Panel, drawFigure, paramList)
        self.panelEA4cFig.draw()

        # bring data to table
        try:
            data = Status.int.GData['EA4c_Table']
            (rows,cols) = data.shape
        except:
            logDebug("PanelEA4c: received corrupt data in key: EA4c_Table")
            (rows,cols) = (0,COLNO)
        decimals = [-1,2,2,2,2,2,2]   #number of decimal digits for each colum
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
            if r == 0:
                attr2 = wx.grid.GridCellAttr()
                attr2.SetTextColour(GRID_LETTER_COLOR_HIGHLIGHT)
                attr2.SetBackgroundColour(GRID_BACKGROUND_COLOR_HIGHLIGHT)
                attr2.SetFont(wx.Font(GRID_LETTER_SIZE, wx.SWISS, wx.NORMAL, wx.BOLD))
                self.grid1.SetRowAttr(r, attr2) #highlight totals row
            else:   
                attr = wx.grid.GridCellAttr()
                attr.SetTextColour(GRID_LETTER_COLOR)
                attr.SetBackgroundColour(GRID_BACKGROUND_COLOR)
                attr.SetFont(wx.Font(GRID_LETTER_SIZE, wx.SWISS, wx.NORMAL, wx.NORMAL))
                self.grid1.SetRowAttr(r, attr)
                
            for c in range(cols):
                try:
                    if decimals[c] >= 0: # -1 indicates text
                        self.grid1.SetCellValue(r, c, \
                            convertDoubleToString(float(data[r][c]),nDecimals = decimals[c]))
                    else:
                        self.grid1.SetCellValue(r, c, data[r][c])
                except Exception, e : 
                    logError(str(e))
                    pass
                if c == labels_column:
                    self.grid1.SetCellAlignment(r, c, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                else:
                    self.grid1.SetCellAlignment(r, c, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        self.Refresh()
        self.Show()
