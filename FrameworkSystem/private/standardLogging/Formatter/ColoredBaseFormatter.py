"""
ColoredBaseFormatter
"""

__RCSID__ = "$Id$"

import sys

from DIRAC.FrameworkSystem.private.standardLogging.Formatter.BaseFormatter import BaseFormatter


class ColoredBaseFormatter(BaseFormatter):
  """
  Formatter of logging:
  - color all messages with a certain color according to the level
  of the messages.
  - useful to make the distinction between log records without colors like stderr
    and log records with colors like stdout.
  """
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
      'ALWAYS': ('black', 'white', False),
      'NOTICE': (None, 'magenta', False),
      'INFO': (None, 'green', False),
      'VERBOSE': (None, 'cyan', False),
      'DEBUG': (None, 'blue', False),
      'WARNING': (None, 'yellow', False),
      'ERROR': (None, 'red', False),
      'CRITICAL': ('red', 'black', False)
  }

  def format(self, record):
    """
    Overriding
    Format the record with colors
    """
    stringRecord = super(ColoredBaseFormatter, self).format(record)
    # post treatment
    if self._options['Color'] and sys.stdout.isatty():
      params = []
      bg, fg, bold = self.LEVEL_MAP[record.levelname]
      if bg in self.COLOR_MAP:
        params.append(str(self.COLOR_MAP[bg] + 40))
      if fg in self.COLOR_MAP:
        params.append(str(self.COLOR_MAP[fg] + 30))
      if bold:
        params.append('1')
      stringRecord = ("".join(('\x1b[', ";".join(params), 'm', stringRecord, '\x1b[0m')))

    return stringRecord
