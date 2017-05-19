import logging
from DIRAC.FrameworkSystem.private.standardLogging.gLogging import gLogging
from DIRAC.FrameworkSystem.private.standardLogging.LogLevels import LogLevels


class gLogger():
  """
  Wrapper of the old gLogger object:
  - made to replace transparently gLogger
  - offer standard logging functionalities
  """

  __initializedLogging = False
  __levels = LogLevels()
  __gLogging = gLogging()

  def __init__(self, name=''):
    self.logger = logging.getLogger(name)

    if not gLogger.__initializedLogging:
      # add levels which has no equivalent in logging, in logging
      oldLevels = gLogger.__levels.getOldLevelNamesValues()
      for lvlName in oldLevels:
        logging.addLevelName(oldLevels[lvlName], lvlName)

      gLogger.__initializedLogging = True

  def initialized(self):
    return __initializedLogging

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
    logging.info("Logging register its backends itself.")

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
    if levelName in gLogger.__levels.getLevels():
      self.logger.setLevel(gLogger.__levels.getLevelValue(levelName))
      result = True
    return result

  def getLevel(self):
    """
    Return the name of the level
    """
    return gLogger.__levels.getLevel(self.logger.getEffectiveLevel())

  def shown(self, levelName):
    """
    Determine if messages with a certain level will be displayed or not
    input: 
    - levelName: string representing the level to analyse
    output:
    - result : boolean which give the answer
    """
    result = False
    if levelName in gLogger.__levels.getLevels():
      result = self.logger.isEnabledFor(gLogger.__levels.getLevelValue(levelName))
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
    return self.logger.name

  def getAllPossibleLevels(self):
    """
    Return a list of all levels available
    """
    return gLogger.__levels.getLevels()

  def always(self, sMsg, sVarMsg=''):
    level = gLogger.__levels.getLevelValue('ALWAYS')
    return self.__createLogRecord(level, sMsg, sVarMsg)
    

  def notice(self, sMsg, sVarMsg=''):
    level = gLogger.__levels.getLevelValue('NOTICE')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def info(self, sMsg, sVarMsg=''):
    level = gLogger.__levels.getLevelValue('INFO')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def verbose(self, sMsg, sVarMsg=''):
    level = gLogger.__levels.getLevelValue('VERBOSE')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def debug(self, sMsg, sVarMsg=''):
    level = gLogger.__levels.getLevelValue('DEBUG')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def warn(self, sMsg, sVarMsg=''):
    level = gLogger.__levels.getLevelValue('WARN')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def error(self, sMsg, sVarMsg=''):
    level = gLogger.__levels.getLevelValue('ERROR')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def exception(self, sMsg="", sVarMsg='', lException=False, lExcInfo=False):
    level = gLogger.__levels.getLevelValue('ERROR')
    return self.__createLogRecord(level, sMsg, sVarMsg, exc_info=True)

  def fatal(self, sMsg, sVarMsg=''):
    level = gLogger.__levels.getLevelValue('CRITICAL')
    return self.__createLogRecord(level, sMsg, sVarMsg)

  def __createLogRecord(self, level, sMsg, sVarMsg, exc_info=False):
    result = False
    if self.logger.isEnabledFor(level):
      self.logger.log(level, "%s %s" % (sMsg, sVarMsg), exc_info=exc_info)
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
