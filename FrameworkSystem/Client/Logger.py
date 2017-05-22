# $HeadURL$
__RCSID__ = "$Id$"
from DIRAC.FrameworkSystem.private.logging.Logger import Logger
# addLogging
from DIRAC.FrameworkSystem.private.standardLogging.LoggerWrapper import LoggerWrapper

#old logger
#gLogger = Logger()

#intermediate solution
gLogger = LoggerWrapper()


def getLogger():
  return gLogger
