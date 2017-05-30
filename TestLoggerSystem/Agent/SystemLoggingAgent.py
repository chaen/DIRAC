""" :mod: SimplestAgent

    Simplest Agent send a simple log message
"""

# imports
from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.DISET.RPCClient import RPCClient

from DIRAC.FrameworkSystem.Client.LoggerClient import LoggerClient

__RCSID__ = "Id: $"


class SystemLoggingAgent(AgentModule):
  """
  .. class:: SimplestAgent

  Simplest agent
  print a message on log
  """

  def initialize(self):
    """ agent's initalisation

    :param self: self reference
    """
    return S_OK()

  def execute(self):
    """ execution in one agent's cycle

    :param self: self reference
    """
    client = LoggerClient()
    result = client.getMessagesBySystem("TestLogger/SimplestAgent")
    if not result['OK']:
      self.log.error("Error while calling the service: %s" % result['Message'])
      return result
    print result['Value']

    print "-----------------------------------------"

    result = client.getSystems()
    if not result['OK']:
      self.log.error("Error while calling the service: %s" % result['Message'])
      return result
    print result['Value']

    #print "-----------------------------------------"
    #
    #result = client.getCountMessages()
    #if not result['OK']:
    #  self.log.error("Error while calling the service: %s" % result['Message'])
    #  return result
    #print result['Value']

    print "-----------------------------------------"

    result = client.getMessages()
    if not result['OK']:
      self.log.error("Error while calling the service: %s" % result['Message'])
      return result
    print result['Value']
    return S_OK()
