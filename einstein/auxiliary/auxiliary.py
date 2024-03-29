#==============================================================================
#
#	E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (www.iee-einstein.org)
#
#------------------------------------------------------------------------------
#
#	AUXILIARY - Auxiliary functions (general)
#			
#------------------------------------------------------------------------------
#			
#	Short description:
#	
#	Module for calculation of energy statistics
#
#==============================================================================
#
#	Version No.: 0.05
#	Created by: 	    Hans Schweiger	30/01/2008
#	Revised by:         Tom Sobota          12/03/2008
#                           Hans Schweiger      21/03/2008
#                           Stoyan Danov        28/03/2008
#                           Hans Schweiger      24/04/2008
#                           Stoyan Danov        05/05/2008
#                           Hans Schweiger      29/06/2008
#                           David Baehrens      07/01/2010
#
#       Changes:
#       - introduction of function frange
#	20/03/08: HP specific functions eliminated. abstract nomenclature of
#                   list and table interpolation functions
#       28/03/2008 added: transpose(), firstHigher()
#       24/04/2008  function "noneFilter" added
#       05/05/2008 bug corrected in interpolateList (yList was used instead of ylist)
#       29/06/2008: HS  change in findFirst/LastNonZero -> fix of bug in HP module
#       07/01/2010: DB introduction of function normalize
#
#------------------------------------------------------------------------------		
#	(C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2008, 2010
#	www.energyxperts.net / info@energyxperts.net
#
#	This program is free software: you can redistribute it or modify it under
#	the terms of the GNU general public license as published by the Free
#	Software Foundation (www.gnu.org).
#
#==============================================================================

from math import *

#------------------------------------------------------------------------------		
#   1. Minimum and maximum values
#------------------------------------------------------------------------------		

#------------------------------------------------------------------------------		
def min(a,b):
#------------------------------------------------------------------------------		
    if a >= b: return b
    else: return a

#------------------------------------------------------------------------------		
def max(a,b):
#------------------------------------------------------------------------------		
    if a >= b: return a
    else: return b

#------------------------------------------------------------------------------		
def maxInList(ylist):
#------------------------------------------------------------------------------		
    m = 0
    for i in range(len(ylist)):
        m = max(m,ylist[i])
    return m

#------------------------------------------------------------------------------		
#   2. Table look-up and interpolation routines
#       - lists: lists of values ylist[i]
#       - tables: pairs of values y-x in lists ylist[i],xlist[i]
#------------------------------------------------------------------------------		

#------------------------------------------------------------------------------
def lastNonZero(ylist):
#------------------------------------------------------------------------------
#finds the last filled position of the list (different from zero)
#------------------------------------------------------------------------------
    n = len(ylist)
    idx = 0
    for i in range(n-1,-1,-1):
        if ylist[i] <> 0.0:
            idx = i
            break
    return idx
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def firstNonZero(ylist):
#------------------------------------------------------------------------------
#finds the first filled position of the list (different from zero)
#------------------------------------------------------------------------------
    i = 0
    n = len(ylist)
    idx = n
    for i in range(n):
        if ylist[i] <> 0:
            idx = i
            break
    return idx
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def findInListASC(y,ylist):
#------------------------------------------------------------------------------
#   selects the table entry with a value closest, but lower to val.
#   returns the index
#------------------------------------------------------------------------------
    for i in range(len(ylist)):
        if y < ylist[i]:
            return int(i-1)
    return(len(ylist)-1)        
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def interpolateList(xi,ylist):
#------------------------------------------------------------------------------
#   interpolates the y-values in a table y(x) for non-integer values of x0
#------------------------------------------------------------------------------
    #finds the temperature interval values (floor and ceil)
    i1 = int(floor(xi)) # math.floor and math.ceil return DOUBLEs -> int() should be applied then
    i0 = int(ceil(xi))
    if i0 == i1: #avoid division to zero
        y = ylist[i1]# SD: error yList en vez de ylist, 05/05/2008
        #print 'interp...1'
    else:
        #print 'interp...2'
        y1 = ylist[i1]
        y0 = ylist[i0]
        #interpolates to find the Q corresponding to T
        y = (y0 * (i1 - xi) + y1 * (xi - i0))/(i1-i0)
    return y   

