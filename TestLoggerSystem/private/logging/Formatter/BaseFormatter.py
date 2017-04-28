import logging
import threading


class BaseFormatter(logging.Formatter):
  """
  Custom formatter which include System/Component in the log message.
  """

  def setFormat(self, fmt, datefmt, componentName, options):
    super(BaseFormatter, self).__init__(fmt, datefmt)
    self.componentName = componentName
    self.options = options

  def getThreadID(self):
    """
    Return the ID of the current thread : this is the gLogger method
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
    """Override format to add System/Component name."""
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

      if self.options['Path']:
        record.name += '['+ record.pathname + ':' + str(record.lineno) + ']'
      if self.options['showThreads']:
        record.name += '[' + self.getThreadID() + ']'

    # exception format
    if record.exc_info is not None:
      exceptionMsg = "== EXCEPTION == " + record.exc_info[0].__name__ + "\n\n" + \
          record.exc_info[0].__name__ + ": " + \
          str(record.exc_info[1]) + "\n" + "==============="
      record.exc_info = None
      # add to lines for multiple line format
      lines.extend(exceptionMsg.split('\n'))

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
    # handler use the same record for different backends
    record.name = logname
    record.msg = logmsg
    record.args = logargs
    record.exc_info = logexcinfo

    return s.strip()
