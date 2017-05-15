import logging


class LogLevels:

  def __init__(self):
    self.__levelDict = {"ALWAYS": logging.INFO,
                        "NOTICE": logging.INFO,
                        "INFO": logging.INFO,
                        "VERBOSE": logging.INFO,
                        "DEBUG": logging.DEBUG,
                        "WARN": logging.WARN,
                        "EXCEPTION": logging.ERROR,
                        "ERROR": logging.ERROR,
                        "FATAL": logging.CRITICAL}

  def getLevelValue(self, sName):
    if self.__levelDict.has_key(sName):
      return self.__levelDict[sName]
    else:
      return None

  def getLevel(self, level):
    """ Get level name given the level digital value 
    """
    for lev in self.__levelDict:
      if self.__levelDict[lev] == level:
        return lev
    return "Unknown"

  def getLevels(self):
    return self.__levelDict.keys()
