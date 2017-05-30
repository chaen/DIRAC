"""
BaseFormatter
"""

__RCSID__ = "$Id$"

import logging


class BaseFormatter(logging.Formatter):
  """
  Formatter of logging:
  - format messages to correspond with the gLogger format.
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

  def format(self, record):
    """
    Overriding

    Format for DIRAC use: add the "system/component" to the logname.
    """
    # pre treatment
    logname = record.name

    if record.name == "root":
      record.name = ""
    else:
      if record.name.startswith("root."):
        record.name = record.name.replace("root.", "")
        record.name = record.name.replace(".","/")
      record.name = "/" + record.name

    stringRecord = super(BaseFormatter, self).format(record)

    # this is important because logger creates the record and the same
    # record is used by different handlers
    record.name = logname

    return stringRecord
