import logging


class LogLevels:

  def __init__(self):
    self.__oldLevels = {"ALWAYS": 46,
                        "NOTICE": 35,
                        "VERBOSE": 15,
                        "EXCEPTION": 44, 
                        "FATAL": 50
                        }

    self.__levelDict = {"INFO": logging.INFO,
                        "DEBUG": logging.DEBUG,
                        "WARN": logging.WARN,
                        "ERROR": logging.ERROR,
                        }
    self.__levelDict.update(self.__oldLevels)

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

  def getOldLevelNamesValues(self):
    oldLevels = {}
    for lvl in self.__oldLevels:
      oldLevels[lvl] = self.__oldLevels[lvl]
    return oldLevels
