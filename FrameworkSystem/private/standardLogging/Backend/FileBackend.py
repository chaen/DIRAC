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
  File backend wrapper
  FileHandler() + BaseFormatter
  """

  def __init__(self):
    super(FileBackend, self).__init__(None, BaseFormatter)
    self.__fileName = 'Dirac-log_%s.log' % getpid()

  def setParameters(self, parameters):
    """
    Each backend can initialize its parameters for their handlers.
    :params parameters: dictionary of parameters. ex: {'FileName': file.log}
    """
    if 'FileName' in parameters:
      self.__fileName = parameters['FileName']

  def configureHandler(self):
    """
    Initialize the handler with the parameters
    """
    self._handler = logging.FileHandler(self.__fileName)
