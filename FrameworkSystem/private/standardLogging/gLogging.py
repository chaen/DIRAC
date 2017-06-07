"""
gLogging
"""

__RCSID__ = "$Id$"

import logging

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

  # componentName is a class variable because the component name is the same for every gLogging objects
  # its default value is "Framework" but it can be configured and composed by the system name and the component name
  _componentName = "Framework"

  def __init__(self, father=None, fathername='', name=''):
    """
    Initialization of the gLogging object.
    :params father: gLogging, father of this new gLogging.
    :params fathername: string representing the name of the father logger in the chain.
    :params name: string representing the name of the logger in the chain. 
    By default, 'fathername' and 'name' are empty, because getChild accepts only string and the first empty
    string corresponds to the root logger. 

    Example: 
    logging.getLogger('') == logging.getLogger('root') root logger
    logging.getLogger('root').getChild('log') == root.log == log child of root
    """

    # gLogging chain
    self._children = []
    self._parent = father

    # all the different backends
    self._backendsDict = {'stdout': StdoutBackend(),
                          'stderr': StderrBackend(),
                          'file': FileBackend(),
                          'server': RemoteBackend()}

    # initialize display options and level with the ones of the gLogging parent
    if self._parent is not None:
      self._options = self._parent.getDisplayOptions()
      self._level = LogLevels.getLevelValue(father.getLevel())
    else:
      self._options = {'showHeaders': True, 'showThreads': False, 'Color': False, 'Path': False}
      # the native level is not used because it has to be to debug to send all messages to the log central
      self._level = None

    # dictionary of the option state, modified by the user or not
    # this is to give to the options the same behaviour that the logging setLevel()
    self._optionsmodified = {'showHeaders': False, 'showThreads': False}
    self._levelmodified = False

    self._backendsList = []

    self._logger = logging.getLogger(fathername).getChild(name)

  def showHeaders(self, yesno=True):
    """
    Depending on the value, display or not the prefix of the message.
    :params yesno: boolean determining the behaviour of the display
    """
    self._setOption('showHeaders', yesno)

  def showThreadIDs(self, yesno=True):
    """
    Depending on the value, display or not the thread ID.
    :params yesno: boolean determining the behaviour of the display
    """
    self._setOption('showThreads', yesno)

  def _setOption(self, optionName, value):
    """
    Depending on the value, modify the value of the option.
    This option will not be modified anymore. 
    The options of the children will be updated if they were not modified before by a developer
    :params optionName: string representing the name of the option to modify
    :params value: boolean to give to the option  
    """
    self._options[optionName] = value
    self._optionsmodified[optionName] = True
    self._setChildrenDisplayOptions(optionName, self._options)
    self._updateFormat()

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
      if stringHandler in self._backendsDict:
        backend = self._backendsDict[stringHandler]

        # check if the backend is already in the list
        if backend not in self._backendsList:
          if backendOptions is not None:
            backend.setParameters(backendOptions.copy())

          backend.configureHandler()
          self._logger.addHandler(backend.getHandler())
          self._backendsList.append(backend)
          self._updateFormat()
      else:
        self._updateFormat()
        self.warn("%s is not a valid backend name.", stringHandler)

  def setLevel(self, levelName):
    """
    Set a level to the logger.
    :params levelName: string representing the level to give to the logger
    :return: boolean representing if the setting is done or not
    """
    result = False
    levelName = levelName.upper()
    if levelName in LogLevels.getLevelNames():
      level = LogLevels.getLevelValue(levelName)
      for backend in self._backendsList:
        backend.setLevel(level)

      self._level = level
      self._levelmodified = True
      self._setChildrenLevel(self._level)
      result = True
    return result

  def getLevel(self):
    """
    :return: the name of the level
    """
    return LogLevels.getLevel(self._level)

  def shown(self, levelName):
    """
    Determine if messages with a certain level will be displayed or not.
    :params levelName: string representing the level to analyse
    :return: boolean which give the answer
    """
    result = False
    levelName = levelName.upper()
    if levelName in LogLevels.getLevelNames():
      result = self._level <= LogLevels.getLevelValue(levelName)
    return result

  @staticmethod
  def getName():
    """
    :return: "system name/component name"
    """
    return gLogging._componentName

  def getSubName(self):
    """
    :return: the name of the logger
    """
    name = self._logger.name
    name = name.replace("root", "")

    if name != "":
      names = name.split('.')
      name = names[-1]

    return name

  def getDisplayOptions(self):
    """
    :return: a copy of the dictionary of the display options and their values
    """
    return self._options.copy()

  def _setChildrenDisplayOptions(self, optionName, options):
    """
    Set the display options of the children if they are not modified by the user
    """
    if not self._optionsmodified[optionName]:
      self._options = options.copy()
      self._updateFormat()
    for child in self._children:
      child._setChildrenDisplayOptions(optionName, options)

  def _setChildrenLevel(self, level):
    """
    Set the level of the children if it is not modified by the user
    """
    if not self._levelmodified:
      self._level = level
    for child in self._children:
      child._setChildrenLevel(level)

  @staticmethod
  def getAllPossibleLevels():
    """
    :return: a list of all levels available
    """
    return LogLevels.getLevelNames()

  def always(self, sMsg, sVarMsg=''):
    """
    Always level
    """
    level = LogLevels.getLevelValue('ALWAYS')
    return self._createLogRecord(level, sMsg, sVarMsg)

  def notice(self, sMsg, sVarMsg=''):
    """
    Notice level
    """
    level = LogLevels.getLevelValue('NOTICE')
    return self._createLogRecord(level, sMsg, sVarMsg)

  def info(self, sMsg, sVarMsg=''):
    """
    Info level
    """
    level = LogLevels.getLevelValue('INFO')
    return self._createLogRecord(level, sMsg, sVarMsg)

  def verbose(self, sMsg, sVarMsg=''):
    """
    Verbose level
    """
    level = LogLevels.getLevelValue('VERBOSE')
    return self._createLogRecord(level, sMsg, sVarMsg)

  def debug(self, sMsg, sVarMsg=''):
    """
    Debug level
    """
    level = LogLevels.getLevelValue('DEBUG')
    return self._createLogRecord(level, sMsg, sVarMsg)

  def warn(self, sMsg, sVarMsg=''):
    """
    Warn
    """
    level = LogLevels.getLevelValue('WARN')
    return self._createLogRecord(level, sMsg, sVarMsg)

  def error(self, sMsg, sVarMsg=''):
    """
    Error level
    """
    level = LogLevels.getLevelValue('ERROR')
    return self._createLogRecord(level, sMsg, sVarMsg)

  def exception(self, sMsg="", sVarMsg='', lException=False, lExcInfo=False):
    """
    Exception level
    """
    level = LogLevels.getLevelValue('ERROR')
    return self._createLogRecord(level, sMsg, sVarMsg, exc_info=True)

  def fatal(self, sMsg, sVarMsg=''):
    """
    Critical level
    """
    level = LogLevels.getLevelValue('FATAL')
    return self._createLogRecord(level, sMsg, sVarMsg)

  def _createLogRecord(self, level, sMsg, sVarMsg, exc_info=False):
    """
    Create a log record according to the level of the message.
    :params level: positive integer representing the level of the log record
    :params sMsg: string representing the message
    :params sVarMsg: string representing an optional message
    :params exc_info: boolean representing the stacktrace for the exception

    :return: boolean representing the result of the log record creation
    """
    result = False
    if self._level <= level:
      self._logger.log(level, "%s %s", sMsg, sVarMsg, exc_info=exc_info, extra={'componentname': self.getName()})
      result = True
    return result

  def showStack(self):
    """
    Display a debug message without any content.
    :return: boolean, True if the message is sent, else False
    """
    return self.debug('')

  def _updateFormat(self):
    """
    Update the format according to the options
    """
    fmt = '%(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    if self._options['showHeaders']:
      fmt = '%(asctime)s UTC %(componentname)s%(name)s'
      if self._options['Path'] and self._level == LogLevels.getLevelValue('DEBUG'):
        fmt += ' [%(pathname)s:%(lineno)d]'
      if self._options['showThreads']:
        fmt += ' [%(thread)d]'
      fmt += ' %(levelname)s: %(message)s'

    for backend in self._backendsList:
      backend.setFormat(fmt, datefmt, self._options)

  def getSubLogger(self, subName, child=True):
    """
    Create a new gLogging object, child of this gLogging, if it does not exists.
    :params subName: the name of the child
    """
    result = self._childExists(subName)
    if result is None:
      child = gLogging(self, self._logger.name, subName)
      self._children.append(child)
    else:
      child = result
    return child

  def _childExists(self, name):
    """
    Check if the object has a child with "name".
    :params name: the name of the child
    :return: boolean, True if it exists, else False
    """
    for child in self._children:
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
