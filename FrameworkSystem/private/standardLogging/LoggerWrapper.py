"""
Logger wrapper for DIRAC use
"""
import logging

from DIRAC.FrameworkSystem.private.standardLogging.LoggingWrapper import LoggingWrapper
from DIRAC.FrameworkSystem.private.standardLogging.LogLevels import LogLevels


class LoggerWrapper(object):
  """
  Wrapper of the old Logger object:
  - made to replace transparently gLogger
  - based on the standard library 'logging'
  """

  __gLogging = LoggingWrapper()

  def __init__(self, name=''):
    self.__logger = logging.getLogger(name)

  def initialized(self):
    logging.warn("Initialized: Deleted method.")
    return True

  def showHeaders(self, yesno=True):
    """
    Depending on the value, display or not the prefix of the message.
    :params yesno: boolean determining the behaviour of the display
    """
    LoggerWrapper.__gLogging.showHeaders(yesno)

  def showThreadIDs(self, yesno=True):
    """
    Depending on the value, display or not the thread ID.
    :params yesno: boolean determining the behaviour of the display
    """
    LoggerWrapper.__gLogging.showThreadIDs(yesno)

  def registerBackends(self, desiredBackends):
    logging.warn("registerBackends: Deleted method. Logging register its backends itself.")

  def initialize(self, systemName, cfgPath):
    """
    Configure gLogger depending on the component used.
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
    return self.__logger.name

  def getAllPossibleLevels(self):
    """
    :return: a list of all levels available
    """
    return LogLevels.getLevelNames()

  def always(self, sMsg, sVarMsg=''):
    level = LogLevels.getLevelValue('ALWAYS')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def notice(self, sMsg, sVarMsg=''):
    level = LogLevels.getLevelValue('NOTICE')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def info(self, sMsg, sVarMsg=''):
    level = LogLevels.getLevelValue('INFO')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def verbose(self, sMsg, sVarMsg=''):
    level = LogLevels.getLevelValue('VERBOSE')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def debug(self, sMsg, sVarMsg=''):
    level = LogLevels.getLevelValue('DEBUG')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def warn(self, sMsg, sVarMsg=''):
    level = LogLevels.getLevelValue('WARNING')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def error(self, sMsg, sVarMsg=''):
    level = LogLevels.getLevelValue('ERROR')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def exception(self, sMsg="", sVarMsg='', lException=False, lExcInfo=False):
    level = LogLevels.getLevelValue('ERROR')
    return self.__createLogRecord(level, sMsg, sVarMsg, exc_info=True)

  def fatal(self, sMsg, sVarMsg=''):
    level = LogLevels.getLevelValue('CRITICAL')
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
      self.__logger.log(level, "%s %s", sMsg, sVarMsg, exc_info=exc_info)
      result = True
    return result

  def showStack(self):
    logging.warn("showStack: Deleted method.")

  def processMessage(self, messageObject):
    logging.warn("processMessage: Deleted method. Logging process its messages itself.")

  def flushAllMessages(self, exitCode=0):
    logging.warn("flushAllMessages: Deleted method. Logging flush all messages itself.")

  def getSubLogger(self, subName, child=True):
    """
    Create a new gLogger object, child of this logger.
    :params subName: the name of the child
    """
    return LoggerWrapper(subName)
