import logging
import sys

from DIRAC.FrameworkSystem.private.standardLogging.Backend.Backend import Backend
from DIRAC.FrameworkSystem.private.standardLogging.Formatter.ColoredBaseFormatter import ColoredBaseFormatter



class StdoutBackend(Backend):

  def __init__(self): 
    super(StdoutBackend, self).__init__(None , ColoredBaseFormatter())

  def setParameters(self, parameters):
    self.handler = logging.StreamHandler(sys.stderr)
