import logging

from DIRAC.FrameworkSystem.private.standardLogging.Backend.Backend import Backend
from DIRAC.FrameworkSystem.private.standardLogging.Formatter.BaseFormatter import BaseFormatter



class FileBackend(Backend):

  def __init__(self):
    super(FileBackend, self).__init__(None, BaseFormatter())

  def setParameters(self, parameters):
    self.handler = logging.FileHandler(parameters['FileName'])
