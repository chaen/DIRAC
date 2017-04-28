import logging
import sys

from DIRAC.TestLoggerSystem.private.logging.Backend.Backend import Backend
from DIRAC.TestLoggerSystem.private.logging.Formatter.BaseFormatter import BaseFormatter



class StderrBackend(Backend):

  def __init__(self):   
    super(StderrBackend, self).__init__(logging.StreamHandler(sys.stderr), BaseFormatter())

  def setParameters(self, parameters):
    pass