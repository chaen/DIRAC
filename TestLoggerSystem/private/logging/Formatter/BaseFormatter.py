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
    if self.options['showHeaders']:
      if record.name != "root":
        record.name = self.componentName + "/" + record.name
      else:
        record.name = self.componentName
      
      if self.options['showThreads']:
        record.name += '[' + self.getThreadID() + ']'

    return super(BaseFormatter, self).format(record)