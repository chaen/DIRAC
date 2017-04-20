#!/usr/bin/env python
"""
  dirac-logger-script

    This script test client loggers

    Usage:
      dirac-logger-script
"""

from DIRAC           import S_OK, S_ERROR, gLogger, exit as DIRACExit
from DIRAC.Core.Base import Script
from DIRAC.TestLoggerSystem.Client.ClientA import ClientA

__RCSID__ = '$Id$'

def main():
  '''
    This is the script main method, which will hold all the logic.
  '''
  log = gLogger.getSubLogger("scriptLog")
  log.always("scriptLog")

  gLogger.always("gLogger")

  logSL = log.getSubLogger("scriptLogSL")
  log.always("scriptLogSL")

  client = ClientA()
  client.logSomething()
  client.logSomethingFromB()


if __name__ == "__main__":
  #Import the required DIRAC modules
  from DIRAC.Interfaces.API.Dirac import Dirac

  # Run the script
  main()

  # Bye
  DIRACExit( 0 )
