# $HeadURL$
__RCSID__ = "$Id$"
from DIRAC.FrameworkSystem.private.logging.Logger import Logger
from DIRAC.FrameworkSystem.private.standardLogging.LoggingRoot import LoggingRoot

# old logger
# useful for testing the new gLogger
# tests are in FrameworkSystem/test/testLoggerWrapper
oldgLogger = Logger()

# new gLogger
gLogger = LoggingRoot()


def getLogger():
  return gLogger
