import logging
from DIRAC.FrameworkSystem.private.standardLogging.LoggingConfiguration import LoggingConfiguration
from DIRAC.FrameworkSystem.private.standardLogging.LogLevels import LogLevels


class gLogger():
  """
  Wrapper of the old gLogger object:
  - made to replace transparently gLogger
  - offer standard logging functionalities
  """

  _initializedLogging = False
  _levels = LogLevels()
  _loggingConfiguration = LoggingConfiguration()

  def __init__(self, name=''):
    self.logger = logging.getLogger(name)

    if not gLogger._initializedLogging:
      # add levels which has no equivalent in logging, in logging
      oldLevels = gLogger._levels.getOldLevelNamesValues()
      for lvlName in oldLevels:
        logging.addLevelName(oldLevels[lvlName], lvlName)

      gLogger._initializedLogging = True

  def initialized(self):
    return _initializedLogging

  def showHeaders(self, yesno=True):
    """
    Depending on the value, display or not the prefix of the message
    input: 
    - yesno: boolean determining the behaviour of the display
    """
    gLogger._loggingConfiguration.showHeaders(yesno)

  def showThreadIDs(self, yesno=True):
    """
    Depending on the value, display or not the thread ID
    input: 
    - yesno: boolean determining the behaviour of the display
    """
    gLogger._loggingConfiguration.showThreadIDs(yesno)

  def registerBackends(self, desiredBackends):
    logging.info("Logging register its backends itself.")

  def initialize(self, systemName, cfgPath):
    """
    Configure gLogger depending on the component used
    input:
    - systemName: string represented as "system name/component name"
    - cfgPath: string of the cfg file path
    """
    gLogger._loggingConfiguration.configureLogging(systemName, cfgPath)

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
    if levelName in gLogger._levels.getLevels():
      self.logger.setLevel(gLogger._levels.getLevelValue(levelName))
      result = True
    return result

  def getLevel(self):
    """
    Return the name of the level
    """
    return gLogger._levels.getLevel(self.logger.getEffectiveLevel())

  def shown(self, levelName):
    """
    Determine if messages with a certain level will be displayed or not
    input: 
    - levelName: string representing the level to analyse
    output:
    - result : boolean which give the answer
    """
    result = False
    if levelName in gLogger._levels.getLevels():
      result = self.logger.isEnabledFor(
          gLogger._levels.getLevelValue(levelName))
    return result

  def getName(self):
    """
    Return "system name/component name"
    """
    return gLogger._loggingConfiguration.componentName

  def getSubName(self):
    """
    Return the name of the logger
    """
    return self.logger.name

  def getAllPossibleLevels(self):
    """
    Return a list of all levels available
    """
    return gLogger._levels.getLevels()

  def always(self, sMsg, sVarMsg=''):
    self.logger.log(gLogger._levels.getLevelValue('ALWAYS'), "%s %s" % (sMsg, sVarMsg))

  def notice(self, sMsg, sVarMsg=''):
    self.logger.log(gLogger._levels.getLevelValue('NOTICE'), "%s %s" % (sMsg, sVarMsg))

  def info(self, sMsg, sVarMsg=''):
    self.logger.info("%s %s" % (sMsg, sVarMsg))

  def verbose(self, sMsg, sVarMsg=''):
    self.logger.log(gLogger._levels.getLevelValue('VERBOSE'), "%s %s" % (sMsg, sVarMsg))

  def debug(self, sMsg, sVarMsg=''):
    self.logger.debug("%s %s" % (sMsg, sVarMsg))

  def warn(self, sMsg, sVarMsg=''):
    self.logger.warn("%s %s" % (sMsg, sVarMsg))

  def error(self, sMsg, sVarMsg=''):
    self.logger.error("%s %s" % (sMsg, sVarMsg))

  def exception(self, sMsg="", sVarMsg='', lException=False, lExcInfo=False):
    self.logger.log(gLogger._levels.getLevelValue('EXCEPTION'), "%s %s" % (sMsg, sVarMsg), exc_info=True)

  def fatal(self, sMsg, sVarMsg=''):
    self.logger.log(gLogger._levels.getLevelValue('FATAL'), "%s %s" % (sMsg, sVarMsg))

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
