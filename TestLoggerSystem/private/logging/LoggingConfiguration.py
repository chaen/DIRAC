import logging
import time
import sys
from os import getpid

from DIRAC.TestLoggerSystem.private.logging.Formatter.BaseFormatter import BaseFormatter
from DIRAC.TestLoggerSystem.private.logging.Formatter.ColoredBaseFormatter import ColoredBaseFormatter
from DIRAC.TestLoggerSystem.private.logging.Backend import Backend

"""
Logging configuration class.
First new logging solution :
Advantages  :  Minimise maintenability, minimise modification
Drawbacks   :  Modify existing logging, alter standard
"""


class LoggingConfiguration():
  """
  Configuration of the standard Python logging to fit with the dirac gLogger 
  """

  @classmethod
  def initializeLogging(cls):
    """
    First logging configuration
    """
    # initialization
    cls.__initializeLoggingLevels()
    cls.__initializeDefaultParameters()
    cls.__initializeBackends()
    cls.__configureHandlers(['stdout'])
    # configuration
    cls.__configureLevel()
    cls.__updateFormat()
    #cls.configureLogging(cls.componentName, cls.cfgPath)

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
  def __initializeDefaultParameters(cls):
    cls.options = {'showHeaders': True, 'showThreads': False,
                   'Color': False, 'FileName': 'Dirac-log_%s.log' % getpid()}
    cls.componentName = "Framework"
    cls.cfgPath = None

  @classmethod
  def __initializeBackends(cls):
    logging.Formatter.converter = time.gmtime
    cls.backendsDict = {'stdout': ('stdout', logging.StreamHandler(sys.stdout), ColoredBaseFormatter()),
                        'stderr': ('stderr', logging.StreamHandler(sys.stderr), BaseFormatter()),
                        'file': ('file', logging.FileHandler(cls.options['FileName']), BaseFormatter())
                        }
    cls.backendsList = []

  @classmethod
  def __configureHandlers(cls, listHandler):
    """
    Attach handler to the root logger
    """
    # update backends which can be modified
    cls.backendsDict['file'] = ('file', logging.FileHandler(
        cls.options['FileName']), BaseFormatter())

    for stringHandler in listHandler:
      stringHandler = stringHandler.lower()
      stringHandler = stringHandler.strip(" ")
      if stringHandler in cls.backendsDict:
        name, handler, formatter = cls.backendsDict[stringHandler]
        logging.getLogger().addHandler(handler)
        cls.backendsList.append(Backend(name, handler, formatter))
      else:
        logging.warning("Unexistant method for showing messages Unexistant %s logging method", stringHandler)

  @classmethod
  def configureLogging(cls, componentName, cfgPath):
    """
    Create and set a new format with the component name to the handlers
    """
    # If not here. doesn't work because of loop dependancies
    from DIRAC.ConfigurationSystem.Client.Config import gConfig

    cls.componentName = componentName
    cls.cfgPath = cfgPath

    # Backend options
    retDict = gConfig.getOptionsDict("%s/BackendsOptions" % cfgPath)
    if retDict['OK']:
      newCfgOptions = retDict['Value']
      if 'FileName' in newCfgOptions:
        cls.options['FileName'] = newCfgOptions['Filename']

    # Log color options
    cls.options['Color'] = gConfig.getValue("%s/LogColor" % cfgPath, False)

    # Configure outputs
    desiredBackends = gConfig.getValue("%s/LogBackends" % cfgPath, 'stdout')
    cls.__configureHandlers(desiredBackends.split(','))

    # Configure verbosity
    #defaultLevel = Logger.defaultLogLevel
    # if "Scripts" in cfgPath:
    #  defaultLevel = gConfig.getValue(
    #      '/Systems/Scripts/LogLevel', Logger.defaultLogLevel)
    #self.setLevel(gConfig.getValue("%s/LogLevel" % cfgPath, defaultLevel))
    # Configure framing
    # self._showCallingFrame = gConfig.getValue(
    #    "%s/LogShowLine" % cfgPath, self._showCallingFrame)

    cls.__updateFormat()

  @classmethod
  def __configureLevel(cls):
    """
    Configure the log level of the running program according to the argv parameter
    It can be : -d, -dd, -ddd
    """
    debLevs = 0
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    for arg in sys.argv:
      if arg.find("-d") == 0:
        debLevs += arg.count("d")
    if debLevs == 1:
      logger.setLevel(logging.VERBOSE)
    elif debLevs == 2:
      logger.setLevel(logging.VERBOSE)
      cls.showHeaders(True)
    elif debLevs >= 3:
      logger.setLevel(logging.DEBUG)
      cls.showHeaders(True)
      cls.showThreadIDs(True)

  @classmethod
  def __setFormatter(cls, fmt, datefmt):
    """
    Add the new formatter to the handlers' logger 
    """
    logger = logging.getLogger()
    for backend in cls.backendsList:
      formatter = backend.formatter
      formatter.setFormat(fmt, datefmt, cls.componentName, cls.options)
      backend.handler.setFormatter(formatter)

  @classmethod
  def showHeaders(cls, val=True):
    """
    Define if it shows all information about the log or only the message
    """
    cls.options['showHeaders'] = val
    cls.__updateFormat()

  @classmethod
  def showThreadIDs(cls, val=True):
    """
    Define if it shows the thread id information about the log or not
    """
    cls.options['showThreads'] = val

  @classmethod
  def __updateFormat(cls):
    """
    Update the format according to the showHeader option
    """
    if cls.options['showHeaders']:
      fmt = 'Logging | %(asctime)s UTC %(name)s %(levelname)s: %(message)s'
      datefmt = '%Y-%m-%d %H:%M:%S'
    else:
      fmt = '%(message)s'
      datefmt = None
    cls.__setFormatter(fmt, datefmt)
