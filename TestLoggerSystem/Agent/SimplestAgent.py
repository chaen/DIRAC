""" :mod: SimplestAgent

    Simplest Agent send a simple log message
"""

## imports
import logging 

from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.DISET.RPCClient import RPCClient

from DIRAC.TestLoggerSystem.Client.ClientA import ClientA

from DIRAC.TestLoggerSystem.private.logging.LoggingConfiguration import LoggingConfiguration

__RCSID__ = "Id: $"


class SimplestAgent(AgentModule):
  """
  .. class:: SimplestAgent

  Simplest agent
  print a message on log
  """

  def initialize(self):
    """ agent's initalisation

    :param self: self reference
    """
    self.message = self.am_getOption('Message', "SimplestAgent is working...")
    
    self.log.info("message = %s" % self.message)

    #gLogger
    self.logger = gLogger.getSubLogger("SimplestAgentSelfLogger")
    #Logging
    self.loggerL = logging.getLogger("SimplestAgentSelfLogging")
    return S_OK()

  def execute(self):
    """ execution in one agent's cycle

    :param self: self reference
    """
    #gLogger
    self.log.info("SimplestAgentLogInherit.execute.message is: %s" % self.message)

    self.logger.info("SimplestAgentSelfLogger.execute.message is: %s" % self.message)

    gLogger.info("SimplestAgentGLogger.execute.message is: %s" % self.message)

    subLogInherit = self.log.getSubLogger("SimplestAgentSubInheritLogger")
    subLogInherit.info("SimplestAgentSubLogInherit.execute.message is: %s" % self.message)

    self.loggerL.info("SimplestAgentSelfLogging.execute.message is: %s" % self.message)
    logging.info("SimplestAgentGLogger.execute.message is: %s" % self.message)

    client = ClientA()

    client.logSomething()
    client.logSomethingFromB()

    self.logger.always(" ")
    self.logger.notice(" ")
    self.logger.info(" ")
    self.logger.verbose(" ")
    self.logger.debug(" ")
    self.logger.warn(" ")
    self.logger.error(" ")
    self.logger.fatal(" ")

    log = gLogger.getSubLogger('log', False)
    log.always("LoggingChildFalse")

    log2 = log.getSubLogger('log2', False)
    log2.always("LoggingChildFalse2")

    log3 = log.getSubLogger('log3', False)
    log3.always("LoggingChildFalse3")

    log4 = log2.getSubLogger('log4', True)
    log4.always("LoggingChildFalse4")

    log5 = log4.getSubLogger('log5', True)
    log5.always("LoggingChildFalse5")

    #Logging
    subLog = self.logger.getSubLogger("SimplestAgentSubLogger")
    self.logger.info("SimplestAgentSubLog.execute.message is: %s" % self.message)

    #Test color option
    self.loggerL.always(" ")
    self.loggerL.notice(" ")
    self.loggerL.info(" ")
    self.loggerL.verbose(" ")
    self.loggerL.debug(" ")
    self.loggerL.warn(" ")
    self.loggerL.error(" ")
    self.loggerL.fatal(" ")

    self.loggerL.exception(" ")

    #Test multi line messages
    self.loggerL.verbose("message\non\nmultiple\nline")

    try:
      1/0
    except:
      self.loggerL.exception("division par 0", exc_info=True)

    # Test showLine option
    gLogger.setLevel('debug')

    gLogger.always("this is a message with showLine option at True")





    result = client.addStuff("somethingWithAgent")
    if not result['OK']:
      self.log.error("Error while calling the service: %s" % result['Message'])
      return result
    self.log.info("Result of the request is %s" % result['Value'])
    return S_OK()
