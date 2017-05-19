import logging
import time
import sys

from DIRAC.FrameworkSystem.private.standardLogging.Backend.StdoutBackend import StdoutBackend
from DIRAC.FrameworkSystem.private.standardLogging.Backend.StderrBackend import StderrBackend
from DIRAC.FrameworkSystem.private.standardLogging.Backend.FileBackend import FileBackend
from DIRAC.FrameworkSystem.private.standardLogging.Backend.LogLevels import LogLevels


class gLogging(object):
  """
  Configuration of the standard Python logging for DIRAC use
  """
  __configuredLogging = False

  __instance = None

  def __new__(cls):
    if gLogging.__instance is None:
      gLogging.__instance = object.__new__(cls)
      gLogging.__instance.initializeLogging()
    return gLogging.__instance

  def initializeLogging(self):
    """
    Initialization and first configuration of the root logger
    """
    # initialization default parameters
    logging.getLogger().setLevel(logging.INFO)
    logging.Formatter.converter = time.gmtime

    self.options = {'showHeaders': True, 'showThreads': False, 'Color': False, 'Path': False}
    self.componentName = "Framework"
    self.cfgPath = None

    # initialization of the backends
    self.backendsList = []
    self.backendsDict = {'stdout': StdoutBackend(), 'stderr': StderrBackend(), 'file': FileBackend()}
    self.__configureHandlers(['stdout'])
    
    # configuration of the level and update of the format
    self.__configureLevel()
    self.__updateFormat()


  def showHeaders(self, val=True):
    """
    Depending on the value, display or not the prefix of the message
    input: 
    - val: boolean determining the behaviour of the display
    """
    self.options['showHeaders'] = val
    self.__updateFormat()

  def showThreadIDs(self, val=True):
    """
    Depending on the value, display or not the thread ID
    input: 
    - val: boolean determining the behaviour of the display
    """
    self.options['showThreads'] = val

  def loadConfigurationFromCFGFile(self, componentName, cfgPath):
    """
    Configure logging with a cfg file
    input:
    - systemName: string represented as "system name/component name"
    - cfgPath: string of the cfg file path
    """
    from DIRAC.ConfigurationSystem.Client.Config import gConfig

    if not gLogging.__configuredLogging:
      self.componentName = componentName
      self.cfgPath = cfgPath

      # Backend options
      desiredBackendsStr = gConfig.getValue("%s/LogBackends" % cfgPath, 'stdout')
      desiredBackends = desiredBackendsStr.split(',')
      
      for backend in desiredBackends:
        retDict = gConfig.getOptionsDict("%s/BackendsOptions" % cfgPath)
        if retDict['OK'] and backend in self.backendsDict:
          self.backendsDict[backend].setParameters(retDict['Value'])

      # Format options
      self.options['Color'] = gConfig.getValue("%s/LogColor" % cfgPath, False)
      self.options['Path'] = gConfig.getValue("%s/LogShowLine" % cfgPath, False)
      
      currentLevelName = logging.getLevelName(logging.getLogger().getEffectiveLevel())
      levelname = gConfig.getValue("%s/LogLevel" % cfgPath, currentLevelName)
      logging.getLogger().setLevel(logging.getLevelName(levelname))

      # Configure outputs
      self.__configureHandlers(desiredBackends)
      self.__updateFormat()

      gLogging.__configuredLogging = True
 

  def __configureHandlers(self, listHandler):
    """
    Attach a list of handlers to the root logger
    input:
    - listHandler: a list of different names attaching to differents backends 
                   attaching to different handlers and formatters
    """
    for stringHandler in listHandler:
      stringHandler = stringHandler.lower()
      stringHandler = stringHandler.strip(" ")

      if stringHandler in self.backendsDict:
        backend = self.backendsDict[stringHandler]
        backend.configureHandler()

        if backend not in self.backendsList:
          logging.getLogger().addHandler(backend.handler)
          self.backendsList.append(backend)
      else:
        self.__updateFormat()
        logging.warning("Unexistant method for showing messages Unexistant %s logging method", stringHandler)

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
      logger.setLevel(logging.INFO)
    elif debLevs == 2:
      logger.setLevel(logging.INFO)
      self.showHeaders(True)
    elif debLevs >= 3:
      logger.setLevel(logging.DEBUG)
      self.showHeaders(True)
      self.showThreadIDs(True)

  def __setFormatter(self, fmt, datefmt):
    """
    Add the new formatter to the handlers' logger
    input:
    - fmt: string representing the format: "%(asctime)s UTC %(name)s %(levelname)s: %(message)"
    - datefmt: string representing the date format: "%Y-%m-%d %H:%M:%S"
    """
    logger = logging.getLogger()
    for backend in self.backendsList:
      formatter = backend.formatter
      formatter.setFormat(fmt, datefmt, self.componentName, self.options)
      backend.handler.setFormatter(formatter)

 

  def __updateFormat(self):
    """
    Update the format according to the showHeader option
    """
    if self.options['showHeaders']:
      fmt = '%(asctime)s UTC %(name)s %(levelname)s: %(message)s'
      datefmt = '%Y-%m-%d %H:%M:%S'
    else:
      fmt = '%(message)s'
      datefmt = None
    self.__setFormatter(fmt, datefmt)
