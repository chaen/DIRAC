import logging

from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC import gLogger


class ClientB:

  def __init__(self):
    #gLogger
    self.logger = gLogger.getSubLogger('loggerclientB')
    #Logging
    self.loggerL = logging.getLogger('loggerclientBL')

  def logSomething(self):
    """Use gLogger"""
    gLogger.always("ClientB.log_something.gLogger")
    
    self.logger.always("ClientB.log_something.selflogger")

    log = self.logger.getSubLogger('logClientB')
    log.always("ClientB.log_something.log")

    logG = gLogger.getSubLogger('logGClientB')
    logG.always("ClientB.log_something.logG")

    logSL = gLogger.getSubLogger('loggerClientB')
    logSL.always("ClientB.log_something.logSL")