import logging
from DIRAC.FrameworkSystem.private.standardLogging.gLogging import gLogging
from DIRAC.FrameworkSystem.private.standardLogging.LogLevels import LogLevels


class gLogger():
  """
  Wrapper of the old gLogger object:
  - made to replace transparently gLogger
  - offer standard logging functionalities
  """

  __gLogging = gLogging()

  def __init__(self, name=''):
    self.__logger = logging.getLogger(name)

  def initialized(self):
    logging.info("Initialized: Deleted method.")
    return True

  def showHeaders(self, yesno=True):
    """
    Depending on the value, display or not the prefix of the message
    input: 
    - yesno: boolean determining the behaviour of the display
    """
    gLogger.__gLogging.showHeaders(yesno)

  def showThreadIDs(self, yesno=True):
    """
    Depending on the value, display or not the thread ID
    input: 
    - yesno: boolean determining the behaviour of the display
    """
    gLogger.__gLogging.showThreadIDs(yesno)

  def registerBackends(self, desiredBackends):
    logging.info("registerBackends: Deleted method. Logging register its backends itself.")

  def initialize(self, systemName, cfgPath):
    """
    Configure gLogger depending on the component used
    input:
    - systemName: string represented as "system name/component name"
    - cfgPath: string of the cfg file path
    """
    gLogger.__gLogging.loadConfigurationFromCFGFile(systemName, cfgPath)

  def setLevel(self, levelName):
    """
    Set a level to the logger
    input:
    - levelName: string representing the level to give to the logger
    output:
    - result: boolean representing if the setting is done or not
    """
    result = False
    levelName = levelName.upper()
    if levelName in LogLevels.getLevelNames():
      self.__logger.setLevel(LogLevels.getLevelValue(levelName))
      result = True
    return result

  def getLevel(self):
    """
    Return the name of the level
    """
    return LogLevels.getLevel(self.__logger.getEffectiveLevel())

  def shown(self, levelName):
    """
    Determine if messages with a certain level will be displayed or not
    input: 
    - levelName: string representing the level to analyse
    output:
    - result : boolean which give the answer
    """
    result = False
    if levelName in LogLevels.getLevelNames():
      result = self.__logger.isEnabledFor(LogLevels.getLevelValue(levelName))
    return result

  def getName(self):
    """
    Return "system name/component name"
    """
    return gLogger.__gLogging.componentName

  def getSubName(self):
    """
    Return the name of the logger
    """
    return self.__logger.name

  def getAllPossibleLevels(self):
    """
    Return a list of all levels available
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
    result = False
    if self.__logger.isEnabledFor(level):
      self.__logger.log(level, "%s %s" % (sMsg, sVarMsg), exc_info=exc_info)
      result = True
    return result

  def showStack(self):
    logging.info("showStack: Deleted method.")

  def processMessage(self, messageObject):
    logging.info("processMessage: Deleted method. Logging process its messages itself.")

  def flushAllMessages(self, exitCode=0):
    logging.info("flushAllMessages: Deleted method. Logging flush all messages itself.")

  def getSubLogger(self, subName, child=True):
    """
    Create a new gLogger object, child of this logger
    input: 
    - subName: the name of the child
    """
    return gLogger(subName)
