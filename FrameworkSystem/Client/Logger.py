# $HeadURL$
__RCSID__ = "$Id$"
from DIRAC.FrameworkSystem.private.logging.Logger import Logger
# addLogging
from DIRAC.FrameworkSystem.private.standardLogging.gLogger import gLogger

#old logger
#gLogger = Logger()

#intermediate solution
gLogger = gLogger()


def getLogger():
  return gLogger
