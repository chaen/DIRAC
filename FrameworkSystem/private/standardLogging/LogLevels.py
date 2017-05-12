import logging


class LogLevels:

  def __init__(self):
    self.__levelDict = {"always": logging.INFO,
                        "notice": logging.INFO,
                        "info": logging.INFO,
                        "verbose": logging.INFO,
                        "debug": logging.DEBUG,
                        "warn": logging.WARN,
                        "exception": logging.ERROR,
                        "error": logging.ERROR,
                        "fatal": logging.CRITICAL}

  def getLevelValue(self, sName):
    sName = sName.lower()
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
