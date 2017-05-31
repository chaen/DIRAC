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

  def format(self, record):
    """
    Overriding. 
    format is the main method of the Formatter object because it is the method which transforms 
    a log record into a string. 

    In this case, the format method change the record name to replace "root" by nothing to avoid
    to pollute the display. 
    In fact, "root" corresponds to the first logger and can appears in all messages. 

    Moreover, the format method change "." by "/" in the log chain.

    For example : Framework/Atom/root.log.sublog will become Framework/Atom/log/sublog

    :params record: the log record containing all the information about the log message: name, level, threadid...
    """
    # create a record name copy
    logname = record.name

    # format the record name removing "root", replacing "." by "/"
    record.name = record.name.replace("root", "")

    if record.name != "":
      record.name = record.name.replace(".", "/")

    # format the record
    stringRecord = super(BaseFormatter, self).format(record)

    # restore the record name with the copy
    # useful because the same record name is used by different handlers and it does not be changed.
    record.name = logname

    return stringRecord
