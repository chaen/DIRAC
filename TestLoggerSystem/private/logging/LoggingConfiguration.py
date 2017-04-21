import logging
import time

"""
Logging configuration script.
First new logging solution :
Advantages  :  Minimise maintenability, minimise modification
Drawbacks   :  Modify existing logging, alter standard
"""

# to move in a new file if it works


class ComponentFormatter(logging.Formatter):
  """
  Custom formatter which include System/Component in the log message.
  """

  def __init__(self, fmt, datefmt, componentName):
    super(ComponentFormatter, self).__init__(fmt, datefmt)
    self.componentName = componentName

  def format(self, record):
    """Override format to add System/Component name."""
    if record.name != "root":
      record.name = self.componentName + "/" + record.name
    else:
      record.name = self.componentName
    return super(ComponentFormatter, self).format(record)


class LoggingConfiguration():
  """
  Configuration of the standard Python logging to fit with the dirac gLogger 
  """

  @classmethod
  def initializeLogging(cls):
    """
    First logging configuration
    """
    cls.__initializeLoggingLevels()
    cls.__initializeHandlers()
    cls.setComponentName()
    logging.getLogger().setLevel(logging.DEBUG)

  @classmethod
  def __initializeLoggingLevels(cls):
    """
    Give new level definition to logging. 
    Warning : 
    -difference between gLogger : not in V
    -maybe not important because gLogger never set level superior to DEBUG
    """
    levelDict = {10: "DEBUG",
                 20: "VERBOSE",
                 30: "WARN",
                 40: "INFO",
                 50: "EXCEPTION",
                 60: "NOTICE",
                 70: "ERROR",
                 80: "ALWAYS",
                 90: "FATAL",
                 }

    for level in levelDict:
      logging.addLevelName(level, levelDict[level])
      setattr(logging, levelDict[level], level)
      setattr(logging.Logger, levelDict[level].lower(),
              (lambda level: lambda inst, msg, *args, **kwargs: inst.log(level, msg, *args, **kwargs))(level))
      setattr(logging, levelDict[level].lower(), (lambda level: lambda msg,
                                                  *args, **kwargs: logging.log(level, msg, *args, **kwargs))(level))

  @classmethod
  def __initializeHandlers(cls):
    """
    Attach handler to the root logger
    """
    logging.getLogger().addHandler(logging.StreamHandler())

  @classmethod
  def setComponentName(cls, componentName="Framework"):
    """
    Create and set a new format with the component name to the handlers
    """
    logging.Formatter.converter = time.gmtime
    logger = logging.getLogger()
    for handler in logger.handlers:
      handler.setFormatter(ComponentFormatter(
          '%(asctime)s UTC %(name)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S', componentName))

  @classmethod
  def removeHandlers(cls):
    """
    This method is only for testing
    """
    logger = logging.getLogger()
    for handler in logger.handlers:
      logger.removeHandler(handler)
