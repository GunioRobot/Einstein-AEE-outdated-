# -*- coding: utf-8 -*-
#==============================================================================
#
#    E I N S T E I N
#
#       Expert System for an Intelligent Supply of Thermal Energy in Industry
#       (www.iee-einstein.org)
#
#------------------------------------------------------------------------------
#
#    UPGRADE
#            
#------------------------------------------------------------------------------
#            
#    Functions for management of version upgrades
#
#==============================================================================
#
#    Version No.: 0.01
#    Created by:         David Baehrens      02/03/2010
#    
#------------------------------------------------------------------------------        
#    (C) copyleft energyXperts.BCN (E4-Experts SL), Barcelona, Spain 2010
#    www.energyxperts.net / info@energyxperts.net
#
#    This program is free software: you can redistribute it or modify it under
#    the terms of the GNU general public license as published by the Free
#    Software Foundation (www.gnu.org).
#
#==============================================================================

"""
:mod:`einstein.modules.upgrade` -- Version upgrades
=============================================================================

   :synopsis: Management of EINSTEIN version upgrades
   :author:   David Baehrens <david.baehrens@energyxperts.net>
"""
from sys                            import exit        
from einstein.modules.messageLogger import logMessage, showError
from einstein.modules.constants     import VERSION
from einstein.GUI.status            import Status

def upgradeEINSTEIN(targetVersion=VERSION, sourceVersion=None, projectIds=None):
    """Perform all defined upgrades to reach the specified version of EINSTEIN"""
    if not sourceVersion: # determine source version
        if projectIds is None: # complete data base upgrade requested
            try:
                sourceVersion = Status.DB.stool.Version['%'].column()[0]
            except KeyError, IndexError: # default version for complete upgrade
                sourceVersion = '1.1'
        else: # default schema version for selected projects
            sourceVersion = '1.1'
        
    if targetVersion == sourceVersion: # no upgrades necessary
        return
    else:
        logMessage('Upgrade to version %s starting' % targetVersion)
    
    if projectIds is not None:
        target = (len(projectIds) == 1) and '1 project' or ('%d projects' % len(projectIds))
    else:
        target = 'data base'
    
    # call all upgrade functions in order of ascending versions and then list order    
    for version in sorted(upgrades.keys()):
        if version > sourceVersion and version <= targetVersion:
            logMessage('Upgrade of %s to version %s starting' % (target, version))
            for upgrade in upgrades[version]:
                logMessage('%s starting' % upgrade.__name__)
                try:
                    upgrade(projectIds)
                except Exception, error:
                    showError('EINSTEIN upgrade failed\n\nError in %s\n%s' % (upgrade.__name__, error))
                    exit('EINSTEIN fatal: upgrade failed')
                logMessage('%s complete' % upgrade.__name__)
            logMessage('Upgrade of %s to version %s complete' % (target, version))

    if projectIds is None: # store reached target version in data base
        try:
            dbTool = Status.DB.stool.get_table()[0]
        except IndexError:
            Status.DB.stool.insert({'Version': targetVersion})
            logMessage('Upgrade to version %s complete: version number inserted' % targetVersion)
        else:
            dbTool.update({'Version': targetVersion})
            logMessage('Upgrade to version %s complete: version number updated' % targetVersion)
    else:
        logMessage('Upgrade to version %s complete' % targetVersion)

def upgradeDBSchema(version):
    """Upgrade data base schema to specified version
       UNUSED for now, needs more work
    """
    import os
    import fnmatch
    import MySQLdb
    schemaUpgrade = fnmatch.filter(os.listdir('../sql'), 'update_einsteinDB_schema_*_to_%s.sql' % version)
    try: # only honor the first upgrade to given version
        sqlSchemaUpgrade = open(os.path.join('../sql', schemaUpgrade[0])).read()
        dbCursor         = Status.SQL.cursor(MySQLdb.cursors.DictCursor)
        logMessage('data base schema upgrade starting')
        dbCursor.execute(sqlSchemaUpgrade)
        logMessage('data base schema upgrade complete: %d rows affected' % dbCursor.rowcount)
    except IndexError: # no upgrade found -> fine
        pass
    
def upgradeDetailedSchedules(projectIds=None):
    """Parameter upgrades for compatibility with detailed schedules"""
    from einstein.modules.schedules     import DEFAULTCHARGETIME
    from einstein.modules.fluids        import Fluid 

    # set defaults in upgraded table qprocessdata
    if projectIds is None: # default to complete table
        processDataRows = Status.DB.qprocessdata.get_table()
    elif projectIds == []: # no projects -> nothing to do
        return
    else: # just process the selected projects
        processDataRows = Status.DB.qprocessdata.sql_select('Questionnaire_id IN (%s)' % ','.join([str(id) for id in projectIds]))
    for processDataRow in processDataRows:
        # VInFlowCycle
        try:
            VInFlowCycle = processDataRow['VInFlowDay'] / processDataRow['NBatch']
        except TypeError: # one of the operands is None == NULL -> Stora NULL
            VInFlowCycle = 'NULL'

        # VOutFlowCycle
        try:
            VOutFlowCycle = processDataRow['VOutFlow'] / processDataRow['NBatch']
        except TypeError: # one of the operands is None == NULL -> Stora NULL
            VOutFlowCycle = 'NULL'

        # HPerYearInFlow
        try:
            HPerYearInFlow  = processDataRow['HBatch'] * processDataRow['NBatch'] * processDataRow['NDaysProc']
        except TypeError: # one of the operands is None == NULL -> Store NULL
            HPerYearInFlow = 'NULL'
        if processDataRow['ProcType'] == 'batch':
            HPerYearInFlow  = DEFAULTCHARGETIME * HPerYearInFlow

        # HPerYearOutFlow
        HPerYearOutFlow = HPerYearInFlow

        # mInFlowNom
        if processDataRow['ProcMedDBFluid_id'] is not None:
            FluidDensity = Fluid(processDataRow['ProcMedDBFluid_id']).rho
        else:
            FluidDensity = None
        try:
            mInFlowNom = (FluidDensity * processDataRow['VInFlowDay'] * processDataRow['NDaysProc']) / HPerYearInFlow
        except TypeError: # one of the operands is None == NULL -> Store NULL
            mInFlowNom = 'NULL'

        # mOutFlowNom
        try:
            mOutFlowNom = (FluidDensity * processDataRow['VOutFlow'] * processDataRow['NDaysProc']) / HPerYearOutFlow
        except TypeError: # one of the operands is None == NULL -> Store NULL
            mOutFlowNom = 'NULL'

        processDataRow.update({
                               'PartLoad'        : 1.0,
			       'VInFlowCycle'    : VInFlowCycle,
			       'VOutFlowCycle'   : VOutFlowCycle,
                               'mInFlowNom'      : mInFlowNom,
                               'mOutFlowNom'     : mOutFlowNom,
                               'HPerYearInFlow'  : HPerYearInFlow,
                               'HPerYearOutFlow' : HPerYearOutFlow
                               })

upgrades =  {
            '1.2' : [upgradeDetailedSchedules],
            }
"""Upgrades to perform in order to reach a specific version of EINSTEIN"""
        
#if __name__ == "__main__":
#    upgradeEINSTEIN(targetVersion='1.2')
