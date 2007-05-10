#!/usr/bin/env python2.4
# $Header: /tmp/libdirac/tmp.stZoy15380/dirac/DIRAC3/DIRAC/Core/scripts/dirac-service.py,v 1.5 2007/05/10 14:46:29 acasajus Exp $
__RCSID__ = "$Id: dirac-service.py,v 1.5 2007/05/10 14:46:29 acasajus Exp $"

import sys
from dirac import DIRAC
from DIRAC.ConfigurationSystem.Client.LocalConfiguration import LocalConfiguration
from DIRAC.LoggingSystem.Client.Logger import gLogger
from DIRAC.Core.DISET.Server import Server

localCfg = LocalConfiguration()

positionalArgs = localCfg.getPositionalArguments()
if len( positionalArgs ) == 0:
  gLogger.initialize( "NOT SPECIFIED", "/" )
  gLogger.fatal( "You must specify which server to run!" )
  sys.exit(1)

serverName = positionalArgs[0]
serverSection = localCfg.setConfigurationForServer( serverName )
localCfg.addMandatoryEntry( "Port" )
localCfg.addMandatoryEntry( "HandlerPath" )
localCfg.addMandatoryEntry( "/DIRAC/Setup" )
resultDict = localCfg.loadUserData()
if not resultDict[ 'OK' ]:
  gLogger.error( "There were errors when loading configuration", resultDict[ 'Message' ] )
  sys.exit(1)


serverToLaunch = Server( serverName )
serverToLaunch.serve()
