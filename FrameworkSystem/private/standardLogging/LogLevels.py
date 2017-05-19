import logging


class LogLevels:
  """
  Wrapper of the old LogLevels class:
  - made to replace transparently gLogger
  """
  __levelDict = {"DEBUG": logging.DEBUG,
                 "VERBOSE": 15,
                 "INFO": logging.INFO,
                 "WARNING": logging.WARN,
                 "NOTICE": 35,
                 "ERROR": logging.ERROR,
                 "ALWAYS": 45,
                 "CRITICAL": logging.CRITICAL
                 }

  @classmethod
  def getLevelValue(cls, sName):
    """
    Return a level value according to a level name
    """
    sName = sName.upper()
    if cls.__levelDict.has_key(sName):
      return cls.__levelDict[sName]
    else:
      return None

  @classmethod
  def getLevel(cls, level):
    """ 
    Return a level name according to a level value
    """
    for lev in cls.__levelDict:
      if cls.__levelDict[lev] == level:
        return lev
    return "Unknown"

  @classmethod
  def getLevelNames(cls):
    """
    Return all level names available in the wrapper
    """
    return cls.__levelDict.keys()

  @classmethod
  def getLevels(cls):
    """
    Return a copy of the dictionary
    """
    return cls.__levelDict.copy()
