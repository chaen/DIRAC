"""
BaseFormatter
"""

__RCSID__ = "$Id$"

import logging


class BaseFormatter(logging.Formatter):
  """
  BaseFormatter is used to format log record to create a string representing a log message. 
  It is based on the Formatter object of the standard logging library.

  This custom formatter is useful for format messages to correspond with the gLogger format.
  """

  def __init__(self, fmt, datefmt, options):
    """
    Initialize the formatter with new arguments.
    :params fmt: string representing the format: "%(asctime)s UTC %(name)s %(levelname)s: %(message)"
    :params datefmt: string representing the date format: "%Y-%m-%d %H:%M:%S"
    :params componentName: string represented as "System/Component"
    :params options: dictionary of logging DIRAC options
    """
    super(BaseFormatter, self).__init__(fmt, datefmt)
    self._options = options
