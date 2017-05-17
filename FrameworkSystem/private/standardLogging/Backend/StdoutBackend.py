import logging
import sys

from DIRAC.FrameworkSystem.private.standardLogging.Backend.Backend import Backend
from DIRAC.FrameworkSystem.private.standardLogging.Formatter.ColoredBaseFormatter import ColoredBaseFormatter


class StdoutBackend(Backend):
  """
  Stdout backend wrapper
  StreamHandler(stdout) + ColorFormatter
  """

  def __init__(self):
    super(StdoutBackend, self).__init__(None, ColoredBaseFormatter())

  def setParameters(self, parameters):
    self.handler = logging.StreamHandler(sys.stdout)
