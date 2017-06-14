"""
Test Speed Log creation
"""

__RCSID__ = "$Id$"

import time
import logging

from DIRAC import gLogger, oldgLogger


class TestSpeedLogCreation(object):
  """
  The purpose is to test the log creation in the three logging systems 
  in order to compare their performances. 
  """

  @staticmethod
  def createErrorLogRecord():
    """
    Create 1 000 000 error log records with the three logging systems and 
    evaluate the timing.
    """
    timegLogger = []
    timeOldgLogger = []
    timeLogging = []
    nbIter = 3
    for j in range(0, nbIter):
      logger = gLogger.getSubLogger("logger")
      start = time.time()
      for i in range(0, 1000000):
        logger.error("%d" % i)
      end = time.time()
      timegLogger.append(end - start)

    for j in range(0, nbIter):
      oldLogger = oldgLogger.getSubLogger("logger")
      start = time.time()
      for i in range(0, 1000000):
        oldLogger.error("%d" % i)
      end = time.time()
      timeOldgLogger.append(end - start)


      logging.getLogger().handlers[0].setFormatter(
          logging.Formatter("%(asctime)s UTC %(name)s %(levelname)s: %(message)s"))
    for j in range(0, nbIter):
      logger = logging.getLogger("logging")
      start = time.time()
      for i in range(0, 1000000):
        logger.error("%d",i)
      end = time.time()
      timeLogging.append(end - start)

    
    time1 = sum(timegLogger) / float(nbIter)
    time2 = sum(timeOldgLogger) / float(nbIter)
    time3 = sum(timeLogging) / float(nbIter)
    return (time1, time2, time3)

if __name__ == '__main__':
  print TestSpeedLogCreation.createErrorLogRecord()
