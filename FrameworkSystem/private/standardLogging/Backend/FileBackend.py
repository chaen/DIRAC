"""
FileBackend wrapper
"""

__RCSID__ = "$Id$"

import logging
from os import getpid

from DIRAC.FrameworkSystem.private.standardLogging.Backend.Backend import Backend
from DIRAC.FrameworkSystem.private.standardLogging.Formatter.BaseFormatter import BaseFormatter


class FileBackend(Backend):
  """
  FileBackend is used to create an abstraction of the handler and the formatter concepts from logging. 
  Here, we gather a FileHandler object and a BaseFormatter. 

  - FileHandler is from the standard logging library: it is used to write log messages in a desired file
    so it needs a filename. 
    
  - BaseFormatter is a custom Formatter object, created for DIRAC in order to get the appropriate display.
    You can find it in FrameworkSystem/private/standardLogging/Formatter
  """

  def __init__(self):
    """
    :params __filename: string representing the default name of the file. 
                        The default name come from the old gLogger.
    """
    super(FileBackend, self).__init__(None, BaseFormatter)
    self.__fileName = 'Dirac-log_%s.log' % getpid()

  def setParameters(self, parameters):
    """
    Each backend can initialize its parameters for their handlers.
    :params parameters: dictionary of parameters. ex: {'FileName': file.log}
    default parameters or cfg options. 
    """
    if 'FileName' in parameters:
      self.__fileName = parameters['FileName']

  def configureHandler(self):
    """
    Initialize the handler with the parameters
    """
    self._handler = logging.FileHandler(self.__fileName)
