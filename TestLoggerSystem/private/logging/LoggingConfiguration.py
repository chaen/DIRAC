import logging
import time

"""
Logging configuration script.
First new logging solution :
Advantages  :  Minimise maintenability, minimise modification
Drawbacks   :  Modify existing logging, alter standard
"""

#to move in a new file if it works
class ComponentFormatter(logging.Formatter):

  def __init__(self, fmt, datefmt, componentName):
    super(ComponentFormatter, self).__init__(fmt, datefmt)
    self.componentName = componentName

  def format(self, record):
    if record.name != "root":
      record.name = self.componentName+"/"+record.name
    else:
      record.name = self.componentName
    return super(ComponentFormatter, self).format(record)


class LoggingConfiguration():

  @classmethod
  def initializeLogging(cls):
    cls.__initializeLoggingLevels()
    cls.__initializeHandlers()
    cls.setComponentName()
    logging.getLogger().setLevel(logging.NOTICE)

  @classmethod
  def __initializeLoggingLevels(cls):
    levelDict = {10: "ALWAYS",
                 20: "NOTICE",
                 30: "INFO",
                 40: "VERBOSE",
                 50: "DEBUG",
                 60: "WARN",
                 70: "ERROR",
                 80: "EXCEPTION",
                 90: "FATAL"}

    for level in levelDict:
      logging.addLevelName(level, levelDict[level])
      setattr(logging, levelDict[level], level)
      setattr(logging.Logger, levelDict[level].lower(),
              (lambda level: lambda inst, msg, *args, **kwargs: inst.log(level, msg, *args, **kwargs))(level))
      setattr(logging, levelDict[level].lower(), (lambda level: lambda msg,
                                                  *args, **kwargs: logging.log(level, msg, *args, **kwargs))(level))

  @classmethod
  def __initializeHandlers(cls):
    logging.getLogger().addHandler(logging.StreamHandler())


  @classmethod
  def setComponentName(cls, componentName="Framework"):
    logging.Formatter.converter = time.gmtime
    logger = logging.getLogger()
    for handler in logger.handlers:
      handler.setFormatter(ComponentFormatter(
          '%(asctime)s UTC %(name)s  %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S', componentName))

  @classmethod
  def removeHandlers(cls):
    logger = logging.getLogger()
    for handler in logger.handlers:
      logger.removeHandler(handler)


