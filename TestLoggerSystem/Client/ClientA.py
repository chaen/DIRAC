import logging

from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC import gLogger
from DIRAC.TestLoggerSystem.Client.ClientB import ClientB


class ClientA:

  def __init__(self):
    self.clientB = ClientB()

    # gLogger
    self.logger = gLogger.getSubLogger('loggerClientA')
    # Logging
    self.loggerL = logging.getLogger('loggerClientAL')

  def logSomething(self):
    """use gLogger"""
    gLogger.always("ClientA.log_something.gLogger")

    self.logger.always("ClientA.log_something.selflogger")

    log = self.logger.getSubLogger('logClientA')
    log.always("ClientA.log_something.log")

    logG = gLogger.getSubLogger('logGClientA')
    logG.always("ClientA.log_something.logG")

    logSL = gLogger.getSubLogger('loggerClientA')
    logSL.always("ClientA.log_something.logSL")

  def logSomethingNew(self):
    """use Logging"""
    logging.always("ClientA.log_something.logging")

    self.loggerL.always("ClientA.log_something.selflogger")

    #Modification because in logging : log.getLogger is impossible.
    #We can do getLogger(name).getChild() but it doesn't fit with 
    #the behaviour of gLogger here. 
    log = logging.getLogger('logClientAL')
    log.always("ClientA.log_something.log")

    logG = logging.getLogger('logGClientAL')
    logG.always("ClientA.log_something.logG")

    logSL = logging.getLogger('loggerClientAL')
    logSL.always("ClientA.log_something.logSL")

  def logSomethingFromB(self):
    """use gLogger"""
    self.clientB.logSomething()

    self.clientB.logger.always("clientA.logSomethingFromB.clientB.logger")

    log = self.clientB.logger.getSubLogger("logClientBFromClientA")
    log.always("clientA.logSomethingFromB.clientB.log")

    logSL = gLogger.getSubLogger("loggerClientB")
    logSL.always('clientA.logSomethingFromB.clientB.logSL')

  def logSomethingFromBNew(self):
    """use Logging"""
    self.clientB.logSomethingNew()

    self.clientB.loggerL.always("clientA.logSomethingFromB.clientB.logger")

    #Modification because in logging : log.getLogger is impossible.
    #We can do getLogger(name).getChild() but it doesn't fit with 
    #the behaviour of gLogger here. 
    log = logging.getLogger("logClientBFromClientAL")
    log.always("clientA.logSomethingFromB.clientB.log")

    logSL = logging.getLogger("loggerClientBL")
    logSL.always('clientA.logSomethingFromB.clientB.logSL')

  def addStuff(self, something):
    atomService = RPCClient('TestLogger/Atom')
    result = atomService.addStuff(something)
    return result