#------------------------------------------------------------------------------
def interpolateTable(x,xlist,ylist):
#------------------------------------------------------------------------------
#   interpolates the table values ylist(xlist) for values of x not in xlist
#   only works for montonous curves (both ascending and descending)
#------------------------------------------------------------------------------

    n = len(xlist)
    for i in range(n-1):
        if ((x >= xlist[i]) and (x < xlist[i+1])) or ((x <= xlist[i]) and (x > xlist[i+1])):
            y = (ylist[i]*(xlist[i+1]-x) + ylist[i+1]*(x-xlist[i]))/(xlist[i+1]-xlist[i])
            break   

#...............................................................................
# check of special cases when x is out of the limits of xlist
# in this case, the corresponding limit value of y is assigned
    
    if xlist[0] < xlist[n-1]:  #ascending list

        if x < xlist[0]:
            y = ylist[0]
            
        elif x >= xlist[n-1]:
            y = ylist[n-1]
            
    else:   # descending list

        if x > xlist[0]:
            y = ylist[0]
            
        elif x <= xlist[n-1]:
            y = ylist[n-1]

    return y

#---------------------------------------------------------------------------
def transpose(T):
    """ Transposes a matrix (list of lists) interchanging rows with columns
    """
    invT = []

    for j in range(len(T[0])):
        row = []
        for i in range(len(T)):
            row.append(T[i][j])
        invT.append(row)

    return invT

#-----------------------------------------------------------------------------
def firstHigher(val, ASClist):
    """Returns the index of the first higher value than val in the
    ascending values list ASClist"""

    for i in range(len(ASClist)):
        if val <= ASClist[i]:
            return i
    
    print 'In auxiliary.py - firstHigher() not found: error!'
    return 0


#-----------------------------------------------------------------------------
def findFirstGE(val, ASClist):
#-----------------------------------------------------------------------------
#   identical to firstHigher, but returns len(ASClist) if val > max(ASClist)
#-----------------------------------------------------------------------------

    for i in range(len(ASClist)):
        if val <= ASClist[i]:
            return i
    
    return len(ASClist)


#------------------------------------------------------------------------------		
#   3. Others
#------------------------------------------------------------------------------		

#------------------------------------------------------------------------------		
def frange(start, end, inc=None):   
#------------------------------------------------------------------------------
#   A range function with float arguments
#------------------------------------------------------------------------------		

    if inc == None:
        inc = 1.0

    L = []
    while True:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)
        
    return L

#------------------------------------------------------------------------------		
def checkLimits(x,xmin,xmax,default=None):   
#------------------------------------------------------------------------------
#   Checks if a value is within limits
#   If no value is given, the default value is assigned
#------------------------------------------------------------------------------		

    if x is None:
        return default
    xl = min(x,xmax)
    xl = max(xl,xmin)
    return xl

#------------------------------------------------------------------------------		
def noneFilter(datalist,substitute=" "):   
#------------------------------------------------------------------------------
#   A range function with float arguments
#------------------------------------------------------------------------------		

    for i in range(len(datalist)):
        if datalist[i] is None:
            datalist[i] = substitute
    return datalist

#------------------------------------------------------------------------------		
def noneFilterNumber(val,substitute=0.0):   
#------------------------------------------------------------------------------
#   A range function with float arguments
#------------------------------------------------------------------------------		

    if val is None:
        val = substitute
    return val

#------------------------------------------------------------------------------		
def cutInterval(x, x0, x1):
#------------------------------------------------------------------------------		
#   returns the fraction of the interval [x0,x1] or [x1,x0] that is below x
#------------------------------------------------------------------------------		

    if x0 is None or x1 is None:
        return 0

    xl = min(x0,x1)
    xh = max(x0,x1)
    
    if x <= xl:
        return 0.0
    elif x <= xh and xh > xl:
        return (x - xl)/(xh-xl)
    else:
        return 1.0

#------------------------------------------------------------------------------
def normalize(v):
# -----------------------------------------------------------------------------
    """Normalize vector v, s.t. \\sum_i v[i] = 1"""
    n = sum(v)
    if n == 0.:
        return v
    else:
        return [v[i] / n for i in range(len(v))]
#==============================================================================