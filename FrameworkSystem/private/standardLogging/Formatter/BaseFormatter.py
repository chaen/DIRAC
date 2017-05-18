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
    self.componentName = componentName
    self.options = options

  def getThreadID(self):
    """
    Return a custom ID of the current thread : this is the gLogger method
    """
    _charData = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    rid = ""
    thid = str(threading.current_thread().ident)
    segments = []
    for iP in range(len(thid)):
      if iP % 4 == 0:
        segments.append("")
      segments[-1] += thid[iP]
    for seg in segments:
      rid += _charData[int(seg) % len(_charData)]
    return rid

  def format(self, record):
    """
    Overriding

    Format for DIRAC use
    """
    # pre treatment
    logname = record.name
    logmsg = record.msg
    logargs = record.args
    logexcinfo = record.exc_info
    lines = []

    if self.options['showHeaders']:
      if record.name != "root":
        record.name = self.componentName + "/" + record.name
      else:
        record.name = self.componentName

      if self.options['Path'] and logging.getLogger().getEffectiveLevel() == 10:
        record.name += '[' + record.pathname + ':' + str(record.lineno) + ']'
      if self.options['showThreads']:
        record.name += '[' + self.getThreadID() + ']'

    s = super(BaseFormatter, self).format(record)

    lines = record.message.split('\n') + lines
    # multi line message
    if len(lines) >= 2:
      s = ""
      record.args = None
      for line in lines:
        record.msg = line
        s += super(BaseFormatter, self).format(record) + "\n"

    # this is important because handler creates the record and the same
    # record is used by different handlers
    record.name = logname
    record.msg = logmsg
    record.args = logargs
    record.exc_info = logexcinfo

    return s.strip()
