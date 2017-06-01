"""
Logger wrapper for DIRAC use
"""

__RCSID__ = "$Id$"

import logging

from DIRAC.FrameworkSystem.private.standardLogging.LoggingInitializer import LoggingInitializer
from DIRAC.FrameworkSystem.private.standardLogging.LogLevels import LogLevels


class gLogging(object):
  """
  The old gLogger object is now separated into two different objects: loggingInitializer and gLogging.
  gLogging is a wrapper of the logger object from the standard logging library which integrate
  some DIRAC concepts. 

  It is used like an interface to use the logger object of the logging library. 
  Its purpose is to replace transparently the old gLogger object in the existing code in order to 
  minimize the changes. 

  In this way, each gLogging embed a logger of logging. It is possible to create sublogger,
  set and get the level of the embedded logger and create log messages with it.

  gLogging delegate its configuration and its global attributes to LoggingInitializer: its purpose is to configure
  the root logger and all the functionalities that concern all the loggers. 
  """

  __gLogging = LoggingInitializer()

  def __init__(self, father= None, fathername='', name=''):
    """
    Initialization of the logger.
    :params fathername: string representing the name of the father logger in the chain.
    :params name: string representing the name of the logger in the chain. 
    By default, 'fathername' and 'name' are empty, because getChild accepts only string and the first empty
    string corresponds to the root logger. 

    Example: 
    logging.getLogger('') == logging.getLogger('root') root logger
    logging.getLogger('root').getChild('log') == root.log == log child of root
    """

    self.__childrens = []
    self.__parent = father
    # this test is True only the first time, at the initialization of the gLogger
    # it gets the root logger
    if not father:
      self.__logger = logging.getLogger(name)
    # then the other times, all loggers go to the else test
    # it corresponds to the children of the root logger
    else:
      self.__logger = logging.getLogger(fathername).getChild(name)

  def initialized(self):
    # initialized: Deleted method. Do not use it.
    return True

  def showHeaders(self, yesno=True):
    """
    Depending on the value, display or not the prefix of the message.
    :params yesno: boolean determining the behaviour of the display
    Delegate it to the LoggingWrapper because showHeaders is common to all loggers.
    """
    gLogging.__gLogging.showHeaders(yesno)

  def showThreadIDs(self, yesno=True):
    """
    Depending on the value, display or not the thread ID.
    :params yesno: boolean determining the behaviour of the display
    Delegate it to the LoggingWrapper because showThreadIDs is common to all loggers.
    """
    gLogging.__gLogging.showThreadIDs(yesno)

  def registerBackends(self, desiredBackends):
    gLogging.__gLogging.configureHandlers(desiredBackends, self.__logger)

  def initialize(self, systemName, cfgPath):
    """
    Delegate the root logger configuration to the LoggingWrapper. 
    It will add handlers to the root logger, format the display, set the appropriate
    levels. This will have an impact on all future loggers of the chain.  
    :params systemName: string represented as "system name/component name"
    :params cfgPath: string of the cfg file path
    """
    gLogging.__gLogging.loadConfigurationFromCFGFile(systemName, cfgPath)

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

  def getName(self):
    """
    :return: "system name/component name"
    """
    return gLogging.__gLogging.getComponent()

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
      self.__logger.log(level, "%s %s", sMsg, sVarMsg, exc_info=exc_info,
                        extra={'componentname': gLogging.__gLogging.getComponent()})
      result = True
    return result

  def showStack(self):
    return self.debug('')

  def processMessage(self, messageObject):
    # processMessage: Deleted method. Do not use it.
    return False

  def flushAllMessages(self, exitCode=0):
    # flushAllMessages: Deleted method. Do not use it.
    pass

  def getSubLogger(self, subName, child=True):
    """
    Create a new gLogger object, child of this logger.
    :params subName: the name of the child
    """
    child = gLogging(self, self.__logger.name, subName)
    self.__childrens.append(child)
    return child
