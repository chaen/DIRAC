"""
StderrBackend wrapper
"""

__RCSID__ = "$Id$"

import logging
import sys

from DIRAC.FrameworkSystem.private.standardLogging.Backend.Backend import Backend
from DIRAC.FrameworkSystem.private.standardLogging.Formatter.BaseFormatter import BaseFormatter


class StderrBackend(Backend):
  """
  Stderr backend wrapper
  StreamHandler(stderr) + BaseFormatter
  """

  def __init__(self):
    super(StderrBackend, self).__init__(None, BaseFormatter)

  def setParameters(self, parameters):
    pass

  def configureHandler(self):
    """
    Initialize the handler with the parameters
    """
    self._handler = logging.StreamHandler(sys.stderr)
