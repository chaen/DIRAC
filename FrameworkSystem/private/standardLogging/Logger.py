import logging


class Logger(logging.getLoggerClass()):
  """
  A custom logger class for DIRAC use
  """

  def __init__(self, name):
    Logger.__init__(name)
