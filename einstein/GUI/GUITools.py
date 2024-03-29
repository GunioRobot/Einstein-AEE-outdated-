# -*- coding: cp1252 -*-
#==============================================================================
#
#	E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (<a href="http://www.iee-einstein.org/" target="_blank">www.iee-einstein.org</a>)
#
#------------------------------------------------------------------------------
#
#	GUI Tools
#
#------------------------------------------------------------------------------
#
#       Common functions used in sevaral GUI panels
#
#==============================================================================
#
#   EINSTEIN Version No.: 1.0
#   Created by: 	Hans Schweiger
#                       03/05/2008 - 05/07/2008
#
#   Update No. 001
#
#   Since Version 1.0 revised by:
#
#                       Hans Schweiger  06/04/2008
#               
#   06/04/2008  HS  Clean-up: elimination of prints
#
#------------------------------------------------------------------------------
#	(C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008,2009
#	http://www.energyxperts.net/
#
#	This program is free software: you can redistribute it or modify it under
#	the terms of the GNU general public license v3 as published by the Free
#	Software Foundation (www.gnu.org).
#
#==============================================================================

import wx
from einstein.modules.constants import *    #not needed here, but in the Panels !!!
from einstein.modules.messageLogger import *

# color set-up for grids and static boxes
ORANGE = '#FF6000'
SOFTORANGE = '#FFA066'
WHITE = '#FFFFFF'
LIGHTGREY = '#F6F6F6'
MIDDLEGREY = '#C0C0C0'
DARKGREY = '#000060'
BLACK = '#000000'

ORANGECASCADE = ['#FF6000','#EE5000','#DD4000','#CC2000','#BB1000',\
                 LIGHTGREY,MIDDLEGREY,DARKGREY,BLACK]
LINETYPES = ['-','--',':','.','-.',]

GRID_LETTER_SIZE = 8 #points
GRID_LABEL_SIZE = 9  # points
GRID_LETTER_COLOR = DARKGREY     # specified as hex #RRGGA
GRID_LETTER_COLOR_HIGHLIGHT = WHITE     # specified as hex #RRGGA
GRID_BACKGROUND_COLOR = LIGHTGREY # idem
GRID_BACKGROUND_COLOR_HIGHLIGHT = SOFTORANGE # idem
GRAPH_BACKGROUND_COLOR = WHITE # idem
TITLE_COLOR = ORANGE

#..............................................................................
#..............................................................................
#..............................................................................
#   Several auxiliary functions for GUI 
#..............................................................................
#..............................................................................
#..............................................................................

def graphSquareFromSaw(resolution, sawValues):
    """Extent to square wave from sawtooth function values
    
    :param resolution: Number of square values for one sawtooth value
    :type  resolution: Integer
    :param sawValues: Sawtooth function values
    :type  sawValues: List
    :returns: Square function values
    :rtype:   List
    """
    squareValues = []
    for y in sawValues:
        squareValues.extend([y]*resolution)
    return squareValues

#------------------------------------------------------------------------------
def _U(text):
#------------------------------------------------------------------------------
#   gets text in UTF-8 from gettext and converts into unicode (for wxPython)
#------------------------------------------------------------------------------
    return unicode(_(text),"utf-8")
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def fillChoice(choice,choiceList,nonePossible=True):
#------------------------------------------------------------------------------
#   fills the list of possible choices from a list of strings
#------------------------------------------------------------------------------
    choice.Clear()
    if nonePossible==True:choice.Append("None")
    for c in choiceList:choice.Append(c)
    choice.SetSelection(0)
#------------------------------------------------------------------------------		
#------------------------------------------------------------------------------		
def setChoice(choice,strChoice):
#------------------------------------------------------------------------------		
#   sets a choice to the string
#------------------------------------------------------------------------------		
    try:choice.SetSelection(choice.FindString(strChoice))
    except:choice.SetSelection(-1)

def check(value):
    """
    Substitute ""'s and None's by 'NULL'

    (should be moved some day to a separate file with sql-tools ...)

    """
    if value != "" and value != "None" and value is not None:
        if isinstance(value, str) or isinstance(value, unicode):
            logDebug("GuiTools (check): string or unicode instance detected: %r"%value)
            return value.encode("utf-8")
        else:
            return value
    else:
        return 'NULL'
#==============================================================================
