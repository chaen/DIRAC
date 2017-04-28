import logging

from DIRAC.TestLoggerSystem.private.logging.Backend.Backend import Backend
from DIRAC.TestLoggerSystem.private.logging.Formatter.BaseFormatter import BaseFormatter



class FileBackend(Backend):

  def __init__(self):
    super(FileBackend, self).__init__(None, BaseFormatter())

  def setParameters(self, parameters):
    self.handler = logging.FileHandler(parameters['FileName'])
