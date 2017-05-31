"""
StdoutBackend wrapper
"""

__RCSID__ = "$Id$"

import logging
import sys

from DIRAC.FrameworkSystem.private.standardLogging.Backend.Backend import Backend
from DIRAC.FrameworkSystem.private.standardLogging.Formatter.ColoredBaseFormatter import ColoredBaseFormatter


class StdoutBackend(Backend):
  """
  StdoutBackend is used to create an abstraction of the handler and the formatter concepts from logging. 
  Here, we gather a StreamHandler object and a BaseFormatter. 

  - StreamHandler is from the standard logging library: it is used to write log messages in a desired stream
    so it needs a name: here it is stdout. 
     
  - ColorBaseFormatter is a custom Formatter object, created for DIRAC in order to get the appropriate display
    with color.
    You can find it in FrameworkSystem/private/standardLogging/Formatter
  """

  def __init__(self):
    super(StdoutBackend, self).__init__(None, ColoredBaseFormatter)

  def setParameters(self, parameters):
    pass

  def configureHandler(self):
    """
    Initialize the handler with the parameters
    """
    self._handler = logging.StreamHandler(sys.stdout)
