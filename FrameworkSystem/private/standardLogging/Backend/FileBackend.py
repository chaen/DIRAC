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
    super(FileBackend, self).__init__(None, BaseFormatter())
    self.fileName = 'Dirac-log_%s.log' % getpid()

  def setParameters(self, parameters):
    if 'FileName' in parameters:
      self.fileName = parameters['FileName']

  def configureHandler(self):
    self.handler = logging.FileHandler(self.fileName)
