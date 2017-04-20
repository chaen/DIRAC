from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC import gLogger
from DIRAC.TestLoggerSystem.Client.ClientB import ClientB


class ClientA:

  def __init__(self):
    self.clientB = ClientB()
    self.logger = gLogger.getSubLogger('loggerClientA')

  def logSomething(self):
    gLogger.always("ClientA.log_something.gLogger")
    
    self.logger.always("ClientA.log_something.selflogger")

    log = self.logger.getSubLogger('logClientA')
    log.always("ClientA.log_something.log")

    logG = gLogger.getSubLogger('logGClientA')
    logG.always("ClientA.log_something.logG")

    logSL = gLogger.getSubLogger('loggerClientA')
    logSL.always("ClientA.log_something.logSL")

  def logSomethingFromB(self):
    self.clientB.logSomething()

    self.clientB.logger.always("clientA.logSomethingFromB.clientB.logger")

    log = self.clientB.logger.getSubLogger("logClientBFromClientA")
    log.always("clientA.logSomethingFromB.clientB.log")

    logSL = gLogger.getSubLogger("loggerClientB")
    logSL.always('clientA.logSomethingFromB.clientB.logSL')

  def addStuff(self, something):
    atomService = RPCClient('TestLogger/Atom')
    result = atomService.addStuff(something)
    return result
