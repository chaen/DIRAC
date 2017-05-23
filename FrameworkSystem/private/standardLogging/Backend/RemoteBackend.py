"""
ServerBackend wrapper
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.FrameworkSystem.private.standardLogging.Backend.Backend import Backend
from DIRAC.FrameworkSystem.private.standardLogging.Formatter.BaseFormatter import BaseFormatter
from DIRAC.FrameworkSystem.private.standardLogging.Handler.RemoteHandler import RemoteHandler
from DIRAC.FrameworkSystem.private.standardLogging.LogLevels import LogLevels


class RemoteBackend(Backend):
  """
  File backend wrapper
  FileHandler() + BaseFormatter
  """

  def __init__(self):
    super(RemoteBackend, self).__init__(None, BaseFormatter)
    self.__site = None
    self.__interactive = True
    self.__sleepTime = 150

  def setParameters(self, parameters):
    """
    Each backend can initialize its parameters for their handlers.
    :params parameters: dictionary of parameters. ex: {'FileName': file.log}
    """
    self.__site = DIRAC.siteName()
    if 'Interactive' in parameters:
      self.__interactive = parameters['Interactive']
    if 'SleepTime' in parameters:
      self.__sleepTime = parameters['SleepTime']

  def configureHandler(self):
    """
    Initialize the handler with the parameters
    """
    self._handler = RemoteHandler(self.__sleepTime, self.__interactive, self.__site)
    self._handler.setLevel(LogLevels.getLevelValue('ERROR'))
