import logging
from DIRAC.FrameworkSystem.private.standardLogging.LoggingConfiguration import LoggingConfiguration


class gLogger():
  """
  Wrapper of the old gLogger object
  """

  _levels = {"always": logging.INFO,
             "notice": logging.INFO,
             "info": logging.INFO,
             "verbose": logging.INFO,
             "debug": logging.DEBUG,
             "warn": logging.WARN,
             "exception": logging.ERROR,
             "error": logging.ERROR,
             "fatal": logging.CRITICAL}

  _initializedLogging = False
  _configuredLogging = False

  def __init__(self, name=''):
    self.logger = logging.getLogger(name)
    if not gLogger._initializedLogging:
      LoggingConfiguration.initializeLogging()
      gLogger._initializedLogging = True


  def initialized(self):
    return _initializedLogging

  def showHeaders(self, yesno=True):
    LoggingConfiguration.showHeaders(yesno)

  def showThreadIDs(self, yesno=True):
    LoggingConfiguration.showThreadIDs(yesno)

  def registerBackends(self, desiredBackends):
    logging.info("Logging register its backends itself.")

  def initialize(self, systemName, cfgPath):
    if not gLogger._configuredLogging:
      LoggingConfiguration.configureLogging(systemName, cfgPath)
      gLogger._configuredLogging = True

  def setLevel(self, levelName):
    result = False
    if levelName in gLogger._levels:
      self.logger.setLevel(gLogger._levels[levelName])
      result = True
    return result

  def getLevel(self):
    return self.logger.getEffectiveLevel()

  def shown(self, levelName):
    result = False
    if levelName in gLogger._levels:
      result = self.logger.isEnabledFor(gLogger._levels[levelName])
    return result

  def getName(self):
    return self.logger.name

  def always(self, sMsg, sVarMsg=''):
    self.logger.info("%s %s" % (sMsg, sVarMsg))

  def notice(self, sMsg, sVarMsg=''):
    self.logger.info("%s %s" % (sMsg, sVarMsg))

  def info(self, sMsg, sVarMsg=''):
    self.logger.info("%s %s" % (sMsg, sVarMsg))

  def verbose(self, sMsg, sVarMsg=''):
    self.logger.info("%s %s" % (sMsg, sVarMsg))

  def debug(self, sMsg, sVarMsg=''):
    self.logger.debug("%s %s" % (sMsg, sVarMsg))

  def warn(self, sMsg, sVarMsg=''):
    self.logger.warn("%s %s" % (sMsg, sVarMsg))

  def error(self, sMsg, sVarMsg=''):
    self.logger.error("%s %s" % (sMsg, sVarMsg))

  def exception(self, sMsg="", sVarMsg='', lException=False, lExcInfo=False):
    self.logger.exception("%s %s" % (sMsg, sVarMsg))

  def fatal(self, sMsg, sVarMsg=''):
    self.logger.critical("%s %s" % (sMsg, sVarMsg))

  def showStack(self):
    logging.info("Deleted method.")

  def processMessage(self, messageObject):
    logging.info("Logging process its messages itself.")

  def flushAllMessages(self, exitCode=0):
    logging.info("Logging flush all messages itself.")

  def getSubLogger(self, subName, child=True):
    return gLogger(subName)
