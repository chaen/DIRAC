import logging


class LogLevels:
  """
  Wrapper of the old LogLevels class:
  - made to replace transparently gLogger
  """

  def __init__(self):
    """
    Initialize a dictionary of levels
    """
    self.__oldLevels = {"ALWAYS": 45,
                        "NOTICE": 25,
                        "VERBOSE": 15,
                        }

    self.__levelDict = {"INFO": logging.INFO,
                        "DEBUG": logging.DEBUG,
                        "WARN": logging.WARN,
                        "ERROR": logging.ERROR,
                        "CRITICAL": logging.CRITICAL
                        }
    self.__levelDict.update(self.__oldLevels)

  def getLevelValue(self, sName):
    """
    Return a level value according to a level name
    """
    if self.__levelDict.has_key(sName):
      return self.__levelDict[sName]
    else:
      return None

  def getLevel(self, level):
    """ 
    Return a level name according to a level value
    """
    for lev in self.__levelDict:
      if self.__levelDict[lev] == level:
        return lev
    return "Unknown"

  def getLevels(self):
    """
    Return all level names available in the wrapper
    """
    return self.__levelDict.keys()

  def getOldLevelNamesValues(self):
    """
    Return a dictionary of old levels from gLogger
    """
    oldLevels = self.__oldLevels.copy()
    return oldLevels
