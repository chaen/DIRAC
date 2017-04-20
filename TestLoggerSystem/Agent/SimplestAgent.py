""" :mod: SimplestAgent

    Simplest Agent send a simple log message
"""

# # imports
from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.DISET.RPCClient import RPCClient

from DIRAC.TestLoggerSystem.Client.ClientA import ClientA


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

    self.logger = gLogger.getSubLogger("SimplestAgentSelfLogger")
    return S_OK()

  def execute(self):
    """ execution in one agent's cycle

    :param self: self reference
    """

    self.log.info("SimplestAgentLogInherit.execute.message is: %s" % self.message)

    self.logger.info("SimplestAgentSelfLogger.execute.message is: %s" % self.message)

    gLogger.info("SimplestAgentGLogger.execute.message is: %s" % self.message)

    subLogInherit = self.log.getSubLogger("SimplestAgentSubInheritLogger")
    subLogInherit.info("SimplestAgentSubLogInherit.execute.message is: %s" % self.message)

    subLog = self.logger.getSubLogger("SimplestAgentSubLogger")
    self.logger.info("SimplestAgentSubLog.execute.message is: %s" % self.message)

    client = ClientA()

    client.logSomething()
    client.logSomethingFromB()

    result = client.addStuff("somethingWithAgent")
    if not result['OK']:
      self.log.error("Error while calling the service: %s" % result['Message'])
      return result
    self.log.info("Result of the request is %s" % result['Value'])
    return S_OK()
