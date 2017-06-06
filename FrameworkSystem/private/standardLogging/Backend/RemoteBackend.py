"""
ServerBackend wrapper
"""

__RCSID__ = "$Id$"

import DIRAC
from DIRAC.FrameworkSystem.private.standardLogging.Backend.AbstractBackend import AbstractBackend
from DIRAC.FrameworkSystem.private.standardLogging.Formatter.BaseFormatter import BaseFormatter
from DIRAC.FrameworkSystem.private.standardLogging.Handler.RemoteHandler import RemoteHandler
from DIRAC.FrameworkSystem.private.standardLogging.LogLevels import LogLevels


class RemoteBackend(AbstractBackend):
  """
  RemoteBackend is used to create an abstraction of the handler and the formatter concepts from logging. 
  Here, we gather a RemoteHandler object and a BaseFormatter. 

  - RemoteHandler is a custom handler object, created for DIRAC because it has no equivalent: 
    it is used to write log messages in a remote DIRAC service: SystemLogging from FrameworkSystem.
    You can find it in FrameworkSystem/private/standardLogging/Handler

  - BaseFormatter is a custom Formatter object, created for DIRAC in order to get the appropriate display.
    You can find it in FrameworkSystem/private/standardLogging/Formatter
  """

  def __init__(self):
    """
    :params __site: string representing the site where the log messages are from.
    :params __interactive: not used at the moment.
    :params __sleepTime: the time separating the log messages sending, in seconds.
    """
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

  def setLevel(self, level):
    pass
