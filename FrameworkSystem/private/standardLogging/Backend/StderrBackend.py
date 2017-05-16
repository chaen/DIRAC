import logging
import sys

from DIRAC.FrameworkSystem.private.standardLogging.Backend.Backend import Backend
from DIRAC.FrameworkSystem.private.standardLogging.Formatter.BaseFormatter import BaseFormatter



class StderrBackend(Backend):

  def __init__(self):   
    super(StderrBackend, self).__init__(None, BaseFormatter())

  def setParameters(self, parameters):
    self.handler = logging.StreamHandler(sys.stderr)