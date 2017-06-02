"""
gLogging
"""

__RCSID__ = "$Id$"

import logging
import time
import sys

from DIRAC.FrameworkSystem.private.standardLogging.LogLevels import LogLevels

from DIRAC.FrameworkSystem.private.standardLogging.Backend.StdoutBackend import StdoutBackend
from DIRAC.FrameworkSystem.private.standardLogging.Backend.StderrBackend import StderrBackend
from DIRAC.FrameworkSystem.private.standardLogging.Backend.FileBackend import FileBackend
from DIRAC.FrameworkSystem.private.standardLogging.Backend.RemoteBackend import RemoteBackend


class gLogging(object):
  """
  gLogging is a wrapper of the logger object from the standard logging library which integrate
  some DIRAC concepts. It is the equivalent to the old gLogger object.

  It is used like an interface to use the logger object of the logging library. 
  Its purpose is to replace transparently the old gLogger object in the existing code in order to 
  minimize the changes. 

  In this way, each gLogging embed a logger of logging. It is possible to create sublogger,
  set and get the level of the embedded logger and create log messages with it.

  gLogging could delegate the initialization and the configuration to a factory of the root logger be it can not
  because it has to wrap the old gLogger.  
  """

  __componentName = "Framework"
  __configuredLogging = False

  def __init__(self, father=None, fathername='', name=''):
    """
    Initialization of the gLogging object.
    :params fathername: string representing the name of the father logger in the chain.
    :params name: string representing the name of the logger in the chain. 
    :params father: gLogging father of this new gLogging.
    By default, 'fathername' and 'name' are empty, because getChild accepts only string and the first empty
    string corresponds to the root logger. 

    Example: 
    logging.getLogger('') == logging.getLogger('root') root logger
    logging.getLogger('root').getChild('log') == root.log == log child of root
    """

    # gLogging chain
    self.__childrens = []
    self.__parent = father

    # all the different backends
    self.__backendsDict = {'stdout': StdoutBackend(),
                           'stderr': StderrBackend(),
                           'file': FileBackend(),
                           'server': RemoteBackend()}

    # initialize display options with the ones of the gLogging parent
    if self.__parent is not None:
      self.__options = self.__parent.getDisplayOptions()
    else:
      self.__options = {'showHeaders': True, 'showThreads': False, 'Color': False, 'Path': False}

    # dictionary of the option state, modified by the user or not
    # this is to give to the options the same behaviour that the logging setLevel()
    self.__optionsmodified = {'showHeaders': False, 'showThreads': False}

    self.__backendsList = []

    # this test is True only the first time, at the initialization of the gLogger
    # it initializes the root logger
    if not father:
      self.__logger = logging.getLogger(name)
      self.__logger.setLevel(LogLevels.getLevelValue('NOTICE'))
      logging.Formatter.converter = time.gmtime

      # initialization of levels
      levels = LogLevels.getLevels()
      for level in levels:
        logging.addLevelName(levels[level], level)

      # initialization of the default backend
      self.registerBackends(['stdout'])

      # configuration of the level and update of the format
      self.__configureLevel()
      self.__updateFormat()

    # then the other times, all loggers go to the else test
    # it corresponds to the childrens of the root logger
    else:
      self.__logger = logging.getLogger(fathername).getChild(name)

  def showHeaders(self, yesno=True):
    """
    Depending on the value, display or not the prefix of the message.
    :params yesno: boolean determining the behaviour of the display
    """
    self.__setOption('showHeaders', yesno)

  def showThreadIDs(self, yesno=True):
    """
    Depending on the value, display or not the thread ID.
    :params yesno: boolean determining the behaviour of the display
    """
    self.__setOption('showThreads', yesno)

  def __setOption(self, optionName, value):
    """
    Depending on the value, modify the value of the option.
    This option will not be modified anymore. 
    The options of the childrens will be updated if they were not modified before by a developer
    :params optionName: string representing the name of the option to modify
    :params value: boolean to give to the option  
    """
    self.__options[optionName] = value
    self.__optionsmodified[optionName] = True
    self._setChildrensDisplayOptions(optionName, self.__options)
    self.__updateFormat()

  def registerBackends(self, desiredBackends, backendOptions=None):
    """
    Attach a list of backends to the gLogging object.
    :params desiredBackends: a list of different names attaching to differents backends.
                             example : ['stdout', 'file', 'server']
    :params backendOptions: a dictionary of different backend options. 
                            example: {'FileName': '/tmp/log.txt'}
    """
    for stringHandler in desiredBackends:
      stringHandler = stringHandler.lower()
      stringHandler = stringHandler.strip()

      # check if the name is correct
      if stringHandler in self.__backendsDict:
        backend = self.__backendsDict[stringHandler]

        # check if the backend is already in the list
        if backend not in self.__backendsList:
          if backendOptions is not None:
            backend.setParameters(backendOptions.copy())

          backend.configureHandler()
          self.__logger.addHandler(backend.getHandler())
          self.__backendsList.append(backend)
          self.__updateFormat()
      else:
        self.__updateFormat()
        self.warn("%s is not a valid backend name.", stringHandler)

  def initialize(self, systemName, cfgPath):
    """
    Configure the root gLogging with a cfg file.
    It can be possible to :
    - attach it some backends : LogBackends = stdout,stderr,file,server 
    - attach backend options : BackendOptions { FileName = /tmp/file.log }
    - add colors and the path of the call : LogColor = True, LogShowLine = True
    - precise a level : LogLevel = DEBUG

    :params systemName: string represented as "system name/component name"
    :params cfgPath: string of the cfg file path
    """
    from DIRAC.ConfigurationSystem.Client.Config import gConfig

    if not gLogging.__configuredLogging:
      backends = (None, None)
      gLogging.__componentName = systemName

      # Backend options
      desiredBackendsStr = gConfig.getValue("%s/LogBackends" % cfgPath, 'stdout')
      desiredBackends = desiredBackendsStr.split(',')

      retDict = gConfig.getOptionsDict("%s/BackendsOptions" % cfgPath)
      if retDict['OK']:
        backends = (desiredBackends, retDict['Value'])
      else:
        backends = (desiredBackends, None)

      # Format options
      self.__options['Color'] = gConfig.getValue("%s/LogColor" % cfgPath, False)
      self.__options['Path'] = gConfig.getValue("%s/LogShowLine" % cfgPath, False)

      currentLevelName = logging.getLevelName(logging.getLogger().getEffectiveLevel())
      levelname = gConfig.getValue("%s/LogLevel" % cfgPath, currentLevelName)
      logging.getLogger().setLevel(logging.getLevelName(levelname))

      desiredBackends, backendOptions = backends
      self.registerBackends(desiredBackends, backendOptions)

      gLogging.__configuredLogging = True

  def setLevel(self, levelName):
    """
    Set a level to the logger.
    :params levelName: string representing the level to give to the logger
    :return: boolean representing if the setting is done or not
    """
    result = False
    levelName = levelName.upper()
    if levelName in LogLevels.getLevelNames():
      self.__logger.setLevel(LogLevels.getLevelValue(levelName))
      result = True
    return result

  def getLevel(self):
    """
    :return: the name of the level
    """
    return LogLevels.getLevel(self.__logger.getEffectiveLevel())

  def shown(self, levelName):
    """
    Determine if messages with a certain level will be displayed or not.
    :params levelName: string representing the level to analyse
    :return: boolean which give the answer
    """
    result = False
    levelName = levelName.upper()
    if levelName in LogLevels.getLevelNames():
      result = self.__logger.isEnabledFor(LogLevels.getLevelValue(levelName))
    return result

  @staticmethod
  def getName():
    """
    :return: "system name/component name"
    """
    return gLogging.__componentName

  def getSubName(self):
    """
    :return: the name of the logger
    """
    name = self.__logger.name
    name = name.replace("root", "")

    if name != "":
      names = name.split('.')
      name = names[-1]

    return name

  def getDisplayOptions(self):
    """
    :return: a copy of the dictionary of the display options and their values
    """
    return self.__options.copy()

  def _setChildrensDisplayOptions(self, optionName, options):
    """
    Set the display options of the childrens if they are not modified by the user
    """
    if not self.__optionsmodified[optionName]:
      self.__options = options.copy()
      self.__updateFormat()
    for child in self.__childrens:
      child._setChildrensDisplayOptions(optionName, options)

  def getAllPossibleLevels(self):
    """
    :return: a list of all levels available
    """
    return LogLevels.getLevelNames()

  def always(self, sMsg, sVarMsg=''):
    """
    Always level
    """
    level = LogLevels.getLevelValue('ALWAYS')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def notice(self, sMsg, sVarMsg=''):
    """
    Notice level
    """
    level = LogLevels.getLevelValue('NOTICE')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def info(self, sMsg, sVarMsg=''):
    """
    Info level
    """
    level = LogLevels.getLevelValue('INFO')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def verbose(self, sMsg, sVarMsg=''):
    """
    Verbose level
    """
    level = LogLevels.getLevelValue('VERBOSE')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def debug(self, sMsg, sVarMsg=''):
    """
    Debug level
    """
    level = LogLevels.getLevelValue('DEBUG')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def warn(self, sMsg, sVarMsg=''):
    """
    Warn
    """
    level = LogLevels.getLevelValue('WARN')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def error(self, sMsg, sVarMsg=''):
    """
    Error level
    """
    level = LogLevels.getLevelValue('ERROR')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def exception(self, sMsg="", sVarMsg='', lException=False, lExcInfo=False):
    """
    Exception level
    """
    level = LogLevels.getLevelValue('ERROR')
    return self.__createLogRecord(level, sMsg, sVarMsg, exc_info=True)

  def fatal(self, sMsg, sVarMsg=''):
    """
    Critical level
    """
    level = LogLevels.getLevelValue('FATAL')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def __createLogRecord(self, level, sMsg, sVarMsg, exc_info=False):
    """
    Create a log record according to the level of the message.
    :params level: positive integer representing the level of the log record
    :params sMsg: string representing the message
    :params sVarMsg: string representing an optional message
    :params exc_info: boolean representing the stacktrace for the exception

    :return: boolean representing the result of the log record creation
    """
    result = False
    if self.__logger.isEnabledFor(level):
      self.__logger.log(level, "%s %s", sMsg, sVarMsg, exc_info=exc_info, extra={'componentname': self.getName()})
      result = True
    return result

  def showStack(self):
    return self.debug('')

  def __updateFormat(self):
    """
    Update the format according to the options
    """
    fmt = '%(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    if self.__options['showHeaders']:
      fmt = '%(asctime)s UTC %(componentname)s%(name)s'
      if self.__options['Path'] and self.__logger.getEffectiveLevel() == LogLevels.getLevelValue('DEBUG'):
        fmt += ' [%(pathname)s:%(lineno)d]'
      if self.__options['showThreads']:
        fmt += ' [%(thread)d]'
      fmt += ' %(levelname)s: %(message)s'

    for backend in self.__backendsList:
      backend.setFormat(fmt, datefmt, self.__options)

  def __configureLevel(self):
    """
    Configure the log level of the root glogging according to the argv parameter
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

  def getSubLogger(self, subName, child=True):
    """
    Create a new gLogging object, child of this gLogging, if it does not exists.
    :params subName: the name of the child
    """
    result = self.__childExists(subName)
    if result is None:
      child = gLogging(self, self.__logger.name, subName)
      self.__childrens.append(child)
    else:
      child = result
    return child

  def __childExists(self, name):
    """
    Check if the object has a child with "name".
    :params name: the name of the child
    :return: boolean, True if it exists, else False
    """
    for child in self.__childrens:
      if name == child.getSubName():
        return child
    return None

  def initialized(self):
    # initialized: Deleted method. Do not use it.
    return True

  def processMessage(self, messageObject):
    # processMessage: Deleted method. Do not use it.
    return False

  def flushAllMessages(self, exitCode=0):
    # flushAllMessages: Deleted method. Do not use it.
    pass
