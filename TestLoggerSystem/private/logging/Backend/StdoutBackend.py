import logging
import sys

from DIRAC.TestLoggerSystem.private.logging.Backend.Backend import Backend
from DIRAC.TestLoggerSystem.private.logging.Formatter.ColoredBaseFormatter import ColoredBaseFormatter



class StdoutBackend(Backend):

  def __init__(self): 
    super(StdoutBackend, self).__init__(logging.StreamHandler(sys.stdout) , ColoredBaseFormatter())

  def setParameters(self, parameters):
    pass
