from DIRAC.TestLoggerSystem.private.logging.Formatter.BaseFormatter import BaseFormatter 

class ColoredBaseFormatter(BaseFormatter):

  def __init__(self, fmt, datefmt, componentName):
    super(ColoredBaseFormatter, self).__init__(fmt, datefmt, componentName)

  def format(self, record):
    return super(ColoredBaseFormatter, self).format(record)