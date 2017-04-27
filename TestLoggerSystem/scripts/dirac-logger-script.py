#!/usr/bin/env python
"""
  dirac-logger-script

    This script test client loggers

    Usage:
      dirac-logger-script
"""

from DIRAC           import S_OK, S_ERROR, gLogger, exit as DIRACExit
from DIRAC.Core.Base import Script


__RCSID__ = '$Id$'

def main():
  '''
    This is the script main method, which will hold all the logic.
  '''
  Script.parseCommandLine( ignoreErrors = False )
  
  #gLogger
  log = gLogger.getSubLogger("scriptLog")
  log.always("scriptLog")

  gLogger.always("gLogger")

  logSL = log.getSubLogger("scriptLogSL")
  log.always("scriptLogSL")

  client = ClientA()
  client.logSomething()
  client.logSomethingFromB()

  #Logging
  log = logging.getLogger("scriptLogL")
  log.always("scriptLogL\nmultiple line")

  logging.always("logging")

  client = ClientA()
  client.logSomethingNew()
  client.logSomethingFromBNew()

  log = gLogger.getSubLogger('log', True)
  log.always("LoggingChildFalse")

  log2 = log.getSubLogger('log2', False)
  log2.always("LoggingChildFalse2")

  log3 = log.getSubLogger('log3', True)
  log3.always("LoggingChildFalse3")

  log4 = log2.getSubLogger('log4', True)
  log4.always("LoggingChildFalse4")

  log5 = log4.getSubLogger('log5', True)
  log5.always("LoggingChildFalse5")

  gLogger.showThreadIDs(True)
  LoggingConfiguration.showThreadIDs(True)

  gLogger.always('logWithThreadID')
  logging.always('logWithThreadID')




if __name__ == "__main__":
  #Import the required DIRAC modules
  import logging
  from DIRAC.Interfaces.API.Dirac import Dirac
  from DIRAC.TestLoggerSystem.Client.ClientA import ClientA
  from DIRAC.TestLoggerSystem.private.logging.LoggingConfiguration import LoggingConfiguration

  # Run the script
  main()

  # Bye
  DIRACExit( 0 )
