"""
LogLevels wrapper
"""

__RCSID__ = "$Id$"

import logging


class LogLevels(object):
  """
  Wrapper of the old LogLevels class. 
  LogLevels is used to integrate custom levels to logging: verbose, notice and always.

  It is useful to make conversion string-integer. 
  In face, logging use only integers while the oldgLogger used strings, so we need a converter.
  Example: log.setLevel(45) in logging become log.setLevel("always") in gLogger. 
  We keep the string form because there are many and many calls with string levels. 
  """
  __levelDict = {"DEBUG": logging.DEBUG,
                 "VERBOSE": 15,
                 "INFO": logging.INFO,
                 "WARN": logging.WARN,
                 "NOTICE": 35,
                 "ERROR": logging.ERROR,
                 "ALWAYS": 45,
                 "FATAL": logging.CRITICAL}

  @classmethod
  def getLevelValue(cls, sName):
    """
    Get a level value from a level name.
    We could use logging.getLevelName() to get the level value but it is less simple.
    :params sName: string representing a level name
    :return: a level value according to a level name
    """
    sName = sName.upper()
    sName = sName.upper()
    return cls.__levelDict.get(sName)

  @classmethod
  def getLevel(cls, level):
    """
    Get a level name from a level value.
    We could use logging.getLevelName() to get the level value but it is less simple.
    :params level: integer representing a level value
    :return: a level name according to a level value
    """
    for lev in cls.__levelDict:
      if cls.__levelDict[lev] == level:
        return lev
    return None

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
