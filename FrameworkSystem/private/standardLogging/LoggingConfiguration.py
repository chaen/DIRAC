import logging
import time
import sys
from os import getpid

from DIRAC.FrameworkSystem.private.standardLogging.Backend.StdoutBackend import StdoutBackend
from DIRAC.FrameworkSystem.private.standardLogging.Backend.StderrBackend import StderrBackend
from DIRAC.FrameworkSystem.private.standardLogging.Backend.FileBackend import FileBackend


"""
Logging configuration class
"""


class LoggingConfiguration():
  """
  Configuration of the standard Python logging to fit with the dirac gLogger 
  """

  @classmethod
  def initializeLogging(cls):
    """
    First logging configuration
    """
    # initialization
    cls.__initializeDefaultParameters()
    cls.__initializeBackends()
    cls.__configureHandlers(['stdout'])
    # configuration
    cls.__configureLevel()
    cls.__updateFormat()


  @classmethod
  def __initializeDefaultParameters(cls):
    cls.options = {'showHeaders': True,
                   'showThreads': False,
                   'Color': False,
                   'Path': False}
    
    cls.handlerOptions = {'file': {'FileName': 'Dirac-log_%s.log' % getpid()},
                          'stderr': {},
                          'stdout': {}}
    
    cls.componentName = "Framework"
    cls.cfgPath = None
    
    logging.getLogger().setLevel(logging.INFO)

  @classmethod
  def __initializeBackends(cls):
    logging.Formatter.converter = time.gmtime
    cls.backendsDict = {'stdout': StdoutBackend(),
                        'stderr': StderrBackend(),
                        'file': FileBackend()
                        }
    cls.backendsList = []

  @classmethod
  def __configureHandlers(cls, listHandler):
    """
    Attach handler to the root logger
    """
    for stringHandler in listHandler:
      stringHandler = stringHandler.lower()
      stringHandler = stringHandler.strip(" ")

      if stringHandler in cls.backendsDict:
        backend = cls.backendsDict[stringHandler]
        backend.setParameters(cls.handlerOptions[stringHandler])

        if backend not in cls.backendsList:
          logging.getLogger().addHandler(backend.handler)
          cls.backendsList.append(backend)
      else:
        # we update the format here, else the warning message will not be
        # formatted for all handlers
        cls.__updateFormat()
        logging.warning(
            "Unexistant method for showing messages Unexistant %s logging method", stringHandler)

  @classmethod
  def configureLogging(cls, componentName, cfgPath):
    """
    Create and set a new format with the component name to the handlers
    """
    # If not here. doesn't work because of loop dependancies
    from DIRAC.ConfigurationSystem.Client.Config import gConfig

    cls.componentName = componentName
    cls.cfgPath = cfgPath

    # Backend options
    desiredBackendsStr = gConfig.getValue("%s/LogBackends" % cfgPath, 'stdout')
    desiredBackends = desiredBackendsStr.split(',')
    for backend in desiredBackends:
      retDict = gConfig.getOptionsDict(
          "%s/NewBackendsOptions/%s" % (cfgPath, backend))
      if retDict['OK'] and backend in cls.handlerOptions:
        cls.handlerOptions[backend].update(retDict['Value'])

    # Format options
    cls.options['Color'] = gConfig.getValue("%s/LogColor" % cfgPath, False)
    cls.options['Path'] = gConfig.getValue("%s/LogShowLine" % cfgPath, False)
    # Configure outputs
    cls.__configureHandlers(desiredBackends)

    cls.__updateFormat()

  @classmethod
  def __configureLevel(cls):
    """
    Configure the log level of the running program according to the argv parameter
    It can be : -d, -dd, -ddd
    """
    debLevs = 0
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    for arg in sys.argv:
      if arg.find("-d") == 0:
        debLevs += arg.count("d")
    if debLevs == 1:
      logger.setLevel(logging.INFO)
    elif debLevs == 2:
      logger.setLevel(logging.INFO)
      cls.showHeaders(True)
    elif debLevs >= 3:
      logger.setLevel(logging.DEBUG)
      cls.showHeaders(True)
      cls.showThreadIDs(True)

  @classmethod
  def __setFormatter(cls, fmt, datefmt):
    """
    Add the new formatter to the handlers' logger 
    """
    logger = logging.getLogger()
    for backend in cls.backendsList:
      formatter = backend.formatter
      formatter.setFormat(fmt, datefmt, cls.componentName, cls.options)
      backend.handler.setFormatter(formatter)

  @classmethod
  def showHeaders(cls, val=True):
    """
    Define if it shows all information about the log or only the message
    """
    cls.options['showHeaders'] = val
    cls.__updateFormat()

  @classmethod
  def showThreadIDs(cls, val=True):
    """
    Define if it shows the thread id information about the log or not
    """
    cls.options['showThreads'] = val

  @classmethod
  def __updateFormat(cls):
    """
    Update the format according to the showHeader option
    """
    if cls.options['showHeaders']:
      fmt = '%(asctime)s UTC %(name)s %(levelname)s: %(message)s'
      datefmt = '%Y-%m-%d %H:%M:%S'
    else:
      fmt = '%(message)s'
      datefmt = None
    cls.__setFormatter(fmt, datefmt)
