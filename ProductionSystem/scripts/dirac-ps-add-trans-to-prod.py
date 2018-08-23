#!/usr/bin/env python

"""
  Add an existing transformation to an existing production
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.Core.Base import Script

Script.setUsageMessage('\n'.join([__doc__.split('\n')[1],
                                  'Usage:',
                                  '  %s prodID' % Script.scriptName,
                                  'Arguments:',
                                  '  prodID: Production ID',
                                  '  transID: Transformation ID',
                                  '  parentTransID: Parent Transformation ID'
                                  ]))


Script.parseCommandLine()

from DIRAC.ProductionSystem.Client.ProductionClient import ProductionClient
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

prodClient = ProductionClient()
transClient = TransformationClient()

# get arguments
args = Script.getPositionalArgs()
if (len(args) == 3):
  parentTransID = args[2]
elif (len(args) == 2):
  parentTransID = -1
else:
  Script.showHelp()

prodID = args[0]
transID = args[1]


res = transClient.getTransformation(transID)
if not res['OK']:
  DIRAC.gLogger.error('Failed to get transformation %s: %s' % (transID, res['Message']))
  DIRAC.exit(-1)

transID = res['Value']['TransformationID']

if parentTransID != -1:
  res = transClient.getTransformation(parentTransID)
  if not res['OK']:
    DIRAC.gLogger.error('Failed to get transformation %s: %s' % (parentTransID, res['Message']))
    DIRAC.exit(-1)
  parentTransID = res['Value']['TransformationID']

res = prodClient.getProduction(prodID)
if not res['OK']:
  DIRAC.gLogger.error('Failed to get production %s: %s' % (prodID, res['Message']))
  DIRAC.exit(-1)

prodID = res['Value']['ProductionID']

res = prodClient.addTransformationsToProduction(prodID, transID, parentTransID)

if not res['OK']:
  DIRAC.gLogger.error(res['Message'])
  DIRAC.exit(-1)

DIRAC.gLogger.notice(
    'Transformation %s successfully added to production %s with parent transformation %s' %
    (transID, prodID, parentTransID))

DIRAC.exit(0)
