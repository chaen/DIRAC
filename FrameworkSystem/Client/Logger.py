# $HeadURL$
__RCSID__ = "$Id$"
from DIRAC.FrameworkSystem.private.logging.Logger import Logger
# addLogging
from DIRAC.TestLoggerSystem.private.logging.LoggingConfiguration import LoggingConfiguration

gLogger = Logger()

# addLogging
LoggingConfiguration.initializeLogging()


def getLogger():
  return gLogger
