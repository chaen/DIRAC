"""
Logger wrapper for DIRAC use
"""

__RCSID__ = "$Id$"

import logging

from DIRAC.FrameworkSystem.private.standardLogging.LoggingWrapper import LoggingWrapper
from DIRAC.FrameworkSystem.private.standardLogging.LogLevels import LogLevels


class LoggerWrapper(object):
  """
  The old gLogger object is now separated into two different objects: loggingWrapper and loggerWrapper.
  LoggerWrapper is a wrapper of the logger object from the standard logging library which integrate
  some DIRAC concepts. 

  It is used like an interface to use the logger object of the logging library. 
  Its purpose is to replace transparently the old gLogger object in the existing code in order to 
  minimize the changes. 

  In this way, each LoggerWrapper embed a logger of logging. It is possible to create sublogger,
  set and get the level of the embedded logger and create log messages with it.

  LoggerWrapper delegate its configuration and its global attributes to LoggingWrapper: its purpose is to configure
  the root logger and all the functionalities that concern all the loggers. 
  """

  __gLogging = LoggingWrapper()

  def __init__(self, fathername='', name=''):
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
    # this test is True only the first time, at the initialization of the gLogger
    # it gets the root logger
    if fathername == '':
      self.__logger = logging.getLogger(name)
    # then the other times, all loggers go to the else test
    # it corresponds to the children of the root logger
    else:
      self.__logger = logging.getLogger(fathername).getChild(name)

  def initialized(self):
    self.verbose("initialized: Deleted method. Do not use it.")
    return True

  def showHeaders(self, yesno=True):
    """
    Depending on the value, display or not the prefix of the message.
    :params yesno: boolean determining the behaviour of the display
    Delegate it to the LoggingWrapper because showHeaders is common to all loggers.
    """
    LoggerWrapper.__gLogging.showHeaders(yesno)

  def showThreadIDs(self, yesno=True):
    """
    Depending on the value, display or not the thread ID.
    :params yesno: boolean determining the behaviour of the display
    Delegate it to the LoggingWrapper because showThreadIDs is common to all loggers.
    """
    LoggerWrapper.__gLogging.showThreadIDs(yesno)

  def registerBackends(self, desiredBackends):
    self.verbose("registerBackends: Deleted method. Do not use it.")

  def initialize(self, systemName, cfgPath):
    """
    Delegate the root logger configuration to the LoggingWrapper. 
    It will add handlers to the root logger, format the display, set the appropriate
    levels. This will have an impact on all future loggers of the chain.  
    :params systemName: string represented as "system name/component name"
    :params cfgPath: string of the cfg file path
    """
    LoggerWrapper.__gLogging.loadConfigurationFromCFGFile(systemName, cfgPath)

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
    return LoggerWrapper.__gLogging.getComponent()

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
                        extra={'componentname': LoggerWrapper.__gLogging.getComponent()})
      result = True
    return result

  def showStack(self):
    self.verbose("showStack: Deleted method. Do not use it.")

  def processMessage(self, messageObject):
    self.verbose("processMessage: Deleted method. Do not use it.")

  def flushAllMessages(self, exitCode=0):
    self.verbose("flushAllMessages: Deleted method. Do not use it.")

  def getSubLogger(self, subName, child=True):
    """
    Create a new gLogger object, child of this logger.
    :params subName: the name of the child
    """
    return LoggerWrapper(self.__logger.name, subName)
