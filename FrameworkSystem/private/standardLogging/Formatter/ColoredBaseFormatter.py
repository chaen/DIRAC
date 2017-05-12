import sys

from DIRAC.FrameworkSystem.private.standardLogging.Formatter.BaseFormatter import BaseFormatter


class ColoredBaseFormatter(BaseFormatter):

  COLOR_MAP = {
      'black': 0,
      'red': 1,
      'green': 2,
      'yellow': 3,
      'blue': 4,
      'magenta': 5,
      'cyan': 6,
      'white': 7
  }

  LEVEL_MAP = {
      'DEBUG': (None, 'blue', False),
      'INFO': (None, 'green', False),      
      'WARNING': (None, 'yellow', False),
      'ERROR': (None, 'red', False),
      'CRITICAL': ('red', 'black', False)
  }

  def setFormat(self, fmt, datefmt, componentName, options):
    super(ColoredBaseFormatter, self).setFormat(
        fmt, datefmt, componentName, options)
    self.options = options

  def format(self, record):
    s = super(ColoredBaseFormatter, self).format(record)
    #post treatment
    if self.options['Color'] and sys.stdout.isatty():
      params = []
      bg, fg, bold = self.LEVEL_MAP[record.levelname]
      if bg in self.COLOR_MAP:
        params.append(str(self.COLOR_MAP[bg] + 40))
      if fg in self.COLOR_MAP:
        params.append(str(self.COLOR_MAP[fg] + 30))
      if bold:
        params.append('1')
      s = ("".join(('\x1b[', ";".join(params), 'm', s, '\x1b[0m')))

    return s
