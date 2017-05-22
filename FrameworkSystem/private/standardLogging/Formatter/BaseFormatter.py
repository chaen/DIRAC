import logging
import threading
import traceback


class BaseFormatter(logging.Formatter):
  """
  Formatter of logging

  Format messages to correspond with the gLogger format
  """

  def setFormat(self, fmt, datefmt, componentName, options):
    """
    Initialize the formatter with new arguments
    input:
    - fmt : string representing the format: "%(asctime)s UTC %(name)s %(levelname)s: %(message)"
    - datefmt : string representing the date format: "%Y-%m-%d %H:%M:%S"
    - componentName: string represented as "System/Component"
    - options: dictionary of logging DIRAC options
    """
    super(BaseFormatter, self).__init__(fmt, datefmt)
    self._componentName = componentName
    self._options = options

  def format(self, record):
    """
    Overriding

    Format for DIRAC use
    """
    # pre treatment
    logname = record.name

    if record.name != "root":
      record.name = self._componentName + "/" + record.name
    else:
      record.name = self._componentName

    s = super(BaseFormatter, self).format(record)

    # this is important because handler creates the record and the same
    # record is used by different handlers
    record.name = logname

    return s
