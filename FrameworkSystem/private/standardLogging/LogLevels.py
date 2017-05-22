"""
LogLevels wrapper
"""
import logging


class LogLevels(object):
  """
  Wrapper of the old LogLevels class:
  - useful for the conversion string-integer because developers use only the string
    form of levels at the moment, and logging need the integer form.
  """
  __levelDict = {"DEBUG": logging.DEBUG,
                 "VERBOSE": 15,
                 "INFO": logging.INFO,
                 "WARNING": logging.WARN,
                 "NOTICE": 35,
                 "ERROR": logging.ERROR,
                 "ALWAYS": 45,
                 "CRITICAL": logging.CRITICAL}

  @classmethod
  def getLevelValue(cls, sName):
    """
    :return: a level value according to a level name
    """
    sName = sName.upper()
    result = None
    if cls.__levelDict.has_key(sName):
      result = cls.__levelDict[sName]
    return result

  @classmethod
  def getLevel(cls, level):
    """
    :return: a level name according to a level value
    """
    for lev in cls.__levelDict:
      if cls.__levelDict[lev] == level:
        return lev
    return "Unknown"

  @classmethod
  def getLevelNames(cls):
    """
    :return: all level names available in the wrapper
    """
    return cls.__levelDict.keys()

  @classmethod
  def getLevels(cls):
    """
    :return: a copy of the dictionary
    """
    return cls.__levelDict.copy()
