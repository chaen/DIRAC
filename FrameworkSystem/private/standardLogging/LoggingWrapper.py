"""
Logging wrapper for DIRAC use
"""

__RCSID__ = "$Id$"

import logging
import time
import sys

from DIRAC.FrameworkSystem.private.standardLogging.Backend.StdoutBackend import StdoutBackend
from DIRAC.FrameworkSystem.private.standardLogging.Backend.StderrBackend import StderrBackend
from DIRAC.FrameworkSystem.private.standardLogging.Backend.FileBackend import FileBackend
from DIRAC.FrameworkSystem.private.standardLogging.Backend.RemoteBackend import RemoteBackend
from DIRAC.FrameworkSystem.private.standardLogging.LogLevels import LogLevels


class LoggingWrapper(object):
  """
  The old gLogger object is now separated into two different objects: loggingWrapper and loggerWrapper.
  LoggingWrapper is a wrapper of the logging module from the standard logging library which integrate
  some DIRAC concepts. 

  Its purpose is to configure the root logger with the cfg file content: handlers and format. 
  As logging from the logging library is unique, we created a singleton to prevent that someone initialize
  the root logger 2 times. 

  It has all the global attributes of the old gLogger like showHeaders, showThreads, Color and Path. 
  LoggerWrapper delegate its configuration and its global attributes to LoggingWrapper.
  """
  __configuredLogging = False

  __instance = None

  def __new__(cls):
    """
    Initialization of the singleton.
    """
    if LoggingWrapper.__instance is None:
      LoggingWrapper.__instance = object.__new__(cls)
    return LoggingWrapper.__instance

  def __init__(self):
    """
    Initialization and first configuration of the root logger
    """
    # initialization of the default parameters
    logging.getLogger().setLevel(LogLevels.getLevelValue('NOTICE'))
    logging.Formatter.converter = time.gmtime

    self.__options = {'showHeaders': True, 'showThreads': False, 'Color': False, 'Path': False}
    self.__componentName = "Framework"

    # initialization of levels
    levels = LogLevels.getLevels()
    for level in levels:
      logging.addLevelName(levels[level], level)

    # initialization of the backends
    self.__backendsList = []
    self.__backendsDict = {'stdout': StdoutBackend(),
                           'stderr': StderrBackend(),
                           'file': FileBackend(),
                           'server': RemoteBackend()}
    self.__configureHandlers(['stdout'])

    # configuration of the level and update of the format
    self.__configureLevel()
    self.__updateFormat()

  def showHeaders(self, val=True):
    """
    Depending on the value, display or not the prefix of the message.
    :params val: boolean determining the behaviour of the display
    """
    self.__options['showHeaders'] = val
    self.__updateFormat()

  def showThreadIDs(self, val=True):
    """
    Depending on the value, display or not the thread ID.
    :params val: boolean determining the behaviour of the display
    """
    self.__options['showThreads'] = val
    self.__updateFormat()

  def getComponent(self):
    """
    :return: string represented as "system/format"
    """
    return self.__componentName

  def loadConfigurationFromCFGFile(self, componentName, cfgPath):
    """
    Configure logging with a cfg file.
    :params systemName: string represented as "system name/component name"
    :params cfgPath: string of the cfg file path
    """
    from DIRAC.ConfigurationSystem.Client.Config import gConfig

    if not LoggingWrapper.__configuredLogging:
      self.__componentName = componentName

      # Backend options
      desiredBackendsStr = gConfig.getValue("%s/LogBackends" % cfgPath, 'stdout')
      desiredBackends = desiredBackendsStr.split(',')

      for backend in desiredBackends:
        retDict = gConfig.getOptionsDict("%s/BackendsOptions" % cfgPath)
        if retDict['OK'] and backend in self.__backendsDict:
          self.__backendsDict[backend].setParameters(retDict['Value'].copy())

      # Format options
      self.__options['Color'] = gConfig.getValue("%s/LogColor" % cfgPath, False)
      self.__options['Path'] = gConfig.getValue("%s/LogShowLine" % cfgPath, False)

      currentLevelName = logging.getLevelName(logging.getLogger().getEffectiveLevel())
      levelname = gConfig.getValue("%s/LogLevel" % cfgPath, currentLevelName)
      logging.getLogger().setLevel(logging.getLevelName(levelname))

      # Configure outputs
      self.__configureHandlers(desiredBackends)
      self.__updateFormat()

      LoggingWrapper.__configuredLogging = True

  def __configureHandlers(self, listHandler):
    """
    Attach a list of handlers to the root logger
    :params listHandler: a list of different names attaching to differents backends.
    """
    for stringHandler in listHandler:
      stringHandler = stringHandler.lower()
      stringHandler = stringHandler.strip()

      if stringHandler in self.__backendsDict:
        backend = self.__backendsDict[stringHandler]

        if backend not in self.__backendsList:
          backend.configureHandler()
          logging.getLogger().addHandler(backend.getHandler())
          self.__backendsList.append(backend)
      else:
        self.__updateFormat()
        logging.warn("%s is not a valid backend name.", stringHandler, extra={'componentname': self.__componentName})

  def __configureLevel(self):
    """
    Configure the log level of the running program according to the argv parameter
    It can be : -d, -dd, -ddd
    Work only for clients, scripts and tests
    Configuration/Client/LocalConfiguration manages services,agents and executors
    """
    debLevs = 0
    logger = logging.getLogger()
    for arg in sys.argv:
      if arg.find("-d") == 0:
        debLevs += arg.count("d")
    if debLevs == 1:
      logger.setLevel(LogLevels.getLevelValue('VERBOSE'))
    elif debLevs == 2:
      logger.setLevel(LogLevels.getLevelValue('VERBOSE'))
      self.showHeaders(True)
    elif debLevs >= 3:
      logger.setLevel(LogLevels.getLevelValue('DEBUG'))
      self.showHeaders(True)
      self.showThreadIDs(True)

  def __updateFormat(self):
    """
    Update the format according to the options
    """
    fmt = '%(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    if self.__options['showHeaders']:
      fmt = '%(asctime)s UTC %(componentname)s%(name)s'
      if self.__options['Path'] and logging.getLogger().getEffectiveLevel() == LogLevels.getLevelValue('DEBUG'):
        fmt += ' [%(pathname)s:%(lineno)d]'
      if self.__options['showThreads']:
        fmt += ' [%(thread)d]'
      fmt += ' %(levelname)s: %(message)s'

    for backend in self.__backendsList:
      backend.setFormat(fmt, datefmt, self.__options)
